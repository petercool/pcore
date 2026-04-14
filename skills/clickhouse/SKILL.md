---
name: clickhouse
description: |
  Write ClickHouse integration code — connect via clickhouse-connect,
  create tables, insert/query DataFrames, ReplacingMergeTree for dedup,
  OHLCV time-series patterns.
  Triggers when: clickhouse, clickhouse-connect, ReplacingMergeTree,
  MergeTree, OHLCV, "insert into clickhouse", "query clickhouse",
  "clickhouse table", FINAL, time-series database, columnar database.
user-invocable: false
---

# ClickHouse

This skill guides writing correct ClickHouse integration code for storing
and querying OHLCV market data and analytics results.

## Official Documentation

**Docs URL**: https://clickhouse.com/docs

## Installation

```bash
uv add "clickhouse-connect>=0.8.0"
```

## Connection

```python
import clickhouse_connect

client = clickhouse_connect.get_client(
    host="127.0.0.1",    # or Tailscale IP for remote access
    port=8123,            # HTTP interface
    username="crescendo",
    password="mypassword",
    database="default",
)
print(client.server_version)  # e.g. 25.7.1.3997
```

For credentials from `.env`:
```python
import os
from dotenv import load_dotenv
load_dotenv()

client = clickhouse_connect.get_client(
    host=os.getenv("CLICKHOUSE_HOST", "127.0.0.1"),
    port=int(os.getenv("CLICKHOUSE_PORT", "8123")),
    username=os.getenv("CLICKHOUSE_USER", "default"),
    password=os.getenv("CLICKHOUSE_PASSWORD", ""),
    database=os.getenv("CLICKHOUSE_DATABASE", "default"),
)
```

## Table Engines

### MergeTree (basic, no dedup)

```sql
CREATE TABLE IF NOT EXISTS events (
    timestamp DateTime64(3, 'UTC'),
    symbol String,
    value Float64
) ENGINE = MergeTree()
ORDER BY (symbol, timestamp)
```

### ReplacingMergeTree (idempotent inserts — our choice for OHLCV)

```sql
CREATE TABLE IF NOT EXISTS ohlcv (
    symbol String,
    timeframe String,
    timestamp DateTime64(3, 'UTC'),
    open Float64,
    high Float64,
    low Float64,
    close Float64,
    volume Float64
) ENGINE = ReplacingMergeTree()
PARTITION BY (symbol, timeframe)
ORDER BY (symbol, timeframe, timestamp)
```

**Why ReplacingMergeTree**: Re-inserting the same `(symbol, timeframe,
timestamp)` row (e.g., during incremental updates) doesn't create
duplicates. Dedup happens automatically during background merges.
Use `SELECT ... FINAL` to force dedup at query time.

## CRUD Operations

### Insert a DataFrame

```python
import pandas as pd

df = pd.DataFrame({
    "symbol": ["BTCUSDT"] * 3,
    "timeframe": ["1d"] * 3,
    "timestamp": pd.to_datetime(["2024-01-01", "2024-01-02", "2024-01-03"], utc=True),
    "open": [42000.0, 42500.0, 43000.0],
    "high": [42800.0, 43200.0, 43500.0],
    "low": [41500.0, 42000.0, 42800.0],
    "close": [42500.0, 43000.0, 43200.0],
    "volume": [1000.0, 1200.0, 800.0],
})

client.insert_df(
    "ohlcv",
    df,
    column_names=["symbol", "timeframe", "timestamp", "open", "high", "low", "close", "volume"],
)
```

### Query to DataFrame

```python
df = client.query_df(
    "SELECT * FROM ohlcv FINAL "
    "WHERE symbol = {symbol:String} AND timeframe = {tf:String} "
    "ORDER BY timestamp",
    parameters={"symbol": "BTCUSDT", "tf": "1d"},
)
```

### Check existence

```python
count = client.command(
    "SELECT count() FROM ohlcv FINAL "
    "WHERE symbol = {s:String} AND timeframe = {t:String}",
    parameters={"s": "BTCUSDT", "t": "1d"},
)
has_data = int(count) > 0
```

### Execute DDL

```python
client.command("CREATE TABLE IF NOT EXISTS ...")
client.command("TRUNCATE TABLE ohlcv")
client.command("DROP TABLE IF EXISTS old_table")
```

## Key Concepts

### FINAL keyword

`SELECT ... FINAL` forces dedup on `ReplacingMergeTree` tables at
query time. Without `FINAL`, you may see duplicate rows if background
merges haven't completed yet.

```sql
-- May return duplicates if recent inserts haven't been merged
SELECT * FROM ohlcv WHERE symbol = 'BTCUSDT'

-- Always returns deduplicated data
SELECT * FROM ohlcv FINAL WHERE symbol = 'BTCUSDT'
```

### Partitioning

```sql
PARTITION BY (symbol, timeframe)
```

ClickHouse only reads relevant partitions when the query filters on
partition columns. `WHERE symbol = 'BTCUSDT'` skips all non-BTC data.

### Parameterised Queries

Always use parameterised queries to prevent SQL injection:

```python
# GOOD — parameterised
client.query_df("SELECT * FROM ohlcv WHERE symbol = {s:String}", parameters={"s": symbol})

# BAD — string interpolation (SQL injection risk)
client.query_df(f"SELECT * FROM ohlcv WHERE symbol = '{symbol}'")
```

## Concurrency

**ClickHouse supports concurrent reads AND writes** from multiple
clients/processes — no single-writer limitation. This is the key
advantage over DuckDB for distributed pipelines.

```python
# Safe from ANY number of Ray workers simultaneously:
client.insert_df("ohlcv", df)   # concurrent writes OK
client.query_df("SELECT ...")   # concurrent reads OK
```

## Quick Reference

| Task | Code |
|------|------|
| Connect | `clickhouse_connect.get_client(host, port, username, password)` |
| Create table | `client.command("CREATE TABLE IF NOT EXISTS ...")` |
| Insert DataFrame | `client.insert_df("table", df, column_names=[...])` |
| Query → DataFrame | `client.query_df("SELECT ...", parameters={...})` |
| Count rows | `client.command("SELECT count() FROM table WHERE ...")` |
| Dedup query | `SELECT * FROM table FINAL WHERE ...` |
| Drop table | `client.command("DROP TABLE IF EXISTS table")` |
| Server version | `client.server_version` |

## Anti-Patterns

- **Forgetting `FINAL`** on ReplacingMergeTree queries — returns duplicates
- **String interpolation in SQL** — use parameterised queries (`{name:Type}`)
- **Inserting row-by-row** — use `insert_df()` for batch inserts (1000x faster)
- **Not closing the client** — `client.close()` when done (though Python GC handles it)
- **Using `127.0.0.1` for remote workers** — use the network IP (e.g., Tailscale IP)

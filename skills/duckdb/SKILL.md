---
name: duckdb
description: |
  Write DuckDB code for analytical queries, Parquet scanning, data exploration,
  and in-memory analytics. Covers the full DuckDB API including connections,
  SQL queries, Parquet integration, concurrency model, and DuckLake.
  Triggers when: duckdb, read_parquet, parquet scan, analytical query, OLAP,
  "query parquet", hive_partitioning, union_by_name, duckdb.connect, DuckLake,
  in-memory database, columnar query.
user-invocable: false
---

# DuckDB

This skill guides writing correct DuckDB code for analytical queries, Parquet
file scanning, and in-memory data exploration. In this project, DuckDB is used
as a **Parquet query engine** (not for data storage — ClickHouse handles that).

## Official Documentation

**Docs URL**: https://duckdb.org/docs

## Installation

```bash
uv add "duckdb>=0.10.0"
```

## Core Patterns

### In-Memory Connection (preferred for analytics)

```python
import duckdb

conn = duckdb.connect(":memory:")  # no file, no locks, pure query engine
df = conn.execute("SELECT 42 AS answer").fetchdf()
conn.close()
```

### Query Parquet Files

```python
conn = duckdb.connect(":memory:")

# Single file
df = conn.execute("SELECT * FROM read_parquet('results.parquet')").fetchdf()

# Glob pattern — scan entire directory tree
df = conn.execute("""
    SELECT * FROM read_parquet('lake/backtests/**/*.parquet')
    ORDER BY sharpe DESC
""").fetchdf()

# Hive-style partition inference (infers partition columns from directory names)
df = conn.execute("""
    SELECT symbol, strategy, sharpe
    FROM read_parquet('lake/backtests/**/*.parquet', hive_partitioning=true)
    WHERE symbol = 'BTCUSDT'
""").fetchdf()
# 'symbol' and 'strategy' columns come from directory names like symbol=BTCUSDT/strategy=trend/

# Union by name (for files with different schemas)
df = conn.execute("""
    SELECT * FROM read_parquet('lake/validation/**/*.parquet',
                               hive_partitioning=true,
                               union_by_name=true)
""").fetchdf()
```

### Write Query Results to Parquet

```python
conn.execute("""
    COPY (SELECT * FROM read_parquet('input/**/*.parquet') WHERE sharpe > 1.0)
    TO 'filtered_results.parquet' (FORMAT parquet, COMPRESSION snappy)
""")
```

### Query Pandas DataFrames Directly

```python
import pandas as pd

df = pd.DataFrame({"a": [1, 2, 3], "b": [4, 5, 6]})
conn = duckdb.connect(":memory:")
result = conn.execute("SELECT * FROM df WHERE a > 1").fetchdf()
# DuckDB can query pandas DataFrames directly by name
```

## Concurrency Model

### The Fundamental Rule

**DuckDB is single-writer, multiple-reader** for `.duckdb` files:
- Multiple processes can read the same file via `read_only=True`
- Only ONE process can write at a time
- A second writer will get a lock error

```python
# SAFE — multiple readers
conn = duckdb.connect("data.duckdb", read_only=True)

# SAFE — in-memory (no file, no locks)
conn = duckdb.connect(":memory:")

# UNSAFE from multiple processes
conn = duckdb.connect("data.duckdb")  # read-write, exclusive lock
```

### Multi-Worker Pattern (used in this project)

For Prefect/Ray pipelines with multiple workers:

1. **Workers write to Parquet files** (immutable, no contention)
2. **Coordinator queries via `duckdb.connect(":memory:")` + `read_parquet()`**
3. **No `.duckdb` file involved** — pure in-memory query engine

```python
# Worker (runs on any Ray node):
result_df.to_parquet(f"lake/backtests/symbol={symbol}/result.parquet")

# Coordinator (runs once, consolidates):
conn = duckdb.connect(":memory:")
leaderboard = conn.execute("""
    SELECT * FROM read_parquet('lake/backtests/**/*.parquet', hive_partitioning=true)
    ORDER BY sharpe DESC LIMIT 20
""").fetchdf()
```

## DuckLake (v1.0, April 2026)

DuckLake provides ACID multi-table transactions over Parquet files
with a SQL catalog. Useful when multiple writers need to modify the
same logical table transactionally.

```sql
ATTACH 'ducklake:sqlite:catalog.db' AS lake;
INSERT INTO lake.backtests VALUES (...);
COMMIT;
```

**When to use**: ACID requirements across concurrent writers.
**When NOT to use**: append-only workloads where each worker writes
independent files (use plain Parquet instead — simpler).

## Quick Reference

| Task | Code |
|------|------|
| In-memory connection | `duckdb.connect(":memory:")` |
| Read Parquet | `SELECT * FROM read_parquet('path')` |
| Glob scan | `read_parquet('dir/**/*.parquet')` |
| Hive partitions | `read_parquet('...', hive_partitioning=true)` |
| Mixed schemas | `read_parquet('...', union_by_name=true)` |
| Write Parquet | `COPY (...) TO 'out.parquet' (FORMAT parquet)` |
| Query DataFrame | `SELECT * FROM df` (pandas DF by variable name) |
| Read-only file | `duckdb.connect('file.duckdb', read_only=True)` |
| Get as DataFrame | `.fetchdf()` |
| Get as list | `.fetchall()` |

## Anti-Patterns

- **Multiple processes writing to same `.duckdb` file** — lock error; use Parquet files instead
- **Opening `.duckdb` without `read_only=True` from workers** — blocks other connections
- **Forgetting `conn.close()`** — holds the file lock
- **Not using `hive_partitioning=true`** — loses partition column info from directory names
- **Not using `union_by_name=true`** for files with different schemas — causes schema mismatch errors
- **Creating a `.duckdb` file when `:memory:` suffices** — unnecessary file I/O and lock complexity

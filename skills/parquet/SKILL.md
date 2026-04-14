---
name: parquet
description: |
  Write and read Apache Parquet files correctly — partitioning strategies, compression,
  DuckDB scans, BigQuery upload, schema management.
  Triggers when: parquet, columnar storage, partition, snappy, zstd, pyarrow, to_parquet,
  read_parquet, hive partitioning, "write parquet", "parquet files".
user-invocable: false
---

# Apache Parquet

This skill guides correct Parquet usage for storing intermediate and final
backtesting results in a data lake pattern.

## Installation

```bash
uv add "pyarrow>=14.0"
# pandas and duckdb already support Parquet natively
```

## Writing Parquet

### Simple write (pandas)

```python
df.to_parquet("results.parquet", compression="snappy", index=False)
```

### Hive-style partitioned write

```python
import pyarrow as pa
import pyarrow.parquet as pq

table = pa.Table.from_pandas(df)
pq.write_to_dataset(
    table,
    root_path="lake/backtests",
    partition_cols=["symbol", "strategy"],
    # Creates: lake/backtests/symbol=BTCUSDT/strategy=trend/part-0.parquet
)
```

### Manual partitioned write (simpler, worker-safe)

```python
from pathlib import Path

def write_result(df: pd.DataFrame, symbol: str, strategy: str, tag: str):
    """Each worker writes its own uniquely-named file. No contention."""
    path = Path(f"lake/backtests/symbol={symbol}/strategy={strategy}")
    path.mkdir(parents=True, exist_ok=True)
    df.to_parquet(path / f"{tag}.parquet", compression="snappy", index=False)
```

## Reading Parquet

### pandas

```python
df = pd.read_parquet("results.parquet")
df = pd.read_parquet("lake/backtests/symbol=BTCUSDT/")  # reads all files in partition
```

### DuckDB (recommended for lake queries — much faster)

```python
import duckdb

conn = duckdb.connect(":memory:")

# Read single file
df = conn.execute("SELECT * FROM read_parquet('results.parquet')").fetchdf()

# Read entire lake with glob + Hive partition inference
df = conn.execute("""
    SELECT symbol, strategy, sharpe, total_return_pct
    FROM read_parquet('lake/backtests/**/*.parquet', hive_partitioning=true)
    WHERE sharpe > 1.0
    ORDER BY sharpe DESC
""").fetchdf()

# Partition pruning — DuckDB only reads relevant partitions
df = conn.execute("""
    SELECT * FROM read_parquet('lake/backtests/**/*.parquet', hive_partitioning=true)
    WHERE symbol = 'BTCUSDT'
""").fetchdf()
# Only reads files under lake/backtests/symbol=BTCUSDT/
```

## Compression

| Codec | Speed | Ratio | When to use |
|-------|-------|-------|-------------|
| `snappy` | Fastest | ~2x | **Default choice** — good balance |
| `zstd` | Fast | ~3x | Long-term storage, BigQuery upload |
| `gzip` | Slow | ~3.5x | Maximum compression, rare reads |
| `none` | Instant | 1x | Debugging only |

## Partitioning Strategies

### For backtesting results

```
lake/
  backtests/
    symbol=BTCUSDT/
      strategy=trend_ema/
        ema_200.parquet
        ema_500.parquet
      strategy=pairs/
        window_2000_z_2.5.parquet
    symbol=ETHUSDT/
      ...
  pairs/
    pair=BTCUSDT_ETHUSDT/
      window_2000_z_2.5.parquet
    pair=BTCUSDT_SPY/
      window_2000_z_2.5.parquet
```

**Rules of thumb:**
- Partition on columns you filter by (symbol, strategy, pair)
- Don't over-partition (< 10K partitions total)
- Keep each file > 1 MB (too many tiny files hurts scan performance)
- Use snake_case for partition column names

## BigQuery Upload

```python
from google.cloud import bigquery

client = bigquery.Client()
with open("results.parquet", "rb") as f:
    job = client.load_table_from_file(
        f, "project.dataset.results",
        job_config=bigquery.LoadJobConfig(
            source_format=bigquery.SourceFormat.PARQUET,
            write_disposition="WRITE_APPEND",
        ),
    )
    job.result()
```

## Anti-Patterns

- **Writing Parquet from multiple processes to the same file** — use separate files per worker
- **Not using `hive_partitioning=true`** in DuckDB `read_parquet()` — loses partition column info
- **Over-partitioning** (one file per trade) — millions of tiny files hurts scan performance; group by logical units
- **Storing large binary blobs in Parquet** — Parquet is for tabular data only; use separate object storage for non-tabular content
- **Using `index=True`** in `to_parquet` — the pandas index becomes a column; usually unwanted

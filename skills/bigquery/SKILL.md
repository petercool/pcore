---
name: bigquery
description: |
  Write Google BigQuery integration code — read/write DataFrames, schema management,
  partitioning, Parquet uploads, cost optimization.
  Triggers when: bigquery, google cloud, GCP, bq, data warehouse, "upload to bigquery",
  "query bigquery", "load parquet to bigquery", partitioned table, clustering.
user-invocable: false
---

# Google BigQuery

This skill guides writing correct BigQuery integration code for storing and
querying backtesting results at scale.

## Official Documentation

**Docs URL**: https://cloud.google.com/bigquery/docs

## Installation & Setup

```bash
# Install Python client
uv add "google-cloud-bigquery[pandas]>=3.0" "google-cloud-bigquery-storage>=2.0"

# Authenticate (one-time)
gcloud auth application-default login
# OR set a service account key
export GOOGLE_APPLICATION_CREDENTIALS="/path/to/service-account.json"
```

## Core Patterns

### Write a DataFrame to BigQuery

```python
from google.cloud import bigquery
import pandas as pd

client = bigquery.Client(project="my-project")

# Simple write
job = client.load_table_from_dataframe(
    df, "project.dataset.backtest_results",
    job_config=bigquery.LoadJobConfig(
        write_disposition="WRITE_APPEND",
    ),
)
job.result()  # wait for completion
```

### Write with Partitioning + Clustering (recommended for time-series)

```python
job_config = bigquery.LoadJobConfig(
    schema=[
        bigquery.SchemaField("symbol", "STRING", mode="REQUIRED"),
        bigquery.SchemaField("date", "DATE", mode="REQUIRED"),
        bigquery.SchemaField("strategy", "STRING"),
        bigquery.SchemaField("sharpe", "FLOAT64"),
        bigquery.SchemaField("total_return_pct", "FLOAT64"),
        bigquery.SchemaField("max_dd_pct", "FLOAT64"),
        bigquery.SchemaField("params", "JSON"),
    ],
    time_partitioning=bigquery.TimePartitioning(
        type_=bigquery.TimePartitioningType.DAY,
        field="date",
    ),
    clustering_fields=["symbol", "strategy"],
    write_disposition="WRITE_APPEND",
)
```

### Load Parquet to BigQuery (bulk upload)

```python
# Most efficient for large datasets — bypass DataFrame conversion
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

### Query BigQuery → DataFrame

```python
query = """
SELECT symbol, strategy, AVG(sharpe) as avg_sharpe
FROM `project.dataset.backtest_results`
WHERE date >= '2024-01-01'
GROUP BY symbol, strategy
ORDER BY avg_sharpe DESC
LIMIT 20
"""
df = client.query(query).to_dataframe()
```

## Cost Optimization

1. **Partition by date** — queries scan only relevant partitions
2. **Cluster by symbol + strategy** — BigQuery pre-sorts data for fast filter scans
3. **Set expiration** — auto-delete old partitions:
   ```python
   time_partitioning=bigquery.TimePartitioning(
       expiration_ms=90 * 24 * 60 * 60 * 1000,  # 90-day TTL
   )
   ```
4. **Use Parquet load jobs** instead of streaming inserts (10x cheaper for batch)
5. **SELECT only needed columns** — BigQuery charges by bytes scanned

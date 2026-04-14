# pcore

Personal Claude Code plugin — research workflows, development patterns,
and productivity skills.

## Installation

```bash
# From GitHub
claude plugin install pcore@petercool

# From local path (development)
claude --plugin-dir /path/to/pcore
```

## Available skills

| Skill | Invoke | Description |
|---|---|---|
| research-iterate-develop | `/pcore:research-iterate-develop` | Numbered experiments, leaderboard-driven iteration, supervisor reports, walk-forward validation |
| vectorbt-pro | `/pcore:vectorbt-pro` | VBT Pro backtesting, data loading, indicators, optimization, parameter sweeps, walk-forward, portfolio analysis |
| crescendo-data | `/pcore:crescendo-data` | Crescendo ClickHouse — OHLCV + whale/shark/lightsaber signals, queries, VBT Pro integration |
| clickhouse | `/pcore:clickhouse` | ClickHouse integration — connect, create tables, insert/query, ReplacingMergeTree, OHLCV patterns |
| duckdb | `/pcore:duckdb` | DuckDB analytical queries, Parquet scanning, in-memory analytics, concurrency, DuckLake |
| bigquery | `/pcore:bigquery` | Google BigQuery — read/write DataFrames, schema management, partitioning, Parquet uploads |
| parquet | `/pcore:parquet` | Apache Parquet — partitioning strategies, compression, DuckDB scans, BigQuery upload |
| prefect | `/pcore:prefect` | Prefect v3 workflow orchestration — flows, tasks, work pools, concurrency, Ray integration |

## What's in the box

The `research-iterate-develop` skill provides:

- **Methodology guide** — core principles for empirical research projects
  (numbered experiments, one hypothesis per script, leaderboard-driven
  iteration, supervisor reports, walk-forward validation)
- **Reference templates** — fill-in-the-blank starting points for:
  - `CLAUDE.md` — project brief with source-of-truth table, invariants,
    current phase
  - `research/exp_NN_topic.py` — canonical experiment script skeleton
  - `research/REPORT_SUPERVISOR.md` — narrative research report structure
  - `docs/strategy-phases.md` — phase roadmap with exit criteria

## Adding to a project

After installing, the skill activates when Claude detects research /
experiment / iteration context. Invoke explicitly with
`/pcore:research-iterate-develop` to get the full methodology guide
and access to the reference templates.

## Development

See `CLAUDE.md` for the contribution workflow.

### Conventional commits

```
feat(research-iterate-develop): add walk-forward validation section
fix(research-iterate-develop): correct experiment numbering guidance
feat: add new skill code-review-checklist
docs: update README installation instructions
```

### Versioning

Automated via [release-please](https://github.com/googleapis/release-please).
Conventional commits on `main` trigger version bumps in
`.claude-plugin/plugin.json` and `CHANGELOG.md`.

## License

MIT

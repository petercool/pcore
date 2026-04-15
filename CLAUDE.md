# pcore — Personal Claude Code Plugin

## What this is

Personal full-stack Claude Code plugin. Skills, agents, and hooks for
research workflows, development patterns, and productivity.

Add marketplace (one-time):
  `claude plugin marketplace add https://github.com/petercool/pcore`
Install:
  `claude plugin install pcore@petercool`
Test locally:
  `claude --plugin-dir /path/to/pcore`

## How to develop

- Branch from `main`, use conventional commits, PR for every change
- Test locally: `claude --plugin-dir .` (from the pcore directory)
- Reload in session: `/reload-plugins`
- Validate: `/plugin validate`

## Adding a new skill

1. Create `skills/<skill-name>/SKILL.md` with frontmatter (`name`, `description`)
2. Add reference files in `skills/<skill-name>/references/` if needed
3. Test locally with `claude --plugin-dir .`
4. Verify skill appears in `/help` output
5. Create a PR with a `feat(<skill-name>):` conventional commit
6. After merge to main, release-please creates a version-bump PR

## Versioning

- Semver in `.claude-plugin/plugin.json` and `.release-please-manifest.json`
- Automated via release-please GitHub Action on push to `main`
- Conventional commits drive bumps:
  - `feat:` or `feat(<scope>):` → minor (0.1.0 → 0.2.0)
  - `fix:` → patch (0.1.0 → 0.1.1)
  - `feat!:` or `BREAKING CHANGE:` → major (or minor while on 0.x)
- `CHANGELOG.md` is auto-generated — do not edit manually

## Invariants

- Every skill MUST have `name` and `description` in SKILL.md frontmatter
- Every skill's `description` MUST include trigger phrases for auto-invocation
- Template files in `references/` use `{{PLACEHOLDER}}` syntax
- All directories live at plugin root — NOT inside `.claude-plugin/`
- Only plugin metadata files (`plugin.json` and `marketplace.json`) go in `.claude-plugin/`

## Current skills

| Skill | Namespace | Description |
|---|---|---|
| research-iterate-develop | `/pcore:research-iterate-develop` | Numbered experiments, leaderboard iteration, supervisor reports |
| vectorbt-pro | `/pcore:vectorbt-pro` | VBT Pro backtesting, data loading, indicators, parameter sweeps, walk-forward |
| crescendo-data | `/pcore:crescendo-data` | Crescendo ClickHouse data — connection, queries, signals, VBT Pro integration |
| clickhouse | `/pcore:clickhouse` | ClickHouse integration — connect, create tables, insert/query, ReplacingMergeTree |
| duckdb | `/pcore:duckdb` | DuckDB analytical queries, Parquet scanning, concurrency, DuckLake |
| bigquery | `/pcore:bigquery` | Google BigQuery — read/write DataFrames, schema, partitioning, Parquet uploads |
| parquet | `/pcore:parquet` | Apache Parquet — partitioning, compression, DuckDB scans, BigQuery upload |
| prefect | `/pcore:prefect` | Prefect v3 workflows — flows, tasks, work pools, concurrency, Ray integration |
| content-brainstorm | `/pcore:content-brainstorm` | Brainstorm content angles from source material — headlines, hooks, descriptions, image plans across LinkedIn/X/blog/podcast/email |
| content-engine | `/pcore:content-engine` | Turn a topic into platform-native posts across LinkedIn/X/Newsletter (v1) — each post rethinks the topic, never reformatted. 17-file content engine with voice, hooks, repurposing chain, audience segments |

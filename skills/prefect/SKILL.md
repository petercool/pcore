---
name: prefect
description: |
  Write Prefect v3 workflow orchestration code — flows, tasks, work pools, concurrency,
  retries, local server, and parallel execution patterns.
  Triggers when: prefect, @flow, @task, workflow, pipeline, orchestration, work pool,
  worker, .submit(), task runner, deployment, schedule, concurrent tasks, retry,
  "run pipeline", "start workers", "prefect server".
user-invocable: false
---

# Prefect v3

This skill guides writing correct Prefect v3 workflow code for data pipelines,
backtesting orchestration, and parallel task execution.

## Official Documentation

**Docs URL**: https://docs.prefect.io/v3

## Installation & Setup

```bash
# Install
uv add "prefect>=3.0"

# Start local server (port 4200)
prefect server start

# Set API URL for local server
prefect config set PREFECT_API_URL="http://127.0.0.1:4200/api"

# Create a process-based work pool
prefect work-pool create research-pool --type process

# Start a worker (in a separate terminal)
prefect worker start --pool research-pool --limit 8
```

## Core Concepts

### Flows and Tasks

```python
from prefect import flow, task
from prefect.futures import wait

@task(retries=3, retry_delay_seconds=[2, 4, 8])
def fetch_data(symbol: str) -> pd.DataFrame:
    """Tasks are the units of work. Retries handle transient failures."""
    return dm.load(symbol, "1d")

@task
def run_backtest(data: pd.DataFrame, params: dict) -> dict:
    """Each task runs independently, can be parallelised."""
    return {"sharpe": 1.5, "return": 42.0}

@flow(name="research-pipeline", log_prints=True)
def research(symbols: list[str]):
    """Flows orchestrate tasks. They can call other flows (subflows)."""
    # .submit() runs tasks concurrently via the work pool
    data_futures = [fetch_data.submit(s) for s in symbols]
    
    # Tasks that take futures as input wait automatically
    results = [run_backtest.submit(d, {"ema": 200}) for d in data_futures]
    
    # Explicit wait + collect results
    wait(results)
    return [r.result() for r in results]
```

### Key Rules

1. **Use `.submit()` for concurrent execution**, not direct calls.
   Direct calls (`fetch_data(symbol)`) run synchronously in the flow.
   `.submit()` sends the task to a worker for parallel execution.

2. **Pass futures as task inputs** for implicit dependency chains.
   When a task receives a future, Prefect waits for it before running.
   ```python
   data_future = fetch_data.submit("BTCUSDT")
   result = process.submit(data_future)  # waits for data_future
   ```

3. **Use `wait()` to collect results** from submitted tasks.
   ```python
   from prefect.futures import wait
   futures = [task.submit(x) for x in items]
   wait(futures)  # blocks until all complete
   results = [f.result() for f in futures]
   ```

4. **Use `wait_for=` for explicit dependencies** without data passing.
   ```python
   setup = setup_task.submit()
   work = do_work.submit(wait_for=[setup])  # waits for setup
   ```

### Concurrency Control

```python
# Limit concurrent tasks via work pool (set at pool creation)
# prefect work-pool create pool-name --type process --limit 8

# Or via task-level concurrency limits
from prefect.concurrency.sync import concurrency

@task
def rate_limited_api_call(symbol: str):
    with concurrency("binance-api", occupy=1):  # max 1 concurrent
        return vbt.BinanceData.pull(symbol)
```

### Retries with Exponential Backoff

```python
from prefect.tasks import exponential_backoff

@task(
    retries=4,
    retry_delay_seconds=exponential_backoff(backoff_factor=2),
    retry_jitter_factor=0.5,
)
def flaky_api_call(symbol: str):
    """Retries at 2s, 4s, 8s, 16s with ±50% jitter."""
    return api.get(symbol)
```

### Subflows (Nested Flows)

```python
@flow
def stage_1_data():
    """Subflow for data acquisition."""
    for symbol in symbols:
        pull_data.submit(symbol)

@flow
def stage_2_features():
    """Subflow for feature engineering."""
    for symbol in symbols:
        compute_features.submit(symbol)

@flow(name="main-pipeline")
def main():
    """Top-level flow calls subflows sequentially."""
    stage_1_data()        # completes before stage_2 starts
    stage_2_features()    # runs after stage_1
```

## Quick Reference

| Pattern | Code |
|---------|------|
| Define a task | `@task(retries=3)` |
| Define a flow | `@flow(name="my-flow")` |
| Run task concurrently | `future = task.submit(arg)` |
| Wait for futures | `wait(futures)` |
| Get result | `future.result()` |
| Explicit dependency | `task.submit(wait_for=[other])` |
| Subflow | Call a `@flow` inside another `@flow` |
| Start server | `prefect server start` |
| Create work pool | `prefect work-pool create NAME --type process` |
| Start worker | `prefect worker start --pool NAME --limit N` |
| Log output | `@flow(log_prints=True)` then use `print()` |

## Ray Integration (prefect-ray)

Use `RayTaskRunner` to distribute tasks across a Ray cluster:

```bash
uv add "prefect-ray>=0.4.0"
```

```python
from prefect_ray.task_runners import RayTaskRunner

@flow(
    task_runner=RayTaskRunner(
        address="ray://100.116.227.41:10001",
        init_kwargs={
            "runtime_env": {
                "working_dir": "/path/to/project",
                "excludes": ["data/", ".venv/", ".git/"],
                "env_vars": {
                    "PREFECT_API_URL": "http://100.116.227.41:4200/api",
                },
            },
        },
    )
)
def distributed_flow():
    futures = [my_task.submit(x) for x in items]
    wait(futures)
```

### Critical Ray lessons (from this project)

1. **Defer ALL project imports into task function bodies** — not module
   level. Ray's `working_dir` sandbox isn't set up when module-level
   code runs during deserialisation.
   ```python
   # BAD — fails on Ray workers
   from data_manager import DataManager  # module level
   @task
   def my_task(): dm = DataManager()

   # GOOD — works on Ray workers
   @task
   def my_task():
       from data_manager import DataManager  # inside function
       dm = DataManager()
   ```

2. **Use `Any` for type annotations on task parameters** — not Pydantic
   models. Ray serialises task arguments; if the model class can't be
   found during deserialisation (before `working_dir` is unpacked),
   it fails silently.

3. **Set `PREFECT_API_URL` in `runtime_env.env_vars`** to the head
   node's network IP (not `127.0.0.1`). Remote workers report task
   status back to the Prefect server — they need a routable address.

4. **Start Prefect server with `--host 0.0.0.0`** so remote workers
   can reach it: `prefect server start --host 0.0.0.0`

5. **Don't use `runtime_env.pip`** if the base Ray venv already has
   the packages. `pip` creates an isolated venv that does NOT inherit
   from the base — packages like vectorbtpro (private git repo) won't
   be found.

6. **Use `excludes` in `working_dir`** to skip large files (data dirs,
   .venv, .git). The upload should be <1MB for fast distribution.

## Anti-Patterns

- **Direct task calls inside flows** — `task(arg)` runs synchronously; use `task.submit(arg)` for concurrency
- **Missing `wait()`** — if you don't wait or collect results, the flow may exit before tasks complete
- **Returning large objects from tasks** — Prefect serialises return values; return small dicts, not full DataFrames
- **Shared mutable state between tasks** — tasks run in separate processes; communicate via return values only
- **Not setting `PREFECT_API_URL`** — tasks can't find the server without this env var
- **Module-level imports of project code in Ray tasks** — fails during deserialisation; defer to function body
- **Using `runtime_env.pip` when base venv has all deps** — creates isolated venv, breaks private packages

---
name: vectorbt-pro
description: |
  Write VectorBT Pro backtesting, data loading, indicator, optimization, and analysis code.
  Triggers when: vectorbt, vbt, backtest, portfolio simulation, parameter sweep, walk-forward,
  indicator factory, signal generation, from_signals, from_orders, TA-Lib indicator, Param,
  Splitter, cross-validation, Sharpe ratio, drawdown, "run a backtest", "optimize strategy",
  "test parameters", "load market data", "build indicator", heatmap, equity curve,
  portfolio optimization, DCA, stop loss, trailing stop, take profit, signal cleaning,
  "VBT Pro", "vectorbtpro", performance metrics, trade analysis, Renko, pair trading.
user-invocable: true
---

# VectorBT Pro

This skill guides writing correct, performant VectorBT Pro code for backtesting, data loading, indicator construction, parameter optimization, and portfolio analysis.

## Official Documentation

**Docs URL**: https://vectorbt.pro/pvt_4f8d7c01

> **NOTE**: VectorBT Pro periodically changes this documentation link. If the URL above returns 404 or is inaccessible, ask the user:
> "The VectorBT Pro docs link appears to be outdated. Please provide the current documentation URL (usually found at vectorbt.pro after login)."
> Then use the updated link for all doc references in this session.

## Three Inviolable Rules

1. **Always `.vbt.signals.clean()` before `PF.from_signals()`** — Overlapping entry/exit signals cause silent position corruption. Every signal pair must be cleaned before portfolio construction.
2. **Always include `fees` in portfolio construction** — Zero-fee backtests are meaningless. Use `fees=0.003` for crypto, `fees=0.001` for equities as minimum defaults.
3. **Use `vbt.Param()` for parameter sweeps, never manual for-loops** — Manual loops over parameters lose VBT's vectorized broadcasting and are 10-100x slower. `vbt.Param()` handles the Cartesian product natively.

## Installation & Setup

### Prerequisites
- **Python >= 3.11**
- **GitHub CLI** (`gh`) — VBT Pro is NOT on PyPI, it's installed from a private GitHub repo
- **TA-Lib** system library (required for `vbt.talib()` indicators)

### Step 1: Install TA-Lib system library
```bash
# macOS (Apple Silicon)
arch -arm64 brew install ta-lib

# macOS (Intel)
brew install ta-lib

# Ubuntu/Debian
sudo apt-get install -y libta-lib0-dev

# Or build from source: https://ta-lib.github.io/ta-lib-python/install.html
```

### Step 2: Authenticate GitHub CLI
```bash
gh auth login
# Select GitHub.com → HTTPS → Login with browser
```

### Step 3a: New project with uv
```bash
# Create project
uv init my-backtest-project
cd my-backtest-project

# Add VBT Pro with extras (adjust rev to latest version)
uv add "vectorbtpro[data,perf,opt,exec,plot,pfopt,stats,msg,io,knwl]" --git https://github.com/polakowo/vectorbt.pro --rev v2026.3.1

# Or in pyproject.toml manually:
# [project] dependencies = ["vectorbtpro[data,perf,opt,exec,plot,pfopt,stats,msg,io,knwl]"]
# [tool.uv.sources] vectorbtpro = { git = "https://github.com/polakowo/vectorbt.pro", rev = "v2026.3.1" }
```

### Step 3b: Existing project with pip
```bash
pip install "vectorbtpro[data,perf,opt,exec,plot,pfopt,stats,msg,io,knwl] @ git+https://github.com/polakowo/vectorbt.pro@v2026.3.1"
```

### Extras Reference
| Extra | Provides |
|-------|----------|
| `data` | Data providers (Binance, Yahoo Finance, TradingView, etc.) |
| `perf` | Numba-accelerated performance metrics |
| `opt` | Parameter optimization, parameterized decorator |
| `exec` | Execution engines (threadpool, dask, processpool) |
| `plot` | Plotly-based interactive visualizations |
| `pfopt` | Portfolio optimization (PortfolioOptimizer, PyPortfolioOpt, Riskfolio) |
| `stats` | Statistical analysis and metrics |
| `msg` | Messaging and notifications |
| `io` | I/O support (HDF5, DuckDB, etc.) |
| `knwl` | Knowledge base and indicator library |

## Import Convention

```python
import vectorbtpro as vbt   # Standard import (recommended)
# or
from vectorbtpro import vbt  # Also works
```

## Quick Reference

| Task | API | Example |
|------|-----|---------|
| Load Binance data | `vbt.BinanceData.pull()` | `vbt.BinanceData.pull("BTCUSDT", start="2020-01-01")` |
| Load Yahoo Finance | `vbt.YFData.pull()` | `vbt.YFData.pull("SPY", start="2020")` |
| Load TradingView | `vbt.TVData.pull()` | `vbt.TVData.pull("AAPL", timeframe="1D")` |
| Cache to HDF5 | `data.to_hdf()` | `data.to_hdf("cache.h5")` |
| Load from HDF5 | `vbt.HDFData.pull()` | `vbt.HDFData.pull("cache.h5")` |
| Run TA-Lib indicator | `vbt.talib("NAME")` | `vbt.talib("RSI").run(close, timeperiod=14)` |
| Fast TA-Lib (no wrapper) | `data.run("talib_func:name")` | `data.run("talib_func:sma", timeperiod=20)` |
| All TA-Lib at once | `data.run("talib")` | `data.run("talib", mavp=vbt.run_arg_dict(periods=14))` |
| Signal crossover | `.vbt.crossed_above/below()` | `fast_sma.vbt.crossed_above(slow_sma)` |
| NaN-safe crossover | `.vbt.crossed_above(x, dropna=True)` | `fast.vbt.crossed_above(slow, dropna=True)` |
| Clean signals | `.vbt.signals.clean()` | `entries, exits = entries.vbt.signals.clean(exits)` |
| Forward-shift signals | `.vbt.signals.fshift()` | `entries = entries.vbt.signals.fshift()` |
| Backtest from signals | `vbt.PF.from_signals()` | See Workflow Step 4 |
| Buy-and-hold benchmark | `vbt.PF.from_holding()` | `vbt.PF.from_holding(close, fees=0.003)` |
| Random signal baseline | `vbt.PF.from_random_signals()` | `vbt.PF.from_random_signals(data, n=10)` |
| DCA backtest | `vbt.PF.from_orders()` | See `references/backtesting-and-signals.md` |
| Parameter sweep | `vbt.Param()` | `sl_stop=vbt.Param([0.03, 0.05, 0.1])` |
| Conditional params | `vbt.Param(vals, condition=)` | `vbt.Param(windows, condition="x < slow")` |
| Stats | `pf.stats()` | `pf.stats(per_column=True)` |
| Heatmap | `.vbt.heatmap()` | `pf.sharpe_ratio.vbt.heatmap(x_level=..., y_level=...)` |
| Walk-forward split | `vbt.Splitter.from_rolling()` | See `references/optimization-and-walkforward.md` |
| Purged K-fold | `vbt.Splitter.from_purged_kfold()` | See `references/optimization-and-walkforward.md` |
| Portfolio optimizer | `vbt.PFO.from_allocate_func()` | See `references/advanced-patterns.md` |
| Inline help | `vbt.phelp()` | `vbt.phelp(vbt.talib("RSI").run)` |

## Core Workflow

### STEP 1: Load Data

```python
import vectorbtpro as vbt

# Crypto from Binance
data = vbt.BinanceData.pull(
    "BTCUSDT",              # Single symbol or list: ["BTCUSDT", "ETHUSDT"]
    start="2020-01-01 UTC",
    end="2024-12-31 UTC",
    timeframe="1d",         # "1m", "5m", "1h", "1d", etc.
)

# Equities from Yahoo Finance
data = vbt.YFData.pull(
    symbols=["SPY", "TLT", "XLF"],
    start="2020",
    missing_index="drop",   # Align timestamps across symbols
)

# Cache to HDF5 (recommended for repeated use)
data.to_hdf("my_data.h5")
data = vbt.HDFData.pull("my_data.h5")
```

**Access OHLCV columns**:
```python
close = data.get("Close")           # All symbols
btc_close = data.get("Close", "BTCUSDT")  # Single symbol (preferred over data.close["BTCUSDT"])
open_ = data.get("Open")
high = data.get("High")
low = data.get("Low")
volume = data.get("Volume")
```

**CHECKPOINT**: Verify `data.symbols` lists expected symbols and `data.index` covers expected date range.

### STEP 2: Build Indicators

```python
# TA-Lib indicators (most common)
rsi = vbt.talib("RSI").run(close, timeperiod=14)
bbands = vbt.talib("BBANDS").run(close, timeperiod=20, nbdevup=2, nbdevdn=2)
macd = vbt.talib("MACD").run(close)

# Access indicator outputs
rsi_values = rsi.rsi                  # RSI series
upper_band = bbands.upperband         # Bollinger upper band
macd_hist = macd.macdhist             # MACD histogram

# Fast single indicator (no factory wrapper, faster)
sma_20 = data.run("talib_func:sma", timeperiod=20)
sma_50 = data.run("talib_func:sma", timeperiod=50)

# Built-in indicators
hurst = vbt.HURST.run(data.close, method=["standard", "logrs"])
ols = vbt.OLS.run(data.get("Close", "BTCUSDT"), data.get("Close", "ETHUSDT"))

# Multi-timeframe indicator
mtf_sma = vbt.talib("SMA").run(data.close, timeperiod=14, timeframe=["1d", "1w", "1M"], skipna=True)

# Multi-parameter indicator (grid search over window values)
rsi_multi = vbt.RSI.run(close, window=list(range(8, 21)), wtype=["simple", "exp", "wilder"], param_product=True)
```

**CHECKPOINT**: Inspect indicator output shape: `rsi.rsi.shape`. For multi-param, check `rsi_multi.wrapper.columns` for parameter levels.

### STEP 3: Generate Signals

```python
# Crossover signals
entries = rsi.rsi.vbt.crossed_below(30)    # RSI crosses below 30 = buy
exits = rsi.rsi.vbt.crossed_above(70)      # RSI crosses above 70 = sell

# SMA crossover
entries = sma_20.vbt.crossed_above(sma_50)
exits = sma_20.vbt.crossed_below(sma_50)

# CRITICAL: Clean overlapping signals before portfolio construction
entries, exits = entries.vbt.signals.clean(exits)

# Forward-shift to avoid same-bar lookahead bias
entries = entries.vbt.signals.fshift()
exits = exits.vbt.signals.fshift()
```

**CHECKPOINT**: Verify `entries.sum()` and `exits.sum()` are non-zero and roughly balanced.

### STEP 4: Construct Portfolio

```python
# Basic signal-based backtest
pf = vbt.PF.from_signals(
    close=close,
    entries=entries,
    exits=exits,
    size=100,                        # Position size
    size_type="valuepercent100",     # 100 = 100% of equity
    fees=0.003,                      # 0.3% commission (crypto)
    init_cash=100_000,
    freq="1d",
)

# With stop losses and take profit
pf = vbt.PF.from_signals(
    close=close,
    entries=entries,
    exits=exits,
    direction="longonly",            # "longonly", "shortonly", "both"
    size=100,
    size_type="valuepercent100",
    fees=0.003,
    init_cash=100_000,
    sl_stop=0.05,                    # 5% stop loss
    tsl_stop=0.1,                    # 10% trailing stop
    tp_stop=0.2,                     # 20% take profit
    freq="1d",
)

# Long and short signals separately
pf = vbt.PF.from_signals(
    close=close,
    long_entries=long_entries,
    long_exits=long_exits,
    short_entries=short_entries,
    short_exits=short_exits,
    fees=0.003,
)

# Buy-and-hold benchmark
bm_pf = vbt.PF.from_holding(close=close, fees=0.003)
```

**Parameter sweep**:
```python
pf = vbt.PF.from_signals(
    close=close,
    entries=entries,
    exits=exits,
    direction=vbt.Param(["longonly", "shortonly", "both"]),
    sl_stop=vbt.Param([0.03, 0.05, 0.1]),
    tsl_stop=vbt.Param([0.05, 0.1]),
    size=100,
    size_type="valuepercent100",
    fees=0.003,
    init_cash=100_000,
)
```

**CHECKPOINT**: `pf.stats()` returns reasonable metrics. Check `pf.trades.count()` > 0.

### STEP 5: Analyze Results

```python
# Summary statistics
pf.stats()                               # Full stats for single backtest
pf.stats(per_column=True)                # Per-param-combo stats (for sweeps)
pf.returns_stats()                       # Return distribution stats

# Individual metrics
pf.total_return                          # Total return
pf.sharpe_ratio                          # Sharpe ratio
pf.max_drawdown                          # Maximum drawdown
pf.annualized_return                     # Annualized return

# Specific metrics for multi-param
pf.stats(["total_return", "total_trades", "win_rate", "expectancy"], agg_func=None)

# Trade analysis
pf.trade_history                         # Full trade record
pf.trades.count()                        # Number of trades
pf.trades.expectancy                     # Expected value per trade
pf.trades.profit_factor                  # Profit factor

# Dynamic metric access (for parameter analysis)
pf.deep_getattr("trades.expectancy")

# Date range analysis
pf.get_sharpe_ratio(sim_start="2023", sim_end="2024")
pf.returns_stats(settings=dict(sim_start="2023", sim_end="2024"))

# Visualization
pf.plot().show()                         # Full portfolio plot
pf.plot_value().show()                   # Equity curve
pf.plot_trade_signals().show()           # Entry/exit on price chart
pf.plot_allocations().show()             # Multi-asset allocation
pf.sharpe_ratio.vbt.heatmap(            # Parameter heatmap
    x_level="sl_stop",
    y_level="tsl_stop",
    slider_level="direction",
).show()
pf.trades.plot_expanding_mfe_returns().show()  # MFE analysis
pf.trades.plot_running_edge_ratio().show()     # Edge ratio
```

**CHECKPOINT**: Compare `pf.sharpe_ratio` to `bm_pf.sharpe_ratio` (buy-and-hold) to validate strategy alpha.

## Loading Data from ClickHouse (project pattern)

In this project, data is loaded from ClickHouse via `DataManager`, NOT from
VBT Pro's built-in `BinanceData` or `YFData` directly. The `DataManager`
queries ClickHouse and wraps the result in `vbt.Data.from_data()`:

```python
from data_manager import DataManager

dm = DataManager()  # reads .env for ClickHouse credentials
data = dm.load("BTCUSDT", "1d", start="2020-01-01", end="2024-12-31")
close = data.get("Close", "BTCUSDT")

# From here, use close with VBT Pro as normal:
entries = close.vbt.crossed_above(close.ewm(span=200).mean())
```

VBT Pro's `BinanceData.pull()` and `YFData.pull()` are used ONLY inside
`DataManager.initialize()` for the initial data fetch. All subsequent
access goes through ClickHouse.

## Anti-Patterns Checklist

- [ ] **Missing `.vbt.signals.clean()`** — Overlapping signals cause silent position corruption
- [ ] **Missing `fees`** — Zero-fee backtests give unrealistically good results
- [ ] **Manual for-loops instead of `vbt.Param()`** — 10-100x slower, loses vectorized broadcasting
- [ ] **Missing `.vbt.signals.fshift()`** — Same-bar execution creates lookahead bias
- [ ] **`data.close["SYMBOL"]`** — Builds close for ALL symbols first. Use `data.get("Close", "SYMBOL")` instead
- [ ] **`vbt.Param()` mixing None with numeric** — Cannot mix None and numbers in one Param. Split into two runs: one without the stop, one with numeric stop values
- [ ] **`param_product=True` without `vbt.Param()`** — Deprecated pattern. Use `vbt.Param()` with named params instead
- [ ] **Large parameter grids without `_random_subset`** — Memory explosion. Use `_random_subset=N` or `broadcast_kwargs=dict(random_subset=N)` for large grids
- [ ] **Forgetting `per_column=True` in stats** — `pf.stats()` on a multi-param portfolio aggregates everything. Use `pf.stats(per_column=True)` to get per-combo metrics
- [ ] **Using `vbt.Portfolio.from_signals()`** — Works but verbose. Use `vbt.PF.from_signals()` as the canonical short form
- [ ] **`sim_start` without `rec_sim_range=True`** — Returns may still be influenced by positions opened before `sim_start`. Use `rec_sim_range=True` for strict date isolation
- [ ] **Running large sweeps without execution engine** — Add `execute_kwargs=dict(engine="threadpool", n_chunks="auto")` for parallel execution

## Reference Documents

Read these when the task requires deeper API knowledge:

- **`references/data-and-indicators.md`** — Data providers, Data object API, custom Indicator Factory (IF), IF.from_expr(), numba-compiled indicators, multi-timeframe, indicator search, data persistence
- **`references/backtesting-and-signals.md`** — Signal generation patterns, PF.from_signals() full parameter reference, PF.from_orders() for DCA, multi-asset portfolios, stats extraction, trade analysis, numba-level simulation
- **`references/optimization-and-walkforward.md`** — vbt.Param() deep dive, @vbt.parameterized decorator, Splitter API, walk-forward validation, purged K-fold CV, mono-chunks, execution engines, @vbt.cv_split
- **`references/advanced-patterns.md`** — Settings, pair trading, portfolio optimization (PFO), pattern recognition, signal detection, Renko, file utilities, Timer, ProgressBar, column operations

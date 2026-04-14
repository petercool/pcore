# Optimization & Walk-Forward Reference

## vbt.Param() Deep Dive

### Basic Usage

```python
# In PF.from_signals() — creates Cartesian product of all Param values
pf = vbt.PF.from_signals(
    close=close,
    entries=entries,
    exits=exits,
    direction=vbt.Param(["longonly", "shortonly", "both"]),
    sl_stop=vbt.Param([0.03, 0.05, 0.1]),
    tsl_stop=vbt.Param([0.05, 0.1]),
    fees=0.003,
)
# Creates 3 x 3 x 2 = 18 parameter combinations

# Named parameters (for better column labels)
entries = rsi.vbt.crossed_below(vbt.Param(list(range(20, 31)), name="lower_th"))
```

### Conditional Parameters

```python
# Filter: only combos where fast < slow
entries, exits = get_signals(
    vbt.Param(fast_sma, condition="__fast__ < __slow__"),
    vbt.Param(slow_sma),
)

# Filter: only combos where window gap >= 5
entries, exits = ma_crossover_signals(
    data,
    vbt.Param(np.arange(5, 50), condition="slow_window - fast_window >= 5"),
    vbt.Param(np.arange(5, 50)),
)

# Filter: avoid self-comparisons (pair trading)
coint_pvalues = coint_pvalue(
    data.close,
    vbt.Param(data.symbols, condition="s1 != s2"),
    vbt.Param(data.symbols),
)
```

### Random Subset (Large Grids)

```python
# Random search from large parameter space
pf = vbt.PF.from_random_signals(
    data,
    n=10,
    sl_stop=vbt.Param(np.arange(1, 100) / 100),
    tsl_stop=vbt.Param(np.arange(1, 100) / 100),
    tp_stop=vbt.Param(np.arange(1, 100) / 100),
    broadcast_kwargs=dict(random_subset=100, seed=42),  # Only 100 random combos
)
```

### Param Level Control

```python
# Control which params form products vs zip together
param_product = vbt.combine_params(
    dict(
        fast_window=vbt.Param(fast_windows, level=0),     # Level 0: zip together
        slow_window=vbt.Param(slow_windows, level=0),     # Level 0: zip together
        signal_window=vbt.Param(signal_windows, level=1), # Level 1: product with level 0
        wtype=vbt.Param(window_types, level=2),            # Level 2: product with levels 0,1
    ),
    random_subset=1_000,
    build_index=False,
)
```

### Mixing None with Numeric (Split Run Pattern)

```python
# CANNOT do: vbt.Param([None, 0.05, 0.1]) — None and numbers don't mix
# SOLUTION: Split into two runs

# Run 1: Without trailing stop
pf_no_tsl = vbt.PF.from_signals(
    close=close, entries=entries, exits=exits,
    sl_stop=vbt.Param([0.03, 0.05, 0.1]),
    # No tsl_stop parameter at all
    fees=0.003,
)

# Run 2: With trailing stop values
pf_with_tsl = vbt.PF.from_signals(
    close=close, entries=entries, exits=exits,
    sl_stop=vbt.Param([0.03, 0.05, 0.1]),
    tsl_stop=vbt.Param([0.05, 0.1]),
    fees=0.003,
)
```

## @vbt.parameterized Decorator

### Basic Usage

```python
@vbt.parameterized(merge_func="column_stack")
def get_signals(fast_sma, slow_sma):
    entries = fast_sma.crossed_above(slow_sma)
    exits = fast_sma.crossed_below(slow_sma)
    return entries, exits

entries, exits = get_signals(
    vbt.Param(fast_sma),
    vbt.Param(slow_sma),
)
```

### With Parallel Execution

```python
@vbt.parameterized(
    merge_func="concat",
    engine="threadpool",        # "threadpool", "pathos", "dask", "processpool"
    distribute="chunks",        # Distribute chunks across workers
    n_chunks="auto",            # Auto = number of CPU cores
)
def coint_pvalue(close, s1, s2):
    import statsmodels.tsa.stattools as ts
    return ts.coint(np.log(close[s1]), np.log(close[s2]))[1]
```

### merge_func Options

| Value | Use Case |
|-------|----------|
| `"column_stack"` | Returns that have matching indices (signals, DataFrames) |
| `"concat"` | Returns that are scalars or Series with different indices |

### With Random Subset

```python
@vbt.parameterized(merge_func="concat")
def test_combination(data, n, sl_stop, tsl_stop, tp_stop):
    return data.run("from_random_signals", n=n, sl_stop=sl_stop, tsl_stop=tsl_stop, tp_stop=tp_stop).total_return

test_combination(
    data,
    n=vbt.Param(np.arange(10, 100)),
    sl_stop=vbt.Param(np.arange(1, 1000) / 1000),
    tsl_stop=vbt.Param(np.arange(1, 1000) / 1000),
    tp_stop=vbt.Param(np.arange(1, 1000) / 1000),
    _random_subset=10,                          # Only test 10 random combos
)
```

### Parameterized Pipeline (Bollinger Bands Example)

```python
@vbt.parameterized(merge_func="concat")
def bbands_sharpe(data, timeperiod=14, nbdevup=2, nbdevdn=2, thup=0.3, thdn=0.1):
    bb = data.run("talib_bbands", timeperiod=timeperiod, nbdevup=nbdevup, nbdevdn=nbdevdn)
    bandwidth = (bb.upperband - bb.lowerband) / bb.middleband
    entries = (data.low < bb.lowerband) & (bandwidth > thup)
    exits = (data.high > bb.upperband) & (bandwidth < thdn)
    pf = vbt.PF.from_signals(data, entries, exits)
    return pf.sharpe_ratio

bbands_sharpe(
    data,
    nbdevup=vbt.Param([1, 2]),
    nbdevdn=vbt.Param([1, 2]),
    thup=vbt.Param([0.4, 0.5]),
    thdn=vbt.Param([0.1, 0.2]),
)
```

## Mono-Chunks (Numba + Parallel)

For maximum performance with numba-compiled functions:

```python
@vbt.parameterized(
    merge_func="concat",
    mono_chunk_len=100,           # 100 param values per array (one chunk)
    chunk_len="auto",             # Auto-split chunks across threads
    engine="threadpool",
    warmup=True,                  # Compile numba once before parallel execution
)
@njit(nogil=True)
def test_stops_nb(close, entries, exits, sl_stop, tp_stop):
    sim_out = vbt.pf_nb.from_signals_nb(
        target_shape=(close.shape[0], sl_stop.shape[1]),
        group_lens=np.full(sl_stop.shape[1], 1),
        close=close,
        long_entries=entries,
        short_entries=exits,
        sl_stop=sl_stop,
        tp_stop=tp_stop,
        save_returns=True,
    )
    return vbt.ret_nb.total_return_nb(sim_out.in_outputs.returns)

# Param with mono_merge_func for proper array stacking
results = test_stops_nb(
    vbt.to_2d_array(data.close),
    vbt.to_2d_array(entries),
    vbt.to_2d_array(exits),
    sl_stop=vbt.Param(np.arange(0.01, 1.0, 0.01), mono_merge_func=np.column_stack),
    tp_stop=vbt.Param(np.arange(0.01, 1.0, 0.01), mono_merge_func=np.column_stack),
)
```

## Splitter API

### Rolling Window Splitter

```python
splitter = vbt.Splitter.from_rolling(
    data.index,
    length=365,                  # Total window length (days)
    split=0.5,                   # 50% train, 50% test
    set_labels=["train", "test"],
    freq="daily",
)
splitter.plots().show()
```

### Time-Range Splitter

```python
splitter = vbt.Splitter.from_ranges(
    index=data.index,
    every="M",                   # Monthly splits
)

# Quarterly splits
splitter = vbt.Splitter.from_ranges(
    index=data.index,
    every="Q",
)
```

### Purged K-Fold Cross-Validation

```python
splitter = vbt.Splitter.from_purged_kfold(
    vbt.date_range("2020", "2024"),
    n_folds=10,
    n_test_folds=2,
    purge_td="3 days",          # Gap between train and test (prevent leakage)
    embargo_td="3 days",        # Additional gap after test
)
splitter.plots().show()
```

### Grouper-Based Splitter

```python
# Split by quarter
splitter = vbt.Splitter.from_grouper(data.index, by="Q")
```

## Cross-Validation Decorators

### @vbt.cv_split — Full CV Pipeline

```python
@vbt.cv_split(
    splitter="from_rolling",
    splitter_kwargs=dict(length=365, split=0.5, set_labels=["train", "test"]),
    takeable_args=["data"],                    # Which args get split by the splitter
    parameterized_kwargs=dict(random_subset=100),
    merge_func="concat",
)
def sma_crossover_cv(data, fast_period, slow_period, metric):
    fast_sma = data.run("sma", fast_period, hide_params=True)
    slow_sma = data.run("sma", slow_period, hide_params=True)
    entries = fast_sma.real_crossed_above(slow_sma)
    exits = fast_sma.real_crossed_below(slow_sma)
    pf = vbt.PF.from_signals(data, entries, exits, direction="both")
    return pf.deep_getattr(metric)             # Dynamic metric access

results = sma_crossover_cv(
    vbt.YFData.pull("BTC-USD", start="4 years ago"),
    vbt.Param(np.arange(20, 50), condition="x < slow_period"),
    vbt.Param(np.arange(20, 50)),
    "trades.expectancy",
)
```

### @vbt.split — Simple Time-Period Splitting

```python
@vbt.split(
    splitter="from_grouper",
    splitter_kwargs=dict(by="Q"),
    takeable_args=["data"],
    merge_func="concat",
)
def get_quarter_return(data):
    return data.returns.vbt.returns.total()

quarterly_returns = get_quarter_return(data.loc["2024"])
```

## Execution Engines

| Engine | Best For | Notes |
|--------|----------|-------|
| `"threadpool"` | I/O-bound or numba-compiled functions | GIL-free with numba |
| `"pathos"` | CPU-bound Python functions | Uses multiprocessing |
| `"dask"` | Large distributed computations | Requires dask installed |
| `"processpool"` | CPU-bound Python functions | Standard multiprocessing |

```python
# Apply to indicator run
result = MyIndicator.run(
    data.close,
    window=np.arange(2, 200),
    param_product=True,
    execute_kwargs=dict(
        engine="threadpool",
        n_chunks="auto",
        show_progress=True,
    ),
)

# Apply to parameterized decorator
@vbt.parameterized(
    merge_func="concat",
    engine="threadpool",
    n_chunks="auto",
)
def my_pipeline(data, param1, param2):
    ...
```

## Heatmap Analysis of Sweep Results

```python
# 2D heatmap of Sharpe ratio
pf.sharpe_ratio.vbt.heatmap(
    x_level="st_period",
    y_level="st_multiplier",
    slider_level="symbol",           # Interactive slider
).show()

# Group by parameter for analysis
stats_df["Expectancy"].groupby("rsi_window").mean()
stats_df.sort_values(by="Expectancy", ascending=False).head()

# Select specific parameter levels
values = pf.deep_getattr("trades.expectancy")
values = values.vbt.select_levels("sl_stop")
grouped = values.groupby(values.index).median()
```

## Walk-Forward Validation Pattern

```python
def build_walk_forward_folds(index, min_train_bars=1260, oos_bars=252, embargo=5):
    """Build expanding-window walk-forward folds."""
    n_bars = len(index)
    folds = []
    start = min_train_bars
    while start + oos_bars <= n_bars:
        train_end = start - embargo
        val_start = start
        val_end = min(start + oos_bars, n_bars)
        folds.append({
            "fold_id": len(folds) + 1,
            "train_slice": slice(0, train_end),
            "test_slice": slice(val_start, val_end),
        })
        start += oos_bars
    return folds

# Apply to backtesting
for fold in folds:
    train_close = close.iloc[fold["train_slice"]]
    test_close = close.iloc[fold["test_slice"]]
    train_entries = entries.iloc[fold["train_slice"]]
    test_entries = entries.iloc[fold["test_slice"]]
    # ... run backtest on each fold
```

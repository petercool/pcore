# Advanced Patterns Reference

## Settings & Configuration

```python
import vectorbtpro as vbt

# Dark theme for all plots
vbt.settings.set_theme("dark")

# Set default frequency for wrapping
vbt.settings["wrapping"]["freq"] = "1D"

# Default parameter values (overridable by Param)
fast_sma = vbt.talib("SMA").run(data.close, vbt.Default(5)).real
slow_sma = vbt.talib("SMA").run(data.close, vbt.Default(10)).real
```

## data.run() — Universal Execution

`data.run()` is VBT Pro's most versatile API. It runs indicators, portfolio methods, and TA-Lib functions through a unified interface.

```python
# Run TA-Lib indicator
sma = data.run("talib:sma", timeperiod=20)
bbands = data.run("talib_bbands", timeperiod=20, nbdevup=2, nbdevdn=2)

# Run fast TA-Lib (no IF wrapper)
sma = data.run("talib_func:sma", timeperiod=20)

# Run built-in portfolio method
bm_pf = data.run("from_holding")

# Run ALL TA-Lib indicators (for ML features)
features = data.run("talib", mavp=vbt.run_arg_dict(periods=14))

# Run custom IF
long_entries, short_entries = data.run(
    MyCustomIndicator,
    window=np.arange(5, 50),
    param_product=True,
    random_subset=1000,
    seed=42,
    unpack=True,                    # Return outputs directly, not IF instance
)

# Run with multi-timeframe
mtf_sma = data.run("talib:sma", timeperiod=14, timeframe=["1d", "1w", "1M"])

# Run built-in indicators
hurst = data.run("hurst", method="standard")
pivot = data.run("pivotinfo", up_th=0.3, down_th=0.2)
sumcon = data.run("sumcon", smooth=10)

# Run with hidden params (cleaner column names)
fast_sma = data.run("sma", 10, hide_params=True)

# Generate random signals
entries, exits = data.run("randnx", n=10, hide_params=True, unpack=True)
```

## Portfolio Optimization (PFO)

### From Allocation Function

```python
symbol_wrapper = data.get_symbol_wrapper(freq="1d")

# Custom allocation function
def equal_weight_func():
    n = len(symbol_wrapper.columns)
    return np.full(n, 1.0 / n)

pfo = vbt.PortfolioOptimizer.from_allocate_func(
    wrapper=symbol_wrapper,
    allocate_func=equal_weight_func,
    every="M",                      # Rebalance monthly
)

# Access results
pfo.allocations                     # Sparse allocation points
pfo.filled_allocations              # Forward-filled allocations
pfo.alloc_records.records_readable  # Human-readable records
pfo.stats()
pfo.plot().show()

# Simulate portfolio from optimizer
pf = vbt.Portfolio.from_optimizer(close=data, optimizer=pfo, freq="1d")
# Or shorthand:
pf = pfo.simulate(data, freq="1d")
```

### From Random Allocations

```python
pfo = vbt.PortfolioOptimizer.from_random(
    wrapper=symbol_wrapper,
    every="W",                      # Weekly rebalance
)
```

### From Custom Allocations

```python
custom_alloc = pd.DataFrame(
    [[0.5, 0.2, 0.3], [0.3, 0.4, 0.3], [0.2, 0.5, 0.3]],
    index=pd.date_range("2020-01-01", periods=3, freq="Q"),
    columns=symbol_wrapper.columns,
)
pfo = vbt.PortfolioOptimizer.from_allocations(wrapper=symbol_wrapper, allocations=custom_alloc)
```

### From Optimize Function (Lookback-Based)

```python
def inv_rank_optimize_func(price):
    ret = (price.iloc[-1] - price.iloc[0]) / price.iloc[0]
    ranks = ret.rank(ascending=False)
    return ranks / ranks.sum()

pfo = vbt.PortfolioOptimizer.from_optimize_func(
    symbol_wrapper,
    inv_rank_optimize_func,
    vbt.Takeable(data.get("Close")),   # Auto-sliced by index range
    every="M",
    lookback_period="3M",              # 3-month lookback window
)
```

### Template-Based Allocation

```python
# Use vbt.Rep() for template substitution
def rotation_func(wrapper, i):
    weight = np.full(len(wrapper.columns), 0)
    weight[i % len(wrapper.columns)] = 1
    return weight

pfo = vbt.PortfolioOptimizer.from_allocate_func(
    symbol_wrapper,
    rotation_func,
    vbt.Rep("wrapper"),                # Substituted with actual wrapper
    vbt.Rep("i"),                      # Substituted with iteration index
    every="M",
)

# Or with RepEval for expression evaluation
pfo = vbt.PortfolioOptimizer.from_allocate_func(
    symbol_wrapper,
    my_func,
    vbt.RepEval("wrapper.columns"),
    vbt.RepEval("wrapper.columns[i % len(wrapper.columns)]"),
    every="M",
)
```

### PyPortfolioOpt Integration

```python
pfo = vbt.PFO.from_pypfopt(
    returns=data.returns,
    optimizer="hrp",                   # Hierarchical Risk Parity
    target="optimize",
    every="M",
)
pfo.plot().show()
```

### Riskfolio-Lib Integration

```python
pfo = vbt.PFO.from_riskfolio(
    returns=data.close.vbt.to_returns(),
    port_cls="hc",                     # Hierarchical clustering
    every="M",
)
pfo.plot().show()
```

### Parameterized Optimization

```python
pfo = vbt.PortfolioOptimizer.from_allocate_func(
    symbol_wrapper,
    my_allocate_func,
    vbt.Param([[0.5, 0.3, 0.2], [0.3, 0.4, 0.3]], keys=pd.Index(["w1", "w2"]), name="weights"),
    every=vbt.Param(["1M", "2M", "3M"]),
)

pf = pfo.simulate(data, freq="1d")
pf.total_return                        # Returns for each param combo
pfo[("3M", "w2")].stats()             # Stats for specific combo
```

## Pair Trading Pattern

```python
import scipy.stats as st

# 1. Find cointegrated pairs
@vbt.parameterized(merge_func="concat", engine="pathos", distribute="chunks", n_chunks="auto")
def coint_pvalue(close, s1, s2):
    import statsmodels.tsa.stattools as ts
    return ts.coint(np.log(close[s1]), np.log(close[s2]))[1]

pvalues = coint_pvalue(
    data.close,
    vbt.Param(data.symbols, condition="s1 != s2"),
    vbt.Param(data.symbols),
)

# 2. Rolling OLS for spread
S1, S2 = "ALGOUSDT", "QTUMUSDT"
WINDOW = 24 * 30
UPPER = st.norm.ppf(1 - 0.05 / 2)
LOWER = -UPPER

ols = vbt.OLS.run(
    data.get("Close", S1),
    data.get("Close", S2),
    window=vbt.Default(WINDOW),
)

# 3. Generate signals from z-score
zscore = ols.zscore
upper_crossed = zscore.vbt.crossed_above(UPPER)
lower_crossed = zscore.vbt.crossed_below(LOWER)

# 4. Build paired long/short entries
long_entries = data.symbol_wrapper.fill(False)
short_entries = data.symbol_wrapper.fill(False)
short_entries.loc[upper_crossed, S1] = True
long_entries.loc[upper_crossed, S2] = True
long_entries.loc[lower_crossed, S1] = True
short_entries.loc[lower_crossed, S2] = True

# 5. Backtest
pf = vbt.PF.from_signals(
    close=data,
    entries=long_entries,
    short_entries=short_entries,
    size=10,
    size_type="valuepercent100",
    group_by=True,
    cash_sharing=True,
    call_seq="auto",
)
```

## Pattern Recognition & Projection

```python
# Find a custom pattern in price data
pattern_ranges = data.hlc3.vbt.find_pattern(
    pattern=[5, 1, 3, 1, 2, 1],       # Descending triangle
    window=100,
    max_window=700,
)

# Find recent pattern and project forward
pattern_ranges = data.hlc3.vbt.find_pattern(
    pattern=data.close[-7:],            # Last 7 bars as template
    rescale_mode="rebase",
)
delta_ranges = pattern_ranges.with_delta(7)   # 7-bar forward projection

fig = data.iloc[-7:].plot(plot_volume=False)
delta_ranges.plot_projections(fig=fig)
fig.show()
```

## Renko Charts

```python
renko_ohlc = data.close.vbt.to_renko_ohlc(1000, reset_index=True)
renko_ohlc.vbt.ohlcv.plot().show()
```

## File Utilities

```python
vbt.file_exists("data.h5")
vbt.remove_file("data.h5", missing_ok=True)
vbt.make_dir("output")
vbt.remove_dir("temp", with_contents=True, missing_ok=True)

# Save/load arbitrary objects (VBT Pro internal serialization)
vbt.save(any_object, "result.file")
loaded = vbt.load("result.file")
```

## Timer & Progress

```python
# Timer
with vbt.Timer() as timer:
    result = expensive_computation()
print(timer.elapsed())

# Progress bar
with vbt.ProgressBar(total=len(items)) as pbar:
    for item in items:
        process(item)
        pbar.set_prefix(f"Processing {item}")
        pbar.update()
```

## Column Operations & MultiIndex

```python
# Rename parameter levels in MultiIndex columns
sma = data.run("talib:sma", timeperiod=range(20, 50, 2))
fast_sma = sma.rename_levels({"sma_timeperiod": "fast"})
slow_sma = sma.rename_levels({"sma_timeperiod": "slow"})

# Select specific column from indicator
close_btc = indicator.select_col_from_obj(indicator.close, "BTCUSDT")

# Select specific levels from MultiIndex
values = pf.deep_getattr("trades.expectancy")
values = values.vbt.select_levels("sl_stop")

# ExceptLevel for grouping
pf = vbt.PF.from_signals(
    data,
    entries=entries,
    group_by=vbt.ExceptLevel("symbol"),   # Group by everything except symbol
    cash_sharing=True,
)

# Broadcasting
r = vbt.broadcast(dict(close=close, threshold=threshold))
result = r["close"].pct_change() >= r["threshold"]

# Convert to 2D array (for numba)
close_2d = vbt.to_2d_array(data.close)
entries_2d = vbt.to_2d_array(entries)

# Index range utilities
ms_points = data.wrapper.get_index_points(every="M")
data.wrapper.index[ms_points]

ranges = data.wrapper.get_index_ranges(every="M", lookback_period="3M")
```

## Plotting Utilities

```python
# Multi-panel subplots
fig = vbt.make_subplots(rows=2, cols=1, shared_xaxes=True)
data.plot(plot_volume=False, add_trace_kwargs=dict(row=1, col=1), fig=fig)
indicator.plot(add_trace_kwargs=dict(row=2, col=1), fig=fig)
fig.show()

# Secondary Y-axis
fig = vbt.make_subplots(specs=[[dict(secondary_y=True)]])
data.plot(plot_volume=False, fig=fig)
hurst.hurst.vbt.plot(fig=fig, add_trace_kwargs=dict(secondary_y=True))

# Signal markers on chart
entries.vbt.signals.plot_as_entries(price, fig=fig)
exits.vbt.signals.plot_as_exits(price, fig=fig)

# Mask ranges visualization
mask.vbt.ranges.plot_shapes(
    column=0.005,
    plot_close=False,
    add_shape_kwargs=dict(fillcolor="orange"),
    fig=fig,
)

# Stacked area chart (allocation visualization)
sim_alloc.vbt.plot(
    trace_kwargs=dict(stackgroup="one"),
    use_gl=False,
).show()

# TA-Lib indicator with built-in plot
vbt.talib("MACD").run(data.close).plot().show()
run_rsi = vbt.talib_func("rsi")
rsi = run_rsi(data.close, timeperiod=12)
plot_rsi = vbt.talib_plot_func("rsi")
plot_rsi(rsi).show()
```

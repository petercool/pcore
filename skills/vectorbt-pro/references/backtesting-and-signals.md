# Backtesting & Signals Reference

## Signal Generation Patterns

### Crossover Signals
```python
# Basic threshold crossover
entries = rsi.rsi.vbt.crossed_below(30)       # RSI crosses below 30 (oversold → buy)
exits = rsi.rsi.vbt.crossed_above(70)         # RSI crosses above 70 (overbought → sell)

# Moving average crossover
entries = fast_sma.vbt.crossed_above(slow_sma)
exits = fast_sma.vbt.crossed_below(slow_sma)

# NaN-safe crossovers (when indicators have gaps)
entries = fast_sma.vbt.crossed_above(slow_sma, dropna=True)
exits = fast_sma.vbt.crossed_below(slow_sma, dropna=True)

# Bollinger Bands signals
bb = data.run("bbands")
entries = data.hlc3.vbt.crossed_above(bb.upper) & (bb.bandwidth < 0.1)
exits = data.hlc3.vbt.crossed_below(bb.upper) & (bb.bandwidth > 0.5)

# Indicator state signals (e.g., SuperTrend direction)
entries = (~st.superl.isnull())       # Long signal when superl has a value
exits = (~st.supers.isnull())         # Short signal when supers has a value
```

### Signal Cleaning & Manipulation

```python
# CRITICAL: Clean overlapping signals before portfolio construction
entries, exits = entries.vbt.signals.clean(exits)

# Forward-shift signals to avoid same-bar lookahead
entries = entries.vbt.signals.fshift()
exits = exits.vbt.signals.fshift()

# Separate signal pairs into individual columns
entries, exits = entries.vbt.signals.unravel_between(exits, relation="anychain")

# Visualization
fig = rsi.plot()
entries.vbt.signals.plot_as_entries(rsi.rsi, fig=fig)
exits.vbt.signals.plot_as_exits(rsi.rsi, fig=fig)
fig.show()
```

### Multi-Parameter Signals with vbt.Param()

```python
# Named parameter signals
entries = rsi.vbt.crossed_below(vbt.Param(list(range(20, 31)), name="lower_th"))
exits = rsi.rsi_crossed_above(vbt.Param(list(range(70, 81)), name="upper_th"))

# Conditional parameters (fast < slow constraint)
entries, exits = get_signals(
    vbt.Param(fast_sma, condition="__fast__ < __slow__"),
    vbt.Param(slow_sma),
)
```

## Portfolio Construction

### PF.from_signals() — Full Parameter Reference

```python
pf = vbt.PF.from_signals(
    # Required
    close=close,                          # Close prices (Series, DataFrame, or Data object)

    # Signal inputs (choose one pair)
    entries=entries,                       # Boolean Series/DataFrame for long entries
    exits=exits,                          # Boolean Series/DataFrame for long exits
    # OR for separate long/short:
    long_entries=long_entries,
    long_exits=long_exits,
    short_entries=short_entries,
    short_exits=short_exits,

    # OHLC (optional, enables intra-bar stop execution)
    open=open_,
    high=high,
    low=low,

    # Position sizing
    size=100,                             # Size value
    size_type="valuepercent100",          # How to interpret size:
    #   "amount"          — absolute number of shares/units
    #   "value"           — dollar value
    #   "percent"         — percent of equity (0.0 to 1.0)
    #   "valuepercent100" — percent of equity (0 to 100)
    #   "targetpercent"   — target allocation (0.0 to 1.0)

    # Direction
    direction="longonly",                 # "longonly", "shortonly", "both"
    upon_opposite_entry="reverse",        # What to do on opposite signal:
    #   "ignore"  — ignore opposite signals
    #   "close"   — close current position
    #   "reverse" — reverse position (close + open opposite)

    # Accumulation
    accumulate="disabled",                # Position accumulation:
    #   "disabled" — one position at a time
    #   "addonly"  — can add to position, exit closes all
    #   "removeonly" — can reduce position, no adding
    #   "both"     — can add and partially reduce

    # Risk management
    sl_stop=0.05,                         # Stop loss (5% from entry)
    tsl_stop=0.1,                         # Trailing stop (10% from peak)
    tp_stop=0.2,                          # Take profit (20% from entry)
    delta_format="percent",               # "percent" (0.05 = 5%) or "percent100" (5 = 5%)
    stop_exit_price="close",              # "close" or "stop" (exact stop level)

    # Costs
    fees=0.003,                           # Commission per trade (0.3%)
    leverage=1.0,                         # Leverage multiplier

    # Capital
    init_cash=100_000,                    # Initial cash (or "auto" for infinite)
    freq="1d",                            # Data frequency

    # Multi-asset grouping
    group_by=True,                        # Group all assets as one portfolio
    # group_by=vbt.ExceptLevel("symbol"), # Group by all levels except symbol
    cash_sharing=True,                    # Share cash across grouped assets
    call_seq="auto",                      # Execute sells before buys in same bar

    # Simulation
    sim_start="auto",                     # Start sim at first signal (or datetime)
)
```

### PF.from_orders() — Manual Order Specification

```python
# DCA (Dollar-Cost Averaging)
pf = vbt.PF.from_orders(
    close=close,
    size=dca_sizes,                # Series with investment amount at each period
    size_type="value",             # Absolute dollar amount
    direction="longonly",
    fees=0.003,
    init_cash=100_000,
    freq="1d",
)

# Portfolio rebalancing
pf = vbt.PF.from_orders(
    close=data.get("Close"),
    size=filled_allocations,       # DataFrame of target allocations
    size_type="targetpercent",
    group_by=True,
    cash_sharing=True,
    call_seq="auto",
)
```

### Benchmarks

```python
# Buy-and-hold
bm_pf = vbt.PF.from_holding(close=close, fees=0.003)
bm_pf = vbt.PF.from_holding(close=close, bm_close=benchmark_close)  # With benchmark

# Random signals (statistical baseline)
rand_pf = vbt.PF.from_random_signals(data, n=10, seed=42)
rand_pf = vbt.PF.from_random_signals(
    data, n=10,
    sl_stop=vbt.Param(np.arange(1, 100) / 100),
    tp_stop=vbt.Param(np.arange(1, 100) / 100),
    broadcast_kwargs=dict(random_subset=100),  # Random search from grid
)

# Via data.run()
bm_pf = data.run("from_holding")
```

## Statistics & Analysis

### Stats Extraction

```python
# Full stats
pf.stats()                                   # Single backtest summary

# Per-column stats (for parameter sweeps)
stats_df = pf.stats(per_column=True)         # Each column = one param combo
returns_stats_df = pf.returns_stats(per_column=True)

# Selected metrics
pf.stats(["total_return", "total_trades", "win_rate", "expectancy"], agg_func=None)

# Key properties
pf.total_return                              # Total return (scalar or Series)
pf.sharpe_ratio                              # Sharpe ratio
pf.sortino_ratio                             # Sortino ratio
pf.max_drawdown                              # Max drawdown
pf.annualized_return                         # Annualized return
pf.calmar_ratio                              # Calmar ratio

# Equity curve
pf.value()                                   # Portfolio value over time
pf.plot_value().show()                       # Plot equity curve
pf.plot_cumulative_returns().show()          # Plot cumulative returns

# Date range analysis
pf.get_sharpe_ratio(sim_start="2023", sim_end="2024")
pf.get_sharpe_ratio(sim_start="2023", rec_sim_range=True)  # Strict isolation
pf.returns_stats(settings=dict(sim_start="2023", sim_end="2024"))

# Dynamic metric access (parameter analysis)
pf.deep_getattr("trades.expectancy")
pf.deep_getattr("trades.winning.pnl.mean")
```

### Trade Analysis

```python
# Trade records
pf.trade_history                             # Full trade record DataFrame
pf.trades.count()                            # Number of trades
pf.trades.expectancy                         # Expected value per trade
pf.trades.profit_factor                      # Profit factor
pf.trades.records_readable                   # Human-readable trade records

# Position analysis
pf.positions.returns                         # Per-position returns

# Trade visualization
pf.trades.plot().show()                      # Trade chart
pf.trades.plot_expanding_mfe_returns().show() # Maximum Favorable Excursion
pf.trades.plot_mae_returns().show()          # Maximum Adverse Excursion
pf.trades.plot_running_edge_ratio(
    trace_kwargs=dict(line_color="limegreen", name="Strategy"),
).show()
```

### Visualization

```python
# Portfolio plot (comprehensive)
pf.plot().show()
pf.plot_value().show()
pf.plot_trade_signals().show()
pf.plot_allocations().show()                 # Multi-asset allocation

# Parameter sweep heatmaps
pf.sharpe_ratio.vbt.heatmap(
    x_level="sl_stop",
    y_level="tsl_stop",
    slider_level="direction",
).show()

# General visualization
series.vbt.plot()                            # Line plot
series.vbt.heatmap()                         # Heatmap
series.vbt.ts_heatmap()                      # Time-series heatmap
series.vbt.barplot()                         # Bar chart
series.vbt.histplot()                        # Histogram

# Multi-panel figures
fig = vbt.make_subplots(rows=2, cols=1, shared_xaxes=True)
data.plot(plot_volume=False, add_trace_kwargs=dict(row=1, col=1), fig=fig)
indicator.plot(add_trace_kwargs=dict(row=2, col=1), fig=fig)
fig.show()

# Rebase prices (compare multiple assets starting from 100)
data.close.vbt.rebase(100).vbt.plot().show()

# Select and plot specific parameter combo
pf[(14, "wilder")].plot_value().show()
```

## Multi-Asset Portfolio Patterns

### Grouped Portfolio (Cash Sharing)

```python
# All assets share one cash pool
pf = vbt.PF.from_signals(
    close=data,
    entries=long_entries,
    short_entries=short_entries,
    size=10,
    size_type="valuepercent100",
    group_by=True,                           # Single group for all assets
    cash_sharing=True,
    call_seq="auto",                         # Sells before buys
)
```

### ExceptLevel Grouping (Parameter Sweep + Multi-Asset)

```python
# Group by parameter combo, keeping symbols separate within each group
pf = vbt.PF.from_signals(
    data,
    entries=entries,                          # Has MultiIndex columns: (param_combos, symbols)
    short_entries=exits,
    size=10,
    size_type="valuepercent100",
    group_by=vbt.ExceptLevel("symbol"),      # Group by everything EXCEPT symbol
    cash_sharing=True,
    call_seq="auto",
)
```

## Numba-Level Simulation (Maximum Performance)

```python
from numba import njit

@njit
def post_segment_func_nb(c):
    """Halt simulation if portfolio value drops to zero."""
    value = vbt.pf_nb.get_group_value_nb(c, c.group)
    if value <= 0:
        vbt.pf_nb.stop_group_sim_nb(c, c.group)

# Direct numba simulation (inside @vbt.parameterized with mono_chunks)
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
```

### OHLC-Native Simulation

```python
# Pass all OHLC for more realistic stop execution (intra-bar)
pf = vbt.PF.from_random_signals(
    open=data.open,
    high=data.high,
    low=data.low,
    close=data.close,
    n=10,
)
```

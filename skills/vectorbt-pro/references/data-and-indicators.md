# Data Loading & Indicator Reference

## Data Providers

### BinanceData
```python
# Single symbol
data = vbt.BinanceData.pull("BTCUSDT", start="2020-01-01 UTC", end="2024-12-31 UTC", timeframe="1d")

# Multiple symbols
data = vbt.BinanceData.pull(
    ["BTCUSDT", "ETHUSDT", "BNBUSDT"],
    start="2020-01-01 UTC",
    end="2024-12-31 UTC",
    timeframe="1h",
    missing_index="drop",       # Align timestamps across symbols
)

# List available symbols
symbols = vbt.BinanceData.list_symbols("*USDT")  # Wildcard search
```

### YFData (Yahoo Finance)
```python
data = vbt.YFData.pull(
    symbols=["SPY", "TLT", "XLF", "XLE"],
    start="2020",
    missing_index="drop",
)
```

### TVData (TradingView)
```python
data = vbt.TVData.pull(
    "AAPL",
    timeframe="1D",
    start="2020-01-01",
    end="2024-12-31",
)
```

### DuckDBData
```python
# Resolve connection
conn = vbt.DuckDBData.resolve_connection("path/to/data.duckdb", read_only=False)

# Pull data
data = vbt.DuckDBData.pull(symbols=["BTCUSDT_1d"], connection=conn)

# Save data to DuckDB
data.to_duckdb(connection=conn, table="symbol_timeframe", if_exists="replace")

conn.close()
```

### HDFData (HDF5 Cache)
```python
# Save
data.to_hdf("my_data.h5")

# Load
data = vbt.HDFData.pull("my_data.h5")

# Load with date filtering
data = vbt.HDFData.pull("my_data.h5", start="2023", end="2024", silence_warnings=True)
```

### Data from DataFrame
```python
# Wrap existing DataFrame as vbt.Data
data = vbt.Data.from_data({"BTCUSDT": df})  # df has OHLCV columns
```

## Data Object API

```python
# Access OHLCV
close = data.get("Close")                    # All symbols as DataFrame
close = data.get("Close", "BTCUSDT")         # Single symbol as Series (preferred)
open_ = data.get("Open")
high = data.get("High")
low = data.get("Low")
volume = data.get("Volume")

# Shorthand accessors
data.close          # Same as data.get("Close") — builds all symbols
data.open
data.high
data.low
data.volume
data.hlc3           # (High + Low + Close) / 3
data.hl2            # (High + Low) / 2

# Metadata
data.symbols        # List of symbol names
data.index          # DatetimeIndex
data.data           # Dict of DataFrames, keyed by symbol
data.stats()        # Data statistics summary
data.data["BTCUSDT"].info()  # Per-symbol info

# Filtering and combining
data.select(["BTCUSDT", "ETHUSDT"])           # Select subset of symbols
data.merge(other_data, missing_index="drop")  # Combine data objects
data.realign(new_index)                       # Align to custom index
data.returns                                   # Return series

# Symbol wrapper (for multi-asset portfolio construction)
symbol_wrapper = data.get_symbol_wrapper(freq="1d")
symbol_wrapper.fill(0.0)                      # Fill with value
symbol_wrapper.fill(False)                    # Fill with boolean
```

## Indicators

### TA-Lib Indicators (Most Common)

```python
# Standard TA-Lib via Indicator Factory (returns IF instance with named outputs)
rsi = vbt.talib("RSI").run(close, timeperiod=14)
rsi.rsi                                      # Access output

bbands = vbt.talib("BBANDS").run(close, timeperiod=20, nbdevup=2, nbdevdn=2)
bbands.upperband
bbands.middleband
bbands.lowerband

macd = vbt.talib("MACD").run(close)
macd.macd
macd.macdsignal
macd.macdhist

# Fast TA-Lib (no IF wrapper, faster for single indicators)
sma = data.run("talib_func:sma", timeperiod=20)   # Returns Series directly
rsi = data.run("talib_func:rsi", timeperiod=14)

# Run ALL TA-Lib indicators at once (useful for ML feature generation)
features = data.run("talib", mavp=vbt.run_arg_dict(periods=14))
features.shape
```

### Built-in Indicators

```python
# RSI with window types
rsi = vbt.RSI.run(close, window=14, wtype="wilder")  # "simple", "exp", "wilder"

# Hurst exponent (mean-reversion vs trend detection)
hurst = vbt.HURST.run(data.close, method=["standard", "logrs", "rs", "dma", "dsod"])

# Rolling OLS regression (pair trading)
ols = vbt.OLS.run(price_x, price_y, window=vbt.Default(720))
ols.error          # Spread
ols.zscore         # Z-score of spread

# Signal detection (anomaly detection in indicator output)
sigdet = vbt.SIGDET.run(series, factor=5)

# Bollinger Bands (built-in)
bb = data.run("bbands")
bb.upperband
bb.lowerband
bb.bandwidth

# Pivot detection
pivot_info = data.run("pivotinfo", up_th=0.3, down_th=0.2)

# WorldQuant Alpha 101
alpha1 = vbt.wqa101(1).run(data.close).out
```

### Indicator Search & Discovery

```python
# Search indicators by name pattern
vbt.IF.list_indicators("*ma")          # All moving averages
vbt.IF.list_indicators("*rsi*")        # All RSI variants

# Get indicator info
vbt.indicator("technical:ZLMA")        # Zero-Lag Moving Average

# Inline help for any function
vbt.phelp(vbt.talib("RSI").run)
vbt.phelp(vbt.PF.from_signals)
```

### Multi-Timeframe Indicators

```python
# Run SMA on multiple timeframes simultaneously
mtf_sma = vbt.talib("SMA").run(
    data.close,
    timeperiod=14,
    timeframe=["1d", "1w", "1M"],    # Daily, weekly, monthly
    skipna=True,
)
mtf_sma.real.vbt.ts_heatmap().show()

# Via data.run()
mtf_result = data.run("talib:sma", timeperiod=14, timeframe=["1d", "1w", "1M"])
```

### Multi-Parameter Indicators

```python
# Grid search over RSI parameters
rsi = vbt.RSI.run(
    close,
    window=list(range(8, 21)),           # 13 window values
    wtype=["simple", "exp", "wilder"],   # 3 window types
    param_product=True,                   # Cartesian product: 13 x 3 = 39 combos
)

# Access by specific parameter combo
rsi.rsi[(14, "wilder")]                  # RSI with window=14, wtype=wilder

# Inspect parameter columns
rsi.wrapper.columns                      # MultiIndex of parameter combos
```

## Custom Indicator Factory (IF)

### Basic IF with apply_func

```python
from numba import njit

# 1. Define the computation (numba for speed)
@njit(nogil=True)
def my_indicator_nb(close, window, threshold):
    result = np.full(close.shape, np.nan)
    for i in range(window, close.shape[0]):
        val = np.mean(close[i-window:i])
        result[i] = 1.0 if val > threshold else -1.0
    return result

# 2. Create the Indicator Factory
MyIndicator = vbt.IF(
    class_name="MyIndicator",
    short_name="mi",
    input_names=["close"],
    param_names=["window", "threshold"],
    output_names=["signal"],
).with_apply_func(
    my_indicator_nb,
    takes_1d=True,       # Function processes 1D arrays (per column)
    window=20,           # Default parameter values
    threshold=0.0,
)

# 3. Run
result = MyIndicator.run(close, window=[10, 20, 30], threshold=0.5, param_product=True)
result.signal

# 4. Help
vbt.phelp(MyIndicator.run)
```

### SuperTrend Example (Multi-Output)

```python
import talib
from numba import njit

@njit(nogil=True)
def supertrend_nb(close, upper, lower):
    trend = np.full(close.shape, np.nan)
    dir_ = np.full(close.shape, 1)
    long = np.full(close.shape, np.nan)
    short = np.full(close.shape, np.nan)
    for i in range(1, close.shape[0]):
        if close[i] > upper[i - 1]:
            dir_[i] = 1
        elif close[i] < lower[i - 1]:
            dir_[i] = -1
        else:
            dir_[i] = dir_[i - 1]
            if dir_[i] > 0 and lower[i] < lower[i - 1]:
                lower[i] = lower[i - 1]
            if dir_[i] < 0 and upper[i] > upper[i - 1]:
                upper[i] = upper[i - 1]
        if dir_[i] > 0:
            trend[i] = long[i] = lower[i]
        else:
            trend[i] = short[i] = upper[i]
    return trend, dir_, long, short

def supertrend_apply(high, low, close, period=7, multiplier=3):
    avg_price = talib.MEDPRICE(high, low)
    atr = talib.ATR(high, low, close, period)
    upper = avg_price + multiplier * atr
    lower = avg_price - multiplier * atr
    return supertrend_nb(close, upper, lower)

SuperTrend = vbt.IF(
    class_name="SuperTrend",
    short_name="st",
    input_names=["high", "low", "close"],
    param_names=["period", "multiplier"],
    output_names=["supert", "superd", "superl", "supers"],
).with_apply_func(supertrend_apply, takes_1d=True, period=7, multiplier=3)

st = SuperTrend.run(high, low, close, period=[5, 7, 10], multiplier=[2.0, 3.0], param_product=True)
```

### IF from Expression

```python
# Expression-based indicator (concise syntax)
expr = """
MACD:
fast_ema = @talib_ema(close, @p_fast_w)
slow_ema = @talib_ema(close, @p_slow_w)
macd = fast_ema - slow_ema
signal = @talib_ema(macd, @p_signal_w)
macd, signal
"""

MACD = vbt.IF.from_expr(expr, fast_w=12, slow_w=26, signal_w=9)
macd = MACD.run(data.close)
macd.macd
macd.signal

# Expression syntax:
# @talib_xxx       — call TA-Lib function
# @p_name          — parameter (becomes tunable)
# @in_close        — explicit input reference
# last line        — output names (comma-separated)
```

### Parallelized Custom Indicator

```python
@njit
def minmax_nb(close, window):
    return (
        vbt.nb.rolling_min_nb(close, window),
        vbt.nb.rolling_max_nb(close, window),
    )

MINMAX = vbt.IndicatorFactory(
    class_name="MINMAX",
    input_names=["close"],
    param_names=["window"],
    output_names=["min", "max"],
).with_apply_func(minmax_nb, window=14)

# Serial
minmax = MINMAX.run(data.close, np.arange(2, 200), jitted_loop=True)

# Multi-threaded (much faster for large grids)
minmax = MINMAX.run(
    data.close,
    np.arange(2, 200),
    jitted_loop=True,
    jitted_warmup=True,          # Compile once before parallelizing
    execute_kwargs=dict(
        engine="threadpool",
        n_chunks="auto",         # One chunk per CPU core
    ),
)
```

## Data Persistence

```python
# HDF5
data.to_hdf("data.h5")
data = vbt.HDFData.pull("data.h5")
data = vbt.Data.from_hdf("data.h5")     # Alternative

# DuckDB
conn = vbt.DuckDBData.resolve_connection("data.duckdb", read_only=False)
data.to_duckdb(connection=conn, table="btcusdt_1d", if_exists="replace")
data = vbt.DuckDBData.pull(symbols=["btcusdt_1d"], connection=conn)
conn.close()

# VBT Pro built-in save/load (uses internal serialization)
vbt.save(any_object, "result.file")
loaded = vbt.load("result.file")
```

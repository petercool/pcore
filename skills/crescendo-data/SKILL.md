---
name: crescendo-data
description: |
  Guide for connecting to and using Crescendo ClickHouse market data in any project.
  Crescendo provides OHLCV + whale/shark/lightsaber trading signals via a managed
  ClickHouse instance. Triggers when: crescendo, clickhouse, market data, whale signal,
  shark signal, lightsaber, trading signals, "fetch data from crescendo", "load market
  data", "connect to clickhouse", CrescendoData, tv_whale, tv_shark, OHLCV signals,
  whale_trade_event, LT_attr, ST_attr, vol_state, pivot_price.
---

# Crescendo Data

Crescendo is a managed ClickHouse time-series database providing OHLCV market
data enriched with proprietary trading signals from three independent systems:
**Whale** (long-term trend regime), **Shark** (short-term momentum/volume),
and **Lightsaber** (directional momentum oscillators). This skill guides
connection, data fetching, signal interpretation, and integration with
backtesting frameworks.

## Data sources (ClickHouse materialized views)

| MV name | System | Contents |
|---|---|---|
| `tv_whale_snapshot_latest_mv` | Whale | OHLCV + trend regime + trade events + pivot levels |
| `tv_shark_snapshot_latest_mv` | Shark | Momentum trade events + volume state |
| `tv_lightsaber_snapshot_latest_mv` | Lightsaber | Short-term + long-term momentum oscillators |
| `tv_symbol_info_latest_mv` | Metadata | Symbol catalog (type, sector, region, description) |

## Signal interpretation

### Whale — long-term trend regime detection

Whale signals identify **macro trend regime changes**. Think of Whale as
a trend-following system that classifies the market into bullish or bearish.

| Column | Type | Values | Meaning |
|---|---|---|---|
| `LT_attr` | **State** (not event) | `0` = bearish, `1` = bullish | Long-term trend regime. This is a continuous state that persists across bars — it is NOT a one-bar event. Use it as a trend filter. |
| `ST_attr` | **State** (discrete) | `0` = bullish, `1` = bearish | Short-term trend state — the fast counterpart to LT_attr. Note: **inverted polarity** vs LT_attr (0=bull here, 1=bull for LT_attr). |
| `whale_trade_event` | Discrete event | `100` = buy, `101` = sell, `0`/null = no event | Explicit whale trade signals — rare, high-conviction events. These fire at regime transitions. |
| `observe_event` | Discrete | numeric | Whale observation events — logged for monitoring, rarely used in entry/exit logic directly. |
| `pivot_price` | Price level | float | A dynamic support/resistance reference price from Whale analysis. Updated at trend transitions. Used for breakout/breakdown detection. |
| `pivot_attr` | Metadata | numeric | Attribution metadata for the pivot level (debugging/logging). |

**How to derive boolean signals from Whale:**

```python
# whale_long: TRUE on explicit buy events OR when LT_attr increases (trend turns bullish)
whale_long = (whale_trade_event == 100) | (LT_attr > LT_attr.shift(1))

# whale_short: TRUE on explicit sell events OR when LT_attr decreases (trend turns bearish)
whale_short = (whale_trade_event == 101) | (LT_attr < LT_attr.shift(1))

# whale_trend: the continuous state — use as a FILTER, not an entry signal
whale_trend = LT_attr  # 0 or 1
```

**Best practice**: take whale_long entries **only when whale_trend = 1** (bullish regime). This filters out counter-trend signals:

```python
entries = whale_long & (whale_trend == 1)
exits = whale_short & (whale_trend == 0)
```

### Shark — short-term momentum / volume extremes

Shark detects **intra-regime momentum extremes** and volume spikes. While
Whale identifies the trend, Shark times entries within it.

| Column | Type | Values | Meaning |
|---|---|---|---|
| `shark_trade_event` | Discrete event | `0` = long (momentum up), `1` = short (momentum down), null = no event | Short-term momentum signal — fires more frequently than whale events |
| `shark_st_attr` | Continuous | float | Shark short-term attribution score |
| `vol_state` | Discrete | `0` = vol extension (uptrend), `1` = vol retraction (uptrend), `2` = vol extension (downtrend), `3` = vol retraction (downtrend) | Volume-trend regime combining volume direction (extension/retraction) with price trend (up/down). Extension = volume expanding, retraction = volume contracting. |

**Boolean signals:**

```python
shark_long = (shark_trade_event == 0)
shark_short = (shark_trade_event == 1)
```

### Lightsaber — directional momentum oscillators

Lightsaber provides **continuous momentum readings** at two timeframes.
Unlike Whale/Shark (which produce boolean signals), Lightsaber values are
typically fed to **ML models as features**, not used directly for entry/exit.

| Column | Type | Values | Meaning |
|---|---|---|---|
| `st_signal` | Continuous | float | Short-term momentum oscillator. Direction and magnitude of recent price momentum. |
| `lt_signal` | Continuous | float | Long-term momentum oscillator. Smoothed directional momentum over a longer horizon. |

**Usage pattern**: feed as input features to neural network / ensemble models
rather than thresholding into boolean signals:

```python
# For ML models (e.g., TFT, LightGBM)
features["lightsaber_st"] = data.get("st_signal")
features["lightsaber_lt"] = data.get("lt_signal")

# If you must threshold (less common):
lightsaber_bullish = (st_signal > 0) & (lt_signal > 0)
```

### Pivot system — dynamic support / resistance

The pivot system tracks **adaptive breakpoint levels** that update at trend
transitions. This is NOT static support/resistance — it's a dynamic level
that the Whale system uses to detect regime-confirming breakouts.

**Usage pattern** (from production backtests):

```python
# Track pivot state with a numba-compiled loop
for i in range(1, len(close)):
    if current_trend == 1:  # Bullish
        if lt_attr[i] == 0:  # Trend just turned bearish
            current_pivot = pivot_price[i]  # Capture new reference level
    else:  # Bearish
        if close[i] > current_pivot:  # Price breaks above pivot
            current_trend = 1  # Confirm bullish reversal

# Entry/exit from pivot state changes
short_entries = active_flag.crossed_below(0.5)  # Trend flag 1 → 0
short_exits = active_flag.crossed_above(0.5)    # Trend flag 0 → 1
```

## Common signal combination patterns

From production backtests in `test-backtest-0`:

### Pattern 1: Whale + Trend confluence (most common)

```python
entries = whale_long & (whale_trend == 1)   # Buy signal + bullish regime
exits = whale_short & (whale_trend == 0)    # Sell signal + bearish regime
```

### Pattern 2: Whale + EMA confluence

```python
fast_ema_up = close > close.ewm(span=20).mean()
entries = whale_long & fast_ema_up
exits = whale_short & ~fast_ema_up
```

### Pattern 3: Whale + Shark confluence

```python
entries = whale_long & shark_long & (whale_trend == 1)
exits = whale_short | shark_short
```

### Pattern 4: Multi-signal ML features

```python
features = pd.DataFrame({
    "whale_trend": data.get("LT_attr"),
    "whale_st": data.get("ST_attr"),
    "shark_vol": data.get("vol_state"),
    "momentum_st": data.get("st_signal"),
    "momentum_lt": data.get("lt_signal"),
})
# Feed to LightGBM, TFT, etc.
```

## Connection setup

### Prerequisites

```bash
pip install clickhouse-connect pydantic-settings
# or
uv add clickhouse-connect pydantic-settings
```

### Environment variables

Create a `.env` file (gitignored) with ClickHouse credentials. See
`references/env-template` for the template. **Ask the team for the host
and password** — do not hardcode credentials in source code.

### Pydantic settings loader

```python
import os
from pydantic import Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class ClickhouseSettings(BaseSettings):
    host: str = Field(default="localhost")
    port: int = Field(default=8443)
    user: str = Field(default="default")
    password: SecretStr = Field(default="")
    database: str = Field(default="default")
    secure: bool = Field(default=True)

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        env_prefix="CLICKHOUSE_",
        case_sensitive=False,
    )
```

### Creating a client

```python
import clickhouse_connect


def get_clickhouse_client():
    settings = ClickhouseSettings()
    return clickhouse_connect.get_client(
        host=settings.host,
        port=settings.port,
        user=settings.user,
        password=settings.password.get_secret_value(),
        database=settings.database,
        secure=settings.secure,
    )
```

## Core queries

### Fetch OHLCV + all signals (primary query)

Joins all three MVs on (symbol, timestamp, timeframe):

```python
DATA_QUERY = """
WITH
    '{SYMBOL}' AS sym,
    '{TIMEFRAME}' AS tf,
    {LIMIT} AS d
SELECT
    w.symbol AS symbol, w.timestamp AS time, w.timeframe AS timeframe,
    w.open, w.high, w.low, w.close,
    w.LT_attr, w.ST_attr,
    w.trade_event AS whale_trade_event,
    w.observe_event, w.pivot_price, w.pivot_attr,
    s.trade_event AS shark_trade_event,
    s.st_attr AS shark_st_attr, s.vol_state,
    l.st_signal, l.lt_signal
FROM (
    SELECT * FROM tv_whale_snapshot_latest_mv
    WHERE symbol = sym AND timeframe = tf AND timestamp >= NOW() - INTERVAL d DAY
) AS w
LEFT JOIN (
    SELECT symbol, timestamp, timeframe, trade_event, st_attr, vol_state
    FROM tv_shark_snapshot_latest_mv
    WHERE symbol = sym AND timeframe = tf AND timestamp >= NOW() - INTERVAL d DAY
) AS s ON w.symbol = s.symbol AND w.timestamp = s.timestamp AND w.timeframe = s.timeframe
LEFT JOIN (
    SELECT symbol, timestamp, timeframe, st_signal, lt_signal
    FROM tv_lightsaber_snapshot_latest_mv
    WHERE symbol = sym AND timeframe = tf AND timestamp >= NOW() - INTERVAL d DAY
) AS l ON w.symbol = l.symbol AND w.timestamp = l.timestamp AND w.timeframe = l.timeframe
ORDER BY w.timestamp DESC;
"""

def get_data_query(symbol: str, timeframe: str, limit: int) -> str:
    return DATA_QUERY.format(SYMBOL=symbol, TIMEFRAME=timeframe, LIMIT=limit)
```

### List available symbols

```python
SYMBOL_INFO_QUERY = """
SELECT
    si.prefix, si.symbol, si.type, si.sector, si.industry, si.region,
    si.description, si.updated_at,
    ts.timeframe, ts.earliest_timestamp, ts.latest_timestamp
FROM tv_symbol_info_latest_mv AS si
LEFT JOIN (
    SELECT symbol, timeframe,
           MIN(timestamp) AS earliest_timestamp,
           MAX(timestamp) AS latest_timestamp
    FROM tv_whale_snapshot_latest_mv
    GROUP BY symbol, timeframe
) AS ts ON si.symbol = ts.symbol
ORDER BY si.symbol, ts.timeframe;
"""
```

## CrescendoData class (drop-in helper)

Copy this class into your project's `src/` or `utils/`:

```python
import functools
import time
from typing import Union, List

import clickhouse_connect
import pandas as pd


def retry_on_exception(retries: int = 2, delay: int = 5, backoff: int = 2):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            _retries, _delay = retries, delay
            for attempt in range(_retries + 1):
                try:
                    return func(*args, **kwargs)
                except Exception:
                    if attempt < _retries:
                        if args and hasattr(args[0], 'get_client'):
                            try:
                                args[0].client = args[0].get_client()
                            except Exception:
                                pass
                        time.sleep(_delay)
                        _delay *= backoff
                    else:
                        raise
        return wrapper
    return decorator


class CrescendoData:
    def __init__(self):
        self.settings = ClickhouseSettings()
        self.client = self.get_client()

    def get_client(self):
        return clickhouse_connect.get_client(
            host=self.settings.host,
            port=self.settings.port,
            user=self.settings.user,
            password=self.settings.password.get_secret_value(),
            database=self.settings.database,
            secure=self.settings.secure,
        )

    @retry_on_exception()
    def get_data(
        self,
        symbol: Union[str, List[str]] = "BTCUSDT",
        timeframe: Union[str, List[str]] = "1D",
        limit: int = 3000,
    ) -> dict[str, pd.DataFrame]:
        """Fetch OHLCV + signals. Returns {f'{symbol}_{timeframe}': DataFrame}.

        The DataFrame is time-indexed with float columns for OHLCV and all
        signal columns. Ready for vbt.Data.from_data() conversion.
        """
        symbols = [symbol] if isinstance(symbol, str) else symbol
        timeframes = [timeframe] if isinstance(timeframe, str) else timeframe
        dfs = []
        for sym in symbols:
            for tf in timeframes:
                try:
                    df = self.client.query_df(get_data_query(sym, tf, limit))
                    if df is not None and not df.empty:
                        dfs.append(df)
                except Exception:
                    continue
        if not dfs:
            return {}
        all_data = pd.concat(dfs, ignore_index=True)
        data_dict = {}
        for (sym, tf), group in all_data.groupby(["symbol", "timeframe"]):
            group = group.copy()
            group["time"] = pd.to_datetime(group["time"])
            group.drop(columns=["symbol", "timeframe"], inplace=True)
            group = group.set_index("time").astype(float)
            data_dict[f"{sym}_{tf}"] = group
        return data_dict

    @retry_on_exception()
    def get_symbol_info(self) -> pd.DataFrame:
        return self.client.query_df(SYMBOL_INFO_QUERY)

    @retry_on_exception()
    def query(self, query_str: str) -> pd.DataFrame:
        return self.client.query_df(query_str)
```

## Integration with VectorBT Pro

### Fetch and persist to DuckDB

```python
import vectorbtpro as vbt


def fetch_data_to_duckdb(
    symbol, timeframe, limit=3000, connection="data/market_data.duckdb",
):
    """Fetch from Crescendo and store in DuckDB for VBT Pro backtesting."""
    client = CrescendoData()
    data = client.get_data(symbol=symbol, timeframe=timeframe, limit=limit)
    data = vbt.Data.from_data(data)
    data.to_duckdb(connection=connection, if_exists="replace")
```

### Load back from DuckDB

```python
data = vbt.DuckDBData.pull("BTCUSDT_1D", connection="data/market_data.duckdb")
close = data.get("close")
whale_trend = data.get("LT_attr")
```

### Derive boolean trading signals for VBT Pro

```python
def crescendo_signals(data: vbt.Data) -> pd.DataFrame:
    """Convert raw Crescendo columns to boolean buy/sell signals.

    Returns a DataFrame with columns: whale_long, whale_short, whale_trend,
    shark_long, shark_short, observe_event, lightsaber_st, lightsaber_lt.
    """
    lt_attr = data.get("LT_attr")
    signals = {
        "whale_long": (data.get("whale_trade_event") == 100)
                      | (lt_attr > lt_attr.shift(1)),
        "whale_short": (data.get("whale_trade_event") == 101)
                       | (lt_attr < lt_attr.shift(1)),
        "whale_trend": lt_attr,                    # state: 0=bear, 1=bull
        "shark_long": data.get("shark_trade_event") == 0,
        "shark_short": data.get("shark_trade_event") == 1,
        "observe_event": data.get("observe_event"),
        "lightsaber_st": data.get("st_signal"),    # continuous momentum
        "lightsaber_lt": data.get("lt_signal"),    # continuous momentum
    }
    return pd.DataFrame(signals)
```

## Project setup checklist

1. Add `clickhouse-connect` and `pydantic-settings` to dependencies
2. Copy `references/env-template` to `.env` and fill in credentials (ask team)
3. Add `.env` and `data/*.duckdb` to `.gitignore`
4. Copy `ClickhouseSettings` + `CrescendoData` class into your `src/`
5. Use `fetch_data_to_duckdb()` for batch pulls
6. Use `crescendo_signals()` to derive boolean entries/exits
7. Combine with technical indicators (EMA, ATR) for confluence strategies

## Available instruments

Crypto pairs (BTCUSDT, ETHUSDT, ADAUSDT, etc.) and other instruments.
Timeframes vary by symbol — common ones are `1D`, `480m`, `60m`. Always
check via `CrescendoData().get_symbol_info()` first.

## Troubleshooting

| Problem | Cause | Fix |
|---|---|---|
| Connection refused / timeout | Wrong host or port | Verify `.env` values; port must be `8443` (TLS) |
| Empty results from `get_data` | Symbol or timeframe doesn't exist | Run `get_symbol_info()` to check availability |
| `Code: 60. Table does not exist` | MV name changed | Check `SHOW TABLES` on the ClickHouse instance |
| `SSL: CERTIFICATE_VERIFY_FAILED` | Missing CA certs | Set `secure=True` (uses system CA bundle) |
| Slow queries | Large `limit` on 1-minute data | Reduce limit or use a coarser timeframe |

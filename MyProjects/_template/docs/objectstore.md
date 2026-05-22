# {{STRATEGY_NAME}} - ObjectStore Schema

## Overview

This document describes the data persisted to ObjectStore during backtests.

**Namespace**: `{{objectstore_namespace}}/`

## Files

| File | Description |
|------|-------------|
| `{{objectstore_namespace}}/daily_snapshots.csv` | Daily portfolio metrics |
| `{{objectstore_namespace}}/positions.csv` | Position-level data |
| `{{objectstore_namespace}}/trades.csv` | Trade executions |

## Schema Stability

ObjectStore keys and column names should remain stable across backtests. When making changes:
- **Add** new columns at the end
- **Never** rename or remove existing columns
- **Document** changes in this file

## daily_snapshots.csv

Daily portfolio-level metrics.

| Column | Type | Description |
|--------|------|-------------|
| `date` | date | Trading date (YYYY-MM-DD) |
| `nav` | float | Net asset value |
| `cash` | float | Available cash |
| `gross_exposure` | float | (long + short) / nav |
| `net_exposure` | float | (long - short) / nav |
| `daily_pnl` | float | NAV change from previous day |
| `cumulative_pnl` | float | NAV - starting cash |
| `num_positions` | int | Count of active positions |

## positions.csv

Position-level data, one row per symbol per day.

| Column | Type | Description |
|--------|------|-------------|
| `date` | date | Trading date (YYYY-MM-DD) |
| `symbol` | string | Ticker symbol |
| `quantity` | float | Position quantity |
| `price` | float | Last price |
| `market_value` | float | quantity * price |
| `weight` | float | market_value / nav |
| `unrealized_pnl` | float | Current unrealized P&L |
| `avg_price` | float | Average entry price |

## trades.csv

Trade execution records.

| Column | Type | Description |
|--------|------|-------------|
| `date` | date | Trade date (YYYY-MM-DD) |
| `symbol` | string | Ticker symbol |
| `action` | string | BUY, SELL, CLOSE |
| `quantity` | float | Trade quantity |
| `price` | float | Execution price |
| `pnl` | float | Realized P&L (if closing) |

## Reading in Research Notebook

```python
from io import StringIO
import pandas as pd

# Initialize QuantBook
qb = QuantBook()

# Read daily snapshots
snapshots_str = qb.ObjectStore.Read("{{objectstore_namespace}}/daily_snapshots.csv")
df_snapshots = pd.read_csv(StringIO(snapshots_str), parse_dates=['date'])

# Read positions
positions_str = qb.ObjectStore.Read("{{objectstore_namespace}}/positions.csv")
df_positions = pd.read_csv(StringIO(positions_str), parse_dates=['date'])

# Read trades
trades_str = qb.ObjectStore.Read("{{objectstore_namespace}}/trades.csv")
df_trades = pd.read_csv(StringIO(trades_str), parse_dates=['date'])
```

## Adding New Output Files

When adding new ObjectStore outputs:

1. Add key to `domain/config.py`
2. Add logging method to `models/logger.py`
3. Document schema in this file
4. Update research notebook examples

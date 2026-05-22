"""
Configuration constants for {{STRATEGY_NAME}}.

Layer: ATOMS (pure constants, no dependencies)

Usage:
    from domain.config import *
"""

# === ObjectStore ===
OBJECTSTORE_NAMESPACE = "{{objectstore_namespace}}"

# === Backtest Defaults ===
DEFAULT_START_DATE = (2022, 1, 1)
DEFAULT_END_DATE = (2024, 1, 1)
DEFAULT_CASH = 100_000
DEFAULT_BENCHMARK = "SPY"

# === Strategy Parameters ===
# TODO: Add strategy-specific parameters

# Example: Signal parameters
# SIGNAL_LOOKBACK = 20
# SIGNAL_THRESHOLD = 0.05

# Example: Portfolio parameters
# MAX_POSITION_SIZE = 0.10  # 10% max per position
# TARGET_VOLATILITY = 0.10  # 10% annual volatility target
# MAX_GROSS_EXPOSURE = 1.0  # 100% max gross exposure

# Example: Execution parameters
# LIMIT_ORDER_OFFSET = 0.005  # 0.5% limit order offset

# {{STRATEGY_NAME}} - Strategy Logic

## Overview

{{STRATEGY_DESCRIPTION}}

## Strategy Type

- **Category**: {{STRATEGY_CATEGORY}}
- **Asset Class**: {{ASSET_CLASS}}
- **Holding Period**: {{HOLDING_PERIOD}}
- **Rebalance Frequency**: {{REBALANCE_FREQUENCY}}

## Universe

{{UNIVERSE_DESCRIPTION}}

## Signal Generation (Alpha Model)

### Parameters

| Parameter | Value | Description |
|-----------|-------|-------------|
| {{PARAM_1}} | {{VALUE_1}} | {{DESC_1}} |
| {{PARAM_2}} | {{VALUE_2}} | {{DESC_2}} |

### Logic

{{SIGNAL_LOGIC_DESCRIPTION}}

```
1. {{STEP_1}}
2. {{STEP_2}}
3. {{STEP_3}}
```

## Portfolio Construction

### Parameters

| Parameter | Value | Description |
|-----------|-------|-------------|
| Max Position Size | {{MAX_POS}}% | Maximum weight per position |
| Target Volatility | {{TARGET_VOL}}% | Portfolio volatility target |
| Max Gross Exposure | {{MAX_GROSS}}% | Maximum gross exposure |

### Constraint Order

1. {{CONSTRAINT_1}}
2. {{CONSTRAINT_2}}
3. {{CONSTRAINT_3}}

## Execution

### Order Types

- **Entry**: {{ENTRY_ORDER_TYPE}}
- **Exit**: {{EXIT_ORDER_TYPE}}

### Parameters

| Parameter | Value | Description |
|-----------|-------|-------------|
| {{EXEC_PARAM_1}} | {{EXEC_VALUE_1}} | {{EXEC_DESC_1}} |

## Risk Management

### Position Limits

- Max per position: {{MAX_POSITION}}%
- Max sector exposure: {{MAX_SECTOR}}%
- Max gross exposure: {{MAX_GROSS}}%

### Stop Loss / Take Profit

{{STOP_LOSS_DESCRIPTION}}

## Backtest Configuration

| Setting | Value |
|---------|-------|
| Start Date | {{START_DATE}} |
| End Date | {{END_DATE}} |
| Starting Cash | ${{STARTING_CASH}} |
| Benchmark | {{BENCHMARK}} |
| Warmup Period | {{WARMUP}} days |

## Strategy Invariants

These rules must not change without explicit approval:

1. {{INVARIANT_1}}
2. {{INVARIANT_2}}
3. {{INVARIANT_3}}

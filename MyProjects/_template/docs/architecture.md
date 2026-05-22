# {{STRATEGY_NAME}} - Architecture

## Overview

{{STRATEGY_DESCRIPTION}}

## Atomic Structure

```
{{PROJECT_NAME}}/
├── main.py                  # COMPOSITION ROOT
│                            # QCAlgorithm facade, wires models together
│
├── models/                  # ORGANISMS
│   ├── alpha.py             # Signal generation orchestrator
│   ├── portfolio.py         # Portfolio construction orchestrator
│   ├── execution.py         # Order execution orchestrator
│   └── logger.py            # ObjectStore logging facade
│
├── domain/                  # MOLECULES + ATOMS
│   ├── config.py            # Configuration constants (ATOMS)
│   ├── models.py            # DTOs, enums, protocols (ATOMS)
│   └── {{feature}}/         # Feature-specific business logic (MOLECULES)
│
└── docs/                    # Documentation
    ├── architecture.md      # This file
    ├── strategy.md          # Strategy logic details
    └── objectstore.md       # Data output schemas
```

## Layer Dependencies

```
┌─────────────────────────────────────────────────────────────┐
│                    COMPOSITION ROOT                          │
│                      (main.py)                               │
│         Can import: ALL layers                               │
└─────────────────────────┬───────────────────────────────────┘
                          │
┌─────────────────────────▼───────────────────────────────────┐
│                       ORGANISMS                              │
│                    (models/*.py)                             │
│         Can import: domain/, AlgorithmImports                │
└─────────────────────────┬───────────────────────────────────┘
                          │
┌─────────────────────────▼───────────────────────────────────┐
│                   MOLECULES + ATOMS                          │
│                    (domain/*.py)                             │
│         Can import: Python stdlib only                       │
└─────────────────────────────────────────────────────────────┘
```

## Key Design Decisions

### 1. {{DECISION_1_TITLE}}

{{DECISION_1_DESCRIPTION}}

### 2. {{DECISION_2_TITLE}}

{{DECISION_2_DESCRIPTION}}

## Data Flow

```
[Universe] → [Alpha Model] → [Portfolio Model] → [Execution Model]
                  ↓                  ↓                   ↓
              Insights           Targets              Orders
                  ↓                  ↓                   ↓
              [Logger] ←─────────────┴───────────────────┘
                  ↓
            [ObjectStore]
```

## Module Responsibilities

| Module | Layer | Responsibility |
|--------|-------|----------------|
| `main.py` | Root | Wire models, handle events |
| `models/alpha.py` | Organism | Generate trading signals |
| `models/portfolio.py` | Organism | Convert signals to targets |
| `models/execution.py` | Organism | Execute orders |
| `models/logger.py` | Organism | Persist data to ObjectStore |
| `domain/config.py` | Atom | Configuration constants |
| `domain/models.py` | Atom | DTOs, enums, protocols |

# Architecture

Projects in this workspace follow an atomic architecture.

## Layers

### Composition Root

The composition root wires the project together.

Responsibilities:

- Scheduling
- Event routing
- Dependency construction
- Top-level orchestration

### Models Layer

The models layer contains orchestration and domain coordination.

Responsibilities:

- Strategy coordination
- Signal orchestration
- Portfolio orchestration
- Risk orchestration

### Domain Layer

The domain layer contains reusable business logic.

Responsibilities:

- Calculations
- Validation
- DTOs
- Metrics
- Utilities
- Pure functions

## Goals

- Improve testability
- Reduce coupling
- Support reusable research
- Improve readability for students
- Enable AI-assisted development safely

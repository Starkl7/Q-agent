# Q-agent

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Contributions Welcome](https://img.shields.io/badge/contributions-welcome-brightgreen.svg)](CONTRIBUTING.md)
[![Security Policy](https://img.shields.io/badge/security-policy-blue.svg)](SECURITY.md)

Q-agent is an open-source teaching and research workspace for quantitative finance, QuantConnect, LEAN CLI workflows, and reproducible trading strategy development.

The project is designed for students, researchers, and practitioners who want to learn how professional quantitative research codebases are organized. It combines strategy scaffolding, agent guidelines, notebook workflows, dataset research ideas, and QuantConnect development practices in one workspace.

## What This Repository Is

This repository is a master workspace for:

- QuantConnect and LEAN CLI development
- Reproducible quantitative finance research
- Teaching students professional repository workflows
- Organizing research notebooks and strategy examples
- Building modular trading strategy prototypes
- Using AI coding agents safely and consistently

Individual strategy projects may live in their own repositories, while this repository provides the shared structure, documentation, templates, and workflow conventions.

## Who This Is For

- Masters students learning quantitative finance and systematic trading
- Students building public GitHub portfolios
- Researchers prototyping trading strategies
- Instructors teaching applied financial technology
- Developers learning QuantConnect and LEAN CLI workflows
- AI-assisted coding users who want a controlled project structure

## Repository Map

```text
Q-agent/
|-- README.md
|-- LICENSE
|-- CONTRIBUTING.md
|-- SECURITY.md
|-- CREDENTIALS.md
|-- AGENTS.md
|-- claude.md
|-- .env.example
|-- docs/
|   |-- getting-started.md
|   |-- project-map.md
|   |-- research-examples.md
|   |-- architecture.md
|   |-- release-checklist.md
|-- MyProjects/
|   |-- _template/
|   |-- .claude/agents/
|   |-- data/             # gitignored; populate via `lean init`
|   |-- storage/          # gitignored
|   |-- lean.json         # gitignored
|   |-- <ProjectName>/
|-- infrastructure/
|   |-- pipelines/        # crypto, edgar, polymarket, wrds, yfinance, ...
|-- References/
|   |-- books/
|   |-- papers/
|   |-- notes/
|   |-- repos/
|-- .github/
|   |-- pull_request_template.md
|   |-- workflows/
```

## Architecture Overview

Projects in this workspace follow an atomic structure:

```text
main.py
  |
  v
models/
  |
  v
domain/
  |
  v
pure functions, DTOs, config, validation, metrics
```

The goal is to keep the composition root thin, isolate orchestration logic, and place reusable business logic in testable modules.

See [docs/architecture.md](docs/architecture.md) for the full architecture guide.

## Quick Start

### 1. Clone the Repository

```bash
cd ~/Documents
git clone https://github.com/WolfpackOfOne/Q-agent.git Q-agent
cd Q-agent
```

### 2. Create a Python Environment

```bash
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install lean
```

### 3. Configure QuantConnect LEAN CLI

```bash
cd MyProjects
lean init
lean login
```

Do not commit `lean.json`, API keys, local credentials, or local data files.

### 4. Verify the Setup

```bash
lean --version
```

## Daily Workflow

```bash
cd ~/Documents/Q-agent
source venv/bin/activate
cd MyProjects
lean cloud push --project "<ProjectName>" --force
lean cloud backtest "<ProjectName>" --name "Description"
```

## Research Examples

This workspace is especially useful for projects that combine multiple data sources. Example research directions include:

- WRDS equity returns combined with EDGAR fundamentals
- WRDS equity returns combined with Piotroski F-Score metrics
- ETF constituent history combined with fund-level liquidity diagnostics
- Polymarket probabilities combined with crypto or ETF returns
- EDGAR fundamentals combined with profitability and quality signals
- QuantConnect backtest outputs combined with notebook-based risk analysis

See [docs/research-examples.md](docs/research-examples.md) for detailed project ideas.

## Documentation

| Document | Purpose |
|---|---|
| [docs/getting-started.md](docs/getting-started.md) | First-time setup and LEAN CLI configuration |
| [docs/project-map.md](docs/project-map.md) | Repository layout and responsibilities |
| [docs/research-examples.md](docs/research-examples.md) | Research project ideas |
| [docs/architecture.md](docs/architecture.md) | Atomic architecture guide |
| [docs/release-checklist.md](docs/release-checklist.md) | Public release checklist |
| [CREDENTIALS.md](CREDENTIALS.md) | All credentials/API keys used by the workspace |
| [CONTRIBUTING.md](CONTRIBUTING.md) | Contribution workflow |
| [SECURITY.md](SECURITY.md) | Security policy |

## Requirements

- Python 3.8 or later
- Git
- QuantConnect account
- LEAN CLI
- Docker Desktop for local backtests

## Open Source License

This project is released under the MIT License. See [LICENSE](LICENSE).

## Important Disclaimer

This repository is for education and research. Nothing in this repository is investment advice. Trading strategies can lose money, and backtests may not reflect live trading results.

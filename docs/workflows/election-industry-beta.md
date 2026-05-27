# Canonical Workflow: ElectionIndustryBeta

## Overview

`ElectionIndustryBeta` is the flagship end-to-end workflow inside Q-agent.

This workflow demonstrates:

```text
Polymarket pipeline
    ->
research notebook
    ->
signal generation
    ->
LEAN strategy
    ->
ObjectStore diagnostics
    ->
post-analysis
```

The project showcases:

- reproducible research
- atomic architecture
- reusable signals
- LEAN integration
- notebook-driven workflows
- AI-compatible quantitative development

---

# Workflow Stages

## 1. Pull Polymarket Data

The workflow begins with historical election probability data from Polymarket.

Example pipeline location:

```text
infrastructure/pipelines/polymarket/
```

Example command:

```bash
python infrastructure/pipelines/polymarket/pull_markets.py
```

---

## 2. Run the Research Notebook

Current notebook:

```text
infrastructure/marimo/notebooks/election_industry_returns.py
```

The notebook:

- loads ETF returns
- loads election probabilities
- computes rolling election betas
- ranks industry sensitivity
- validates signal behavior

---

## 3. Generate trump_prob.csv

The workflow generates:

```text
data/trump_prob.csv
```

This file becomes the deterministic signal input for LEAN.

Benefits:

- reproducible backtests
- environment-independent execution
- notebook/strategy separation
- no live API dependency during backtests

---

## 4. Run the LEAN Strategy

Main strategy:

```text
MyProjects/ElectionIndustryBeta/main.py
```

The strategy:

1. Pulls ETF return history
2. Computes rolling election betas
3. Ranks industries
4. Longs top-K industries
5. Shorts bottom-K industries
6. Logs diagnostics to ObjectStore

---

# Architecture

## Composition Root

```text
main.py
```

## Organisms

```text
models/
```

Examples:

- ElectionBetaAlpha
- ElectionBetaPortfolio
- MarketOrderExecutor
- PortfolioLogger

## Molecules and Atoms

```text
domain/
```

Examples:

- signals/
- config/
- models/

The signal logic lives in:

```text
domain/signals/election_beta.py
```

which links to:

```text
MyProjects/shared/signals/election_beta.py
```

This demonstrates reusable pure-Python signal architecture.

---

# Example LEAN Commands

## Local Backtest

```bash
lean backtest "ElectionIndustryBeta"
```

## Cloud Backtest

```bash
lean cloud backtest "ElectionIndustryBeta"
```

## Generate Report

```bash
lean report
```

---

# 5. Analyze ObjectStore Outputs

The strategy logs structured diagnostics including:

- trades
- positions
- exposures
- portfolio snapshots
- signal diagnostics

This enables notebook-driven post-analysis.

---

# 6. Review Diagnostics Notebook

Potential notebook locations:

```text
research/
infrastructure/marimo/notebooks/
```

Potential analyses:

- rolling Sharpe
- drawdowns
- sector concentration
- election sensitivity
- exposure diagnostics
- signal persistence

---

# Why This Workflow Matters

Most quantitative finance repositories fail to demonstrate a complete research lifecycle.

`ElectionIndustryBeta` connects:

```text
pipeline
    ->
research notebook
    ->
signal generation
    ->
LEAN strategy
    ->
ObjectStore diagnostics
```

This is the canonical Q-agent workflow.

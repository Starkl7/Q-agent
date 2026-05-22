<!--
claude_md:
  version: 2.0.0
  last_updated: 2026-04-02
  owners: [WolfpackOfOne]
  review_cadence: "monthly + after major architecture changes"
  changelog:
    - date: 2026-04-02
      change: "Full restructure per deep-research-report best practices"
    - date: 2026-03-30
      change: "Initial CLI reference version"
-->

# claude.md - QuantConnect Algorithm Workspace

## Purpose

Help Claude ship correct, safe algorithm changes in this QuantConnect LEAN workspace with minimal back-and-forth.

Success means:
- Changes are small and targeted to the request.
- Algorithms compile and backtest without errors.
- LEAN API gotchas are avoided proactively.
- No secrets or credentials are committed.

## Scope

Applies repo-wide. For project-specific rules, check `<ProjectName>/claude.md` or `<ProjectName>/docs/`.
Architecture guidelines live in `AGENTS.md`. Push detailed playbooks to skills rather than growing this file.

## Working style

- Be concise and direct.
- Prefer incremental steps; verify assumptions by reading code before suggesting changes.
- Ask clarifying questions only when blocked.
- For non-trivial changes, propose a brief plan before editing.

## Safety & guardrails

- Never introduce secrets (API keys, tokens, credentials) in code, logs, or docs.
- Never run destructive actions (dropping data, force-pushing, deleting projects) without explicit confirmation.
- Do not edit files inside `Lean/` (reference-only engine repo).
- Always activate the venv before running CLI commands: `source ~/Documents/Q-agent/venv/bin/activate`

---

## Project map

```
Q-agent/
├── venv/                    # Python virtual environment (activate first!)
├── Lean/                    # LEAN engine repo (reference only, do not edit)
├── AGENTS.md                # Architecture guidelines
├── claude.md                # This file
└── MyProjects/              # Algorithm projects
    ├── lean.json            # LEAN CLI configuration
    ├── data/                # Local market data
    ├── storage/             # ObjectStore outputs
    ├── shared/              # Reusable signal atoms (never pushed to QC)
    │   └── signals/         # Pure Python signal files — see shared/signals/README.md
    └── <ProjectName>/       # Individual projects
        ├── main.py          # Algorithm entry point
        ├── config.json      # Cloud/local IDs (DO NOT COMMIT)
        ├── models/          # Algorithm modules
        ├── domain/          # Business logic
        │   └── signals/     # Symlinks → shared/signals/ (see below)
        ├── docs/            # Documentation
        └── research/        # Jupyter notebooks
```

## Commands & environment

```bash
# Session setup
cd ~/Documents/Q-agent && source venv/bin/activate && cd MyProjects

# Cloud workflow
lean cloud push --project "<Project>" --force
lean cloud backtest "<Project>" --name "Test"
lean cloud pull --project "<Project>"

# Local workflow
lean backtest "<Project>"
lean research "<Project>"
```

Validation: `python -m py_compile main.py models/*.py`

## LEAN API gotchas

These are hard-won lessons. Follow them as imperative rules:

- **Always call `SetWarmUp` in `Initialize`** with the longest lookback the strategy needs. Omitting it means `IsReady` stays `False` and no trades fire until enough history accumulates organically.
- **`DateRules.MonthStart(n)` treats `n` as a Symbol, not a day offset.** Use `DateRules.MonthStart()` for the first trading day, or `DateRules.MonthStart("SPY", 5)` for a day offset.
- **Avoid the `SetAlpha` + `SetPortfolioConstruction` + coarse universe pattern** in teaching projects. Use direct `SetHoldings` calls in a `_rebalance` method instead.
- **Pyright warnings on LEAN PascalCase API are false positives.** `AlgorithmImports` resolves at runtime. Suppress with `# type: ignore` if needed; backtests compile fine.

## Shared signals library

`MyProjects/shared/signals/` is the canonical source for reusable signal atoms (pure Python, no `AlgorithmImports`). Projects consume them via symlinks — `lean cloud push` follows symlinks and uploads the file content, so QC cloud sees a normal file. `shared/` itself is never inside any project directory and is never pushed.

**One-time setup per project** (run from inside the project directory):
```bash
mkdir -p domain/signals
ln -s ../shared/signals/my_signal.py domain/signals/my_signal.py
```

**Rules:**
- Signal files in `shared/signals/` must be pure Python (no LEAN imports, no QC types)
- Edit `shared/signals/` — never the symlink copy inside a project
- All projects that need a signal get their own symlink; no project gets signals it doesn't use

## Coding conventions

- Never add `Co-Authored-By` tags to commit messages.
- Make the smallest correct change; avoid drive-by refactors.
- Do not add new dependencies without asking first.
- Keep changes localized to the task at hand.
- For new projects, use the `new-strategy-coder` agent (see `.claude/agents/new_strategy_coder.md`).
- Document all ObjectStore keys in `docs/objectstore.md`.

## Troubleshooting

| Error | Fix |
|---|---|
| `lean: command not found` | `source ~/Documents/Q-agent/venv/bin/activate` |
| `lean.json not found` | `cd ~/Documents/Q-agent/MyProjects` |
| collaboration lock | add `--force` to `lean cloud push` |
| `is not a Lean project` | directory has no `config.json` — use `lean project-create` |
| No data in local backtest | use cloud: `lean cloud backtest "<ProjectName>"` |
| Docker errors | make sure Docker Desktop is running |

## Data sources

- **Local (yfinance)**: Any ticker Yahoo Finance covers — free, no credentials. See `infrastructure/pipelines/yfinance/`. Run `python scripts/run_pipeline.py --tickers AAPL SPY` from that directory.
- **Local (WRDS/CRSP)**: Full 30-stock equity universe + SPY + SGOV daily data (1998-present). See `infrastructure/pipelines/wrds/claude.md`.
- **Local WRDS (additional entitlements)**: Broader access via `--profile <additional>` — adds OptionMetrics European options (full, 2002–2023, daily + tick) and IBES analyst earnings estimates (1980–2026, 35M rows). US options, RavenPack, 13F ownership, and short interest are denied. No extraction pipelines built yet for additional-entitlement sources.
- **Cloud**: Authoritative. Full equity history, options chains, alternative data. Use for final results.
- **New pipeline**: Use the `new-pipeline-coder` agent to add any new data source. It always outputs LEAN-format files.

## ObjectStore

- Write in algorithm: `self.ObjectStore.Save("namespace/file.csv", csv_string)`
- Read in notebook: `qb.ObjectStore.Read("namespace/file.csv")`

## Project Memory

This workspace uses hook-based memory in `.claude/memory/`.

Memory files:
- `.claude/memory/commands.md`
- `.claude/memory/lean-gotchas.md`
- `.claude/memory/data-pipelines.md`
- `.claude/memory/objectstore.md`
- `.claude/memory/decisions.md`
- `.claude/memory/teaching-style.md`

Do not store secrets in memory files.

When you discover a durable command, data source rule, LEAN gotcha, ObjectStore schema note, or decision, prefer updating the appropriate memory file instead of bloating this `claude.md`.

Automatic extraction writes candidates to `.claude/memory/pending.md`. Review that file manually before promoting entries to durable memory.

## Resources

- **Architecture guidelines**: `AGENTS.md`
- **New project bootstrap**: `.claude/agents/new_strategy_coder.md`
- **New data pipeline**: `.claude/agents/new-pipeline-coder.md`
- **LEAN CLI guide**: `MyProjects/.claude/agents/lean-cli.md`
- **GitHub sync**: `MyProjects/.claude/agents/github-sync.md`
- **References library**: `References/index.md` (books, repos, papers, notes)
- **QuantConnect docs**: https://www.quantconnect.com/docs

## Maintenance protocol

- If you discover a repeated mistake or missing context, propose a small update to this file.
- Prefer moving detailed playbooks into skills rather than growing this file.
- Keep this file under ~150 lines when possible.
- Path-specific rules belong in `.claude/rules/`, not here.

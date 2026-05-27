# MyProjects/shared/

Reusable, pure-Python atoms that any QuantConnect project in this workspace can consume — without copy-pasting code between projects.

This directory is **outside** every project's tree and is **never pushed to QuantConnect Cloud directly**. Projects consume its contents via relative symlinks inside their own `domain/signals/` directory. When `lean cloud push` walks the project, it follows the symlink and uploads the *content* — so QC Cloud sees a normal file, the local workspace sees a single source of truth.

## Layout

```
MyProjects/shared/
├── README.md             # This file
└── signals/              # Pure-Python signal atoms
    ├── __init__.py
    └── <signal_name>.py  # e.g. election_beta.py
```

## Authoring rules

A file in `shared/signals/` is a **pure Python atom**. Specifically:

- ✅ Allowed imports: stdlib, `pandas`, `numpy`, `scipy`.
- ❌ Forbidden imports: `AlgorithmImports`, anything QuantConnect-specific, anything project-specific.
- ✅ It must be importable and runnable in a plain `python` shell — no LEAN runtime needed.
- ✅ Functions, not classes-with-state. Signals are math, not lifecycle.
- ✅ Unit-testable: deterministic inputs in, deterministic outputs out. Add a synthetic-data sanity check before committing.

`shared/signals/election_beta.py` is the worked example — read it before authoring a new one.

## Consuming a shared signal from a project

From inside the project directory:

```bash
mkdir -p domain/signals
ln -s ../../../shared/signals/election_beta.py domain/signals/election_beta.py
```

### Why three `..`?

Symlink targets are resolved **relative to the symlink's location**, not the current working directory. The symlink lives at `<Project>/domain/signals/election_beta.py`, so to reach `MyProjects/shared/signals/election_beta.py`:

```
<Project>/domain/signals/  ← symlink lives here
        ../                ← out of signals/
        ../../             ← out of domain/
        ../../../          ← out of <Project>/   → MyProjects/
        ../../../shared/signals/election_beta.py  ✓
```

Two `..` resolves to `<Project>/domain/shared/...` — that path **does not exist** and you'll get a broken link with no error until import time.

### Verify the link

```bash
ls -la domain/signals/election_beta.py
# → election_beta.py -> ../../../shared/signals/election_beta.py

python -c "from domain.signals.election_beta import rolling_beta; print('ok')"
```

## Editing

- **Always edit the shared file**, never the symlink copy inside a project. Edits to the link silently modify the shared source — which affects every project that consumes it.
- Changing a function signature in a shared atom is a breaking change for every consumer. Grep the workspace first:
  ```bash
  grep -rn "from domain.signals.<name> import" MyProjects/
  ```

## Cloud push behaviour

`lean cloud push` follows symlinks when walking the project directory and uploads file *content* to QuantConnect Cloud. QC never sees the link — the cloud build behaves identically to a local clone. `git` records the symlink itself, so collaborators get the same wiring after `git clone`.

Rules:

- Do not create symlinks that point outside `MyProjects/shared/` (keeps paths predictable across machines).
- Always use **relative** symlink targets, never absolute.

## Adding a new shared signal

1. Create `shared/signals/<name>.py` with pure-Python math.
2. Add a synthetic-data unit test at the bottom of the file or a sibling `test_<name>.py`. Run it with a plain venv.
3. From each project that needs it: `ln -s ../../../shared/signals/<name>.py domain/signals/<name>.py`.
4. Commit both the shared file and the project's symlink.

## See also

- Workspace `CLAUDE.md` — § "Shared signals library"
- Workspace `AGENTS.md` — § "Using Shared Signals"
- Worked example: `MyProjects/ElectionIndustryBeta/domain/signals/election_beta.py`

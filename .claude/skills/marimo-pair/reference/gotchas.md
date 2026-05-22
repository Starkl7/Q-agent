# Marimo Pair Gotchas

## File Edits Can Be Lost

When a marimo server is running, do not edit the notebook `.py` file directly.
The kernel owns the live notebook state and can overwrite direct file edits on
its next save.

Use `marimo._code_mode` instead:

```python
import marimo._code_mode as cm

async with cm.get_context() as ctx:
    ctx.edit_cell(cell.id, code="x = 1")
    ctx.run_cell(cell.id)
```

## Code Mode Must Use `async with`

`ctx.create_cell`, `ctx.edit_cell`, and `ctx.run_cell` queue notebook
mutations. The `async with cm.get_context()` manager flushes them. Without the
context manager, changes silently do nothing.

## Execute Script Runs In The Notebook Kernel

`execute-code.sh` sends code to the running marimo kernel. Import errors and
syntax errors come from the submitted code or notebook environment, not the
local shell Python.

## Token Servers Are Harder To Discover

Only `--no-token` servers are reliably discoverable through the local registry.
If a server uses token auth, set `MARIMO_TOKEN` in the environment and target
the URL or port explicitly.

## NotebookCell API — Use `.id`, Not `.cell_id`

The `NotebookCell` object exposes:
- `cell.id` — use this for `run_cell()`, `edit_cell()`, `delete_cell()`
- `cell.code` — source code string
- `cell.status` — `"idle"`, `"running"`, `"marimo-error"`, `"exception"`
- `cell.errors` — list of `CellError` with `.kind` and `.msg`
- `cell.name` — usually `"_"`

**Not**: `cell.cell_id`, `cell.__dict__` (both raise `AttributeError`).

## MultipleDefinitionError — The Most Common Failure

marimo treats **every** top-level variable assignment as a cell export. If two
cells assign the same name (`fig`, `ax`, `df`, `h`, `j`, `x`, `i`...), both
cells get `MultipleDefinitionError` and neither executes.

This includes:
- Loop variables: `for ticker in ...` exports `ticker`
- Plot handles: `fig, ax = plt.subplots(...)` exports both
- Temporary DataFrames: `df = pd.DataFrame(...)` exports `df`

Fix: use unique names (`fig_hist`, `fig_3d`) or prefix with `_` (`_ticker`,
`_h`).

## Function Cells That Never Execute

A cell defined as `def _(df, plt): ... return (fig,)` is a function cell. Its
body only runs when marimo detects a downstream cell that consumes `fig`. If
nothing consumes it, **the body never executes and the plot never renders** —
the user just sees a function definition.

Fix: ensure every returned variable from a function cell is referenced by at
least one downstream cell, or restructure as a statement cell where the last
expression is the figure object.

## marimo Reformats Notebooks on Open

When marimo opens a `.py` file, it rewrites it: updates `__generated_with`,
strips unused variables from return tuples, and reformats whitespace. This
means:
- The `Write` tool will fail with "file modified since read"
- The `Edit` tool's exact-match strings won't match the reformatted version

Fix: if you need to rewrite the whole file, kill the server first (`pkill -f
"marimo edit.*filename"`), write the file with Bash (`cat > file << 'EOF'`),
then restart. Use `code_mode` for live edits.

## Validation Errors From `get_context()`

`ctx.edit_cell()` can raise `RuntimeError: Multiply-defined names` if the new
cell code introduces a name collision. Use `skip_validation=True` to bypass:

```python
async with cm.get_context(skip_validation=True) as ctx:
    ctx.edit_cell(cell.id, code=new_code)
```

This lets the edit land, but the underlying collision still prevents execution.
Fix the variable names before removing `skip_validation`.

## `ctx.packages.add()` for Missing Modules

`ModuleNotFoundError` in a cell means the package isn't in the marimo venv.
Use `ctx.packages.add("package_name")` — it installs into the correct venv and
handles kernel restarts. Don't `pip install` externally while the server runs.

## Calendar Days ≠ Trading Days in Event Windows

`pd.Timedelta(days=10)` counts calendar days. A 16-calendar-day window rarely
contains exactly 16 trading days, so strict `len(window) == WINDOW_SIZE` drops
most rows. Use index-based slicing (`.iloc`) or `pd.bdate_range()` instead.

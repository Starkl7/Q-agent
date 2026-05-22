# Notebook Improvements

Use this when improving an existing marimo notebook.

## Preserve The Dataflow

Inspect the live cell graph before making structural edits:

```python
import marimo._code_mode as cm

async with cm.get_context() as ctx:
    for cell in ctx.cells:
        print(cell.name, cell.status)
```

Edit existing cells when possible. Create new cells for genuinely new concepts or outputs.

## Cell Names

Most cells do not need explicit names. Add names only when they make repeated edits or debugging easier.

## Outputs

Prefer visible outputs that help the user inspect the current research state:

- compact tables for data checks
- charts for ranked or time-series comparisons
- short printed summaries for validation counts

Avoid large raw dumps unless the user asks for them.

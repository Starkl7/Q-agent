# Rich Representations

Use marimo-native UI elements for simple controls and `anywidget` for custom interactive components.

## Simple Controls

Prefer `mo.ui` widgets for ordinary controls:

```python
import marimo as mo

lookback = mo.ui.slider(20, 252, value=126, label="Lookback")
lookback
```

Update `mo.ui` values from code mode with `ctx.set_ui_value(element, new_value)` rather than mutating private attributes.

## Custom Widgets

Use `anywidget` only when the notebook needs custom HTML/CSS/JavaScript behavior that `mo.ui` cannot express cleanly.

Choose one reactivity bridge per widget:

- `mo.state` plus traitlet `.observe()` when you need explicit control over synced traits
- `mo.ui.anywidget()` when the whole synced widget value should be reactive

Do not mix both approaches for the same widget.

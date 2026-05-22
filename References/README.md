# References

Shared research material for this QuantConnect workspace.

## Layout

- `books/`: PDFs and other long-form reference material
- `repos/`: upstream research/code repositories cloned for study
- `notes/`: personal summaries, extraction notes, and QC-specific implementation notes

## Workflow

- Keep upstream material here instead of inside `MyProjects/`.
- Use `MyProjects/` only for runnable LEAN projects.
- When a reference chapter becomes a real QC implementation, create a separate project in `MyProjects/`.
- Prefer project names that match your existing convention, for example `AlphaMethods_Ch7_*` or `ML4Trading_Ch12_*`.

## QuantConnect Data Repos

- Free QC alternative-data reference repos currently cloned here: `Lean.DataSource.FRED`, `Lean.DataSource.USTreasury`, and `Lean.DataSource.USInterestRate`.
- Treat these repos as implementation references for LEAN data-source patterns and example algorithms.
- Some other QuantConnect data-source repos are useful as code references but map to paid datasets in the QuantConnect Dataset Market, so avoid assuming local access just because the source repo is public.

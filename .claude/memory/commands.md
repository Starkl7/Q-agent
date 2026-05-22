# Commands

Durable project-specific commands that have been confirmed to work.

Keep entries short and include the working directory if relevant.

---

## Infrastructure shared venv

```bash
# Activate (crypto + polymarket pipelines)
cd ~/Documents/Q-agent/infrastructure && source .venv/bin/activate

# Bootstrap from scratch (idempotent)
cd ~/Documents/Q-agent/infrastructure && bash setup.sh
```

## Pre-commit hook — marimo notebook export

Hook lives at `.git/hooks/pre-commit`. The correct marimo binary path is:
```
infrastructure/marimo/venv/bin/marimo
```
The hook exports staged marimo `.py` notebooks to `.ipynb` (with outputs) so GitHub renders them. It prompts interactively before exporting.

---
name: push
description: Commit and push the WRDS project to GitHub. Use when the user says "push", "commit", "sync", or wants to send changes to git/github.
---

# Push to GitHub

Push the current WRDS project changes to GitHub.

## Steps

1. **Check status**: Run `git status` and `git diff` to review uncommitted changes.
2. **Validate syntax**: Run `python -m py_compile` on changed `.py` files to catch syntax errors before pushing.
3. **Commit to git**: If there are uncommitted changes, stage them and create a commit with a clear message describing the changes. Ask the user for a commit message if the changes are non-trivial and the intent is unclear.
4. **Push to GitHub**: Run `git push` to sync with the remote repository.
5. **Report results**: Confirm success or report any errors.

## Guidelines
- Always check `git status` before committing — do not commit if there are no changes
- Do not commit files listed in `.gitignore` (data/raw/, venv/, __pycache__/, .env, lean-data/, etc.)
- If syntax validation fails, stop and fix the errors before pushing

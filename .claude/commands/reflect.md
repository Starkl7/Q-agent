---
description: Review pending memory candidates and promote durable project learnings into .claude/memory.
allowed-tools:
  - Read
  - Edit
---

# Reflect

Review `.claude/memory/pending.md` and promote only durable, reusable project knowledge into the appropriate memory file:

- `.claude/memory/commands.md` for confirmed commands that are useful to reuse
- `.claude/memory/lean-gotchas.md` for confirmed LEAN, Docker, cloud, or research-container issues and fixes
- `.claude/memory/wrds-data-sources.md` for WRDS/CRSP table, extraction, or schema notes
- `.claude/memory/objectstore.md` for ObjectStore keys, schema notes, and migration cautions
- `.claude/memory/decisions.md` for architecture or workflow decisions and their rationale
- `.claude/memory/teaching-style.md` for durable teaching or demo preferences

Rules:

1. Do not store secrets, usernames, tokens, DSNs, config values, or private credentials.
2. Do not promote one-off command history unless it represents a reusable workflow.
3. Rewrite promoted entries into concise, stable notes with enough context to be useful later.
4. Leave ambiguous entries in `pending.md`.
5. After promotion, remove only the entries you promoted from `pending.md`.

$ARGUMENTS

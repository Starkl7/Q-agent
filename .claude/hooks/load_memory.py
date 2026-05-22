#!/usr/bin/env python3
"""
SessionStart hook that loads project memory files into Claude Code context.

This keeps memory separate from CLAUDE.md but still makes it available at the
beginning of future sessions.
"""

import json
import os
import sys
from pathlib import Path


MAX_CHARS_PER_FILE = 6000

MEMORY_FILES = [
    "commands.md",
    "lean-gotchas.md",
    "wrds-data-sources.md",
    "objectstore.md",
    "decisions.md",
    "teaching-style.md",
]


def main() -> int:
    raw = sys.stdin.read()

    try:
        event = json.loads(raw)
    except json.JSONDecodeError:
        event = {}

    project_dir = Path(
        os.environ.get("CLAUDE_PROJECT_DIR", event.get("cwd", "."))
    ).resolve()

    memory_dir = project_dir / ".claude" / "memory"

    sections = []

    for filename in MEMORY_FILES:
        path = memory_dir / filename
        if not path.exists():
            continue

        content = path.read_text(encoding="utf-8").strip()
        if not content:
            continue

        if len(content) > MAX_CHARS_PER_FILE:
            content = content[-MAX_CHARS_PER_FILE:]

        sections.append(f"## {filename}\n\n{content}")

    if not sections:
        return 0

    context = (
        "Project memory loaded from .claude/memory. "
        "Use this as helpful project context, but prefer current user instructions "
        "if they conflict.\n\n"
        + "\n\n---\n\n".join(sections)
    )

    output = {
        "hookSpecificOutput": {
            "hookEventName": "SessionStart",
            "additionalContext": context,
        }
    }

    print(json.dumps(output))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

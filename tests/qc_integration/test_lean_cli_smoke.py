"""Smoke tests for the LEAN CLI environment.

Marked `integration` because they require `lean` to be installed and a
working Docker/Python environment. CI skips these by default; run locally
with `pytest -m integration` to exercise them.
"""

from __future__ import annotations

import shutil
import subprocess

import pytest


pytestmark = pytest.mark.integration


def test_lean_cli_is_installed():
    assert shutil.which("lean"), "lean CLI is not on PATH — activate the venv first"


def test_lean_version_runs():
    result = subprocess.run(
        ["lean", "--version"],
        capture_output=True,
        text=True,
        timeout=30,
    )
    assert result.returncode == 0, f"`lean --version` failed: {result.stderr}"
    assert result.stdout.strip(), "`lean --version` produced no output"

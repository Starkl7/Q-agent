"""Shared fixtures for the Q-agent workspace test suite."""

from pathlib import Path

import pytest


REPO_ROOT = Path(__file__).resolve().parent.parent


@pytest.fixture(scope="session")
def repo_root() -> Path:
    return REPO_ROOT


@pytest.fixture(scope="session")
def template_dir(repo_root: Path) -> Path:
    return repo_root / "MyProjects" / "_template"


@pytest.fixture(scope="session")
def pipelines_dir(repo_root: Path) -> Path:
    return repo_root / "infrastructure" / "pipelines"

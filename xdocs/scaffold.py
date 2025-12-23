from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class InitResult:
    created: list[Path]
    skipped: list[Path]


def _write_file(path: Path, content: str, *, force: bool) -> bool:
    if path.exists() and not force:
        return False
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    return True


def init_repo(
    *,
    root: Path,
    docs_dir: str = "docs",
    force: bool = False,
    ci_install: str = "xdocs",
) -> InitResult:
    """
    Scaffold pytest + GitHub Actions glue into an arbitrary repo.

    `ci_install` is the pip install target for xdocs in CI, e.g.
      - "xdocs" (PyPI, once published)
      - "xdocs @ git+https://github.com/ORG/REPO.git"
      - "git+https://github.com/ORG/REPO.git"
    """
    root = root.resolve()
    created: list[Path] = []
    skipped: list[Path] = []

    test_path = root / "tests" / "test_xdocs.py"
    test_content = f"""\
from __future__ import annotations

import os
from pathlib import Path

import pytest

from xdocs.assertions import assert_result
from xdocs.extract import extract_from_paths
from xdocs.runner import run_snippet


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[1]


@pytest.mark.parametrize("snippet", extract_from_paths([_repo_root() / "{docs_dir}"], project_root=_repo_root()))
def test_docs_snippet(snippet) -> None:
    accept = os.environ.get("XDOCS_ACCEPT") == "1"
    result = run_snippet(snippet, project_root=_repo_root())
    assert_result(snippet, result, accept=accept)
"""
    if _write_file(test_path, test_content, force=force):
        created.append(test_path)
    else:
        skipped.append(test_path)

    wf_path = root / ".github" / "workflows" / "xdocs.yml"
    wf_content = f"""\
name: xdocs

on:
  pull_request:
  push:
    branches: ["main"]

jobs:
  xdocs:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - uses: actions/setup-python@v5
        with:
          python-version: "3.12"
          cache: "pip"

      - name: Install project + xdocs
        run: |
          python -m pip install --upgrade pip
          # Install your project (adjust extras as needed)
          python -m pip install -e ".[dev]" || python -m pip install -e .
          python -m pip install "{ci_install}"

      - name: Run executable docs
        run: pytest

      - name: Upload xdocs snapshots (on failure)
        if: failure()
        uses: actions/upload-artifact@v4
        with:
          name: xdocs-snapshots
          path: {docs_dir}/.xdocs_snapshots
"""
    if _write_file(wf_path, wf_content, force=force):
        created.append(wf_path)
    else:
        skipped.append(wf_path)

    return InitResult(created=created, skipped=skipped)



from __future__ import annotations

import os
from pathlib import Path

import pytest

from xdocs.assertions import assert_result
from xdocs.extract import extract_from_paths
from xdocs.runner import run_snippet


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[1]


@pytest.mark.parametrize("snippet", extract_from_paths([_repo_root() / "docs"], project_root=_repo_root()))
def test_docs_snippet(snippet) -> None:
    accept = os.environ.get("XDOCS_ACCEPT") == "1"
    result = run_snippet(snippet, project_root=_repo_root())
    assert_result(snippet, result, accept=accept)



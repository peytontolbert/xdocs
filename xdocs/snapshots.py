from __future__ import annotations

from pathlib import Path

from .models import Snippet


def snapshot_dir_for(md_path: Path) -> Path:
    return md_path.parent / ".xdocs_snapshots"


def snapshot_path(snippet: Snippet) -> Path:
    # stable-ish filename: <docname>__<index>__<hash>.stdout
    doc = snippet.path.name.replace("/", "_")
    tail = snippet.id.split("::")[-1]
    return snapshot_dir_for(snippet.path) / f"{doc}__{snippet.index}__{tail}.stdout"



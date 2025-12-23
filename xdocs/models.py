from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class Snippet:
    id: str
    path: Path
    index: int
    lang: str
    code: str
    meta: dict[str, str]



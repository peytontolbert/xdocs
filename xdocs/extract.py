from __future__ import annotations

import hashlib
import re
from pathlib import Path

from .models import Snippet


_FENCE_RE = re.compile(
    r"(?ms)^```(?P<info>[^\n]*)\n(?P<body>.*?)(?:\n)```[ \t]*$"
)


def _parse_info(info: str) -> tuple[str, dict[str, str]]:
    """
    Info string format (simple MVP):
      "python xdocs"
      "python xdocs expect=\"stdout:Hello\""
    """
    info = info.strip()
    if not info:
        return "", {}

    parts = info.split()
    lang = parts[0].strip()
    meta: dict[str, str] = {}

    # Remaining tokens: either flags (xdocs) or key=val
    for token in parts[1:]:
        if "=" not in token:
            meta[token] = "true"
            continue
        k, v = token.split("=", 1)
        v = v.strip()
        if (len(v) >= 2) and ((v[0] == v[-1] == '"') or (v[0] == v[-1] == "'")):
            v = v[1:-1]
        meta[k.strip()] = v

    return lang, meta


def extract_from_markdown(md_path: Path, *, project_root: Path | None = None) -> list[Snippet]:
    text = md_path.read_text(encoding="utf-8")
    out: list[Snippet] = []

    matches = list(_FENCE_RE.finditer(text))
    for i, m in enumerate(matches):
        info = m.group("info")
        body = m.group("body")
        lang, meta = _parse_info(info)
        if meta.get("xdocs") != "true":
            continue

        h = hashlib.sha256(body.encode("utf-8")).hexdigest()[:8]
        try:
            rel = md_path.resolve().relative_to(project_root.resolve()) if project_root else md_path
            base = rel.as_posix()
        except Exception:
            base = md_path.as_posix()
        sid = f"{base}::{i}::{h}"
        out.append(
            Snippet(
                id=sid,
                path=md_path,
                index=i,
                lang=lang,
                code=body.rstrip() + "\n",
                meta=meta,
            )
        )

    return out


def extract_from_paths(paths: list[Path], *, project_root: Path | None = None) -> list[Snippet]:
    md_files: list[Path] = []
    for p in paths:
        if p.is_dir():
            md_files.extend(sorted(p.rglob("*.md")))
        elif p.suffix.lower() == ".md":
            md_files.append(p)

    snippets: list[Snippet] = []
    for md in sorted(set(md_files)):
        snippets.extend(extract_from_markdown(md, project_root=project_root))
    return snippets



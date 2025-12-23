from __future__ import annotations

import os
import re


_ANSI_RE = re.compile(r"\x1b\[[0-9;]*m")


def normalize_text(text: str) -> str:
    # Stable newlines + strip ANSI
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    text = _ANSI_RE.sub("", text)

    # Normalize common path noise (best-effort)
    tmp = os.environ.get("TMPDIR") or os.environ.get("TMP") or "/tmp"
    text = text.replace(tmp, "<TMP>")

    # Trim trailing whitespace on each line
    text = "\n".join(line.rstrip() for line in text.split("\n")).rstrip() + "\n"
    return text



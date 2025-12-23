from __future__ import annotations

import os
import subprocess
import sys
import tempfile
from dataclasses import dataclass
from pathlib import Path

from .models import Snippet


@dataclass(frozen=True)
class RunResult:
    returncode: int
    stdout: str
    stderr: str


def run_snippet(
    snippet: Snippet,
    *,
    project_root: Path | None = None,
    timeout_s: float = 30.0,
) -> RunResult:
    """
    Execute a snippet against a target project root.

    By default, `project_root` is the current working directory.
    """
    project_root = (project_root or Path.cwd()).resolve()
    env = dict(os.environ)

    # Make common project layouts importable.
    pythonpath_parts: list[str] = []
    if (project_root / "src").exists():
        pythonpath_parts.append(str(project_root / "src"))
    pythonpath_parts.append(str(project_root))
    if env.get("PYTHONPATH"):
        pythonpath_parts.append(env["PYTHONPATH"])
    env["PYTHONPATH"] = os.pathsep.join(pythonpath_parts).strip(os.pathsep)

    with tempfile.TemporaryDirectory(prefix="xdocs-") as td:
        cwd = Path(td)

        if snippet.lang == "python":
            path = cwd / "snippet.py"
            path.write_text(snippet.code, encoding="utf-8")
            # Note: avoid `-I` because it ignores PYTHONPATH; docs often import the local `src/` package.
            cmd = [sys.executable, "-u", str(path)]
        elif snippet.lang == "bash":
            path = cwd / "snippet.sh"
            path.write_text("set -euo pipefail\n" + snippet.code, encoding="utf-8")
            cmd = ["bash", str(path)]
        else:
            raise ValueError(f"Unsupported snippet language: {snippet.lang!r}")

        p = subprocess.run(
            cmd,
            cwd=str(cwd),
            env=env,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=timeout_s,
        )

        return RunResult(returncode=p.returncode, stdout=p.stdout, stderr=p.stderr)



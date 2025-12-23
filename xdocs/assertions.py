from __future__ import annotations

from .models import Snippet
from .normalize import normalize_text
from .runner import RunResult
from .snapshots import snapshot_path


class AssertionFailure(AssertionError):
    """Raised when an executable-doc assertion fails."""


def _expect_stdout_contains(snippet: Snippet, stdout: str) -> None:
    expect = snippet.meta.get("expect")
    if not expect:
        return
    # MVP DSL: expect="stdout:<substring>"
    if not expect.startswith("stdout:"):
        raise AssertionFailure(f"{snippet.id}: unsupported expect format: {expect!r}")
    needle = expect[len("stdout:") :]
    if needle not in stdout:
        raise AssertionFailure(
            f"{snippet.id}: stdout did not contain {needle!r}\n\n--- stdout ---\n{stdout}"
        )


def assert_result(
    snippet: Snippet,
    result: RunResult,
    *,
    accept: bool,
) -> None:
    if result.returncode != 0:
        raise AssertionFailure(
            f"{snippet.id}: non-zero exit ({result.returncode})\n\n"
            f"--- stdout ---\n{result.stdout}\n\n--- stderr ---\n{result.stderr}"
        )

    stdout = normalize_text(result.stdout)
    _expect_stdout_contains(snippet, stdout)

    # Default contract: snapshot stdout (unless explicit expect is provided).
    if snippet.meta.get("expect"):
        return

    snap = snapshot_path(snippet)
    snap.parent.mkdir(parents=True, exist_ok=True)

    if accept or not snap.exists():
        if not snap.exists() and not accept:
            raise AssertionFailure(
                f"{snippet.id}: missing snapshot {snap.as_posix()}\n"
                f"Run with XDOCS_ACCEPT=1 to generate snapshots."
            )
        snap.write_text(stdout, encoding="utf-8")
        return

    expected = snap.read_text(encoding="utf-8")
    if expected != stdout:
        raise AssertionFailure(
            f"{snippet.id}: stdout snapshot mismatch\n\n"
            f"--- expected ({snap.as_posix()}) ---\n{expected}\n\n"
            f"--- actual ---\n{stdout}\n\n"
            f"Run with XDOCS_ACCEPT=1 to accept the new output."
        )



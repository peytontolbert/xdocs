from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

from .assertions import AssertionFailure, assert_result
from .extract import extract_from_paths
from .runner import run_snippet
from .scaffold import init_repo


def _resolve_paths(root: Path, paths: list[Path] | None) -> list[Path]:
    root = root.resolve()
    if not paths:
        return [root / "docs"]
    out: list[Path] = []
    for p in paths:
        out.append(p if p.is_absolute() else (root / p))
    return out


def cmd_extract(args: argparse.Namespace) -> int:
    paths = _resolve_paths(args.root, args.paths)
    snippets = extract_from_paths(paths, project_root=args.root)
    for s in snippets:
        print(f"{s.id}\t{s.lang}\t{s.path.as_posix()}#{s.index}")
    return 0


def cmd_run(args: argparse.Namespace, *, accept: bool) -> int:
    paths = _resolve_paths(args.root, args.paths)
    snippets = extract_from_paths(paths, project_root=args.root)
    if not snippets:
        print("xdocs: no snippets found", file=sys.stderr)
        return 0

    failures: list[str] = []
    for s in snippets:
        try:
            result = run_snippet(s, project_root=args.root, timeout_s=args.timeout)
            assert_result(s, result, accept=accept)
        except (AssertionFailure, Exception) as e:
            failures.append(str(e))

    if failures:
        print("\n\n".join(failures), file=sys.stderr)
        return 1
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="xdocs")
    parser.add_argument(
        "--root",
        type=Path,
        default=Path.cwd(),
        help="Target project root (defaults to current working directory).",
    )
    sub = parser.add_subparsers(dest="cmd", required=True)

    p_extract = sub.add_parser("extract", help="List executable snippets discovered in docs.")
    p_extract.add_argument("paths", nargs="*", type=Path)
    p_extract.set_defaults(_fn=cmd_extract)

    p_run = sub.add_parser("run", help="Execute snippets and verify snapshots/assertions.")
    p_run.add_argument("paths", nargs="*", type=Path)
    p_run.add_argument("--timeout", type=float, default=30.0)
    p_run.set_defaults(_fn=lambda a: cmd_run(a, accept=False))

    p_accept = sub.add_parser("accept", help="Execute snippets and (re)write snapshots.")
    p_accept.add_argument("paths", nargs="*", type=Path)
    p_accept.add_argument("--timeout", type=float, default=30.0)
    p_accept.set_defaults(_fn=lambda a: cmd_run(a, accept=True))

    p_init = sub.add_parser("init", help="Scaffold pytest + GitHub Actions glue into a repo.")
    p_init.add_argument("--docs-dir", default="docs", help="Docs directory to scan (default: docs).")
    p_init.add_argument(
        "--ci-install",
        default="xdocs",
        help='pip install target for xdocs in CI (e.g. "xdocs @ git+https://github.com/ORG/REPO.git").',
    )
    p_init.add_argument("--force", action="store_true", help="Overwrite existing files.")
    p_init.set_defaults(
        _fn=lambda a: (
            0
            if _print_init(init_repo(root=a.root, docs_dir=a.docs_dir, force=a.force, ci_install=a.ci_install))
            else 0
        )
    )

    args = parser.parse_args(argv)

    # Allow env override for snapshot acceptance (useful in CI/local pytest).
    if args.cmd in {"run", "accept"}:
        accept_env = os.environ.get("XDOCS_ACCEPT") == "1"
        if accept_env:
            return cmd_run(args, accept=True)

    return int(args._fn(args))


def _print_init(result) -> bool:
    # tiny helper to keep init output readable
    for p in result.created:
        print(f"created: {p.as_posix()}")
    for p in result.skipped:
        print(f"skipped: {p.as_posix()}", file=sys.stderr)
    return True


if __name__ == "__main__":
    raise SystemExit(main())



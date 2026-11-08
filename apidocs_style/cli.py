"""Command line entry point.

Exit codes: 0 clean, 1 issues at or above ``--fail-level``, 2 unreadable path.
"""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import asdict
from pathlib import Path
from typing import Sequence

from .checks import Issue, iter_documents, scan_file
from .rules import DEFAULT_FAIL_LEVEL, LEVELS, rank


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="apidocs-style",
        description="Check API reference pages against the house style guide.",
    )
    parser.add_argument("paths", nargs="+", metavar="PATH", help="file or directory to check")
    parser.add_argument(
        "--format", choices=("text", "json"), default="text", help="report format"
    )
    parser.add_argument(
        "--min-level", choices=LEVELS, default="suggestion", help="hide issues below this level"
    )
    parser.add_argument(
        "--fail-level",
        choices=LEVELS + ("never",),
        default=DEFAULT_FAIL_LEVEL,
        help="lowest level that makes the run fail",
    )
    return parser


def render_text(issues: list[Issue]) -> str:
    lines = []
    for issue in issues:
        lines.append(
            f"{issue.path}:{issue.line}:{issue.column}: "
            f"{issue.level} {issue.rule} {issue.message}"
        )
        lines.append(f"    {issue.suggestion}")
        lines.append(f"    > {issue.excerpt}")
    return "\n".join(lines)


def summarize(issues: list[Issue]) -> dict[str, int]:
    summary = {level: 0 for level in LEVELS}
    for issue in issues:
        summary[issue.level] += 1
    return summary


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)

    try:
        documents = sorted(iter_documents([Path(path) for path in args.paths]))
    except FileNotFoundError as error:
        print(f"apidocs-style: {error}", file=sys.stderr)
        return 2

    issues = [
        issue
        for document in documents
        for issue in scan_file(document)
        if rank(issue.level) <= rank(args.min_level)
    ]
    issues.sort(key=lambda issue: (issue.path, rank(issue.level), issue.line, issue.column))

    summary = summarize(issues)
    if args.format == "json":
        print(
            json.dumps(
                {
                    "documents": len(documents),
                    "issues": [asdict(issue) for issue in issues],
                    "summary": summary,
                },
                indent=2,
            )
        )
    else:
        if issues:
            print(render_text(issues))
            print()
        counts = ", ".join(f"{count} {level}" for level, count in summary.items() if count)
        files = "file" if len(documents) == 1 else "files"
        print(f"{len(documents)} {files} checked: {counts or 'no issues'}")

    if args.fail_level == "never":
        return 0
    return 1 if any(rank(issue.level) <= rank(args.fail_level) for issue in issues) else 0


if __name__ == "__main__":
    raise SystemExit(main())

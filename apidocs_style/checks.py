"""Scanner that turns page prose into rule violations.

The scanner is deliberately shallow: it tracks fenced code blocks and front
matter, masks inline code and link targets, then applies line rules. Deeper
parsing would drift from the Vale rules that run in CI and cost the speed
needed to run this on every save.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Iterator

from .rules import (
    FENCE_RULE,
    LONG_SENTENCE_RULE,
    LONG_SENTENCE_WORDS,
    RULES,
    UNCLOSED_FENCE_RULE,
    Rule,
)

SUFFIXES = frozenset({".md", ".mdx", ".rst"})
INLINE_CODE = re.compile(r"`[^`\n]*`")
LINK_TARGET = re.compile(r"\]\([^)\n]*\)")
SENTENCE = re.compile(r"[^.!?]+[.!?]")
WORD = re.compile(r"[\w'-]+")
EXCERPT_LIMIT = 120


@dataclass(frozen=True)
class Issue:
    """A violation located at a path, line, and column."""

    path: str
    line: int
    column: int
    rule: str
    level: str
    message: str
    suggestion: str
    excerpt: str


def _issue(path: str, line: int, column: int, rule: Rule, source: str) -> Issue:
    return Issue(
        path=path,
        line=line,
        column=column,
        rule=rule.id,
        level=rule.level,
        message=rule.message,
        suggestion=rule.suggestion,
        excerpt=source.strip()[:EXCERPT_LIMIT],
    )


def mask(line: str) -> str:
    """Blank out spans whose contents are not prose, keeping columns stable."""

    masked = line
    for pattern in (INLINE_CODE, LINK_TARGET):
        masked = pattern.sub(lambda match: " " * len(match.group()), masked)
    return masked


def _long_sentences(path: str, line_no: int, masked: str, source: str) -> list[Issue]:
    found = []
    for match in SENTENCE.finditer(masked):
        if len(WORD.findall(match.group())) > LONG_SENTENCE_WORDS:
            found.append(_issue(path, line_no, match.start() + 1, LONG_SENTENCE_RULE, source))
    return found


def scan_text(text: str, display_path: str = "<text>") -> list[Issue]:
    """Return every violation in ``text``, in source order."""

    issues: list[Issue] = []
    in_fence = False
    in_front_matter = False
    fence_line = 0
    lines = text.splitlines()

    for line_no, line in enumerate(lines, start=1):
        stripped = line.strip()

        if line_no == 1 and stripped == "---":
            in_front_matter = True
            continue
        if in_front_matter:
            if stripped in {"---", "..."}:
                in_front_matter = False
            continue

        if stripped.startswith("```"):
            if not in_fence:
                if FENCE_RULE.pattern.match(stripped):
                    column = len(line) - len(line.lstrip()) + 1
                    issues.append(_issue(display_path, line_no, column, FENCE_RULE, line))
                fence_line = line_no
            in_fence = not in_fence
            continue

        if in_fence:
            continue

        masked = mask(line)
        for rule in RULES:
            target = line if rule.raw else masked
            for match in rule.pattern.finditer(target):
                issues.append(_issue(display_path, line_no, match.start() + 1, rule, line))

        if not stripped.startswith("#"):
            issues.extend(_long_sentences(display_path, line_no, masked, line))

    if in_fence:
        issues.append(
            _issue(display_path, fence_line, 1, UNCLOSED_FENCE_RULE, lines[fence_line - 1])
        )
    return issues


def scan_file(path: Path, root: Path | None = None) -> list[Issue]:
    """Scan one file, displaying it relative to ``root`` when given."""

    display = str(path.relative_to(root)) if root is not None else str(path)
    return scan_text(path.read_text(encoding="utf-8", errors="replace"), display)


def iter_documents(paths: Iterable[Path]) -> Iterator[Path]:
    """Yield supported files from files and directories, sorted per directory."""

    for raw in paths:
        path = Path(raw)
        if path.is_dir():
            for child in sorted(path.rglob("*")):
                if child.is_file() and child.suffix in SUFFIXES:
                    yield child
        elif path.is_file():
            yield path
        else:
            raise FileNotFoundError(f"no such file or directory: {raw}")

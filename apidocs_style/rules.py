"""Style rules for API reference pages.

Every rule here has a partner file in ``styles/APIReference`` so a page is
reported the same way whether it is checked locally or by Vale in CI. Change
both together: the rule id is the contract. The computed rules (sentence
length, unclosed fence) have no Vale counterpart and run here only.
"""

from __future__ import annotations

import re
from dataclasses import dataclass

LEVELS = ("error", "warning", "suggestion")
DEFAULT_FAIL_LEVEL = "warning"
LONG_SENTENCE_WORDS = 25


@dataclass(frozen=True)
class Rule:
    """One line-oriented check.

    ``pattern`` is unused for computed rules such as the sentence length
    limit; keep it empty rather than None so callers never branch on it.
    ``raw`` marks rules that must see unmasked source, such as trailing
    whitespace.
    """

    id: str
    level: str
    pattern: re.Pattern[str]
    message: str
    suggestion: str
    raw: bool = False

    def __post_init__(self) -> None:
        if self.level not in LEVELS:
            raise ValueError(f"{self.id}: unknown level {self.level!r}")


FENCE_RULE = Rule(
    id="APIRef.CodeFenceLanguage",
    level="error",
    pattern=re.compile(r"^```[ \t]*$"),
    message="Fenced code block has no language tag.",
    suggestion="Tag the fence, for example ```json, so readers and highlighters can parse it.",
)

UNCLOSED_FENCE_RULE = Rule(
    id="APIRef.CodeFenceClosed",
    level="error",
    pattern=re.compile(r""),
    message="Code fence is never closed.",
    suggestion="Close the block with a line containing only ```.",
)

LONG_SENTENCE_RULE = Rule(
    id="APIRef.SentenceLength",
    level="suggestion",
    pattern=re.compile(r""),
    message=f"Sentence is longer than {LONG_SENTENCE_WORDS} words.",
    suggestion="Split it, or move the detail into a list.",
)

RULES: tuple[Rule, ...] = (
    Rule(
        id="APIRef.LatinAbbreviation",
        level="warning",
        pattern=re.compile(r"\b(?:e\.g\.|i\.e\.|etc\.)"),
        message="Latin abbreviation in running prose.",
        suggestion="Write 'for example', 'that is', or 'and so on'.",
    ),
    Rule(
        id="APIRef.WordyPhrase",
        level="warning",
        pattern=re.compile(
            r"\b(?:in order to|prior to|at this point in time|in the event that|utilize[sd]?)\b",
            re.IGNORECASE,
        ),
        message="Wordy phrase.",
        suggestion="Use 'to', 'before', 'now', 'if', or 'use'.",
    ),
    Rule(
        id="APIRef.FutureTense",
        level="warning",
        pattern=re.compile(
            r"\bwill (?:be )?(?:return|send|create|update|delete|charge|refund)\w*\b",
            re.IGNORECASE,
        ),
        message="Future tense for behavior that happens now.",
        suggestion="Use the present tense: 'the server returns'.",
    ),
    Rule(
        id="APIRef.PassiveVoice",
        level="suggestion",
        pattern=re.compile(
            r"\b(?:is|are|was|were|be|been|being)\s+"
            r"(?:\w+ed|built|done|given|made|sent|shown|taken|written)\b",
            re.IGNORECASE,
        ),
        message="Passive voice in reference text.",
        suggestion="Name the actor: 'the server returns', not 'is returned'.",
    ),
    Rule(
        id="APIRef.SecondPerson",
        level="suggestion",
        pattern=re.compile(r"\b(?:users?|clients?|developers?) (?:can|should|must|may)\b"),
        message="Third person subject in a task statement.",
        suggestion="Address the reader: 'you can'.",
    ),
    Rule(
        id="APIRef.TrailingSpace",
        level="suggestion",
        pattern=re.compile(r"[ \t]+$"),
        message="Trailing whitespace.",
        suggestion="Strip it.",
        raw=True,
    ),
)

BY_ID: dict[str, Rule] = {rule.id: rule for rule in RULES}


def rank(level: str) -> int:
    """Severity order; lower is more severe, so filters compare with ``<=``."""

    return LEVELS.index(level)

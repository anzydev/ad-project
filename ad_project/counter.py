"""
Text and character analysis utilities for ad-project.
Provides specific character counting and text statistics.
"""

from collections import Counter
from dataclasses import dataclass
from typing import Dict, Optional


@dataclass
class CharStats:
    """Statistics for text character analysis."""
    total_chars: int
    non_space_chars: int
    whitespace_chars: int
    lines: int
    words: int
    digits: int
    target_char: Optional[str] = None
    target_count: int = 0
    top_chars: Optional[Dict[str, int]] = None


def count_specific_char(text: str, target: str, case_sensitive: bool = True) -> int:
    """
    Count occurrences of a specific character or substring in text.

    Args:
        text: Input string.
        target: Character or substring to search for.
        case_sensitive: Whether to match case.

    Returns:
        Integer count of occurrences.
    """
    if not text or not target:
        return 0
    if not case_sensitive:
        return text.lower().count(target.lower())
    return text.count(target)


def analyze_text(text: str, target_char: Optional[str] = None, case_sensitive: bool = True) -> CharStats:
    """
    Analyze text and return character and word metrics.

    Args:
        text: Input string to inspect.
        target_char: Optional specific character to count.
        case_sensitive: Whether target character count is case sensitive.

    Returns:
        CharStats dataclass with calculated metrics.
    """
    if not text:
        return CharStats(
            total_chars=0,
            non_space_chars=0,
            whitespace_chars=0,
            lines=0,
            words=0,
            digits=0,
            target_char=target_char,
            target_count=0,
            top_chars={},
        )

    total_chars = len(text)
    whitespaces = sum(1 for c in text if c.isspace())
    non_spaces = total_chars - whitespaces
    digits = sum(1 for c in text if c.isdigit())
    lines = len(text.splitlines()) or (1 if text else 0)
    words = len(text.split())

    target_count = 0
    if target_char:
        target_count = count_specific_char(text, target_char, case_sensitive=case_sensitive)

    # Calculate top 5 most frequent non-space characters
    counter = Counter(c for c in text if not c.isspace())
    top_chars = dict(counter.most_common(5))

    return CharStats(
        total_chars=total_chars,
        non_space_chars=non_spaces,
        whitespace_chars=whitespaces,
        lines=lines,
        words=words,
        digits=digits,
        target_char=target_char,
        target_count=target_count,
        top_chars=top_chars,
    )

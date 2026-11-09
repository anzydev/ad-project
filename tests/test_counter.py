"""
Unit tests for specific character counter and text analyzer.
"""

from ad_project.counter import count_specific_char, analyze_text, CharStats


def test_count_specific_char_basic():
    text = "Antigravity terminal monitor for Python"
    assert count_specific_char(text, "t") == 5
    assert count_specific_char(text, "A", case_sensitive=True) == 1
    assert count_specific_char(text, "a", case_sensitive=False) == 3


def test_count_specific_char_empty():
    assert count_specific_char("", "a") == 0
    assert count_specific_char("hello", "") == 0
    assert count_specific_char("", "") == 0


def test_analyze_text_empty():
    stats = analyze_text("")
    assert stats.total_chars == 0
    assert stats.words == 0
    assert stats.target_count == 0


def test_analyze_text_with_target():
    sample = "Hello World! 1234\nSecond line here."
    stats = analyze_text(sample, target_char="l", case_sensitive=True)
    assert stats.total_chars == len(sample)
    assert stats.lines == 2
    assert stats.words == 6
    assert stats.digits == 4
    assert stats.target_char == "l"
    assert stats.target_count == 4  # 'Hello' (2), 'World' (1), 'line' (1)
    assert isinstance(stats.top_chars, dict)


def test_analyze_text_case_insensitive_target():
    sample = "AaBbCc AA"
    stats = analyze_text(sample, target_char="a", case_sensitive=False)
    assert stats.target_count == 4

"""
Unit tests for formatting utilities, color helpers, and terminal widgets.
"""

import pytest
from rich.text import Text

from ad_project.utils import (
    NonBlockingInput,
    create_progress_bar,
    format_bytes,
    format_frequency,
    format_rate,
    format_uptime,
    get_percent_color,
)


def test_format_bytes():
    assert format_bytes(-5) == "0 B"
    assert format_bytes(0) == "0 B"
    assert format_bytes(500) == "500 B"
    assert format_bytes(1024) == "1.0 KB"
    assert format_bytes(1024 * 1024) == "1.0 MB"
    assert format_bytes(1024 * 1024 * 1024) == "1.0 GB"
    assert format_bytes(1024 * 1024 * 1024 * 1024) == "1.0 TB"
    assert format_bytes(1536, decimal_places=2) == "1.50 KB"


def test_format_rate():
    assert format_rate(0) == "0.0 B/s"
    assert format_rate(-10) == "0.0 B/s"
    assert format_rate(1024) == "1.0 KB/s"
    assert format_rate(5 * 1024 * 1024) == "5.0 MB/s"


def test_format_uptime():
    assert format_uptime(0) == "0m 0s"
    assert format_uptime(45) == "0m 45s"
    assert format_uptime(125) == "2m 5s"
    assert format_uptime(3665) == "1h 1m"
    assert format_uptime(90000) == "1d 1h 0m"
    assert format_uptime(176400) == "2d 1h 0m"


def test_format_frequency():
    assert format_frequency(None) == "N/A"
    assert format_frequency(0) == "N/A"
    assert format_frequency(-100) == "N/A"
    # Apple silicon direct GHz reporting (< 100)
    assert format_frequency(3.5) == "3.50 GHz"
    # Standard MHz reporting
    assert format_frequency(800) == "800 MHz"
    assert format_frequency(2400) == "2.40 GHz"
    assert format_frequency(3200) == "3.20 GHz"


def test_get_percent_color():
    assert get_percent_color(0.0) == "bright_green"
    assert get_percent_color(59.9) == "bright_green"
    assert get_percent_color(60.0) == "bright_yellow"
    assert get_percent_color(84.9) == "bright_yellow"
    assert get_percent_color(85.0) == "bright_red"
    assert get_percent_color(100.0) == "bright_red"


def test_create_progress_bar():
    bar = create_progress_bar(50.0, width=10)
    assert isinstance(bar, Text)
    plain = bar.plain
    assert "50.0%" in plain
    assert "█" in plain
    assert "░" in plain

    # Clamping behavior
    bar_neg = create_progress_bar(-20.0, width=10)
    assert "0.0%" in bar_neg.plain

    bar_high = create_progress_bar(150.0, width=10)
    assert "100.0%" in bar_high.plain


def test_non_blocking_input_context():
    with NonBlockingInput() as reader:
        # Non-blocking query should return None or a single char string
        res = reader.get_key(timeout=0.001)
        assert res is None or isinstance(res, str)


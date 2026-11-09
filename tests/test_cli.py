"""
Unit tests for CLI argument parsing and execution flags.
"""

from rich.console import Console

from ad_project.cli import parse_args, run_single_snapshot
from ad_project.collectors import SystemMonitor


def test_parse_args_defaults():
    args = parse_args([])
    assert args.interval == 1.5
    assert args.once is False


def test_parse_args_custom():
    args = parse_args(["-i", "2.5", "--once"])
    assert args.interval == 2.5
    assert args.once is True


def test_run_single_snapshot():
    console = Console(width=100)
    monitor = SystemMonitor()
    code = run_single_snapshot(console, monitor, interval=1.0)
    assert code == 0

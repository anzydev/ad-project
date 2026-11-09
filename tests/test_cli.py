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
    args = parse_args(["-i", "2.5", "--once", "--count-text", "hello world", "--char", "l"])
    assert args.interval == 2.5
    assert args.once is True
    assert args.count_text == "hello world"
    assert args.char == "l"


def test_main_count_text():
    from ad_project.cli import main
    code = main(["--count-text", "banana", "--char", "a"])
    assert code == 0


def test_main_json_and_export(tmp_path, capsys):
    from ad_project.cli import main
    # Test --json flag
    code = main(["--json"])
    assert code == 0
    captured = capsys.readouterr()
    assert '"cpu"' in captured.out

    # Test --export flag
    out_file = tmp_path / "cli_export.json"
    code = main(["--export", str(out_file)])
    assert code == 0
    assert out_file.exists()


def test_run_single_snapshot():
    console = Console(width=100)
    monitor = SystemMonitor()
    code = run_single_snapshot(console, monitor, interval=1.0)
    assert code == 0

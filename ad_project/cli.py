"""
Command-line interface and main event loop for Terminal System Monitor.
"""

import argparse
import os
import signal
import sys
import time

from rich.console import Console
from rich.live import Live

from ad_project import __title__, __version__
from ad_project.collectors import SystemMonitor
from ad_project.ui import render_dashboard
from ad_project.utils import NonBlockingInput


def parse_args(args=None) -> argparse.Namespace:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        prog="ad-project",
        description="A lightweight, real-time, cross-platform terminal system monitor by anzydev.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument(
        "-i",
        "--interval",
        type=float,
        default=1.5,
        help="Refresh interval in seconds (min: 0.2, max: 60.0)",
    )
    parser.add_argument(
        "--once",
        action="store_true",
        help="Print a single system snapshot and exit (ideal for scripting and cron)",
    )
    parser.add_argument(
        "-v",
        "--version",
        action="version",
        version=f"{__title__} v{__version__}",
    )
    return parser.parse_args(args)


def run_single_snapshot(console: Console, monitor: SystemMonitor, interval: float) -> int:
    """Collect and print a single system metrics snapshot."""
    # Warm up CPU counters slightly for non-zero reading on first snapshot
    time.sleep(0.15)
    snapshot = monitor.collect_snapshot()
    dashboard = render_dashboard(
        snapshot=snapshot,
        interval=interval,
        console_width=console.width,
        console_height=console.height,
    )
    console.print(dashboard)
    return 0


def run_live_monitor(console: Console, monitor: SystemMonitor, initial_interval: float) -> int:
    """Run real-time auto-refreshing terminal dashboard."""
    interval = max(0.2, min(60.0, initial_interval))
    paused = False

    # Warm up CPU/network metrics
    time.sleep(0.1)

    # Use alternate screen so user terminal history remains clean
    use_alt_screen = console.is_terminal and not bool(os.getenv("NO_ALT_SCREEN"))

    try:
        with Live(
            console=console,
            screen=use_alt_screen,
            auto_refresh=False,
            redirect_stderr=False,
        ) as live:
            with NonBlockingInput() as key_reader:
                while True:
                    # Collect snapshot
                    snapshot = monitor.collect_snapshot()
                    dashboard = render_dashboard(
                        snapshot=snapshot,
                        interval=interval,
                        console_width=console.width,
                        console_height=console.height,
                    )
                    live.update(dashboard, refresh=True)

                    # Sleep loop with interactive key polling
                    start_time = time.monotonic()
                    while time.monotonic() - start_time < interval:
                        # Poll key with small timeout
                        key = key_reader.get_key(timeout=0.1)
                        if key:
                            if key in ("q", "x", "\x03"):  # 'q', 'x', or Ctrl+C
                                return 0
                            elif key == "r":
                                # Immediate refresh
                                break
                            elif key in ("+", "="):
                                interval = min(10.0, round(interval + 0.5, 1))
                                break
                            elif key in ("-", "_"):
                                interval = max(0.5, round(interval - 0.5, 1))
                                break
                            elif key in ("p", " "):
                                paused = not paused
                                while paused:
                                    pk = key_reader.get_key(timeout=0.2)
                                    if pk in ("q", "x", "\x03"):
                                        return 0
                                    elif pk in ("p", " ", "r"):
                                        paused = False
                                        break

    except KeyboardInterrupt:
        return 0
    except Exception as e:
        console.print(f"[bold red]Error running system monitor:[/] {e}")
        return 1

    return 0


def main(args=None) -> int:
    """Main CLI entrypoint."""
    parsed = parse_args(args)
    console = Console()
    monitor = SystemMonitor()

    def sig_handler(sig, frame):
        # Graceful exit on SIGTERM/SIGINT
        sys.exit(0)

    try:
        signal.signal(signal.SIGINT, sig_handler)
        if hasattr(signal, "SIGTERM"):
            signal.signal(signal.SIGTERM, sig_handler)
    except Exception:
        pass

    if parsed.once:
        return run_single_snapshot(console, monitor, parsed.interval)

    return run_live_monitor(console, monitor, parsed.interval)


if __name__ == "__main__":
    sys.exit(main())


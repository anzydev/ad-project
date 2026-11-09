"""
Utility functions for unit formatting, UI styling, and cross-platform terminal input.
"""

import os
import sys
import time
from typing import Optional
from rich.text import Text


def format_bytes(bytes_count: float, decimal_places: int = 1) -> str:
    """
    Format a byte count into a human-readable string (B, KB, MB, GB, TB).
    """
    if bytes_count < 0:
        return "0 B"
    units = ["B", "KB", "MB", "GB", "TB", "PB"]
    unit_index = 0
    val = float(bytes_count)
    while val >= 1024.0 and unit_index < len(units) - 1:
        val /= 1024.0
        unit_index += 1

    if unit_index == 0:
        return f"{int(val)} B"
    return f"{val:.{decimal_places}f} {units[unit_index]}"


def format_rate(bytes_per_sec: float) -> str:
    """
    Format a transfer rate in bytes per second into human-readable rate string.
    """
    if bytes_per_sec <= 0:
        return "0.0 B/s"
    return f"{format_bytes(bytes_per_sec, decimal_places=1)}/s"


def format_uptime(seconds: float) -> str:
    """
    Convert elapsed seconds into a readable uptime string (e.g., '2d 5h 34m' or '1h 12m').
    """
    total_seconds = max(0, int(seconds))
    days, remainder = divmod(total_seconds, 86400)
    hours, remainder = divmod(remainder, 3600)
    minutes, secs = divmod(remainder, 60)

    parts = []
    if days > 0:
        parts.append(f"{days}d")
    if hours > 0 or days > 0:
        parts.append(f"{hours}h")
    parts.append(f"{minutes}m")

    # If uptime is less than 1 hour, also include seconds
    if days == 0 and hours == 0:
        parts.append(f"{secs}s")

    return " ".join(parts)


def format_frequency(freq_mhz: Optional[float]) -> str:
    """
    Format CPU frequency gracefully across platforms.
    """
    if freq_mhz is None or freq_mhz <= 0:
        return "N/A"
    # Some platforms (e.g. Apple Silicon on certain kernels) report frequency in GHz directly (< 100)
    if freq_mhz < 100:
        return f"{freq_mhz:.2f} GHz"
    if freq_mhz >= 1000:
        return f"{freq_mhz / 1000.0:.2f} GHz"
    return f"{freq_mhz:.0f} MHz"


def get_percent_color(percent: float) -> str:
    """
    Return appropriate Rich color name based on utilization percentage.
    - Green: < 60%
    - Yellow: 60% - 85%
    - Red: >= 85%
    """
    if percent >= 85.0:
        return "bright_red"
    if percent >= 60.0:
        return "bright_yellow"
    return "bright_green"


def create_progress_bar(
    percent: float,
    width: int = 12,
    fill_char: str = "█",
    empty_char: str = "░",
    show_percent: bool = True
) -> Text:
    """
    Create a colored unicode progress bar with consistent styling.
    """
    pct = max(0.0, min(100.0, percent))
    filled_count = int(round((pct / 100.0) * width))
    empty_count = max(0, width - filled_count)
    color = get_percent_color(pct)

    bar = Text()
    bar.append(fill_char * filled_count, style=color)
    bar.append(empty_char * empty_count, style="dim")

    if show_percent:
        bar.append(f" {pct:5.1f}%", style=f"bold {color}")

    return bar


class NonBlockingInput:
    """
    Cross-platform context manager for reading non-blocking single keypresses.
    Supports Unix (macOS, Linux) and Windows, with safe fallback when non-interactive.
    """

    def __init__(self):
        self.is_windows = os.name == "nt"
        self.old_settings = None
        self.is_tty = sys.stdin.isatty()

    def __enter__(self):
        if not self.is_windows and self.is_tty:
            try:
                import termios
                import tty
                self.old_settings = termios.tcgetattr(sys.stdin.fileno())
                tty.setcbreak(sys.stdin.fileno())
            except Exception:
                self.old_settings = None
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if not self.is_windows and self.old_settings is not None:
            try:
                import termios
                termios.tcsetattr(sys.stdin.fileno(), termios.TCSADRAIN, self.old_settings)
            except Exception:
                pass

    def get_key(self, timeout: float = 0.0) -> Optional[str]:
        """
        Poll for a single character keypress without blocking.
        Returns the character or None if no input is ready.
        """
        if not self.is_tty:
            if timeout > 0:
                time.sleep(timeout)
            return None

        if self.is_windows:
            try:
                import msvcrt
                if timeout > 0:
                    time.sleep(timeout)
                if msvcrt.kbhit():
                    ch = msvcrt.getch()
                    return ch.decode("utf-8", errors="ignore").lower()
            except Exception:
                return None
            return None

        # POSIX (macOS, Linux)
        if self.old_settings is None:
            if timeout > 0:
                time.sleep(timeout)
            return None

        try:
            import select
            rlist, _, _ = select.select([sys.stdin], [], [], max(0.0, timeout))
            if rlist:
                ch = sys.stdin.read(1)
                return ch.lower() if ch else None
        except Exception:
            return None
        return None


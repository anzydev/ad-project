"""
Unit tests for UI rendering and layout adaptation.
"""

from rich.console import Console

from ad_project.collectors import SystemMonitor
from ad_project.ui import (
    _clean_mount_label,
    render_cpu_panel,
    render_dashboard,
    render_disk_panel,
    render_footer,
    render_header,
    render_memory_panel,
    render_net_battery_panel,
    render_process_panel,
)


def test_clean_mount_label():
    assert _clean_mount_label("/") == "/"
    assert _clean_mount_label("C:\\") == "C:\\"
    assert _clean_mount_label("/System/Volumes/Data") == "System Data"
    assert _clean_mount_label("/Volumes/BackupDisk") == "BackupDisk"


def test_ui_components_render():
    monitor = SystemMonitor()
    snapshot = monitor.collect_snapshot()

    header = render_header(
        snapshot.system_info,
        snapshot.uptime_formatted,
        interval=1.5,
        timestamp=snapshot.timestamp,
    )
    assert header is not None

    cpu_panel = render_cpu_panel(snapshot.cpu)
    assert cpu_panel is not None

    mem_panel = render_memory_panel(snapshot.memory)
    assert mem_panel is not None

    disk_panel = render_disk_panel(snapshot.disk)
    assert disk_panel is not None

    net_bat_panel = render_net_battery_panel(snapshot.network, snapshot.battery)
    assert net_bat_panel is not None

    proc_panel = render_process_panel(snapshot.top_processes)
    assert proc_panel is not None

    footer = render_footer(interval=1.5)
    assert footer is not None


def test_dashboard_wide_and_narrow():
    monitor = SystemMonitor()
    snapshot = monitor.collect_snapshot()

    console_wide = Console(width=110, height=35)
    dash_wide = render_dashboard(
        snapshot,
        interval=1.5,
        console_width=console_wide.width,
        console_height=console_wide.height,
    )
    console_wide.print(dash_wide)

    console_narrow = Console(width=75, height=30)
    dash_narrow = render_dashboard(
        snapshot,
        interval=1.5,
        console_width=console_narrow.width,
        console_height=console_narrow.height,
    )
    console_narrow.print(dash_narrow)

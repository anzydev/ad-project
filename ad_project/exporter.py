"""
System snapshot export utilities for ad-project.
Provides serialization of monitoring metrics to JSON and text summaries.
"""

import json
from dataclasses import asdict
from typing import Any, Dict, Optional

from ad_project.models import DashboardSnapshot


def snapshot_to_dict(snapshot: DashboardSnapshot) -> Dict[str, Any]:
    """
    Convert a DashboardSnapshot into a JSON-serializable dictionary.

    Args:
        snapshot: DashboardSnapshot instance.

    Returns:
        Dictionary representation of system metrics.
    """
    data = asdict(snapshot)
    return data


def export_snapshot_to_json(
    snapshot: DashboardSnapshot,
    file_path: Optional[str] = None,
    indent: int = 2,
) -> str:
    """
    Export snapshot metrics to a formatted JSON string, and optionally save to file.

    Args:
        snapshot: Dashboard metrics snapshot.
        file_path: Optional file path to write JSON.
        indent: JSON indentation spaces.

    Returns:
        JSON formatted string.
    """
    payload = snapshot_to_dict(snapshot)
    json_str = json.dumps(payload, indent=indent, default=str)
    if file_path:
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(json_str)
    return json_str


def export_snapshot_summary(snapshot: DashboardSnapshot) -> str:
    """
    Generate a quick plaintext summary of key system metrics.

    Args:
        snapshot: Dashboard metrics snapshot.

    Returns:
        Multi-line plain text summary.
    """
    sys_info = snapshot.system_info
    cpu = snapshot.cpu
    mem = snapshot.memory
    battery = snapshot.battery

    lines = [
        f"Host: {sys_info.hostname} | OS: {sys_info.os_name} {sys_info.os_release}",
        f"CPU: {cpu.overall_percent:.1f}% across {cpu.core_count_logical} cores",
        f"RAM: {mem.ram_percent:.1f}% ({mem.ram_used / (1024**3):.1f} GB used / {mem.ram_total / (1024**3):.1f} GB)",
        f"Disks Monitored: {len(snapshot.disk.partitions)}",
        f"Top Processes: {len(snapshot.top_processes)} listed",
    ]
    if battery.has_battery and battery.percent is not None:
        lines.append(f"Battery: {battery.percent:.1f}% ({'Charging' if battery.power_plugged else 'Discharging'})")
    return "\n".join(lines)

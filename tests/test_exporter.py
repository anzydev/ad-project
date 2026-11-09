"""
Unit tests for system snapshot exporter.
"""

import json
from ad_project.collectors import SystemMonitor
from ad_project.exporter import (
    snapshot_to_dict,
    export_snapshot_to_json,
    export_snapshot_summary,
)


def test_snapshot_to_dict():
    monitor = SystemMonitor()
    snapshot = monitor.collect_snapshot()
    data = snapshot_to_dict(snapshot)

    assert isinstance(data, dict)
    assert "cpu" in data
    assert "memory" in data
    assert "disk" in data
    assert "network" in data
    assert "system_info" in data
    assert "top_processes" in data


def test_export_snapshot_to_json(tmp_path):
    monitor = SystemMonitor()
    snapshot = monitor.collect_snapshot()

    # Test string output
    json_str = export_snapshot_to_json(snapshot)
    parsed = json.loads(json_str)
    assert parsed["cpu"]["core_count_logical"] > 0

    # Test file output
    out_file = tmp_path / "snapshot.json"
    result = export_snapshot_to_json(snapshot, file_path=str(out_file))
    assert out_file.exists()
    assert out_file.read_text(encoding="utf-8") == result


def test_export_snapshot_summary():
    monitor = SystemMonitor()
    snapshot = monitor.collect_snapshot()
    summary = export_snapshot_summary(snapshot)

    assert "Host:" in summary
    assert "CPU:" in summary
    assert "RAM:" in summary

"""
Unit tests for system metrics collectors and graceful fallbacks.
"""

from unittest.mock import MagicMock, patch
import pytest

from ad_project.collectors import (
    BatteryCollector,
    CPUCollector,
    DiskCollector,
    MemoryCollector,
    NetworkTracker,
    ProcessCollector,
    SystemInfoCollector,
    SystemMonitor,
)


def test_cpu_collector():
    collector = CPUCollector()
    metrics = collector.collect()
    assert isinstance(metrics.overall_percent, float)
    assert isinstance(metrics.per_core_percent, list)
    assert metrics.core_count_physical >= 1
    assert metrics.core_count_logical >= 1


def test_memory_collector():
    collector = MemoryCollector()
    metrics = collector.collect()
    assert metrics.ram_total > 0
    assert 0.0 <= metrics.ram_percent <= 100.0
    assert metrics.swap_total >= 0
    assert 0.0 <= metrics.swap_percent <= 100.0


def test_disk_collector():
    collector = DiskCollector()
    metrics = collector.collect()
    assert len(metrics.partitions) > 0
    for part in metrics.partitions:
        assert part.total > 0
        assert 0.0 <= part.percent <= 100.0
        assert len(part.mountpoint) > 0


def test_network_tracker():
    tracker = NetworkTracker()
    metrics = tracker.collect()
    assert metrics.bytes_sent >= 0
    assert metrics.bytes_recv >= 0
    assert metrics.upload_speed_bps >= 0.0
    assert metrics.download_speed_bps >= 0.0


def test_battery_collector_real():
    collector = BatteryCollector()
    metrics = collector.collect()
    assert isinstance(metrics.has_battery, bool)
    assert metrics.status_text is not None


def test_battery_collector_no_battery_fallback():
    collector = BatteryCollector()
    with patch("psutil.sensors_battery", return_value=None):
        metrics = collector.collect()
        assert metrics.has_battery is False
        assert metrics.percent is None
        assert "No Battery" in metrics.status_text


def test_battery_collector_mock_charging():
    collector = BatteryCollector()
    mock_bat = MagicMock(percent=82.5, power_plugged=True, secsleft=-1)
    with patch("psutil.sensors_battery", return_value=mock_bat):
        metrics = collector.collect()
        assert metrics.has_battery is True
        assert metrics.percent == 82.5
        assert "Charging" in metrics.status_text


def test_system_info_collector():
    collector = SystemInfoCollector()
    info = collector.collect()
    assert len(info.hostname) > 0
    assert len(info.os_name) > 0
    assert len(info.architecture) > 0
    assert len(info.cpu_brand) > 0
    assert info.boot_time > 0


def test_process_collector():
    collector = ProcessCollector()
    procs = collector.collect(limit=5)
    assert isinstance(procs, list)
    assert len(procs) <= 5
    for p in procs:
        assert p.pid > 0
        assert len(p.name) > 0
        assert p.memory_percent >= 0.0
        assert p.memory_rss >= 0


def test_system_monitor_snapshot():
    monitor = SystemMonitor()
    snapshot = monitor.collect_snapshot()
    assert snapshot.timestamp > 0
    assert snapshot.uptime_seconds >= 0
    assert snapshot.cpu is not None
    assert snapshot.memory is not None
    assert snapshot.disk is not None
    assert snapshot.network is not None
    assert snapshot.battery is not None
    assert isinstance(snapshot.top_processes, list)


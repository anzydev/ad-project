"""
Unit tests for data model initialization and serialization.
"""

from ad_project.models import (
    BatteryMetrics,
    CPUMetrics,
    DashboardSnapshot,
    DiskMetrics,
    DiskPartitionUsage,
    MemoryMetrics,
    NetworkMetrics,
    ProcessInfo,
    SystemInfo,
)


def test_models_creation():
    cpu = CPUMetrics(
        overall_percent=25.0,
        per_core_percent=[20.0, 30.0],
        core_count_physical=2,
        core_count_logical=4,
        freq_current_mhz=2400.0,
        load_average=(1.0, 0.8, 0.5),
    )
    assert cpu.overall_percent == 25.0
    assert len(cpu.per_core_percent) == 2

    mem = MemoryMetrics(
        ram_total=16000000000,
        ram_used=8000000000,
        ram_available=8000000000,
        ram_free=4000000000,
        ram_percent=50.0,
        swap_total=2000000000,
        swap_used=500000000,
        swap_free=1500000000,
        swap_percent=25.0,
    )
    assert mem.ram_percent == 50.0

    disk_part = DiskPartitionUsage(
        device="/dev/sda1",
        mountpoint="/",
        fstype="ext4",
        total=500000000000,
        used=100000000000,
        free=400000000000,
        percent=20.0,
    )
    disk = DiskMetrics(partitions=[disk_part])
    assert len(disk.partitions) == 1

    net = NetworkMetrics(
        bytes_sent=1000,
        bytes_recv=2000,
        upload_speed_bps=500.0,
        download_speed_bps=1000.0,
    )
    assert net.upload_speed_bps == 500.0

    bat = BatteryMetrics(
        has_battery=True,
        percent=85.0,
        power_plugged=False,
        seconds_left=7200,
        status_text="Discharging 🔋",
    )
    assert bat.percent == 85.0

    sys_info = SystemInfo(
        hostname="test-host",
        os_name="Linux",
        os_release="6.1.0",
        os_version="Debian",
        architecture="x86_64",
        cpu_brand="Test CPU @ 2.50GHz",
        boot_time=1700000000.0,
        python_version="3.11.0",
    )
    assert sys_info.hostname == "test-host"

    proc = ProcessInfo(
        pid=1234,
        name="python",
        username="user",
        cpu_percent=12.5,
        memory_percent=3.2,
        memory_rss=104857600,
        status="running",
    )
    assert proc.pid == 1234

    snapshot = DashboardSnapshot(
        timestamp=1700001000.0,
        system_info=sys_info,
        uptime_seconds=1000.0,
        uptime_formatted="16m 40s",
        cpu=cpu,
        memory=mem,
        disk=disk,
        network=net,
        battery=bat,
        top_processes=[proc],
    )
    assert snapshot.uptime_seconds == 1000.0
    assert len(snapshot.top_processes) == 1


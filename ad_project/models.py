"""
Data models representing system metrics and dashboard snapshots.
"""

from dataclasses import dataclass, field
from typing import List, Optional, Tuple


@dataclass
class CPUMetrics:
    """CPU metrics including overall usage, per-core usage, and frequency."""
    overall_percent: float
    per_core_percent: List[float]
    core_count_physical: int
    core_count_logical: int
    freq_current_mhz: Optional[float] = None
    freq_min_mhz: Optional[float] = None
    freq_max_mhz: Optional[float] = None
    load_average: Optional[Tuple[float, float, float]] = None


@dataclass
class MemoryMetrics:
    """RAM and Swap memory metrics."""
    ram_total: int
    ram_used: int
    ram_available: int
    ram_free: int
    ram_percent: float
    swap_total: int
    swap_used: int
    swap_free: int
    swap_percent: float


@dataclass
class DiskPartitionUsage:
    """Usage metrics for a single disk partition or mountpoint."""
    device: str
    mountpoint: str
    fstype: str
    total: int
    used: int
    free: int
    percent: float


@dataclass
class DiskMetrics:
    """List of all relevant disk partition usages."""
    partitions: List[DiskPartitionUsage] = field(default_factory=list)


@dataclass
class NetworkMetrics:
    """Network I/O rates and cumulative metrics."""
    bytes_sent: int
    bytes_recv: int
    upload_speed_bps: float
    download_speed_bps: float
    packets_sent: int = 0
    packets_recv: int = 0


@dataclass
class BatteryMetrics:
    """Battery percentage and power state."""
    has_battery: bool
    percent: Optional[float] = None
    power_plugged: Optional[bool] = None
    seconds_left: Optional[int] = None
    status_text: str = "N/A"


@dataclass
class SystemInfo:
    """Static and semi-static host hardware and OS information."""
    hostname: str
    os_name: str
    os_release: str
    os_version: str
    architecture: str
    cpu_brand: str
    boot_time: float
    python_version: str


@dataclass
class ProcessInfo:
    """Metrics for an individual running process."""
    pid: int
    name: str
    username: str
    cpu_percent: float
    memory_percent: float
    memory_rss: int
    status: str


@dataclass
class DashboardSnapshot:
    """Consolidated system state at a specific point in time."""
    timestamp: float
    system_info: SystemInfo
    uptime_seconds: float
    uptime_formatted: str
    cpu: CPUMetrics
    memory: MemoryMetrics
    disk: DiskMetrics
    network: NetworkMetrics
    battery: BatteryMetrics
    top_processes: List[ProcessInfo] = field(default_factory=list)


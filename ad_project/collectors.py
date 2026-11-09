"""
Metrics collectors using psutil with cross-platform compatibility and graceful fallbacks.
"""

import os
import platform
import subprocess
import time
from typing import Dict, List, Optional, Tuple

import psutil

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
from ad_project.utils import format_uptime


class CPUCollector:
    """Collects CPU metrics including per-core usage and frequencies."""

    def __init__(self):
        # Initial non-blocking call to initialize CPU counters
        psutil.cpu_percent(interval=None, percpu=True)
        psutil.cpu_percent(interval=None)

    def collect(self) -> CPUMetrics:
        overall = psutil.cpu_percent(interval=None)
        per_core = psutil.cpu_percent(interval=None, percpu=True)
        phys_cores = psutil.cpu_count(logical=False) or psutil.cpu_count(logical=True) or 1
        log_cores = psutil.cpu_count(logical=True) or phys_cores

        freq_curr, freq_min, freq_max = None, None, None
        try:
            freq = psutil.cpu_freq()
            if freq:
                freq_curr = freq.current if freq.current > 0 else None
                freq_min = freq.min if freq.min > 0 else None
                freq_max = freq.max if freq.max > 0 else None
        except Exception:
            pass

        load_avg = None
        if hasattr(os, "getloadavg"):
            try:
                load_avg = os.getloadavg()
            except Exception:
                pass

        return CPUMetrics(
            overall_percent=overall,
            per_core_percent=per_core,
            core_count_physical=phys_cores,
            core_count_logical=log_cores,
            freq_current_mhz=freq_curr,
            freq_min_mhz=freq_min,
            freq_max_mhz=freq_max,
            load_average=load_avg,
        )


class MemoryCollector:
    """Collects RAM and Swap utilization."""

    def collect(self) -> MemoryMetrics:
        vm = psutil.virtual_memory()
        sm = psutil.swap_memory()

        return MemoryMetrics(
            ram_total=vm.total,
            ram_used=vm.used,
            ram_available=vm.available,
            ram_free=vm.free,
            ram_percent=vm.percent,
            swap_total=sm.total,
            swap_used=sm.used,
            swap_free=sm.free,
            swap_percent=sm.percent,
        )


class DiskCollector:
    """Collects disk partitions and usage, safely filtering out system-internal volumes."""

    def __init__(self):
        self.is_mac = platform.system() == "Darwin"
        self.is_linux = platform.system() == "Linux"
        self.is_windows = os.name == "nt"

    def collect(self) -> DiskMetrics:
        partitions: List[DiskPartitionUsage] = []
        seen_devices = set()

        try:
            parts = psutil.disk_partitions(all=False)
        except Exception:
            parts = []

        for p in parts:
            # Filter out virtual / internal system volumes
            if self.is_mac:
                # Exclude APFS internal volumes, keeping user Data and Root
                if p.mountpoint.startswith("/System/Volumes/") and p.mountpoint != "/System/Volumes/Data":
                    continue
            elif self.is_linux:
                if p.fstype in ("squashfs", "iso9660", "tmpfs", "devtmpfs", "overlay", "ramfs"):
                    continue

            try:
                usage = psutil.disk_usage(p.mountpoint)
                dev_key = (p.device, usage.total)
                if dev_key in seen_devices and p.mountpoint not in ("/", "C:\\"):
                    continue
                seen_devices.add(dev_key)

                partitions.append(
                    DiskPartitionUsage(
                        device=p.device,
                        mountpoint=p.mountpoint,
                        fstype=p.fstype,
                        total=usage.total,
                        used=usage.used,
                        free=usage.free,
                        percent=usage.percent,
                    )
                )
            except (PermissionError, FileNotFoundError, OSError):
                continue

        # Fallback to root if no partitions were gathered
        if not partitions:
            root_path = "C:\\" if self.is_windows else "/"
            try:
                root_usage = psutil.disk_usage(root_path)
                partitions.append(
                    DiskPartitionUsage(
                        device=root_path,
                        mountpoint=root_path,
                        fstype="unknown",
                        total=root_usage.total,
                        used=root_usage.used,
                        free=root_usage.free,
                        percent=root_usage.percent,
                    )
                )
            except Exception:
                pass

        return DiskMetrics(partitions=partitions)


class NetworkTracker:
    """Calculates upload and download rates based on counter deltas between samples."""

    def __init__(self):
        self.last_sent: Optional[int] = None
        self.last_recv: Optional[int] = None
        self.last_time: Optional[float] = None
        # Initialize
        self._sample()

    def _sample(self) -> Tuple[int, int, int, int]:
        try:
            io = psutil.net_io_counters()
            return io.bytes_sent, io.bytes_recv, io.packets_sent, io.packets_recv
        except Exception:
            return 0, 0, 0, 0

    def collect(self) -> NetworkMetrics:
        sent, recv, pkts_sent, pkts_recv = self._sample()
        now = time.monotonic()

        up_speed = 0.0
        down_speed = 0.0

        if self.last_time is not None and self.last_sent is not None and self.last_recv is not None:
            elapsed = now - self.last_time
            if elapsed > 0:
                delta_sent = sent - self.last_sent
                delta_recv = recv - self.last_recv
                # Guard against counter rollover / resets
                if delta_sent >= 0:
                    up_speed = delta_sent / elapsed
                if delta_recv >= 0:
                    down_speed = delta_recv / elapsed

        self.last_sent = sent
        self.last_recv = recv
        self.last_time = now

        return NetworkMetrics(
            bytes_sent=sent,
            bytes_recv=recv,
            upload_speed_bps=up_speed,
            download_speed_bps=down_speed,
            packets_sent=pkts_sent,
            packets_recv=pkts_recv,
        )


class BatteryCollector:
    """Collects battery status with graceful fallback for desktops/servers."""

    def collect(self) -> BatteryMetrics:
        try:
            bat = psutil.sensors_battery()
        except Exception:
            bat = None

        if bat is None:
            return BatteryMetrics(
                has_battery=False,
                percent=None,
                power_plugged=True,
                seconds_left=None,
                status_text="AC Power (No Battery)",
            )

        pct = round(bat.percent, 1)
        plugged = bat.power_plugged
        secs_left = bat.secsleft if (bat.secsleft is not None and bat.secsleft > 0) else None

        if plugged:
            if pct >= 99.0:
                status = "Full (Plugged in)"
            else:
                status = "Charging ⚡"
        else:
            status = "Discharging 🔋"

        return BatteryMetrics(
            has_battery=True,
            percent=pct,
            power_plugged=plugged,
            seconds_left=secs_left,
            status_text=status,
        )


class SystemInfoCollector:
    """Collects static and semi-static host hardware and OS information."""

    def __init__(self):
        self._cached_cpu_brand: Optional[str] = None
        self._boot_time = psutil.boot_time()

    def get_cpu_brand(self) -> str:
        if self._cached_cpu_brand is not None:
            return self._cached_cpu_brand

        brand = ""
        system = platform.system()
        try:
            if system == "Darwin":
                out = subprocess.check_output(["sysctl", "-n", "machdep.cpu.brand_string"], stderr=subprocess.DEVNULL)
                brand = out.decode("utf-8", errors="ignore").strip()
            elif system == "Linux":
                if os.path.exists("/proc/cpuinfo"):
                    with open("/proc/cpuinfo", "r", encoding="utf-8", errors="ignore") as f:
                        for line in f:
                            if "model name" in line:
                                brand = line.split(":", 1)[1].strip()
                                break
            elif system == "Windows":
                brand = platform.processor() or "x86/x64 Processor"
        except Exception:
            pass

        if not brand:
            brand = platform.processor() or platform.machine() or "Generic CPU"

        self._cached_cpu_brand = brand
        return self._cached_cpu_brand

    def collect(self) -> SystemInfo:
        return SystemInfo(
            hostname=platform.node() or "localhost",
            os_name=platform.system(),
            os_release=platform.release(),
            os_version=platform.version(),
            architecture=platform.machine(),
            cpu_brand=self.get_cpu_brand(),
            boot_time=self._boot_time,
            python_version=platform.python_version(),
        )


class ProcessCollector:
    """Collects top memory-consuming processes and computes real CPU utilization."""

    def __init__(self):
        self._proc_cache: Dict[int, psutil.Process] = {}

    def collect(self, limit: int = 5) -> List[ProcessInfo]:
        procs: List[ProcessInfo] = []
        current_pids = set()

        for p in psutil.process_iter(["pid", "name", "username", "memory_percent", "memory_info", "status"]):
            try:
                info = p.info
                pid = info.get("pid")
                if pid is None or pid == 0:
                    continue

                current_pids.add(pid)
                mem_pct = info.get("memory_percent") or 0.0
                mem_info = info.get("memory_info")
                rss = mem_info.rss if mem_info else 0

                # Track Process object for non-blocking cpu_percent measurement
                if pid in self._proc_cache:
                    proc_obj = self._proc_cache[pid]
                    try:
                        cpu_pct = proc_obj.cpu_percent(interval=None)
                    except Exception:
                        cpu_pct = 0.0
                else:
                    self._proc_cache[pid] = p
                    try:
                        p.cpu_percent(interval=None)  # prime counter
                    except Exception:
                        pass
                    cpu_pct = 0.0

                procs.append(
                    ProcessInfo(
                        pid=pid,
                        name=info.get("name") or "unknown",
                        username=info.get("username") or "system",
                        cpu_percent=cpu_pct,
                        memory_percent=mem_pct,
                        memory_rss=rss,
                        status=info.get("status") or "running",
                    )
                )
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess, OSError):
                continue

        # Prune terminated PIDs from cache
        dead_pids = set(self._proc_cache.keys()) - current_pids
        for dead_pid in dead_pids:
            self._proc_cache.pop(dead_pid, None)

        # Sort descending by memory_percent
        procs.sort(key=lambda x: x.memory_percent, reverse=True)
        return procs[:limit]


class SystemMonitor:
    """Consolidated orchestrator for gathering all system telemetry."""

    def __init__(self):
        self.cpu_collector = CPUCollector()
        self.memory_collector = MemoryCollector()
        self.disk_collector = DiskCollector()
        self.network_tracker = NetworkTracker()
        self.battery_collector = BatteryCollector()
        self.system_info_collector = SystemInfoCollector()
        self.process_collector = ProcessCollector()

        # Cache static system info
        self._system_info = self.system_info_collector.collect()

    def get_system_info(self) -> SystemInfo:
        return self._system_info

    def collect_snapshot(self) -> DashboardSnapshot:
        now = time.time()
        uptime_sec = max(0.0, now - self._system_info.boot_time)

        return DashboardSnapshot(
            timestamp=now,
            system_info=self._system_info,
            uptime_seconds=uptime_sec,
            uptime_formatted=format_uptime(uptime_sec),
            cpu=self.cpu_collector.collect(),
            memory=self.memory_collector.collect(),
            disk=self.disk_collector.collect(),
            network=self.network_tracker.collect(),
            battery=self.battery_collector.collect(),
            top_processes=self.process_collector.collect(limit=5),
        )

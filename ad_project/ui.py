"""
Rich UI dashboard layout, panels, tables, and color-coded widgets.
"""

from datetime import datetime
from typing import List

from rich.console import Group, RenderableType
from rich.layout import Layout
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from ad_project.models import (
    BatteryMetrics,
    CPUMetrics,
    DashboardSnapshot,
    DiskMetrics,
    MemoryMetrics,
    NetworkMetrics,
    ProcessInfo,
    SystemInfo,
)
from ad_project.utils import (
    create_progress_bar,
    format_bytes,
    format_frequency,
    format_rate,
    get_percent_color,
)


def _clean_mount_label(mountpoint: str, max_len: int = 15) -> str:
    """Format mount point paths compactly for clean table rendering."""
    if mountpoint in ("/", "C:\\", "C:"):
        return mountpoint
    if mountpoint == "/System/Volumes/Data" or "/System/Volumes/Data" in mountpoint:
        return "System Data"
    if mountpoint.startswith("/Volumes/"):
        name = mountpoint[len("/Volumes/"):]
        return name[:max_len]
    if len(mountpoint) > max_len:
        return mountpoint[:max_len - 2] + ".."
    return mountpoint


def render_header(info: SystemInfo, uptime_formatted: str, interval: float, timestamp: float) -> Panel:
    """Render top header panel with host, OS, hardware, and uptime info."""
    time_str = datetime.fromtimestamp(timestamp).strftime("%H:%M:%S")

    grid = Table.grid(expand=True)
    grid.add_column(ratio=1)
    grid.add_column(ratio=1, justify="right")

    grid.add_row(
        Text.from_markup("[bold bright_cyan]⚡ AD-PROJECT MONITOR[/] [dim]v1.0.0[/]"),
        Text.from_markup(f"[dim]CPU:[/] [bold white]{info.cpu_brand}[/]"),
    )
    grid.add_row(
        Text.from_markup(f"[dim]Host:[/] [bold white]{info.hostname}[/]"),
        Text.from_markup(f"[dim]Uptime:[/] [bold bright_green]{uptime_formatted}[/]"),
    )
    grid.add_row(
        Text.from_markup(f"[dim]OS:[/]   [white]{info.os_name} {info.os_release} ({info.architecture})[/]"),
        Text.from_markup(f"[dim]Clock:[/] [white]{time_str}[/]  [dim]| Int:[/] [cyan]{interval:.1f}s[/]"),
    )

    return Panel(grid, border_style="bright_blue", padding=(0, 1))


def render_cpu_panel(cpu: CPUMetrics, max_core_rows: int = 5) -> Panel:
    """Render CPU utilization, frequency, load averages, and per-core progress bars."""
    content = Table.grid(expand=True)
    content.add_column()

    freq_str = format_frequency(cpu.freq_current_mhz)
    load_str = ""
    if cpu.load_average:
        l1, l5, l15 = cpu.load_average
        load_str = f"  [dim]Load Avg:[/] {l1:.2f}, {l5:.2f}, {l15:.2f}"

    overall_row = (
        Text.from_markup("[bold]Total:[/] ")
        + create_progress_bar(cpu.overall_percent, width=8)
        + Text.from_markup(f"  [dim]Freq:[/] {freq_str}{load_str}")
    )
    content.add_row(overall_row)
    content.add_row(Text(""))

    # Per-core grid
    core_count = len(cpu.per_core_percent)
    cols = 2 if core_count <= 16 else 4
    core_grid = Table.grid(expand=True, padding=(0, 1))
    for _ in range(cols):
        core_grid.add_column(ratio=1)

    rows_needed = (core_count + cols - 1) // cols
    display_rows = min(rows_needed, max_core_rows)

    for r in range(display_rows):
        cells = []
        for c in range(cols):
            idx = r * cols + c
            if idx < core_count:
                pct = cpu.per_core_percent[idx]
                cell = Text.from_markup(f"[dim]C{idx:02d}:[/] ") + create_progress_bar(pct, width=5)
            else:
                cell = Text("")
            cells.append(cell)
        core_grid.add_row(*cells)

    if rows_needed > max_core_rows:
        remaining = core_count - (display_rows * cols)
        core_grid.add_row(Text.from_markup(f"[dim]+ {remaining} more cores...[/]"))

    content.add_row(core_grid)

    title = f"[bold bright_cyan]🖥  CPU Metrics ({cpu.core_count_logical} Cores)[/]"
    return Panel(content, title=title, border_style="bright_cyan", padding=(0, 1))


def render_memory_panel(mem: MemoryMetrics) -> Panel:
    """Render RAM and Swap bars and utilization statistics."""
    grid = Table.grid(expand=True, padding=(0, 1))
    grid.add_column()

    ram_bar = create_progress_bar(mem.ram_percent, width=8)
    ram_used = format_bytes(mem.ram_used)
    ram_total = format_bytes(mem.ram_total)
    ram_avail = format_bytes(mem.ram_available)
    ram_free = format_bytes(mem.ram_free)

    grid.add_row(
        Text.from_markup("[bold]RAM:  [/]")
        + ram_bar
        + Text.from_markup(f" [dim]{ram_used} / {ram_total}[/]")
    )
    grid.add_row(Text.from_markup(f"[dim]      Free: {ram_free}  |  Avail: {ram_avail}[/]"))

    grid.add_row(Text(""))

    swap_bar = create_progress_bar(mem.swap_percent, width=8)
    swap_used = format_bytes(mem.swap_used)
    swap_total = format_bytes(mem.swap_total)
    swap_free = format_bytes(mem.swap_free)

    grid.add_row(
        Text.from_markup("[bold]Swap: [/]")
        + swap_bar
        + Text.from_markup(f" [dim]{swap_used} / {swap_total}[/]")
    )
    grid.add_row(Text.from_markup(f"[dim]      Free: {swap_free}[/]"))

    return Panel(grid, title="[bold bright_magenta]💾 Memory & Swap[/]", border_style="bright_magenta", padding=(0, 1))


def render_disk_panel(disk: DiskMetrics, max_rows: int = 4) -> Panel:
    """Render mounted disk partitions and usage bars."""
    table = Table(box=None, expand=True, padding=(0, 1), show_header=True, header_style="bold yellow")
    table.add_column("Mount", ratio=2, no_wrap=True)
    table.add_column("Usage", no_wrap=True)
    table.add_column("Used", justify="right", width=9)
    table.add_column("Total", justify="right", width=9)

    for part in disk.partitions[:max_rows]:
        label = _clean_mount_label(part.mountpoint)
        table.add_row(
            label,
            create_progress_bar(part.percent, width=6),
            format_bytes(part.used),
            format_bytes(part.total),
        )

    if len(disk.partitions) > max_rows:
        table.add_row(f"[dim]+ {len(disk.partitions) - max_rows} more...[/]", "", "", "")

    return Panel(table, title="[bold bright_yellow]💽 Disk Storage[/]", border_style="bright_yellow", padding=(0, 1))


def render_net_battery_panel(net: NetworkMetrics, bat: BatteryMetrics) -> Panel:
    """Render real-time network speeds and battery power metrics."""
    grid = Table.grid(expand=True, padding=(0, 1))
    grid.add_column()

    up_speed = format_rate(net.upload_speed_bps)
    down_speed = format_rate(net.download_speed_bps)
    tot_sent = format_bytes(net.bytes_sent)
    tot_recv = format_bytes(net.bytes_recv)

    grid.add_row(Text.from_markup(f"[bold bright_green]▲ Upload:[/]   [white]{up_speed}[/] [dim](Tot: {tot_sent})[/]"))
    grid.add_row(Text.from_markup(f"[bold bright_cyan]▼ Download:[/] [white]{down_speed}[/] [dim](Tot: {tot_recv})[/]"))
    grid.add_row(Text(""))

    # Battery line
    if bat.has_battery and bat.percent is not None:
        bat_bar = create_progress_bar(bat.percent, width=8)
        time_rem = ""
        if bat.seconds_left:
            mins_left = bat.seconds_left // 60
            hrs = mins_left // 60
            mins = mins_left % 60
            time_rem = f" [dim]({hrs}h {mins:02d}m)[/]"
        bat_row = (
            Text.from_markup("[bold yellow]Battery:[/]    ")
            + bat_bar
            + Text.from_markup(f"  [dim]{bat.status_text}{time_rem}[/]")
        )
    else:
        bat_row = Text.from_markup(f"[bold yellow]Battery:[/]    [dim]🔌 {bat.status_text}[/]")

    grid.add_row(bat_row)

    return Panel(grid, title="[bold bright_green]🌐 Network & 🔋 Battery[/]", border_style="bright_green", padding=(0, 1))


def render_process_panel(processes: List[ProcessInfo], console_width: int = 100) -> Panel:
    """Render top 5 memory-consuming processes in a styled table."""
    table = Table(box=None, expand=True, padding=(0, 1), show_header=True, header_style="bold bright_red")
    table.add_column("PID", justify="right", width=6, style="dim")
    table.add_column("Process Name", ratio=3, style="bold white", no_wrap=True)

    show_user = console_width >= 95
    if show_user:
        table.add_column("User", width=12, style="dim", no_wrap=True)

    table.add_column("CPU %", justify="right", width=7)
    table.add_column("Memory %", justify="right", width=13)
    table.add_column("RSS", justify="right", width=9)
    table.add_column("Status", justify="center", width=8)

    for proc in processes:
        cpu_col = get_percent_color(proc.cpu_percent)
        mem_bar = create_progress_bar(proc.memory_percent, width=5)
        rss_str = format_bytes(proc.memory_rss)
        status_style = "green" if proc.status.lower() in ("running", "active") else "dim"

        row = [
            str(proc.pid),
            proc.name,
        ]
        if show_user:
            row.append(proc.username)
        row.extend([
            f"[{cpu_col}]{proc.cpu_percent:5.1f}%[/]",
            mem_bar,
            rss_str,
            f"[{status_style}]{proc.status}[/]",
        ])
        table.add_row(*row)

    return Panel(table, title="[bold bright_red]🔥 Top 5 Memory Processes[/]", border_style="bright_red", padding=(0, 1))


def render_footer(interval: float) -> Panel:
    """Render interactive keybindings and status footer."""
    text = (
        "[bold bright_cyan][Q][/] Quit  [dim]|[/]  "
        "[bold bright_cyan][R][/] Refresh  [dim]|[/]  "
        "[bold bright_cyan][+][/]/[bold bright_cyan][-][/] Change Interval  [dim]|[/]  "
        f"[dim]Interval: [/][bold white]{interval:.1f}s[/]  [dim]|  Status: [/][bold bright_green]Active[/]"
    )
    return Panel(Text.from_markup(text, justify="center"), border_style="dim", padding=(0, 1))


def render_dashboard(
    snapshot: DashboardSnapshot,
    interval: float,
    console_width: int = 100,
    console_height: int = 30
) -> RenderableType:
    """
    Construct the responsive dashboard layout based on current terminal dimensions.
    """
    header_panel = render_header(
        snapshot.system_info,
        snapshot.uptime_formatted,
        interval,
        snapshot.timestamp,
    )
    cpu_panel = render_cpu_panel(snapshot.cpu)
    mem_panel = render_memory_panel(snapshot.memory)
    disk_panel = render_disk_panel(snapshot.disk)
    net_bat_panel = render_net_battery_panel(snapshot.network, snapshot.battery)
    proc_panel = render_process_panel(snapshot.top_processes, console_width=console_width)
    footer_panel = render_footer(interval)

    # In narrow terminals (< 85 columns), stack panels vertically for readability
    if console_width < 85:
        return Group(
            header_panel,
            cpu_panel,
            mem_panel,
            disk_panel,
            net_bat_panel,
            proc_panel,
            footer_panel,
        )

    # Standard wide layout with Rich Layout grid
    layout = Layout()
    layout.split_column(
        Layout(header_panel, name="header", size=5),
        Layout(name="body", ratio=1),
        Layout(proc_panel, name="proc", size=9),
        Layout(footer_panel, name="footer", size=3),
    )

    layout["body"].split_row(
        Layout(name="left", ratio=1),
        Layout(name="right", ratio=1),
    )

    layout["left"].split_column(
        Layout(cpu_panel, ratio=1),
        Layout(mem_panel, ratio=1),
    )

    layout["right"].split_column(
        Layout(disk_panel, ratio=1),
        Layout(net_bat_panel, ratio=1),
    )

    return layout

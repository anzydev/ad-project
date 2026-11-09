# ⚡ AD-Project: Terminal System Monitor (`admon`)

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Author: anzydev](https://img.shields.io/badge/author-anzydev-green.svg)](https://github.com/anzydev)
[![Platform](https://img.shields.io/badge/platform-macOS%20%7C%20Linux%20%7C%20Windows-lightgrey.svg)]()
[![Code Style: Rich](https://img.shields.io/badge/code%20style-rich-purple.svg)](https://github.com/Textualize/rich)
[![Tests: Passing](https://img.shields.io/badge/tests-24%20passed-brightgreen.svg)]()

A lightweight, modular, cross-platform terminal system monitor built with **Python**, **`psutil`**, and **`Rich`**.

Features a clean, real-time terminal dashboard with color-coded progress bars, organized panels, automatic auto-refreshing, interactive keybindings, and graceful fallbacks for desktop and virtualized environments.

Developed by [anzydev](https://github.com/anzydev).

---

## 🖥 Dashboard Preview

```text
╭──────────────────────────────────────────────────────────────────────────────╮
│ ⚡ AD-PROJECT MONITOR v1.0.0                                   CPU: Apple M4 │
│ Host: MacBook-Pro.local                                   Uptime: 3d 12h 45m │
│ OS:   Darwin 24.6.0 (arm64)                     Clock: 04:45:00  | Int: 1.5s │
╰──────────────────────────────────────────────────────────────────────────────╯
╭────────── 🖥  CPU Metrics (10 Cores) ───────────╮╭─────────────── 💽 Disk Storage ────────────────╮
│ Total: ██░░░░░░  25.0%  Freq: 4.00 GHz  Load   ││  Mount       Usage            Used      Total  │
│ Avg: 2.10, 1.95, 1.80                          ││  /           ░░░░░░   3.4%   10.5 GB   460.4 GB  │
│                                                ││  System Data ██░░░░  32.5%  143.2 GB   460.4 GB  │
│ C00: ██░░░  31.2%      C01: █░░░░  20.0%       ││  External    ████░░  63.0%   19.3 MB    31.3 MB  │
│ C02: █░░░░  15.0%      C03: ░░░░░   5.0%       ││                                                │
╰────────────────────────────────────────────────╯╰────────────────────────────────────────────────╯
╭─────────────── 💾 Memory & Swap ───────────────╮╭─────────── 🌐 Network & 🔋 Battery ────────────╮
│ RAM:  █████░░░  59.8% 8.3 GB / 16.0 GB         ││ ▲ Upload:   342.5 KB/s (Tot: 3.7 GB)           │
│       Free: 320.0 MB  |  Avail: 6.4 GB         ││ ▼ Download: 1.24 MB/s  (Tot: 1.4 GB)           │
│                                                ││                                                │
│ Swap: ██░░░░░░  29.4% 601.7 MB / 2.0 GB        ││ Battery:    █░░░░░░░  16.0%  Discharging 🔋    │
│       Free: 1.4 GB                             ││ (1h 45m)                                       │
╰────────────────────────────────────────────────╯╰────────────────────────────────────────────────╯
╭─────────────────────────────────── 🔥 Top 5 Memory Processes ────────────────────────────────────╮
│     PID  Process Name                           User            CPU %       Memory %        RSS  │
│   31616  Brave Browser Helper (Renderer)        username         0.0%   ░░░░░   4.3%   708.2 MB  │
│   31912  Brave Browser Helper (Renderer)        username         0.0%   ░░░░░   4.1%   672.3 MB  │
│   31535  Brave Browser Helper (Renderer)        username         0.0%   ░░░░░   3.8%   623.6 MB  │
│   28625  Brave Browser                          username         0.0%   ░░░░░   3.7%   610.0 MB  │
│   28776  Brave Browser Helper (Renderer)        username         0.0%   ░░░░░   2.1%   352.2 MB  │
╰──────────────────────────────────────────────────────────────────────────────────────────────────╯
╭──────────────────────────────────────────────────────────────────────────────────────────────────╮
│    [Q] Quit  |  [R] Refresh  |  [+]/[-] Change Interval  |  Interval: 1.5s  |  Status: Active    │
╰──────────────────────────────────────────────────────────────────────────────────────────────────╯
```

---

## ✨ Features

- **🖥 CPU Telemetry**: Overall utilization, per-core CPU bars (dynamically adapting to 4, 8, 16, 32+ cores), hardware CPU frequency, and Unix load averages (1m, 5m, 15m).
- **💾 Memory & Swap**: RAM used, total, available, and free space; Swap partition consumption; color-coded utilization thresholds.
- **🌐 Network Speeds & Bandwidth**: Real-time upload and download transfer rates (e.g. KB/s, MB/s) calculated over time deltas, plus cumulative data counters.
- **🔋 Battery & Power Health**: Current battery charge percentage, charging/discharging status indicator, and estimated runtime remaining. Gracefully handles desktop systems and servers without batteries (`🔌 AC Power (No Battery)`).
- **💽 Disk & Partitions**: Mounted drives and filesystems with storage meters. Intelligently filters out noisy macOS internal APFS system snapshots and Linux virtual filesystems (`squashfs`, `tmpfs`, `devtmpfs`).
- **🔥 Top 5 Memory Processes**: Live table tracking the top 5 memory-hungry processes by RSS and memory percentage, including PID, process name, username, status, and non-blocking CPU usage.
- **🎨 Modern Rich Terminal UI**: Responsive 2-column or stacked grid layout that auto-adapts to terminal width and height, utilizing Unicode blocks (`█`, `░`) and dynamic status alerts.
- **⚡ Interactive Keyboard Controls**: Modify refresh rates on the fly, trigger immediate refreshes, pause updates, or exit cleanly.
- **📸 Single-Snapshot Mode (`--once`)**: Ideal for cron jobs, CI/CD pipelines, piping, or shell scripts.
- **🛡 Robust Error Handling**: Catches transient process termination errors (`NoSuchProcess`, `AccessDenied`, `ZombieProcess`), unmounted drive I/O errors, and restores terminal settings upon termination (`Ctrl+C` or `q`).

---

## 🚀 Installation

### 1. Clone the Repository
```bash
git clone https://github.com/anzydev/ad-project.git
cd ad-project
```

### 2. Set Up Virtual Environment (Recommended)
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

Alternatively, install in editable mode to expose the `ad-project` and `admon` commands:
```bash
pip install -e .
```

---

## 💻 Usage

### Run Real-Time Dashboard
```bash
python main.py
```
Or if installed via pip:
```bash
admon
# or
ad-project
```

### Custom Refresh Interval
Set the update rate (in seconds):
```bash
python main.py -i 2.0
```

### Single Snapshot (Scripting / Headless)
Print the metrics once and exit immediately with exit code `0`:
```bash
python main.py --once
```

### Check Version & Help
```bash
python main.py --version
python main.py --help
```

---

## ⌨️ Interactive Keybindings

When running in real-time mode, control the dashboard directly from your keyboard without pressing `Enter`:

| Key | Action |
|:---:|:---|
| <kbd>q</kbd> or <kbd>x</kbd> | Exit the monitor and restore terminal cleanly |
| <kbd>r</kbd> | Force an immediate metrics refresh |
| <kbd>+</kbd> or <kbd>=</kbd> | Increase refresh interval by `0.5s` (slower updates, lower CPU) |
| <kbd>-</kbd> or <kbd>_</kbd> | Decrease refresh interval by `0.5s` (faster updates, down to `0.5s`) |
| <kbd>p</kbd> or <kbd>Space</kbd> | Pause / Resume real-time updates |
| <kbd>Ctrl+C</kbd> | Cleanly terminate application |

---

## 📂 Project Structure

```text
ad-project/
├── ad_project/
│   ├── __init__.py          # Package metadata and public exports
│   ├── __main__.py          # Entrypoint for `python -m ad_project`
│   ├── cli.py               # Argument parser, signal handler, and event loop
│   ├── collectors.py        # System, CPU, Memory, Disk, Network, Battery & Process collectors
│   ├── models.py            # Strongly typed Dataclasses for telemetry snapshots
│   ├── ui.py                # Rich dashboard layout, panels, tables, and color-coded bars
│   └── utils.py             # Formatters (bytes, rate, uptime, freq) & non-blocking input
├── tests/
│   ├── __init__.py
│   ├── test_cli.py          # Unit tests for CLI flags and snapshot runner
│   ├── test_collectors.py   # Unit tests for collectors and fallback mocks
│   ├── test_models.py       # Unit tests for dataclass validation
│   ├── test_ui.py           # Unit tests for responsive rendering across terminal widths
│   └── test_utils.py        # Unit tests for formatting logic and progress bars
├── main.py                  # Direct runner script (`python main.py`)
├── requirements.txt         # Core dependencies (`psutil`, `rich`)
├── pyproject.toml           # Packaging metadata (PEP 517/621) and CLI scripts
├── .gitignore               # Standard Python and OS gitignore
├── LICENSE                  # MIT License
└── README.md                # Project documentation and guide
```

---

## 🌐 Cross-Platform Compatibility

Tested and designed for **macOS**, **Linux**, and **Windows**:

| Metric | macOS | Linux | Windows | Fallback Behavior |
|:---|:---:|:---:|:---:|:---|
| **CPU % & Per-Core** | ✅ | ✅ | ✅ | Standard psutil counter |
| **CPU Frequency** | ✅ | ✅ | ✅ | Formatted in MHz/GHz or `N/A` if unavailable |
| **Load Averages** | ✅ | ✅ | ⚠️ *(N/A)* | Gracefully omitted on Windows |
| **RAM & Swap** | ✅ | ✅ | ✅ | Virtual memory & swap metrics |
| **Disk Partitions** | ✅ | ✅ | ✅ | Filters APFS system snapshots & Linux loop mounts |
| **Network I/O** | ✅ | ✅ | ✅ | Non-blocking delta rate calculation |
| **Battery Status** | ✅ | ✅ | ✅ | Falls back to `AC Power (No Battery)` on desktops/VMs |
| **Top 5 Processes** | ✅ | ✅ | ✅ | Handles `AccessDenied` and `NoSuchProcess` safely |

---

## 🧪 Running Unit Tests

Run the full test suite with `pytest`:
```bash
pytest -v
```

---

## 📄 License

This project is licensed under the [MIT License](LICENSE) by [anzydev](https://github.com/anzydev).

"""
AD-Project: Terminal System Monitor (ad_project)
A clean, real-time, cross-platform terminal dashboard using psutil and Rich.
"""

__title__ = "ad-project"
__version__ = "1.0.0"
__author__ = "anzydev"
__license__ = "MIT"

from ad_project.collectors import SystemMonitor
from ad_project.counter import CharStats, analyze_text, count_specific_char
from ad_project.models import DashboardSnapshot

__all__ = [
    "SystemMonitor",
    "DashboardSnapshot",
    "CharStats",
    "analyze_text",
    "count_specific_char",
    "__version__",
]

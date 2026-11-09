"""
AD-Project: Terminal System Monitor (ad_project)
A clean, real-time, cross-platform terminal dashboard using psutil and Rich.
"""

__title__ = "ad-project"
__version__ = "1.0.0"
__author__ = "anzydev"
__license__ = "MIT"

from ad_project.collectors import SystemMonitor
from ad_project.models import DashboardSnapshot

__all__ = ["SystemMonitor", "DashboardSnapshot", "__version__"]

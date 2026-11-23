"""Optional scheduled persistence of local monitor snapshots."""

import asyncio
import logging

from prisma import Prisma
from starlette.concurrency import run_in_threadpool

from ad_project.api.config import Settings
from ad_project.api.serialization import snapshot_record
from ad_project.collectors import SystemMonitor

logger = logging.getLogger(__name__)


async def collect_periodically(db: Prisma, settings: Settings, owner_id: str) -> None:
    """Persist snapshots at a bounded interval until application shutdown."""
    monitor = SystemMonitor()
    while True:
        try:
            snapshot = await run_in_threadpool(monitor.collect_snapshot)
            await db.snapshot.create(data=snapshot_record(snapshot, owner_id))
        except asyncio.CancelledError:
            raise
        except Exception:
            logger.exception("Background snapshot collection failed")
        await asyncio.sleep(settings.collection_interval_seconds)

"""Conversion helpers between monitor snapshots and persisted API records."""

import json
from datetime import datetime, timezone

from ad_project.models import DashboardSnapshot


def snapshot_payload(snapshot: DashboardSnapshot) -> dict:
    """Return a JSON-safe dictionary using the existing exporter contract."""
    from ad_project.exporter import snapshot_to_dict

    return snapshot_to_dict(snapshot)


def snapshot_record(snapshot: DashboardSnapshot, owner_id: str) -> dict:
    """Build Prisma input for one collected monitor snapshot."""
    payload = snapshot_payload(snapshot)
    return {
        "owner_id": owner_id,
        "captured_at": datetime.fromtimestamp(snapshot.timestamp, tz=timezone.utc),
        "cpu_percent": snapshot.cpu.overall_percent,
        "memory_percent": snapshot.memory.ram_percent,
        "payload": json.dumps(payload, default=str),
    }


def persisted_snapshot_response(record) -> dict:
    """Convert a Prisma record into the public response shape."""
    return {
        "id": record.id,
        "owner_id": record.owner_id,
        "captured_at": record.captured_at,
        "cpu_percent": record.cpu_percent,
        "memory_percent": record.memory_percent,
        "payload": json.loads(record.payload),
    }

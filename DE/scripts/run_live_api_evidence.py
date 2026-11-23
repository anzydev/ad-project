#!/usr/bin/env python3
"""Exercise the running FastAPI app and verify its writes directly in PostgreSQL."""
import json
import sys
import uuid
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

import httpx
import psycopg
from ad_project.api.config import get_settings

BASE = "http://127.0.0.1:8000"
DSN = get_settings().database_url


def assert_status(response, status, operation):
    assert response.status_code == status, f"{operation}: {response.status_code} {response.text}"
    print(f"{operation}: HTTP {status}")
    return response.json() if response.content else None


def main():
    email = f"de-live-{uuid.uuid4().hex}@example.org"
    user_id = None
    with httpx.Client(base_url=BASE, timeout=20) as api:
        health = assert_status(api.get("/api/v1/health"), 200, "API_HEALTH")
        assert health["database"] == "ok"
        try:
            registration = assert_status(
                api.post("/api/v1/auth/register", json={
                    "email": email, "password": "temporary-demo-password-123"
                }),
                201, "REGISTER",
            )
            user_id = registration["user"]["id"]
            auth = {"Authorization": f"Bearer {registration['access_token']}"}
            assert_status(
                api.post("/api/v1/auth/register", json={
                    "email": email, "password": "temporary-demo-password-123"
                }),
                409, "DUPLICATE_EMAIL_REJECTED",
            )
            snapshot = assert_status(
                api.post("/api/v1/snapshots/collect", headers=auth),
                201, "COLLECT_REAL_MAC_METRICS",
            )
            snapshot_id = snapshot["id"]
            with psycopg.connect(DSN) as db:
                record = db.execute(
                    'SELECT "cpu_percent", "memory_percent", "payload" '
                    'FROM "Snapshot" WHERE "id"=%s AND "owner_id"=%s',
                    (snapshot_id, user_id),
                ).fetchone()
            assert record is not None
            payload = json.loads(record[2])
            assert "cpu" in payload and "memory" in payload
            print("DATABASE_VERIFICATION: real monitoring snapshot persisted with CPU/memory payload")
            assert_status(api.get("/api/v1/snapshots", headers=auth), 200, "READ_HISTORY")
            alert = assert_status(
                api.post("/api/v1/alerts", headers=auth, json={
                    "metric": "cpu", "threshold": 75.0, "message": "CPU demo alert"
                }),
                201, "CREATE_ALERT",
            )
            assert_status(api.patch(
                f"/api/v1/alerts/{alert['id']}",
                headers=auth, json={"resolved": True},
            ), 200, "RESOLVE_ALERT")
            assert_status(api.delete(
                f"/api/v1/alerts/{alert['id']}", headers=auth,
            ), 204, "DELETE_ALERT")
            assert_status(api.delete(
                f"/api/v1/snapshots/{snapshot_id}", headers=auth,
            ), 204, "DELETE_SNAPSHOT")
            print("LIVE_API_INTEGRATION: PASS")
        finally:
            if user_id:
                with psycopg.connect(DSN) as db:
                    db.execute('DELETE FROM "User" WHERE "id"=%s', (user_id,))
                print("CLEANUP: temporary test user removed")


if __name__ == "__main__":
    main()

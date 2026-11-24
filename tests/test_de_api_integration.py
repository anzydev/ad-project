"""Real DB-backed API checks for the Data Engineering viva (skipped without PostgreSQL)."""

import uuid

import psycopg
import pytest
from fastapi.testclient import TestClient

try:
    from ad_project.api.app import app
except RuntimeError as exc:
    if "prisma" in str(exc).lower():
        pytest.skip("Prisma client not generated in this environment", allow_module_level=True)
    raise

from ad_project.api.config import get_settings


@pytest.fixture()
def live_api():
    dsn = get_settings().database_url
    try:
        with psycopg.connect(dsn, connect_timeout=2) as connection:
            connection.execute("SELECT 1")
    except psycopg.Error:
        pytest.skip("Local PostgreSQL development database is unavailable")

    created_users = []
    try:
        with TestClient(app) as client:
            yield client, created_users, dsn
    finally:
        if created_users:
            with psycopg.connect(dsn) as connection:
                connection.execute(
                    'DELETE FROM "User" WHERE "id" = ANY(%s)',
                    (created_users,),
                )


def test_actual_api_crud_validation_isolation_and_atomic_batch(live_api):
    client, user_ids, dsn = live_api

    def register():
        email = f"decheck-{uuid.uuid4().hex}@example.org"
        result = client.post(
            "/api/v1/auth/register",
            json={"email": email, "password": "example-test-passphrase-123"},
        )
        assert result.status_code == 201, result.text
        user_ids.append(result.json()["user"]["id"])
        return email, {"Authorization": f"Bearer {result.json()['access_token']}"}

    email_a, auth_a = register()
    _, auth_b = register()

    duplicate = client.post(
        "/api/v1/auth/register",
        json={"email": email_a, "password": "example-test-passphrase-123"},
    )
    assert duplicate.status_code == 409, duplicate.text

    def metrics(cpu=24.5, memory=45.0):
        return {"cpu": {"overall_percent": cpu}, "memory": {"ram_percent": memory}}

    assert client.post("/api/v1/snapshots", headers=auth_a, json={"payload": {}}).status_code == 422
    single = client.post(
        "/api/v1/snapshots", headers=auth_a, json={"payload": metrics()}
    )
    assert single.status_code == 201, single.text
    record_id = single.json()["id"]

    assert client.patch(
        f"/api/v1/snapshots/{record_id}",
        headers=auth_b,
        json={"payload": metrics(99, 99)},
    ).status_code == 404
    assert client.delete(
        f"/api/v1/snapshots/{record_id}", headers=auth_b
    ).status_code == 404

    changed = client.patch(
        f"/api/v1/snapshots/{record_id}",
        headers=auth_a,
        json={"payload": metrics(32.5, 54.0)},
    )
    assert changed.status_code == 200, changed.text
    assert changed.json()["cpu_percent"] == 32.5
    with psycopg.connect(dsn) as connection:
        cpu, memory, payload = connection.execute(
            'SELECT "cpu_percent", "memory_percent", "payload" FROM "Snapshot" WHERE "id"=%s',
            (record_id,),
        ).fetchone()
    assert (cpu, memory) == (32.5, 54.0)
    assert '"overall_percent": 32.5' in payload

    count_before = client.get("/api/v1/snapshots", headers=auth_a).json()["total"]
    bad_batch = client.post(
        "/api/v1/snapshots/batch",
        headers=auth_a,
        json={"snapshots": [
            {"payload": metrics()},
            {"payload": metrics(150, 40)},
        ]},
    )
    assert bad_batch.status_code == 422, bad_batch.text
    count_after = client.get("/api/v1/snapshots", headers=auth_a).json()["total"]
    assert count_before == count_after

    batch = client.post(
        "/api/v1/snapshots/batch", headers=auth_a,
        json={"snapshots": [{"payload": metrics()}, {"payload": metrics(80, 60)}]},
    )
    assert batch.status_code == 201, batch.text
    assert len(batch.json()) == 2

    alert = client.post(
        "/api/v1/alerts", headers=auth_a,
        json={"metric": "cpu", "threshold": 70, "message": "CPU crossed threshold"},
    )
    assert alert.status_code == 201, alert.text
    alert_id = alert.json()["id"]
    assert client.get("/api/v1/alerts?resolved=false", headers=auth_a).status_code == 200
    assert client.patch(
        f"/api/v1/alerts/{alert_id}", headers=auth_b, json={"resolved": True},
    ).status_code == 404
    resolved = client.patch(
        f"/api/v1/alerts/{alert_id}", headers=auth_a, json={"resolved": True},
    )
    assert resolved.status_code == 200 and resolved.json()["resolved"] is True
    assert client.delete(f"/api/v1/alerts/{alert_id}", headers=auth_a).status_code == 204
    assert client.delete(f"/api/v1/snapshots/{record_id}", headers=auth_a).status_code == 204
    assert client.post(
        "/api/v1/alerts", headers=auth_a,
        json={"metric": "cpu", "threshold": 120, "message": "Invalid"},
    ).status_code == 422

import psycopg
import pytest

from ad_project.api.config import get_settings


DSN = get_settings().database_url


@pytest.fixture
def db():
    try:
        conn = psycopg.connect(DSN)
    except psycopg.Error:
        pytest.skip("PostgreSQL is not available")
    yield conn
    conn.close()


def test_snapshot_constraint_rejects_invalid_cpu(db):
    owner = db.execute('SELECT "id" FROM "User" LIMIT 1').fetchone()
    if owner is None:
        pytest.skip("No seed user available")
    db.rollback()
    with pytest.raises(psycopg.errors.CheckViolation):
        db.execute(
            'INSERT INTO "Snapshot" ("id","owner_id","captured_at","cpu_percent","memory_percent","payload") '
            'VALUES (%s,%s,now(),150.0,40.0,%s)',
            ("de-pytest-invalid-cpu", owner[0], '{"test":"constraint"}'),
        )
    db.rollback()


def test_transaction_commit_and_rollback(db):
    owner = db.execute('SELECT "id" FROM "User" LIMIT 1').fetchone()
    if owner is None:
        pytest.skip("No seed user available")

    db.execute(
        'INSERT INTO "Snapshot" ("id","owner_id","captured_at","cpu_percent","memory_percent","payload") '
        'VALUES (%s,%s,now(),21.0,31.0,%s)',
        ("de-pytest-commit", owner[0], '{"test":"commit"}'),
    )
    db.commit()
    assert db.execute(
        'SELECT count(*) FROM "Snapshot" WHERE "id"=%s',
        ("de-pytest-commit",),
    ).fetchone()[0] == 1

    db.execute(
        'INSERT INTO "Snapshot" ("id","owner_id","captured_at","cpu_percent","memory_percent","payload") '
        'VALUES (%s,%s,now(),22.0,32.0,%s)',
        ("de-pytest-rollback", owner[0], '{"test":"rollback"}'),
    )
    db.rollback()
    assert db.execute(
        'SELECT count(*) FROM "Snapshot" WHERE "id"=%s',
        ("de-pytest-rollback",),
    ).fetchone()[0] == 0

    db.execute('DELETE FROM "Snapshot" WHERE "id"=%s', ("de-pytest-commit",))
    db.commit()

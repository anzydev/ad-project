#!/usr/bin/env python3
import psycopg
from psycopg import errors

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from ad_project.api.config import get_settings

DSN = get_settings().database_url

with psycopg.connect(DSN) as conn:
    user = conn.execute(
        'SELECT "id" FROM "User" ORDER BY "created_at" LIMIT 1'
    ).fetchone()
    owner_id = user[0]

    # Make the demonstration safe to repeat without deleting unrelated records.
    conn.execute('DELETE FROM "Snapshot" WHERE "id"=%s', ("de-tx-commit",))
    conn.execute('DELETE FROM "Alert" WHERE "id"=%s', ("de-tx-alert-commit",))

    # Successful atomic commit
    conn.execute(
        'INSERT INTO "Snapshot" ("id","owner_id","captured_at","cpu_percent","memory_percent","payload") '
        'VALUES (%s,%s,now(),25.0,35.0,%s)',
        ("de-tx-commit", owner_id, '{"demo":"transaction commit","cpu":{"overall_percent":25.0},"memory":{"ram_percent":35.0}}'),
    )
    conn.execute(
        'INSERT INTO "Alert" ("id","owner_id","metric","threshold","message","resolved","created_at") '
        'VALUES (%s,%s,%s,%s,%s,false,now())',
        ("de-tx-alert-commit", owner_id, "cpu", 70.0, "Transaction commit demonstration"),
    )
    print("COMMIT demo: inserted Snapshot and Alert together")

    conn.execute('DELETE FROM "Snapshot" WHERE "id"=%s', ("de-tx-rollback",))
    conn.execute('DELETE FROM "Alert" WHERE "id"=%s', ("de-tx-alert-rollback",))

# Separate transaction: explicit rollback after inserting two records
with psycopg.connect(DSN) as conn:
    conn.execute("BEGIN")
    conn.execute(
        'INSERT INTO "Snapshot" ("id","owner_id","captured_at","cpu_percent","memory_percent","payload") '
        'VALUES (%s,%s,now(),33.0,44.0,%s)',
        ("de-tx-rollback", owner_id, '{"demo":"rollback","cpu":{"overall_percent":33.0},"memory":{"ram_percent":44.0}}'),
    )
    conn.execute(
        'INSERT INTO "Alert" ("id","owner_id","metric","threshold","message","resolved","created_at") '
        'VALUES (%s,%s,%s,%s,%s,false,now())',
        ("de-tx-alert-rollback", owner_id, "memory", 80.0, "This alert will roll back"),
    )
    conn.rollback()
    print("ROLLBACK demo: Snapshot and Alert were not retained")

with psycopg.connect(DSN) as conn:
    for table, id_value in (
        ('Snapshot', 'de-tx-constraint-should-not-exist'),
    ):
        try:
            conn.execute(
                'INSERT INTO "Snapshot" ("id","owner_id","captured_at","cpu_percent","memory_percent","payload") '
                'VALUES (%s,%s,now(),150.0,35.0,%s)',
                (id_value, owner_id, '{"invalid":true}'),
            )
            conn.commit()
        except errors.CheckViolation as exc:
            conn.rollback()
            print(f"CONSTRAINT demo: rejected cpu_percent=150 ({exc.diag.constraint_name})")

with psycopg.connect(DSN) as conn:
    rollback_count = conn.execute(
        'SELECT count(*) FROM "Snapshot" WHERE "id" IN (%s,%s)',
        ("de-tx-rollback", "de-tx-constraint-should-not-exist"),
    ).fetchone()[0]
    commit_count = conn.execute(
        'SELECT count(*) FROM "Snapshot" WHERE "id"=%s',
        ("de-tx-commit",),
    ).fetchone()[0]
    print(f"Verification: committed={commit_count}, rolled_back={rollback_count}")

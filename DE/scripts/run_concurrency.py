#!/usr/bin/env python3
import json
import threading
import time
import psycopg

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from ad_project.api.config import get_settings

DSN = get_settings().database_url

with psycopg.connect(DSN) as seed:
    owner = seed.execute('SELECT "id" FROM "User" LIMIT 1').fetchone()[0]
    seed.execute(
        'INSERT INTO "Snapshot" ("id","owner_id","captured_at","cpu_percent","memory_percent","payload") '
        'VALUES (%s,%s,now(),10.0,20.0,%s) '
        'ON CONFLICT ("id") DO UPDATE SET "cpu_percent"=10.0, "memory_percent"=20.0, "payload"=EXCLUDED."payload"',
        ("de-concurrency-demo", owner, '{"demo":"concurrency","cpu":{"overall_percent":10.0},"memory":{"ram_percent":20.0}}'),
    )
    seed.commit()

barrier = threading.Barrier(2)
results = {}

def worker(name, new_cpu):
    with psycopg.connect(DSN) as conn:
        barrier.wait()
        conn.execute("BEGIN")
        row = conn.execute(
            'SELECT "cpu_percent" FROM "Snapshot" WHERE "id"=%s FOR UPDATE',
            ("de-concurrency-demo",),
        ).fetchone()
        results[name] = {"read_before": row[0]}
        time.sleep(0.25)
        conn.execute(
            'UPDATE "Snapshot" SET "cpu_percent"=%s, "payload"=%s WHERE "id"=%s',
            (new_cpu, json.dumps({"demo":"concurrency","cpu":{"overall_percent":new_cpu},"memory":{"ram_percent":20.0}}), "de-concurrency-demo"),
        )
        conn.commit()

threads = [
    threading.Thread(target=worker, args=("A", 31.0)),
    threading.Thread(target=worker, args=("B", 57.0)),
]
for thread in threads:
    thread.start()
for thread in threads:
    thread.join()

with psycopg.connect(DSN) as conn:
    final = conn.execute(
        'SELECT "cpu_percent" FROM "Snapshot" WHERE "id"=%s',
        ("de-concurrency-demo",),
    ).fetchone()[0]

print("Concurrency demo: two transactions used SELECT ... FOR UPDATE")
print(results)
print(f"Final committed cpu_percent={final}")

#!/usr/bin/env python3
import pathlib
import psycopg
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from ad_project.api.config import get_settings

ROOT = pathlib.Path(__file__).resolve().parents[2]
SQL_FILE = ROOT / "DE" / "04_SAMPLE_DATA.sql"

with psycopg.connect(get_settings().database_url) as conn:
    conn.execute(SQL_FILE.read_text())
    counts = conn.execute(
        'SELECT (SELECT count(*) FROM "User"), '
        '(SELECT count(*) FROM "Snapshot"), '
        '(SELECT count(*) FROM "Alert")'
    ).fetchone()

print("Seed data applied.")
print(f"Rows: users={counts[0]}, snapshots={counts[1]}, alerts={counts[2]}")

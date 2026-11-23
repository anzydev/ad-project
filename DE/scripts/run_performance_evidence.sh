#!/bin/bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
cd "$ROOT"
set -a
. ./.env
set +a

/Library/PostgreSQL/18/bin/psql "$DATABASE_URL" -v ON_ERROR_STOP=1 <<'SQL' > DE/evidence/performance_output.txt
\pset pager off
ANALYZE "Snapshot";

\echo 'ACTUAL PLANNER DECISION: user monitoring history'
EXPLAIN (ANALYZE, BUFFERS)
SELECT "id", "captured_at", "cpu_percent", "memory_percent"
FROM "Snapshot"
WHERE "owner_id"='de-user-002'
ORDER BY "captured_at" DESC
LIMIT 20;

\echo 'INDEX ACCESS PATH (seq scan disabled only for this transaction)'
BEGIN;
SET LOCAL enable_seqscan = off;
EXPLAIN (ANALYZE, BUFFERS)
SELECT "id", "captured_at", "cpu_percent", "memory_percent"
FROM "Snapshot"
WHERE "owner_id"='de-user-002'
ORDER BY "captured_at" DESC
LIMIT 20;
ROLLBACK;

\echo 'INDEX DEFINITIONS'
SELECT indexname,indexdef FROM pg_indexes
WHERE schemaname='public' AND tablename='Snapshot';
SQL

echo "Actual query plans recorded in DE/evidence/performance_output.txt"

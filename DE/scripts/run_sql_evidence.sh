#!/bin/bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
mkdir -p "$ROOT/DE/evidence"
cd "$ROOT"
set -a
. ./.env
set +a

/Library/PostgreSQL/18/bin/psql "$DATABASE_URL" -v ON_ERROR_STOP=1 \
  -f DE/04_SAMPLE_DATA.sql > DE/evidence/sample_data_load.txt
/Library/PostgreSQL/18/bin/psql "$DATABASE_URL" -v ON_ERROR_STOP=1 \
  -f DE/05_PROJECT_SQL_QUERIES.sql > DE/evidence/sql_queries_output.txt
.venv/bin/python DE/scripts/run_transactions.py > DE/evidence/transactions_output.txt
.venv/bin/python DE/scripts/run_concurrency.py > DE/evidence/concurrency_output.txt

echo "SQL and transaction evidence written to DE/evidence/"

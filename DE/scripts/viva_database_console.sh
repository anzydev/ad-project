#!/bin/zsh
set -e
cd "$(dirname "$0")/../.."
set -a
source .env
set +a
PSQL="/Library/PostgreSQL/18/bin/psql"
clear
echo "====================================================="
echo " AD PROJECT | LIVE POSTGRESQL DATABASE DEMONSTRATION"
echo "====================================================="
echo "Project tables:"
"$PSQL" "$DATABASE_URL" -v ON_ERROR_STOP=1 -c '\dt'
echo
echo "Current record counts:"
"$PSQL" "$DATABASE_URL" -v ON_ERROR_STOP=1 -c 'SELECT (SELECT COUNT(*) FROM "User") AS users, (SELECT COUNT(*) FROM "Snapshot") AS snapshots, (SELECT COUNT(*) FROM "Alert") AS alerts;'
echo
echo "Q2 | Actual User to Snapshot JOIN:"
"$PSQL" "$DATABASE_URL" -v ON_ERROR_STOP=1 -c 'SELECT u.email, s.captured_at, s.cpu_percent, s.memory_percent FROM "User" u JOIN "Snapshot" s ON s.owner_id=u.id ORDER BY s.captured_at DESC LIMIT 5;'
echo
echo "Q5 | Actual CPU aggregates:"
"$PSQL" "$DATABASE_URL" -v ON_ERROR_STOP=1 -c 'SELECT count(*) AS samples, round(avg(cpu_percent)::numeric,2) AS average_cpu, max(cpu_percent) AS max_cpu FROM "Snapshot";'
echo
echo "Interactive PostgreSQL prompt ready. Use \\dt, \\d \"Snapshot\", or SELECT queries."
exec "$PSQL" "$DATABASE_URL"

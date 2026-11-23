#!/bin/bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
PGDATA="${AD_PROJECT_PGDATA:-$HOME/.local/share/ad-project/pgdata}"
PG_BIN="${PG_BIN:-/Library/PostgreSQL/18/bin}"

cd "$ROOT"
if [ ! -f ".env" ]; then
  echo "Missing .env; copy .env.example and configure DATABASE_URL." >&2
  exit 1
fi
set -a
. ./.env
set +a

if [ ! -f "$PGDATA/PG_VERSION" ]; then
  echo "PostgreSQL data directory missing: $PGDATA" >&2
  echo "Preserved backup (if available): $HOME/.local/share/ad-project/backups/" >&2
  exit 1
fi

if "$PG_BIN/pg_isready" -h 127.0.0.1 -p 5432 >/dev/null 2>&1; then
  RUNNING_DIR="$("$PG_BIN/psql" "$DATABASE_URL" -Atc 'SHOW data_directory')"
  if [ "$RUNNING_DIR" != "$PGDATA" ]; then
    echo "Port 5432 is already used by a different PostgreSQL cluster: $RUNNING_DIR" >&2
    exit 1
  fi
else
  "$PG_BIN/pg_ctl" -D "$PGDATA" -l "$HOME/.local/share/ad-project/postgres.log" \
    -o "-h 127.0.0.1 -p 5432" -w start
fi

"$PG_BIN/psql" "$DATABASE_URL" -v ON_ERROR_STOP=1 -Atc "SELECT current_database(), current_user"
echo "AD Project PostgreSQL is ready."

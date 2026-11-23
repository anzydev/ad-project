# 1. Database setup and verification

## Components
- PostgreSQL 18 (local, loopback-only development instance)
- FastAPI and Prisma Client Python 0.15
- Database: `ad_project`
- Migrations: `20261113130000_initial`, `20261121120000_de_constraints_indexes`, and `20261121214500_remove_redundant_indexes`

## Stored data and safety
The development database is stored persistently at `~/.local/share/ad-project/pgdata`, **not** inside temporary Coding AI session state. A pre-relocation database backup is at `~/.local/share/ad-project/backups/before-relocation.dump`. The original session-state copy was not deleted.

The instance is configured for **localhost-only demonstration**, and must not be exposed to external networks. Local PostgreSQL trust authentication is not suitable for production. JWT/API authentication is separate from this database-level configuration.

## Start and verify
From the project root:

```bash
./DE/scripts/setup_database.sh
source .venv/bin/activate
prisma migrate deploy --schema prisma/schema.prisma
prisma generate --schema prisma/schema.prisma
uvicorn ad_project.api.app:app --host 127.0.0.1 --port 8000
```

In another terminal:

```bash
curl http://127.0.0.1:8000/api/v1/health
/Library/PostgreSQL/18/bin/psql "$(grep '^DATABASE_URL=' .env | cut -d= -f2-)" -c 'SELECT count(*) FROM "Snapshot";'
```

The startup script **does not create or overwrite an unfamiliar database cluster**. If its expected PGDATA is absent, it fails with instructions rather than risking deletion or replacement of user data.

## Actual verification evidence
See `evidence/database_health.txt`, `evidence/migration.txt`, `evidence/table_counts.txt`, and `evidence/api_health.txt`. Re-run the tests with `.venv/bin/python -m pytest -q`. The working FastAPI server must be restarted after backend code changes to load new endpoints.

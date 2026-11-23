# 8. Database ↔ backend integration

## Architecture
`psutil` → Python monitoring collectors → FastAPI REST API → Prisma Client Python → PostgreSQL. Prisma connection lifecycle is in `ad_project/api/database.py`. Direct monitoring collection saves a snapshot with `POST /api/v1/snapshots/collect`.

## Working operations
- User account registration: `POST /api/v1/auth/register`; login `POST /api/v1/auth/login`.
- Create/list/modify/delete owner-scoped snapshots: `POST, GET /api/v1/snapshots`, `PATCH, DELETE /api/v1/snapshots/{snapshot_id}`.
- Multi-row atomic insert: `POST /api/v1/snapshots/batch`, which uses `async with db.tx()`.
- Create/list/resolve/delete owner-scoped alerts: `POST, GET /api/v1/alerts`, `PATCH, DELETE /api/v1/alerts/{alert_id}`.
- Admin read/update/delete: `GET /api/v1/admin/users`, `PATCH, DELETE /api/v1/admin/users/{user_id}`.

Request validation is in `ad_project/api/schemas.py` and `ad_project/api/routes.py`; JWT ownership checks are in `ad_project/api/dependencies.py`. API mutation routes enforce owner boundaries.

## Real database integration test
`tests/test_de_api_integration.py` registers isolated test users and demonstrates:
1. Duplicate-email rejection.
2. CREATE + PATCH a snapshot, followed by a direct PostgreSQL SELECT proving both persisted scalar metrics and JSON payload were updated.
3. Cross-user edit/delete requests rejected with 404.
4. An invalid two-item batch returning 422 with **no partial snapshot remaining**.
5. A valid atomic batch creating two records.
6. Alert CREATE, GET, resolve PATCH, DELETE and ownership checks.
7. Cleanup of the isolated test users and associated records.

Run: `.venv/bin/python -m pytest tests/test_de_api_integration.py -vv`.

## Genuine captured outputs
See `evidence/api_crud_output.txt` (earlier API run), `evidence/transactions_output.txt`, `evidence/sql_queries_output.txt`, and `evidence/api_integration_test.txt`. API test output is captured from a real invocation, not synthesized. The SQL queries can be repeated using `./DE/scripts/run_sql_evidence.sh`.

## Limitation
An alert can now be created and resolved through the API, but automatic alert creation from threshold crossings is **not** implemented by the monitor. Describe alerts as supported records, not as an autonomous notification engine.

# Database selection and justification

**Selected technology:** PostgreSQL 18 — relational (SQL) database. The application uses Prisma Client Python from its FastAPI backend.

## Nature of our data
- **Structured:** User accounts, role, ownership, timestamps, CPU and memory percentages, alert state.
- **Flexible/semi-structured:** The full system-monitoring snapshot is serialized into the `Snapshot.payload` TEXT column as JSON. This retains extra metrics without adding columns for every new system measurement.
- **Relationships:** A User has many Snapshots and many Alerts, enforced by foreign keys.

## Real usage
- **Writes:** registration, snapshot insertion (manual or background), and alert create/update.
- **Reads:** email lookup during login, recently captured snapshots for one user, and filtered unresolved alerts.
- **Estimated volume:** At one snapshot/minute, a continuously running user generates 1,440 snapshots/day, about 43,200 per 30-day month. These are **planning estimates**, not measured production traffic.
- **Consistency:** A snapshot must belong to a valid user; unique emails are enforced; range checks reject invalid CPU/memory values. PostgreSQL provides atomic statements and explicit multi-write transactions for batch insertion.

## Alternative considered
**MongoDB** stores flexible snapshots naturally as documents and could reduce the need for serialized payload text. We selected **PostgreSQL** because the important user→snapshot/alert relationships, foreign-key guarantees, SQL reporting (JOIN / GROUP BY / HAVING), and precise transactions are stronger design priorities for this project.

## Main operations to demonstrate
- `POST /api/v1/snapshots/collect` — writes collected system metrics for the authenticated user.
- `GET /api/v1/snapshots?page=1&page_size=20` — bounded history by user and time.
- `POST /api/v1/auth/login` — lookup by unique email and validate credentials.

See `09_BACKEND_INTEGRATION.md` and `evidence/live_api_smoke_output.txt` for verified integration.

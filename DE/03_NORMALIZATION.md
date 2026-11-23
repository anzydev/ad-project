# 3. Normalization: 1NF → 2NF → 3NF

## Before normalization (conceptual example)
A single `MonitoringLog` record containing `user_id, email, role, captured_at, cpu_percent, memory_percent, alert_message` for each reading would repeat user details. Email/role changes could require updating many rows, and one reading with multiple alerts could produce repeated monitoring fields.

This is a **design illustration**, not a claim that the project originally had this physical table.

## First Normal Form (1NF)
The final relational tables have unique rows identified by `id`; there are no repeating SQL column groups or multi-valued columns. The application treats `Snapshot.payload` as one serialized, opaque monitoring document. Its nested content is retained for flexibility rather than relational searches.

## Second Normal Form (2NF)
Each table has a single-column primary key (`id`), so there are no partial dependencies on a portion of a composite primary key. In an alternative composite-key history table such as `(user_id, captured_at)`, `email` would depend on only `user_id`; separating `User` avoids that problem.

## Third Normal Form (3NF)
Functional dependencies in the main relational attributes:
- `User.id → email, password_hash, role, created_at, updated_at`.
- `Snapshot.id → owner_id, captured_at, cpu_percent, memory_percent, payload`.
- `Alert.id → owner_id, metric, threshold, message, created_at, resolved`.
- `User.email → User.id` because email is UNIQUE.

Owner email and role are not stored as separate columns on `Snapshot` or `Alert`; they are obtained through their foreign-key relationship to `User`. This removes unnecessary transitive dependencies and user-information update anomalies. The normalized relational entities are therefore designed for 3NF.

## Deliberate denormalization / caveat
The full monitoring document in `Snapshot.payload` may **also** contain CPU and memory values that appear in the scalar `cpu_percent` and `memory_percent` columns. This is deliberate duplication to support flexible full snapshots while allowing fast SQL filtering and aggregates on common metrics.

`ad_project/api/routes.py:snapshot_metrics` validates the two values (0–100), and create/update/batch API routes save the scalar fields and JSON document in the same database write. `ad_project/api/serialization.py:snapshot_record` does likewise for locally collected readings.

**Limitation:** a raw SQL write can still make the JSON content disagree with the scalar columns. PostgreSQL CHECK constraints validate the numeric ranges, not cross-field equivalence inside the text document. SQL seed/demo records use corresponding values, but we do not claim full database-enforced synchronization.

## Final schema
See `prisma/schema.prisma` for models, keys, and indexes, plus `prisma/migrations/` for actual PostgreSQL DDL and constraints. The ER diagram is in `02_ER_DIAGRAM.md`.

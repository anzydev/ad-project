# Final PostgreSQL database schema

The **authoritative definitions** are in `../prisma/schema.prisma` and `../prisma/migrations/`. This document mirrors the implemented structure; it is not a separate schema to maintain.

| Table | Column | PostgreSQL type / rule |
|---|---|---|
| User | id | TEXT PRIMARY KEY; Prisma-generated cuid |
| User | email | TEXT NOT NULL UNIQUE; lowercase CHECK |
| User | password_hash | TEXT NOT NULL; nonempty CHECK |
| User | role | UserRole enum ('USER','ADMIN'), default 'USER' |
| User | created_at, updated_at | TIMESTAMP(3) NOT NULL |
| Snapshot | id | TEXT PRIMARY KEY |
| Snapshot | owner_id | TEXT NOT NULL; FK → User.id ON DELETE CASCADE |
| Snapshot | captured_at | TIMESTAMP(3) NOT NULL DEFAULT now() |
| Snapshot | cpu_percent, memory_percent | DOUBLE PRECISION NOT NULL; CHECK between 0 and 100 |
| Snapshot | payload | TEXT NOT NULL; nonempty CHECK |
| Alert | id | TEXT PRIMARY KEY |
| Alert | owner_id | TEXT NOT NULL; FK → User.id ON DELETE CASCADE |
| Alert | metric, message | TEXT NOT NULL; nonempty CHECK |
| Alert | threshold | DOUBLE PRECISION NOT NULL; CHECK between 0 and 100 |
| Alert | resolved | BOOLEAN NOT NULL DEFAULT false |
| Alert | created_at | TIMESTAMP(3) NOT NULL DEFAULT now() |

## Relationships
- User **1:N** Snapshot (`Snapshot.owner_id`).
- User **1:N** Alert (`Alert.owner_id`).
- No 1:1 or M:N relationship is required by the present functional design. Do not invent unnecessary junction tables.

## Indexes
- Unique index: `User_email_key`.
- Monitoring indexes: `Snapshot_owner_id_captured_at_idx`, `Snapshot_captured_at_idx`, `Snapshot_cpu_memory_idx`.
- Alert index: `Alert_owner_id_resolved_created_at_idx`.
- Each primary key also has a unique B-tree index.

The constraint migration adds numeric-range and nonempty-value checks. A later migration removes indexes that duplicated existing index prefixes. Use `prisma migrate status` and the actual database console for runtime verification.

For a visual ER diagram, see `02_ER_DIAGRAM.md` or `evidence/er-diagram.svg`.

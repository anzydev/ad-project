# Individual DBMS viva recording — 9:30 target (10:00 maximum)

**Rule:** Keep your screen visible throughout; show the actual terminal monitor, schema, API and genuine PostgreSQL results. This file is a speaking guide, not a replacement for a live demonstration. Every student records and submits their own video.

## Before recording
From the project root, open two terminals. In terminal A:

```bash
./DE/scripts/setup_database.sh
source .venv/bin/activate
prisma migrate status --schema prisma/schema.prisma
uvicorn ad_project.api.app:app --host 127.0.0.1 --port 8000
```

If port 8000 is already occupied by the same backend, do not start another instance: verify the current one has `/api/v1/alerts` in `http://127.0.0.1:8000/docs`. Restart the old backend after changing code.

In terminal B:

```bash
python main.py --once
curl http://127.0.0.1:8000/api/v1/health
./DE/scripts/run_sql_evidence.sh
./DE/scripts/run_performance_evidence.sh
```

Open these files before starting OBS: `prisma/schema.prisma`, `DE/02_ER_DIAGRAM.md`, `DE/03_NORMALIZATION.md`, `ad_project/api/routes.py`, `DE/evidence/sql_queries_output.txt`, `DE/evidence/transactions_output.txt`, and `DE/evidence/performance_output.txt`. Use only previously verified commands in the recording.

## 0:00–0:30 Introduction
**Say:** "My major project is AD Project, a real-time system monitor built in Python. It tracks CPU, memory, disk, network, battery and process information. I added a FastAPI backend using Prisma and PostgreSQL to store and retrieve authenticated users' monitoring snapshots and alert records. I'll explain the five database design and implementation questions through my actual code and query results."

**Show:** `python main.py --once`, then `GET /api/v1/health`.

## Q1 — 0:30–2:00. Why PostgreSQL?
**Say:** "I selected PostgreSQL, a relational database, because my application has structured ownership relationships: each snapshot and alert belongs to a user. The frequent writes are new monitoring snapshots, while common reads are user lookup at login and the user's latest monitoring history. Additional metrics are serialized as JSON text in the snapshot payload, so I retain some flexibility. One snapshot per minute would mean about 1,440 rows per user per day, so timestamp filtering, indexing and retention matter as the system grows. PostgreSQL gives strong referential integrity and ACID transactions. I considered MongoDB because flexible monitoring metrics fit documents, but chose PostgreSQL because user ownership, SQL aggregation and relational constraints are central here."

**Show:** `prisma/schema.prisma`, `ad_project/api/routes.py:create_snapshot`, `list_snapshots`; real Q5 JOIN and Q6 filter output from `DE/evidence/sql_queries_output.txt`.

## Q2 — 2:00–3:35. Schema and ER diagram
**Say:** "My database contains User, Snapshot and Alert. Each has an ID primary key. User has a unique email, password hash and role. Snapshot has owner ID, capture timestamp, CPU, memory and full payload. Alert has owner ID, metric, threshold, message and resolved status. Snapshot.owner_id and Alert.owner_id are foreign keys to User.id, giving two one-to-many relationships. A user can own many snapshots and many alerts; there is no many-to-many requirement, so no junction table is necessary. Foreign keys are defined with ON DELETE CASCADE. My migration defines all these constraints, and this actual JOIN query reads snapshot metrics alongside each owner's email."

**Show:** `DE/02_ER_DIAGRAM.md` or `DE/evidence/er-diagram.svg`, `prisma/migrations/20261113130000_initial/migration.sql`, and Q5 JOIN output.

## Q3 — 3:35–4:55. Normalization
**Say:** "The main relational structure was designed for Third Normal Form. In First Normal Form, each SQL column is treated as a single value with no repeating columns. In Second Normal Form, our single-column primary keys remove partial-key dependencies. In Third Normal Form, user email and role are stored only in User, not repeated for every snapshot or alert. For example, Snapshot.id determines the snapshot owner, timestamp and readings. One deliberate trade-off is storing CPU and memory both as scalar columns and within the complete serialized payload. This gives efficient SQL filtering and retains flexible monitoring details. The application extracts and validates the scalar values from the same payload when creating or updating snapshots. However, raw SQL could bypass that synchronization, so this isn't a database-level guarantee."

**Show:** `DE/03_NORMALIZATION.md`, `ad_project/api/routes.py:snapshot_metrics`, and `ad_project/api/serialization.py:snapshot_record`.

## Q4 — 4:55–7:10. Data correctness, transactions and concurrency
**Say:** "I protect correctness both through the database and through the API. The database enforces primary keys, NOT NULL, unique user email and foreign keys. I added CHECK constraints for CPU, memory and thresholds to stay between zero and one hundred. Pydantic validates API inputs before insertion. For atomicity I implemented a real batch snapshot route using Prisma's transaction context. All requested snapshots are written together; if a later item fails validation, earlier inserts are rolled back. Separately, my PostgreSQL transaction demonstration inserts a snapshot and alert together, then shows an explicit rollback case. PostgreSQL's default Read Committed isolation uses MVCC, and the concurrency demo uses SELECT FOR UPDATE to serialize changes to one snapshot. A unique constraint also prevents two registrations from creating the same email. These are concrete integrity protections, not just definitions."

**Show:** constraints migration, `create_snapshot_batch` in `routes.py`, `DE/evidence/transactions_output.txt`, `DE/evidence/concurrency_output.txt`, and `tests/test_de_api_integration.py`. Point at the rejected CPU=150 output.

## Q5 — 7:10–9:00. Database efficiency
**Say:** "My main index is on Snapshot(owner_id, captured_at), because users commonly request their own recent monitoring history. There is also a unique index on email for account lookup, a timestamp index, a CPU/memory index for metric filtering, and an Alert(owner_id, resolved, created_at) index for unresolved-alert queries. I actually removed two redundant indexes after reviewing their overlap with existing indexes, because extra indexes consume storage and slow down writes. The snapshot API also enforces pagination, limiting responses to a maximum of one hundred records. EXPLAIN ANALYZE shows the actual planner choice on my demo dataset. Because the dataset is small, a sequential scan can be faster; I do not claim that indexes guarantee speed on every query. At one hundred times the current scale, the first concern would be growing snapshot history, so I would evaluate retention, partitioning, batching and query plans."

**Show:** `prisma/schema.prisma` indexes, `list_snapshots` pagination, `DE/evidence/performance_output.txt` and the index-cleanup migration.

## 9:00–9:30 Conclusion
**Say:** "In AD Project, PostgreSQL supports real features: authenticated users, monitoring history, alerts, controlled updates and SQL analysis. The ER model, normalization, constraints, transaction demos and indexing choices are present in the implementation and in our GitHub DE deliverables. Thank you."

## Submission reminder
- Individual video, **maximum 10 minutes**.
- Screen stays visible throughout; slides alone are not sufficient.
- Explain actual project code and real query results.
- Upload video, copy its shareable link, and submit it through the university form.
- Video submission deadline stated in the instructor's notice: **22 November 2026**.
- GitHub `DE` folder should be committed and pushed only after review/permission.

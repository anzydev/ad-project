# AD Project — Data Engineering deliverables

PostgreSQL + FastAPI + Prisma integration for the real-time Python system monitor. This folder maps the DBMS integrated-project rubric to actual code, schemas, SQL queries, and verified execution results.

## Mandatory deliverables

| Instructor requirement | Evidence |
|---|---|
| 1. Database choice and justification | [00_DATABASE_SELECTION.md](00_DATABASE_SELECTION.md) |
| 2. ER diagram and relationships | [02_ER_DIAGRAM.md](02_ER_DIAGRAM.md), [SVG diagram](evidence/er-diagram.svg) |
| 3. 1NF → 2NF → 3NF and denormalization | [03_NORMALIZATION.md](03_NORMALIZATION.md) |
| 4. Final implemented schema | [10_FINAL_SCHEMA.md](10_FINAL_SCHEMA.md), [Prisma schema](../prisma/schema.prisma), [migrations](../prisma/migrations/) |
| 5. Sample records | [04_SAMPLE_DATA.sql](04_SAMPLE_DATA.sql), [seed output](evidence/sample_data_load.txt) |
| 6. At least 10 queries + explanations + outputs | [05_PROJECT_SQL_QUERIES.sql](05_PROJECT_SQL_QUERIES.sql), [11_QUERY_EXPLANATIONS.md](11_QUERY_EXPLANATIONS.md), [actual outputs](evidence/sql_queries_output.txt) |
| 7. Database-backend integration | [09_BACKEND_INTEGRATION.md](09_BACKEND_INTEGRATION.md), [live API evidence](evidence/live_api_smoke_output.txt) |
| 8. Architecture/implementation decisions | [01_DATABASE_SETUP.md](01_DATABASE_SETUP.md), [06_TRANSACTIONS_AND_CONSTRAINTS.md](06_TRANSACTIONS_AND_CONSTRAINTS.md), [07_INDEXING_AND_PERFORMANCE.md](07_INDEXING_AND_PERFORMANCE.md) |

The separate [08_VIVA_DEMO.md](08_VIVA_DEMO.md) contains individual Q1–Q5 speaking scripts and a 9:30 screen-recording plan.

## Reproduce the live demonstrations
From the existing project root:

```bash
./DE/scripts/setup_database.sh
source .venv/bin/activate
prisma migrate status --schema prisma/schema.prisma
python main.py --once
# In another terminal, start or keep the API running on port 8000:
uvicorn ad_project.api.app:app --host 127.0.0.1 --port 8000
# After checking http://127.0.0.1:8000/docs:
./DE/scripts/run_sql_evidence.sh
./DE/scripts/run_performance_evidence.sh
python DE/scripts/run_live_api_evidence.py
python -m pytest -q
```

**Important:** Do not start another Uvicorn server if port 8000 is already running this project. The demo scripts use isolated test records and produce real outputs; never run them against a production database.

## Evidence folder
`evidence/` contains actual PostgreSQL query outputs, transaction commit/rollback and concurrency results, EXPLAIN ANALYZE plans, a generated ER SVG, live API persistence results, and the terminal monitor output. Outputs are demonstrations, not fabricated results. The small dataset may lead PostgreSQL to choose sequential scans.

The local database is for coursework demonstration on loopback; its local trust authentication is **not production-secure**. Secrets and `.env` are excluded from Git.

## Submission status
This folder contains the DE technical evidence intended for the project repository. Repository publication and portal submission should be verified independently. The **individual viva video** is a separate user-recorded submission; no recording or upload is performed by these scripts. The course form must be completed independently.

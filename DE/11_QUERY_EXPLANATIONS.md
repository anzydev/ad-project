# Twelve actual project-specific SQL operations

The executable SQL is in `05_PROJECT_SQL_QUERIES.sql`. All twelve operations were run against the development database, with **real output** captured in `evidence/sql_queries_output.txt`. Use `./DE/scripts/run_sql_evidence.sh` to reproduce. Statements affecting data target clearly named demo rows.

| Query | Database concept | Why this operation matters to AD Project |
|---|---|---|
| Q1 | INSERT + ON CONFLICT | Create or refresh a test user in an idempotent demo |
| Q2 | UPDATE | Demonstrate administrator modification of a test user's role |
| Q3 | DELETE | Delete only the known demo snapshot (cleanup/replacement) |
| Q4 | INSERT + SELECT + ON CONFLICT | Persist a new monitoring snapshot belonging to a valid user |
| Q5 | JOIN | Read snapshot CPU/memory alongside the owning user's email |
| Q6 | WHERE + ORDER BY | Find CPU readings exceeding 50% and sort highest first |
| Q7 | ORDER BY + LIMIT | Display the highest recorded memory readings |
| Q8 | COUNT, AVG, MAX | Compute overall monitoring activity and resource statistics |
| Q9 | GROUP BY | Summarize monitoring count and average CPU per user |
| Q10 | HAVING | Identify users who accumulated multiple monitoring snapshots |
| Q11 | Subquery | Find unusually high CPU readings above the global average |
| Q12 | JOIN + GROUP BY + HAVING | Identify users with unresolved monitoring alerts |

## Reading the results
- `INSERT 0 1`: one row was inserted.
- `UPDATE 1`: the targeted test user was updated.
- `DELETE 1` or `DELETE 0`: whether the one known demo row existed on that run.
- A SELECT result prints its selected columns and the number of matching rows.
- Aggregate and GROUP BY queries summarize sample monitoring history; the results depend on the current dataset.

## Evidence and repeatability
`04_SAMPLE_DATA.sql` seeds multiple owners, snapshots with CPU/memory values and alerts with both resolved statuses. Running the seed multiple times is supported through `ON CONFLICT`. The query output is regenerated with PostgreSQL `psql -v ON_ERROR_STOP=1`; the script exits on a genuine SQL error instead of silently claiming success.

For API INSERT, UPDATE, DELETE and owner authorization, see `09_BACKEND_INTEGRATION.md`. For constraint rejection and rollback, see `06_TRANSACTIONS_AND_CONSTRAINTS.md`.

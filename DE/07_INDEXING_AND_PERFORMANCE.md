# 5. Indexing and performance

## Indexes currently maintained
- `User_email_key` — unique email lookups and duplicate prevention during login/registration.
- `Snapshot_owner_id_captured_at_idx` — per-user monitoring history ordered by time (B-tree can be scanned backwards for DESC).
- `Snapshot_captured_at_idx` — global timestamp lookups.
- `Snapshot_cpu_memory_idx` — CPU-leading filtering and possible CPU/memory range searches.
- `Alert_owner_id_resolved_created_at_idx` — filtering unresolved alerts per owner, ordered by creation time.

The original primary-key indexes on each table are also maintained automatically.

## Indexes rejected after evaluation
The initial DE migration created `Snapshot_owner_id_captured_at_payload_idx` (despite its name it did not index payload) and `Alert_owner_id_resolved_idx`. Both largely repeated the prefix of existing B-tree indexes. Migration `20261121214500_remove_redundant_indexes` removes them to reduce storage and write overhead. We intentionally do not index every JSON text payload: the application does not query its inner fields with SQL.

## Measured plans
Run:
```bash
./DE/scripts/run_performance_evidence.sh
```
See `evidence/performance_output.txt` for actual `EXPLAIN (ANALYZE, BUFFERS)` results. The script **does not drop indexes**. It first records the optimizer's natural plan, then forces the index path in a local transaction solely to illustrate how the B-tree can serve the query. A forced plan is **not** evidence of better real-world latency.

With the tiny demo dataset, PostgreSQL may prefer a sequential scan; do not promise a performance improvement based only on these milliseconds.

## Other efficiency measures
The snapshot-history endpoint bounds page size to 100 and filters by the authenticated owner's ID. The alert list is also capped at 100. At 100× scale, snapshot growth and write rate are likely the first bottlenecks; consider retention policies, time partitioning, batching, and checking production query plans before adding more indexes. Sharding is not implemented.

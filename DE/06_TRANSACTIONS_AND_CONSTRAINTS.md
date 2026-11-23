# 4. Transactions, rollback, concurrency, and constraints

## ACID demonstration

- **Atomicity:** `/api/v1/snapshots/batch` creates every snapshot inside one Prisma transaction. One failure rolls back all writes.
- **Consistency:** database checks keep CPU/memory/alert thresholds between 0 and 100.
- **Isolation:** the concurrency script uses `SELECT ... FOR UPDATE` so two transactions serialize updates to the same snapshot.
- **Durability:** successful Prisma and psycopg commits remain visible after reconnection.

## Constraints

The constraints migration adds:

- Snapshot CPU and memory ranges
- Alert threshold range
- Non-empty metric, message, password hash, and payload values
- Lowercase email
- Foreign keys and cascade delete
- Unique user email

## Rollback evidence

[evidence/transactions_output.txt](evidence/transactions_output.txt) proves:

- A successful transaction retains both a snapshot and alert.
- An explicit rollback retains neither record.
- A CPU value of 150 violates the check constraint and is rejected.

## Concurrency evidence

[evidence/concurrency_output.txt](evidence/concurrency_output.txt) shows two transactions locking the same row and the final committed value.

\pset pager off
\pset border 2

\echo 'Q1 INSERT: Add one realistic user'
INSERT INTO "User" ("id","email","password_hash","role","created_at","updated_at")
VALUES ('de-demo-user','demo@adproject.local','pbkdf2_sha256$310000$demo$demo','USER',now(),now())
ON CONFLICT ("id") DO UPDATE SET "updated_at"=now();

\echo 'Q2 UPDATE: Raise the demo user role'
UPDATE "User" SET "role"='ADMIN', "updated_at"=now()
WHERE "id"='de-demo-user';

\echo 'Q3 DELETE: Remove only the demo snapshot if present'
DELETE FROM "Snapshot" WHERE "id"='de-demo-snapshot';

\echo 'Q4 INSERT: Add a snapshot for the demo user'
INSERT INTO "Snapshot" ("id","owner_id","captured_at","cpu_percent","memory_percent","payload")
SELECT 'de-demo-snapshot','de-demo-user',now(),64.25,58.75,'{"source":"query-demo","hostname":"demo-host","cpu":{"overall_percent":64.25},"memory":{"ram_percent":58.75}}'
WHERE EXISTS (SELECT 1 FROM "User" WHERE "id"='de-demo-user')
ON CONFLICT ("id") DO UPDATE SET "captured_at"=now(), "cpu_percent"=64.25, "memory_percent"=58.75, "payload"=EXCLUDED."payload";

\echo 'Q5 JOIN: Owners and their snapshots'
SELECT u."email", s."captured_at", s."cpu_percent", s."memory_percent"
FROM "User" u JOIN "Snapshot" s ON s."owner_id"=u."id"
ORDER BY s."captured_at" DESC;

\echo 'Q6 FILTERING: CPU above 50 percent'
SELECT "id","owner_id","cpu_percent","captured_at"
FROM "Snapshot" WHERE "cpu_percent" > 50
ORDER BY "cpu_percent" DESC;

\echo 'Q7 SORTING: Highest memory snapshots'
SELECT "id","owner_id","memory_percent","captured_at"
FROM "Snapshot" ORDER BY "memory_percent" DESC, "captured_at" DESC LIMIT 10;

\echo 'Q8 AGGREGATE: Overall snapshot averages'
SELECT count(*) AS snapshots,
       round(avg("cpu_percent")::numeric,2) AS avg_cpu,
       round(max("memory_percent")::numeric,2) AS max_memory
FROM "Snapshot";

\echo 'Q9 GROUP BY: Snapshot counts per owner'
SELECT "owner_id", count(*) AS snapshot_count,
       round(avg("cpu_percent")::numeric,2) AS avg_cpu
FROM "Snapshot" GROUP BY "owner_id";

\echo 'Q10 HAVING: Owners with more than one snapshot'
SELECT "owner_id", count(*) AS snapshot_count
FROM "Snapshot" GROUP BY "owner_id" HAVING count(*) > 1;

\echo 'Q11 SUBQUERY: Above-average CPU snapshots'
SELECT "id","owner_id","cpu_percent"
FROM "Snapshot"
WHERE "cpu_percent" > (SELECT avg("cpu_percent") FROM "Snapshot")
ORDER BY "cpu_percent" DESC;

\echo 'Q12 JOIN + GROUP + HAVING: Users with unresolved alerts'
SELECT u."email", count(a."id") AS unresolved_alerts
FROM "User" u JOIN "Alert" a ON a."owner_id"=u."id"
WHERE a."resolved"=false
GROUP BY u."email"
HAVING count(a."id") >= 1
ORDER BY unresolved_alerts DESC, u."email";

-- Remove redundant indexes: the original indexes already serve these query prefixes.
-- A B-tree on (owner_id, captured_at) can be scanned in reverse for DESC order.
DROP INDEX IF EXISTS "Snapshot_owner_id_captured_at_payload_idx";
DROP INDEX IF EXISTS "Alert_owner_id_resolved_idx";

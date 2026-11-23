-- DE deliverable constraints and performance indexes
ALTER TABLE "User"
  ADD CONSTRAINT "User_email_lowercase_check" CHECK ("email" = lower("email")),
  ADD CONSTRAINT "User_password_hash_not_empty_check" CHECK (length("password_hash") > 0);

ALTER TABLE "Snapshot"
  ADD CONSTRAINT "Snapshot_cpu_percent_range_check"
    CHECK ("cpu_percent" >= 0 AND "cpu_percent" <= 100),
  ADD CONSTRAINT "Snapshot_memory_percent_range_check"
    CHECK ("memory_percent" >= 0 AND "memory_percent" <= 100),
  ADD CONSTRAINT "Snapshot_payload_not_empty_check"
    CHECK (length("payload") > 0);

ALTER TABLE "Alert"
  ADD CONSTRAINT "Alert_metric_not_empty_check" CHECK (length("metric") > 0),
  ADD CONSTRAINT "Alert_threshold_range_check"
    CHECK ("threshold" >= 0 AND "threshold" <= 100),
  ADD CONSTRAINT "Alert_message_not_empty_check" CHECK (length("message") > 0);

CREATE INDEX "Snapshot_owner_id_captured_at_payload_idx"
  ON "Snapshot"("owner_id", "captured_at" DESC);
CREATE INDEX "Snapshot_cpu_memory_idx"
  ON "Snapshot"("cpu_percent", "memory_percent");
CREATE INDEX "Alert_owner_id_resolved_idx"
  ON "Alert"("owner_id", "resolved");

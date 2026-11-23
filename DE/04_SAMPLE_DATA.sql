-- Realistic seed data for AD-Project
-- Password hashes are demonstration strings because the application uses
-- its own PBKDF2 generator for real registered accounts.

INSERT INTO "User" ("id", "email", "password_hash", "role", "created_at", "updated_at") VALUES
  ('de-admin-001', 'admin@adproject.local', 'pbkdf2_sha256$310000$de_demo_admin$de_demo_digest', 'ADMIN', now() - interval '40 days', now()),
  ('de-user-002', 'maya@adproject.local', 'pbkdf2_sha256$310000$de_demo_maya$de_demo_digest', 'USER', now() - interval '35 days', now()),
  ('de-user-003', 'liam@adproject.local', 'pbkdf2_sha256$310000$de_demo_liam$de_demo_digest', 'USER', now() - interval '28 days', now()),
  ('de-user-004', 'sofia@adproject.local', 'pbkdf2_sha256$310000$de_demo_sofia$de_demo_digest', 'USER', now() - interval '18 days', now()),
  ('de-user-005', 'noah@adproject.local', 'pbkdf2_sha256$310000$de_demo_noah$de_demo_digest', 'USER', now() - interval '10 days', now())
ON CONFLICT ("id") DO NOTHING;

INSERT INTO "Snapshot" ("id", "owner_id", "captured_at", "cpu_percent", "memory_percent", "payload") VALUES
  ('de-snap-001', 'de-user-002', now() - interval '12 hours', 18.5, 42.0, '{"source":"seed","hostname":"maya-laptop","cpu":{"overall_percent":18.5},"memory":{"ram_percent":42.0}}'),
  ('de-snap-002', 'de-user-002', now() - interval '10 hours', 42.0, 48.5, '{"source":"seed","hostname":"maya-laptop","cpu":{"overall_percent":42.0},"memory":{"ram_percent":48.5}}'),
  ('de-snap-003', 'de-user-002', now() - interval '8 hours', 76.0, 71.5, '{"source":"seed","hostname":"maya-laptop","cpu":{"overall_percent":76.0},"memory":{"ram_percent":71.5}}'),
  ('de-snap-004', 'de-user-003', now() - interval '9 hours', 23.0, 55.0, '{"source":"seed","hostname":"liam-desktop","cpu":{"overall_percent":23.0},"memory":{"ram_percent":55.0}}'),
  ('de-snap-005', 'de-user-003', now() - interval '7 hours', 51.5, 62.0, '{"source":"seed","hostname":"liam-desktop","cpu":{"overall_percent":51.5},"memory":{"ram_percent":62.0}}'),
  ('de-snap-006', 'de-user-004', now() - interval '6 hours', 88.0, 83.0, '{"source":"seed","hostname":"sofia-mac","cpu":{"overall_percent":88.0},"memory":{"ram_percent":83.0}}'),
  ('de-snap-007', 'de-user-004', now() - interval '4 hours', 31.0, 67.0, '{"source":"seed","hostname":"sofia-mac","cpu":{"overall_percent":31.0},"memory":{"ram_percent":67.0}}'),
  ('de-snap-008', 'de-user-005', now() - interval '3 hours', 12.5, 38.0, '{"source":"seed","hostname":"noah-server","cpu":{"overall_percent":12.5},"memory":{"ram_percent":38.0}}')
ON CONFLICT ("id") DO UPDATE SET "payload"=EXCLUDED."payload";

INSERT INTO "Alert" ("id", "owner_id", "metric", "threshold", "message", "created_at", "resolved") VALUES
  ('de-alert-001', 'de-user-002', 'cpu', 70.0, 'CPU usage exceeded 70 percent', now() - interval '8 hours', true),
  ('de-alert-002', 'de-user-003', 'memory', 60.0, 'Memory usage exceeded 60 percent', now() - interval '7 hours', false),
  ('de-alert-003', 'de-user-004', 'cpu', 80.0, 'CPU usage exceeded 80 percent', now() - interval '6 hours', false),
  ('de-alert-004', 'de-user-005', 'memory', 90.0, 'Memory usage exceeded 90 percent', now() - interval '2 hours', false)
ON CONFLICT ("id") DO NOTHING;

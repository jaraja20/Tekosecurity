-- TEKOSECURE — actions_log table
-- Run this ONCE in Supabase SQL Editor
-- (https://app.supabase.com/project/fsucygjqzskwtnynvgob/sql/new)

CREATE TABLE IF NOT EXISTS actions_log (
    id           BIGSERIAL PRIMARY KEY,
    created_at   TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    actor        VARCHAR(255) NOT NULL,
    action       VARCHAR(64)  NOT NULL,   -- BLOCK_IP_REAL, CLOSE_ALERT, ...
    target_ip    VARCHAR(45),             -- IPv4/IPv6 or "N/A"
    attack_id    BIGINT,                  -- FK-ish to attacks.id (nullable)
    status       VARCHAR(20) NOT NULL,    -- SUCCESS | PARTIAL | FAILED
    details      TEXT                     -- JSON blob
);

CREATE INDEX IF NOT EXISTS idx_actions_log_created_at ON actions_log(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_actions_log_actor       ON actions_log(actor);
CREATE INDEX IF NOT EXISTS idx_actions_log_action      ON actions_log(action);
CREATE INDEX IF NOT EXISTS idx_actions_log_target_ip   ON actions_log(target_ip);

-- Enable Row Level Security and grant read/insert to authenticated users.
-- (Adjust to your team's policy — this is a permissive starting point.)
ALTER TABLE actions_log ENABLE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS actions_log_read_authenticated ON actions_log;
CREATE POLICY actions_log_read_authenticated ON actions_log
    FOR SELECT USING (auth.role() = 'authenticated');

DROP POLICY IF EXISTS actions_log_insert_authenticated ON actions_log;
CREATE POLICY actions_log_insert_authenticated ON actions_log
    FOR INSERT WITH CHECK (auth.role() = 'authenticated');

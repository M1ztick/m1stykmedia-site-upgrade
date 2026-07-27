-- Subscribers for the Dispatch mailing list.
--
-- email is stored lowercased/trimmed and is the natural key, so the UNIQUE
-- index makes a re-subscribe a no-op instead of a duplicate row.
CREATE TABLE IF NOT EXISTS subscribers (
  id            INTEGER PRIMARY KEY AUTOINCREMENT,
  email         TEXT    NOT NULL,
  status        TEXT    NOT NULL DEFAULT 'active',   -- 'active' | 'unsubscribed'
  source        TEXT,                                -- page path the signup came from
  created_at    TEXT    NOT NULL DEFAULT (datetime('now')),
  updated_at    TEXT    NOT NULL DEFAULT (datetime('now'))
);

CREATE UNIQUE INDEX IF NOT EXISTS idx_subscribers_email ON subscribers (email);
CREATE INDEX IF NOT EXISTS idx_subscribers_status ON subscribers (status);

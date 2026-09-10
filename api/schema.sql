-- This worker shares onepiecedle-api's D1 database: players and sessions are
-- the common account tables, everything game-specific is prefixed av_.
-- Solve counter: one row per (game day, spoiler limit = book name, '' for none), incremented on a
-- verified solve. Kept separate from players so the counter works for people
-- who never sign up.
CREATE TABLE IF NOT EXISTS av_solves (
  day         TEXT NOT NULL,
  arc_limit   TEXT NOT NULL DEFAULT '',
  count       INTEGER NOT NULL DEFAULT 0,
  PRIMARY KEY (day, arc_limit)
);

-- One counted solve per address per day, so the tally reads as "people" and
-- the daily write count stays bounded. The address is salted and hashed; the
-- raw IP is never stored.
-- Keyed per bucket, not just per day: each (day, arc_limit) is its own tally,
-- so one address must be able to count once in each bucket it solves.
CREATE TABLE IF NOT EXISTS av_counted (
  day       TEXT NOT NULL,
  arc_limit TEXT NOT NULL DEFAULT '',
  ip_hash   TEXT NOT NULL,
  PRIMARY KEY (day, arc_limit, ip_hash)
);

-- Workers Free allows 10ms CPU per request, far too little for a real
-- password KDF, so the 600k-iteration PBKDF2 runs in the browser and the
-- server stores a salted SHA-256 of the derived key. The server therefore
-- never sees the password, and a database leak isn't directly replayable.
CREATE TABLE IF NOT EXISTS players (
  id            TEXT PRIMARY KEY,
  name          TEXT NOT NULL,
  name_key      TEXT NOT NULL UNIQUE, -- lowercased, for case-insensitive uniqueness
  password_salt TEXT NOT NULL,
  password_hash TEXT NOT NULL,
  created_at    TEXT NOT NULL,
  last_seen     TEXT NOT NULL
);

-- The browser stores a session token, never the password. Multiple rows per
-- player so signing in on a second device doesn't evict the first.
CREATE TABLE IF NOT EXISTS sessions (
  token_hash  TEXT PRIMARY KEY,
  player_id   TEXT NOT NULL,
  created_at  TEXT NOT NULL,
  FOREIGN KEY (player_id) REFERENCES players(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_sessions_player ON sessions(player_id);

-- One row per player per game day. Re-solving the same day (e.g. after
-- changing the spoiler limit) updates in place rather than inserting, which
-- keeps the daily write count bounded.
CREATE TABLE IF NOT EXISTS av_results (
  player_id   TEXT NOT NULL,
  day         TEXT NOT NULL,
  arc_limit   TEXT NOT NULL DEFAULT '',
  guesses     INTEGER NOT NULL,
  solved_at   TEXT NOT NULL,
  PRIMARY KEY (player_id, day),
  FOREIGN KEY (player_id) REFERENCES players(id) ON DELETE CASCADE
);

-- Denormalised standings so the leaderboard is a single indexed scan rather
-- than an aggregate over every result row (D1 free tier bills row reads).
CREATE TABLE IF NOT EXISTS av_standings (
  player_id     TEXT PRIMARY KEY,
  wins          INTEGER NOT NULL DEFAULT 0,
  total_guesses INTEGER NOT NULL DEFAULT 0,
  streak        INTEGER NOT NULL DEFAULT 0,
  max_streak    INTEGER NOT NULL DEFAULT 0,
  last_win_day  TEXT,
  -- Spoiler limit of the most recent win, shown as a column on the board so
  -- the roster a record was set against is visible.
  last_arc_limit TEXT NOT NULL DEFAULT '',
  FOREIGN KEY (player_id) REFERENCES players(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_av_standings_wins ON av_standings(wins DESC);
CREATE INDEX IF NOT EXISTS idx_av_standings_streak ON av_standings(max_streak DESC);
CREATE INDEX IF NOT EXISTS idx_av_results_day ON av_results(day, guesses);

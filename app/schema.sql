CREATE TABLE IF NOT EXISTS trainees (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    callsign TEXT NOT NULL,
    unit TEXT NOT NULL,
    created_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%SZ', 'now')),
    UNIQUE (callsign, unit)
);

CREATE TABLE IF NOT EXISTS sessions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    trainee_id INTEGER NOT NULL REFERENCES trainees (id),
    scenario_id TEXT NOT NULL,
    scenario_name TEXT NOT NULL,
    seed INTEGER NOT NULL,
    params TEXT,
    started_at TEXT NOT NULL,
    duration_s REAL NOT NULL,
    total REAL NOT NULL,
    detection REAL NOT NULL,
    classification REAL NOT NULL,
    engagement REAL NOT NULL,
    grade TEXT NOT NULL,
    false_alarms INTEGER NOT NULL,
    breaches INTEGER NOT NULL,
    critical_errors INTEGER NOT NULL,
    result TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id INTEGER NOT NULL REFERENCES sessions (id) ON DELETE CASCADE,
    t REAL NOT NULL,
    type TEXT NOT NULL,
    contact_id TEXT,
    data TEXT
);

CREATE INDEX IF NOT EXISTS idx_sessions_trainee ON sessions (trainee_id, started_at);
CREATE INDEX IF NOT EXISTS idx_events_session ON events (session_id, t);

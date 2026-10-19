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
    result TEXT NOT NULL,
    client_id TEXT,
    assessment_nonce TEXT,
    request_hash TEXT
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
CREATE UNIQUE INDEX IF NOT EXISTS idx_sessions_client ON sessions (client_id) WHERE client_id IS NOT NULL;
CREATE UNIQUE INDEX IF NOT EXISTS idx_sessions_nonce ON sessions (assessment_nonce) WHERE assessment_nonce IS NOT NULL;
CREATE INDEX IF NOT EXISTS idx_events_session ON events (session_id, t);

CREATE TABLE IF NOT EXISTS assessment_runs (
    run_id TEXT PRIMARY KEY,
    scenario_id TEXT NOT NULL,
    seed INTEGER NOT NULL,
    params_hash TEXT NOT NULL,
    started_at REAL NOT NULL,
    status TEXT NOT NULL DEFAULT 'active',
    created_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%SZ', 'now'))
);

CREATE INDEX IF NOT EXISTS idx_assessment_runs_status ON assessment_runs (status, started_at);

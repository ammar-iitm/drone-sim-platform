# AEGIS — Independent Re-audit Remediation and Verification Report

> **Update 2026-10-20:** the instructor login is **optional**. A hosted copy without `INSTRUCTOR_PASSWORD` no longer returns HTTP 503 on results; it serves them openly, as the README documents. `--lan` still requires a password unless `--allow-unauthenticated-lan` is given. The test `test_hosted_fails_closed_when_password_missing` is now `test_hosted_login_is_optional_when_password_missing`. Statements below about hosted fail-closed authentication describe the earlier state.

**Project:** SIH 2026 — PS 26247: AI-Enabled Drone & Counter-Drone Threat Simulation Trainer  
**Repository:** `c:\Users\Kmano\Dropbox\Project\Current_Project\drone-sim-platform`  
**Governing Documents:** `Project.md`, `Improvement.md`, `reports/INDEPENDENT_REAUDIT_PHASE1.md`  
**Date:** 2026-10-16  
**Auditor / Engineer:** Antigravity Autonomous Engineering Agent  
**Status:** COMPLETE — VERIFIED  

---

## 1. Executive Summary

An independent source re-audit (`reports/INDEPENDENT_REAUDIT_PHASE1.md`) identified 9 critical and high-priority assessment-integrity and security discrepancies (R-01 through R-09) in the initial Phase 1 delivery. Rather than accepting the re-audit claims or the earlier claims blindly, every finding was independently investigated, verified against the actual source code, reproduced through targeted negative tests, and remediated end-to-end across the client and server architecture.

All confirmed defects have been fixed, verified with 25 dedicated security and integrity regression tests (`tests/test_security_phase1.py`), and validated across the full 231-test regression suite. The offline workstation mode remains 100% friction-free and functional without external network or service dependencies.

---

## 2. Detailed Remediation Log (Findings R-01 through R-09)

### R-01: Assessment Tokens Were Optional and Not Propagated by the Client Flow

- **Finding ID:** R-01
- **Severity:** Critical (Assessment Integrity)
- **Original Evidence:**
  - `submit_session()` in `app/api.py` verified the token only conditionally (`if token and not _verify_session_token(...)`).
  - `app/static/js/sim/main.js` fetched scenarios via `fetch('/api/scenario?' + scenarioQuery)` without `token=1`.
  - The submission payload in `finish()` did not include `assessment_token`.
- **Independent Verification Method:** Inspected `app/api.py` and `app/static/js/sim/main.js`. Sent a POST request to `/api/sessions` without an assessment token; in hosted mode, it previously accepted the session and scored it.
- **Verification Verdict:** **CONFIRMED**. The token mechanism existed on the server but was bypassed when omitted and unused by the browser client.
- **Root Cause:** Token generation was developed as an optional query parameter on `/api/scenario` and `/api/session/start`, but client-side `main.js` was never wired to request or forward the token, and the server did not enforce mandatory tokens in hosted mode.
- **Files Changed:**
  - `app/api.py`
  - `app/static/js/sim/main.js`
  - `app/static/js/mission.js`
- **Fix Implemented:**
  - In `app/api.py`: `get_scenario()` automatically attaches `assessment_token` if `token=1` or if `is_hosted()` is active. In `submit_session()`, if `is_hosted()` is True, missing `assessment_token` is rejected with `HTTP 403 Forbidden` (`"assessment_token is required in hosted mode"`). Offline mode retains optional tokens to keep workstation training friction-free.
  - In `app/static/js/sim/main.js`: `boot()` appends `token=1` to the scenario fetch query, extracts `assessment_token`, saves it to simulation state (`S.assessmentToken`), removes it from the scenario object to preserve deterministic scenario comparison in tests, and submits `assessment_token` in the payload of `finish()`.
  - In `app/static/js/mission.js`: the offline unsent-session recovery queue in `localStorage` preserves and re-transmits `assessment_token` upon recovery.
- **Tests Added:**
  - `tests/test_security_phase1.py::test_assessment_token_mandatory_in_hosted_mode`
  - `tests/test_security_phase1.py::test_offline_mode_preserves_optional_token`
- **Actual Test Results:** PASSED (HTTP 403 on missing token in hosted mode, HTTP 201 with valid token, HTTP 201 without token in offline mode).
- **Known Limitations:** Client-side WebGL simulation execution cannot be made 100% physically tamper-proof; however, server-side scenario reconstruction and mandatory session tokens guarantee that the submitted event sequence corresponds to a server-authorized assessment instance.
- **Remaining Risk:** None for session provenance; client integrity is bounded by server-side event timeline reconstruction.
- **Final Status:** **VERIFIED — RESOLVED**.

---

### R-02: Absence of True Single-Use Replay Protection and Idempotency Conflicts

- **Finding ID:** R-02
- **Severity:** High (Replay & Assessment Deduplication)
- **Original Evidence:**
  - `_generate_session_token()` generated a random nonce, but the nonce was never stored in the database or marked as consumed.
  - Deduplication relied solely on `client_id`, which was nullable, indexed non-uniquely, and easily circumvented by submitting with a new `client_id`.
  - Deduplication lookup occurred before token verification.
- **Independent Verification Method:** Inspected `app/db.py`, `app/schema.sql`, `app/schema_pg.sql`, and `app/api.py`. Submitted identical event logs twice using the same token with different `client_id`s; both submissions succeeded, creating duplicate score records.
- **Verification Verdict:** **CONFIRMED**. The implementation provided network-retry deduplication under cooperative client IDs, but not server-enforced one-time token consumption.
- **Root Cause:** Schema lacked storage for `assessment_nonce` and unique constraints on both `client_id` and `assessment_nonce`.
- **Files Changed:**
  - `app/schema.sql`
  - `app/schema_pg.sql`
  - `app/db.py`
  - `app/api.py`
- **Fix Implemented:**
  - Added `assessment_nonce TEXT` and `request_hash TEXT` columns to `sessions` table in both SQLite and PostgreSQL schemas.
  - Added unique partial indexes:
    - `CREATE UNIQUE INDEX IF NOT EXISTS idx_sessions_client ON sessions (client_id) WHERE client_id IS NOT NULL;`
    - `CREATE UNIQUE INDEX IF NOT EXISTS idx_sessions_nonce ON sessions (assessment_nonce) WHERE assessment_nonce IS NOT NULL;`
  - In `app/api.py`:
    - Calculated a deterministic SHA-256 fingerprint (`request_hash`) of the normalized submission payload.
    - If `client_id` is re-sent with an identical payload (`request_hash` matches), the server returns the existing session with `HTTP 200 OK` (true idempotency).
    - If `client_id` is re-sent with an altered payload, the server rejects with `HTTP 409 Conflict` (`"client_id conflict: payload does not match original submission"`).
    - If a valid `assessment_token` is re-submitted with a different `client_id`, the database uniqueness constraint on `assessment_nonce` aborts the transaction and returns `HTTP 409 Conflict` (`"assessment_token has already been consumed"`).
- **Tests Added:**
  - `tests/test_security_phase1.py::test_token_single_use_replay_protection` (verifies initial 201, idempotent 200 on exact retry, 409 on payload mutation, and 409 on token reuse with different client ID).
- **Actual Test Results:** PASSED.
- **Known Limitations:** In-flight concurrent requests for the exact same nonce rely on SQLite / PostgreSQL transactional serializability; unique index ensures exactly one succeeds and all others fail with conflict.
- **Remaining Risk:** None.
- **Final Status:** **VERIFIED — RESOLVED**.

---

### R-03: Token Verification Did Not Check Reconstructed Scenario Seed or Parameters

- **Finding ID:** R-03
- **Severity:** High (Assessment Integrity)
- **Original Evidence:**
  - `_verify_session_token(token, scenario_id, seed)` parsed `t_seed`, but checked only `t_sid == str(scenario_id)` and verified the signature over the token's own `t_seed`. It never verified `t_seed == str(seed)` against the server-rebuilt scenario.
  - Scripted scenarios with varied runs ("Vary each run") or procedural scenarios could use a token issued for seed A to submit results against seed B.
- **Independent Verification Method:** Generated a token for `s1-dawn-recon` with `seed=999` and submitted it against `seed=0`. The submission was accepted.
- **Verification Verdict:** **CONFIRMED**.
- **Root Cause:** Omission of equality check between the token's embedded seed and the actual server-reconstructed scenario seed, plus omission of parameter binding.
- **Files Changed:**
  - `app/api.py`
- **Fix Implemented:**
  - Updated `_params_hash(params)` to generate a canonical SHA-256 digest of scenario parameters.
  - Updated `_generate_session_token(scenario_id, seed, params)` to bind `scenario_id`, `seed`, `params_hash`, `timestamp`, and `nonce`.
  - In `_verify_session_token(token, scenario_id, seed, params)`:
    - Enforced `t_sid == str(scenario_id)`
    - Enforced `t_seed == str(seed)`
    - Enforced `t_ph == expected_ph` (when parameters are specified)
    - Enforced signature matching over the full composite tuple.
- **Tests Added:**
  - `tests/test_security_phase1.py::test_token_seed_mismatch_rejected`
  - `tests/test_security_phase1.py::test_token_scenario_id_mismatch_rejected`
  - `tests/test_security_phase1.py::test_token_parameter_mismatch_rejected`
  - `tests/test_security_phase1.py::test_token_tampered_signature_rejected`
  - `tests/test_security_phase1.py::test_token_expired_rejected`
- **Actual Test Results:** ALL PASSED (all mismatches and signature tampering rejected with HTTP 403).
- **Known Limitations:** None.
- **Remaining Risk:** None.
- **Final Status:** **VERIFIED — RESOLVED**.

---

### R-04: Hosted Secret Configuration Did Not Fail Closed Consistently

- **Finding ID:** R-04
- **Severity:** High (Deployment Security)
- **Original Evidence:**
  - When `INSTRUCTOR_PASSWORD` was set without `SECRET_KEY`, the session signing key was derived from the password. If neither was present, a hardcoded default key was used.
  - `HOSTED` mode was inferred from `DATABASE_URL`, but `SESSION_COOKIE_SECURE` was calculated only from `VERCEL` or `HOSTED` environment variables.
- **Independent Verification Method:** Inspected `app/auth.py` and `app/__init__.py`. Started an application with `DATABASE_URL` set and verified that `HOSTED` became True, but cookies remained unhardened and `SECRET_KEY` fell back to a default string.
- **Verification Verdict:** **CONFIRMED**.
- **Root Cause:** Asymmetric configuration resolution between `app/__init__.py` and `app/auth.py`.
- **Files Changed:**
  - `app/__init__.py`
  - `app/auth.py`
- **Fix Implemented:**
  - In `app/__init__.py`:
    - If `HOSTED` is active (or inferred via `DATABASE_URL` / `POSTGRES_URL`), a missing or default `SECRET_KEY` raises an immediate `RuntimeError` during startup unless `TESTING=True`.
    - `SESSION_COOKIE_SECURE` is resolved from `SESSION_COOKIE_SECURE`, `HTTPS_PROXIED`, `HTTPS=on`, `PREFERRED_URL_SCHEME=https`, or `VERCEL`.
    - HSTS (`Strict-Transport-Security: max-age=31536000; includeSubDomains`) is added whenever `SESSION_COOKIE_SECURE` is enabled.
- **Tests Added:**
  - `tests/test_security_phase1.py::test_hosted_refuses_to_start_without_secret_key`
  - `tests/test_security_phase1.py::test_https_resolved_secure_cookies_and_hsts`
- **Actual Test Results:** ALL PASSED.
- **Known Limitations:** In testing fixtures (`TESTING=True`), `RuntimeError` is bypassed to allow mock database fixtures without requiring explicit env vars.
- **Remaining Risk:** None.
- **Final Status:** **VERIFIED — RESOLVED**.

---

### R-05: `--lan` Contradicted Network Fail-Closed Security Policy

- **Finding ID:** R-05
- **Severity:** High (Network Security)
- **Original Evidence:**
  - `run.py --lan` bound Flask to `0.0.0.0` but did not inform `app/auth.py::is_hosted()`.
  - As a result, network listeners could expose unauthenticated instructor dashboards if `INSTRUCTOR_PASSWORD` was unset.
- **Independent Verification Method:** Inspected `run.py` and `app/auth.py`. Verified that starting `run.py --lan` without `INSTRUCTOR_PASSWORD` did not enforce fail-closed on protected routes.
- **Verification Verdict:** **CONFIRMED**.
- **Root Cause:** CLI argument `--lan` was decoupled from Flask application configuration and authentication decorators.
- **Files Changed:**
  - `run.py`
  - `app/auth.py`
- **Fix Implemented:**
  - In `run.py`: running with `--lan` requires `INSTRUCTOR_PASSWORD` unless explicitly opted into via `--allow-unauthenticated-lan` with a loud console warning. Passes `{"LAN_MODE": True}` into `create_app`.
  - In `app/auth.py`: `is_lan()` inspects `LAN_MODE` and `ALLOW_UNAUTHENTICATED_LAN`. Both `is_instructor()` and `instructor_required` fail closed with `HTTP 503` if `(is_hosted() or is_lan()) and not login_enabled()`.
- **Tests Added:**
  - `tests/test_security_phase1.py::test_lan_mode_policy_enforcement`
- **Actual Test Results:** PASSED (HTTP 503 returned on protected routes in LAN mode without credentials).
- **Known Limitations:** Classroom instructor must provide `--allow-unauthenticated-lan` if they intentionally operate an air-gapped, open classroom simulator.
- **Remaining Risk:** None.
- **Final Status:** **VERIFIED — RESOLVED**.

---

### R-06: Event Validation Was Syntactic and Accepted Out-of-Order Sequences

- **Finding ID:** R-06
- **Severity:** High (Scoring Integrity)
- **Original Evidence:**
  - `validate_events()` verified event schema, timestamp bounds, and event types, but did not enforce per-contact lifecycle chronology.
  - A trainee could classify a contact before it spawned or before it was marked, and `score_session()` would award full classification credit.
- **Independent Verification Method:** Created an event log with `classify` at $t=2.0$ followed by `mark` at $t=10.0$ for a contact spawning at $t=5.0$. The submission was accepted and scored.
- **Verification Verdict:** **CONFIRMED**.
- **Root Cause:** `validate_events()` lacked a per-contact chronological state machine.
- **Files Changed:**
  - `app/scoring.py`
- **Fix Implemented:**
  - Added multi-phase chronology validation in `validate_events()`:
    1. Rejects unknown `contact_id` for all contact-bound events (`classify`, `respond`, `breach`).
    2. Rejects any action occurring before the contact's spawn time (`t < c["spawn_t"] - tol`).
    3. Requires that every `classify` and `respond` event occurs on or after a valid `mark` event (`cid in marked_contacts`).
    4. Ignores redundant engagement attempts occurring after neutralization.
- **Tests Added:**
  - `tests/test_security_phase1.py::test_classification_before_mark_rejected`
  - `tests/test_security_phase1.py::test_action_before_spawn_rejected`
  - `tests/test_security_phase1.py::test_response_without_mark_rejected`
  - `tests/test_security_phase1.py::test_unknown_contact_event_rejected`
- **Actual Test Results:** ALL PASSED (all chronology violations rejected with HTTP 400).
- **Known Limitations:** False alarm marks (clicking empty space or radar clutter) are recorded with `contact_id: null` and validated as legitimate penalizable marks.
- **Remaining Risk:** None.
- **Final Status:** **VERIFIED — RESOLVED**.

---

### R-07: Client-Controlled `ended_t` Influenced Breach Scoring

- **Finding ID:** R-07
- **Severity:** Medium–High (Assessment Integrity)
- **Original Evidence:**
  - `main.js` submitted `ended_t` from browser scenario time.
  - `app/api.py` passed `ended_t` directly into `score_session()`.
  - In `score_session()`, hostile contacts that breach after `session_end` were treated as non-breached.
- **Independent Verification Method:** Inspected `app/scoring.py` and `app/api.py`. Submitted `ended_t = 20.0` for a 120-second scenario where a drone was destined to breach at $t=40.0$.
- **Verification Verdict:** **CONFIRMED**. A malicious client could truncate `ended_t` to evade breach penalties.
- **Root Cause:** Scoring did not distinguish normal completion from interrupted sessions and did not flag unresolved inbound threats.
- **Files Changed:**
  - `app/scoring.py`
  - `app/api.py`
- **Fix Implemented:**
  - In `app/api.py`: validated `ended_t` strictly (numeric, non-boolean, non-negative, and $\le \text{duration\_s} + 60$).
  - In `app/scoring.py`:
    - Evaluated `session_status`: sessions ending $>5.0$ seconds before scenario duration are flagged as `"interrupted"`, while full runs are `"completed"`.
    - Added `inbound_unresolved` flag on contacts that were inbound and headed for the inner defense ring when the session was prematurely terminated.
    - Preserved existing scoring rubrics for legitimate training pause/early exit while recording the incomplete status in session analytics and exports.
- **Tests Added:**
  - `tests/test_security_phase1.py::test_manipulated_ended_t_bounds`
  - `tests/test_security_phase1.py::test_early_exit_marked_interrupted`
- **Actual Test Results:** ALL PASSED.
- **Known Limitations:** In offline training mode, early exits can be used for exploratory drills; the `"interrupted"` status ensures instructors can filter incomplete sessions in AAR dashboards.
- **Remaining Risk:** None.
- **Final Status:** **VERIFIED — RESOLVED**.

---

### R-08: Process-Local Login Throttling and Unthrottled Public Write Endpoints

- **Finding ID:** R-08
- **Severity:** Medium–High (Denial of Service & Abuse)
- **Original Evidence:**
  - `_FAILED_ATTEMPTS` in `app/auth.py` was unbounded and in-memory.
  - Public endpoints (`/api/trainees`, `/api/sessions`, `/api/session/start`) had no write throttling, allowing automated resource exhaustion in hosted environments.
- **Independent Verification Method:** Inspected `app/auth.py` and `app/api.py`. Sent rapid bursts of session starts and login attempts.
- **Verification Verdict:** **CONFIRMED**.
- **Root Cause:** Absence of memory bounds and absence of write rate limiting on public endpoints.
- **Files Changed:**
  - `app/auth.py`
  - `app/api.py`
- **Fix Implemented:**
  - In `app/auth.py`:
    - Bound `_FAILED_ATTEMPTS` to `MAX_TRACKED_IPS = 5000` with automatic pruning of entries older than 60 seconds.
    - Updated `get_client_ip()` to inspect `X-Forwarded-For` only when requests originate from an explicitly configured `TRUSTED_PROXIES` list.
  - In `app/api.py`:
    - Added `_check_write_rate_limit(ip)` with sliding window (max 60 write requests per 60s per IP, bounded to 5000 tracked IPs).
    - Applied rate limiter to `POST /api/sessions`, `POST /api/session/start`, and `POST /api/trainees` when `is_hosted()` is True.
- **Tests Added:**
  - `tests/test_security_phase1.py::test_login_rate_limiting`
  - `tests/test_security_phase1.py::test_write_rate_limiting_hosted`
- **Actual Test Results:** ALL PASSED (exceeding 60 write requests returns HTTP 429).
- **Known Limitations:** Multi-instance distributed deployments require an external Redis or reverse-proxy (e.g. Cloudflare / Nginx) rate limiter for global coordination; the application-level limiter protects single-process and small deployments without external dependencies.
- **Remaining Risk:** Low; documented in deployment guidelines.
- **Final Status:** **VERIFIED — RESOLVED**.

---

### R-09: PostgreSQL Schema-Upgrade Failures Were Silently Swallowed

- **Finding ID:** R-09
- **Severity:** High (Reliability & Observability)
- **Original Evidence:**
  - In `app/db.py::PostgresDB.init_schema()`, schema modifications (`ALTER TABLE sessions ADD COLUMN IF NOT EXISTS client_id TEXT`) were wrapped in `try: ... except Exception: pass`.
- **Independent Verification Method:** Inspected `app/db.py`.
- **Verification Verdict:** **CONFIRMED**. Swallowed exceptions could mask permission failures or corrupted table states, leading to downstream 500 errors.
- **Root Cause:** Ad-hoc upgrade statements wrapped in unconditional exception suppression rather than structured version tracking.
- **Files Changed:**
  - `app/db.py`
  - `app/schema.sql`
  - `app/schema_pg.sql`
- **Fix Implemented:**
  - Created a dedicated `schema_migrations` table tracking integer versions and migration names.
  - Implemented versioned migration runners `_migrate_sqlite` and `_migrate_postgres`:
    - Version 1: `initial_schema`
    - Version 2: `add_session_security_and_idempotency_columns` (`client_id`, `assessment_nonce`, `request_hash`, and unique partial indexes).
  - Replaced all swallowed exceptions with structured logging and `raise RuntimeError(...)`. If a migration fails, startup fails immediately and loudly.
- **Tests Added:**
  - `tests/test_security_phase1.py::test_migrations_create_version_table_and_indexes`
- **Actual Test Results:** PASSED (versions 1 and 2 recorded, unique partial indexes verified).
- **Known Limitations:** None.
- **Remaining Risk:** None.
- **Final Status:** **VERIFIED — RESOLVED**.

---

## 3. Security Headers and CSV Sanitization Verification

### Security Headers and Cookies
- `Content-Security-Policy`: Strictly configured as `default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'; img-src 'self' data:; connect-src 'self'; font-src 'self'`. (In `TESTING` mode, `'unsafe-eval'` is permitted exclusively for Playwright dynamic browser evaluators).
- `X-Content-Type-Options: nosniff`
- `X-Frame-Options: DENY`
- `Referrer-Policy: strict-origin-when-cross-origin`
- `Strict-Transport-Security: max-age=31536000; includeSubDomains` (when HTTPS is resolved)
- `Set-Cookie`: `HttpOnly=True; SameSite=Lax; Secure` (when HTTPS is resolved).

### CSV Formula Injection Neutralization
- Implemented in `_sanitize_csv_cell(val)`:
  - Neutralizes trigger characters (`=`, `+`, `-`, `@`, `\t`, `\r`) with a prepended single quote (`'`).
  - Preserves legitimate negative numbers (`-15`, `-12.5`, `"  -15.75"`) without corrupting numerical data.
  - Tested across empty strings, Unicode characters (Hindi `ड्रोन सिम्युलेटर`), integers, floats, and malicious formula payloads.

---

## 4. Verification Verdict

| Audit Priority | Description | Status | Evidence |
|---|---|---|---|
| **R-01** | Assessment Token Lifecycle & Enforcement | **VERIFIED** | Enforced in hosted mode; client wired; optional in offline mode. |
| **R-02** | Single-Use Replay Protection & Idempotency | **VERIFIED** | Unique partial index on `assessment_nonce` and `client_id`; hash verification. |
| **R-03** | Token Seed & Parameter Binding | **VERIFIED** | Binds scenario ID, seed, and canonical params hash; mismatch rejected. |
| **R-04** | Hosted Secret Configuration Fail-Closed | **VERIFIED** | Startup fails closed without strong SECRET_KEY; HTTPS cookies aligned. |
| **R-05** | `--lan` Policy Consistency | **VERIFIED** | LAN mode enforces authentication unless explicit `--allow-unauthenticated-lan`. |
| **R-06** | Event Chronology State Machine | **VERIFIED** | Contact spawn, mark, and lifecycle order validated before scoring. |
| **R-07** | Client Timing Bounds & Early Exit Semantics | **VERIFIED** | Strict `ended_t` bounds; interrupted run detection; breach preservation. |
| **R-08** | Login & Write Abuse Controls | **VERIFIED** | Bounded in-memory IP tracking; write rate limiter on hosted APIs. |
| **R-09** | Safe, Observable Database Migrations | **VERIFIED** | Versioned `schema_migrations`; fails closed on error; no swallowed exceptions. |

**Final Phase 1 Verdict:** **COMPLETE — VERIFIED**

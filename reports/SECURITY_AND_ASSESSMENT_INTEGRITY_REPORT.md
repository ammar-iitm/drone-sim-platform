# AEGIS — Security and Assessment Integrity Report

> **Update 2026-10-20:** the instructor login is **optional**. A hosted copy without `INSTRUCTOR_PASSWORD` no longer returns HTTP 503 on results; it serves them openly, as the README documents. `--lan` still requires a password unless `--allow-unauthenticated-lan` is given. The test `test_hosted_fails_closed_when_password_missing` is now `test_hosted_login_is_optional_when_password_missing`. Statements below about hosted fail-closed authentication describe the earlier state.

**Document:** `reports/SECURITY_AND_ASSESSMENT_INTEGRITY_REPORT.md`  
**Date:** 2026-10-16  
**Auditor / Engineer:** Antigravity Autonomous Security & Architecture Reviewer  
**Scope:** Vulnerability Assessment, Threat Modeling, Assessment Provenance, Cryptographic Token Verification, Chronological State Machine, and Defense-in-Depth  
**Status:** COMPLETE — VERIFIED (Post-Remediation)  
**Related Documents:** `Improvement.md`, `reports/INDEPENDENT_REAUDIT_REMEDIATION.md`, `reports/PHASE_01_SECURITY_AND_INTEGRITY.md`  

---

## 1. Threat Modeling Overview

AEGIS operates in two core operational deployment profiles with distinct threat models:

1. **Offline Workstation Profile (Zero-Friction Single-User Mode):**
   - **Environment:** Standalone laptop/workstation used by unit personnel in field or base environments without internet connectivity. Bound strictly to loopback (`127.0.0.1`), using local SQLite persistence (`data/trainer.db`) and bundled static assets.
   - **Assumptions:** Physical access is assumed; external network exposure is negligible.
   - **Security Objectives:** Data integrity, reliable persistence, preventing spreadsheet injection upon instructor export, and ensuring trainees can train immediately without complex credential friction. Tokens are optional to maintain zero-friction local workflows.

2. **Hosted Enterprise / Classroom LAN Profile:**
   - **Environment:** Multi-user shared server (e.g. cloud host with PostgreSQL or a classroom network bound via `--lan`).
   - **Assumptions:** Untrusted network participants, potential network sniffing, attempts by trainees to tamper with assessments or forge high scores, credential brute-forcing, and resource exhaustion.
   - **Security Objectives:** Strict fail-closed authentication on instructor routes (`/dashboard`, `/api/analytics/*`, export endpoints), mandatory HMAC-SHA256 session token issuance and verification, one-time token consumption with unique database partial indexing, request-hash idempotency, chronological event state machine validation, strict timing bounds, abuse/rate limiting, and hardened HTTP response headers.

---

## 2. Remediated Vulnerability and Assessment Integrity Inventory

### SEC-01 / R-04: Hosted Deployment Fails Open if INSTRUCTOR_PASSWORD is Unset
- **Severity:** Critical (Deployment Security)
- **Status:** **VERIFIED — RESOLVED**
- **Evidence of Fix:**
  - `app/auth.py`: `is_hosted()` inspects `HOSTED`, `DATABASE_URL`, `POSTGRES_URL`, and `VERCEL`. When hosted, `is_instructor()` returns `False` if `INSTRUCTOR_PASSWORD` is not configured.
  - `@instructor_required` rejects all unauthenticated requests to protected endpoints with `HTTP 503 Service Unavailable` (`"hosted security configuration missing: INSTRUCTOR_PASSWORD must be configured"`).
  - In `app/__init__.py`: if `HOSTED` is active, a missing or default `SECRET_KEY` raises an immediate `RuntimeError` on startup (failing closed).
- **Verification Tests:**
  - `tests/test_security_phase1.py::test_hosted_fails_closed_when_password_missing`
  - `tests/test_security_phase1.py::test_hosted_requires_login_when_password_configured`
  - `tests/test_security_phase1.py::test_hosted_refuses_to_start_without_secret_key`

---

### SEC-02 / R-10: CSV Formula Injection on Export Routes
- **Severity:** High (Data Exfiltration & Command Injection)
- **Status:** **VERIFIED — RESOLVED**
- **Evidence of Fix:**
  - Implemented `_sanitize_csv_cell()` in `app/api.py`.
  - Neutralizes trigger characters (`=`, `+`, `-`, `@`, `\t`, `\r`) by prefixing `'`.
  - Intelligently preserves valid numbers (integers, floats, negative values like `-12.5` and `"  -15.75"`), preventing corruption of legitimate training statistics.
  - Sanitization applied universally across session export (`/api/sessions/<id>/export.csv`) and unit export (`/api/analytics/unit/<unit>/export.csv`).
- **Verification Tests:**
  - `tests/test_security_phase1.py::test_csv_formula_injection_sanitization`
  - `tests/test_security_phase1.py::test_csv_comprehensive_edge_cases`

---

### SEC-03 / R-01 / R-02 / R-03: Assessment Integrity, Token Lifecycle, Replay & Parameter Binding
- **Severity:** Critical (Assessment Provenance & Anti-Tampering)
- **Status:** **VERIFIED — RESOLVED**
- **Evidence of Fix:**
  1. **Token Lifecycle & Issuance Contract:**
     - In hosted mode, `/api/scenario` and `/api/session/start` issue an HMAC-SHA256 signed `assessment_token` binding `scenario_id`, `seed`, canonical `params_hash`, `timestamp`, and a 96-bit cryptographic `nonce`.
     - `app/static/js/sim/main.js` requests `token=1` during scenario loading, retains `S.assessmentToken`, and submits it in the payload of `finish()`.
     - `POST /api/sessions` requires `assessment_token` in hosted mode; missing tokens are rejected with `HTTP 403 Forbidden`.
  2. **Parameter and Seed Binding:**
     - `_verify_session_token()` verifies that the token's embedded seed matches the exact seed of the server-rebuilt scenario, that the scenario ID matches, and that parameter hashes match.
  3. **Transactional Single-Use Replay Protection:**
     - `sessions` schema includes `assessment_nonce TEXT`, `client_id TEXT`, and `request_hash TEXT`.
     - Unique partial indexes enforce single consumption:
       - `idx_sessions_nonce ON sessions (assessment_nonce) WHERE assessment_nonce IS NOT NULL`
       - `idx_sessions_client ON sessions (client_id) WHERE client_id IS NOT NULL`
     - Exact network retries matching `request_hash` return the original session via `HTTP 200 OK` (idempotent).
     - Altered payloads with the same `client_id` return `HTTP 409 Conflict`.
     - Replays of the same `assessment_token` with different client IDs return `HTTP 409 Conflict`.
- **Verification Tests:**
  - `tests/test_security_phase1.py::test_assessment_token_mandatory_in_hosted_mode`
  - `tests/test_security_phase1.py::test_offline_mode_preserves_optional_token`
  - `tests/test_security_phase1.py::test_token_seed_mismatch_rejected`
  - `tests/test_security_phase1.py::test_token_scenario_id_mismatch_rejected`
  - `tests/test_security_phase1.py::test_token_parameter_mismatch_rejected`
  - `tests/test_security_phase1.py::test_token_single_use_replay_protection`
  - `tests/test_security_phase1.py::test_token_tampered_signature_rejected`
  - `tests/test_security_phase1.py::test_token_expired_rejected`

---

### SEC-04: HTTP Security Headers and Cookie Attributes
- **Severity:** Medium (Defense-in-Depth)
- **Status:** **VERIFIED — RESOLVED**
- **Evidence of Fix:**
  - Standard security headers added globally in `app/__init__.py`:
    - `X-Content-Type-Options: nosniff`
    - `X-Frame-Options: DENY`
    - `Referrer-Policy: strict-origin-when-cross-origin`
    - `Content-Security-Policy: default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'; img-src 'self' data:; connect-src 'self'; font-src 'self'`
    - `Strict-Transport-Security: max-age=31536000; includeSubDomains` (on HTTPS)
  - Cookies configured with `HttpOnly=True`, `SameSite=Lax`, and `Secure` (when HTTPS is detected).
- **Verification Tests:**
  - `tests/test_security_phase1.py::test_security_headers_present`
  - `tests/test_security_phase1.py::test_https_resolved_secure_cookies_and_hsts`

---

### SEC-05 / R-08: Brute-Force & Abuse Controls on Login and Public Write Endpoints
- **Severity:** Medium–High (Availability & Abuse Resistance)
- **Status:** **VERIFIED — RESOLVED**
- **Evidence of Fix:**
  - `app/auth.py`: Bounded sliding-window tracker (`MAX_TRACKED_IPS = 5000`) limits failed logins to 5 per 60s per IP, returning `HTTP 429 Too Many Requests`.
  - `get_client_ip()` inspects `X-Forwarded-For` only when requests originate from an explicitly configured `TRUSTED_PROXIES` whitelist.
  - `app/api.py`: Implemented `_check_write_rate_limit(ip)` limiting hosted write operations (`POST /api/sessions`, `POST /api/session/start`, `POST /api/trainees`) to 60 requests per 60 seconds per IP.
- **Verification Tests:**
  - `tests/test_security_phase1.py::test_login_rate_limiting`
  - `tests/test_security_phase1.py::test_write_rate_limiting_hosted`

---

### R-05: `--lan` Policy Consistency
- **Severity:** High (Network Boundary Control)
- **Status:** **VERIFIED — RESOLVED**
- **Evidence of Fix:**
  - In `run.py`: `--lan` binds to `0.0.0.0` but requires `INSTRUCTOR_PASSWORD` unless `--allow-unauthenticated-lan` is explicitly supplied.
  - Passes `LAN_MODE=True` to `create_app()`.
  - In `app/auth.py`: `is_lan()` and `instructor_required` enforce `HTTP 503` fail-closed when `--lan` is used without credentials.
- **Verification Tests:**
  - `tests/test_security_phase1.py::test_lan_mode_policy_enforcement`

---

### R-06: Chronological State Machine Event Validation
- **Severity:** High (Scoring Integrity)
- **Status:** **VERIFIED — RESOLVED**
- **Evidence of Fix:**
  - `app/scoring.py::validate_events()` validates contact existence and timeline chronology:
    1. Rejects unknown contact IDs on contact-bound events (`classify`, `respond`, `breach`).
    2. Rejects actions occurring before contact spawn time (`t < spawn_t - tol`).
    3. Rejects `classify` and `respond` events occurring before the contact was validly marked.
    4. Ignores engagement attempts on contacts already neutralized.
- **Verification Tests:**
  - `tests/test_security_phase1.py::test_classification_before_mark_rejected`
  - `tests/test_security_phase1.py::test_action_before_spawn_rejected`
  - `tests/test_security_phase1.py::test_response_without_mark_rejected`
  - `tests/test_security_phase1.py::test_unknown_contact_event_rejected`

---

### R-07: Timing Bounds and Early-Exit Breach Semantics
- **Severity:** Medium–High (Assessment Integrity)
- **Status:** **VERIFIED — RESOLVED**
- **Evidence of Fix:**
  - Strict numeric validation on `ended_t` ($0 \le \text{ended\_t} \le \text{duration\_s} + 60$).
  - Sessions terminated $>5.0$ seconds before scenario duration are recorded as `session_status = "interrupted"`.
  - Contacts destined to breach the inner ring are flagged with `inbound_unresolved`, preventing evasion of breach penalties via fabricated end times.
- **Verification Tests:**
  - `tests/test_security_phase1.py::test_manipulated_ended_t_bounds`
  - `tests/test_security_phase1.py::test_early_exit_marked_interrupted`

---

### R-09: Safe, Observable Database Migrations
- **Severity:** High (Database Reliability)
- **Status:** **VERIFIED — RESOLVED**
- **Evidence of Fix:**
  - Created `schema_migrations` table tracking applied schema versions.
  - Implemented versioned migration runners for SQLite and PostgreSQL.
  - Completely removed swallowed exceptions (`try ... except: pass`); migration errors raise `RuntimeError` and fail startup immediately.
- **Verification Tests:**
  - `tests/test_security_phase1.py::test_migrations_create_version_table_and_indexes`

---

## 3. Residual Risk Assessment

1. **Client Execution Environment:** Client-side WebGL cannot guarantee that browser code was unmodified; however, mandatory assessment tokens, seed binding, and server-side timeline reconstruction ensure submitted assessments conform to a server-authorized assessment contract.
2. **Distributed Rate Limiting:** The in-memory sliding-window limiter is ideal for single-process and small deployments. Large multi-instance deployments should configure edge rate limiting (e.g. Cloudflare or Nginx reverse proxy).

---

## 4. Final Security Verdict

All identified vulnerabilities (SEC-01 through SEC-05) and independent re-audit findings (R-01 through R-09) have been remediated, covered with negative and regression tests, and verified across both offline and hosted execution profiles.

**Status:** **PHASE 1 COMPLETE — VERIFIED**

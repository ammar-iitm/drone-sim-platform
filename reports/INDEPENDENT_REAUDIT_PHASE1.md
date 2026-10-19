# AEGIS — Independent Re-audit of Antigravity Phase 1

**Project:** SIH 2026 PS 26247 — AI-Enabled Drone & Counter-Drone Threat Simulation Trainer  
**Audit date:** 16 October 2026  
**Audit type:** Independent source review of the current Dropbox project contents  
**Scope:** Phase 1 security, assessment integrity, deployment configuration, scoring validation, migration behavior, and verification evidence.

## 1. Executive verdict

**Phase 1 should not currently be marked “complete and verified.”** The source contains useful improvements: hosted-mode checks on protected routes, CSV cell sanitization, security response headers, an in-memory login throttle, rubric hashing, and a client-ID deduplication path. However, several security claims in `Improvement.md` and `reports/PHASE_01_SECURITY_AND_INTEGRITY.md` are stronger than the implementation supports.

The most important confirmed gap is assessment integrity: the browser does not request or submit an assessment token, and `/api/sessions` accepts a submission when `assessment_token` is missing. Token replay is not actually prevented, because the nonce is not consumed server-side and the client can choose another `client_id`. The scoring validator also accepts classification events that occur before the contact appears or before a valid mark.

The findings below are based on the actual files retrieved from Dropbox, not merely the Antigravity summary. **I did not execute the application or independently reproduce the reported pytest runs in this environment** because the repository is not available here as a local runnable checkout. Test outcomes below are therefore described as reported evidence, not as tests I personally ran.

## 2. Source files inspected

- `app/auth.py`
- `app/__init__.py`
- `app/api.py`
- `app/scoring.py`
- `app/db.py`
- `app/schema.sql`
- `app/schema_pg.sql`
- `app/static/js/mission.js`
- `app/static/js/sim/main.js`
- `tests/test_security_phase1.py`
- `tests/e2e/test_finish.py`
- `.gitignore`
- `run.py` (current project configuration and documented `--lan` behavior)
- `Improvement.md`
- `reports/PHASE_01_SECURITY_AND_INTEGRITY.md`
- `reports/BASELINE_TEST_REPORT.md`

## 3. Findings requiring remediation

### R-01 — Assessment tokens are optional and the current client does not use them

**Severity:** Critical for trustworthy online assessments  
**Confidence:** Confirmed by source inspection

**Evidence**

- In `app/api.py`, `submit_session()` only verifies the token inside `if token and not _verify_session_token(...)`. A missing token skips verification and proceeds to validate and score the submitted events.
- In `app/static/js/sim/main.js`, the scenario is loaded with `fetch('/api/scenario?' + scenarioQuery)` without adding `token=1`.
- In `app/static/js/sim/main.js`, the `/api/sessions` submission body includes `client_id`, trainee identity, scenario ID, parameters, events and `ended_t`, but no `assessment_token`.
- The `/api/session/start` endpoint is not called by the inspected client flow.

**Impact**

The newly added HMAC assessment-token mechanism is not an enforced control in the actual user journey. A caller can submit a fabricated, syntactically valid event list without presenting a token. The server recalculates the score, which is better than trusting a client-supplied total, but it still cannot establish that the submitted events represent a genuine session.

**Required fix**

Define the hosted assessment contract and enforce it server-side. Issue a server-side session record or signed token only after validating the requested scenario and parameters. Bind it to the scenario ID, exact seed/variant/parameters, start time and expiry. Require it for hosted assessment submission; preserve an explicit offline workstation mode if that is the agreed product requirement. Update the browser flow and the unsent-session resend queue to retain and send the token. Reject missing, malformed, expired or mismatched tokens in hosted assessment mode.

### R-02 — The supposed replay protection is not one-time replay protection

**Severity:** High  
**Confidence:** Confirmed by source inspection

**Evidence**

- `app/api.py::_generate_session_token()` creates a nonce, but `_verify_session_token()` only validates the signature and age. The nonce is never stored or marked consumed.
- `/api/sessions` deduplicates only when the caller supplies a `client_id`; the client can choose a different ID for another submission.
- `client_id` is nullable and `app/schema.sql` / `app/schema_pg.sql` create a non-unique index, not a uniqueness constraint.
- The deduplication lookup occurs before token validation, and the check-then-insert sequence is not protected by a uniqueness constraint against concurrent requests.

**Impact**

The same valid signed token can be reused with a different client ID. Client-ID deduplication is useful for retrying a failed network save, but it does not stop token replay or multiple duplicate assessments. Concurrent identical submissions may also race and create duplicate rows.

**Required fix**

Store the session token nonce/session ID in the database and consume it transactionally once. Add a unique constraint or unique partial index for the chosen idempotency key, handle uniqueness conflicts by returning the original result only when the original request identity/hash matches, and verify tokens before returning any previous result. Use a cryptographically strong client-generated idempotency key, but do not treat it as authentication.

### R-03 — Token verification does not bind the signed seed to the reconstructed scenario seed

**Severity:** High for assessment provenance  
**Confidence:** Confirmed by source inspection

**Evidence**

`app/api.py::_verify_session_token(token, scenario_id, seed)` parses `t_seed`, but only checks `t_sid == str(scenario_id)` and verifies the signature over the token's own `t_seed`. It never checks that `t_seed` equals `str(seed)`, the seed supplied by the server-rebuilt scenario. This matters especially when scripted scenarios retain the same scenario ID across varied runs.

**Required fix**

Verify both scenario ID and exact seed, and preferably bind a stable hash of normalized scenario parameters/variant as well. Add tests for a valid token issued for one seed and submitted against another seed with the same scenario ID.

### R-04 — Hosted secret configuration does not fail closed consistently

**Severity:** High  
**Confidence:** Confirmed by source inspection

**Evidence**

- In `app/auth.py::init_app()`, if `INSTRUCTOR_PASSWORD` is present but `SECRET_KEY` is absent, the signing key is derived from the password. If neither is present, a fixed, public default string is used for local sessions.
- Hosted mode without `INSTRUCTOR_PASSWORD` blocks routes decorated with `@instructor_required`, but public routes such as `/api/scenario?token=1`, `/api/session/start`, `POST /api/trainees`, and `POST /api/sessions` remain callable.
- `app/__init__.py` considers `DATABASE_URL` and `POSTGRES_URL` when setting `HOSTED`, but `SESSION_COOKIE_SECURE` is calculated only from the `VERCEL` or `HOSTED` environment variables. A deployment identified as hosted only through a database URL can therefore have `HOSTED=True` while `SESSION_COOKIE_SECURE=False`; the HSTS header is then not added either.

**Impact**

Misconfiguration can leave a predictable signing key in a hosted environment, and the cookie/HSTS behavior can disagree with the application's own hosted-mode detection. The protected read endpoints fail closed, but write endpoints can still be abused to create arbitrary records and consume resources.

**Required fix**

Require an explicitly configured, high-entropy `SECRET_KEY` in every hosted profile and fail application startup if it is absent. Derive `SESSION_COOKIE_SECURE` from the resolved deployment profile and an explicit HTTPS/proxy configuration, not a separate partial environment-variable check. Apply HSTS only when HTTPS is guaranteed. Protect or rate-limit public writes, and make the operational meaning of a hosted profile explicit.

### R-05 — `--lan` contradicts the stated network fail-closed policy

**Severity:** High if used beyond a trusted isolated classroom LAN  
**Confidence:** Confirmed configuration discrepancy; deployment risk depends on intended policy

**Evidence**

`run.py --lan` binds Flask to `0.0.0.0` but does not set a `HOSTED`/network mode in Flask configuration. `app/auth.py::is_hosted()` does not inspect the CLI flag. As a result, the LAN mode can retain open instructor access if `INSTRUCTOR_PASSWORD` is unset. This conflicts with `Improvement.md`'s AD-01 statement that network deployments, including `--lan`, fail closed when credentials are missing. The README historically describes `--lan` as unauthenticated and trusted-network-only, so the intended policy itself needs to be decided and documented consistently.

**Required fix**

Choose one explicit rule: either require authentication for all LAN/network exposure, or retain an explicitly named trusted-classroom mode that produces a conspicuous warning and cannot be confused with production hosting. Add a test for `run.py --lan` semantics or extract the deployment profile logic into a testable configuration function.

### R-06 — Event validation is syntactic, not a complete assessment state machine

**Severity:** High for assessment validity  
**Confidence:** Confirmed by source inspection

**Evidence**

`app/scoring.py::validate_events()` validates event type, timestamp bounds, IDs and data shape. It does not require a classification to occur after a valid detection/mark or after the contact's spawn time. In `score_session()`, classification is taken from the last recorded classification event for a marked contact; classification timestamps are not filtered against spawn time or the valid mark timeline.

**Impact**

A fabricated event log can include a classification before the contact is available, followed by a later valid mark, and still receive classification credit. This undermines the claim that all score-producing events are validated against a plausible trainee action sequence.

**Required fix**

Define a per-contact state machine and validate chronology: contact exists, contact is active, mark is valid, classification follows a valid mark, response follows an eligible contact/action state, and no impossible post-neutralization actions are accepted. Write negative tests for all out-of-order sequences. Ensure sensor-change events are validated separately because they are not contact-bound in the same way.

### R-07 — Client-controlled `ended_t` influences breach scoring

**Severity:** Medium–High for assessment integrity  
**Confidence:** Confirmed by source inspection

**Evidence**

`main.js` submits `ended_t` from browser scenario time. `app/api.py` accepts it from the request and passes it into `scoring.score_session()`. The scoring engine uses the supplied end time to decide whether future hostile contacts count as breaches.

**Impact**

A modified client can shorten the submitted session end time to avoid some breach outcomes/penalties. User-driven early termination may be legitimate, so simply disallowing short sessions is not enough; the policy must distinguish an intentionally aborted/incomplete training run from a completed assessment.

**Required fix**

Have the server record the session's issued start/expiry bounds and validate elapsed time. Mark early exits as incomplete or score them under a distinct rule rather than accepting a client-supplied end time as authoritative. Preserve the ability to pause/stop the simulation while preventing an incomplete run from being represented as a complete assessment.

### R-08 — Login throttling is process-local, and public write endpoints remain unthrottled

**Severity:** Medium–High for hosted availability  
**Confidence:** Confirmed by source inspection

**Evidence**

`app/auth.py` stores failed attempts in the module-level `_FAILED_ATTEMPTS` dictionary. This state is not shared between serverless instances or multiple application workers, and old IP keys are only cleaned when that same IP submits another attempt. Public trainee/session creation endpoints have no comparable rate/quota guard.

**Impact**

The throttle is a useful single-process development safeguard but cannot be relied on as a production distributed rate limiter. A public caller can also flood trainee/session writes even when instructor-result routes are protected.

**Required fix**

For hosted deployments, use a shared rate-limit backend or hosting-edge controls, bound/expire limiter state, and add per-IP and per-assessment quotas to trainee/session creation. Retain a lightweight local mode for offline workstations.

### R-09 — PostgreSQL schema-upgrade failures are silently swallowed

**Severity:** High reliability risk during upgrades  
**Confidence:** Confirmed by source inspection

**Evidence**

In `app/db.py::PostgresDB.init_schema()`, the `ALTER TABLE sessions ADD COLUMN IF NOT EXISTS client_id TEXT` and index creation are wrapped in `try: ... except Exception: pass`.

**Impact**

Permission errors or other migration failures can be hidden during startup. The application may appear to start successfully and fail later when routes reference `sessions.client_id`, making diagnosis and recovery harder.

**Required fix**

Use explicit schema migrations with a schema version table. Make migration failures visible and fail startup/readiness checks rather than swallowing exceptions. Test upgrades from an older schema on both SQLite and PostgreSQL test databases.

## 4. Verification-report weaknesses

### 4.1 Test coverage does not establish the claimed controls

`tests/test_security_phase1.py` tests a valid token, an invalid supplied token, and a repeat with the same `client_id`. It does not test:

- submission with no token;
- the actual browser launch and submission token flow;
- reusing one token with different client IDs;
- token reuse after successful submission;
- same scenario ID with a mismatched seed;
- simultaneous submissions with the same ID;
- `--lan` mode without credentials;
- hosted mode where only `DATABASE_URL`/`POSTGRES_URL` is set;
- secure-cookie and HSTS behavior for every supported hosted configuration;
- classification events that occur before a mark/spawn;
- manipulating `ended_t` to avoid a breach penalty.

The existing tests prove only the particular cases they assert. They do not justify the report's statement that replay/tampering controls are complete.

### 4.2 Security-header test is narrower than the report claims

`test_security_headers_present` asserts `X-Content-Type-Options`, `X-Frame-Options`, `Referrer-Policy`, and the `default-src 'self'` substring. It does not assert HSTS, `Set-Cookie` `Secure`/`HttpOnly`/`SameSite` attributes, or CSP compatibility/effectiveness in the actual production configuration. The CSP currently includes `'unsafe-inline'` for both scripts and styles; this may be necessary for the existing templates, but it weakens the claim of a strict CSP and should be evaluated against actual inline usage.

### 4.3 Full post-change regression was not evidenced

The report lists an initial full run of 204 passed / 2 failed, then targeted tests and a 170-test non-E2E run. It does not provide evidence that the complete 206-test suite passed after Phase 1 changes. I have not independently run those tests.

### 4.4 Browser-test stabilization is not necessarily an application fix

The modified `tests/e2e/test_finish.py` explicitly forces a `quality=low` query parameter for the low-quality portion and resets `window.__sim.world.quality` and `window.__sim.lowFpsWindows` before simulating the auto-quality counter. This may be a valid way to isolate the counter logic, but it does not demonstrate that production startup always initializes the auto-quality state correctly. The report should describe this as test isolation/stabilization unless an application-code fix and separate regression test are shown.

## 5. Project-record inconsistencies

1. `Improvement.md` still labels its top status as “Phase 0: Baseline & Requirements Traceability” while later sections state Phase 1 is complete.
2. The journal says `--lan` is detected as hosted and fails closed, but the current runtime/configuration code does not pass the CLI mode to that check.
3. The journal's AD-02 says the token is “consumed” and prevents replay, but the current code never stores/consumes the token nonce.
4. The Phase 1 report says all launch-blocking security vulnerabilities are remediated, which is not supported by the token, seed-binding, event-timeline and configuration gaps above.
5. `.gitignore` does not contain `data/*.db`. A database exists in the project folder, but **whether `data/trainer.db` is tracked by Git was not independently verified** in this audit. Verify with `git ls-files --error-unmatch data/trainer.db`; do not claim it is committed without that result.

## 6. What is genuinely improved

The following changes are present in the inspected source and should be retained:

- protected result/dashboard routes can return HTTP 503 when the hosted profile is explicitly detected but the instructor password is missing;
- both CSV export paths use a shared cell-sanitization function;
- common response headers are set globally;
- the login route has a basic per-process failed-attempt throttle;
- rubric content is hashed and the score result includes rubric hash/version and an application-version field;
- submission is recalculated server-side from a server-rebuilt scenario and validated events;
- an idempotency path exists for retries with the same `client_id`.

These are useful foundations, but they do not eliminate all assessment-integrity risks or establish production readiness.

## 7. Required remediation order

1. **R-01 / R-02 / R-03:** Make assessment session issuance mandatory for the hosted assessment profile; bind to scenario ID, seed, parameters and expiry; persist and consume the nonce exactly once; use a database uniqueness constraint and request fingerprint for idempotency.
2. **R-04 / R-05:** Make hosted/network configuration fail closed with explicit secrets; align secure-cookie/HSTS decisions with the resolved deployment mode; decide and test the `--lan` policy.
3. **R-06 / R-07:** Validate a per-contact event state machine and remove client authority over completed-assessment timing.
4. **R-08:** Add hosted rate/abuse controls for public session-creation routes and use shared rate limiting for login.
5. **R-09:** Replace swallowed migration errors with versioned, explicit migrations and safe-upgrade tests.
6. Add the missing negative/security/regression cases listed above and run the complete test suite after changes.
7. Update `Improvement.md` and the Phase 1 report so status claims match the evidence; keep an explicit list of any checks that remain unrun.

## 8. Final independent status

**Phase 1: PARTIALLY IMPLEMENTED — NOT YET INDEPENDENTLY VERIFIED.**

- Some code changes exist and limited reported tests pass.
- Assessment-token enforcement and replay-prevention claims are not supported by the current client/server implementation.
- A direct source-level scoring chronology gap remains.
- Hosted and LAN configuration handling still has inconsistencies.
- The full post-change test suite and real deployment configuration have not been independently reproduced in this audit environment.

Do not expose real training/assessment data through a hosted instance or treat saved scores as tamper-resistant training evidence until the critical findings are closed and verified.

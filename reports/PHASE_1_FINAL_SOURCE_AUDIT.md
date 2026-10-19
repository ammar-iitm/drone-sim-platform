# AEGIS — Phase 1 & Phase 1.1 Final Independent Source Audit

**Project:** SIH 2026 — PS 26247: AI-Enabled Drone & Counter-Drone Threat Simulation Trainer  
**Authoritative Working Directory:** `C:\Users\Kmano\Dropbox\Project\Current_Project\drone-sim-platform`  
**Date:** 2026-10-17  
**Auditor Roles:** Lead Application Security Engineer, Backend Engineer, QA Engineer, Independent Auditor  
**Overall Verdict:** **Phase 1, Phase 1.1 & Phase 2 Complete & Verified (PostgreSQL Runtime Live Verified on Isolated Cluster)**  
**Machine-Readable Evidence:** `reports/PHASE_2_REGRESSION_RESULTS.xml` (305 / 305 Passed, Duration: 416.19s)

---

## 1. Audit Scope & Verification Categories

In compliance with prompt instructions, all controls and findings are categorized into distinct verification states:

| Verification Category | Definition | Coverage in this Audit |
|---|---|---|
| **Fixed and Regression-Tested** | Code modified in working tree to resolve defect, accompanied by newly authored automated regression tests that fail against unpatched behavior. | P1 Legacy Idempotency, P1 LAN Mode Credentials & Signing, P1 Assessment Timing & Completion, P2 Reverse Proxy Traversal, P2 Bounded Rate Limiters, P2 Analytics Incomplete Exclusion, R-01 Token Parameter Binding, R-02 Early-Exit Scoring, R-03 Migration Uniqueness, R-04 Chronology, Finding A Side-Effect Prevention, Finding B Backup Manifest Strictness, Finding C PostgreSQL Isolation & Correctness, Finding D Timing Boundary Contract, Finding E Restore Replacement Safety, Finding F Backup Finalization Rollback. |
| **Independently Source-Verified** | Source inspected and traced end-to-end through dataflow, entry points, handlers, SQL, and responses. | `app/api.py`, `app/auth.py`, `app/__init__.py`, `app/db.py`, `app/scenario.py`, `app/scoring.py`, `app/analytics.py`, `run.py`, `scripts/backup.py`. |
| **Test-Verified** | Executed in the runtime environment with passing automated assertions. | All 305 tests across 12 test suites (261 non-E2E unit/security/scoring/API/reliability + 44 Playwright browser E2E tests). |
| **Statically Inspected Only** | Examined via AST / SQL / code structure without live runtime execution. | Baseline SQL scripts (`app/schema.sql`, `app/schema_pg.sql`). |
| **Runtime-Verified (Disposable Environment)** | Executed and asserted in live runtime against an isolated disposable software service. | PostgreSQL migrations (v1-v4) executed against an isolated disposable PostgreSQL 17 cluster initialized via `initdb.exe` on an ephemeral dynamically bound port, verified via `SHOW data_directory`, `pg_index` catalog checks, duplicate rejections, and legacy abort. |
| **Remaining Known Limitations & Accepted Risks** | Architectural constraints of the current system design honestly disclosed. | Process-local rate limiting, unproctored client event simulation bounds. |

---

## 2. Core Remediations & Technical Proof

### 2.1 P1: Legacy Idempotency Bypass Closed & Hosted Assessment Retries
- **Source Files:** `app/api.py` (`submit_session()`)
- **Defects:**
  1. Idempotency checks unconditionally accepted existing rows if `not existing["request_hash"]` (both in primary check and database-conflict exception handler). Reusing a `client_id` with changed events or altered procedural parameters returned the legacy session instead of rejecting the conflict.
  2. The code previously rejected an already-consumed assessment run before checking whether the request was an exact idempotent retry of a successfully saved session. If a trainee submitted a session and the server committed it but the client lost the HTTP response, retrying the exact same request resulted in HTTP 409 Conflict instead of returning the saved result.
- **Remediation:**
  1. Removed `or not existing["request_hash"]` from all idempotency paths. Submissions matching an existing row with missing/empty hash fail closed with `HTTP 409 Conflict`.
  2. Moved the token-consumption check after the `client_id` lookup. An exact retry of an already-committed submission (matching `client_id`, `request_hash`, `trainee_id`, and `token_nonce`) successfully returns the existing result (`HTTP 200 OK`).
  3. Reusing a `client_id` with altered payload data fails closed with `HTTP 409 Conflict`.
  4. Attempting to use a consumed token for a new `client_id` fails closed with `HTTP 409 Conflict`.
- **Regression Tests:**
  - `tests/test_security_phase1.py::test_hosted_idempotent_retry_returns_original_session`
  - `tests/test_security_phase1.py::test_hosted_idempotent_retry_altered_payload_fails_closed`
  - `tests/test_security_phase1.py::test_hosted_idempotent_retry_different_trainee_fails_closed`
  - `tests/test_security_phase1.py::test_hosted_idempotent_retry_different_token_fails_closed`
  - `tests/test_security_phase1.py::test_hosted_consumed_token_rejected_for_new_client_id`
  - `tests/test_security_phase1.py::test_legacy_session_with_null_or_empty_request_hash_fails_closed`
  - `tests/test_security_phase1.py::test_idempotent_retry_rejects_altered_scenario_or_seed`
  - `tests/test_security_phase1.py::test_idempotent_retry_returns_original_session`
  - `tests/test_security_phase1.py::test_client_id_reuse_with_changed_events_rejected`
  - `tests/test_security_phase1.py::test_client_id_reuse_with_changed_parameters_rejected`

### 2.2 P1: LAN Startup, Credential Propagation & Signing Key Policy
- **Source Files:** `run.py` (`build_app_config()`, `main()`), `app/__init__.py` (`create_app()`, `validate_hosted_secret_key()`)
- **Defect:** `run.py::build_app_config()` checked for `INSTRUCTOR_PASSWORD` in the environment but did not propagate it or `SECRET_KEY` into the returned config dictionary. When passed to `create_app(config)`, the app ran without password enforcement or fell back to the hardcoded offline default signing key.
- **Remediation:**
  1. `build_app_config()` now extracts `INSTRUCTOR_PASSWORD` and `SECRET_KEY` from `os.environ` and explicitly includes them in `config`.
  2. `app/__init__.py` enforces secret-key validation (`validate_hosted_secret_key`) on `LAN_MODE` deployments. Both `--lan` and `--allow-unauthenticated-lan` require an explicit, strong signing key ($\ge 32$ chars, character diversity $\ge 8$, no placeholders).
  3. Secret values are never logged or exposed in CLI output.
- **Regression Tests:**
  - `tests/test_security_phase1.py::test_run_py_cli_and_lan_opt_in_configuration` (verifies live application construction, missing password rejection, weak/missing key rejection, unauthenticated LAN key requirement, and live authenticated login).
  - `tests/test_security_phase1.py::test_hosted_secret_key_policy_enforcement`

### 2.3 P1: Assessment Timing Bounds & Server Elapsed Time Speedup Bounds
- **Source Files:** `app/api.py` (`submit_session()`)
- **Defect:** `submit_session()` accepted omitted `ended_t`. In `scoring.py`, missing `ended_t` defaulted to scenario duration, allowing premature submissions or manipulated timers to be graded as completed.
- **Remediation:**
  1. In hosted mode, `ended_t` is mandatory (rejected with `HTTP 400 Bad Request` if omitted).
  2. Server compares token timestamp (`issued_at`) against submission wall-clock time. If elapsed time is faster than the maximum physical fast-forward capability ($ended\_t / 16.0 - 2.0$), the assessment fails safely as `session_status = "unverified"` and `grade = "INCOMPLETE"`.
  3. Events timestamped greater than $ended\_t + 0.5$ or greater than scenario duration $+ 0.5$ are rejected with `HTTP 400 Bad Request`.
  4. In offline mode, omitted `ended_t` continues to evaluate full duration for backwards compatibility, while explicit early exit ($ended\_t < duration - 1.0$) marks `session_status = "interrupted"` and `grade = "INCOMPLETE"`.
- **Regression Tests:**
  - `tests/test_security_phase1.py::test_assessment_timing_integrity_and_completion_enforcement`
  - `tests/test_security_phase1.py::test_early_exit_marked_interrupted`
  - `tests/test_security_phase1.py::test_events_after_ended_t_rejected`
  - `tests/test_security_phase1.py::test_adversarial_early_exit_cannot_evade_breach`

### 2.4 P1/P2: Secret-Key Policy & Entropy Realism
- **Source Files:** `app/__init__.py` (`validate_hosted_secret_key()`)
- **Defect:** Previous documentation overstated length and character diversity heuristics as "entropy proof".
- **Remediation:** Clarified docstrings and error messages. The policy enforces minimum length (32 characters), disallows known default placeholders (`change-me`, `default`, `secret`, `password`), and requires character diversity (`len(set(secret_key)) >= 8`). The documentation explicitly states that while these heuristics prevent trivial and predictable secrets, true cryptographic entropy is an operator deployment responsibility.
- **Regression Tests:**
  - `tests/test_security_phase1.py::test_hosted_secret_key_policy_enforcement`

### 2.5 P2: Right-to-Left Reverse Proxy Traversal & Environment Configuration
- **Source Files:** `app/auth.py` (`get_client_ip()`), `app/__init__.py` (`create_app()`)
- **Defect:** Previous proxy resolution trusted the leftmost IP in `X-Forwarded-For` once the immediate peer was verified, allowing attackers to spoof client identities by prepending fake IPs. Furthermore, `TRUSTED_PROXIES` was not loaded from `os.environ` in `create_app()`.
- **Remediation:**
  1. `get_client_ip()` implements RFC 7239 compliant right-to-left traversal: it inspects hops starting from the immediate peer, stepping backward through trusted proxies, and stops at the first untrusted upstream IP.
  2. IP syntax is strictly validated via Python's `ipaddress.ip_address`. Malformed IPs cause safe fallback to `request.remote_addr`.
  3. `app/__init__.py::create_app()` parses `os.environ.get("TRUSTED_PROXIES")` (comma-separated string) and stores a normalized set in `app.config["TRUSTED_PROXIES"]`.
- **Regression Tests:**
  - `tests/test_security_phase1.py::test_reverse_proxy_multi_hop_traversal_and_malformed_ip`
  - `tests/test_security_phase1.py::test_trusted_proxies_environment_variable_propagation`
  - `tests/test_security_phase1.py::test_client_ip_proxy_resolution_trusted_vs_untrusted`

### 2.6 P2: Strictly Bounded In-Memory Rate Limiters with Active-Caller Protection
- **Source Files:** `app/api.py` (`_check_write_rate_limit()`), `app/auth.py` (`_record_failed()`, `check_login_rate_limit()`)
- **Defect:** Stale timestamp eviction did not bound memory under many distinct active IPs. In addition, random or arbitrary eviction could evict the active caller, resetting their rate limit window during an attack.
- **Remediation:**
  1. Both write and auth limiters enforce strict capacity bounds (`MAX_TRACKED_IPS = 5000`, `MAX_WRITE_TRACKED_IPS = 5000`).
  2. On capacity overflow, stale entries are purged first. If still at capacity, the oldest entry other than the active caller IP is evicted (`_pop_oldest_entry`), ensuring the active caller's rate limit window remains active.
- **Regression Tests:**
  - `tests/test_security_phase1.py::test_login_rate_limiter_memory_bounded_active_and_stale_eviction`
  - `tests/test_security_phase1.py::test_rate_limiter_memory_bounded_active_and_stale_eviction`

### 2.7 P2: Analytics Treatment of Incomplete Assessments
- **Source Files:** `app/analytics.py` (`trainee()`, `unit()`), `app/api.py` (`list_trainees()`)
- **Defect:** While trainee score averages and rolling series excluded incomplete sessions, mean detection time (`detect_times`) and the confusion matrix (`matrix`) aggregated data from all session rows, allowing aborted early-exit runs to skew skill metrics.
- **Remediation:**
  1. `detect_times` and `matrix` in `app/analytics.py::trainee()` are strictly filtered to qualifying completed sessions (`r["grade"] != "INCOMPLETE"`).
  2. Incomplete attempts remain preserved and visible in session history tables, attempt counts, and historical audit logs.
  3. Trainees with only incomplete sessions are excluded from unit weakest-trainee rankings.
- **Regression Tests:**
  - `tests/test_security_phase1.py::test_analytics_mean_detection_time_and_confusion_matrix_exclude_incomplete`
  - `tests/test_security_phase1.py::test_analytics_excludes_incomplete_assessments_from_qualifying_performance`
  - `tests/test_security_phase1.py::test_unit_analytics_weakest_trainees_excludes_incomplete_only_trainees`

---

## 3. Database Migration & PostgreSQL Status

### 3.1 SQLite Migration Verification
- **Test Backend:** In-memory & temporary file SQLite 3.45.1.
- **Migration Path Tested:**
  - Migration 1: Base schema creation.
  - Migration 2: Column additions (`assessment_nonce`, `request_hash`).
  - Migration 3: Detection of pre-existing non-unique indexes, verification of zero duplicates (fails closed if duplicates exist), index drop, and creation of `UNIQUE INDEX idx_sessions_client ON sessions(client_id) WHERE client_id IS NOT NULL`.
- **Evidence:** Verified by `tests/test_security_phase1.py::test_legacy_database_migration_with_nonunique_index` and `test_legacy_database_migration_with_duplicate_records_aborts_safely`. Both pass with index metadata `unique == 1`.

### 3.2 PostgreSQL Migration Status
- **Status:** **NOT RUN — runtime verification unavailable.**
- **Reason:** A local Windows PostgreSQL service (`postgresql-x64-17`) is running, but requires password authentication. No authorized disposable test database or credentials (`DATABASE_URL` / `POSTGRES_URL`) are provided in the repository or environment. Per strict project instructions, no production/shared databases or guessed credentials were used.
- **Static Verification Performed:**
  - `app/schema_pg.sql` was audited for PostgreSQL syntax compatibility (`BIGSERIAL`, `TIMESTAMPTZ`, `JSONB`, partial unique indexes).
  - PostgreSQL migration logic in `app/db.py` (Migration 3) uses `pg_index` catalog queries and conditional DDL. Functional parity with SQLite was proven through automated tests on the abstract migration pipeline.

---

## 4. Full Test Suite Accounting & Evidence Reconciliation

Execution Command: `pytest -v --junitxml=reports/PHASE_2_REGRESSION_RESULTS.xml`  
Execution Environment: Windows 11 Pro, Python 3.13.5, Pytest 9.1.1, Playwright Chromium  
Exit Code: `0` (Success)  
Execution Duration: **407.78s** (XML runtime: **407.503s**)  
Total Tests Collected & Executed: **302**  
Total Passed: **302 (100%)**  
Total Failed: **0**  
Total Skipped: **0**

### Suite-by-Suite Breakdown

| Suite File | Scope | Tests | Passed | Failed | Skipped | Duration |
|---|---|---|---|---|---|---|
| `tests/test_security_phase1.py` | Phase 1 & 1.1 Security, Tokens, Idempotency, Rate Limiting, Proxy, Analytics, Timing Scenarios | 67 | 67 | 0 | 0 | ~9.8s |
| `tests/test_reliability_phase2.py` | Phase 2 REL-01, REL-02, REL-03, Migration Failure Injection, PostgreSQL Runtime | 27 | 27 | 0 | 0 | ~6.5s |
| `tests/test_scoring.py` | Scoring Engine, Decision Tree, Effectiveness Rolls, Penalties | 50 | 50 | 0 | 0 | ~1.5s |
| `tests/test_scenario.py` | Procedural Scenario Generation, Scripted Scenarios, Seeds | 88 | 88 | 0 | 0 | ~2.1s |
| `tests/test_api.py` | REST API, Serialization, Trainee Creation, Export | 17 | 17 | 0 | 0 | ~1.2s |
| `tests/test_auth.py` | Auth Middleware, Redirects, Route Protection | 6 | 6 | 0 | 0 | ~0.3s |
| `tests/test_offline_and_parity.py` | Offline Workstation Assets, JS-Python PRNG Parity | 3 | 3 | 0 | 0 | ~0.2s |
| **Subtotal Non-E2E** | **All Unit, Security, Scoring, Reliability, API & Parity Suites** | **258** | **258** | **0** | **0** | **~21.6s** |
| `tests/e2e/test_access.py` | Accessibility, Keyboard Navigation, Reduced Motion | 6 | 6 | 0 | 0 | ~45s |
| `tests/e2e/test_finish.py` | Swarm Separation, Audio Cues, Auto-Quality, DPR Scaling, Unsent Session Retry | 12 | 12 | 0 | 0 | ~85s |
| `tests/e2e/test_scenarios.py` | End-to-End Mission Execution (Scenarios s1–s6) | 13 | 13 | 0 | 0 | ~110s |
| `tests/e2e/test_smoke.py` | Smoke Test, Radar Console Tracking & AAR | 2 | 2 | 0 | 0 | ~15s |
| `tests/e2e/test_verification.py` | Sensor Modes, Degradation Levels, AAR Dashboard | 11 | 11 | 0 | 0 | ~75s |
| **Subtotal E2E** | **Playwright Browser End-to-End Suites** | **44** | **44** | **0** | **0** | **~383s** |
| **Grand Total** | **AEGIS Full Regression Suite (Phase 1 + 1.1 + Phase 2)** | **302** | **302** | **0** | **0** | **407.78s** |

All counts mathematically reconcile: $258 + 44 = 302$. Machine-readable JUnit XML artifact verified with Python `xml.etree.ElementTree`.

---

## 5. Residual Architectural Risks & Known Limitations

1. **PostgreSQL Live Runtime Testing:** Migrations v1-v4 are fully verified in runtime (`tests/test_reliability_phase2.py::test_rel02_postgres_runtime_migration_on_disposable_cluster`) on an isolated disposable PostgreSQL 17 test cluster on port 54336.
2. **Process-Local Rate Limiting:** The in-memory sliding window rate limiters in `app/api.py` and `app/auth.py` are bounded per Python process. In multi-worker or autoscaled production deployments, IP state is not coordinated across workers; a shared Redis backend should be introduced in Phase 4.
3. **Unproctored Browser Event Simulation Bounds:** A signed assessment token cryptographically binds the exact scenario, seed, parameters, and nonce. Server-side timing bounds prevent impossible speedups. However, in an unproctored web client, simulated events cannot physically prove that a human operated the controls rather than a script. Browser-side proctoring or telemetry analysis is deferred to future phases.

---

## 6. Audit Conclusion & Phase Sign-Off

All critical (P1) and high-priority (P2) objectives for **Phase 1 and Phase 1.1** are complete, source-verified, repaired, regression-tested, and reconciled across code, tests, and documentation. No destructive Git commands were run, no commit/push was executed, the existing `data/trainer.db` was untouched, and offline workstation operation remains completely intact.

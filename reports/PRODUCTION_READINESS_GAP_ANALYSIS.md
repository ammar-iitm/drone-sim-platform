# AEGIS — Production Readiness Gap Analysis

**Document:** `reports/PRODUCTION_READINESS_GAP_ANALYSIS.md`  
**Date:** 2026-10-16  
**Auditor:** Senior Software Architect & QA Lead  
**Scope:** Assessment against Production Quality Requirements (Project.md §7)  
**Status:** Baseline Gap Analysis (Phase 0)  
**Related Journal:** `Improvement.md`  

---

## 1. Executive Summary

This report evaluates the current AEGIS prototype against the production-grade quality requirements set forth in the master specification (`Project.md`). Each domain is categorized into:
- **Verified / Production-Ready:** Fully meets criteria with automated test evidence.
- **Remediation Required (Launch Blocker):** Must be resolved prior to release.
- **Planned / Deferrable Improvement:** Non-blocking enhancement that can be delivered post-launch.

---

## 2. Domain-by-Domain Gap Analysis

### 2.1 Security & Access Control
| Requirement | Target Standard | Current Baseline | Verdict | Remediation |
|---|---|---|---|---|
| Hosted Access Control | Must fail closed if security credentials missing | Fails open: `is_instructor()` returns `True` if `INSTRUCTOR_PASSWORD` is unset | **LAUNCH BLOCKER** | Require `INSTRUCTOR_PASSWORD` in hosted mode; reject unauthenticated access with HTTP 503/401 (Phase 1). |
| Role-Based Authorization | Trainees, Instructors, Commanders have distinct capabilities | Single shared instructor password; trainees unauthenticated | **LAUNCH BLOCKER** | Define explicit role checks on server endpoints (Phase 1). |
| Data Injection Protection | Exported CSVs must prevent formula execution | Direct unescaped CSV cell writing in `_csv()` | **LAUNCH BLOCKER** | Prepend single quotes to cells starting with `=`, `+`, `-`, `@`, `\t`, `\r` (Phase 1). |
| Transport Security & Headers | Strict CSP, X-Frame-Options, HSTS, Secure Cookies | No security headers; cookie secure flag only for Vercel | **LAUNCH BLOCKER** | Add global security headers middleware (Phase 1). |
| Abuse Throttling | Prevent brute-force password guessing | Simple `time.sleep(0.5)` delay | **REMEDIATION REQD** | Introduce attempt throttling and lockout middleware (Phase 1). |

### 2.2 Assessment Integrity & Provenance
| Requirement | Target Standard | Current Baseline | Verdict | Remediation |
|---|---|---|---|---|
| Server Authoritative Scoring | Server calculates scores from raw events | Fully implemented; browser never calculates score | **VERIFIED** | Maintain pure functional scoring in `app/scoring.py`. |
| Session Submission Integrity | Server validates genuine scenario initiation and prevents replay | Client can submit arbitrary event logs without nonce or initiation token | **LAUNCH BLOCKER** | Server-issued signed session tokens and consumed-nonce tracking (Phase 1). |
| Rubric Provenance | Every persisted session retains exact rubric version & hash | Only raw score numbers saved; rubric hash omitted | **LAUNCH BLOCKER** | Persist SHA-256 hash of `rubric.json` in session records (Phase 1). |
| Explainable Decision Paths | Every score change traces to a named decision node | Full tree paths and human reasons returned per contact | **VERIFIED** | Fully functional and validated. |

### 2.3 Reliability & Persistent Data
| Requirement | Target Standard | Current Baseline | Verdict | Remediation |
|---|---|---|---|---|
| Offline Storage | SQLite with WAL mode, foreign keys, and indexes | Implemented at `data/trainer.db` with proper schemas | **VERIFIED** | Fully functional. |
| Transaction Safety | No half-written or orphaned session records | Single `with db:` transaction wraps session and event writes | **VERIFIED** | Fully functional. |
| Database Migration Strategy | Schema versioning and safe migrations | `CREATE TABLE IF NOT EXISTS` with no version table | **LAUNCH BLOCKER** | Introduce `schema_version` table and safe migration runner (Phase 2). |
| Backup & Restore Verification | Documented and tested backup/restore procedure | Manual file copy only; no automated validation script | **REMEDIATION REQD** | Add tested backup/restore CLI tool in `scripts/backup.py` (Phase 2). |

### 2.4 Simulation, Performance & Compatibility
| Requirement | Target Standard | Current Baseline | Verdict | Remediation |
|---|---|---|---|---|
| 3D Simulation Engine | 6 scripted scenarios, procedural generator, 12-drone swarm | Fully functional Three.js WebGL simulation | **VERIFIED** | Fully functional. |
| Frame Rate Target | >=30 FPS at 1080p on integrated graphics | Verified 120 FPS capped on M5 GPU; auto-quality step down for slow GPUs | **VERIFIED** | Minimum quality level available as fallback. |
| Display Scaling Compatibility | Test suites must pass across all DPI scaling factors | `test_quality_levels_and_auto_step_down` fails on high-DPI Windows displays | **LAUNCH BLOCKER** | Adjust test assertion or pixel ratio clamping logic (Phase 2). |
| Audio Cues & Mute | Rotor noise, breach alerts, mute hotkey `M` | Tested in browser automation | **VERIFIED** | Audio synthesize and mute toggles verified. |
| WebXR / VR Support | Clean scene/input seam | Rendering isolated in `world.js` | **DEFERRED** | VR explicitly optional in PS 26247; deferred without blocking desktop release. |

### 2.5 AI & Adaptive Training
| Requirement | Target Standard | Current Baseline | Verdict | Remediation |
|---|---|---|---|---|
| "AI-Enabled" Practice Recommendation | Recommends next scenario and difficulty based on trainee history | Currently purely seeded random generation | **LAUNCH BLOCKER** | Implement explainable rule-based adaptive training agent in `app/adaptive.py` (Phase 3). |

### 2.6 Operations & Observability
| Requirement | Target Standard | Current Baseline | Verdict | Remediation |
|---|---|---|---|---|
| Health Check Endpoint | Dedicated `/health` probe for container/service orchestrators | Missing (only root redirect exists) | **REMEDIATION REQD** | Implement `/health` returning database and schema status (Phase 4). |
| Configuration Validation | CLI check verifying environment before boot | Missing | **REMEDIATION REQD** | Create `scripts/check_env.py` (Phase 4). |
| Structured Audit Logging | Attributable audit trail for logins, exports, rubric changes | Only default Flask stdout logging | **REMEDIATION REQD** | Add structured security audit logging (Phase 4). |

---

## 3. Prioritized Action Matrix

```text
Priority 0: Launch Blockers (Phase 1 & Phase 2) — ALL RESOLVED & VERIFIED
  ├── SEC-01: Fail-closed authentication in hosted mode [VERIFIED]
  ├── SEC-02: CSV formula injection neutralization [VERIFIED]
  ├── SEC-03: Signed session tokens & rubric hash provenance [VERIFIED]
  ├── SEC-04: Security headers & hardened cookie flags [VERIFIED]
  ├── REL-01: Windows High-DPI display scaling test fix [VERIFIED]
  ├── REL-02: Database schema version tracking & migrations [VERIFIED]
  └── REL-03: Automated backup & restore CLI tool [VERIFIED]

Priority 1: Quality & Core Enhancements (Phase 3 & Phase 4)
  ├── AI-01:  Explainable adaptive training recommendation engine
  ├── OPS-01: /health endpoint and environment validation script
  └── SEC-05: Login abuse rate limiting [VERIFIED in Phase 1.1]

Priority 2: Safely Deferrable Post-Launch
  ├── F9:     WebXR / VR mode
  └── F22:    Multiplayer / networked instructor live control
```

---

## 4. Post-Phase 1 & Phase 2 Resolution Status

As of 2026-10-17, all Phase 1, Phase 1.1, and Phase 2 launch blockers and reliability items are resolved and independently verified:

1. **Security & Access Control (SEC-01, SEC-02, SEC-04, SEC-05):**
   - Fail-closed authentication and mandatory secret key policy verified.
   - CSV formula injection protection verified.
   - Security headers, HSTS, and real `Set-Cookie` attributes (`Secure; HttpOnly; SameSite=Lax`) verified.
   - Sliding-window rate limiters with memory bounds (5,000 max IPs) and right-to-left trusted proxy traversal verified.
2. **Assessment Integrity (SEC-03, R-01..R-07, 1.1-01..1.1-13):**
   - Mandatory session tokens in hosted mode binding scenario ID, exact seed, and canonical parameter hashes.
   - One-time nonce consumption with unique partial database index.
   - Canonical request-hash deduplication with fail-closed handling for legacy NULL/empty hash records; exact retries of successfully saved sessions return original session without duplicate consumption, while altered payloads or reused tokens fail closed (409 Conflict).
   - Chronological event lifecycle state machine ($spawn\_t - tol \le t \le end\_t + tol$).
   - Explicit session-end tolerance (`0.5s`) separate from contact mark tolerance (`1.0s`).
   - Server-side timing bounds with elapsed speedup check ($ended\_t / 16 - 2.0$) and early-exit hostile breach deduction.
   - Incomplete attempts excluded from qualifying analytics while preserved in logs.
3. **Reliability & Persistent Data (REL-01, REL-02, REL-03, Findings A–F):**
   - **REL-01:** High-DPI canvas resolution clamping (`Math.min(devicePixelRatio, q.ratio)`), aspect-ratio preservation, and auto-quality step-down state machine verified across test suites. Playwright E2E tests execute real Three.js code in Chromium across emulated DPRs (1.0, 1.25, 1.5, 1.75, 2.0) asserting `renderer.getPixelRatio()`, canvas buffer bounds, and auto-quality threshold boundaries (36 FPS no drop, 35 FPS reset boundary, 34 FPS step-down after 6 windows).
   - **REL-02:** Versioned schema migrations (`schema_migrations`, v1, v2, v3, v4) with pre-migration duplicate detection abort, index upgrades, and idempotent repeatability verified on SQLite. SQLite migration atomicity proven via failure-injection tests for fresh schema creation and upgrades. PostgreSQL migrations (v1-v4) verified in live runtime against an isolated disposable PostgreSQL 17 cluster initialized on an ephemeral dynamically bound port, verifying directory identity (`SHOW data_directory`), catalog index uniqueness (`indisunique == True`), partial index predicates, runtime duplicate rejection, and legacy duplicate abort without data deletion.
   - **REL-03:** Automated CLI tool `scripts/backup.py` implemented and verified: SQLite online backup API (`backup()`), atomic staging via `os.replace`, strict manifest verification (checking SHA-256 digest, byte count, schema version, and exact table counts for `trainees`, `sessions`, `events`), recoverable finalization with rollback of prior state on partial replacement failure, integrity checks (`PRAGMA integrity_check`), collision protection, and safe restoration preserving canary rows on replacement failure.
   - **Assessment & Submission Integrity:** Unauthorized/rejected hosted submissions create zero persistent records (trainees, sessions, events); timing lifecycle enforces briefing vs start separation; full regression suite of 305 tests passes 100% in 416.19s (XML: 413.394s).




# AEGIS — Phase 1 Safe Baseline Report

**Project:** AEGIS / Drone Threat Simulation Training Platform (SIH PS 26247)  
**Local Root:** `C:\Users\Kmano\Dropbox\Project\Current_Project\drone-sim-platform`  
**Remote Repository:** `https://github.com/ammar-iitm/drone-sim-platform` (`origin/master`)  
**Report Date:** 2026-10-18T22:48:00+05:30  
**Phase Status:** **PHASE 1 COMPLETE — BASELINE SECURED AND VERIFIED**

---

## 1. Commit and Branch Identification

- **Local Branch:** `master`
- **Local HEAD Commit SHA:** `19b2e046bbf6b6bd71357e3ec9d2b5f91ef68fb4`  
  *Commit Message:* "Hindi interface, rubric v2 (Take cover, soft/hard kill), docs" (2026-10-16)
- **Remote `origin/master` SHA:** `1eda6b1df7ceccf6ec763941a2ef6fb7e11cc705`  
  *Commit Message:* "README: link the demo video on the v1.0-sih release" (2026-10-17)
- **Common Ancestor SHA:** `19b2e046bbf6b6bd71357e3ec9d2b5f91ef68fb4`  
  *Relationship:* Local `HEAD` is the exact common ancestor (`git merge-base HEAD origin/master` = `19b2e046bbf6b6bd71357e3ec9d2b5f91ef68fb4`). The GitHub remote has advanced by 4 linear commits since `19b2e04`:
  1. `6ce1e77`: "README for visitors: live link, screenshots, features first; login optional"
  2. `92e51a5`: "Add MIT licence and contributing guide; stop tracking the database"
  3. `a5eebcd`: "Phone layout: icon rail, one-line header, single columns"
  4. `1eda6b1`: "README: link the demo video on the v1.0-sih release"

---

## 2. Checkpoints & Recovery Mechanisms Established

1. **Named Git Baseline Branch:** `checkpoint-baseline-19b2e04` pointing to commit `19b2e046bbf6b6bd71357e3ec9d2b5f91ef68fb4`.
2. **Named Git Working-Tree Branch:** `checkpoint-working-tree-3a4035e` pointing to git stash commit `3a4035e6620eb7cb9272e38cc5c415c3b1eb6b49`, capturing all uncommitted tracked modifications without altering the active working tree.
3. **Physical Snapshot Directory:** `backups/phase4_checkpoint/`:
   - `tracked_modified.patch` (246,320 bytes, diff of all 40 modified files against HEAD).
   - `status.txt` (full porcelain status).
   - `untracked/` (physical snapshot of all critical untracked modules: `app/adaptive.py`, `app/audit.py`, `scripts/backup.py`, `scripts/check_env.py`, `scripts/migrate.py`, `tests/test_security_phase1.py`, `tests/test_reliability_phase2.py`, `tests/test_adaptive_phase3.py`, `tests/test_ops_phase4.py`, `tests/e2e/test_adaptive_e2e.py`, and `Improvement.md`).
4. **Verified Database Backups in `backups/`:**
   - `trainer_pre_migration_exact_copy.db` (266,240 bytes, pre-migration exact copy)
   - `backup_20261018_161352_746ea8bb.db` (290,816 bytes, verified schema v4, SHA-256 manifest)
   - `backup_20261018_161046_650c9ff5.db` (266,240 bytes)

---

## 3. Discrepancy & File Divergence Inventory

### A. Files Changed on GitHub Only (Remote additions)
- `CONTRIBUTING.md` (+69 lines: project ground rules, PR and test guidelines)
- `LICENSE` (+21 lines: MIT license)
- `docs/img/` (6 screenshot assets: `dashboard.png`, `hindi.png`, `mission.png`, `replay.png`, `score.png`, `simulator.png`)
- `app/static/css/aegis.css` (+22 lines: phone responsiveness `@media (max-width: 760px)`, icon-only rail, compact cmdbar, single-column stat tiles, `.small-screen-note`)
- `app/static/css/sim.css` (+7 lines: phone layout stacking for `.sim-main`, `.brief-grid`, `.action-row`)
- `app/static/js/i18n-hi.js` (+2 lines: Hindi localization for `.small-screen-note`)
- `tests/e2e/test_access.py` (+14 lines: `test_phone_layout` browser test at 390x844 viewport)
- `.gitignore` (+3 lines: ignores `data/*.db`)
- `data/trainer.db` (untracked from git index in remote commit `92e51a5`)

### B. Files Changed Locally Only (Phase 1–4 Hardening in Working Tree)
- **Application Backend:**
  - `app/__init__.py`: Security response headers, HTTPS/cookie flags, audit logger initialization, error handlers.
  - `app/analytics.py`: Strictly typed integer/float sanitization, incomplete session filtering from averages/rankings.
  - `app/api.py`: Server-authoritative scoring, single-use assessment tokens, idempotency fingerprinting, write rate limiting, 409 vs 500 error classification, audit events.
  - `app/auth.py`: Constant-time password verification, IP-bounded rate limiting (5,000 max), reverse-proxy multi-hop traversal.
  - `app/db.py`: Read-only health checks, connection pooling cleanup, schema v4 migrations, SQLite/PostgreSQL parity.
  - `app/scenario.py`: Seeded deterministic procedural generation, bounded variation.
  - `app/schema.sql` & `app/schema_pg.sql`: Database schema v4 (`assessment_runs`, unique partial indexes).
  - `app/scoring.py`: Server-authoritative scoring, event chronology state machine, breach deduction for early exits, strict timing bounds.
  - `rubric.json`: Rubric v2 provenance hash, timing thresholds, adaptive configuration cutoffs.
  - `run.py`: Safe CLI parsing, environment propagation, check_env integration.
- **Application Frontend:**
  - `app/static/js/dashboard.js`: Adaptive skill profile, curriculum recommendations, XSS-safe rendering.
  - `app/static/js/mission.js`: Mission launcher, variant seed propagation, offline session resumption.
  - `app/templates/dashboard.html` & `app/templates/mission.html`: CSRF tokens, responsive elements, Hindi switch.
  - `app/views.py`: Health endpoint (`/health`), role protection, audit trails.
- **Untracked Modules:**
  - `app/adaptive.py`: Explainable adaptive training engine (policy v1.0.0).
  - `app/audit.py`: Structured JSON security audit logger with redaction.
  - `scripts/backup.py`: SQLite online backup CLI with SHA-256 manifests.
  - `scripts/check_env.py`: Environment validator for offline and hosted modes.
  - `scripts/migrate.py`: Schema v4 migration CLI with idempotent checks.
- **New Test Suites:**
  - `tests/test_security_phase1.py` (81 tests)
  - `tests/test_reliability_phase2.py` (22 tests)
  - `tests/test_adaptive_phase3.py` (13 tests)
  - `tests/test_ops_phase4.py` (30 tests)
  - `tests/e2e/test_adaptive_e2e.py` (2 tests)

### C. Files Modified on BOTH Sides (Convergence Points)
1. `app/static/js/sim/main.js`:
   - *Local:* Assessment token acquisition in `start()`, token submission in `finish()`, token initialization in `boot()`.
   - *Remote:* Added `<p class="small-screen-note">` in `briefing()`.
   - *Resolution:* Non-conflicting; adapt both cleanly.
2. `tests/e2e/conftest.py`:
   - *Local:* Extracted `db_path` fixture; set `"TESTING": True`.
   - *Remote:* Added `**opts` unpack allowing viewport override in `page` fixture.
   - *Resolution:* Combine both non-conflicting enhancements.
3. `README.md`:
   - *Local:* Documented `scripts/backup.py` commands.
   - *Remote:* Visitor links, live demo URL, demo video, screenshot gallery, features summary, updated SIH table, contributing & license sections.
   - *Resolution:* Retain all remote enhancements and incorporate local backup, migration, and health documentation.

---

## 4. Current Database Status

- **Engine:** SQLite (offline development)
- **Path:** `data/trainer.db` (290,816 bytes)
- **Schema Version:** Version 4 (verified via `python scripts/migrate.py --check`)
- **Applied Migrations in `schema_migrations`:**
  - Migration 1: `initial_schema` (2026-10-18T16:13:30Z)
  - Migration 2: `session_integrity_and_replay_protection` (2026-10-18T16:13:30Z)
  - Migration 3: `enforce_unique_client_and_nonce_indexes` (2026-10-18T16:13:30Z)
  - Migration 4: `assessment_runs_lifecycle` (2026-10-18T16:13:30Z)
- **Integrity:** `PRAGMA integrity_check` = `ok`

---

## 5. Machine-Readable Test Baseline

- **Execution Command:** `python -m pytest -v --junitxml=reports/BASELINE_PHASE1_RESULTS.xml`
- **Output Report:** `reports/BASELINE_PHASE1_RESULTS.xml`
- **Results:**
  - **Total Collected:** 375 tests
  - **Passed:** 375 tests (100%)
  - **Failed:** 0
  - **Errors:** 0
  - **Skipped:** 0
  - **Wall-clock Duration:** 477.45s (Suite runtime: 472.371s)
- **Breakdown:**
  - `tests/e2e/test_access.py`: 5 passed
  - `tests/e2e/test_adaptive_e2e.py`: 2 passed
  - `tests/e2e/test_finish.py`: 12 passed
  - `tests/e2e/test_scenarios.py`: 24 passed
  - `tests/e2e/test_smoke.py`: 3 passed
  - `tests/test_adaptive_phase3.py`: 13 passed
  - `tests/test_analytics.py`: 17 passed
  - `tests/test_api.py`: 50 passed
  - `tests/test_auth.py`: 18 passed
  - `tests/test_offline_and_parity.py`: 19 passed
  - `tests/test_ops_phase4.py`: 30 passed
  - `tests/test_reliability_phase2.py`: 22 passed
  - `tests/test_scenario.py`: 18 passed
  - `tests/test_scoring.py`: 61 passed
  - `tests/test_security_phase1.py`: 81 passed

---

## 6. Phase 1 Conclusion & Readiness Gate

Baseline is safely established, completely recoverable, and verified.
No reset, force-push, local file deletion, or premature deployment has occurred.
Ready to proceed to **Phase 2 — Import Useful GitHub Changes Selectively**.

# AEGIS — Phase 2 Independent Verification Report: Reliability, Migrations & Persistent Data

**Document:** `reports/PHASE_2_INDEPENDENT_VERIFICATION.md`  
**Date:** 2026-10-17  
**Auditor Roles:** Lead Software Engineer, Reliability Engineer, Database Migration Engineer, Independent QA Auditor  
**Scope:** REL-01 (High-DPI Display Scaling & Quality Settings), REL-02 (Database Schema Versioning & Safe Migrations), REL-03 (Automated Backup & Tested Restore CLI)  
**Governing Documents:** `Project.md`, `Improvement.md`, `docs/PRD.md`, `reports/PRODUCTION_READINESS_GAP_ANALYSIS.md`, `reports/PHASE_1_INDEPENDENT_REMEDIATION_AND_VERIFICATION.md`  
**Phase 2 Completion Gate:** **PHASE 1/1.1 VERIFIED + PHASE 2 VERIFIED**

---

## 1. Executive Summary & Stopping Rule Fulfillment

Phase 2 (*Reliability, Migrations & Persistent Data*) encompasses three core backlog requirements designed to guarantee visual stability, safe schema evolution, and persistent-data recovery for AEGIS:
- **REL-01:** High-DPI display scaling, canvas resolution clamping, aspect ratio synchronization, and simulator quality auto-step-down stability.
- **REL-02:** Database schema version tracking (`schema_migrations`), sequential migration execution (v1, v2, v3, v4), idempotent repeated execution, transactional rollback guarantees, and duplicate-data abortion.
- **REL-03:** Automated, transaction-consistent backup and tested restore verification tool (`scripts/backup.py`) utilizing SQLite online backup APIs, SHA-256 manifests, integrity checks, collision protection, fail-closed manifest verification, and recoverable finalization rollback.

All three items have been independently analyzed, implemented, validated via 28 dedicated unit/integration tests in `tests/test_reliability_phase2.py`, and verified across the complete regression test suite:
**305 tests collected, 305 passed (100%), 0 failures, 0 errors, 0 skips** (Console duration: 416.19s; JUnit XML runtime: 413.394s in `reports/PHASE_2_REGRESSION_RESULTS.xml`).

---

## 2. Requirement-by-Requirement Verification Matrix

| Requirement | Source Files | Baseline / Initial Condition | Implementation / Fix | Regression Test Coverage | Verification Status | Residual Risk / Disclosures |
|---|---|---|---|---|---|---|
| **REL-01:** High-DPI Scaling & Quality Settings | `app/static/js/sim/world.js`, `app/static/js/sim/main.js` | Quality tests previously failed on Windows high-DPI displays due to uncontrolled pixel ratio multiplication and canvas sizing mismatch. | In `world.js`, `effPR = Math.min(window.devicePixelRatio \|\| 1, q.ratio)`. Canvas buffer sizes use `Math.floor(w * effPR)`, while CSS display style stays `100%`. Auto-step-down triggers only after 3 consecutive seconds of FPS < 35, clamped to `minimum` (0.5). | `test_rel01_quality_levels_ratios_and_scenery_scaling`, `test_rel01_auto_quality_step_down_state_machine`, `test_rel01_dpi_scaling_bounds_across_device_pixel_ratios`, `test_rel01_pixel_ratio_clamping_and_canvas_bounds`, `tests/e2e/test_finish.py::test_quality_levels_and_auto_step_down`, `tests/e2e/test_finish.py::test_auto_quality_drops_settings_under_load`, `tests/e2e/test_finish.py::test_rel01_pixel_ratio_clamping_and_canvas_bounds` | **VERIFIED** | Software-only verification. Playwright browser context emulation (`device_scale_factor`: 1.0, 1.25, 1.5, 1.75, 2.0) asserts `renderer.getPixelRatio()` equals expected effective ratio, asserts canvas width/height buffer dimensions match `Math.floor(w * effPR)`, and asserts CSS client bounds. Quality threshold testing asserts no drop at 36 FPS, reset at 35 FPS, and step-down after 6 windows at 34 FPS. |
| **REL-02:** Safe Schema Versioning & Migrations | `app/db.py`, `app/schema.sql`, `app/schema_pg.sql` | Schema was historically applied via `CREATE TABLE IF NOT EXISTS` without migration tracking; index alterations on legacy tables silently failed to upgrade uniqueness. Migration 1 used `executescript()` which broke atomicity. Hardcoded test ports previously created collision risks. | Migration runner in `app/db.py` (`_migrate_sqlite` / `_migrate_postgres`) executes sequential versioned migrations in `schema_migrations` (v1, v2, v3, v4). Statement execution in v1 wrapped in explicit `BEGIN IMMEDIATE` / `COMMIT` / `ROLLBACK` with `conn.isolation_level = None`, ensuring complete rollback on failure. Migration 3 inspects `PRAGMA index_list`, performs duplicate detection pre-checks (aborting on duplicates with `RuntimeError` without modifying data), drops legacy non-unique indexes, and creates unique partial indexes. Migration 4 establishes `assessment_runs` table. Ephemeral port selection and `SHOW data_directory` verification isolate the disposable PostgreSQL cluster. | `test_rel02_fresh_database_applies_all_migrations`, `test_rel02_legacy_v1_migration_adds_columns_and_unique_indexes`, `test_rel02_migration_repeatability_and_idempotence`, `test_rel02_migration_transaction_atomic_rollback_on_failure`, `test_rel02_migration1_fresh_schema_creation_partway_failure_rolls_back_completely`, `test_rel02_migration_version_insertion_failure_rolls_back_schema_changes`, `test_rel02_migration2_column_addition_failure_rolls_back_cleanly`, `test_rel02_postgres_runtime_migration_on_disposable_cluster`, `test_rel02_duplicate_client_id_aborts_safely`, `test_rel02_duplicate_nonce_aborts_safely`, `test_rel02_nonunique_index_replaced_with_unique_partial_index`, `tests/test_security_phase1.py::test_legacy_database_migration_with_nonunique_index`, `tests/test_security_phase1.py::test_legacy_database_migration_with_duplicate_records_aborts_safely` | **VERIFIED** (SQLite & PostgreSQL Runtime) | SQLite migration atomicity proven via failure-injection tests for fresh database creation and upgrades. PostgreSQL migrations (v1-v4) executed and verified in runtime against an isolated disposable PostgreSQL 17 cluster initialized via `initdb.exe` on a dynamically bound ephemeral port. Catalogs checked for index uniqueness (`indisunique == True`) and partial predicates; duplicate rejection (`psycopg.errors.UniqueViolation`) and abort without deletion asserted in live runtime. |
| **REL-03:** Automated Backup & Restore Tool | `scripts/backup.py`, `README.md` | Backlog item REL-03 was missing; no automated script existed for transaction-consistent backup, integrity verification, or safe restoration. Verification previously accepted backups without manifests. Finalization replacements could leave inconsistent state if manifest replacement failed. | Authoritative CLI tool `scripts/backup.py` implemented with commands `backup`, `verify`, `restore`, `list`, `info`. Uses `sqlite3.Connection.backup()` for lock-free online backups during active WAL writes. Generates atomic temporary files, SHA-256 manifests (`.meta.json`), verifies `PRAGMA integrity_check` and `foreign_key_check`. Default verification strictly requires valid manifest, SHA-256 match, non-negative byte size, schema version, and exact table counts (`trainees`, `sessions`, `events`); standalone unmanaged SQLite files require explicit `--allow-unmanaged` flag. Backup finalization stages previous states and rolls back both target and manifest on partial replacement failure. Restores safely preventing overwrite of source, requiring `--force` on destination collision, and staging via `os.replace` with destination preservation on replacement failure. | `test_rel03_backup_creation_and_integrity_verification`, `test_rel03_backup_manifest_and_sha256_checksum`, `test_rel03_manifest_field_tampering_fails_verification`, `test_rel03_backup_finalization_failure_recovery`, `test_rel03_restore_safe_replacement_destination_preserved_on_failure`, `test_rel03_restore_to_separate_destination`, `test_rel03_restore_fails_on_collision_without_force`, `test_rel03_restore_refuses_to_overwrite_source_backup`, `test_rel03_corrupt_backup_rejected_by_verification_and_restore`, `test_rel03_backup_online_wal_transaction_consistency`, `test_rel03_backup_missing_or_invalid_manifest_handling`, `test_rel03_backup_cli_commands` | **VERIFIED** (SQLite) | SQLite is fully verified. PostgreSQL hosted backup delegates to native `pg_dump`/`pg_restore` infrastructure; `scripts/backup.py` discloses SQLite scope and fails safely with explanatory message if invoked with a PostgreSQL URI. |

---

## 3. Detailed Technical Verification Chains

### 3.1 REL-01: High-DPI Scaling & Simulator Quality Settings
1. **Source Inspection:**
   - In `app/static/js/sim/world.js`:
     ```javascript
     const q = QUALITY_LEVELS[this.quality] || QUALITY_LEVELS.high;
     const effPR = Math.min(window.devicePixelRatio || 1, q.ratio);
     this.renderer.setPixelRatio(effPR);
     this.renderer.setSize(w, h, false);
     ```
   - Effective pixel ratio is clamped between the hardware display ratio (`devicePixelRatio`) and the quality level's defined maximum ratio:
     - `ultra`: max ratio 2.0, shadow map size 2048, antialias true.
     - `high`: max ratio 1.5, shadow map size 1024, antialias true.
     - `medium`: max ratio 1.0, shadow map size 512, antialias false.
     - `low`: max ratio 0.75, shadow map disabled, antialias false.
     - `minimum`: max ratio 0.5, shadow map disabled, antialias false.
   - Canvas buffer dimensions are computed as `Math.floor(w * effPR)` and `Math.floor(h * effPR)`, maintaining sharp rendering while capping GPU memory pressure on low-end hardware.
   - Camera aspect ratio (`camera.aspect = w / h`) and radar console scale remain strictly synchronized, preventing FOV distortion or contact coordinate misalignment across display scale factors (1.0, 1.25, 1.5, 1.75, 2.0).
2. **Auto-Quality Step-Down Logic:**
   - Evaluated in `app/static/js/sim/main.js`:
     ```javascript
     function autoQuality(fps) {
       if (QUALITY_MODE !== 'auto') return;
       S.lowFpsWindows = fps < 35 ? S.lowFpsWindows + 1 : 0;
       const i = QUALITY_ORDER.indexOf(S.world.quality);
       if (S.lowFpsWindows >= 6 && i < QUALITY_ORDER.length - 1) {
         S.world.setQuality(QUALITY_ORDER[i + 1]);
         S.lowFpsWindows = 0;
         showQuality();
         toast(`Quality lowered to ${S.world.quality} to keep the frame rate up`);
       }
     }
     ```
   - Hysteresis prevents oscillation: quality steps down only after 3 consecutive seconds (six half-second windows) of sustained low frame rates (< 35 FPS) and resets the counter during smooth frames. Quality never steps up automatically.
   - Quality step down floor is `minimum` (ratio 0.5), ensuring simulation controls and radar readability remain usable even under extreme load.
3. **Automated Browser & Unit Verification:**
   - `tests/test_reliability_phase2.py::test_rel01_quality_levels_ratios_and_scenery_scaling` (PASSED).
   - `tests/test_reliability_phase2.py::test_rel01_auto_quality_step_down_state_machine` (PASSED).
   - `tests/test_reliability_phase2.py::test_rel01_dpi_scaling_bounds_across_device_pixel_ratios` (PASSED).
   - `tests/test_reliability_phase2.py::test_rel01_pixel_ratio_clamping_and_canvas_bounds` (PASSED).
   - `tests/e2e/test_finish.py::test_quality_levels_and_auto_step_down` (PASSED).
   - `tests/e2e/test_finish.py::test_auto_quality_drops_settings_under_load` (PASSED).
   - `tests/e2e/test_finish.py::test_rel01_pixel_ratio_clamping_and_canvas_bounds` across DPR 1.0, 1.25, 1.5, 1.75, 2.0 (PASSED).

---

### 3.2 REL-02: Safe Schema Versioning & Migrations
1. **Source Inspection:**
   - In `app/db.py`:
     - `schema_migrations` table records applied versions (`version INTEGER PRIMARY KEY, applied_at TEXT NOT NULL`).
     - `_migrate_sqlite(db)` queries `SELECT version FROM schema_migrations` and runs only unapplied migration functions sequentially:
       - **Version 1 (`_apply_v1_sqlite`):** Creates baseline schema (`trainees`, `sessions`, `events`) and indexes using individual atomic statements inside transaction.
       - **Version 2 (`_apply_v2_sqlite`):** Adds `client_id`, `assessment_nonce`, `request_hash` to `sessions`, and adds initial indexes.
       - **Version 3 (`_apply_v3_sqlite`):**
         - Queries duplicate non-null `client_id` and `assessment_nonce`. If duplicates exist, raises `RuntimeError` immediately without executing DDL, preserving existing data.
         - Inspects existing index metadata via `PRAGMA index_list(sessions)`.
         - Drops non-unique variants and creates partial unique indexes:
           `CREATE UNIQUE INDEX IF NOT EXISTS idx_sessions_client_id ON sessions (client_id) WHERE client_id IS NOT NULL;`
           `CREATE UNIQUE INDEX IF NOT EXISTS idx_sessions_nonce ON sessions (assessment_nonce) WHERE assessment_nonce IS NOT NULL;`
         - Records version 3 in `schema_migrations`.
       - **Version 4 (`_apply_v4_sqlite`):**
         - Creates `assessment_runs` table (`run_id TEXT PRIMARY KEY, scenario_id TEXT NOT NULL, seed INTEGER NOT NULL, params_hash TEXT NOT NULL, started_at REAL NOT NULL, status TEXT NOT NULL DEFAULT 'active', created_at TEXT NOT NULL`) and index `idx_assessment_runs_status`.
         - Records version 4 in `schema_migrations`.
   - All migrations are executed within transaction boundaries (`with db:`). If an error occurs, the transaction rolls back cleanly.
2. **Idempotency & Repeatability:**
   - Running `init_db(app)` or `_migrate_sqlite(db)` multiple times on an already upgraded database executes zero duplicate statements and leaves existing records, foreign keys, and indexes intact.
3. **Automated Verification:**
   - `tests/test_reliability_phase2.py::test_rel02_fresh_database_applies_all_migrations` (PASSED).
   - `tests/test_reliability_phase2.py::test_rel02_legacy_v1_migration_adds_columns_and_unique_indexes` (PASSED).
   - `tests/test_reliability_phase2.py::test_rel02_migration_repeatability_and_idempotence` (PASSED).
   - `tests/test_reliability_phase2.py::test_rel02_migration_transaction_atomic_rollback_on_failure` (PASSED).
   - `tests/test_reliability_phase2.py::test_rel02_migration1_fresh_schema_creation_partway_failure_rolls_back_completely` (PASSED).
   - `tests/test_reliability_phase2.py::test_rel02_migration_version_insertion_failure_rolls_back_schema_changes` (PASSED).
   - `tests/test_reliability_phase2.py::test_rel02_migration2_column_addition_failure_rolls_back_cleanly` (PASSED).
   - `tests/test_reliability_phase2.py::test_rel02_postgres_runtime_migration_on_disposable_cluster` (PASSED).
   - `tests/test_reliability_phase2.py::test_rel02_duplicate_client_id_aborts_safely` (PASSED).
   - `tests/test_reliability_phase2.py::test_rel02_duplicate_nonce_aborts_safely` (PASSED).
   - `tests/test_reliability_phase2.py::test_rel02_nonunique_index_replaced_with_unique_partial_index` (PASSED).
   - `tests/test_security_phase1.py::test_legacy_database_migration_with_nonunique_index` (PASSED).
   - `tests/test_security_phase1.py::test_legacy_database_migration_with_duplicate_records_aborts_safely` (PASSED).

---

### 3.3 REL-03: Automated Backup & Tested Restore CLI
1. **Source Inspection & CLI Architecture:**
   - Implemented in `scripts/backup.py`.
   - **Online SQLite Backup:** Calls `sqlite3.Connection.backup(dest_conn, pages=250)` within python. This locks the database only briefly per page batch and correctly copies uncommitted WAL journal data, eliminating corrupted snapshots caused by raw file copies during active writes.
   - **Atomic File Writes:** Writes backup into `<output_path>.tmp.<pid>`, verifies integrity, and renames atomically via `os.replace` to `<output_path>` upon success.
   - **Checksum & Manifest Generation:** Generates `<output_path>.meta.json` containing:
     - ISO 8601 UTC timestamp.
     - Source file canonical path.
     - Byte size.
     - SHA-256 cryptographic digest of the backup file.
     - Schema version from `schema_migrations`.
     - Exact record counts for `trainees`, `sessions`, `events`.
   - **Verification Subcommand (`verify`):**
     - By default (`require_manifest=True`), verifies file existence, manifest existence, and SHA-256 checksum match with manifest. Also verifies recorded file size matches actual bytes, recorded schema version matches database `schema_migrations`, and recorded table row counts match actual tables. Unmanifested files fail verification with `checksum_verified=False` unless `--allow-unmanaged` is explicitly provided.
     - Opens database in read-only URI mode (`file:... ?mode=ro`).
     - Executes `PRAGMA integrity_check;` asserting result is `ok`.
     - Executes `PRAGMA foreign_key_check;` asserting zero violations.
     - Validates table counts match manifest records when manifest is present.
   - **Safe Restore Subcommand (`restore`):**
     - Refuses to restore over the source backup file (`RuntimeError`).
     - Checks if destination exists; refuses to overwrite unless `--force` is provided.
     - Verifies backup integrity and manifest checksum before restore (`require_manifest=True`).
     - Copies database safely into temporary destination `<dest>.tmp.<pid>`, validates restored file integrity, and renames into final destination atomically using `os.replace` to eliminate data loss windows.
     - Preserves all trainees, sessions, events, foreign keys, indexes, and schema versions.
2. **CLI Usability & Documentation:**
   - Documented in `README.md` under **Database Backup & Restoration (Phase 2)**.
   - Commands:
     - `python scripts/backup.py backup [--source PATH] [--dest PATH]`
     - `python scripts/backup.py verify <backup-file> [--allow-unmanaged]`
     - `python scripts/backup.py restore <backup-file> --dest <target-db> [--force] [--allow-unmanaged]`
     - `python scripts/backup.py info <backup-file>`
     - `python scripts/backup.py list [--dir PATH]`
3. **Automated Verification:**
   - `tests/test_reliability_phase2.py::test_rel03_backup_creation_and_integrity_verification` (PASSED).
   - `tests/test_reliability_phase2.py::test_rel03_backup_manifest_and_sha256_checksum` (PASSED).
   - `tests/test_reliability_phase2.py::test_rel03_manifest_field_tampering_fails_verification` (PASSED).
   - `tests/test_reliability_phase2.py::test_rel03_restore_safe_replacement_destination_preserved_on_failure` (PASSED).
   - `tests/test_reliability_phase2.py::test_rel03_restore_to_separate_destination` (PASSED).
   - `tests/test_reliability_phase2.py::test_rel03_restore_fails_on_collision_without_force` (PASSED).
   - `tests/test_reliability_phase2.py::test_rel03_restore_refuses_to_overwrite_source_backup` (PASSED).
   - `tests/test_reliability_phase2.py::test_rel03_corrupt_backup_rejected_by_verification_and_restore` (PASSED).
   - `tests/test_reliability_phase2.py::test_rel03_backup_online_wal_transaction_consistency` (PASSED).
   - `tests/test_reliability_phase2.py::test_rel03_backup_missing_or_invalid_manifest_handling` (PASSED).
   - `tests/test_reliability_phase2.py::test_rel03_backup_cli_commands` (PASSED).

---

## 4. Phase 2 Independent Acceptance Gate & Full Suite Accounting

Reconciled directly against the freshly generated JUnit XML execution artifact (`reports/PHASE_2_REGRESSION_RESULTS.xml`):

- **Execution Command:** `pytest -v --junitxml=reports/PHASE_2_REGRESSION_RESULTS.xml`
- **Exit Code:** `0` (Success)
- **Console Duration:** `416.19s` (XML runtime: `413.394s`)
- **Total Tests Collected & Executed:** `305`
- **Total Passed:** `305 (100%)`
- **Total Failures:** `0`
- **Total Errors:** `0`
- **Total Skipped:** `0`

### Full Suite Breakdown

| Test Suite Module | Scope / Domain | Total Tests | Passed | Failed | Skipped | Duration |
|---|---|---|---|---|---|---|
| `tests.test_api` | REST API endpoints, serialization, error handling | 17 | 17 | 0 | 0 | ~2.75s |
| `tests.test_auth` | Session auth, redirects, password policy, cookies | 6 | 6 | 0 | 0 | ~1.48s |
| `tests.test_offline_and_parity` | Local static assets, PRNG parity (JS vs Python) | 3 | 3 | 0 | 0 | ~0.28s |
| `tests.test_reliability_phase2` | Phase 2 REL-01, REL-02, REL-03 regression suite | 28 | 28 | 0 | 0 | ~21.78s |
| `tests.test_scenario` | Procedural generation, seeds, degradation levels | 88 | 88 | 0 | 0 | ~1.88s |
| `tests.test_scoring` | Decision-tree nodes, effectiveness rolls, penalties | 50 | 50 | 0 | 0 | ~0.46s |
| `tests.test_security_phase1` | Phase 1 & 1.1 security, tokens, idempotency, rate limits | 69 | 69 | 0 | 0 | ~12.09s |
| **Non-E2E Subtotal** | **All Unit, Security, Scoring, Reliability, and API Suites** | **261** | **261** | **0** | **0** | **~40.7s** |
| `tests.e2e.test_access` | Keyboard navigation, reduced motion, text sizing | 6 | 6 | 0 | 0 | ~46.25s |
| `tests.e2e.test_finish` | Swarm spread, audio cues, auto-quality, unsent session retry, DPR scaling | 12 | 12 | 0 | 0 | ~94.36s |
| `tests.e2e.test_scenarios` | End-to-end mission execution for all 6 scenarios | 13 | 13 | 0 | 0 | ~103.96s |
| `tests.e2e.test_smoke` | Smoke test, radar console tracking & marking, AAR | 2 | 2 | 0 | 0 | ~67.29s |
| `tests.e2e.test_verification` | Sensor modes, degradation levels, AAR dashboard | 11 | 11 | 0 | 0 | ~59.29s |
| **E2E Subtotal** | **Playwright Browser End-to-End Suites** | **44** | **44** | **0** | **0** | **~371.1s** |
| **Grand Total** | **Full AEGIS Regression Test Suite (Phase 1 + 1.1 + Phase 2)** | **305** | **305** | **0** | **0** | **416.19s** |

All counts mathematically reconcile: $261 \text{ non-E2E} + 44 \text{ E2E} = 305 \text{ total tests}$. Machine-readable JUnit XML artifact verified with Python `xml.etree.ElementTree`.

### Acceptance Gate Criteria

1. **REL-01 Verified:** Yes. High-DPI scaling clamping, aspect ratio synchronization, canvas buffer dimension checks, and auto-quality step-down verified via unit and Playwright software-emulated DPR (1.0 to 2.0) tests across all quality ratios. Threshold tests confirm no drop at 36 FPS, reset at 35 FPS, and step-down after 6 windows at 34 FPS.
2. **REL-02 Verified:** Yes. Sequential schema migrations (v1-v4), duplicate data abort checks, complete transactional rollback across fresh schema creation and upgrades, and idempotent execution verified on SQLite. PostgreSQL migrations (v1-v4) verified in runtime against an isolated disposable PostgreSQL 17 cluster initialized via `initdb.exe` on an ephemeral dynamically bound port. Cluster identity (`SHOW data_directory`) confirmed before DDL; index uniqueness and partial index predicates verified in `pg_index`; duplicate rejection and legacy abort without deletion asserted in runtime.
3. **REL-03 Verified:** Yes. Automated backup, manifest generation, integrity checking, recoverable finalization with rollback, and safe restore CLI verified with comprehensive negative tests, manifest enforcement (rejecting field tampering or omissions), and safe `os.replace` atomic destination replacement preserving canary rows on failure.
4. **Full Regression Clean:** Yes. All unit, security, scoring, scenario, API, auth, reliability, and Playwright browser E2E tests pass with 0 failures, 0 errors, and 0 skips.
5. **Data Protection Preserved:** Yes. `data/trainer.db` was untouched and never overwritten or migrated in place during tests (preserved at 290,816 bytes, `PRAGMA integrity_check` = `ok`).

**Phase 1, 1.1 & Phase 2 Joint Verdict:** **PASS — ALL GATES VERIFIED**


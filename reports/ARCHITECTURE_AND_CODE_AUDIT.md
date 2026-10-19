# AEGIS — Architecture and Code Audit Report

**Document:** `reports/ARCHITECTURE_AND_CODE_AUDIT.md`  
**Date:** 2026-10-16  
**Auditor:** Senior Software Architect  
**Scope:** Full-Stack Architecture, Backend APIs, Simulator, Persistence, and Scoring Engine  
**Status:** Complete Audit (Phase 0)  
**Related Journal:** `Improvement.md`  

---

## 1. System Architecture Overview

AEGIS follows an offline-first, server-authoritative web architecture designed for low-friction local execution on standard laptops while maintaining compatibility with cloud-hosted PostgreSQL instances.

```text
Browser Client (Offline / WebGL)                     Flask Application Server (Local / WSGI)
+------------------------------------+               +--------------------------------------+
| - Three.js 3D Viewport             |               | app/views.py (Page Routes)           |
| - Sensor Modes (EO, NV, Thermal)   |  HTTP/JSON    | app/auth.py (Instructor / Session)   |
| - Radar Console Canvas             | ------------> | app/api.py (REST API & Validation)   |
| - Action Logger (Marks, Classes)   | <------------ | app/scenario.py (Scenario Gen/Parse) |
| - AAR Dashboard & Canvas Charts    |               | app/scoring.py (Decision Tree Engine)|
+------------------------------------+               | app/analytics.py (Statistical Rollup)|
                                                     +--------------------------------------+
                                                                    |
                                                     +--------------------------------------+
                                                     | Persistence Layer (app/db.py)        |
                                                     | - Local: SQLite WAL (trainer.db)     |
                                                     | - Hosted: PostgreSQL via psycopg     |
                                                     +--------------------------------------+
```

---

## 2. Component-by-Component Architectural Audit

### 2.1 Frontend & Simulator Architecture
- **Files Inspected:**
  - `app/static/js/sim/world.js` (348 lines): Scene setup, camera, lighting presets, terrain heightfield, building instanced meshes, contact silhouettes.
  - `app/static/js/sim/main.js` (547 lines): Main simulation loop (30 Hz fixed logic tick, requestAnimationFrame rendering), event capture, reticle raycasting, sensor mode switching, keyboard/mouse input handling.
  - `app/static/js/sim/radar.js` (215 lines): Radar sweep animation, polar sweep math, track latency, dropout calculation, radar console display.
  - `app/static/js/sim/rng.js` (29 lines): Deterministic `mulberry32` pseudorandom generator.
- **Strengths:**
  - High performance: Uses `THREE.InstancedMesh` for building geometry (single draw call for up to thousands of urban blocks).
  - Clear separation of concerns: `world.js` manages rendering; `main.js` manages state and event generation; `radar.js` manages simulated sensor tracks.
  - Fully offline: Zero CDN imports. Three.js (`three.module.js`) and Chart.js (`chart.umd.js`) are locally vendored in `app/static/vendor/`.
- **Architectural Findings & Risks:**
  - Display DPI scaling issue in `world.js:L270`: `this.renderer.setPixelRatio(Math.min(window.devicePixelRatio || 1, q.ratio));` sets pixel ratio as high as devicePixelRatio on scaling displays, causing test assertions in `test_finish.py:L190` (`assert low[0] <= 0.75`) to fail on Windows machines with display scaling > 100%.

### 2.2 Flask Routes and API Boundaries
- **Files Inspected:**
  - `app/views.py` (40 lines): Page routes (`/`, `/mission`, `/sim`, `/dashboard`, `/help`, `/dashboard/session/<id>`).
  - `app/api.py` (297 lines): REST endpoints for scenarios, trainees, sessions, analytics, and CSV exports.
- **Strengths:**
  - Clean separation between server-rendered HTML templates and JSON data APIs.
  - Type-safe URL routing using `IdConverter` (`app/db.py:L26-30`), restricting database IDs to valid ranges (1 to 2^63 - 1).
  - Centralized error handlers for `ApiError` and `HTTPException` (`app/api.py:L27-34`).
- **Architectural Findings & Risks:**
  - **Fail-Open Authorization:** In `app/auth.py:L23-25`:
    ```python
    def is_instructor():
        return not login_enabled() or session.get("instructor") is True
    ```
    If `INSTRUCTOR_PASSWORD` is omitted in hosted environments, `login_enabled()` is false, meaning every user is treated as an instructor and all analytics/export/session endpoints are exposed.
  - **Direct Form Submission without CSRF:** `/login` and `/logout` rely on standard HTML forms without CSRF tokens.

### 2.3 Scenario Generation & Deterministic Reproducibility
- **Files Inspected:**
  - `app/scenario.py` (380 lines): Canonical scenario schemas, scripted loading, procedural generation (`generate()`), scripted variations (`build_scripted()`), difficulty presets.
  - `app/scenarios/*.json`: 6 hand-crafted scenarios with fixed waypoints and par times.
  - `app/rng.py` (28 lines): Seeded Python random number generator.
- **Strengths:**
  - Deterministic by seed: Identical seeds produce bit-exact waypoints, spawn times, terrain seeds, and speed multipliers.
  - Strict input validation: Parameters are clamped and checked against allowed sets (e.g., `time_of_day` in `{"day", "dusk", "night"}`).
  - Scripted variant generator (`build_scripted()`): Adds angular rotation (up to 30°) and spawn jitter to avoid rote memorization while strictly preserving par-detection times and flight objectives.

### 2.4 Server-Authoritative Decision Tree Scoring
- **Files Inspected:**
  - `app/scoring.py` (388 lines): Pure functional scoring engine.
  - `rubric.json`: Declarative scoring weights, detection par multipliers, classification confusion mappings, and engagement outcome scores.
- **Strengths:**
  - Untrusted client model: The client never submits scores. It submits raw timestamped action events (`mark`, `classify`, `respond`, `sensor`, `breach`).
  - Strict payload validation (`validate_events()` at `scoring.py:L26-62`): Limits event count to 5000, validates time bounds (`0 <= t <= duration + 60`), checks contact ID string lengths, verifies classification and response keys against `rubric.json`.
  - Transparent explainability: Every contact result returns an explicit decision-tree path (e.g. `["detection/detected_fast", "classification/exact", "engagement/correct_effective"]`) and human-readable reason string.
- **Architectural Findings & Risks:**
  - **Missing Assessment Provenance:** `app/api.py:L173-181` saves scenario and score results, but does not store the SHA-256 hash or version of the `rubric.json` used. If an instructor alters `rubric.json`, historical sessions cannot be mathematically verified against the active rubric at test time.

### 2.5 Storage, Transactions, and Concurrency
- **Files Inspected:**
  - `app/db.py` (151 lines): Storage abstraction layer supporting SQLite and PostgreSQL.
  - `app/schema.sql`: SQLite schema with foreign keys, indexes, and WAL mode.
  - `app/schema_pg.sql`: PostgreSQL schema with BIGINT primary keys and `ON CONFLICT` support.
- **Strengths:**
  - Atomic session persistence: `app/api.py:L172` wraps session and event insertion in a single transaction (`with db:`), guaranteeing no orphaned session records if event insertion fails.
  - Safe concurrency: `find_or_create_trainee` (`app/api.py:L120-123`) utilizes `ON CONFLICT (callsign, unit) DO NOTHING` to prevent race conditions during concurrent user submissions.
- **Architectural Findings & Risks:**
  - **No Migration Mechanism:** Schemas are executed via `init_schema()` without version tracking or Alembic/custom migration steps. Modifying table structures in production would require manual SQL scripts.
  - **PostgreSQL Connection Pool:** In hosted PostgreSQL mode (`PostgresDB`), a new connection is instantiated per request context (`g.db = connect(current_app)` in `get_db()`). While suitable for serverless functions, non-serverless multi-threaded WSGI servers could exhaust connection limits.

### 2.6 AAR Calculations, Analytics, and Exports
- **Files Inspected:**
  - `app/analytics.py` (102 lines): Historical session rollups, score averages, weakest skill calculations, trainee confusion matrix.
  - `app/api.py:L227-277`: CSV export functions `_csv()`, `export_session()`, and `export_unit()`.
- **Strengths:**
  - Pure SQL aggregations: Calculates averages and counts directly in the database engine using cross-compatible SQL (`avg1()` function).
  - Handles sparse data: Safe against trainees with zero recorded sessions.
- **Architectural Findings & Risks:**
  - **CSV Formula Injection:** `_csv()` writes strings directly via Python's standard `csv.writer`. Values starting with `=`, `+`, `-`, `@`, `\t`, or `\r` in `callsign` or `unit` are not neutralized, presenting a direct code injection risk when exported CSV files are opened in spreadsheet applications.

---

## 3. Dependency and Maintainability Assessment

### Dependency Footprint
The runtime dependency list is exceptionally lean:
- `Flask==3.1.3`
- `psycopg[binary]==3.2.4` (optional for PostgreSQL)
- Zero external runtime JavaScript CDNs or asset downloads.

### Code Quality and Cleanliness
- Code follows clean Python conventions, functional design for scoring and scenario generation, and modular JavaScript ES modules.
- Maintainability is high due to low coupling between simulator rendering (`world.js`), input handling (`main.js`), and backend scoring (`scoring.py`).

---

## 4. Remediation Roadmap

1. **Phase 1 (Security & Integrity):** Fail-closed hosted authentication, session start nonces, rubric hash provenance, CSV formula neutralization, HTTP security headers.
2. **Phase 2 (Reliability & Persistence):** Fix DPI scaling in simulator quality step-down test, introduce schema versioning table and migration runner, backup verification script.
3. **Phase 3 (AI & Adaptive Training):** Introduce explainable adaptive practice recommender in `app/adaptive.py`.
4. **Phase 4 (Operations):** Add health check endpoint (`/health`), configuration validator, and structured audit logs.

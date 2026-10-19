# AEGIS Drone Threat Trainer — Initial Baseline Report

**Document:** `reports/INITIAL_BASELINE_REPORT.md`  
**Date:** 2026-10-16  
**Author:** Senior Software Architect & Security Reviewer  
**Status:** Baseline Established (Phase 0)  
**Related Improvement Journal:** `Improvement.md`  

---

## 1. Executive Summary

This report establishes the verified baseline of the AEGIS Drone & Counter-Drone Threat Simulation Trainer (SIH 2026, Problem Statement 26247). An independent inspection of the workspace, Git repository, dependencies, architecture, and automated test suites was performed on 2026-10-16.

The prototype demonstrates a functioning, well-structured software simulation and training pipeline:
1. A browser-based 3D simulator rendering multiple drone classes, sensor modes (Day EO, Night Vision, Thermal), degradation effects, and a radar console.
2. A deterministic scenario generator producing 6 scripted mission scenarios and procedural variants.
3. A server-authoritative decision-tree scoring engine that validates event logs and produces transparent scoring paths.
4. An After-Action Review (AAR) dashboard providing historical trends, confusion matrices, unit comparisons, and replay views.
5. Fully functional offline operation using local bundled assets and an embedded SQLite database.

Material gaps exist in production security (hosted access controls fail open by default, CSV formula injection vulnerability, lack of session submission nonces, and unhardened HTTP headers), test robustness on high-DPI Windows displays, and lack of database migration tooling.

---

## 2. Environment and Repository Condition

- **Operating System:** Windows 11 (64-bit)
- **Python Runtime:** Python 3.13.5 (installed at `C:\Users\Kmano\AppData\Local\Programs\Python\Python313\python.exe`)
- **Pytest Version:** pytest 9.1.1, pluggy 1.6.0
- **Browser Automation:** Playwright with Chromium (Channel: Chrome 145+)
- **Git Branch:** `master`
- **Current Commit:** `19b2e04` (*Hindi interface, rubric v2 (Take cover, soft/hard kill), docs*)
- **Working Tree:** Clean, no uncommitted changes prior to Phase 0 documentation.
- **Repository Path:** `c:\Users\Kmano\Dropbox\Project\Current_Project\drone-sim-platform`

---

## 3. Active Architecture and Frameworks

| Layer | Technology | Vendored / Managed | Active Configuration |
|---|---|---|---|
| Backend Web Server | Flask 3.1.3 | PyPI (`requirements.txt`) | WSGI app factory in `app/__init__.py`, routes in `app/views.py` and `app/api.py` |
| 3D Simulation Engine | Three.js 0.186.1 | Vendored local ES module | Bundled at `app/static/vendor/three.module.js` |
| Visualization & Charts | Chart.js 4.5.1 | Vendored local UMD bundle | Bundled at `app/static/vendor/chart.umd.js` |
| Local Offline Persistence | SQLite 3 | Python Standard Library | Database at `data/trainer.db` (auto-created) with WAL mode & foreign keys |
| Hosted Persistence | PostgreSQL (`psycopg`) | PyPI (`requirements.txt`) | Activated via `DATABASE_URL` environment variable |
| Scoring Configuration | JSON (`rubric.json`) | Repository Root | Versioned rubric defining weights, tiers, classes, penalties, and responses |
| Packaging & Run Scripts | PowerShell, Batch, Shell | Root & `scripts/` | `start.bat`, `start.sh`, `run.py`, `scripts/package.py` |

---

## 4. Feature Implementation Inventory

| Feature | Primary Code Location | Frontend / Templates | Key Tests |
|---|---|---|---|
| Mission Selection & Briefing | `app/api.py`, `app/scenario.py` | `templates/mission.html`, `static/js/mission.js` | `tests/test_scenario.py`, `tests/e2e/test_scenarios.py` |
| 3D Simulator World & Contacts | `app/static/js/sim/world.js`, `app/geometry.py` | `templates/sim.html`, `static/js/sim/main.js` | `tests/e2e/test_smoke.py`, `tests/e2e/test_finish.py` |
| Radar Console & Audio | `app/static/js/sim/radar.js` | `static/js/sim/radar.js`, Web Audio API | `tests/e2e/test_finish.py` |
| Server-Side Decision Tree Scoring | `app/scoring.py`, `rubric.json` | Returned via JSON to `sim.js` | `tests/test_scoring.py` (60+ unit tests) |
| AAR Dashboard & Analytics | `app/analytics.py`, `app/api.py` | `templates/dashboard.html`, `static/js/dashboard.js` | `tests/test_api.py`, `tests/e2e/test_finish.py` |
| Session Replay & Timeline | `app/api.py` (`/api/sessions/<id>`) | `templates/session.html`, `static/js/session.js`, `replay.js` | `tests/e2e/test_finish.py` |
| Instructor Access Control | `app/auth.py` | `templates/login.html` | `tests/test_auth.py` |
| CSV Data Export | `app/api.py` (`_csv()`) | Dashboard export buttons | `tests/test_api.py` |

---

## 5. Discrepancies Between Documentation and Implementation

1. **Test Pass Claims vs. Baseline Reality:**
   - README claims "206 pass: 164 Python tests and 42 browser tests."
   - Independent test execution on Windows 11 identified a failure in `tests/e2e/test_finish.py::test_quality_levels_and_auto_step_down` due to Windows display DPI scaling.
2. **"AI-Enabled" Problem Statement Claim:**
   - The PS title is "AI-Enabled Drone & Counter-Drone Threat Simulation Trainer."
   - The current codebase uses deterministic pseudorandom generation (`mulberry32` / Python `random.Random`), geometric motion, and rule-based decision trees. No AI/ML model is active. An explainable adaptive practice recommender must be formalized.
3. **Hosted Security Posture:**
   - Documentation notes optional instructor authentication, but in actual code, omitting `INSTRUCTOR_PASSWORD` causes `is_instructor()` to return `True`, leaving all hosted sessions and exports publicly readable.

---

## 6. Initial Production Blockers

1. **Critical:** Insecure Default in Hosted Deployments (Fail-Open Auth).
2. **High:** CSV Formula Injection on Export Routes.
3. **High:** Unprotected Session Submission (No Nonce, Replay Vulnerability).
4. **Medium:** Flaky / Display-DPI Dependent Browser Test on Windows.
5. **Medium:** Absence of Database Migration and Schema Version Tracking.

---

## 7. Next Actions

Proceed directly to Phase 1: Remediate critical security vulnerabilities and harden assessment integrity.

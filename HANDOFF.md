# Hand-off: AEGIS // Drone Threat Trainer (SIH PS 26247)

Oct 7, 2026 · Repo: [ammar-iitm/drone-sim-platform](https://github.com/ammar-iitm/drone-sim-platform) (private), branch `master`, commit `3627c66` or later.

This is the starting page for anyone picking up the project. The detail lives in the documents linked below; this file says where things stand, how to get going, and what is left.

## Where it stands

- **The prototype is complete.** All three problem-statement outcomes work end to end: a 3D simulator with scripted and procedural scenarios, decision-tree scoring, and the AAR dashboard. It runs offline on a laptop.
- **Requirements:** 19 of 21 PRD requirements are verified by tests or screenshots. Two are partial:
  - **F8 audio:** tested in code, but nobody has listened yet.
  - **F9 VR:** not built; desktop only by lead decision.
- **Tests:** 146 pass in total, 114 Python and 32 browser (Playwright).
- **Checklist:** 66 of 81 items ticked. Of the 15 left, 4 are not applicable because there is no demo, and 11 are open (see "What is left").
- **No demo is scheduled** (lead decision, 2026-10-07). [docs/DEMO.md](docs/DEMO.md) is kept as a ready walkthrough in case one is arranged.

## Get going in 5 minutes

```bash
git clone https://github.com/ammar-iitm/drone-sim-platform.git
cd drone-sim-platform
./start.sh --demo            # Windows: start.bat --demo (not yet tested on Windows)
```

This needs Python 3.10 or newer, and internet once for the first install. The script then opens http://localhost:5050/mission with a seeded demo cohort.

To run the tests:

```bash
.venv/bin/python -m pytest tests --ignore=tests/e2e    # 114 Python tests, under a second
.venv/bin/pip install playwright                        # browser tests use the installed Chrome
.venv/bin/python -m pytest                              # all 146
```

[README.md](README.md) covers controls, options, graphics quality and rubric editing.

## Map of the code

| Path | What it is |
| --- | --- |
| `app/__init__.py` | Flask app factory. The database is `data/trainer.db` (SQLite) and the rubric is `rubric.json` |
| `app/api.py` | JSON API: scenarios, rubric, trainees, sessions (submit, then score, then store), analytics, CSV export |
| `app/scoring.py` | The decision tree. A pure function of scenario, events and rubric. **The server owns the score** and ignores any score the browser sends |
| `app/scenario.py`, `app/scenarios/*.json` | Seeded procedural generator and the six scripted scenarios |
| `app/rng.py` and `app/static/js/sim/rng.js` | Response rolls that are bit-identical in Python and JS (a test enforces this) |
| `app/analytics.py` | Trainee trends, unit rollup, weakest skill, confusion matrix |
| `app/static/js/sim/` | The simulator. `main.js` holds the loop, input and HUD; `world.js` the Three.js rendering (the VR seam); `radar.js` the radar model; `audio.js`, `marks.js`, `path.js` |
| `app/templates/`, `app/static/css/` | Pages and the Stitch "AEGIS" dark look |
| `rubric.json` | Every scoring number. Edits apply to the next session with no restart |
| `tests/` | Python tests; `tests/e2e/` holds the Playwright tests, which block every non-local request |
| `scripts/seed_demo.py`, `scripts/package.py` | Demo data (`--reset`), and the submission zip in `dist/` |
| `archive/` | The original Antigravity prototype (Node/React/Unity). Kept for reference, not used |
| `frontend/` | An empty leftover Vite cache. Not tracked by git; safe to ignore |

## Documents

| Document | Use it for |
| --- | --- |
| [docs/STATUS.md](docs/STATUS.md) | The evidence: the requirement map F1 to F21, scoring rules, decisions, human checks |
| [docs/CHECKLIST.md](docs/CHECKLIST.md) | The full task list. Tick only what you actually ran and saw work |
| [docs/TEAM_PLAN.md](docs/TEAM_PLAN.md) | Who does what: Lead, Track A (test and polish), Track B (rubric and submission) |
| [docs/RUBRIC_SOURCES.md](docs/RUBRIC_SOURCES.md) | **Draft.** Rubric compared with public counter-UAS sources (#14) |
| [docs/PS_MAPPING.md](docs/PS_MAPPING.md) | **Draft.** Each problem-statement element mapped to features and evidence (#19) |
| [docs/PRD.md](docs/PRD.md), [docs/AVD.md](docs/AVD.md), [docs/VISUAL_DESIGN.md](docs/VISUAL_DESIGN.md) | The original plan |
| [docs/DEMO.md](docs/DEMO.md) | Walkthrough script (no demo scheduled) |

## Decisions already made (2026-10-07)

- **Stack:** Flask and SQLite on the server; Three.js and Chart.js vendored, with no CDN.
- **Look:** Stitch dark theme only. This deviates on purpose from the Visual Design doc's light dashboard.
- **Text:** data text is at least 14 px, and only captions are 12 px. A test enforces this.
- **Desktop only.** No VR in this release.
- **Grade bands:** A ≥ 90, B ≥ 80, C ≥ 70, D ≥ 60, otherwise F.
- **No demo** for now. Issues #1, #3, #17 and #18 are closed as not planned; reopen them if a demo comes back.

## What is left

Tracked as GitHub issues with labels `lead`, `track-a` and `track-b`.

| Owner | Issue | Task | Blocked on |
| --- | --- | --- | --- |
| Lead | #7 | Confirm the track owners and the merge reviewer; share teammates' GitHub usernames | — |
| Lead | #6 | Pick the target laptop and record its GPU and browser | — |
| Track A | #8 | 12-drone swarm at 30 fps or better on the target laptop (so far: 30 fps with 8 drones) | #6 |
| Track A | #9 | Launch to first scenario in under 60 s, timed by hand (scripted run: 2.3 s warm, 8.4 s cold) | #6 |
| Track A | #10 | Install on a second machine from the README only; **run `start.bat` on Windows** | — |
| Track A | #11 | Human checks: listen to the audio cues and M to mute, greyscale colour-blind review, Urban Canyon feel | — |
| Track A | #13 | Keep the full suite green on every merge | ongoing |
| Track B | #14 | Review `RUBRIC_SOURCES.md`; read ATP 3-01.81 directly; mark rows Agreed, Changed or Rejected | — |
| Track B | #15 | Agree the scoring interpretations with the lead, including whether Take cover or Report should earn credit against a hostile | Lead |
| Track B | #16 | Read the plan docs against the running app and list disagreements | — |
| Track B | #19 | Paste the official PS 26247 text into `PS_MAPPING.md` and check every row | — |
| Track B | #20 | Build the zip (`scripts/package.py`), submit on the SIH portal, keep the confirmation | #19 |

## Known limits and risks

- **Frame rate headroom is thin.** 30 fps was measured with 8 drones on the team laptop. Quality levels (Auto, High, Medium, Low) exist, but 12 drones has not been measured on real hardware.
- **`start.bat` has never run on Windows.**
- **The cold-start time (8.4 s) had pip's cache warm.** A truly fresh machine will be slower on the first install.
- **Rubric numbers** (weights, penalties, grade bands, the 300 m "late" range) are team choices. No public source gives them. Say so if anyone asks.
- **Scoring is server-side only.** If the server is down at the end of a session, the session is kept in the browser and offered for resending on Mission select.
- **`--lan` mode has no login.** Use it only on a trusted network.

## Working rules

- Work on one branch per track (`track-a`, `track-b`), open small PRs into `master`, and the lead reviews.
- Run `.venv/bin/python -m pytest` before every PR. All tests must pass.
- When you tick a checklist item, add its evidence (a number, test name or screenshot) to `STATUS.md` in the same PR.
- Never hand-edit `data/trainer.db`. Regenerate it with `scripts/seed_demo.py --reset`.
- Don't delete anything from the repo; move retired code to `archive/`.

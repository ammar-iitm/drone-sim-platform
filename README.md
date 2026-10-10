# AEGIS // Drone Threat Trainer (SIH PS 26247)

A browser-based simulator that trains unit-level personnel to detect, classify and respond to drone and swarm threats. Every session is scored on the server by an explainable decision tree, and an after-action review (AAR) dashboard tracks trainees and units over repeated sessions. It runs fully offline on an ordinary laptop.

This README is the single place for how to run the trainer, where it stands and what is left. The original design specs are in [docs/PRD.md](docs/PRD.md) (requirements F1–F21), [docs/AVD.md](docs/AVD.md) (architecture) and [docs/VISUAL_DESIGN.md](docs/VISUAL_DESIGN.md). [docs/RUBRIC_SOURCES.md](docs/RUBRIC_SOURCES.md) is the working draft for the rubric review (issue #14).

## Problem statement (SIH PS 26247)

The official statement asks for a software platform that trains personnel to recognise, classify and respond to drone and swarm threats across day and night, degraded sensors, urban and rural terrain, and single-drone and swarm attacks, usable at unit level with minimal specialised hardware. Its four expected outcomes, and where each is met:

| Expected outcome | How the trainer meets it |
| --- | --- |
| Desktop or VR-capable simulator with scripted and procedurally generated threat scenarios | Browser 3D simulator (Three.js) with six scripted scenarios, each with a learning objective, and a seeded procedural generator. Desktop only; the statement accepts desktop **or** VR |
| Decision-tree based scoring on detection time, threat classification accuracy and engagement decisions | Server-side decision tree from `rubric.json`; every score shows its tree path and a reason |
| After-action review (AAR) dashboard tracking individual and unit performance over repeated sessions | `/dashboard`: trainee trends, unit rollup, weakest skill and trainees, confusion matrix, session timelines, CSV export |
| Adjustable difficulty and scenario randomization to prevent rote learning | Difficulty 1–5 scales speed, counts, decoys and degradation together. The procedural seed is random on every visit, and scripted scenarios launch as a seeded variant by default (**Vary each run**) |

The rest of the statement is covered too:
- **Drone types:** commercial quadcopters and hexacopters, and a military-grade fixed-wing loitering drone.
- **Distractors:** birds, balloons used as decoys, and a friendly aircraft.
- **Conditions:** day, dusk and night; EO, night vision and thermal; four sensor degradation levels with fog, noise and radar dropout; urban and rural terrain.
- **Attacks:** single drones and swarms of up to 12.
- **Hardware:** it runs offline in a browser on an ordinary laptop.

## Status (2026-10-10)

- **Requirements:** 19 of the 21 PRD requirements are verified by tests or screenshots. Two are partial:
  - **F8 audio:** every cue and the mute key are tested in code, but nobody has listened yet (issue #11).
  - **F9 VR:** not built, by decision; rendering is isolated in `world.js` so it can be added later.
- **Tests:** 186 pass: 147 Python tests and 39 browser tests. The browser tests play all six scenarios end to end, both standard and varied.
- **Offline:** verified. Every browser test blocks non-local requests, and a full run with Wi-Fi off was done by hand on 2026-10-06.
- **Target laptop:** MacBook Pro (Mac17,9), Apple M5 Pro (15-core CPU, 16-core GPU), 24 GB, macOS 27.0.1, Chrome 155.0.8059.39.
  - **12-drone swarm:** 120 fps on both Auto and Low quality at 1920 × 1080. That is the display's refresh cap.
  - **Launch to first scenario:** 0.7 s with `.venv` already built; 5.4 s from a fresh clone, where `start.sh` builds `.venv` and installs everything first. The target is under 60 s.
  - Both were measured on 2026-10-10 by a script driving a visible Chrome window.

## Install and run

You need Python 3.10 or newer and a current Chrome, Edge or Firefox. The first start needs internet once to install Flask; after that everything runs offline. Three.js and Chart.js are bundled in `app/static/vendor/`, and the pages use system fonts.

**One command** (creates `.venv` on the first run, then opens the browser at http://localhost:5050/mission):

```bash
./start.sh              # macOS or Linux
./start.sh --demo       # also seed a demo cohort (6 trainees, 2 units, 30 scored sessions) if there is no database yet
```

```bat
start.bat               :: Windows (double-click works too)
start.bat --demo
```

**By hand:**

```bash
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt        # Windows: .venv\Scripts\pip install -r requirements.txt
.venv/bin/python run.py                          # Windows: .venv\Scripts\python run.py
```

Options:

```bash
.venv/bin/python scripts/seed_demo.py --reset    # reset the database to the demo cohort
.venv/bin/python run.py --port 8000 --lan        # expose on the local network (no login; trusted networks only)
NO_BROWSER=1 ./start.sh                          # start without opening a browser
.venv/bin/python scripts/package.py              # build dist/drone-threat-trainer-<date>.zip to copy to another machine
```

**Graphics quality.** On a slow laptop, choose **Graphics quality** on Mission select:
- **Auto** (the default) starts at High and steps down if the frame rate stays under 35 fps for 3 seconds.
- **Low** renders at 0.75× resolution with no antialiasing and draws only the nearest 35% of scenery.

You can also add `&quality=low` to a simulator URL.

**If a save fails.** If the server is unreachable when a session ends, the session is kept in the browser. Mission select then offers to send it once the server is back.

## Hosted version (Vercel)

Live at **https://drone-sim-platform.vercel.app**. It's public, with no login.

- **Hosting:** the Vercel project `drone-sim-platform` on team `the-layers`, running as one Flask function in `iad1` (US East). `index.py` is the entrypoint.
- **Database:** Neon Postgres from the Vercel Marketplace (`drone-trainer-db`). Neon sets `DATABASE_URL` on the project. When `DATABASE_URL` is set the app uses Postgres (`app/schema_pg.sql`); otherwise it uses the local SQLite file, so the laptop version stays fully offline. Queries are written once; `app/db.py` translates them for Postgres.
- **Deploying:** run `npx vercel deploy --prod` from the repo root. The project is **not** connected to GitHub, so pushing doesn't deploy. `.vercelignore` keeps tests, archive, screenshots and local data out of the upload.
- **Testing on Postgres:** `TEST_DATABASE_URL=<url> .venv/bin/python -m pytest tests --ignore=tests/e2e` runs the Python tests on Postgres. The test tables are dropped before every test, so point it at a throwaway database (for example, run `CREATE DATABASE trainer_test` in the Neon project and use that URL), **never** the live `neondb`.
- **Sidebar labels:** the sidebar and simulator show **Hosted / Postgres hosted** instead of **Offline / SQLite local**.

## Using it

1. **Mission select** (`/mission`): enter a callsign and unit. Pick one of the six scripted scenarios, or set seed, difficulty, time of day, terrain, degradation, swarm size and threat mix for a procedural one. Then press **Launch**.
   - **Vary each run** (on by default) launches a scripted scenario as a seeded variant: every approach turns by the same angle (up to 30°), spawn times shift, and response rolls change, so trainees cannot learn it by rote. The learning objective stays the same. Untick it to replay the standard version. A variant is reproducible from its number (`/sim?id=s1-dawn-recon&vary=4242`).
   - The procedural seed starts on a new random value on every visit.
2. **Simulator** (`/sim`): read the briefing, press **Enter**, and work the threats.

   | Input | Action |
   | --- | --- |
   | Drag or arrow keys | Look |
   | Wheel or `+` / `-` | Zoom 1x, 2x, 4x, 8x |
   | Click, or `Space` at the reticle | Mark a contact (empty sky is a false alarm) |
   | Click a radar track | Mark that track |
   | `Tab` / `Shift+Tab` | Cycle marked contacts |
   | `1` to `5` | Classify: Recon quadcopter, Armed loitering drone, Decoy or balloon, Bird, Friendly aircraft |
   | `T` `R` `J` `I` `C` | Respond: Track, Report, Jam, Intercept, Take cover |
   | `S` | Sensor mode: day EO, night vision, thermal |
   | `Q` | Radar console: full-screen scope plus track table |
   | `[` / `]` | Radar range 1.5, 3 or 6 km |
   | `Space` in the console | Mark the closest unmarked radar track |
   | `M` | Mute or unmute the audio cues |
   | `P` / `Esc` | Pause / end the session |

3. **Score screen**: shows the composite score, grade, stage bars and the decision-tree path with a reason for every contact. **Run same seed again** replays the identical scenario, including the same variant of a scripted one.
4. **Help and scoring** (`/help`): controls, threat markers, sensors and radar, and the full scoring tree drawn live from `rubric.json`.
5. **AAR dashboard** (`/dashboard`): shows the unit overview, trainee progress (with a table view), unit comparison, confusion matrix and session log. Each session links to the session review timeline.

## Editing the rubric

All scoring numbers live in [`rubric.json`](rubric.json). The next session is scored with whatever the file says, with no code change or restart. Each key controls:

| Key | Controls |
| --- | --- |
| `weights` | Stage weights (default 30 detection, 30 classification, 40 engagement) |
| `detection_tiers` | Points by time-to-detect as a multiple of the contact's par time |
| `classification_scores` | Exact, same family, wrong family |
| `engagement_scores` | Correct and effective, correct but failed roll, late or unsuitable, none or breach, restraint, unnecessary engagement |
| `penalties` | False alarm (and cap), breach, critical error |
| `grade_bands` | Minimum total for each grade |
| `geometry` | Inner ring radius (breach), "late" range, mark tolerance |
| `classes` | Class labels, families and hot keys; `critical_misclassification` says which wrong calls are critical |
| `responses` | Labels, hot keys, whether a response engages, range limits and effectiveness per drone model |
| `expected_responses` | Suitable responses per model (a scenario contact can override this) |

The browser never sends a score. It sends raw events (`mark`, `classify`, `respond`, `sensor`, `breach`), and the server rebuilds the scenario from its id (and variant number) or seed and scores it. Response success rolls come from the scenario seed (`app/rng.py`, mirrored in `app/static/js/sim/rng.js`), so the result is reproducible.

## Folder layout

```
app/
  __init__.py        Flask app factory
  api.py             JSON API (scenarios, rubric, trainees, sessions, analytics)
  views.py           Pages: /mission, /sim, /dashboard, /dashboard/session/<id>, /help
  scenario.py        Seeded generator: scripted + procedural scenarios, difficulty table
  scenarios/*.json   The six scripted scenarios (waypoints as bearing, range, altitude)
  scoring.py         Decision-tree scoring: a pure function of scenario, events and rubric
  geometry.py        Contact paths (shared maths with static/js/sim/path.js)
  rng.py             Seeded rolls (bit-identical with static/js/sim/rng.js)
  analytics.py       Trends, confusion matrix, unit rollup
  db.py, schema.sql  Storage: SQLite (data/trainer.db) by default; Postgres (schema_pg.sql) when DATABASE_URL is set
  templates/         Pages in the AEGIS (Stitch) style
  static/css/        aegis.css (design system), sim.css (HUD)
  static/js/sim/     Simulator: world.js (Three.js scene), radar.js, main.js (loop, input, HUD)
  static/js/         mission.js, dashboard.js, session.js, help.js, results.js
  static/vendor/     Three.js 0.186.1, Chart.js 4.5.1 (with licences)
rubric.json          Editable scoring rubric
run.py               Start the app (start.sh / start.bat wrap it with first-run setup)
index.py             Vercel entrypoint (hosted version)
scripts/seed_demo.py Seed a demo cohort through the real API
scripts/package.py   Build a clean zip to copy to another machine
tests/               pytest: generator, scenario variants, scoring tree, API, offline check, JS/Python roll parity
tests/e2e/           Browser tests (Playwright with the installed Chrome); screenshots go to test-results/
archive/             Earlier Antigravity prototype (Node/React/Unity) and the original Stitch screens
docs/                PRD, AVD and Visual Design specs; rubric sources draft
data/                SQLite database (created on first run; delete to reset)
```

## Tests

```bash
.venv/bin/python -m pytest tests --ignore=tests/e2e    # 147 Python tests, under a second
.venv/bin/pip install playwright                        # once: the browser tests drive the installed Chrome
.venv/bin/python -m pytest                              # all 186, about 5 minutes
TEST_DATABASE_URL=<postgres url> .venv/bin/python -m pytest tests --ignore=tests/e2e   # same tests on Postgres
```

The browser tests block every non-local request, so they also check that nothing is fetched from the internet.

## Decisions

| Date | Decision |
| --- | --- |
| 2026-10-07 | **Stack:** Flask and SQLite on the server; Three.js and Chart.js vendored, with no CDN |
| 2026-10-07 | **Look:** Stitch "AEGIS" dark theme only. This deliberately departs from the Visual Design doc's light dashboard |
| 2026-10-07 | **Text:** data text is at least 14 px; only captions are 12 px (enforced by `test_access::test_text_sizes`) |
| 2026-10-07 | **Desktop only.** No VR in this release |
| 2026-10-07 | **Grade bands:** A ≥ 90, B ≥ 80, C ≥ 70, D ≥ 60, otherwise F |
| 2026-10-07 | **No demo is scheduled** |
| 2026-10-10 | **No zip submission.** `scripts/package.py` still builds one if it is ever needed |
| 2026-10-10 | **Target laptop:** the MacBook Pro listed under Status |
| 2026-10-10 | **Team:** Ammar owns every track and reviews merges |
| 2026-10-10 | **Hosted on Vercel** with Neon Postgres, public link, no login. Local and offline use stays on SQLite |

## Open scoring questions (issue #15)

These are how the code reads the AVD today. Each one needs a yes or a change:

1. A correct, timely response that fails its success roll keeps 60% of the engagement points even if the drone then breaches. The 10-point breach penalty still applies.
2. Decoys count as non-threats: they are scored only if marked, and engaging one is an unnecessary engagement.
3. "Late" means engaging inside 300 m.
4. Suitable responses: jam or intercept for quadcopters and hexacopters, and intercept only for fixed-wing drones.
5. Swarm members are counted on top of the difficulty table's hostile count.
6. Should **Take cover** or **Report** earn credit against a hostile drone?

## What is left

Tracked as GitHub issues, all assigned to Ammar:

| Issue | Task |
| --- | --- |
| #10 | Install on a second machine using only this README, including the first-ever run of `start.bat` on Windows. A weaker laptop would also test performance |
| #11 | Human checks. Play any scenario with sound on: the rotor hum should rise as a drone closes in, the tick, chime, buzz and breach alarm should play on their events, and **M** should mute. Set macOS Display → Colour filters → Greyscale and check that the threat markers (triangle, diamond, circle, square, each with a text label) and the dashboard still read clearly. In Urban Canyon, the drone should show for about 4 s around T+37 s and again on final approach |
| #14 | Review `docs/RUBRIC_SOURCES.md` against public counter-drone guidance (read ATP 3-01.81 directly), and mark each row Agreed, Changed or Rejected |
| #15 | Settle the open scoring questions above |
| #16 | Read the PRD, AVD and Visual Design docs against the running app and list any disagreements |
| #13 | Keep the full test suite passing on every merge (ongoing) |

## Known limits and risks

- **This is a decision-training aid, not a weapons simulator.** Responses are abstract categories with configurable effectiveness. There is no ballistic or countermeasure modelling.
- **The rubric numbers are team choices.** The structure follows public counter-drone principles, but no public source gives the weights (30/30/40), detection tiers, penalties (2/10/25), grade bands or the 300 m "late" range. Say so if asked, and don't cite doctrine for them. Instructors can edit all of them.
- **The target laptop is fast.** 120 fps on an M5 Pro says little about the PRD baseline (integrated GPU, 8 GB RAM). An earlier run reached only 30 fps with 8 drones, before quality levels existed. On weaker machines, Auto lowers the quality by itself; measure there before relying on it.
- **`start.bat` has never run on Windows.**
- **The cold-start times had pip's download cache warm.** A truly fresh machine will be slower on the first install. `start.sh` needs Python 3.10 or newer and refuses macOS's built-in 3.9 with a clear message.
- **Scoring needs the server.** If the server is down when a session ends, the session is kept in the browser and offered for resending on Mission select.
- **Identity:** trainees are identified by callsign and unit only.
- **`--lan` mode has no login.** Use it only on a trusted network.
- **The hosted version is public with no login.** Anyone with the link can create trainees and sessions, and read the dashboard and CSV exports. Keep real personnel data off it. Before wider use, add instructor login or turn on Vercel Deployment Protection.
- **Hosted latency:** every request opens a new database connection to Neon, and Neon's free tier sleeps when idle. The first request after a quiet spell takes a second or two longer.
- **Visual effects are not scored.** Swarm separation and wobble are drawn on top of each drone's path; the server always scores the clean path.

## Working rules

- Run `.venv/bin/python -m pytest` before every merge. All tests must pass.
- Never hand-edit `data/trainer.db`. Regenerate it with `scripts/seed_demo.py --reset`.
- Keep retired code in `archive/` rather than deleting it.
- Commit messages are plain text with no tool attribution.

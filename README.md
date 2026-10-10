# AEGIS // Drone Threat Trainer (SIH PS 26247)

A browser-based simulator that trains unit-level personnel to detect, classify and respond to drone and swarm threats. Every session is scored on the server by an explainable decision tree, and an after-action review (AAR) dashboard tracks trainees and units over repeated sessions. It runs fully offline on an ordinary laptop.

New to the project? Start with [HANDOFF.md](HANDOFF.md). Planning documents: [docs/PRD.md](docs/PRD.md), [docs/AVD.md](docs/AVD.md), [docs/VISUAL_DESIGN.md](docs/VISUAL_DESIGN.md), [docs/CHECKLIST.md](docs/CHECKLIST.md), [docs/STATUS.md](docs/STATUS.md).

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
.venv/bin/python run.py --port 8000 --lan        # expose on the local network (no login; see AVD)
NO_BROWSER=1 ./start.sh                          # start without opening a browser
.venv/bin/python scripts/package.py              # build dist/drone-threat-trainer-<date>.zip for submission or another machine
```

**Graphics quality.** On a slow laptop, choose **Graphics quality** on Mission select:
- **Auto** (the default) starts at High and steps down if the frame rate stays under 35 fps for 3 seconds.
- **Low** renders at 0.75× resolution with no antialiasing and draws only the nearest 35% of scenery.

You can also add `&quality=low` to a simulator URL.

**If a save fails.** If the server is unreachable when a session ends, the session is kept in the browser. Mission select then offers to send it once the server is back.

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

3. **Score screen**: shows the composite score, grade, stage bars and the decision-tree path with a reason for every contact. **Run same seed again** replays the identical scenario.
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
  db.py, schema.sql  SQLite storage (data/trainer.db)
  templates/         Pages in the AEGIS (Stitch) style
  static/css/        aegis.css (design system), sim.css (HUD)
  static/js/sim/     Simulator: world.js (Three.js scene), radar.js, main.js (loop, input, HUD)
  static/js/         mission.js, dashboard.js, session.js, help.js, results.js
  static/vendor/     Three.js 0.186.1, Chart.js 4.5.1 (with licences)
rubric.json          Editable scoring rubric
run.py               Start the app (start.sh / start.bat wrap it with first-run setup)
scripts/seed_demo.py Seed a demo cohort through the real API
scripts/package.py   Build a clean zip for submission or another machine
tests/               pytest: generator, scoring tree, API, offline check, JS/Python roll parity
tests/e2e/           Browser smoke test (Playwright with the installed Chrome)
archive/             Earlier Antigravity prototype (Node/React/Unity) and the original Stitch screens
docs/                PRD, AVD, Visual Design, checklist, status audit
data/                SQLite database (created on first run; delete to reset)
```

## Tests

```bash
.venv/bin/python -m pytest              # all tests, including the browser smoke test
.venv/bin/python -m pytest tests/e2e    # browser only: needs `pip install playwright` and Google Chrome
```

The browser test blocks every non-local request, so it also checks that nothing is fetched from the internet.

## Assumptions and limits

- This is a decision-training aid, not a weapons simulator. Responses are abstract categories with configurable effectiveness, and there is no ballistic or countermeasure modelling.
- The rubric is built from public counter-drone principles, and instructors can edit it.
- Trainees are identified by callsign and unit only.
- `--lan` mode has no authentication. Add instructor login before any shared deployment.

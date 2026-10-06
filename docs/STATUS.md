# Project Status Audit: Drone Threat Trainer (SIH PS 26247)

**Date:** 2026-10-06
**Yardstick:** `docs/PRD.md` (F1–F21), `docs/AVD.md`, `docs/VISUAL_DESIGN.md`, `docs/CHECKLIST.md`, copied unchanged from `~/Downloads` on 2026-10-06.
**Scope:** Audit only. No source code was edited, moved or deleted. No dependencies were installed.
**Auditor environment:** macOS (Darwin 27), Node v26.7.0, npm 11.19.0, Python 3.14.6 (Flask and pytest **not** installed), Google Chrome 154 headless, no Playwright.

## Summary

Of the 21 requirements: **0 Verified, 1 Partial, 0 Present but unverified, 20 Missing, 0 Broken.** The only Partial is F20: the backend keeps an ordered list of the last 50 events in memory, but with no scores, no storage and no UI. The existing code was built by Antigravity against a different, lighter plan that it wrote itself (Unity client, Node backend, Postgres). It does not follow the AVD's stack: **Node/Express + React/Vite + a Unity C# script instead of Flask + Three.js + SQLite + pytest**.

What exists:
- Six polished but entirely **static** UI mockups exported from Google Stitch, shown in iframes by a small React shell. Every number on screen is hard-coded.
- A ~100-line Express/WebSocket server with one REST route (`/api/status`).
- One Unity script with no Unity project around it.

What doesn't exist: a 3D simulator, a scenario generator, a scoring engine, a database, a rubric file and tests. Every AVD endpoint returns 404, so the determinism and event-log scoring checks could not be run. Three hard constraints are not met: offline, server-owned scoring and determinism. Offline is actively broken: with external DNS blocked, every screen renders unstyled. Separately, `npm run build` fails on six unused auto-converted React files, and screen 6 throws a runtime `ReferenceError`. Nothing in `docs/CHECKLIST.md` could be ticked. **The practical conclusion is that the build is effectively at milestone 0 of the PRD. The mockups are useful only as visual reference, and even they conflict with the Visual Design doc on fonts, palette, text size and offline use.**

---

## Step 1: Plan documents

The four docs were not in the project when the audit started (there was no `docs/` folder). They were found in `~/Downloads` and copied to `docs/` without changes. Antigravity had also written its own, different `PRD.md`/`AVD.md`/`Visual_Design.md` into `~/.gemini/antigravity/brain/8a179d63-…/`. Those describe Unity + Node + Postgres + InfluxDB and requirements FR-1.1–FR-4.2, which explains why the code diverges from your plan. They are **not** the yardstick here.

Key yardstick facts used below:
- **AVD stack:** Flask, SQLite (stdlib), plain-Python generator and scoring, Three.js and Chart.js vendored locally, system fonts, pytest + Playwright.
- **AVD endpoints:** `/api/scenarios`, `/api/scenario`, `/api/rubric`, `/api/trainees` (GET, POST), `/api/sessions` (GET, POST), `/api/sessions/<id>`, `/api/analytics/trainee/<id>`, `/api/analytics/unit/<unit>`.
- **VD:** system fonts, specific light/dark/HUD tokens, threat = colour + shape + label, minimum 14 px body text, full keyboard path, table view for every chart.

---

## Step 2: Inventory

### Folder tree (excluding `node_modules`, `.git`, caches)

```
drone-sim-platform/
├── docs/                    PRD, AVD, VISUAL_DESIGN, CHECKLIST (copied in by this audit), STATUS (this file)
├── backend/                 Node, not Flask
│   ├── index.js             Express 5 + ws: GET /api/status, WebSocket relay of 3 message types
│   ├── simulate.js          Dummy client: fake telemetry at 5 Hz + a random canned event every 3.5 s (hard-coded ws://localhost:3001)
│   ├── package.json         express 5.2.1, ws 8.22.0, cors 2.8.6, dotenv 18.0.5 (dotenv unused); "test" script just errors
│   └── package-lock.json
├── frontend/                Vite 8 + React 19 + TypeScript 6 + Tailwind 4
│   ├── index.html           <title>frontend</title>
│   ├── vite.config.ts       tailwind + react plugins; no backend proxy
│   ├── package.json         also recharts + lucide-react (unused)
│   ├── .oxlintrc.json, tsconfig*.json, README.md (Vite template), .gitignore
│   ├── public/favicon.svg, icons.svg
│   ├── public/stitch/screen1..6.html/.png   Static Stitch mockups served to the iframes
│   └── src/
│       ├── main.tsx         React root
│       ├── App.tsx          6-tab nav; shows the chosen mockup in an <iframe>
│       ├── index.css; App.css (template, unused); assets/ (template images)
│       └── LiveDashboard, ScenarioBuilder, AARReports, UnitRoster, ReadinessMatrix, FlightRoster .tsx
│                            Regex-converted mockups. Not imported anywhere. Do not compile.
├── stitch_ui/
│   ├── screen1..6.html/.png Original Stitch exports (byte-identical to frontend/public/stitch)
│   └── convert.js           One-off HTML→JSX regex converter that produced the broken .tsx files
└── unity_integration/
    └── TelemetryManager.cs  Unity WebSocket client stub: send telemetry/events; SPAWN_KAMIKAZE / TOGGLE_JAMMING only log
```

Six mockup screens: 1 Live Dashboard (2D radar), 2 Scenario Builder, 3 AAR Reports, 4 Unit Roster, 5 Readiness Matrix, 6 Flight Inspector.

### Backend routes and messages

| Kind | Name | What it does | Evidence |
|---|---|---|---|
| REST | `GET /api/status` | Returns the single global in-memory `sessionState` | `backend/index.js:31` |
| WS | `INIT_STATE` | Sent to each client on connect | `backend/index.js:40` |
| WS | `SIMULATION_UPDATE` | Overwrites global `drones`/`timeElapsed`, rebroadcasts the whole state | `backend/index.js:47-58` |
| WS | `NEW_EVENT` | Prepends to global `events` (cap 50), rebroadcasts | `backend/index.js:60-71` |
| WS | `INSTRUCTOR_COMMAND` | Logs and rebroadcasts | `backend/index.js:73-82` |

Templates: none (Flask/Jinja not used). Static scripts: inline `<script>` blocks in each mockup (Tailwind config plus mock interactivity, e.g. 37 `onclick` handlers in screen6). **Tests: none.** Config: two `package.json`, `tsconfig*.json`, `vite.config.ts`, `.oxlintrc.json`. No `requirements.txt`, no `rubric.json`, no DB schema, no `.env`.

### Differences from the plan

**Different stack (AVD → existing)**

| AVD | Existing | Note |
|---|---|---|
| Flask (Python) | Express 5 + ws (Node) | Plus WebSocket push, which the AVD doesn't use |
| SQLite, `data/` folder | In-memory JS object, no persistence | |
| Plain Python generator + scoring | Neither exists | |
| Three.js 3D first-person view | None. Static SVG radar mockup + a Unity C# stub | PRD lists VR as a non-goal for the first release |
| Chart.js vendored | recharts installed, unused; mockup charts are static SVG | |
| Server-rendered pages | React SPA showing static HTML in iframes | |
| System fonts | Google Fonts: Inter, Space Mono, Material Symbols | |
| pytest + Playwright | No tests | |

**Different API:** only `/api/status`, which isn't in the AVD. None of the 9 AVD endpoints exist. Telemetry is pushed over WebSocket rather than sent as a POSTed event log, and the event schema differs: `{level, message, time}` free text versus the AVD's `{t, type: mark|classify|respond|sensor|breach, contact_id, data}`.

**Different domain vocabulary in the mockups:**
- They use "IFF Mode-4 spoofing", "CIWS", "DEFCON", "kinetic shield", "RF jammer cone" and a 5-category rubric (Detection, Classification/IFF, Engagement, Swarm countermeasure, Composure).
- The PRD instead uses 5 classes (Recon quadcopter, Armed loitering drone, Decoy/balloon, Bird, Friendly), 5 responses (Track, Report, Jam, Intercept, Take cover) and 3 weighted metrics.
- Screen 3 shows **physiological telemetry** (heart rate, GSR "cognitive load", eye tunnelling). That is in no plan and can't be backed by real data.

**Present but not in the plan:** Unity script, WebSocket relay, `simulate.js`, `stitch_ui/convert.js` and its 6 broken outputs, the Flight Inspector screen. Roster and Readiness Matrix are close to the AVD's "Trainee progress" and "Unit overview" views.

**Expected but missing:** everything in the AVD's Flask/Three.js/SQLite design. See Step 4.

---

## Step 3: What actually runs

### Install

| Command | Result |
|---|---|
| `ls requirements.txt` | `No such file or directory` |
| `python3 --version` | `Python 3.14.6` |
| `python3 -c "import flask"` | `ModuleNotFoundError: No module named 'flask'` |
| `python3 -m pytest --version` | `No module named pytest` |
| `cd backend && npm ls --depth=0` | exit 0: cors@2.8.6, dotenv@18.0.5, express@5.2.1, ws@8.22.0 |
| `cd frontend && npm ls --depth=0` | exit 0: all 15 deps resolved (react 19.3.0, vite 8.3.3, typescript 6.0.3, tailwindcss 4.3.3 …) |
| `git rev-parse --is-inside-work-tree` | `fatal: not a git repository` |

I didn't run a fresh `npm ci` because `node_modules` was already present and you asked me not to install.

### Start

**Ports 3001 and 5173 were already in use** by `node index.js` (PID 50151, started 13:42) and `vite` (PID 51001, started 14:22), probably left by Antigravity. I left them running and used spare ports.

| Command | Output |
|---|---|
| `PORT=3901 node backend/index.js` | `Backend Server running on port 3901` / `WebSocket server listening on ws://localhost:3901`. No warnings. (Default port 3001.) |
| `cd frontend && npx vite --port 5901 --strictPort` | `VITE v8.3.3 ready in 122 ms`, `Local: http://localhost:5901/`. No warnings. (Default port 5173.) |

### AVD endpoints (all against port 3901)

| Request | Status | Sample |
|---|---|---|
| `GET /api/scenarios` | **404** | `Cannot GET /api/scenarios` |
| `GET /api/scenario?seed=42` | **404** | `Cannot GET /api/scenario` |
| `GET /api/rubric` | **404** | `Cannot GET /api/rubric` |
| `GET /api/trainees` | **404** | `Cannot GET /api/trainees` |
| `GET /api/sessions` | **404** | `Cannot GET /api/sessions` |
| `POST /api/sessions` | **404** | `Cannot POST /api/sessions` |
| `GET /api/analytics/summary` | **404** | `Cannot GET /api/analytics/summary` (`/trainee/<id>` and `/unit/<unit>` don't exist either: there is no `/api/analytics` route at all) |
| `GET /` | **404** | `Cannot GET /` (the backend serves no pages) |
| `GET /api/status` (not in AVD) | **200** | `{"status":"running","sessionState":{"activeSession":true,"traineeName":"John Doe (Unit A)","timeElapsed":0,"baseHealth":100,"events":[],"metrics":{"detectionTime":0,"classificationAccuracy":100,"engagementScore":"Pending"},"drones":[]}}` |

### WebSocket relay (scratch script, two clients A and B)

A sent `SIMULATION_UPDATE`, `NEW_EVENT`, `INSTRUCTOR_COMMAND`, the string `not json`, and `{"type":"SIMULATION_UPDATE"}` with no payload.

- B received `['INIT_STATE','SIMULATION_UPDATE','NEW_EVENT','INSTRUCTOR_COMMAND']`, and `/api/status` then reflected the drone and the event.
- The malformed inputs logged `SyntaxError: Unexpected token 'o'` and `TypeError: Cannot read properties of undefined (reading 'drones')` at `backend/index.js:49`. Both were caught; **the server did not crash**.
- **No frontend code connects to it.** Grepping `frontend/src` and all six mockups for `WebSocket|fetch(|localhost|XMLHttpRequest` found 0 hits.

### Tests, type-check, lint, build

| Command | Result |
|---|---|
| `cd backend && npm test` | `Error: no test specified` (exit 1). **0 tests** |
| `find` for `*.test.*`, `*.spec.*`, `test_*`, `tests/` | none. **Pass 0 / fail 0 / error 0** |
| `cd frontend && npx tsc -p tsconfig.app.json --noEmit` (the `tsc` half of `npm run build`) | **FAIL, 20 errors**, all in the six converted screens, e.g. `src/LiveDashboard.tsx(6,5217): error TS17002: Expected corresponding JSX closing tag for 'a'.` |
| `cd frontend && npx oxlint` | the same parse errors in 6 files, plus `App.tsx:19:46 warning no-unused-vars '_'` |
| `npx vite build --outDir <scratch>` (skips `tsc`) | OK in 198 ms: 220.58 kB JS, 26.84 kB CSS. Works only because `App.tsx` never imports the broken files |

**`npm run build` therefore fails as configured.**

### Browser check (Playwright not available)

Playwright isn't installed (no CLI, no `ms-playwright` cache, no Python module). I used the **Google Chrome already installed, in headless mode** (`--screenshot`, `--enable-logging=stderr`). Screenshots are in the session scratchpad `…/scratchpad/shots/`, which is temporary; I can copy them to `docs/` on request.

There is **no simulator page**. The closest thing is screen 1, a static 2D radar mockup. The dashboard pages are the static screens 3–5.

| Screenshot | Page | Console errors |
|---|---|---|
| `app-shell.png` | `/` React shell + Live Dashboard iframe | Tailwind CDN "should not be used in production" warning only |
| `screen1.png` | Live Dashboard: static radar, 3 hard-coded targets | none |
| `screen2.png` | Scenario Builder | CDN warning |
| `screen3.png` | AAR Reports: hard-coded 82.4 / B+, timeline, event log, physiological panel | CDN warning |
| `screen4.png` | Unit Roster | CDN warning |
| `screen5.png` | Readiness Matrix | CDN warning |
| `screen6.png` | Flight Inspector | **`Uncaught ReferenceError: elIffBenchmark is not defined`** at `frontend/public/stitch/screen6.html:1292` (the variable is declared as `elIffBench`) |

### Offline check

Chrome was run with external DNS blocked (`--host-resolver-rules="MAP * ~NOTFOUND, EXCLUDE localhost"`). `screen1-offline.png` and `screen4-offline.png` render as **unstyled black-on-white HTML**, with icon ligature names printed as raw text ("grid_view", "volume_up"). Console: `Uncaught ReferenceError: tailwind is not defined`.

Every runtime external URL:

| URL | Where |
|---|---|
| `https://cdn.tailwindcss.com` | `frontend/public/stitch/screen1-5.html` line 4 (same in `stitch_ui/`) |
| `https://cdn.tailwindcss.com?plugins=forms,container-queries` | `frontend/public/stitch/screen6.html` |
| `https://fonts.googleapis.com` (preconnect) | all 6 screens |
| `https://fonts.gstatic.com` (preconnect) | all 6 screens |
| `https://fonts.googleapis.com/css2?family=Inter…&family=Space+Mono…` | all 6 screens |
| `https://fonts.googleapis.com/css2?family=Material+Symbols+Outlined…` (2 variants) | all 6 screens |
| `ws://localhost:3001` | `backend/simulate.js:3`, `unity_integration/TelemetryManager.cs:40` (local only, OK) |

`frontend/src`, `frontend/index.html` and `backend/*` have no external URLs.

### Determinism check: not possible
`GET /api/scenario?seed=42` → 404 on both calls. There is no seeded generator anywhere; the only randomness is `Math.random()` in `backend/simulate.js:29`.

### Hand-made event log scoring: not possible
`POST /api/sessions` with `{"events":[{"t":3.2,"type":"detect","contact":"c1"}]}` → **404**. The only score fields are constants that nothing updates: `backend/index.js:23-25` (`detectionTime: 0`, `classificationAccuracy: 100`, `engagementScore: 'Pending'`). There are no tree paths or reasons.

---

## Step 4: Requirement map

### 4a. F1–F21

| ID | Requirement | Status | Evidence | Gap or note |
|---|---|---|---|---|
| F1 | 3D first-person OP view, terrain, sky, day/dusk/night lighting | Missing | No Three.js or any 3D code; `find` shows no renderer. Screen 1 is a static 2D SVG (`screen1.png`) | Core of milestone 1 |
| F2 | EO, night-vision and thermal sensor modes | Missing | No sensor-mode code (keyword grep over backend, Unity script, `App.tsx`) | |
| F3 | Degraded sensors: noise, reduced range, radar dropout, fog | Missing | Only `TelemetryManager.cs:164-169` logs "Toggling Jamming" | C# not compiled; no Unity project |
| F4 | Radar display with tracks carrying latency and noise | Missing | Screen 1 radar is a static SVG with hard-coded labels (`screen1.png`); no track logic | Usable as visual reference |
| F5 | Look, zoom, mark, classify, respond by mouse and keyboard | Missing | No input handling; the mockup buttons do nothing, and no `mark`/`classify`/`respond` events exist | |
| F6 | Distinct quadcopter, fixed-wing, balloon, bird, friendly | Missing | `simulate.js:17` sends `drones: []`; no models | |
| F7 | Swarms: shared goals, formation offsets, avoidance | Missing | No swarm code | |
| F8 | Audio cues + mute (Should) | Missing | No audio files or code | |
| F9 | VR/WebXR seam (Could) | Missing | Nothing. The Unity stub is a separate client, not a seam in a browser renderer | |
| F10 | Six scripted scenarios with objectives | Missing | `GET /api/scenarios` → 404 | |
| F11 | Seeded procedural generation, same seed = same scenario | Missing | `GET /api/scenario?seed=42` → 404; no PRNG | |
| F12 | Difficulty 1–5 (Should) | Missing | No generator. Screen 2 has a static difficulty control (`screen2.png`) | |
| F13 | Decision-tree scoring of detection, classification, engagement | Missing | `backend/index.js:23-25` constants only; `POST /api/sessions` → 404 | |
| F14 | Tree path and reason for every score change | Missing | Same as F13 | AAR mockup shows invented reasons as static text |
| F15 | Penalties: false alarm, missed, engaging friendly/benign, breach | Missing | Same as F13 | |
| F16 | Editable rubric file (Should) | Missing | No `rubric.json`; `GET /api/rubric` → 404 | |
| F17 | Store every session and event log in a local DB | Missing | In-memory only (`backend/index.js:16`), events capped at 50 (`:64`), lost on restart; no SQLite | |
| F18 | Per-trainee history and trends | Missing | `GET /api/sessions` → 404. Screens 4 and 6 are static (`screen4.png`, `screen6.png`) | |
| F19 | Unit rollup, weakest skill, weakest trainees | Missing | No analytics route. Screen 5 is static (`screen5.png`) | |
| F20 | Session replay timeline with events in order and scores (Should) | Partial | **Works:** the backend keeps received events in order (newest first, last 50) and returns them from `/api/status`, verified by the WS test. **Doesn't:** no scores, no persistence, no per-session separation; the AAR timeline in `screen3.png` is static and never reads them | |
| F21 | CSV export (Could) | Missing | Screen 3 has a "TELEMETRY CSV" button with no handler | |

**Totals: 0 Verified · 1 Partial · 0 Present, unverified · 20 Missing · 0 Broken.**

### 4b. Non-functional requirements (PRD)

| Category | Status | Evidence |
|---|---|---|
| Hardware (browser only, no engine install) | Missing | The only simulator code targets Unity, which needs an engine install |
| Performance (30 fps, 12 drones; load < 5 s) | Missing | No renderer to measure. The mockups took > 20 s to settle in headless Chrome on a first run (screens 3 and 5) because of CDN Tailwind's in-browser compile |
| Offline | **Violated (verified)** | `screen1-offline.png`, `tailwind is not defined` |
| Determinism | Missing | No generator |
| Explainability | Missing | No scoring |
| Configurability (rubric JSON) | Missing | No `rubric.json` |
| Accessibility | Not met | See Step 5 |
| Data handling (SQLite, callsign only) | Missing | No DB. Mockups use names and ranks ("LT. J. MILLER", "MAJ. VANCE") rather than callsigns |
| Reliability | Partial | A malformed WS message doesn't crash the server (verified), but every session is lost on restart |
| Maintainability (separate modules, tests) | Missing | 0 tests; no generator or scoring modules |

### 4c. Scoring rules (AVD "Scoring engine")

**No scoring code exists.** Evidence: `backend/index.js:23-25` are constants that nothing changes. A grep for `score|grade|rubric|classif|decision` over the backend and the Unity script finds only those constants. `POST /api/sessions` → 404. Every rule is therefore **Missing**. The AAR mockup (`screen3.png`) shows a *different* scheme, which is useful to know before anyone wires it up.

| Rule (AVD) | Status | What the mockup shows instead |
|---|---|---|
| Detection tiers: missed 0; 100/75/40/10% at 0.5×/1×/2× par | Missing | "94% [EXCEEDS SPEC]", avg latency 2.1 s vs 3.5 s standard |
| Classification: exact 100%, same family 50%, wrong family 0, hostile-called-benign/friendly = critical | Missing | "68%", "1 Critical Misclassification" (static) |
| Engagement, hostile: correct + timely + works 100% | Missing | "84% [PROFICIENT]" |
| Engagement, hostile: correct choice, failed roll 60% | Missing | n/a |
| Engagement, hostile: late or unsuitable 20% | Missing | n/a |
| Engagement, hostile: none or breach 0 | Missing | n/a |
| Engagement, benign: restraint 100%, unnecessary engagement 0 | Missing | n/a |
| Engagement: friendly engaged = critical | Missing | n/a |
| Only hostiles must be detected; others scored only if marked | Missing | n/a |
| False alarm −2 each, max −10 | Missing | n/a |
| Breach −10 each | Missing | "−12 PTS perimeter leak" (different value) |
| Critical −25 each | Missing | "−25 PTS" on an IFF misidentification (matches the value, but static) |
| Weights 30/30/40 from `rubric.json` | Missing | 5 categories, no weights shown, plus "Swarm countermeasure" and "Composure" |
| Clamp 0–100 | Missing | n/a |
| Grade bands | Missing | "B+ / QUALIFIED" static text; the bands aren't defined in the AVD either (to decide) |

Note for the build: the AVD says the total maps "to a grade band" but never defines the bands. Decide them when you write `rubric.json`.

---

## Step 5: Risks and differences (most threatening to the demo first)

### 1. Broken or crashing
1. **There is no runnable product loop.** No scenario can be played, scored or stored. Against the PRD's own warning, the project "only looks good in screenshots".
2. **`npm run build` fails** with 20 TS errors in the six unused converted `.tsx` files.
3. **Screen 6 runtime error** `elIffBenchmark is not defined` (`frontend/public/stitch/screen6.html:1292`).
4. **Stray processes on 3001/5173** (PIDs 50151, 51001). A fresh start gets `EADDRINUSE`, or Vite moves to another port.

### 2. Hard-constraint violations
5. **Offline: violated.** CDN Tailwind plus Google Fonts and Material Symbols; offline, every screen is unstyled (`screen1-offline.png`). The VD also requires system fonts.
6. **Server owns the score: not met.** There is no score, and the displayed scores are hard-coded HTML. The Unity design has the client run "Local Scoring" (from Antigravity's AVD), which contradicts your AVD.
7. **Determinism: not met.** No seeded generator.
8. **No real weapon modelling: borderline in the mockups.** No weapon code exists, but the mockup vocabulary ("CIWS", "kinetic", "kinetic penetrator", "DEFCON", "IFF Mode-4") reads like a weapons and C2 system. The PRD asks for abstract responses (Track/Report/Jam/Intercept/Take cover) and "a decision-training aid, not a weapons simulator". The physiological panel is an unbacked realism claim, one of the PRD's listed risks.
9. **Personal data:** mockups use names and ranks. The PRD says callsign and unit only.

### 3. Differences from the AVD to decide on
| Topic | Existing | AVD | Recommendation |
|---|---|---|---|
| Backend | Node/Express + ws | Flask + SQLite | **Switch to Flask.** Only ~100 lines of Node exist, and the AVD, kickoff prompt and checklist all assume Python and pytest. Keeping Node would mean rewriting all three docs |
| Simulator | Unity stub | Three.js in the browser | **Follow the AVD.** No Unity project exists, the PRD defers VR, and "no engine install" is a hardware requirement |
| Frontend | React/Vite SPA with iframes | Flask-served pages with vendored JS | **Your call.** Vite *can* bundle everything offline, but it adds a Node build step and a second toolchain. Simplest: plain pages served by Flask, as the AVD says. If you keep Vite, record it in the AVD |
| Live push | WebSocket relay | POST the event log at session end | Follow the AVD. The WS relay isn't needed (the PRD has no live instructor view; multiplayer and networked instructor control are non-goals) |
| Charts | recharts installed, unused | Chart.js vendored | Follow the AVD |
| Visual style | Stitch: Inter/Space Mono, `#121316`/`#00FF66` neon, 9–11 px labels | System fonts, VD tokens, 14 px minimum | Treat the mockups as layout inspiration only, and restyle to the VD tokens |
| Screens | 6 (incl. Flight Inspector) | Simulator HUD + 4 dashboard views | Map: screen1 → HUD radar panel, screen3 → Session review, screen4 → Trainee progress, screen5 → Unit overview. Drop screen6 unless it earns its place |
| Unity script | `unity_integration/` | not in plan | Park it (see C-tier) |

### 4. Performance concerns visible now
- `backend/index.js:53-57` re-serializes the **whole** state, including 50 events, once per client on every update (5 Hz × clients). This is moot if you move to the AVD design.
- `backend/index.js:62` uses an `events.unshift` array capped at 50. The cap throws history away, which conflicts with F17 and F20.
- The CDN Tailwind JIT compiles in the browser on every page load. Screen 6 is 97 KB of inline markup and handlers. These are slow first loads, against the PRD's "< 5 s load".
- Draw calls, per-frame allocations and swarm arrays: nothing to assess yet (no renderer). When building, watch for allocating `Vector3`s in the 30 Hz tick and an event log that grows without bound in long sessions. Validate its size server-side, as the AVD already says.

### 5. Accessibility gaps against the Visual Design doc
- **Text under 14 px is the default.** The mockup tokens are `label-sm` = **9 px** and `label-md`/`body-sm` = **11 px** (Tailwind config, `screen1.html` line 4). Uses of the 9 px token: screen1 79, screen2 110, screen3 78, screen4 83, screen5 116, screen6 223. The VD floor is 14 px for body text and 12 px only for non-essential captions.
- **Colour-only signals.** Radar contacts are all red or amber diamonds; hostile vs unknown is colour only. The VD requires red triangle HOSTILE / amber diamond UNKNOWN / blue circle FRIENDLY / grey square BENIGN.
- **No keyboard path.** The mockups have no hot keys. Screen6 uses 37 `onclick` handlers (focusability unchecked). `aria-` attributes: 1 each on screens 1, 3 and 4; 0 on screens 2, 5 and 6. Icon fonts are read aloud as ligature names.
- **Missing table views.** Charts and radar have no table equivalent. Only screens 4, 5 and 6 contain a `<table>`.
- **No light theme.** The VD wants the dashboard to follow the light/dark preference; the mockups are dark only.
- **Reduced motion** is not handled (`animate-pulse` is used on the badges).

---

## Step 6: What is left

Sizes: S = under half a day, M = 1–2 days, L = 3+ days. The PRD's walking-skeleton-first order is followed, so there is always a demo.

### Must have (F1–F7, F10, F11, F13–F15, F17–F19)
| # | What | Files | Size |
|---|---|---|---|
| M0 | **Decide keep vs switch** for backend, frontend and visual style (Step 5 §3), and record the decision in the AVD | `docs/AVD.md` | S |
| M1 | `git init` + first commit. Stop the stray servers. Move the Node, React and Unity code into an `archive/` folder (or a branch) so it stays available as reference without getting in the way | root | S |
| M2 | Flask skeleton: `requirements.txt` (Flask, pytest; needs your OK to install), app factory, serves `/sim` and `/dashboard`, SQLite schema for trainees/sessions/events, `GET /api/trainees`, POST callsign | `app/__init__.py`, `app/db.py`, `schema.sql`, `requirements.txt` | S–M |
| M3 | Vendor **Three.js** and **Chart.js** into `static/vendor/`, use system fonts, and add a test that greps templates and static files for `http(s)://` | `static/vendor/`, `tests/test_offline.py` | S |
| M4 | **Scenario generator** (seeded `random.Random(seed)`), JSON per the AVD schema, scripted scenario 1, `GET /api/scenarios`, `GET /api/scenario`. Determinism tests | `app/scenario.py`, `app/scenarios/*.json`, `tests/test_scenario.py` | M |
| M5 | **Scoring engine** as a pure function + `rubric.json` (30/30/40, tiers, penalties, clamp; you to decide grade bands) + `GET /api/rubric`. A pytest per tree branch | `app/scoring.py`, `rubric.json`, `tests/test_scoring.py` | M–L |
| M6 | `POST /api/sessions` (validate → score → store → return paths), `GET /api/sessions`, `GET /api/sessions/<id>`. API tests incl. bad input | `app/api.py`, `tests/test_api.py` | M |
| M7 | **Walking-skeleton simulator:** Three.js scene with a flat ground and sky, one quadcopter flying its waypoints, mouse look, click to mark, keys 1–5 to classify and T/R/J/I/C to respond, breach at the inner ring, POST the log, show the score screen with reasons | `templates/sim.html`, `static/sim/*.js` | L |
| M8 | Remaining scripted scenarios 2–6 + procedural parameters | `app/scenarios/`, `app/scenario.py` | M |
| M9 | Six contact models with distinct silhouettes and motion; swarm leader-follow + separation | `static/sim/contacts.js`, `swarm.js` | M–L |
| M10 | Sensor modes (EO/dusk/NV/thermal via CSS filters) + degradation levels 0–3 + radar panel with noise/latency/dropout | `static/sim/sensors.js`, `radar.js` | M |
| M11 | Terrain: rural height field + urban blocks from `terrain_seed`; day/dusk/night sky | `static/sim/terrain.js` | M |
| M12 | Analytics endpoints + dashboard: trainee trends (rolling mean of 3), confusion matrix, unit rollup with weakest skill and trainees, session table. Restyle from mockups 3/4/5 using VD tokens | `app/analytics.py`, `templates/dashboard.html`, `static/dash/*.js`, `tests/test_analytics.py` | L |

### Should have (F8, F12, F16, F20)
| # | What | Files | Size |
|---|---|---|---|
| S1 | Difficulty 1–5 slider driving the AVD table | `app/scenario.py`, scenario picker UI | S |
| S2 | Rubric editable without code (F16), mostly done by M5. Add reload-on-change and a note in the README | `rubric.json`, `app/scoring.py` | S |
| S3 | Session review timeline with per-event points (F20) | dashboard session view | M |
| S4 | Audio cues + mute (F8), using bundled audio or WebAudio-generated tones | `static/sim/audio.js` | S–M |
| S5 | Accessibility pass: 14 px, threat shapes and labels, keyboard path (Tab cycles contacts), focus rings, chart table views, reduced motion, light theme | all templates/CSS | M |
| S6 | Playwright smoke test (needs your OK to install) + fps counter | `tests/e2e/`, `static/sim/fps.js` | S–M |
| S7 | Seeded demo cohort script (several trainees × 3+ sessions) | `scripts/seed_demo.py` | S |

### Could have (F9, F21)
| # | What | Files | Size |
|---|---|---|---|
| C1 | CSV export of session or unit (F21) | `app/api.py` | S |
| C2 | Keep the render layer behind an interface so a WebXR renderer can swap in (F9) | `static/sim/renderer.js` | S if done during M7 |
| C3 | Unity/VR client reusing `TelemetryManager.cs` ideas against the Flask API | `archive/unity_integration` | L |

### If you decide to keep the current Node/React stack instead
Do M1 then these cheap fixes first, and the demo still looks the same:
- (a) exclude or delete the six broken `.tsx` files so `npm run build` passes (S);
- (b) fix the screen6 typo `elIffBenchmark` → `elIffBench` (S);
- (c) compile Tailwind locally with the already installed `@tailwindcss/vite` and self-host the fonts (M).

M4–M12 still apply, just written in JS. You would also need to rewrite the AVD, kickoff prompt and checklist away from Flask/pytest.

### Recommended order (a working demo after every step)
1. **M0, M1** (decisions + git; the current mockups stay viewable from `archive/` as a fallback).
2. **M2 → M3** (Flask serves an empty sim page and dashboard, offline from day one).
3. **M4 → M5 → M6** (scenario, scoring and storage, each demoable with `curl` and covered by pytest). The scoring engine is the cheapest way to make F13–F15 real.
4. **M7** (walking skeleton: PRD milestone 1 complete, end to end).
5. **M12 minimal** (trainee history + session review reading real data) → F17–F19 visible.
6. **M8, M10, M11, M9** (scenario depth, milestone 2).
7. Should-haves, **S5 and S7 first** (judges will see them), then **S6**, then the rest.

---

## Needs a human check

1. **Stack decision (M0).** Read Step 5 §3 and choose: switch to the AVD stack (recommended) or keep Node/React and update the docs.
2. **Stray servers.** Run `lsof -iTCP:3001 -iTCP:5173 -sTCP:LISTEN`; if you didn't start them on purpose, `kill 50151 51001`.
3. **Mockup look.** Run `cd frontend && npm run dev`, open http://localhost:5173 and click all six tabs. Decide which layouts are worth carrying over.
4. **Offline yourself.** Turn Wi-Fi off and hard-reload a tab to see the unstyled page.
5. **Colour-only signals.** On Live Dashboard, turn on macOS greyscale (Settings → Accessibility → Display → Colour filters). Can you tell hostile from unknown?
6. **Keyboard.** Tab through any screen. Is every control reachable, and is focus visible?
7. **Unity script.** I can't compile C# here. Only relevant if you keep a Unity track.
8. **PRD open questions** (CHECKLIST "Before building"): demo format and internet, VR expected or not, an official ROE reference, who plays the instructor.

## CHECKLIST.md

`docs/CHECKLIST.md` was copied from `~/Downloads` unchanged. **No boxes were ticked**, because none of its 81 items was verified in Step 3:
- There is no git repo.
- Python 3.14 is present, but Flask and pytest are not.
- Three.js and Chart.js are not vendored.
- No Flask app, schema, generator, rubric, scoring, simulator, scenario or dashboard item exists.
- No quality gate passes. The offline gate was tested and failed.

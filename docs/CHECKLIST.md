# SIH26247 Drone Threat Trainer: Build and Submission Checklist

Oct 6, 2026 · Ammar Hashmi

## Before building

Settle these first, because each one changes what gets built. The first four match the open questions in the PRD.

- [ ] Confirm the date and format of the final demo: own laptop or projector, internet available or not
- [ ] Confirm whether a VR demonstration is expected, or desktop is enough
- [ ] Find any official reference for threat classes and rules of engagement to align the rubric with
- [ ] Decide who plays the instructor during the demo
- [ ] Confirm the team and who owns the simulator, backend and dashboard
- [ ] Pick the demo laptop and note its GPU and browser
- [x] Create the project folder and a Git repository with a first commit
- [x] Install Python 3.10 or newer, Flask and pytest
- [x] Copy Three.js and Chart.js into the static folder so nothing loads from the internet
- [ ] Read the PRD, AVD and Visual Design docs once as a team and note any disagreements

## Backend and data

These cover requirements F11 to F17 and the API in the AVD.

- [x] Flask app starts and serves the simulator and dashboard pages
- [x] SQLite schema created for trainees, sessions and events
- [x] Scenario generator produces valid JSON from a seed and parameters
- [x] The same seed returns an identical scenario (checked by a test)
- [x] Difficulty 1 to 5 sets hostile count, swarm size, decoys, degradation and speed as in the AVD table
- [x] `rubric.json` holds weights, thresholds, penalties, expected responses and effectiveness values
- [x] Scoring engine returns per-contact tree paths, reasons and points
- [x] Session totals apply weights, penalties, clamping and grade bands
- [x] `POST /api/sessions` validates, scores and stores a submitted event log
- [x] `GET /api/sessions` and `/api/sessions/<id>` return history and detail
- [x] Trainee and unit analytics endpoints return trends, confusion matrix and weakest skill
- [x] Bad input is rejected with a clear error and never corrupts the database

## Simulator

These cover requirements F1 to F9. Build the walking skeleton first: one contact that can be marked, classified and answered.

- [x] 3D scene renders with sky, lighting and terrain for day, dusk and night
- [x] Rural terrain from a seeded height field and urban terrain from seeded blocks
- [x] Look, zoom, mark, classify and respond controls work by mouse and keyboard
- [x] Contacts fly their waypoint paths with seeded wobble
- [x] All six contact types render with distinct silhouettes and motion
- [x] Swarm members follow a leader with formation offsets and separation
- [x] Day, night vision and thermal modes are clearly different, and switching takes under a second
- [x] Four degradation levels change noise, fog, visible range and radar dropout
- [x] Radar shows tracks with latency and noise, and never reveals the true class
- [x] Marking empty sky logs a false alarm
- [x] A contact reaching the inner ring logs a breach
- [x] Responses apply their effectiveness roll using the scenario's seeded generator
- [x] Every action is stamped with scenario time and added to the event log
- [x] The finished session is submitted to the server and the score screen shows the tree reasons
- [ ] Audio cues and a mute button (should have)
- [x] Frame rate counter shows at least 30 fps with a 12-drone swarm

## Scenarios

These cover requirements F10 to F12. Each scripted scenario should be played end to end once before it is ticked.

- [x] Scenario 1, Dawn Recon Pass, plays through and scores correctly
- [x] Scenario 2, Night Loitering Drone, shows that jamming is weak against it
- [x] Scenario 3, Urban Canyon, gives a short detection window behind buildings
- [x] Scenario 4, Mixed Traffic, punishes engaging birds or the friendly aircraft
- [x] Scenario 5, Fog and Noise, forces reliance on radar and cues
- [x] Scenario 6, Saturation Swarm, overloads the trainee with eight drones and two decoys
- [x] Each scripted scenario shows its learning objective on the start screen
- [x] The instructor can set time of day, terrain, threat mix, swarm size, degradation and seed
- [x] Difficulty slider changes all the linked knobs together
- [x] A seed shown on the score screen can be reused to replay the same scenario

## AAR dashboard

These cover requirements F17 to F21 and the layout in the Visual Design doc.

- [x] Unit and trainee pickers sit in one row above the charts
- [x] Four summary tiles: sessions, average score, weakest skill, breaches
- [x] Progress line chart with detection, classification and engagement, direct labels and a legend
- [x] Chart colours match the validated palette, and blue always means detection
- [x] Unit comparison bars sorted by score
- [x] Confusion matrix of true class against chosen class
- [x] Sortable session table with a link to each session review
- [x] Session review shows the event timeline with decision paths, reasons and points
- [x] Every chart has hover details and a table view
- [ ] Light and dark themes both read correctly
- [x] CSV export of a session or unit report (could have)

## Quality gates

Nothing should be called done until these pass on the demo laptop.

- [x] Generator tests pass: same seed identical, different seeds differ, every difficulty respects its table
- [x] Scoring tests pass for every branch: missed, slow, fast, wrong family, friendly engaged, restraint, breach, false alarms
- [x] API tests pass: submit, read back, analytics shapes, bad input rejected
- [x] Browser smoke test loads the simulator with no console errors and saves a session
- [x] The whole system works with Wi-Fi switched off
- [ ] The simulator holds 30 fps or better with a 12-drone swarm on the demo laptop
- [ ] Launch to first scenario takes under 60 seconds from a clean start
- [x] Every score change shows a decision-tree reason
- [x] Keyboard-only run through a full scenario works
- [ ] Text is at least 14 px and focus rings are visible
- [ ] Threat state never relies on colour alone
- [x] Reduced-motion setting is respected

## Demo and submission

- [x] Seed a demo cohort of trainees with several sessions each so the dashboard shows real trends
- [x] Write a three to five minute walkthrough script: scenario, decision, score, dashboard
- [ ] Rehearse the demo twice from a clean start, including one deliberate mistake to show the tree reason
- [ ] Prepare a fallback: a recorded screen capture in case the live demo fails
- [x] Write the README with install and run steps, folder layout and how to edit the rubric
- [x] State assumptions and limits plainly: public-source rubric, abstract responses, no real weapon modelling
- [x] Map each of the three required outcomes in the problem statement to where it appears in the demo
- [ ] Package the project folder and test it on a second machine
- [ ] Re-read the problem statement one last time and tick off each outcome
- [ ] Submit through the SIH portal and keep a copy of the confirmation

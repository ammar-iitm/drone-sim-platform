# SIH26247 Drone Threat Trainer: Product Requirements (PRD)

Oct 6, 2026 · Ammar Hashmi

## Overview

SIH problem statement 26247 asks for a software simulator that trains unit-level personnel to recognise, classify and respond to drone and swarm threats, because classroom teaching and live-fire drills are costly, weather-dependent and too scarce to give troops enough repetitions.

The Drone Threat Trainer answers it with three parts: a browser-based 3D simulator that runs on an ordinary laptop with no internet, a Flask backend that scores every session with an explainable decision tree, and an after-action review (AAR) dashboard that tracks individuals and units across repeated sessions.

For the hackathon, done means:

1. A trainee can run six scripted scenarios and an unlimited number of procedurally generated ones, covering day and night, degraded sensors, urban and rural terrain, single drones and swarms.
2. Every session is scored on detection time, threat classification accuracy and engagement decisions.
3. The dashboard shows each trainee's and each unit's progress over repeated sessions.
4. All of it runs offline on a standard laptop with no specialised hardware.

## Goals and non-goals

The product succeeds if one runnable demo covers every outcome the problem statement lists, and fails if it only looks good in screenshots.

**Goals**

- Deliver all three required outcomes in one demo: the simulator with scripted and procedural scenarios, decision-tree scoring, and the AAR dashboard.
- Let a trainee start a scenario within 60 seconds of launching the app, with no instructor setup beyond picking a scenario.
- Make scoring explainable: every point gained or lost traces to a named node in the decision tree.
- Hold at least 30 frames per second on an integrated-GPU laptop, and work fully offline.
- Show a visible trend across repeated sessions so the value of repetition is evident.

**Non-goals**

- No real weapon, ballistics or countermeasure modelling. Responses are abstract categories with configurable effectiveness.
- No classified doctrine. The scoring rubric is built from public principles and the instructor can edit it.
- No VR build in the first release, although the design keeps a clean seam for it.
- No multiplayer or networked instructor control.
- No integration with real sensors or command systems.

## Users and personas

Three people use the product, and the trainee's experience matters most because repetition only helps if sessions are quick and clear.

| Persona | Role | Job to be done | What they need from the product |
| --- | --- | --- | --- |
| Trainee | Sentry or air-defence operator at unit level | Spot a contact, decide what it is, choose a response, all under time pressure | A readable sensor view, simple controls, instant feedback, a way to repeat |
| Instructor | Trainer running a session block | Assign scenarios, see where each trainee goes wrong, adjust difficulty | Scenario picker with seed and difficulty control, per-trainee AAR, editable rubric |
| Unit commander | Officer responsible for readiness | Judge whether the unit is ready and which skill is weakest | Unit rollup, trends over time, weakest-skill view |

## User stories

Each story has an acceptance test that can be checked in the demo.

| ID | Story | Acceptance criteria |
| --- | --- | --- |
| U1 | As a trainee, I want to scan the sky through a sensor view and mark a contact when I spot it | Clicking a contact within the reticle logs a detection with a timestamp; marking empty sky logs a false alarm |
| U2 | As a trainee, I want to classify a marked contact | I can choose from Recon quadcopter, Armed loitering drone, Decoy or balloon, Bird, and Friendly aircraft; the choice is logged |
| U3 | As a trainee, I want to choose a response to a classified contact | I can choose Track only, Report, Jam, Intercept, or Take cover; the response takes effect and is logged |
| U4 | As a trainee, I want to switch sensor modes | Day, night vision and thermal modes change the view within one second; degraded modes visibly reduce clarity |
| U5 | As a trainee, I want immediate feedback after a session | A score screen shows detection, classification and engagement results with the decision-tree reason for each |
| U6 | As an instructor, I want to choose or generate a scenario | I can pick a scripted scenario, or set time of day, terrain, threat mix, swarm size, sensor degradation and a seed, and get the same scenario again from the same seed |
| U7 | As an instructor, I want to see a trainee's history | The dashboard lists every session for a trainee with scores and a trend line per metric |
| U8 | As an instructor, I want to adjust scoring weights | Changing the rubric file changes the next session's scoring without a code change |
| U9 | As a commander, I want a unit readiness view | The dashboard shows unit average per metric, the weakest skill and the weakest trainees |

## Functional requirements

These requirements map directly to the three outcomes in the problem statement, plus the supporting pieces needed to make them work.

| ID | Area | Requirement | Priority |
| --- | --- | --- | --- |
| F1 | Simulator | Render a first-person observation-post view in 3D with terrain, sky and lighting for day, dusk and night | Must |
| F2 | Simulator | Provide EO, night-vision and thermal sensor modes with a visible difference between them | Must |
| F3 | Simulator | Model degraded sensors: noise, reduced range, intermittent radar dropout, fog | Must |
| F4 | Simulator | Show a radar display with contact tracks that carry latency and noise | Must |
| F5 | Simulator | Support look, zoom, mark, classify and respond controls by mouse and keyboard | Must |
| F6 | Simulator | Render distinct threat classes: quadcopter, fixed-wing loitering drone, decoy balloon, bird, friendly aircraft | Must |
| F7 | Simulator | Model swarms with shared goals, formation offsets and simple avoidance | Must |
| F8 | Simulator | Give audio cues for rotor noise and alerts, with a mute control | Should |
| F9 | Simulator | Keep a clean input and scene seam so a VR or WebXR mode can be added later | Could |
| F10 | Scenarios | Ship six scripted scenarios with stated learning objectives | Must |
| F11 | Scenarios | Generate scenarios procedurally from a seed and parameters; the same seed gives the same scenario | Must |
| F12 | Scenarios | Offer a difficulty setting from 1 to 5 that changes speed, count, decoys and sensor degradation | Should |
| F13 | Scoring | Score detection time, classification accuracy and engagement decisions with a decision tree | Must |
| F14 | Scoring | Return the tree path and reason for every score change | Must |
| F15 | Scoring | Penalise false alarms, missed contacts, engaging friendly or benign contacts, and breaches | Must |
| F16 | Scoring | Load weights and thresholds from an editable rubric file | Should |
| F17 | AAR | Store every session and its event log in a local database | Must |
| F18 | AAR | Show per-trainee history and trends for each metric | Must |
| F19 | AAR | Show a unit rollup with the weakest skill and weakest trainees | Must |
| F20 | AAR | Provide a session replay timeline listing events in order with their scores | Should |
| F21 | AAR | Export a session or unit report as CSV | Could |

## Scenario catalogue

Six scripted scenarios each teach one skill, and the procedural generator mixes the same ingredients for endless variety.

| # | Scenario | Time and terrain | Threat | Sensor condition | Learning objective |
| --- | --- | --- | --- | --- | --- |
| 1 | Dawn Recon Pass | Dawn, rural | One small quadcopter | Clear | Basic detect, classify, report |
| 2 | Night Loitering Drone | Night, rural | One fixed-wing loitering drone | Night vision or thermal | Recognise an autonomous drone that jamming will not stop |
| 3 | Urban Canyon | Day, urban | One quadcopter appearing between buildings | Clear but occluded | Detect fast in a short window |
| 4 | Mixed Traffic | Day, rural | Three birds, one friendly aircraft, one hostile quadcopter | Clear | Restraint: do not engage benign or friendly contacts |
| 5 | Fog and Noise | Dusk, rural | Two quadcopters | Heavy noise, fog, radar dropout | Rely on radar and cues when the picture is poor |
| 6 | Saturation Swarm | Night, urban | Swarm of eight from two axes, plus two decoys | Thermal | Prioritise and triage under overload |

**Procedural parameters**

- Seed: any integer; the same seed always rebuilds the same scenario.
- Time of day: day, dusk or night.
- Terrain: rural or urban.
- Threat mix: counts of hostile, decoy, benign and friendly contacts.
- Swarm size: 0 to 12, with one or two approach axes.
- Sensor degradation: levels 0 to 3.
- Difficulty: 1 to 5, which scales speed, count, decoy ratio and degradation together.

## Non-functional requirements

The tool has to run where a unit actually trains: on a standard laptop, possibly with no network.

| Category | Requirement |
| --- | --- |
| Hardware | Runs on a laptop with an integrated GPU, 8 GB RAM and a current Chrome, Edge or Firefox; no installation of a game engine or GPU drivers beyond the browser |
| Performance | At least 30 fps at 1080p with a 12-drone swarm; scenario loads in under 5 seconds |
| Offline | All assets and libraries are bundled locally; nothing is fetched from the internet at run time |
| Determinism | The same seed and parameters always produce the same scenario |
| Explainability | Every score change records the decision-tree node and reason |
| Configurability | Rubric weights, thresholds and response effectiveness are edited in a JSON file, not in code |
| Accessibility | Colour is never the only signal; text is at least 14 px; all controls work by keyboard; palette is colour-blind safe |
| Data handling | Sessions are stored locally in SQLite; trainees are identified by callsign, with no personal data required |
| Reliability | A crash mid-session loses at most that session; the database is never corrupted |
| Maintainability | Scenario, scoring and rendering are separate modules with automated tests for generation and scoring |

## Success metrics

Every metric below can be checked by a person or a test before the demo.

| Metric | Target | How it is verified |
| --- | --- | --- |
| Required outcomes covered | 3 of 3 | Walk through the problem statement during the demo |
| Scripted scenarios playable | 6 of 6 | Run each once end to end |
| Frame rate with a 12-drone swarm | 30 fps or better | In-app fps counter on the demo laptop |
| Same seed gives same scenario | 100% | Automated test comparing generated scenario JSON |
| Score changes with a decision-tree reason | 100% | Automated test over recorded sessions |
| Time from launch to first scenario | 60 seconds or less | Stopwatch on a clean start |
| Works with network disabled | Yes | Run the demo with Wi-Fi off |
| Dashboard shows a trend | After 3 sessions per trainee | Seeded demo cohort plus a live session |

## Milestones and scope tiers

The build order puts the end-to-end loop first, so there is always a working demo, then adds depth.

1. **Walking skeleton:** one scenario flies, can be marked, classified and answered, and a score is saved and shown.
2. **Scenario depth:** all six scripted scenarios, the procedural generator and sensor modes.
3. **Scoring and AAR:** the full decision tree, the rubric file, and the dashboard with trends and unit rollup.
4. **Polish:** audio, replay timeline, accessibility pass, seeded demo data.
5. **Demo readiness:** test run offline on the demo laptop, README and a short walkthrough script.

| Tier | Scope |
| --- | --- |
| Must have | F1 to F7, F10, F11, F13 to F15, F17 to F19 |
| Should have | F8, F12, F16, F20 |
| Could have | F9 (VR seam) and F21 (CSV export) |

## Risks, assumptions and open questions

The biggest risk is that the simulator looks like a toy, so realism of behaviour and sensors gets the most attention.

| Risk | Impact | Mitigation |
| --- | --- | --- |
| Visuals look unconvincing to a defence audience | Lower credibility with judges | Invest in sensor effects, believable flight paths and a clean tactical HUD rather than detailed models |
| Scoring seen as arbitrary | Judges question the rubric | Show the tree path for every score, state assumptions, make the rubric editable |
| Scope too large for the time | Unfinished demo | Build the walking skeleton first and follow the tier order |
| Weak laptop GPU | Low frame rate | Low-poly scene, capped draw distance, a quality setting |
| Realism claims overreach | Loss of trust | Describe the tool as a decision-training aid, not a weapons simulator |

**Assumptions**

- The demo runs on a normal laptop, possibly without internet.
- Public information on drone types and counter-drone principles is enough for training-level realism.
- Instructors can supply or edit the rubric.

**Open questions**

- [ ] What are the date and format of the final demo (projector, own laptop, internet available)?
- [ ] Is a VR demonstration expected, or is desktop enough?
- [ ] Is there an official reference for classification categories and rules of engagement to align the rubric with?
- [ ] Who plays the instructor during the demo?

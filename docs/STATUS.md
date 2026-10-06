# Project Status: Drone Threat Trainer (SIH PS 26247)

**Date:** 2026-10-06 (updated after the build; replaces the morning audit, summarised under History)
**Yardstick:** `docs/PRD.md` (F1–F21), `docs/AVD.md`, `docs/VISUAL_DESIGN.md`, `docs/CHECKLIST.md`
**Stack:** as the AVD specifies (Flask, SQLite, Three.js 0.186.1, Chart.js 4.5.1, pytest, Playwright), with the UI in the Stitch "AEGIS" visual style.
**Evidence rule:** "Verified" means a test or screenshot from an actual run. Test names refer to `tests/`; screenshots are in `test-results/`.

## Summary

Of the 21 requirements: **18 Verified, 2 Partial, 1 Present but unverified, 0 Missing, 0 Broken.**
- **Partial:** F7 (swarm avoidance is fixed formation spacing plus a visual spread on engagement, not dynamic avoidance) and F9 (the VR seam is an isolated renderer module, not a WebXR mode).
- **Present but unverified:** F8 (audio cues are implemented, but sound cannot be checked in a headless browser).
- **Tests:** 136 automated tests pass. They cover the generator, every scoring branch, the API, the offline rule, JS/Python roll parity, and 22 browser tests that include all six scenarios played end to end.
- **Checklist:** 58 of 81 items are ticked.
- **What remains:** checks only a person can do on the demo laptop (Wi-Fi off, frame rate, hearing the audio, colour-blind review), five open decisions, and demo rehearsal.

## Requirement map

| ID | Requirement | Status | Evidence | Gap or note |
| --- | --- | --- | --- | --- |
| F1 | 3D observation-post view, terrain, sky, day/dusk/night | Verified | `test_smoke::test_play_score_and_review`, `03-sim-marked.png` (dusk), `10-sensor-*.png`; night and urban screenshots taken during the build | |
| F2 | EO, night vision, thermal, visibly different | Verified | `test_verification::test_sensor_modes_differ_and_switch_fast` (3 distinct filters and images, switch well under 1 s), `10-sensor-eo/nv/thermal.png` | |
| F3 | Degraded sensors: noise, reduced range, radar dropout, fog | Verified | `test_scenario::test_four_degradation_levels_match_visual_design_table`, `test_verification::test_four_degradation_levels_in_the_view`, `11-degradation-3.png` | |
| F4 | Radar with tracks that carry latency and noise | Verified | `test_verification::test_radar_latency_and_noise` (updates once per 2 s sweep, lags truth, error under 250 m), `test_smoke::test_radar_console_tracks_and_marking` (never shows class), `07-radar-console.png` | Full radar model: RCS-based detection, clutter, false returns, 2-of-3 track initiation |
| F5 | Look, zoom, mark, classify, respond by mouse and keyboard | Verified | `test_verification::test_look_and_zoom_by_mouse_and_keyboard`, `test_smoke::test_play_score_and_review` (mouse mark), `test_access::test_keyboard_only_run` | |
| F6 | Distinct quadcopter, hexacopter, fixed-wing, balloon, bird, friendly | Verified | `test_verification::test_contact_silhouettes` (6 distinct geometries), `12-silhouettes.png` | Motion cues (wobble, bird wing flap, friendly nav light) not separately tested |
| F7 | Swarms: shared goals, formation offsets, avoidance | Partial | **Works:** shared leader path and formation offsets (`test_scenario::test_scripted_catalogue_matches_prd`, `test_scenarios[s6]`). **Not dynamic:** 30 m formation spacing keeps members apart, and the group spreads 40 m when engaged (`app/static/js/sim/main.js`, visual only, no test) | Real separation steering is a possible upgrade |
| F8 | Audio cues and mute (Should) | Present, unverified | `app/static/js/sim/audio.js`: rotor hum by distance, mark tick, response chime, failure buzz, breach alarm; mute on **M** | Needs a person to listen |
| F9 | Clean seam for VR/WebXR (Could) | Partial | Rendering is isolated in `world.js`; game logic and input live in `main.js` | No WebXR mode, as the PRD states |
| F10 | Six scripted scenarios with objectives | Verified | `test_scenarios::test_scenario_plays_end_to_end` ×6, each checking its own learning objective | |
| F11 | Seeded procedural generation; same seed, same scenario | Verified | `test_scenario::test_same_seed_gives_identical_json` ×5, `test_api::test_procedural_via_api_is_deterministic`, `test_verification::test_instructor_settings_and_seed_reuse` | |
| F12 | Difficulty 1–5 (Should) | Verified | `test_scenario::test_difficulty_table_is_respected` (15 cases), mission page slider | |
| F13 | Decision-tree scoring of detection, classification, engagement | Verified | `tests/test_scoring.py` (43 tests) | |
| F14 | Tree path and reason for every score change | Verified | `test_scoring::test_every_scored_stage_has_reason_and_node`, `04-score.png`, `05-session.png` | |
| F15 | Penalties: false alarms, missed, friendly/benign engaged, breaches | Verified | `test_scoring` (false alarms capped, missed, friendly engaged, unnecessary engagement, breach), `test_verification::test_false_alarm_and_breach` | |
| F16 | Editable rubric file (Should) | Verified | `test_scoring::test_weights_come_from_rubric`; `api.rubric()` re-reads `rubric.json` on every request, so edits apply to the next session without a restart | |
| F17 | Store sessions and event logs locally | Verified | `test_api::test_submit_score_store_and_read_back`, `test_api::test_bad_input_rejected_and_database_untouched` (integrity check) | SQLite in `data/trainer.db` |
| F18 | Per-trainee history and trends | Verified | `test_api::test_analytics_shapes`, `test_verification::test_dashboard_sorting_tables_and_tooltips`, `06-dashboard.png` | |
| F19 | Unit rollup, weakest skill and trainees | Verified | `test_api::test_analytics_shapes`, `06-dashboard.png` | |
| F20 | Session replay timeline with scores (Should) | Verified | `05-session.png`, `test_smoke` opens the review page | Event list with points; no animated playback |
| F21 | CSV export (Could) | Verified | `test_api::test_csv_exports` (session and unit) | |

## Scoring rules (AVD)

| Rule | Status |
| --- | --- |
| Detection tiers 100/75/40/10% at 0.5×/1×/2× par; missed 0 | As written (`rubric.json` `detection_tiers`) |
| Classification exact 100, same family 50, wrong family 0; hostile called benign or friendly is critical | As written |
| Engagement, hostile: correct and effective 100, correct but failed roll 60, late or unsuitable 20, none or breach 0 | As written, with one interpretation: a correct, timely decision that fails its roll keeps 60% even if the drone then breaches (the AVD's "not punished for bad luck"); the −10 breach penalty still applies |
| Engagement, non-hostile: restraint 100, unnecessary 0, friendly engaged critical | As written |
| Only hostiles must be detected; others scored only if marked | As written |
| Penalties: false alarm 2 (cap 10), breach 10, critical 25 | As written |
| Weights 30/30/40 from `rubric.json`; clamp 0–100 | As written |
| Grade bands | AVD gives none; placeholder A ≥ 90, B ≥ 80, C ≥ 70, D ≥ 60, F (decision pending) |
| Server owns the score; rolls from the scenario seed | Implemented; browser and server rolls are bit-identical (`test_offline_and_parity::test_js_and_python_rolls_match`) |

## Hard constraints

| Constraint | Status | Evidence |
| --- | --- | --- |
| Offline | Met in tests | Every browser test blocks non-local requests: zero attempts recorded. `test_offline_and_parity::test_no_external_urls_in_pages_scripts_or_styles`. A real Wi-Fi-off run on the demo laptop is still a human check |
| Deterministic | Met | Generator tests; seed-reuse browser test |
| Server-owned scoring | Met | `api.submit_session` rebuilds the scenario and ignores any client score (`test_submit_score_store_and_read_back` sends `total: 100`) |
| No real weapon modelling | Met | Abstract responses with configurable effectiveness only |

## Open decisions

1. **Grade bands:** confirm A ≥ 90, B ≥ 80, C ≥ 70, D ≥ 60, or supply official bands.
2. **Rubric interpretations:** failed-roll-then-breach scores 60%; decoys are non-threats; "late" means within 300 m; suitable responses per model (jam or intercept for quadcopters and hexacopters, intercept only for fixed-wing).
3. **Theme:** the Visual Design doc asks for a light dashboard theme; the Stitch design is dark only. Currently dark only.
4. **Text size:** 12 px monospace captions are used for labels, table headers and readouts (allowed as captions by the Visual Design doc), and body text is 14 px. Confirm this, or move all data text to 14 px.
5. **Swarm counting:** swarm members are counted on top of the difficulty table's hostile count.

## Needs a human check

1. **On the demo laptop:** run `scripts/seed_demo.py --reset` and `run.py` with Wi-Fi off, play Saturation Swarm, and read the FPS chip (target 30 or more).
2. **Audio:** play any scenario with sound on. The rotor hum should rise as a drone closes in, and the chime, buzz and breach alarm should play on their events. Check that **M** mutes.
3. **Colour-blind review:** set macOS Display → Colour filters → Greyscale, then check that threat markers (triangle, diamond, circle, square, all with text labels) and the dashboard still read correctly.
4. **Urban Canyon feel:** the drone should be visible for about 4 s around T+37 s and again on final approach.
5. **Second machine:** clone the repo and follow the README.

## History: the morning audit

At 15:00 the project was an Antigravity prototype: six static Stitch HTML mockups in a React shell, a 100-line Express/WebSocket relay, and a Unity C# script with no Unity project. All 21 requirements were Missing or Partial, `npm run build` failed, and the UI did not work offline. That code is kept in `archive/`, and the Stitch screens remain the visual reference for the current UI.

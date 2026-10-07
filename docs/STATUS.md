# Project Status: Drone Threat Trainer (SIH PS 26247)

**Date:** 2026-10-06 (updated after the build; replaces the morning audit, summarised under History)
**Yardstick:** `docs/PRD.md` (F1–F21), `docs/AVD.md`, `docs/VISUAL_DESIGN.md`, `docs/CHECKLIST.md`
**Stack:** as the AVD specifies (Flask, SQLite, Three.js 0.186.1, Chart.js 4.5.1, pytest, Playwright), with the UI in the Stitch "AEGIS" visual style.
**Evidence rule:** "Verified" means a test or screenshot from an actual run. Test names refer to `tests/`; screenshots are in `test-results/`.

## Summary

Of the 21 requirements: **19 Verified, 2 Partial, 0 Present but unverified, 0 Missing, 0 Broken.**
- **Partial:** F8 (every audio cue, the distance-based hum and mute are verified by test, but nobody has listened yet) and F9 (the VR seam is an isolated renderer module, not a WebXR mode).
- **Tests:** 146 automated tests pass. They cover the generator, every scoring branch, the API, the offline rule, JS/Python roll parity, and 32 browser tests that include all six scenarios played end to end.
- **Checklist:** 66 of 81 items are ticked.
- **What remains:** checks only a person can do on the target laptop (frame rate with 12 drones, hearing the audio, colour-blind review, a second machine) and the open rubric interpretations. No demo is scheduled.

## Requirement map

| ID | Requirement | Status | Evidence | Gap or note |
| --- | --- | --- | --- | --- |
| F1 | 3D observation-post view, terrain, sky, day/dusk/night | Verified | `test_smoke::test_play_score_and_review`, `03-sim-marked.png` (dusk), `10-sensor-*.png`; night and urban screenshots taken during the build | |
| F2 | EO, night vision, thermal, visibly different | Verified | `test_verification::test_sensor_modes_differ_and_switch_fast` (3 distinct filters and images, switch well under 1 s), `10-sensor-eo/nv/thermal.png` | |
| F3 | Degraded sensors: noise, reduced range, radar dropout, fog | Verified | `test_scenario::test_four_degradation_levels_match_visual_design_table`, `test_verification::test_four_degradation_levels_in_the_view`, `11-degradation-3.png` | |
| F4 | Radar with tracks that carry latency and noise | Verified | `test_verification::test_radar_latency_and_noise` (updates once per 2 s sweep, lags truth, error under 250 m), `test_smoke::test_radar_console_tracks_and_marking` (never shows class), `07-radar-console.png` | Full radar model: RCS-based detection, clutter, false returns, 2-of-3 track initiation |
| F5 | Look, zoom, mark, classify, respond by mouse and keyboard | Verified | `test_verification::test_look_and_zoom_by_mouse_and_keyboard`, `test_smoke::test_play_score_and_review` (mouse mark), `test_access::test_keyboard_only_run` | |
| F6 | Distinct quadcopter, hexacopter, fixed-wing, balloon, bird, friendly | Verified | `test_verification::test_contact_silhouettes` (6 distinct geometries), `12-silhouettes.png`, `test_finish::test_motion_cues_differ_by_type` (erratic bird, steady aircraft, flapping wings, blinking nav light) | |
| F7 | Swarms: shared goals, formation offsets, avoidance | Verified | Shared leader path and formation offsets (`test_scenario::test_scripted_catalogue_matches_prd`); separation steering keeps members at least 20 m apart, and the group spreads when engaged (`test_finish::test_swarm_keeps_separation_and_spreads_when_engaged`) | Separation and spread are visual; the server scores the formation path |
| F8 | Audio cues and mute (Should) | Partial | **Verified by test:** the hum rises as a drone closes, and the tick, chime, buzz and two-tone breach alarm fire on their events; **M** mutes and unmutes (`test_finish::test_audio_cues_and_mute`, `test_breach_alarm_sounds`). **Not yet:** a person listening | Human check 3 |
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
| Grade bands | AVD gives none; lead decided A ≥ 90, B ≥ 80, C ≥ 70, D ≥ 60, F (2026-10-07) |
| Server owns the score; rolls from the scenario seed | Implemented; browser and server rolls are bit-identical (`test_offline_and_parity::test_js_and_python_rolls_match`) |

## Hard constraints

| Constraint | Status | Evidence |
| --- | --- | --- |
| Offline | Met | Every browser test blocks non-local requests: zero attempts recorded. `test_offline_and_parity::test_no_external_urls_in_pages_scripts_or_styles`. Human check 2026-10-06: fresh clone, install, seed and full run on the target laptop with Wi-Fi off |
| Deterministic | Met | Generator tests; seed-reuse browser test |
| Server-owned scoring | Met | `api.submit_session` rebuilds the scenario and ignores any client score (`test_submit_score_store_and_read_back` sends `total: 100`) |
| No real weapon modelling | Met | Abstract responses with configurable effectiveness only |

## Hand-over readiness (2026-10-07)

| Item | Evidence |
| --- | --- |
| One-command start | `start.sh` (macOS/Linux): from an unzipped package with no `.venv`, `./start.sh --demo` created the environment, installed, seeded and served `/mission` in **8.4 s** on the dev Mac (pip cache warm). `start.bat` for Windows is written but **not yet run on Windows** (track A, issue #10) |
| Launch to first scenario | Warm `./start.sh` to a running scenario took **2.3 s** with scripted clicks on the dev Mac. Still to be timed by hand on the target laptop (issue #9) |
| Self-contained package | `scripts/package.py` builds a 0.6 MB zip (71 files, vendored libraries included). The 114 non-browser tests pass inside the unzipped package |
| No lost sessions | If saving fails, the session is kept in the browser and Mission select offers to resend it (`test_finish::test_unsaved_session_is_kept_and_resent`) |
| In-app help | `/help` explains controls, markers, sensors and radar, and draws the scoring tree from the live rubric (`test_finish::test_help_page_shows_live_rubric`) |

## Decisions

Decided by the lead on 2026-10-07:

- **No demo is scheduled.** The demo-only tasks (date and format, presenter roles, rehearsals, fallback video) are closed as not planned; `DEMO.md` is kept as a ready walkthrough in case one is arranged. Machine checks continue on a "target laptop" instead of a demo laptop.
- **Grade bands:** A ≥ 90, B ≥ 80, C ≥ 70, D ≥ 60, otherwise F (as in `rubric.json`).
- **VR:** desktop only for this release, as in the PRD. Rendering stays isolated in `world.js` so VR can be added later.
- **Theme:** keep the Stitch dark look only. This is a deliberate deviation from the Visual Design doc's light dashboard theme.
- **Text size:** all data text is at least 14 px. Only captions (section labels, column headers, hot-key hints, chip names) are 12 px, which matches the Visual Design rule. Enforced by `test_access::test_text_sizes`.

Still open (track B, issue #15):

1. **Rubric interpretations:** failed-roll-then-breach scores 60%; decoys are non-threats; "late" means within 300 m; suitable responses per model (jam or intercept for quadcopters and hexacopters, intercept only for fixed-wing).
2. **Swarm counting:** swarm members are counted on top of the difficulty table's hostile count.

## Needs a human check

1. ~~**On the target laptop:** Wi-Fi-off run~~ done 2026-10-06. Saturation Swarm (8 drones) measured **30 fps**: passes, but with no headroom. Since then, quality levels have been added (Auto/High/Medium/Low; Auto steps down after 3 s under 35 fps). Re-measure on the target laptop with a 12-drone swarm: `/sim?callsign=test&unit=test&seed=7&difficulty=5&swarm=12&degradation=0`, first on Auto, then on Low.
2. **Audio:** play any scenario with sound on. The rotor hum should rise as a drone closes in, and the chime, buzz and breach alarm should play on their events. Check that **M** mutes.
3. **Colour-blind review** (my review of the greyscale render `13-greyscale-markers.png` passed: all four states are distinct by shape and text; please confirm by eye): set macOS Display → Colour filters → Greyscale, then check that threat markers (triangle, diamond, circle, square, all with text labels) and the dashboard still read correctly.
4. **Urban Canyon feel:** the drone should be visible for about 4 s around T+37 s and again on final approach.
5. **Second machine:** clone the repo and follow the README.

## History: the morning audit

At 15:00 the project was an Antigravity prototype: six static Stitch HTML mockups in a React shell, a 100-line Express/WebSocket relay, and a Unity C# script with no Unity project. All 21 requirements were Missing or Partial, `npm run build` failed, and the UI did not work offline. That code is kept in `archive/`, and the Stitch screens remain the visual reference for the current UI.

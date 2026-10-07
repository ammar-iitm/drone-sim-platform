# Problem statement mapping (draft for track B, issue #19)

Oct 7, 2026 · **Draft.** This maps each element of SIH PS 26247 to where it appears in the app and the evidence that it works.

**Caveat:** the official problem-statement text could not be found online from here. The elements below come from the paraphrase in `docs/PRD.md` (Overview and "done means"). **Track B must check every row against the official PS text from the SIH portal** and add any element that is missing here.

## Elements of the problem statement

| # | PS element | Where it is in the app | Evidence (test or screenshot) | Status |
| --- | --- | --- | --- | --- |
| P1 | A software simulator | Browser 3D simulator at `/sim` (Three.js), served by Flask | `test_smoke::test_play_score_and_review` | Met |
| P2 | Trains unit-level personnel | Each trainee has a callsign and a unit; the dashboard rolls up by unit | `test_api::test_analytics_shapes`, `06-dashboard.png` | Met |
| P3 | Recognise drone threats | Scan, zoom and mark contacts in EO, night-vision and thermal views, with radar cueing | `test_verification::test_look_and_zoom_by_mouse_and_keyboard`, `test_verification::test_sensor_modes_differ_and_switch_fast`, `test_smoke::test_radar_console_tracks_and_marking` | Met |
| P4 | Classify drone threats | Five classes (keys 1 to 5) across six visually distinct contact types | `test_verification::test_contact_silhouettes`, `test_finish::test_motion_cues_differ_by_type` | Met |
| P5 | Respond to drone threats | Track, Report, Jam, Intercept and Take cover, with seeded success rolls | `tests/test_scoring.py` (engagement branches), `test_access::test_keyboard_only_run` | Met |
| P6 | Swarm threats | Swarms with formation offsets, separation, and spread when engaged; up to 12 drones | `test_finish::test_swarm_keeps_separation_and_spreads_when_engaged`, the Saturation Swarm scenario | Met. 12-drone frame rate on the target laptop still unmeasured (#8) |
| P7 | Replaces costly, scarce live drills with repetitions | Unlimited procedural scenarios from a seed; 2.3 s warm start to a running scenario | `test_scenario::test_same_seed_gives_identical_json`, hand-over timing in `STATUS.md` | Met. Hand timing on the target laptop still to do (#9) |
| P8 | Not dependent on weather or time of day | Day, dusk and night; fog and sensor degradation at four levels | `test_scenario::test_four_degradation_levels_match_visual_design_table`, `test_verification::test_four_degradation_levels_in_the_view` | Met |
| P9 | Scripted scenarios | Six scripted scenarios, each with a learning objective | `test_scenarios::test_scenario_plays_end_to_end` ×6 | Met |
| P10 | Procedurally generated scenarios | Seeded generator: difficulty 1 to 5, terrain, time, threat mix, swarm size, degradation | `test_api::test_procedural_via_api_is_deterministic`, `test_verification::test_instructor_settings_and_seed_reuse` | Met |
| P11 | Urban and rural terrain | Urban Canyon (low-altitude masking) and rural scenarios | `test_scenarios` (Urban Canyon objective) | Met. Human "feel" check still pending (#11) |
| P12 | Scoring of detection time | Detection tiers against a par time per scenario | `tests/test_scoring.py` (detection tiers) | Met |
| P13 | Scoring of classification accuracy | Exact, same family or wrong family; critical misclassification | `tests/test_scoring.py` (classification) | Met |
| P14 | Scoring of engagement decisions | Decision tree: correct and effective, failed roll, late or unsuitable, restraint, friendly engaged | `tests/test_scoring.py`, `test_scoring::test_every_scored_stage_has_reason_and_node` | Met |
| P15 | Scoring by decision tree | Every score shows its tree path and a reason; the rubric is editable in `rubric.json` | `04-score.png`, `05-session.png`, `test_scoring::test_weights_come_from_rubric` | Met. Rubric references are drafted in `RUBRIC_SOURCES.md` (#14) |
| P16 | After-action review | Session review page with an event timeline and points per event; CSV export | `05-session.png`, `test_api::test_csv_exports` | Met |
| P17 | Track individuals over repeated sessions | Per-trainee history and trend charts | `test_verification::test_dashboard_sorting_tables_and_tooltips` | Met |
| P18 | Track units over repeated sessions | Unit rollup, weakest skill, weakest trainees, confusion matrix | `test_api::test_analytics_shapes`, `06-dashboard.png` | Met |
| P19 | Runs on a standard laptop, offline | No external requests; vendored libraries; Wi-Fi-off run done by hand on 2026-10-06 | `test_offline_and_parity::test_no_external_urls_in_pages_scripts_or_styles`, `STATUS.md` human check 1 | Met. Second-machine install still to do (#10) |

## Summary

- All 19 elements found in the PRD's paraphrase map to a working feature with automated evidence.
- Four rows depend on checks still open on the target laptop: P6 (#8), P7 (#9), P11 (#11) and P19 (#10).
- Not part of the PS as paraphrased, and out of scope: VR (desktop only, lead decision 2026-10-07) and real weapon modelling (a PRD non-goal).

## What track B still has to do

- [ ] Get the official PS 26247 text from the SIH portal and paste it at the top of this file.
- [ ] Check each row against it, and add any element that is missing.
- [ ] Re-check the four open rows once #8 to #11 are done.
- [ ] Tick "Re-read the problem statement one last time and tick off each outcome" in `CHECKLIST.md`.

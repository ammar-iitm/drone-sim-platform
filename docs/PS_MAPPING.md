# Problem statement mapping (track B, issue #19)

Oct 10, 2026 · This maps each element of SIH PS 26247 to where it appears in the app and the evidence that it works. Rows P1 to P19 were drafted from the PRD's paraphrase; they have now been checked against the official text below, and P20 to P24 were added for elements the paraphrase missed.

## Official problem statement (SIH PS 26247)

> **Background:** Recent conflicts have shown that low-cost commercial and military-grade drones, employed individually and in swarms,have become a decisive battlefield factor. Existing training replies on classroom instruction and limited live-fire drills, which are costly, weather-dependent and do not scale to give troops adequate repetitions.
>
> **Detailed Description:** A software-based simulation platform is required to train personnel in recognizing, classifying and responding to drone/swarm threats across varied and realistic scenarios (day/ night,degraded sensors, urban/ rural terrain, single-drone and swarm attacks). The tool should be usable at unit level with minimal speacialized hardware.
>
> **Expected Solution/ Outcomes:**
> - Desktop or VR-capable simulator with scripted and procedurally generated threat scenarios.
> - Decision-tree based scoring on detection time, threat classification accuracy and engagement decisions.
> - After-action review (AAR) dashboard tracking individual/ unit performance over repeated sessions.
> - Adjustments difficulty and scenario randomization to prevent rote learning.

(Pasted as given, typos included.)

## Elements of the problem statement

| # | PS element | Where it is in the app | Evidence (test or screenshot) | Status |
| --- | --- | --- | --- | --- |
| P1 | A software simulator | Browser 3D simulator at `/sim` (Three.js), served by Flask | `test_smoke::test_play_score_and_review` | Met |
| P2 | Usable at unit level with minimal specialised hardware | Each trainee has a callsign and a unit; the dashboard rolls up by unit | `test_api::test_analytics_shapes`, `06-dashboard.png` | Met |
| P3 | Recognise drone threats | Scan, zoom and mark contacts in EO, night-vision and thermal views, with radar cueing | `test_verification::test_look_and_zoom_by_mouse_and_keyboard`, `test_verification::test_sensor_modes_differ_and_switch_fast`, `test_smoke::test_radar_console_tracks_and_marking` | Met |
| P4 | Classify drone threats | Five classes (keys 1 to 5) across six visually distinct contact types | `test_verification::test_contact_silhouettes`, `test_finish::test_motion_cues_differ_by_type` | Met |
| P5 | Respond to drone threats | Track, Report, Jam, Intercept and Take cover, with seeded success rolls | `tests/test_scoring.py` (engagement branches), `test_access::test_keyboard_only_run` | Met |
| P6 | Swarm threats | Swarms with formation offsets, separation, and spread when engaged; up to 12 drones | `test_finish::test_swarm_keeps_separation_and_spreads_when_engaged`, the Saturation Swarm scenario | Met. 12-drone frame rate on the target laptop still unmeasured (#8) |
| P7 | Replaces costly, scarce live drills with repetitions | Unlimited procedural scenarios from a seed; 2.3 s warm start to a running scenario | `test_scenario::test_same_seed_gives_identical_json`, hand-over timing in `STATUS.md` | Met. Hand timing on the target laptop still to do (#9) |
| P8 | Day/night and degraded sensors; not weather-dependent | Day, dusk and night; fog and sensor degradation at four levels | `test_scenario::test_four_degradation_levels_match_visual_design_table`, `test_verification::test_four_degradation_levels_in_the_view` | Met |
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
| P20 | Low-cost commercial and military-grade drones | Commercial quadcopters and hexacopters; a military-grade fixed-wing loitering drone (Night Loiter, and in procedural mixes) | `test_verification::test_contact_silhouettes`, `test_scenarios` (Night Loiter objective) | Met |
| P21 | Single-drone and swarm attacks | Single-drone scenarios (Dawn Recon, Night Loiter, Urban Canyon) and Saturation Swarm; procedural swarm size 0 to 12 | `test_scenarios::test_scenario_plays_end_to_end` ×6 | Met |
| P22 | Desktop or VR-capable simulator | Desktop simulator. VR is not built (lead decision 2026-10-07); the PS asks for desktop **or** VR, so desktop meets it | `test_smoke::test_play_score_and_review` | Met (desktop) |
| P23 | Adjustable difficulty | Difficulty 1 to 5 on Mission select scales speed, counts, decoys and degradation together | `test_scenario::test_difficulty_table_is_respected` | Met |
| P24 | Scenario randomization to prevent rote learning | Procedural seed starts on a new random value each visit (**Random** re-draws). Scripted scenarios launch as a seeded variant by default (**Vary each run**): every approach turns by one angle up to 30°, spawn times shift and jitter, and response rolls change, with the learning objective kept; Urban Canyon varies only timing and rolls because its route runs between buildings | `test_verification::test_mission_select_randomises_by_default`, `test_scenario::test_variant_keeps_the_learning_objective` (×18), `test_scenarios::test_scenario_plays_end_to_end[*-variant]` ×6, `test_api::test_scripted_variant_is_served_scored_and_stored` | Met |

## Summary

- Checked against the official text: all 24 elements are met with automated evidence. P24 (rote learning) was partial and was closed on 2026-10-10 with random default seeds and scripted variants.
- Four rows also depend on checks still open on the target laptop: P6 (#8), P7 (#9), P11 (#11) and P19 (#10).
- VR is not built; the PS accepts desktop. Real weapon modelling is out of scope (a PRD non-goal).

## What track B still has to do

- [x] Get the official PS 26247 text from the SIH portal and paste it at the top of this file.
- [x] Check each row against it, and add any element that is missing (P20 to P24 added).
- [x] Close the P24 gap (randomization to prevent rote learning).
- [ ] Re-check the four open rows once #8 to #11 are done.
- [ ] Tick "Re-read the problem statement one last time and tick off each outcome" in `CHECKLIST.md`.

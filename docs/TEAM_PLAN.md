# Team plan for the remaining work

Oct 6, 2026 · Status at commit `92d8893`: 19 of 21 requirements verified, 144 tests passing, checklist 63 of 81. See [STATUS.md](STATUS.md) for evidence, [DEMO.md](DEMO.md) for the judging script and [CHECKLIST.md](CHECKLIST.md) for the full list.

**Update 2026-10-07: no demo is scheduled.** L1, L3, B4 and B5 are closed as not planned (issues #1, #3, #17, #18) and can be reopened if a demo is arranged. "Demo laptop" below now means the target laptop the trainer will run on.

The 18 open checklist items split into two tracks that touch different files, so both can run at the same time without merge conflicts. A handful of decisions belong to the team lead and unblock parts of both tracks.

## Lead (Ammar): decisions, first

These block work below. Decide them and note the answers in `STATUS.md` under "Open decisions".

| # | Decision | Blocks |
| --- | --- | --- |
| ~~L1~~ | ~~Demo date and format~~ (no demo): own laptop or projector, internet or not | A1, B4 |
| L2 | VR demo expected, or desktop only? (The PRD says desktop; VR is a Could) | Nothing if desktop |
| ~~L3~~ | ~~Who plays the instructor in the demo, and who drives the laptop~~ (no demo) | B4 |
| L4 | Light theme for the dashboard: needed, or keep the Stitch dark look? | A5 |
| L5 | Text size: keep 12 px captions, or move all data text to 14 px? | A5 |
| ~~L6~~ | ~~Pick the target laptop~~ (done 2026-10-10: MacBook Pro, M5 Pro, Chrome 155) | A1 to A4 |
| ~~L7~~ | ~~Team owners~~ (done 2026-10-10: Ammar owns A and B and reviews merges) | Everyone |

Checklist items covered: "Confirm the date and format…", "Confirm whether a VR demonstration…", "Decide who plays the instructor…", "Confirm the team…", "Pick the demo laptop…".

## Teammate A: Test and polish

**Owns:** `app/static/css/`, `app/templates/`, `app/static/js/sim/world.js`, `tests/e2e/`. Works on branch `track-a`.

| # | Task | How to do it | Done when | Size |
| --- | --- | --- | --- | --- |
| ~~A1~~ | ~~12-drone frame rate~~ (done 2026-10-10: 120 fps on Auto and Low) | `git pull`, run `run.py`, open `/sim?callsign=test&unit=test&seed=7&difficulty=5&swarm=12&degradation=0`, wait for the swarm (watch the radar), face it, and read the FPS and Quality chips. Repeat with Graphics quality set to Low on Mission select. | 30 fps or more on Auto or Low. Record both numbers in `STATUS.md`. If under 30 even on Low, open an issue with the laptop model and the numbers. | S |
| ~~A2~~ | ~~Launch to first scenario under 60 s~~ (done 2026-10-10: 0.7 s warm, 5.4 s cold) | From a terminal with the app stopped, start a stopwatch, run `.venv/bin/python run.py`, open `/mission`, enter a callsign, pick Dawn Recon Pass, press Launch, then Enter. | Stopwatch reads under 60 s. Record the time. | S |
| A3 | Second machine | On a laptop that has never run the project, follow only `README.md`: clone, create the venv, `pip install`, run. Then switch Wi-Fi off and play one scenario. | It works using only the README. Fix any README gaps you hit. | S |
| A4 | Human sense checks | The checks under "Needs a human check" in `STATUS.md`: **audio** (hum, tick, chime, buzz, breach alarm, M to mute), **colour-blind** (macOS Greyscale filter: markers and dashboard still readable), **Urban Canyon feel** (a brief window around T+37 s at about 115°). | Each passes, or an issue is filed with a screenshot. | S |
| A5 | Theme and text size, after L4 and L5 | Light theme: add light-mode tokens to `aegis.css` from the Visual Design doc's light column, applied to the dashboard pages only (the simulator stays dark). Text: if 14 px is chosen, raise `.label` and the table header sizes, then fix any wrapping. | `python -m pytest tests/e2e` passes, including `test_access::test_text_sizes`. Before and after screenshots are attached to the PR. | M |
| A6 | Keep the browser tests green | Run the full suite before every merge: `.venv/bin/python -m pytest`. | 144 or more pass. | ongoing |

Checklist items covered: "Audio cues and a mute button", "Light and dark themes both read correctly", "The simulator holds 30 fps…", "Launch to first scenario…", "Text is at least 14 px…", "Threat state never relies on colour alone", "Package the project folder and test it on a second machine".

## Teammate B: Rubric and demo

**Owns:** `rubric.json`, `app/scenarios/*.json`, `docs/DEMO.md`, the slides and video, and the submission. Works on branch `track-b`.

| # | Task | How to do it | Done when | Size |
| --- | --- | --- | --- | --- |
| B1 | Align the rubric with an official or public reference | Look for public counter-UAS doctrine or SIH guidance on threat classes and rules of engagement. Compare with `rubric.json`: classes and families, expected responses per drone model, penalties and grade bands. List the differences, then edit `rubric.json`. No code change is needed. | Each change is cited in a short "Rubric sources" section in `STATUS.md`, and `.venv/bin/python -m pytest tests/test_scoring.py` still passes. If a test fails because a rule changed on purpose, update the test with a comment explaining why. | M |
| B2 | Confirm the scoring interpretations | Review the five "Open decisions" items in `STATUS.md` that are about scoring (grade bands, failed-roll-then-breach, decoys as non-threats, the 300 m "late" range, swarm counting) and agree them with the lead. | Each is marked "Agreed" or changed in `rubric.json`. | S |
| B3 | Read the plan docs and record disagreements | Read the PRD, AVD and Visual Design docs against the running app. | Disagreements are listed in `STATUS.md`; anything that needs code becomes an issue for A. | S |
| ~~B4~~ | ~~Rehearse twice~~ (no demo), after L1 and L3 | Follow `docs/DEMO.md` from a clean start (`scripts/seed_demo.py --reset`), including the deliberate mistake (jamming the friendly aircraft). Time it, and tighten the script where it runs long. | Two full runs under 5 minutes; edits made to `DEMO.md`. | M |
| ~~B5~~ | ~~Fallback recording~~ (no demo) | QuickTime → New Screen Recording of one clean run of the script, with narration. Keep it on the demo laptop and a USB stick. | A video under 5 minutes, played back once to confirm it works. | S |
| ~~B6~~ | ~~Problem-statement check~~ (done 2026-10-10, see `PS_MAPPING.md`) | Re-read SIH PS 26247 and tick each required outcome against the table at the top of `DEMO.md`. | Every outcome maps to a moment in the demo. | S |
| ~~B7~~ | ~~Submit~~ (not needed: no zip submission, 2026-10-10) | Submit on the SIH portal, following its format, with the repo link if requested. The repo is private, so add judges or export a zip if the portal needs access. | Confirmation saved (screenshot or PDF) in the team drive. | S |

Checklist items covered: "Find any official reference…", "Read the PRD, AVD and Visual Design docs…", "Rehearse the demo twice…", "Prepare a fallback…", "Re-read the problem statement…", "Submit through the SIH portal…".

## Order and dependencies

```text
Day 1   Lead: L1-L7 decisions       A: A1, A2, A3, A4 (laptop checks)      B: B1, B2, B3 (rubric)
Day 2   Lead: review merges         A: A5 (theme/text), A6                  B: B4, B5 (rehearse, record)
Last    Everyone: one joint full rehearsal on the demo laptop, then B6 and B7
```

- B4 and B5 should use the final rubric (after B1 and B2) and the final look (after A5), so the recording matches the live demo.
- Anything A finds that changes behaviour (for example, the frame rate is too low) is an issue for the lead to prioritise.

## Working rules

- One branch per track, with small PRs into `master`. The lead reviews.
- Run `.venv/bin/python -m pytest` before opening a PR; all tests must pass.
- When you finish a checklist item, tick it in `docs/CHECKLIST.md` in the same PR and add the evidence (a number, screenshot or test name) to `STATUS.md`. Only tick what you actually ran and saw work.
- Don't hand-edit `data/trainer.db`. Regenerate it with `scripts/seed_demo.py --reset`.

# Rubric sources (draft for track B, issue #14)

Oct 7, 2026 · **Draft.** Track B should check each source and then mark every row Agreed, Changed or Rejected. Nothing in `rubric.json` has been changed yet.

## How to read this

`rubric.json` mixes two kinds of rule:

1. **Structure:** what is scored and in what order, which contacts count as threats, and which response suits which drone. Public doctrine and reporting speak to these, and the table below compares them.
2. **Numbers:** the weights (30/30/40), detection tiers, penalty sizes (2/10/25) and grade bands. **None of the public sources found gives numbers for these.** They are training choices made by the team, and the help page and `STATUS.md` should say so plainly rather than cite doctrine for them.

Only public, unclassified material is used, as the PRD requires.

## Sources

| Key | Source | What was actually read |
| --- | --- | --- |
| S1 | US Army, *ATP 3-01.81 Counter-Unmanned Aircraft System (C-UAS)*, August 2023 (supersedes April 2017). [irp.fas.org/doddir/army/atp3-01-81.pdf](https://irp.fas.org/doddir/army/atp3-01-81.pdf) | Only search summaries. The PDF could not be downloaded from here. **Track B: read chapters 1 to 3 and confirm the rows that cite S1.** |
| S2 | Ferguson and Lemler, "Understanding the Counterdrone Fight: Insights from Combat in Iraq and Syria", Modern War Institute, West Point, 2024. [mwi.westpoint.edu](https://mwi.westpoint.edu/understanding-the-counterdrone-fight-insights-from-combat-in-iraq-and-syria/) | The article itself |
| S3 | "Counter-Unmanned Aerial Systems (C-UAS) Training and Implementation at the National Training Center", army.mil, Sep 2, 2025. [army.mil/article/288207](https://www.army.mil/article/288207/counter_unmanned_aerial_systems_c_uas_training_and_implementation_at_the_national_training_center) | The article itself |
| S4 | Ministry of Civil Aviation, National Counter Rogue Drone Guidelines, 2019, as summarised by [Drishti IAS](https://www.drishtiias.com/daily-updates/daily-news-analysis/national-anti-drone-guidelines/print_manually) | A secondary summary only. Track B should find the original if possible |
| S5 | Drone Rules, 2021 (India), weight categories, as summarised by [Bar and Bench](https://www.barandbench.com/columns/the-drone-rules-2021-next-technological-revolution) | A secondary summary only |
| S6 | US DoD UAS group classification. [Penn State GEOG 892](https://courses.ems.psu.edu/geog892/node/637), [Wikipedia](https://en.wikipedia.org/wiki/UAS_groups_of_the_United_States_military) | Summaries |

## Comparison with `rubric.json`

| # | Rule in the rubric | What the sources say | Verdict | Proposed action |
| --- | --- | --- | --- | --- |
| R1 | Three scored stages, in order: detection, classification, engagement | The C-UAS process is "detect, identify, decide, and defeat" (S1, S2). Positive identification comes before the decision to defeat (S2) | Aligned | None. The "decide" step is folded into engagement; the help page could name all four steps |
| R2 | Five classes: Recon quadcopter, Armed loitering drone, Decoy or balloon, Bird, Friendly aircraft | Operators must "distinguish between birds, balloons, OWAUAS [one-way attack UAS], and friendly aircraft" (S2) | Aligned | Optional: relabel "Armed loitering drone" as "Armed or one-way attack drone" to match the source's term |
| R3 | Calling a hostile a non-threat or friendly is a critical error (−25) | Fratricide and missed threats are the main risks; the source warns that visual-only acquisition raises "the risk of hitting a friendly aircraft by mistake" (S2) | Aligned in spirit | The −25 size is a team choice (see "How to read this") |
| R4 | Engaging a friendly is critical (−25); engaging a non-threat scores 0 | Positive ID before engagement (S2); friendly-aircraft risk (S2) | Aligned | None |
| R5 | Jam is suitable for quadcopters and hexacopters; intercept only for fixed-wing (jam 10% effective) | Electronic defeat was "most effective against smaller drones"; against drones on "preprogrammed waypoints … kinetic defeat options are currently more effective" (S2) | Aligned | Optional: say in `help.html` that the fixed-wing is assumed to fly preprogrammed waypoints, which is why jamming rarely works |
| R6 | Jam = non-destructive, intercept = destructive | India's guidelines split responses into **soft kill** (jamming, forced landing) and **hard kill** (destroying the drone) (S4) | Aligned | Recommended for an Indian audience: relabel as "Jam (soft kill)" and "Intercept (hard kill)". Labels only, no code change |
| R7 | Detection scored against a par time per scenario | Detection time varies widely: fixed-wing drones are seen "several minutes out", while terrain-masked ones are seen "seconds away" (S2) | Aligned | None. Urban Canyon already models terrain masking |
| R8 | **Report** and **Take cover** against a hostile score 20% ("unsuitable") | Contact with an unidentified UAS may come before an attack, so units should assume they have been seen and take passive measures such as dispersion and camouflage (S1 summary, S3). The C-UAS contact report is **BARS**: bearing, altitude, range, speed (S2) | **Possible gap** | Discuss with the lead (see "Points for discussion" 1) |
| R9 | Hostile drones fly at up to 150 m and 49 m/s (≈95 kt) | DoD Group 1: under 20 lb, below 1,200 ft AGL (≈366 m), under 100 kt (S6). India: micro 250 g–2 kg, small 2–25 kg (S5) | Aligned | Optional: add "Group 1 / micro to small class" to the help page so instructors can relate it to real drones |
| R10 | Weights 30/30/40, detection tiers 100/75/40/10 %, penalties 2/10/25, grade bands A90 to F | No public numbers found (S1 to S6) | Team choice | Keep. Say so in the help page and `STATUS.md`, and do not cite doctrine for them |
| R11 | "Late" means a response from inside 300 m | No public number found | Team choice | Keep, and list it as a team choice (it is also an open item in issue #15) |

## Points for discussion with the lead (issue #15)

1. **Passive defence and reporting (R8).** At present Take cover or Report against a hostile scores 20%, the same as a wrong response. The sources treat reporting (BARS) and passive defence as correct actions in their own right. Two options, neither of which has been made:
   - **(a) Keep as is.** The trainer is about defeat decisions, so a hostile you do not engage counts as unsuitable. This is simple, and the score already explains it.
   - **(b) Credit the right passive action.** If no suitable defeat response is possible in time (for example, an armed drone already inside 300 m), Take cover scores 100% instead of 20%. This needs a small code change in `app/scoring.py`, a new test, and a rubric entry such as `"passive_when_late": ["TAKE_COVER"]`.

   **Recommendation:** (a) for this release, with (b) logged as a future improvement. It changes scoring logic late, and the sources do not give a threshold.
2. **Labels (R2, R6).** Rename to "Jam (soft kill)" and "Intercept (hard kill)", and possibly "Armed or one-way attack drone". This is a `rubric.json` edit only, but check that the browser tests do not assert the old labels: `grep -rn "Armed loitering\|\"Jam\"\|\"Intercept\"" tests`.

## What track B still has to do

- [ ] Read S1 (ATP 3-01.81) directly and confirm or correct the rows that cite it (R1, R8).
- [ ] Look for the original MoCA 2019 guidelines (S4) instead of the summary.
- [ ] Mark each row R1 to R11 as Agreed, Changed or Rejected.
- [ ] Make any agreed `rubric.json` edits, then run `.venv/bin/python -m pytest`.
- [ ] Move the final version into a "Rubric sources" section of `STATUS.md` and tick the checklist item.

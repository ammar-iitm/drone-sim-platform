# Rubric sources (issue #14)

Oct 16, 2026 · Every row below has been checked against the sources. The two proposed changes were agreed by the lead on 2026-10-16 and are now in `rubric.json` (version 2).

## How to read this

`rubric.json` mixes two kinds of rule:

1. **Structure:** what is scored and in what order, which contacts count as threats, and which response suits which drone. Public doctrine and reporting speak to these, and the table below compares them.
2. **Numbers:** the weights (30/30/40), detection tiers, penalty sizes (2/10/25) and grade bands. **None of the public sources found gives numbers for these.** They are training choices made by the team, and the help page and the README should say so plainly rather than cite doctrine for them.

Only public, unclassified material is used, as the PRD requires.

## Sources

| Key | Source | What was actually read |
| --- | --- | --- |
| S1 | US Army, *ATP 3-01.81 Counter-Unmanned Aircraft System (C-UAS) Operations*, 23 May 2025 (supersedes the 11 August 2023 edition). Approved for public release. [armypubs.army.mil](https://armypubs.army.mil/epubs/DR_pubs/DR_a/ARN43877-ATP_3-01.81-000-WEB-1.pdf) | **The full PDF.** Chapter 1 (UAS links and autonomous operation) and chapter 5 (passive and active defence) were read directly; paragraph numbers are cited below |
| S2 | Ferguson and Lemler, "Understanding the Counterdrone Fight: Insights from Combat in Iraq and Syria", Modern War Institute, West Point, 2024. [mwi.westpoint.edu](https://mwi.westpoint.edu/understanding-the-counterdrone-fight-insights-from-combat-in-iraq-and-syria/) | The article itself |
| S3 | "Counter-Unmanned Aerial Systems (C-UAS) Training and Implementation at the National Training Center", army.mil, Sep 2, 2025. [army.mil/article/288207](https://www.army.mil/article/288207/counter_unmanned_aerial_systems_c_uas_training_and_implementation_at_the_national_training_center) | The article itself |
| S4 | Ministry of Civil Aviation, National Counter Rogue Drone Guidelines, 2019, as summarised by [Drishti IAS](https://www.drishtiias.com/daily-updates/daily-news-analysis/national-anti-drone-guidelines/print_manually) | A secondary summary only. The original (`civilaviation.gov.in/.../Counter_rogue_drone_guidelnes_NSCS.pdf`) now returns "Page is not available" (checked 2026-10-16) |
| S5 | Drone Rules, 2021 (India), weight categories, as summarised by [Bar and Bench](https://www.barandbench.com/columns/the-drone-rules-2021-next-technological-revolution) | A secondary summary only |
| S6 | US DoD UAS group classification. [Penn State GEOG 892](https://courses.ems.psu.edu/geog892/node/637), [Wikipedia](https://en.wikipedia.org/wiki/UAS_groups_of_the_United_States_military) | Summaries |

## Comparison with `rubric.json`

| # | Rule in the rubric | What the sources say | Verdict |
| --- | --- | --- | --- |
| R1 | Three scored stages, in order: detection, classification, engagement | Active defence is "a multi-step sequence … to detect, track, identify, decide, and potentially engage an unknown UAS. The quicker these steps can be applied, the more effective the response" (S1, 5-23). Detection time is scored against par, which matches "the quicker" | **Agreed.** Track and decide are folded into the three stages; the help page could name all five steps |
| R2 | Five classes: Recon quadcopter, Armed loitering drone, Decoy or balloon, Bird, Friendly aircraft | Identification "should lead to a specific name or category" (S1, 5-30); visual recognition separates rotary-wing, fixed-wing and hybrid forms (S1, 5-5). Operators must tell apart birds, balloons, one-way attack UAS and friendly aircraft (S2) | **Agreed** |
| R3 | Calling a hostile a non-threat or friendly is a critical error (−25) | "Soldiers that encounter UAS should consider them as a threat eligible for engagement unless positively identified as friendly" (S1, 5-39). Early identification is needed "to maximize engagement times and avoid fratricide" (S1, 5-28) | **Agreed.** The −25 size is a team choice |
| R4 | Engaging a friendly is critical (−25); engaging a non-threat scores 0 | Timely identification "reduces the risk of friendly fire"; defeat must "confirm the identity of the UAS and prevent fratricide" (S1, 5-28, 5-33) | **Agreed** |
| R5 | Jam is suitable for quadcopters and hexacopters; intercept only for fixed-wing (jam 10% effective) | "Autonomous operations do not need a data link, can be programmed from launch to recovery" (S1, 1-14); a pre-programmed flight profile lets the link be disconnected in flight (S1, 5-24). Electronic defeat works best on small drones; kinetic options work better against drones on pre-programmed waypoints (S2) | **Agreed.** The help page should say the fixed-wing is assumed to fly pre-programmed waypoints |
| R6 | Jam = non-destructive, intercept = destructive | S1 splits defeat into "non-lethal or lethal procedures" (5-33) and methods into "physical and nonphysical" (5-31). India's guidelines call them soft kill and hard kill (S4, secondary only) | **Changed (labels only):** "Jam (soft kill)" and "Intercept (hard kill)", the S4 terms, for an Indian audience. No scoring change |
| R7 | Detection scored against a par time per scenario | Detection depends on "time of day, ambient light levels, meteorological conditions, and observer alertness" (S1, 5-24); terrain-masked drones may be seen only seconds away (S2) | **Agreed.** Par times already depend on visibility and model |
| R8 | **Report** and **Take cover** against a hostile score 20% ("unsuitable") | "Reporting of a threat UAS should utilize a standard reporting format", the SALUTE spot report, so units can "quickly adjust force protection measures and coordinate immediate response" (S1, 5-8, table 5-1). Reporting supports the response rather than replacing it. Passive defence: "In cases where the enemy aerial platforms are outside the range of the unit's weapons, a unit's most lucrative option can be to disperse and seek cover" (S1, chapter 5 introduction) | **Changed:** **Take cover** scores 100% (`correct_passive`) when the hostile then stays beyond the reach of every suitable response (`passive_responses` in the rubric). If it later comes within reach, the trainee should have engaged, so cover alone stays 20%. **Report** stays 20% as an engagement decision, since reporting accompanies a response |
| R9 | Hostile drones fly at up to 150 m and 49 m/s (≈95 kt) | S1 uses the DoD groups (table 5-4 aims by Group 1, 2, 3–5). Group 1: under 20 lb, below 1,200 ft AGL, under 100 kt (S6). India: micro 250 g–2 kg, small 2–25 kg (S5) | **Agreed** |
| R10 | Weights 30/30/40, detection tiers 100/75/40/10 %, penalties 2/10/25, grade bands A90 to F | No public numbers found (S1 to S6) | **Agreed as a team choice.** Say so; do not cite doctrine for them |
| R11 | "Late" means a response from inside 300 m | S1 gives no number: "The farther out an aircraft is positively identified, the more time is given to make engagement decisions" (5-5) | **Agreed as a team choice** |
| R12 | A timely successful retry after a missed first attempt scores 100% (issue #15) | Other C-UAS capabilities "continue to track the threat UAS in case the target was initially missed, and they can engage or re-engage as necessary" (S1, 5-36); "continue jamming, until the UAS is inoperable" (S1, 5-34) | **Agreed.** Doctrine supports re-engaging |

## Decisions

Both proposals were agreed on 2026-10-16 (R6 and R8 above). Issue #14 is closed.

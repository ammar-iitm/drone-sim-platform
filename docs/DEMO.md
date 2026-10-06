# Demo walkthrough: AEGIS // Drone Threat Trainer

Oct 6, 2026 · For the SIH 26247 judging slot. Target length: 4 to 5 minutes.

## The three outcomes and where they appear

| Problem-statement outcome | Where it is shown | Time in script |
| --- | --- | --- |
| 1. Desktop simulator with scripted and procedurally generated scenarios | Mission select (6 scripted cards and the seeded generator), then the live simulator | 0:20 to 2:30 |
| 2. Decision-tree scoring of detection time, classification and engagement | Score screen with the tree path and reason per contact; `rubric.json` | 2:30 to 3:15 |
| 3. AAR dashboard tracking individuals and units over repeated sessions | Dashboard: trends, unit rollup, weakest skill, confusion matrix, session review | 3:15 to 4:15 |

## Before the slot (10 minutes)

1. Turn **Wi-Fi off**. Everything below must work offline.
2. In a terminal in the project folder:
   ```bash
   .venv/bin/python scripts/seed_demo.py --reset     # fresh demo cohort: 6 trainees, 2 units, 30 sessions
   .venv/bin/python run.py                           # http://localhost:5050
   ```
3. Open Chrome full screen at `http://localhost:5050/mission`. Set the zoom to 100%.
4. Sound on, at a moderate volume.
5. Have `rubric.json` open in an editor in a second window.
6. Have the fallback recording ready to play (see below).

## Script

**0:00 · The problem (15 s).** "Counter-drone training today is classroom slides and rare live-fire days. This is a laptop simulator that gives unlimited, scored repetitions, and it runs with no internet."

**0:15 · Mission select (30 s).**
- Type callsign `DEMO-1`, unit `4 GUARDS`.
- Point at the six scripted cards: "each teaches one skill."
- In the procedural generator, set seed `48213` and difficulty 4. Point out that the same seed always rebuilds the same scenario.
- Then choose **Mixed Traffic** and press **Launch**.

**0:45 · The simulator (1 min 45 s).**
- Read the objective on the briefing ("Restraint…") and press **Enter**.
- Drag to scan. Press **Q** for the radar console: "a 30 rpm surveillance radar. Tracks form from sweeps, with noise and clutter, and it never tells you what the contact is." Press **Q** again.
- Turn towards a radar track. Click the contact in the view to mark it, then press **4 Bird** and **T Track**. "That's restraint: correct."
- **Deliberate mistake:** when the friendly aircraft appears, mark it, press **5 Friendly**, then press **J Jam** anyway. Point at the toast.
- When the hostile quadcopter appears (about 40 s in, from the north-west), mark it, press **1 Recon**, then **I Intercept** at around 1 km.
- Press **S** to show night vision and thermal briefly.
- Press **Esc**, then **Enter**, to end.

**2:30 · Score screen (45 s).**
- Composite score and grade, three weighted stage bars, and penalties.
- Scroll to the friendly aircraft: "jamming a friendly is a critical error, minus 25, and here is the exact branch and reason."
- Scroll to the hostile: "detected on par, classified exactly, intercepted at 1 km."
- "The browser never sends a score; the server recomputes everything from raw events and the rubric file." Optionally show `rubric.json` and change a weight.

**3:15 · AAR dashboard (1 min).**
- Open **AAR dashboard**, unit `4 GUARDS`.
- Summary tiles, then the weakest skill.
- The progress chart for one trainee shows improvement over repeated sessions; click **Table** to show the accessible table view.
- In the confusion matrix, point out "bird versus quadcopter mix-ups stand out".
- Open one session for the event timeline with the points behind each event. Click **Export CSV**.

**4:15 · Close (20 s).** "Offline, standard laptop, explainable and editable scoring. It's a decision-training aid, not a weapons simulator: responses are abstract categories, and the rubric comes from public principles."

## Fallback

If anything fails live, play the screen recording.
- **Making it:** QuickTime → File → New Screen Recording, then run this script once.
- **Speeding up the boring parts:** add `&speed=4` to a simulator URL to fast-forward. A "Fast-forward" chip shows it is on.

## Likely questions

| Question | Short answer |
| --- | --- |
| How realistic is the radar? | Simplified radar equation: detection range scales with the fourth root of radar cross-section, with low-altitude clutter masking, noise, false returns, and track initiation after 2 of 3 sweeps. It is tuned for training, not engineering. |
| Where does the rubric come from? | Public counter-drone principles. Every weight, threshold and penalty is in `rubric.json`, editable by the instructor without code. |
| Can it run in VR? | Not in this release (a PRD non-goal). Rendering is isolated in `world.js`, so a WebXR renderer can replace it. |
| Can scores be faked from the browser? | No. The server rebuilds the scenario from its id or seed and scores raw events, including re-running the response rolls. |
| What hardware does it need? | A browser with WebGL and Python. It holds 60 fps with 12 drones on a laptop GPU in testing. |

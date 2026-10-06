# SIH26247 Drone Threat Trainer: Visual Design

Oct 6, 2026 · Ammar Hashmi

## Design principles and mood

The interface should feel like a calm operations room: a dark, low-glare simulator where the trainee can read the situation at a glance, and a clean dashboard where an instructor can read the results just as quickly.

- **Legible first.** Anything the trainee must act on is high contrast and large enough to read under pressure.
- **Calm, not gamey.** No screen shake, explosions or flashing rewards. Feedback is clear and sober, which suits a training tool for a defence audience.
- **Meaning never rides on colour alone.** Threat state uses a colour, a shape and a label together.
- **One focal point.** The sensor view dominates, and panels around it stay quiet until they matter.
- **Dark simulator, themed dashboard.** The simulator HUD is always dark to protect night vision and reduce glare. The dashboard follows the viewer's light or dark preference.
- **Same system everywhere.** The simulator and dashboard share tokens, type and components so they read as one product.

## Colour tokens

Colours are defined once as tokens and used by role. The dashboard swaps between the light and dark columns; the simulator HUD always uses the HUD column.

| Token | Light | Dark | HUD (always dark) | Use |
| --- | --- | --- | --- | --- |
| surface | `#fcfcfb` | `#1a1a19` | `#0e1110` | Page and chart background |
| surface-raised | `#ffffff` | `#222221` | `#171a18` | Panels and cards |
| border | `#d9d8d3` | `#383835` | `#2d322f` | Panel edges, table rules |
| text-primary | `#0b0b0b` | `#ffffff` | `#e8ece9` | Main text and values |
| text-secondary | `#52514e` | `#c3c2b7` | `#a4aca7` | Labels and hints |
| accent | `#2a78d6` | `#3987e5` | `#3987e5` | Selection, focus, primary buttons |
| good | `#0ca30c` | `#0ca30c` | `#0ca30c` | Correct decisions, passed targets |
| warning | `#fab219` | `#fab219` | `#fab219` | Unknown contacts, caution |
| critical | `#d03b3b` | `#d03b3b` | `#d03b3b` | Hostile contacts, breaches, critical errors |

**Chart series.** The dashboard's three metrics use fixed colours: detection in blue (`#2a78d6` light, `#3987e5` dark), classification in orange (`#eb6834` light, `#d95926` dark) and engagement in aqua (`#1baf7a` light, `#199e70` dark). These passed the palette validator in both modes, with a colour-blind separation above 9 in both. Aqua falls below 3:1 contrast on the light surface, so every line is also directly labelled and each chart has a table view.

**Threat markers on the HUD** pair colour with shape and a text tag, so they work for colour-blind users: hostile is a red triangle labelled HOSTILE, unknown is an amber diamond labelled UNKNOWN, friendly is a blue circle labelled FRIENDLY, and benign is a grey square labelled BENIGN. The marker the trainee has selected gets a white ring.

## Typography and spacing

The app uses system fonts, because bundled web fonts add weight and the tool must work offline. Numbers use a monospaced face with tabular figures so timers and scores do not jitter as they change.

| Role | Font | Size | Weight |
| --- | --- | --- | --- |
| Page title | System sans | 28 px | 600 |
| Section heading | System sans | 20 px | 600 |
| Body and table text | System sans | 14 px | 400 |
| Labels and captions | System sans | 12 px | 500 |
| Timers, ranges, scores | System monospace | 14 to 28 px | 600 |

Spacing runs on a 4 px base: 4, 8, 12, 16, 24 and 32. Panels use 8 px corner radius, 1 px borders and no shadows. The minimum body text size is 14 px, and the only 12 px text is non-essential captions.

## Simulator HUD layout

```text
+--------------------------------------------------------------------------+
| Night Loitering Drone            03:12 of 05:00        Sensor: night vision |
+--------------------------------------------------------+-----------------+
| NIGHT VISION                                           | Radar           |
|                                                        |      (o)        |
|    ^ C1 · HOSTILE                                      |   rings + sweep |
|                          ( + )      (<>) C2 · UNKNOWN  +-----------------+
|                          reticle     selected, blue    | Contacts        |
|                                      ring              | ^ C1 HOSTILE .9 |
|  ~~~~~~~~~~~ terrain silhouette ~~~~~~~~~~~~~~~~~~~~~~ | <> C2 UNKNOWN   |
| BRG 042° · ZOOM 4x                                     | [] C3 BENIGN    |
+--------------------------------------------------------+-----------------+
| Classify  [Recon (1)] [Armed (2)] [Decoy (3)] [Bird (4)] [Friendly (5)]  |
| Respond   [Track (T)] [Report (R)] [Jam (J)] [Intercept (I)] [Take cover (C)] |
+--------------------------------------------------------------------------+
```

The sensor view takes most of the screen, with radar and the contact list in a side column. Classification and response sit in two rows beneath it, each button showing its hot key, so a trainee can work the whole decision from the keyboard. The selected contact carries a blue ring in the view and an edge mark in the list.

## Sensor mode visuals

Each sensor mode changes how the same scene looks, and the differences have to be obvious within a second of switching so trainees learn what each sensor is good and bad at.

| Mode | Look | How it is made |
| --- | --- | --- |
| Day EO | Natural colour, blue sky, hard shadows, contacts dark against the sky | No filter; daytime lighting |
| Dusk | Low warm light, reduced contrast, long shadows | Brightness 0.75, saturation 0.8, slight sepia |
| Night vision | Green phosphor, grain, vignette, bright point lights | Greyscale then green tint, brightness up, plus a grain overlay and edge vignette |
| Thermal | White-hot greyscale; warm objects (drones, birds, aircraft) glow bright against a cooler background | Greyscale with raised contrast; warm contacts rendered with a bright emissive core |

Sensor degradation applies on top of any mode, in four levels:

| Level | Image noise | Fog | Visible range | Radar dropout |
| --- | --- | --- | --- | --- |
| 0 | None | None | 3000 m | 0% |
| 1 | Light | Thin | 2200 m | 8% |
| 2 | Moderate | Medium | 1500 m | 18% |
| 3 | Heavy | Thick | 900 m | 30% |

Degradation also fades distant contacts into the haze, so at high levels the trainee must lean on radar and movement cues, which is the skill the scenario is meant to teach.

## Drone, decoy and terrain visuals

Contacts are low-polygon silhouettes designed to be told apart by shape and motion, which is how real observers tell them apart at range. At long range every contact is drawn at a minimum on-screen size of 6 px so it stays visible, and a marked contact gets a ring.

| Contact | Silhouette | Motion cue | Common confusion it teaches |
| --- | --- | --- | --- |
| Quadcopter (recon) | Flat body with four short arms in an X | Steady glide with small hover pauses | Versus a bird |
| Hexacopter (armed) | Larger X body with a visible payload under it | Slower, heavier approach | Versus a recon quadcopter |
| Fixed-wing loitering drone | Swept wing with a thin body | Fast, smooth arcs, then a dive | Versus a friendly aircraft |
| Decoy balloon | Round shape, no arms | Slow drift with the wind | Versus a hovering drone |
| Bird | Small, with wing flaps | Erratic turns, sudden changes of height | Versus a small quadcopter |
| Friendly aircraft | Larger body with a blinking navigation light | Straight, steady path | Versus a hostile fixed-wing drone |

**Terrain and sky.** Rural terrain is low-poly rolling hills in muted greens and browns with scattered trees. Urban terrain is a grid of grey blocks of varied height with darker streets. The sky is a gradient that changes with time of day: pale blue by day, orange to deep blue at dusk, near black with stars at night. In every case terrain stays visually quiet so contacts stand out.

## AAR dashboard layout

The dashboard is organised so the most important answer sits top left and each deeper question is one scroll or tab away.

| Area | Contents | Chart or element |
| --- | --- | --- |
| Header row | Unit and trainee pickers, date range | Two dropdowns and a range control, all in one row above the charts |
| Summary tiles | Sessions, average score, weakest skill, breaches | Four stat tiles with one headline number each |
| Progress chart | Detection, classification and engagement by session | Line chart, three series with direct end labels and a legend, plus a rolling mean |
| Unit comparison | Average per metric for each trainee | Horizontal bars, sorted, thin marks with rounded ends |
| Confusion matrix | True class against the trainee's choice | Single-hue blue grid, darker means more frequent, counts printed in cells |
| Session table | Date, scenario, score, grade, breaches, false alarms | Sortable table with a link to the session review |
| Session review | Timeline of events with each contact's decision path, reason and points | Vertical timeline with status icons and labels, never colour alone |

Every chart has a table view and hover details. Charts use one axis only, thin marks, recessive grid lines and colour assigned to the same metric everywhere, so blue always means detection.

## Component library

A small set of components is reused across the simulator and dashboard.

| Component | Specification |
| --- | --- |
| Primary button | Accent fill, white text, 8 px radius, 40 px high, visible 2 px focus ring |
| Secondary button | Transparent with a 1 px border, text-primary label |
| Response button | Larger, icon plus label plus hot key, for example Jam (J); the destructive responses use the critical colour only for their border |
| Panel | Raised surface, 1 px border, 8 px radius, 16 px padding, a 12 px uppercase label on top |
| Threat badge | Shape icon, text label and colour together, for example a red triangle with HOSTILE |
| Contact row | Contact id, state badge, range and bearing in monospace, selected row gets an accent edge |
| Timer and score | Large monospace figures with tabular numerals |
| Table | 14 px text, 1 px row rules, sortable headers with arrow icons, no zebra stripes |
| Tooltip | Raised surface, 12 px text, appears on hover and on keyboard focus |
| Toast | Bottom centre, 3 seconds, icon plus text, used for confirmations such as Session saved |

## Motion, audio and accessibility

**Motion.** Interface transitions last 150 ms and ease out. The only continuous motion is the world itself, the radar sweep and a pulsing ring on a selected contact. Users who prefer reduced motion get a static ring and an instant radar update, and the simulator's camera never shakes.

**Audio.** Sound carries information the eyes might miss. A faint rotor hum rises in volume and pitch as a contact approaches, a short tick confirms a mark, a distinct two-tone alert signals a breach, and a soft chime confirms a response. Total volume is capped, every sound has a visual counterpart, and a mute button sits in the HUD.

**Accessibility.**

- Text contrast is at least 4.5:1 and graphics at least 3:1, with the one noted exception of aqua on the light surface, which is always directly labelled.
- Threat state, scoring outcomes and status are never shown by colour alone.
- The simulator is fully operable by keyboard: arrow keys look, plus and minus zoom, Tab cycles contacts, number keys classify, letter keys respond.
- Body text is at least 14 px, and focus rings are always visible.
- Charts offer a table view for screen reader users and for anyone who prefers numbers.

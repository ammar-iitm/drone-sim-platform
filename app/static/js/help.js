// Help page: controls and the scoring tree, drawn from the live rubric so it never goes stale.
import { esc } from './results.js';

const $ = (id) => document.getElementById(id);
const pct = (v) => `${Math.round(v * 100)}%`;
const rows = (el, head, body) => {
  el.innerHTML = `<thead><tr>${head.map((h) => `<th scope="col">${esc(h)}</th>`).join('')}</tr></thead>
    <tbody>${body.map((r) => `<tr>${r.map((c) => `<td>${c}</td>`).join('')}</tr>`).join('')}</tbody>`;
};

const CONTROLS = [
  ['Drag or arrow keys', 'Look'], ['Wheel or + / -', 'Zoom 1x, 2x, 4x, 8x'],
  ['Click, or Space at the reticle', 'Mark a contact (empty sky is a false alarm)'], ['Click a radar track', 'Mark that track'],
  ['Tab / Shift+Tab', 'Cycle marked contacts'], ['1 to 5', 'Classify the selected contact'],
  ['T R J I C', 'Track, Report, Jam, Intercept, Take cover'], ['S', 'Sensor mode: day EO, night vision, thermal'],
  ['Q', 'Radar console with track table'], ['Space in the console', 'Mark the closest unmarked track'],
  ['[ and ]', 'Radar range 1.5, 3 or 6 km'], ['M', 'Mute or unmute'], ['P / Esc', 'Pause / end the session'],
];

async function load() {
  rows($('controls'), ['Input', 'Action'], CONTROLS.map(([k, v]) => [`<span class="key">${esc(k)}</span>`, esc(v)]));
  const r = await (await fetch('/api/rubric')).json();
  $('rubric-v').textContent = `v${r.version}`;
  const w = r.weights;
  $('flow').innerHTML = [`Detection × ${w.detection}`, `Classification × ${w.classification}`, `Engagement × ${w.engagement}`,
    'minus penalties', 'clamped 0 to 100', 'grade']
    .map((s, i) => `${i ? '<span class="arrow" aria-hidden="true">→</span>' : ''}<span class="chip"><strong>${esc(s)}</strong></span>`).join('');

  rows($('t-detection'), ['Time to mark', 'Branch', 'Score'], [
    ...r.detection_tiers.map((t, i, all) => [
      t.max_par_ratio === null ? `over ${all[i - 1].max_par_ratio}× par` : `up to ${t.max_par_ratio}× par`,
      esc(t.node.replaceAll('_', ' ')), pct(t.score)]),
    ['never marked (hostile)', 'missed', '0%'],
  ]);
  const cs = r.classification_scores;
  rows($('t-classification'), ['Your call', 'Branch', 'Score'], [
    ['exact type', 'exact', pct(cs.exact)],
    ['right family, wrong type', 'same family', pct(cs.same_family)],
    ['wrong family', 'wrong family', pct(cs.wrong_family)],
    ['hostile called benign or friendly', 'critical misclassification', `${pct(cs.wrong_family)} and −${r.penalties.critical}`],
  ]);
  const es = r.engagement_scores;
  rows($('t-engagement'), ['Situation', 'Score'], [
    ['Hostile: suitable, timely, worked', pct(es.correct_effective)],
    [`Hostile: suitable and timely, missed, then a suitable retry stopped it before ${r.geometry.late_range_m} m`, pct(es.correct_effective)],
    ['Hostile: suitable and timely, but the roll failed (decision credited)', pct(es.correct_failed_roll)],
    [`Hostile: late (inside ${r.geometry.late_range_m} m) or unsuitable`, pct(es.late_or_unsuitable)],
    ['Hostile: no response, or it breached the inner ring', pct(es.none_or_breach)],
    ['Not a threat: held fire (restraint)', pct(es.restraint)],
    ['Not a threat: engaged anyway', pct(es.unnecessary_engagement)],
    ['Friendly aircraft engaged', `${pct(es.unnecessary_engagement)} and −${r.penalties.critical}`],
  ]);
  const p = r.penalties;
  rows($('t-penalties'), ['Item', 'Value'], [
    ['False alarm', `−${p.false_alarm} each, at most −${p.false_alarm_cap}`],
    [`Breach (hostile reaches ${r.geometry.inner_ring_m} m)`, `−${p.breach} each`],
    ['Critical error', `−${p.critical} each`],
    ...r.grade_bands.map((g) => [`Grade ${esc(g.grade)}`, `${g.min} or more · ${esc(g.label)}`]),
  ]);
  const models = Object.keys(r.models);
  const engaging = Object.entries(r.responses).filter(([, v]) => v.engages);
  rows($('t-responses'), ['Drone type', 'True class', 'Suitable responses', ...engaging.map(([, v]) => `${v.label} chance`)],
    models.map((m) => [esc(m.replace('_', ' ')), esc(r.classes[r.models[m].true_class].label),
      esc((r.expected_responses[m] || []).map((x) => r.responses[x].label).join(', ') || 'hold fire'),
      ...engaging.map(([, v]) => pct(v.effectiveness[m] ?? 0))]));
}

load();

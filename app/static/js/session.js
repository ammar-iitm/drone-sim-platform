// Session review: ordered event timeline with the tree outcome and points behind each event.
import { esc, renderStages, renderPenalties, renderContacts, gradeBlock } from './results.js';

const $ = (id) => document.getElementById(id);
const id = document.querySelector('main').dataset.session;
const fmt = (t) => `${String(Math.floor(t / 60)).padStart(2, '0')}:${(t % 60).toFixed(1).padStart(4, '0')}`;

function describe(item, rubric) {
  const d = item.data || {};
  switch (item.type) {
    case 'mark': return item.contact_id ? `Mark ${item.contact_id}${d.via ? ' via ' + d.via : ''}` : `Mark empty sky${d.bearing != null ? ' at ' + d.bearing + '°' : ''}`;
    case 'classify': return `Classify ${item.contact_id} as ${rubric.classes[d.class]?.label || d.class}`;
    case 'respond': return `${rubric.responses[d.response]?.label || d.response} → ${item.contact_id}`;
    case 'sensor': return `Sensor: ${({ eo: 'Day EO', nv: 'Night vision', thermal: 'Thermal', radar: 'Radar console' })[d.mode] || d.mode}`;
    case 'breach': return `Breach: ${item.contact_id} reached the inner ring`;
    case 'neutralised': return `${item.contact_id} neutralised`;
    default: return item.type;
  }
}

async function load() {
  const [sRes, rRes] = await Promise.all([fetch(`/api/sessions/${id}`), fetch('/api/rubric')]);
  const s = await sRes.json();
  const rubric = await rRes.json();
  if (!sRes.ok) {
    $('head').innerHTML = `<div class="notice error">${esc(s.error)}</div> <a class="btn" href="/dashboard">Back to dashboard</a>`;
    return;
  }
  const r = s.result;
  document.title = `Session ${s.id} · ${s.scenario_name} · AEGIS`;
  $('head').innerHTML = `
    <div class="group">
      <div class="kv"><span class="label">AAR debrief · session ${s.id}</span><span class="value-lg">${esc(s.scenario_name.toUpperCase())}</span></div>
      <div class="kv"><span class="label">Trainee</span><span class="value green">${esc(s.callsign)} / ${esc(s.unit)}</span></div>
      <div class="kv"><span class="label">Date (UTC)</span><span class="value">${esc(s.started_at.replace('T', ' ').replace('Z', ''))}</span></div>
      <div class="kv"><span class="label">Seed · duration</span><span class="value">${s.seed} · ${fmt(s.duration_s)}</span></div>
    </div>
    <div class="group">${gradeBlock(r)}
      <div class="kv" style="gap:8px">
        <a class="btn primary" href="${esc(replayUrl(s))}">Run same seed again</a>
        <a class="btn" href="/api/sessions/${s.id}/export.csv" download>Export CSV</a>
        <a class="btn" href="/dashboard">Dashboard</a></div></div>`;
  $('rubric-version').textContent = `Rubric v${r.rubric_version}`;
  $('stages').innerHTML = renderStages(r);
  $('penalties').innerHTML = renderPenalties(r);
  $('contacts').innerHTML = renderContacts(r, rubric);
  $('event-count').textContent = `${r.timeline.length} entries`;
  $('timeline').innerHTML = r.timeline.map((item) => {
    const pts = item.notes.reduce((a, n) => a + (n.stage === 'penalty' ? n.points : 0), 0);
    const neg = item.notes.some((n) => n.stage === 'penalty' || n.points === 0);
    const notes = item.notes.map((n) => `<div class="note"><span class="badge ${n.points < 0 || n.points < 40 ? 'bad' : n.points < 75 ? 'warn' : 'good'}">
        ${esc(n.stage)} · ${esc(n.node.replaceAll('_', ' '))} · ${n.stage === 'penalty' ? n.points : n.points + '%'}</span> ${esc(n.reason)}</div>`).join('');
    return `<li class="${neg ? 'neg' : ''}"><span class="t">${fmt(item.t)}</span>
      <span class="what">${esc(describe(item, rubric))}</span><span class="value ${pts < 0 ? 'red' : ''}">${pts ? pts + ' pts' : ''}</span>${notes}</li>`;
  }).join('') || '<li><span></span><span>No events were recorded.</span></li>';
}

function replayUrl(s) {
  const q = new URLSearchParams({ callsign: s.callsign, unit: s.unit });
  if (s.params) Object.entries(s.params).forEach(([k, v]) => q.set(k, v));
  else q.set('id', s.scenario_id);
  return '/sim?' + q;
}

load();

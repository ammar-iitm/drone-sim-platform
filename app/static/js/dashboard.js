// AAR dashboard: unit overview, trainee progress, comparison, confusion matrix and session log.
import { esc, fmtDateIST } from './results.js';
import { t as tr } from './i18n.js'; // chart text is drawn on canvas, so translate it here

const $ = (id) => document.getElementById(id);
const METRICS = ['detection', 'classification', 'engagement'];
const css = getComputedStyle(document.documentElement);
const COLOR = Object.fromEntries(METRICS.map((m) => [m, css.getPropertyValue(`--series-${m}`).trim()]));
const store = {
  get(k) { try { return localStorage.getItem(k); } catch { return null; } },
  set(k, v) { try { localStorage.setItem(k, v); } catch { /* ignore */ } },
};
const charts = {};
let sessionsSort = { key: 'started_at', dir: -1 };
let sessionsRows = [];

Chart.defaults.color = '#b9ccb5';
Chart.defaults.font.family = css.getPropertyValue('--font-mono');
Chart.defaults.font.size = 12;
Chart.defaults.borderColor = '#2a2f2b';

// Direct labels at the end of each line (Visual Design: label lines, do not rely on colour).
const endLabels = {
  id: 'endLabels',
  afterDatasetsDraw(chart) {
    const { ctx } = chart;
    chart.data.datasets.forEach((ds, i) => {
      const meta = chart.getDatasetMeta(i);
      if (meta.hidden || !meta.data.length || ds.noLabel) return;
      const pt = meta.data[meta.data.length - 1];
      ctx.save();
      ctx.fillStyle = ds.borderColor;
      ctx.font = '700 12px ' + Chart.defaults.font.family;
      ctx.textBaseline = 'middle';
      ctx.fillText(ds.label.split(' ')[0], pt.x + 6, pt.y);
      ctx.restore();
    });
  },
};

function bindToggles() {
  document.querySelectorAll('.toggle').forEach((group) => {
    group.addEventListener('click', (e) => {
      const b = e.target.closest('button[data-view]');
      if (!b) return;
      const panel = group.closest('.panel');
      group.querySelectorAll('button').forEach((x) => x.setAttribute('aria-pressed', String(x === b)));
      panel.querySelectorAll('[data-pane]').forEach((p) => { p.hidden = p.dataset.pane !== b.dataset.view; });
    });
  });
}

function table(el, headers, rows) {
  el.innerHTML = `<thead><tr>${headers.map((h) => `<th scope="col">${esc(h)}</th>`).join('')}</tr></thead>
    <tbody>${rows.map((r) => `<tr>${r.map((c) => `<td>${c}</td>`).join('')}</tr>`).join('')}</tbody>`;
}

function fmtNum(v) { return v == null ? '--' : Number(v).toFixed(1); }
// Dates and callsigns never break across lines in table cells ("ATLAS-" / "2").
function nowrap(text) { return `<span class="nowrap">${esc(text)}</span>`; }
function date(s) { return `<span class="nowrap">${fmtDateIST(s, { compact: true })}</span>`; }

async function json(url) {
  const res = await fetch(url);
  const data = await res.json();
  if (!res.ok) throw new Error(data.error || res.statusText);
  return data;
}

async function loadUnits() {
  const trainees = await json('/api/trainees');
  const withSessions = trainees.filter((t) => t.sessions > 0);
  if (!withSessions.length) { $('empty').hidden = false; $('content').hidden = true; return null; }
  const units = [...new Set(withSessions.map((t) => t.unit))];
  const saved = store.get('dtt.dash.unit');
  $('unit').innerHTML = units.map((u) => `<option ${u === saved ? 'selected' : ''}>${esc(u)}</option>`).join('');
  return trainees;
}

async function loadUnit() {
  const unit = $('unit').value;
  store.set('dtt.dash.unit', unit);
  $('export-unit').href = `/api/analytics/unit/${encodeURIComponent(unit)}/export.csv`;
  const u = await json(`/api/analytics/unit/${encodeURIComponent(unit)}`);
  $('t-sessions').textContent = u.sessions;
  $('t-avg').textContent = fmtNum(u.averages.total);
  $('t-weak').textContent = u.weakest_skill ? u.weakest_skill.toUpperCase() : '--';
  $('t-weak-v').textContent = u.weakest_skill ? `Unit average ${fmtNum(u.averages[u.weakest_skill])} vs target ${u.target}` : '';
  $('t-breaches').textContent = u.breaches;

  const trained = u.trainees.filter((t) => t.sessions);
  const saved = store.get('dtt.dash.trainee');
  $('trainee').innerHTML = trained.map((t) => `<option value="${t.id}" ${String(t.id) === saved ? 'selected' : ''}>${esc(t.callsign)} (${t.sessions})</option>`).join('');

  const sorted = [...trained].sort((a, b) => b.total - a.total);
  charts.compare?.destroy();
  charts.compare = new Chart($('compare'), {
    type: 'bar',
    data: { labels: sorted.map((t) => t.callsign),
      datasets: [{ label: tr('Average score'), data: sorted.map((t) => t.total), backgroundColor: '#00e3fd', borderRadius: 4, barThickness: 14 }] },
    options: { indexAxis: 'y', maintainAspectRatio: false, scales: { x: { min: 0, max: 100 } }, plugins: { legend: { display: false } },
      interaction: { mode: 'index', axis: 'y', intersect: false } },
  });
  table($('compare-table'), ['Trainee', 'Sessions', 'Average', ...METRICS, 'Breaches'],
    sorted.map((t) => [nowrap(t.callsign), t.sessions, fmtNum(t.total), ...METRICS.map((m) => fmtNum(t[m])), t.breaches ?? 0]));
  $('weakest').innerHTML = '<div class="label" style="margin-top:12px">Weakest trainees</div>' +
    u.weakest_trainees.map((t) => `<div class="row"><span class="value">${esc(t.callsign)}</span><span class="badge ${t.total < 60 ? 'bad' : t.total < 80 ? 'warn' : 'good'}">${fmtNum(t.total)}</span></div>`).join('');

  table($('recent'), ['Date (IST)', 'Trainee', 'Scenario', 'Score', 'Grade'],
    u.recent.map((s) => [date(s.started_at), nowrap(s.callsign), `<a href="/dashboard/session/${s.id}">${esc(s.scenario_name)}</a>`, fmtNum(s.total), esc(s.grade)]));
  await loadTrainee();
}

async function loadTrainee() {
  const id = $('trainee').value;
  if (!id) return;
  store.set('dtt.dash.trainee', id);
  const a = await json(`/api/analytics/trainee/${id}`);
  const name = a.trainee.callsign;
  ['progress-name', 'confusion-name', 'sessions-name'].forEach((k) => { $(k).textContent = name; });
  const labels = a.sessions.map((_, i) => `S${i + 1}`);
  charts.progress?.destroy();
  charts.progress = new Chart($('progress'), {
    type: 'line',
    data: {
      labels,
      datasets: [
        ...METRICS.map((m) => ({ label: tr(m[0].toUpperCase() + m.slice(1)), data: a.series[m], borderColor: COLOR[m], backgroundColor: COLOR[m], borderWidth: 2, pointRadius: 3, tension: 0 })),
        { label: tr('Total, rolling mean of 3'), data: a.rolling.total, borderColor: '#e3e2e6', borderDash: [5, 4], borderWidth: 1.5, pointRadius: 0, noLabel: true },
      ],
    },
    options: { maintainAspectRatio: false, layout: { padding: { right: 118 } }, scales: { y: { min: 0, max: 100 } },
      interaction: { mode: 'index', intersect: false }, plugins: { legend: { position: 'bottom' } } },
    plugins: [endLabels],
  });
  table($('progress-table'), ['Session', 'Date (IST)', ...METRICS, 'Total', 'Rolling total'],
    a.sessions.map((s, i) => [labels[i], date(s.started_at), ...METRICS.map((m) => fmtNum(s[m])), fmtNum(s.total), fmtNum(a.rolling.total[i])]));
  const ch = a.change;
  $('progress-notes').textContent = `First to latest: total ${ch.total == null ? '--' : (ch.total >= 0 ? '+' : '') + ch.total} · ` +
    `mean time to detect ${a.mean_time_to_detect_s ?? '--'} s · false alarms per session ${a.false_alarms_per_session ?? '--'}`;

  // Confusion matrix: single-hue blue, counts printed in every cell.
  const { rows, columns, counts } = a.confusion;
  const max = Math.max(1, ...rows.flatMap((r) => columns.map((c) => counts[r][c])));
  const short = { RECON_UAS: 'Recon', ARMED_UAS: 'Armed', DECOY: 'Decoy', BIRD: 'Bird', FRIENDLY: 'Friendly', NOT_CLASSIFIED: 'None' };
  $('confusion').innerHTML = `<thead><tr><th scope="col">Truth \\ call</th>${columns.map((c) => `<th scope="col">${short[c]}</th>`).join('')}</tr></thead>
    <tbody>${rows.map((r) => `<tr><th scope="row">${short[r]}</th>${columns.map((c) => {
      const n = counts[r][c], alpha = n ? 0.15 + 0.75 * (n / max) : 0;
      const ring = r === c ? 'box-shadow: inset 0 0 0 1px #00ff66;' : '';
      return `<td class="cell" style="background: rgba(57,135,229,${alpha.toFixed(2)}); ${ring}">${n}</td>`;
    }).join('')}</tr>`).join('')}</tbody>`;

  sessionsRows = a.sessions;
  renderSessions();
}

function renderSessions() {
  const cols = [['started_at', 'Date (IST)'], ['scenario_name', 'Scenario'], ['total', 'Score'], ['grade', 'Grade'],
    ['detection', 'Det.'], ['classification', 'Class.'], ['engagement', 'Eng.'], ['breaches', 'Breaches'], ['false_alarms', 'False alarms']];
  const { key, dir } = sessionsSort;
  const rows = [...sessionsRows].sort((a, b) => (a[key] > b[key] ? 1 : a[key] < b[key] ? -1 : 0) * dir);
  $('sessions').innerHTML = `<thead><tr>${cols.map(([k, h]) => `<th scope="col" aria-sort="${k === key ? (dir > 0 ? 'ascending' : 'descending') : 'none'}">
      <button type="button" data-sort="${k}">${h}${k === key ? (dir > 0 ? ' ▲' : ' ▼') : ''}</button></th>`).join('')}</tr></thead>
    <tbody>${rows.map((s) => `<tr><td>${date(s.started_at)}</td><td><a href="/dashboard/session/${s.id}">${esc(s.scenario_name)}</a></td>
      <td>${fmtNum(s.total)}</td><td>${esc(s.grade)}</td>${METRICS.map((m) => `<td>${fmtNum(s[m])}</td>`).join('')}
      <td>${s.breaches}</td><td>${s.false_alarms}</td></tr>`).join('')}</tbody>`;
}

$('sessions').addEventListener('click', (e) => {
  const b = e.target.closest('button[data-sort]');
  if (!b) return;
  sessionsSort = { key: b.dataset.sort, dir: sessionsSort.key === b.dataset.sort ? -sessionsSort.dir : 1 };
  renderSessions();
});
$('unit').addEventListener('change', loadUnit);
$('trainee').addEventListener('change', loadTrainee);
bindToggles();

loadUnits().then((t) => t && loadUnit()).catch((err) => {
  $('empty').hidden = false;
  $('empty').innerHTML = `<div class="notice error">${esc(err.message)}</div>`;
  $('content').hidden = true;
});

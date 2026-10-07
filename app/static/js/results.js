// Score breakdown rendering, shared by the simulator score screen and the session review page.
import { badge, FAMILY_STATE } from './sim/marks.js';

export function esc(s) {
  return String(s ?? '').replace(/[&<>"']/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));
}

const STAGE_COLOR = { detection: 'var(--series-detection)', classification: 'var(--series-classification)', engagement: 'var(--series-engagement)' };

function outcomeBadge(points) {
  if (points >= 75) return `<span class="badge good">${points}%</span>`;
  if (points >= 40) return `<span class="badge warn">${points}%</span>`;
  return `<span class="badge bad">${points}%</span>`;
}

function trueState(c) {
  return { hostile: 'hostile', friendly: 'friendly', decoy: 'benign', benign: 'benign' }[c.threat] || 'unknown';
}

export function renderStages(result) {
  return ['detection', 'classification', 'engagement'].map((s) => {
    const v = result.stages[s];
    return `<div class="stage">
      <span class="label">${s} · weight ${result.weights[s]}</span>
      <span class="value">${v.toFixed(1)}%</span>
      <div class="bar" role="img" aria-label="${s} ${v.toFixed(1)} percent, target 80">
        <span style="width:${v}%;background:${STAGE_COLOR[s]}"></span><span class="target" style="left:80%"></span></div>
    </div>`;
  }).join('');
}

export function renderPenalties(result) {
  const p = result.penalties;
  return `<div class="stage"><span class="label">Weighted score</span><span class="value">${result.weighted.toFixed(1)}</span></div>
    <div class="stage"><span class="label">False alarms × ${p.false_alarms}</span><span class="value ${p.false_alarm_points ? 'amber' : ''}">−${p.false_alarm_points}</span></div>
    <div class="stage"><span class="label">Breaches × ${p.breaches}</span><span class="value ${p.breach_points ? 'red' : ''}">−${p.breach_points}</span></div>
    <div class="stage"><span class="label">Critical errors × ${p.critical_errors}</span><span class="value ${p.critical_points ? 'red' : ''}">−${p.critical_points}</span></div>
    <div class="stage"><span class="label">Total (clamped 0 to 100)</span><span class="value green">${result.total.toFixed(1)}</span></div>`;
}

export function renderContacts(result, rubric) {
  const label = (cls) => (rubric?.classes?.[cls]?.label) || cls;
  return result.contacts.map((c) => {
    if (!c.scored) {
      return `<article class="ccard"><div class="label data">${esc(c.id)} · ${esc(c.model.replace('_', ' '))}</div>
        ${badge(trueState(c))}<p class="muted">Not scored: a non-hostile contact that was never marked.</p></article>`;
    }
    const stages = ['detection', 'classification', 'engagement'].map((s) => `
      <div><div class="stage-name">${s} · ${esc(c[s].node.replaceAll('_', ' '))} ${outcomeBadge(Math.round(c[s].points * 100))}</div>
      <p>${esc(c[s].reason)}</p></div>`).join('');
    const flags = [c.breached ? '<span class="badge bad">Breach −10</span>' : '',
      ...c.critical.map(() => '<span class="badge bad">Critical −25</span>'),
      c.neutralised_t != null ? `<span class="badge good">Neutralised T+${c.neutralised_t.toFixed(1)} s</span>` : ''].join('');
    return `<article class="ccard">
      <div class="label data">${esc(c.id)} · ${esc(c.model.replace('_', ' '))} · truth: ${esc(label(c.true_class))}</div>
      <div class="path">${badge(trueState(c))}${flags}</div>
      <div class="path" aria-label="Decision tree path">${c.path.map((p) => `<span class="chip">${esc(p)}</span>`).join('')}</div>
      ${stages}
    </article>`;
  }).join('');
}

export function gradeBlock(result) {
  return `<div class="grade"><div class="label">Composite score</div>
    <div class="value-xl green">${result.total.toFixed(1)}<span class="label"> / 100</span></div>
    <div class="value-lg">${esc(result.grade)}</div><div class="label green">${esc(result.grade_label)}</div></div>`;
}

export { FAMILY_STATE };

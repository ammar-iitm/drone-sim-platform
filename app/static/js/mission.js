// Mission select: pick a trainee and a scripted or procedural scenario, then launch the simulator.
const $ = (id) => document.getElementById(id);
const store = {
  get(k) { try { return localStorage.getItem(k); } catch { return null; } },
  set(k, v) { try { localStorage.setItem(k, v); } catch { /* private mode */ } },
};

let selection = null; // { kind: 'scripted', id, name } | { kind: 'procedural', params, name }

function esc(s) {
  return String(s).replace(/[&<>"']/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));
}

function updateHeader() {
  const cs = $('callsign').value.trim().toUpperCase();
  const unit = $('unit').value.trim().toUpperCase();
  $('who').textContent = cs && unit ? `${cs} / ${unit}` : 'NOT SET';
  $('selected-name').textContent = selection ? selection.name.toUpperCase() : 'NONE';
  $('launch').disabled = !(cs && unit && selection);
}

function select(sel) {
  selection = sel;
  document.querySelectorAll('.card').forEach((c) => c.setAttribute('aria-pressed', String(c.dataset.id === sel.id)));
  updateHeader();
}

async function loadScripted() {
  const list = await (await fetch('/api/scenarios')).json();
  $('count-scripted').textContent = list.length;
  $('cards').innerHTML = list.map((s) => `
    <article class="card" role="listitem" data-id="${esc(s.id)}" aria-pressed="false">
      <button class="select" type="button" data-id="${esc(s.id)}" data-name="${esc(s.name)}">
        <span class="label data cyan">SCN-0${s.order} · ${esc(s.threat_summary)}</span>
        <h3>${esc(s.name)}</h3>
        <p>${esc(s.objective)}</p>
        <span class="tags">
          <span class="chip">${esc(s.time_of_day)}</span><span class="chip">${esc(s.terrain)}</span>
          <span class="chip ${s.degradation ? 'amber' : ''}">Degradation <strong>${s.degradation}</strong></span>
        </span>
      </button>
    </article>`).join('');
  $('cards').addEventListener('click', (e) => {
    const b = e.target.closest('button.select');
    if (b) select({ kind: 'scripted', id: b.dataset.id, name: b.dataset.name });
  });
}

async function loadUnits() {
  try {
    const trainees = await (await fetch('/api/trainees')).json();
    const units = [...new Set(trainees.map((t) => t.unit))];
    $('units').innerHTML = units.map((u) => `<option value="${esc(u)}">`).join('');
  } catch { /* first run */ }
}

function procParams() {
  const out = {};
  for (const el of $('proc-form').elements) {
    if (el.name && el.value !== '') out[el.name] = el.value;
  }
  return out;
}

async function preview() {
  const params = procParams();
  const res = await fetch('/api/scenario?' + new URLSearchParams(params));
  const data = await res.json();
  if (!res.ok) {
    $('preview').className = 'notice preview error';
    $('preview').textContent = data.error;
    return null;
  }
  const counts = {};
  data.contacts.forEach((c) => { counts[c.threat] = (counts[c.threat] || 0) + 1; });
  $('preview').className = 'notice preview';
  $('preview').innerHTML = `
    <div class="value cyan">${esc(data.name.toUpperCase())}</div>
    <div class="label data" style="margin-top:6px">${esc(data.id)} · ${Math.round(data.duration_s)} s ·
      ${counts.hostile || 0} hostile · ${counts.decoy || 0} decoy · ${counts.benign || 0} bird · ${counts.friendly || 0} friendly</div>`;
  return { params: data.params, name: data.name, id: data.id };
}

function launch() {
  if ($('launch').disabled) return;
  const callsign = $('callsign').value.trim();
  const unit = $('unit').value.trim();
  store.set('dtt.callsign', callsign);
  store.set('dtt.unit', unit);
  store.set('dtt.quality', $('quality').value);
  const q = new URLSearchParams({ callsign, unit });
  if ($('quality').value !== 'auto') q.set('quality', $('quality').value);
  if (selection.kind === 'scripted') q.set('id', selection.id);
  else Object.entries(selection.params).forEach(([k, v]) => q.set(k, v));
  location.href = '/sim?' + q;
}

$('callsign').value = store.get('dtt.callsign') || '';
$('unit').value = store.get('dtt.unit') || '';
$('quality').value = store.get('dtt.quality') || 'auto';
['callsign', 'unit'].forEach((id) => $(id).addEventListener('input', updateHeader));
$('difficulty').addEventListener('input', () => { $('difficulty-out').textContent = $('difficulty').value; });
$('reseed').addEventListener('click', () => { $('seed').value = Math.floor(Math.random() * 1e6); preview(); });
$('proc-form').addEventListener('change', preview);
$('use-proc').addEventListener('click', async () => {
  const p = await preview();
  if (p) select({ kind: 'procedural', id: p.id, params: p.params, name: p.name });
});
$('launch').addEventListener('click', launch);
document.addEventListener('keydown', (e) => {
  if (e.key === 'Enter' && !(e.target instanceof HTMLButtonElement)) { e.preventDefault(); launch(); }
});

loadScripted();
loadUnits();
preview();
updateHeader();

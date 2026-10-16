// Simulator: game loop, input, HUD and session submission.
// The browser only records raw events; the server rebuilds the scenario and scores them.
import * as THREE from '/static/vendor/three.module.js';
import { World, QUALITY_ORDER } from './world.js';
import { Sound } from './audio.js';
import { Radar, fmtR, pad3 } from './radar.js';
import { rollFor } from './rng.js';
import { positionAt, endTime, rangeAt, endsInside, bearingOf } from './path.js';
import { drawShape, badge, STATE_COLOR, STATE_LABEL, FAMILY_STATE } from './marks.js';
import { esc, renderStages, renderPenalties, renderContacts, gradeBlock } from '../results.js';
import { t as tr } from '../i18n.js'; // canvas text is not in the page, so translate it where it is drawn

const $ = (id) => document.getElementById(id);
const TICK = 1 / 30;
const UNSENT_KEY = 'dtt.unsent';
const DRONES = new Set(['quadcopter', 'hexacopter', 'fixed_wing']);
const MIN_SEPARATION_M = 22;
const swarmGroups = new Map(); // reused every frame: group -> live member meshes
const ZOOMS = [1, 2, 4, 8];
const MODES = ['eo', 'nv', 'thermal'];
const MODE_NAME = { eo: 'Day EO', nv: 'Night vision', thermal: 'Thermal' };
const MODE_FILTER = {
  eo: 'none',
  nv: 'grayscale(1) sepia(1) hue-rotate(62deg) saturate(3.5) brightness(1.35) contrast(1.1)',
  thermal: 'grayscale(1) contrast(1.2) brightness(1.6)',
};
const reducedMotion = matchMedia('(prefers-reduced-motion: reduce)').matches;
const round3 = (t) => Math.round(t * 1000) / 1000;
const fmt = (t) => `${String(Math.floor(t / 60)).padStart(2, '0')}:${String(Math.floor(t % 60)).padStart(2, '0')}`;

const query = new URLSearchParams(location.search);
// Fast-forward for instructor demos and automated tests (?speed=1..16). Scenario time drives everything.
const SPEED = Math.min(16, Math.max(1, Number(query.get('speed')) || 1));
// Quality: auto (start high, step down if the frame rate stays low) or a fixed level.
const QUALITY_MODE = ['auto', ...QUALITY_ORDER].includes(query.get('quality')) ? query.get('quality') : 'auto';
const trainee = { callsign: (query.get('callsign') || '').trim(), unit: (query.get('unit') || '').trim() };

const S = {
  scenario: null, rubric: null, world: null, radar: null,
  t: 0, acc: 0, last: 0, phase: 'loading', // loading | briefing | running | paused | confirm | submitting | done
  yaw: 0, pitch: 4, zoomIdx: 0, mode: 'eo', radarMode: false,
  status: new Map(),  // id -> { neutralisedT, breached, attempts, left }
  scatter: new Map(), // swarm group -> scenario time it was first engaged
  marked: new Map(),  // id -> { state, chosen, last, markedT }
  selected: null, events: [], held: new Set(),
  sound: new Sound(), lowFpsWindows: 0,
  listDirty: true, alertUntil: 0, toastTimer: 0, frames: 0, fpsT: 0, resolvedAt: null,
};
const tmp = [0, 0, 0];
const tmpV = new THREE.Vector3();
const ahead = new THREE.Vector3();
const raycaster = new THREE.Raycaster();

// ------------------------------------------------------------ screens

function screen(html, focusSel) {
  $('screen').hidden = false;
  $('screen-card').innerHTML = html;
  const f = focusSel && $('screen-card').querySelector(focusSel);
  if (f) f.focus({ preventScroll: true });
  $('screen-card').scrollTop = 0;
}
function hideScreen() {
  $('screen').hidden = true;
  $('view').focus();
}

function briefing() {
  const sc = S.scenario, env = sc.environment;
  const keys = [['Drag / Arrows', 'Look around'], ['Wheel / + −', 'Zoom 1x, 2x, 4x, 8x'], ['Click / Space', 'Mark a contact (empty sky is a false alarm)'],
    ['Radar click', 'Mark a radar track'], ['Tab', 'Cycle marked contacts'], ['1 – 5', 'Classify the selected contact'],
    ['T R J I C', 'Track, Report, Jam, Intercept, Take cover'], ['S', 'Sensor mode: EO, night vision, thermal'],
    ['Q', 'Radar console (full-screen scope and track table)'], ['Space in console', 'Mark the closest unmarked radar track'], ['M', 'Mute or unmute sound'], ['[ ]', 'Radar range 1.5, 3 or 6 km'], ['P / Esc', 'Pause / end session']];
  screen(`
    <div class="score-head"><div><div class="label cyan">${sc.kind === 'scripted' ? 'Scripted scenario' + (sc.params ? ' · variant ' + sc.params.vary : '') : 'Procedural · seed ' + sc.seed}</div>
      <h2 id="screen-title" class="panel-title" style="font-size:24px">${esc(sc.name)}</h2></div>
      <div class="path"><span class="chip">${env.time_of_day}</span><span class="chip">${env.terrain}</span>
      <span class="chip ${env.degradation ? 'amber' : ''}">Degradation <strong>${env.degradation}</strong></span>
      <span class="chip">${fmt(sc.duration_s)}</span></div></div>
    <div class="brief-grid">
      <div class="panel"><div class="panel-head"><h3 class="panel-title"><span class="tag">OBJ</span>Learning objective</h3></div>
        <div class="panel-body"><p style="margin:0;font-size:16px">${esc(sc.objective)}</p>
        <p class="label" style="margin-top:12px">Trainee ${esc(trainee.callsign.toUpperCase())} / ${esc(trainee.unit.toUpperCase())}</p></div></div>
      <div class="panel"><div class="panel-head"><h3 class="panel-title"><span class="tag">KEY</span>Controls</h3></div>
        <div class="panel-body keys">${keys.map(([k, v]) => `<span class="key">${k}</span><span>${v}</span>`).join('')}</div></div>
    </div>
    <div class="screen-actions"><button class="btn primary" id="begin">Begin exercise <kbd>Enter</kbd></button>
      <a class="btn" href="/mission">Back to mission select</a></div>`, '#begin');
  $('begin').addEventListener('click', start);
  S.phase = 'briefing';
}

function start() {
  S.sound.start();
  hideScreen();
  S.phase = 'running';
  S.last = performance.now();
}

function pause(on) {
  if (on && S.phase === 'running') {
    S.phase = 'paused';
    S.sound.rotor(0, false);
    screen(`<h2 id="screen-title" class="panel-title">Paused at T+${fmt(S.t)}</h2>
      <div class="screen-actions"><button class="btn primary" id="resume">Resume <kbd>P</kbd></button></div>`, '#resume');
    $('resume').addEventListener('click', () => pause(false));
  } else if (!on && S.phase === 'paused') {
    hideScreen();
    S.phase = 'running';
    S.last = performance.now();
  }
}

function confirmEnd() {
  if (S.phase !== 'running') return;
  S.phase = 'confirm';
  screen(`<h2 id="screen-title" class="panel-title">End the session now?</h2>
    <p>Hostile contacts that are still inbound will count as missed.</p>
    <div class="screen-actions"><button class="btn danger" id="end-yes">End and score <kbd>Enter</kbd></button>
    <button class="btn" id="end-no">Keep going <kbd>Esc</kbd></button></div>`, '#end-yes');
  $('end-yes').addEventListener('click', finish);
  $('end-no').addEventListener('click', () => { hideScreen(); S.phase = 'running'; S.last = performance.now(); });
}

// ------------------------------------------------------------ helpers

function isAlive(c, t) {
  const st = S.status.get(c.id);
  if (t < c.spawn_t || t >= endTime(c)) return false;
  return !(st.neutralisedT !== null && t >= st.neutralisedT);
}

function toast(text) {
  let el = document.querySelector('.toast');
  if (!el) { el = document.createElement('div'); el.className = 'toast'; el.setAttribute('role', 'status'); document.body.append(el); }
  el.textContent = text;
  clearTimeout(S.toastTimer);
  S.toastTimer = setTimeout(() => el.remove(), 2200);
}

function alertBanner(text) {
  $('alert').textContent = text;
  $('alert').hidden = false;
  S.alertUntil = S.t + 4;
}

function log(type, contactId, data = {}) {
  const ev = { t: round3(S.t), type, contact_id: contactId, data };
  S.events.push(ev);
  return ev;
}

function effectiveness(resp, c, t) {
  const spec = S.rubric.responses[resp];
  if (!spec.engages) return 0;
  let base = spec.effectiveness[c.model] ?? 0;
  const r = rangeAt(c, t);
  if (r === null) return 0;
  if (r > (spec.max_range_m ?? Infinity)) base *= spec.out_of_range_factor ?? 0;
  if (spec.fast_speed_mps && c.speed_mps > spec.fast_speed_mps) base *= spec.fast_factor ?? 1;
  return Math.round(base * 10000) / 10000;
}

function contactById(id) {
  return S.scenario.contacts.find((c) => c.id === id);
}

// ------------------------------------------------------------ marking and decisions

function mark(c, via) {
  if (S.marked.has(c.id)) { select(c.id); return; }
  log('mark', c.id, { via });
  S.marked.set(c.id, { state: 'unknown', chosen: null, last: null, markedT: S.t });
  select(c.id);
  S.sound.tick();
  toast(`${c.id} marked`);
}

function falseAlarm(px, py, via) {
  const el = $('view');
  const ndc = new THREE.Vector3((px / el.clientWidth) * 2 - 1, -(py / el.clientHeight) * 2 + 1, 0.5).unproject(S.world.camera);
  ndc.sub(S.world.camera.position);
  log('mark', null, { via, bearing: Math.round(bearingOf(ndc.x, ndc.z)) });
  S.sound.fail();
  toast('Nothing there: false alarm logged');
}

function screenPos(c, out) {
  const mesh = S.world.meshes.get(c.id);
  tmpV.copy(mesh.position).project(S.world.camera);
  if (tmpV.z > 1 || tmpV.z < -1) return false;
  const el = $('view');
  out.x = (tmpV.x + 1) / 2 * el.clientWidth;
  out.y = (1 - tmpV.y) / 2 * el.clientHeight;
  return true;
}

function occluded(c) {
  const mesh = S.world.meshes.get(c.id);
  const cam = S.world.camera.position;
  const dir = tmpV.copy(mesh.position).sub(cam);
  const d = dir.length();
  raycaster.set(cam, dir.normalize());
  raycaster.far = d - 3;
  return raycaster.intersectObjects(S.world.occluders, false).length > 0;
}

function markAt(px, py, via) {
  const vr = S.scenario.environment.visual_range_m;
  const p = { x: 0, y: 0 };
  let best = null, bestD = Infinity;
  for (const c of S.scenario.contacts) {
    if (!isAlive(c, S.t)) continue;
    const mesh = S.world.meshes.get(c.id);
    const d = mesh.position.distanceTo(S.world.camera.position);
    if (d > vr * 1.02 || !screenPos(c, p)) continue;
    const sizePx = (mesh.userData.size * mesh.scale.x) / S.world.metresPerPixel(d);
    const tol = Math.max(16, sizePx / 2 + 8);
    const sd = Math.hypot(p.x - px, p.y - py);
    if (sd <= tol && sd < bestD && !occluded(c)) { best = c; bestD = sd; }
  }
  if (best) mark(best, via); else falseAlarm(px, py, via);
}

function select(id) {
  S.selected = id;
  S.listDirty = true;
  updateButtons();
}

function cycle(dir) {
  const ids = [...S.marked.keys()].filter((id) => isAlive(contactById(id), S.t));
  if (!ids.length) { toast('No live marked contacts'); return; }
  const i = ids.indexOf(S.selected);
  select(ids[(i + dir + ids.length) % ids.length]);
}

function classify(cls) {
  const id = S.selected;
  if (!id || !S.marked.has(id)) { toast('Select a marked contact first'); return; }
  log('classify', id, { class: cls });
  const m = S.marked.get(id);
  m.chosen = cls;
  m.state = FAMILY_STATE[S.rubric.classes[cls].family] || 'unknown';
  S.listDirty = true;
  toast(`${id}: ${S.rubric.classes[cls].label}`);
}

function respond(resp) {
  const id = S.selected;
  const c = id && contactById(id);
  if (!c || !S.marked.has(id)) { toast('Select a marked contact first'); return; }
  if (!isAlive(c, S.t)) { toast(`${id} is no longer active`); return; }
  const ev = log('respond', id, { response: resp });
  const spec = S.rubric.responses[resp];
  const m = S.marked.get(id);
  if (spec.engages) {
    if (c.swarm && !S.scatter.has(c.swarm.group)) S.scatter.set(c.swarm.group, ev.t);
    const st = S.status.get(id);
    const eff = effectiveness(resp, c, ev.t);
    const ok = rollFor(S.scenario.seed, id, st.attempts) < eff;
    st.attempts += 1;
    m.last = `${spec.label} ${ok ? 'hit' : 'failed'}`;
    if (ok) {
      st.neutralisedT = ev.t;
      S.sound.chime();
      toast(`${id} neutralised (${spec.label})`);
    } else {
      S.sound.fail();
      toast(`${spec.label} failed against ${id}`);
    }
  } else {
    m.last = spec.label;
    S.sound.chime();
    toast(`${id}: ${spec.label}`);
  }
  S.listDirty = true;
  updateButtons();
}

function setMode(mode) {
  if (S.radarMode) toggleConsole(false);
  S.mode = mode;
  S.world.setSensorMode(mode);
  $('gl').style.filter = MODE_FILTER[mode];
  $('vignette').classList.toggle('on', mode === 'nv');
  for (const id of ['mode-title', 'hud-mode']) $(id).textContent = MODE_NAME[mode];
  $('sensor-readout').textContent = MODE_NAME[mode].toUpperCase();
  if (S.phase === 'running') log('sensor', null, { mode });
}

function toggleMute() {
  S.sound.setMuted(!S.sound.muted);
  $('btn-mute').innerHTML = `${S.sound.muted ? 'Sound off' : 'Sound on'} <kbd>M</kbd>`;
  $('btn-mute').setAttribute('aria-pressed', String(S.sound.muted));
  toast(S.sound.muted ? 'Sound muted' : 'Sound on');
}

/** Keyboard path on the radar: mark the closest live track that is not marked yet. */
function markNearestTrack() {
  const row = S.radar.rows().find((r) => !S.marked.has(r.contactId) && isAlive(contactById(r.contactId), S.t));
  if (row) mark(contactById(row.contactId), 'radar');
  else toast('No unmarked radar tracks');
}

function toggleConsole(on = !S.radarMode) {
  S.radarMode = on;
  $('view').classList.toggle('radar-mode', on);
  $('sim').classList.toggle('console', on);
  $('radar-big').hidden = !on;
  $('radar-wrap').hidden = on;
  $('track-table').hidden = !on;
  if (on) renderTrackTable();
  const name = on ? 'Radar console' : MODE_NAME[S.mode];
  for (const id of ['mode-title', 'hud-mode']) $(id).textContent = name;
  $('sensor-readout').textContent = name.toUpperCase();
  if (S.phase === 'running') log('sensor', null, { mode: on ? 'radar' : S.mode });
  S.listDirty = true;
}

/** Click on a radar scope: a track or return from a real contact marks it; a lone return is a false alarm. */
function radarPick(canvas, x, y) {
  const hit = S.radar.pick(canvas, x, y);
  if (!hit) return;
  if (hit.contactId) {
    const c = contactById(hit.contactId);
    if (isAlive(c, S.t)) mark(c, 'radar'); else toast('Track lost');
  } else {
    log('mark', null, { via: 'radar' });
    S.sound.fail();
    toast('Clutter or noise, no target: false alarm logged');
  }
}

function renderTrackTable() {
  const rows = S.radar.rows();
  $('track-table').innerHTML = rows.length ? `<table class="data"><thead><tr><th scope="col">Track</th><th scope="col">Range</th>
    <th scope="col">Brg</th><th scope="col">Alt m</th><th scope="col">m/s</th><th scope="col">Hdg</th><th scope="col">Size</th><th scope="col">Mark</th></tr></thead><tbody>
    ${rows.map((r) => {
      const m = S.marked.get(r.contactId);
      return `<tr aria-selected="${r.contactId === S.selected}"><td><button type="button" data-cid="${r.contactId}">${r.track}</button>${r.coasting ? ' <span class="muted">coast</span>' : ''}</td>
        <td>${fmtR(r.range)}</td><td>${pad3(r.bearing)}°</td><td>${Math.round(r.alt)}</td><td>${Math.round(r.speed)}</td>
        <td>${r.heading === null ? '---' : pad3(r.heading) + '°'}</td><td>${r.size}</td><td>${m ? badge(m.state) + ' ' + r.contactId : '<span class="muted">unmarked</span>'}</td></tr>`;
    }).join('')}</tbody></table>` : '<p class="contact-list"><span class="empty" style="display:block">No radar tracks. A track forms after 2 hits in 3 sweeps.</span></p>';
}

// ------------------------------------------------------------ HUD widgets

function buildButtons() {
  $('classify-buttons').innerHTML = Object.entries(S.rubric.classes).map(([k, v]) =>
    `<button class="btn" type="button" data-class="${k}">${esc(v.label)} <kbd>${v.key}</kbd></button>`).join('');
  $('respond-buttons').innerHTML = Object.entries(S.rubric.responses).map(([k, v]) =>
    `<button class="btn ${v.engages ? 'engage' : ''}" type="button" data-response="${k}">${esc(v.label)} <kbd>${v.key}</kbd></button>`).join('');
  $('classify-buttons').addEventListener('click', (e) => {
    const b = e.target.closest('button'); if (b && S.phase === 'running') { classify(b.dataset.class); $('view').focus(); }
  });
  $('respond-buttons').addEventListener('click', (e) => {
    const b = e.target.closest('button'); if (b && S.phase === 'running') { respond(b.dataset.response); $('view').focus(); }
  });
}

function updateButtons() {
  const id = S.selected;
  const c = id && contactById(id);
  const live = c && isAlive(c, S.t);
  $('sel-label').textContent = id ? `· ${id}${live ? '' : ' (inactive)'}` : 'no contact selected';
  document.querySelectorAll('#classify-buttons button').forEach((b) => { b.disabled = !id; });
  document.querySelectorAll('#respond-buttons button').forEach((b) => { b.disabled = !live; });
}

function renderList() {
  const rows = [...S.marked.entries()].map(([id, m]) => {
    const c = contactById(id);
    const st = S.status.get(id);
    const status = st.neutralisedT !== null ? 'Neutralised' : st.breached ? 'Breached' : isAlive(c, S.t) ? 'Active' : 'Gone';
    const r = rangeAt(c, S.t);
    positionAt(c, S.t, tmp);
    const where = r !== null ? `RNG ${Math.round(r / 10) * 10} m · BRG ${String(Math.round(bearingOf(tmp[0], tmp[2]))).padStart(3, '0')}°` : '';
    const cls = m.chosen ? S.rubric.classes[m.chosen].label : 'Unclassified';
    return `<li><button type="button" data-id="${id}" aria-pressed="${id === S.selected}">
      ${badge(m.state)}<span class="cid">${id}</span><span class="label">${status}</span>
      <span class="meta">${where}${where ? ' · ' : ''}${esc(cls)}${m.last ? ' · ' + esc(m.last) : ''}</span></button></li>`;
  });
  $('contacts').innerHTML = rows.length ? rows.join('') : '<li class="empty">No contacts marked yet. Click a contact in the view or a radar track.</li>';
  S.listDirty = false;
}

// ------------------------------------------------------------ simulation tick

function tick() {
  S.t += TICK;
  const turn = 40 * TICK / ZOOMS[S.zoomIdx];
  if (S.held.has('ArrowLeft')) S.yaw -= turn;
  if (S.held.has('ArrowRight')) S.yaw += turn;
  if (S.held.has('ArrowUp')) S.pitch = Math.min(60, S.pitch + turn);
  if (S.held.has('ArrowDown')) S.pitch = Math.max(-10, S.pitch - turn);

  S.radar.update(S.t, isAlive);

  const inner = S.rubric.geometry.inner_ring_m;
  let unresolved = 0;
  let lastSpawn = 0;
  for (const c of S.scenario.contacts) {
    lastSpawn = Math.max(lastSpawn, c.spawn_t);
    if (c.threat !== 'hostile') continue;
    const st = S.status.get(c.id);
    if (st.neutralisedT !== null || st.breached) continue;
    if (S.t >= endTime(c)) {
      if (endsInside(c, inner)) {
        st.breached = true;
        log('breach', c.id);
        alertBanner(`Breach: ${c.id} reached the inner ring`);
        S.sound.alert();
        S.listDirty = true;
      }
      continue;
    }
    unresolved += 1;
  }
  let nearest = Infinity, fast = false;
  for (const c of S.scenario.contacts) {
    if (!DRONES.has(c.model) || !isAlive(c, S.t)) continue;
    const r = rangeAt(c, S.t);
    if (r !== null && r < nearest) { nearest = r; fast = c.model === 'fixed_wing'; }
  }
  S.sound.rotor(Math.pow(Math.max(0, 1 - nearest / 1500), 2), fast);
  if (S.alertUntil && S.t > S.alertUntil) { $('alert').hidden = true; S.alertUntil = 0; }
  if (S.t >= S.scenario.duration_s) { finish(); return; }
  if (unresolved === 0 && S.t > lastSpawn) {
    S.resolvedAt ??= S.t;
    if (S.t - S.resolvedAt > 3) finish();
  }
}

// ------------------------------------------------------------ rendering

let noisePattern = null;
function makeNoise(ctx) {
  const c = document.createElement('canvas');
  c.width = c.height = 128;
  const g = c.getContext('2d');
  const img = g.createImageData(128, 128);
  for (let i = 0; i < img.data.length; i += 4) {
    const v = Math.random() * 255;
    img.data[i] = img.data[i + 1] = img.data[i + 2] = v;
    img.data[i + 3] = 255;
  }
  g.putImageData(img, 0, 0);
  return ctx.createPattern(c, 'repeat');
}

function sizeCanvas(cv, w, h) {
  const dpr = Math.min(window.devicePixelRatio || 1, 2);
  if (cv.width !== Math.round(w * dpr) || cv.height !== Math.round(h * dpr)) {
    cv.width = Math.round(w * dpr); cv.height = Math.round(h * dpr);
  }
  const ctx = cv.getContext('2d');
  ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
  return ctx;
}

function drawFrame() {
  const w = S.world, cam = w.camera, t = S.t;
  cam.rotation.y = -S.yaw * Math.PI / 180;
  cam.rotation.x = S.pitch * Math.PI / 180;

  const vr = S.scenario.environment.visual_range_m;
  const view = $('view');
  const vw = view.clientWidth, vh = view.clientHeight;
  const brg = ((S.yaw % 360) + 360) % 360;
  const scopeOpts = { t, yaw: brg, fov: cam.fov * cam.aspect, marked: S.marked, selectedId: S.selected };
  if (S.radarMode) {
    S.radar.draw($('radar-big'), { ...scopeOpts, big: true });
    drawReadouts(t, brg);
    return;
  }
  for (const list of swarmGroups.values()) list.length = 0;
  for (const c of S.scenario.contacts) {
    const mesh = w.meshes.get(c.id);
    if (!isAlive(c, t) || !positionAt(c, t, tmp)) { mesh.visible = false; continue; }
    if (c.swarm) {
      if (!swarmGroups.has(c.swarm.group)) swarmGroups.set(c.swarm.group, []);
      swarmGroups.get(c.swarm.group).push(mesh);
    }
    w.wobble(c, t, tmp);
    // Swarm separation: once any member is engaged, the group spreads out over 3 s (visual only;
    // the server scores the formation path, and 40 m is well inside every scoring threshold).
    const t0 = c.swarm && S.scatter.get(c.swarm.group);
    if (typeof t0 === 'number' && t >= t0) {
      const f = Math.min(1, (t - t0) / 3), a = (c.wobble_seed % 360) * Math.PI / 180;
      tmp[0] += Math.cos(a) * 40 * f; tmp[1] += 10 * f * Math.sin(a * 3); tmp[2] += Math.sin(a) * 40 * f;
    }
    mesh.position.set(tmp[0], tmp[1], tmp[2]);
    const d = mesh.position.distanceTo(cam.position);
    mesh.visible = d < vr * 1.05;
    if (!mesh.visible) continue;
    if (c.model !== 'balloon' && positionAt(c, t + 0.5, tmp)) mesh.lookAt(ahead.set(tmp[0], tmp[1], tmp[2]));
    mesh.scale.setScalar(Math.max(1, (6 * w.metresPerPixel(d)) / mesh.userData.size));
    if (mesh.userData.wings) {
      const a = Math.sin(t * 13 + mesh.userData.phase[0]) * 0.7;
      mesh.userData.wings[0].rotation.z = a;
      mesh.userData.wings[1].rotation.z = -a;
    }
    if (mesh.userData.nav) mesh.userData.nav.visible = (t % 1.2) < 0.18;
  }
  separate();
  w.render();

  // Marker overlay (not affected by the sensor filter).
  const ctx = sizeCanvas($('overlay'), vw, vh);
  ctx.clearRect(0, 0, vw, vh);
  ctx.font = '700 14px ui-monospace, Menlo, monospace';
  ctx.textBaseline = 'middle';
  const p = { x: 0, y: 0 };
  for (const [id, m] of S.marked) {
    const c = contactById(id);
    const st = S.status.get(id);
    if (st.neutralisedT !== null && t - st.neutralisedT < 3) {
      if (positionAt(c, st.neutralisedT, tmp)) {
        tmpV.set(tmp[0], tmp[1], tmp[2]).project(cam);
        if (tmpV.z < 1) {
          const x = (tmpV.x + 1) / 2 * vw, y = (1 - tmpV.y) / 2 * vh;
          ctx.strokeStyle = '#00ff66'; ctx.lineWidth = 2;
          ctx.beginPath(); ctx.moveTo(x - 8, y - 8); ctx.lineTo(x + 8, y + 8); ctx.moveTo(x + 8, y - 8); ctx.lineTo(x - 8, y + 8); ctx.stroke();
          ctx.fillStyle = '#00ff66'; ctx.fillText(`${id} NEUTRALISED`, x + 14, y);
        }
      }
      continue;
    }
    if (!isAlive(c, t) || !w.meshes.get(id).visible || !screenPos(c, p)) continue;
    if (p.x < -20 || p.y < -20 || p.x > vw + 20 || p.y > vh + 20) continue;
    const y = p.y - 22;
    drawShape(ctx, m.state, p.x, y, 7, STATE_COLOR[m.state]);
    const text = `${id} · ${tr(STATE_LABEL[m.state])}`;
    const tw = ctx.measureText(text).width;
    ctx.fillStyle = 'rgba(13, 14, 17, 0.78)'; ctx.fillRect(p.x + 12, y - 10, tw + 10, 20);
    ctx.fillStyle = STATE_COLOR[m.state]; ctx.fillText(text, p.x + 17, y);
    if (id === S.selected) {
      const r = reducedMotion ? 14 : 13 + Math.sin(performance.now() / 180) * 2;
      ctx.strokeStyle = '#ffffff'; ctx.lineWidth = 2;
      ctx.beginPath(); ctx.arc(p.x, p.y, r, 0, Math.PI * 2); ctx.stroke();
    }
  }

  // Sensor noise and grain.
  const env = S.scenario.environment;
  const level = env.noise * 0.55 + (S.mode === 'nv' ? 0.12 : 0) + (S.mode === 'thermal' ? 0.05 : 0);
  const nctx = sizeCanvas($('noise'), vw, vh);
  nctx.clearRect(0, 0, vw, vh);
  if (level > 0) {
    noisePattern ??= makeNoise(nctx);
    nctx.globalAlpha = level;
    nctx.translate(Math.random() * 128, Math.random() * 128);
    nctx.fillStyle = noisePattern;
    nctx.fillRect(-128, -128, vw + 256, vh + 256);
    nctx.globalAlpha = 1;
  }

  S.radar.draw($('radar'), scopeOpts);
  drawReadouts(t, brg);
}

function drawReadouts(t, brg) {
  $('brg').textContent = `BRG ${String(Math.round(brg) % 360).padStart(3, '0')}°`;
  $('elev').textContent = `ELV ${S.pitch >= 0 ? '+' : ''}${Math.round(S.pitch)}°`;
  $('zoom').textContent = `ZOOM ${ZOOMS[S.zoomIdx]}x`;
  $('clock').textContent = fmt(t);
  $('elapsed').textContent = `${fmt(t)} / ${fmt(S.scenario.duration_s)}`;
  $('radar-status').textContent = S.radar.status();
  if (S.radarMode && Math.floor(t * 2) !== Math.floor((t - TICK) * 2)) renderTrackTable();
  if (S.listDirty || Math.floor(t * 2) !== Math.floor((t - TICK) * 2)) { renderList(); updateButtons(); }
}

/** Swarm avoidance: push apart any two members of a group closer than the minimum separation.
 * Stateless (recomputed from the path each frame), so it never drifts and stays deterministic. */
function separate() {
  for (const members of swarmGroups.values()) {
    for (let pass = 0; pass < 3; pass++) {
      for (let i = 0; i < members.length; i++) {
        for (let j = i + 1; j < members.length; j++) {
          const a = members[i].position, b = members[j].position;
          const dx = a.x - b.x, dy = a.y - b.y, dz = a.z - b.z;
          const d = Math.hypot(dx, dy, dz);
          if (d >= MIN_SEPARATION_M || d < 1e-3) continue;
          const k = (MIN_SEPARATION_M - d) / (2 * d);
          a.x += dx * k; a.y += dy * k; a.z += dz * k;
          b.x -= dx * k; b.y -= dy * k; b.z -= dz * k;
        }
      }
    }
  }
}

function showQuality() {
  $('quality').textContent = `${QUALITY_MODE === 'auto' ? 'Auto · ' : ''}${S.world.quality}`.toUpperCase();
}

/** Auto quality: after 3 s (six half-second windows) under 35 fps, step down one level. Never steps up. */
function autoQuality(fps) {
  if (QUALITY_MODE !== 'auto') return;
  S.lowFpsWindows = fps < 35 ? S.lowFpsWindows + 1 : 0;
  const i = QUALITY_ORDER.indexOf(S.world.quality);
  if (S.lowFpsWindows >= 6 && i < QUALITY_ORDER.length - 1) {
    S.world.setQuality(QUALITY_ORDER[i + 1]);
    S.lowFpsWindows = 0;
    showQuality();
    toast(`Quality lowered to ${S.world.quality} to keep the frame rate up`);
  }
}

function loop(now) {
  requestAnimationFrame(loop);
  if (!S.world) return;
  if (S.phase === 'running') {
    S.acc += Math.min(0.25, (now - S.last) / 1000) * SPEED;
    S.last = now;
    while (S.acc >= TICK && S.phase === 'running') { tick(); S.acc -= TICK; }
  }
  drawFrame();
  S.frames += 1;
  if (now - S.fpsT > 500) {
    const fps = Math.round((S.frames * 1000) / (now - S.fpsT));
    $('fps').textContent = fps;
    S.frames = 0;
    S.fpsT = now;
    if (S.phase === 'running' && !S.radarMode) autoQuality(fps);
  }
}

// ------------------------------------------------------------ finish and score

async function finish() {
  if (['submitting', 'done'].includes(S.phase)) return;
  S.phase = 'submitting';
  S.sound.rotor(0, false);
  screen('<h2 id="screen-title" class="panel-title">Scoring on the server…</h2><p class="label">Raw events only are sent; the server rebuilds the scenario and scores them.</p>');
  S.clientId ??= `${Date.now()}-${Math.random().toString(36).slice(2, 8)}`;
  const body = { client_id: S.clientId, callsign: trainee.callsign, unit: trainee.unit, scenario_id: S.scenario.id,
    params: S.scenario.params, events: S.events, ended_t: round3(Math.min(S.t, S.scenario.duration_s)) };
  try {
    const res = await fetch('/api/sessions', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(body) });
    const data = await res.json();
    if (!res.ok) throw new Error(data.error || res.statusText);
    S.phase = 'done';
    try {
      const saved = JSON.parse(localStorage.getItem(UNSENT_KEY) || '[]').filter((b) => b.client_id !== body.client_id);
      localStorage.setItem(UNSENT_KEY, JSON.stringify(saved));
    } catch { /* storage unavailable */ }
    showResults(data);
  } catch (err) {
    S.phase = 'confirm';
    // Keep the raw events in this browser so the session is not lost; Mission select offers to resend it.
    let kept = false;
    try {
      const saved = JSON.parse(localStorage.getItem(UNSENT_KEY) || '[]').filter((b) => b.client_id !== body.client_id);
      saved.push(body);
      localStorage.setItem(UNSENT_KEY, JSON.stringify(saved.slice(-10)));
      kept = true;
    } catch { /* storage unavailable */ }
    screen(`<h2 id="screen-title" class="panel-title">Could not save the session</h2>
      <div class="notice error">${esc(err.message)}</div>
      <p>${kept ? 'The session is kept in this browser. Try again now, or resend it later from Mission select.' : 'Try again before leaving this page.'}</p>
      <div class="screen-actions"><button class="btn primary" id="retry">Try again</button></div>`, '#retry');
    $('retry').addEventListener('click', () => { S.phase = 'running'; finish(); });
  }
}

function showResults(r) {
  const sc = S.scenario;
  const again = location.pathname + location.search;
  screen(`
    <div class="score-head">
      <div><div class="label cyan">Session ${r.session_id} · ${esc(r.trainee.callsign)} / ${esc(r.trainee.unit)}</div>
        <h2 id="screen-title" class="panel-title" style="font-size:24px">${esc(sc.name)} · debrief</h2>
        <div class="label">Seed ${sc.seed} · ${esc(sc.id)} · ended T+${fmt(r.ended_t)}</div></div>
      ${gradeBlock(r)}
    </div>
    <div class="brief-grid">
      <div class="panel"><div class="panel-head"><h3 class="panel-title"><span class="tag">01</span>Evaluation breakdown</h3></div>
        <div class="panel-body">${renderStages(r)}</div></div>
      <div class="panel"><div class="panel-head"><h3 class="panel-title"><span class="tag">02</span>Penalties and total</h3></div>
        <div class="panel-body">${renderPenalties(r)}</div></div>
    </div>
    <div class="panel"><div class="panel-head"><h3 class="panel-title"><span class="tag">03</span>Decision tree by contact</h3></div>
      <div class="panel-body contact-cards">${renderContacts(r, S.rubric)}</div></div>
    <div class="screen-actions">
      <a class="btn primary" href="${esc(again)}" id="again">Run same seed again</a>
      <a class="btn" href="/dashboard/session/${r.session_id}">Session review</a>
      <a class="btn" href="/dashboard">AAR dashboard</a>
      <a class="btn" href="/mission">Mission select</a>
    </div>`, '#again');
}

// ------------------------------------------------------------ input

function bindInput() {
  const view = $('view');
  let down = null;
  view.addEventListener('contextmenu', (e) => e.preventDefault());
  view.addEventListener('pointerdown', (e) => {
    if (S.phase !== 'running') return;
    down = { x: e.clientX, y: e.clientY, moved: false };
    view.setPointerCapture(e.pointerId);
    view.focus();
  });
  view.addEventListener('pointermove', (e) => {
    if (!down) return;
    const dx = e.clientX - down.x, dy = e.clientY - down.y;
    if (!down.moved && Math.hypot(dx, dy) < 5) return;
    down.moved = true;
    const k = 0.12 / ZOOMS[S.zoomIdx];
    S.yaw -= e.movementX * k;
    S.pitch = Math.max(-10, Math.min(60, S.pitch + e.movementY * k));
  });
  view.addEventListener('pointerup', (e) => {
    if (down && !down.moved && S.phase === 'running') {
      const r = view.getBoundingClientRect();
      if (S.radarMode) radarPick($('radar-big'), e.clientX - r.left, e.clientY - r.top);
      else markAt(e.clientX - r.left, e.clientY - r.top, 'view');
    }
    down = null;
  });
  view.addEventListener('wheel', (e) => {
    e.preventDefault();
    S.zoomIdx = Math.max(0, Math.min(ZOOMS.length - 1, S.zoomIdx + (e.deltaY < 0 ? 1 : -1)));
    S.world.setZoom(ZOOMS[S.zoomIdx]);
  }, { passive: false });

  $('radar').addEventListener('click', (e) => {
    if (S.phase !== 'running') return;
    const r = e.currentTarget.getBoundingClientRect();
    radarPick($('radar'), e.clientX - r.left, e.clientY - r.top);
  });
  $('track-table').addEventListener('click', (e) => {
    const b = e.target.closest('button[data-cid]');
    if (!b || S.phase !== 'running') return;
    const c = contactById(b.dataset.cid);
    if (isAlive(c, S.t)) mark(c, 'radar'); else toast('Track lost');
  });
  $('btn-console').addEventListener('click', () => { if (S.phase === 'running') toggleConsole(); $('view').focus(); });
  $('btn-range').addEventListener('click', () => { S.radar.scaleIdx = (S.radar.scaleIdx + 1) % 3; $('view').focus(); });
  $('contacts').addEventListener('click', (e) => {
    const b = e.target.closest('button[data-id]');
    if (b) { select(b.dataset.id); $('view').focus(); }
  });
  $('btn-sensor').addEventListener('click', () => { setMode(MODES[(MODES.indexOf(S.mode) + 1) % MODES.length]); $('view').focus(); });
  $('btn-pause').addEventListener('click', () => pause(S.phase === 'running'));
  $('btn-end').addEventListener('click', confirmEnd);
  $('btn-mute').addEventListener('click', () => { toggleMute(); $('view').focus(); });
  $('btn-mute').innerHTML = `${S.sound.muted ? 'Sound off' : 'Sound on'} <kbd>M</kbd>`;

  const classKeys = () => Object.fromEntries(Object.entries(S.rubric.classes).map(([k, v]) => [v.key, k]));
  const respKeys = () => Object.fromEntries(Object.entries(S.rubric.responses).map(([k, v]) => [v.key.toLowerCase(), k]));

  document.addEventListener('keydown', (e) => {
    if (e.target instanceof HTMLInputElement || e.metaKey || e.ctrlKey || e.altKey) return;
    if (e.target instanceof HTMLAnchorElement && e.key === 'Enter') return; // let links (e.g. the skip link) work
    const key = e.key;
    if (S.phase === 'briefing' && key === 'Enter') { e.preventDefault(); start(); return; }
    if (S.phase === 'paused' && (key === 'p' || key === 'P' || key === 'Enter')) { e.preventDefault(); pause(false); return; }
    if (S.phase === 'confirm' && key === 'Escape') { e.preventDefault(); $('end-no')?.click(); return; }
    if (S.phase === 'confirm' && key === 'Enter') { e.preventDefault(); $('end-yes')?.click(); return; }
    if (S.phase !== 'running') return;

    if (key.startsWith('Arrow')) { S.held.add(key); e.preventDefault(); return; }
    if (key === ' ') {
      e.preventDefault();
      if (S.radarMode) markNearestTrack();
      else markAt(view.clientWidth / 2, view.clientHeight / 2, 'reticle');
      return;
    }
    if (key === '[' || key === ']') { S.radar.cycleScale(key === ']' ? 1 : -1); return; }
    if (key === 'Tab') { e.preventDefault(); cycle(e.shiftKey ? -1 : 1); return; }
    if (key === '+' || key === '=') { S.zoomIdx = Math.min(ZOOMS.length - 1, S.zoomIdx + 1); S.world.setZoom(ZOOMS[S.zoomIdx]); return; }
    if (key === '-' || key === '_') { S.zoomIdx = Math.max(0, S.zoomIdx - 1); S.world.setZoom(ZOOMS[S.zoomIdx]); return; }
    if (key === 'Escape') { e.preventDefault(); confirmEnd(); return; }
    const lower = key.toLowerCase();
    if (lower === 'p') { pause(true); return; }
    if (lower === 'q') { toggleConsole(); return; }
    if (lower === 'm') { toggleMute(); return; }
    if (lower === 's') { setMode(MODES[(MODES.indexOf(S.mode) + 1) % MODES.length]); return; }
    const cls = classKeys()[key];
    if (cls) { classify(cls); return; }
    const resp = respKeys()[lower];
    if (resp) { e.preventDefault(); respond(resp); }
  });
  document.addEventListener('keyup', (e) => S.held.delete(e.key));
  window.addEventListener('blur', () => S.held.clear());

  new ResizeObserver(() => {
    const v = $('view');
    S.world.resize(v.clientWidth, v.clientHeight);
  }).observe($('view'));
}

// ------------------------------------------------------------ boot

async function boot() {
  if (!trainee.callsign || !trainee.unit) {
    screen(`<h2 id="screen-title" class="panel-title">No trainee or scenario selected</h2>
      <p>Pick a trainee callsign, unit and scenario first.</p>
      <div class="screen-actions"><a class="btn primary" href="/mission" id="go">Mission select</a></div>`, '#go');
    return;
  }
  const scenarioQuery = new URLSearchParams(query);
  scenarioQuery.delete('callsign');
  scenarioQuery.delete('unit');
  scenarioQuery.delete('speed');
  scenarioQuery.delete('quality');
  try {
    const [sRes, rRes] = await Promise.all([fetch('/api/scenario?' + scenarioQuery), fetch('/api/rubric')]);
    const sc = await sRes.json();
    if (!sRes.ok) throw new Error(sc.error);
    S.scenario = sc;
    S.rubric = await rRes.json();
  } catch (err) {
    screen(`<h2 id="screen-title" class="panel-title">Could not load the scenario</h2><div class="notice error">${esc(err.message)}</div>
      <div class="screen-actions"><a class="btn" href="/mission">Mission select</a></div>`);
    return;
  }
  const sc = S.scenario, env = sc.environment;
  for (const c of sc.contacts) S.status.set(c.id, { neutralisedT: null, breached: false, attempts: 0 });
  $('trainee').textContent = `${trainee.callsign.toUpperCase()} / ${trainee.unit.toUpperCase()}`;
  $('scenario-name').textContent = sc.name.toUpperCase();
  $('env').textContent = `${env.time_of_day} · ${env.terrain} · vis ${env.visual_range_m} m`.toUpperCase();
  $('degr-label').textContent = `Degradation ${env.degradation}`;
  document.title = `${sc.name} · Simulator · AEGIS`;
  if (SPEED > 1) {
    $('speed-chip').hidden = false;
    $('speed').textContent = `×${SPEED}`;
  }

  S.world = new World($('gl'), sc, QUALITY_MODE === 'auto' ? 'high' : QUALITY_MODE);
  showQuality();
  S.radar = new Radar(sc, reducedMotion);
  const v = $('view');
  S.world.resize(v.clientWidth, v.clientHeight);
  setMode('eo');
  buildButtons();
  updateButtons();
  bindInput();
  briefing();
}

requestAnimationFrame(loop);
boot();
window.__sim = S; // exposed for the browser tests
S.autoQuality = autoQuality;
// Test hooks: the same decision functions the keyboard and mouse call.
window.__simApi = { mark: (id) => mark(contactById(id), 'radar'), classify, respond, select: (id) => select(id),
  contactById, isAlive, range: (id) => rangeAt(contactById(id), S.t),
  /** Clear line of sight from the post to where a contact is at scenario time t (null if not flying). */
  lineOfSight(id, t) {
    if (!positionAt(contactById(id), t, tmp)) return null;
    const cam = S.world.camera.position;
    const dir = new THREE.Vector3(tmp[0], tmp[1], tmp[2]).sub(cam);
    const d = dir.length();
    raycaster.set(cam, dir.normalize());
    raycaster.far = d - 3;
    return raycaster.intersectObjects(S.world.occluders, false).length === 0;
  } };

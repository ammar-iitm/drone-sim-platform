// AAR replay: a top-down map of the session, rebuilt from the scenario and the event log.
// Shows every contact's true identity and track, the trainee's marks and responses, and where
// each contact was neutralised or breached, with play / pause, speed and a time scrubber.
import { positionAt, endTime } from './sim/path.js';
import { drawShape, STATE_COLOR, STATE_LABEL } from './sim/marks.js';

const THREAT_STATE = { hostile: 'hostile', friendly: 'friendly', benign: 'benign', decoy: 'benign' };
const EVENT_FLASH_S = 2.5; // how long a response line or false-alarm ray stays on the map
const SPEEDS = [1, 4, 16];
const fmt = (t) => `${String(Math.floor(t / 60)).padStart(2, '0')}:${(t % 60).toFixed(1).padStart(4, '0')}`;

export class Replay {
  constructor(root, { scenario, result, rubric }) {
    this.root = root;
    this.scenario = scenario;
    this.timeline = result.timeline;
    this.duration = result.ended_t || scenario.duration_s;
    this.geo = rubric.geometry;
    this.t = 0;
    this.speed = 4;
    this.playing = false;
    this.contacts = scenario.contacts;
    this.status = new Map(result.contacts.map((c) => [c.id, c]));
    this.firstMark = new Map();
    for (const e of this.timeline) {
      if (e.type === 'mark' && e.contact_id && !this.firstMark.has(e.contact_id)) this.firstMark.set(e.contact_id, e.t);
    }
    // Map scale: fit the farthest waypoint, with the rings drawn in whole kilometres.
    let far = 1000;
    for (const c of this.contacts) for (const w of c.waypoints) far = Math.max(far, Math.hypot(w[0], w[2]));
    this.extent = Math.min(6000, Math.ceil(far / 500) * 500);
    this.build();
    this.seek(0);
  }

  build() {
    this.root.innerHTML = `
      <div class="replay-stage"><canvas class="replay-map" role="img" aria-label="Top-down replay of the session"></canvas></div>
      <div class="replay-bar">
        <button type="button" class="btn primary" data-act="play" aria-keyshortcuts="Space">Play</button>
        <button type="button" class="btn" data-act="speed" aria-label="Replay speed">×${this.speed}</button>
        <input type="range" class="replay-scrub" min="0" max="${this.duration}" step="0.1" value="0" aria-label="Replay time">
        <span class="value replay-time" aria-live="off"></span>
      </div>
      <p class="replay-caption label" aria-live="polite"></p>
      <ul class="replay-legend label">
        ${['hostile', 'benign', 'friendly'].map((s) => `<li><svg aria-hidden="true" width="14" height="14"><use href="#s-${s}"/></svg> ${STATE_LABEL[s]}</li>`).join('')}
        <li><span class="swatch ring"></span> Marked by trainee</li>
        <li><span class="swatch line"></span> Response</li>
        <li><span class="swatch fa"></span> False alarm</li>
      </ul>`;
    this.canvas = this.root.querySelector('canvas');
    this.playBtn = this.root.querySelector('[data-act=play]');
    this.speedBtn = this.root.querySelector('[data-act=speed]');
    this.scrub = this.root.querySelector('.replay-scrub');
    this.timeEl = this.root.querySelector('.replay-time');
    this.caption = this.root.querySelector('.replay-caption');
    this.playBtn.addEventListener('click', () => this.toggle());
    this.speedBtn.addEventListener('click', () => {
      this.speed = SPEEDS[(SPEEDS.indexOf(this.speed) + 1) % SPEEDS.length];
      this.speedBtn.textContent = `×${this.speed}`;
    });
    this.scrub.addEventListener('input', () => { this.pause(); this.seek(Number(this.scrub.value)); });
    this.root.addEventListener('keydown', (e) => {
      if (e.target === this.scrub) return;
      if (e.key === ' ') { e.preventDefault(); this.toggle(); }
    });
    new ResizeObserver(() => this.draw()).observe(this.canvas);
  }

  toggle() { if (this.playing) this.pause(); else this.play(); }

  play() {
    if (this.t >= this.duration) this.seek(0);
    this.playing = true;
    this.playBtn.textContent = 'Pause';
    let last = performance.now();
    const step = (now) => {
      if (!this.playing) return;
      const t = Math.min(this.duration, this.t + ((now - last) / 1000) * this.speed);
      last = now;
      this.seek(t);
      if (t >= this.duration) this.pause(); else requestAnimationFrame(step);
    };
    requestAnimationFrame(step);
  }

  pause() {
    this.playing = false;
    this.playBtn.textContent = 'Play';
  }

  seek(t) {
    this.t = Math.max(0, Math.min(this.duration, t));
    this.scrub.value = this.t;
    this.timeEl.textContent = `T+${fmt(this.t)} / ${fmt(this.duration)}`;
    const recent = this.timeline.filter((e) => e.t <= this.t).at(-1);
    this.caption.textContent = recent ? `Last event at T+${fmt(recent.t)}: ${this.describe(recent)}` : 'Before the first event.';
    this.draw();
  }

  describe(e) {
    const d = e.data || {};
    const outcome = e.notes?.length ? ` (${e.notes.map((n) => n.node.replaceAll('_', ' ')).join(', ')})` : '';
    switch (e.type) {
      case 'mark': return (e.contact_id ? `marked ${e.contact_id}` : 'marked empty sky') + outcome;
      case 'classify': return `classified ${e.contact_id} as ${d.class}${outcome}`;
      case 'respond': return `${d.response} on ${e.contact_id}${outcome}`;
      case 'neutralised': return `${e.contact_id} neutralised`;
      case 'breach': return `${e.contact_id} breached the inner ring`;
      case 'sensor': return `sensor changed to ${d.mode}`;
      default: return e.type;
    }
  }

  draw() {
    const cv = this.canvas;
    const w = cv.clientWidth, h = cv.clientHeight;
    if (!w || !h) return;
    const dpr = window.devicePixelRatio || 1;
    if (cv.width !== Math.round(w * dpr) || cv.height !== Math.round(h * dpr)) {
      cv.width = Math.round(w * dpr); cv.height = Math.round(h * dpr);
    }
    const ctx = cv.getContext('2d');
    ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
    ctx.clearRect(0, 0, w, h);
    const cx = w / 2, cy = h / 2, k = (Math.min(w, h) / 2 - 18) / this.extent;
    const toScreen = (p) => [cx + p[0] * k, cy + p[2] * k]; // north (-z) is up

    // Range rings, the late line and the inner ring.
    ctx.font = '12px ui-monospace, Menlo, monospace';
    ctx.lineWidth = 1;
    for (let r = 1000; r <= this.extent; r += 1000) this.ring(ctx, cx, cy, r * k, '#2d3a2c', [], `${r / 1000} km`);
    this.ring(ctx, cx, cy, this.geo.late_range_m * k, '#ffb95f', [4, 4], `${this.geo.late_range_m} m late`);
    this.ring(ctx, cx, cy, this.geo.inner_ring_m * k, '#ff6b5e', [2, 3], '');
    ctx.fillStyle = '#849581'; ctx.textAlign = 'center';
    ctx.fillText('N', cx, 12);
    ctx.fillStyle = '#00ff66'; ctx.fillRect(cx - 3, cy - 3, 6, 6);

    // Response lines and false-alarm rays that happened in the last few seconds.
    for (const e of this.timeline) {
      if (e.t > this.t || this.t - e.t > EVENT_FLASH_S) continue;
      const fade = 1 - (this.t - e.t) / EVENT_FLASH_S;
      if (e.type === 'respond' && e.contact_id) {
        const c = this.contacts.find((x) => x.id === e.contact_id);
        const p = [0, 0, 0];
        if (c && positionAt(c, e.t, p)) this.line(ctx, cx, cy, ...toScreen(p), `rgba(0, 227, 253, ${fade})`, []);
      } else if (e.type === 'mark' && !e.contact_id && typeof e.data?.bearing === 'number') {
        const a = (e.data.bearing * Math.PI) / 180, len = Math.min(w, h) / 2;
        this.line(ctx, cx, cy, cx + Math.sin(a) * len, cy - Math.cos(a) * len, `rgba(255, 185, 95, ${fade})`, [6, 4]);
      }
    }

    // Contacts: faint track so far, then the current position with its true identity.
    const p = [0, 0, 0];
    for (const c of this.contacts) {
      if (this.t < c.spawn_t) continue;
      const st = this.status.get(c.id) || {};
      const end = endTime(c);
      const gone = st.neutralised_t != null && this.t >= st.neutralised_t;
      const breached = st.breached && this.t >= end;
      if (!gone && !breached && this.t >= end) continue; // flew out of the area
      const state = THREAT_STATE[c.threat] || 'unknown';
      const color = STATE_COLOR[state];
      const stopT = Math.min(this.t, end - 0.01, st.neutralised_t ?? Infinity);
      ctx.strokeStyle = color; ctx.globalAlpha = 0.35; ctx.lineWidth = 1.5; ctx.setLineDash([]);
      ctx.beginPath();
      for (let s = c.spawn_t; s <= stopT; s += 1) {
        if (!positionAt(c, s, p)) break;
        const [x, y] = toScreen(p);
        if (s === c.spawn_t) ctx.moveTo(x, y); else ctx.lineTo(x, y);
      }
      if (positionAt(c, stopT, p)) ctx.lineTo(...toScreen(p));
      ctx.stroke();
      ctx.globalAlpha = 1;
      if (!positionAt(c, stopT, p)) continue;
      const [x, y] = toScreen(p);
      ctx.globalAlpha = gone || breached ? 0.55 : 1;
      drawShape(ctx, state, x, y, 7, color);
      ctx.globalAlpha = 1;
      if (this.firstMark.has(c.id) && this.t >= this.firstMark.get(c.id)) {
        ctx.strokeStyle = '#ffffff'; ctx.lineWidth = 1.5; ctx.setLineDash([]);
        ctx.beginPath(); ctx.arc(x, y, 12, 0, Math.PI * 2); ctx.stroke();
      }
      if (gone) this.cross(ctx, x, y, '#00ff66');
      if (breached) this.cross(ctx, x, y, '#ff6b5e');
      ctx.fillStyle = '#e3e2e6'; ctx.textAlign = 'left';
      ctx.fillText(`${c.id}${gone ? ' DOWN' : breached ? ' BREACH' : ''}`, x + 12, y - 10);
    }
  }

  ring(ctx, cx, cy, r, color, dash, label) {
    ctx.strokeStyle = color; ctx.setLineDash(dash);
    ctx.beginPath(); ctx.arc(cx, cy, r, 0, Math.PI * 2); ctx.stroke();
    ctx.setLineDash([]);
    if (label) { ctx.fillStyle = color; ctx.textAlign = 'left'; ctx.fillText(label, cx + 4, cy - r - 4); }
  }

  line(ctx, x1, y1, x2, y2, color, dash) {
    ctx.strokeStyle = color; ctx.lineWidth = 2; ctx.setLineDash(dash);
    ctx.beginPath(); ctx.moveTo(x1, y1); ctx.lineTo(x2, y2); ctx.stroke();
    ctx.setLineDash([]);
  }

  cross(ctx, x, y, color) {
    ctx.strokeStyle = color; ctx.lineWidth = 2.5; ctx.setLineDash([]);
    ctx.beginPath(); ctx.moveTo(x - 9, y - 9); ctx.lineTo(x + 9, y + 9); ctx.moveTo(x + 9, y - 9); ctx.lineTo(x - 9, y + 9); ctx.stroke();
  }
}

/** The /api/scenario query that rebuilds the scenario a session was flown on. */
export function scenarioQuery(session) {
  const q = new URLSearchParams();
  if (!String(session.scenario_id).startsWith('proc-')) q.set('id', session.scenario_id);
  if (session.params) Object.entries(session.params).forEach(([k, v]) => q.set(k, v));
  return q;
}

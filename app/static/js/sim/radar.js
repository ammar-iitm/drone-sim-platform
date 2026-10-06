// Surveillance radar simulation.
//
// A rotating beam (30 rpm) can only detect a contact as it sweeps past it. Detection
// probability follows a simplified radar equation: the range for a 50% chance scales with
// the fourth root of radar cross-section (RCS), shrinks with weather degradation, and drops
// for low targets in ground clutter (much worse among buildings). Detections become plots
// with range and bearing noise; ground clutter and random false returns produce plots too.
// A tracker starts a track after 2 hits in 3 sweeps, smooths it with an alpha-beta filter
// and drops it after 3 missed sweeps. The radar never reports the true class.
//
// Everything here is visual training aid only; marks made on the radar go to the server as
// ordinary "mark" events and the server scores them.
import { mulberry32 } from './rng.js';
import { positionAt, bearingOf } from './path.js';
import { drawShape, STATE_COLOR } from './marks.js';

export const RCS_M2 = { quadcopter: 0.01, hexacopter: 0.05, fixed_wing: 0.1, balloon: 0.3, bird: 0.01, friendly_aircraft: 5 };
const R0 = 4000;            // metres at which a 1 m² target has a 50% detection chance in clear air
const PERIOD = 2;           // seconds per antenna rotation (30 rpm)
const DECAY = PERIOD * 1.5; // phosphor afterglow time constant
const SCALES = [1500, 3000, 6000];
const ALPHA = 0.55, BETA = 0.25;
const GREEN = '0, 255, 102';

const fmtR = (m) => (m >= 1000 ? `${(m / 1000).toFixed(2)} km` : `${Math.round(m)} m`);
const pad3 = (d) => String(Math.round(d) % 360).padStart(3, '0');

export class Radar {
  constructor(scenario, reducedMotion) {
    this.env = scenario.environment;
    this.contacts = scenario.contacts;
    this.urban = this.env.terrain === 'urban';
    this.rand = mulberry32((scenario.seed ^ 0x9e3779b9) >>> 0);
    this.reducedMotion = reducedMotion;
    this.az = 0;
    this.lastAz = null;
    this.plots = [];
    this.tracks = new Map();   // contact id -> track
    this.history = new Map();  // contact id -> { hits: [bool], last: {x, z, t} }
    this.nextTrack = 1;
    this.scaleIdx = 1;
    this.falseRate = 0.4 + 2.5 * this.env.noise + 0.6 * this.env.degradation; // false returns per rotation
    this.clutter = this.makeClutter();
    this.picks = new WeakMap(); // canvas -> clickable items in screen space
    this.pos = [0, 0, 0];
  }

  // ------------------------------------------------------------ simulation

  makeClutter() {
    const rnd = mulberry32((this.env.terrain_seed ^ 0xc1a7) >>> 0);
    const cells = [];
    const n = this.urban ? 90 : 34;
    for (let i = 0; i < n; i++) {
      const b = rnd() * 360;
      const r = this.urban ? 150 + Math.pow(rnd(), 1.5) * 1700 : 250 + Math.pow(rnd(), 1.3) * 2300;
      const rad = (b * Math.PI) / 180;
      cells.push({ b, x: Math.sin(rad) * r, z: -Math.cos(rad) * r, amp: (this.urban ? 0.2 : 0.14) + rnd() * 0.25 });
    }
    return cells;
  }

  gauss() {
    const u = Math.max(1e-9, this.rand()), v = this.rand();
    return Math.sqrt(-2 * Math.log(u)) * Math.cos(2 * Math.PI * v);
  }

  /** Probability of detecting a contact on one pass of the beam. */
  pd(c, r, alt) {
    const r50 = R0 * Math.pow(RCS_M2[c.model], 0.25) * (1 - 0.12 * this.env.degradation);
    let p = 1 / (1 + Math.pow(r / r50, 8));
    if (alt < 40 && r > 300) p *= this.urban ? 0.35 : 0.6; // ground clutter and masking
    return p * (1 - this.env.radar_dropout);
  }

  crossed(b, prev, now) {
    const span = (now - prev + 360) % 360;
    const d = (b - prev + 360) % 360;
    return d > 0 && d <= span;
  }

  /** Advance the antenna to scenario time t. Called on every fixed logic tick. */
  update(t, isAlive) {
    this.az = ((t / PERIOD) * 360) % 360;
    if (this.lastAz === null) { this.lastAz = this.az; return; }
    const prev = this.lastAz, now = this.az;
    const span = (now - prev + 360) % 360;

    for (const c of this.contacts) {
      if (!isAlive(c, t) || !positionAt(c, t, this.pos)) {
        this.tracks.delete(c.id);
        this.history.delete(c.id);
        continue;
      }
      const [x, alt, z] = this.pos;
      const r = Math.hypot(x, z);
      const b = bearingOf(x, z);
      if (!this.crossed(b, prev, now)) continue;
      // Always draw the same four numbers per pass so the random stream stays aligned.
      const u = this.rand(), n1 = this.gauss(), n2 = this.gauss(), n3 = this.gauss();
      const p = this.pd(c, r, alt);
      const hit = u < p;
      const h = this.history.get(c.id) || { hits: [], last: null };
      h.hits.push(hit);
      if (h.hits.length > 3) h.hits.shift();
      this.history.set(c.id, h);
      const tr = this.tracks.get(c.id);

      if (!hit) {
        if (tr && ++tr.misses > 3) this.tracks.delete(c.id);
        continue;
      }
      const sr = 8 + 30 * this.env.noise + 0.008 * r;
      const sb = (0.5 + 2 * this.env.noise) * Math.PI / 180;
      const mr = Math.max(20, r + n1 * sr), mb = (b * Math.PI) / 180 + n2 * sb;
      const mx = Math.sin(mb) * mr, mz = -Math.cos(mb) * mr;
      const malt = Math.max(0, alt + n3 * (12 + 0.02 * r));
      const amp = Math.min(1, 0.45 + 0.55 * p + 0.1 * Math.log10(RCS_M2[c.model] * 100));
      this.plots.push({ x: mx, z: mz, born: t, amp, contactId: c.id });

      if (tr) {
        const dt = Math.max(0.5, t - tr.t);
        const px = tr.x + tr.vx * dt, pz = tr.z + tr.vz * dt;
        const rx = mx - px, rz = mz - pz;
        tr.x = px + ALPHA * rx; tr.z = pz + ALPHA * rz;
        tr.vx += (BETA / dt) * rx; tr.vz += (BETA / dt) * rz;
        tr.alt = tr.alt * 0.6 + malt * 0.4;
        tr.t = t; tr.misses = 0; tr.amp = amp; tr.hits += 1;
        tr.trail.push([mx, mz]);
        if (tr.trail.length > 8) tr.trail.shift();
      } else if (h.last && h.hits.filter(Boolean).length >= 2) {
        const dt = Math.max(0.5, t - h.last.t);
        this.tracks.set(c.id, {
          id: `T${String(this.nextTrack++).padStart(2, '0')}`, contactId: c.id,
          x: mx, z: mz, vx: (mx - h.last.x) / dt, vz: (mz - h.last.z) / dt, alt: malt,
          t, misses: 0, amp, hits: 2, size: RCS_M2[c.model] < 0.03 ? 'S' : RCS_M2[c.model] < 1 ? 'M' : 'L',
          trail: [[h.last.x, h.last.z], [mx, mz]],
        });
      }
      h.last = { x: mx, z: mz, t };
    }

    // Ground clutter returns as the beam passes each cell.
    for (const cell of this.clutter) {
      if (!this.crossed(cell.b, prev, now)) continue;
      const a = cell.amp * (0.4 + 0.6 * this.rand());
      if (a > 0.12) this.plots.push({ x: cell.x + this.gauss() * 15, z: cell.z + this.gauss() * 15, born: t, amp: a, contactId: null });
    }
    // Random false returns (noise, interference) inside the swept sector.
    if (this.rand() < (this.falseRate * span) / 360) {
      const b = (prev + this.rand() * span) * Math.PI / 180;
      const r = 200 + this.rand() * 2800;
      this.plots.push({ x: Math.sin(b) * r, z: -Math.cos(b) * r, born: t, amp: 0.35 + 0.4 * this.rand(), contactId: null });
    }
    this.lastAz = now;
    const cutoff = t - DECAY * 3;
    if (this.plots.length && this.plots[0].born < cutoff) this.plots = this.plots.filter((p) => p.born >= cutoff);
  }

  // ------------------------------------------------------------ queries

  get scale() { return SCALES[this.scaleIdx]; }
  cycleScale(dir) { this.scaleIdx = Math.max(0, Math.min(SCALES.length - 1, this.scaleIdx + dir)); }

  readout(tr) {
    const range = Math.hypot(tr.x, tr.z);
    const speed = Math.hypot(tr.vx, tr.vz);
    return { track: tr.id, range, bearing: bearingOf(tr.x, tr.z), alt: tr.alt, speed,
      heading: speed > 0.5 ? bearingOf(tr.vx, tr.vz) : null, size: tr.size, coasting: tr.misses > 0 };
  }

  trackForContact(id) { return this.tracks.get(id); }

  status() {
    return `30 RPM · ${this.scale / 1000} KM · ${this.tracks.size} TRK`;
  }

  // ------------------------------------------------------------ drawing

  /**
   * Draw the PPI scope onto a canvas. opts: { t, yaw, fov, marked, selectedId, big }.
   */
  draw(canvas, opts) {
    const { t, yaw, fov, marked, selectedId, big } = opts;
    const w = canvas.clientWidth, h = canvas.clientHeight || w;
    const dpr = Math.min(window.devicePixelRatio || 1, 2);
    if (canvas.width !== Math.round(w * dpr) || canvas.height !== Math.round(h * dpr)) {
      canvas.width = Math.round(w * dpr); canvas.height = Math.round(h * dpr);
    }
    const ctx = canvas.getContext('2d');
    ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
    ctx.fillStyle = '#0a0c0b';
    ctx.fillRect(0, 0, w, h);
    const cx = w / 2, cy = h / 2;
    const R = Math.min(w, h) / 2 - (big ? 34 : 16);
    const k = R / this.scale;
    const toScreen = (x, z) => [cx + x * k, cy + z * k];
    const fontPx = big ? 14 : 12;
    ctx.font = `${fontPx}px ui-monospace, Menlo, monospace`;

    // Optical field of view.
    const yawRad = ((yaw - 90) * Math.PI) / 180, half = (fov / 2) * Math.PI / 180;
    ctx.fillStyle = 'rgba(0, 227, 253, 0.07)';
    ctx.beginPath(); ctx.moveTo(cx, cy); ctx.arc(cx, cy, R, yawRad - half, yawRad + half); ctx.closePath(); ctx.fill();

    // Rings and bearing ticks.
    ctx.strokeStyle = 'rgba(0, 255, 102, 0.22)'; ctx.lineWidth = 1;
    for (let i = 1; i <= 4; i++) { ctx.beginPath(); ctx.arc(cx, cy, (R * i) / 4, 0, Math.PI * 2); ctx.stroke(); }
    for (let d = 0; d < 360; d += 10) {
      const a = ((d - 90) * Math.PI) / 180, len = d % 30 ? 5 : 10;
      ctx.beginPath();
      ctx.moveTo(cx + Math.cos(a) * R, cy + Math.sin(a) * R);
      ctx.lineTo(cx + Math.cos(a) * (R - len), cy + Math.sin(a) * (R - len));
      ctx.stroke();
    }
    ctx.fillStyle = '#b9ccb5'; ctx.textAlign = 'center'; ctx.textBaseline = 'middle';
    const labels = big ? [...Array(12)].map((_, i) => [i * 30, pad3(i * 30)]) : [[0, 'N'], [90, 'E'], [180, 'S'], [270, 'W']];
    for (const [d, txt] of labels) {
      const a = ((d - 90) * Math.PI) / 180;
      ctx.fillText(txt, cx + Math.cos(a) * (R + (big ? 18 : 9)), cy + Math.sin(a) * (R + (big ? 18 : 9)));
    }
    ctx.textAlign = 'left';
    for (let i = 1; i <= 4; i++) {
      ctx.fillStyle = 'rgba(185, 204, 181, 0.7)';
      ctx.fillText(fmtR((this.scale * i) / 4), cx + 4, cy - (R * i) / 4 + fontPx * 0.7);
    }

    // Sweep with afterglow.
    const az = ((this.az - 90) * Math.PI) / 180;
    if (!this.reducedMotion) {
      const slices = 18, fan = (40 * Math.PI) / 180;
      for (let i = 0; i < slices; i++) {
        const a0 = az - fan + (fan * i) / slices, a1 = az - fan + (fan * (i + 1)) / slices;
        ctx.fillStyle = `rgba(${GREEN}, ${(0.16 * (i + 1)) / slices})`;
        ctx.beginPath(); ctx.moveTo(cx, cy); ctx.arc(cx, cy, R, a0, a1); ctx.closePath(); ctx.fill();
      }
    }
    ctx.strokeStyle = `rgba(${GREEN}, 0.8)`; ctx.lineWidth = 1.5;
    ctx.beginPath(); ctx.moveTo(cx, cy); ctx.lineTo(cx + Math.cos(az) * R, cy + Math.sin(az) * R); ctx.stroke();

    // Main-bang clutter at the post and the inner ring.
    const g = ctx.createRadialGradient(cx, cy, 0, cx, cy, Math.max(6, 150 * k));
    g.addColorStop(0, `rgba(${GREEN}, 0.35)`); g.addColorStop(1, `rgba(${GREEN}, 0)`);
    ctx.fillStyle = g; ctx.beginPath(); ctx.arc(cx, cy, Math.max(6, 150 * k), 0, Math.PI * 2); ctx.fill();
    ctx.strokeStyle = 'rgba(255, 107, 94, 0.7)'; ctx.setLineDash([3, 3]);
    ctx.beginPath(); ctx.arc(cx, cy, Math.max(3, 120 * k), 0, Math.PI * 2); ctx.stroke(); ctx.setLineDash([]);

    // Plots (returns), fading with phosphor decay.
    const picks = [];
    const dot = big ? 3.2 : 2.3;
    for (const p of this.plots) {
      const inten = p.amp * Math.exp(-(t - p.born) / DECAY);
      if (inten < 0.04) continue;
      const [x, y] = toScreen(p.x, p.z);
      if (Math.hypot(x - cx, y - cy) > R) continue;
      ctx.fillStyle = `rgba(${GREEN}, ${Math.min(1, inten).toFixed(3)})`;
      ctx.beginPath(); ctx.arc(x, y, dot, 0, Math.PI * 2); ctx.fill();
      if (inten > 0.15) picks.push({ x, y, contactId: p.contactId, kind: 'plot', pri: 1 });
    }

    // Tracks.
    ctx.textBaseline = 'middle';
    for (const tr of this.tracks.values()) {
      const [x, y] = toScreen(tr.x, tr.z);
      if (Math.hypot(x - cx, y - cy) > R + 4) continue;
      const m = marked.get(tr.contactId);
      const alpha = tr.misses ? 0.55 : 1;
      ctx.globalAlpha = alpha;
      ctx.fillStyle = 'rgba(0, 227, 253, 0.6)';
      for (const [hx, hz] of tr.trail.slice(0, -1)) {
        const [sx, sy] = toScreen(hx, hz);
        ctx.fillRect(sx - 1, sy - 1, 2, 2);
      }
      const [vx, vy] = [tr.vx * 30 * k, tr.vz * 30 * k]; // 30 s velocity leader
      ctx.strokeStyle = m ? STATE_COLOR[m.state] : '#00e3fd'; ctx.lineWidth = 1.5;
      ctx.beginPath(); ctx.moveTo(x, y); ctx.lineTo(x + vx, y + vy); ctx.stroke();
      if (m) {
        drawShape(ctx, m.state, x, y, big ? 8 : 6, STATE_COLOR[m.state]);
      } else {
        ctx.strokeStyle = '#00e3fd'; ctx.lineWidth = 1.5;
        if (tr.misses) ctx.setLineDash([2, 2]);
        ctx.strokeRect(x - (big ? 6 : 5), y - (big ? 6 : 5), big ? 12 : 10, big ? 12 : 10);
        ctx.setLineDash([]);
      }
      if (tr.contactId === selectedId) {
        ctx.strokeStyle = '#ffffff'; ctx.lineWidth = 2;
        ctx.beginPath(); ctx.arc(x, y, big ? 15 : 11, 0, Math.PI * 2); ctx.stroke();
      }
      const label = m ? `${tr.id} ${tr.contactId}` : `${tr.id} ${tr.size}`;
      ctx.fillStyle = m ? STATE_COLOR[m.state] : '#00e3fd';
      ctx.fillText(label, x + (big ? 12 : 9), y - (big ? 12 : 9));
      if (big) {
        const ro = this.readout(tr);
        ctx.fillStyle = 'rgba(185, 204, 181, 0.85)';
        ctx.fillText(`${Math.round(ro.speed)} m/s · ${Math.round(ro.alt)} m`, x + 12, y + 6);
      }
      ctx.globalAlpha = 1;
      picks.push({ x, y, contactId: tr.contactId, kind: 'track', pri: 0 });
    }

    // Selected track readout.
    const sel = selectedId && this.tracks.get(selectedId);
    if (sel) {
      const ro = this.readout(sel);
      const lines = [`${ro.track}${ro.coasting ? ' (coasting)' : ''} · ${selectedId}`,
        `RNG ${fmtR(ro.range)} · BRG ${pad3(ro.bearing)}°`,
        `ALT ~${Math.round(ro.alt)} m · ${Math.round(ro.speed)} m/s`,
        `HDG ${ro.heading === null ? '---' : pad3(ro.heading) + '°'} · SIZE ${ro.size}`];
      const lh = fontPx + 4, bw = big ? 250 : 190, bh = lines.length * lh + 8;
      const bx = 6, by = h - bh - 6;
      ctx.fillStyle = 'rgba(13, 14, 17, 0.85)'; ctx.fillRect(bx, by, bw, bh);
      ctx.strokeStyle = '#3b4b3a'; ctx.strokeRect(bx, by, bw, bh);
      ctx.fillStyle = '#e3e2e6';
      lines.forEach((l, i) => ctx.fillText(l, bx + 6, by + 4 + lh * i + lh / 2));
    }
    this.picks.set(canvas, picks);
  }

  /** Nearest clickable track or return near a point: { contactId, kind } or null. */
  pick(canvas, px, py) {
    let best = null, bestD = Infinity;
    for (const p of this.picks.get(canvas) || []) {
      const d = Math.hypot(p.x - px, p.y - py) + p.pri * 4; // prefer tracks over raw returns
      if (d < 16 && d < bestD) { best = p; bestD = d; }
    }
    return best;
  }

  /** Rows for the track table (radar console and screen readers). */
  rows() {
    return [...this.tracks.values()].map((tr) => ({ ...this.readout(tr), contactId: tr.contactId }))
      .sort((a, b) => a.range - b.range);
  }
}

export { fmtR, pad3 };

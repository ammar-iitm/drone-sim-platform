// Audio cues, generated with WebAudio so there are no files to bundle (Visual Design "Audio").
// Every sound has a visual counterpart (toast, alert banner or marker), total volume is capped,
// and the mute setting is remembered in this browser.

const KEY = 'dtt.muted';
const MAX_GAIN = 0.22;

export class Sound {
  constructor() {
    this.ctx = null;
    try { this.muted = localStorage.getItem(KEY) === '1'; } catch { this.muted = false; }
  }

  /** Create the audio graph. Must be called from a user gesture (Begin, a key press). */
  start() {
    if (this.ctx) { this.ctx.resume(); return; }
    const AC = window.AudioContext || window.webkitAudioContext;
    if (!AC) return;
    const ctx = (this.ctx = new AC());
    this.master = ctx.createGain();
    this.master.gain.value = this.muted ? 0 : MAX_GAIN;
    this.master.connect(ctx.destination);

    // Rotor hum: two detuned saws through a low-pass filter; gain and pitch follow the nearest drone.
    this.humGain = ctx.createGain();
    this.humGain.gain.value = 0;
    this.humFilter = ctx.createBiquadFilter();
    this.humFilter.type = 'lowpass';
    this.humFilter.frequency.value = 700;
    this.humFilter.connect(this.humGain).connect(this.master);
    this.hum = [0, 7].map((detune) => {
      const o = ctx.createOscillator();
      o.type = 'sawtooth';
      o.frequency.value = 150;
      o.detune.value = detune;
      o.connect(this.humFilter);
      o.start();
      return o;
    });
  }

  setMuted(m) {
    this.muted = m;
    try { localStorage.setItem(KEY, m ? '1' : '0'); } catch { /* ignore */ }
    if (this.master) this.master.gain.setTargetAtTime(m ? 0 : MAX_GAIN, this.ctx.currentTime, 0.05);
  }

  /** level 0..1 from the nearest drone's distance; fast raises the pitch (fixed-wing). */
  rotor(level, fast) {
    if (!this.ctx) return;
    const t = this.ctx.currentTime;
    this.humGain.gain.setTargetAtTime(0.35 * level, t, 0.15);
    const f = (fast ? 260 : 140) + 120 * level;
    for (const o of this.hum) o.frequency.setTargetAtTime(f, t, 0.2);
  }

  tone(freq, dur, { type = 'sine', gain = 0.6, at = 0 } = {}) {
    if (!this.ctx) return;
    const t = this.ctx.currentTime + at;
    const o = this.ctx.createOscillator(), g = this.ctx.createGain();
    o.type = type;
    o.frequency.value = freq;
    g.gain.setValueAtTime(0, t);
    g.gain.linearRampToValueAtTime(gain, t + 0.01);
    g.gain.exponentialRampToValueAtTime(0.001, t + dur);
    o.connect(g).connect(this.master);
    o.start(t);
    o.stop(t + dur + 0.05);
  }

  tick() { this.tone(1400, 0.05, { type: 'square', gain: 0.25 }); }
  chime() { this.tone(1046, 0.4); this.tone(1318, 0.45, { at: 0.08, gain: 0.45 }); }
  fail() { this.tone(220, 0.25, { type: 'triangle', gain: 0.5 }); }
  alert() { for (let i = 0; i < 4; i++) this.tone(i % 2 ? 660 : 880, 0.16, { type: 'square', gain: 0.35, at: i * 0.18 }); }
}

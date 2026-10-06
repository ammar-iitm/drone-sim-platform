// Seeded randomness. rollFor() must match app/rng.py roll() bit for bit, because the
// server re-runs every response roll when it scores a session.

export function fnv1a(text) {
  let h = 0x811c9dc5;
  for (const byte of new TextEncoder().encode(text)) {
    h ^= byte;
    h = Math.imul(h, 0x01000193);
  }
  return h >>> 0;
}

export function mulberry32Step(state) {
  const a = (state + 0x6d2b79f5) | 0;
  let t = Math.imul(a ^ (a >>> 15), a | 1);
  t = (t + Math.imul(t ^ (t >>> 7), t | 61)) ^ t;
  return [a >>> 0, ((t ^ (t >>> 14)) >>> 0) / 4294967296];
}

/** A stream of floats in [0, 1) from a 32-bit seed. */
export function mulberry32(seed) {
  let state = seed >>> 0;
  return () => {
    const [next, value] = mulberry32Step(state);
    state = next;
    return value;
  };
}

export function rollFor(seed, contactId, attempt) {
  return mulberry32Step(fnv1a(`${seed}:${contactId}:${attempt}`))[1];
}

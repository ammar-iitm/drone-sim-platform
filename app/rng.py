"""Deterministic helpers shared with the browser.

`roll` must give bit-identical results to `rollFor` in static/js/sim/rng.js,
because the simulator shows the outcome of a response and the server scores it.
"""

MASK = 0xFFFFFFFF


def _imul(a: int, b: int) -> int:
    return (a * b) & MASK


def fnv1a(text: str) -> int:
    h = 0x811C9DC5
    for byte in text.encode("utf-8"):
        h ^= byte
        h = _imul(h, 0x01000193)
    return h


def mulberry32_step(state: int) -> tuple[int, float]:
    """One step of mulberry32. Returns (new_state, value in [0, 1))."""
    a = (state + 0x6D2B79F5) & MASK
    t = _imul(a ^ (a >> 15), a | 1)
    t = ((t + _imul(t ^ (t >> 7), t | 61)) & MASK) ^ t
    return a, ((t ^ (t >> 14)) & MASK) / 4294967296


def roll(seed: int, contact_id: str, attempt: int) -> float:
    """Success roll for the n-th engaging response against one contact."""
    _, value = mulberry32_step(fnv1a(f"{seed}:{contact_id}:{attempt}"))
    return value

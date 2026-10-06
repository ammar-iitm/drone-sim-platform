// Threat markers: colour, shape and a text label together (Visual Design doc).
export const STATE_COLOR = { hostile: '#ff6b5e', unknown: '#ffb95f', friendly: '#6aa8ff', benign: '#a4aca7' };
export const STATE_LABEL = { hostile: 'HOSTILE', unknown: 'UNKNOWN', friendly: 'FRIENDLY', benign: 'BENIGN' };
export const FAMILY_STATE = { hostile_uas: 'hostile', non_threat: 'benign', friendly: 'friendly' };

export function drawShape(ctx, state, x, y, r, color) {
  ctx.fillStyle = color;
  ctx.strokeStyle = '#0d0e11';
  ctx.lineWidth = 1.5;
  ctx.beginPath();
  if (state === 'hostile') {
    ctx.moveTo(x, y - r); ctx.lineTo(x + r, y + r * 0.8); ctx.lineTo(x - r, y + r * 0.8); ctx.closePath();
  } else if (state === 'friendly') {
    ctx.arc(x, y, r * 0.85, 0, Math.PI * 2);
  } else if (state === 'benign') {
    ctx.rect(x - r * 0.75, y - r * 0.75, r * 1.5, r * 1.5);
  } else {
    ctx.moveTo(x, y - r); ctx.lineTo(x + r, y); ctx.lineTo(x, y + r); ctx.lineTo(x - r, y); ctx.closePath();
  }
  ctx.fill();
  ctx.stroke();
}

/** Inline SVG badge for HTML lists (shape symbols live in base.html). */
export function badge(state) {
  return `<span class="badge ${state}"><svg aria-hidden="true"><use href="#s-${state}"/></svg>${STATE_LABEL[state]}</span>`;
}

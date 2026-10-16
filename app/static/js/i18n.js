// Hindi / English switch (GIGW: bilingual content; the Indian Army site defaults to Hindi).
// English is the source language of every page. When Hindi is chosen, visible text and a few
// attributes are translated as pages render, including text that scripts add later, so page
// code stays in English. Strings without a translation stay in English (mostly data, such as
// callsigns, and long help prose that a Hindi speaker should translate as whole paragraphs).
import { HI, HI_UPPER, HI_PATTERNS } from './i18n-hi.js';

const KEY = 'dtt.lang';
const ATTRS = ['placeholder', 'title', 'aria-label'];
const shown = new WeakMap(); // text node -> { en, hi } last applied, so new English is noticed

function stored() {
  try { return localStorage.getItem(KEY); } catch { return null; }
}

export const lang = stored() === 'hi' ? 'hi' : 'en';

/** Hindi for one English string, or the string itself if there is no translation. */
export function t(en) {
  if (lang !== 'hi' || !en) return en;
  const key = en.replace(/\s+/g, ' ').trim();
  let hi = HI.get(key) ?? HI_UPPER.get(key.toUpperCase());
  for (let i = 0; hi === undefined && i < HI_PATTERNS.length; i++) {
    const m = key.match(HI_PATTERNS[i][0]);
    if (m) hi = HI_PATTERNS[i][1](...m.slice(1));
  }
  // Keep the text's own leading and trailing spaces, which separate it from its neighbours.
  return hi === undefined ? en : en.match(/^\s*/)[0] + hi + en.match(/\s*$/)[0];
}

function translateText(node) {
  const p = node.parentElement;
  if (!p || p.closest('script, style, [data-no-i18n]')) return;
  const last = shown.get(node);
  const en = last && node.nodeValue === last.hi ? last.en : node.nodeValue;
  const hi = t(en);
  if (hi !== node.nodeValue) node.nodeValue = hi;
  shown.set(node, { en, hi });
}

function translateAttrs(el) {
  if (el.closest('[data-no-i18n]')) return;
  for (const a of ATTRS) {
    if (!el.hasAttribute(a)) continue;
    const prev = el.getAttribute(`data-hi-${a}`);
    const en = prev !== null && el.getAttribute(a) === prev ? el.getAttribute(`data-en-${a}`) : el.getAttribute(a);
    const hi = t(en);
    if (hi !== en) {
      el.setAttribute(`data-en-${a}`, en);
      el.setAttribute(`data-hi-${a}`, hi);
      if (el.getAttribute(a) !== hi) el.setAttribute(a, hi);
    }
  }
}

function translateTree(root) {
  if (root.nodeType === Node.TEXT_NODE) { translateText(root); return; }
  if (root.nodeType !== Node.ELEMENT_NODE) return;
  translateAttrs(root);
  const walker = document.createTreeWalker(root, NodeFilter.SHOW_TEXT | NodeFilter.SHOW_ELEMENT);
  for (let n = walker.nextNode(); n; n = walker.nextNode()) {
    if (n.nodeType === Node.TEXT_NODE) translateText(n); else translateAttrs(n);
  }
}

function start() {
  const toggle = document.getElementById('lang-toggle');
  if (toggle) {
    toggle.textContent = lang === 'hi' ? 'English' : 'हिंदी';
    toggle.lang = lang === 'hi' ? 'en' : 'hi';
    toggle.setAttribute('aria-label', lang === 'hi' ? 'Switch to English' : 'हिंदी में देखें (switch to Hindi)');
    toggle.addEventListener('click', () => {
      try { localStorage.setItem(KEY, lang === 'hi' ? 'en' : 'hi'); } catch { /* private mode */ }
      location.reload();
    });
  }
  if (lang !== 'hi') return;
  document.documentElement.lang = 'hi';
  document.title = t(document.title.split(' · ')[0]) + ' · AEGIS';
  translateTree(document.body);
  new MutationObserver((records) => {
    for (const r of records) {
      if (r.type === 'characterData') translateText(r.target);
      else if (r.type === 'attributes') translateAttrs(r.target);
      else for (const n of r.addedNodes) translateTree(n);
    }
  }).observe(document.body, { childList: true, subtree: true, characterData: true, attributes: true, attributeFilter: ATTRS });
}

if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', start);
else start();

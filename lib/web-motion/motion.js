// web-motion: a browser port of the pure motion math from rossark-motion-skill
// (templates/react-native/motion.ts, MIT © 2026 rossark0, https://github.com/rossark0/rossark-motion-skill).
// No React Native / Reanimated: every function is a pure function of time in ms, so it can be
// driven by requestAnimationFrame, a GSAP timeline, or huashu-motion's OM.clock(tl, draw, seconds).
//
// Plain script: exposes window.Motion. Also works as a CommonJS module for tests.
(function (root) {
  'use strict';

  /** A CSS-style cubic-bezier easing function (x1, y1, x2, y2), solved for x by Newton + bisection. */
  function bezier(x1, y1, x2, y2) {
    const cx = 3 * x1, bx = 3 * (x2 - x1) - cx, ax = 1 - cx - bx;
    const cy = 3 * y1, by = 3 * (y2 - y1) - cy, ay = 1 - cy - by;
    const sx = (s) => ((ax * s + bx) * s + cx) * s;
    const sy = (s) => ((ay * s + by) * s + cy) * s;
    const dx = (s) => (3 * ax * s + 2 * bx) * s + cx;
    function solve(x) {
      let s = x;
      for (let i = 0; i < 8; i++) {
        const e = sx(s) - x;
        if (Math.abs(e) < 1e-6) return s;
        const d = dx(s);
        if (Math.abs(d) < 1e-6) break;
        s -= e / d;
      }
      let lo = 0, hi = 1;
      s = x;
      while (lo < hi) {
        const v = sx(s);
        if (Math.abs(v - x) < 1e-6) return s;
        if (x > v) lo = s; else hi = s;
        s = (lo + hi) / 2;
        if (hi - lo < 1e-7) break;
      }
      return s;
    }
    return (p) => (p <= 0 ? 0 : p >= 1 ? 1 : sy(solve(p)));
  }

  // The skill's curves: travel = ease-in-out, arrive/open = ease-out, leave/fall = ease-in.
  const EASE_IN_OUT = bezier(0.77, 0, 0.175, 1);
  const EASE_OUT = bezier(0.23, 1, 0.32, 1);
  const EASE_IN = bezier(0.55, 0, 1, 0.45);

  /** Keyframes [ms, value, 'out'?]: eases into and out of every key. Right for ONE move (blink, lid). */
  function track(t, keys) {
    if (t <= keys[0][0]) return keys[0][1];
    for (let i = 1; i < keys.length; i++) {
      const k1 = keys[i];
      if (t <= k1[0]) {
        const k0 = keys[i - 1];
        const span = k1[0] - k0[0];
        const p = span > 0 ? (t - k0[0]) / span : 1;
        const e = k1[2] === 'out' ? EASE_OUT(p) : EASE_IN_OUT(p);
        return k0[1] + (k1[1] - k0[1]) * e;
      }
    }
    return keys[keys.length - 1][1];
  }

  /** Smooth path through key poses [ms, value] (monotone cubic): for acting, never stops at a pose. */
  function flow(t, k) {
    const n = k.length;
    if (t <= k[0][0]) return k[0][1];
    if (t >= k[n - 1][0]) return k[n - 1][1];
    let i = 0;
    while (k[i + 1][0] < t) i++;
    const slope = (j) => (k[j + 1][1] - k[j][1]) / (k[j + 1][0] - k[j][0]);
    function tangent(j) {
      if (j === 0 || j === n - 1) return 0;
      const a = slope(j - 1), b = slope(j);
      if (a * b <= 0) return 0;
      const h0 = k[j][0] - k[j - 1][0], h1 = k[j + 1][0] - k[j][0];
      const w0 = 2 * h1 + h0, w1 = h1 + 2 * h0;
      return (w0 + w1) / (w0 / a + w1 / b);
    }
    const h = k[i + 1][0] - k[i][0];
    const s = (t - k[i][0]) / h, s2 = s * s, s3 = s2 * s;
    return (2 * s3 - 3 * s2 + 1) * k[i][1] + (s3 - 2 * s2 + s) * h * tangent(i) +
      (-2 * s3 + 3 * s2) * k[i + 1][1] + (s3 - s2) * h * tangent(i + 1);
  }

  /** 0 → 1 inside the window [a, b] (eased), 0 before, 1 after: one beat of a one-shot scene. */
  function seg(t, a, b, curve = 'out') {
    if (t <= a) return 0;
    if (t >= b) return 1;
    const p = (t - a) / (b - a);
    return curve === 'out' ? EASE_OUT(p) : EASE_IN_OUT(p);
  }

  /** Smooth -1 … 1 back-and-forth; phase (0–1) offsets one item from the next. */
  const wave = (t, period, phase = 0) => Math.sin((t / period + phase) * Math.PI * 2);

  /** 0 … 1 progress through a loop, with phase. */
  function loop(t, period, phase = 0) {
    const p = (t / period + phase) % 1;
    return p < 0 ? p + 1 : p;
  }

  /** 0 at both ends, 1 in the middle: fade in and out over a loop. */
  const bell = (p) => Math.sin(Math.PI * Math.min(1, Math.max(0, p)));

  /** Stable pseudo-random [0, 1) for item i: the same on every frame and every render. */
  function seeded(i, salt = 0) {
    const x = Math.sin(i * 12.9898 + salt * 78.233) * 43758.5453;
    return x - Math.floor(x);
  }

  /** Linear interpolation. */
  const mix = (a, b, p) => a + (b - a) * p;

  const Motion = { bezier, EASE_IN_OUT, EASE_OUT, EASE_IN, track, flow, seg, wave, loop, bell, seeded, mix };
  if (typeof module !== 'undefined' && module.exports) module.exports = Motion;
  else root.Motion = Motion;
})(typeof window !== 'undefined' ? window : globalThis);

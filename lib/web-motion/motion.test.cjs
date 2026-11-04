const test = require('node:test');
const assert = require('node:assert');
const M = require('./motion.js');
const near = (a, b, e = 1e-3) => assert.ok(Math.abs(a - b) < e, `${a} ≉ ${b}`);

test('bezier matches CSS "ease" (0.25,0.1,0.25,1) at known points', () => {
  const ease = M.bezier(0.25, 0.1, 0.25, 1);
  near(ease(0.5), 0.8024); near(ease(0.25), 0.4094); near(ease(0), 0); near(ease(1), 1);
});
test('curves are monotone and hit their ends', () => {
  for (const f of [M.EASE_IN_OUT, M.EASE_OUT, M.EASE_IN]) {
    let prev = -1;
    for (let p = 0; p <= 1.0001; p += 0.01) { const v = f(p); assert.ok(v >= prev - 1e-9); prev = v; }
    near(f(0), 0); near(f(1), 1);
  }
  near(M.EASE_IN_OUT(0.5), 0.59597); near(M.EASE_OUT(0.3), 0.84301); // cross-checked by brute force
});
test('track hits every key and eases', () => {
  const k = [[0, 0], [100, 10], [200, 0, 'out']];
  near(M.track(0, k), 0); near(M.track(100, k), 10); near(M.track(200, k), 0); near(M.track(50, k), 5.9597);
});
test('flow passes through keys, never overshoots, and keeps moving through a pose', () => {
  const k = [[0, 0], [500, 10], [1000, 30], [1500, 30], [2000, 0]];
  for (const [t, v] of k) near(M.flow(t, k), v);
  for (let t = 0; t <= 2000; t += 5) { const v = M.flow(t, k); assert.ok(v >= -1e-9 && v <= 30 + 1e-9); }
  // at the 500 ms pose, the speed is not zero (that's the point of flow vs track)
  assert.ok(M.flow(510, k) - M.flow(490, k) > 0.1);
  assert.ok(Math.abs(M.track(510, k) - M.track(490, k)) < 0.1);
});
test('seg, loop, bell, seeded', () => {
  near(M.seg(-1, 0, 1), 0); near(M.seg(2, 0, 1), 1);
  near(M.loop(1500, 1000), 0.5); near(M.loop(-250, 1000), 0.75);
  near(M.bell(0), 0); near(M.bell(0.5), 1); near(M.bell(1), 0, 1e-9);
  assert.strictEqual(M.seeded(3), M.seeded(3)); assert.ok(M.seeded(3) >= 0 && M.seeded(3) < 1);
});

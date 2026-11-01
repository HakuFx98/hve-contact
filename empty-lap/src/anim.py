"""Animation helpers: easing, keyframe tracks, deterministic noise."""
import math


def clamp(x, a=0.0, b=1.0):
    return a if x < a else b if x > b else x


def lerp(a, b, t):
    if isinstance(a, tuple):
        return tuple(lerp(x, y, t) for x, y in zip(a, b))
    return a + (b - a) * t


def smooth(t):
    t = clamp(t)
    return t * t * (3 - 2 * t)


def smoother(t):
    t = clamp(t)
    return t * t * t * (t * (t * 6 - 15) + 10)


def ease_out(t):
    t = clamp(t)
    return 1 - (1 - t) ** 3


def ease_in(t):
    t = clamp(t)
    return t ** 3


def linear(t):
    return clamp(t)


def ease_out_back(t, s=1.6):
    t = clamp(t) - 1
    return t * t * ((s + 1) * t + s) + 1


def seg(t, t0, t1, ease=smooth):
    if t1 <= t0:
        return 1.0 if t >= t1 else 0.0
    return ease((t - t0) / (t1 - t0))


def kf(t, keys, ease=smooth):
    """Piecewise keyframes [(time, value[, ease])]. Ease of a key applies to the
    segment that ends at that key."""
    if t <= keys[0][0]:
        return keys[0][1]
    for i in range(1, len(keys)):
        if t <= keys[i][0]:
            t0, v0 = keys[i - 1][0], keys[i - 1][1]
            t1, v1 = keys[i][0], keys[i][1]
            e = keys[i][2] if len(keys[i]) > 2 else ease
            return lerp(v0, v1, e((t - t0) / (t1 - t0)) if t1 > t0 else 1)
    return keys[-1][1]


def window(t, t0, t1, fade=0.15):
    """1 inside [t0,t1] with soft edges."""
    return seg(t, t0 - fade, t0 + fade) * (1 - seg(t, t1 - fade, t1 + fade))


def wob(seed, t, amp=1.0, speed=1.0):
    return amp * (0.6 * math.sin(1.3 * t * speed + seed * 2.1)
                  + 0.4 * math.sin(2.7 * t * speed + seed * 5.3))


def blink_auto(t, seed=0, period=3.6):
    """Natural blink pulses at quasi-random intervals."""
    # deterministic sequence of blink times
    import random
    rnd = random.Random(seed)
    bt = 0.9 + rnd.random()
    while bt < t - 0.3:
        bt += period * (0.7 + 0.6 * rnd.random())
    d = abs(t - bt)
    return clamp(1 - d / 0.085) if d < 0.085 else 0.0

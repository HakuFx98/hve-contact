"""Original score + sound design for THE EMPTY LAP (fully synthesized, no samples,
no third-party music -> no licensing encumbrance).

Sound effects that depend on motion (paw steps, purr level, breathing, fabric
rustle) are derived directly from the animation state in scenes.py, so audio and
picture stay in sync by construction.

usage: python3 audio.py out.wav
"""
import sys
import math
import wave
import numpy as np
import scenes

SR = 48000
DUR = scenes.DURATION
N = int(SR * DUR)
rng = np.random.default_rng(2024)


# ------------------------------------------------------------------ dsp helpers
def band(x, lo=None, hi=None, order=2):
    """Zero-phase FFT band filter with smooth (butterworth-like) skirts."""
    n = len(x)
    nf = 1 << (n - 1).bit_length()
    X = np.fft.rfft(x, nf)
    f = np.fft.rfftfreq(nf, 1 / SR)
    g = np.ones_like(f)
    if lo:
        g *= 1 / np.sqrt(1 + (lo / np.maximum(f, 1e-3)) ** (2 * order))
    if hi:
        g *= 1 / np.sqrt(1 + (f / hi) ** (2 * order))
    return np.fft.irfft(X * g, nf)[:n]


def noise(n):
    return rng.standard_normal(n)


def env_exp(n, tau):
    return np.exp(-np.arange(n) / (tau * SR))


def add(buf, sig, t0, gain=1.0, pan=0.0):
    i0 = int(round(t0 * SR))
    if i0 >= buf.shape[1] or i0 + len(sig) <= 0:
        return
    s = sig
    if i0 < 0:
        s = s[-i0:]
        i0 = 0
    s = s[: buf.shape[1] - i0]
    l = math.cos((pan + 1) * math.pi / 4)
    r = math.sin((pan + 1) * math.pi / 4)
    buf[0, i0:i0 + len(s)] += s * gain * l * 1.4142
    buf[1, i0:i0 + len(s)] += s * gain * r * 1.4142


def reverb_ir(seconds=2.8, damp=5200, seed=5):
    r = np.random.default_rng(seed)
    n = int(seconds * SR)
    t = np.arange(n) / SR
    out = []
    for ch in range(2):
        x = r.standard_normal(n) * np.exp(-t * 6.9 / seconds)
        x = band(x, 120, damp)
        # early reflections
        for d, a in ((0.011, 0.5), (0.019, 0.35), (0.027, 0.3), (0.041, 0.22)):
            x[int((d + 0.003 * ch) * SR)] += a * 6
        out.append(x / np.sqrt(np.sum(x ** 2)))
    return np.array(out)


def convolve(x, ir):
    n = len(x) + len(ir) - 1
    nf = 1 << (n - 1).bit_length()
    y = np.fft.irfft(np.fft.rfft(x, nf) * np.fft.rfft(ir, nf), nf)[:len(x)]
    return y


def reverb(buf, wet, seconds=2.8, damp=5200):
    ir = reverb_ir(seconds, damp)
    mono = buf.mean(axis=0)
    out = buf.copy()
    for ch in range(2):
        out[ch] = buf[ch] * (1 - wet * 0.35) + convolve(mono, ir[ch]) * wet
    return out


# ------------------------------------------------------------------ piano
NOTE = {'C': 0, 'C#': 1, 'Db': 1, 'D': 2, 'D#': 3, 'Eb': 3, 'E': 4, 'F': 5, 'F#': 6, 'Gb': 6, 'G': 7,
        'G#': 8, 'Ab': 8, 'A': 9, 'A#': 10, 'Bb': 10, 'B': 11}


def midi(name):
    p, o = name[:-1], int(name[-1])
    return 12 * (o + 1) + NOTE[p]


def freq(name):
    return 440.0 * 2 ** ((midi(name) - 69) / 12)


def piano(f, dur, vel):
    tail = 3.2
    n = int((dur + tail) * SR)
    t = np.arange(n) / SR
    out = np.zeros(n)
    B = 0.00035
    bright = 0.55 + 0.6 * vel
    for detune, g in ((1.0, 0.62), (1.00055, 0.38)):
        for k in range(1, 13):
            fk = k * f * detune * math.sqrt(1 + B * k * k)
            if fk > 15000:
                break
            amp = g * (bright ** (k - 1)) / k ** 0.9
            dk = (0.55 + 0.45 * k) * (f / 262.0) ** 0.45
            e = 0.55 * np.exp(-t * dk * 1.9) + 0.45 * np.exp(-t * dk * 0.42)
            out += amp * e * np.sin(2 * np.pi * fk * t + rng.random() * 6.28)
    out *= 1 - np.exp(-t / 0.0035)
    rel = np.ones(n)
    i = int(dur * SR)
    rel[i:] = np.exp(-(t[i:] - dur) / 0.32)
    out *= rel
    h = band(noise(int(0.02 * SR)), 200, 2400) * env_exp(int(0.02 * SR), 0.004) * 0.05
    out[:len(h)] += h
    return out * vel * 0.16


def score():
    """Return list of (time, note, dur, vel, pan)."""
    ev = []
    beat = 0.8
    bar = 4 * beat

    def arp(t0, chord, vel, pattern=(0, 1, 2, 3, 4, 3, 2, 1), step=beat / 2, length=None, hold=1.6):
        for i, idx in enumerate(pattern):
            tt = t0 + i * step
            if length and tt >= t0 + length - 1e-6:
                break
            jitter = rng.normal(0, 0.006)
            v = vel * (1.0 if i == 0 else 0.78) * (0.92 + 0.12 * rng.random())
            ev.append((tt + jitter, chord[idx], hold, v, -0.35))

    def mel(t0, notes, vel, b=beat):
        for n_, s, d in notes:
            ev.append((t0 + s * b + rng.normal(0, 0.008), n_, d * b * 1.05, vel * (0.92 + 0.12 * rng.random()), 0.15))

    t = 4.25  # flashback begins: warm theme
    A = [
        (['F2', 'C3', 'F3', 'A3', 'C4'], [('C5', 0, 1), ('A4', 1, .5), ('C5', 1.5, .5), ('F5', 2, 1.5), ('E5', 3.5, .5)]),
        (['E2', 'C3', 'E3', 'G3', 'C4'], [('D5', 0, 1), ('C5', 1, 1), ('G4', 2, 2)]),
        (['D2', 'A2', 'D3', 'F3', 'A3'], [('A4', 0, 1), ('F4', 1, .5), ('A4', 1.5, .5), ('D5', 2, 1.5), ('C5', 3.5, .5)]),
        (['A#1', 'F2', 'A#2', 'D3', 'F3'], [('A#4', 0, 1), ('A4', 1, 1), ('F4', 2, 2)]),
        (['A2', 'C3', 'F3', 'A3', 'C4'], [('C5', 0, 1), ('F5', 1, 1), ('A5', 2, 1.5), ('G5', 3.5, .5)]),
    ]
    vels = [0.42, 0.46, 0.48, 0.50, 0.54]
    for i, (ch, ml) in enumerate(A):
        tb = t + i * bar
        arp(tb, ch, vels[i] * 0.62)
        mel(tb, ml, vels[i])
    # bar 6: Gm7 -> C7 (leans into the change)
    tb = t + 5 * bar
    arp(tb, ['G2', 'D3', 'F3', 'A#3', 'D4'], 0.30, length=bar / 2)
    arp(tb + bar / 2, ['C2', 'G2', 'C3', 'E3', 'A#3'], 0.28, length=bar / 2)
    mel(tb, [('F5', 0, 1), ('D5', 1, 1), ('E5', 2, 1), ('C5', 3, 1)], 0.48)
    # S4: something changes - sparser, quieter, minor
    tb = t + 6 * bar  # 23.45
    B4 = [
        (['D2', 'A2', 'F3', 'A3'], [('A4', 0, 2), ('F4', 2, 1), ('E4', 3, 1)], 0.40),
        (['A#1', 'F2', 'D3', 'F3'], [('D4', 0, 3.5)], 0.34),
        (['G1', 'D2', 'A#2', 'D3'], [('A#4', 0, 1.5), ('A4', 1.5, .5), ('G4', 2, 2)], 0.30),
    ]
    for i, (ch, ml, v) in enumerate(B4):
        b0 = tb + i * bar
        for j, nn in enumerate(ch):
            ev.append((b0 + j * beat, nn, 2.2, v * 0.6, -0.3))
        mel(b0, ml, v)
    b0 = tb + 3 * bar  # 33.05 unresolved A-sus, fading under the black
    for j, nn in enumerate(['A1', 'E2', 'A2', 'D3']):
        ev.append((b0 + j * 0.25, nn, 1.6, 0.20, -0.3))
    ev.append((b0 + 0.9, 'C#3', 2.4, 0.16, -0.2))
    # S5: near silence - one soft dyad when he sees the bell
    ev.append((41.0, 'D4', 2.5, 0.12, 0.2))
    ev.append((41.06, 'A4', 2.5, 0.10, 0.25))
    # S6: the memory - theme returns, higher and slower
    mb = 0.9
    tm = 45.3
    for j, nn in enumerate(['F3', 'C4', 'A4']):
        ev.append((tm + j * 0.45, nn, 3.2, 0.20, -0.3))
    mel(tm, [('C6', 0, 1), ('A5', 1, .5), ('C6', 1.5, .5), ('F6', 2, 1.5), ('E6', 3.5, .5)], 0.30, b=mb)
    tm2 = tm + 4 * mb  # 48.9
    for j, nn in enumerate(['D3', 'A3', 'F4']):
        ev.append((tm2 + j * 0.45, nn, 2.6, 0.18, -0.3))
    mel(tm2, [('D6', 0, 1)], 0.26, b=mb)
    ev.append((tm2 + 0.95, 'C6', 2.8, 0.22, 0.15))        # left hanging as his eyes open
    ev.append((50.2, 'A#2', 3.5, 0.17, -0.3))             # tear
    ev.append((50.25, 'F3', 3.5, 0.14, -0.2))
    ev.append((50.32, 'C4', 3.5, 0.12, 0.0))
    ev.append((50.40, 'D4', 3.5, 0.12, 0.1))
    # S7: resolution
    for j, nn in enumerate(['G2', 'D3', 'F3', 'A#3']):
        ev.append((53.3 + j * 0.18, nn, 1.6, 0.16, -0.25))
    ev.append((54.5, 'C5', 1.0, 0.20, 0.15))
    for j, nn in enumerate(['A#2', 'F3', 'C4', 'D4']):
        ev.append((55.4 + j * 0.14, nn, 1.2, 0.17, -0.25))
    ev.append((55.45, 'D5', 0.9, 0.21, 0.15))
    for j, nn in enumerate(['C3', 'F3', 'G3']):
        ev.append((56.4 + j * 0.12, nn, 0.7, 0.15, -0.25))
    ev.append((56.45, 'C5', 0.6, 0.19, 0.15))
    for j, nn in enumerate(['C3', 'E3', 'G3', 'A#3']):
        ev.append((57.0 + j * 0.10, nn, 0.8, 0.14, -0.25))
    ev.append((57.05, 'A#4', 0.8, 0.18, 0.15))
    for j, nn in enumerate(['F2', 'C3', 'F3', 'A3', 'C4']):
        ev.append((57.8 + j * 0.16, nn, 2.4, 0.17, -0.25))
    ev.append((58.05, 'A4', 2.2, 0.20, 0.15))
    ev.append((58.7, 'F5', 1.6, 0.10, 0.2))
    return ev


def render_music():
    buf = np.zeros((2, N + SR * 4))
    for (t0, nn, d, v, pan) in score():
        add(buf, piano(freq(nn), d, v), t0, 1.0, pan)
    buf = buf[:, :N]
    buf = reverb(buf, 0.42, 3.0, 4800)
    # gentle overall fade at the very end
    tt = np.arange(N) / SR
    buf *= np.clip((60.0 - tt) / 1.4, 0, 1)
    return buf


# ------------------------------------------------------------------ sfx
def bell_hit(amp, f0=3150.0):
    n = int(0.9 * SR)
    t = np.arange(n) / SR
    out = np.zeros(n)
    for r, a, d in ((1, 1, 7), (1.51, .55, 9), (2.08, .4, 12), (2.73, .25, 15), (3.62, .15, 19)):
        out += a * np.sin(2 * np.pi * f0 * r * t + rng.random() * 6) * np.exp(-t * d)
    out *= 1 - np.exp(-t / 0.0008)
    return out * amp * 0.05


def jingle(buf, t0, hits=4, spread=0.14, amp=1.0, pan=0.0):
    for i in range(hits):
        tt = t0 + spread * (i / max(1, hits - 1)) ** 1.3 + rng.normal(0, 0.008)
        add(buf, bell_hit(amp * (1.0 - 0.18 * i) * (0.8 + 0.4 * rng.random()), 3150 * (1 + rng.normal(0, 0.03))), tt,
            1.0, pan)


def thump(amp, lp=260, dur=0.12):
    n = int(dur * SR)
    s = band(noise(n), 40, lp) * env_exp(n, dur / 4)
    return s / (np.abs(s).max() + 1e-9) * amp


def tick(amp, f=2600):
    n = int(0.02 * SR)
    s = band(noise(n), f * 0.6, f * 2.2) * env_exp(n, 0.0025)
    return s / (np.abs(s).max() + 1e-9) * amp


def paw(amp):
    n = int(0.05 * SR)
    s = band(noise(n), 250, 2600) * env_exp(n, 0.008)
    s = s / (np.abs(s).max() + 1e-9) * amp
    s += thump(amp * 0.7, 180, 0.05)
    return s


def top_state(t):
    layers, _ = scenes.frame(t)
    layers = [l for l in layers if l[1] > 0]
    return max(layers, key=lambda l: l[1])[0] if layers else None


def render_sfx():
    dry = np.zeros((2, N + SR * 2))
    fps = 120
    T = np.arange(int(DUR * fps)) / fps
    states = [top_state(t) for t in T]

    # --- paw steps from the gait cycle
    offs = (math.pi, 0.0, 0.0, math.pi)
    prev = None
    for t, st in zip(T, states):
        K = st.get('cat') if st else None
        if not K or K.get('gait', 0) < 0.05:
            prev = None
            continue
        ph = K.get('phase', 0.0)
        cur = [((ph + o) % (2 * math.pi)) for o in offs]
        if prev is not None:
            for a, b in zip(prev, cur):
                if a < math.pi / 2 <= b:
                    g = 0.06 * min(1.0, K['gait'] * 1.4)
                    pan = max(-1, min(1, (K['x'] - 540) / 700))
                    add(dry, paw(g), t, 1.0, pan)
                    if K.get('bell') and rng.random() < 0.6 * K['gait']:
                        jingle(dry, t + 0.01, 2, 0.05, 0.35 * K['gait'], pan)
        prev = cur

    # --- scripted hits
    for tp in (0.25, 0.80, 1.35, 1.90):                       # S1 pats on the empty lap
        add(dry, thump(0.16, 320, 0.10), tp, 1.0, -0.1)
    ev_jumps = [(6.42, 6.88), (13.55, 13.98)]                 # launch, land on lap
    for a, b in ev_jumps:
        add(dry, paw(0.07), a, 1.0, -0.5)
        jingle(dry, a + 0.02, 3, 0.10, 0.7, -0.4)
        add(dry, thump(0.14, 300, 0.14), b, 1.0, -0.1)
        jingle(dry, b + 0.01, 4, 0.16, 0.8, -0.1)
    # S4: failed jump, fall, second attempt, lift
    add(dry, paw(0.05), 25.8, 1.0, -0.5)
    jingle(dry, 25.82, 3, 0.10, 0.5, -0.5)
    add(dry, thump(0.12, 380, 0.10), 26.08, 1.0, -0.4)        # paws hit the knee
    add(dry, thump(0.16, 260, 0.16), 26.35, 1.0, -0.5)        # falls back down
    jingle(dry, 26.36, 5, 0.25, 0.8, -0.5)
    add(dry, paw(0.04), 28.0, 1.0, -0.45)
    jingle(dry, 28.05, 2, 0.08, 0.4, -0.45)
    for k in range(5):                                        # scrabbling paws
        add(dry, tick(0.025, 1800 + 300 * k), 28.5 + k * 0.1, 1.0, -0.4)
    jingle(dry, 29.1, 3, 0.18, 0.5, -0.3)                     # lifted
    add(dry, thump(0.08, 260, 0.12), 30.25, 1.0, -0.1)
    # phantom bell in the hook (reverb heavy, distant)
    ghost = np.zeros_like(dry)
    jingle(ghost, 1.58, 3, 0.16, 0.55, -0.6)
    # S7: picking up and placing the bell
    jingle(dry, 54.28, 3, 0.12, 0.55, 0.4)
    jingle(dry, 55.4, 1, 0.0, 0.35, -0.1)
    add(dry, thump(0.05, 300, 0.08), 55.38, 1.0, -0.1)

    # --- clock in the present (S1, S5) - absent in memories
    for k in range(0, 60):
        tt = 0.5 + k * 1.0
        if tt < 4.0 or 34.6 < tt < 44.0:
            add(dry, tick(0.018 if k % 2 else 0.014, 2400 if k % 2 else 2000), tt, 1.0, 0.6)

    # --- continuous layers from animation state (per-sample envelopes)
    tt = np.arange(N) / SR
    purr_lvl = np.zeros(len(T))
    mem_lvl = np.zeros(len(T))
    breath_ph = np.zeros(len(T))
    breath_g = np.zeros(len(T))
    fabric = np.zeros(len(T))
    sigh = np.zeros(len(T))
    prev_h = None
    for i, (t, st) in enumerate(zip(T, states)):
        if not st:
            continue
        K = st.get('cat')
        if K:
            purr_lvl[i] = K.get('purr', 0.0) * K.get('alpha', 1.0)
        M = st.get('memory')
        if M:
            mem_lvl[i] = M.get('purr', 0.0) * M.get('alpha', 0.0)
        C = st['char']
        breath_ph[i] = C.get('breath', 0.0)
        sigh[i] = C.get('sigh', 0.0)
        # breathing is only audible in the quiet present-day scenes
        breath_g[i] = 0.5 if t < 4 else (0.25 if 23 < t < 34 else (1.0 if t > 34 else 0.0))
        h = np.array(C['near_hand'] + C['far_hand'])
        if prev_h is not None:
            fabric[i] = np.linalg.norm(h - prev_h) * fps
        prev_h = h
    up = lambda a: np.interp(tt, T, a)
    # purr: 25 Hz pulse train through low noise, swelling with breaths
    carrier = band(noise(N), 50, 420)
    pulses = (0.5 + 0.5 * np.sin(2 * np.pi * 25.5 * tt + 0.3 * np.sin(2 * np.pi * 0.7 * tt))) ** 3
    swell = 0.65 + 0.35 * np.sin(2 * np.pi * tt / 2.4)
    purr = carrier * pulses * swell
    purr /= np.abs(purr).max()
    p_l = up(purr_lvl)
    add(dry, purr * p_l * 0.11, 0.0, 1.0, -0.05)
    mem = band(purr * up(mem_lvl) * 0.09, 70, 300)
    add(ghost, mem, 0.0, 1.0, -0.1)
    # breathing: airy band noise following the breath phase (inhale on rising sin)
    bp = up(breath_ph)
    insp = np.clip(np.cos(bp), 0, 1) ** 2 * 0.6 + np.clip(-np.cos(bp), 0, 1) ** 2 * 0.35
    air = band(noise(N), 350, 2200)
    air /= np.abs(air).max()
    sg = up(sigh)
    br = air * (insp * up(breath_g) * 0.010 + sg * 0.035)
    add(dry, br, 0.0, 1.0, 0.05)
    # fabric rustle from hand motion
    fab = band(noise(N), 900, 6500)
    fab /= np.abs(fab).max()
    fl = np.clip(up(fabric) / 900.0, 0, 1) ** 1.2
    add(dry, fab * fl * 0.035, 0.0, 1.0, 0.0)
    # rain in the montage (16.4-19.75)
    rain = band(noise(N), 1500, 9000)
    rain /= np.abs(rain).max()
    rw = np.clip((tt - 16.2) / 0.4, 0, 1) * np.clip((20.0 - tt) / 0.4, 0, 1)
    add(dry, rain * rw * 0.018, 0.0, 1.0, -0.2)
    for k in range(60):
        add(dry, tick(0.012 * rng.random(), 3500), 16.4 + rng.random() * 3.3, 1.0, rng.uniform(-0.8, 0.0))
    # room tone (everywhere, quieter in the empty scenes' silence is still 'air')
    room = band(noise(N), 30, 500)
    room /= np.abs(room).max()
    add(dry, room * 0.006, 0.0, 1.0, 0.0)
    dry = dry[:, :N]
    ghost = ghost[:, :N]
    out = reverb(dry, 0.12, 1.4, 6000) + reverb(ghost, 0.85, 3.5, 3500)
    return out


def main(path):
    music = render_music()
    sfx = render_sfx()
    mix = music * 1.0 + sfx * 1.0
    # fade in/out edges, soft limiter
    tt = np.arange(N) / SR
    mix *= np.clip(tt / 0.02, 0, 1)
    peak = np.abs(mix).max()
    mix = mix / peak * 0.89
    mix = np.tanh(mix * 1.1) / np.tanh(1.1)
    pcm = (np.clip(mix, -1, 1) * 32767).astype(np.int16).T.copy()
    with wave.open(path, 'wb') as w:
        w.setnchannels(2)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes(pcm.tobytes())
    print('wrote', path, 'peak', peak)


if __name__ == '__main__':
    main(sys.argv[1])

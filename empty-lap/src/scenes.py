"""THE EMPTY LAP - Episode 001 - full choreography (60 s @ 30 fps).

Every value here is keyframed animation for the procedural rigs in rig.py.
frame(t) -> (layers, overlays) where layers = [(state, weight), ...]
"""
import math
from anim import (kf, seg, window, lerp, clamp, smooth, ease_out, ease_in, linear,
                  ease_out_back, blink_auto)
import rig

FPS = 30
DURATION = 60.0
TAU = 2 * math.pi

# scene boundaries (seconds)
S1, S2, S3A, S3B, S3C, S4, S5, S6, S7, END = 0.0, 4.2, 13.0, 16.4, 19.75, 23.0, 34.0, 44.0, 53.0, 60.0

# anchors (world units)
LAP_CAT = (470.0, 1452.0)
REST_N = (470.0, 1394.0)     # near hand resting on the lap
REST_F = (790.0, 1405.0)     # far hand hanging at the side
ROOM_N = (606.0, 1236.0)     # near hand lifted to make room
FLOOR = rig.FLOOR_Y
LAUNCH_X = 215.0

# ------------------------------------------------------------------ looks
WARM = dict(tint=(1.0, 0.965, 0.90), pool=(0.20, 0.17, 0.13), sky=(0.98, 0.90, 0.74), win_a=0.55,
            season=None, patch_a=0.07, patch_x=330, light=(1.0, 0.9, 0.7), glow=0.35,
            glow_col=(1.0, 0.82, 0.55), vignette=0.50)
AUTUMN = dict(WARM, tint=(1.0, 0.94, 0.86), sky=(0.96, 0.80, 0.60), season='leaves', patch_a=0.09,
              patch_x=250, glow=0.45)
RAIN = dict(WARM, tint=(0.92, 0.93, 0.97), pool=(0.12, 0.12, 0.14), sky=(0.62, 0.66, 0.74),
            season='rain', patch_a=0.0, glow=0.10, glow_col=(0.8, 0.85, 1.0))
NIGHT = dict(WARM, tint=(0.80, 0.80, 0.88), pool=(0.16, 0.13, 0.09), sky=(0.20, 0.24, 0.36),
             season='snow', patch_a=0.0, glow=0.75, glow_col=(1.0, 0.75, 0.45), vignette=0.62)
DUSK = dict(WARM, tint=(0.90, 0.88, 0.90), pool=(0.12, 0.11, 0.12), sky=(0.72, 0.62, 0.62),
            season=None, patch_a=0.03, patch_x=300, glow=0.12, glow_col=(1.0, 0.8, 0.7), vignette=0.6)
DUSK_DARK = dict(DUSK, tint=(0.66, 0.67, 0.74), pool=(0.06, 0.06, 0.08), sky=(0.30, 0.32, 0.42),
                 glow=0.0, vignette=0.75)
PRESENT = dict(WARM, tint=(0.84, 0.86, 0.92), pool=(0.07, 0.08, 0.10), sky=(0.40, 0.45, 0.58),
               season='stars', win_a=0.40, patch_a=0.0, glow=0.0, glow_col=(0.8, 0.85, 1.0),
               vignette=0.62)
MEMORY = dict(WARM, win_a=0.30, glow=0.65)


def mix(a, b, w):
    out = {}
    for k in set(a) | set(b):
        va, vb = a.get(k, b.get(k)), b.get(k, a.get(k))
        if isinstance(va, (int, float)) and isinstance(vb, (int, float)):
            out[k] = lerp(va, vb, w)
        elif isinstance(va, tuple) and isinstance(vb, tuple):
            out[k] = lerp(va, vb, w)
        else:
            out[k] = vb if w >= 0.5 else va
    return out


def look(L, bell='box', **kw):
    S = dict(pool=L['pool'], sky=L['sky'], win_a=L['win_a'], season=L['season'], patch_a=L['patch_a'],
             patch_x=L['patch_x'], light=L['light'], bell=bell)
    S.update(kw)
    G = dict(tint=L['tint'], glow=L['glow'], glow_col=L['glow_col'], vignette=L['vignette'],
             glow_pos=(540, 1100))
    return S, G


# ------------------------------------------------------------------ bases
def char_base(t, seed=1, rate=1 / 3.6):
    return dict(yaw=-0.40, pitch=0.0, mouth=0.6, near_hand=REST_N, far_hand=REST_F,
                breath=TAU * t * rate, blink=blink_auto(t, seed), closed_style='soft',
                near_bow=0.12, far_bow=-0.10)


def cat_base(t):
    return dict(x=LAP_CAT[0], y=LAP_CAT[1], face=1, lie=1.0, eyes='happy', bell=True, tail_up=1.0,
                tail_sway=0.22, tail_phase=t * 2.2, breath=t * 2.6, floor_shadow=False,
                blink=0.0)


def cat_point(K, local):
    """World position of a point given in the cat's body frame (before flip)."""
    st, lie, curl, cr = K.get('stretch', 0), K.get('lie', 0), K.get('curl', 0), K.get('crouch', 0)
    rx = 122 * (1 + 0.16 * st) * (1 + 0.14 * lie - 0.10 * curl) * (1 + 0.05 * cr)
    ry = 84 * (1 - 0.10 * st) * (1 + 0.30 * lie + 0.25 * curl) * (1 - 0.10 * cr)
    legL = 46 * (1 - max(lie, curl)) * (1 - 0.75 * cr) * (1 - 0.3 * st) + 26 * K.get('dangle', 0)
    cy = -(legL + ry - 8)
    px, py = local[0] * rx, cy + local[1] * ry
    pv = (-rx * 0.55, 0.0)
    a = -K.get('rot', 0.0)
    c, s = math.cos(a), math.sin(a)
    x, y = px - pv[0], py - pv[1]
    x, y = pv[0] + x * c - y * s, pv[1] + x * s + y * c
    f = K.get('face', 1)
    return (K['x'] + f * x, K['y'] + y)


def jump_arc(u, t0, t1, p0, p1, h):
    p = seg(u, t0, t1, linear)
    x = lerp(p0[0], p1[0], smooth(p) * 0.6 + p * 0.4)
    y = lerp(p0[1], p1[1], p) - h * 4 * p * (1 - p)
    return x, y, p


def heart(u, t0, x, y, s=2.0):
    p = seg(u, t0, t0 + 1.5, linear)
    if p <= 0 or p >= 1:
        return None
    a = seg(p, 0, 0.2) * (1 - seg(p, 0.6, 1.0))
    return (x + 8 * math.sin(p * 6), y - 90 * ease_out(p), s * (0.7 + 0.3 * ease_out_back(min(1, p * 3))), a)


# ------------------------------------------------------------------ S1 hook
def s1(t):
    u = t - S1
    C = char_base(t, 11)
    if u < 2.25:
        f = ((u + 0.30) % 0.55) / 0.55
        h = 28 * math.sin(math.pi * f) ** 0.8
        C['near_hand'] = (466, 1392 - h)
    else:
        C['near_hand'] = kf(u, [(2.25, (466, 1392)), (2.7, (472, 1394))])
    C['yaw'] = kf(u, [(0, -0.55), (1.75, -0.55), (2.3, -0.88), (3.2, -0.84), (3.95, -0.52)])
    C['pitch'] = kf(u, [(0, 0.16), (1.75, 0.16), (2.3, -0.04), (3.2, -0.02), (3.95, 0.18)])
    C['mouth'] = kf(u, [(0, 0.20), (1.8, 0.20), (2.3, 0.45), (3.1, 0.40), (3.9, -0.05)])
    C['eye_scale'] = kf(u, [(0, 1.0), (1.8, 1.0), (2.25, 1.12), (3.2, 1.10), (3.9, 1.0)])
    C['head_tilt'] = kf(u, [(0, -0.04), (1.8, -0.04), (2.35, 0.03), (3.3, 0.02), (4.0, -0.05)])
    C['look'] = kf(u, [(0, (0, 0.3)), (1.8, (0, 0.3)), (2.3, (-1.0, 0)), (3.2, (-1.0, 0)), (3.9, (0, 0.4))])
    S, G = look(PRESENT)
    st = dict(cam=kf(u, [(0, (545, 1262, 1.16)), (4.4, (538, 1255, 1.27))], linear),
              set=S, char=C, cat=None, grade=G)
    return st


# ------------------------------------------------------------------ S2 happy days
def s2(t):
    u = max(0.0, t - S2)
    C = char_base(t, 2)
    K = cat_base(t)
    # --- cat: run in from the left, wiggle, jump, settle
    K['floor_shadow'] = True
    if u < 2.22:
        x = kf(u, [(0.2, -260), (1.25, 120, linear), (1.6, LAUNCH_X, ease_out)])
        gait = kf(u, [(0, 1.0), (1.2, 1.0), (1.6, 0.0)])
        ph = u * TAU * 3.0
        cr = kf(u, [(1.5, 0.0), (1.8, 0.85), (2.14, 0.9), (2.22, 0.3)])
        wig = window(u, 1.85, 2.10, 0.05)
        K.update(x=x + 5 * math.sin(u * TAU * 6) * wig, y=FLOOR, lie=0.0, eyes='open', gait=gait, phase=ph,
                 bob=7 * abs(math.sin(ph)) * gait, crouch=cr, tail_sway=0.45, tail_phase=t * 4.0,
                 bell_swing=ph, head_tilt=0.12 * cr)
    elif u < 2.68:
        x, y, p = jump_arc(u, 2.22, 2.68, (LAUNCH_X, FLOOR), LAP_CAT, 170)
        K.update(x=x, y=y, lie=0.0, eyes='open', jump=math.sin(math.pi * p) ** 0.6,
                 rot=0.38 * (1 - 2 * p) * math.sin(math.pi * p) * 1.6, tail_sway=0.3, bell_swing=u * 20)
    else:
        K['floor_shadow'] = False
        K['crouch'] = kf(u, [(2.68, 0.6), (2.98, 0.0, ease_out_back)])
        K['lie'] = kf(u, [(2.7, 0.0), (3.1, 0.6), (4.4, 0.62), (4.9, 0.3), (5.6, 0.45), (6.6, 1.0)])
        K['stretch'] = kf(u, [(4.4, 0), (4.9, 1.0), (5.25, 1.0), (5.7, 0)])
        K['eyes'] = 'open' if u < 2.95 else ('closed' if 4.5 < u < 5.5 else 'happy')
        K['head_tilt'] = kf(u, [(2.9, 0.0), (3.2, 0.22), (4.3, 0.22), (4.6, 0.0), (6.6, 0.04)])
        K['ear'] = window(u, 3.3, 3.5, 0.06) + window(u, 7.6, 7.75, 0.06)
        K['purr'] = seg(u, 3.0, 3.6) * 0.9
        K['tail_sway'] = 0.25
        K['bell_swing'] = math.exp(-(u - 2.68) * 3) * (u - 2.68) * 30
    # --- character
    C['yaw'] = kf(u, [(0, -0.62), (0.6, -0.92), (1.6, -0.80), (2.35, -0.50), (2.9, -0.36), (7.0, -0.32)])
    C['pitch'] = kf(u, [(0, 0.0), (1.6, 0.14), (2.6, 0.08), (3.0, 0.10)])
    C['look'] = kf(u, [(0, (-0.6, 0)), (1.6, (-0.8, 0.5)), (2.6, (0.4, 0.2)), (3.0, (0.6, 0.5))])
    C['mouth'] = kf(u, [(0, 0.55), (1.0, 0.75), (2.7, 1.0), (4.0, 0.85), (7.0, 0.95)])
    C['eye_scale'] = kf(u, [(0, 1.0), (2.0, 1.1), (2.9, 1.0)])
    C['feet_amp'] = window(u, 0.4, 2.0, 0.3) * 1.0 + 0.25 * seg(u, 6.6, 7.4)
    C['feet_phase'] = t * 6.0
    C['head_tilt'] = kf(u, [(0, 0.0), (2.9, 0.0), (3.4, -0.05), (6.4, -0.04), (7.0, -0.07)])
    hd, _, _, _ = rig.cat_head_world(K)
    scratch = (hd[0] - 18 + 8 * math.cos(u * TAU * 3.4), hd[1] - 66 + 6 * math.sin(u * TAU * 3.4))
    sp = ((u - 6.4) % 2.0) / 2.0
    stroke = (lerp(575, 450, smooth(sp / 0.7)) if sp < 0.7 else lerp(450, 575, smooth((sp - 0.7) / 0.3)),
              1288 + (0 if sp < 0.7 else -26 * math.sin(math.pi * (sp - 0.7) / 0.3)))
    C['near_hand'] = kf(u, [(0, REST_N), (1.45, REST_N), (1.95, ROOM_N), (2.5, ROOM_N),
                            (2.78, (540, 1310)), (2.95, scratch), (4.4, scratch), (4.8, ROOM_N),
                            (5.6, ROOM_N), (6.4, (575, 1288)), (8.8, stroke)])
    if u > 6.4:
        C['near_hand'] = stroke
    elif 2.95 <= u <= 4.4:
        C['near_hand'] = scratch
    C['far_hand'] = kf(u, [(0, REST_F), (2.45, REST_F), (2.75, (640, 1415)), (3.5, (650, 1418)),
                           (4.3, REST_F)])
    sb = kf(u, [(7.3, 0), (7.6, 1), (7.9, 1), (8.3, 0)])
    C['blink'] = max(C['blink'], sb)
    C['closed_style'] = 'happy'
    S, G = look(WARM, bell=None)
    hearts = [h for h in (heart(u, 6.9, 700, 1170, 2.3), heart(u, 7.35, 650, 1190, 1.6)) if h]
    st = dict(cam=kf(u, [(0, (520, 1262, 1.0)), (2.0, (520, 1262, 1.02)), (3.0, (540, 1268, 1.10)),
                         (8.8, (548, 1255, 1.26))]),
              set=S, char=C, cat=K, grade=G, hearts=hearts)
    return st


# ------------------------------------------------------------------ S3 routine montage
def s3a(t):
    u = max(0.0, t - S3A)
    C = char_base(t, 3)
    K = cat_base(t)
    if u < 0.55:
        K.update(x=LAUNCH_X, y=FLOOR, lie=0, eyes='open', crouch=kf(u, [(0, 0.3), (0.35, 0.85), (0.55, 0.9)]),
                 floor_shadow=True, head_tilt=0.15, tail_sway=0.4, tail_phase=t * 4)
    elif u < 0.98:
        x, y, p = jump_arc(u, 0.55, 0.98, (LAUNCH_X, FLOOR), LAP_CAT, 160)
        K.update(x=x, y=y, lie=0, eyes='open', jump=math.sin(math.pi * p) ** 0.6, floor_shadow=True,
                 rot=0.6 * (1 - 2 * p) * math.sin(math.pi * p), bell_swing=u * 20)
    else:
        K['crouch'] = kf(u, [(0.98, 0.55), (1.25, 0, ease_out_back)])
        K['lie'] = kf(u, [(1.0, 0.0), (1.4, 0.55), (2.9, 0.6), (3.4, 0.9)])
        K['knead'] = window(u, 1.3, 2.9, 0.15)
        K['knead_phase'] = u * 8.0
        K['eyes'] = 'happy'
        K['purr'] = seg(u, 1.3, 1.8) * 0.8
    C['near_hand'] = kf(u, [(0, REST_N), (0.15, REST_N), (0.5, ROOM_N), (1.4, ROOM_N), (1.9, (560, 1288)),
                            (3.4, (548, 1292))])
    C['yaw'] = kf(u, [(0, -0.72), (0.9, -0.5), (1.5, -0.36)])
    C['pitch'] = kf(u, [(0, 0.12), (1.0, 0.10)])
    C['mouth'] = kf(u, [(0, 0.7), (1.1, 0.95)])
    C['feet_amp'] = 0.3 * window(u, 1.2, 3.3)
    C['feet_phase'] = t * 4
    S, G = look(AUTUMN, bell=None)
    return dict(cam=kf(u, [(0, (520, 1262, 1.04)), (3.4, (532, 1262, 1.11))], linear), set=S, char=C,
                cat=K, grade=G)


def s3b(t):
    u = max(0.0, t - S3B)
    C = char_base(t, 4)
    K = cat_base(t)
    K['lie'] = 0.55
    K['eyes'] = 'open' if u < 2.55 else 'happy'
    K['head_tilt'] = kf(u, [(0, 0.30), (2.3, 0.30), (2.6, 0.12), (3.4, 0.10)])
    K['blink'] = kf(u, [(1.3, 0), (1.6, 1), (1.95, 1), (2.15, 0)])
    K['head_dx'] = kf(u, [(2.3, 0), (2.55, 10), (2.9, 4)])
    K['head_dy'] = kf(u, [(2.3, 0), (2.55, -14), (2.9, -6)])
    K['ear'] = window(u, 0.6, 0.75, 0.05)
    K['purr'] = seg(u, 2.5, 2.9) * 0.8
    C['blink'] = max(C['blink'] * (1 - window(u, 0.2, 2.2, 0.01)), kf(u, [(0.4, 0), (0.75, 1), (1.05, 1), (1.3, 0)]))
    C['yaw'] = -0.30
    C['pitch'] = kf(u, [(0, 0.16), (3.4, 0.18)])
    C['look'] = (0.7, 0.6)
    C['mouth'] = kf(u, [(0, 0.6), (2.4, 0.65), (2.75, 1.0)])
    C['head_tilt'] = kf(u, [(0, 0.0), (2.5, 0.0), (3.0, -0.06)])
    hd, _, _, _ = rig.cat_head_world(K)
    C['near_hand'] = kf(u, [(0, (hd[0] - 40, hd[1] - 30)), (2.2, (hd[0] - 30, hd[1] - 40)),
                            (2.6, (hd[0] - 6, hd[1] - 74)), (3.4, (hd[0] - 10, hd[1] - 70))])
    S, G = look(RAIN, bell=None)
    return dict(cam=kf(u, [(0, (585, 1185, 1.55)), (3.4, (585, 1180, 1.63))], linear), set=S, char=C,
                cat=K, grade=G)


def s3c(t):
    u = max(0.0, t - S3C)
    C = char_base(t, 5, rate=1 / 4.0)
    K = cat_base(t)
    K.update(lie=0.2, curl=1.0, eyes='closed', purr=0.45, breath=TAU * t / 4.0 + 0.4, breath_amp=1.4,
             tail_sway=0.12 + 0.25 * window(u, 1.6, 2.0, 0.1), tail_phase=t * 3.0)
    C['blink'] = 1.0
    C['pitch'] = 0.20
    C['yaw'] = -0.34
    C['head_tilt'] = kf(u, [(0, -0.04), (3.3, -0.07)])
    C['crouch'] = 0.10
    C['mouth'] = 0.5
    C['breath_amp'] = 1.4
    C['near_hand'] = (540, 1318)
    C['far_hand'] = (735, 1420)
    S, G = look(NIGHT, bell=None)
    return dict(cam=kf(u, [(0, (540, 1262, 1.14)), (3.3, (540, 1252, 1.22))], linear), set=S, char=C,
                cat=K, grade=G)


# ------------------------------------------------------------------ S4 something changes
def s4(t):
    u = max(0.0, t - S4)
    C = char_base(t, 6)
    K = cat_base(t)
    K.update(floor_shadow=True, lie=0.0, eyes='open', tail_up=0.35, tail_sway=0.15, tail_phase=t * 1.6)
    hold = None
    if u < 2.8:
        x = kf(u, [(0, -250), (2.2, 210, ease_out)])
        gait = kf(u, [(0, 0.55), (1.8, 0.55), (2.25, 0.0)])
        ph = u * TAU * 1.5
        K.update(x=x, y=FLOOR, gait=gait, phase=ph, head_dy=10, bob=2 * abs(math.sin(ph)) * gait,
                 crouch=kf(u, [(2.2, 0), (2.8, 0.75)]), bell_swing=ph)
    elif u < 3.35:
        x, y, p = jump_arc(u, 2.8, 3.35, (210, FLOOR), (290, FLOOR), 230)
        K.update(x=x, y=y, jump=math.sin(math.pi * p) ** 0.6, rot=0.45 * math.sin(math.pi * p) * (1 - p),
                 bell_swing=u * 25)
    elif u < 5.0:
        K.update(x=kf(u, [(3.35, 290), (3.8, 268)]), y=FLOOR,
                 crouch=kf(u, [(3.35, 0.7), (3.8, 0.1), (4.6, 0.1), (5.0, 0.55)]),
                 rot=0.08 * math.sin((u - 3.35) * 14) * math.exp(-(u - 3.35) * 4),
                 head_tilt=kf(u, [(3.6, 0.0), (4.0, 0.3), (4.6, 0.3), (5.0, 0.1)]),
                 ear_down=seg(u, 3.4, 3.8) * 0.6, bell_swing=math.exp(-(u - 3.35) * 3) * u * 20)
    elif u < 6.0:
        r = kf(u, [(5.0, 0.0), (5.45, 0.95, ease_out), (6.0, 0.85)])
        K.update(x=kf(u, [(5.0, 268), (5.45, 276)]), y=FLOOR, rot=r, jump=0.5 * seg(u, 5.0, 5.3),
                 knead=seg(u, 5.45, 5.6), knead_phase=u * 16, head_tilt=0.1, ear_down=0.5, bell_swing=u * 12,
                 crouch=kf(u, [(5.0, 0.55), (5.2, 0.0)]))
    elif u < 7.3:
        p = seg(u, 6.0, 7.3)
        K.update(x=lerp(276, LAP_CAT[0], p), y=lerp(FLOOR, LAP_CAT[1], p) - 40 * math.sin(math.pi * p),
                 rot=lerp(0.85, 0.0, p), dangle=1 - seg(u, 6.6, 7.3), jump=0.5 * (1 - p),
                 lie=0.6 * seg(u, 6.8, 7.3), floor_shadow=p < 0.5, head_tilt=0.1, ear_down=0.5 * (1 - p),
                 bell_swing=u * 6)
        hold = p
    else:
        K.update(x=LAP_CAT[0], y=LAP_CAT[1], floor_shadow=False,
                 lie=kf(u, [(7.3, 0.6), (8.6, 0.25)]), curl=kf(u, [(7.3, 0.0), (8.6, 1.0)]),
                 eyes='open' if u < 7.9 else 'closed', blink=kf(u, [(7.6, 0), (7.9, 1)]),
                 purr=0.35 * window(u, 8.6, 10.3, 0.4), breath=TAU * t / 2.4, breath_amp=0.8,
                 tail_sway=0.08, head_tilt=0.0)
    # --- character
    C['yaw'] = kf(u, [(0, -0.75), (2.0, -0.82), (3.0, -0.85), (3.3, -0.95), (5.0, -0.92), (6.6, -0.6),
                      (7.4, -0.32), (11, -0.30)])
    C['pitch'] = kf(u, [(0, 0.06), (2.0, 0.12), (3.3, 0.28), (5.0, 0.30), (7.3, 0.20), (8.0, 0.24)])
    C['look'] = kf(u, [(0, (-0.6, 0.3)), (3.3, (-1, 1)), (6.5, (-0.5, 1)), (7.5, (0.6, 0.6))])
    C['mouth'] = kf(u, [(0, 0.55), (2.8, 0.55), (3.25, 0.0), (5.5, -0.12), (7.5, -0.08), (9.0, -0.15)])
    C['mouth_open'] = window(u, 3.25, 3.75, 0.08) * 0.7
    C['eye_scale'] = kf(u, [(3.1, 1.0), (3.35, 1.28), (4.2, 1.12), (6.0, 1.06), (8.0, 1.0)])
    C['lean'] = kf(u, [(4.9, 0.0), (5.6, -0.30), (6.1, -0.30), (7.3, 0.0)])
    C['crouch'] = kf(u, [(4.9, 0.0), (5.6, 0.65), (6.1, 0.65), (7.3, 0.08)])
    C['head_tilt'] = kf(u, [(0, 0), (3.3, -0.04), (7.5, -0.02), (8.6, -0.09)])
    # hands
    if 5.0 <= u < 7.3:
        chest = cat_point(K, (0.55, 0.15))
        belly = cat_point(K, (0.0, 0.85))
        w = seg(u, 5.0, 5.75)
        C['near_hand'] = lerp(kf(u, [(5.0, ROOM_N), (5.5, (420, 1360))]), (chest[0] - 10, chest[1]), w)
        C['far_hand'] = lerp(REST_F, (belly[0] + 10, belly[1] + 18), w)
        C['near_bow'] = 0.18
    elif u >= 7.3:
        hd, _, _, _ = rig.cat_head_world(K)
        sp = ((u - 8.6) % 2.4) / 2.4 if u > 8.6 else 0.0
        if sp < 0.72:
            q = smooth(sp / 0.72)
            hp = (hd[0] - 14 - 150 * q, hd[1] - 58 + 18 * q)
        else:
            q = smooth((sp - 0.72) / 0.28)
            hp = (hd[0] - 164 + 150 * q, hd[1] - 40 - 18 * q - 22 * math.sin(math.pi * q))
        C['near_hand'] = kf(u, [(7.3, (520, 1330)), (8.2, (hd[0] - 14, hd[1] - 58)), (8.6, hp)])
        if u > 8.6:
            C['near_hand'] = hp
        C['far_hand'] = kf(u, [(7.3, (560, 1440)), (8.2, (700, 1425))])
    else:
        C['near_hand'] = kf(u, [(0, REST_N), (1.2, REST_N), (1.8, ROOM_N), (3.2, ROOM_N),
                                (3.4, (610, 1215)), (4.2, ROOM_N)])
    sb = kf(u, [(9.4, 0), (9.75, 1), (10.1, 1), (10.5, 0)])
    C['blink'] = max(C['blink'], sb)
    L = mix(DUSK, DUSK_DARK, seg(u, 6.0, 11.0))
    S, G = look(L, bell=None)
    cam = kf(u, [(0, (470, 1285, 1.0)), (2.5, (450, 1300, 1.05)), (5.0, (470, 1312, 1.12)),
                 (7.3, (540, 1272, 1.22)), (11.0, (560, 1235, 1.50))])
    return dict(cam=cam, set=S, char=C, cat=K, grade=G)


# ------------------------------------------------------------------ S5 the empty space
def s5(t):
    u = max(0.0, t - S5)
    C = char_base(t, 7, rate=1 / 4.0)
    C['near_hand'] = kf(u, [(0, REST_N), (1.5, REST_N), (2.4, ROOM_N), (5.5, ROOM_N), (6.9, REST_N)])
    C['near_hand'] = (C['near_hand'][0] + 2 * math.sin(t * 0.7), C['near_hand'][1])
    C['yaw'] = kf(u, [(0, -0.5), (1.4, -0.5), (2.4, -0.88), (5.5, -0.92), (6.9, 0.42), (8.0, 0.40),
                      (9.1, -0.50)])
    C['pitch'] = kf(u, [(0, 0.12), (1.4, 0.12), (2.4, -0.02), (5.5, 0.02), (6.9, 0.26), (8.0, 0.26),
                        (9.1, 0.32)])
    C['look'] = kf(u, [(0, (0, 0.4)), (2.4, (-1, 0)), (5.5, (-1, 0.2)), (6.9, (1, 0.8)), (8.0, (0.8, 0.8)),
                       (9.1, (0, 1))])
    C['mouth'] = kf(u, [(0, 0.05), (1.5, 0.05), (2.4, 0.22), (5.0, 0.12), (6.9, -0.05), (8.0, -0.2),
                        (9.2, -0.35)])
    C['eye_scale'] = kf(u, [(1.5, 1.0), (2.4, 1.08), (5.0, 1.04), (6.5, 1.0)])
    C['head_tilt'] = kf(u, [(0, 0.0), (3.0, 0.02), (5.0, -0.02), (8.0, 0.0), (9.4, -0.05)])
    C['crouch'] = kf(u, [(8.0, 0.0), (9.4, 0.12)])
    S, G = look(PRESENT, bell='box')
    cam = kf(u, [(0, (540, 1250, 1.0)), (2.4, (530, 1252, 1.0)), (5.5, (440, 1270, 1.05)),
                 (7.4, (660, 1300, 1.18)), (10.0, (560, 1240, 1.30))])
    return dict(cam=cam, set=S, char=C, cat=None, grade=G)


# ------------------------------------------------------------------ S6 the memory
def s6(t):
    u = max(0.0, t - S6)
    C = char_base(t, 8, rate=1 / 3.2)
    eyes = kf(u, [(0, 0.0), (1.1, 1.0), (5.0, 1.0), (5.7, 0.0)])
    C['blink'] = max(eyes, C['blink'] if u > 6.0 else 0.0)
    C['yaw'] = -0.50
    C['pitch'] = kf(u, [(0, 0.32), (6.0, 0.28), (9, 0.27)])
    C['look'] = (0, 1)
    C['mouth'] = kf(u, [(0, -0.35), (2.0, 0.2), (4.6, 0.25), (5.6, -0.1), (6.5, -0.45)])
    C['crouch'] = 0.12
    C['head_tilt'] = kf(u, [(0, -0.05), (3.0, -0.07), (6.5, -0.03)])
    alpha = kf(u, [(1.0, 0.0), (1.9, 0.80), (4.8, 0.80), (5.9, 0.0)])
    M = cat_base(t)
    M.update(lie=1.0, curl=kf(u, [(1.4, 0.0), (2.8, 0.55)]), eyes='happy' if u < 2.4 else 'closed',
             ghost=True, alpha=alpha, purr=0.6, bell=True, breath=TAU * t / 2.6)
    # instinctive strokes over the remembered cat
    if 2.2 <= u < 5.0:
        sp = ((u - 2.2) % 1.4) / 1.4
        if sp < 0.7:
            q = smooth(sp / 0.7)
            hp = (lerp(565, 430, q), 1288 + 10 * q)
        else:
            q = smooth((sp - 0.7) / 0.3)
            hp = (lerp(430, 565, q), 1298 - 10 * q - 24 * math.sin(math.pi * q))
        C['near_hand'] = lerp(kf(u, [(1.6, REST_N), (2.2, (565, 1288))]), hp, seg(u, 2.2, 2.35))
    else:
        C['near_hand'] = kf(u, [(1.6, REST_N), (2.2, (565, 1288)), (5.0, (565, 1288)), (5.9, (500, 1360)),
                                (6.6, (488, 1392))])
    C['tear'] = kf(u, [(6.0, 0.0), (8.8, 1.0)], linear) if u >= 6.0 else -1.0
    L = mix(PRESENT, MEMORY, alpha / 0.80 * 0.8)
    S, G = look(L, bell='box')
    cam = kf(u, [(0, (560, 1240, 1.30)), (5.0, (560, 1180, 1.50)), (8.6, (560, 1060, 1.85)),
                 (9.0, (560, 1052, 1.86))])
    return dict(cam=cam, set=S, char=C, cat=None, memory=M if alpha > 0 else None, grade=G)


# ------------------------------------------------------------------ S7 the ending
def s7(t):
    u = max(0.0, t - S7)
    C = char_base(t, 9, rate=1 / 3.8)
    C['tear'] = 1.0
    C['yaw'] = kf(u, [(0, -0.50), (1.2, 0.45), (1.6, 0.40), (2.4, -0.46)])
    C['pitch'] = kf(u, [(0, 0.27), (1.2, 0.30), (2.4, 0.32)])
    C['look'] = kf(u, [(0, (0, 1)), (1.2, (1, 1)), (2.4, (0, 1))])
    C['lean'] = kf(u, [(0, 0.0), (1.2, 0.10), (2.3, 0.0)])
    C['crouch'] = kf(u, [(0, 0.12), (2.0, 0.05), (3.0, 0.14)])
    bell_pick = rig.BELL_BOX
    C['far_hand'] = kf(u, [(0, REST_F), (1.2, (bell_pick[0] + 4, bell_pick[1] - 30)),
                           (1.45, (bell_pick[0] - 10, bell_pick[1] - 40)), (2.35, (498, 1360)),
                           (2.6, (505, 1355)), (3.6, (508, 1338))])
    C['far_bow'] = kf(u, [(0, -0.10), (1.2, -0.16), (2.3, 0.10), (3.6, 0.22)])
    C['near_hand'] = kf(u, [(0, REST_N), (2.3, REST_N), (3.6, (446, 1342))])
    C['near_bow'] = kf(u, [(2.3, 0.12), (3.6, 0.55)])
    C['sigh'] = window(u, 2.8, 3.6, 0.4)
    eyes = kf(u, [(3.0, 0.0), (3.5, 1.0)])
    C['blink'] = max(C['blink'], eyes)
    C['mouth'] = kf(u, [(0, -0.45), (2.4, -0.35), (3.6, 0.12), (5.0, 0.2)])
    C['head_tilt'] = kf(u, [(0, -0.03), (2.4, -0.04), (3.6, -0.10)])
    if u < 1.3:
        bell = 'box'
    elif u < 2.4:
        bell = 'hand'
    else:
        bell = 'lap'
    warm = seg(u, 2.6, 6.5) * 0.45
    L = mix(PRESENT, MEMORY, warm)
    L['win_a'] = PRESENT['win_a']
    S, G = look(L, bell=bell, bell_pos=(482, 1392))
    cam = kf(u, [(0, (560, 1052, 1.86)), (1.6, (650, 1262, 1.30)), (2.6, (580, 1280, 1.28)),
                 (7.0, (560, 1245, 0.92), linear)])
    return dict(cam=cam, set=S, char=C, cat=None, grade=G)


# ------------------------------------------------------------------ timeline
def frame(t):
    L = []
    ov = {'captions': []}
    if t < S2 + 0.3:
        w = seg(t, 3.98, 4.22)
        if w < 1:
            L.append((s1(t), 1.0))
        if w > 0:
            L.append((s2(t), w))
        ov['bloom'] = kf(t, [(3.86, 0.0), (4.10, 0.93), (4.42, 0.0)])
    elif t < S3A + 0.2:
        L.append((s2(t), 1.0))
        if t > S3A - 0.2:
            L.append((s3a(t), seg(t, S3A - 0.2, S3A + 0.2)))
    elif t < S3B + 0.2:
        L.append((s3a(t), 1.0))
        if t > S3B - 0.2:
            L.append((s3b(t), seg(t, S3B - 0.2, S3B + 0.2)))
    elif t < S3C + 0.2:
        L.append((s3b(t), 1.0))
        if t > S3C - 0.2:
            L.append((s3c(t), seg(t, S3C - 0.2, S3C + 0.2)))
    elif t < S4 + 0.25:
        L.append((s3c(t), 1.0))
        if t > S4 - 0.25:
            L.append((s4(t), seg(t, S4 - 0.25, S4 + 0.25)))
    elif t < S5:
        L.append((s4(t), 1.0))
        ov['black'] = seg(t, S5 - 0.75, S5 - 0.05)
    elif t < S6:
        L.append((s5(t), 1.0))
        ov['black'] = 1 - seg(t, S5, S5 + 0.8)
    elif t < S7:
        L.append((s6(t), 1.0))
    else:
        L.append((s7(t), 1.0))
        ov['black'] = seg(t, 58.9, 59.85)
    a1 = seg(t, 0.12, 0.55) * (1 - seg(t, 3.4, 3.95))
    if a1 > 0:
        ov['captions'].append(("He still saved her a spot.", a1, 250, 56, seg(t, 0.12, 0.8)))
    a2 = seg(t, S7 + 3.4, S7 + 4.2)
    if a2 > 0:
        ov['captions'].append(("Some spaces stay filled with love.", a2, 250, 52, seg(t, S7 + 3.4, S7 + 4.6)))
    return L, ov

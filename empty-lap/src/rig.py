"""Character, cat and set rigs for THE EMPTY LAP.

All shapes are drawn procedurally with cairo so the characters stay perfectly
on-model in every frame. Proportions, line weight, the offset gray drop-shadow
and the black void background are matched to reference/character_reference.jpg
(world units = reference pixels x 1.78).
"""
import math
import cairo
from anim import clamp, lerp, wob

INK = (0.13, 0.13, 0.15)
WHITE = (0.985, 0.985, 0.98)
GRAY = (0.68, 0.68, 0.69)        # offset shadow, sampled from the reference (174,174,174)
FARW = (0.90, 0.90, 0.91)        # far-side limbs
BLUE = (0.36, 0.62, 0.95)        # tear marks (reference ~ (80,150,240))
TEARC = (0.40, 0.66, 0.98)
LW = 5.0
SH = (13.0, 11.0)                # shadow offset (down-right, as in reference)
STYLE = {'shadows': True}        # switched off for the translucent memory cat

FLOOR_Y = 1690.0
HIP = (655.0, 1478.0)            # seat contact point of the character
BOX = (548.0, 1513.0, 905.0, 1688.0)   # stool box (x0,y0,x1,y1)
BELL_BOX = (850.0, 1491.0)       # where the bell rests on the box


# ----------------------------------------------------------------- primitives
def rot(p, a, o=(0.0, 0.0)):
    c, s = math.cos(a), math.sin(a)
    x, y = p[0] - o[0], p[1] - o[1]
    return (o[0] + x * c - y * s, o[1] + x * s + y * c)


def ellipse_pts(cx, cy, rx, ry, rot_a=0.0, seed=0.0, t=0.0, amp=0.8, n=80, shape=None):
    pts = []
    c, s = math.cos(rot_a), math.sin(rot_a)
    for i in range(n):
        th = 2 * math.pi * i / n
        k = 1 + amp * (0.6 * math.sin(3 * th + seed * 1.7 + 0.8 * t)
                       + 0.4 * math.sin(5 * th + seed * 3.1 - 0.6 * t)) / max(rx, ry, 1)
        x, y = rx * math.cos(th) * k, ry * math.sin(th) * k
        if shape:
            x, y = shape(th, x, y)
        pts.append((cx + x * c - y * s, cy + x * s + y * c))
    return pts


def path(ctx, pts, closed=True):
    ctx.move_to(*pts[0])
    for p in pts[1:]:
        ctx.line_to(*p)
    if closed:
        ctx.close_path()


def shape(ctx, pts, fill=WHITE, ink=INK, lw=LW, shadow=True, shadow_col=GRAY):
    if shadow and STYLE['shadows']:
        path(ctx, [(x + SH[0], y + SH[1]) for x, y in pts])
        ctx.set_source_rgb(*shadow_col)
        ctx.fill()
    path(ctx, pts)
    ctx.set_source_rgb(*fill)
    ctx.fill()
    if ink is not None and lw > 0:
        path(ctx, pts)
        ctx.set_source_rgb(*ink)
        ctx.set_line_width(lw)
        ctx.stroke()


def quad_pts(p0, p1, p2, n=18):
    out = []
    for i in range(n + 1):
        u = i / n
        a = (1 - u) ** 2
        b = 2 * (1 - u) * u
        c = u * u
        out.append((a * p0[0] + b * p1[0] + c * p2[0], a * p0[1] + b * p1[1] + c * p2[1]))
    return out


def tube(ctx, pts, w, fill=WHITE, ink=INK, lw=LW, shadow=True, start_ink=0):
    """A rounded limb: outline stroke + fill stroke. start_ink skips the outline
    on the first N points so limbs blend into the body they grow from."""
    ctx.set_line_cap(cairo.LINE_CAP_ROUND)
    ctx.set_line_join(cairo.LINE_JOIN_ROUND)
    if shadow and STYLE['shadows']:
        path(ctx, [(x + SH[0], y + SH[1]) for x, y in pts], closed=False)
        ctx.set_source_rgb(*GRAY)
        ctx.set_line_width(w + lw)
        ctx.stroke()
    ip = pts[start_ink:] if start_ink else pts
    if len(ip) >= 2:
        path(ctx, ip, closed=False)
        ctx.set_source_rgb(*ink)
        ctx.set_line_width(w + 2 * lw)
        ctx.stroke()
    path(ctx, pts, closed=False)
    ctx.set_source_rgb(*fill)
    ctx.set_line_width(w)
    ctx.stroke()


def line(ctx, pts, lw=LW, col=INK, closed=False):
    ctx.set_line_cap(cairo.LINE_CAP_ROUND)
    ctx.set_line_join(cairo.LINE_JOIN_ROUND)
    path(ctx, pts, closed)
    ctx.set_source_rgb(*col)
    ctx.set_line_width(lw)
    ctx.stroke()


def rounded_rect_pts(x0, y0, x1, y1, r, n=6):
    pts = []
    for cx, cy, a0 in ((x1 - r, y0 + r, -math.pi / 2), (x1 - r, y1 - r, 0),
                       (x0 + r, y1 - r, math.pi / 2), (x0 + r, y0 + r, math.pi)):
        for i in range(n + 1):
            a = a0 + (math.pi / 2) * i / n
            pts.append((cx + r * math.cos(a), cy + r * math.sin(a)))
    return pts


def ik(s, p, l1, l2, bend):
    """Two-bone IK. bend=+1/-1 picks elbow side. Returns (elbow, hand)."""
    dx, dy = p[0] - s[0], p[1] - s[1]
    d = math.hypot(dx, dy)
    reach = l1 + l2
    if d > reach * 0.999:
        k = min(d / reach, 1.15)       # cartoon stretch up to 15%
        l1 *= k
        l2 *= k
        reach = l1 + l2
        if d > reach * 0.999:
            d = reach * 0.999
            p = (s[0] + dx / math.hypot(dx, dy) * d, s[1] + dy / math.hypot(dx, dy) * d)
    d = max(d, 1e-3)
    a = math.atan2(dy, dx)
    cosb = clamp((l1 * l1 + d * d - l2 * l2) / (2 * l1 * d), -1, 1)
    b = math.acos(cosb)
    e = (s[0] + l1 * math.cos(a + bend * b), s[1] + l1 * math.sin(a + bend * b))
    return e, p


def heart_pts(cx, cy, s):
    pts = []
    for i in range(60):
        t = 2 * math.pi * i / 60
        x = 16 * math.sin(t) ** 3
        y = -(13 * math.cos(t) - 5 * math.cos(2 * t) - 2 * math.cos(3 * t) - math.cos(4 * t))
        pts.append((cx + x * s, cy + y * s))
    return pts


# ----------------------------------------------------------------- bell
def draw_bell(ctx, x, y, s=1.0, ribbon=False, ang=0.0, t=0.0):
    ctx.save()
    ctx.translate(x, y)
    ctx.rotate(ang)
    ctx.scale(s, s)
    if ribbon:
        # the little collar, coiled beside the bell
        pts = ellipse_pts(-6, 10, 34, 10, 0.0, seed=3, t=0, amp=0.5, n=48)
        line(ctx, pts, lw=5.5, col=INK, closed=True)
        line(ctx, pts, lw=2.0, col=(0.55, 0.58, 0.62), closed=True)
    pts = ellipse_pts(0, 0, 13, 12.5, n=40, amp=0.2)
    shape(ctx, pts, fill=(0.93, 0.92, 0.88), lw=3.0)
    line(ctx, [(-7, 2), (7, 2)], lw=2.4)
    ctx.arc(0, 6, 2.2, 0, 2 * math.pi)
    ctx.set_source_rgb(*INK)
    ctx.fill()
    ctx.arc(-4.5, -4.5, 3.0, 0, 2 * math.pi)
    ctx.set_source_rgb(1, 1, 1)
    ctx.fill()
    ctx.arc(0, -14, 4, 0, 2 * math.pi)
    ctx.set_source_rgb(*INK)
    ctx.set_line_width(2.4)
    ctx.stroke()
    ctx.restore()


# ----------------------------------------------------------------- character
def ub(C, p):
    """Upper-body local (relative to HIP) -> world."""
    x, y = p
    cr = C.get('crouch', 0.0)
    y = y * (1 - 0.07 * cr)
    q = rot((x, y), C.get('lean', 0.0))
    return (HIP[0] + q[0] - 34 * cr, HIP[1] + q[1] + 30 * cr)


def char_geom(C):
    b = math.sin(C.get('breath', 0.0)) * C.get('breath_amp', 1.0)
    sigh = C.get('sigh', 0.0)
    G = {}
    G['breath'] = b
    G['neck'] = ub(C, (-70, -318 - 4 * b - 10 * sigh))
    a = C.get('lean', 0.0) + C.get('head_tilt', 0.0)
    G['head_ang'] = a
    G['head'] = (G['neck'][0] + (-33 * math.cos(a) + 232 * math.sin(a)),
                 G['neck'][1] + (-33 * math.sin(a) - 232 * math.cos(a)))
    G['sh_near'] = ub(C, (22, -300 - 3 * b - 8 * sigh))
    G['sh_far'] = ub(C, (84, -318 - 3 * b - 8 * sigh))
    return G


HEAD_R = 224.0


def draw_head(ctx, C, G, t):
    hx, hy = G['head']
    pts = ellipse_pts(hx, hy, HEAD_R, HEAD_R * 0.985, G['head_ang'], seed=1, t=t, amp=0.9)
    # gray rim like the reference: shows at the top and right of the head
    path(ctx, [(x + 13, y - 9) for x, y in pts])
    ctx.set_source_rgb(*GRAY)
    ctx.fill()
    shape(ctx, pts, shadow=False)
    ctx.save()
    path(ctx, pts)
    ctx.clip()
    ctx.translate(hx, hy)
    ctx.rotate(G['head_ang'])
    draw_face(ctx, C, t)
    ctx.restore()
    path(ctx, pts)
    ctx.set_source_rgb(*INK)
    ctx.set_line_width(LW)
    ctx.stroke()


def proj(yaw, pitch, r=HEAD_R * 0.93):
    return (r * math.sin(yaw) * math.cos(max(0.0, pitch - 0.6)), r * math.sin(min(pitch, 1.1))), math.cos(yaw)


def draw_face(ctx, C, t):
    yaw = clamp(C.get('yaw', -0.40), -0.64, 0.58)
    pitch = 0.5 * C.get('pitch', 0.0)
    es = C.get('eye_scale', 1.0)
    blink = clamp(C.get('blink', 0.0))
    style = C.get('closed_style', 'soft')
    lx, ly = C.get('look', (0.0, 0.0))
    eyes = []
    for d in (-0.34, 0.34):
        (x, y), vis = proj(yaw + d, 0.72 + pitch)
        eyes.append((x + lx * 7, y + ly * 6, vis))
    for i, (x, y, vis) in enumerate(eyes):
        if vis < 0.12:
            continue
        sx = clamp(vis * 1.15, 0.35, 1.0)
        # static blue tear mark (reference: small drop just under each eye)
        tx, ty = x - 9 * sx, y + 19 * es
        ctx.save()
        ctx.translate(tx, ty)
        ctx.scale(sx * 1.3, 1.3)
        ctx.move_to(0, -9)
        ctx.curve_to(5, -2, 8, 3, 6, 7)
        ctx.curve_to(4, 11, -4, 11, -6, 7)
        ctx.curve_to(-8, 3, -5, -2, 0, -9)
        ctx.set_source_rgb(*BLUE)
        ctx.fill()
        ctx.restore()
        r = 14.5 * es
        if blink < 0.82:
            ctx.save()
            ctx.translate(x, y)
            ctx.scale(sx, max(0.1, 1 - blink))
            ctx.arc(0, 0, r, 0, 2 * math.pi)
            ctx.set_source_rgb(*INK)
            ctx.fill()
            ctx.arc(-4.5, -5.0, 3.6 * es, 0, 2 * math.pi)
            ctx.set_source_rgb(1, 1, 1)
            ctx.fill()
            ctx.restore()
        else:
            w = 12 * sx
            if style == 'happy':
                pts = quad_pts((x - w, y + 3), (x, y - 12), (x + w, y + 3), 10)
            else:
                pts = quad_pts((x - w, y - 1), (x, y + 8), (x + w, y - 1), 10)
            line(ctx, pts, lw=4.2)
    (mx, my), mvis = proj(yaw, 0.90 + pitch)
    if mvis > 0.15:
        m = C.get('mouth', 0.6)
        mo = C.get('mouth_open', 0.0)
        w = 20 * clamp(mvis * 1.2, 0.4, 1)
        if mo > 0.05:
            ctx.save()
            ctx.translate(mx, my + 2)
            ctx.scale(1, 1.1)
            ctx.arc(0, 0, 6 + 4 * mo, 0, 2 * math.pi)
            ctx.set_source_rgb(*INK)
            ctx.fill()
            ctx.restore()
        else:
            pts = quad_pts((mx - w, my - 3 * m), (mx, my + 16 * m), (mx + w, my - 3 * m), 12)
            line(ctx, pts, lw=4.0)
    # moving tear
    tp = C.get('tear', -1.0)
    if tp >= 0:
        x, y, vis = eyes[0]
        grow = clamp(tp / 0.22)
        slide = clamp((tp - 0.22) / 0.78)
        ty = y + 26 + 120 * (slide ** 1.4)
        tx = x - 4 - 10 * slide - 6 * math.sin(slide * 3)
        if slide > 0:
            ctx.set_source_rgba(*TEARC, 0.35)
            ctx.set_line_width(3.0)
            ctx.move_to(x - 2, y + 22)
            ctx.curve_to(x - 4, y + 40, tx + 2, ty - 30, tx, ty - 8)
            ctx.stroke()
        s = 0.35 + 0.75 * grow
        a = 1.0 - clamp((tp - 0.92) / 0.08)
        ctx.save()
        ctx.translate(tx, ty)
        ctx.scale(s, s * (1 + 0.15 * slide))
        ctx.move_to(0, -16)
        ctx.curve_to(7, -5, 12, 3, 10, 9)
        ctx.curve_to(7, 16, -7, 16, -10, 9)
        ctx.curve_to(-12, 3, -7, -5, 0, -16)
        ctx.set_source_rgba(*TEARC, a)
        ctx.fill_preserve()
        ctx.set_source_rgba(0.15, 0.30, 0.55, a)
        ctx.set_line_width(2)
        ctx.stroke()
        ctx.arc(-3.5, 4, 2.6, 0, 2 * math.pi)
        ctx.set_source_rgba(1, 1, 1, 0.9 * a)
        ctx.fill()
        ctx.restore()


def draw_torso(ctx, C, G, t):
    b = G['breath']
    sigh = C.get('sigh', 0.0)
    # bean-shaped body: wider at the bottom, sits on the box
    def sh(th, x, y):
        k = 1 + 0.07 * math.sin(th)
        return x * k, y
    cx, cy = -18, -222 - 2 * b - 5 * sigh
    rx, ry = 122 * (1 + 0.012 * b + 0.02 * sigh), 236 * (1 + 0.010 * b + 0.025 * sigh)
    local = ellipse_pts(cx, cy, rx, ry, -0.06, seed=2, t=t, amp=0.9, shape=sh)
    pts = [ub(C, p) for p in local]
    shape(ctx, pts)


def draw_legs(ctx, C, t):
    sw = C.get('feet_amp', 0.0)
    ph = C.get('feet_phase', t * 5.0)
    knee = (392.0, 1468.0)
    # far shin (behind)
    a2 = 0.04 + sw * 0.16 * math.sin(ph + 2.0)
    top2 = (knee[0] + 70, knee[1] + 10)
    foot2 = rot((top2[0] + 8, top2[1] + 182), a2, top2)
    tube(ctx, [top2, foot2], 90)
    # near shin
    a1 = -0.02 + sw * 0.18 * math.sin(ph)
    top1 = (knee[0] - 2, knee[1] + 4)
    foot1 = rot((top1[0] + 4, top1[1] + 186), a1, top1)
    tube(ctx, [top1, foot1], 94)
    # thigh: a fat rounded tube from the hip to the knee (reference: soft sloping lap)
    tube(ctx, quad_pts((650, 1440), (520, 1438), (knee[0] + 8, knee[1] - 6), 10), 128)


def _offset_poly(pts, widths, extra=0.0):
    """Closed outline polygon around a centreline with per-point half-widths."""
    left, right = [], []
    n = len(pts)
    for i in range(n):
        a = pts[max(0, i - 1)]
        b = pts[min(n - 1, i + 1)]
        dx, dy = b[0] - a[0], b[1] - a[1]
        d = math.hypot(dx, dy) or 1.0
        nx, ny = -dy / d, dx / d
        w = widths[i] / 2 + extra
        left.append((pts[i][0] + nx * w, pts[i][1] + ny * w))
        right.append((pts[i][0] - nx * w, pts[i][1] - ny * w))
    # round caps (sweep from one side to the other through the tube's end)
    def cap(c, w, a_start):
        return [(c[0] + w * math.cos(a_start - math.pi * k / 8), c[1] + w * math.sin(a_start - math.pi * k / 8))
                for k in range(1, 8)]
    e0, e1 = pts[0], pts[-1]
    aL1 = math.atan2(left[-1][1] - e1[1], left[-1][0] - e1[0])
    aR0 = math.atan2(right[0][1] - e0[1], right[0][0] - e0[0])
    return left + cap(e1, widths[-1] / 2 + extra, aL1) + right[::-1] + cap(e0, widths[0] / 2 + extra, aR0)


def mitten_pts(p, ang, hr, style='rest', thumb=1, t=0.0, seed=0.0):
    """Soft mitten hand: a rounded oval pushed forward from the wrist, with a
    small thumb nub. style: rest | cup | curl | grip | nub"""
    if style == 'nub':
        return ellipse_pts(p[0], p[1], hr * 0.95, hr * 0.85, ang, seed=seed, t=t, amp=0.3, n=36), None
    L = {'rest': 1.25, 'cup': 1.15, 'curl': 1.05, 'grip': 0.95}.get(style, 1.2)
    Wd = {'rest': 0.95, 'cup': 1.05, 'curl': 1.12, 'grip': 1.0}.get(style, 1.0)
    cx, cy = p[0] + math.cos(ang) * hr * 0.55, p[1] + math.sin(ang) * hr * 0.55

    def sh(th, x, y):
        # flatter at the wrist end, rounder at the fingertips
        k = 1.0 if math.cos(th) > 0 else 0.86
        return x * k, y
    pts = ellipse_pts(cx, cy, hr * L, hr * Wd, ang, seed=seed, t=t, amp=0.4, n=48, shape=sh)
    tb = None
    if style in ('rest', 'cup', 'grip'):
        ta = ang + thumb * 1.25
        tb = (p[0] + math.cos(ang) * hr * 0.35 + math.cos(ta) * hr * 0.95,
              p[1] + math.sin(ang) * hr * 0.35 + math.sin(ta) * hr * 0.95, hr * 0.42)
    return pts, tb


def draw_arm(ctx, s, hand, bow, w, hr, fill=WHITE, t=0.0, mitten=0.0, hand_ang=None,
             style='rest', thumb=1, blend=0.35, taper=0.78, seed=0.0):
    """Arm + mitten drawn as ONE soft silhouette (as in the reference): the arm
    grows out of the body with no outline at the shoulder, tapers slightly, and
    flows into the mitten with no seam at the wrist."""
    p = hand
    dx, dy = p[0] - s[0], p[1] - s[1]
    d = max(math.hypot(dx, dy), 1e-3)
    nx, ny = -dy / d, dx / d
    m = ((s[0] + p[0]) / 2 + nx * bow * d, (s[1] + p[1]) / 2 + ny * bow * d)
    pts = quad_pts(s, m, p, 24)
    widths = [w * (1 - (1 - taper) * (i / (len(pts) - 1))) for i in range(len(pts))]
    if hand_ang is None:
        hand_ang = math.atan2(p[1] - pts[-4][1], p[0] - pts[-4][0])
    hp, tb = mitten_pts(p, hand_ang, hr, style, thumb, t, seed)
    body = _offset_poly(pts, widths)
    n = len(pts)
    L, R = [], []
    for q in range(n):
        a = pts[max(0, q - 1)]
        b = pts[min(n - 1, q + 1)]
        ddx, ddy = b[0] - a[0], b[1] - a[1]
        dd = math.hypot(ddx, ddy) or 1.0
        nnx, nny = -ddy / dd, ddx / dd
        L.append((pts[q][0] + nnx * widths[q] / 2, pts[q][1] + nny * widths[q] / 2))
        R.append((pts[q][0] - nnx * widths[q] / 2, pts[q][1] - nny * widths[q] / 2))

    def dil(ptsl, e):
        cx = sum(x for x, _ in ptsl) / len(ptsl)
        cy = sum(y for _, y in ptsl) / len(ptsl)
        out = []
        for x, y in ptsl:
            vx, vy = x - cx, y - cy
            r = math.hypot(vx, vy) or 1.0
            out.append((x + vx / r * e, y + vy / r * e))
        return out
    # shadow
    if STYLE['shadows']:
        ctx.set_source_rgb(*GRAY)
        for poly in (body[len(body) // 6:], hp):
            path(ctx, [(x + SH[0], y + SH[1]) for x, y in poly])
            ctx.fill()
    # arm body (white, same as torso) then open ink lines that fade out toward the shoulder
    ctx.set_source_rgb(*fill)
    path(ctx, body)
    ctx.fill()
    ctx.set_source_rgb(*INK)
    ctx.set_line_cap(cairo.LINE_CAP_ROUND)
    for edge in (L, R):
        for q in range(1, n):
            u = q / (n - 1)
            ramp = clamp((u - blend * 0.35) / 0.55)
            if ramp <= 0.02:
                continue
            ctx.set_line_width(LW * ramp ** 0.8)
            ctx.move_to(*edge[q - 1])
            ctx.line_to(*edge[q])
            ctx.stroke()
    # hand: closed soft mitten
    ctx.set_source_rgb(*INK)
    path(ctx, dil(hp, LW / 2))
    ctx.fill()
    if tb:
        ctx.arc(tb[0], tb[1], tb[2] + LW / 2, 0, 2 * math.pi)
        ctx.fill()
    ctx.set_source_rgb(*fill)
    if tb:
        ctx.arc(tb[0], tb[1], tb[2] - LW / 2, 0, 2 * math.pi)
        ctx.fill()
    path(ctx, hp)
    ctx.fill()
    # little finger-fold line on curled / cupped hands (reference detail)
    if style in ('curl', 'cup'):
        fa = hand_ang + thumb * 0.9
        c = (p[0] + math.cos(hand_ang) * hr * 0.75, p[1] + math.sin(hand_ang) * hr * 0.75)
        a0 = fa + math.pi * 0.55
        ctx.set_source_rgb(*INK)
        ctx.set_line_width(3.0)
        ctx.set_line_cap(cairo.LINE_CAP_ROUND)
        r = hr * 0.55
        ctx.arc(c[0] + math.cos(fa) * r * 0.2, c[1] + math.sin(fa) * r * 0.2, r, a0, a0 + 1.1)
        ctx.stroke()
    return p


def draw_character_back(ctx, C, G, t):
    """Box-side parts: torso, legs, far arm."""
    draw_torso(ctx, C, G, t)
    draw_legs(ctx, C, t)
    G['far_hand'] = draw_arm(ctx, G['sh_far'], C.get('far_hand', (768, 1414)),
                             C.get('far_bow', -0.05), 54, C.get('far_hr', 21), t=t,
                             style=C.get('far_style', 'nub'), thumb=-1, blend=0.55, taper=0.62,
                             hand_ang=C.get('far_hand_ang'), seed=3)


def draw_character_front(ctx, C, G, t):
    G['near_hand'] = draw_arm(ctx, G['sh_near'], C.get('near_hand', (585, 1285)),
                              C.get('near_bow', -0.12), 74, C.get('near_hr', 40), t=t,
                              hand_ang=C.get('near_hand_ang'), style=C.get('near_style', 'rest'),
                              thumb=C.get('near_thumb', 1), blend=0.30, taper=0.80, seed=5)
    draw_head(ctx, C, G, t)


# ----------------------------------------------------------------- cat
def draw_cat(ctx, K, t):
    if not K or K.get('alpha', 1.0) <= 0.001:
        return
    alpha = K.get('alpha', 1.0)
    STYLE['shadows'] = not K.get('ghost', False)
    if alpha < 0.999:
        ctx.push_group()
    if K.get('ghost'):
        g = cairo.RadialGradient(K['x'], K['y'] - 110, 10, K['x'], K['y'] - 110, 300)
        g.add_color_stop_rgba(0, 1, 0.97, 0.9, 0.35)
        g.add_color_stop_rgba(1, 1, 0.97, 0.9, 0.0)
        ctx.set_source(g)
        ctx.paint()
    ctx.save()
    ctx.translate(K['x'], K['y'])
    s = K.get('scale', 1.0)
    f = K.get('face', 1)
    ctx.scale(f * s, s)
    curl = K.get('curl', 0.0)
    lie = K.get('lie', 0.0)
    cr = K.get('crouch', 0.0)
    st = K.get('stretch', 0.0)
    jp = K.get('jump', 0.0)
    dg = K.get('dangle', 0.0)
    gait = K.get('gait', 0.0)
    ph = K.get('phase', 0.0)
    br = math.sin(K.get('breath', t * 2.6)) * K.get('breath_amp', 1.0)
    rx = 126 * (1 + 0.16 * st) * (1 + 0.14 * lie - 0.10 * curl) * (1 + 0.05 * cr)
    ry = 88 * (1 - 0.10 * st) * (1 + 0.30 * lie + 0.25 * curl) * (1 - 0.10 * cr) * (1 + 0.025 * br)
    legL = 36 * (1 - clamp(max(lie, curl) / 0.45)) * (1 - 0.75 * cr) * (1 - 0.3 * st) + 26 * dg
    bob = K.get('bob', 0.0)
    cx = 0.0
    cy = -(legL + ry - 8) - bob
    # pivot rotation (rear-up / jump pitch) around rear feet
    r = K.get('rot', 0.0)
    pv = (-rx * 0.55, 0)
    ctx.translate(*pv)
    ctx.rotate(-r)
    ctx.translate(-pv[0], -pv[1])

    hip_y = cy + ry * 0.55
    legs = {  # name: (hip x, phase offset, near?)
        'ff': (rx * 0.55, math.pi, False), 'fb': (-rx * 0.42, 0.0, False),
        'nf': (rx * 0.38, 0.0, True), 'nb': (-rx * 0.60, math.pi, True)}

    def foot(name):
        hx, off, near = legs[name]
        front = name[1] == 'f'
        fx = hx + gait * 22 * math.sin(ph + off)
        lift = gait * 16 * max(0.0, math.cos(ph + off))
        fy = -lift
        if jp > 0:
            jx, jy = ((rx * 0.95 + 26, cy + ry * 0.25) if front else (-rx * 0.95 - 20, cy + ry * 0.6))
            fx, fy = lerp(fx, jx, jp), lerp(fy, jy, jp)
        if st > 0 and front:
            fx, fy = lerp(fx, rx * 1.05 + 40, st), lerp(fy, -4, st)
        kn = K.get('knead', 0.0)
        if kn > 0 and front:
            fy -= kn * 12 * max(0.0, math.sin(K.get('knead_phase', t * 9) + (0 if near else math.pi)))
        if dg > 0:
            fx, fy = lerp(fx, hx * 0.9, dg), lerp(fy, hip_y + legL, dg)
        return fx, fy, front, near

    def draw_leg(name, fill):
        fx, fy, front, near = foot(name)
        hx = legs[name][0]
        if legL < 4 and jp < 0.05 and dg < 0.05:
            return
        # short soft stub; the rounded end is the paw (top hidden under the body)
        tube(ctx, [(hx, hip_y - 30), (fx + 2, fy - 21)], 42, fill=fill, shadow=near)
        if near:
            line(ctx, [(fx - 3, fy - 4), (fx - 3, fy - 11)], lw=2.6)
            line(ctx, [(fx + 7, fy - 4), (fx + 7, fy - 11)], lw=2.6)

    # tail
    tw = K.get('tail_wrap', curl)
    tu = K.get('tail_up', 1.0)
    sway = K.get('tail_sway', 0.25)
    tph = K.get('tail_phase', t * 2.4)
    base = (cx - rx * 0.88, cy + ry * 0.05 - 10 * tw)
    tp = [base]
    ang_up = [math.pi + 0.55 + 0.17 * i for i in range(10)]
    ang_low = [math.pi - 0.35 + 0.05 * i for i in range(10)]
    ang_wrap = [math.pi * 0.62 - 0.30 * i for i in range(10)]
    seg_l = 15.0 * (1 + 0.1 * tw)
    p = base
    for i in range(10):
        a = lerp(lerp(ang_low[i], ang_up[i], tu), ang_wrap[i], tw)
        a += sway * (i / 9) * math.sin(tph - 0.55 * i)
        p = (p[0] + seg_l * math.cos(a), p[1] + seg_l * math.sin(a))
        tp.append(p)
    if tw < 0.5:
        tube(ctx, tp, 34, shadow=True)

    draw_leg('ff', FARW)
    draw_leg('fb', FARW)

    draw_leg('nf', WHITE)
    draw_leg('nb', WHITE)
    body = ellipse_pts(cx, cy, rx, ry, 0.0, seed=7, t=t, amp=0.9)
    shape(ctx, body)
    # haunch line (reference: a curved hip/leg shape on the rear)
    if lie + curl > 0.05:
        hk = clamp(lie + curl)
        # folded hind leg: an open arc on the rear of the body
        ctx.save()
        path(ctx, body)
        ctx.clip()
        ctx.set_source_rgba(*INK, hk)
        ctx.set_line_width(3.4)
        ctx.save()
        ctx.translate(cx - rx * 0.42, cy + ry * 0.05)
        ctx.scale(rx * 0.34, ry * 0.40)
        ctx.arc(0, 0, 1, math.pi * 1.05, math.pi * 1.95)
        ctx.restore()
        ctx.stroke()
        ctx.restore()
        # little back paw curl
        bx, by = cx - rx * 0.62, cy + ry * 0.62
        ctx.set_source_rgba(*INK, hk)
        ctx.set_line_width(3.4)
        ctx.arc(bx, by, 14, math.pi * 0.9, math.pi * 2.1)
        ctx.stroke()


    if jp > 0.25 or dg > 0.25 or K.get('rot', 0.0) > 0.3:
        draw_leg('nf', WHITE)       # reaching paws stay visible in the air
        draw_leg('nb', WHITE)
    if tw >= 0.5:
        tube(ctx, tp, 32, shadow=True)

    # head
    hxs, hys = rx * 0.92, -ry * 0.74
    hxl, hyl = rx * 1.08, -ry * 0.25     # lying (reference pose)
    hxc, hyc = rx * 0.82, ry * 0.05      # curled asleep
    hxt, hyt = rx * 1.05, -ry * 0.25     # stretch
    hx = lerp(lerp(lerp(hxs, hxl, lie), hxc, curl), hxt, st) + 10 * cr + K.get('head_dx', 0.0)
    hy = lerp(lerp(lerp(hys, hyl, lie), hyc, curl), hyt, st) + 16 * cr + K.get('head_dy', 0.0)
    hx += cx
    hy += cy
    hr = 92.0
    ha = -K.get('head_tilt', 0.0) + 0.18 * curl
    ear_tw = K.get('ear', 0.0)
    ear_dn = K.get('ear_down', 0.0)
    ctx.save()
    ctx.translate(hx, hy)
    ctx.rotate(ha)

    def ear(ang, flick, far):
        bx, by = (hr * 0.98) * math.cos(ang), (hr * 0.92) * math.sin(ang)
        out = ang + flick
        tipd = 44 - 10 * ear_dn
        tip = (bx + tipd * math.cos(out - 0.12 + 0.5 * ear_dn * (1 if ang > -math.pi / 2 else -1)),
               by + tipd * math.sin(out - 0.12 + 0.5 * ear_dn * (1 if ang > -math.pi / 2 else -1)))
        l = (bx + 30 * math.cos(ang - 1.25), by + 30 * math.sin(ang - 1.25))
        r_ = (bx + 30 * math.cos(ang + 1.25), by + 30 * math.sin(ang + 1.25))
        pts = quad_pts(l, (tip[0] * 0.9 + l[0] * 0.1, tip[1] * 0.9 + l[1] * 0.1), tip, 6)[:-1] + \
            [tip] + quad_pts(tip, (tip[0] * 0.9 + r_[0] * 0.1, tip[1] * 0.9 + r_[1] * 0.1), r_, 6)[1:]
        shape(ctx, pts + [(bx * 0.8, by * 0.8)], shadow=not far)
        # inner ear stroke
        m = ((l[0] + r_[0]) / 2, (l[1] + r_[1]) / 2)
        line(ctx, [(m[0] * 0.95 + tip[0] * 0.05, m[1] * 0.95 + tip[1] * 0.05),
                   (tip[0] * 0.7 + m[0] * 0.3, tip[1] * 0.7 + m[1] * 0.3)], lw=3.0)
    ear(-2.35, -0.0 - 0.25 * ear_tw, True)
    ear(-0.80, 0.30 * ear_tw, False)
    hpts = ellipse_pts(0, 0, hr * 1.06, hr * 0.94, 0, seed=9, t=t, amp=0.6, n=64)
    shape(ctx, hpts)
    # face (3/4 toward viewer)
    eyes = K.get('eyes', 'open')
    bl = clamp(K.get('blink', 0.0))
    for ex in (-8.0, 34.0):
        ey = 8.0
        if eyes == 'open' and bl < 0.8:
            ctx.save()
            ctx.translate(ex, ey)
            ctx.scale(1, max(0.1, 1 - bl))
            ctx.arc(0, 0, 7.5, 0, 2 * math.pi)
            ctx.set_source_rgb(*INK)
            ctx.fill()
            ctx.arc(-2.2, -2.6, 2.3, 0, 2 * math.pi)
            ctx.set_source_rgb(1, 1, 1)
            ctx.fill()
            ctx.restore()
        elif eyes == 'happy' or (eyes == 'open' and bl >= 0.8):
            line(ctx, quad_pts((ex - 9, ey + 3), (ex, ey - 9), (ex + 9, ey + 3), 8), lw=3.4)
        else:  # closed / sleeping
            line(ctx, quad_pts((ex - 9, ey - 1), (ex, ey + 7), (ex + 9, ey - 1), 8), lw=3.4)
    # nose + w mouth
    mx, my = 14.0, 22.0
    ctx.arc(mx, my - 3, 2.6, 0, 2 * math.pi)
    ctx.set_source_rgb(*INK)
    ctx.fill()
    line(ctx, quad_pts((mx - 10, my + 2), (mx - 5, my + 9), (mx, my + 1), 6), lw=3.0)
    line(ctx, quad_pts((mx, my + 1), (mx + 5, my + 9), (mx + 10, my + 2), 6), lw=3.0)
    if K.get('bell', False):
        # thin collar + tiny bell
        line(ctx, quad_pts((-58, 58), (5, 86), (60, 52), 12), lw=3.4)
        draw_bell(ctx, 6, 92, s=1.05, ang=0.25 * math.sin(K.get('bell_swing', 0.0)))
    ctx.restore()

    # front paws over the lap (reference pose) with claw ticks
    if lie > 0.4 and curl < 0.6:
        pa = clamp((lie - 0.4) / 0.4) * (1 - clamp((curl - 0.3) / 0.3))
        for px in (rx * 0.62, rx * 1.18):
            py = cy + ry * 0.92
            ptsp = ellipse_pts(px, py, 24, 18, n=30, amp=0.3)
            if pa > 0.02:
                ctx.push_group()
                shape(ctx, ptsp, shadow=False)
                for k in (-1, 0, 1):
                    line(ctx, [(px + k * 9, py + 14), (px + k * 13, py + 26)], lw=2.6)
                ctx.pop_group_to_source()
                ctx.paint_with_alpha(pa)
    ctx.restore()
    # purr marks
    pu = K.get('purr', 0.0)
    if pu > 0.02:
        bx = K['x'] - f * 40
        by = K['y'] - 2 * ry - 40
        for i in range(2):
            jitter = math.sin(t * 22 + i * 2) * 3
            ctx.set_source_rgba(0.75, 0.75, 0.78, pu * 0.8)
            ctx.set_line_width(3.0)
            xo = bx + (i * 26 - 13) * f
            ctx.move_to(xo - 10, by + jitter + i * 10)
            ctx.curve_to(xo - 4, by - 8 + jitter + i * 10, xo + 4, by + 8 + jitter + i * 10,
                         xo + 10, by + jitter + i * 10)
            ctx.stroke()
    if alpha < 0.999:
        ctx.pop_group_to_source()
        ctx.paint_with_alpha(alpha)
    STYLE['shadows'] = True


def cat_head_world(K):
    """Approximate world position of the cat's head (for hands to touch)."""
    curl, lie, st, cr = K.get('curl', 0), K.get('lie', 0), K.get('stretch', 0), K.get('crouch', 0)
    rx = 126 * (1 + 0.16 * st) * (1 + 0.14 * lie - 0.10 * curl) * (1 + 0.05 * cr)
    ry = 88 * (1 - 0.10 * st) * (1 + 0.30 * lie + 0.25 * curl) * (1 - 0.10 * cr)
    legL = 36 * (1 - clamp(max(lie, curl) / 0.45)) * (1 - 0.75 * cr) * (1 - 0.3 * st)
    cy = -(legL + ry - 8)
    hx = lerp(lerp(lerp(rx * 0.92, rx * 1.08, lie), rx * 0.82, curl), rx * 1.05, st)
    hy = lerp(lerp(lerp(-ry * 0.74, -ry * 0.25, lie), ry * 0.05, curl), -ry * 0.25, st)
    f = K.get('face', 1)
    return (K['x'] + f * hx, K['y'] + cy + hy), (K['x'], K['y'] + cy), rx, ry


# ----------------------------------------------------------------- set
def draw_set(ctx, S, t):
    # black void with a soft pool of light around the characters
    ctx.set_source_rgb(0.012, 0.012, 0.016)
    ctx.paint()
    pr, pg, pb = S.get('pool', (0.10, 0.10, 0.11))
    g = cairo.RadialGradient(600, 1330, 40, 600, 1330, 900)
    g.add_color_stop_rgba(0, pr, pg, pb, 1)
    g.add_color_stop_rgba(0.55, pr * 0.45, pg * 0.45, pb * 0.45, 1)
    g.add_color_stop_rgba(1, 0, 0, 0, 0)
    ctx.set_source(g)
    ctx.paint()
    # window, far away in the dark (upper left) - carries time of day and seasons
    wa = S.get('win_a', 0.5)
    if wa > 0.01:
        draw_window(ctx, S, t, wa)
    # floor: faint line + contact shadows
    ctx.set_source_rgba(1, 1, 1, 0.05 * S.get('floor_a', 1.0))
    ctx.set_line_width(2.0)
    ctx.move_to(-600, FLOOR_Y + 2)
    ctx.line_to(1700, FLOOR_Y + 2)
    ctx.stroke()
    for (cx, cy, rx, ry, a) in [(700, FLOOR_Y + 4, 330, 26, 0.55)]:
        sg = cairo.RadialGradient(cx, cy, 5, cx, cy, rx)
        sg.add_color_stop_rgba(0, 0, 0, 0, a)
        sg.add_color_stop_rgba(1, 0, 0, 0, 0)
        ctx.save()
        ctx.translate(cx, cy)
        ctx.scale(1, ry / rx)
        ctx.translate(-cx, -cy)
        ctx.set_source(sg)
        ctx.arc(cx, cy, rx, 0, 2 * math.pi)
        ctx.fill()
        ctx.restore()
    # window light on the floor
    pa = S.get('patch_a', 0.0)
    if pa > 0.005:
        px = S.get('patch_x', 200)
        lr, lg, lb = S.get('light', (1, 1, 1))
        ctx.push_group()
        ctx.move_to(px - 120, FLOOR_Y - 10)
        ctx.line_to(px + 260, FLOOR_Y - 10)
        ctx.line_to(px + 420, FLOOR_Y + 160)
        ctx.line_to(px - 60, FLOOR_Y + 160)
        ctx.close_path()
        ctx.set_source_rgba(lr, lg, lb, pa)
        ctx.fill()
        ctx.pop_group_to_source()
        ctx.paint()


WIN = (60.0, 640.0, 330.0, 1010.0)


def draw_window(ctx, S, t, wa):
    x0, y0, x1, y1 = WIN
    sr, sg_, sb = S.get('sky', (0.5, 0.5, 0.55))
    ctx.push_group()
    # glow
    gl = cairo.RadialGradient((x0 + x1) / 2, (y0 + y1) / 2, 50, (x0 + x1) / 2, (y0 + y1) / 2, 420)
    gl.add_color_stop_rgba(0, sr, sg_, sb, 0.25)
    gl.add_color_stop_rgba(1, sr, sg_, sb, 0)
    ctx.set_source(gl)
    ctx.paint()
    ctx.rectangle(x0, y0, x1 - x0, y1 - y0)
    ctx.set_source_rgb(sr, sg_, sb)
    ctx.fill()
    # season particles
    ctx.save()
    ctx.rectangle(x0, y0, x1 - x0, y1 - y0)
    ctx.clip()
    season = S.get('season')
    if season == 'leaves':
        for i in range(9):
            sp = 0.18 + 0.05 * (i % 3)
            u = (t * sp + i * 0.137) % 1.0
            x = x0 + ((i * 97) % 260) + 50 * math.sin(t * 1.3 + i) - 40 * u
            y = y0 - 20 + u * (y1 - y0 + 40)
            ctx.save()
            ctx.translate(x, y)
            ctx.rotate(t * 2 + i)
            ctx.scale(1, 0.5)
            ctx.arc(0, 0, 9, 0, 2 * math.pi)
            ctx.set_source_rgba(0.55, 0.45, 0.35, 0.8)
            ctx.fill()
            ctx.restore()
    elif season == 'rain':
        ctx.set_source_rgba(0.85, 0.88, 0.95, 0.45)
        ctx.set_line_width(2)
        for i in range(40):
            u = (t * 1.6 + i * 0.0731) % 1.0
            x = x0 + (i * 53) % 280
            y = y0 - 40 + u * (y1 - y0 + 80)
            ctx.move_to(x, y)
            ctx.line_to(x - 6, y + 30)
        ctx.stroke()
    elif season == 'snow':
        for i in range(34):
            u = (t * (0.06 + 0.02 * (i % 4)) + i * 0.091) % 1.0
            x = x0 + (i * 71) % 270 + 12 * math.sin(t * 0.9 + i)
            y = y0 - 10 + u * (y1 - y0 + 20)
            ctx.arc(x, y, 3 + (i % 3), 0, 2 * math.pi)
            ctx.set_source_rgba(1, 1, 1, 0.85)
            ctx.fill()
    elif season == 'stars':
        for i in range(10):
            x = x0 + 20 + (i * 83) % 240
            y = y0 + 30 + (i * 57) % 300
            a = 0.4 + 0.4 * math.sin(t * 1.5 + i)
            ctx.arc(x, y, 2.2, 0, 2 * math.pi)
            ctx.set_source_rgba(1, 1, 1, a)
            ctx.fill()
    ctx.restore()
    # frame + mullions (hand-drawn style)
    fr = (0.30, 0.30, 0.32)
    ctx.set_source_rgb(*fr)
    ctx.set_line_width(9)
    ctx.rectangle(x0, y0, x1 - x0, y1 - y0)
    ctx.stroke()
    ctx.set_line_width(6)
    ctx.move_to((x0 + x1) / 2, y0)
    ctx.line_to((x0 + x1) / 2, y1)
    ctx.move_to(x0, (y0 + y1) / 2 - 20)
    ctx.line_to(x1, (y0 + y1) / 2 - 20)
    ctx.stroke()
    ctx.pop_group_to_source()
    ctx.paint_with_alpha(wa)


def draw_box(ctx, S, t):
    x0, y0, x1, y1 = BOX
    pts = rounded_rect_pts(x0, y0, x1, y1, 16)
    shape(ctx, pts)
    if S.get('bell') == 'box':
        draw_bell(ctx, BELL_BOX[0], BELL_BOX[1], s=1.25, ribbon=True,
                  ang=0.12 * math.sin(S.get('bell_wobble', 0.0)))

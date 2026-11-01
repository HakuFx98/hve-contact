"""Frame compositor: camera, draw order, grading, captions, film texture."""
import math
import random
import cairo
import numpy as np
import rig
from anim import clamp

W, H = 1080, 1920
FONT = "Inter Display Light"

_grain = None
_grain_arr = None


def grain_surface():
    global _grain, _grain_arr
    if _grain is None:
        rng = np.random.default_rng(7)
        g = rng.normal(0, 1, (H, W)).astype(np.float32)
        # soft paper fibres: blend fine grain with a blurred field
        lo = rng.normal(0, 1, (H // 24 + 2, W // 24 + 2)).astype(np.float32)
        lo = np.kron(lo, np.ones((24, 24), np.float32))[:H, :W]
        v = 0.75 * g + 0.6 * lo
        v = np.clip(128 + v * 22, 0, 255).astype(np.uint8)
        a = np.full((H, W), 255, np.uint8)
        arr = np.dstack([v, v, v, a]).copy()
        _grain = cairo.ImageSurface.create_for_data(memoryview(arr), cairo.FORMAT_ARGB32, W, H)
        _grain_arr = arr
    return _grain


def draw_world(ctx, st, t):
    cam = st['cam']
    cx, cy, z = cam
    ctx.save()
    ctx.translate(W / 2, H / 2)
    ctx.scale(z, z)
    ctx.translate(-cx, -cy)
    S = st['set']
    rig.draw_set(ctx, S, t)
    C = st['char']
    G = rig.char_geom(C)
    K = st.get('cat')
    # floor cat shadow
    if K and K.get('floor_shadow') and K.get('alpha', 1) > 0:
        h = max(0.0, rig.FLOOR_Y - K['y'])
        k = 1 / (1 + h / 160)
        ctx.save()
        ctx.translate(K['x'], rig.FLOOR_Y + 4)
        ctx.scale(1, 0.12)
        g = cairo.RadialGradient(0, 0, 4, 0, 0, 150 * k)
        g.add_color_stop_rgba(0, 0, 0, 0, 0.6 * k * K.get('alpha', 1))
        g.add_color_stop_rgba(1, 0, 0, 0, 0)
        ctx.set_source(g)
        ctx.arc(0, 0, 150, 0, 2 * math.pi)
        ctx.fill()
        ctx.restore()
    if st.get('no_char'):
        if K:
            rig.draw_cat(ctx, K, t)
        ctx.restore()
        return
    behind = K and K.get('layer') == 'floor_back'
    if behind:
        rig.draw_cat(ctx, K, t)
    rig.draw_box(ctx, S, t)
    rig.draw_character_back(ctx, C, G, t)
    if K and not behind and K.get('layer') != 'top':
        rig.draw_cat(ctx, K, t)
    M = st.get('memory')
    if M:
        rig.draw_cat(ctx, M, t)
    if S.get('bell') == 'lap':
        bx, by = S.get('bell_pos', (480, 1400))
        rig.draw_bell(ctx, bx, by, s=1.25, ribbon=True)
    rig.draw_character_front(ctx, C, G, t)
    if K and K.get('layer') == 'top':
        rig.draw_cat(ctx, K, t)
    if S.get('bell') == 'hand':
        hx, hy = G['far_hand']
        rig.draw_bell(ctx, hx - 6, hy + 22, s=1.25, ang=0.2 * math.sin(t * 6))
    for hz in st.get('hearts', []):
        x, y, s, a = hz
        if a > 0:
            ctx.push_group()
            rig.shape(ctx, rig.heart_pts(x, y, s), fill=rig.WHITE, lw=3.0, shadow=False)
            ctx.pop_group_to_source()
            ctx.paint_with_alpha(a)
    ctx.restore()


def grade(ctx, st, t):
    gr = st['grade']
    tr, tg, tb = gr.get('tint', (1, 1, 1))
    ctx.set_operator(cairo.OPERATOR_MULTIPLY)
    ctx.set_source_rgb(tr, tg, tb)
    ctx.paint()
    ctx.set_operator(cairo.OPERATOR_OVER)
    # warm lamp / memory glow
    gl = gr.get('glow', 0.0)
    if gl > 0.005:
        gx, gy = gr.get('glow_pos', (W / 2, H * 0.55))
        g = cairo.RadialGradient(gx, gy, 20, gx, gy, 900)
        r, g_, b = gr.get('glow_col', (1.0, 0.85, 0.6))
        g.add_color_stop_rgba(0, r, g_, b, 0.22 * gl)
        g.add_color_stop_rgba(1, r, g_, b, 0)
        ctx.set_operator(cairo.OPERATOR_SCREEN)
        ctx.set_source(g)
        ctx.paint()
        ctx.set_operator(cairo.OPERATOR_OVER)
    v = gr.get('vignette', 0.55)
    g = cairo.RadialGradient(W / 2, H * 0.5, H * 0.28, W / 2, H * 0.5, H * 0.72)
    g.add_color_stop_rgba(0, 0, 0, 0, 0)
    g.add_color_stop_rgba(1, 0, 0, 0, v)
    ctx.set_source(g)
    ctx.paint()


def caption(ctx, text, a, y=300, size=58, rise=0.0):
    if not text or a <= 0.003:
        return
    ctx.save()
    ctx.select_font_face(FONT, cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_NORMAL)
    ctx.set_font_size(size)
    ext = ctx.text_extents(text)
    x = (W - ext.x_advance) / 2
    yy = y + 12 * (1 - rise)
    ctx.move_to(x, yy)
    ctx.text_path(text)
    ctx.set_source_rgba(0, 0, 0, 0.6 * a)
    ctx.set_line_width(10)
    ctx.stroke_preserve()
    ctx.set_source_rgba(0.96, 0.96, 0.95, a)
    ctx.fill()
    ctx.restore()


def render_state(ctx, st, t):
    draw_world(ctx, st, t)
    grade(ctx, st, t)


def render_frame(layers, t, overlays):
    """layers: list of (state, weight). Returns BGRA bytes."""
    surf = cairo.ImageSurface(cairo.FORMAT_ARGB32, W, H)
    ctx = cairo.Context(surf)
    ctx.set_antialias(cairo.ANTIALIAS_BEST)
    first = True
    for st, w in layers:
        if w <= 0.001:
            continue
        if first:
            render_state(ctx, st, t)
            first = False
        else:
            ctx.push_group()
            render_state(ctx, st, t)
            ctx.pop_group_to_source()
            ctx.paint_with_alpha(w)
    # paper/film texture
    ctx.set_operator(cairo.OPERATOR_SOFT_LIGHT)
    ctx.set_source_surface(grain_surface(), 0, 0)
    ctx.paint_with_alpha(0.30)
    ctx.set_operator(cairo.OPERATOR_OVER)
    bloom = overlays.get('bloom', 0.0)
    if bloom > 0:
        ctx.set_source_rgba(1, 0.97, 0.92, bloom)
        ctx.paint()
    for (text, a, y, size, rise) in overlays.get('captions', []):
        caption(ctx, text, a, y, size, rise)
    blk = overlays.get('black', 0.0)
    if blk > 0:
        ctx.set_source_rgba(0, 0, 0, clamp(blk))
        ctx.paint()
    surf.flush()
    return surf

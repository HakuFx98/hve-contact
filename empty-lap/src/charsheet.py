"""Character model sheet for THE EMPTY LAP: model vs reference, expressions,
hand poses, cat poses, palette. Rendered with the same rigs as the film."""
import sys
import math
from PIL import Image, ImageDraw, ImageFont
import film
import rig
import scenes

BG = (14, 14, 17)
FONT = "/usr/share/fonts/opentype/inter/InterDisplay-Light.otf"
FONTB = "/usr/share/fonts/opentype/inter/InterDisplay-Medium.otf"


def font(sz, bold=False):
    try:
        return ImageFont.truetype(FONTB if bold else FONT, sz)
    except Exception:
        return ImageFont.load_default()


def shot(char=None, cat=None, cam=(560, 1260, 1.0), bell=None, bell_pos=None, crop=None, size=None, no_char=False):
    C = dict(yaw=-0.40, pitch=0.0, mouth=0.6, near_hand=scenes.REST_N, far_hand=scenes.REST_F, breath=0.0)
    C.update(char or {})
    S = dict(win_a=0.0, pool=(0.0, 0.0, 0.0), bell=bell)
    if bell_pos:
        S['bell_pos'] = bell_pos
    st = dict(cam=cam, set=S, char=C, cat=cat, grade=dict(tint=(1, 1, 1), vignette=0.0), no_char=no_char)
    s = film.render_frame([(st, 1.0)], 0.0, {})
    im = Image.frombuffer('RGBA', (film.W, film.H), bytes(s.get_data()), 'raw', 'BGRA', 0, 1).convert('RGB')
    if crop:
        im = im.crop(crop)
    if size:
        im = im.resize(size, Image.LANCZOS)
    return im


def cat_on_lap(**kw):
    K = dict(x=470, y=1452, face=1, lie=1.0, eyes='happy', tail_up=1, tail_sway=0.0, bell=True, breath=0.0)
    K.update(kw)
    return K


def cat_floor(**kw):
    K = dict(x=540, y=1690, face=1, lie=0.0, eyes='open', tail_up=1, tail_sway=0.0, bell=True, breath=0.0,
             floor_shadow=True)
    K.update(kw)
    return K


def main(out):
    Wd = 2400
    sheet = Image.new('RGB', (Wd, 6400), BG)
    d = ImageDraw.Draw(sheet)
    y = 50
    d.text((60, y), "THE EMPTY LAP  —  Character Model Sheet  ·  Ep. 001", font=font(64, True), fill=(240, 240, 240))
    y += 90
    d.text((60, y), "Matched to the supplied reference. Every pose below is rendered by the same rig used for the film.",
           font=font(34), fill=(170, 170, 175))
    y += 80

    def label(x, yy, txt, sz=30, col=(200, 200, 205)):
        d.text((x, yy), txt, font=font(sz), fill=col)

    def section(title):
        nonlocal y
        d.line([(60, y), (Wd - 60, y)], fill=(70, 70, 76), width=2)
        y += 20
        d.text((60, y), title, font=font(44, True), fill=(235, 235, 235))
        y += 75

    # --- A. model vs reference
    section("A · Model vs. reference (resting pose)")
    crop = (130, 380, 1050, 1430)
    a = shot(char=dict(near_hand=(552, 1270), near_style='curl', near_hand_ang=2.2, mouth=0.7),
             cat=cat_on_lap(), crop=crop, size=(690, 788))
    ref = Image.open('../reference/character_reference.jpg').convert('RGB').resize((1080, 1922))
    r2 = Image.new('RGB', (1080, 1920))
    r2.paste(ref, (-20, -300))
    b = r2.crop(crop).resize((690, 788))
    sheet.paste(a, (60, y))
    sheet.paste(b, (790, y))
    label(60, y + 795, "OUR MODEL")
    label(790, y + 795, "REFERENCE")
    # specs text
    sx = 1560
    specs = [
        ("Proportions", ["Head ≈ 1.0 × body height", "Head radius 224 · body 122×236", "Cat head ≈ 0.4 × his head"]),
        ("Line & shading", ["Ink #222226, 3.6 px (thin)", "No inner shading — flat white", "Gray rim #ADADB0, offset ↘",
                            "Head rim shows top + right"]),
        ("Face", ["Dot eyes, tiny highlight, low on face", "Blue drop under each eye", "Small 'u' smile"]),
        ("Arms & hands", ["Soft arms, no outline at shoulder", "Arm flows into mitten, no wrist line",
                          "Near mitten big · far hand tiny nub"]),
        ("World", ["Black void · white box stool", "Only light & a far window change"]),
    ]
    yy = y
    for head, lines in specs:
        d.text((sx, yy), head, font=font(32, True), fill=(235, 235, 235))
        yy += 44
        for ln in lines:
            d.text((sx + 10, yy), "· " + ln, font=font(27), fill=(175, 175, 180))
            yy += 38
        yy += 16
    # palette
    pal = [((251, 251, 250), "white"), ((174, 174, 176), "rim gray"), ((34, 34, 38), "ink"),
           ((92, 158, 242), "tear blue"), ((3, 3, 4), "void")]
    for i, (c, n) in enumerate(pal):
        px = sx + i * 150
        d.rectangle([px, yy, px + 110, yy + 60], fill=c, outline=(120, 120, 120))
        d.text((px, yy + 66), n, font=font(24), fill=(170, 170, 175))
    y += 980

    # --- B. expressions
    section("B · Expressions")
    exprs = [
        ("content", dict(mouth=0.7)),
        ("joy", dict(mouth=1.0, blink=1.0, closed_style='happy')),
        ("hopeful", dict(yaw=-0.52, pitch=-0.05, mouth=0.42, eye_scale=1.12, look=(-1, 0))),
        ("worried / gasp", dict(yaw=-0.48, pitch=0.3, mouth_open=0.7, eye_scale=1.28, look=(-1, 1))),
        ("sad", dict(pitch=0.32, mouth=-0.38, head_tilt=-0.05, look=(0, 1))),
        ("memory (eyes shut)", dict(pitch=0.3, mouth=0.22, blink=1.0)),
        ("crying", dict(pitch=0.28, mouth=-0.45, tear=0.62, look=(0, 1))),
        ("acceptance", dict(pitch=0.32, mouth=0.18, blink=1.0, tear=1.0, head_tilt=-0.08)),
    ]
    cw = (Wd - 120) // 4
    for i, (n, c) in enumerate(exprs):
        cx, cy = 60 + (i % 4) * cw, y + (i // 4) * 560
        im = shot(char=c, cam=(560, 960, 1.6), crop=(120, 700, 960, 1460), size=(cw - 30, 500))
        sheet.paste(im, (cx, cy))
        label(cx, cy + 505, n)
    y += 1140

    # --- C. hand poses
    section("C · Arm & hand poses")
    hc = (90, 560, 1060, 1600)
    poses = [
        ("rest on lap", dict(near_hand=(470, 1392), near_hand_ang=2.75, near_style='rest'), None, None),
        ("pat the empty spot", dict(near_hand=(468, 1358), near_hand_ang=2.4, near_style='rest', pitch=0.2,
                                    yaw=-0.55, mouth=0.2), None, None),
        ("make room", dict(near_hand=(372, 1236), near_hand_ang=-2.5, near_style='rest', near_bow=-0.18,
                           yaw=-0.62, mouth=0.42, eye_scale=1.08), None, None),
        ("stroke her back", dict(near_hand=(520, 1282), near_hand_ang=2.5, near_style='curl', mouth=0.9),
         cat_on_lap(), None),
        ("scratch her head", dict(near_hand=(586, 1232), near_hand_ang=0.9, near_style='curl', near_hr=34,
                                  mouth=1.0, yaw=-0.3, pitch=0.12), cat_on_lap(head_tilt=0.22, lie=0.6), None),
        ("lift her up", dict(lean=-0.30, crouch=0.65, near_hand=(352, 1500), near_hand_ang=1.2,
                             near_style='cup', far_hand=(318, 1570), far_style='cup', far_hr=26,
                             far_hand_ang=0.4, yaw=-0.62, pitch=0.3, mouth=-0.1),
         cat_floor(x=276, rot=0.85, jump=0.5, ear_down=0.5, head_tilt=0.1), None),
        ("pick up the bell", dict(lean=0.10, yaw=0.45, pitch=0.3, far_hand=(852, 1462), far_style='grip',
                                  far_hr=24, far_hand_ang=1.4, mouth=-0.35, tear=1.0), None, 'hand'),
        ("holding the empty space (ending)", dict(near_hand=(552, 1272), near_hand_ang=2.2, near_style='curl',
                                     far_hand=(640, 1418), far_hand_ang=3.0, far_style='cup', far_hr=24,
                                     far_bow=-0.25, blink=1.0, pitch=0.30, mouth=0.18, head_tilt=-0.06,
                                     tear=1.0), None, 'lap'),
    ]
    for i, (n, c, k, bell) in enumerate(poses):
        cx, cy = 60 + (i % 4) * cw, y + (i // 4) * 640
        im = shot(char=c, cat=k, bell=bell, bell_pos=(482, 1392), crop=hc, size=(cw - 30, 580))
        sheet.paste(im, (cx, cy))
        label(cx, cy + 585, n)
    y += 1290

    # --- D. cat
    section("D · Her poses & faces")
    cc = (240, 1330, 840, 1760)
    cats = [
        ("walk", cat_floor(gait=0.55, phase=1.0)),
        ("run", cat_floor(gait=1.0, phase=0.6, bob=5, tail_sway=0.3)),
        ("wiggle (about to jump)", cat_floor(crouch=0.85, head_tilt=0.12)),
        ("jump", cat_floor(y=1600, jump=1.0, rot=0.2)),
        ("lying — reference pose", cat_on_lap(x=520, y=1690)),
        ("stretch", cat_on_lap(x=500, y=1690, lie=0.3, stretch=1.0, eyes='closed')),
        ("curled asleep", cat_on_lap(x=520, y=1690, lie=0.2, curl=1.0, eyes='closed')),
        ("rear up (too weak to jump)", cat_floor(x=520, rot=0.9, jump=0.5, ear_down=0.5)),
    ]
    for i, (n, k) in enumerate(cats):
        cx, cy = 60 + (i % 4) * cw, y + (i // 4) * 470
        im = shot(char=dict(), cat=k, cam=(540, 1540, 1.5), crop=(90, 560, 990, 1230), size=(cw - 30, 410), no_char=True)
        # remove the character: render cat alone by hiding him off-camera is simpler -> crop shows cat region
        sheet.paste(im, (cx, cy))
        label(cx, cy + 415, n)
    y += 960
    sheet = sheet.crop((0, 0, Wd, y + 20))
    sheet.save(out)


if __name__ == '__main__':
    main(sys.argv[1])

"""Render THE EMPTY LAP to frames / MP4.

usage:
  python3 render.py sheet out.png t1 t2 ...    # contact sheet of chosen times
  python3 render.py video out_silent.mp4        # full 60 s render (H.264, 30 fps)
"""
import sys
import subprocess
from multiprocessing import Pool
import film
import scenes


def render_t(t):
    layers, ov = scenes.frame(t)
    surf = film.render_frame(layers, t, ov)
    return bytes(surf.get_data())


def sheet(out, times):
    from PIL import Image
    thumbs = []
    for t in times:
        layers, ov = scenes.frame(t)
        s = film.render_frame(layers, t, ov)
        im = Image.frombuffer('RGBA', (film.W, film.H), bytes(s.get_data()), 'raw', 'BGRA', 0, 1).convert('RGB')
        thumbs.append(im.resize((270, 480)))
    cols = min(6, len(thumbs))
    rows = (len(thumbs) + cols - 1) // cols
    sh = Image.new('RGB', (cols * 274, rows * 500), (40, 40, 40))
    from PIL import ImageDraw
    d = ImageDraw.Draw(sh)
    for i, (im, t) in enumerate(zip(thumbs, times)):
        x, y = (i % cols) * 274 + 2, (i // cols) * 500 + 2
        sh.paste(im, (x, y))
        d.text((x + 4, y + 482), f"t={t:.2f}", fill=(255, 255, 0))
    sh.save(out)


def video(out):
    n = int(round(scenes.DURATION * scenes.FPS))
    cmd = ['ffmpeg', '-y', '-loglevel', 'error', '-f', 'rawvideo', '-pix_fmt', 'bgra',
           '-s', f'{film.W}x{film.H}', '-r', str(scenes.FPS), '-i', '-',
           '-c:v', 'libx264', '-preset', 'slow', '-crf', '17', '-tune', 'animation',
           '-pix_fmt', 'yuv420p', '-r', str(scenes.FPS), out]
    p = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    times = [i / scenes.FPS for i in range(n)]
    with Pool(4) as pool:
        for i, data in enumerate(pool.imap(render_t, times, chunksize=4)):
            p.stdin.write(data)
            if i % 150 == 0:
                print(f"frame {i}/{n}", flush=True)
    p.stdin.close()
    p.wait()


if __name__ == '__main__':
    if sys.argv[1] == 'sheet':
        sheet(sys.argv[2], [float(x) for x in sys.argv[3:]])
    else:
        video(sys.argv[2])

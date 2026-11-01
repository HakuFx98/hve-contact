"""Vertical thumbnail (1080x1920): the empty lap, the bell, the memory, the tear."""
import sys
import cairo
import film
import scenes


def main(out):
    t = 51.0
    st = scenes.s6(t)
    C = st['char']
    C.update(blink=0.0, tear=0.55, mouth=-0.4, yaw=-0.42, pitch=0.30, near_hand=(500, 1380))
    M = scenes.cat_base(t)
    M.update(lie=1.0, curl=0.35, eyes='closed', ghost=True, alpha=0.74, purr=0.0, bell=False)
    st['memory'] = M
    st['set']['bell'] = 'lap'
    st['set']['bell_pos'] = (560, 1392)
    st['grade'] = dict(scenes.look(scenes.mix(scenes.PRESENT, scenes.MEMORY, 0.45))[1])
    st['cam'] = (575, 1098, 1.40)
    ov = {'captions': [("THE EMPTY LAP", 1.0, 250, 92, 1.0),
                       ("he still saved her a spot", 0.92, 340, 50, 1.0)]}
    s = film.render_frame([(st, 1.0)], t, ov)
    s.write_to_png(out)


if __name__ == '__main__':
    main(sys.argv[1])

# hve-contact

## Video tooling

### huashu-motion (`tools/huashu-motion`)

Motion graphics written as code: a film is one `index.html` (GSAP / Canvas / Three.js / SVG),
rendered to MP4, MOV (with alpha), WebM or GIF through headless Chrome + FFmpeg, with a generated
soundtrack. It has 12 templates, including kinetic type, finance chart, keynote UI, whiteboard,
3Blue1Brown-style and a talking-head package (name plates, keyword captions, transparent overlays for
CapCut/Premiere). Upstream: https://github.com/alchaincyf/huashu-motion (MIT), pinned at v0.3.1.

Vendored as a git submodule; its agent skill is linked at `.claude/skills/huashu-motion`.

```bash
git submodule update --init
```

```bash
node tools/huashu-motion/cli/om.js doctor
```

```bash
node tools/huashu-motion/cli/om.js new my-film && cd my-film && node ../tools/huashu-motion/cli/om.js sound && node ../tools/huashu-motion/cli/om.js render
```

Requirements: Node 22+, Chrome/Chromium, FFmpeg.

Licensing notes: GSAP is under its own "no charge" license and the bundled fonts are under SIL OFL 1.1
(see `tools/huashu-motion/THIRD_PARTY.md`). The "bean Huashu" cartoon character (storytime template,
`runtime/clip/lib/toon.js`) is **not** MIT. Don't use it in our published videos.

Known limitation on Linux/headless: embedding a `<video>` clip that has no `data-duration`
can time out during render (upstream test 107). Set `data-duration` on embedded footage.

### rossark-motion-skill (`tools/rossark-motion-skill`)

A method for making drawn things feel alive (characters, plants, icons, scenes): one clock,
real pivots, follow-through, idle life, `flow()` through key poses instead of stop-and-go
tweens, and blinks long enough not to flicker. Upstream: https://github.com/rossark0/rossark-motion-skill
(MIT). Its skill is linked at `.claude/skills/rossark-motion-skill`.

Its engine targets React Native and SwiftUI, and its demo renderer needs macOS. For our web
films we use **`lib/web-motion/motion.js`**, a browser port of the same math (`track`, `flow`,
`seg`, `wave`, `loop`, `bell`, `seeded` and the curves). It drops straight into huashu-motion:

```js
OM.clock(tl, (s) => draw(s * 1000), durationSeconds);   // draw() reads Motion.flow(t, keys) etc.
```

```bash
node --test lib/web-motion/motion.test.cjs
```

Its video tools work on Linux too, for checking timing frame by frame:

```bash
bash tools/rossark-motion-skill/tools/sheet.sh video.mp4 START DUR W:H:X:Y [PER_ROW] [FPS] [OUT]
```

## Demos

- `demos/alive-mascot`: an original mascot built with both skills (breathing, gliding gaze with
  the head a beat behind, blinks, a wave, a hop with squash and a trailing antenna), with
  music and effects. Render it:

```bash
cd demos/alive-mascot && node ../../tools/huashu-motion/cli/om.js sound && node ../../tools/huashu-motion/cli/om.js render
```

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

### take-one (`tools/take-one`)

A "one line → finished short film" studio pipeline (strategist, writer, storyboard, composer,
editor, and a fresh reviewer that scores each cut and sends it back under the bar), rendered from
canvas code with headless Chrome + FFmpeg. Upstream: https://github.com/talsiach/take-one (MIT;
a few music/gate files are Apache-2.0; the Take One name and logo are not licensed). Its skill
is linked at `.claude/skills/take-one`.

What it adds beyond huashu-motion:
- **21 illustrated looks**, each with a written method (`references/styles/`): watercolor, ink wash,
  pixel art, paper cutout, crayon storybook, riso pop, pencil test, kinetic lyric, editorial HUD,
  dark premium, title sequence, and more.
- Methods for voice-over, captions, vertical cuts, music videos, and optional paid image/video/voice/
  music services. It asks before spending anything and always has a free code-only route.
- Checks: a render gate for pops, an edge audit for things cut off by the frame, a text audit, a face audit.

The two overlap (both are code-rendered film pipelines with music and QA). Rough rule: huashu-motion
for product/launch motion graphics and talking-head packaging; take-one for illustrated or story-led
films.

```bash
bash tools/take-one/scripts/doctor.sh
```

```bash
bash tools/take-one/scripts/new-canvas-project.sh my-film && cd my-film && node export.mjs 60 film.mp4
```

Linux notes (upstream is tested on macOS only):
- Scripts that live outside a film project (`assets/previews-src/snap.mjs`, the gate, the audits) need
  `playwright-core` resolvable. `NODE_PATH` does **not** work for these ES modules. Symlink a
  `node_modules` containing it next to the script, or set `PLAYWRIGHT_NODE_MODULES` where supported.
- This cloud environment blocks `cdn.jsdelivr.net`, so the 3D looks that import three.js from the CDN
  need a local copy (`npm install three@<version>` and point the import at it).
- `scripts/matte.swift` (type behind a person) is macOS-only.

## Demos

- `demos/alive-mascot`: an original mascot built with both skills (breathing, gliding gaze with
  the head a beat behind, blinks, a wave, a hop with squash and a trailing antenna), with
  music and effects. Render it:

```bash
cd demos/alive-mascot && node ../../tools/huashu-motion/cli/om.js sound && node ../../tools/huashu-motion/cli/om.js render
```

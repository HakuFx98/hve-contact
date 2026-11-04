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

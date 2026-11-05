# Handoff: 3D "What If" storytelling animation

Read this first. It sums up a previous session that ran in a cloud container
with no GPU. You are now on the owner's laptop, which has an **RTX 5060 laptop GPU**.

## Goal

Make **long-form (~7–11 min) narrated "What If" storytelling videos** for YouTube,
not Shorts. The style combines two reference channels into our own look:

- **Jeremy Bearimy** (`@jeremybearimytheory`, e.g. "What IF You Had Creative Mode in Real Life?")
- **IFinity** ("What If You Could Turn Invisible at Will?", youtu.be/jqXG42osQOc)

Keep our own story, character names and colours so the channel doesn't read as a copy.

## What the reference style looks like (from video analysis + screenshots)

**Characters**
- Big smooth matte head, pale lilac-white (`#fbf8ff`). No hair by default; caps are an optional accessory.
- **Thick dark outlines** (`#1d1430`) around every part. This is the most important part of the look.
- Faces drawn as **2D lines** projected onto the head:
  - smug: half-lidded eyes and one raised brow
  - happy: `^ ^` arcs and an open smile
  - shock: big oval eyes and an O mouth
  - also: dizzy spirals, flat neutral
- Hoodie with a hood collar, two white drawstrings and a front pocket.
- Stick-thin white neck and legs, ball hands, small rounded shoes.
- Head-to-body ratio about 1 : 2.5.

**Look**
- Dusk palette: sky gradient purple `#5d4f9e` → lilac → peach/pink `#f0a9b4`.
- Purple city with warm lit windows (`#ffd28a`).
- Warm sunset key light, a **back rim light** for the glowing edge, and a soft lilac front fill.
- Atmosphere: fog, floating dust, bloom, and **strong depth-of-field blur** behind characters.

**Pacing and camera**
- Average shot length is about **2–3 s**.
- Moves: slow push-ins, low-angle hero shots, slow orbits, snap zooms with a white flash on key beats.
- Pose-to-pose motion with short holds.

**On-screen graphics**
- Word-by-word captions with the current word highlighted.
- Game-style ability pills in the top right: dark `#1d1528` pill, gold `#f5ce62` letter-spaced text, icon.
- IFinity-style **"RULE N"** cards on frosted glass.

**Story structure**
- Second-person narration ("You…").
- Hook in an everyday setting, then the power appears.
- About 5–6 "rules" or consequences, often with real science or psychology.
- An emotional turn near the end (isolation, cost), then a resolution with a friend.
- Ends with a question to viewers ("What would you do?").

## Tech stack

- **Remotion 4.0.540** (videos written in React) plus **three.js 0.169** via `@remotion/three`.
- 3D libraries: `@react-three/fiber` 8, `drei` 9, `@react-three/postprocessing` 2.
- Output is 1280×720 at 30 fps. Switch to 1920×1080 for real episodes.

## Files (`animation-sample/src/`)

| File | What it is |
|---|---|
| `Episode.tsx` | **Current main work.** "What If You Could Pause Time?" opening: 4 shots, about 11 s. Holds the `SHOTS` list (one narration line per shot), `Stage` (lights, set, post-processing), captions, `Abilities` pills, `RuleCard`, and the snap flash. |
| `Toon.tsx` | **Current character.** Outlined hoodie toon. The outline is an inverted hull: a custom `ShaderMaterial` pushes back faces out along normals; drei `<Outlines>` did not render. Faces are canvas textures applied with drei `<Decal>`. It also has poses (`idle`, `cheer`, `fists`, `wave`) and the **walk cycle**: set `walk = distanceTravelled / STRIDE` and `walkAmp` (0–1) so feet don't slide. |
| `City.tsx` | Rooftop-at-dusk set: gradient `Sky`, `Building` with lit-window textures (seeded, so every frame draws the same), water tower, parapet, skyline, `Dust` particles. Use the `rng()` helper for randomness, never `Math.random()`. |
| `Story3D.tsx`, `Character3D.tsx` | Older 3D hallway test with a skin-tone character. Superseded; kept for reference. |
| `WhatIf.tsx`, `Character.tsx` | Oldest version: 2D SVG. Superseded. |
| `Root.tsx` | Registers the compositions `Episode`, `Story3D` and `WhatIf`. |

Characters so far:
- **Kai**: the protagonist, the "you" of the narration. Mint hoodie `#3ccf9b`.
- **Juni**: Kai's friend. Pink-red hoodie `#e0607e` and a dark cap.

## How to run on this PC

```bash
cd animation-sample
```
```bash
npm install
```
```bash
npx remotion studio
```
```bash
npx remotion render Episode out/episode.mp4 --gl=angle
```

- `--gl=angle` uses the GPU on Windows. If renders are slow, Windows may be using the built-in graphics instead of the RTX. Set the browser to "High performance" in Windows Settings → System → Display → Graphics.
- In the cloud the only option that worked was `--gl=swangle` with `--browser-executable=/opt/pw-browsers/chromium`. **Don't use those on this PC.**
- Cloud speed with no GPU was about 6 min for 11 s (roughly 30× real time). Measure the GPU speed and report it to the owner.

## Known issues and polish to-dos

- `npx tsc` reports missing JSX types for three.js tags (`group`, `mesh`…). This is only a types problem and doesn't affect rendering. Fix it by adding `import '@react-three/fiber'` type augmentation or `"types"` to the tsconfig.
- Motion is still basic. Needed next:
  - squash and stretch on jumps
  - anticipation before moves
  - head turns and look-ats
  - a run cycle
  - a hand-snap pose
- No audio yet. Needs narration (AI voice), music and sound effects (pops, whooshes, chimes), with shots timed to the narration.
- Only one set exists (the rooftop). Likely needed: bedroom, classroom or hallway, street, park, interior with warm lamps.
- Renders for review go in `out/`. Don't commit big batches of test PNGs; `out/*.png` is in `.gitignore`.

## Suggested next steps (ask the owner which first)

1. Write a full episode script and shot list, about 150–200 shots for 8–10 min, in the structure above.
2. Add a voiceover, and drive shot lengths and captions from the audio timing.
3. Improve the animation (see the to-dos above) and build more sets.
4. Render the full episode at 1080p on the GPU.

## Git

Branch: `claude/confident-bell-n9qltx` on `HakuFx98/hve-contact`. Commit and push work there.

# THE EMPTY LAP — Animated Emotional Short · Episode 001

A 60-second, vertical (1080×1920, 30 fps) 2D animated short with no dialogue,
built for YouTube Shorts, TikTok and Reels.

| Deliverable | File |
|---|---|
| Finished film (H.264 High, 30 fps, AAC 48 kHz stereo) | `output/the_empty_lap_ep001.mp4` |
| Vertical thumbnail 1080×1920 | `output/the_empty_lap_ep001_thumbnail.png` |
| Title / description / hashtags | `output/youtube_metadata.md` |
| QA contact sheets + audio level map | `qa/` |
| Character reference (as supplied) | `reference/character_reference.jpg` |
| Editable project (all source) | `src/` and `build.sh` |

## Production approach

Everything is **procedural vector animation in code** (Python + cairo), with a
**fully synthesized original score and sound design** (numpy), assembled with
ffmpeg. The characters are rigs rather than drawings or generated video, so:

- the character and cat are **exactly on-model in every frame**, with no AI
  morphing, flicker or anatomy drift;
- every frame has real animation (breathing, blinking, gait cycles, jump arcs,
  squash and stretch, overlapping tail motion, IK-free rubber-hose arms, head
  turns rendered on a sphere, a tear that forms and runs);
- any shot, timing or expression can be edited by changing a keyframe and
  re-rendering (`./build.sh`).

### Reference analysis → consistency rules (`src/rig.py`)
Measured from `reference/character_reference.jpg` (world units = ref px × 1.78):

- **Black void background**, white characters, thin dark outline (3.6 px),
  flat **gray (174,174,174) offset drop-shadow** to the lower right; on the
  head the gray rim shows at the top and right, as in the reference.
- **Character:** head radius 224, centred above and in front of a tall bean
  body; 3/4 view facing left; black dot eyes with a small highlight sitting low
  on the face; tiny "u" smile; **small blue drop under each eye**; soft
  rubber-hose arms with mitten hands; fat sloping thigh, two hanging shins;
  sits on a **white box stool**.
- **Cat:** chubby white body, round head with pointed ears and inner-ear
  strokes, 3/4 face (dot eyes or ^ ^ happy arcs, "ω" mouth), curling tail,
  folded hind-leg line, front paws with claw ticks hanging over the lap. Its
  resting pose on the lap reproduces the reference image.
- Story additions (not in the reference): a tiny collar bell, needed by the
  brief; a distant window, used only to show time of day and seasons.

### Storyboard as built (`src/scenes.py`)
| Time | Scene | What happens |
|---|---|---|
| 0.0–4.2 | 1 Hook | Present day, cool light, clock ticking. He pats his empty lap. A faint bell jingles; he looks up, hopeful, toward where she used to come from, then back down. Caption: *"He still saved her a spot."* |
| 4.2–13.0 | 2 Happy days | Warm flashback (memory flash). She runs in from the left (bell jingling), wiggles, jumps, and he makes room and catches her. Head scratches, ear flick, stretch, then she settles into **the reference pose**. Purring, a slow blink, little hearts. Piano begins. |
| 13.0–23.0 | 3 Routine | Montage across seasons in the window. **Autumn:** she jumps up, he makes room, she kneads. **Rain:** a slow-blink exchange ("I love you" in cat), then a head-butt into his hand. **Snowy night, lamp glow:** both dozing, breathing together. |
| 23.0–34.0 | 4 Something changes | Dusk. She walks in slowly, tail low. The jump falls short and she tumbles back; he gasps. She tries again, weaker, ending up on her hind legs against his knee. He leans down, lifts her, and she curls up asleep while he strokes her head. The light fades to black; the music thins out. |
| 34.0–44.0 | 5 The empty space | Next evening. Out of habit he lifts his hand to make room and looks toward the empty floor. Nothing comes; only the clock. He turns, sees her collar and bell on the box, then looks down at his lap. |
| 44.0–53.0 | 6 The memory | He closes his eyes. A glowing memory of her curls into his lap and he strokes it; the theme returns. His eyes open, the memory fades, and a blue tear forms and rolls down his cheek. |
| 53.0–60.0 | 7 The ending | He picks up the bell, places it on his lap, and wraps his arms around the empty space with a sigh. The camera pulls back. Caption: *"Some spaces stay filled with love."* Fade to black; the piano resolves on F major. |

The ending fades to silence and black. The opening is another evening of the
same ritual, so the film loops naturally for rewatches.

### Sound (`src/audio.py`)
- **Score:** original piano piece in F major (75 bpm), synthesized from
  additive inharmonic partials with hammer noise and a convolution room
  reverb. It enters with the flashback, thins into D minor with an unresolved
  A-sus at the decline, falls almost silent in the empty-space scene, returns
  high and slow for the memory, and resolves at the end.
- **SFX:** paw steps triggered from the cat's gait phase; collar-bell jingles
  (inharmonic bell model); a purr made from a 25 Hz pulse-modulated low noise,
  with its level driven by the animation; breathing driven by the character's
  breath cycle; fabric rustle driven by hand speed; pats, landings and the
  fall; rain in the montage; and a clock heard **only in the present-day
  scenes**.
- Master: -16 LUFS integrated, -1 dBTP target, 48 kHz.

## Rebuild
```bash
pip install pycairo numpy pillow   # ffmpeg with libx264 required
./build.sh
```
Contact sheet of any moments: `cd src && python3 render.py sheet out.png 1.0 6.9 50.5`

## QA report (final render)
- File: 60.0 s · 1080×1920 · H.264 High · 30 fps (1800 frames) · AAC-LC 256 kb/s 48 kHz stereo · -16.6 LUFS integrated.
- Character match: compared side by side against the reference at the reference pose (see the S2 ending). Proportions, line weight, gray offset shadow, low dot eyes with blue drops, and the cat's ^ ^ face and claw ticks all match.
- Motion: every shot has character animation (no static holds; even "silence" keeps breathing, blinks and micro head moves). Checked on contact sheets at 2 s intervals: `qa/contact_sheet_every2s.png`.
- Sync: SFX are generated from the animation data (gait → steps, purr → purr, breath → breath, hand speed → fabric); scripted hits are keyed to the same times as the picture. Level map with story beats: `qa/audio_levels.png`.
- **Not done:** listening playback. This environment has no audio output, so the mix was checked by measurement (loudness, level-over-time against beats), not by ear. Please do a headphone pass before publishing.

# Title reveal: huashu-motion (GSAP) → pure CSS

- **Target**: the title reveal of huashu-motion's `blank` template, 0–2.4 s of its render, crop 130,280,1340,380.
- **Destination**: `index.html` here, plain CSS keyframes (no GSAP, no JS).
- **Fidelity**: pixel-faithful (same text, fonts and layout), so the comparison is fair.

Not a blind test: the reference's source was known. The comparison is what proves the match.

| Element | Property | Start | Duration | From → to | Easing |
|---|---|---|---|---|---|
| kicker | opacity, x | 0.15 s | 0.6 s | 0, −30 px → 1, 0 | power3.out |
| each title character | y (masked) | 0.25 s + 45 ms × i | 0.9 s | 110 % → 0 | expo.out |
| rule | scaleX from the left | 0.9 s | 0.9 s | 0 → 1 | expo.inOut |
| subtitle | opacity, y | 1.25 s | 0.7 s | 0, 20 px → **1**, 0 | power3.out |

GSAP curves are reproduced exactly with CSS `linear()` (60 samples each); `cubic-bezier` approximations
were too short in the tail.

## Rounds

| Round | Change | Pixels differing | Timing error | Verdict |
|---|---|---|---|---|
| 1 | cubic-bezier approximations, subtitle opacity .72 | 1.48 % | end −0.267 s | timing FAIL |
| 2 | exact GSAP curves via `linear()`, subtitle to opacity 1 | 1.02 % | end −0.233 s | timing FAIL* |
| 2, same pipeline | clone encoded to H.264 and re-extracted, like the reference | 1.05 % | start −0.033 s, end +0.033 s | **PASS** |
| 3 | all delays +1 frame | 1.06 % | unchanged (auto-align absorbed it) | reverted |

\* Not a real timing error. compare.ts ignores anti-aliased edge changes, so the underline's sub-pixel growth
counted in the compressed reference but not in the lossless clone frames. Captured the same way, the
two settle within a frame of each other.

Open: frames 19–23 (mid-rise) still differ by up to 4.6 %, under the 5 % limit. See `report.md`.

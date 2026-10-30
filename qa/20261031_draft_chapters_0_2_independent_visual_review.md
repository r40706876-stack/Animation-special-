# DRAFT chapters 0 and 2: independently inspected actual GitHub artifacts (2026-10-31 IST)

Source: GitHub Actions rough-cut run [41110464863](https://github.com/r40706876-stack/Animation-special-/actions/runs/41110464863), artifacts `jewel-v68-draft-chapter-0` (13011178018) and `jewel-v68-draft-chapter-2` (13012575772). Downloaded both ZIP artifacts and decoded the contained MP4 files independently with local ffmpeg, extracting frames at 0, 2, 4, 6 and 8 seconds for **each** chapter. This is actual rendered footage, not inferred from CI success.

## Verified technical properties

| Chapter | Duration | Video frames | FPS | Dimensions | Full ffmpeg decode |
|---|---:|---:|---:|---:|---|
| 0 | 10.000 s | 240 | 24 | 162 x 288 | PASS |
| 2 | 10.000 s | 240 | 24 | 162 x 288 | PASS |

These are individual low-resolution DRAFT chapters; no 140-second film is established by these checks. Neither standalone chapter contains the final synchronized Hindi narration. Narration and DRAFT watermark must be verified on the **assembled** film, not assumed from individual renders.

## Actual visual observations — DRAFT only, FINAL visual gate FAIL

- **Chapter 0, forest encounter:** The teal wasp approaches from the left, the cockroach remains to the right, and the leaf litter/plant silhouettes create some scene depth. However, both insects are very small within the vertical frame, especially at 0–4 seconds. The scene reads as a sparse clay-like stage rather than a layered realistic forest. A large amount of uninformative ground occupies the lower frame.
- **Chapter 2, cockroach escape:** The camera is closer and the wasp's approach is visible over the 0–8-second samples. But the cockroach barely communicates an urgent escape; there is no legible chase/flight interaction. At 8 seconds the wasp overlaps the cockroach, yet the movement lacks convincing wing/leg articulation in still sampling. Need to inspect the moving footage when refining action; stills alone do not prove gait quality.
- Both chapters exhibit simple low-detail materials, shallow environment layering and compositions that do not yet meet the requested cinematic realism. The current DRAFT resolution is intentionally low and cannot be used to approve final texture quality.

## Action / next steps

1. **Do not cancel or rerender successful chapters 0 and 2 now.** Finish and assemble all 14 DRAFT chapters first, preserving artifacts and V4.
2. After rough-cut assembly, assess pacing, story continuity, visible DRAFT watermark, 140.000s/3360 frames, audio presence and independent Hindi intelligibility/synchronization.
3. For final-quality pass, tighten chapter 0 framing (larger recognizable insects, stronger layered forest foreground/background, less empty soil). Make chapter 2's cockroach escape behavior and wasp pursuit legible in motion. Re-render only failed chapters using cache-aware workflow.
4. Final visual quality remains **FAIL / not approved**, irrespective of green CI or decode success.

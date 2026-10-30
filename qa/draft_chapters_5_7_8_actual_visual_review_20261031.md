# DRAFT chapters 5, 7, 8 — independently decoded visual QA (2026-10-31)

Source: GitHub Actions rough-cut run [41110464863](https://github.com/r40706876-stack/Animation-special-/actions/runs/41110464863), downloaded artifacts `jewel-v68-draft-chapter-5` (13019045929), `chapter-7` (13019128684), `chapter-8` (13019114408). Review based on actual MP4 frames at 0, 2, 4, 6 and 8 seconds, not on CI status or stills from the original 2-second specimen.

## Verified technical facts

| Chapter | Dimensions | FPS | Frames | Duration | Complete FFmpeg decode |
|---|---|---|---|---|---|
| 5 | 162x288 | 24 | 240 | 10.000 s | PASS |
| 7 | 162x288 | 24 | 240 | 10.000 s | PASS |
| 8 | 162x288 | 24 | 240 | 10.000 s | PASS |

Measured mean absolute grayscale frame changes across consecutive 0/2/4/6/8-second samples (pixel values out of 255): chapter 5 = 11.84/14.75/12.99/7.54; chapter 7 = 7.37/11.15/10.34/5.73; chapter 8 = 4.97/7.42/8.28/7.98. These demonstrate changing images, **not** scientifically correct or sufficiently legible actor animation.

## Actual visual findings and targeted final fixes

- **Chapter 5 — head ganglion sting: FAIL final visual QA.** In the sampled frames the wasp overlaps the roach but the needle/head contact point is not legible. The scene looks like two insects walking in parallel. Create a real readable close shot with wasp abdominal sting tip contacting the intended head region; avoid false anatomical claims. Use a visibly different contact pose and cutaway/schematic only if explicitly labeled.
- **Chapter 7 — changed walking behavior: FAIL final visual QA.** Roach and wasp drift laterally with no distinct before/after gait or behavior. Use clearly different roach locomotion with shot composition showing the entire legs and body; do not rely on a camera pan to simulate behavior.
- **Chapter 8 — antenna guidance: FAIL final visual QA.** Wasp and roach approach each other in a wide shot; antenna contact or guidance is not visible. Animate wasp holding or guiding the antenna in a dedicated closer shot, with physically readable separation and contact.
- **Cross-shot:** chapters 5/7/8 all share similar flat forest ground and near-side insect poses; varied camera angles, contrast, clear actor silhouettes, real motion and story-specific actions are still required.

## Production decision

All three chapters are **acceptable only as provisional DRAFT animatic placeholders**. Do not rerender successful chapters mid-rough-cut; finish assembling the first 14x10s source-bound 140s DRAFT, then perform targeted fixes to the failing chapters. Final quality approval remains CLOSED. A successful video decode cannot validate Hindi narration or scientific visual accuracy. Preserve V4 and successful chapter artifacts.

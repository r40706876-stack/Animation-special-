# V6.8.20 independently inspected artifact — 2026-10-30

Source: [run 41050999844](https://github.com/r40706876-stack/Animation-special-/actions/runs/41050999844), commit `5fa6f807`, artifact `jewel-wasp-v68-anatomy-gate` ID `12975894770`, 3,693,969 ZIP bytes.

## Actual evidence inspected
Downloaded and extracted the ZIP, opened `anatomy_still.png`, `roach_macro.png`, `wasp_macro.png`, `wasp_touchdown_frame48.png`, `motion_strip.png`, and `wasp_macro_motion_strip.png`. Independently ran `ffmpeg -v error -xerror -i ... -f null -` on BOTH MP4s. `ffprobe` counted 48 frames / 24 fps / 2.000000 seconds for `anatomy_motion.mp4` and 24 frames / 24 fps / 1.000000 second for `wasp_macro_motion.mp4`. Short-proof technical decode PASS, not full-film approval.

## Visual QA FAIL
- Frame-48 low-angle wasp macro has a large dark horizontal band at the bottom. This is a framing/ground-plane artifact; the diagnostic is not acceptable.
- The wasp still looks like a rigid, simplified teal toy with slender stick legs, an oversized unsegmented silhouette, and faint, poorly legible wing membranes. A photographed-insect appearance has NOT been achieved.
- The cockroach looks like overlapping flat plates with thin stick legs and a separated buttonlike head.
- Forest has an evenly lit beige stage, repeated fern shapes, and cylindrical tree trunks. It lacks a layered, photorealistic forest floor.
- Five-frame and four-frame motion strips show limited compositional and action variation. A visible believable touchdown remains unproven by the image alone; sting, burrow, egg and larva actions are not present in this specimen proof.
- A successful CI workflow is evidence only of render/decode, NOT 100% visual quality.

## Correction launched
Commit [`7bdd636`](https://github.com/r40706876-stack/Animation-special-/commit/7bdd636295247a179ec608d17727ebcafa3a95d2) changes ONLY the diagnostic camera (higher angle and tighter portrait framing to remove the dark underground band) and adds a numeric world-space gate measuring six wasp tarsus mesh vertices relative to the soil at frames 1 and 48. It requires at least two tarsi near ground, no deep intersection, and initially airborne feet. This is a **geometry-only** test, not biological motion approval. [Proof run 41057769325](https://github.com/r40706876-stack/Animation-special-/actions/runs/41057769325) must finish and its actual new artifact must be reviewed before any visual pass.

## Full film
The 14-chapter full renderer is deliberately fail-closed because the V6.8 rigs are not integrated. Do not remove this guard or spend full-render time until chapter-specific animated action proofs and actual visual QA pass. No verified 3,360-frame / 140-second final, complete Hindi narration or synchronized playable film exists. Preserve V4 and earlier artifacts.

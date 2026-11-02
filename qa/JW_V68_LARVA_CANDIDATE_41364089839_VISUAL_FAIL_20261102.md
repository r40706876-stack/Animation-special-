# Jewel Wasp V6.8 candidate — independent visual FAIL (2026-11-02)

**This is NOT a final approval and must not be promoted into the 14-chapter story renderer.**

## Direct artifact inspection
- Run: https://github.com/r40706876-stack/Animation-special-/actions/runs/41364089839
- Artifact: https://github.com/r40706876-stack/Animation-special-/actions/runs/41364089839/artifacts/13106813469
- Candidate source SHA: `2e28134ed72a2556d04c658998217991cbb7c098`; `QA.json` reports candidate-only, `visual_approved=false`.
- Inspected the actual `DRAFT_EGG_LARVA_CONTACT.png` (chapter 12 frames 120 and 180), `ch12_motion_strip.png` (four distinct frames from the 24-frame motion proof), and preflight log.
- **Visual FAIL:** the externally attached larva still looks like a detached beige bivalve shell with a dark horizontal seam, oversized relative to the flank, rather than a soft living larva. It is also placed outside the host rather than visibly developing within it. The 24-frame strip shows no convincingly readable growth/feeding action. Camera-facing/contact assertions and 24-frame H.264 decode are technical checks only, not visual evidence of believable anatomy.
- Technical preflight passed: `JW_LARVA_CAMERA_CONTACT 0.2406 0.28` and action projection at frame 180 `(0.642,0.375,1.909)`. This only proves a projected target, not a good visual.

## Safe targeted correction under evaluation
- A separate candidate, commit [`9fb2810a`](https://github.com/r40706876-stack/Animation-special-/commit/9fb2810aea2f82e005f92d13281b9343c4cacc8c), replaces the exterior shell with a **clearly schematic translucent near-side abdomen cutaway** and a compact softly segmented larva within the host. It preserves the original V6.8 anatomy rig, V4, and the actual 14-chapter story renderer. It changes the camera to focus on the internal action and adds a cutaway geometry preflight.
- The automatically triggered low-cost candidate QA is https://github.com/r40706876-stack/Animation-special-/actions/runs/41368963939 . This run was **queued**, not rendered or visually approved, when this note was prepared.
- Do not merge the candidate until its actual 360×640 stills **and** animated proof have been independently inspected. If it still looks artificial, revise the storyboard/shot, not the same tiny specimen repeatedly.
- The existing 14-chapter DRAFT preview run https://github.com/r40706876-stack/Animation-special-/actions/runs/41359048481 remains in progress and is not to be cancelled or invalidated by this experiment.

## Final gates
`draft_only=true`, `visual_approved=false`, `hindi_listen_verified=false`, `full_render_authorized=false`. A green proof run is not a final film. Preserve successful chapters and V4; require final independent 3360-frame, 24fps, 140-second, full-decode, synchronized Hindi and visual checks.

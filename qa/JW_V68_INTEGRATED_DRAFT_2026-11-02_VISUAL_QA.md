# Jewel Wasp V6.8 integrated 140-second DRAFT — independent visual QA (2026-11-02)

**Artifact:** GitHub Actions run 41402745255, artifact 13146151415 (`jewel-wasp-v68-INTEGRATED-140s-rough-cut-DRAFT-NOT-FINAL`).

## Confirmed technical milestones
- All seven updated chapters (3, 5, 8, 10, 11, 12, 13) rendered; the seven unchanged baseline chapters (0, 1, 2, 4, 6, 7, 9) were reused.
- Assembled MP4 independently downloaded and tested with `ffmpeg -v error -xerror -i ... -f null -` (complete decode PASS).
- `ffprobe -count_frames`: exactly 3360 video frames, 24/1 fps, 140.000 s; portrait 216x384, H.264 video and AAC stereo 44.1 kHz audio.
- Visible `DRAFT - NOT FINAL` watermark. Reused older Hindi narration is present, but **not listen-verified or scene-sync-approved**. Audio signal/codec presence does not establish intelligibility.
- This is an integrated *low-resolution DRAFT*, **not** a visually approved or final film.

## Actual pixel review
Viewed the provided 14-chapter contact sheet, and independently sampled actual video frames at +1, +5, +9 seconds for chapters 3, 5, 8, 10, 11, 12, 13.

- **3 and 5 (sting):** near-duplicate insect-over-roach staging; anatomical contact and needle cannot be reliably identified in sampled low-resolution pixels; motion proof needed.
- **8 (antenna guidance):** two insects visible, but physical antenna-grasp is not legible; needs camera/action detail and short motion proof.
- **10 (burrow entry):** hole visible, cockroach partly cropped at start and absent from sampled middle/end frames. The entry action is not readable. **Visual FAIL.**
- **11 (egg placement):** extreme close-up crops the wasp and host; white egg/ovipositor gesture is not legible. **Visual FAIL.**
- **12 (larva):** pale flat capsule remains static-looking in sampled frames, no convincing internal segmented larva/host cutaway. **Visual FAIL.**
- **13 (emergence):** mostly empty burrow at +1/+5 seconds, tiny distant wasp visible only near +9 seconds; emergence itself is not clearly readable. **Visual FAIL.**
- Broadly: insects remain simplistic/toy-like, repeated woodland backgrounds and compositions. Do not mark anatomical/organic visual quality as passed.

## Safe action taken
Commit `0bc8327c8bcc6d8640d2729742f7a44073c7d7eb` adjusts story renderer (NOT V4):
- Chapter 10 camera tracks actor toward burrow mouth instead of centering only on empty hole.
- Chapter 11 wider shot and focus blend to include depositing wasp as well as egg.
- Chapter 13 slightly earlier rise and closer hole-focused camera for a longer readable emergence.
These changes **have not been visually re-rendered or approved**. First run geometry preflight and low-cost selected stills/motion previews for 10, 11, 13. Do not rerender all 14 or change successful artifact baselines without evidence.

## Next gate
1. Cheap preflight of camera changes; then short animated proof / still contact sheet for chapters 8, 10, 11, 12, 13 (focus on failed events).
2. Improve cutaway larva geometry/material and the sting/antenna action readability based on real frames.
3. Re-render only failed chapters and reuse all unaffected successful artifacts, assemble updated DRAFT.
4. Independently listen to Hindi narration and verify shot-level timing; only then consider costly final resolution.
5. Keep V4 and final visual gate intact. No green CI substitutes for visual approval.

## Follow-up: bounded integrated story proofs requested (2026-11-02)
- Existing targeted workflow updated in commit `0f60aae330822c31191b1ca0d4fab8e769557521` to use the **actual integrated story renderer**, not the separate 2-second anatomy specimen.
- Structural preflight targets action chapters **3, 5, 8, 10, 11, 12, 13**; source compilation and chapter geometry checks run before any pixels.
- Explicit source-hash-bound request `ops/JW_V68_TARGETED_PROOF_REQUEST.txt` created in commit `12e8cd7b8f78339db1289f94093312e25e8ddec4` to trigger bounded DRAFT stills (10 selected frames) and 24-frame motion windows (3, 8, 10, 11, 12, 13).
- Workflow continues to watermark previews, ffmpeg-decode motion clips, require 24 frames per clip, and save a contact sheet and provenance with `visual_approved=false`. It does **not** run the 14-chapter full render.
- **Execution status not yet verified:** GitHub connector's commit-to-runs lookup does not return push-triggered runs. Do not report these proofs as rendered, passed, or visually inspected until actual run/jobs/artifacts are independently retrieved.
- The already assembled 140-second DRAFT remains technically valid but visually failed. Hindi speech intelligibility and scene synchronization remain unapproved. V4, old chapters, and final gates remain untouched.

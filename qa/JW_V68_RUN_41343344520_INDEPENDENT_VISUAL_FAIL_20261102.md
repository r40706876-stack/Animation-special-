# Jewel Wasp V6.8 — independent rendered egg/larva visual QA (2026-11-02 IST)

**FINAL VISUAL QA: FAIL. DRAFT ONLY.** This report is based on actual downloaded renders, not a green Actions badge. Do not use it to approve a final film or to re-render the whole 140 seconds.

## Reproducible evidence
- Current story source: `ef1148dc43d5eda85c9c5c45b66351d4b931545e`.
- Targeted run: https://github.com/r40706876-stack/Animation-special-/actions/runs/41343344520
- Artifact ID: `13098819383`, 18 files, including `DRAFT_EGG_LARVA_CONTACT.png`, 4 stills, `ch11_DRAFT.mp4`, `ch12_DRAFT.mp4`, 2 four-frame motion strips and Blender logs.
- Chapter 11/12 geometry preflight: PASS; proof-window camera projections are inside frame. Both 24-frame H.264 motion files decode. **These technical passes do not establish visual quality.**
- Inspected the actual 2x2 still contact sheet and both 4-frame motion strips. These are only one-second action samples, not full ten-second reviews.

## Actual failures visible in frames
1. **Chapter 11 egg placement: FAIL.** At frame 205 the egg reads as a round white bead below the roach, separated visually from the femur; the leg attachment and ovipositor-to-egg transfer are not readable. At frame 140 the huge wasp abdomen obscures the contact area. In the 24-frame motion strip, a thin appendage swings past the roach while the white bead appears separately. This is not a convincing oviposition action despite camera-framing preflight PASS.
2. **Chapter 12 larva: FAIL.** In stills at 120/180 and the motion strip, the pale, broad, strongly striped body resembles a rigid shell/clam stuck to the cockroach flank, not a soft tapered feeding larva. The scale is disproportionately large; the brown head capsule looks like a detached knob. Shape-key growth alone is insufficient. Camera visibility is adequate but biological plausibility is not.
3. **Cross-shot continuity: FAIL/PENDING.** Egg-to-larva transition is not demonstrated; the leg egg and flank larva look like unrelated objects. The present one-second samples do not verify the full ten-second chapter action or Hindi narration.

## Safe next correction (actual 14-chapter story renderer only)
- **Do not rerun the isolated 2-second anatomy specimen.** In `src/jewel_wasp_v68_story_draft.py` chapter 11, align the egg's long axis with the actual animated roach femur, move its centre onto the femur surface rather than the space beside the leg, and make the attachment/contact visibly readable; stage the wasp abdomen so the ovipositor tip and egg are visible together. Add leg-to-egg world-space distance assertions at the actual placement frames, not merely camera-projection checks.
- In chapter 12, reduce larva length/girth and material contrast; use a tapered curved organic body with soft segmentation and a connected small head. Keep it visibly contacting the abdomen through the growth frames and validate actual motion.
- Make one **low-cost still-only preflight** of these two chapters first. Review both stills **before** spending CPU on 24-frame motion proofs; then review motion before any chapter-wide render. Keep explicit DRAFT watermark.
- Do not push an edit to the story renderer while full preview run `41343344530` is in progress: the preview workflow has `cancel-in-progress: true`, so a new push would waste the current 14-chapter proof. Apply focused corrections once the running proof finishes, preserving artifacts.
- The existing rough-cut run `41245294072` already has a technical 3360-frame / 140.000-second DRAFT. Preserve it as an **older-source baseline**, not as a current visually approved film. New source changes require new source-specific proof and eventual selective chapter replacement.
- Keep V4 and all final quality gates intact; Hindi narration intelligibility, semantic timing, and independent full-video visual approval remain outstanding.

**QA disposition:** `visual_approved=false`, `final_film=false`, `full_render_authorized=false`.

# Jewel Wasp V6.8 DRAFT action proof — independent visual QA (2026-11-01)

Source: [Actions run 41258115173](https://github.com/r40706876-stack/Animation-special-/actions/runs/41258115173), artifact `jewel-wasp-v68-story-draft-preview` (13068195058), source SHA `7eaee894dd6ecbaac384dec4ffa4faa119827e9f`.

**Verdict: TECHNICAL PROOF PASS / VISUAL QUALITY FAIL / FINAL APPROVAL BLOCKED.** This is not a final film. Preserve V4 and the existing 140-second DRAFT rough cut.

## Evidence inspected
- All 14 actual DRAFT chapter stills in `DRAFT_14_CHAPTER_CONTACT.png`.
- Four-frame motion strips and decoded MP4s for chapters 1, 3, 5, 8, 10, 11, 12.
- All seven proof MP4s contain 24 frames at 24fps, 270x480, 1.000s. DRAFT overlays are visible. This validates decoding, **not** realism or action.
- The preview report explicitly has `visual_approved=false`, `final_film=false`.
- Chapter 13 motion proof was missing from the original proof matrix. A separate low-cost targeted chapter 13 proof workflow was added in commit `14c3255443fd7ff31949292fd04bd31f8a3af6c2`; inspect its artifact before approving emergence.

## Visual failures requiring targeted fixes
1. **Sting, chapters 3 and 5:** the wasp overlaps the cockroach, but the sting's insertion point and body contact cannot be clearly distinguished at normal viewing size. A geometry assertion alone is not visual proof. Reframe and expose the actual contact, verify with multiple motion frames.
2. **Burrow, chapter 10:** motion shows the roach disappearing down a circular opening, but the animal/entrance are toy-like and the approach is not convincingly staged. Confirm a continuous approach-to-descent shot, no ground intersection, and adequate silhouette visibility.
3. **Egg, chapter 11:** egg appears as a flat white oval below the roach rather than an unmistakably attached, elongated egg on the host. Ovipositor and deposition are not readable. Correct placement, shape, contrast and camera angle.
4. **Larva, chapter 12:** the larva resembles a broad pleated sheet, not a volumetric segmented larva. Change its silhouette, cross-section and attachment, then prove bending/growth in motion.
5. **Camera / staging:** multiple chapters repeat similar eye-level two-insect compositions despite independent camera offsets. Distinguish shot sizes, angles and narrative beats more strongly.
6. **Finale, chapter 13:** still shows a wasp near the burrow but cannot prove emergence. The new targeted motion proof must be viewed before acceptance.
7. **Hindi narration:** no synchronized audible narration was verified from these silent 1-second motion proof clips. Independently listen to the assembled 140-second DRAFT and check timing/word intelligibility.

## Safe production next steps
- Do not rerender all 14 chapters or run a high-quality final on the strength of green CI.
- Review the chapter 13 targeted motion artifact; then patch only failed story chapters and run inexpensive focused preflight/still/motion proofs.
- Reuse already-good chapter renders, keep the visible DRAFT watermark, preserve V4 and final quality gates.
- Only after visual approval, run the final render and independently verify 3360 frames, 24fps, exact 140s, full FFmpeg decode, audible synchronized Hindi narration and final contact sheet.

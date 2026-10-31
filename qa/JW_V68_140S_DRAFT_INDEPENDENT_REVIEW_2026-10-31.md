# Jewel Wasp 140-second DRAFT — independent artifact review (2026-10-31)

**Scope:** GitHub Actions [rough-cut run 41110464863](https://github.com/r40706876-stack/Animation-special-/actions/runs/41110464863), artifact `jewel-wasp-v68-140s-rough-cut-DRAFT-NOT-FINAL` (ID 13027612977). This review is **not final approval**.

## Independently verified from downloaded MP4

- File: `JEWEL_WASP_140S_ROUGH_CUT_DRAFT.mp4`; source commit `029293a70abb98f1f5cf7c03bcf91d78295fce20`.
- Exactly 14 concatenated chapters x 10 s, 3360 video frames at 24 fps, 140.000 s container duration.
- H.264 video 162 x 288; AAC stereo 44.1 kHz; full `ffmpeg -v error -xerror -i <file> -map 0:v:0 -f null -` decode succeeded.
- DRAFT - NOT FINAL watermark is visible in inspected frames.
- Audio stream exists and is non-silent through the 14 narration intervals; `voice.log` reports `JEWEL_FULL_HINDI_NARRATION_READY 14`. **Human listening/intelligibility and word-to-action sync are NOT verified**. Silence detection at -38 dB found a ~3.66 s gap from 76.59 to 80.25 s; some other chapter boundaries have ~2 s silence. Do not mark Hindi narration as final QA pass.
- Independently viewed supplied 14-chapter contact sheet and 28 frames at chapter offsets +2s and +7s. Distinct chapter positions/camera angles exist, but composition remains very repetitive and some actions are not visually intelligible.

## Final visual QA: FAIL (DRAFT rough cut is useful as a story scaffold)

- Chapters 0–2: distant insects, empty ground, weak readable pursuit/escape.
- Chapters 3 and 5: sting contact with correct thoracic/head targets cannot be identified confidently.
- Chapters 4 and 6: symbolic neural dots without readable change in motion/behavior.
- Chapters 7 and 8: walking/antenna-guidance behavior insufficiently distinct from ordinary motion.
- Chapters 9–10: burrow is a dark flat oval; cockroach's entry/descent is unclear.
- Chapter 11: egg placement is not readable at rough-cut scale; previously rendered egg sat on dorsal body rather than near leg.
- Chapter 12: eight white detached sphere segments read as pearls, not an organic larva.
- Chapter 13: repeats earlier wide encounter staging; needs a distinct finale composition.

## Targeted next step (do not rerender all 140 s)

The first focused source correction is [commit 0579fdfd](https://github.com/r40706876-stack/Animation-special-/commit/0579fdfd500cf26dd06cec4f0b5d436887eeca65): one continuous tapered larval mesh with subtle annular grooves, near-leg egg attachment, macro framing for chapters 11/12, and descending cockroach motion in chapter 10. **These edits are unverified until fresh preview artifacts are inspected**. Push triggers the low-cost `jewel_wasp_v68_story_draft.yml` preview workflow, which renders 14 stills and only four 1-second action clips (chapters 3, 5, 10, 12).

Review new contact sheet AND animated proof clips, then fix remaining fails (especially sting, antenna, walking and forest realism). Keep V4 and successful original DRAFT chapter artifacts intact. The old 140-second DRAFT MP4 is an independently decoded baseline, not a finished film. **Do not approve a new full render until previews pass visual QA.**

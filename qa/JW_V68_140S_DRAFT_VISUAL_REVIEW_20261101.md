# Jewel Wasp V6.8 — 140-second DRAFT rough cut independent visual QA (2026-11-01)

**Status: DRAFT ROUGH CUT COMPLETE; FINAL VISUAL AND HINDI-LISTEN QUALITY GATES FAIL / UNVERIFIED.** Do not claim this is a finished film. Preserve V4, successful chapter artifacts, and source-fingerprint caches.

## Exact reviewed evidence

- [GitHub Actions rough-cut run 41245294072](https://github.com/r40706876-stack/Animation-special-/actions/runs/41245294072), commit `e9817cd21f4dc67f60d1517db28751e38102bb9b`.
- [DRAFT assembly artifact 13063132162](https://github.com/r40706876-stack/Animation-special-/actions/runs/41245294072/artifacts/13063132162), containing `JEWEL_WASP_140S_ROUGH_CUT_DRAFT.mp4`, 14-chapter contact sheet, audio-signal report, and voice log.
- Independently downloaded and decoded actual MP4 using `ffmpeg -v error -xerror -i ... -f null -`: PASS. `ffprobe`: H.264 216x384, 24 fps, exactly 3360 video frames, duration 140.000 seconds, AAC audio track. Visible DRAFT - NOT FINAL watermark in reviewed frames.
- `DRAFT_AUDIO_SIGNAL_QA.json` reports signal in all 14 chapters and no long silence warnings at its chosen threshold. **This is not a language, intelligibility, or semantic sync check.** `voice.log` reports chapter tempo increases from ~1.04x to 1.38x; accelerated Hindi voice must be listened to.
- Independently inspected supplied contact sheet and 35 extracted frames: chapters 3,5,9,10,11,12,13 at chapter offsets +1,+3,+5,+7,+9 seconds. A frame sequence is not a substitute for listening and watching full motion.

## Actual visual findings (FAIL for final)

- **3 and 5 — thoracic/head sting:** wasp is cut off at the right/top of several action frames; needle contact cannot be identified reliably. Fix framing to show abdomen, target, and contact in the same shot.
- **9 — burrow approach:** a recognizable opening and approach are present; entry is not demonstrated in this chapter.
- **10 — burrow entry:** wasp obstructs the entrance in late frames, and the cockroach is not clearly seen disappearing into the tunnel. Keep wasp off the mouth and show descent below the opening.
- **11 — egg:** a white egg appears near the roach at the end, but it looks round, not a distinct elongated leg-attached egg. Ovipositor contact needs a 1-second action proof.
- **12 — larva:** visible growth occurs, but it reads as a broad flat pale strip on the roach, not a convincingly volumetric organic larva.
- **13 — finale:** generic wide wasp/roach forest composition repeats the opening; no visually distinct life-cycle payoff or emergence.
- **Across chapters:** V6.8 assets are integrated, but anatomy and environment still appear simplified; close-ups, occlusion, grounded movement, and scientific readability require visual QA.

## Focused correction and evidence gate

- [Targeted story-renderer correction 7eaee894](https://github.com/r40706876-stack/Animation-special-/commit/7eaee894dd6ecbaac384dec4ffa4faa119827e9f): less clipped sting composition, repositioned wasp and deeper cockroach descent at burrow, elongated egg silhouette, more volumetric warm-tan segmented larva, and a distinct burrow-emergence finale. **Unverified until new stills and animated proofs are inspected.**
- [New low-cost preview workflow run 41258115173](https://github.com/r40706876-stack/Animation-special-/actions/runs/41258115173) was triggered by that source edit. Check geometry preflight and actual still/motion artifacts before accepting any change. This does **not** authorize a new 14x240-frame high-quality render.
- After reviewing previews, fix only failed chapters and preserve unchanged successful 10-second segments. Because the source fingerprint changed, any future DRAFT cache reuse must be deliberate and validated; do not blindly treat stale visuals as new.
- Keep final gate closed until visual inspection of all chapters, full audio listening and semantic synchronization, 3360-frame technical decode, exact 140s and independently playable final MP4.

**V4 sources were not edited.**

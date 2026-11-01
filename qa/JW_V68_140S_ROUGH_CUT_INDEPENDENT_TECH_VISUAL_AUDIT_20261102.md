# Jewel Wasp — 140-second older-source DRAFT independent audit (2026-11-02 IST)

**FINAL QUALITY: NOT APPROVED. Do not deliver as final.** This is a direct inspection of the existing rough-cut artifact, not a green-CI inference.

## Provenance and technical verification
- GitHub Actions run: https://github.com/r40706876-stack/Animation-special-/actions/runs/41245294072
- Artifact: `jewel-wasp-v68-140s-rough-cut-DRAFT-NOT-FINAL`, ID `13063132162`.
- Artifact's `DRAFT_QA.json` identifies source commit `e9817cd21f4dc67f60d1517db28751e38102bb9b`, **not** the latest renderer.
- Independently ran `ffprobe` on `JEWEL_WASP_140S_ROUGH_CUT_DRAFT.mp4`: H.264 video, 24/1 fps, **3360 frames**, exactly **140.000000 s**, AAC audio present.
- Independently ran `ffmpeg -v error -xerror -i JEWEL_WASP_140S_ROUGH_CUT_DRAFT.mp4 -f null -`: **FULL_DECODE_OK**.
- Resolution is only **216x384** (DRAFT), not high-quality final.
- `DRAFT_AUDIO_SIGNAL_QA.json` reports audible signal in all 14 10-second windows; **language, intelligibility, narration-to-action synchronization and full listening are NOT verified**. Audio presence must not be reported as a Hindi QA pass.

## Actual visual inspection
- Inspected the artifact's `DRAFT_14_CHAPTER_CONTACT.jpg`: all fourteen story positions are represented and the watermark clearly says **DRAFT - NOT FINAL**, but the image is a very low-resolution animatic, not visually approved 3D film.
- Composition varies (forest wide views, pursuit, sting macro, burrow, egg, larva, finale), but the ground appears broad, washed out and sparsely textured in multiple shots; subject silhouettes and scene action are sometimes unclear.
- The old chapter 11 wasp is disproportionately prominent in the macro and obscures the egg transfer. The old chapter 12 larva resembles a pale rigid shell on the roach flank. A contact sheet alone does not verify flight, sting, entry, oviposition or emergence continuity.
- Also inspected **actual** targeted run `41343344520` artifact `13098819383`: four 360x640 DRAFT stills and two 24-frame motion strips. Chapter 11 shows a detached round white egg and moving thin appendage without readable deposition; chapter 12 shows an oversized, striped shell-like larva with a knob-like head. **Both visual FAIL despite preflight and H.264 decode PASS.**
- Do not infer improvements from later commits until their rendered pixels are inspected.

## Cost-aware next steps
1. Preserve V4, this older 140s DRAFT, and successful chapter artifacts. Never re-render all 14 merely to repair 11/12.
2. Existing full 14-chapter preview run `41343344530` is still in progress at the time of this audit; avoid source pushes that would cancel it (`cancel-in-progress: true`).
3. Stage corrections in the **actual story renderer**: femur-aligned slender egg with animated world-space leg-contact assertion and a wasp staged behind the egg; shorter tapered warm-tan larva with softer segments, smaller connected head, and growth anchored to the host cuticle.
4. First run only low-cost chapter 11/12 still preflight and independently inspect stills; then motion proofs; only then selectively replace failing chapter renders and check full 140s continuity.
5. Final film requires independent 3360-frame/24fps/140s/full-decode verification **and** visual quality approval **and** intelligible synchronized Hindi narration.

**QA disposition:** `draft_only=true`, `technical_baseline_pass=true`, `visual_approved=false`, `hindi_listen_verified=false`, `full_render_authorized=false`.

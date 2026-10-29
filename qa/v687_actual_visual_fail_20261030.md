# V6.8.7 independent still + motion QA — 2026-10-30 (IST)

- Source commit: `a07570f6cb266de4d47e4400d1d2ae0bf4c1f06c`.
- Actual proof: https://github.com/r40706876-stack/Animation-special-/actions/runs/40968597702
- Downloaded GitHub artifact: `12940641031` (`jewel-wasp-v68-anatomy-gate`).
- Independently probed and decoded `anatomy_motion.mp4`: 270x480 H.264, 48 frames, 24fps, exactly 2.000s, FFmpeg full decode PASS.
- Independently opened the 540x960 still, 5-frame motion strip, and an enlarged frame-1/frame-24/frame-48 strip. **Visual QA FAIL.** Technical CI green does NOT imply visual approval.

## Actual observations
1. Frame 1 cuts off the cockroach at the right edge; the initial left-biased camera focus is inappropriate for a two-insect composition.
2. A dark gray horizontal void remains across the bottom of the portrait frame, despite the extended soil plane. The previous low camera geometry causes lower image rays to miss the soil.
3. Cockroach pronotum/elytra are smooth and toy-like; wasp wings/limbs and the insect-to-ground contact are still not convincing enough.
4. Trees resemble featureless dark cylinders, and there is too much empty uniform soil, with insufficient layered undergrowth.
5. Motion shows an approach/hover but does not establish a believable sting, walking, burrowing, egg laying or larval movement. A 2s proof cannot approve all 14 chapters.
6. **Full-render integration blocker:** `src/jewel_wasp_v6_full.py` still loads the V6 proof scene plus V6.7 pass. V6.8 anatomy source is not integrated into the actual 14-chapter renderer.

## Corrective next proof
- V6.8.8 commits `4f211777` and `1658573f` elevate and recenter the camera, reduce pronotum/eye exaggeration and add midground foliage and roots.
- These corrections are **not visually approved** until their own rendered still and short animation have been independently viewed.
- Keep full 140-second render gated. Preserve V4 and successful artifacts; integrate approved V6.8 anatomy into the actual 14-chapter scene before representative chapter proofs.

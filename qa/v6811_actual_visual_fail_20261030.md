# V6.8.11 independently inspected actual proof — technical PASS, visual FAIL (2026-10-30)

- Workflow run: https://github.com/r40706876-stack/Animation-special-/actions/runs/40993846672
- Source commit: `fb4baa18b68be5de8157b3a01a433d04ff94217d`
- Downloaded artifact ID: `12951613196` (`jewel-wasp-v68-anatomy-gate`).
- Downloaded ZIP SHA-256: `d8e57506f6312fa437a2493a16607c67ebb36d39015c3cc5ecfa8084fb0eab71`.
- Independent `ffprobe`: `anatomy_motion.mp4` is 270x480, 24fps, **48 frames**, 2.000s; `wasp_macro_motion.mp4` is 270x480, 24fps, **24 frames**, 1.000s.
- Both videos passed an independent full `ffmpeg -v error -xerror -i FILE -f null -` decode.
- **Actually viewed** `anatomy_still.png`, `roach_macro.png`, `wasp_macro.png`, `motion_strip.png`, and `wasp_macro_motion_strip.png`. This judgment is not inferred from green GitHub Actions.

## Actual visual findings

1. Both insects are visible and the floor no longer has the previous black edge. Nevertheless the encounter is small within a portrait composition and much of the frame is empty floor.
2. The jewel wasp still resembles a simplified toy: large round head/thorax, protruding bead-like eyes, evenly striped capsule abdomen, stiff orange legs. The wing transparency is visible, but the wing/body silhouette is not natural enough.
3. The cockroach is too cylindrical and smooth, with a saucer-like pronotum, flat overlapping wing plates, bead-like joints and sparse legs. It does not yet read as a convincing real cockroach.
4. The forest is made of repeated flat leaf silhouettes, straight stems and simple trunks; scale, light and material variation remain insufficient.
5. The sampled wide and macro motion frames show flight/pose changes but do **not** prove believable walk, sting, burrow, egg placement or larva action. No 14-chapter visual approval can be inferred.

**VISUAL GATE: FAIL. FULL-FILM GATE: CLOSED.**

## Follow-up

- V6.8.12 anatomy changes are committed separately to `src/jewel_wasp_v68_anatomy_proof.py` (commit `7d8130c`); inspect its actual new artifact before claiming improvement.
- V6.8 clean-room proof is **not integrated** into `src/jewel_wasp_v6_full.py`; that full renderer still injects V6.7. Integration requires an explicit source path and a reviewed chapter-level proof, not just a successful anatomy specimen.
- Do not create `ops/V6_VISUAL_APPROVED.txt` or launch the expensive 14-chapter render until the scene and motion proof have passed independent review.
- Keep V4 and existing successful chapter artifacts untouched.

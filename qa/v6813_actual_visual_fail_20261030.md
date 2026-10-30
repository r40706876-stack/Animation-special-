# V6.8.13 independent actual-artifact QA — 2026-10-30

Source commit: b2296aaca01ae90db190d0528e8b3698df17e846
Proof run: https://github.com/r40706876-stack/Animation-special-/actions/runs/41004740123
Artifact: jewel-wasp-v68-anatomy-gate (artifact ID 12956222919; ZIP downloaded and independently inspected).

## Technical PASS (proof only)
- anatomy_motion.mp4: 270x480 H.264, 48 decoded frames at 24 fps, exactly 2.000 seconds; full ffmpeg decode PASS.
- wasp_macro_motion.mp4: 270x480 H.264, 24 decoded frames at 24 fps, exactly 1.000 second; full ffmpeg decode PASS.
- Inspected actual roach_macro.png, wasp_macro.png and five-frame motion_strip.png from this artifact, not only CI status.

## Visual FAIL (full-film gate remains closed)
- Roach macro: elytra still look like overlapping detached, planar plates rather than a naturally curved dorsal shell; visible large smooth toy-like pronotum and rigid straight legs.
- Wasp macro: oversized simple rounded head/thorax, straight cylindrical legs and simplified transparent wings; does not resemble documentary-quality anatomy.
- Two-second motion strip: specimens remain small in a largely static, sparse, flat-looking forest. Motion demonstrates basic approach/hover but does NOT prove sting, burrow, egg laying or larval activity.
- No independently approved 14-chapter story proof, 140-second full film, or synchronized Hindi narration.

## Corrective action
V6.8.14 source commit d17962aabe7c4296f1acc02783b75bb903184230 lowers and curves the roach elytra, reduces flat plate look, darkens/roughens wing cuticle, replaces raised pronotum button, and adjusts wasp head and eye microtexture. New proof must be downloaded and independently inspected before any approval. This is an experiment, not a claim of visual quality.

## Integration blocker
src/jewel_wasp_v6_full.py still builds its scenes from jewel_wasp_v6_proof.py and injects jewel_wasp_v67_focus_pass.py. It does NOT use the independent V6.8 anatomy proof. The V6 full workflow's approval fingerprint also omits the V6.8 source. Any eventual integration must update the chapter renderer, proof and source-fingerprint gate together, preserve V4 and successful chapter artifacts, and be re-reviewed before expensive full render.

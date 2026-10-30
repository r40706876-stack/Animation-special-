# V6.8.16 actual-artifact independent QA — 2026-10-30

**GitHub Actions run:** https://github.com/r40706876-stack/Animation-special-/actions/runs/41022475727  
**Source commit:** `eb5f70aa978e4f51e83887f1ade31b0d2cd04ef2`  
**Downloaded artifact:** `jewel-wasp-v68-anatomy-gate`, id `12964090606`, ZIP 3,026,003 bytes.

## Technical result: PASS for short specimen proofs only
- Independently unpacked the artifact and ran `ffprobe` and full `ffmpeg -v error -xerror -i FILE -f null -` decode on **both** MP4s.
- `anatomy_motion.mp4`: 270×480, 24 fps, **48 decoded frames**, **2.000 seconds**, full decode PASS.
- `wasp_macro_motion.mp4`: 270×480, 24 fps, **24 decoded frames**, **1.000 seconds**, full decode PASS.
- Opened actual `anatomy_still.png`, `wasp_macro.png`, `roach_macro.png`, `motion_strip.png` and `wasp_macro_motion_strip.png`; these are not simulated descriptions.

## Visual result: FAIL — full render must remain gated
The wasp still reads as a stylized metallic insect: a smooth oversized oval thorax, large detached-looking pointed gaster, tiny spherical head, long straight stick-like legs and barely visible wing membranes. Its flight is a lateral glide/hover, not a believable sting or locomotion interaction. The cockroach remains a simplified flattened oval with a conspicuous round disk-like pronotum and repeated raised parallel lines on its wing covers; legs are rigid. The forest resembles a stage with repetitive flat foliage, polygonal leaf litter, cylindrical distant trunks and large bare soil areas. Contact strips do not demonstrate convincing sting, burrow, egg deposition or larva movement.

## Required next gate
1. Improve wasp femur/tibia bend and ground-contact anatomy; replace round cockroach pronotum with a thin integrated shield and tone down wing-cover line ridges.
2. Run a **new** short anatomy/motion proof and visually inspect its actual artifact; do not approve based on CI alone.
3. Integrate approved V6.8 roots into the **real** 14-chapter renderer. The old `src/jewel_wasp_full.py` still imports `jewel_wasp_3d.py`; V6.8 proof alone does not validate 14 distinct shots.
4. Produce independent action proofs for sting, antenna leading, burrow, egg and larva. Keep the 140s full render blocked until those previews pass.

**Preservation:** No changes to V4, prior chapter artifacts or previous run outputs. Green technical CI is not 100% visual quality.

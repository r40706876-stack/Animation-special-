# V6.7.3 independent partial visual QA — 2026-10-29

Source: `540edb11af66be0d6b1fd0ce8809112da3052434`.
Proof: https://github.com/r40706876-stack/Animation-special-/actions/runs/40844741407

Downloaded and opened actual artifact ZIPs (not just green checks):
- chapter 3: artifact 12887995962; `proof/chapter_03.png`, `motion/motion_3.mp4`
- chapter 5: artifact 12887536140; `proof/chapter_05.png`, `motion/motion_5.mp4`
- chapter 12: artifact 12885709114; `proof/chapter_12.png`, `motion/motion_12.mp4`

Each MP4 has 48 frames at 24fps, 270x480, 2 seconds. Sampled actual frames at 0, 0.5, 1, 1.5 seconds and examined original full-resolution stills.

**VISUAL FAIL — do not approve 14-chapter full render.**

- **3 sting:** Insects are identifiable, but stinger appears as an unusually long rigid tan rod from wasp to roach. No convincing short anatomically connected insertion; scene still has simplified bead/ellipsoid bodies and uniformly straight appendages.
- **5 sting:** Wasp overlaps cockroach, so the actual sting contact is occluded. Even with wider V6.7.3 camera, the event is not legible.
- **12 larva:** Camera now gives a large clear larva, but it reads as a white slug with protruding spines on a broad brown wing cover. Real larval folds and plausible surface attachment are missing. Animated deformation is subtle and does not yet demonstrate credible crawling.
- **10 burrow:** Job was still running when this partial review was written; no claim of approval or failure without opening its evidence.

Broader persistent weaknesses: simplistic flat ground and repeating schematic foliage, simplified insect anatomy/rigging, unnatural movement. Technical CI success and ffmpeg decode cannot certify visual quality.

**Next bounded fix, only after chapter 10 artifact is preserved:** stage a distinctly tighter chapter-3 sting insert and side-separated chapter-5 view; replace floating larval 'fold' ellipsoids with continuous mesh grooves and a modestly warmer cuticle; inspect chapter-10 late-entry frames before touching burrow. Preserve all V4/V6 successful artifacts. Prevent new push from cancelling the currently running chapter-10 job. Compare full-resolution stills and 48-frame motion strips before any full render.

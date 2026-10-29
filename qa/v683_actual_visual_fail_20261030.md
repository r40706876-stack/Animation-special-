# V6.8.3 independent visual QA — 2026-10-30 IST

Source proof: https://github.com/r40706876-stack/Animation-special-/actions/runs/40933444597
Artifact: jewel-wasp-v68-anatomy-gate (ID 12924374400)
Source commit: 043b71b012d4392ce121dd957c361cbbd3fad1f9

## Technical checks
- All proof workflow steps passed, including Blender render, 48-frame ffmpeg decode, 24 fps.
- Downloaded and independently decoded the actual MP4, not just relying on the green workflow.
- Proof is only 2 seconds; it cannot establish readiness for a 140-second film.

## Visual QA: FAIL (actual still and five-frame strip viewed)
- The 9:16 composition clips the wasp at the left edge and the cockroach at the right edge in the motion strip.
- Forest floor ends in a prominent dark horizontal strip near the bottom of the still; scene is visibly artificial.
- Both insects still look like simplified hard-surface toy models; wing membrane and roach dorsal shell need better organic form.
- The motion shows wing flapping and slight approach, but does not prove believable walking, sting, burrow, egg or larva.
- The insects are placed low in the portrait frame and do not use the frame effectively.

## Corrective action
V6.8.4 proof code change b42d6b27c66dfb4ece35911ae9a845bedbe4732c:
- Reframe camera and reduce root rig scales to avoid horizontal cropping.
- Enlarge forest-floor geometry to avoid the visible ground edge.
- Add warm amber wasp leg cuticle for anatomical differentiation.
- Preserve V4 and all successful prior artifacts.

## Next gate
Download and VIEW the new V6.8.4 still and five-frame animated strip. Verify actual composition and movement; no full 14-chapter render until visual QA passes. Green CI is technical only.
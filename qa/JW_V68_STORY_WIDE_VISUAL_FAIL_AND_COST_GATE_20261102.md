# Jewel Wasp V6.8 — story-wide independent DRAFT visual review (2026-11-02)

**Disposition: VISUAL FAIL; FINAL RENDER NOT AUTHORIZED.** This review inspected the actual downloaded PNG contact sheets, 14 chapter stills, 24-frame motion proof strips, and decoded motion clips, not merely GitHub green checks.

## Evidence provenance
- Existing complete 14-chapter still/motion preview: [run 41359048481](https://github.com/r40706876-stack/Animation-special-/actions/runs/41359048481), artifact ID `13108914899`, source `cd5ede0740fa4330cf09863a92a9ecfd024fd21c`. Contains 14 stills and motion clips for chapters 1,3,5,8,10,11,12,13.
- New experimental action candidate: [run 41379814200](https://github.com/r40706876-stack/Animation-special-/actions/runs/41379814200), artifact ID `13115891518`, source `d225bc164af3c5bdb9a6723de694b09fd40ddf72`. Contains six action stills, five 24-frame motion proofs, and geometry preflights for chapters 3,5,8,10,11,12.
- Both runs completed technically; candidate's `QA.json` explicitly says `candidate_only=true`, `visual_approved=false`, `final_film=false`.
- The older 140s DRAFT file was independently probed again: 3360 video frames at 24 fps, 140.000 s, H.264 + AAC. This does **not** certify Hindi intelligibility or scene-synced narration.

## Observed story-wide visual failures
| Chapter(s) | Directly observed issue | Required change before expensive render |
|---|---|---|
| 0–2 | Wasp and roach read as simple teal/brown capsule-shaped models; environment is repetitive and sparse; flight and pursuit are not convincing from the stills. | Rework silhouette, wing visibility and camera-led chase progression; retain cheap shots until the whole 10s action reads. |
| 3,5 | Sting target is near camera but the actual sting contact is not visually legible in the proof; generic root translation dominates. | Show an unobstructed macro view with the sting tip, target and reaction in the same shot; review motion, not only geometry contact. |
| 4,6,7 | Scientific effects/behavior are not visually explained; vegetation or roach body dominates. | Clear schematic insert and distinct behavioral response, avoiding identical roach walk cycles. |
| 8 | Antenna guidance appears as another generic two-insect shot, without clearly visible antenna grasp/contact. | Stage a readable antenna-to-wasp contact, host response and directional lead. |
| 9,10 | Burrow is an obvious circular pit; 24-frame chapter 10 proof has little readable entry movement. | Show full-size cockroach crossing rim and descending, with motivated side/overhead camera. |
| 11 | Egg is a small pale sliver near a leg, but transfer is occluded by the huge teal wasp; world-space contact number 0.0252 does not establish visible oviposition. | Unobstructed leg macro and egg deposition with before/after continuity. |
| 12 | New cutaway has a dark host cavity, but larva still reads as a pale flat shell/lozenge on the outside; no obvious convincing soft internal development. | Redesign staging and anatomy at the story scale; do not keep rerendering the same 1-second larva window. |
| 13 | Burrow departure still reads as a generic wasp above the pit; the short motion proof alone does not establish complete emergence. | Verify the full 10s progression from tunnel to flight. |

The candidate's chapter 12 geometric preflight reported 241 removed faces and a camera-facing larva, but the rendered pixels still fail. The short proof motion is technically present; motion metrics cannot prove biological action. Chapters 3,8,10,11,12 candidate 24-frame clips all decode, but remain **not visually approved**.

## Strategy change implemented
- Updated `.github/workflows/jewel_wasp_v68_larva_candidate_20261102.yml` in commit `c5d743caf1ac7a6c6e3e885e2a1837b70b944af5`: every push performs **all fourteen chapter geometry preflights** and saves evidence, rather than automatically spending ~90 minutes on another identical batch of 24-frame specimens.
- Full still/motion rendering now requires explicit `workflow_dispatch` with `render_proofs=true` after story-wide preflight inspection. This changes only experimental candidate QA, not V4 or the existing approved-source rough-cut artifacts.
- Do not merge the experimental cutaway into `src/jewel_wasp_v68_story_draft.py` based on a green run. No final render or final-quality bypass.

## Next production sequence
1. Review 14-chapter preflight results from the cheap run triggered by the workflow update. Fix structural failures without high-cost rerenders.
2. Make **one coordinated, story-wide** change set to model silhouettes, action staging and camera compositions, with priority 3/5 sting, 8 guidance, 10 burrow, 11 egg, 12 larva. Avoid 1-second micro-iterations.
3. Render a full storyboard contact sheet and short proofs **only after** coherent 14-shot planning; reuse exact-source chapter artifacts where possible. Review actual images and action clips before accepting any chapter.
4. Assemble a new visible-watermark 14x10s DRAFT, independently verify all 3360 frames, full decode, and listen to/sync-check the Hindi narration.
5. Only after story-wide visual approval, render high quality and repeat independent technical **and** visual verification.

**Protected:** V4, prior successful chapter artifacts and older 140s DRAFT. **Quality gates remain strict:** `visual_approved=false`, `hindi_listen_verified=false`, `final_film=false`.

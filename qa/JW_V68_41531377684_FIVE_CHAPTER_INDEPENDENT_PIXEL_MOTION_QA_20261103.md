# Jewel Wasp V6.8 — independent source-bound five-chapter pixel/motion QA (2026-11-03)

## Evidence
- Source-bound DRAFT proof run: https://github.com/r40706876-stack/Animation-special-/actions/runs/41531377684
- Renderer source commit `29f50cc358e0fc09d3c789af1ba1d9e4a39bfab3`, SHA256 `8636ad6d7078f7b955a8b7e3e4f84bb9a1079aaa5e548b0f3d76039b77e11d22` from all five QA.json files.
- Independently downloaded and extracted the actual ZIP artifacts: ch3 `13182763147`, ch5 `13182199276`, ch8 `13182473484`, ch11 `13183896804`, ch12 `13184795842`.
- Independently inspected each actual contact still, motion strip and full-resolution chapter still. Used local ffprobe and complete ffmpeg decode for each MP4; **all five are 24 frames at 24 fps, 270x480**, with no decode error.
- All five QA.json files explicitly say `draft_only=true`, `visual_approved=false`, `final_film=false`, `hindi_listen_verified=false`, `V4_preserved=true`.
- These are one-second action proofs, **not** five approved ten-second story chapters.

## Actual visual decisions
| Chapter | Observed pixels and action | Decision |
|---|---|---|
| 3 thoracic sting | Giant blue-green wasp abdomen and wings partly obscure the cockroach; needle/contact target is not clearly identifiable. Four motion samples do not establish convincing sting penetration or thoracic response. | FAIL |
| 5 head-ganglion sting | Close crop loses the wasp head and target; large blue-green body and wing occupy most of the frame. Motion appears very similar to ch3; ganglion-specific contact/reaction not readable. | FAIL |
| 8 antenna grasp | Both insect heads and some leg/mandible geometry visible, but grasped antenna-to-mandible contact is tiny and not clearly readable as a hold in the four motion samples. | FAIL |
| 11 egg deposition | White oval attached to cockroach leg is clearly visible, but oversized turquoise wasp abdomen covers much of the contact area; the ovipositor and egg transfer cannot be followed in the 145–168 clip. Existing 145/170 stills do not show pre-contact. | PARTIAL OBJECT, ACTION FAIL |
| 12 larva | Cutaway is visible, but grub looks like a pale hard-edged scalloped plaque rather than soft rounded living larva; four motion samples show no unmistakable localized contraction/feeding. | FAIL |

**Visual approval: 0/5.** The previous proof baseline ch10/ch13 is unchanged and remains only partially successful; no new final-film approval.

## Economical next actions
1. Fix actual story-renderer anatomy/staging, not another isolated 2-second specimen: correct wasp/roach relative silhouette and preserve a visible ovipositor/sting, enlarge legible mandible/antenna contact, make larva rounder and less scalloped with visibly localized motion.
2. Run geometry/camera preflight after the focused changes; only then authorize bounded DRAFT proof of changed chapters. Reuse unchanged successful proof artifacts and V4.
3. The already committed chapter-11 proof workflow patch `fed4dfc` adds frames 120–143 (pre-contact) alongside 145–168, but **has not been executed** as of this report. Do not claim egg transfer approved without this evidence.
4. Do not initiate expensive full render until visual stills + animated clips pass. Existing watermarked 140s DRAFT remains **unapproved**; independent intelligible Hindi narration/scene-sync listening, full technical decode, and final visual verification remain pending.

## Separate unrelated workflow failure
Latest scheduled `Science Documentary Studio` run `41532297863` failed because a marine-bioluminescence image request returned HTTP 402; its code correctly refused an unrelated insect fallback. This is not a Jewel Wasp V6.8 proof failure; do not waste Jewel Wasp chapter renders attempting to fix that unrelated external image provider.

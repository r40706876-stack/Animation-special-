# Jewel Wasp V6.8 — batch visual and narration audit (2026-10-31)

**Status: FINAL VISUAL QUALITY FAIL; no final render authorized.** This is a combined diagnosis, not a proof of fixes.

## Actual evidence examined

- Previous preview run [41170125163](https://github.com/r40706876-stack/Animation-special-/actions/runs/41170125163), artifact 13032738347: downloaded and opened the actual 7x2, 14-chapter contact sheet and animated action strips (especially sting 3 and burrow 10).
- Independently inspected the earlier 140s DRAFT MP4 (run 41110464863) and ran ffmpeg silence detection. The draft has 3360 frames but its 162x288 output is far too small for quality approval.
- New burrow/egg/larva source commit 04ccb347 is under preview run [41178238074](https://github.com/r40706876-stack/Animation-special-/actions/runs/41178238074). Its visual quality is **not yet verified**; do not infer improvement from passing preflight.

## Defects to address together, before another expensive full render

1. **Readability:** actors are often small, cropped or merged into low-contrast earth; the brown cockroach and soil have similar value. Sting strips show a wasp body obscuring the contact point. Brighten subject separation and stage true close-up coverage, not just higher pixel count.
2. **Story progression:** many chapters still look like the same two insects on the same forest patch. A 10-second chapter needs motivated establishing/action/reaction coverage and a visible action climax, not one static angle plus root translation.
3. **Rig/physics:** cockroach/wasp gait is procedural, but visible foot contacts, turn direction, wingbeat and body orientation are not independently approved. Test both flight and walking clips.
4. **Sting:** two close-up contact shots (thorax chapter 3; head chapter 5) must show tip, insertion, hold, withdrawal and a visible roach response. Geometry preflight alone cannot prove a viewer can see the sting.
5. **Burrow:** prior proof 10 looked like roach/wasp beside a dark disc. New open tunnel geometry needs an actual descending-motion clip and camera view that reveals the mouth and depth.
6. **Egg and larva:** prior still 11 showed tiny bright beads and 12 looked like pale stripes/pearls. New near-side egg and continuous larva must be inspected at growth/placement frames, with macro action shots.
7. **Forest/materials:** too many repeated straight trunks, flat foliage and evenly lit soil. Preserve layered forest but improve macro ground texture, natural shadows, and foreground/background depth.
8. **Audio:** old DRAFT contains a measured ~3.66s continuous silence at 76.59–80.25s. In half-second window analysis chapter 7 had a 3.0s inactive run, chapter 11 had 2.5s. New TTS pacing commit 6a7954b9 and gap diagnostic f3c36170 are unrendered/unlistened; no sync approval.

## Critical preview-time mismatch in current workflow

The workflow currently uses **JW_STILL_FRAME=120** and **JW_MOTION_START=108 for all chapters**. This misses key story actions by design:
- Ch 3,5 sting reaches/holds near frames **120–170**; show still at **145**, motion starting **118**.
- Ch 10 burrow descends around **175–240**; show still at **195**, motion starting **165**.
- Ch 11 egg grows around **145–240**; show still at **190**, motion starting **150**.
- Ch 12 larva grows/deforms throughout; show still at **180**, motion starting **108**.
- Add flight ch 1 and antenna-guidance/walking ch 8 motion evidence before final.
- Label contact-sheet tiles by chapter number and action, so reviewers can identify narrative failures.

**Do not push a story/workflow change while run 41178238074 is rendering**: preview workflow uses a shared concurrency group with cancel-in-progress=true, so another push would destroy expensive in-flight proof work. After the current artifact is uploaded, inspect its contact sheet AND motion strips, then apply a **single batch** of source/workflow corrections, run cheap preflight and targeted previews, and review real pixels before any 14x240-frame rerender.

## Hard acceptance boundary

- 14 distinct, legible 10-second chapter actions; visible realistic sting, burrow, egg and larva motion; no toy-like insects or flat repeated forest.
- 14 labeled stills and independent animated proofs must pass visual inspection. Green CI is not approval.
- Hindi speech must be audibly intelligible and scene-synchronized, not merely an audio stream with signal.
- Only then high-quality render, 3360 frames at 24fps, exact 140s, complete decode, verified audio, final playable MP4 and contact sheet.
- Preserve V4, all previous successful artifacts and the DRAFT watermark on unapproved outputs.

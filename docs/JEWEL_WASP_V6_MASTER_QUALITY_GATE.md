# Jewel Wasp V6 — one-pass production quality gate

Goal: original 14-chapter, 140-second 3D film. Do not approve a full render merely because stills render.

## All fixes must be planned together before expensive rendering
1. Anatomical models: distinct jewel wasp and cockroach silhouettes; segmented abdomen, six jointed legs each, compound eyes, antennae, correctly attached translucent wasp wings; believable scale and contacts.
2. Materials: layered iridescent emerald/blue chitin with roughness variation, cockroach brown textured exoskeleton, non-plastic soil, physically plausible highlights.
3. Forest: dense layered vegetation with near/mid/far depth, bark, foliage, roots, scattered litter, uneven earth; avoid empty flat green ground and lollipop trees.
4. Movement: grounded gait with alternating tripod contacts; purposeful wingbeat and flight paths; leg IK or consistent planted feet; no sliding, clipping or static insects.
5. Story actions: each chapter must clearly depict the appropriate moment (approach, encounter, sting, paralysis, leading/dragging, burrow, egg, larva); distinct compositions.
6. Camera: macro anatomy shots, tracking, close/wide establishing, clear sightlines for sting, burrow and larva; no cropped bodies or obscured key actions.
7. Lighting: natural directional key, bounce, contact shadows, volumetric depth when feasible, consistent exposure, non-overblown highlights.
8. Audio: intelligible and accurately timed Hindi narration, synchronized effects and music, no silent gaps or clipping.
9. Editing: story continuity, deliberate shot changes, avoid repeated near-identical 10-second compositions.

## Mandatory staged QA
- Static render all 14 chapters as contact sheet with chapter labels.
- Short animated proof clips for flight, walking, sting, burrow and larva. A still image cannot prove animation quality.
- Human visual review of actual frames and clips; reject toy-like models, empty forest, clipping, unclear action, or repetitive shots.
- Only after visual approval render 14 x 240 frames in parallel. Preserve successful chapter artifacts and rerender only failed/changed chapters.
- Assemble and verify 3360 video frames at 24 fps, 140 seconds, audio stream and Hindi narration, ffmpeg full decode, contact sheet and playable MP4.
- Report visual and technical verdict separately. Do not call an unreviewed render 10/10 or finished.

## Reuse for future films
Extract shared character rigs, forest assets, material presets, camera shot recipes, audio synchronization and QA scripts into versioned reusable modules. Record failure modes and regression tests so later films do not restart from scratch.

Current V5 proof run 40729527770 passed technical rendering but did not pass visual acceptance. No V6 full render authorized before animated proof and visual QA.

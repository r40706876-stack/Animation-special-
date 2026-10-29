# V6.7.5 independent visual QA — 2026-10-29

Source: [GitHub Actions run 40868717939](https://github.com/r40706876-stack/Animation-special-/actions/runs/40868717939), artifact jewel-wasp-v675-focused-visual-evidence (ID 12898066906). Downloaded the ZIP and inspected actual contact_v67.png and three 48-frame motion strips (chapters 3, 5, 12).

## Technical: PASS, not approval
All four jobs completed successfully. Independent ffprobe and full ffmpeg decode verified each motion clip: 48 frames, 24 fps, 270x480, 2.000 seconds.

## Visual: FAIL
- Chapter 3: toy-like turquoise wasp and oversized brown cockroach; legacy straight antenna/needle rods dominate and make actual insertion unclear; wasp cropped.
- Chapter 5: both bodies cut off at the frame edges; no unambiguous sting contact; rod-like appendages obscure the story.
- Chapter 12: larva remains a pale slug on a giant wing cover; body movement subtle and context unconvincing.
- Forest still resembles flat, sparse stage dressing. This is not an acceptable documentary visual standard.

## V6.7.6 targeted changes
Code commit b45143fa8a2f63b898702a0ba85f99e13452664f hides duplicate legacy needle/straight antenna objects, replaces antennae with curved geometry, replaces opaque ellipsoid wasp wings with translucent veined membranes, reframes the whole actors, and adds subtle segmented larval shading plus stronger peristalsis. These are hypotheses pending NEW still/motion evidence, not a claimed fix.

Keep V4 and all successful artifacts. No expensive 14-chapter render until real motion and still visual acceptance. If V6.7.6 fails, stop iterating camera-only changes and replace the foundational insect models/environment.

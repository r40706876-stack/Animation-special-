# V6 visual review — actual proof 40748149982 (2026-10-29 IST)

**Decision: FAIL — full 140-second V6 render is not approved.**

Reviewed the real 14-shot contact sheet and all five six-frame motion strips from the successful V6 proof artifact. This is a visual review, not an inference from green GitHub Actions.

## Observed defects

- Chapters 0–9: many nearly interchangeable medium shots; poor storytelling progression and weak shot variety. Automatic 8×8 perceptual comparison flagged 15 near-duplicate pairs.
- Insect anatomy: both models still read as simplified, rounded toy geometry. Emerald wasp lacks credible narrow waist, wing structure and fine compound-eye detail; roach shell/legs remain conspicuously schematic.
- Chapter 10: a thick foreground tree trunk obscures the burrow/roach action. Chapter 13 has a similarly obstructed ending.
- Chapter 11–12: the white egg/larva reads as a floating blob rather than a believable egg deposited on the cockroach and a growing segmented larva.
- Motion 0: nearly static (measured sampled-frame difference 0.83); 3 and 5 show wing motion but no convincing visible sting contact. Motion 10 preserves the foreground obstruction. Motion 12 shows wasp flight and a white blob but unclear larva development.
- The background is brighter and more populated than V4 but still looks like sparse, regular procedural sticks and flat foliage.

## Changes made in response

- Commit `6ccc9765` and syntax fix `5e89c38`: story-specific camera framing, clearer wide vs macro shots, foreground trunk removal along burrow camera sightlines, repositioned egg and segmented larva.
- Commit `17fdf529`: cancel superseded proof renders rather than spending runner minutes on outdated source.
- Commits `fcd6e9b` and `f395c769`: generate real motion contact strips and auto-audit each completed successful proof run.

## Next verification

- Inspect fresh proof run `40767077776` after completion, not the old stills. The previous successful source run was `40748149982`.
- If new proof still fails, continue targeted anatomy and action animation corrections; do not write `STILL_REVIEW=PASS` or `MOTION_REVIEW=PASS` without a genuine visual pass.
- A successful Blender render or a 24-frame clip decode is **not** a substitute for visual quality approval. Hindi narration listening review and 140-second final decode are later independent gates.

Evidence: [original contact sheet](contact_v6.png), [automatic audit](audit.json), [motion strip folder](motion_strips/).

## Fresh direct visual review — successful proof 40767077776

Reviewed the actual artifact `12854115550` (14 still PNGs, contact sheet and five 24-frame motion MP4s). This is the newer proof, not an assumption from green CI. **Decision remains FAIL.**

- Chapters 2, 3, 5 and 8: oversized pale cockroach dorsal plates and spherical teal wasp sections still resemble toy insects. The white crossing wings look like opaque paddles rather than transparent venated membranes.
- Chapters 0 and 1: the animals are very small relative to the frame; the forest is an open beige floor with repetitive fern ladders and sparse stick trunks.
- Chapters 3 and 5: nearly identical camera angles, no clearly readable stinger-to-body contact in sampled 24-frame motion strips.
- Chapter 10: obstruction is reduced, but the burrow reads as a grey pebble pile; a dark opening is not obvious.
- Chapters 11 and 12: egg and larva are tiny pale marks on the roach while the wasp dominates the shot. Larval development is not visually legible.
- Motion 0: movement is still hard to see in a wide shot; 3/5 have visible wing movement but no convincing sting, 10/12 still lack decisive narrative action.

### New V6.1 corrective pass, pending fresh proof

- Commit `ad666c51`: add a reusable anatomy/story pass with darkened and narrowed roach dorsal plates, a segmented jewel-wasp gaster and petiole, compound-eye facets, animated pointed translucent wings and venation, a dark burrow aperture, and a visible nine-segment larva without an obscuring hovering wasp.
- Commit `7514e1a8`: load the V6.1 pass and give chapters 3/5 distinct sting camera angles and chapters 11/12 tighter egg/larva macro framing.
- Commit `59e12b44`: strengthen the expensive full-render approval gate to fingerprint all dependent Blender scene files, preventing stale visual approvals after anatomical changes.

**Do not approve the full render based on these code changes.** The revised Blender proof still needs to complete and its actual stills and animated motion must be inspected. V4 remains untouched.

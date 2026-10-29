# V6.8 original anatomy proof: independent visual QA — FAIL (2026-10-29)

Source GitHub Actions run: https://github.com/r40706876-stack/Animation-special-/actions/runs/40905214599
Source artifact: `jewel-wasp-v68-anatomy-gate` (artifact ID 12912028379; original still, 48-frame MP4, five-frame contact strip and logs).

## Technical evidence
- Workflow clean-anatomy job: completed successfully.
- MP4 inspected with ffprobe: 270 × 480, 24/1 fps, 48 frames, 2.000 seconds.
- Still and 5-frame motion contact strip were actually opened and visually inspected.
- This proves only that the short prototype rendered and decoded; it is not an approved 140-second film.

## Visual gate: FAIL
- Insect body geometry remains toy-like and oversimplified. Wasp gaster is a smooth, brightly striped tube; cockroach pronotum and elytra look like smooth plastic pieces.
- Tall thin foreground plant stems obscure the wasp and cockroach.
- Forest floor is largely flat brown with repeated detached oval leaves, not a believable layered forest.
- Across the five motion-strip samples the insects scarcely change position. Root translation and wing motion alone do not establish a convincing approach/walk/flight action.
- Portrait framing wastes substantial vertical area above and below the subjects.
- No convincing sting, burrow, egg or larva motion was demonstrated in this isolated anatomy test.

## Corrective work
Commit `c8bd4b5f3dbf91e6418faedef8c2825cd746918c` introduces a V6.8.1 prototype: color variation, mandibular palps, roach pronotal marking/cerci, curved leaf blade meshes instead of flat ovals, background-only vegetation, closer camera angle, stronger approach/hover/leg and antenna motion, and a higher-resolution still.

**V6.8.1 is unverified until its new artifact is rendered and independently viewed.** Do not start a 14-chapter full render on the basis of CI green. Keep V4 and successful chapter artifacts unchanged.

# V6.8.1 actual visual QA — FAIL (2026-10-29)

## Evidence
- GitHub Actions proof run: https://github.com/r40706876-stack/Animation-special-/actions/runs/40915247546
- Source commit: c8bd4b5f3dbf91e6418faedef8c2825cd746918c
- Artifact: jewel-wasp-v68-anatomy-gate (GitHub artifact ID 12916439549)
- Independently inspected files: anatomy_still.png and motion_strip.png (five frames from 48-frame proof).
- Workflow technical status: success; ffmpeg decode, frame count 48, and 24fps checks passed.

## Visual rejection
- Specimens retain smooth plastic/toy-like chitin, especially brown cockroach wing covers and bright emerald wasp.
- Flat exposed grey horizon and sparse ground vegetation prevent credible layered forest.
- The two specimens occupy a narrow band in the middle of a tall 9:16 frame, leaving large empty top and bottom regions.
- Five motion-strip samples are nearly identical; gait and wing movement are hard to read at mobile size.
- No evidence yet of a convincing sting, burrow, egg, larva, or complete 14-chapter story.

## Corrective iteration
- Commit a9157745d20638f741a93a52b1ec118aaf2a43ea introduces darker/rougher cuticle, a forest-depth backdrop and tree layers, an animated close-up/two-shot/close-up camera, more obvious approach, wingbeat, and gait.
- This is **not approved** until its actual still and motion proof are downloaded and viewed. A successful workflow is technical evidence only.
- Do not start expensive 14-chapter full render based on this report. Preserve V4 and successful artifacts.

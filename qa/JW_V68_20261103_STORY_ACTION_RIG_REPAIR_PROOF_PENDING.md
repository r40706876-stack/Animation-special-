# Jewel Wasp V6.8 — targeted STORY action rig repair and bounded proof gate (2026-11-03)

## Evidence before editing
- Prior 7 real still/motion proof artifacts: [run 41503397444](https://github.com/r40706876-stack/Animation-special-/actions/runs/41503397444), independent [pixel/motion QA](JW_V68_41503397444_SEVEN_CHAPTER_PIXEL_MOTION_QA_20261103.md): **0/7 final-visual-approved**.
- Failures were principally cropped/occluded wasp anatomy and sting, indistinct antenna grasp, tiny egg placement, and a flattened larva. Burrow entry and emergence had partial action progress; their last successful proofs are **reused**, not automatically approved.
- Existing integrated 14 x 10-second, 140-second low-resolution DRAFT remains technically decodable; not final, not approved for visuals or narration.

## Source-bound work, not another isolated 2-second specimen
- [0369b1f](https://github.com/r40706876-stack/Animation-special-/commit/0369b1f49620df5cc26769e411761f41d041ca0f): in the **actual 14-chapter renderer**, chapter 12 now has a deeper dark internal cavity, a larger rounded grub cross-section, deeper organic segment grooves and keyed axial shortening/radial thickening. The camera-facing cuticle depth remains constrained by the existing geometry preflight.
- [ee1924d](https://github.com/r40706876-stack/Animation-special-/commit/ee1924def881ac212e14b9960c365ef947b35fa4): chapter 8 adds paired animated mandibles at the actual wasp jaw; chapters 3 and 5 now have distinct thoracic-leg-buckling versus head/antenna response; chapter 11 adds a transient egg moving from the ovipositor to the articulated femur-attached egg. This is **geometry/animation code**, not proof of visual realism.
- [2a25d06](https://github.com/r40706876-stack/Animation-special-/commit/2a25d065312d49b395c8f166d31f0589a8627418): source-bound per-chapter QA workflow now skips expensive Blender installation and rendering for chapters not selected in the request. The previous successful 10/13 proof artifacts remain untouched.
- [29f50cc](https://github.com/r40706876-stack/Animation-special-/commit/29f50cc358e0fc09d3c789af1ba1d9e4a39bfab3): exact story/anatomy blob-hash-bound **DRAFT ONLY** request for **3,5,8,11,12**. No 140-second/full-quality render requested.
- Compared changes since prior QA head `75c3a10`: only the story renderer, targeted workflow and proof request changed. No V4 files or unchanged chapter artifacts modified.

## Cheap structural gate
- [14-chapter geometry preflight run 41530929086](https://github.com/r40706876-stack/Animation-special-/actions/runs/41530929086) **completed successfully** on source `ee1924de`.
- [7-action geometry preflight run 41530928525](https://github.com/r40706876-stack/Animation-special-/actions/runs/41530928525) **completed successfully** on the same source; costly rendering step was explicitly skipped.
- [Selective five-chapter DRAFT proof run 41531377684](https://github.com/r40706876-stack/Animation-special-/actions/runs/41531377684) was triggered with a source-bound request. At writing, proof generation/visual review was **not yet verified**. Do not treat green preflight as a visual pass.

## Independent provisional audio signal check on existing DRAFT
- Local `ffprobe` confirms H.264 3360 frames at 24 fps, 140.000s; AAC stereo 44.1kHz. This is the **previous DRAFT**, not the newly repaired footage.
- Independently decoded audio to mono 8kHz PCM and checked each of fourteen 10s chapter windows in 0.5s intervals: all fourteen chapters had **17/20** half-second windows above -47 dBFS. Chapter RMS was approximately -25.2 to -24.3 dBFS; no chapter was silent.
- **Not** a Hindi-language, speech intelligibility, narration-to-scene synchronization, music balance or final sound-quality approval. Those require actual listening/semantic comparison, not merely audio activity.

## Required next steps
1. Wait for five source-bound chapter proof artifacts; independently inspect **actual** contact stills and 24-frame animated clips at the action windows. Check the egg transfer, mandible grasp, differentiated sting responses, and visibly rounded contracting larva. If a job fails, inspect exact logs and repair only the failing job.
2. If pixels/motion still fail, improve the relevant rig/occlusion and repeat only the failed proof chapter(s). Keep 10/13 proof baselines and unaffected complete 10-second chapter artifacts.
3. Only after visual QA passes, assemble a revised watermarked **DRAFT** and independently listen/check Hindi chapter timing. Do not trigger expensive full film without explicit final visual and audio acceptance.
4. Preserve V4, do not relax final quality gates, and do not claim completion based on green CI.

## Follow-up checkpoint: five proof artifacts and missing pre-contact evidence (2026-11-03)

- [Run 41531377684](https://github.com/r40706876-stack/Animation-special-/actions/runs/41531377684) completed with seven matrix jobs, but only **five** requested chapters (3, 5, 8, 11, 12) actually rendered and uploaded artifacts; chapters 10/13 were deliberately skipped and their older proof baselines preserved. Artifact IDs: ch3 `13182763147`, ch5 `13182199276`, ch8 `13182473484`, ch11 `13183896804`, ch12 `13184795842`. The chapter-11 job log explicitly reports `TECHNICAL_PASS__VISUAL_QA_PENDING`; all five jobs succeeded, which is **not** visual approval.
- ZIPs were downloaded, but independent image/video inspection could not proceed because the local media/container execution service returned `redis.exceptions.ConnectionError`. **No new chapter is visually approved**; do not infer improvement from logs, artifact sizes or preflight.
- [Workflow patch fed4dfc](https://github.com/r40706876-stack/Animation-special-/commit/fed4dfc1f9440da2f6671af39eb90e56229a9d89) fixes a concrete evidence gap: chapter 11 previously sampled only frames 145-168, missing the first egg transfer at frames 120-143. Future *source-bound DRAFT-only* chapter-11 proof requests will retain the old 24-frame deposition clip and add a separate 24-frame pre-contact clip plus frame-120 still. Contact-sheet tiling now accommodates three stills. This workflow edit was committed and re-read, but **not execution-tested or visually verified**; no expensive render was triggered.
- Next: when media inspection works, inspect all five actual contact sheets and both chapter-11 motion windows, compare against previous 0/7 approved baseline, repair only failing rigs/shots, and trigger a new bounded proof request only if needed. Keep V4, prior successful full-length chapters, existing 140s DRAFT and final quality gates untouched. Hindi narration listening/synchronization and final 140s film remain unapproved.

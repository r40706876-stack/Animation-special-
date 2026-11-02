# Jewel Wasp V6.8 integrated DRAFT — independent partial visual QA (2026-11-02)

Status: **NOT FINAL / NOT VISUALLY APPROVED**. Evidence from GitHub Actions run [41402745255](https://github.com/r40706876-stack/Animation-special-/actions/runs/41402745255). The original V4 and baseline run 41245294072 must remain untouched.

## Independently inspected low-resolution chapter artifacts

- Chapter 10: artifact 13136695680, `chapter_10.mp4`. Local FFmpeg full decode succeeds; 216x384, 24fps, 240 frames. Contact-sheet inspection at 1/3/5/7/9 seconds shows cockroach approaching and partly disappearing into a circular burrow. **Visual FAIL / revision needed**: cockroach is cut off at left during approach; entry is not consistently clear, and scene reads as a simple flat round pit rather than convincing natural burrow. Do not mark burrow action approved.
- Chapter 12: artifact 13135198798, `chapter_12.mp4`. Local FFmpeg full decode succeeds; 216x384, 24fps, 240 frames. Contact-sheet inspection at 1/3/5/7/9 seconds shows a pale flat oval growing in a cross-section. **Visual FAIL / revision needed**: larva is not anatomically recognizable; no convincing feeding or body articulation; cross-section foreground obscures the action. Do not mark larva action approved.
- Earlier reviewed chapters 3, 5 and 8: technical decode passed but visual concerns remain: toy-like wasp, repetitive composition in 3/5, and antenna-grasp action insufficiently legible in 8. These are not visually approved.

- Chapter 11: artifact 13141255983, `chapter_11.mp4`. Independently downloaded and decoded all 240 frames (216x384, 24fps); reviewed frames at 1/3/5/7/9 seconds and an enlarged 7-second frame. **Visual FAIL / revision needed**: an ivory egg becomes visible hanging near the cockroach's near-side leg by 7 seconds, but its deposition is not clearly legible and the blue wasp's body resembles an unarticulated slug above the cockroach. The camera crops the wasp for much of the sequence. World-space femur contact assertions are NOT a substitute for readable oviposition or anatomically believable motion. Preserve this artifact for the first integrated DRAFT; revise only after assembly and targeted preview.

## Workflow state at this review

- 14/14 geometry preflights passed. Changed chapters 3, 5, 8, 10, 12 have completed jobs and downloadable artifacts.
- Chapter 11 subsequently completed with artifact 13141255983 and the independent visual failure above. Chapter 13 remains in progress as of the later check; its in-progress job log returned GitHub 404 BlobNotFound, so no frame-progress claim is made.
- Baseline run 41245294072 still has all 14 older chapter artifacts and its provisional 140-second DRAFT. Reuse only unchanged chapters 0, 1, 2, 4, 6, 7, 9 as specified by the pinned request.
- Integrated 140-second assembly is blocked until chapter 13 finishes; do not initiate another expensive full render while it runs.
- Hindi narration is provisional, not independently listened to or sync-approved. 3360-frame integrated technical decode and contact-sheet QA remain pending.

## Next safe production gates

1. Wait for chapter 13, then inspect its actual still contact sheet and moving emergence sequence; Chapter 11 egg-placement stills have now been inspected and failed visual approval.
2. Let the existing workflow assemble the watermarked 140-second DRAFT using seven reused and seven changed chapters; independently verify 3360 frames at 24fps, 140 seconds, full decode, audio presence.
3. Independently listen to Hindi narration, compare its timing to all 14 chapters, and inspect a whole-film contact sheet.
4. Batch-fix only visually failed chapters (priority: larva, burrow, antenna grasp, composition); use targeted cheap proof renders before any expensive final render. Keep strict final quality gates closed.

**Do not infer visual success from green CI or preflight geometry.**

# Jewel Wasp V6.8 integrated DRAFT — independent partial visual QA (2026-11-02)

Status: **NOT FINAL / NOT VISUALLY APPROVED**. Evidence from GitHub Actions run [41402745255](https://github.com/r40706876-stack/Animation-special-/actions/runs/41402745255). The original V4 and baseline run 41245294072 must remain untouched.

## Independently inspected low-resolution chapter artifacts

- Chapter 10: artifact 13136695680, `chapter_10.mp4`. Local FFmpeg full decode succeeds; 216x384, 24fps, 240 frames. Contact-sheet inspection at 1/3/5/7/9 seconds shows cockroach approaching and partly disappearing into a circular burrow. **Visual FAIL / revision needed**: cockroach is cut off at left during approach; entry is not consistently clear, and scene reads as a simple flat round pit rather than convincing natural burrow. Do not mark burrow action approved.
- Chapter 12: artifact 13135198798, `chapter_12.mp4`. Local FFmpeg full decode succeeds; 216x384, 24fps, 240 frames. Contact-sheet inspection at 1/3/5/7/9 seconds shows a pale flat oval growing in a cross-section. **Visual FAIL / revision needed**: larva is not anatomically recognizable; no convincing feeding or body articulation; cross-section foreground obscures the action. Do not mark larva action approved.
- Earlier reviewed chapters 3, 5 and 8: technical decode passed but visual concerns remain: toy-like wasp, repetitive composition in 3/5, and antenna-grasp action insufficiently legible in 8. These are not visually approved.

## Workflow state at this review

- 14/14 geometry preflights passed. Changed chapters 3, 5, 8, 10, 12 have completed jobs and downloadable artifacts.
- Changed chapters 11 and 13 were still running; no chapter artifacts at the time of review. Their in-progress job logs returned GitHub 404 BlobNotFound, so no frame-progress claim is made.
- Baseline run 41245294072 still has all 14 older chapter artifacts and its provisional 140-second DRAFT. Reuse only unchanged chapters 0, 1, 2, 4, 6, 7, 9 as specified by the pinned request.
- Integrated 140-second assembly is blocked until chapters 11 and 13 finish; do not initiate another expensive full render while they run.
- Hindi narration is provisional, not independently listened to or sync-approved. 3360-frame integrated technical decode and contact-sheet QA remain pending.

## Next safe production gates

1. Wait for chapters 11 and 13; inspect both still contact sheets and moving sequences, with special attention to egg placement and emergence.
2. Let the existing workflow assemble the watermarked 140-second DRAFT using seven reused and seven changed chapters; independently verify 3360 frames at 24fps, 140 seconds, full decode, audio presence.
3. Independently listen to Hindi narration, compare its timing to all 14 chapters, and inspect a whole-film contact sheet.
4. Batch-fix only visually failed chapters (priority: larva, burrow, antenna grasp, composition); use targeted cheap proof renders before any expensive final render. Keep strict final quality gates closed.

**Do not infer visual success from green CI or preflight geometry.**

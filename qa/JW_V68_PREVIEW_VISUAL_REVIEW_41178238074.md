# Jewel Wasp V6.8 — independent preview review, 2026-10-31

## Evidence inspected, not inferred from CI
- [Run 41178238074](https://github.com/r40706876-stack/Animation-special-/actions/runs/41178238074), completed successfully; downloaded artifact **13034839063** (9,111,799 bytes), `jewel-wasp-v68-story-draft-preview`.
- Its `DRAFT_QA.json` identifies source commit `04ccb3474ab7898b92e139c18739c137bf6d578f`, `visual_approved=false`, `final_film=false`.
- Opened the **actual 14-chapter contact sheet** and **five actual 4-frame motion strips** for chapters 3, 5, 10, 11, 12. Each source proof MP4 contains 24 frames at 24fps and 270x480 resolution.
- The run is technically green but **VISUAL QA FAILED**. Do not approve a final render.

## What the images show
1. **Chapters 0–13:** essentially the same forest-floor backdrop, with near-identical insect presentation; subjects often crop at portrait boundaries. A sequence of differently named chapters is not yet a coherent film.
2. **Sting 3 and 5:** the wasp's body overlaps the cockroach, but the sting tip, insertion, hold, withdrawal and cockroach reaction are **not visually readable** in the actual strips. A numerical contact assertion cannot replace the image.
3. **Burrow 10:** the cockroach looks rotated over a dark hole, rather than visibly walking down a plausible tunnel. The mouth, soil wall and body-depth relationship remain confusing.
4. **Egg 11:** the wasp dominates the view, the egg placement is not independently identifiable in the strip.
5. **Larva 12:** the pale larva resembles a flat bright patch on the cockroach, not a clearly articulated moving larva.
6. **Hindi audio:** the previous 140-second DRAFT had a ~3.66-second silence gap. New audio code is not yet independently listened to or synchronized. No approval.

## Batch corrective changes made after inspection
- `4b45af09`: tighter macro framing for sting/egg/larva, flank offsets for egg and larva, retain full-size cockroach while pitching into burrow, numerical projection preflight for action focal points. **Code change only, not a passed visual proof.**
- `fa0e74de`: still proof frames aligned to actions (3/5=145, 10=195, 11=205, 12=180); motion starts (1=90, 3/5=118, 8=118, 10=168, 11=152, 12=112); added flight and guidance motion evidence, labeled contact sheet and visible DRAFT watermark on proof clips. **Workflow change only, not a passed visual proof.**
- Both changes trigger the existing preview workflow; it has a cancel-in-progress concurrency group. Avoid another source/workflow push until the newest proof finishes and its actual images are examined.

## Required next gate
1. Find the latest preview run for `fa0e74de`. Inspect **preflight errors and actual artifact**. If numerical projection assertions fail, correct the framing before any expensive render.
2. Open the new labeled 14-shot contact sheet AND seven 1-second clips. Compare actual sting, burrow, egg, larva, flight and walk against the above failures.
3. If still unclear, change **only failing scenes** and repeat low-cost proof. Preserve V4 and successful artifacts.
4. Do not authorize a final 14x240-frame render until distinct story actions, biological legibility and Hindi narration have separately passed.
5. Final independent gates: 14x240=3360 frames, 24fps, exactly 140 seconds, full ffmpeg decode, intelligible synchronized Hindi speech, visual quality, playable MP4 and contact sheet. No green-CI shortcut.

**Status: 140-second low-res DRAFT exists, but final film not complete or approved.**

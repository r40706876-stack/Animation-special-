# V6.8 Chapter 13 emergence — independently inspected proof (2026-11-01)

Source: [Run 41270471607](https://github.com/r40706876-stack/Animation-special-/actions/runs/41270471607), artifact `jewel-wasp-v68-ch13-finale-draft-proof` (13069058637), source commit `14c3255443fd7ff31949292fd04bd31f8a3af6c2`.

**Technical PASS / Visual FAIL / Final gate CLOSED.**

- Downloaded and inspected the actual 1-second DRAFT MP4 and its four-frame strip, plus chapter 13 stills at frames 45 and 180.
- FFprobe: 270x480, 24 fps, 24 frames, 1.000 seconds. DRAFT watermark is visible. The job's QA.json explicitly says `visual_approved=false`.
- In the 25-48 motion strip the wasp stays nearly in the same on-screen position and the opening is not shown as an unambiguous emergence. At frame 45 the insect is already above the rim. At frame 180 it is again hovering near the opening; no convincing rise/departure sequence is established by this evidence.
- The source camera followed the wasp from frame 1 to 240, canceling much of the apparent vertical motion relative to the burrow. The wasp started only 0.24 world units below the surface, so it was already partly visible.
- Targeted source correction [1180e1b3](https://github.com/r40706876-stack/Animation-special-/commit/1180e1b31c7222aeed8adc845a0b9f62bcddf389) moves the initial root deeper and holds the camera on the burrow through frame 120 before following departure. This is **unverified** until new stills and motion are viewed.
- Targeted proof workflow correction [72f73432](https://github.com/r40706876-stack/Animation-special-/commit/72f73432998c508f4157535c1c67f667e5a091a1) requests four stills (25,90,180,230) and separate 24-frame rise/departure proofs (starts 80,175), not an expensive 140-second rerender.
- [New targeted proof run 41274274206](https://github.com/r40706876-stack/Animation-special-/actions/runs/41274274206) queued at time of this report. Do not mark visual approval based on a successful job.

V4 source and the earlier 140-second DRAFT are untouched. Other failed action scenes (sting, burrow entry, egg, larva) and audible Hindi synchronization still require independent QA before final rendering.

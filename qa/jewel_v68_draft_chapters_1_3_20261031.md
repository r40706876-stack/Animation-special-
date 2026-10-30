# Jewel Wasp V6.8 — independent DRAFT chapter artifact QA (2026-10-31)

Scope: GitHub Actions rough-cut run [41110464863](https://github.com/r40706876-stack/Animation-special-/actions/runs/41110464863). Downloaded artifact ZIPs `jewel-v68-draft-chapter-1` (ID 13008769806) and `jewel-v68-draft-chapter-3` (ID 13011155402) and independently inspected their extracted MP4s. These are only two of fourteen chapters, not a completed film.

| Chapter | Frame count | FPS | Duration | Resolution | Full ffmpeg decode | Visual verdict |
| --- | ---: | ---: | ---: | --- | --- | --- |
| 1 — pursuit | 240 | 24 | 10.000 s | 162x288 | PASS | DRAFT ONLY: actor tiny in opening, limited legibility of pursuit; visual realism not final |
| 3 — thoracic sting | 240 | 24 | 10.000 s | 162x288 | PASS | DRAFT ONLY: actor and roach visible but actual sting-to-thorax contact is not convincingly demonstrated |

Viewed contact frames at 1, 4, and 8 seconds for both chapters. Measured substantial decoded frame changes between beginning and later sampled frames; these are moving videos, not static stills. Forest appears sparse and synthetic, ground is overly smooth, and insect silhouettes/materials remain stylized. The chapter MP4s are silent, as designed: the separate assembly stage is responsible for Hindi narration and a visible DRAFT watermark. Neither audio nor watermark has been verified in an assembled output. Technical chapter decode does not imply final visual approval.

At observation time: chapter jobs 1 and 3 succeeded, chapters 0/2/4/5 running, remaining chapters queued. No failed jobs and no assembled 140-second artifact observed. Do not restart successful chapters or modify V4. Next: await remaining chapters, verify 14x240 frames, review actual 14-chapter contact and moving proofs, check audio intelligibility and synchronization, and keep final visual gate closed.

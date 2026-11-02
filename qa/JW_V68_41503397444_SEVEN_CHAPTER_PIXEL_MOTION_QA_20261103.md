# Jewel Wasp V6.8 — independent seven-chapter pixel + motion QA (2026-11-03 02:16 IST)

## Provenance and technical verification
- GitHub Actions run: https://github.com/r40706876-stack/Animation-special-/actions/runs/41503397444
- Exact renderer source commit: `2ba376aa2056d68d2c6a6aaf9a67d03b09720ee8`; story SHA-256 in each QA.json: `dea6e9f23942ebb4bdaeb205d283cda75354ae5570dc4c3ad82106336fb72653`.
- Independently downloaded and extracted all seven actual GitHub artifact ZIPs: ch3 `13170758514`, ch5 `13170343848`, ch8 `13170277681`, ch10 `13172016898`, ch11 `13171594003`, ch12 `13172236836`, ch13 `13173395939`.
- Viewed the actual 7 chapter still contact sheets, individual frame stills, and all 7 motion strips, not just workflow green checks.
- Independently ran `ffprobe -count_frames` and complete `ffmpeg -v error -xerror -i ... -f null -` on **each** MP4: all seven are **24 frames, 24 fps, exactly 1.000 s, 270x480 H.264, complete decode pass**.
- Every artifact QA.json explicitly states `draft_only=true`, `visual_approved=false`, `final_film=false`, `hindi_listen_verified=false`, `V4_preserved=true`. These are 1-second action proofs, **not** seven replacement 10-second chapters.

## Independent visual findings — 0/7 approved for final film
| Chapter | What the actual pixels/motion show | Visual decision |
|---|---|---|
| 3 thoracic sting | Overlapping, partly cropped insects; a narrow appendage reaches toward host but an unmistakable anatomical sting/penetration and response cannot be read. Camera holds nearly the same composition as chapter 5. | FAIL |
| 5 head ganglion sting | **New missing motion proof now exists**, but still largely duplicates ch3: large turquoise body, translucent wings, no clearly localized head-ganglion contact or convincing reaction. | FAIL |
| 8 antenna guidance | Wasp head and roach visible, but actual antenna-to-mandible grasp is tiny/ambiguous. The 24-frame sequence looks like a generic near-contact movement. | FAIL |
| 10 burrow entry | Real modeled mouth and progressive roach descent are now readable in four sampled motion frames; **partial improvement**. However host appears to sink into a circular pit, rather than an anatomically convincing head-first guided entry. | PARTIAL, NOT PASS |
| 11 egg placement | A white oval is visible on a near-side leg, a positive improvement over an invisible egg. However the giant turquoise wasp body obscures the ovipositor; 24 frames do not show a legible egg being deposited. | PARTIAL OBJECT VISIBILITY, ACTION FAIL |
| 12 larval development | Cutaway and light-colored ridged object are visible, but larva still looks like a flat scalloped strip against the abdomen. Four motion samples show no convincing rounded grub contraction or feeding action. | FAIL |
| 13 emergence | A wasp is visible crossing from the pit and flying away, an improvement over the previous proof window. However the tiny schematic model and sudden movement do not convincingly show a complete body passing through a narrow opening and transitioning to flight. | PARTIAL, NOT PASS |

## Production decision
**No new expensive full render or repeat of the same 2-second anatomy specimen.** Technical QA is green, visual QA remains **0/7 approved**. Stop treating camera keyframes alone as the principal fix: the recurring failure is stylized insect/larva silhouette, occlusion, insufficient articulation and action staging.

Next economical work, in order:
1. **Model/rig + shot staging correction** on the *actual 14-chapter story renderer*, not the isolated specimen. Prioritize recognizable wasp head/mandibles, jointed legs, slim petiole/abdomen, visible ovipositor/sting, roach antenna contact, three-dimensional grub; avoid oversized smooth turquoise ellipsoids and close-up crops. Retain V6.8 assets and V4.
2. For ch3/5 make thoracic vs head-ganglion sting visually different (different camera side, target, host response). Ch8 must include a visible antenna held in mandibles. Ch11 show before-contact / ovipositor-contact / attached egg in one coherent shot. Ch12 give the grub depth, soft segmented volume and an obvious contraction; do not enlarge a flat strip. Ch10/13 use a coherent rim crossing with legs/body and continuity.
3. Preflight actual changed chapters, render only bounded source-bound DRAFT stills and 24-frame clips; inspect actual pixels and motion before re-rendering full 10-second segments. Reuse existing complete chapter artifacts when unaffected.
4. After *visual* approval, integrate a revised watermarked 140-second rough cut. Independently listen to Hindi narration and check scene synchronization; audio codec presence is not speech verification.
5. Only after technical **and** visual approval attempt high-quality final assembly and independently verify 3360 frames at 24fps, 140.000 s, full ffmpeg decode, narration and real visual quality.

The earlier 14x10-second low-res integrated rough cut remains a **DRAFT**, not final. No final quality gates relaxed; no V4 files modified; no evidence of an approved final film.

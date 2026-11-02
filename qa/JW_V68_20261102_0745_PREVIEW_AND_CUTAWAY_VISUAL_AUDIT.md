# Jewel Wasp V6.8 — independent preview and larva candidate visual audit (2026-11-02 IST)

**Disposition: DRAFT ONLY; FINAL VISUAL FAIL.** Do not confuse successful CI, contact checks, or H.264 decoding with approved insect realism or storytelling.

## Evidence inspected directly
- 14-chapter preview run [41359048481](https://github.com/r40706876-stack/Animation-special-/actions/runs/41359048481), source `cd5ede0740fa4330cf09863a92a9ecfd024fd21c`, completed SUCCESS at 2026-11-02 01:14 UTC; artifact `13108914899` (62 files). Downloaded and opened the **actual 14-still DRAFT contact sheet** and **eight 4-frame action strips**; inspected 1-second motion proof outputs. All 14 labeled stills and eight 24-frame clips are present; technical success is not visual approval.
- Chapter-12 cutaway candidate run [41368963939](https://github.com/r40706876-stack/Animation-special-/actions/runs/41368963939), source `9fb2810aea2f82e005f92d13281b9343c4cacc8c`, completed SUCCESS at 2026-11-02 00:59 UTC; artifact `13109176219` (10 files). Downloaded and opened both DRAFT stills, the combined contact sheet, and the four-frame motion strip. Candidate preflight reported `JW_LARVA_SCHEMATIC_CUTAWAY 226` and `JW_INTERNAL_LARVA_CUTAWAY_CONTACT 0.1685 0.262 226`; this is geometric evidence only.
- Older 140-second DRAFT run [41245294072](https://github.com/r40706876-stack/Animation-special-/actions/runs/41245294072), artifact `13063132162`, is already a complete **older-source** 14x10-second low-resolution rough cut: 3360 frames, 24fps, 140.0s, H.264 + AAC. Audio signal is present in all 14 chapter windows; no Hindi intelligibility or action-sync listening pass is claimed. Its source commit is `e9817cd21f4dc67f60d1517db28751e38102bb9b`, NOT the new V6.8 renderer.

## Actual pixel/motion review (not inferred from source)
- Chapters 0–2 and 7–9: visually repetitive forest staging and insect distances; the roach/wasp relationship is not consistently readable as a changing story.
- Chapters 3 and 5: wasp approaches roach, but the *needle entering the relevant anatomical site* is not legible in the four-frame motion strips; do not pass sting action.
- Chapters 4 and 6: bright orange schematic dots appear outside the roach; they do not independently communicate internal neural action.
- Chapter 8: antenna-guided walking is not clearly demonstrated by the proof; two nearby insects alone are insufficient.
- Chapter 10: circular burrow is visible and roach shifts toward its mouth, but continuous full-body entry cannot be certified from a one-second strip.
- Chapter 11: tiny white egg is visible near a leg in the still; the large wasp blocks the laying interaction in the motion strip. Geometry contact of 0.0252 is not visual proof of deposition.
- Chapter 12, main renderer: white, flat, clam-like larva still appears on the outside of the host; FAIL.
- Chapter 12, new cutaway candidate: the supposed translucent flank is not visually readable as a cutaway. A pale, flattened oval still appears as an exterior shell in both stills and the motion strip; FAIL. Do **not** merge the candidate merely because its preflight passes.
- Chapter 13: the wasp is visible emerging from the burrow across the four-frame strip, an improvement in action readability, but anatomy and full 10-second continuity remain unapproved.

## Production decision: stop the isolated 1-second larva loop
1. Preserve V4, all successful chapter artifacts, the existing 140-second DRAFT, and strict final gates.
2. Do **not** trigger another full 14x240-frame render merely because 14 stills/8 strips passed CI. The 140-second low-cost rough-cut milestone exists at older source, not latest source. Do not call latest-source 140-second rough cut complete.
3. Next work should be a **single story-level visual correction pass**: staging/shot continuity, anatomically readable sting, antenna contact, complete burrow entry, egg deposition, and a **distinct explanatory internal-larva shot** (rather than endless rescaling of the same exterior white oval). Use low-res previews and only re-render changed chapters, reusing exact-source successes.
4. Maintain chapter-aligned Hindi narration; independently listen and check timing before any final approval.
5. Only after actual revised stills AND animated motion pass, assemble 14x10 seconds and independently verify 3360 frames/24fps/140 seconds, complete decode, playable MP4, audible intelligible synced Hindi, and a human-viewed contact sheet.

**Gates:** `rough_cut_older_source_technical_pass=true`; `latest_source_rough_cut_complete=false`; `candidate_cutaway_visual_pass=false`; `story_preview_visual_pass=false`; `final_render_authorized=false`; `hindi_listen_verified=false`.

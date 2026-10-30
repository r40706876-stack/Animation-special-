# V6.8.25 actual artifact independent review — 2026-10-30

Source run: https://github.com/r40706876-stack/Animation-special-/actions/runs/41093268380
Artifact: jewel-wasp-v68-anatomy-gate, ID 12997368719.

## Technical short-proof checks
- Downloaded the actual ZIP and extracted specimen, wasp, cockroach, touchdown stills, motion strips and both MP4s.
- Independently decoded both clips with ffmpeg -v error -xerror (no errors).
- Wide specimen motion: 270x480, 48 frames, 24fps (2s).
- Wasp macro motion: 270x480, 24 frames, 24fps (1s).
- Touchdown geometry reports PASS with 3 tarsi within 12mm of soil; gaps in meters: [0.0883, 0.0062, 0.0047, -0.0040, 0.0389, 0.0642].
- Geometry PASS is not a natural-motion or visual-quality approval.

## Actual still and animated visual QA: FAIL for final
- Reviewed real wide motion strip, wasp macro motion strip and frame-48 touchdown still, not just CI status.
- Wings now have more visible venation and leaf litter is less uniform, but the wasp still resembles a metallic toy: rounded thorax/head, long straight thin legs, stiff wings.
- Cockroach is a flat plated shape with simplified legs; the touchdown still crops much of its body at the right edge.
- Forest has obvious repeated leaf polygons and cylindrical trunks, little natural photographic depth; ground is still broad smooth grey.
- Motion strips show short approach/landing only. No evidence of convincing first/second sting, antenna-guided walk, burrow entry, egg placement, larval growth or 14-shot continuity.
- The 140-second film remains unverified.

## Production pivot implemented
- Integrated the V6.8.25 scene builder and exact ANATOMY_WASP_ROOT/ANATOMY_ROACH_ROOT into a separate 14-chapter **DRAFT** renderer: src/jewel_wasp_v68_story_draft.py.
- Added a preview workflow for 14 stills plus 1s action clips for chapters 3,5,10,12: .github/workflows/jewel_wasp_v68_story_draft.yml.
- Added a separate **preview-gated** 14 x 240-frame rough-cut pipeline with per-chapter caching, Hindi narration attempt and persistent DRAFT watermark: .github/workflows/jewel_wasp_v68_draft_140s.yml.
- The full DRAFT job must NOT run until the actual new chapter contact sheet AND short motion clips are independently reviewed. Review marker is bound to both source blob hashes.
- V4, old full renderer, old proofs and successful artifacts remain unchanged. This rough-cut path is not final visual approval.

## Next run
- Inspect latest 14-chapter preview run and its actual artifact. Diagnose failed steps before retrying.
- If stills and action clips are usable for a rough cut, commit the source-bound DRAFT-only review marker and let the 140-second draft render run. Otherwise fix the specific chapter/action first.
- Preserve strict final visual, Hindi listening and 3360-frame technical gates after rough cut.

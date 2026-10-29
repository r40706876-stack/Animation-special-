# V6.8.5 independently viewed proof — visual FAIL (2026-10-30 IST)

- Source commit: `55373627e7736db6a6f09041d3cd381234930bc9`.
- Actual GitHub Actions proof run: https://github.com/r40706876-stack/Animation-special-/actions/runs/40952603894
- Artifact: `jewel-wasp-v68-anatomy-gate` (artifact ID 12934525656), downloaded and inspected.
- Technical QA: **PASS**. Decoded 48 H.264 frames, 270x480, 24 fps, exactly 2.000 seconds. Full ffmpeg decode returned no errors.
- Visual QA: **FAIL**. Viewed actual `anatomy_still.png` and five-frame `motion_strip.png`, not just workflow status. Ground-edge black band is fixed; however, the roach is still an overly pale toy-like extruded shell, the wasp and roach are small in the portrait frame, the ground occupies too much space, the forest is sparse, and most visible motion is translation with limited leg/wing anatomical realism. No convincing sting/oviposition is shown; this is an anatomy-only proof.
- Follow-up code commit: `d2b468902e4d91c148948cee75cdacd5b93fc227` (V6.8.6): darkened roach cuticle, added dorsal elytral vein lines, low foreground leaf litter and stones, and animated a wasp-closeup / two-subject / roach-closeup proof camera. These are **unverified code changes** until a new actual proof artifact is rendered, decoded, and visually inspected.
- **Gate remains CLOSED**. Do not start the expensive 14-chapter full render on the basis of technical success. Keep V4 and successful chapter artifacts untouched. The eventual 140s / 3360-frame film, Hindi audio and final MP4 are not verified.

## Full-film integration blocker
The current `.github/workflows/jewel_wasp_v6_full.yml` still executes `src/jewel_wasp_v6_full.py` using the V6/V6.7 source bundle, **not** `src/jewel_wasp_v68_anatomy_proof.py`. A clean-room V6.8 anatomy PASS by itself would **not** upgrade any of the 14 full-film chapters. Before authorizing full render, integrate approved V6.8 rigs/materials/forest and chapter-specific motion into the actual full-film scene, generate representative chapter proofs from that exact integrated source, and re-review. Existing V6 approval fingerprint protects the older source but is not evidence of V6.8 integration.

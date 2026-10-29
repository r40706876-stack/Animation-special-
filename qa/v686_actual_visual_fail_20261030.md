# V6.8.6 independent visual QA — 2026-10-30 (IST)

- Source commit: `d2b468902e4d91c148948cee75cdacd5b93fc227`
- Actual GitHub Actions proof: https://github.com/r40706876-stack/Animation-special-/actions/runs/40961024904
- Downloaded artifact ID: `12938155050`, `jewel-wasp-v68-anatomy-gate`.
- Independently decoded `anatomy_motion.mp4` using FFmpeg `-xerror`: **PASS**. 270×480, 48 frames, 24 fps, exact 2.000 seconds.
- Independently opened and viewed `anatomy_still.png` and the five-frame `motion_strip.png`. **Visual QA: FAIL**. Technical CI success does not imply visual approval.

## Observed problems
1. Cockroach has an overly boxy, slab-like elytron and oversized rounded pronotum; it reads as a toy instead of an organic insect.
2. Both insects have simplified, rigid limbs; the original motion keyframes rotate leg pieces about their own mesh centers, rather than articulating a connected limb at the hip.
3. The background has a large featureless soil expanse and unnaturally heavy upright trunk cylinders. Camera moves leave substantial unused portrait area.
4. Approach and wing motion are visible, but walking, sting, burrow, oviposition, egg and larval motion are **not** established by this isolated 2-second specimen test.
5. The current 14-chapter full-film workflow still runs the older V6/V6.7 scene bundle. **No V6.8 clean-room anatomy is integrated into the actual full renderer.**

## Next gate
- Follow-up source correction: `a07570f6cb266de4d47e4400d1d2ae0bf4c1f06c` (V6.8.7). This changes elytron width profile, pronotum proportions, leg-parent pivots, and portrait camera composition. These are **unverified changes** until the next proof artifact is rendered, decoded, and visually reviewed.
- Require independent still AND animated visual approval of the corrected rig. Then integrate the approved components into the real full-film scene, and render representative chapters from **that same source** before expensive 14-chapter rendering.
- **Full film gate CLOSED.** Preserve V4 and successful prior artifacts. No claim of a 140-second / 3360-frame, intelligible Hindi-narrated final film.

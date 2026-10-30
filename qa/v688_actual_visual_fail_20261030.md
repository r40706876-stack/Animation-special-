# V6.8.8 independently viewed visual QA — 2026-10-30 (IST)

- Source commit: `1658573f38dbc58df80d798d412b5afff71d0c03`.
- GitHub Actions run: https://github.com/r40706876-stack/Animation-special-/actions/runs/40975322103
- Downloaded artifact: `12943396486`, `jewel-wasp-v68-anatomy-gate`, 1,079,627 compressed bytes.
- Inspected actual `anatomy_still.png` (540x960), `motion_strip.png` (five samples), and `anatomy_motion.mp4`.
- Independently checked MP4 with FFprobe: 270x480 H.264, 48 frames, 24fps, exactly 2.000 seconds; full FFmpeg decode returned no errors.
- **Technical proof PASS; independent visual QA FAIL.**

## Observed issues (actual frames, not an assumed outcome)
1. Both insects are now in frame, and the earlier obvious black bottom strip is absent; however, the insects are too small for convincing anatomical inspection in a 9:16 frame.
2. The cockroach is visibly assembled from smooth, intersecting oval segments. The dorsal wing covers and thorax look like a toy rather than an articulated insect.
3. Wasp wings look whitish, legs are rigid-looking, and the body material lacks convincing organic microstructure.
4. The ground dominates the frame as a smooth, nearly featureless brown stage. The trees are dark cylinders near the upper edge, and foliage is mostly flat litter.
5. Five sampled frames show a visible approach, but not enough independently legible wing, walking, sting, burrow, egg or larva motion to approve a 14-chapter film.
6. The full 14-chapter renderer `src/jewel_wasp_v6_full.py` still executes the older V6 scene and V6.7 pass. It **does not load** the V6.8 clean-room anatomy. A passing V6.8 proof therefore cannot approve the full renderer.

## Next evidence gate
- V6.8.9 code commit `3d8a8c6` replaces intersecting roach sternite ovals with a continuous cuticle mesh, adjusts wing/chitin materials and adds standing understory ferns.
- Workflow commit `6eab5ec` adds a separate roach macro still to the regular two-subject still and 48-frame animated proof. These changes are **unverified** until the new artifact is downloaded and viewed.
- New workflow: https://github.com/r40706876-stack/Animation-special-/actions/runs/40981670337
- Do not trigger expensive 14-chapter full rendering yet. First inspect both real stills and animation; then integrate approved anatomy into actual full-render scene and review representative story-action proofs (sting, burrow, egg, larva, flight) before release.
- Preserve V4, successful artifacts, and existing approval gates. Green CI is never a visual-quality pass.

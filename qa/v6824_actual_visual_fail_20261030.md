# V6.8.24 independent actual-artifact review — 2026-10-30

Source run: https://github.com/r40706876-stack/Animation-special-/actions/runs/41084673048
Artifact: jewel-wasp-v68-anatomy-gate (ID 12993973254); ZIP SHA256 b9e4bad5bf0722e1f10f24a0287d6e7d61dcdc75c038e38fa5016d19bc0afd00.

## Technical evidence (short proof only)
- Downloaded the actual ZIP, extracted 14 proof files and independently decoded both MP4s with ffmpeg -v error -xerror.
- Main proof: 270x480 H.264, 48 frames at 24 fps, 2.000 seconds.
- Macro proof: 270x480 H.264, 24 frames at 24 fps, 1.000 second.
- GitHub job clean-anatomy concluded success; geometry preflight passed. Frame-48 named tarsus-to-ground gaps (m): 0.0883, 0.0062, 0.0047, -0.0040, 0.0389, 0.0642. Three of six are within 12mm; worst penetration 4mm. Numeric PASS is NOT locomotion quality approval.

## Actual visual inspection — FAIL
- Reviewed actual specimen, cockroach and wasp macro stills, frame-48 touchdown still, and BOTH animated contact strips from the downloaded artifact.
- The prior black band at the bottom of touchdown still is improved/absent; the frame-48 shot now includes the wasp and most of the roach, but roach right edge remains cropped.
- Wasp still reads as a smooth metallic teal toy: spherical thorax/head, stick-like amber legs and glassy featureless wings. Roach has a thin detached-looking dorsal shell and plate-like pronotum.
- Forest still has uniform grey soil, repeated paper-shaped leaves and pole-like trunks; little believable depth or decaying organic ground texture.
- Wide 48-frame motion is near-static at small subject scale; macro proof shows an approach/landing but does not demonstrate natural flight-to-walk transition or a convincing sting.
- No visible/verified burrow, egg deposition or larval animation. No 14 distinct chapters or 140-second final film verified.

## Follow-up change: V6.8.25
Commit: https://github.com/r40706876-stack/Animation-special-/commit/326777bd4448c793882c2540071f8d512d092af6
- Added fine wing marginal and cross venation to reduce featureless glass appearance.
- Diversified forest litter materials to include damp brown, russet and olive decaying leaves instead of uniform yellow paper-like chips.
- This is a **candidate visual improvement**, not a visual PASS. Await its fresh workflow render and inspect actual stills and short animated proofs before any expensive full render.
- Do not modify V4 or discard successful chapter artifacts.

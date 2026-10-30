# V6.8.21 actual-artifact QA — 2026-10-30

Source: [GitHub Actions run 41057769325](https://github.com/r40706876-stack/Animation-special-/actions/runs/41057769325), commit `7bdd636`, artifact ID `12981631784` (3,043,777 ZIP bytes).

## Independent evidence
Downloaded and extracted the actual artifact. Opened `anatomy_still.png`, `roach_macro.png`, `wasp_macro.png`, `motion_strip.png`, and `wasp_macro_motion_strip.png`. Independently decoded both MP4s with `ffmpeg -v error -xerror -i ... -f null -` and counted frames with `ffprobe`: 48 frames at 24 fps, 2.000 seconds; and 24 frames at 24 fps, 1.000 second. These two short video decodes PASS; they do not prove a full film.

## Confirmed failure
The `Render actual frame-48 touchdown macro` step failed. The archived `touchdown.log` prints final six tarsus-to-soil gaps (metres): `[0.0303, -0.0433, -0.0533, -0.0620, -0.0191, 0.0062]`. Three tarsi penetrated the soil by over 4 cm, one by 6.2 cm. The geometry assertion stopped Blender before it rendered `wasp_touchdown_frame48.png`. The job is correctly marked **FAIL**, despite successful short MP4 decodes and uploaded artifacts. Do not rerun unchanged failed jobs.

## Actual visual QA — FAIL
The downloaded images show simplified shiny oval wasp anatomy with long straight stick legs, rigid cockroach wing plates and leg rods, repeated leaf/fern geometry, cylinder-like trunks, flat beige ground and weak forest depth. Five-frame and four-frame strips show very little distinct motion or camera composition. A convincing landing, sting, burrow, egg or larva action has not been visually proven. Do not call this photorealistic or production-approved.

## Targeted correction
V6.8.22 raises the wasp's final landing root by 4.2 cm while retaining the same airborne initial pose; predicted final gaps from the logged measurements become approximately `[0.0723, -0.0013, -0.0113, -0.0200, 0.0229, 0.0482]` m. The numerical gate is tightened from 5.5 cm to 2.5 cm and requires at least three tarsi near ground, with no foot deeper than 2.5 cm. **These values are predictions only** until the next Blender preflight measures the actual animated vertices. A fast preflight now runs before expensive still/motion renders to avoid wasting runner time on known geometry failures. The full diagnostic frame-48 still and actual visual inspection remain mandatory after numerical success.

The 14-chapter full renderer remains fail-closed; V6.8 rigs, sting, burrow, egg and larva animations are not integrated/approved. Preserve V4 and all prior successful artifacts. No verified 3,360-frame 140-second film with audible synchronized Hindi narration exists yet.

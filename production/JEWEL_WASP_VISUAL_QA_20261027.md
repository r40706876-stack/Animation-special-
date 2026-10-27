# Independent visual QA — 2026-10-27

Source: GitHub Actions run 40469153029, all six five-second shot artifacts downloaded and inspected. Local FFmpeg concatenation produced a **30.000-second, 720-frame, 540x960 MP4** that decoded without errors. This is a verified *technical motion proof*, NOT a polished documentary.

## What the actual frames show
- Cockroach and wasp are visibly low-poly, with a mostly empty, flat brown ground and a few elliptical green leaves.
- Shots 1–3 reuse almost the same tight cockroach head view; storytelling variety is insufficient.
- Three oversized round neural markers in shots 2 and 3 look like eggs on top of the head, not a cutaway.
- Sting and antenna-led movement are not visually convincing; a closeup of body overlap is not proof of a targeted sting.
- The burrow finale does not show a convincing underground interior.
- No readable Hindi captions; the original failed assembly had no narration. The recovery workflow attempts free Hindi TTS and records its presence accurately.

## Actions taken
- Root failure in assembly: ffmpeg missing (exit 127). Added FFmpeg install to original workflow and a recovery workflow reusing already rendered shots.
- Revised source rig: limb and antenna articulation, wasp wing flutter, physical stinger, smaller neural markers, egg detail, wider camera framing.
- Added reusable Hindi narration generator. A revised full render is required before these visual fixes can be assessed.

## Release gate
Never describe the original six-shot output as polished or reference-quality. Review frames from the **new** render at 1 and 3.8 seconds per shot and compare to these findings. Final release requires coherent sting, neural cutaway, antenna-leading and burrow sequence, voice/captions, accurate morphology, and a real visual QA sign-off, not only MP4 decode.

# EP01 — Jewel Wasp vs Cockroach | 3D scientific story

## Production target
Original Hindi 9:16 cinematic **full-length 120–150-second** 3D documentary inspired by the *scientific storytelling techniques* of the user's first reference (not a shot-for-shot copy). This is the PRIMARY project; octopus was a Blender render smoke test only. Do not substitute still images with Ken Burns motion and call them 3D.

## Factual guardrails
Emerald cockroach wasp (Ampulex compressa) initially stings the cockroach's thoracic ganglia to temporarily impair its front legs, then delivers a targeted sting to the head ganglia. The cockroach remains able to walk but shows reduced spontaneous escape behavior. The wasp guides it by an antenna to a burrow; its larva later feeds on the host. Do not claim literal mind control, complete paralysis, or a scientifically proven single 'decision center'. Anatomical highlights must be schematic, not fabricated clinical imaging.

## Legacy 30-second proof (NOT the complete story) — VO + 3D action
| Seconds | Narration (Hindi) | Actual animated action | Camera / reveal |
|---|---|---|---|
| 0–3 | “एक छोटी ततैया… कॉकरोच को भागने से रोक सकती है?” | Cockroach races across wet leaf; metallic green wasp swoops into frame | Ground-level macro tracking, rapid rack-focus to wasp |
| 3–7 | “पहले डंक से उसके आगे के पैर कुछ देर कमजोर पड़ते हैं।” | Wasp lands, curls abdomen and stings thorax; front legs buckle | Side macro → translucent thorax cutaway showing thoracic nerve ganglia |
| 7–11 | “लेकिन असली चाल दूसरा डंक है—सिर के पास।” | Wasp repositions and delivers targeted head sting | Extreme macro, 180-degree camera arc; thin anatomical cutaway |
| 11–15 | “ज़हर उसके भागने के व्यवहार को बदल देता है।” | Glowing schematic nerve pathway transitions to real cockroach | Camera passes through translucent head and pulls out |
| 15–19 | “वह लकवाग्रस्त नहीं है… फिर भी भाग नहीं रहा!” | Split-action: normal cockroach flees; affected one moves slowly | Wide comparison with moving subjects, not static cards |
| 19–24 | “ततैया उसका एंटीना पकड़कर बिल की ओर ले जाती है।” | Wasp grips antenna and leads walking cockroach across roots | Low tracking dolly following two rigged insects |
| 24–28 | “वहीं अगली पीढ़ी के लिए कहानी बदल जाती है।” | Camera enters burrow; wasp places egg on host, non-graphic | Smooth descending crane and cave cutaway |
| 28–30 | “प्रकृति का सबसे अजीब व्यवहार-परिवर्तन!” | Burrow silhouette, rapid pullback to forest floor | Final wide reveal with clear conclusion |

## Reusable Blender assets required
- Rigged cockroach: six articulated legs, antennae, thorax, abdomen, wing covers, walk/run/hesitate actions.
- Rigged jewel wasp: six legs, jointed abdomen, stinger, translucent wings, fly/land/sting/lead actions.
- Forest floor kit: leaf, twigs, roots, stones, burrow entrance and interior, wet material, volumetric light.
- Scientific overlay kit: toggleable translucent cutaway and schematic ganglia, animated path glow.
- Camera kit: macro tracking, rack focus, orbit, push-through, low dolly, split comparison, burrow crane.
- Lighting kit: dramatic rim light, diffuse forest canopy, cave interior; consistent color and readable silhouettes.
- Sound: original ambient forest, wing buzz, footfalls, subtle impact, Hindi VO; licensed/free only.

## Quality gate (mandatory)
1. Story is **30 s ±1 s**, 9:16, 24 or 30 fps, continuous A/V decode, audio present, and no clipped Hindi captions.
2. Every 3–5 s there is a visible new **animated action**; no 5-second stationary characters or recycled octopus underwater set.
3. Frames at 0.5, 2, 5, 9, 13, 17, 21, 26, 29 seconds inspected as a contact sheet; confirm anatomy, poses, camera variety and no intersections.
4. Camera movements and body motion must be observable across adjacent frames, not merely stated in code.
5. Publish MP4 and contact sheet with source commit, frame count, dimensions, duration, audio and decode QA. **Do not report final success without visual inspection.**

## Execution order
Build reusable wasp/cockroach rigs and forest scene; render 3-second motion proof; expand to seven continuous action beats; render full 30 seconds in parallel shot jobs; assemble and run visual QA. Fix failures in the GitHub workflow before cosmetic iteration. The existing 2D documentary generator is NOT the final rendering engine for this project.


## REQUIRED COMPLETE FILM — 120–150 seconds, not a 30s summary
The 30s proof is a technical milestone only. Never label it the finished reference-inspired film. Use 24 fps, 9:16, 12–15 distinct 8–12-second chapters; prioritize readable movement and visual continuity over artificial length.

| Chapter | Approx seconds | On-screen narrative/action |
|---|---|---|
| 1 | 0–10 | Establish forest floor, live cockroach foraging and wasp entering scene; clear scale and geography |
| 2 | 10–20 | Wasp searches, approaches and pursues the cockroach; believable flying/leg contact |
| 3 | 20–30 | Cockroach attempts escape, wasp positions its body; visible spatial continuity |
| 4 | 30–40 | First sting into thoracic nerve region; anatomical schematic labels, not fabricated imaging |
| 5 | 40–50 | Transient front-leg impairment, wasp repositions, cockroach response |
| 6 | 50–60 | Second targeted head sting and accurate schematic of head ganglia |
| 7 | 60–70 | Venom mechanism explained with restrained, explicitly schematic neural overlays |
| 8 | 70–80 | Cockroach regains walking capacity but displays reduced escape motivation |
| 9 | 80–90 | Wasp cleans/inspects, grabs antenna; show contact and scale clearly |
| 10 | 90–100 | Antenna-led walking along roots and leaf litter toward burrow |
| 11 | 100–110 | Entrance and inside-burrow camera reveal; cockroach enters |
| 12 | 110–120 | Egg attached to host, wasp closes burrow; non-graphic |
| 13 | 120–130 | Time-lapse egg hatching and larva development, schematic/non-graphic |
| 14 | 130–140 | Life cycle conclusion and return to forest; science recap |

### Full-film acceptance criteria
- Render all chapters and assemble 140 seconds with original Hindi narration timed to visible actions; no frozen filler, no repeated 5-second shots.
- Reusable rigged insects, natural walk cycles, distinct wasp fly/land/sting/antenna-grip motions, credible burrow and forest environment, multiple camera types.
- Verify each chapter's actual frames, 9:16 resolution, decode, audio, total runtime, and inspect contact sheets before calling it complete.
- Existing 30s MP4 is only a technical proof. Build a separate full-length workflow and output `videos/JEWEL_WASP_FULL_STORY.mp4`; do not overwrite the verified 30s proof.

## Execution checkpoint — 2026-10-27
- Reusable procedural forest props, smoother insect meshes and cockroach wing covers: `src/jewel_wasp_3d.py`, commit `8afe0604`.
- New full-film source: `src/jewel_wasp_full.py` with fourteen independently animated 240-frame chapters (10 seconds each).
- Timed original Hindi narration source: `src/jewel_wasp_full_audio.py`, each chapter fit to 10 seconds without clipping.
- Parallel Blender workflow: `.github/workflows/jewel_wasp_full.yml`; initial run **40506557738** (https://github.com/r40706876-stack/Animation-special-/actions/runs/40506557738).
- At checkpoint, chapters are running/queued; **no 140-second MP4 exists yet**. Do not call this a polished final film until frame-by-frame visual inspection and technical QA pass.
- Previous 30-second render is a technical proof only. Do not overwrite it or present it as the complete film.

# Independent DRAFT chapter 4 and 6 visual QA — 2026-10-31 (IST)

Source: 140s DRAFT rough-cut workflow run [41110464863](https://github.com/r40706876-stack/Animation-special-/actions/runs/41110464863). Inspected downloaded, decoded GitHub artifacts, not the source scene alone.

| Chapter | Artifact ID | MP4 | Decode | Video | Audio |
|---|---:|---|---|---|---|
| 4 — Temporary motor effect | 13016031794 | chapter_4.mp4 | FFmpeg full decode PASS | H264, 162x288, 24fps, 240 frames, 10.000s | No audio stream (expected: per-chapter render silent; narration assembled later) |
| 6 — Neural response | 13017198634 | chapter_6.mp4 | FFmpeg full decode PASS | H264, 162x288, 24fps, 240 frames, 10.000s | No audio stream (expected: per-chapter render silent; narration assembled later) |

Visually reviewed actual frames at 0, 2, 4, 6 and 8 seconds for **both** chapters. Both show a brown cockroach with a row of small glowing orange dots on its dorsal surface, green leaves and brown ground. Motion is present but subtle: the camera composition and subject are nearly unchanged over the 10-second beat. The wasp is intentionally absent in both shots, per the source renderer.

**Chapter 4 visual FAIL for final:** the supposed temporary motor effect is not clearly expressed by a change in leg motion, stance, or body reaction. Glowing dorsal dots look like attached external objects rather than an explicitly framed explanatory nervous-system schematic. The causal relation to the prior sting is not understandable from the shot alone.

**Chapter 6 visual FAIL for final:** a similar cockroach-and-orange-dots shot is repeated, so the head-ganglion/neural response does not read as a distinct explanatory beat. No labeled cutaway, pulse propagation, or clear head-region emphasis. Distinct compositions are required.

**Rough-cut gate:** Retain both technically valid segments as DRAFT placeholders so the full 14-chapter assembly can proceed without rerendering successful chapters. Do not treat technical decode, the existence of glow nodes, or green CI as scientific/anatomical/visual approval. The original videos contain no Hindi narration: check only after assembly. The final QA gate stays CLOSED.

**Targeted next-pass fixes (after obtaining the 140s rough cut):**
1. Chapter 4: readable medium-close side view of cockroach legs, a short transient motor pause/recovery, with leg pose and temporal response actually visible.
2. Chapter 6: clearly differentiated close head-region scientific schematic (explicitly labeled stylized diagram) with a traveling neural pulse and the behavior implication; do not depict dorsal beads as literal ganglia.
3. Maintain the V6.8 rigs, original forest, distinct shot sizes, safe framing and 10s/240-frame contracts; preview both motion sequences before committing to expensive full renders.
4. Preserve V4, existing successful draft chapter artifacts and the source-fingerprint cache; rerender only affected chapters for a later revision, not the currently running draft.

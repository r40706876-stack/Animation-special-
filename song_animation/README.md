# Song animation — first working module

Original 2D illustration renderer plus optional audio → timed ASR → Gemini scene plan → MP4 pipeline. All generated videos are **review drafts**. Existing Katha/Jewel Wasp/other workflows are unchanged.

## Working now

- Five supported visual actions: one hand gives a rose, rose opens into the next scene, moving top-down crowd with a stationary rose owner, diverging paths, heart/memory paths.
- Deterministic original layered artwork; individual hands/people/petals move. No stock clips or static-image Ken Burns substitution.
- Actual faster-whisper large-v3-turbo word timestamps retained; no time distribution by word length.
- Optional supplied timed-lyrics JSON (`--lyrics`) in the same format as generated `lyrics.json`.
- Whole-segment meaning supplied to Gemini; unsupported themes must fail rather than invent assets or force unrelated visuals.
- Continuous integer frame timeline, cue-word validation, all transcript words covered once, MP4 decode/duration/frame count checks, contact sheet and sampled pixel-motion report.
- No Instagram, Telegram or other automatic publishing.

## Run

Install FFmpeg, Python 3.11 and `pip install -r song_animation/requirements.txt`.

Silent original motion proof (no model/API dependency):

```bash
python -m unittest discover -s song_animation/tests -v
python -m song_animation.render --plan song_animation/examples/proof.json --out song_proof --width 1080
```

Your audio (up to 180 seconds; `GEMINI_API_KEY` required):

```bash
python -m song_animation.run --audio path/to/song.mp3 --out song_draft --width 1080
```

Outputs: `preview.mp4`, `contact.jpg`, `motion.json`, `receipt.json`, `plan.json`. Automatic mode additionally emits `lyrics.json`, `music.json`, `status.json` when stages complete. Planner calls are bounded to three actually discovered text models. Render cache requires identical plan, source audio, renderer source and width.

GitHub workflow runs a proof first, then the reference song on changes to this feature branch. `workflow_dispatch` supports a repository audio path once workflow is available on the default branch; the feature-branch push trigger does not require merging. Standard CPU runner, no GPU required. The included reference audio is extracted from the user's supplied 34-second reference for this requested experiment; it is not an original soundtrack or a stock asset for distribution.

## Honest limits

This is a **limited five-action prototype**, not arbitrary-song animation. Lyrics recognition for singing can be inaccurate. Hindi forced alignment, expanded character/asset generation, semantic output scoring, scene-level persistent caching and automatic upload detection are future stages. Music beats are available to the planner; actions currently use lyric cues, not a guaranteed beat-synchronized choreography. Artwork is rendered at 540×960 and cleanly upscaled to 1080×1920, not native high-detail 1080p illustration. Contact sheets/technical PASS do not certify lyric meaning or retention. Full original-art film quality requires visual review and iteration.

The silent proof uses a hand-authored plan to verify motion; it does not prove the automatic song planner. Inspect the separate real-song draft and transcript before evaluating that pipeline.

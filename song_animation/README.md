# Song Animation: illustrated music-video drafts

Upload short audio under `song_animation/inputs/`. The workflow chooses the new/changed songs and processes each in an independent job (two simultaneously). Code-only changes use the reference song for integration testing. The workflow runs on `main` after merge and on the song-animation feature branch before merge. Manual runs accept one exact repository audio path; empty input runs the motion proof only.

## Current pipeline

Actual song audio → directly transcribed Hindi phrases → approximate phrase cues → whole-segment Gemini direction → supported illustrated actions → MP4 and review artifacts.

- Eight original actions: rose handover, flower portal, moving crowd, diverging paths, memory heart, rose-prick, wounded heart, thorn avoidance.
- Characters, hands, petals and paths actually move. No downloaded stock clips or static-image zoom substitution.
- Direct-audio mode keeps honest **phrase-level** timestamps. It does not pretend each word has been force-aligned. Unclear lyrics and unexplained missing openings stop rendering.
- `--transcriber whisper` compares faster-whisper large-v3-turbo with a separate retry of omitted opening audio. Its timestamps also require listening review.
- Available text models are discovered; up to three are attempted, preferring stable lighter models. The script never executes model-written code.
- `--allow-local-recovery` can make an explicitly labelled local-rule draft when direction API access fails. It supports only the pain/relationship vocabulary represented by the eight actions. Unrelated themes are rejected.
- Exact-audio/transcriber checkpoints resume lyric analysis. The included reference also has its completed direct-audio analysis keyed by SHA-256; a different audio cannot use that transcript, and its scene plan is still generated afresh. Restored caches contain analysis only, never an old preview that could be mistaken for a new result. Render reuse checks inputs, renderer code, dimensions and output SHA-256.
- Integer-frame timeline rejects gaps, overlaps, unsupported actions and unreadably short or over-eight-second shots. Every lyric unit must belong to exactly one scene.
- Technical checks include decoded frames, dimensions, duration, audio stream and sampled movement. All outputs remain review drafts and are never automatically posted.

## Local use

Python 3.11, FFmpeg and fonts-noto-core required (Pillow must support RAQM for Hindi shaping):

```bash
pip install -r song_animation/requirements.txt
python -m unittest discover -s song_animation/tests -v
python -m song_animation.render --plan song_animation/examples/proof.json --out song_proof --width 1080
```

The 16-second motion proof is silent and uses a hand-authored plan. It proves the renderer, not lyric understanding.

For a song (up to 180 seconds), set `GEMINI_API_KEY` and run:

```bash
python -m song_animation.run --audio path/to/song.mp3 --out song_draft --width 1080 --allow-local-recovery
```

Optional: `--lyrics timed_lyrics.json` uses supplied units/timings; `--planner local` selects local rules explicitly. No character-count timing distribution is used.

## Review files

`preview.mp4`, `contact.jpg`, `plan.json`, `motion.json`, `receipt.json`, `lyrics.json`, `music.json`, `status.json`; raw AI responses and HTTP/model attempt summaries accompany their completed stages. `plan.planner` identifies Gemini versus local rules. `lyrics.timing_granularity` distinguishes phrases from word-timestamp ASR. Failure keeps diagnostics; it does not produce a generic unrelated export.

The included `reference.mp3` was extracted from the user's supplied 34-second reference for this experiment. It is not an original soundtrack for reuse in other productions.

## Limits

This is a limited eight-action prototype, not arbitrary-song animation. New visual subjects and actions require new assets/renderer support. Hindi singing recognition, approximate phrase cues, symbolism and scene continuity need actual listening/viewing review. Technical PASS does not certify emotional quality or retention. Art is drawn at 540×960 and upscaled to 1080×1920. Automatic asset generation, Hindi forced word alignment, semantic output judging and persistent per-shot rendering are further stages. Existing Katha/Jewel Wasp/other workflows are unaffected.

## Visible lyrics and stronger motion

Each supplied timed phrase is burned into the video as properly shaped Hindi text in a bright safe-area panel; key emotion words use an accent colour. Captions appear and disappear at the source phrase boundaries and remain absent during instrumental portions. An editable lyrics.srt is exported too. This is phrase-timed text, not verified word-level karaoke.

The illustration now includes coordinated walker arm swing, more pedestrians and moving petals, a hand recoil at the thorn event, a stronger heart pulse and a restrained illustration push-in. Captions remain on a fixed plane. The existing actual object actions and scar continuity remain in place.

# Upload a song → a new illustrated film of up to 30 seconds

The default pipeline now generates a new storyboard, custom SVG artwork and layered animation for the uploaded song. It no longer selects from the old eight-scene menu. Characters, objects, settings, palettes and narrative are open-vocabulary model outputs. Motion uses a general hierarchical keyframe renderer (translation, rotation, scale, opacity and articulated child layers).

## Automatic workflow

1. Upload MP3/WAV/M4A/OGG/OPUS/AAC/MP4 audio under `song_animation/inputs/` on the deployed branch.
2. The upload diff selects each new/changed audio independently; two songs can run simultaneously.
3. A source of 30 seconds or less stays its available length. Longer sources produce a 30-second clip. Short reel sources up to 45 seconds use the opening; longer songs use the strongest sustained-energy window. This is an energy heuristic, not a guarantee of the best lyrical chorus. CLI `--start SECONDS` overrides selection.
4. Audio analysis detects language, genre and mood, transcribes phrases in the original script, and marks unclear/instrumental portions. Uncertain words are not invented.
5. The director writes a shared style/character bible and a connected song-specific storyboard. The illustrator generates original scene layers and rigs; no fixed theme/object list is used. Storyboard/art calls try an available full Flash model before the lighter model, within the same bounded three-model transport budget.
6. SVG validation, relative-motion checks, bounded scene-package repair, rendering, phrase captions, original soundtrack, decoding and duration checks run. Actual-frame advisory review accompanies the draft. Dark-scene contrast is flagged for review rather than rejecting a valid neon/night art style.
7. Download the Actions artifact's `preview.mp4`; `lyrics.srt`, selection, lyrics, storyboard, plan, SVG assets, contact sheet, motion report and visual review are included.

The workflow runs automatically on `main` after deployment and on the song-animation feature branch before merge. Existing Katha/Jewel Wasp workflows are separate. No social publishing occurs.

## GitHub पर कैसे चलाएँ

- इस folder के `inputs/` में **Add file → Upload files** से अपना गाना upload करके commit करें। Merge के बाद `main` branch चुनें; उससे पहले feature branch पर परीक्षण चलता है।
- **Actions → Song Animation - draft and motion proof** में नया run खोलें। पहले proof, फिर प्रत्येक नए गाने का अलग generation job चलेगा।
- Run पूरा होने पर नीचे **Artifacts → song-draft-review-…** download करें और ZIP के अंदर `preview.mp4` खोलें। `lyrics.srt` भी साथ मिलेगा।
- पुराने गाने को दोबारा चलाने के लिए **Run workflow** में उसका repository path दें। Download किए गए artifacts 7 दिन तक रखे जाते हैं; अपने वीडियो को अलग सुरक्षित रखें।
- Repository secret `GEMINI_API_KEY` और उस key पर उपलब्ध model/quota ज़रूरी हैं। AI service बंद या quota खत्म होने पर run स्पष्ट failure और checkpoints रखेगा।

The two `DEMO_*_12s.mp3` inputs are original synthetic instrumental QA fixtures. They exercise different musical moods and multiple-upload selection; they are not a claim of real-song quality across all genres.

## Run locally

Python 3.11, FFmpeg, libcairo2, fonts-noto-core and optionally fonts-noto-cjk are required. Pillow must support RAQM. Set the existing `GEMINI_API_KEY`.

```bash
pip install -r song_animation/requirements.txt
python -m song_animation.run --audio path/to/full_song.mp3 --out song_draft
python -m song_animation.run --audio path/to/full_song.mp3 --start 47 --out chosen_excerpt
```

Output never exceeds 30 seconds. Inputs shorter than 30 seconds are not silently stretched or padded into longer songs.

Optional Whisper transcription needs `pip install -r song_animation/requirements-whisper.txt`. The default audio-model path does not download Whisper weights.

The old eight-action renderer remains available only with `--engine classic`, for reproducibility. It is not the default fallback for unrelated new songs. Generated artwork requires working model access; provider failure retains diagnostics/checkpoints rather than substituting an unrelated template.

## Checks and recovery

- Original source SHA-256 plus clip selection and transcriber version guard analysis reuse. An included prior transcript is reusable only for its exact source and uncut phrases; it is not an artwork or scene-plan preset.
- Storyboard/scene checkpoints reuse matching successful scene packages. Invalid layers receive at most two package repair attempts. Provider calls try at most three discovered models per request.
- SVGs contain only bounded vector geometry and local gradients/clip paths. Scripts, external URLs, images, embedded HTML, external references and generated executable code are rejected.
- At least two independent foreground motions are required per scene. Captions and camera movement do not satisfy that check. Pixel-motion checks inspect the underlying scene, not caption changes.
- Font selection covers common Latin, Indic, Arabic, Thai and CJK scripts where the installed Noto fonts support them. Phrase timing remains approximate; this is not force-aligned word karaoke.
- Source audio, frame count, 9:16 export dimensions, 30-second duration cap and full decoding are checked. Art is composed at 540×960 and exported at 1080×1920.
- Visual review is advisory. It does not certify emotional connection, exact wording/timing, character consistency, beauty, or audience retention. Open vocabulary removes the eight-scene menu; it does not guarantee flawless output for every possible song/language/action.

## Deterministic smoke checks

```bash
python -m unittest discover -s song_animation/tests -v
python -m song_animation.render --plan song_animation/examples/vector_smoke.json --out vector_proof --width 1080
```

The synthetic proof shows journey/kite, devotional lamp/bell and festival/drum compositions with original authored SVG test data. It tests renderer versatility, not live model generation or real-song genre quality. The real uploaded reference runs separately through the generated-art pipeline.

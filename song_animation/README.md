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


### Automatic corrections and output checks

New uploads use the actual source clip (up to 30 seconds). A failed lyric/language or literal-meaning check triggers one automatic recovery attempt using two consistent audio-fingerprint windows, or independent multilingual ASR if a match is unavailable. Recognition is a hint, never proof of the lyrics or original authorship. The second transcript still has to match the actual audio. Unresolved/unclear words stop semantic scene generation. No Hindi language is forced onto other songs.

The actual encoded MP4 is decoded for every shot's visual review. Five explicit checks are required for every shot: lyric meaning, finished illustration, meaningful object/character motion, anatomy/continuity and readable captions. A missing review is a hold. Up to two repair passes rebuild the failing shots and re-render/re-review. Audio is compared with the original clip; codecs, duration, dimensions and complete decoding are also checked.

Only an output passing these checks receives `checked.mp4` and a `song-checked-*` artifact. A blocked run keeps a clearly labelled review draft and diagnostics; stale checked/preview files are removed before a new attempt. These automated checks are not a guarantee of human approval, exact word timing, reference-beating artwork, performance metrics or universal song support. Uploads remain reviewable; automatic publishing remains off.

Full-model audio meaning and encoded-frame reviews are required. Lite-model approval is never sufficient to create checked.mp4. The stored original-artwork finish reference accompanies the visual review, and bright daylight treatments have a measured brightness floor before scene caching. If suitable model access is unavailable, the run holds instead of lowering the standard.


### One connected emotional story per song

Lyrics provide meaning, emotion and timing; they are not a list of nouns to illustrate. The director now plans one premise, emotional desire, encounter/choice, carried consequence and earned final gesture. Persistent subjects may be people, relationships or objects depending on the song. Romance, sadness and human protagonists are never mandatory.

Every shot records its narrative purpose, emotional change and the incoming/outgoing state of each persistent subject. A scene cannot reset a lost object, wound or relationship, or substitute a camera move for story progression. Structurally valid plans also receive a full-model story critique before assets are generated; failed plans are replanned within a bounded three-attempt budget. The new protocol invalidates old standalone-metaphor scene caches.

The artist receives the whole story and state chain. Encoded-video review checks every adjacent shot for causal connection, persistent state and emotional progression, as well as whether the ending pays off the setup. Individually attractive but disconnected pictures cannot clear the output gate. These checks enforce the production workflow; they do not prove that a particular audience will emotionally connect.

Lyric acceptance now includes an independent ASR decoder even when the direct model initially sounds confident. An established language may guide that decoder for this clip only; unknown languages keep automatic detection. The full audio reviewer receives both transcripts and must resolve disagreements in actual words/verbs. Its rejection reasons are carried into the automatic correction attempt, preventing a coherent but wrong action such as lifting versus writing from silently passing.

### Multiple visual setups for new songs

For 20–30 seconds the director must plan at least five shots, three distinct story setups and four visible events. Concrete locations and blocking are tracked separately from camera framing: different zooms on one desk remain one setup. Three consecutive repeats are rejected before illustration. The full-model reviewer separately checks the actual decoded MP4 for visual variety, so changing setup names cannot pass a repetitive film.

Repository uploads under `song_animation/inputs/` automatically use `--artwork painted-sets`. This backend paints original song-specific environments on a CPU with the pinned `stabilityai/sd-turbo` model and keeps independently animated vector actors/props in front. It caches by actual environment, shared setting/palette and model revision. It does not reuse this poet's courtyard for unrelated genres. PNG data is bounded, decoded and embedded in the render plan; arbitrary file paths and external image URLs are not accepted. Existing lyric, narrative, meaningful motion, anatomy and finish checks still apply. A painted background alone does not certify animation quality.

Local installation for this optional backend:

```bash
pip install torch==2.5.1 torchvision==0.20.1 --index-url https://download.pytorch.org/whl/cpu
pip install -r song_animation/requirements.txt -r song_animation/requirements-painted.txt
python -m song_animation.run --audio song_animation/inputs/YOUR_SONG.mp3 --out song_output --width 1080 --artwork painted-sets
```

Only `checked.mp4` is a cleared automatic output; a review draft or a successful directed-example workflow is not proof the automatic song pipeline cleared. No universal quality or retention guarantee is made. The included `poet_multiscene` film is separately directed original artwork for the supplied recording and is labelled as such.

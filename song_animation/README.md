# Song upload → a connected animated story, up to 30 seconds

Upload a song under `song_animation/inputs/` on **main**. The changed audio is selected automatically by **Actions → Song Animation - verified checks and review drafts**. Multiple uploads enter separate jobs processed one at a time. Code-only pushes run renderer/tests; they do not process every old song or prove a finished song video.

## What the pipeline does

1. Keeps an input of 30 seconds or less at its available length. Longer sources produce an excerpt of up to 30 seconds. Short reel sources up to 45 seconds use the opening; longer songs use a sustained-energy window. This heuristic does not guarantee the best chorus. CLI `--start` overrides selection.
2. Checks original-script lyrics against actual audio and an independent multilingual decoder. Unresolved words hold generation. An included transcript correction is reusable only for its exact source hash and uncut phrases. Phrase timing is not invented word-level karaoke.
3. Writes one connected story with persistent subjects, choices, consequences and a shared style/character bible. Settings, subjects and actions are generated for the song, without an eight-animation menu. For 20–30 seconds, the story requires at least five shots, three setups and four visible events.
4. Creates validated SVG motion rigs and original raster cutouts/settings. The upload default is `flux-layers`: public FLUX original images, or a coherent whole-source local SD-Turbo text-to-image fallback if that image service fails. CPU inference can be slow and lower quality; it is not an approval. The optional `HF_TOKEN` is passed only to the image service. `GEMINI_API_KEY` with usable full-model access is required for lyrics, story and video review.
5. Animates independent foreground layers, adds readable lyrics, and exports the original soundtrack as a vertical MP4. Encoded-video review checks meaning, story progression, anatomy/continuity, illustration finish, motion and captions. Decoder measurements separately check repeated compositions, dimensions, duration, audio and complete decoding.
6. Repairs failing shots within two passes. Only an output clearing every required gate receives **checked.mp4**. A failed or incomplete review retains a labelled draft/diagnostics instead of calling it ready.

## Download the result

Open the upload's Actions run. A cleared song has an artifact named **song-checked-…**, containing `checked.mp4`, `lyrics.srt`, `quality_gate.json` and `status.json`. The **song-draft-review-…** artifact contains `preview.mp4`, scene plans and diagnostics when available; a preview is not an approved export. Artifacts expire after seven days, so download videos you want to retain. No social publishing occurs.

To retry an old song, use **Run workflow**, choose main and enter its repository audio path. One pending source is also retried daily at **07:05 UTC / 12:35 IST**. Failed attempts rotate behind untried songs; a completed receipt requires the exact source, selected clip, checked-video hashes and passed gate. Provider service/quota problems can still block a run.

## Recovery

Analysis, story candidates, validated scene packages, original images and repair checkpoints are cached. Repair checkpoints require the exact selected audio bytes, lyrics and render configuration. Successful repaired shots are saved individually, so a provider outage does not restart the whole repair. Quota-exhausted, unauthorized or retired models are skipped during that run; transient errors receive bounded retries. A source switched to CPU artwork retains that backend on resume, avoiding mixed styles from partial public generation. A new source cannot reuse that choice by filename alone.

Cache eviction or changes to source/configuration can require regeneration. Planning is checked before installing the large local image model. Song jobs have a 90-minute limit. No finite retry budget guarantees service availability.

## Local use

Python 3.11, FFmpeg, libcairo2 and Noto fonts are required; Pillow needs RAQM. Set `GEMINI_API_KEY` without placing it in source files.

```bash
pip install torch==2.5.1 torchvision==0.20.1 --index-url https://download.pytorch.org/whl/cpu
pip install -r song_animation/requirements.txt -r song_animation/requirements-painted.txt -r song_animation/requirements-cutouts.txt
python -m song_animation.resume --audio path/to/song.mp3 --out song_output --width 1080 --artwork flux-layers
```

The plain CLI defaults to SVG artwork unless `--artwork` is specified. `painted-sets` and `painted-layers` retain earlier CPU painting experiments; `--engine classic` retains the old fixed renderer for reproducibility. These are not automatically substituted for unknown songs.

```bash
python -m unittest discover -s song_animation/tests -q
python -m song_animation.cpu_character_probe
```

The isolated CPU character workflow performs actual text-to-image generation and matting. It is a backend test, not a completed-song certificate. Synthetic renderer proofs similarly test code, not real-song quality.

## Verification boundary

A separately directed nine-shot film for the supplied recording is available through `examples/poet_gpu_film.py`; it uses original artwork and is not evidence that arbitrary uploads automatically achieve that quality. At the reliability update, 157 local tests passed. Earlier fully automatic supplied-song runs were held for flat artwork, repetitive staging or provider failures. The new CPU original-art fallback still needs actual aesthetic and full-song verification. Automated gates can miss errors: no claim is made of zero failures, every language/genre, exact word timing, reference-beating visuals, human approval or audience connection.

# Original raster artwork and the directed song example

The automatic workflow now selects `flux-layers`: original FLUX cutouts and viewpoint-specific settings replace painting texture over geometric SVG placeholders. Story planning, caption checks, motion rigs, decoded-video variety checks and the final meaning/anatomy review remain required. The legacy CPU renderer remains selectable for comparisons.

## Current verification boundary

The source-specific `examples/poet_gpu_film.py` is a directed, curated 30-second example with nine shots. Its artwork includes an original FLUX character and earlier original approved illustrations. It is not proof that arbitrary new songs automatically achieve the same finish. Do not mark a source completed from this example or from a green code-only run.

The public FLUX service generated real images in testing but also returned an opaque failure before a complete automatic film cleared review. The separate public video-generation trial did not produce a usable clip. Those services must not be described as reliable unlimited production capacity.

## Run

```sh
pip install -r song_animation/requirements.txt
pip install -r song_animation/requirements-cutouts.txt
python -m song_animation.resume --audio song_animation/inputs/your_song.m4a --out song_draft --width 1080 --artwork flux-layers
```

The existing Gemini repository secret supplies transcription/story/review access. Optional `HF_TOKEN` supplies the user's own Hugging Face authentication to the public image service. Anonymous access is quota-limited. No accounts, tokens, IP addresses or alternate endpoints are rotated to bypass limits. An opaque provider error is held rather than blindly retried.

Generated PNGs, alpha cutouts and their provenance are cached. Changing the rendering backend preserves only a storyboard whose full source analysis/music key matches; another song cannot reuse it. Final MP4 acceptance still requires the actual decoded-video checks. No template/genre list or universal-quality certificate is used.

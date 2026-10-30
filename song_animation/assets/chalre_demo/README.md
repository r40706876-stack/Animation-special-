# Supplied Saraiki song: corrected authored film

The earlier Hindi/Bhangra interpretation was wrong. Two independent audio fingerprint windows matched `Chalre Chalre Waal` (track 903407118, source positions 47.407625 and 50.40765625). The fingerprint service uploader name is not certified original authorship. Multilingual ASR supports the audible phonetics; identification and lyric comparison resolve the meaning. Phrase timing remains approximate. The final audible line is cut off: captions do not complete it using the full song.

This is an authored correction for the exact supplied recording, not evidence that all new songs automatically obtain this artwork. The original clip's verified hash keys the analysis fixture; unrelated songs cannot inherit its words or imagery.

Reproduce without image APIs:

```bash
python -m song_animation.examples.chalre_film --audio song_animation/inputs/ritik_new_song_20261030.mp3 --out chalre_film
```

The renderer uses a coherent anatomical character, spatially deformed loose cloth, subtle independent hair deformation, gesturing secondary figures, town layers and separately timed captions. The output is 1080x1920 H.264/AAC with fast-start playback. No audience-retention or universal-quality claim is made.

## Artwork prompts (built-in image generation)

1. Head reference: isolated handsome young South Asian man, warm medium-brown skin, soft dark eyes, slight affectionate smile, detailed abundant wavy curly black hair with ringlets, light neat stubble; three-quarter portrait; no clothing or shoulders; premium finely engraved watercolor, warm sunlight, true transparent background; no text or watermark.
2. Costume reference: separate connected torso and hands, ivory cotton kurta with embroidered open band collar, black bronze-bordered shawl over viewer-right shoulder, one hand holding it; realistic anatomy, fine engraved watercolor, true transparency, no head or scenery.
3. `shawl.webp`: one long soft charcoal-black woven shawl tail, bronze border and tassels, subtle S curve from narrow upper-left attachment to lower-right end; modeled folds and visible fibers, engraved watercolor, transparent background, no body/text.
4. `hero.webp` final composition: combine the exact head/hair identity from reference 1 with costume/body reference 2 into one anatomically coherent head-to-waist character. Natural neck correctly enters the open band collar, no cutout seams, skin flaps or floating head. Preserve face, abundant dark curls, subtle smile, ivory kurta, black bronze-bordered shawl and hand holding it. Realistic head/shoulder proportions, gently tilted three-quarter pose, premium finely engraved watercolor in warm light, complete head/arms/hands/torso, true transparent background, no scenery or text.

Only the final coherent hero and the separate loose shawl are consumed by the movie. The intermediate head/torso assets are not used in the final assembly.

# Original lyric illustration assets

Created using the built-in imagegen tool for the authored 6.8-second art-direction proof. This example is not proof that the GitHub Gemini key can generate the same artwork automatically. The separate image-art capability workflow tests that connection.

- `rose.webp`: richly detailed crimson botanical rose, organically curled petals, engraved ink contours, watercolor/gouache shading, short stem and two leaves, transparent background, no text.
- `palm.webp`: anatomically correct open right palm with natural separated fingers, warm peach shading, fine sepia contours, off-white rolled cuff, transparent background, no object or wound initially.
- `thorns.webp`: a naturally curved horizontal olive-brown woody branch with irregular sharp thorns, subtle gold highlights and a few muted green leaves, engraved botanical watercolor, transparent background.

The renderer supplies the causal animation: separate footprints navigate around branches; independent rose petals touch the palm and symbolic marks appear at that contact. It is not a still-image pan. Caption timestamps are approximate source-phrase boundaries.

Run from the repository root:

```
python -m song_animation.examples.lyric_meaning_demo --audio song_animation/inputs/reference.mp3 --out meaning_demo
```

All four generation prompts used the `illustration-story` production-animation-asset specification, premium handcrafted editorial quality, complete isolated subject, generous clear margins, no borders/text/watermarks. The full positive descriptions above document the subject and material requirements. The output PNGs were resized to WebP production assets; original high-resolution generations remain in the conversation.

- `heart.webp`: recognisable anatomical exterior heart in dusty-rose/ivory terracotta watercolor with finely engraved contours, subtle surface vessels, no wounds/bleeding or labels, transparent background.

The 30-second authored showcase is `python -m song_animation.examples.lyric_film_showcase --audio song_animation/inputs/reference.mp3 --out meaning_showcase`. It maps each timed source phrase to scars on a heart, a damaging gift, footprints avoiding thorns, flower-petal contact marks, strangers in a crowd, and fraying bonds to familiar hands. It is authored specifically for the reference, and must not be presented as universal automatic generation evidence.

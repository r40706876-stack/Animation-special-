# Directed poem story for the supplied audio 1000076620

This is an authored film for this recording, not a reusable fixed plot for all songs and not evidence of universal automatic generation. It uses only the supplied audio, original generated artwork and animated ink/paper/hand layers. No imagery from the uploaded video is used. The output uses the opening 29.988 seconds within the existing 30-second limit.

The story carries the same paper, writing hand, remembered woman and cup through: waiting to express a feeling, inspiration becoming a poem, hesitation over the unsaid line, and writing a metaphor instead. The ending leaves the letter unsent. The cup remains on the desk; there is no drinking or toast scene.

A direct model transcribed the final verb as “उठा लिया” and approved itself. Independent large-v3 decoding of the actual tail instead found “लिख दिया” with high word confidence. The film uses “जाम लिख दिया”. ASR is evidence, not an infallible transcript; phrase timings remain approximate. Native model review in the general pipeline now also receives independent decoder evidence and disagreement feedback before accepting lyrics.

Reproduce:

```bash
python -m song_animation.examples.poet_story_film --audio song_animation/inputs/song_1000076620.m4a --out poet_story
```

The separate directed-render workflow exports H.264/AAC at 1080x1920. The general song pipeline and its checked-output gate remain separate. This example does not bypass that gate for other inputs.

## Artwork prompt set (built-in image generation)

- `muse.webp`: original left-facing three-quarter profile of an adult South Asian woman, expressive eyes and restrained affectionate smile, dark wavy hair, teal silk dupatta with subtle gold edging, tiny gold earring, head/upper shoulders, premium engraved watercolor, warm natural light and genuine alpha transparency. No scenery, text, borders, logos or other faces.
- `writing_hand.webp`: above-angle cutout of one adult South Asian man's anatomically correct right hand and ivory kurta cuff, natural five-finger grip on one dark reed/calligraphy pen, nib projects toward lower left and remains exposed, fine engraved watercolor with realistic skin/cotton texture and transparent background. No paper, desk, text or duplicate hand.
- `goblet.webp`: one complete antique silver goblet, engraved botanical bowl, scalloped rim, short slender stem and low round foot, glimpse of dark burgundy liquid, fine watercolor/ink shading, warm silver highlights and transparent background. No hand, table, scene, lettering or watermark.

An intermediate held-goblet image was explored but is deliberately not consumed by the film, because the verified action is writing rather than lifting a drink.

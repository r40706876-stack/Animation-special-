# Real audio acceptance

The manually repaired 30-second `song_1000077365` film cleared actual visual and technical checks in run 41394878172. That does not establish unattended success for other recordings.

The user authorized three further real supplied recordings to run without manual scene/art/lyric corrections:

| Input | Source duration | Purpose |
|---|---:|---|
| `ritik_new_song_20261030.mp3` | 15.31s | Short Punjabi vocal input |
| `reference.mp3` | 34.25s | Hindi hurt/trust ghazal; automatic 30s excerpt |
| `song_1000076620.m4a` | 41.19s | Hindi romantic ghazal; automatic 30s excerpt |

The initial live run **41410103196**, commit **c81b7e8291af9b1582d533a3f8ae83c2f0353b7a**, failed all three cases during fresh lyric verification before scene generation. No MP4 was produced. Its 8 MB artifact preserves the automatic analysis and exact selected audio for all three sources. Failures included Romanized Hindi, actual word disagreements, and a false rejection of the orthographic pair `ज़ख़्म`/`ज़ख्म`. A short blind-listening crop also lacked the musical phrase context. Recovery strengthens native-script instructions and full-model transcription, supplies the unprompted selected clip alongside physical region crops, and normalizes nukta consistently with the existing independent-ASR conflict comparison. Different verbs, negations and uncertain listening still fail. This document is not a pass receipt.

`Song quality acceptance - three real inputs` runs one case at a time under the same workflow concurrency group as normal song production. It uses the same production entry point and image dependencies. `SONG_ACCEPTANCE_COLD_START=1` disables the hand-corrected lyric fixture and all preserved manually directed source art. No ordinary production-output cache is imported. The suite's own automatic checkpoints can resume after interruptions; successful outputs are rechecked before reuse.

Each case must clear composition and decoded-export visual review, then independently pass the actual MP4 decode, dimensions, duration and source-audio correlation checks. Missing reviews or a green status JSON without the real video cannot pass. Automated rejection/repair remains enabled. Quota/service holds defer remaining sources and preserve intermediate work; deferred is not passed. Run artifacts retain the complete case directories and `acceptance_report.json`.

After a live run completes, inspect its actual contact images and playable outputs before calling acceptance complete. Do not hand-fill per-source scenes/art/lyrics to make the suite pass, lower gates, count instrumental demos as real songs, or claim every future input will be error-free from three examples.

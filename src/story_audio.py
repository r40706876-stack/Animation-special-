"""Original 25-second underwater score and sound cues, no external samples."""
import array
import math
import pathlib
import random
import sys
import wave

RATE = 22050
DURATION = 25.0
TAU = math.tau
SAMPLES = int(RATE * DURATION)
track = array.array("f", [0.0]) * SAMPLES
rng = random.Random(20261027)


def note(start, pitch, duration, gain=.1, kind="bell"):
    first = max(0, int(start * RATE))
    count = min(int(duration * RATE), SAMPLES - first)
    for i in range(max(0, count)):
        t = i / RATE
        attack = min(1.0, t / .025)
        release = max(0.0, (duration - t) / .15)
        if kind == "bell":
            env = attack * math.exp(-3.5 * t / max(.1, duration)) * min(1.0, release)
            signal = math.sin(TAU * pitch * t) + .26 * math.sin(TAU * pitch * 2.01 * t)
        elif kind == "bass":
            env = attack * min(1.0, release) * .75
            signal = math.sin(TAU * pitch * t) + .12 * math.sin(TAU * pitch * 2 * t)
        else:
            env = attack * min(1.0, release) * .6
            signal = math.sin(TAU * pitch * t) + .16 * math.sin(TAU * pitch * 1.5 * t)
        track[first + i] += gain * env * signal


def whoosh(start, duration=.48, gain=.09):
    first = int(start * RATE)
    count = min(int(duration * RATE), SAMPLES - first)
    smoothed = 0.0
    for i in range(max(0, count)):
        t = i / RATE / duration
        smoothed = .88 * smoothed + .12 * rng.uniform(-1, 1)
        track[first + i] += gain * math.sin(math.pi * t) ** 2 * smoothed


# Deterministic original pentatonic motif and five story-beat cues.
melody = [392.0, 440.0, 523.25, 587.33, 523.25, 440.0, 392.0, 329.63]
for bar in range(10):
    start = bar * 2.5
    note(start, melody[bar % len(melody)], 1.25, .048, "pad")
    note(start + 1.25, melody[(bar + 2) % len(melody)] / 2, 1.2, .032, "bass")
for t, p in [(0.35, 784), (.7, 1046.5), (1.15, 1318.5)]:
    note(t, p, .9, .10)
whoosh(5.15, .6, .14)
note(5.35, 349.2, .55, .14, "bass")
for t in [10.1, 10.7, 11.3, 11.9, 12.5, 13.1, 13.7, 14.3]:
    note(t, 220, .15, .085, "bass")
for t in [10.4, 12.5, 14.0]:
    whoosh(t, .55, .12)
for t, p in [(16.2, 523.25), (16.65, 659.25), (17.1, 784)]:
    note(t, p, 1.1, .10)
for t, p in [(20.6, 523.25), (21.1, 659.25), (21.6, 784),
             (22.1, 1046.5), (23.0, 1318.5)]:
    note(t, p, 1.4, .095)

peak = max(abs(x) for x in track) or 1.0
normalization = min(1.0, .75 / peak)
pcm = array.array("h")
for i, value in enumerate(track):
    fade = min(1.0, (SAMPLES - i) / (RATE * .65))
    pcm.append(int(max(-1.0, min(1.0, value * normalization * fade)) * 32767))
output = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else "octopus_story_audio.wav")
output.parent.mkdir(parents=True, exist_ok=True)
with wave.open(str(output), "wb") as wav:
    wav.setnchannels(1)
    wav.setsampwidth(2)
    wav.setframerate(RATE)
    wav.writeframes(pcm.tobytes())
print("ORIGINAL_STORY_AUDIO_READY", output, "duration", DURATION)

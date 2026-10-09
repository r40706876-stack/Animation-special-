"""Audio -> Hindi words with timing (free, offline, faster-whisper)."""
import os


def transcribe(audio_path):
    from faster_whisper import WhisperModel

    model_name = os.getenv("WHISPER_MODEL") or "large-v3-turbo"
    print(f"[whisper] model={model_name} file={audio_path}")
    model = WhisperModel(model_name, device="cpu", compute_type="int8")
    segments, _ = model.transcribe(
        str(audio_path),
        language="hi",
        word_timestamps=True,
        vad_filter=True,
        initial_prompt="यह एक हिंदी धार्मिक कथा है। भगवान, संत, राजा, गाँव की कहानी।",
    )
    words = []
    for seg in segments:
        for w in seg.words or []:
            text = w.word.strip()
            if text:
                words.append({"w": text, "s": round(w.start, 2), "e": round(w.end, 2)})
    print(f"[whisper] {len(words)} words")
    return words

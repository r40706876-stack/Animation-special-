"""Conservative signal diagnostic for the 14 x 10-second DRAFT.

This is NOT Hindi language, intelligibility, or sync approval.
"""
import array
import json
import math
import pathlib
import subprocess
import sys

RATE = 8000
CHAPTER_SECONDS = 10
CHAPTERS = 14
WINDOW_SECONDS = 0.5
THRESHOLD_DBFS = -47.0

def main(video, report_path):
    probe = json.loads(subprocess.check_output([
        "ffprobe", "-v", "error", "-show_entries",
        "stream=codec_type:format=duration", "-of", "json", video], text=True))
    audio_present = any(s.get("codec_type") == "audio" for s in probe.get("streams", []))
    report = {
        "draft_only": True, "audio_stream_present": audio_present,
        "language_verified": False, "intelligibility_verified": False,
        "narration_sync_verified": False, "threshold_dbfs": THRESHOLD_DBFS,
        "chapters": [],
    }
    if audio_present:
        pcm = subprocess.run([
            "ffmpeg", "-v", "error", "-xerror", "-i", video,
            "-map", "0:a:0", "-vn", "-ac", "1", "-ar", str(RATE),
            "-t", str(CHAPTERS * CHAPTER_SECONDS), "-f", "s16le", "-"
        ], check=True, stdout=subprocess.PIPE).stdout
        if len(pcm) % 2:
            raise ValueError("Malformed 16-bit PCM length")
        samples = array.array("h")
        samples.frombytes(pcm)
        window = int(RATE * WINDOW_SECONDS)
        windows_per_chapter = int(CHAPTER_SECONDS / WINDOW_SECONDS)
        for i in range(CHAPTERS):
            levels = []
            for w in range(windows_per_chapter):
                start = (i * windows_per_chapter + w) * window
                block = samples[start:start + window]
                if not block:
                    levels.append(-120.0)
                    continue
                rms = math.sqrt(sum(v*v for v in block) / len(block)) / 32768
                levels.append(20 * math.log10(max(rms, 1e-6)))
            active_flags = [v > THRESHOLD_DBFS for v in levels]
            active = sum(active_flags)
            longest_gap = 0
            gap = 0
            for audible in active_flags:
                gap = 0 if audible else gap + 1
                longest_gap = max(longest_gap, gap)
            report["chapters"].append({
                "chapter": i, "active_half_second_windows": active,
                "total_half_second_windows": windows_per_chapter,
                "peak_window_dbfs": round(max(levels), 2),
                "signal_present": active >= 4,
                "longest_silent_interval_seconds": round(longest_gap * WINDOW_SECONDS, 2),
                "long_silence_warning": longest_gap * WINDOW_SECONDS > 2.0,
                "speech_density_precheck": active >= 14 and longest_gap * WINDOW_SECONDS <= 2.0,
            })
    report["all_chapters_have_signal"] = bool(
        audio_present and len(report["chapters"]) == CHAPTERS
        and all(c["signal_present"] for c in report["chapters"]))
    report["speech_density_precheck_pass"] = bool(
        report["all_chapters_have_signal"] and
        all(c["speech_density_precheck"] for c in report["chapters"]))
    report["interpretation"] = (
        "Signal and 0.5s silence-gap checks only; human Hindi listening and action sync still required."
        if audio_present else "No audio stream; narration missing.")
    pathlib.Path(report_path).write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n")
    print(json.dumps(report, ensure_ascii=False))

if __name__ == "__main__":
    if len(sys.argv) != 3:
        sys.exit("Usage: python draft_audio_gate.py VIDEO.mp4 REPORT.json")
    main(sys.argv[1], sys.argv[2])

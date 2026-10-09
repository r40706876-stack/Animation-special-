"""Plan + words + backgrounds + audio -> 1080x1920 MP4 (Playwright + ffmpeg)."""
import base64
import json
import os
import pathlib
import subprocess

from playwright.sync_api import sync_playwright

HERE = pathlib.Path(__file__).parent


def audio_duration(path):
    out = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(path)],
        capture_output=True, text=True, check=True,
    )
    return float(out.stdout.strip())


def build_html(plan, words, bg_paths, html_path):
    bgs = {k: "data:image/jpeg;base64," + base64.b64encode(pathlib.Path(p).read_bytes()).decode()
           for k, p in bg_paths.items()}
    data = {
        "title": plan["title"],
        "characters": [{"id": c["id"], "svg": c["svg"]} for c in plan["characters"]],
        "scenes": plan["scenes"],
        "words": words,
        "bgs": bgs,
    }
    tpl = (HERE / "template.html").read_text(encoding="utf-8")
    payload = json.dumps(data, ensure_ascii=False).replace("</", "<\\/")
    html_path.write_text(tpl.replace("__DATA__", payload), encoding="utf-8")
    return html_path


def render_video(plan, words, bg_paths, audio_path, out_path, workdir):
    fps = int(os.getenv("FPS", "24"))
    duration = audio_duration(audio_path)
    workdir.mkdir(parents=True, exist_ok=True)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    html = build_html(plan, words, bg_paths, workdir / "scene.html")
    n = int(duration * fps) + 1
    print(f"[render] {duration:.1f}s, {n} frames @ {fps}fps")

    ff = subprocess.Popen([
        "ffmpeg", "-y", "-loglevel", "error",
        "-f", "image2pipe", "-framerate", str(fps), "-i", "-",
        "-i", str(audio_path),
        "-map", "0:v", "-map", "1:a",
        "-c:v", "libx264", "-preset", "veryfast", "-crf", "20", "-pix_fmt", "yuv420p",
        "-c:a", "aac", "-b:a", "160k", "-shortest", "-movflags", "+faststart",
        str(out_path),
    ], stdin=subprocess.PIPE)

    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page(viewport={"width": 540, "height": 960}, device_scale_factor=2)
        page.goto(html.resolve().as_uri())
        page.wait_for_function("window.READY === true")
        page.wait_for_timeout(500)  # images decode
        stage = page.locator("#stage")
        for i in range(n):
            page.evaluate(f"render({i / fps:.4f})")
            ff.stdin.write(stage.screenshot(type="jpeg", quality=92))
            if i % (fps * 10) == 0:
                print(f"[render] {i}/{n}")
        browser.close()

    ff.stdin.close()
    if ff.wait() != 0:
        raise RuntimeError("ffmpeg fail")
    print(f"[render] ban gaya: {out_path}")
    return out_path

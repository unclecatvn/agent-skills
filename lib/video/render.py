"""Render intro.html to an MP4 with its score, or to PNG stills (and the score) to check an edit.

    python3 render.py intro.html agent-skills-intro.mp4
    python3 render.py intro.html stills/ 4 12.5      # stills/t004.0.png, stills/t012.5.png, stills/score.wav

The page is drawn at twice the size and holds still; window.renderAt(t) returns the camera [cx, cy, scale] and whether a
caption shows. The camera is applied here, a sub-pixel crop scaled down, so text never re-rasterises while it moves; the
captions are a second, transparent pass laid on top. score.mjs (Node) synthesizes the music and every sound effect on the
cues the page lists in window.MUSIC.
"""
import io
import json
import pathlib
import subprocess
import sys
import tempfile

from PIL import Image
from playwright.sync_api import sync_playwright

FPS = 60
SS = 2  # the page's pixels per output pixel at scale 1
HUD = {"x": 0, "y": 0, "width": 1920, "height": 300}  # where the captions live, in output pixels
HERE = pathlib.Path(__file__).resolve().parent


def score(music, wav):
    subprocess.run(
        ["node", "--input-type=module", "-e",
         "import { score } from './score.mjs'; import fs from 'node:fs';"
         "fs.writeFileSync(process.argv[1], score(JSON.parse(fs.readFileSync(0, 'utf8'))));", str(wav)],
        input=json.dumps(music), text=True, check=True, cwd=HERE)


def ffmpeg(*args, **kw):
    return subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", *args], **kw)


def gain(wav, target=-16, ceiling=-1.5):
    """One linear gain to bring the score to target LUFS without passing the true-peak ceiling (dB)."""
    r = subprocess.run(["ffmpeg", "-hide_banner", "-nostats", "-i", wav, "-af", "loudnorm=print_format=json", "-f", "null", "-"],
                       capture_output=True, text=True, check=True)
    m = json.loads(r.stderr[r.stderr.rindex("{"):r.stderr.rindex("}") + 1])
    return min(target - float(m["input_i"]), ceiling - float(m["input_tp"]))


def frame(page, t):
    """The frame at t, 1920 × 1080: the page through the camera, the captions on top."""
    cx, cy, s, hud = page.evaluate("t => window.renderAt(t)", t)
    shot = Image.open(io.BytesIO(page.screenshot(type="jpeg", quality=92))).convert("RGB")
    w, h = 1920 / s, 1080 / s
    im = shot.resize((1920, 1080), Image.LANCZOS, box=((cx - w / 2) * SS, (cy - h / 2) * SS, (cx + w / 2) * SS, (cy + h / 2) * SS))
    if hud:
        page.evaluate("document.body.dataset.pass = 'hud'")
        cap = Image.open(io.BytesIO(page.screenshot(clip=HUD, omit_background=True))).convert("RGBA")
        page.evaluate("document.body.dataset.pass = ''")
        cap = cap.resize((HUD["width"], HUD["height"]), Image.LANCZOS)
        im.paste(cap, (HUD["x"], HUD["y"]), cap)
    return im


src, out, *times = sys.argv[1:]
with sync_playwright() as pw:
    browser = pw.chromium.launch()
    page = browser.new_page(viewport={"width": 1920, "height": 1080}, device_scale_factor=SS)
    page.on("pageerror", lambda e: print("stage:", e, file=sys.stderr))
    page.goto(pathlib.Path(src).resolve().as_uri())
    page.wait_for_function("window.ready === true", timeout=60_000)
    music = page.evaluate("window.MUSIC")

    if not out.endswith(".mp4"):
        stills = pathlib.Path(out)
        stills.mkdir(parents=True, exist_ok=True)
        score(music, stills / "score.wav")
        for t in times:
            frame(page, float(t)).save(stills / f"t{float(t):05.1f}.png")
    else:
        with tempfile.TemporaryDirectory() as tmp:
            picture, wav = f"{tmp}/picture.mp4", f"{tmp}/score.wav"
            score(music, wav)
            db = gain(wav)
            # About 10 minutes for the 80 s film at 60 fps.
            enc = ffmpeg("-f", "rawvideo", "-pix_fmt", "rgb24", "-s", "1920x1080", "-framerate", str(FPS), "-i", "-",
                         "-c:v", "libx264", "-preset", "slow", "-crf", "21", "-pix_fmt", "yuv420p", picture, stdin=subprocess.PIPE)
            n = round(music["duration"] * FPS)
            for i in range(n):
                enc.stdin.write(frame(page, i / FPS).tobytes())
                if i % FPS == 0:
                    print(f"\r{i}/{n} frames", end="", flush=True)
            enc.stdin.close()
            if enc.wait():
                sys.exit("ffmpeg failed on the picture")
            mux = ffmpeg("-i", picture, "-i", wav, "-map", "0:v", "-map", "1:a", "-c:v", "copy",
                         "-af", f"volume={db:.2f}dB", "-ar", "48000", "-c:a", "aac", "-b:a", "192k",
                         "-shortest", "-movflags", "+faststart", out)
            sys.exit(mux.wait())
    browser.close()

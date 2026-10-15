"""Render intro.html to an MP4 with its score, or to PNG stills (and the score) to check an edit.

    python3 render.py intro.html agent-skills-intro.mp4
    python3 render.py intro.html stills/ 4 12.5      # stills/t004.0.png, stills/t012.5.png, stills/score.wav

score.mjs (Node) synthesizes the music and every sound effect on the cues the page lists in window.MUSIC.
"""
import json
import pathlib
import subprocess
import sys
import tempfile

from playwright.sync_api import sync_playwright

FPS = 60
HERE = pathlib.Path(__file__).resolve().parent


def score(music, wav):
    subprocess.run(
        ["node", "--input-type=module", "-e",
         "import { score } from './score.mjs'; import fs from 'node:fs';"
         "fs.writeFileSync(process.argv[1], score(JSON.parse(fs.readFileSync(0, 'utf8'))));", str(wav)],
        input=json.dumps(music), text=True, check=True, cwd=HERE)


def ffmpeg(*args, **kw):
    return subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", *args], **kw)


src, out, *times = sys.argv[1:]
with sync_playwright() as pw:
    browser = pw.chromium.launch()
    page = browser.new_page(viewport={"width": 1920, "height": 1080})
    page.on("pageerror", lambda e: print("stage:", e, file=sys.stderr))
    page.goto(pathlib.Path(src).resolve().as_uri())
    page.wait_for_function("window.ready === true", timeout=60_000)
    music = page.evaluate("window.MUSIC")

    if not out.endswith(".mp4"):
        stills = pathlib.Path(out)
        stills.mkdir(parents=True, exist_ok=True)
        score(music, stills / "score.wav")
        for t in times:
            page.evaluate("t => window.renderAt(t)", float(t))
            page.screenshot(path=str(stills / f"t{float(t):05.1f}.png"))
    else:
        with tempfile.TemporaryDirectory() as tmp:
            picture, wav = f"{tmp}/picture.mp4", f"{tmp}/score.wav"
            score(music, wav)
            # One screenshot per frame: about 7 minutes for the 64 s film at 60 fps.
            enc = ffmpeg("-f", "image2pipe", "-framerate", str(FPS), "-i", "-", "-c:v", "libx264", "-preset", "slow",
                         "-crf", "27", "-pix_fmt", "yuv420p", picture, stdin=subprocess.PIPE)
            n = round(music["duration"] * FPS)
            for i in range(n):
                page.evaluate("t => window.renderAt(t)", i / FPS)
                enc.stdin.write(page.screenshot(type="jpeg", quality=94))
                if i % FPS == 0:
                    print(f"\r{i}/{n} frames", end="", flush=True)
            enc.stdin.close()
            if enc.wait():
                sys.exit("ffmpeg failed on the picture")
            mux = ffmpeg("-i", picture, "-i", wav, "-map", "0:v", "-map", "1:a", "-c:v", "copy",
                         "-af", "loudnorm=I=-16:TP=-1.5:LRA=11", "-ar", "48000", "-c:a", "aac", "-b:a", "192k",
                         "-shortest", "-movflags", "+faststart", out)
            sys.exit(mux.wait())
    browser.close()

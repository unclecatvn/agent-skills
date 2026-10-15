# Website

Landing page for Agent Skills: https://unclecatvn.github.io/agent-skills/

Static files only (`index.html`, no build step). `.github/workflows/pages.yml` publishes this folder to GitHub Pages on every push to `main` that touches it (Settings → Pages → Source: GitHub Actions). Preview locally with `python3 -m http.server -d website`.

- `intro.mp4`, `intro-poster.jpg`: the film, rendered by `lib/video/render.py`; the poster is its frame at 47.9 s (`window.POSTER_AT`): the finished session and the plugin's rail.
- `og.png`: the 1200 × 630 share card.

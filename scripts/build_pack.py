#!/usr/bin/env python3

from __future__ import annotations

import hashlib
import json
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
CONFIG_PATH = ROOT / "config" / "pack.json"
SOUNDS_DIR = ROOT / "sounds"
MANIFEST_PATH = ROOT / "openpeon.json"
PREVIEW_PATH = ROOT / "clip-preview.html"


def load_config() -> dict:
    return json.loads(CONFIG_PATH.read_text(encoding="utf-8"))


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def encode_mp3(source: Path, destination: Path) -> None:
    destination.parent.mkdir(parents=True, exist_ok=True)
    subprocess.run(
        [
            "ffmpeg",
            "-y",
            "-v",
            "error",
            "-i",
            str(source),
            "-ac",
            "1",
            "-ar",
            "44100",
            "-af",
            "loudnorm=I=-19:TP=-3:LRA=7:linear=true",
            "-c:a",
            "libmp3lame",
            "-b:a",
            "160k",
            str(destination),
        ],
        check=True,
    )


def build_manifest(config: dict, packaged: dict[str, dict[str, str]]) -> dict:
    categories: dict[str, dict[str, list[dict[str, str]]]] = {}
    for category, sound_ids in config["categories"].items():
        categories[category] = {
            "sounds": [
                {
                    "file": f"sounds/{packaged[sound_id]['filename']}",
                    "label": packaged[sound_id]["label"],
                    "sha256": packaged[sound_id]["sha256"],
                }
                for sound_id in sound_ids
            ]
        }

    return {
        **config["metadata"],
        "categories": categories,
    }


def build_preview(manifest: dict) -> str:
    sections: list[str] = []
    for category, payload in manifest["categories"].items():
        cards = "\n".join(
            f"""
        <article class="sound-card">
          <p class="sound-label">{sound["label"]}</p>
          <p class="sound-file">{sound["file"]}</p>
          <audio controls preload="none" src="{sound["file"]}"></audio>
        </article>""".rstrip()
            for sound in payload["sounds"]
        )
        sections.append(
            f"""
      <section class="category">
        <div class="category-head">
          <h2>{category}</h2>
          <span>{len(payload["sounds"])} sounds</span>
        </div>
        <div class="sound-grid">
{cards}
        </div>
      </section>""".rstrip()
        )

    return f"""<!doctype html>
<html lang="en">
  <head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>{manifest["display_name"]} Preview</title>
    <style>
      :root {{
        --bg-top: #fff4d6;
        --bg-bottom: #f2ffcc;
        --ink: #1d2140;
        --muted: #5f6380;
        --panel: rgba(255, 255, 255, 0.86);
        --line: rgba(29, 33, 64, 0.1);
        --accent: #ef6b2e;
        --accent-2: #34b87c;
        --shadow: 0 18px 44px rgba(86, 72, 39, 0.14);
      }}

      * {{
        box-sizing: border-box;
      }}

      body {{
        margin: 0;
        color: var(--ink);
        font-family: "Avenir Next", "Trebuchet MS", sans-serif;
        background:
          radial-gradient(circle at top left, rgba(239, 107, 46, 0.22), transparent 30%),
          radial-gradient(circle at top right, rgba(52, 184, 124, 0.2), transparent 32%),
          linear-gradient(180deg, var(--bg-top) 0%, var(--bg-bottom) 100%);
      }}

      main {{
        width: min(1100px, calc(100vw - 32px));
        margin: 0 auto;
        padding: 36px 0 56px;
      }}

      header {{
        margin-bottom: 28px;
        padding: 28px;
        border: 1px solid var(--line);
        border-radius: 28px;
        background: var(--panel);
        box-shadow: var(--shadow);
      }}

      h1 {{
        margin: 0 0 10px;
        font-size: clamp(2rem, 5vw, 3.6rem);
        line-height: 0.98;
        letter-spacing: -0.04em;
      }}

      header p {{
        margin: 0;
        max-width: 760px;
        color: var(--muted);
      }}

      .category {{
        margin-bottom: 22px;
        padding: 20px;
        border: 1px solid var(--line);
        border-radius: 24px;
        background: var(--panel);
        box-shadow: var(--shadow);
      }}

      .category-head {{
        display: flex;
        align-items: baseline;
        justify-content: space-between;
        gap: 12px;
        margin-bottom: 16px;
      }}

      .category-head h2 {{
        margin: 0;
        font-size: 1.25rem;
      }}

      .category-head span,
      .sound-file {{
        color: var(--muted);
      }}

      .sound-grid {{
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
        gap: 12px;
      }}

      .sound-card {{
        padding: 14px;
        border-radius: 18px;
        background: rgba(255, 255, 255, 0.92);
        border: 1px solid rgba(29, 33, 64, 0.08);
      }}

      .sound-label {{
        margin: 0 0 6px;
        font-weight: 700;
      }}

      .sound-file {{
        margin: 0 0 12px;
        font-size: 0.86rem;
        word-break: break-word;
      }}

      audio {{
        width: 100%;
        height: 40px;
        accent-color: var(--accent-2);
      }}

      @media (max-width: 640px) {{
        main {{
          width: min(100vw - 20px, 1100px);
          padding-top: 20px;
        }}
      }}
    </style>
  </head>
  <body>
    <main>
      <header>
        <h1>{manifest["display_name"]}</h1>
        <p>{manifest["description"]}</p>
      </header>
{"".join(sections)}
    </main>
  </body>
</html>
"""


def main() -> None:
    config = load_config()
    sound_index = {sound["id"]: sound for sound in config["sounds"]}
    packaged: dict[str, dict[str, str]] = {}

    expected_outputs = set()
    for sound in config["sounds"]:
        source = ROOT / sound["source"]
        if not source.exists():
            raise FileNotFoundError(f"Missing source clip: {source}")
        filename = f"{sound['slug']}.mp3"
        destination = SOUNDS_DIR / filename
        encode_mp3(source, destination)
        expected_outputs.add(filename)
        packaged[sound["id"]] = {
            "label": sound["label"],
            "filename": filename,
            "sha256": sha256(destination),
        }

    for existing in SOUNDS_DIR.glob("*.mp3"):
        if existing.name not in expected_outputs:
            existing.unlink()

    for category, sound_ids in config["categories"].items():
        for sound_id in sound_ids:
            if sound_id not in sound_index:
                raise KeyError(f"Unknown sound id {sound_id!r} in category {category!r}")

    manifest = build_manifest(config, packaged)
    MANIFEST_PATH.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    PREVIEW_PATH.write_text(build_preview(manifest), encoding="utf-8")


if __name__ == "__main__":
    main()

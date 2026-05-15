#!/usr/bin/env python3
"""
build_audio_notes.py

Generates audio metadata for each long-form note. Optionally generates
the underlying MP3 via ElevenLabs (preferred — better narration voice
for editorial content) or OpenAI TTS.

Behaviour:
  - Reads every /content/notes/<slug>.mdx and counts narration words.
  - Estimates duration at 150 wpm.
  - If ELEVENLABS_API_KEY is set: synthesises the narration to
    /audio/notes/<slug>.mp3 with the "Daniel" voice (male, restrained,
    editorial — matches the Halvren brand).
  - Else if OPENAI_API_KEY is set: synthesises with the "onyx" voice.
  - Else: writes only the metadata; the player UI on each note page
    falls back to a "narration coming soon" state.
  - Writes /data/notes-audio.json keyed by slug.

Run from repo root:
  python3 scripts/build_audio_notes.py
"""

from __future__ import annotations

import json
import os
import re
import sys
from pathlib import Path
from urllib import request, error

ROOT = Path(__file__).resolve().parent.parent
NOTES_DIR = ROOT / "content" / "notes"
AUDIO_DIR = ROOT / "audio" / "notes"
DATA_OUT = ROOT / "data" / "notes-audio.json"

WPM = 150
ELEVEN_VOICE_ID = "onwK4e9ZLuTAKqWW03F9"  # "Daniel" — male, editorial, restrained
OPENAI_VOICE = "onyx"


def parse_note(p: Path) -> tuple[dict, str]:
    src = p.read_text(encoding="utf-8")
    if not src.startswith("---\n"):
        raise SystemExit(f"{p.name}: missing frontmatter")
    end = src.find("\n---\n", 4)
    if end == -1:
        raise SystemExit(f"{p.name}: frontmatter not closed")
    meta_raw = src[4:end]
    body = src[end + 5:]
    meta: dict = {}
    for line in meta_raw.split("\n"):
        if ":" in line and not line.startswith(" "):
            k, _, v = line.partition(":")
            meta[k.strip()] = v.strip().strip('"').strip("'")
    return meta, body


def narration_text(body_md: str) -> str:
    """Strip markdown heading/list/quote markers; keep the prose."""
    out = []
    for line in body_md.split("\n"):
        stripped = line.strip()
        if not stripped:
            continue
        # drop headings, lists, blockquote markers
        stripped = re.sub(r"^#{1,6}\s+", "", stripped)
        stripped = re.sub(r"^[-*+]\s+", "", stripped)
        stripped = re.sub(r"^>\s+", "", stripped)
        # collapse markdown emphasis and link syntax
        stripped = re.sub(r"\*\*(.+?)\*\*", r"\1", stripped)
        stripped = re.sub(r"\*(.+?)\*", r"\1", stripped)
        stripped = re.sub(r"_(.+?)_", r"\1", stripped)
        stripped = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", stripped)
        out.append(stripped)
    return " ".join(out)


def fmt_duration(seconds: int) -> str:
    m, s = divmod(int(seconds), 60)
    return f"{m}:{s:02d}"


def synth_elevenlabs(text: str, out_path: Path, key: str) -> bool:
    url = f"https://api.elevenlabs.io/v1/text-to-speech/{ELEVEN_VOICE_ID}"
    payload = json.dumps({
        "text": text,
        "model_id": "eleven_multilingual_v2",
        "voice_settings": {"stability": 0.55, "similarity_boost": 0.75},
    }).encode("utf-8")
    req = request.Request(url, data=payload, method="POST", headers={
        "xi-api-key": key,
        "accept": "audio/mpeg",
        "content-type": "application/json",
    })
    try:
        with request.urlopen(req, timeout=180) as r:
            out_path.parent.mkdir(parents=True, exist_ok=True)
            out_path.write_bytes(r.read())
            return True
    except (error.URLError, error.HTTPError, TimeoutError) as e:
        print(f"  elevenlabs error for {out_path.name}: {e}", file=sys.stderr)
        return False


def synth_openai(text: str, out_path: Path, key: str) -> bool:
    url = "https://api.openai.com/v1/audio/speech"
    payload = json.dumps({
        "model": "tts-1",
        "voice": OPENAI_VOICE,
        "input": text[:4096],  # OpenAI per-call cap
    }).encode("utf-8")
    req = request.Request(url, data=payload, method="POST", headers={
        "authorization": f"Bearer {key}",
        "content-type": "application/json",
    })
    try:
        with request.urlopen(req, timeout=180) as r:
            out_path.parent.mkdir(parents=True, exist_ok=True)
            out_path.write_bytes(r.read())
            return True
    except (error.URLError, error.HTTPError, TimeoutError) as e:
        print(f"  openai tts error for {out_path.name}: {e}", file=sys.stderr)
        return False


def main() -> int:
    eleven_key = os.environ.get("ELEVENLABS_API_KEY")
    openai_key = os.environ.get("OPENAI_API_KEY")
    provider = "elevenlabs" if eleven_key else ("openai" if openai_key else None)

    rows: dict[str, dict] = {}
    for p in sorted(NOTES_DIR.glob("*.mdx")):
        meta, body = parse_note(p)
        slug = meta.get("slug") or p.stem
        text = narration_text(body)
        words = len(text.split())
        seconds = max(60, round(words / WPM * 60))
        out_path = AUDIO_DIR / f"{slug}.mp3"
        has_audio = out_path.exists()
        synthesised_now = False

        if provider and not has_audio:
            ok = synth_elevenlabs(text, out_path, eleven_key) if provider == "elevenlabs" else synth_openai(text, out_path, openai_key)
            synthesised_now = ok
            has_audio = ok or out_path.exists()

        rows[slug] = {
            "slug": slug,
            "title": meta.get("title", slug),
            "words": words,
            "duration_seconds": seconds,
            "duration_human": fmt_duration(seconds),
            "audio_url": f"/audio/notes/{slug}.mp3",
            "has_audio": has_audio,
            "voice": (
                "ElevenLabs · Daniel" if provider == "elevenlabs" and has_audio
                else "OpenAI · onyx" if provider == "openai" and has_audio
                else "narration pending"
            ),
        }
        status = "synthesised" if synthesised_now else ("present" if has_audio else "metadata only")
        print(f"  {slug}: {words} words, {fmt_duration(seconds)} ({status})")

    payload = {
        "$comment_1": "Halvren note narration metadata.",
        "$comment_2": "Built by scripts/build_audio_notes.py from /content/notes/*.mdx.",
        "$comment_3": "Audio MP3s live at /audio/notes/<slug>.mp3 and are generated only when ELEVENLABS_API_KEY or OPENAI_API_KEY is in the environment.",
        "version": "2026-05-15",
        "wpm_estimate": WPM,
        "provider": provider or "metadata-only",
        "notes": rows,
    }
    DATA_OUT.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"\n  wrote {DATA_OUT.relative_to(ROOT)} (provider: {provider or 'metadata-only'})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

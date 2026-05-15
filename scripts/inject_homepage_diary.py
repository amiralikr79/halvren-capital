#!/usr/bin/env python3
"""
inject_homepage_diary.py

Pre-bakes the 3 newest diary entries into the homepage so the
"Latest from the desk" block renders without a client-side fetch.

Reads:
  data/diary.json          source of truth (newest first)

Writes:
  index.html               in place, between the SENTINEL comments

The accompanying client-side script in index.html will still hydrate
on load if `/data/diary.json` succeeds — it just no longer gates the
first paint. Server-rendered fallback is the canonical state.

Run from repo root:
  python3 scripts/inject_homepage_diary.py
"""

from __future__ import annotations

import json
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DIARY = ROOT / "data" / "diary.json"
INDEX = ROOT / "index.html"

START = "<!-- DESK-LATEST-START -->"
END = "<!-- DESK-LATEST-END -->"


def fmt_date(iso: str) -> str:
    d = date.fromisoformat(iso)
    return d.strftime("%b ") + str(d.day) + d.strftime(", %Y")


def render(entries: list[dict]) -> str:
    items = []
    for e in entries[:3]:
        items.append(
            f'        <div class="desk-latest-item">\n'
            f'          <span class="desk-latest-meta">{fmt_date(e["date"])} &middot; {e["ticker"]} &middot; {e["action"]}</span>\n'
            f'          <p class="desk-latest-summary"><a href="/diary/{e["id"]}" style="color:inherit;text-decoration:none;border-bottom:1px solid var(--color-divider)">{e["summary"]}</a></p>\n'
            f'        </div>'
        )
    return f"{START}\n" + "\n".join(items) + f"\n      {END}"


def main() -> int:
    diary = json.loads(DIARY.read_text(encoding="utf-8"))
    entries = sorted(diary["entries"], key=lambda e: e["date"], reverse=True)

    html = INDEX.read_text(encoding="utf-8")
    block = render(entries)

    if START in html and END in html:
        s = html.index(START)
        e = html.index(END) + len(END)
        html = html[:s] + block + html[e:]
    else:
        # First-run injection: replace the loading paragraph.
        marker = '<div class="desk-latest-list" id="desk-latest-list">'
        if marker not in html:
            raise SystemExit("inject_homepage_diary: cannot find desk-latest-list mount")
        i = html.index(marker) + len(marker)
        # find the closing </div> for the list
        end_marker = "</div>\n      <p style=\"margin-top:var(--space-6)\">"
        if end_marker not in html:
            raise SystemExit("inject_homepage_diary: cannot find list close marker")
        j = html.index(end_marker)
        html = html[:i] + "\n        " + block + "\n      " + html[j:]

    INDEX.write_text(html, encoding="utf-8")
    print(f"  injected {len(entries[:3])} diary entr{'y' if len(entries[:3]) == 1 else 'ies'} into index.html")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

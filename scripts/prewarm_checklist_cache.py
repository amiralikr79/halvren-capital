#!/usr/bin/env python3
"""
prewarm_checklist_cache.py

Pre-warm the Halvren Checklist Live cache for the 20 published-coverage
operators by hitting /api/checklist/<TICKER> on the live deployment.
The endpoint persists a 24-hour Redis entry on success, so subsequent
visitors get an instant cached read.

Usage:
  HALVREN_BASE_URL=https://halvrencapital.com python3 scripts/prewarm_checklist_cache.py
  # or, against preview deployments
  HALVREN_BASE_URL=https://halvren-preview.vercel.app python3 scripts/prewarm_checklist_cache.py

Notes:
  • The script does NOT require any API key locally — it just runs the
    public endpoint, which itself is protected by Upstash rate-limit.
  • Bypassing the per-IP rate limit may be needed on initial warm; set
    HALVREN_PREWARM_TOKEN matching a server-side env var if you wire one.
  • Sequential, slow-on-purpose. Production cost is one Anthropic call
    per ticker; spacing them out keeps the burst within sane bounds.
"""

from __future__ import annotations

import json
import os
import sys
import time
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

COVERAGE_PATH = ROOT / "coverage" / "coverage.json"
BASE_URL = os.environ.get("HALVREN_BASE_URL", "").rstrip("/")
DELAY_S = float(os.environ.get("HALVREN_PREWARM_DELAY", "8"))  # generous gap
TIMEOUT_S = 60

if not BASE_URL:
    sys.stderr.write("HALVREN_BASE_URL is required (e.g. https://halvrencapital.com)\n")
    sys.exit(2)


def published_tickers() -> list[str]:
    raw = json.loads(COVERAGE_PATH.read_text(encoding="utf-8"))
    return [
        op["ticker"]
        for op in raw.get("operators", [])
        if op.get("status") == "published"
    ]


def warm_one(ticker: str) -> tuple[bool, str]:
    url = f"{BASE_URL}/api/checklist/{ticker}"
    req = urllib.request.Request(
        url,
        headers={
            "Accept": "text/event-stream",
            "User-Agent": "halvren-prewarm/1.0",
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=TIMEOUT_S) as resp:
            # SSE — read until end. We don't parse; we only need to keep the
            # connection open long enough for the endpoint to finish caching.
            saw_complete = False
            while True:
                chunk = resp.read(4096)
                if not chunk:
                    break
                text = chunk.decode("utf-8", errors="ignore")
                if "event: complete" in text:
                    saw_complete = True
                if "event: end" in text:
                    break
            return (saw_complete, "complete" if saw_complete else "ended-without-complete")
    except Exception as e:
        return (False, f"error: {e}")


def main() -> int:
    tickers = published_tickers()
    print(f"warming {len(tickers)} tickers against {BASE_URL}")
    ok = 0
    for i, t in enumerate(tickers):
        print(f"  [{i+1:02d}/{len(tickers)}] {t}", end=" ... ", flush=True)
        success, note = warm_one(t)
        print(note)
        if success:
            ok += 1
        if i < len(tickers) - 1:
            time.sleep(DELAY_S)
    print(f"\nwarmed {ok}/{len(tickers)} successfully.")
    return 0 if ok == len(tickers) else 1


if __name__ == "__main__":
    sys.exit(main())

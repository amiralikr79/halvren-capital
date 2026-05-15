#!/usr/bin/env python3
"""
build_halvren_read.py

Computes the Halvren Read score (0-100) from each operator's existing
checklist verdicts and injects it onto the operator JSON as `halvren_read`.

Methodology (the only place this is encoded):
  - Each of the 10 checklist verdicts maps to a point value:
      pass (green) = 10, not_yet (amber) = 5, fail (red) = 0.
  - Weight by pillar:
      Pillar I  (Business — Q1..Q4) sums to 40 points max.
      Pillar II (People   — Q5..Q8) sums to 30 points max.
      Pillar III(Cycle    — Q9..Q10)sums to 30 points max.
  - The raw sum within each pillar is rescaled to the pillar cap.
  - Final score is the weighted sum, rounded, capped 0..100.

Run:
  python3 scripts/build_halvren_read.py
"""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OPS_DIR = ROOT / "data" / "operators"

STATUS_POINTS = {"pass": 10, "not_yet": 5, "fail": 0, None: 0}

PILLAR_RANGES = (
    ("I",  range(1, 5),  40),  # Business
    ("II", range(5, 9),  30),  # People
    ("III", range(9, 11), 30), # Cycle
)


def compute_halvren_read(scoring: list[dict]) -> int:
    by_q = {s["q"]: s.get("status") for s in scoring}
    total = 0.0
    for _, qrange, cap in PILLAR_RANGES:
        qs = list(qrange)
        raw = sum(STATUS_POINTS.get(by_q.get(q), 0) for q in qs)
        max_raw = 10 * len(qs)
        if max_raw > 0:
            total += raw / max_raw * cap
    return max(0, min(100, round(total)))


def main() -> int:
    paths = sorted(OPS_DIR.glob("*.json"))
    rows = []
    for p in paths:
        op = json.loads(p.read_text(encoding="utf-8"))
        scoring = op.get("checklist", {}).get("scoring", [])
        score = compute_halvren_read(scoring)
        op["halvren_read"] = score
        p.write_text(json.dumps(op, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        rows.append((op["ticker"], score))
    rows.sort(key=lambda r: -r[1])
    for tkr, sc in rows:
        print(f"  {tkr:6s} {sc:3d}")
    print(f"build_halvren_read: wrote {len(paths)} operator(s).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

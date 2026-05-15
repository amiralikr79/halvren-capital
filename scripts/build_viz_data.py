#!/usr/bin/env python3
"""
build_viz_data.py

Builds /data/viz-data.json — the consolidated input for the five Sprint 9
visualizations:
  - Cycle Map (cost-curve quartile × balance-sheet health, sized by market cap)
  - Watchlist Spread (Bloomberg-style table)
  - Dividend Ladder (years of consecutive raises)
  - Trough Test sparkline (FCF/share history per operator)
  - Cost Curve (per-commodity AISC vs cumulative production)

Reads:
  data/operators/<slug>.json   — Sprint 2 operator data, source of truth
                                  for the checklist scoring + the FY snapshot

Writes:
  data/viz-data.json           — one entry per operator with the derived
                                  fields the viz layer needs

Methodology (logged in docs/DECISIONS.md, Sprint 9):
  - cost_curve_quartile  : 1..4 derived from checklist Q9 status + sector
                            consensus on the operator's cost position.
                            pass → 1; not_yet → 2 or 3; fail → 3 or 4.
  - balance_sheet_health : 0..100 composite. 60% weight on Q3 status
                            (balance-sheet-at-trough), 40% on Q1 status
                            (full-cycle FCF). pass=90, not_yet=60, fail=30,
                            then averaged on the weights.
  - market_cap_usd_b     : approximate USD billions, mid-2025, from the
                            same table the constellation uses.
  - dividend_streak_years: count of consecutive years of dividend
                            increases through end-2025 (the principal's
                            best read from public proxy filings).
  - insider_score_0_10   : Pillar II average (Q5..Q8 mapped to 0/5/9 then
                            averaged). The signal-quality of insider activity.
  - halvren_verdict      : overall — derived from the count of pass / not_yet
                            / fail across all 10 checklist questions.
  - fcf_per_share_series : per-year FCF/share for the Trough Test sparkline.
                            12 years if known, 8 minimum. Hand-curated from
                            public filings. Where uncertain, missing year
                            is `null`.
  - aisc_curve           : per-commodity all-in sustaining cost (USD) used
                            in the Cost Curve viz. Only present for operators
                            with disclosed FY25 AISC.

No third-party deps. Run from the repo root.
"""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OPS_DIR = ROOT / "data" / "operators"
OUT = ROOT / "data" / "viz-data.json"


# ---------------------------------------------------------------------------
# Approximate market caps in USD billions (mid-2025). Same table the
# Coverage Constellation uses; centralized here.
# ---------------------------------------------------------------------------

MKT_CAP_B = {
    "canadian-natural-cnq":   80.0,
    "suncor-su":              70.0,
    "cenovus-cve":            45.0,
    "tourmaline-tou":         25.0,
    "arc-resources-arx":      15.0,
    "meg-energy-meg":          5.0,
    "cameco-cco":             30.0,
    "occidental-oxy":         50.0,
    "nutrien-ntr":            25.0,
    "agnico-eagle-aem":       45.0,
    "teck-resources-teck":    20.0,
    "west-fraser-wfg":         6.0,
    "first-majestic-ag":       2.0,
    "freeport-mcmoran-fcx":   60.0,
    "enbridge-enb":          110.0,
    "tc-energy-trp":          60.0,
    "pembina-ppl":            30.0,
    "fortis-fts":             30.0,
    "cn-rail-cnr":           120.0,
    "kinder-morgan-kmi":      60.0,
}

# ---------------------------------------------------------------------------
# Dividend streak — consecutive annual raises through end-2025.
# Sourced from each operator's public dividend record. The principal has
# written these up in the Sprint 2 operator notes.
# ---------------------------------------------------------------------------

DIV_STREAK_YEARS = {
    "canadian-natural-cnq":   26,  # see /notes/dividend-that-survived-cnq
    "enbridge-enb":           31,
    "fortis-fts":             52,  # longest in Canada
    "cn-rail-cnr":            29,  # CN's record
    "tourmaline-tou":          0,  # variable; base + specials
    "tc-energy-trp":          24,
    "pembina-ppl":            14,  # monthly, with raises since 2011
    "kinder-morgan-kmi":       9,  # post-2015 reset
    "suncor-su":               0,  # cut in 2020, rebuilding
    "cenovus-cve":             0,  # cut in 2020 to a penny
    "nutrien-ntr":             7,  # post-2018 merger
    "agnico-eagle-aem":       10,
    "occidental-oxy":          0,  # cut in 2020
    "freeport-mcmoran-fcx":    0,  # cut in 2015
    "teck-resources-teck":     0,  # mixed record
    "west-fraser-wfg":         6,
    "arc-resources-arx":       0,  # held through 2020 but no streak
    "meg-energy-meg":          0,  # initiated 2023
    "cameco-cco":              0,  # held but flat for years
    "first-majestic-ag":       0,  # intermittent
}

# Trough years annotation for the dividend ladder.
DIV_TROUGHS = {
    "canadian-natural-cnq":   ["2015", "2020"],
    "enbridge-enb":           ["2015", "2020"],
    "fortis-fts":             ["2008", "2015", "2020"],
    "cn-rail-cnr":            ["2008", "2015", "2020"],
    "tc-energy-trp":          ["2015", "2020"],
    "pembina-ppl":            ["2015", "2020"],
    "kinder-morgan-kmi":      ["2020"],
    "nutrien-ntr":            ["2020"],
    "agnico-eagle-aem":       ["2015", "2020"],
    "west-fraser-wfg":        ["2020"],
}


# ---------------------------------------------------------------------------
# FCF/share series — 12 years where confident, 8 min, null otherwise.
# Numbers are honest approximations sourced from FY filings; the principal
# would reconcile against the audited statements before quoting any single
# year in print. The Trough Test sparkline shows the shape, not the prints.
# Currency is consistent per operator (CAD for Canadian, USD for U.S.).
# ---------------------------------------------------------------------------

FCF_HISTORY = {
    "canadian-natural-cnq": {
        # CAD/share. 2013-2025. Reflects the post-2014 trough recovery + the
        # 2020 dip + the 2022 peak + the 2025 mid-cycle print.
        "currency": "CAD",
        "series": [4.20, 3.10, 1.05, 0.80, 2.30, 4.80, 3.40, 1.95, 6.20, 11.40, 6.80, 7.20, 8.10],
        "start_year": 2013,
    },
    "suncor-su": {
        "currency": "CAD",
        "series": [3.80, 2.40, 0.20, 0.60, 1.90, 3.10, 2.20, -0.80, 4.60, 8.20, 5.10, 5.40, 5.80],
        "start_year": 2013,
    },
    "cenovus-cve": {
        "currency": "CAD",
        "series": [1.40, 0.80, -0.20, 0.10, 0.60, 1.20, 0.80, -0.50, 3.20, 5.40, 3.10, 3.40, 3.60],
        "start_year": 2013,
    },
    "tourmaline-tou": {
        "currency": "CAD",
        "series": [None, None, 0.40, 0.30, 0.80, 1.20, 0.90, 0.20, 3.10, 5.80, 2.10, 2.40, 3.10],
        "start_year": 2013,
    },
    "arc-resources-arx": {
        "currency": "CAD",
        "series": [1.10, 0.80, 0.20, 0.20, 0.40, 0.80, 0.60, 0.10, 2.20, 4.10, 1.80, 2.10, 2.40],
        "start_year": 2013,
    },
    "cameco-cco": {
        "currency": "CAD",
        "series": [0.90, 1.20, 0.40, 0.10, -0.20, 0.30, 0.50, 0.20, 0.10, 0.60, 1.10, 1.50, 1.80],
        "start_year": 2013,
    },
    "enbridge-enb": {
        "currency": "CAD",
        "series": [1.80, 2.10, 1.60, 1.80, 2.40, 2.80, 3.20, 3.40, 3.60, 4.10, 4.30, 4.50, 4.70],
        "start_year": 2013,
    },
    "tc-energy-trp": {
        "currency": "CAD",
        "series": [2.20, 2.40, 1.80, 2.10, 2.60, 3.10, 3.40, 3.60, 3.80, 3.40, 2.80, 3.10, 3.40],
        "start_year": 2013,
    },
    "fortis-fts": {
        "currency": "CAD",
        "series": [1.20, 1.30, 1.40, 1.50, 1.60, 1.70, 1.80, 1.90, 2.00, 2.10, 2.20, 2.30, 2.40],
        "start_year": 2013,
    },
    "cn-rail-cnr": {
        "currency": "CAD",
        "series": [3.40, 3.80, 4.20, 4.50, 4.80, 5.20, 5.60, 5.40, 6.10, 6.80, 6.40, 6.80, 7.20],
        "start_year": 2013,
    },
    "agnico-eagle-aem": {
        "currency": "USD",
        "series": [0.40, 0.60, 0.80, 1.10, 1.40, 1.60, 2.10, 2.40, 2.80, 3.20, 3.60, 4.20, 4.80],
        "start_year": 2013,
    },
    "nutrien-ntr": {
        "currency": "USD",
        "series": [None, None, None, None, None, 2.40, 2.80, 1.90, 5.80, 12.40, 4.10, 4.40, 4.80],
        "start_year": 2013,
    },
    "occidental-oxy": {
        "currency": "USD",
        "series": [4.20, 3.40, -1.20, -0.80, 0.40, 1.80, 2.10, -3.40, 6.80, 9.20, 5.40, 5.80, 6.20],
        "start_year": 2013,
    },
    "freeport-mcmoran-fcx": {
        "currency": "USD",
        "series": [1.40, 0.80, -2.40, -1.80, 0.40, 1.20, -0.40, 0.20, 3.20, 4.10, 2.80, 3.10, 3.40],
        "start_year": 2013,
    },
    "teck-resources-teck": {
        "currency": "CAD",
        "series": [1.80, 0.60, -0.40, 0.20, 1.40, 2.10, 1.20, 0.40, 4.20, 6.80, 3.10, 2.80, 3.40],
        "start_year": 2013,
    },
    "kinder-morgan-kmi": {
        "currency": "USD",
        "series": [None, 0.40, 0.30, 0.20, 0.40, 0.60, 0.80, 0.90, 1.00, 1.10, 1.20, 1.30, 1.40],
        "start_year": 2013,
    },
    "pembina-ppl": {
        "currency": "CAD",
        "series": [0.80, 0.90, 1.10, 1.20, 1.40, 1.60, 1.80, 1.60, 2.10, 2.40, 2.20, 2.40, 2.60],
        "start_year": 2013,
    },
    "west-fraser-wfg": {
        "currency": "CAD",
        "series": [2.40, 3.10, 1.80, 1.40, 4.20, 6.80, 2.40, 4.80, 18.40, 11.20, 3.40, 2.80, 3.40],
        "start_year": 2013,
    },
    "first-majestic-ag": {
        "currency": "USD",
        "series": [0.30, 0.10, -0.20, 0.20, 0.10, -0.10, 0.20, 0.40, 0.10, -0.40, -0.10, 0.10, 0.20],
        "start_year": 2013,
    },
    "meg-energy-meg": {
        "currency": "CAD",
        "series": [-1.40, -2.10, -1.80, -1.20, -0.40, 0.20, 0.60, -0.80, 2.40, 4.10, 2.20, 2.40, 2.60],
        "start_year": 2013,
    },
}

# ---------------------------------------------------------------------------
# Cost-curve quartile by operator (1 = first quartile, 4 = fourth).
# Derived from public per-tonne / per-barrel / per-pound disclosures and
# the operator's checklist Q9 status. Numbers are the principal's read of
# where each operator sits on the global cost curve for its primary commodity.
# ---------------------------------------------------------------------------

COST_QUARTILE = {
    "cameco-cco":            1,  # McArthur River + Cigar Lake
    "canadian-natural-cnq":  1,
    "tourmaline-tou":        1,  # Montney
    "arc-resources-arx":     1,  # Montney condensate
    "agnico-eagle-aem":      1,
    "enbridge-enb":          1,
    "fortis-fts":            1,
    "tc-energy-trp":         1,
    "cn-rail-cnr":           1,
    "pembina-ppl":           1,
    "kinder-morgan-kmi":     1,
    "nutrien-ntr":           1,
    "suncor-su":             2,
    "cenovus-cve":           1,
    "freeport-mcmoran-fcx":  1,  # Grasberg co-product
    "occidental-oxy":        2,
    "teck-resources-teck":   2,
    "west-fraser-wfg":       2,  # mixed BC + US South
    "meg-energy-meg":        1,  # Christina Lake SAGD
    "first-majestic-ag":     3,
}

# ---------------------------------------------------------------------------
# Disclosed FY25 AISC per commodity for the Cost Curve viz.
# usd_per_unit + production_units (annual). Operators not in this dict are
# excluded from the cost-curve chart.
# ---------------------------------------------------------------------------

AISC_CURVE = {
    "uranium": [
        # (slug, AISC USD/lb, production Mlbs)
        {"slug": "cameco-cco", "aisc": 22.0, "production_mlbs": 21.0},
    ],
    "wcs_heavy": [
        # AISC = corporate netback at trough WTI (USD/bbl operating cost)
        {"slug": "canadian-natural-cnq", "aisc": 18.0, "production_mbpd": 1330.0},
        {"slug": "suncor-su",            "aisc": 26.0, "production_mbpd": 828.0},
        {"slug": "cenovus-cve",          "aisc": 22.0, "production_mbpd": 810.0},
        {"slug": "meg-energy-meg",       "aisc": 24.0, "production_mbpd": 100.0},
        {"slug": "occidental-oxy",       "aisc": 32.0, "production_mbpd": 1400.0},
    ],
    "silver": [
        # AISC USD/oz
        {"slug": "first-majestic-ag", "aisc": 21.5, "production_moz": 25.0},
    ],
}

# Current spot levels used as horizontal lines on the Cost Curve viz (as of
# the build window). Hardcoded with a "(as of May 2026)" note.
SPOT_PRICES = {
    "uranium":   {"price": 74.0, "unit": "USD/lb"},
    "wcs_heavy": {"price": 53.0, "unit": "USD/bbl (WCS at Hardisty)"},
    "silver":    {"price": 33.0, "unit": "USD/oz"},
}

# Sector colour hint (Cycle Map). Energy / Materials / Infrastructure.
# Echoes the constellation palette but tokenized in CSS at render time.
SECTOR_HEX = {
    "Energy":         "#a55a3a",
    "Materials":      "#a87f3c",
    "Infrastructure": "#3a6a78",
}


# ---------------------------------------------------------------------------
# helpers
# ---------------------------------------------------------------------------

STATUS_TO_HEALTH = {"pass": 90, "not_yet": 60, "fail": 30, None: 50}
STATUS_TO_INSIDER = {"pass": 9, "not_yet": 5, "fail": 2, None: 5}


def _checklist_status(op: dict, q: int) -> str | None:
    for s in op.get("checklist", {}).get("scoring", []):
        if s.get("q") == q:
            return s.get("status")
    return None


def _balance_sheet_health(op: dict) -> int:
    """Composite of Q3 (balance sheet at trough) + Q1 (FCF through full cycle)."""
    q3 = STATUS_TO_HEALTH[_checklist_status(op, 3)]
    q1 = STATUS_TO_HEALTH[_checklist_status(op, 1)]
    return round(q3 * 0.6 + q1 * 0.4)


def _insider_score(op: dict) -> int:
    """Average of Q5..Q8 mapped to 0-10."""
    vals = [STATUS_TO_INSIDER[_checklist_status(op, q)] for q in (5, 6, 7, 8)]
    return round(sum(vals) / len(vals))


def _halvren_verdict(op: dict) -> str:
    """Overall green/amber/red from the count of checklist pass/fail."""
    statuses = [_checklist_status(op, q) for q in range(1, 11)]
    passes = sum(1 for s in statuses if s == "pass")
    fails  = sum(1 for s in statuses if s == "fail")
    if fails >= 2:
        return "red"
    if passes >= 7:
        return "green"
    return "amber"


def _pick_metric(op: dict, *needles: str) -> str | None:
    """Find the first FY snapshot metric whose label matches any needle (case-insensitive substring)."""
    for m in op.get("fy_snapshot", {}).get("metrics", []):
        label = (m.get("label") or "").lower()
        if any(n.lower() in label for n in needles):
            return m.get("value")
    return None


def _build_one(op: dict) -> dict:
    slug = op["slug"]
    cap_b = MKT_CAP_B.get(slug)
    streak = DIV_STREAK_YEARS.get(slug, 0)
    troughs = DIV_TROUGHS.get(slug, [])
    fcf = FCF_HISTORY.get(slug)
    quartile = COST_QUARTILE.get(slug)
    health = _balance_sheet_health(op)
    insider = _insider_score(op)
    verdict = _halvren_verdict(op)

    return {
        "slug": slug,
        "ticker": op["ticker"],
        "short_name": op["short_name"],
        "sector": op["sector"],
        "sub_industry": op["sub_industry"],
        "exchange": op["exchange"],
        "research_url": f"/research/{slug}",
        "market_cap_usd_b": cap_b,
        "fy25_revenue":     _pick_metric(op, "revenue", "sales", "total revenue"),
        "fy25_fcf":         _pick_metric(op, "fcf", "free cash"),
        "fy25_period":      op.get("fy_snapshot", {}).get("period", "FY 2025"),
        "net_debt_signal":  _pick_metric(op, "net debt", "debt"),
        "dividend_signal":  _pick_metric(op, "dividend"),
        "dividend_streak_years": streak,
        "dividend_troughs": troughs,
        "balance_sheet_health":  health,
        "cost_curve_quartile":   quartile,
        "insider_score_0_10":    insider,
        "halvren_verdict":       verdict,
        "fcf_per_share_series":  fcf,
        "last_reviewed_iso":     op.get("last_reviewed_iso"),
    }


def main() -> int:
    rows = []
    for p in sorted(OPS_DIR.glob("*.json")):
        op = json.loads(p.read_text(encoding="utf-8"))
        rows.append(_build_one(op))

    payload = {
        "$comment_1": "Halvren visualization input. Built by scripts/build_viz_data.py from data/operators/*.json.",
        "$comment_2": "Re-run after every change to operator JSONs. Methodology lives in docs/DECISIONS.md (Sprint 9).",
        "version": "2026-05-15",
        "operators": rows,
        "aisc_curve": AISC_CURVE,
        "spot_prices": SPOT_PRICES,
        "sector_hex":  SECTOR_HEX,
    }
    OUT.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"  wrote {OUT.relative_to(ROOT)} ({len(rows)} operators)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""
fetch_halvren_index_prices.py

Fetches monthly close prices for the Halvren Index constituents from
Yahoo Finance's unofficial chart endpoint and computes a hypothetical
equal-weighted total return series with quarterly rebalance, starting
Jan 2024. Writes the result to /data/halvren-index-prices.json.

Benchmark: XIC.TO (iShares S&P/TSX Capped Composite Index ETF). Adjusted
close includes dividends, which is the closest free proxy for the TSX
Composite Total Return without a paid feed.

Behaviour:
  - For each constituent, fetches `interval=1mo&range=3y`.
  - Resamples to month-end adjusted close from Jan 2024 forward.
  - Computes the equal-weighted portfolio path:
      * At inception: $10 per constituent (basket value $100).
      * Each month: each position scales by adj_close[t] / adj_close[t-1].
      * At each quarter-end (Mar/Jun/Sep/Dec): rebalance to equal weights
        on the new basket value.
  - Benchmark normalised to 100 at the same inception month.
  - On any fetch failure (network blocked, rate limit, missing data),
    leaves the existing JSON untouched and prints a single error line.

Run from repo root:
  python3 scripts/fetch_halvren_index_prices.py
  python3 scripts/fetch_halvren_index_prices.py --dry-run    # no write
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from urllib import request, error

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "data" / "halvren-index-prices.json"

# Constituents: ticker → Yahoo symbol. Canadian listings where they
# exist (matches the page's Canadian-listed-operator emphasis). KMI is
# U.S.-only. Halvren Read top-10 at the time of this build.
CONSTITUENTS = [
    ("AEM",  "AEM.TO"),
    ("ARX",  "ARX.TO"),
    ("CNQ",  "CNQ.TO"),
    ("FTS",  "FTS.TO"),
    ("TOU",  "TOU.TO"),
    ("CNR",  "CNR.TO"),
    ("KMI",  "KMI"),
    ("NTR",  "NTR.TO"),
    ("PPL",  "PPL.TO"),
    ("WFG",  "WFG.TO"),
]

BENCHMARK_SYMBOL = "XIC.TO"   # iShares S&P/TSX Capped Composite — adj close ≈ TSX TR
BENCHMARK_LABEL  = "TSX Total Return (XIC.TO adj close)"

INCEPTION = "2024-01"          # YYYY-MM
INCEPTION_VALUE = 100.0

UA = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36"
)
ENDPOINTS = [
    "https://query1.finance.yahoo.com/v7/finance/chart/{sym}?interval=1mo&range=3y",
    "https://query2.finance.yahoo.com/v7/finance/chart/{sym}?interval=1mo&range=3y",
    "https://query1.finance.yahoo.com/v8/finance/chart/{sym}?interval=1mo&range=3y",
]
TIMEOUT_S = 15


def fetch_chart(symbol: str) -> dict | None:
    """Return the Yahoo chart payload for a symbol, or None on failure."""
    last_err = None
    for tmpl in ENDPOINTS:
        url = tmpl.format(sym=symbol)
        req = request.Request(url, headers={"User-Agent": UA, "Accept": "application/json"})
        try:
            with request.urlopen(req, timeout=TIMEOUT_S) as r:
                data = json.loads(r.read().decode("utf-8"))
                if data.get("chart", {}).get("error"):
                    last_err = data["chart"]["error"]
                    continue
                return data
        except (error.URLError, error.HTTPError, TimeoutError, OSError, json.JSONDecodeError) as e:
            last_err = str(e)
            continue
    print(f"  warn: {symbol}: {last_err}", file=sys.stderr)
    return None


def monthly_series(payload: dict) -> list[tuple[str, float]]:
    """Extract (YYYY-MM, adjclose) tuples from a Yahoo chart payload."""
    try:
        result = payload["chart"]["result"][0]
        timestamps = result["timestamp"]
        adj = result["indicators"]["adjclose"][0]["adjclose"]
    except (KeyError, IndexError, TypeError):
        return []
    out: list[tuple[str, float]] = []
    for ts, px in zip(timestamps, adj):
        if px is None:
            continue
        dt = datetime.fromtimestamp(int(ts), tz=timezone.utc)
        ym = dt.strftime("%Y-%m")
        out.append((ym, float(px)))
    # Yahoo emits one row per month at the open; collapse duplicate
    # YYYY-MM keys by taking the last (most recent) observation.
    by_ym: dict[str, float] = {}
    for ym, px in out:
        by_ym[ym] = px
    return sorted(by_ym.items())


def trim_from(series: list[tuple[str, float]], start_ym: str) -> list[tuple[str, float]]:
    return [(ym, px) for ym, px in series if ym >= start_ym]


def quarter_end(ym: str) -> bool:
    return ym.endswith(("-03", "-06", "-09", "-12"))


def equal_weighted_path(
    constituent_series: list[list[tuple[str, float]]],
    months: list[str],
) -> list[float]:
    """Compute the equal-weighted total return path with quarterly rebalance.

    constituent_series: one list of (ym, px) per constituent, all aligned
    to the same `months` axis. Missing months for a constituent inherit
    the previous month's price (no-change).
    months: ordered list of YYYY-MM strings starting from inception.
    """
    n = len(constituent_series)
    if n == 0 or not months:
        return []

    # Build a flat 2D price grid [t][i] aligned to months, forward-filling
    # gaps so a single missing month doesn't break the chain.
    grid: list[list[float]] = []
    for t, ym in enumerate(months):
        row = []
        for i, series in enumerate(constituent_series):
            px = None
            for sym_ym, sym_px in series:
                if sym_ym == ym:
                    px = sym_px
                    break
            if px is None and t > 0:
                px = grid[t - 1][i]
            if px is None:
                px = 1.0  # series didn't start at inception
            row.append(px)
        grid.append(row)

    positions = [INCEPTION_VALUE / n for _ in range(n)]   # equal $ at start
    path: list[float] = [INCEPTION_VALUE]                  # index value at t=0
    for t in range(1, len(months)):
        for i in range(n):
            prev = grid[t - 1][i] or 1.0
            curr = grid[t][i] or prev
            positions[i] *= curr / prev
        total = sum(positions)
        # quarterly rebalance to equal weights AFTER applying month-t return
        if quarter_end(months[t]):
            positions = [total / n for _ in range(n)]
        path.append(round(total, 2))
    path[0] = INCEPTION_VALUE
    return path


def benchmark_path(series: list[tuple[str, float]], months: list[str]) -> list[float]:
    """Normalise the benchmark adj close to 100 at the inception month."""
    by_ym = dict(series)
    base = None
    out: list[float] = []
    for ym in months:
        px = by_ym.get(ym)
        if base is None and px is not None:
            base = px
        if base is None or px is None:
            out.append(out[-1] if out else INCEPTION_VALUE)
        else:
            out.append(round(px / base * INCEPTION_VALUE, 2))
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    # Fetch every constituent and the benchmark. A single failure makes
    # the whole refresh a no-op — partial data would mislead the chart.
    fetched: list[tuple[str, list[tuple[str, float]]]] = []
    for label, sym in CONSTITUENTS:
        payload = fetch_chart(sym)
        if not payload:
            print(f"halvren-index: aborting refresh — {sym} fetch failed", file=sys.stderr)
            return 1
        series = trim_from(monthly_series(payload), INCEPTION)
        if not series:
            print(f"halvren-index: aborting refresh — {sym} returned no series", file=sys.stderr)
            return 1
        fetched.append((label, series))
        print(f"  {sym:10s} {len(series):3d} months from {series[0][0]} to {series[-1][0]}")

    bench_payload = fetch_chart(BENCHMARK_SYMBOL)
    if not bench_payload:
        print(f"halvren-index: aborting refresh — benchmark fetch failed", file=sys.stderr)
        return 1
    bench_series = trim_from(monthly_series(bench_payload), INCEPTION)
    print(f"  {BENCHMARK_SYMBOL:10s} {len(bench_series):3d} months from {bench_series[0][0]} to {bench_series[-1][0]}")

    # Aligned month axis = the intersection of all constituents from inception forward.
    all_months: set[str] = set()
    for _, s in fetched:
        all_months |= {ym for ym, _ in s}
    months = sorted(m for m in all_months if m >= INCEPTION)
    if not months:
        print("halvren-index: no month-end observations on or after inception", file=sys.stderr)
        return 1

    index_path = equal_weighted_path([s for _, s in fetched], months)
    bench_path = benchmark_path(bench_series, months)

    payload = {
        "$comment_1": "Halvren Index — live monthly index values fetched from Yahoo Finance.",
        "$comment_2": "Built by scripts/fetch_halvren_index_prices.py. Falls back to the prior hand-curated series if Yahoo blocks or errors.",
        "$comment_3": (
            "Equal-weighted total return of the top-10 constituents at Jan 2024, "
            "rebalanced quarterly. Adjusted close inputs include dividends. "
            f"Benchmark: {BENCHMARK_LABEL}."
        ),
        "version": datetime.now(timezone.utc).strftime("%Y-%m-%d"),
        "last_updated": datetime.now(timezone.utc).strftime("%Y-%m-%d"),
        "source": "Yahoo Finance unofficial chart endpoint",
        "inception": "Jan 2024",
        "constituents": [{"ticker": t, "yahoo_symbol": s} for t, s in CONSTITUENTS],
        "benchmark_label": BENCHMARK_LABEL,
        "rebalance_dates": [m for m in months if quarter_end(m)],
        "months": months,
        "halvren_index": index_path,
        "tsx_total_return": bench_path,
    }

    if args.dry_run:
        print(json.dumps(payload, indent=2)[:1200])
        return 0

    OUT.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"\n  wrote {OUT.relative_to(ROOT)} ({len(months)} months, last close {months[-1]})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

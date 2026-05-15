#!/usr/bin/env python3
"""
build_halvren_index.py

Renders /halvren-index/index.html — a hypothetical equal-weighted
basket of the top 10 operators by Halvren Read, rebalanced quarterly.

Reads:
  data/operators/<slug>.json      to derive the top 10 by halvren_read
  data/halvren-index-prices.json  hand-curated month-end index values
                                   (since true price feeds aren't wired
                                   yet — see DECISIONS for methodology)

Writes:
  halvren-index/index.html

Run from repo root:
  python3 scripts/build_halvren_index.py
"""

from __future__ import annotations
import json
import sys
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OPS_DIR = ROOT / "data" / "operators"
PRICES_FILE = ROOT / "data" / "halvren-index-prices.json"
OUT = ROOT / "halvren-index" / "index.html"

SITE = "https://halvrencapital.com"


def load_operators() -> list[dict]:
    rows = []
    for p in sorted(OPS_DIR.glob("*.json")):
        d = json.loads(p.read_text(encoding="utf-8"))
        rows.append(d)
    return rows


def top_ten(ops: list[dict]) -> list[dict]:
    ranked = sorted(ops, key=lambda o: (-o.get("halvren_read", 0), o["ticker"]))
    return ranked[:10]


def band(score: int) -> str:
    if score == 100:
        return "perfect"
    if score >= 85:
        return "elite"
    if score >= 70:
        return "solid"
    if score >= 50:
        return "mid"
    return "low"


_Q_LABEL = {1:"Q1",2:"Q2",3:"Q3",4:"Q4",5:"Q5",6:"Q6",7:"Q7",8:"Q8",9:"Q9",10:"Q10"}


def render_mark_sm(o: dict) -> str:
    """Small Halvren Read Mark for the index constituent table.
    Loads the operator's checklist verdicts directly from data/operators/<slug>.json."""
    full_path = ROOT / "data" / "operators" / f"{o['slug']}.json"
    if not full_path.exists():
        return f"<span class='mono'>{o['halvren_read']}</span>"
    full = json.loads(full_path.read_text(encoding="utf-8"))
    score = full.get("halvren_read", o["halvren_read"])
    b = band(score)
    scoring = (full.get("checklist") or {}).get("scoring") or []
    by_q = {s["q"]: s.get("status") for s in scoring}
    rows = []
    for row_qs in ([1,2,3,4,5],[6,7,8,9,10]):
        rows.append('<div class="hread-grid-row">' +
            "".join(f'<span class="hread-chip" data-v="{by_q.get(q) or "null"}">{_Q_LABEL[q]}</span>' for q in row_qs) +
            '</div>')
    return (
        f'<a class="hread-mark hread-mark--sm" data-band="{b}" href="/research/{o["slug"]}" '
        f'aria-label="Halvren Read {score} of 100 — see operator">'
        f'<div class="hread-circle" data-band="{b}">'
        f'<div class="hread-num-wrap"><span class="hread-num">{score}</span><span class="hread-of">/100</span></div>'
        f'<div class="hread-grid" aria-hidden="true">'
        f'<span class="hread-grid-eyebrow">10 checklist verdicts</span>{"".join(rows)}'
        f'</div></div>'
        f'</a>'
    )


def render_table(top: list[dict]) -> str:
    rows = []
    weight = round(100 / len(top), 1)
    for i, o in enumerate(top, 1):
        rows.append(
            f"        <tr>\n"
            f"          <td class='mono'>{i}</td>\n"
            f"          <td><a href='/research/{o['slug']}' style='color:var(--ink);text-decoration:none;border-bottom:1px solid var(--line);font-family:var(--font-data)'>{o['ticker']}</a></td>\n"
            f"          <td>{o['short_name']}</td>\n"
            f"          <td>{o['sector']} &middot; {o['sub_industry']}</td>\n"
            f"          <td class='hindex-mark'>{render_mark_sm(o)}</td>\n"
            f"          <td class='mono'>2024-01</td>\n"
            f"          <td class='mono'>{weight}%</td>\n"
            f"        </tr>"
        )
    return "\n".join(rows)


def render_chart(prices: dict) -> str:
    """Build an inline SVG line chart from the hand-curated monthly index series."""
    months = prices["months"]
    index = prices["halvren_index"]
    bench = prices["tsx_total_return"]
    n = len(months)
    if n < 2 or len(index) != n or len(bench) != n:
        return "<p style='color:var(--color-text-muted)'>Index history coming with the next refresh.</p>"

    # SVG geometry
    W, H = 720, 240
    PAD_L, PAD_R, PAD_T, PAD_B = 48, 24, 24, 32
    inner_w, inner_h = W - PAD_L - PAD_R, H - PAD_T - PAD_B

    # value range
    all_vals = index + bench
    lo, hi = min(all_vals), max(all_vals)
    span = max(0.5, hi - lo)
    pad = span * 0.08
    lo -= pad; hi += pad

    def x(i: int) -> float:
        return PAD_L + (i / (n - 1)) * inner_w

    def y(v: float) -> float:
        return PAD_T + inner_h * (1 - (v - lo) / (hi - lo))

    def to_path(series: list[float]) -> str:
        pts = [f"{x(i):.1f},{y(v):.1f}" for i, v in enumerate(series)]
        return "M " + " L ".join(pts)

    index_path = to_path(index)
    bench_path = to_path(bench)

    # x ticks: first, middle, last month
    ticks = [(0, months[0]), (n // 2, months[n // 2]), (n - 1, months[-1])]
    tick_text = "".join(
        f'<text class="hindex-chart-axis-text" x="{x(i):.0f}" y="{H - 8}" text-anchor="middle">{m}</text>'
        for i, m in ticks
    )

    # y ticks: lo, mid, hi (rounded to 5)
    def fmt(v: float) -> str:
        return f"{round(v):d}"
    y_ticks = [lo, (lo + hi) / 2, hi]
    y_text = "".join(
        f'<text class="hindex-chart-axis-text" x="{PAD_L - 8}" y="{y(v) + 3:.0f}" text-anchor="end">{fmt(v)}</text>'
        for v in y_ticks
    )

    # final values for inline labels
    end_label_idx = f'<text class="hindex-chart-label" x="{x(n-1) - 4:.0f}" y="{y(index[-1]) - 8:.0f}" text-anchor="end">Halvren Index {fmt(index[-1])}</text>'
    end_label_bench = f'<text class="hindex-chart-label" x="{x(n-1) - 4:.0f}" y="{y(bench[-1]) + 16:.0f}" text-anchor="end">TSX TR {fmt(bench[-1])}</text>'

    return f"""<svg viewBox="0 0 {W} {H}" preserveAspectRatio="xMidYMid meet" role="img" aria-label="Halvren Index hypothetical performance vs TSX Total Return since Jan 2024">
  <line class="hindex-chart-axis" x1="{PAD_L}" y1="{H - PAD_B}" x2="{W - PAD_R}" y2="{H - PAD_B}"></line>
  <line class="hindex-chart-axis" x1="{PAD_L}" y1="{PAD_T}" x2="{PAD_L}" y2="{H - PAD_B}"></line>
  {tick_text}
  {y_text}
  <path class="hindex-chart-bench" d="{bench_path}"></path>
  <path class="hindex-chart-line" d="{index_path}"></path>
  {end_label_idx}
  {end_label_bench}
</svg>"""


def refresh_prices(skip_fetch: bool) -> None:
    """Try to refresh /data/halvren-index-prices.json from Yahoo Finance.
    Falls back silently to the existing on-disk file if the fetch fails —
    that file ships with the hand-curated reconstruction so the page can
    always render. Honest failure is logged to stderr."""
    if skip_fetch:
        return
    import subprocess
    fetcher = ROOT / "scripts" / "fetch_halvren_index_prices.py"
    if not fetcher.exists():
        return
    try:
        res = subprocess.run(
            ["python3", str(fetcher)],
            capture_output=True, text=True, timeout=120,
        )
        if res.returncode == 0:
            print(res.stdout.rstrip())
        else:
            tail = (res.stderr or res.stdout or "").strip().splitlines()
            note = tail[-1] if tail else "unknown error"
            print(f"halvren-index: live fetch unavailable ({note}); using on-disk series.")
    except Exception as ex:
        print(f"halvren-index: live fetch skipped ({ex}); using on-disk series.")


def main() -> int:
    import os
    skip_fetch = bool(os.environ.get("HALVREN_INDEX_SKIP_FETCH")) or ("--render-only" in sys.argv)
    refresh_prices(skip_fetch=skip_fetch)

    ops = load_operators()
    top = top_ten(ops)

    if not PRICES_FILE.exists():
        prices = {"months": [], "halvren_index": [], "tsx_total_return": []}
    else:
        prices = json.loads(PRICES_FILE.read_text(encoding="utf-8"))

    chart_svg = render_chart(prices)
    table_html = render_table(top)
    inception = prices.get("inception", "Jan 2024")
    last_value_iso = prices.get("months", [""])[-1] if prices.get("months") else ""
    last_idx = prices.get("halvren_index", [None])[-1] if prices.get("halvren_index") else None
    last_bench = prices.get("tsx_total_return", [None])[-1] if prices.get("tsx_total_return") else None
    last_updated = prices.get("last_updated") or prices.get("version") or ""
    source_note = prices.get("source") or ""

    summary_line = ""
    if last_idx and last_bench:
        diff = last_idx - last_bench
        sign = "+" if diff >= 0 else ""
        summary_line = (
            f"Hypothetical: <strong>{round(last_idx)}</strong> vs TSX Total Return <strong>{round(last_bench)}</strong> "
            f"as of {last_value_iso} &middot; <strong>{sign}{round(diff)}</strong> spread since inception."
        )

    last_updated_line = (
        f'<p class="hindex-updated">Last updated {last_updated}'
        + (f' &middot; {source_note}' if source_note else '')
        + '</p>'
    ) if last_updated else ''

    jsonld = json.dumps({
        "@context": "https://schema.org",
        "@graph": [
            {
                "@type": "WebPage",
                "name": "The Halvren Index",
                "url": f"{SITE}/halvren-index",
                "description": "Hypothetical equal-weighted basket of the top 10 operators by Halvren Read.",
                "inLanguage": "en-CA",
                "isPartOf": {"@id": f"{SITE}/#website"},
            },
            {
                "@type": "BreadcrumbList",
                "itemListElement": [
                    {"@type": "ListItem", "position": 1, "name": "Home", "item": f"{SITE}/"},
                    {"@type": "ListItem", "position": 2, "name": "Halvren Index", "item": f"{SITE}/halvren-index"},
                ],
            },
        ],
    }, ensure_ascii=False, separators=(",", ":"))

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0, viewport-fit=cover">
<title>The Halvren Index — top 10 operators by Halvren Read | Halvren Capital</title>
<meta name="description" content="A hypothetical equal-weighted basket of the top 10 operators by Halvren Read, rebalanced quarterly. Not a fund, not a benchmark. The desk's coverage top-decile, made legible.">
<meta name="theme-color" content="#111010" media="(prefers-color-scheme: dark)">
<meta name="theme-color" content="#f7f6f2" media="(prefers-color-scheme: light)">
<meta name="color-scheme" content="dark light">
<script>(function(){{try{{var c=document.cookie.split('; ').find(function(r){{return r.indexOf('halvren-theme=')===0}});var s=c?c.split('=')[1]:null;var t=s||(window.matchMedia('(prefers-color-scheme: light)').matches?'light':'dark');document.documentElement.setAttribute('data-theme',t);}}catch(e){{document.documentElement.setAttribute('data-theme','dark');}}}})();</script>
<link rel="canonical" href="{SITE}/halvren-index">
<meta property="og:type" content="website">
<meta property="og:title" content="The Halvren Index — Halvren Capital">
<meta property="og:description" content="Top 10 operators by Halvren Read, equal-weighted, rebalanced quarterly. Not a fund. Not a benchmark.">
<meta property="og:url" content="{SITE}/halvren-index">
<meta property="og:image" content="{SITE}/og.png">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:image" content="{SITE}/og.png">
<meta name="robots" content="index,follow,max-image-preview:large">
<link rel="icon" type="image/svg+xml" href="data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 32 32'><rect width='32' height='32' rx='6' fill='%23111010'/><path d='M7 8 L7 24 M7 16 L15 16 M15 8 L15 24' stroke='%23e8e6e2' stroke-width='2.5' stroke-linecap='round' stroke-linejoin='round' fill='none'/><path d='M19 8 L19 24 M19 8 L26 16 L19 24' stroke='%23c9a84c' stroke-width='2.5' stroke-linecap='round' stroke-linejoin='round' fill='none'/></svg>">
<script type="application/ld+json">
{jsonld}
</script>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Cormorant+Garamond:ital,wght@0,500;0,600;1,500&family=Inter:wght@400;500;600&family=Instrument+Serif:ital@0;1&family=JetBrains+Mono:wght@400;500&display=swap" rel="stylesheet">
<link rel="stylesheet" href="/page.css">
</head>
<body>
<a href="#main" class="skip-link">Skip to content</a>
<nav>
  <a href="/" class="nav-logo" aria-label="Halvren Capital — home">
    <svg class="nav-logo-mark" viewBox="0 0 32 32" fill="none" aria-hidden="true">
      <rect width="32" height="32" rx="4" fill="none"/>
      <path d="M6 6 L6 26 M6 16 L16 16 M16 6 L16 26" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"/>
      <path d="M20 6 L20 26 M20 6 L28 16 L20 26" stroke="var(--color-gold)" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"/>
    </svg>
    <span class="nav-logo-name">Halvren Capital</span>
  </a>
  <div class="nav-links" id="nav-links" data-open="false">
    <a href="/start">Start</a>
    <a href="/research">Research</a>
    <a href="/halvren-index" aria-current="page">Halvren Index</a>
    <a href="/notes">Notes</a>
    <a href="/letters">Letters</a>
    <a href="/process">Process</a>
    <a href="/about">About</a>
  </div>
  <div class="nav-right">
    <a href="/" class="nav-back">Back to home</a>
    <button class="theme-toggle" data-theme-toggle aria-label="Toggle theme" type="button">
      <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"/></svg>
    </button>
    <button class="nav-burger" data-nav-open aria-label="Open menu" aria-controls="nav-overlay" aria-expanded="false" type="button"><svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" aria-hidden="true"><path d="M4 9h16M4 15h16"/></svg></button>
  </div>
</nav>

<main id="main">
  <div class="hindex-page">
    <p class="doc-breadcrumb"><a href="/">Home</a><span class="doc-breadcrumb-sep">/</span><span>Halvren Index</span></p>
    <div class="hindex-header">
      <p class="section-label">The Halvren Index</p>
      <h1>Top 10 operators by Halvren Read, equal-weighted, rebalanced <em>quarterly.</em></h1>
      <p class="hindex-lede">An honest reduction of the desk's coverage top-decile to a single line. The Halvren Index is not a fund and not a benchmark; it is the simplest way to ask, "what would owning the desk's highest-conviction operators have looked like."</p>
    </div>

    <table class="hindex-table" aria-label="Halvren Index constituents">
      <thead>
        <tr>
          <th class="mono">#</th>
          <th>Ticker</th>
          <th>Operator</th>
          <th>Sector</th>
          <th class="mono">Halvren Read</th>
          <th class="mono">Included since</th>
          <th class="mono">Weight</th>
        </tr>
      </thead>
      <tbody>
{table_html}
      </tbody>
    </table>

    <div class="hindex-chart">
      {chart_svg}
      <div class="hindex-chart-legend">
        <span class="lg-index">Halvren Index (hypothetical)</span>
        <span class="lg-bench">TSX Total Return</span>
      </div>
    </div>
    {last_updated_line}
    {f'<p class="hindex-context" style="font-style:normal;text-transform:none;letter-spacing:0;font-family:var(--font-body);font-size:var(--text-sm);color:var(--color-text)">{summary_line}</p>' if summary_line else ''}

    <p class="hindex-context">Inception: {inception} &middot; Rebalance: quarterly &middot; Methodology: top 10 by Halvren Read at rebalance date.</p>

    <div class="hindex-disclaimer">
      This is not a fund. This is not a benchmark. This is the desk's coverage top-decile, made legible. Past performance does not predict future returns. Halvren may hold positions in any of these names.
    </div>

    <a class="hindex-method-link" href="/methodology">Read the methodology &rarr;</a>
  </div>
</main>

<footer>
  <div class="footer-trust">
    <span class="footer-trust-item">Canadian &amp; U.S. markets</span>
    <span class="footer-trust-sep">&middot;</span>
    <span class="footer-trust-item">AI-augmented &middot; human-reviewed</span>
    <span class="footer-trust-sep">&middot;</span>
    <span class="footer-trust-item">Proprietary capital</span>
    <span class="footer-trust-sep">&middot;</span>
    <span class="footer-trust-item">Public research is free</span>
  </div>
  <div class="footer-inner">
    <div class="footer-brand">Halvren Capital &mdash; Vancouver &mdash; Est. 2025</div>
    <div class="footer-disclaimer">
      <p>Halvren Capital publishes research and commentary for informational and educational purposes only. Nothing on this site constitutes an offer, solicitation, or recommendation to buy or sell any security.</p>
      <p>Halvren manages proprietary capital and is not a registered investment adviser, broker-dealer, or portfolio manager. The author may hold positions in securities discussed and may transact at any time without notice.</p>
    </div>
  </div>
  <div class="footer-inner footer-meta">
    <span>&copy; 2025&ndash;2026 Halvren Capital. All rights reserved.</span>
    <a href="/version" class="footer-last-reviewed"><strong>Last reviewed:</strong> {date.today().strftime('%B %d, %Y')}</a>
    <span><a href="/privacy">Privacy</a> &middot; <a href="/terms">Terms</a> &middot; <a href="/version">Version</a></span>
  </div>
</footer>
<script src="/nav.js" defer></script>
<script src="/sprint12.js" defer></script>
<aside class="nav-overlay" id="nav-overlay" role="dialog" aria-modal="true" aria-label="Main navigation" aria-hidden="true" hidden>
  <div class="nav-overlay-bar">
    <a href="/" class="nav-overlay-brand">Halvren Capital</a>
    <button class="nav-overlay-close" data-nav-close aria-label="Close menu" type="button">
      <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" aria-hidden="true"><path d="M6 6 L18 18 M18 6 L6 18"/></svg>
    </button>
  </div>
  <nav class="nav-overlay-links" aria-label="Site sections">
    <a href="/start">Start</a>
    <a href="/research">Research</a>
    <a href="/halvren-index">Halvren Index</a>
    <a href="/notes">Notes</a>
    <a href="/coverage">Coverage</a>
    <a href="/checklist">Checklist</a>
    <a href="/compare">Compare</a>
    <a href="/methodology">Methodology</a>
    <a href="/glossary">Glossary</a>
    <a href="/diary">Diary</a>
    <a href="/letters">Letters</a>
    <a href="/process">Process</a>
    <a href="/access">Access</a>
    <a href="/about">About</a>
  </nav>
  <div class="nav-overlay-foot">Halvren Capital &middot; Vancouver</div>
</aside>
<script src="/nav-overlay.js" defer></script>
</body>
</html>
"""
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(html, encoding="utf-8")
    print(f"  wrote {OUT.relative_to(ROOT)} (10 constituents, {len(prices.get('months', []))} months of history)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

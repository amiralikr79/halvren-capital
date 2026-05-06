#!/usr/bin/env python3
"""
build_coverage.py

Renders /coverage from a single source of truth.

Reads:
  data/operators/<slug>.json    deep operators (have a /research/<slug> page)
  data/coverage-queued.json     operators on the desk without a deep page yet

Writes:
  coverage/index.html           sortable + filterable table (vanilla JS, SSR-rendered default sort)
  coverage/coverage.json        full normalized list, public, no auth
  coverage/coverage.csv         same list as CSV

  Deletes coverage.html at the repo root if present, so Vercel resolves
  /coverage to the new directory layout (cleanUrls).

Run from the repo root:
  python3 scripts/build_coverage.py

Acceptance (sprint 2):
  - /coverage renders all 31 rows; default sort by last_reviewed desc.
  - Filter chips work for sector and sub-industry.
  - /coverage/coverage.json and /coverage/coverage.csv parse cleanly.
  - ItemList JSON-LD includes every operator URL with a research page.

No third-party dependencies.
"""

from __future__ import annotations

import csv
import io
import json
import sys
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT / "data" / "operators"
QUEUED_FILE = ROOT / "data" / "coverage-queued.json"
OUT_DIR = ROOT / "coverage"
OUT_HTML = OUT_DIR / "index.html"
OUT_JSON = OUT_DIR / "coverage.json"
OUT_CSV = OUT_DIR / "coverage.csv"
OLD_ROOT_HTML = ROOT / "coverage.html"

CANONICAL_SECTORS = ("Energy", "Materials", "Infrastructure")

STATUS_LABEL = {
    "published":   "Published",
    "on_the_desk": "On the desk",
    "watching":    "Watching",
    "monitoring":  "Monitoring",
    "queued":      "Queued",
}

# Slug derivation for deep operators — matches data/operators/<slug>.json filenames
def deep_slug(op: dict) -> str:
    return op["slug"]


# --------------------------------------------------------------------------- #
# loaders
# --------------------------------------------------------------------------- #

def load_deep() -> list[dict]:
    out = []
    for p in sorted(DATA_DIR.glob("*.json")):
        op = json.loads(p.read_text(encoding="utf-8"))
        op.setdefault("slug", p.stem)
        out.append(op)
    return out


def load_queued() -> list[dict]:
    if not QUEUED_FILE.exists():
        return []
    raw = json.loads(QUEUED_FILE.read_text(encoding="utf-8"))
    return list(raw.get("operators", []))


# --------------------------------------------------------------------------- #
# normalization — produce one shape for the table, JSON, CSV
# --------------------------------------------------------------------------- #

def checklist_score(op: dict) -> int | None:
    """count of 'pass' across the 10 questions, or None if no question is scored yet."""
    cl = op.get("checklist") or {}
    scoring = cl.get("scoring") or []
    if not scoring or all(s.get("status") is None for s in scoring):
        return None
    return sum(1 for s in scoring if s.get("status") == "pass")


def normalize_deep(op: dict) -> dict:
    return {
        "ticker": op["ticker"],
        "exchange": op["exchange"],
        "name": op["name"],
        "short_name": op["short_name"],
        "sector": op["sector"],
        "sub_industry": op["sub_industry"],
        "sub_industry_detail": None,  # detail lives in the research page for deep ops
        "region": _region_from_exchange(op["exchange"]),
        "status": "published",
        "last_reviewed_iso": op.get("last_reviewed_iso"),
        "next_earnings_iso": op.get("next_earnings_iso"),
        "checklist_score": checklist_score(op),
        "research_url": f"/research/{op['slug']}",
        "url": op.get("url"),
    }


def normalize_queued(op: dict) -> dict:
    return {
        "ticker": op["ticker"],
        "exchange": op.get("exchange"),
        "name": op["name"],
        "short_name": op["short_name"],
        "sector": op["sector"],
        "sub_industry": op["sub_industry"],
        "sub_industry_detail": op.get("sub_industry_detail"),
        "region": op.get("region"),
        "status": op.get("status") or "queued",
        "last_reviewed_iso": op.get("last_reviewed_iso"),
        "next_earnings_iso": op.get("next_earnings_iso"),
        "checklist_score": None,
        "research_url": None,
        "url": op.get("url"),
    }


def _region_from_exchange(s: str) -> str:
    if not s:
        return "Canada"
    if "TSX" in s:
        return "Canada"
    if "NYSE" in s or "NASDAQ" in s:
        return "United States"
    return "Canada"


# --------------------------------------------------------------------------- #
# sort key for default render — last_reviewed desc, nulls last, tiebreak by ticker
# --------------------------------------------------------------------------- #

def default_sort_key(op: dict) -> tuple:
    lr = op.get("last_reviewed_iso") or ""
    # "" sorts before any ISO date in asc; we'll reverse below
    return (lr == "", _neg(lr), op["ticker"])


def _neg(s: str) -> str:
    """Return a string that sorts the inverse of s. Trick for desc within the tuple."""
    # ISO dates of fixed length compare lexicographically; we want desc, so invert
    if not s:
        return ""
    return "".join(chr(255 - ord(c)) if c.isdigit() else c for c in s)


# --------------------------------------------------------------------------- #
# CSV / JSON
# --------------------------------------------------------------------------- #

CSV_FIELDS = (
    "ticker name short_name sector sub_industry sub_industry_detail region "
    "status last_reviewed_iso next_earnings_iso checklist_score "
    "exchange research_url url"
).split()


def write_json(operators: list[dict]) -> None:
    payload = {
        "$comment":  "Halvren Capital coverage universe. Public, no auth. Rebuilt by scripts/build_coverage.py.",
        "generated_iso": date.today().isoformat(),
        "count": len(operators),
        "operators": operators,
    }
    OUT_JSON.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def write_csv(operators: list[dict]) -> None:
    buf = io.StringIO()
    w = csv.DictWriter(buf, fieldnames=CSV_FIELDS, extrasaction="ignore")
    w.writeheader()
    for o in operators:
        row = {k: ("" if o.get(k) is None else o.get(k)) for k in CSV_FIELDS}
        w.writerow(row)
    OUT_CSV.write_text(buf.getvalue(), encoding="utf-8")


# --------------------------------------------------------------------------- #
# HTML rendering
# --------------------------------------------------------------------------- #

def _esc(s: str | None) -> str:
    if s is None:
        return ""
    return (
        str(s)
        .replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
    )


def _date_human(iso: str | None) -> str:
    if not iso:
        return "&mdash;"
    d = date.fromisoformat(iso)
    return d.strftime("%b ") + str(d.day) + d.strftime(", %Y")


def _score_cell(score: int | None) -> str:
    return "&mdash;" if score is None else f"{score}/10"


def render_row(o: dict) -> str:
    rurl = o.get("research_url")
    if rurl:
        ticker_cell = f'<a href="{rurl}">{_esc(o["ticker"])}</a>'
        name_cell   = f'<a href="{rurl}">{_esc(o["short_name"])}</a>'
    else:
        ticker_cell = _esc(o["ticker"])
        name_cell   = _esc(o["short_name"])

    sub = _esc(o["sub_industry"]) if o.get("sub_industry") else "&mdash;"
    sub_detail = ""
    if o.get("sub_industry_detail"):
        sub_detail = f'<span class="cov-sub-detail">{_esc(o["sub_industry_detail"])}</span>'

    last = _date_human(o.get("last_reviewed_iso"))
    nxt  = _date_human(o.get("next_earnings_iso"))
    score = _score_cell(o.get("checklist_score"))
    status = o["status"]

    return (
        f'<tr data-sector="{_esc(o["sector"])}" data-sub="{_esc(o["sub_industry"] or "")}" data-status="{status}" data-region="{_esc(o.get("region") or "")}">'
        f'<td class="cov-tkr"><span class="cov-tkr-mono">{ticker_cell}</span></td>'
        f'<td class="cov-name">{name_cell}</td>'
        f'<td>{_esc(o["sector"])}</td>'
        f'<td class="cov-sub">{sub}{sub_detail}</td>'
        f'<td class="cov-date">{last}</td>'
        f'<td class="cov-score">{score}</td>'
        f'<td class="cov-date">{nxt}</td>'
        f'<td><span class="cov-st cov-st--{status}">{STATUS_LABEL.get(status, status)}</span></td>'
        f'</tr>'
    )


def render_filter_chips(operators: list[dict]) -> str:
    sub_set = sorted({o["sub_industry"] for o in operators if o.get("sub_industry")})
    sector_chips = (
        '<button type="button" class="cov-chip is-active" data-filter="sector" data-value="">All sectors</button>'
        + "".join(
            f'<button type="button" class="cov-chip" data-filter="sector" data-value="{_esc(s)}">{_esc(s)}</button>'
            for s in CANONICAL_SECTORS
        )
    )
    sub_chips = (
        '<button type="button" class="cov-chip is-active" data-filter="sub" data-value="">All sub-industries</button>'
        + "".join(
            f'<button type="button" class="cov-chip" data-filter="sub" data-value="{_esc(s)}">{_esc(s)}</button>'
            for s in sub_set
        )
    )
    return f"""
    <div class="cov-controls" role="region" aria-label="Coverage filters and exports">
      <div class="cov-chips" role="group" aria-label="Filter by sector">
        <p class="cov-chips-label">Sector</p>
        {sector_chips}
      </div>
      <div class="cov-chips" role="group" aria-label="Filter by sub-industry">
        <p class="cov-chips-label">Sub-industry</p>
        {sub_chips}
      </div>
      <div class="cov-export">
        <p class="cov-chips-label">Export</p>
        <a href="/coverage/coverage.json" class="cov-export-link">JSON</a>
        <a href="/coverage/coverage.csv" class="cov-export-link">CSV</a>
        <span class="cov-result-count" aria-live="polite"><span id="cov-result-count">{len(operators)}</span> operators</span>
      </div>
    </div>"""


def render_table(operators: list[dict]) -> str:
    rows = "\n          ".join(render_row(o) for o in operators)
    return f"""
    <div class="cov-table-wrap">
      <table class="cov-table cov-table--full">
        <thead>
          <tr>
            <th data-sort="ticker"            tabindex="0" role="columnheader">Ticker <span class="sort-ind"></span></th>
            <th data-sort="short_name"        tabindex="0" role="columnheader">Name <span class="sort-ind"></span></th>
            <th data-sort="sector"            tabindex="0" role="columnheader">Sector <span class="sort-ind"></span></th>
            <th data-sort="sub_industry"      tabindex="0" role="columnheader">Sub-industry <span class="sort-ind"></span></th>
            <th data-sort="last_reviewed_iso" tabindex="0" role="columnheader" aria-sort="descending">Last reviewed <span class="sort-ind">&darr;</span></th>
            <th data-sort="checklist_score"   tabindex="0" role="columnheader">Checklist <span class="sort-ind"></span></th>
            <th data-sort="next_earnings_iso" tabindex="0" role="columnheader">Next earnings <span class="sort-ind"></span></th>
            <th data-sort="status"            tabindex="0" role="columnheader">Status <span class="sort-ind"></span></th>
          </tr>
        </thead>
        <tbody class="cov-tbody">
          {rows}
        </tbody>
      </table>
    </div>"""


def render_itemlist_jsonld(operators: list[dict]) -> str:
    base = "https://halvrencapital.com"
    items = []
    pos = 1
    for o in operators:
        url = (base + o["research_url"]) if o.get("research_url") else (base + "/coverage")
        items.append({
            "@type": "ListItem",
            "position": pos,
            "name": f'{o["name"]} ({o["ticker"]})',
            "url": url,
        })
        pos += 1
    payload = {
        "@context": "https://schema.org",
        "@type": "ItemList",
        "name": "Halvren Capital coverage universe",
        "itemListOrder": "ItemListOrderAscending",
        "numberOfItems": len(operators),
        "itemListElement": items,
    }
    return json.dumps(payload, ensure_ascii=False, separators=(",", ":"))


def render_collection_jsonld(operators: list[dict]) -> str:
    """Page-level CollectionPage + BreadcrumbList, mirroring the prior coverage.html."""
    base = "https://halvrencapital.com"
    payload = {
        "@context": "https://schema.org",
        "@graph": [
            {
                "@type": "CollectionPage",
                "name": "Halvren coverage universe",
                "description": (
                    f"All {len(operators)} Canadian and U.S. operators on the Halvren desk, "
                    "sortable by sector, sub-industry, last reviewed, checklist score, and next earnings."
                ),
                "url": f"{base}/coverage",
                "publisher": {"@id": f"{base}/#organization"},
                "author":    {"@id": f"{base}/#amirali"},
                "inLanguage": "en-CA",
                "datePublished": "2026-04-19",
                "dateModified": date.today().isoformat(),
            },
            {
                "@type": "BreadcrumbList",
                "itemListElement": [
                    {"@type": "ListItem", "position": 1, "name": "Home",     "item": f"{base}/"},
                    {"@type": "ListItem", "position": 2, "name": "Coverage", "item": f"{base}/coverage"},
                ],
            },
        ],
    }
    return json.dumps(payload, ensure_ascii=False, separators=(",", ":"))


# --------------------------------------------------------------------------- #
# inline JSON + JS for sort/filter
# --------------------------------------------------------------------------- #

CLIENT_JS = r"""
(function () {
  var node = document.getElementById('coverage-data');
  if (!node) return;
  var data;
  try { data = JSON.parse(node.textContent); } catch (e) { return; }

  var tbody = document.querySelector('.cov-tbody');
  var countEl = document.getElementById('cov-result-count');
  var headers = document.querySelectorAll('.cov-table--full thead th[data-sort]');

  var STATUS_LABEL = {
    published: 'Published',
    on_the_desk: 'On the desk',
    watching: 'Watching',
    monitoring: 'Monitoring',
    queued: 'Queued'
  };

  var state = { sector: '', sub: '', sortKey: 'last_reviewed_iso', sortDir: 'desc' };

  function esc(s) {
    return String(s == null ? '' : s)
      .replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;');
  }
  function dateHuman(iso) {
    if (!iso) return '—';
    var d = new Date(iso + 'T00:00:00');
    if (isNaN(d.getTime())) return '—';
    var months = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'];
    return months[d.getUTCMonth()] + ' ' + d.getUTCDate() + ', ' + d.getUTCFullYear();
  }
  function scoreCell(s) { return s == null ? '—' : (s + '/10'); }

  function compare(a, b, key, dir) {
    var av = a[key], bv = b[key];
    if (av == null && bv == null) return 0;
    if (av == null) return 1;          // nulls always last
    if (bv == null) return -1;
    if (typeof av === 'number' && typeof bv === 'number') return dir === 'asc' ? av - bv : bv - av;
    av = String(av).toLowerCase(); bv = String(bv).toLowerCase();
    if (av < bv) return dir === 'asc' ? -1 : 1;
    if (av > bv) return dir === 'asc' ?  1 : -1;
    return 0;
  }

  function rowHtml(o) {
    var rurl = o.research_url;
    var tk = rurl ? '<a href="' + rurl + '">' + esc(o.ticker) + '</a>' : esc(o.ticker);
    var nm = rurl ? '<a href="' + rurl + '">' + esc(o.short_name) + '</a>' : esc(o.short_name);
    var subDetail = o.sub_industry_detail ? '<span class="cov-sub-detail">' + esc(o.sub_industry_detail) + '</span>' : '';
    return '<tr data-sector="' + esc(o.sector) + '" data-sub="' + esc(o.sub_industry || '') + '" data-status="' + o.status + '">' +
      '<td class="cov-tkr"><span class="cov-tkr-mono">' + tk + '</span></td>' +
      '<td class="cov-name">' + nm + '</td>' +
      '<td>' + esc(o.sector) + '</td>' +
      '<td class="cov-sub">' + esc(o.sub_industry || '—') + subDetail + '</td>' +
      '<td class="cov-date">' + dateHuman(o.last_reviewed_iso) + '</td>' +
      '<td class="cov-score">' + scoreCell(o.checklist_score) + '</td>' +
      '<td class="cov-date">' + dateHuman(o.next_earnings_iso) + '</td>' +
      '<td><span class="cov-st cov-st--' + o.status + '">' + (STATUS_LABEL[o.status] || o.status) + '</span></td>' +
      '</tr>';
  }

  function applySortIndicators() {
    for (var i = 0; i < headers.length; i++) {
      var th = headers[i];
      var ind = th.querySelector('.sort-ind');
      if (th.getAttribute('data-sort') === state.sortKey) {
        th.setAttribute('aria-sort', state.sortDir === 'asc' ? 'ascending' : 'descending');
        if (ind) ind.textContent = state.sortDir === 'asc' ? '↑' : '↓';
      } else {
        th.removeAttribute('aria-sort');
        if (ind) ind.textContent = '';
      }
    }
  }

  function render() {
    var rows = data.filter(function (o) {
      if (state.sector && o.sector !== state.sector) return false;
      if (state.sub && o.sub_industry !== state.sub) return false;
      return true;
    }).slice().sort(function (a, b) {
      return compare(a, b, state.sortKey, state.sortDir);
    });
    tbody.innerHTML = rows.map(rowHtml).join('');
    if (countEl) countEl.textContent = rows.length;
    applySortIndicators();
  }

  // chip handlers
  var chips = document.querySelectorAll('.cov-chip');
  for (var i = 0; i < chips.length; i++) {
    chips[i].addEventListener('click', (function (chip) {
      return function () {
        var which = chip.getAttribute('data-filter');
        var value = chip.getAttribute('data-value') || '';
        state[which === 'sector' ? 'sector' : 'sub'] = value;
        var siblings = document.querySelectorAll('.cov-chip[data-filter="' + which + '"]');
        for (var j = 0; j < siblings.length; j++) siblings[j].classList.remove('is-active');
        chip.classList.add('is-active');
        render();
      };
    })(chips[i]));
  }

  // header sort handlers
  for (var k = 0; k < headers.length; k++) {
    headers[k].addEventListener('click', (function (th) {
      return function () {
        var key = th.getAttribute('data-sort');
        if (state.sortKey === key) {
          state.sortDir = state.sortDir === 'asc' ? 'desc' : 'asc';
        } else {
          state.sortKey = key;
          // dates default to desc, everything else asc
          state.sortDir = (key.indexOf('iso') >= 0 || key === 'checklist_score') ? 'desc' : 'asc';
        }
        render();
      };
    })(headers[k]));
    headers[k].addEventListener('keydown', (function (th) {
      return function (e) { if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); th.click(); } };
    })(headers[k]));
  }
})();
""".strip()


# --------------------------------------------------------------------------- #
# page template
# --------------------------------------------------------------------------- #

PAGE_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0, viewport-fit=cover">
<title>Coverage universe — Canadian and U.S. operators on the Halvren desk | Halvren Capital</title>
<meta name="description" content="Every Canadian and U.S. operator on the Halvren desk. Sortable by sector, sub-industry, last reviewed, checklist score, and next earnings. JSON and CSV exports.">
<meta name="theme-color" content="#111010" media="(prefers-color-scheme: dark)">
<meta name="theme-color" content="#f7f6f2" media="(prefers-color-scheme: light)">
<meta name="color-scheme" content="dark light">
<script>(function(){{try{{var s=localStorage.getItem('halvren-theme');var p=window.matchMedia('(prefers-color-scheme: light)').matches?'light':'dark';document.documentElement.setAttribute('data-theme',s||p);}}catch(e){{document.documentElement.setAttribute('data-theme','dark');}}}})();</script>
<link rel="canonical" href="https://halvrencapital.com/coverage">
<meta property="og:type" content="website">
<meta property="og:title" content="Halvren Capital — Coverage universe">
<meta property="og:description" content="Every Canadian and U.S. operator on the Halvren desk, organized by sector and status.">
<meta property="og:url" content="https://halvrencapital.com/coverage">
<meta property="og:image" content="https://halvrencapital.com/og.png">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:image" content="https://halvrencapital.com/og.png">
<meta name="robots" content="index,follow,max-image-preview:large">
<link rel="alternate" type="application/json" href="/coverage/coverage.json" title="Coverage universe (JSON)">
<link rel="icon" type="image/svg+xml" href="data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 32 32'><rect width='32' height='32' rx='6' fill='%23111010'/><path d='M7 8 L7 24 M7 16 L15 16 M15 8 L15 24' stroke='%23e8e6e2' stroke-width='2.5' stroke-linecap='round' stroke-linejoin='round' fill='none'/><path d='M19 8 L19 24 M19 8 L26 16 L19 24' stroke='%23c9a84c' stroke-width='2.5' stroke-linecap='round' stroke-linejoin='round' fill='none'/></svg>">
<script type="application/ld+json">
{collection_jsonld}
</script>
<script type="application/ld+json">
{itemlist_jsonld}
</script>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Instrument+Serif:ital@0;1&family=DM+Sans:wght@300;400;500&family=JetBrains+Mono:wght@400;500&display=swap" rel="stylesheet">
<link rel="stylesheet" href="/page.css">
</head>
<body>
<div class="progress-bar" aria-hidden="true"><div class="progress-bar-fill"></div></div>
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
    <a href="/research">Research</a>
    <a href="/letters">Letters</a>
    <a href="/process">Process</a>
    <a href="/access">Access</a>
    <a href="/about">About</a>
  </div>
  <div class="nav-right">
    <a href="/" class="nav-back">Back to home</a>
    <button class="theme-toggle" data-theme-toggle aria-label="Toggle theme" type="button">
      <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"/></svg>
    </button>
    <button class="nav-toggle" data-nav-toggle aria-label="Open menu" aria-controls="nav-links" aria-expanded="false" type="button">
      <span class="nav-toggle-open"><svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><path d="M4 7h16M4 12h16M4 17h16"/></svg></span>
      <span class="nav-toggle-close"><svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><path d="M6 6 L18 18 M18 6 L6 18"/></svg></span>
    </button>
  </div>
</nav>

<main id="main" class="doc-main">
  <article class="doc-article">
    <p class="doc-breadcrumb"><a href="/">Home</a><span class="doc-breadcrumb-sep">/</span><span>Coverage</span></p>
    <div class="cov-header">
      <p class="section-label">Coverage universe</p>
      <h1 class="doc-h1">Thirty-one names we read on a quarterly cadence. Most never become a position. The list <em>is the work.</em></h1>
      <p class="cov-lede">Halvren covers operators across <strong>Canada and the United States</strong> in energy, materials, and infrastructure. The list below is the working universe. The Canadian sectors are deepest, the legacy of the firm's home market and the SEDAR+ ingestion layer that has been live the longest. The U.S. universe is in the build, ingested through SEC EDGAR at the same standard. A name appears here when it has earned the read, regardless of whether it has earned a position.</p>
    </div>

    <div class="legend" aria-label="Status legend">
      <div class="legend-item">
        <span class="legend-label published">Published</span>
        <p class="legend-desc">A full writeup is live on the site, with FY data, business analysis, and the Halvren Checklist applied.</p>
      </div>
      <div class="legend-item">
        <span class="legend-label desk">On the desk</span>
        <p class="legend-desc">Actively researching. A public writeup is queued or close. The work happens before the page does.</p>
      </div>
      <div class="legend-item">
        <span class="legend-label watching">Watching</span>
        <p class="legend-desc">Quarterly review. The thesis or the price has not earned active research, but the name remains in scope.</p>
      </div>
      <div class="legend-item">
        <span class="legend-label monitoring">Monitoring</span>
        <p class="legend-desc">Tracked at a distance. We read the disclosures when they land but have not formed a working view.</p>
      </div>
    </div>
{filter_chips}
{table}

    <p class="bottom-note"><strong style="color:var(--color-text)">A note on the list.</strong> The universe will grow. Coverage is shaped by where operating risk is genuinely interesting, not by what an index weights. The list is reviewed at the end of each quarter and refreshed in the <a href="/letters">quarterly letter</a>. Names not on the list are not necessarily uncovered &mdash; they have not yet earned a place. For the methodology behind the list, see <a href="/process">how the desk works</a>. <a href="mailto:amirali@halvrencapital.com">Write</a> if there is a name we should be reading.</p>
  </article>
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
    <div class="footer-brand">Halvren Capital<span>Vancouver, BC &middot; Est. 2025</span></div>
    <div class="footer-disclaimer">
      <p>Halvren Capital publishes research and commentary for informational and educational purposes only. Nothing on this site constitutes an offer, solicitation, or recommendation to buy or sell any security.</p>
      <p>Halvren manages proprietary capital and is not a registered investment adviser, broker-dealer, or portfolio manager. The author may hold positions in securities discussed and may transact at any time without notice.</p>
    </div>
  </div>
  <div class="footer-inner footer-meta">
    <span>&copy; 2025–2026 Halvren Capital. All rights reserved.</span>
    <span><a href="/">Home</a> &middot; <a href="/research">Research</a> &middot; <a href="/coverage">Coverage</a> &middot; <a href="/digest">Digest</a> &middot; <a href="/performance">Performance</a> &middot; <a href="/press">Press</a> &middot; <a href="/letters">Letters</a> &middot; <a href="/process">Process</a> &middot; <a href="/access">Access</a> &middot; <a href="/about">About</a> &middot; <a href="/privacy">Privacy</a> &middot; <a href="/terms">Terms</a></span>
  </div>
</footer>

<script type="application/json" id="coverage-data">{coverage_data_json}</script>
<script>{client_js}</script>
<script src="/nav.js" defer></script>
</body>
</html>
"""


# --------------------------------------------------------------------------- #
# driver
# --------------------------------------------------------------------------- #

def main() -> int:
    deep    = [normalize_deep(o) for o in load_deep()]
    queued  = [normalize_queued(o) for o in load_queued()]
    operators = sorted(deep + queued, key=default_sort_key)

    OUT_DIR.mkdir(parents=True, exist_ok=True)

    write_json(operators)
    write_csv(operators)

    # render HTML
    html = PAGE_TEMPLATE.format(
        filter_chips      = render_filter_chips(operators),
        table             = render_table(operators),
        collection_jsonld = render_collection_jsonld(operators),
        itemlist_jsonld   = render_itemlist_jsonld(operators),
        coverage_data_json= json.dumps(operators, ensure_ascii=False, separators=(",", ":")),
        client_js         = CLIENT_JS,
    )
    OUT_HTML.write_text(html, encoding="utf-8")

    # remove the legacy root-level coverage.html if present, so /coverage resolves to coverage/index.html
    if OLD_ROOT_HTML.exists():
        OLD_ROOT_HTML.unlink()
        print(f"  removed legacy {OLD_ROOT_HTML.relative_to(ROOT)}")

    print(f"  wrote {OUT_HTML.relative_to(ROOT)}")
    print(f"  wrote {OUT_JSON.relative_to(ROOT)}")
    print(f"  wrote {OUT_CSV.relative_to(ROOT)}")
    print(f"build_coverage: {len(operators)} operators ({len(deep)} deep + {len(queued)} queued).")
    return 0


if __name__ == "__main__":
    sys.exit(main())

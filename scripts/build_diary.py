#!/usr/bin/env python3
"""
build_diary.py

Renders:
  /diary/index.html         the public Cycle Diary feed (newest first)
  /diary/<id>.html          per-entry indexable page
  /diary/feed.xml           RSS 2.0 feed of diary entries

Reads /data/diary.json (newest first, see file for schema). Operator
slugs are validated against /data/operators/<slug>.json so a typo
fails the build rather than ships a dead link.

Run from repo root:
  python3 scripts/build_diary.py
"""

from __future__ import annotations
import json
from datetime import datetime, timezone
from email.utils import formatdate
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data" / "diary.json"
OPS_DIR = ROOT / "data" / "operators"
OUT_DIR = ROOT / "diary"
OUT_DIR.mkdir(exist_ok=True)

SITE = "https://halvrencapital.com"

ACTION_LABEL = {
    "promoted": "Promoted",
    "demoted": "Demoted",
    "flagged": "Flagged",
    "added": "Added",
    "killed": "Killed",
    "reviewed": "Reviewed",
}

FILTER_ORDER = ["all", "promoted", "demoted", "flagged", "added", "killed", "reviewed"]


def fmt_date(iso: str) -> str:
    d = datetime.strptime(iso, "%Y-%m-%d")
    return d.strftime("%B ") + str(d.day) + d.strftime(", %Y")


def fmt_date_mono(iso: str) -> str:
    d = datetime.strptime(iso, "%Y-%m-%d")
    return d.strftime("%Y-%m-%d")


def load_operator(slug: str) -> dict:
    p = OPS_DIR / f"{slug}.json"
    if not p.exists():
        raise SystemExit(f"build_diary: unknown operator slug: {slug}")
    return json.loads(p.read_text(encoding="utf-8"))


def render_chrome_head(canonical: str, title: str, desc: str, og_title: str | None = None, og_image: str | None = None) -> str:
    og_t = og_title or title
    og_i = og_image or f"{SITE}/og.png"
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0, viewport-fit=cover">
<title>{title}</title>
<meta name="description" content="{desc}">
<meta name="theme-color" content="#111010" media="(prefers-color-scheme: dark)">
<meta name="theme-color" content="#f7f6f2" media="(prefers-color-scheme: light)">
<meta name="color-scheme" content="dark light">
<script>(function(){{try{{var s=localStorage.getItem('halvren-theme');var p=window.matchMedia('(prefers-color-scheme: light)').matches?'light':'dark';document.documentElement.setAttribute('data-theme',s||p);}}catch(e){{document.documentElement.setAttribute('data-theme','dark');}}}})();</script>
<link rel="canonical" href="{canonical}">
<meta property="og:type" content="website">
<meta property="og:title" content="{og_t}">
<meta property="og:description" content="{desc}">
<meta property="og:url" content="{canonical}">
<meta property="og:image" content="{og_i}">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:image" content="{og_i}">
<meta name="robots" content="index,follow,max-image-preview:large">
<link rel="alternate" type="application/rss+xml" title="Halvren Cycle Diary" href="/diary/feed.xml">
<link rel="icon" type="image/svg+xml" href="data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 32 32'><rect width='32' height='32' rx='6' fill='%23111010'/><path d='M7 8 L7 24 M7 16 L15 16 M15 8 L15 24' stroke='%23e8e6e2' stroke-width='2.5' stroke-linecap='round' stroke-linejoin='round' fill='none'/><path d='M19 8 L19 24 M19 8 L26 16 L19 24' stroke='%23c9a84c' stroke-width='2.5' stroke-linecap='round' stroke-linejoin='round' fill='none'/></svg>">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Cormorant+Garamond:ital,wght@0,500;0,600;1,500&family=Instrument+Serif:ital@0;1&family=DM+Sans:wght@300;400;500&family=JetBrains+Mono:wght@400;500&display=swap" rel="stylesheet">
<link rel="stylesheet" href="/page.css">
</head>"""


CHROME_NAV = """<a href="#main" class="skip-link">Skip to content</a>
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
    <a href="/notes">Notes</a>
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
    <button class="nav-burger" data-nav-open aria-label="Open menu" aria-controls="nav-overlay" aria-expanded="false" type="button"><svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" aria-hidden="true"><path d="M4 9h16M4 15h16"/></svg></button>
  </div>
</nav>"""


CHROME_FOOT = """<footer>
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
    <a href="/version" class="footer-last-reviewed" title="Build provenance and changelog"><strong>Last reviewed:</strong> May 15, 2026</a>
    <span><a href="/privacy">Privacy</a> &middot; <a href="/terms">Terms</a> &middot; <a href="/version">Version</a></span>
  </div>
</footer>
<script src="/nav.js" defer></script>
<aside class="nav-overlay" id="nav-overlay" role="dialog" aria-modal="true" aria-label="Main navigation" aria-hidden="true" hidden>
  <div class="nav-overlay-bar">
    <a href="/" class="nav-overlay-brand">Halvren Capital</a>
    <button class="nav-overlay-close" data-nav-close aria-label="Close menu" type="button">
      <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" aria-hidden="true"><path d="M6 6 L18 18 M18 6 L6 18"/></svg>
    </button>
  </div>
  <nav class="nav-overlay-links" aria-label="Site sections">
    <a href="/research">Research</a>
    <a href="/notes">Notes</a>
    <a href="/coverage">Coverage</a>
    <a href="/checklist">Checklist</a>
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
<script src="/nav-overlay.js" defer></script>"""


def render_entry_card(e: dict, all_ops: dict[str, dict]) -> str:
    op = all_ops.get(e["slug"]) if e.get("slug") else None
    short = (op or {}).get("short_name", e["ticker"])
    summary = e["summary"]
    return f"""
      <article class="diary-entry" data-action="{e['action']}" data-id="{e['id']}">
        <div class="diary-entry-date">{fmt_date(e['date'])}</div>
        <div class="diary-entry-body">
          <div class="diary-entry-row">
            <a class="diary-entry-ticker" href="/research/{e['slug']}">{e['ticker']}</a>
            <span class="diary-entry-action" data-a="{e['action']}">{ACTION_LABEL[e['action']]}</span>
            <span style="color:var(--color-text-faint);font-size:11px;font-family:var(--font-body);letter-spacing:0.04em">{short}</span>
          </div>
          <p class="diary-entry-summary">{summary}</p>
          <a class="diary-entry-link" href="/diary/{e['id']}">Read the entry &rarr;</a>
        </div>
      </article>"""


def render_index(entries: list[dict], all_ops: dict[str, dict]) -> str:
    cards = "".join(render_entry_card(e, all_ops) for e in entries)
    filters = "".join(
        f'<button type="button" class="diary-filter" data-filter="{f}" aria-pressed="{ "true" if f == "all" else "false" }">{f.capitalize() if f != "all" else "All"}</button>'
        for f in FILTER_ORDER
    )
    jsonld = {
        "@context": "https://schema.org",
        "@graph": [
            {
                "@type": "CollectionPage",
                "name": "Halvren Cycle Diary",
                "url": f"{SITE}/diary",
                "description": "Public log of desk actions on the Halvren coverage universe.",
                "inLanguage": "en-CA",
                "isPartOf": {"@id": f"{SITE}/#website"},
            },
            {
                "@type": "BreadcrumbList",
                "itemListElement": [
                    {"@type": "ListItem", "position": 1, "name": "Home", "item": f"{SITE}/"},
                    {"@type": "ListItem", "position": 2, "name": "Diary", "item": f"{SITE}/diary"},
                ],
            },
        ],
    }
    head = render_chrome_head(
        canonical=f"{SITE}/diary",
        title="Cycle Diary — Public log of desk actions | Halvren Capital",
        desc="A chronological public log of what the Halvren desk did: who got promoted, who got flagged, who got reviewed.",
        og_title="Cycle Diary — Halvren Capital",
    )
    return f"""{head}
<body>
{CHROME_NAV}

<main id="main">
  <div class="diary-page">
    <div class="diary-header">
      <p class="doc-breadcrumb"><a href="/">Home</a><span class="doc-breadcrumb-sep">/</span><span>Diary</span></p>
      <p class="section-label">The Cycle Diary</p>
      <h1 class="doc-h1">What the desk actually <em>did</em>.</h1>
      <p class="doc-meta">Newest first &middot; promoted / demoted / flagged / added / killed / reviewed</p>
      <p class="doc-p">Every coverage-level action this desk takes, logged in public. Not opinions; actions. Promoted means the desk's read got stronger. Demoted means it got weaker. Flagged means something new entered the picture and the work isn't finished.</p>
    </div>
    <div class="diary-filters" role="tablist" aria-label="Filter by action">
      {filters}
    </div>
    <div class="diary-feed" id="diary-feed">{cards}
    </div>
  </div>
</main>

{CHROME_FOOT}
<script type="application/ld+json">{json.dumps(jsonld, ensure_ascii=False, separators=(",", ":"))}</script>
<script>
(function(){{
  var filters = document.querySelectorAll('.diary-filter');
  var entries = document.querySelectorAll('.diary-entry');
  filters.forEach(function(b){{
    b.addEventListener('click', function(){{
      var f = b.getAttribute('data-filter');
      filters.forEach(function(x){{ x.setAttribute('aria-pressed', x === b ? 'true' : 'false'); }});
      entries.forEach(function(e){{
        var match = (f === 'all') || (e.getAttribute('data-action') === f);
        e.style.display = match ? '' : 'none';
      }});
    }});
  }});
}})();
</script>
</body>
</html>
"""


def render_entry_page(e: dict, all_ops: dict[str, dict], prev: dict | None, nxt: dict | None) -> str:
    op = all_ops.get(e["slug"]) or {}
    short = op.get("short_name", e["ticker"])
    sector = op.get("sector", "")
    sub = op.get("sub_industry", "")
    date_long = fmt_date(e["date"])
    canonical = f"{SITE}/diary/{e['id']}"
    desc = f"Halvren desk action on {short} ({e['ticker']}): {e['action']}. {e['summary']}"
    og_image = f"{SITE}/api/og/diary/{e['id']}"
    head = render_chrome_head(
        canonical=canonical,
        title=f"{date_long} · {e['ticker']} · {ACTION_LABEL[e['action']]} | Halvren Cycle Diary",
        desc=desc,
        og_title=f"{e['ticker']} {ACTION_LABEL[e['action']].lower()} — {date_long}",
        og_image=og_image,
    )
    jsonld = {
        "@context": "https://schema.org",
        "@graph": [
            {
                "@type": "Article",
                "headline": f"{e['ticker']} {ACTION_LABEL[e['action']].lower()} — {date_long}",
                "datePublished": e["date"],
                "dateModified": e["date"],
                "url": canonical,
                "author": {"@id": f"{SITE}/#amirali"},
                "publisher": {"@id": f"{SITE}/#organization"},
                "image": og_image,
                "description": desc,
                "mainEntityOfPage": canonical,
                "inLanguage": "en-CA",
            },
            {
                "@type": "BreadcrumbList",
                "itemListElement": [
                    {"@type": "ListItem", "position": 1, "name": "Home", "item": f"{SITE}/"},
                    {"@type": "ListItem", "position": 2, "name": "Diary", "item": f"{SITE}/diary"},
                    {"@type": "ListItem", "position": 3, "name": e["id"], "item": canonical},
                ],
            },
        ],
    }
    nav_links = []
    if prev: nav_links.append(f'<a href="/diary/{prev["id"]}">&larr; Newer: {prev["ticker"]} {prev["action"]}</a>')
    if nxt:  nav_links.append(f'<a href="/diary/{nxt["id"]}">Older: {nxt["ticker"]} {nxt["action"]} &rarr;</a>')
    pager = '<p class="doc-p" style="display:flex;justify-content:space-between;gap:var(--space-4);font-size:var(--text-sm);font-family:var(--font-body)">' + ''.join(f'<span>{x}</span>' for x in nav_links) + '</p>' if nav_links else ''
    return f"""{head}
<body>
{CHROME_NAV}

<main id="main" class="doc-main">
  <article class="doc-article">
    <p class="doc-breadcrumb"><a href="/">Home</a><span class="doc-breadcrumb-sep">/</span><a href="/diary">Diary</a><span class="doc-breadcrumb-sep">/</span><span>{e['id']}</span></p>
    <p class="section-label">Cycle Diary &middot; {date_long}</p>
    <h1 class="doc-h1">{e['ticker']} &middot; <em>{ACTION_LABEL[e['action']].lower()}.</em></h1>
    <p class="doc-meta">{short} &middot; {sector}{' · ' + sub if sub else ''}</p>

    <p class="doc-p" style="font-family:var(--font-display);font-style:italic;font-size:var(--text-lg);color:var(--color-text);line-height:1.55;margin:var(--space-8) 0">{e['summary']}</p>

    <div class="diary-entry" style="display:grid;grid-template-columns:160px 1fr;gap:var(--space-5);margin:var(--space-8) 0">
      <div class="diary-entry-date">{fmt_date_mono(e['date'])}</div>
      <div class="diary-entry-body">
        <div class="diary-entry-row">
          <a class="diary-entry-ticker" href="/research/{e['slug']}">{e['ticker']}</a>
          <span class="diary-entry-action" data-a="{e['action']}">{ACTION_LABEL[e['action']]}</span>
        </div>
        <p class="diary-entry-summary">{e['summary']}</p>
        <p style="font-size:11px;color:var(--color-text-muted);letter-spacing:0.04em;margin-top:var(--space-3)">For the full read on {short}, see the <a href="/research/{e['slug']}" style="color:var(--color-gold);border-bottom:1px solid oklch(from var(--color-gold) l c h/0.3)">operator page</a>.</p>
      </div>
    </div>

    {pager}

    <hr class="doc-divider">
    <p class="doc-p" style="font-size:var(--text-sm);color:var(--color-text-faint)">The Cycle Diary is a public log of desk actions, newest first. <a href="/diary">Return to the feed &rarr;</a> &middot; <a href="/diary/feed.xml">RSS</a></p>
  </article>
</main>

{CHROME_FOOT}
<script type="application/ld+json">{json.dumps(jsonld, ensure_ascii=False, separators=(",", ":"))}</script>
</body>
</html>
"""


def render_rss(entries: list[dict], all_ops: dict[str, dict]) -> str:
    now = datetime.now(timezone.utc)
    pubdate = formatdate(timeval=now.timestamp(), usegmt=True)
    items_xml = []
    for e in entries:
        d = datetime.strptime(e["date"], "%Y-%m-%d").replace(tzinfo=timezone.utc)
        item_pub = formatdate(timeval=d.timestamp(), usegmt=True)
        op = all_ops.get(e["slug"]) or {}
        short = op.get("short_name", e["ticker"])
        title = f"{e['ticker']} {ACTION_LABEL[e['action']].lower()} — {fmt_date(e['date'])}"
        link = f"{SITE}/diary/{e['id']}"
        desc = f"{short}. {e['summary']}"
        items_xml.append(
            f"""    <item>
      <title>{title}</title>
      <link>{link}</link>
      <guid isPermaLink="true">{link}</guid>
      <pubDate>{item_pub}</pubDate>
      <author>amirali@halvrencapital.com (Amirali Karimi)</author>
      <category>{ACTION_LABEL[e['action']]}</category>
      <description><![CDATA[{desc}]]></description>
    </item>"""
        )
    body = "\n".join(items_xml)
    return f"""<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0" xmlns:atom="http://www.w3.org/2005/Atom">
  <channel>
    <title>Halvren Cycle Diary</title>
    <link>{SITE}/diary</link>
    <atom:link href="{SITE}/diary/feed.xml" rel="self" type="application/rss+xml"/>
    <description>Public log of desk actions on the Halvren coverage universe. Newest first.</description>
    <language>en-CA</language>
    <copyright>Copyright 2025–2026 Halvren Capital</copyright>
    <lastBuildDate>{pubdate}</lastBuildDate>
    <generator>halvren scripts/build_diary.py</generator>
{body}
  </channel>
</rss>
"""


def main() -> int:
    data = json.loads(DATA.read_text(encoding="utf-8"))
    entries = list(data["entries"])
    # sort by date desc for safety
    entries.sort(key=lambda e: e["date"], reverse=True)

    # validate slugs
    all_ops: dict[str, dict] = {}
    for e in entries:
        slug = e["slug"]
        if slug not in all_ops:
            all_ops[slug] = load_operator(slug)
        if e["action"] not in ACTION_LABEL:
            raise SystemExit(f"build_diary: unknown action: {e['action']}")

    # write index
    (OUT_DIR / "index.html").write_text(render_index(entries, all_ops), encoding="utf-8")
    print(f"  wrote {(OUT_DIR / 'index.html').relative_to(ROOT)}")

    # write per-entry pages
    for i, e in enumerate(entries):
        prev = entries[i - 1] if i > 0 else None
        nxt = entries[i + 1] if i + 1 < len(entries) else None
        out = OUT_DIR / f"{e['id']}.html"
        out.write_text(render_entry_page(e, all_ops, prev, nxt), encoding="utf-8")
    print(f"  wrote {len(entries)} entry page(s)")

    # write feed
    (OUT_DIR / "feed.xml").write_text(render_rss(entries, all_ops), encoding="utf-8")
    print(f"  wrote {(OUT_DIR / 'feed.xml').relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

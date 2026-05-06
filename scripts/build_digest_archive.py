#!/usr/bin/env python3
"""
build_digest_archive.py

Renders the multi-week digest archive from /data/digest/*.json + /content/digest/*.md.

Outputs:
  digest/index.html               archive list — all weeks, newest first
  digest/<week>/index.html        per-week detail page — only generated for
                                  backfilled weeks; non-backfilled weeks (e.g.
                                  the rich Week 18 page) are preserved verbatim
  digest/latest.json              slim counter snapshot for the homepage to fetch

Adding a new week: drop one JSON in /data/digest/ + one matching MD in
/content/digest/, then run this script. The archive index regenerates; the
per-week page only regenerates if backfilled is true.

This script does not touch /data/digest-week.json or scripts/build_digest.py —
those drive the live ingestion pipeline for the current week and are owned
by a separate concern.

No third-party dependencies.
"""

from __future__ import annotations

import datetime as dt
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT / "data" / "digest"
CONTENT_DIR = ROOT / "content" / "digest"
OUT_DIR = ROOT / "digest"

INDEX_OUT = OUT_DIR / "index.html"
LATEST_JSON = OUT_DIR / "latest.json"

WEEK_RE = re.compile(r"^(\d{4})-W(\d{2})$")


# --------------------------------------------------------------------------- #
# loaders
# --------------------------------------------------------------------------- #

def load_weeks() -> list[dict]:
    weeks = []
    for p in sorted(DATA_DIR.glob("*.json"), reverse=True):
        m = WEEK_RE.match(p.stem)
        if not m:
            continue
        try:
            data = json.loads(p.read_text(encoding="utf-8"))
        except json.JSONDecodeError as e:
            die(f"{p.name}: invalid JSON ({e})")
        # tolerate both shapes — counters may live at top level (sprint-shape)
        # or under stats.* (legacy ingestion shape)
        stats = data.get("stats") or {}
        for k in ("filings_ingested", "pages_read"):
            if k not in data and k in stats:
                data[k] = stats[k]
        if "audio_hours" not in data:
            # try to parse from "incl. 7.4 hrs of call audio"
            m2 = re.search(r"([\d.]+)\s*hrs?", str(stats.get("pages_breakdown", "")))
            data["audio_hours"] = float(m2.group(1)) if m2 else 0.0
        for required in ("week_iso", "filings_ingested", "pages_read"):
            if required not in data:
                die(f"{p.name}: missing required field {required!r}")

        data["__slug"] = p.stem
        body_path = CONTENT_DIR / f"{p.stem}.md"
        data["__body_md"] = body_path.read_text(encoding="utf-8") if body_path.exists() else ""
        weeks.append(data)
    weeks.sort(key=lambda w: (w.get("week_iso", ""),), reverse=True)
    return weeks


def die(msg: str) -> int:
    sys.stderr.write(f"build_digest_archive: error: {msg}\n")
    sys.exit(1)


# --------------------------------------------------------------------------- #
# tiny markdown parser — supports `## h2`, `### h3`, `- list`, `> pullquote`,
# blank-line-separated paragraphs, inline `_italic_` (whole-paragraph wrap)
# --------------------------------------------------------------------------- #

def _normalize(src: str) -> str:
    lines = src.replace("\r\n", "\n").split("\n")
    out: list[str] = []
    for ln in lines:
        s = ln.lstrip()
        is_block = s.startswith(("## ", "### ", "> ", "- "))
        if is_block and out and out[-1].strip() != "":
            out.append("")
        out.append(ln)
    final: list[str] = []
    for i, ln in enumerate(out):
        final.append(ln)
        is_h = ln.lstrip().startswith(("## ", "### "))
        nxt = out[i + 1] if i + 1 < len(out) else ""
        if is_h and nxt.strip() and not nxt.lstrip().startswith(("## ", "### ", "> ", "- ")):
            final.append("")
    return "\n".join(final)


def render_md(src: str) -> str:
    if not src.strip():
        return ""
    src = _normalize(src)
    out: list[str] = []
    pending: list[str] = []

    def flush():
        if pending:
            out.append('<ul class="doc-ul">')
            for li in pending:
                out.append(f"  <li>{li.strip()}</li>")
            out.append("</ul>")
            pending.clear()

    for block in re.split(r"\n\s*\n", src.strip(), flags=re.MULTILINE):
        block = block.rstrip()
        if not block:
            continue
        lines = block.split("\n")
        if all(ln.lstrip().startswith("- ") for ln in lines):
            for ln in lines:
                pending.append(ln.lstrip()[2:])
            continue
        flush()
        if block.startswith("### "):
            out.append(f'<h3 class="doc-h3">{_inline(block[4:].strip())}</h3>')
            continue
        if block.startswith("## "):
            out.append(f'<h2 class="doc-h2">{_inline(block[3:].strip())}</h2>')
            continue
        if block.startswith("> "):
            t = " ".join(ln.lstrip("> ").rstrip() for ln in lines)
            out.append(f'<p class="doc-pullquote">{_inline(t)}</p>')
            continue
        text = " ".join(ln.strip() for ln in lines)
        # whole-paragraph italic (`_..._`)
        if text.startswith("_") and text.endswith("_") and text.count("_") == 2:
            out.append(f'<p class="doc-p doc-p--italic"><em>{_inline(text[1:-1])}</em></p>')
        else:
            out.append(f'<p class="doc-p">{_inline(text)}</p>')
    flush()
    return "\n".join(out)


_INLINE_ITALIC_RE = re.compile(r"(?<![\w_])_(?!_)([^_\n]+?)_(?![\w_])")


def _inline(s: str) -> str:
    # only minimal inline: _italic_ (single underscore wrap, non-breaking)
    return _INLINE_ITALIC_RE.sub(r"<em>\1</em>", s)


# --------------------------------------------------------------------------- #
# date helpers
# --------------------------------------------------------------------------- #

def fmt_date(iso: str | None) -> str:
    if not iso:
        return "—"
    try:
        d = dt.date.fromisoformat(iso)
    except ValueError:
        # tolerate ISO datetime
        try:
            d = dt.datetime.fromisoformat(iso.replace("Z", "+00:00")).date()
        except ValueError:
            return iso
    return d.strftime("%b ") + str(d.day) + d.strftime(", %Y")


# --------------------------------------------------------------------------- #
# template fragments
# --------------------------------------------------------------------------- #

NAV = """<nav>
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
</nav>"""

FOOTER = """<footer>
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
      <p>Halvren manages proprietary capital and is not a registered investment adviser, broker-dealer, or portfolio manager. The author may hold positions in securities discussed and may transact in them at any time without notice.</p>
    </div>
  </div>
  <div class="footer-inner footer-meta">
    <span>&copy; 2025–2026 Halvren Capital. All rights reserved.</span>
    <span><a href="/">Home</a> &middot; <a href="/research">Research</a> &middot; <a href="/coverage">Coverage</a> &middot; <a href="/digest">Digest</a> &middot; <a href="/performance">Performance</a> &middot; <a href="/press">Press</a> &middot; <a href="/letters">Letters</a> &middot; <a href="/process">Process</a> &middot; <a href="/access">Access</a> &middot; <a href="/about">About</a> &middot; <a href="/privacy">Privacy</a> &middot; <a href="/terms">Terms</a></span>
  </div>
</footer>"""

HEAD_BASE = """<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0, viewport-fit=cover">
<meta name="theme-color" content="#111010" media="(prefers-color-scheme: dark)">
<meta name="theme-color" content="#f7f6f2" media="(prefers-color-scheme: light)">
<meta name="color-scheme" content="dark light">
<script>(function(){try{var s=localStorage.getItem('halvren-theme');var p=window.matchMedia('(prefers-color-scheme: light)').matches?'light':'dark';document.documentElement.setAttribute('data-theme',s||p);}catch(e){document.documentElement.setAttribute('data-theme','dark');}})();</script>
<link rel="icon" type="image/svg+xml" href="data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 32 32'><rect width='32' height='32' rx='6' fill='%23111010'/><path d='M7 8 L7 24 M7 16 L15 16 M15 8 L15 24' stroke='%23e8e6e2' stroke-width='2.5' stroke-linecap='round' stroke-linejoin='round' fill='none'/><path d='M19 8 L19 24 M19 8 L26 16 L19 24' stroke='%23c9a84c' stroke-width='2.5' stroke-linecap='round' stroke-linejoin='round' fill='none'/></svg>">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Instrument+Serif:ital@0;1&family=DM+Sans:wght@300;400;500&family=JetBrains+Mono:wght@400;500&display=swap" rel="stylesheet">
<link rel="stylesheet" href="/page.css">"""


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


# --------------------------------------------------------------------------- #
# per-week detail page (for backfilled weeks only)
# --------------------------------------------------------------------------- #

def render_week_page(w: dict) -> str:
    week_iso = w["week_iso"]
    label = w.get("week_label", week_iso)
    canonical = f"https://halvrencapital.com/digest/{week_iso}"

    flags_html = ""
    if w.get("model_flags"):
        items = "".join(
            f"""
        <li class="dx-flag">
          <span class="dx-flag-tkr">{_esc(f.get('ticker', ''))}</span>
          <span class="dx-flag-type">{_esc(f.get('flag_type', ''))}</span>
          <p class="dx-flag-summary">{_esc(f.get('summary', ''))}</p>
        </li>"""
            for f in w["model_flags"]
        )
        flags_html = f"""
    <section class="dx-section" aria-labelledby="dx-flags-h">
      <h2 class="doc-h2" id="dx-flags-h">Model flags</h2>
      <ul class="dx-list">{items}
      </ul>
    </section>"""

    prom_html = ""
    if w.get("promoted_to_desk"):
        items = "".join(
            f"""
        <li class="dx-prom">
          <span class="dx-flag-tkr">{_esc(p.get('ticker', ''))}</span>
          <p class="dx-flag-summary">{_esc(p.get('reason', ''))}</p>
        </li>"""
            for p in w["promoted_to_desk"]
        )
        prom_html = f"""
    <section class="dx-section" aria-labelledby="dx-prom-h">
      <h2 class="doc-h2" id="dx-prom-h">Promoted to desk</h2>
      <ul class="dx-list">{items}
      </ul>
    </section>"""

    backfill_footer = ""
    if w.get("backfilled"):
        backfill_footer = """
    <p class="dx-backfill-note"><strong>Backfilled at launch.</strong> The counters are accurate to the desk's run for the week; the per-operator detail is illustrative and will be replaced as the ingestion pipeline catches up.</p>"""

    body = render_md(w.get("__body_md", ""))

    article_jsonld = {
        "@context": "https://schema.org",
        "@type": "Article",
        "headline": f"Halvren Digest — {label}",
        "description": (
            f"Weekly Halvren Capital ingestion digest for {label}. "
            f"{w['filings_ingested']} filings, {w['pages_read']:,} pages, {w['audio_hours']} hours of audio."
        ),
        "datePublished": (w.get("updated_iso") or w.get("week_of") or week_iso) + ("" if "T" in (w.get("updated_iso") or "") else "T00:00:00Z"),
        "author": {"@id": "https://halvrencapital.com/#amirali"},
        "publisher": {"@id": "https://halvrencapital.com/#organization"},
        "mainEntityOfPage": canonical,
        "inLanguage": "en-CA",
    }

    breadcrumbs_jsonld = {
        "@context": "https://schema.org",
        "@type": "BreadcrumbList",
        "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": "Home",   "item": "https://halvrencapital.com/"},
            {"@type": "ListItem", "position": 2, "name": "Digest", "item": "https://halvrencapital.com/digest"},
            {"@type": "ListItem", "position": 3, "name": label,    "item": canonical},
        ],
    }

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<title>{_esc(label)} — Halvren Digest | Halvren Capital</title>
<meta name="description" content="Weekly Halvren Capital ingestion digest for {_esc(label)}. {w['filings_ingested']} filings, {w['pages_read']:,} pages of disclosure, {w['audio_hours']} hours of call audio.">
<link rel="canonical" href="{canonical}">
<meta property="og:type" content="article">
<meta property="og:title" content="{_esc(label)} — Halvren Digest">
<meta property="og:description" content="Weekly ingestion digest for the Halvren coverage universe.">
<meta property="og:url" content="{canonical}">
<meta property="og:image" content="https://halvrencapital.com/og-digest.png">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:image" content="https://halvrencapital.com/og-digest.png">
<meta name="robots" content="index,follow,max-image-preview:large">
{HEAD_BASE}
<script type="application/ld+json">{json.dumps(article_jsonld, ensure_ascii=False, separators=(",", ":"))}</script>
<script type="application/ld+json">{json.dumps(breadcrumbs_jsonld, ensure_ascii=False, separators=(",", ":"))}</script>
</head>
<body>
<div class="progress-bar" aria-hidden="true"><div class="progress-bar-fill"></div></div>
<a href="#main" class="skip-link">Skip to content</a>
{NAV}

<main id="main" class="doc-main">
  <article class="doc-article">
    <p class="doc-breadcrumb"><a href="/">Home</a><span class="doc-breadcrumb-sep">/</span><a href="/digest">Digest</a><span class="doc-breadcrumb-sep">/</span><span>{_esc(week_iso)}</span></p>
    <p class="section-label">{('Backfilled · ' if w.get('backfilled') else 'Weekly digest · ')}{_esc(label)}</p>
    <h1 class="doc-h1">{_esc(label.split(' · ')[0])}: <em>{_esc(label.split(' · ')[1] if ' · ' in label else 'the desk read').strip()}</em></h1>

    <div class="dx-counters">
      <div class="dx-counter"><span class="dx-counter-num">{w['filings_ingested']}</span><span class="dx-counter-label">Filings ingested</span></div>
      <div class="dx-counter"><span class="dx-counter-num">{w['pages_read']:,}</span><span class="dx-counter-label">Pages read</span></div>
      <div class="dx-counter"><span class="dx-counter-num">{w['audio_hours']}</span><span class="dx-counter-label">Hours of audio</span></div>
      <div class="dx-counter"><span class="dx-counter-num">{len(w.get('model_flags') or [])}<span class="dx-counter-arrow">→</span>{len(w.get('promoted_to_desk') or [])}</span><span class="dx-counter-label">Flags → promoted</span></div>
    </div>

    {body}
{flags_html}{prom_html}
{backfill_footer}

    <hr class="doc-divider">
    <p class="doc-p" style="font-size:var(--text-sm);color:var(--color-text-faint);margin-top:var(--space-8)">
      <strong>Method.</strong> The Halvren digest reads SEDAR+ and SEC EDGAR filings, the Substack/IR press-release feed for SEDAR-only names, and earnings-call transcripts for the entire <a href="/coverage">coverage universe</a>. Each week's counters are the number of unique disclosures the desk's pipeline ingested. Model flags surface tonal shifts and section-length anomalies the desk reviews; promotions to the desk reflect names that earned a deeper look that week.
    </p>
    <p style="margin-top:var(--space-8)"><a href="/digest" style="font-size:var(--text-sm);color:var(--color-gold);border-bottom:1px solid oklch(from var(--color-gold) l c h/0.3);padding-bottom:2px;font-family:var(--font-body)">&larr; All weeks</a></p>
  </article>
</main>

{FOOTER}
<script>(function(){{var f=document.querySelector('.progress-bar-fill');if(!f)return;function u(){{var h=document.documentElement;var m=h.scrollHeight-h.clientHeight;f.style.width=(m>0?Math.min(100,Math.max(0,(h.scrollTop/m)*100)):0)+'%';}}addEventListener('scroll',u,{{passive:true}});addEventListener('resize',u);u();}})();</script>
<script src="/nav.js" defer></script>
</body>
</html>
"""


# --------------------------------------------------------------------------- #
# archive index page
# --------------------------------------------------------------------------- #

def render_index_page(weeks: list[dict]) -> str:
    cards = ""
    for w in weeks:
        week_iso = w["week_iso"]
        label = w.get("week_label", week_iso)
        flags_n = len(w.get("model_flags") or [])
        prom_n = len(w.get("promoted_to_desk") or [])
        backfill_pill = '<span class="dx-list-pill">Backfilled</span>' if w.get("backfilled") else ""
        cards += f"""
        <a class="dx-archive-card" href="/digest/{_esc(week_iso)}">
          <div class="dx-archive-row">
            <span class="dx-archive-eyebrow">{_esc(label.split(' · ')[1] if ' · ' in label else label)}</span>
            {backfill_pill}
          </div>
          <h3 class="dx-archive-title">{_esc(label.split(' · ')[0])}</h3>
          <div class="dx-archive-counters">
            <span><strong>{w['filings_ingested']}</strong> filings</span>
            <span class="op-header-sep">·</span>
            <span><strong>{w['pages_read']:,}</strong> pages</span>
            <span class="op-header-sep">·</span>
            <span><strong>{w['audio_hours']}</strong>h audio</span>
            <span class="op-header-sep">·</span>
            <span><strong>{flags_n}</strong>→<strong>{prom_n}</strong> flags→promoted</span>
          </div>
          <span class="dx-archive-cta">Read principal note &rarr;</span>
        </a>"""

    collection_jsonld = {
        "@context": "https://schema.org",
        "@type": "CollectionPage",
        "name": "Halvren Digest — weekly archive",
        "description": "Weekly digest of filings, transcripts, and disclosure read across the Halvren coverage universe.",
        "url": "https://halvrencapital.com/digest",
        "publisher": {"@id": "https://halvrencapital.com/#organization"},
        "author":    {"@id": "https://halvrencapital.com/#amirali"},
        "inLanguage": "en-CA",
    }
    breadcrumbs_jsonld = {
        "@context": "https://schema.org",
        "@type": "BreadcrumbList",
        "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": "Home",   "item": "https://halvrencapital.com/"},
            {"@type": "ListItem", "position": 2, "name": "Digest", "item": "https://halvrencapital.com/digest"},
        ],
    }
    item_list_jsonld = {
        "@context": "https://schema.org",
        "@type": "ItemList",
        "name": "Halvren Digest — weekly archive",
        "numberOfItems": len(weeks),
        "itemListElement": [
            {
                "@type": "ListItem",
                "position": i + 1,
                "name": w.get("week_label", w["week_iso"]),
                "url": f"https://halvrencapital.com/digest/{w['week_iso']}",
            }
            for i, w in enumerate(weeks)
        ],
    }

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<title>The Digest — weekly archive | Halvren Capital</title>
<meta name="description" content="Every week's digest from the Halvren research desk. Filings, transcripts, model flags, and the names promoted to deeper review.">
<link rel="canonical" href="https://halvrencapital.com/digest">
<meta property="og:type" content="website">
<meta property="og:title" content="The Halvren Digest — weekly archive">
<meta property="og:description" content="Every week's read from the Halvren research desk.">
<meta property="og:url" content="https://halvrencapital.com/digest">
<meta property="og:image" content="https://halvrencapital.com/og-digest.png">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:image" content="https://halvrencapital.com/og-digest.png">
<meta name="robots" content="index,follow,max-image-preview:large">
{HEAD_BASE}
<script type="application/ld+json">{json.dumps(collection_jsonld, ensure_ascii=False, separators=(",", ":"))}</script>
<script type="application/ld+json">{json.dumps(breadcrumbs_jsonld, ensure_ascii=False, separators=(",", ":"))}</script>
<script type="application/ld+json">{json.dumps(item_list_jsonld, ensure_ascii=False, separators=(",", ":"))}</script>
</head>
<body>
<div class="progress-bar" aria-hidden="true"><div class="progress-bar-fill"></div></div>
<a href="#main" class="skip-link">Skip to content</a>
{NAV}

<main id="main" class="doc-main">
  <article class="doc-article">
    <p class="doc-breadcrumb"><a href="/">Home</a><span class="doc-breadcrumb-sep">/</span><span>Digest</span></p>
    <p class="section-label">The desk's weekly read</p>
    <h1 class="doc-h1">Every week, what the desk read. <em>Archived.</em></h1>
    <p class="doc-p" style="max-width:64ch">The Halvren digest reads every Canadian and U.S. operator on the <a href="/coverage">coverage universe</a> on a weekly cadence. Models read at scale and summarize. The principal flags the names that earn a deeper read. Each week below has its own page; the most recent is at the top.</p>

    <section class="dx-archive-list" aria-label="Weekly digests, newest first">{cards}
    </section>

    <p class="doc-p" style="font-size:var(--text-sm);color:var(--color-text-faint);margin-top:var(--space-12);max-width:72ch">
      <strong>What the counters mean.</strong> "Filings ingested" is unique disclosures the pipeline pulled from SEDAR+, SEC EDGAR, and IR press-release feeds. "Pages read" is the total page count across those filings, including transcripts. "Hours of audio" is the running time of earnings calls processed via transcript. "Flags → promoted" is the count of model-flagged sections that earned a same-week promotion to the desk for deeper review. Backfilled weeks have approximate per-operator detail; their counters are accurate.
    </p>
  </article>
</main>

{FOOTER}
<script>(function(){{var f=document.querySelector('.progress-bar-fill');if(!f)return;function u(){{var h=document.documentElement;var m=h.scrollHeight-h.clientHeight;f.style.width=(m>0?Math.min(100,Math.max(0,(h.scrollTop/m)*100)):0)+'%';}}addEventListener('scroll',u,{{passive:true}});addEventListener('resize',u);u();}})();</script>
<script src="/nav.js" defer></script>
</body>
</html>
"""


# --------------------------------------------------------------------------- #
# slim latest.json (for homepage hydration)
# --------------------------------------------------------------------------- #

def render_latest_json(latest: dict) -> str:
    stats = latest.get("stats") or {}
    # the homepage shows desk-wide counts (e.g. "11 model flags this week"),
    # not the length of the curated arrays — fall back to array length only when
    # there is no stats.* number available.
    model_flags_count = stats.get("model_flags")
    if model_flags_count is None:
        model_flags_count = len(latest.get("model_flags") or [])
    promoted_count = stats.get("promoted_to_desk")
    if promoted_count is None:
        promoted_count = len(latest.get("promoted_to_desk") or [])

    payload = {
        "$comment": "Slim digest counters for the homepage. Regenerated by scripts/build_digest_archive.py from data/digest/<latest>.json. Cached 1 hour at the edge.",
        "week_iso": latest["week_iso"],
        "week_label": latest.get("week_label"),
        "week_of": latest.get("week_of"),
        "updated_iso": latest.get("updated_iso"),
        "updated_human": latest.get("updated_human"),
        "filings_ingested": latest["filings_ingested"],
        "pages_read": latest["pages_read"],
        "audio_hours": latest["audio_hours"],
        "model_flags": model_flags_count,
        "promoted_to_desk": promoted_count,
        "url": f"/digest/{latest['week_iso']}",
        "backfilled": bool(latest.get("backfilled")),
    }
    return json.dumps(payload, ensure_ascii=False, indent=2) + "\n"


# --------------------------------------------------------------------------- #
# driver
# --------------------------------------------------------------------------- #

def main() -> int:
    weeks = load_weeks()
    if not weeks:
        die("no digest entries found in data/digest/. Add at least one JSON file.")

    OUT_DIR.mkdir(parents=True, exist_ok=True)

    # archive index
    INDEX_OUT.write_text(render_index_page(weeks), encoding="utf-8")
    print(f"  wrote {INDEX_OUT.relative_to(ROOT)}")

    # latest.json
    LATEST_JSON.write_text(render_latest_json(weeks[0]), encoding="utf-8")
    print(f"  wrote {LATEST_JSON.relative_to(ROOT)}")

    # per-week pages — only generate for backfilled weeks; non-backfilled weeks
    # keep their existing rich page (e.g. digest/2026-W18/index.html written
    # by hand or by scripts/build_digest.py)
    written = 0
    skipped = 0
    for w in weeks:
        out = OUT_DIR / w["week_iso"] / "index.html"
        out.parent.mkdir(parents=True, exist_ok=True)
        if w.get("backfilled") or not out.exists():
            out.write_text(render_week_page(w), encoding="utf-8")
            print(f"  wrote {out.relative_to(ROOT)}")
            written += 1
        else:
            print(f"  skipped {out.relative_to(ROOT)} (non-backfilled, file exists)")
            skipped += 1

    print(f"build_digest_archive: {len(weeks)} weeks ({written} pages written, {skipped} preserved).")
    return 0


if __name__ == "__main__":
    sys.exit(main())

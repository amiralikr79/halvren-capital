#!/usr/bin/env python3
"""
build_notes.py

Renders /notes/<slug>.html and /notes/index.html from /content/notes/<slug>.mdx.

Source format: YAML-ish frontmatter + Markdown body.

  ---
  title: How to read a Canadian oil & gas operator in seven numbers
  slug: how-to-read-canadian-oil-gas-operator-seven-numbers
  date: 2026-05-14
  excerpt: |
    Forty words give or take. The seven numbers we read before any other.
  reading_time: 9
  tags:
    - Energy
    - Capital allocation
    - Operator quality
  related:
    - the-cost-curve-is-a-lie
    - what-2015-and-2020-told-us
  operators:
    - canadian-natural-cnq
    - eog-resources
  ---

  Body in markdown begins here.

Outputs:
  notes/<slug>.html      one file per note
  notes/index.html       editorial-letter style list

The /notes index reads like a back issue of a quarterly letter, not a blog
grid. Date on the left, title in serif, a one-sentence pull, the tags as a
quiet row underneath. Sort by date desc by default; tag chips filter in
place (vanilla JS, no framework, no SSR-vs-CSR dance).

Run from the repo root:
  python3 scripts/build_notes.py             # build all
  python3 scripts/build_notes.py <slug>      # build one
"""

from __future__ import annotations

import json
import re
import sys
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC_DIR = ROOT / "content" / "notes"
OUT_DIR = ROOT / "notes"
DATA_OPS_DIR = ROOT / "data" / "operators"
SITE_META_FILE = ROOT / "content" / "site-meta.json"

REQUIRED_FRONTMATTER = {"title", "slug", "date", "excerpt", "reading_time", "tags", "meta_description"}


# --------------------------------------------------------------------------- #
# frontmatter parser — small, deliberate, only handles what notes use
# --------------------------------------------------------------------------- #

def parse_frontmatter(src: str) -> tuple[dict, str]:
    """Return (meta, body). Frontmatter must be between '---' lines at the top."""
    if not src.startswith("---\n"):
        die("note missing frontmatter")
    end = src.find("\n---\n", 4)
    if end == -1:
        die("note frontmatter not closed")
    head = src[4:end]
    body = src[end + 5:]
    meta = _parse_yaml_subset(head)
    return meta, body


def _parse_yaml_subset(src: str) -> dict:
    """
    Handles:
      key: scalar value
      key: |        # block scalar follows
        line1
        line2
      key:          # list follows
        - item
        - item
    Lists and block scalars do not nest beyond one level. Good enough for notes.
    """
    out: dict = {}
    lines = src.split("\n")
    i = 0
    while i < len(lines):
        raw = lines[i]
        if not raw.strip() or raw.lstrip().startswith("#"):
            i += 1
            continue
        if not raw.startswith(" ") and ":" in raw:
            key, _, rest = raw.partition(":")
            key = key.strip()
            rest = rest.strip()
            if rest == "|":
                # block scalar — collect indented lines
                buf: list[str] = []
                i += 1
                while i < len(lines) and (lines[i].startswith("  ") or lines[i] == ""):
                    buf.append(lines[i][2:] if lines[i].startswith("  ") else "")
                    i += 1
                out[key] = "\n".join(buf).strip()
                continue
            if rest == "":
                # list — collect "  - item" lines
                items: list[str] = []
                i += 1
                while i < len(lines) and lines[i].lstrip().startswith("- "):
                    items.append(lines[i].lstrip()[2:].strip())
                    i += 1
                out[key] = items
                continue
            out[key] = _coerce(rest)
            i += 1
            continue
        i += 1
    return out


def _coerce(s: str):
    if s.isdigit():
        return int(s)
    # strip surrounding quotes
    if (s.startswith('"') and s.endswith('"')) or (s.startswith("'") and s.endswith("'")):
        return s[1:-1]
    return s


# --------------------------------------------------------------------------- #
# markdown — same posture as build_operators.py: H2/H3, lists, pullquotes,
# inline HTML pass-through. Adds blockquote and inline link support.
# --------------------------------------------------------------------------- #

def render_markdown(src: str) -> str:
    src = _normalize(src)
    blocks = re.split(r"\n\s*\n", src.strip(), flags=re.MULTILINE)
    out: list[str] = []
    pending_list: list[str] = []

    def flush_list():
        if pending_list:
            out.append('<ul class="doc-ul">')
            for li in pending_list:
                out.append(f"  <li>{_inline(li.strip())}</li>")
            out.append("</ul>")
            pending_list.clear()

    for block in blocks:
        block = block.rstrip()
        if not block:
            continue
        lines = block.split("\n")

        if all(ln.lstrip().startswith("- ") for ln in lines):
            for ln in lines:
                pending_list.append(ln.lstrip()[2:])
            continue
        flush_list()

        if block.startswith("### "):
            out.append(f'<h3 class="doc-h3">{_inline(block[4:].strip())}</h3>')
            continue
        if block.startswith("## "):
            out.append(f'<h2 class="doc-h2">{_inline(block[3:].strip())}</h2>')
            continue
        if block.startswith("> "):
            txt = " ".join(ln.lstrip("> ").rstrip() for ln in lines)
            out.append(f'<p class="doc-pullquote">{_inline(txt)}</p>')
            continue

        text = " ".join(ln.strip() for ln in lines)
        out.append(f'<p class="doc-p">{_inline(text)}</p>')

    flush_list()
    return "\n".join(out)


def _normalize(src: str) -> str:
    lines = src.replace("\r\n", "\n").split("\n")
    out: list[str] = []
    for ln in lines:
        stripped = ln.lstrip()
        is_block_start = stripped.startswith(("## ", "### ", "> ", "- "))
        if is_block_start and out and out[-1].strip() != "":
            out.append("")
        out.append(ln)
    final: list[str] = []
    for i, ln in enumerate(out):
        final.append(ln)
        is_heading = ln.lstrip().startswith(("## ", "### "))
        nxt = out[i + 1] if i + 1 < len(out) else ""
        if is_heading and nxt.strip() and not nxt.lstrip().startswith(("## ", "### ", "> ", "- ")):
            final.append("")
    return "\n".join(final)


# inline: [label](href) → <a>, **strong** → <strong>, _em_ already HTML
_LINK_RE = re.compile(r"\[([^\]]+)\]\(([^)]+)\)")
_STRONG_RE = re.compile(r"\*\*([^*]+)\*\*")


def _inline(s: str) -> str:
    s = _LINK_RE.sub(r'<a href="\2">\1</a>', s)
    s = _STRONG_RE.sub(r"<strong>\1</strong>", s)
    return s


# --------------------------------------------------------------------------- #
# date helpers
# --------------------------------------------------------------------------- #

def fmt_iso_long(iso: str) -> str:
    d = date.fromisoformat(iso)
    return d.strftime("%B ") + str(d.day) + d.strftime(", %Y")


def fmt_iso_short(iso: str) -> str:
    d = date.fromisoformat(iso)
    return d.strftime("%b ") + str(d.day) + d.strftime(", %Y")


# --------------------------------------------------------------------------- #
# JSON-LD
# --------------------------------------------------------------------------- #

def build_jsonld(meta: dict) -> str:
    base = "https://halvrencapital.com"
    canonical = f"{base}/notes/{meta['slug']}"
    og_image = og_url_for(meta)
    article = {
        "@type": "Article",
        "headline": meta["title"],
        "description": meta["meta_description"],
        "author":    {"@id": f"{base}/#amirali"},
        "publisher": {"@id": f"{base}/#organization"},
        "datePublished": meta["date"],
        "dateModified":  meta.get("modified", meta["date"]),
        "mainEntityOfPage": canonical,
        "image": og_image,
        "inLanguage": "en-CA",
        "keywords": ", ".join(meta.get("tags") or []),
    }
    breadcrumbs = {
        "@type": "BreadcrumbList",
        "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": "Home",  "item": f"{base}/"},
            {"@type": "ListItem", "position": 2, "name": "Notes", "item": f"{base}/notes"},
            {"@type": "ListItem", "position": 3, "name": meta["title"], "item": canonical},
        ],
    }
    payload = {"@context": "https://schema.org", "@graph": [article, breadcrumbs]}
    return json.dumps(payload, ensure_ascii=False, separators=(",", ":"))


def og_url_for(meta: dict) -> str:
    from urllib.parse import quote
    return (
        "https://halvrencapital.com/api/og"
        f"?title={quote(meta['title'])}"
        f"&eyebrow={quote('Halvren Notes')}"
    )


# --------------------------------------------------------------------------- #
# related blocks
# --------------------------------------------------------------------------- #

def render_related_notes(meta: dict, all_meta: dict[str, dict]) -> str:
    rels = meta.get("related") or []
    cards = []
    for slug in rels[:2]:
        r = all_meta.get(slug)
        if not r:
            continue
        cards.append(f"""
        <a href="/notes/{slug}" class="related-card">
          <p class="related-label">Note &middot; {fmt_iso_short(r['date'])}</p>
          <p class="related-title">{r['title']}</p>
          <p class="related-dek">{r['excerpt']}</p>
        </a>""")
    if not cards:
        return ""
    return f"""
    <hr class="doc-divider">
    <section class="related">
      <div class="related-head"><p class="section-label">What to read next</p></div>
      <div class="related-grid">{''.join(cards)}</div>
      <p class="related-more"><a href="/notes">All notes &rarr;</a></p>
    </section>"""


def render_operator_crosslinks(meta: dict) -> str:
    ops = meta.get("operators") or []
    if not ops:
        return ""
    cards = []
    for slug in ops[:3]:
        p = DATA_OPS_DIR / f"{slug}.json"
        if not p.exists():
            continue
        d = json.loads(p.read_text(encoding="utf-8"))
        cards.append(f"""
        <a href="/research/{slug}" class="related-card">
          <p class="related-label">{d['sub_industry']} &middot; {d['ticker']}</p>
          <p class="related-title">{d['headline_html']}</p>
          <p class="related-dek">{d['short_name']} &mdash; {d['sub_industry']} on the desk.</p>
        </a>""")
    if not cards:
        return ""
    return f"""
    <hr class="doc-divider">
    <section class="related">
      <div class="related-head"><p class="section-label">Operators referenced</p></div>
      <div class="related-grid">{''.join(cards)}</div>
    </section>"""


# --------------------------------------------------------------------------- #
# page templates
# --------------------------------------------------------------------------- #

NOTE_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0, viewport-fit=cover">
<title>{title} | Halvren Notes</title>
<meta name="description" content="{meta_description}">
<meta name="theme-color" content="#111010" media="(prefers-color-scheme: dark)">
<meta name="theme-color" content="#f7f6f2" media="(prefers-color-scheme: light)">
<meta name="color-scheme" content="dark light">
<script>(function(){{try{{var s=localStorage.getItem('halvren-theme');var p=window.matchMedia('(prefers-color-scheme: light)').matches?'light':'dark';document.documentElement.setAttribute('data-theme',s||p);}}catch(e){{document.documentElement.setAttribute('data-theme','dark');}}}})();</script>
<link rel="canonical" href="https://halvrencapital.com/notes/{slug}">
<meta property="og:type" content="article">
<meta property="og:title" content="{og_title}">
<meta property="og:description" content="{meta_description}">
<meta property="og:url" content="https://halvrencapital.com/notes/{slug}">
<meta property="og:image" content="{og_image}">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:image" content="{og_image}">
<meta name="robots" content="index,follow,max-image-preview:large">
<link rel="icon" type="image/svg+xml" href="data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 32 32'><rect width='32' height='32' rx='6' fill='%23111010'/><path d='M7 8 L7 24 M7 16 L15 16 M15 8 L15 24' stroke='%23e8e6e2' stroke-width='2.5' stroke-linecap='round' stroke-linejoin='round' fill='none'/><path d='M19 8 L19 24 M19 8 L26 16 L19 24' stroke='%23c9a84c' stroke-width='2.5' stroke-linecap='round' stroke-linejoin='round' fill='none'/></svg>">
<script type="application/ld+json">
{jsonld}
</script>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Cormorant+Garamond:ital,wght@0,500;0,600;1,500&family=Instrument+Serif:ital@0;1&family=DM+Sans:wght@300;400;500&family=JetBrains+Mono:wght@400;500&display=swap" rel="stylesheet">
<link rel="stylesheet" href="/page.css">
<style>
.note-meta-row{{display:flex;align-items:center;gap:var(--space-4);flex-wrap:wrap;margin-top:var(--space-3);font-family:var(--font-body);font-size:var(--text-xs);color:var(--color-text-muted);letter-spacing:0.04em}}
.note-meta-row .sep{{color:var(--color-text-faint)}}
.note-tags{{display:flex;gap:var(--space-2);flex-wrap:wrap;margin-top:var(--space-3)}}
.note-tag{{font-family:var(--font-body);font-size:var(--text-xs);letter-spacing:0.08em;text-transform:uppercase;color:var(--color-text-muted);padding:var(--space-1) var(--space-3);border:1px solid var(--color-divider);border-radius:999px}}
.note-disclaimer{{margin-top:var(--space-12);padding-top:var(--space-6);border-top:1px solid var(--color-divider);font-size:var(--text-xs);color:var(--color-text-faint);letter-spacing:0.02em;line-height:1.7;max-width:72ch}}
</style>
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
    <a href="/notes" aria-current="page">Notes</a>
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
</nav>

<main id="main" class="doc-main">
  <article class="doc-article">
    <p class="doc-breadcrumb"><a href="/">Home</a><span class="doc-breadcrumb-sep">/</span><a href="/notes">Notes</a><span class="doc-breadcrumb-sep">/</span><span>{short_label}</span></p>
    <p class="section-label">Halvren Notes</p>
    <h1 class="doc-h1">{title}</h1>
    <div class="byline">
      <img src="/amirali.jpg" alt="Amirali Karimi" class="byline-avatar" width="52" height="52" loading="lazy">
      <div class="byline-body">
        <p class="byline-name"><a href="/about">Amirali Karimi</a></p>
        <p class="byline-meta">Founder, Halvren Capital &middot; Vancouver, BC</p>
      </div>
      <p class="byline-date">Published {date_human} &middot; {reading_time}-min read</p>
    </div>
    <div class="note-tags">{tag_chips}</div>

    <div class="doc-body">
{body_html}
    </div>

    <p class="note-disclaimer">This note is for informational and educational purposes only and is not a recommendation, solicitation, or price call. The author may hold positions in any of the operators referenced and may transact at any time without notice. Halvren Capital manages proprietary capital and is not currently accepting outside investors. See the <a href="/terms">Terms of Use</a> for the full disclaimer.</p>
{operator_crosslinks}
{related_block}
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
    <div class="footer-brand">Halvren Capital &mdash; Vancouver &mdash; Est. 2025</div>
    <div class="footer-disclaimer">
      <p>Halvren Capital publishes research and commentary for informational and educational purposes only. Nothing on this site constitutes an offer, solicitation, or recommendation to buy or sell any security.</p>
      <p>Halvren manages proprietary capital and is not currently accepting outside investors. Halvren is not a registered investment adviser, broker-dealer, or portfolio manager. The author may hold positions in securities discussed and may transact in them at any time without notice.</p>
    </div>
  </div>
  <div class="footer-inner footer-meta">
    <span>&copy; 2025–2026 Halvren Capital. All rights reserved.</span>
    <a href="/version" class="footer-last-reviewed" title="Build provenance and changelog"><strong>Last reviewed:</strong> {last_full_site_review}</a>
    <span><a href="/privacy">Privacy</a> &middot; <a href="/terms">Terms</a></span>
  </div>
</footer>
<script>(function(){{var f=document.querySelector('.progress-bar-fill');if(!f)return;function u(){{var h=document.documentElement;var m=h.scrollHeight-h.clientHeight;f.style.width=(m>0?Math.min(100,Math.max(0,(h.scrollTop/m)*100)):0)+'%';}}addEventListener('scroll',u,{{passive:true}});addEventListener('resize',u);u();}})();</script>
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
    <a href="/letters">Letters</a>
    <a href="/process">Process</a>
    <a href="/access">Access</a>
    <a href="/about">About</a>
  </nav>
  <div class="nav-overlay-foot">Halvren Capital &middot; Vancouver</div>
</aside>
<script src="/nav-overlay.js" defer></script>
<script src="/viz.js" defer></script>
<script src="/glossary.js" defer></script>
</body>
</html>
"""


INDEX_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0, viewport-fit=cover">
<title>Halvren Notes — short, opinionated research on Canadian &amp; U.S. operators</title>
<meta name="description" content="Halvren Notes — single-claim essays on cost curves, capital allocation, and the operators the desk reads carefully. No price targets. No marketing language.">
<meta name="theme-color" content="#111010" media="(prefers-color-scheme: dark)">
<meta name="theme-color" content="#f7f6f2" media="(prefers-color-scheme: light)">
<meta name="color-scheme" content="dark light">
<script>(function(){{try{{var s=localStorage.getItem('halvren-theme');var p=window.matchMedia('(prefers-color-scheme: light)').matches?'light':'dark';document.documentElement.setAttribute('data-theme',s||p);}}catch(e){{document.documentElement.setAttribute('data-theme','dark');}}}})();</script>
<link rel="canonical" href="https://halvrencapital.com/notes">
<meta property="og:type" content="website">
<meta property="og:title" content="Halvren Notes — short, opinionated research">
<meta property="og:description" content="Single-claim essays on cost curves, capital allocation, and the operators the desk reads carefully.">
<meta property="og:url" content="https://halvrencapital.com/notes">
<meta property="og:image" content="https://halvrencapital.com/api/og?title=Halvren%20Notes&eyebrow=Research%20%C2%B7%20Vancouver">
<meta name="twitter:card" content="summary_large_image">
<meta name="robots" content="index,follow,max-image-preview:large">
<link rel="icon" type="image/svg+xml" href="data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 32 32'><rect width='32' height='32' rx='6' fill='%23111010'/><path d='M7 8 L7 24 M7 16 L15 16 M15 8 L15 24' stroke='%23e8e6e2' stroke-width='2.5' stroke-linecap='round' stroke-linejoin='round' fill='none'/><path d='M19 8 L19 24 M19 8 L26 16 L19 24' stroke='%23c9a84c' stroke-width='2.5' stroke-linecap='round' stroke-linejoin='round' fill='none'/></svg>">
<script type="application/ld+json">
{collection_jsonld}
</script>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Cormorant+Garamond:ital,wght@0,500;0,600;1,500&family=Instrument+Serif:ital@0;1&family=DM+Sans:wght@300;400;500&family=JetBrains+Mono:wght@400;500&display=swap" rel="stylesheet">
<link rel="stylesheet" href="/page.css">
<style>
.notes-masthead{{max-width:var(--content-default);margin-bottom:var(--space-10)}}
.notes-masthead .doc-h1{{margin-bottom:var(--space-4)}}
.notes-issue-meta{{font-family:var(--font-body);font-size:var(--text-xs);letter-spacing:0.12em;text-transform:uppercase;color:var(--color-text-muted);margin-bottom:var(--space-4)}}
.notes-lede{{font-size:var(--text-base);color:var(--color-text-muted);line-height:1.7;max-width:60ch}}
.notes-tagbar{{margin-top:var(--space-8);padding-top:var(--space-5);border-top:1px solid var(--color-divider);display:flex;flex-wrap:wrap;gap:var(--space-2);align-items:center}}
.notes-tagbar-label{{font-family:var(--font-body);font-size:var(--text-xs);letter-spacing:0.12em;text-transform:uppercase;color:var(--color-text-muted);margin-right:var(--space-2)}}
.notes-tag{{font-family:var(--font-body);font-size:var(--text-xs);letter-spacing:0.06em;color:var(--color-text-muted);padding:var(--space-1) var(--space-3);border:1px solid var(--color-divider);border-radius:999px;cursor:pointer;background:transparent}}
.notes-tag:hover{{color:var(--color-text);border-color:var(--color-text-muted)}}
.notes-tag[aria-pressed="true"]{{color:var(--color-bg);background:var(--color-text);border-color:var(--color-text)}}
.notes-list{{display:flex;flex-direction:column;border-top:1px solid var(--color-divider)}}
.notes-item{{display:grid;grid-template-columns:120px 1fr;gap:var(--space-6);padding:var(--space-7) 0;border-bottom:1px solid var(--color-divider);transition:opacity 220ms var(--ease-soft)}}
.notes-item[hidden]{{display:none}}
.notes-item-date{{font-family:var(--font-body);font-size:var(--text-xs);letter-spacing:0.08em;text-transform:uppercase;color:var(--color-text-muted);padding-top:6px}}
.notes-item-body a.notes-item-title{{display:inline-block;font-family:var(--font-display);font-size:var(--text-xl);line-height:1.18;letter-spacing:-0.01em;color:var(--color-text);text-decoration:none;border:none;margin-bottom:var(--space-3)}}
.notes-item-body a.notes-item-title:hover{{color:var(--color-gold)}}
.notes-item-pull{{font-size:var(--text-sm);color:var(--color-text-muted);line-height:1.7;max-width:64ch;margin-bottom:var(--space-3)}}
.notes-item-tags{{display:flex;flex-wrap:wrap;gap:var(--space-2)}}
.notes-item-tag{{font-family:var(--font-body);font-size:11px;letter-spacing:0.06em;color:var(--color-text-faint);text-transform:uppercase}}
.notes-item-tag::after{{content:" \\002F";padding:0 4px;color:var(--color-text-faint)}}
.notes-item-tag:last-child::after{{content:""}}
.notes-footnote{{margin-top:var(--space-10);font-size:var(--text-xs);color:var(--color-text-faint);letter-spacing:0.03em;max-width:72ch;line-height:1.7}}
@media(max-width:700px){{.notes-item{{grid-template-columns:1fr;gap:var(--space-2)}}}}
</style>
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
    <a href="/research">Research</a>
    <a href="/notes" aria-current="page">Notes</a>
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
</nav>

<main id="main" class="doc-main">
  <article class="doc-article">
    <header class="notes-masthead">
      <p class="notes-issue-meta">Halvren Notes &middot; {issue_count} pieces &middot; {issue_window}</p>
      <h1 class="doc-h1">The desk's <em>working notes.</em></h1>
      <p class="notes-lede">Single-claim essays. Each one carries its own thesis and ends where it lands. Numbers are sourced; opinions are signed. No price targets. No marketing language. If a piece does not earn 1,500 words, it does not get published.</p>
      <div class="notes-tagbar" role="group" aria-label="Filter by tag">
        <span class="notes-tagbar-label">Filter</span>
{tag_chips_html}
      </div>
    </header>

    <ol class="notes-list" id="notes-list">
{items_html}
    </ol>

    <p class="notes-footnote">All notes are reviewed by the principal before publication. Cross-links to <a href="/research">research pages</a> and the <a href="/coverage">coverage universe</a> point to the operator data behind each claim. Subscribe to the <a href="/letters">Halvren letter</a> for the quarterly synthesis.</p>
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
    <div class="footer-brand">Halvren Capital &mdash; Vancouver &mdash; Est. 2025</div>
    <div class="footer-disclaimer">
      <p>Halvren Capital publishes research and commentary for informational and educational purposes only. Nothing on this site constitutes an offer, solicitation, or recommendation to buy or sell any security.</p>
      <p>Halvren manages proprietary capital and is not currently accepting outside investors. Halvren is not a registered investment adviser, broker-dealer, or portfolio manager. The author may hold positions in securities discussed and may transact in them at any time without notice.</p>
    </div>
  </div>
  <div class="footer-inner footer-meta">
    <span>&copy; 2025–2026 Halvren Capital. All rights reserved.</span>
    <a href="/version" class="footer-last-reviewed" title="Build provenance and changelog"><strong>Last reviewed:</strong> {last_full_site_review}</a>
    <span><a href="/privacy">Privacy</a> &middot; <a href="/terms">Terms</a></span>
  </div>
</footer>
<script src="/nav.js" defer></script>
<script>
(function(){{
  var chips = document.querySelectorAll('.notes-tag');
  var items = document.querySelectorAll('.notes-item');
  var current = '';
  chips.forEach(function(c){{
    c.addEventListener('click', function(){{
      var tag = c.getAttribute('data-tag') || '';
      current = (current === tag) ? '' : tag;
      chips.forEach(function(x){{x.setAttribute('aria-pressed', (x.getAttribute('data-tag')||'') === current ? 'true' : 'false');}});
      items.forEach(function(it){{
        if (!current) {{ it.removeAttribute('hidden'); return; }}
        var tags = (it.getAttribute('data-tags') || '').split('|');
        if (tags.indexOf(current) >= 0) it.removeAttribute('hidden');
        else it.setAttribute('hidden', '');
      }});
    }});
  }});
}})();
</script>
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
    <a href="/letters">Letters</a>
    <a href="/process">Process</a>
    <a href="/access">Access</a>
    <a href="/about">About</a>
  </nav>
  <div class="nav-overlay-foot">Halvren Capital &middot; Vancouver</div>
</aside>
<script src="/nav-overlay.js" defer></script>
<script src="/viz.js" defer></script>
</body>
</html>
"""


# --------------------------------------------------------------------------- #
# helpers
# --------------------------------------------------------------------------- #

def _esc(s: str) -> str:
    return (
        str(s)
        .replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
    )


def _strip_html(s: str) -> str:
    return re.sub(r"<[^>]+>", "", s).replace("&mdash;", "—").replace("&amp;", "&")


def die(msg: str) -> None:
    sys.stderr.write(f"build_notes: error: {msg}\n")
    sys.exit(1)


# --------------------------------------------------------------------------- #
# index renderer
# --------------------------------------------------------------------------- #

def render_index(notes: list[dict], last_site_review: str) -> str:
    notes_sorted = sorted(notes, key=lambda n: n["date"], reverse=True)

    # collect tag set in stable order (first appearance wins)
    seen: list[str] = []
    for n in notes_sorted:
        for t in n.get("tags") or []:
            if t not in seen:
                seen.append(t)

    tag_chips = "".join(
        f'<button type="button" class="notes-tag" data-tag="{_esc(t)}" aria-pressed="false">{_esc(t)}</button>\n'
        for t in seen
    )

    items_html = []
    for n in notes_sorted:
        tags_attr = "|".join(n.get("tags") or [])
        tag_spans = "".join(
            f'<span class="notes-item-tag">{_esc(t)}</span>'
            for t in (n.get("tags") or [])
        )
        items_html.append(f"""    <li class="notes-item" data-tags="{_esc(tags_attr)}">
      <div class="notes-item-date">{fmt_iso_short(n['date'])}</div>
      <div class="notes-item-body">
        <a class="notes-item-title" href="/notes/{n['slug']}">{_esc(n['title'])}</a>
        <p class="notes-item-pull">{_esc(n['excerpt'])}</p>
        <div class="notes-item-tags">{tag_spans}</div>
      </div>
    </li>""")

    # window: oldest..newest date string
    if notes_sorted:
        newest = fmt_iso_short(notes_sorted[0]["date"])
        oldest = fmt_iso_short(notes_sorted[-1]["date"])
        window = f"{oldest} – {newest}"
    else:
        window = ""

    collection_jsonld = json.dumps(
        {
            "@context": "https://schema.org",
            "@graph": [
                {
                    "@type": "CollectionPage",
                    "name": "Halvren Notes",
                    "description": "Single-claim essays on cost curves, capital allocation, and the operators the desk reads carefully.",
                    "url": "https://halvrencapital.com/notes",
                    "publisher": {"@id": "https://halvrencapital.com/#organization"},
                    "author":    {"@id": "https://halvrencapital.com/#amirali"},
                    "inLanguage": "en-CA",
                    "hasPart": [
                        {
                            "@type": "Article",
                            "url": f"https://halvrencapital.com/notes/{n['slug']}",
                            "headline": n["title"],
                            "datePublished": n["date"],
                        }
                        for n in notes_sorted
                    ],
                }
            ],
        },
        ensure_ascii=False, separators=(",", ":"),
    )

    return INDEX_TEMPLATE.format(
        issue_count=len(notes_sorted),
        issue_window=window,
        tag_chips_html=tag_chips,
        items_html="\n".join(items_html),
        collection_jsonld=collection_jsonld,
        last_full_site_review=last_site_review,
    )


# --------------------------------------------------------------------------- #
# driver
# --------------------------------------------------------------------------- #

def build_one(meta: dict, body_md: str, all_meta: dict[str, dict], last_site_review: str) -> Path:
    body_html = render_markdown(body_md)
    tag_chips = "".join(
        f'<span class="note-tag">{_esc(t)}</span>'
        for t in (meta.get("tags") or [])
    )
    page = NOTE_TEMPLATE.format(
        slug=meta["slug"],
        title=_esc(meta["title"]),
        og_title=_esc(meta["title"]),
        meta_description=_esc(meta["meta_description"]),
        og_image=og_url_for(meta),
        jsonld=build_jsonld(meta),
        short_label=_esc(meta["slug"].replace("-", " ")[:48]),
        date_human=fmt_iso_long(meta["date"]),
        reading_time=int(meta.get("reading_time") or 8),
        tag_chips=tag_chips,
        body_html=body_html,
        operator_crosslinks=render_operator_crosslinks(meta),
        related_block=render_related_notes(meta, all_meta),
        last_full_site_review=last_site_review,
    )
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    out = OUT_DIR / f"{meta['slug']}.html"
    out.write_text(page, encoding="utf-8")
    return out


def load_all() -> list[tuple[dict, str]]:
    if not SRC_DIR.exists():
        die(f"source dir not found: {SRC_DIR.relative_to(ROOT)}")
    out: list[tuple[dict, str]] = []
    for p in sorted(SRC_DIR.glob("*.mdx")):
        meta, body = parse_frontmatter(p.read_text(encoding="utf-8"))
        missing = REQUIRED_FRONTMATTER - set(meta.keys())
        if missing:
            die(f"{p.name}: missing frontmatter keys: {sorted(missing)}")
        out.append((meta, body))
    return out


def main(argv: list[str]) -> int:
    pairs = load_all()
    all_meta = {m["slug"]: m for m, _ in pairs}
    site_meta = json.loads(SITE_META_FILE.read_text(encoding="utf-8")) if SITE_META_FILE.exists() else {}
    last_site_review = (
        site_meta.get("last_full_site_review_human")
        or site_meta.get("last_full_site_review")
        or "—"
    )

    targets = set(argv[1:]) if len(argv) > 1 else None
    for meta, body in pairs:
        if targets and meta["slug"] not in targets:
            continue
        out = build_one(meta, body, all_meta, last_site_review)
        print(f"  wrote {out.relative_to(ROOT)}")

    # index always rebuilds
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    (OUT_DIR / "index.html").write_text(
        render_index([m for m, _ in pairs], last_site_review),
        encoding="utf-8",
    )
    print(f"  wrote notes/index.html")
    print(f"build_notes: rendered {len(pairs)} note(s) + index.")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))

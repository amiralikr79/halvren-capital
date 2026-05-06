#!/usr/bin/env python3
"""
build_operators.py

Renders /research/<slug>.html for every /data/operators/<slug>.json.

Reads:
  data/operators/<slug>.json    typed data block (see scripts/operator-schema.md)
  content/operators/<slug>.md   principal prose body
  scripts/checklist_questions.json  canonical 10 questions

Writes:
  research/<slug>.html          one file per operator

Run from the repo root:
  python3 scripts/build_operators.py             # build all
  python3 scripts/build_operators.py cameco-cco  # build one

Exits non-zero on missing required fields or unreadable input. The script
holds the section order specified in Sprint 1 — header, the read, by the
numbers, what we track, the note, scorecard, disclosure footer — and is
the only place that order is encoded.

No third-party dependencies.
"""

from __future__ import annotations

import json
import re
import sys
from datetime import date, datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT / "data" / "operators"
CONTENT_DIR = ROOT / "content" / "operators"
OUT_DIR = ROOT / "research"
QUESTIONS_FILE = ROOT / "scripts" / "checklist_questions.json"

REQUIRED_FIELDS = (
    "slug ticker exchange name short_name url sector sub_industry "
    "page_eyebrow headline_html page_title meta_description og_title "
    "og_description og_image published_iso modified_iso the_read "
    "fy_snapshot leadership what_we_track checklist last_reviewed_iso "
    "position_disclosure disclosure_footnote_html back_link related_slugs"
).split()

ALLOWED_SECTORS = {"Energy", "Materials", "Infrastructure"}
ALLOWED_STATUSES = {"pass", "not_yet", "fail", None}
ALLOWED_DISCLOSURES = {"may_hold", "holds", "none"}


# --------------------------------------------------------------------------- #
# tiny markdown parser — handles only what the operator body files use:
#   ## h2, ### h3, - lists, > pullquotes, blank-line-separated paragraphs
# inline HTML is passed through verbatim so the principal's <em>, <strong>,
# and HTML entities survive.
# --------------------------------------------------------------------------- #

def _normalize(src: str) -> str:
    """Force blank lines around block boundaries so the splitter sees clean blocks.
    Forgiving for headings/lists/blockquotes that the principal may write without
    a blank line between."""
    lines = src.replace("\r\n", "\n").split("\n")
    out: list[str] = []
    for ln in lines:
        stripped = ln.lstrip()
        is_block_start = (
            stripped.startswith(("## ", "### ", "> ", "- "))
        )
        if is_block_start and out and out[-1].strip() != "":
            out.append("")
        out.append(ln)
    # also ensure a blank after a heading line if the next line is text
    final: list[str] = []
    for i, ln in enumerate(out):
        final.append(ln)
        is_heading = ln.lstrip().startswith(("## ", "### "))
        nxt = out[i + 1] if i + 1 < len(out) else ""
        if is_heading and nxt.strip() and not nxt.lstrip().startswith(("## ", "### ", "> ", "- ")):
            final.append("")
    return "\n".join(final)


def render_markdown(src: str) -> str:
    src = _normalize(src)
    out: list[str] = []
    pending_list: list[str] = []

    def flush_list() -> None:
        if pending_list:
            out.append('<ul class="doc-ul">')
            for li in pending_list:
                out.append(f"  <li>{li.strip()}</li>")
            out.append("</ul>")
            pending_list.clear()

    blocks = re.split(r"\n\s*\n", src.strip(), flags=re.MULTILINE)
    for block in blocks:
        block = block.rstrip()
        if not block:
            continue

        lines = block.split("\n")

        # bullet list — every line starts with "- "
        if all(ln.lstrip().startswith("- ") for ln in lines):
            for ln in lines:
                pending_list.append(ln.lstrip()[2:])
            continue
        flush_list()

        # heading (single-line block by construction post-normalize)
        if block.startswith("### "):
            out.append(f'<h3 class="doc-h3">{block[4:].strip()}</h3>')
            continue
        if block.startswith("## "):
            out.append(f'<h2 class="doc-h2">{block[3:].strip()}</h2>')
            continue

        # pullquote
        if block.startswith("> "):
            text = " ".join(ln.lstrip("> ").rstrip() for ln in lines)
            out.append(f'<p class="doc-pullquote">{text}</p>')
            continue

        # default: paragraph (preserve inline HTML, join multi-line on space)
        text = " ".join(ln.strip() for ln in lines)
        out.append(f'<p class="doc-p">{text}</p>')

    flush_list()
    return "\n".join(out)


# --------------------------------------------------------------------------- #
# date helpers
# --------------------------------------------------------------------------- #

def fmt_iso_human(iso: str | None) -> str:
    """2026-04-18 -> 'April 2026'. Returns '—' for None."""
    if not iso:
        return "&mdash;"
    d = date.fromisoformat(iso)
    return d.strftime("%B %Y")


def fmt_iso_long(iso: str | None) -> str:
    """2026-04-18 -> 'April 18, 2026'. Returns '—' for None."""
    if not iso:
        return "&mdash;"
    d = date.fromisoformat(iso)
    return d.strftime("%B ") + str(d.day) + d.strftime(", %Y")


def relative_countdown_html(iso: str | None) -> str:
    """Render a relative countdown to a future date, or a placeholder."""
    if not iso:
        return '<span class="op-header-countdown">&mdash;</span>'
    target = date.fromisoformat(iso)
    today = date.today()
    delta = (target - today).days
    if delta < 0:
        return f'<span class="op-header-countdown" data-state="past">{abs(delta)}d ago</span>'
    if delta == 0:
        return '<span class="op-header-countdown" data-state="today">today</span>'
    return f'<span class="op-header-countdown" data-state="future">in {delta}d</span>'


# --------------------------------------------------------------------------- #
# section renderers
# --------------------------------------------------------------------------- #

def render_header_strip(op: dict) -> str:
    last = fmt_iso_long(op["last_reviewed_iso"])
    nxt = fmt_iso_long(op.get("next_earnings_iso"))
    countdown = relative_countdown_html(op.get("next_earnings_iso"))
    return f"""
    <div class="op-header">
      <div class="op-header-row">
        <span class="op-header-tkr">{op['ticker']}</span>
        <span class="op-header-sep">&middot;</span>
        <span class="op-header-listing">{op['exchange']}</span>
        <span class="op-header-sep">&middot;</span>
        <span class="op-header-sector">{op['sector']} &middot; {op['sub_industry']}</span>
      </div>
      <div class="op-header-row op-header-row--dates">
        <span class="op-header-meta"><span class="op-header-meta-label">Last reviewed</span> {last}</span>
        <span class="op-header-sep">&middot;</span>
        <span class="op-header-meta"><span class="op-header-meta-label">Next earnings</span> {nxt} {countdown}</span>
      </div>
    </div>"""


def render_the_read(op: dict) -> str:
    r = op["the_read"]
    summary = r.get("summary")
    if not summary:
        # PRINCIPAL placeholder — render visibly so it's caught in review
        return """
    <section class="op-read" aria-labelledby="op-read-h">
      <p class="op-read-eyebrow" id="op-read-h">The read &middot; machine block</p>
      <p class="op-read-summary op-read-summary--placeholder">
        <!-- PRINCIPAL: write the_read.summary (~30 words, machine-style abstract). -->
        Awaiting principal-reviewed machine summary.
      </p>
    </section>"""
    stamp_bits = []
    if r.get("generated_iso"):
        stamp_bits.append(f"Generated {fmt_iso_long(r['generated_iso'])}")
    if r.get("source_filing"):
        stamp_bits.append(f"from {r['source_filing']}")
    if r.get("principal_reviewed_iso"):
        stamp_bits.append(
            f"Reviewed by principal {fmt_iso_long(r['principal_reviewed_iso'])}"
        )
    stamp = ". ".join(stamp_bits) + ("." if stamp_bits else "")
    return f"""
    <section class="op-read" aria-labelledby="op-read-h">
      <p class="op-read-eyebrow" id="op-read-h">The read &middot; machine block</p>
      <p class="op-read-summary">{summary}</p>
      <p class="op-read-stamp">{stamp}</p>
    </section>"""


def render_by_the_numbers(op: dict) -> str:
    snap = op["fy_snapshot"]
    rows = []
    for m in snap["metrics"]:
        val = m.get("value") or "&mdash;"
        note = f' <span class="op-stat-note">{m["note"]}</span>' if m.get("note") else ""
        rows.append(f"      <dt>{m['label']}</dt><dd>{val}{note}</dd>")
    return f"""
    <section class="op-section" aria-labelledby="op-numbers-h">
      <h2 class="doc-h2" id="op-numbers-h">By the numbers</h2>
      <dl class="doc-stats">
        <dt class="doc-stats-caption">{snap['period']}</dt>
{chr(10).join(rows)}
      </dl>
    </section>"""


def render_what_we_track(op: dict) -> str:
    items = op.get("what_we_track") or []
    if not items:
        return ""
    lis = "\n".join(f"        <li>{x}</li>" for x in items)
    return f"""
    <section class="op-section" aria-labelledby="op-track-h">
      <h2 class="doc-h2" id="op-track-h">What we track</h2>
      <ul class="doc-ul op-track-list">
{lis}
      </ul>
    </section>"""


def render_the_note(body_html: str) -> str:
    return f"""
    <section class="op-section op-note" aria-labelledby="op-note-h">
      <h2 class="doc-h2" id="op-note-h">The note</h2>
      {body_html}
    </section>"""


def render_scorecard(op: dict, questions: list[dict], pillars: dict) -> str:
    by_q = {q["q"]: q for q in questions}
    scoring = {s["q"]: s for s in op["checklist"]["scoring"]}

    # build one block per pillar — matches /checklist.html structure
    pillar_blocks: list[str] = []
    for roman in ("I", "II", "III"):
        pinfo = pillars[roman]
        items_html = []
        for qnum in pinfo["questions"]:
            q = by_q[qnum]
            s = scoring.get(qnum, {"status": None, "note": None})
            status = s.get("status")
            status_attr = status if status in {"pass", "not_yet", "fail"} else "null"
            status_label = {
                "pass": "Pass",
                "not_yet": "Not yet",
                "fail": "Fail",
                None: "Pending principal review",
            }[status]
            note = s.get("note") or q["default_note"]
            items_html.append(f"""
        <div class="sc-item">
          <span class="sc-num">{qnum:02d}</span>
          <div>
            <div class="sc-row">
              <span class="sc-dot" data-status="{status_attr}" aria-hidden="true"></span>
              <p class="sc-q">{q['question_html']}</p>
            </div>
            <p class="sc-status" data-status="{status_attr}">{status_label}</p>
            <p class="sc-note">{note}</p>
          </div>
        </div>""")

        pillar_blocks.append(f"""
      <div class="sc-pillar">
        <p class="sc-pillar-label">Pillar {roman}</p>
        <h3 class="sc-pillar-title">{pinfo['label']}</h3>
        {''.join(items_html)}
      </div>""")

    commentary = op["checklist"]["pillar_commentary"]
    return f"""
    <section class="op-section op-scorecard" aria-labelledby="op-sc-h">
      <h2 class="doc-h2" id="op-sc-h">Checklist scorecard</h2>
      <p class="op-sc-intro">Ten questions, three pillars. Status icons reflect the principal's read on this name; absent a green dot, fall back to the question's standard note.
        See the <a href="/checklist">full Checklist</a> for the framework.</p>
      <div class="sc-grid">
{''.join(pillar_blocks)}
      </div>
      <div class="op-sc-commentary">
        <p class="doc-p">{commentary['I']}</p>
        <p class="doc-p">{commentary['II']}</p>
        <p class="doc-p">{commentary['III']}</p>
      </div>
    </section>"""


def render_disclosure_footer(op: dict) -> str:
    bl = op["back_link"]
    return f"""
    <section class="op-disclosure" aria-labelledby="op-disc-h">
      <hr class="doc-divider">
      <h2 class="doc-h2 op-disc-h" id="op-disc-h">Disclosure</h2>
      <p class="doc-p op-disc-text">{op['disclosure_footnote_html']}</p>
      <p class="op-disc-meta">Last reviewed {fmt_iso_long(op['last_reviewed_iso'])}.</p>
      <p class="op-back"><a href="{bl['href']}">&larr; {bl['label']}</a></p>
    </section>"""


def render_related(op: dict, all_ops: dict[str, dict]) -> str:
    rels = []
    for slug in (op.get("related_slugs") or [])[:2]:
        r = all_ops.get(slug)
        if not r:
            continue
        label = f"{r['sub_industry']} &middot; {r['ticker']}"
        # synth dek from short_name + sub_industry
        rels.append(f"""
        <a href="/research/{slug}" class="related-card">
          <p class="related-label">{label}</p>
          <p class="related-title">{r['headline_html']}</p>
          <p class="related-dek">{r['short_name']} &mdash; {r['sub_industry']} on the desk; FY {r['fy_snapshot']['period'].split()[-1]} numbers reviewed {fmt_iso_human(r['last_reviewed_iso'])}.</p>
        </a>""")
    if not rels:
        return ""
    return f"""
    <hr class="doc-divider">
    <section class="related">
      <div class="related-head"><p class="section-label">Keep reading</p></div>
      <div class="related-grid">{''.join(rels)}</div>
      <p class="related-more"><a href="/research">See the full research archive &rarr;</a></p>
    </section>"""


# --------------------------------------------------------------------------- #
# JSON-LD builder — Article + BreadcrumbList + FinancialProduct
# --------------------------------------------------------------------------- #

def build_jsonld(op: dict) -> str:
    base = "https://halvrencapital.com"
    canonical = f"{base}/research/{op['slug']}"
    img = f"{base}{op['og_image']}" if op["og_image"].startswith("/") else op["og_image"]

    article = {
        "@type": "Article",
        "headline": _strip_html(op["headline_html"]),
        "description": op["meta_description"],
        "about": [{
            "@type": "Corporation",
            "name": op["name"],
            "tickerSymbol": op["ticker"],
            "sameAs": op["url"],
        }],
        "author":    {"@id": f"{base}/#amirali"},
        "publisher": {"@id": f"{base}/#organization"},
        "datePublished": op["published_iso"],
        "dateModified":  op["modified_iso"],
        "mainEntityOfPage": canonical,
        "image": img,
        "inLanguage": "en-CA",
    }
    breadcrumbs = {
        "@type": "BreadcrumbList",
        "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": "Home",     "item": f"{base}/"},
            {"@type": "ListItem", "position": 2, "name": "Research", "item": f"{base}/research"},
            {"@type": "ListItem", "position": 3, "name": f"{op['short_name']} ({op['ticker']})", "item": canonical},
        ],
    }
    disclosure_text = {
        "may_hold": "The author may hold a position and may transact at any time without notice.",
        "holds":    "The author holds a position and may transact at any time without notice.",
        "none":     "The author does not currently hold a position.",
    }[op["position_disclosure"]]
    finprod = {
        "@type": "FinancialProduct",
        "name": f"{op['name']} ({op['ticker']})",
        "category": "Equity",
        "description": (
            f"Halvren Capital research note on {op['name']}. "
            f"{disclosure_text} Not investment advice."
        ),
        "url":      canonical,
        "provider": {"@id": f"{base}/#organization"},
        "isRelatedTo": {"@id": f"{base}/checklist"},
    }
    payload = {"@context": "https://schema.org", "@graph": [article, breadcrumbs, finprod]}
    return json.dumps(payload, ensure_ascii=False, separators=(",", ":"))


def _strip_html(s: str) -> str:
    return re.sub(r"<[^>]+>", "", s).replace("&amp;", "&").replace("&ldquo;", "“").replace("&rdquo;", "”")


# --------------------------------------------------------------------------- #
# page template
# --------------------------------------------------------------------------- #

PAGE_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0, viewport-fit=cover">
<title>{page_title}</title>
<meta name="description" content="{meta_description}">
<meta name="theme-color" content="#111010" media="(prefers-color-scheme: dark)">
<meta name="theme-color" content="#f7f6f2" media="(prefers-color-scheme: light)">
<meta name="color-scheme" content="dark light">
<script>(function(){{try{{var s=localStorage.getItem('halvren-theme');var p=window.matchMedia('(prefers-color-scheme: light)').matches?'light':'dark';document.documentElement.setAttribute('data-theme',s||p);}}catch(e){{document.documentElement.setAttribute('data-theme','dark');}}}})();</script>
<link rel="canonical" href="https://halvrencapital.com/research/{slug}">
<meta property="og:type" content="article">
<meta property="og:title" content="{og_title}">
<meta property="og:description" content="{og_description}">
<meta property="og:url" content="https://halvrencapital.com/research/{slug}">
<meta property="og:image" content="https://halvrencapital.com{og_image}">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:image" content="https://halvrencapital.com{og_image}">
<meta name="robots" content="index,follow,max-image-preview:large">
<link rel="icon" type="image/svg+xml" href="data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 32 32'><rect width='32' height='32' rx='6' fill='%23111010'/><path d='M7 8 L7 24 M7 16 L15 16 M15 8 L15 24' stroke='%23e8e6e2' stroke-width='2.5' stroke-linecap='round' stroke-linejoin='round' fill='none'/><path d='M19 8 L19 24 M19 8 L26 16 L19 24' stroke='%23c9a84c' stroke-width='2.5' stroke-linecap='round' stroke-linejoin='round' fill='none'/></svg>">
<script type="application/ld+json">
{jsonld}
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
    <a href="/research" aria-current="page">Research</a>
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
    <p class="doc-breadcrumb"><a href="/">Home</a><span class="doc-breadcrumb-sep">/</span><a href="/research">Research</a><span class="doc-breadcrumb-sep">/</span><span>{ticker}</span></p>
    <p class="section-label">{page_eyebrow}</p>
    <h1 class="doc-h1">{headline_html}</h1>
    <div class="byline">
      <img src="/amirali.jpg" alt="Amirali Karimi" class="byline-avatar" width="52" height="52" loading="lazy">
      <div class="byline-body">
        <p class="byline-name"><a href="/about">Amirali Karimi</a></p>
        <p class="byline-meta">Founder, Halvren Capital &middot; Vancouver, BC &middot; SFU Economics &middot; CFA candidate</p>
      </div>
      <p class="byline-date">Published {published_human} &middot; Reviewed quarterly</p>
    </div>
{header_strip}
{the_read}
{by_the_numbers}
{what_we_track}
{the_note}
{scorecard}
{disclosure_footer}
{related}
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
      <p>Halvren manages proprietary capital and is not currently accepting outside investors. Halvren is not a registered investment adviser, broker-dealer, or portfolio manager. The author may hold positions in securities discussed and may transact in them at any time without notice.</p>
    </div>
  </div>
  <div class="footer-inner footer-meta">
    <span>&copy; 2025–2026 Halvren Capital. All rights reserved.</span>
    <span><a href="/">Home</a> &middot; <a href="/research">Research</a> &middot; <a href="/coverage">Coverage</a> &middot; <a href="/digest">Digest</a> &middot; <a href="/performance">Performance</a> &middot; <a href="/press">Press</a> &middot; <a href="/letters">Letters</a> &middot; <a href="/process">Process</a> &middot; <a href="/access">Access</a> &middot; <a href="/about">About</a> &middot; <a href="/privacy">Privacy</a> &middot; <a href="/terms">Terms</a></span>
  </div>
</footer>
<script>(function(){{var f=document.querySelector('.progress-bar-fill');if(!f)return;function u(){{var h=document.documentElement;var m=h.scrollHeight-h.clientHeight;f.style.width=(m>0?Math.min(100,Math.max(0,(h.scrollTop/m)*100)):0)+'%';}}addEventListener('scroll',u,{{passive:true}});addEventListener('resize',u);u();}})();</script>
<script src="/nav.js" defer></script>
</body>
</html>
"""


# --------------------------------------------------------------------------- #
# validation + driver
# --------------------------------------------------------------------------- #

def validate(op: dict, slug: str) -> None:
    missing = [f for f in REQUIRED_FIELDS if f not in op]
    if missing:
        die(f"{slug}: missing required fields: {', '.join(missing)}")
    if op["sector"] not in ALLOWED_SECTORS:
        die(f"{slug}: sector must be one of {ALLOWED_SECTORS}, got {op['sector']!r}")
    if op["position_disclosure"] not in ALLOWED_DISCLOSURES:
        die(f"{slug}: position_disclosure must be one of {ALLOWED_DISCLOSURES}")
    sc = op["checklist"]["scoring"]
    if [s["q"] for s in sc] != list(range(1, 11)):
        die(f"{slug}: checklist.scoring must list questions 1..10 in order")
    for s in sc:
        if s.get("status") not in ALLOWED_STATUSES:
            die(f"{slug}: checklist q{s['q']} status invalid: {s.get('status')!r}")
    pc = op["checklist"]["pillar_commentary"]
    for k in ("I", "II", "III"):
        if not pc.get(k):
            die(f"{slug}: missing checklist.pillar_commentary.{k}")


def die(msg: str) -> None:
    sys.stderr.write(f"build_operators: error: {msg}\n")
    sys.exit(1)


def build_one(slug: str, all_ops: dict[str, dict], questions_doc: dict) -> Path:
    op = all_ops[slug]
    body_path = CONTENT_DIR / f"{slug}.md"
    if not body_path.exists():
        die(f"{slug}: missing {body_path.relative_to(ROOT)}")
    body_md = body_path.read_text(encoding="utf-8")
    body_html = render_markdown(body_md)

    page = PAGE_TEMPLATE.format(
        slug=slug,
        ticker=op["ticker"],
        page_eyebrow=op["page_eyebrow"],
        headline_html=op["headline_html"],
        page_title=op["page_title"],
        meta_description=op["meta_description"],
        og_title=op["og_title"],
        og_description=op["og_description"],
        og_image=op["og_image"],
        published_human=fmt_iso_human(op["published_iso"]),
        jsonld=build_jsonld(op),
        header_strip=render_header_strip(op),
        the_read=render_the_read(op),
        by_the_numbers=render_by_the_numbers(op),
        what_we_track=render_what_we_track(op),
        the_note=render_the_note(body_html),
        scorecard=render_scorecard(op, questions_doc["questions"], questions_doc["_pillars"]),
        disclosure_footer=render_disclosure_footer(op),
        related=render_related(op, all_ops),
    )

    out = OUT_DIR / f"{slug}.html"
    out.write_text(page, encoding="utf-8")
    return out


def main(argv: list[str]) -> int:
    if not QUESTIONS_FILE.exists():
        die(f"missing {QUESTIONS_FILE.relative_to(ROOT)}")
    questions_doc = json.loads(QUESTIONS_FILE.read_text(encoding="utf-8"))

    all_paths = sorted(DATA_DIR.glob("*.json"))
    all_ops: dict[str, dict] = {}
    for p in all_paths:
        slug = p.stem
        op = json.loads(p.read_text(encoding="utf-8"))
        op.setdefault("slug", slug)
        validate(op, slug)
        all_ops[slug] = op

    targets = argv[1:] if len(argv) > 1 else list(all_ops.keys())
    for slug in targets:
        if slug not in all_ops:
            die(f"unknown operator slug: {slug}")
        out = build_one(slug, all_ops, questions_doc)
        print(f"  wrote {out.relative_to(ROOT)}")

    print(f"build_operators: rendered {len(targets)} operator page(s).")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))

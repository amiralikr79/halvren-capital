#!/usr/bin/env python3
"""
build_glossary.py

Renders /glossary.html from /data/glossary.json.

The glossary page is the authoritative A-Z index. The same JSON drives
the inline popover behaviour via /glossary.js on operator and note pages.

Run from repo root:
  python3 scripts/build_glossary.py
"""
from __future__ import annotations
import json
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data" / "glossary.json"
OUT = ROOT / "glossary.html"


def _alpha_letter(t: dict) -> str:
    name = t["term"].lstrip("$_- ").upper()
    ch = name[0]
    return ch if ch.isalpha() else "#"


def render_jsonld(terms: list[dict]) -> str:
    base = "https://halvrencapital.com"
    items = [{
        "@type": "DefinedTermSet",
        "@id": f"{base}/glossary#set",
        "name": "Halvren Glossary",
        "url": f"{base}/glossary",
        "inLanguage": "en-CA",
        "creator": {"@id": f"{base}/#amirali"},
        "publisher": {"@id": f"{base}/#organization"},
    }]
    for t in terms:
        items.append({
            "@type": "DefinedTerm",
            "@id": f"{base}/glossary#term-{t['slug']}",
            "name": t["term"],
            "description": _strip(t["definition"]),
            "inDefinedTermSet": {"@id": f"{base}/glossary#set"},
        })
    items.append({
        "@type": "BreadcrumbList",
        "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": "Home", "item": f"{base}/"},
            {"@type": "ListItem", "position": 2, "name": "Glossary", "item": f"{base}/glossary"},
        ],
    })
    return json.dumps({"@context": "https://schema.org", "@graph": items}, ensure_ascii=False, separators=(",", ":"))


def _strip(s: str) -> str:
    import re
    return re.sub(r"<[^>]+>", "", s).replace("&amp;", "&").replace("&ndash;", "–").replace("&mdash;", "—")


def main() -> int:
    data = json.loads(DATA.read_text(encoding="utf-8"))
    terms = sorted(data["terms"], key=lambda t: t["term"].lower())

    groups = defaultdict(list)
    for t in terms:
        groups[_alpha_letter(t)].append(t)
    letters = sorted(groups.keys())

    # jump list (only letters with entries)
    jump_html = "\n".join(
        f'      <a href="#letter-{l}">{l}</a>' for l in letters
    )

    blocks: list[str] = []
    for l in letters:
        items = []
        for t in groups[l]:
            aliases_html = ""
            if t.get("aliases"):
                aliases_html = f'<p class="gl-aliases">also: {", ".join(t["aliases"])}</p>'
            items.append(f"""
        <div class="gl-entry" id="term-{t['slug']}" data-term="{t['term'].lower()}">
          <h3 class="gl-entry-h">{t['term']} <a class="gl-anchor" href="#term-{t['slug']}" aria-label="Permalink to {t['term']}">#</a></h3>
          {aliases_html}
          <p class="gl-entry-def">{t['definition']}</p>
        </div>""")
        blocks.append(f"""
      <section class="gl-letter-block" id="letter-{l}">
        <h2 class="gl-letter">{l}</h2>
        {''.join(items)}
      </section>""")

    jsonld = render_jsonld(terms)
    count = len(terms)

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0, viewport-fit=cover">
<title>Glossary — The terms the desk uses | Halvren Capital</title>
<meta name="description" content="The {count} terms Halvren uses most often, defined in plain language with one opinion baked in. AISC, FCF, ND/EBITDA, take-or-pay, half-cycle and the rest.">
<meta name="theme-color" content="#111010" media="(prefers-color-scheme: dark)">
<meta name="theme-color" content="#f7f6f2" media="(prefers-color-scheme: light)">
<meta name="color-scheme" content="dark light">
<script>(function(){{try{{var c=document.cookie.split('; ').find(function(r){{return r.indexOf('halvren-theme=')===0}});var s=c?c.split('=')[1]:null;var t=s||(window.matchMedia('(prefers-color-scheme: light)').matches?'light':'dark');document.documentElement.setAttribute('data-theme',t);}}catch(e){{document.documentElement.setAttribute('data-theme','dark');}}}})();</script>
<link rel="canonical" href="https://halvrencapital.com/glossary">
<meta property="og:type" content="website">
<meta property="og:title" content="Glossary — Halvren Capital">
<meta property="og:description" content="A working glossary of the terms Halvren uses, defined in plain language with one opinion baked in.">
<meta property="og:url" content="https://halvrencapital.com/glossary">
<meta property="og:image" content="https://halvrencapital.com/og.png">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:image" content="https://halvrencapital.com/og.png">
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
</nav>

<main id="main">
  <div class="gl-page">
    <aside class="gl-jump" aria-label="Jump to letter">
{jump_html}
    </aside>
    <section>
      <p class="doc-breadcrumb"><a href="/">Home</a><span class="doc-breadcrumb-sep">/</span><span>Glossary</span></p>
      <p class="section-label">Working glossary</p>
      <h1 class="doc-h1">The terms the desk uses, <em>defined.</em></h1>
      <p class="doc-meta">Maintained May 2026 &middot; {count} terms</p>
      <div class="gl-search-wrap">
        <input class="gl-search" type="search" id="gl-search" placeholder="Type to filter — e.g. AISC, take-or-pay, ROIC" aria-label="Filter glossary terms">
      </div>
      <div class="gl-list" id="gl-list">{''.join(blocks)}
      </div>
    </section>
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
    <a href="/version" class="footer-last-reviewed" title="Build provenance and changelog"><strong>Last reviewed:</strong> May 15, 2026</a>
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
    <a href="/research">Research</a>
    <a href="/notes">Notes</a>
    <a href="/coverage">Coverage</a>
    <a href="/checklist">Checklist</a>
    <a href="/methodology">Methodology</a>
    <a href="/glossary" aria-current="page">Glossary</a>
    <a href="/letters">Letters</a>
    <a href="/process">Process</a>
    <a href="/access">Access</a>
    <a href="/about">About</a>
  </nav>
  <div class="nav-overlay-foot">Halvren Capital &middot; Vancouver</div>
</aside>
<script src="/nav-overlay.js" defer></script>
<script>
(function(){{
  var input = document.getElementById('gl-search');
  if (!input) return;
  var entries = Array.prototype.slice.call(document.querySelectorAll('.gl-entry'));
  var blocks = Array.prototype.slice.call(document.querySelectorAll('.gl-letter-block'));
  input.addEventListener('input', function() {{
    var q = (input.value || '').trim().toLowerCase();
    if (!q) {{
      entries.forEach(function(e){{ e.style.display = ''; }});
      blocks.forEach(function(b){{ b.style.display = ''; }});
      return;
    }}
    entries.forEach(function(e) {{
      var term = (e.getAttribute('data-term') || '').toLowerCase();
      var def = (e.textContent || '').toLowerCase();
      var match = term.indexOf(q) !== -1 || def.indexOf(q) !== -1;
      e.style.display = match ? '' : 'none';
    }});
    blocks.forEach(function(b) {{
      var visible = Array.prototype.some.call(b.querySelectorAll('.gl-entry'), function(e){{ return e.style.display !== 'none'; }});
      b.style.display = visible ? '' : 'none';
    }});
  }});
}})();
</script>
</body>
</html>
"""
    OUT.write_text(html, encoding="utf-8")
    print(f"  wrote {OUT.relative_to(ROOT)} ({count} terms)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

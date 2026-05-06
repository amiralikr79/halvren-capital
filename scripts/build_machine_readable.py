#!/usr/bin/env python3
"""
build_machine_readable.py

Emits the three machine-readable artifacts the site exposes for LLM
indexing and crawler consumption:

  llms.txt        a slim, llmstxt.org-style index of the site's public surface
  llms-full.txt   concatenated full text — founding memo + checklist questions
                  + operator notes + recent digest entries — for offline ingestion
                  by an LLM. Capped soft at ~500KB.
  sitemap.xml     authoritative XML sitemap. Rebuilt from a single source of
                  truth across data/operators/, coverage/coverage.json,
                  data/digest/, content/letters/, etc.

Run from the repo root:

  python3 scripts/build_machine_readable.py

No third-party dependencies. Uses Python's html.parser to strip tags when
folding article HTML into plain text.
"""

from __future__ import annotations

import datetime as dt
import json
import re
import sys
from html.parser import HTMLParser
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SITE = "https://halvrencapital.com"
CHECKLIST = json.loads((ROOT / "content" / "checklist.json").read_text(encoding="utf-8"))


# --------------------------------------------------------------------------- #
# helpers
# --------------------------------------------------------------------------- #

class _ArticleTextExtractor(HTMLParser):
    """Pull plain text from inside <article class="doc-article">; tolerate
    operator pages, letters pages, and the founding memo. Ignores script,
    style, and svg content."""

    SKIP = {"script", "style", "svg", "noscript", "form", "button", "nav", "footer"}

    def __init__(self) -> None:
        super().__init__()
        self.in_article = 0
        self.skip_depth = 0
        self.buf: list[str] = []
        self.last_was_break = False

    def handle_starttag(self, tag, attrs):
        if tag in self.SKIP:
            self.skip_depth += 1
            return
        attr = dict(attrs)
        if tag == "article" and "doc-article" in (attr.get("class") or ""):
            self.in_article += 1
        if not self.in_article or self.skip_depth:
            return
        # block-level breaks become double newlines
        if tag in {"p", "div", "section", "li", "h1", "h2", "h3", "h4", "h5", "h6", "blockquote", "pre", "br", "hr"}:
            if not self.last_was_break:
                self.buf.append("\n\n" if tag != "br" else "\n")
                self.last_was_break = True

    def handle_endtag(self, tag):
        if tag in self.SKIP and self.skip_depth:
            self.skip_depth -= 1
            return
        if tag == "article" and self.in_article:
            self.in_article -= 1
        if self.in_article and tag in {"h1", "h2", "h3", "h4", "h5", "h6"}:
            if not self.last_was_break:
                self.buf.append("\n")
                self.last_was_break = True

    def handle_data(self, data):
        if self.in_article and not self.skip_depth and data.strip():
            self.buf.append(data)
            self.last_was_break = False

    def text(self) -> str:
        raw = "".join(self.buf)
        # collapse runs of whitespace, preserve paragraph boundaries
        raw = re.sub(r"[ \t]+", " ", raw)
        raw = re.sub(r"\n{3,}", "\n\n", raw)
        return raw.strip()


def html_to_text(path: Path) -> str:
    if not path.exists():
        return ""
    p = _ArticleTextExtractor()
    try:
        p.feed(path.read_text(encoding="utf-8"))
    except Exception:
        return ""
    return p.text()


def md_to_text(path: Path) -> str:
    if not path.exists():
        return ""
    src = path.read_text(encoding="utf-8")
    # strip basic markdown markers — we want the prose, not the formatting
    src = re.sub(r"<!--.*?-->", "", src, flags=re.DOTALL)
    src = re.sub(r"^(#{1,6})\s+", "", src, flags=re.MULTILINE)
    src = re.sub(r"_(.+?)_", r"\1", src)
    src = re.sub(r"\*\*(.+?)\*\*", r"\1", src)
    src = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", r"\1 (\2)", src)
    src = re.sub(r"<[^>]+>", "", src)
    return src.strip()


def _strip_inline_html(s: str) -> str:
    return re.sub(r"<[^>]+>", "", s).replace("&amp;", "&").replace("&mdash;", "—").replace("&middot;", "·").replace("&ldquo;", "“").replace("&rdquo;", "”")


# --------------------------------------------------------------------------- #
# loaders — single source of truth across the site
# --------------------------------------------------------------------------- #

def load_operators() -> list[dict]:
    out = []
    for p in sorted((ROOT / "data" / "operators").glob("*.json")):
        op = json.loads(p.read_text(encoding="utf-8"))
        op["__body_md"] = (ROOT / "content" / "operators" / f"{p.stem}.md").read_text(encoding="utf-8") if (ROOT / "content" / "operators" / f"{p.stem}.md").exists() else ""
        out.append(op)
    return out


def load_coverage() -> dict:
    p = ROOT / "coverage" / "coverage.json"
    return json.loads(p.read_text(encoding="utf-8")) if p.exists() else {"operators": []}


def load_digest_weeks() -> list[dict]:
    out = []
    for p in sorted((ROOT / "data" / "digest").glob("*.json"), reverse=True):
        try:
            data = json.loads(p.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            continue
        body_path = ROOT / "content" / "digest" / f"{p.stem}.md"
        data["__body_md"] = body_path.read_text(encoding="utf-8") if body_path.exists() else ""
        out.append(data)
    out.sort(key=lambda w: w.get("week_iso", ""), reverse=True)
    return out


# --------------------------------------------------------------------------- #
# llms.txt — slim index, llmstxt.org-style
# --------------------------------------------------------------------------- #

def render_llms_txt() -> str:
    operators = load_operators()
    coverage = load_coverage().get("operators", [])

    operator_lines = []
    for op in sorted(operators, key=lambda o: o["ticker"]):
        operator_lines.append(
            f"- [{op['short_name']} ({op['ticker']})]({SITE}/research/{op['slug']}): "
            f"{op['sector']} · {op['sub_industry']}. {op.get('the_read', {}).get('summary') or 'Halvren research note.'}"
        )

    queued = [o for o in coverage if not o.get("research_url")]
    queued_lines = []
    for o in sorted(queued, key=lambda o: o["ticker"])[:50]:
        queued_lines.append(
            f"- {o['ticker']} — {o['name']} · {o['sector']}/{o.get('sub_industry') or ''} (status: {o.get('status') or 'queued'})"
        )

    out = f"""# Halvren Capital

> Halvren Capital is an AI-augmented research desk covering Canadian and U.S. operators in energy, materials, and infrastructure. Models read at scale. The principal signs the decision. The book is proprietary. The work is public.

This file follows the llmstxt.org convention: a stable, machine-readable index of the most useful URLs on this site, with short descriptions. For everything below, the canonical site is {SITE}.

## What we publish

- [Homepage]({SITE}/): three sectors, one principal, the desk's beliefs, and the current watchlist.
- [Coverage universe]({SITE}/coverage): all 31 Canadian and U.S. operators on the desk, sortable. Includes [coverage.json]({SITE}/coverage/coverage.json) and [coverage.csv]({SITE}/coverage/coverage.csv) for direct ingestion.
- [The Halvren Checklist]({SITE}/checklist): the ten questions the desk runs before any operator earns the writeup. Pillars: the business (1–4), the people (5–8), the cycle (9–10).
- [Live Checklist scoring]({SITE}/checklist#cl-tool): a public tool that runs any ticker through the ten questions against current public filings via web search, with citations. Result URLs are shareable; the tool's output is machine-generated and explicitly not principal-reviewed.
- [Weekly digest archive]({SITE}/digest): each Friday, a short read on what the desk ingested across the coverage universe. Latest counters at [digest/latest.json]({SITE}/digest/latest.json).
- [Founding memo]({SITE}/memo/founding): why Halvren exists.

## Operator research notes

Each note carries a 30-word machine-readable abstract, full-cycle commentary, an FY snapshot, the Halvren Checklist applied, and disclosure. {len(operators)} notes published:

{chr(10).join(operator_lines)}

## On the desk (no full writeup yet)

{chr(10).join(queued_lines)}

## Contact and access

- Author: Amirali Karimi, founder and principal of Halvren Capital. SFU Economics, CFA candidate. Vancouver, BC.
- Email: amirali@halvrencapital.com
- Substack: https://substack.com/@halvrencapital
- LinkedIn: https://www.linkedin.com/in/amirali-karimi-405766199/
- Halvren manages proprietary capital and is **not currently accepting outside investors** — see [/access]({SITE}/access).

## License and AI training policy

Halvren publishes its public research for free for individual readers and for non-commercial educational use. AI training and machine ingestion are **permitted with attribution** to halvrencapital.com — see [/about]({SITE}/about) for the full AI & Indexing Policy. Commercial republication or paid syndication requires written permission. Nothing on this site is investment advice. See [/terms]({SITE}/terms) for the full disclaimer and [/privacy]({SITE}/privacy) for data practices (no analytics; no third-party tracking).

## Crawler etiquette

This site is intentionally lean: no tracking pixels, no third-party JS, warm-light CSS, static HTML where possible. Be polite — keep request rates modest, identify yourself in User-Agent, and respect [robots.txt]({SITE}/robots.txt). If you are an LLM training crawler, [llms-full.txt]({SITE}/llms-full.txt) is the concatenated long-form text in one file.
"""
    return out


# --------------------------------------------------------------------------- #
# llms-full.txt — concatenated long-form text
# --------------------------------------------------------------------------- #

def render_llms_full_txt() -> str:
    operators = load_operators()
    digests = load_digest_weeks()[:8]

    parts: list[str] = []
    parts.append("# Halvren Capital — full text bundle")
    parts.append("")
    parts.append(
        "This file concatenates the principal-authored long-form text on the site "
        "(founding memo, the Halvren Checklist, every operator research note, and "
        "the most recent digest entries) for offline ingestion by an LLM. Generated "
        f"on {dt.date.today().isoformat()} by scripts/build_machine_readable.py. The canonical site is "
        f"{SITE}. AI training is permitted with attribution; see {SITE}/about."
    )
    parts.append("")
    parts.append("---")
    parts.append("")

    # founding memo
    memo_path = ROOT / "memo" / "founding.html"
    parts.append("## Founding memo")
    parts.append(f"Source: {SITE}/memo/founding")
    parts.append("")
    memo_text = html_to_text(memo_path)
    parts.append(memo_text or "(founding memo unavailable at build time)")
    parts.append("")
    parts.append("---")
    parts.append("")

    # checklist questions
    parts.append("## The Halvren Checklist — ten questions")
    parts.append(f"Source: {SITE}/checklist")
    parts.append("")
    pillars = CHECKLIST.get("_pillars", {})
    for roman in ("I", "II", "III"):
        info = pillars.get(roman, {})
        parts.append(f"### Pillar {roman} — {info.get('label', '')}")
        for q in CHECKLIST["questions"]:
            if q["pillar"] != roman:
                continue
            parts.append(f"  {q['q']:>2}. {_strip_inline_html(q['question_html'])}")
            parts.append(f"      Standard note: {_strip_inline_html(q['default_note'])}")
        parts.append("")
    parts.append("---")
    parts.append("")

    # operator research notes
    parts.append("## Operator research notes")
    parts.append("")
    for op in sorted(operators, key=lambda o: o["ticker"]):
        url = f"{SITE}/research/{op['slug']}"
        parts.append(f"### {op['short_name']} ({op['ticker']}) — {op['sector']} · {op['sub_industry']}")
        parts.append(f"Source: {url}")
        parts.append(f"Last reviewed: {op.get('last_reviewed_iso') or '—'}")
        parts.append(f"Listings: {op['exchange']}")
        parts.append("")
        the_read = (op.get("the_read") or {}).get("summary")
        if the_read:
            parts.append(f"Machine-readable abstract: {the_read}")
            parts.append("")
        parts.append("**FY snapshot.** " + "; ".join(
            f"{m['label']}: {m['value']}" for m in (op.get("fy_snapshot") or {}).get("metrics", [])
        ))
        parts.append("")
        parts.append("**What we track.** " + " · ".join(op.get("what_we_track") or []))
        parts.append("")
        body = op.get("__body_md", "").strip()
        if body:
            # strip markdown formatting for plain text
            body = re.sub(r"^(#{1,6})\s+(.*)$", r"\2", body, flags=re.MULTILINE)
            body = re.sub(r"<[^>]+>", "", body)
            body = re.sub(r"_(.+?)_", r"\1", body)
            parts.append(body.strip())
            parts.append("")
        commentary = (op.get("checklist") or {}).get("pillar_commentary") or {}
        for k in ("I", "II", "III"):
            text = _strip_inline_html(commentary.get(k, ""))
            if text:
                parts.append(text)
                parts.append("")
        parts.append("---")
        parts.append("")

    # recent digest entries
    parts.append("## Recent digest entries (most recent 8)")
    parts.append("")
    for w in digests:
        url = f"{SITE}/digest/{w['week_iso']}"
        parts.append(f"### {w.get('week_label') or w['week_iso']}")
        parts.append(f"Source: {url}")
        backfill = " (backfilled at launch)" if w.get("backfilled") else ""
        parts.append(f"Counters{backfill}: {w.get('filings_ingested', 0)} filings, "
                     f"{w.get('pages_read', 0):,} pages, {w.get('audio_hours', 0)} audio hrs.")
        parts.append("")

        body = (w.get("__body_md") or "").strip()
        if body:
            body = re.sub(r"^(#{1,6})\s+(.*)$", r"\2", body, flags=re.MULTILINE)
            body = re.sub(r"<!--.*?-->", "", body, flags=re.DOTALL)
            body = re.sub(r"<[^>]+>", "", body)
            body = re.sub(r"_(.+?)_", r"\1", body)
            parts.append(body.strip())
            parts.append("")

        # rich items array (only present on Week 18 today)
        items = w.get("items") or []
        for it in items[:6]:
            parts.append(f"- {it.get('ticker')} {it.get('name')} ({it.get('sector_label')}): {_strip_inline_html(it.get('summary_html', ''))}")
            note = (it.get("note") or {}).get("body_html")
            if note:
                parts.append(f"    Note ({(it.get('note') or {}).get('label')}): {_strip_inline_html(note)}")
        parts.append("")
        parts.append("---")
        parts.append("")

    out = "\n".join(parts)
    return out


# --------------------------------------------------------------------------- #
# sitemap.xml — authoritative, regenerated from a single source
# --------------------------------------------------------------------------- #

STATIC_URLS = [
    # (path, priority, changefreq) — top-level routes that don't have generated lastmod
    ("/",                  "1.0",  "weekly"),
    ("/about",             "0.9",  "monthly"),
    ("/access",            "0.9",  "monthly"),
    ("/research",          "0.9",  "weekly"),
    ("/coverage",          "0.95", "weekly"),
    ("/coverage/coverage.json", "0.5", "weekly"),
    ("/coverage/coverage.csv",  "0.5", "weekly"),
    ("/digest",            "0.95", "weekly"),
    ("/digest/latest.json","0.5",  "weekly"),
    ("/performance",       "1.0",  "monthly"),
    ("/press",             "0.7",  "monthly"),
    ("/checklist",         "0.95", "monthly"),
    ("/process",           "0.9",  "monthly"),
    ("/glossary",          "0.7",  "monthly"),
    ("/letters",           "0.9",  "monthly"),
    ("/letters/q1-2026",   "0.8",  "yearly"),
    ("/letters/three-questions-2025", "0.9", "yearly"),
    ("/memo/founding",     "0.7",  "yearly"),
    ("/llms.txt",          "0.6",  "weekly"),
    ("/llms-full.txt",     "0.6",  "weekly"),
    ("/privacy",           "0.3",  "yearly"),
    ("/terms",             "0.3",  "yearly"),
]


def render_sitemap() -> str:
    today = dt.date.today().isoformat()
    operators = load_operators()
    digests = load_digest_weeks()

    rows: list[str] = []

    def row(loc: str, lastmod: str, freq: str, priority: str) -> None:
        rows.append(
            "  <url>\n"
            f"    <loc>{SITE}{loc}</loc>\n"
            f"    <lastmod>{lastmod}</lastmod>\n"
            f"    <changefreq>{freq}</changefreq>\n"
            f"    <priority>{priority}</priority>\n"
            "  </url>"
        )

    for path, priority, freq in STATIC_URLS:
        row(path, today, freq, priority)

    for op in sorted(operators, key=lambda o: o["ticker"]):
        lastmod = op.get("modified_iso") or op.get("last_reviewed_iso") or today
        row(f"/research/{op['slug']}", lastmod[:10], "monthly", "0.85")

    for w in digests:
        lastmod = (w.get("updated_iso") or w.get("week_of") or today)[:10]
        row(f"/digest/{w['week_iso']}", lastmod, "monthly", "0.75" if w.get("backfilled") else "0.85")

    body = "\n".join(rows)
    return (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        f"{body}\n"
        '</urlset>\n'
    )


# --------------------------------------------------------------------------- #
# driver
# --------------------------------------------------------------------------- #

def main() -> int:
    llms = render_llms_txt()
    full = render_llms_full_txt()
    sm = render_sitemap()

    (ROOT / "llms.txt").write_text(llms, encoding="utf-8")
    print(f"  wrote llms.txt ({len(llms.encode('utf-8')):,} bytes)")

    full_bytes = full.encode("utf-8")
    if len(full_bytes) > 500 * 1024:
        sys.stderr.write(
            f"build_machine_readable: warning: llms-full.txt is {len(full_bytes):,} bytes (> 500KB target)\n"
        )
    (ROOT / "llms-full.txt").write_text(full, encoding="utf-8")
    print(f"  wrote llms-full.txt ({len(full_bytes):,} bytes)")

    (ROOT / "sitemap.xml").write_text(sm, encoding="utf-8")
    n_urls = sm.count("<url>")
    print(f"  wrote sitemap.xml ({n_urls} URLs)")

    return 0


if __name__ == "__main__":
    sys.exit(main())

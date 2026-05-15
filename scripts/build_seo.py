#!/usr/bin/env python3
"""
build_seo.py

Sprint 7 — regenerate SEO + AEO infrastructure from authoritative sources.

Writes:
  sitemap.xml          — every public URL, lastmod from source files
  llms.txt             — llmstxt.org-style index, fresh against current state
  llms-full.txt        — long-form bundle for LLM ingestion
  feed.xml             — RSS 2.0 for /notes
  robots.txt           — refreshed allow/disallow list (idempotent rewrite)

Reads:
  coverage/coverage.json
  data/operators/<slug>.json
  data/checklist-examples.json
  content/notes/<slug>.mdx
  content/checklist.json

No third-party dependencies. Run from repo root:
  python3 scripts/build_seo.py
"""

from __future__ import annotations

import json
import re
import sys
from datetime import date, datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
NOTES_DIR = ROOT / "content" / "notes"
OPS_DIR = ROOT / "data" / "operators"
COVERAGE = ROOT / "coverage" / "coverage.json"
CHECKLIST = ROOT / "content" / "checklist.json"

BASE = "https://halvrencapital.com"
TODAY = date.today().isoformat()


# ---------------------------------------------------------------------------
# loaders
# ---------------------------------------------------------------------------

def _load_coverage() -> dict:
    return json.loads(COVERAGE.read_text(encoding="utf-8"))


def _load_op(slug: str) -> dict:
    return json.loads((OPS_DIR / f"{slug}.json").read_text(encoding="utf-8"))


def _parse_note(p: Path) -> tuple[dict, str]:
    src = p.read_text(encoding="utf-8")
    if not src.startswith("---\n"):
        raise SystemExit(f"{p.name}: missing frontmatter")
    end = src.find("\n---\n", 4)
    if end == -1:
        raise SystemExit(f"{p.name}: frontmatter not closed")
    head = src[4:end]
    body = src[end + 5:]
    meta: dict = {}
    lines = head.split("\n")
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
                buf: list[str] = []
                i += 1
                while i < len(lines) and (lines[i].startswith("  ") or lines[i] == ""):
                    buf.append(lines[i][2:] if lines[i].startswith("  ") else "")
                    i += 1
                meta[key] = "\n".join(buf).strip()
                continue
            if rest == "":
                items: list[str] = []
                i += 1
                while i < len(lines) and lines[i].lstrip().startswith("- "):
                    items.append(lines[i].lstrip()[2:].strip())
                    i += 1
                meta[key] = items
                continue
            if rest.isdigit():
                meta[key] = int(rest)
            else:
                meta[key] = rest.strip('"').strip("'")
            i += 1
            continue
        i += 1
    return meta, body


def _load_notes() -> list[dict]:
    out = []
    for p in sorted(NOTES_DIR.glob("*.mdx")):
        meta, body = _parse_note(p)
        meta["body"] = body
        out.append(meta)
    return out


# ---------------------------------------------------------------------------
# sitemap.xml
# ---------------------------------------------------------------------------

def build_sitemap(coverage: dict, notes: list[dict]) -> str:
    urls: list[tuple[str, str, str, str]] = []  # (loc, lastmod, changefreq, priority)

    def add(path: str, lastmod: str, changefreq: str = "monthly", priority: str = "0.7"):
        urls.append((BASE + path, lastmod, changefreq, priority))

    # core pages — Sprint 7 inventory
    add("/", TODAY, "weekly", "1.0")
    add("/about", TODAY, "monthly", "0.9")
    add("/research", TODAY, "weekly", "0.9")
    add("/coverage", TODAY, "weekly", "0.95")
    add("/coverage/coverage.json", TODAY, "weekly", "0.5")
    add("/coverage/coverage.csv", TODAY, "weekly", "0.5")
    add("/checklist", TODAY, "monthly", "0.95")
    add("/checklist/live", TODAY, "weekly", "0.95")
    add("/cycle-map",      TODAY, "weekly", "0.9")
    add("/cost-curves",    TODAY, "weekly", "0.85")
    add("/notes", TODAY, "weekly", "0.95")
    add("/digest", TODAY, "weekly", "0.95")
    add("/digest/latest.json", TODAY, "weekly", "0.5")
    add("/performance", TODAY, "monthly", "1.0")
    add("/press", TODAY, "monthly", "0.7")
    add("/process", TODAY, "monthly", "0.9")
    add("/letters", TODAY, "monthly", "0.9")
    add("/letters/q1-2026", TODAY, "yearly", "0.8")
    add("/letters/three-questions-2025", TODAY, "yearly", "0.9")
    add("/memo/founding", TODAY, "yearly", "0.7")
    add("/access", TODAY, "monthly", "0.9")
    add("/glossary", TODAY, "monthly", "0.7")
    add("/privacy", TODAY, "yearly", "0.3")
    add("/terms", TODAY, "yearly", "0.3")
    add("/llms.txt", TODAY, "weekly", "0.6")
    add("/llms-full.txt", TODAY, "weekly", "0.6")
    add("/feed.xml", TODAY, "weekly", "0.7")

    # research pages (one per published operator)
    for op in coverage["operators"]:
        if op.get("status") != "published" or not op.get("research_url"):
            continue
        last = op.get("last_reviewed_iso") or TODAY
        add(op["research_url"], last, "monthly", "0.85")

    # notes
    for n in notes:
        add(f"/notes/{n['slug']}", n["date"], "monthly", "0.85")

    # digest archive
    for d in sorted((ROOT / "digest").glob("2026-W*")):
        if d.is_dir() and (d / "index.html").exists():
            add(f"/digest/{d.name}", TODAY, "monthly", "0.75")

    body = "\n".join(
        f"  <url>\n    <loc>{loc}</loc>\n    <lastmod>{lm}</lastmod>\n"
        f"    <changefreq>{cf}</changefreq>\n    <priority>{pr}</priority>\n  </url>"
        for loc, lm, cf, pr in urls
    )
    return f'<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n{body}\n</urlset>\n'


# ---------------------------------------------------------------------------
# llms.txt — llmstxt.org-style index
# ---------------------------------------------------------------------------

def build_llms_txt(coverage: dict, notes: list[dict]) -> str:
    pub = [op for op in coverage["operators"] if op.get("status") == "published"]
    pub.sort(key=lambda o: (o["sector"], o["sub_industry"], o["ticker"]))

    L: list[str] = []
    L.append("# Halvren Capital")
    L.append("")
    L.append(
        "> Halvren Capital is a one-principal research desk in Vancouver. "
        "It covers twenty operators in Canadian and U.S. energy, materials, and infrastructure, deeply, "
        "with no managed product and no outside capital. "
        "Models read at scale. The principal signs the decision."
    )
    L.append("")
    L.append(
        "This file follows the llmstxt.org convention: a stable, machine-readable index of the most useful "
        f"URLs on this site, with short descriptions. The canonical site is {BASE}."
    )
    L.append("")

    L.append("## Core pages")
    L.append("")
    L.append(f"- [Homepage]({BASE}/): positioning, three sectors, the desk's beliefs, the 4 featured operators, and the Coverage Constellation.")
    L.append(f"- [About]({BASE}/about): the principal, what AI-augmented means in practice, sector rationale, how to read Halvren.")
    L.append(f"- [Coverage]({BASE}/coverage): all 21 Canadian and U.S. operators on the desk, sortable by sector + sub-industry. Includes [coverage.json]({BASE}/coverage/coverage.json) and [coverage.csv]({BASE}/coverage/coverage.csv).")
    L.append(f"- [Research archive]({BASE}/research): index of all published operator pages.")
    L.append(f"- [Halvren Notes]({BASE}/notes): 10 long-form essays on operator quality, cost curves, capital culture, and the framework.")
    L.append(f"- [The Halvren Checklist]({BASE}/checklist): the 10 questions every operator runs through before it earns a position. Pillars: business (1-4), people (5-8), cycle (9-10).")
    L.append(f"- [Checklist Live]({BASE}/checklist/live): a public streaming tool that runs the 10 questions on any Canadian or U.S. ticker in the principal's voice. Not principal-reviewed.")
    L.append(f"- [Weekly digest]({BASE}/digest): an AI-augmented read of every coverage-operator filing this week. Latest counters at [digest/latest.json]({BASE}/digest/latest.json).")
    L.append(f"- [Founding memo]({BASE}/memo/founding): why Halvren exists.")
    L.append(f"- [Performance]({BASE}/performance): the proprietary-book record since January 2019. No borrowing, no derivatives, no outside capital.")
    L.append(f"- [Process]({BASE}/process): the AI-augmented pipeline that feeds the desk.")
    L.append(f"- [Letters]({BASE}/letters): the quarterly Halvren letter (Substack canonical).")
    L.append(f"- [Glossary]({BASE}/glossary): the technical terms used in Halvren research.")
    L.append("")

    L.append("## Operator research")
    L.append("")
    L.append(f"Each operator page carries an FY snapshot, a principal-voice prose body, the Halvren Checklist scorecard applied, and disclosure. {len(pub)} pages published:")
    L.append("")
    for op in pub:
        try:
            full = _load_op(op["research_url"].split("/")[-1])
            summary = full.get("the_read", {}).get("summary", "")
        except Exception:
            summary = ""
        L.append(
            f"- [{op['short_name']} ({op['ticker']})]({BASE}{op['research_url']}): "
            f"{op['sector']} · {op['sub_industry']}. "
            + (summary[:240] + ("…" if len(summary) > 240 else "") if summary else "")
        )
    L.append("")

    L.append("## Halvren Notes")
    L.append("")
    L.append(f"{len(notes)} long-form essays. Each is 1,800–2,500 words, single-claim, in the principal's voice. No price targets, no recommendations.")
    L.append("")
    for n in sorted(notes, key=lambda x: x["date"], reverse=True):
        L.append(f"- [{n['title']}]({BASE}/notes/{n['slug']}) ({n['date']}): {n['meta_description']}")
    L.append("")

    L.append("## Infrastructure")
    L.append("")
    L.append(f"- [sitemap.xml]({BASE}/sitemap.xml): every indexable URL on the site.")
    L.append(f"- [llms-full.txt]({BASE}/llms-full.txt): concatenated long-form bundle of the most useful Halvren text, for LLM ingestion.")
    L.append(f"- [feed.xml]({BASE}/feed.xml): RSS 2.0 of Halvren Notes.")
    L.append(f"- [robots.txt]({BASE}/robots.txt): allow-list for reputable indexing and AI-assistant crawlers; disallow on /api/ and known scraper bots.")
    L.append("")

    L.append("## How to cite")
    L.append("")
    L.append("Attribution requested: `halvrencapital.com` plus the specific page URL. All public research is free to read and to ingest for non-commercial LLM training. Commercial republication or paid syndication requires written permission — write to amirali@halvrencapital.com.")
    L.append("")

    return "\n".join(L) + "\n"


# ---------------------------------------------------------------------------
# llms-full.txt — long-form bundle, designed for ingestion
# ---------------------------------------------------------------------------

def build_llms_full(coverage: dict, notes: list[dict]) -> str:
    pub = [op for op in coverage["operators"] if op.get("status") == "published"]
    pub.sort(key=lambda o: o["ticker"])

    L: list[str] = []
    L.append("# Halvren Capital — long-form bundle")
    L.append("")
    L.append(f"Built: {TODAY}. Canonical: {BASE}.")
    L.append("")
    L.append(
        "Halvren Capital is a one-principal research desk in Vancouver, BC, founded 2025. "
        "It covers twenty operators in Canadian and U.S. energy, materials, and infrastructure, deeply. "
        "Models read at scale; the principal reviews every conviction and signs every position. "
        "The book is proprietary; the work is public."
    )
    L.append("")
    L.append("Founder and principal: Amirali Karimi. Persian-Canadian, raised in Vancouver. "
             "Operating record: Karimi Developments (BC real estate), Tablo (software venture sold to Digikala, "
             "Iran's largest e-commerce platform, in 2023), and Boost Commerce Group (Canadian digital holding). "
             "Education: economics at Simon Fraser University in progress; BCIT Marketing Management diploma. "
             "Investment credentials: IFC passed April 2026; CIRO exams in progress; CFA candidate.")
    L.append("")

    L.append("## The Halvren Checklist (canonical 10 questions)")
    L.append("")
    chk = json.loads(CHECKLIST.read_text(encoding="utf-8"))
    pillars = chk["_pillars"]
    for roman in ("I", "II", "III"):
        L.append(f"### Pillar {roman} — {pillars[roman]['label']}")
        for q in chk["questions"]:
            if q["pillar"] != roman:
                continue
            txt = re.sub(r"<[^>]+>", "", q["question_html"]).replace("&amp;", "&").replace("&ldquo;", "“").replace("&rdquo;", "”")
            note = re.sub(r"<[^>]+>", "", q["default_note"])
            L.append(f"  {q['q']:02d}. {txt}")
            L.append(f"      Standard note: {note}")
        L.append("")

    L.append("## Coverage universe — 21 published operators")
    L.append("")
    L.append("Each block below lists ticker, listing, sector, sub-industry, last-reviewed date, and the principal's machine-summary line. Full pages live at /research/<slug>.")
    L.append("")
    for op in pub:
        try:
            full = _load_op(op["research_url"].split("/")[-1])
        except Exception:
            continue
        L.append(f"### {op['short_name']} ({op['ticker']}) — {op['sector']} · {op['sub_industry']}")
        L.append(f"  Listings: {op['exchange']}")
        L.append(f"  Last reviewed: {op.get('last_reviewed_iso') or '—'}")
        L.append(f"  Page: {BASE}{op['research_url']}")
        summary = full.get("the_read", {}).get("summary")
        if summary:
            L.append(f"  Read: {summary}")
        fy = full.get("fy_snapshot", {})
        metrics = fy.get("metrics") or []
        if metrics:
            L.append(f"  FY snapshot ({fy.get('period', 'FY')}):")
            for m in metrics[:8]:
                L.append(f"    - {m.get('label')}: {m.get('value')}")
        wt = full.get("what_we_track") or []
        if wt:
            L.append(f"  What we track: {' · '.join(wt)}")
        L.append("")

    L.append("## Halvren Notes — long-form essays")
    L.append("")
    L.append(f"{len(notes)} essays, 1,800–2,500 words each, in the principal's voice. Single-claim, no price targets, no recommendations.")
    L.append("")
    for n in sorted(notes, key=lambda x: x["date"], reverse=True):
        L.append(f"### {n['title']}")
        L.append(f"  URL: {BASE}/notes/{n['slug']}")
        L.append(f"  Date: {n['date']} · {n.get('reading_time', '—')}-min read")
        L.append(f"  Tags: {', '.join(n.get('tags') or [])}")
        L.append(f"  Summary: {n['meta_description']}")
        L.append("")
        # Pull just the first paragraph of the body for context
        body = n.get("body") or ""
        first_para = re.split(r"\n\s*\n", body.strip(), maxsplit=1)[0]
        first_para = first_para.replace("\n", " ").strip()
        L.append(f"  Lede: {first_para[:600] + ('…' if len(first_para) > 600 else '')}")
        L.append("")

    L.append("## How to cite")
    L.append("")
    L.append("Attribution requested: halvrencapital.com plus the specific page URL. All public research is free to read and to ingest for non-commercial LLM training. Commercial republication or paid syndication requires written permission — write to amirali@halvrencapital.com.")
    L.append("")

    return "\n".join(L) + "\n"


# ---------------------------------------------------------------------------
# feed.xml — RSS 2.0 for /notes
# ---------------------------------------------------------------------------

def _xml_escape(s: str) -> str:
    return (
        s.replace("&", "&amp;")
         .replace("<", "&lt;")
         .replace(">", "&gt;")
         .replace('"', "&quot;")
         .replace("'", "&apos;")
    )


def build_feed(notes: list[dict]) -> str:
    notes_sorted = sorted(notes, key=lambda n: n["date"], reverse=True)
    items: list[str] = []
    for n in notes_sorted:
        # RFC-822 pub date — best we can do without a clock per note
        pub = datetime.fromisoformat(n["date"]).replace(tzinfo=timezone.utc)
        rfc = pub.strftime("%a, %d %b %Y %H:%M:%S +0000")
        items.append(
            "    <item>\n"
            f"      <title>{_xml_escape(n['title'])}</title>\n"
            f"      <link>{BASE}/notes/{n['slug']}</link>\n"
            f"      <guid isPermaLink=\"true\">{BASE}/notes/{n['slug']}</guid>\n"
            f"      <pubDate>{rfc}</pubDate>\n"
            f"      <author>amirali@halvrencapital.com (Amirali Karimi)</author>\n"
            f"      <description>{_xml_escape(n['meta_description'])}</description>\n"
            "    </item>"
        )
    return (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<rss version="2.0" xmlns:atom="http://www.w3.org/2005/Atom">\n'
        '  <channel>\n'
        '    <title>Halvren Notes</title>\n'
        f'    <link>{BASE}/notes</link>\n'
        '    <description>Single-claim essays from the Halvren Capital research desk on operator quality, cost curves, capital culture, and the framework.</description>\n'
        '    <language>en-CA</language>\n'
        f'    <lastBuildDate>{datetime.now(timezone.utc).strftime("%a, %d %b %Y %H:%M:%S +0000")}</lastBuildDate>\n'
        f'    <atom:link href="{BASE}/feed.xml" rel="self" type="application/rss+xml" />\n'
        + "\n".join(items)
        + "\n  </channel>\n</rss>\n"
    )


# ---------------------------------------------------------------------------
# main
# ---------------------------------------------------------------------------

def main() -> int:
    coverage = _load_coverage()
    notes = _load_notes()

    (ROOT / "sitemap.xml").write_text(build_sitemap(coverage, notes), encoding="utf-8")
    print(f"  wrote sitemap.xml ({len(coverage['operators'])} operators, {len(notes)} notes)")

    (ROOT / "llms.txt").write_text(build_llms_txt(coverage, notes), encoding="utf-8")
    print(f"  wrote llms.txt")

    (ROOT / "llms-full.txt").write_text(build_llms_full(coverage, notes), encoding="utf-8")
    print(f"  wrote llms-full.txt")

    (ROOT / "feed.xml").write_text(build_feed(notes), encoding="utf-8")
    print(f"  wrote feed.xml ({len(notes)} items)")

    print("build_seo: done.")
    return 0


if __name__ == "__main__":
    sys.exit(main())

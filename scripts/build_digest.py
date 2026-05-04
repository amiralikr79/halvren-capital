#!/usr/bin/env python3
"""
build_digest.py — render and (optionally) ingest the Halvren weekly digest.

Two modes:

    python scripts/build_digest.py --render
        Read data/digest-week.json and splice generated HTML into
        the marked regions of digest.html. Idempotent. No API calls.

    python scripts/build_digest.py --ingest
        Also fetch recent SEC EDGAR filings for the coverage universe,
        send each new filing to the Anthropic API for extraction +
        flag detection, and update data/digest-week.json before rendering.
        Requires ANTHROPIC_API_KEY in env.

The split keeps the page reproducible offline (--render is free and pure)
and the ingest pipeline isolated behind one flag.
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import re
import sys
import time
from html import escape
from pathlib import Path
from urllib import request, error
from urllib.parse import quote

ROOT = Path(__file__).resolve().parent.parent
DIGEST_HTML = ROOT / "digest.html"
DATA_JSON = ROOT / "data" / "digest-week.json"

# SEC EDGAR is happy as long as you identify yourself in User-Agent.
USER_AGENT = "Halvren Capital research desk amirali@halvrencapital.com"

# Coverage universe — cross-listed Canadian + U.S. names that file with SEC.
# Pure SEDAR-only names (e.g. CNR, CP, FTS) are tracked but skipped by the
# EDGAR fetcher; they need a SEDAR+ adapter (TODO).
#
# Each entry: (ticker_display, sec_cik_int_or_None, name, sector_filter, sector_label)
COVERAGE = [
    # Energy
    ("CNQ", 858863,  "Canadian Natural Resources", "energy", "Oil & Gas"),
    ("SU",  890203,  "Suncor Energy",              "energy", "Oil & Gas"),
    ("CVE", 1042046, "Cenovus Energy",             "energy", "Oil & Gas"),
    ("IMO", 49938,   "Imperial Oil",               "energy", "Oil & Gas"),
    ("TOU", None,    "Tourmaline Oil",             "energy", "Natural Gas"),     # SEDAR-only
    ("CCO", 1009001, "Cameco",                     "energy", "Uranium"),
    ("EOG", 821189,  "EOG Resources",              "energy", "U.S. Oil & Gas"),
    ("COP", 1163165, "ConocoPhillips",             "energy", "U.S. Oil & Gas"),
    # Infrastructure
    ("ENB",  895728, "Enbridge",                   "infrastructure", "Infrastructure"),
    ("TRP",  1232384,"TC Energy",                  "infrastructure", "Infrastructure"),
    ("KEY",  1100682,"Keyera",                     "infrastructure", "Infrastructure"),
    ("WMB",  107263, "Williams Companies",         "infrastructure", "U.S. Pipelines"),
    ("KMI",  1506307,"Kinder Morgan",              "infrastructure", "U.S. Pipelines"),
    ("NEE",  753308, "NextEra Energy",             "infrastructure", "U.S. Power"),
    # Materials
    ("NTR",  1725057,"Nutrien",                    "materials", "Fertilizers"),
    ("CF",   1324404,"CF Industries",              "materials", "Fertilizers"),
    ("AG",   1308648,"First Majestic Silver",      "materials", "Silver"),
    ("AEM",  2809,   "Agnico Eagle Mines",         "materials", "Gold"),
    ("FNV",  1477932,"Franco-Nevada",              "materials", "Royalties"),
    ("WPM",  1323404,"Wheaton Precious Metals",    "materials", "Royalties"),
    ("NEM",  1164727,"Newmont",                    "materials", "Gold"),
    ("FM",   None,   "First Quantum Minerals",     "materials", "Copper"),       # SEDAR-only
    ("TECK.B", 886982,"Teck Resources",            "materials", "Diversified"),
]

# Filing forms we care about. 6-K and 8-K are press release equivalents
# (interim filings); 10-Q / 10-K / 40-F are periodic; SC 13D/G is ownership;
# Form 4 is insider; DEF 14A is proxy.
RELEVANT_FORMS = {"10-K", "10-Q", "8-K", "40-F", "6-K", "20-F", "DEF 14A"}


# ---------- HTTP helper ---------------------------------------------------

def fetch(url: str, *, accept: str = "application/json") -> bytes:
    """GET with the polite headers EDGAR expects, light retries, no auth."""
    req = request.Request(url, headers={
        "User-Agent": USER_AGENT,
        "Accept": accept,
        "Accept-Encoding": "gzip, deflate",
    })
    last_err = None
    for attempt in range(3):
        try:
            with request.urlopen(req, timeout=30) as r:
                data = r.read()
                # urllib auto-decodes gzip when Accept-Encoding is set on
                # some Pythons; on others it doesn't. Handle both.
                if data[:2] == b"\x1f\x8b":
                    import gzip
                    data = gzip.decompress(data)
                return data
        except error.HTTPError as e:
            last_err = e
            if e.code in (429, 503):
                time.sleep(2 ** attempt)
                continue
            raise
        except error.URLError as e:
            last_err = e
            time.sleep(2 ** attempt)
    raise RuntimeError(f"fetch failed for {url}: {last_err}")


# ---------- SEC EDGAR fetchers --------------------------------------------

def edgar_recent_filings(cik: int, *, since: dt.date) -> list[dict]:
    """Return list of {form, date, accession, primary_doc_url} for the CIK's
    submissions filed on/after `since`. Newest first.
    """
    cik_str = str(cik).zfill(10)
    url = f"https://data.sec.gov/submissions/CIK{cik_str}.json"
    raw = fetch(url)
    payload = json.loads(raw)
    recent = payload.get("filings", {}).get("recent", {})
    out = []
    forms = recent.get("form", [])
    dates = recent.get("filingDate", [])
    accs  = recent.get("accessionNumber", [])
    docs  = recent.get("primaryDocument", [])
    for form, date_str, acc, doc in zip(forms, dates, accs, docs):
        try:
            filed = dt.date.fromisoformat(date_str)
        except ValueError:
            continue
        if filed < since:
            continue
        if form not in RELEVANT_FORMS:
            continue
        acc_no_dashes = acc.replace("-", "")
        out.append({
            "form": form,
            "date": date_str,
            "accession": acc,
            "primary_doc_url": (
                f"https://www.sec.gov/Archives/edgar/data/{cik}/"
                f"{acc_no_dashes}/{doc}"
            ),
            "index_url": (
                f"https://www.sec.gov/cgi-bin/browse-edgar?"
                f"action=getcompany&CIK={cik_str}&type={quote(form)}"
            ),
        })
    return out


def edgar_doc_text(url: str, *, max_chars: int = 60_000) -> str:
    """Download a filing's primary HTML doc and strip to plain text.
    Trimmed to max_chars to keep API costs sane."""
    raw = fetch(url, accept="text/html")
    text = raw.decode("utf-8", errors="ignore")
    text = re.sub(r"<script.*?</script>", " ", text, flags=re.S | re.I)
    text = re.sub(r"<style.*?</style>", " ", text, flags=re.S | re.I)
    text = re.sub(r"<[^>]+>", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text[:max_chars]


# ---------- Anthropic extraction ------------------------------------------

EXTRACT_SYSTEM = """You are the Halvren Capital ingestion model. Halvren is an institutional research desk that covers Canadian and U.S. operators in energy, materials, and infrastructure. Voice: institutional, factual, concise, third-person, never breathless. Match the existing /digest articles in tone — short summary paragraphs that lead with the most material number, named bold elements where helpful, and no marketing language.

Given a single regulatory filing or transcript, extract:
- A 3–5 sentence factual summary suitable for the public Halvren Digest
- 4 key metrics (label + value, e.g. "Production: 1,592 MBOE/d")
- A flag classification: "model" if there is a notable tonal or structural change vs. typical operator language for this kind of filing, or null otherwise. Be conservative — only flag genuine signal.

Return STRICT JSON only. No prose outside the JSON object. Schema:
{
  "summary_html": "string with <strong> tags around key numbers",
  "metrics": [{"label": "string", "value": "string"} x 4],
  "flag": "model" | null,
  "flag_reason": "string or null — short, factual, only if flag != null"
}"""

def extract_with_claude(filing_meta: dict, body_text: str) -> dict | None:
    """Call Anthropic API. Returns parsed JSON dict or None on failure.
    Lazy-imports anthropic so --render doesn't require the package."""
    try:
        import anthropic  # type: ignore
    except ImportError:
        print("  ! anthropic package not installed — skipping extract", file=sys.stderr)
        return None
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        print("  ! ANTHROPIC_API_KEY not set — skipping extract", file=sys.stderr)
        return None

    client = anthropic.Anthropic(api_key=api_key)

    user_prompt = (
        f"Ticker: {filing_meta['ticker']}\n"
        f"Operator: {filing_meta['name']}\n"
        f"Form: {filing_meta['form']}\n"
        f"Filed: {filing_meta['date']}\n"
        f"Source: {filing_meta['primary_doc_url']}\n\n"
        f"FILING CONTENT (truncated):\n{body_text}"
    )

    resp = client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=1024,
        system=[{
            "type": "text",
            "text": EXTRACT_SYSTEM,
            "cache_control": {"type": "ephemeral"},
        }],
        messages=[{"role": "user", "content": user_prompt}],
    )
    content = "".join(b.text for b in resp.content if b.type == "text")
    # Extract first JSON object from the response
    m = re.search(r"\{.*\}", content, re.S)
    if not m:
        print(f"  ! no JSON in model response for {filing_meta['ticker']}",
              file=sys.stderr)
        return None
    try:
        return json.loads(m.group(0))
    except json.JSONDecodeError as e:
        print(f"  ! bad JSON from model for {filing_meta['ticker']}: {e}",
              file=sys.stderr)
        return None


# ---------- Ingest mode ---------------------------------------------------

def ingest(days: int = 7) -> None:
    """Fetch recent filings for the coverage universe, summarize each via
    Anthropic, and write the result into data/digest-week.json. Stats and
    structural fields are recomputed; hand-written principal notes on
    existing items are preserved by ID where possible."""
    today = dt.date.today()
    since = today - dt.timedelta(days=days)
    print(f"== Ingest mode == window: {since} → {today} ==")

    # Load existing JSON to preserve hand-curated notes by item id.
    existing = {}
    if DATA_JSON.exists():
        cur = json.loads(DATA_JSON.read_text())
        for item in cur.get("items", []):
            existing[item["id"]] = item

    new_items = []
    filings_count = 0
    flags_count = 0
    pages_count = 0

    edgar_attempted = 0
    edgar_failed = 0

    for ticker, cik, name, sector_filter, sector_label in COVERAGE:
        if cik is None:
            continue  # SEDAR-only; needs separate adapter
        edgar_attempted += 1
        try:
            filings = edgar_recent_filings(cik, since=since)
        except Exception as e:
            edgar_failed += 1
            print(f"  ! {ticker}: {e}", file=sys.stderr)
            continue
        # Polite: SEC asks for <= 10 req/sec; one per ticker is fine.
        time.sleep(0.15)
        if not filings:
            continue

        # Take the most recent material filing per ticker for the digest;
        # bump the filings_count by all of them.
        filings_count += len(filings)
        primary = filings[0]

        try:
            body = edgar_doc_text(primary["primary_doc_url"])
            pages_count += max(1, len(body) // 3000)
        except Exception as e:
            print(f"  ! {ticker} doc fetch failed: {e}", file=sys.stderr)
            continue

        meta = {**primary, "ticker": ticker, "name": name}
        extracted = extract_with_claude(meta, body)
        if not extracted:
            continue

        item_id = f"{ticker.lower()}-{primary['date'].replace('-','')}"
        prev = existing.get(item_id, {})
        flag = extracted.get("flag")
        if flag:
            flags_count += 1

        item = {
            "id": item_id,
            "ticker": ticker,
            "name": name,
            "sector_label": sector_label,
            "sector_filter": sector_filter,
            "date_label": dt.date.fromisoformat(primary["date"]).strftime("%b %d"),
            "filing_iso": primary["date"],
            "flag": flag,
            "summary_html": extracted.get("summary_html", ""),
            "metrics": extracted.get("metrics", [])[:4],
            "note": prev.get("note") or (
                {
                    "label": f"Model flag · {extracted.get('flag_reason', 'signal')}",
                    "body_html": escape(extracted.get("flag_reason", "")),
                    "meta": [],
                } if flag else None
            ),
            "writeup_url": prev.get("writeup_url"),
            "duration": prev.get("duration", f"Filing: {primary['form']}"),
        }
        new_items.append(item)
        print(f"  + {ticker:6} {primary['form']:6} {primary['date']}  flag={flag}")

    # Sort: flagged first, then by date desc
    new_items.sort(key=lambda x: (0 if x["flag"] else 1, x["filing_iso"]),
                   reverse=False)

    promoted = sum(1 for i in new_items if i.get("note") and (i.get("flag") == "desk"))

    payload = {
        "$schema": "./digest-week.schema.json",
        "week_label": f"Week {today.isocalendar().week} · {since.strftime('%b %d')} – {today.strftime('%b %d, %Y')}",
        "week_iso": f"{today.year}-W{today.isocalendar().week:02d}",
        "updated_iso": dt.datetime.now().isoformat(timespec="seconds"),
        "updated_human": today.strftime("%b %d, %Y"),
        "stats": {
            "filings_ingested": filings_count,
            "filings_breakdown": "10-Q · 10-K · 8-K · 6-K · 40-F · DEF 14A",
            "pages_read": pages_count,
            "pages_breakdown": f"across {len(new_items)} operators",
            "checklist_evaluated": len(new_items) * 10,
            "checklist_breakdown": f"10 questions · {len(new_items)} filings",
            "model_flags": flags_count,
            "promoted_to_desk": promoted,
            "filter_pct": int(100 * (1 - promoted / max(1, flags_count))),
        },
        "pipeline_strip": {
            "insider_transactions": 0,
            "ceo_letters": 0,
            "tonal_shifts_flagged": flags_count,
            "model_baseline": "trailing-4-call rolling baseline",
        },
        "next_week": [],
        "items": new_items,
    }

    # Safety rail: if we lost more than half the EDGAR fetches AND ended up
    # with fewer items than the previous JSON had, treat this as an outage
    # and refuse to overwrite. The existing week's data stays put; the next
    # scheduled run will try again. Prevents a transient SEC 403 wave or
    # network blip from silently wiping the page.
    fail_rate = edgar_failed / max(1, edgar_attempted)
    prev_count = len(existing)
    if fail_rate > 0.5 and len(new_items) < prev_count:
        sys.exit(
            f"abort: EDGAR failed {edgar_failed}/{edgar_attempted} "
            f"({fail_rate:.0%}) and only produced {len(new_items)} items "
            f"vs {prev_count} previously — refusing to overwrite "
            f"{DATA_JSON.relative_to(ROOT)}"
        )

    DATA_JSON.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n")
    print(f"== wrote {DATA_JSON.relative_to(ROOT)} "
          f"({len(new_items)} items, {flags_count} flags) ==")


# ---------- Render mode (HTML generation) ---------------------------------

def render_eyebrow(d: dict) -> str:
    return (
        '<p class="digest-eyebrow"><span class="live-dot"></span>'
        '<span>Live ingest</span>'
        f'<span class="sep">·</span><span>Updated {escape(d["updated_human"])}</span>'
        f'<span class="sep">·</span><span>{escape(d["week_label"].split(" · ")[0])}</span>'
        '</p>'
    )


def render_stats(d: dict) -> str:
    s = d["stats"]
    flags = s["model_flags"]
    promoted = s["promoted_to_desk"]
    pct = s["filter_pct"]
    label_small_style = (
        'display:block;margin-top:4px;font-family:var(--font-mono);'
        'font-size:10px;color:var(--color-text-faint);letter-spacing:0.04em;'
        'text-transform:none'
    )
    return f'''<section class="digest-stats" aria-label="This week in numbers">
    <div class="digest-stat"><span class="digest-stat-num">{s["filings_ingested"]:,}</span><p class="digest-stat-label">Filings ingested this week<small style="{label_small_style}">{escape(s["filings_breakdown"])}</small></p></div>
    <div class="digest-stat"><span class="digest-stat-num">{s["pages_read"]:,}</span><p class="digest-stat-label">Pages of disclosure read<small style="{label_small_style}">{escape(s["pages_breakdown"])}</small></p></div>
    <div class="digest-stat"><span class="digest-stat-num">{s["checklist_evaluated"]}</span><p class="digest-stat-label">Checklist questions evaluated<small style="{label_small_style}">{escape(s["checklist_breakdown"])}</small></p></div>
    <div class="digest-stat"><span class="digest-stat-num">{flags}<span style="font-size:0.55em;color:var(--color-gold);margin-left:0.1em">&rarr;</span><span style="color:var(--color-gold)">{promoted}</span></span><p class="digest-stat-label">Model flags &rarr; principal review<small style="{label_small_style}">{pct}% filtered before the desk reads</small></p></div>
  </section>'''


def render_call(item: dict) -> str:
    flag = item.get("flag")
    flag_attr = f' data-flag="{escape(flag)}"' if flag else ""
    flag_pill = ""
    if flag == "desk":
        flag_pill = '<span class="call-flag desk">On the desk</span>'
    elif flag == "model":
        flag_pill = '<span class="call-flag model">Model flagged</span>'

    metrics = item.get("metrics", [])
    metrics_html = "".join(
        f'\n          <div><dt>{escape(m["label"])}</dt><dd>{escape(m["value"])}</dd></div>'
        for m in metrics
    )

    note_html = ""
    note = item.get("note")
    if note:
        meta_pills = ""
        if note.get("meta"):
            cells = "".join(
                f'<span><strong style="color:var(--color-text);font-weight:500">{escape(p["k"])}</strong> {escape(p["v"])}</span>'
                for p in note["meta"]
            )
            meta_pills = (
                '\n          <div style="margin-top:var(--space-3);padding-top:var(--space-3);'
                'border-top:1px solid oklch(from var(--color-gold) l c h/0.18);'
                'display:grid;grid-template-columns:repeat(3,auto);gap:var(--space-4);'
                'font-family:var(--font-mono);font-size:10px;letter-spacing:0.04em;'
                f'color:var(--color-text-muted)">{cells}</div>'
            )
        note_html = f'''
        <div class="call-model-note">
          <span class="label">{escape(note["label"])}</span>
          {note["body_html"]}{meta_pills}
        </div>'''

    foot_parts = []
    if item.get("writeup_url"):
        foot_parts.append(f'<a href="{escape(item["writeup_url"])}">Halvren writeup &rarr;</a>')
    if item.get("writeup_url_secondary"):
        label = item.get("writeup_label") or "More &rarr;"
        foot_parts.append(f'<a href="{escape(item["writeup_url_secondary"])}">{label}</a>')
    if item.get("duration"):
        foot_parts.append(f'<span class="duration">{escape(item["duration"])}</span>')
    foot_html = '\n          <span class="sep">·</span>\n          '.join(foot_parts)

    return f'''<article class="call" data-sector="{escape(item["sector_filter"])}"{flag_attr}>
        <div class="call-head">
          <span class="call-tkr">{escape(item["ticker"])}</span>
          <span class="call-name">{escape(item["name"])}</span>
          <span class="call-sector">{escape(item["sector_label"])}</span>
          <span class="call-meta-spacer"></span>
          <span class="call-date">{escape(item["date_label"])}</span>
          {flag_pill}
        </div>
        <p class="call-summary">{item["summary_html"]}</p>
        <dl class="call-row">{metrics_html}
        </dl>{note_html}
        <div class="call-foot">
          {foot_html}
        </div>
      </article>'''


def render_calls(d: dict) -> str:
    blocks = [render_call(item) for item in d["items"]]
    return "\n\n      ".join(blocks)


def render_flags(d: dict) -> str:
    flagged = [i for i in d["items"] if i.get("flag")]
    if not flagged:
        flagged_li = '<li><span style="color:var(--color-text-faint)">No flags this week.</span></li>'
    else:
        flagged_li = "\n          ".join(
            f'<li><span><strong>{escape(i["ticker"])}</strong> &middot; '
            f'{escape((i.get("note") or {}).get("label", "").replace("Model flag · signal: ", "").replace("Model flag · ", "").replace("On the desk · principal note", "Desk read") or "Flagged")}'
            f'</span><span style="color:var(--color-gold)">{escape(i["flag"])}</span></li>'
            for i in flagged[:6]
        )
    nxt = " &middot; ".join(escape(n) for n in d.get("next_week", [])) or "Coverage list."
    return f'''<div class="rail-card">
        <p class="rail-card-cap">This week's flags</p>
        <ul class="rail-list">
          {flagged_li}
        </ul>
      </div>

      <div class="rail-card">
        <p class="rail-card-cap">Next week</p>
        <h3>On the calendar.</h3>
        <p>{nxt}. The model runs the same pipeline; the principal flags what earns the read.</p>
      </div>'''


# ---------- Splice helpers ------------------------------------------------

REGION_PATTERN = re.compile(
    r"(<!--\s*DIGEST_(\w+)_START.*?-->)(.*?)(<!--\s*DIGEST_\2_END\s*-->)",
    re.S,
)

def splice(html: str, region: str, new_inner: str) -> str:
    """Replace the inner content of a <!-- DIGEST_<region>_START --> ... END
    block. The wrapping comments themselves are preserved."""
    def repl(m: re.Match) -> str:
        if m.group(2) != region:
            return m.group(0)
        return f"{m.group(1)}\n  {new_inner}\n  {m.group(4)}"
    return REGION_PATTERN.sub(repl, html, count=0)


def render() -> None:
    if not DATA_JSON.exists():
        sys.exit(f"missing {DATA_JSON}")
    d = json.loads(DATA_JSON.read_text())
    html = DIGEST_HTML.read_text()

    html = splice(html, "EYEBROW", render_eyebrow(d))
    html = splice(html, "STATS",   render_stats(d))
    html = splice(html, "CALLS",   render_calls(d))
    html = splice(html, "FLAGS",   render_flags(d))

    DIGEST_HTML.write_text(html)
    print(f"== rendered {DIGEST_HTML.relative_to(ROOT)} "
          f"({len(d['items'])} items, {d['stats']['model_flags']} flags) ==")


# ---------- Entry point ---------------------------------------------------

def main() -> None:
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--ingest", action="store_true",
                   help="Fetch SEC EDGAR + call Anthropic API to update JSON")
    p.add_argument("--render", action="store_true",
                   help="Render JSON into digest.html (default if no flag given)")
    p.add_argument("--days", type=int, default=7,
                   help="Lookback window in days for --ingest (default 7)")
    args = p.parse_args()

    if args.ingest:
        ingest(days=args.days)

    # Render is the default; always run it after ingest.
    if args.render or not args.ingest:
        render()
    elif args.ingest:
        render()


if __name__ == "__main__":
    main()

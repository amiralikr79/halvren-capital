# Halvren build scripts

Scripts that turn the static site into a *living* one. Right now there is
exactly one: `build_digest.py`, the pipeline behind [`/digest`](../digest.html).

---

## `build_digest.py` — weekly Halvren Digest

### What it does

The Halvren Digest is a weekly AI-augmented read of every Canadian and U.S.
operator on the [coverage list](../coverage.html). The script turns that
into a page:

```
SEC EDGAR  ─┐
            ├─►  scripts/build_digest.py  ─►  data/digest-week.json  ─►  digest.html
SEDAR+ ─────┘                            (Anthropic API for extraction)        (spliced into marked regions)
```

The HTML is server-rendered. No client-side fetching, no JS dependency, no
hydration jankiness. The page reads exactly the same with JS off.

### Two modes

```bash
# 1) Render mode (default). Free, offline, idempotent. Reads the JSON and
#    splices it into digest.html. Run anytime to refresh after editing the
#    JSON by hand.
python3 scripts/build_digest.py --render

# 2) Ingest mode. Fetches recent SEC EDGAR filings for every cross-listed
#    name in COVERAGE (in the script), summarises each via the Anthropic
#    API, updates data/digest-week.json, then re-renders. Requires
#    ANTHROPIC_API_KEY in env.
ANTHROPIC_API_KEY=sk-ant-... python3 scripts/build_digest.py --ingest
```

Common combos:

```bash
# Default (no flag) → render only
python3 scripts/build_digest.py

# Ingest with a 30-day lookback (instead of the default 7)
python3 scripts/build_digest.py --ingest --days 30
```

### What gets generated

The script splices into four marked regions in `digest.html`:

- `<!-- DIGEST_EYEBROW_START / END -->` — the live-ingest pill at the top
- `<!-- DIGEST_STATS_START / END -->` — the four-up numbers strip
- `<!-- DIGEST_CALLS_START / END -->` — the call/filing article cards
- `<!-- DIGEST_FLAGS_START / END -->` — the right-rail flag list + next week

Everything else in `digest.html` is hand-controlled. You can edit the
methodology, the rail copy, the lead heading, the subscribe form — none of
it gets touched.

### Source of truth

`data/digest-week.json` holds the structured data for the current week. It is
the **single source of truth** — render is just a deterministic projection of
this file into HTML. When ingest runs, it overwrites this file but
**preserves hand-curated principal notes by item id**, so any "On the desk"
commentary you add by hand survives the next ingest.

### Coverage universe

The script reads from a hardcoded `COVERAGE` list at the top of
`build_digest.py` — 24 entries currently, mapping each ticker to its SEC CIK
where the operator is cross-listed. Pure SEDAR-only names (TOU, FM,
some others) have `cik=None` and are skipped by the EDGAR fetcher.

To add a name: add a tuple to `COVERAGE`. To find a CIK, search EDGAR:
<https://www.sec.gov/cgi-bin/browse-edgar?action=getcompany&company=cameco>

A SEDAR+ adapter is the obvious next addition; it doesn't have a clean
public API, so it'll need either a paid wrapper or a careful scrape.

### Cost

The model is `claude-haiku-4-5`. With prompt caching on the system prompt
and ~60K chars per filing trimmed, expect well under **$0.50/week** at the
current 24-name universe. Calling Sonnet/Opus would cost ~10× more — Haiku
is the right tier for high-volume extraction.

The script uses **prompt caching** on the system prompt
(`cache_control: ephemeral`) so you don't pay full price for the system
prompt on every call.

### Running on a schedule

A GitHub Actions workflow at
[`.github/workflows/build-digest.yml`](../.github/workflows/build-digest.yml)
runs the ingest every Monday at 12:00 UTC, commits the updated JSON +
HTML, and pushes back to the branch. Vercel/Netlify auto-deploys on the
push.

To enable:

1. **Add a repo secret.** Settings → Secrets and variables → Actions → New
   repository secret. Name `ANTHROPIC_API_KEY`, value `sk-ant-...`
2. The workflow already has `permissions: contents: write` so it can push
3. (Optional) Trigger it manually once: Actions tab → "Build Halvren
   Digest" → "Run workflow"

Until the secret is set, the scheduled runs won't fail — they'll just log a
warning and re-render the existing JSON, which is a no-op.

### Operator notes

- **Adding a hand-written principal note.** Open `data/digest-week.json`,
  find the item by id (e.g., `cnq-2026q1`), set its `note` field with
  `label`, `body_html`, and optional `meta` array. Run `--render`. Done.
- **Promoting a flag from "model" to "desk".** Same — edit the item's
  `flag` field to `"desk"` and add a principal note. Re-render.
- **Killing a flag the model got wrong.** Set `flag: null` and `note: null`
  in the JSON, re-render. (The next ingest may re-flag if the source
  language hasn't changed — to suppress permanently, add the item id to a
  TODO suppression list.)
- **Forcing a fresh look at a specific name.** Bump `--days` to 30 or 60
  and re-run ingest.

### Canadian-only names — IR feed adapter

SEDAR+ has no clean public API. Rather than scrape its SPA (fragile,
breaks without notice), the script falls back to whatever press-release
feed each Canadian-only operator publishes directly. Map a ticker to a
stable RSS or Atom URL via the `MANUAL_FEEDS` dict in
`build_digest.py`:

```python
MANUAL_FEEDS = {
    "TOU":    "https://www.globenewswire.com/RssFeed/orgclass/4/feedTitle/Tourmaline-Oil-Corp",
    "FM":     "https://www.first-quantum.com/_resources/news/news.xml",
    # ...
}
```

Once a feed URL is set, the same downstream pipeline (extract +
flag via Anthropic) handles it identically to an EDGAR filing — it
just enters the loop through a different door. Most Canadian
operators publish either:

- **Globe Newswire** at `https://www.globenewswire.com/RssFeed/orgclass/4/feedTitle/<slug>`
- **Newsfile** at `https://api.newsfilecorp.com/issuer/<id>/recent`
- A self-hosted RSS/Atom feed on the IR page

Check the issuer's "News &amp; events" page for the RSS icon. Leaving
the value `None` cleanly suppresses that ticker from the digest.

The parser handles both RSS 2.0 and Atom feeds.

### What's deliberately deferred

- **Earnings call transcripts.** EDGAR carries press releases and
  10-Q/10-K, not full transcripts. Adding a transcript provider
  (Seeking Alpha, Tikr, AlphaSense API) gives the model materially
  more to work with — the digest's tonal-shift detection becomes much
  sharper with a verbatim transcript than with an IR press release.
- **Insider transaction granularity.** Form 4 ingestion is live; the
  current renderer caps at 6 in the right rail. A standalone
  /insiders page with the full firehose, sortable by ticker / value /
  reporter, is the next obvious extension.
- **Email newsletter.** The "Get the digest" form on `/digest` points
  at Substack; the script doesn't push to subscribers directly.
  Substack handles delivery, the script handles content.

These are the obvious extensions; each is a few hours of work on top of
the v1 scaffolding.

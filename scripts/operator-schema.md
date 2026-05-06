# Operator schema

A covered operator is two files:

- `/data/operators/<slug>.json` — the typed data block
- `/content/operators/<slug>.md` — the principal's prose body

`scripts/build_operators.py` reads both and renders `/research/<slug>.html`
against the shared template. **Adding a new operator never requires a code
change** — only a new JSON file and a new Markdown body.

The slug is the kebab-case form of the page URL (e.g. `cameco-cco`,
`canadian-natural-cnq`). It appears in the canonical URL and the file paths.

---

## JSON shape

```jsonc
{
  "slug":       "cameco-cco",                // matches file basename
  "ticker":     "CCO",                       // primary listing
  "exchange":   "TSX / NYSE",                // human-readable listing string
  "name":       "Cameco Corporation",        // legal name (Article schema)
  "short_name": "Cameco",                    // breadcrumb / related cards
  "url":        "https://...",               // company URL (Article.about.sameAs)

  // Sector + sub-industry — both used on the page header AND for filtering
  // on /coverage in a later sprint. Allowed sector values:
  //   "Energy" | "Materials" | "Infrastructure"
  "sector":         "Energy",
  "sub_industry":   "Uranium",
  "page_eyebrow":   "On the desk · Uranium",   // section-label text above H1

  // Page H1 — kept as raw HTML so the principal's italic <em> can survive.
  // Must include a closing period, exactly as it would appear on the page.
  "headline_html":  "Cameco (CCO): A mine with a cost structure, read <em>honestly.</em>",

  // OG / meta
  "page_title":     "Cameco (CCO) — A mine with a cost structure, read honestly | Halvren Capital",
  "meta_description": "...",
  "og_title":       "Cameco (CCO) — A mine with a cost structure, read honestly",
  "og_description": "...",
  "og_image":       "/og-research-cco.png",   // root-relative, exists in repo
  "published_iso":  "2026-04-18",              // datePublished
  "modified_iso":   "2026-04-18",              // dateModified

  // The Read — the machine-style abstract printed in a muted block at the
  // top of the page. ~30 words. The principal reviews; the timestamp stamp
  // proves it.
  "the_read": {
    "summary":               "Saskatchewan uranium miner ...",
    "generated_iso":         "2026-04-18",
    "source_filing":         "Cameco FY 2025 earnings release (Feb 2026)",
    "principal_reviewed_iso":"2026-04-18"
  },

  // FY snapshot — drives the "By the numbers" data block. Order is preserved.
  // Any metric.note is rendered in muted text under the value.
  "fy_snapshot": {
    "period": "FY 2025",
    "metrics": [
      {"label": "Revenue",          "value": "C$3.48B (+11% YoY)"},
      {"label": "Adj. net earnings","value": "C$627M (vs C$292M FY24)"}
    ]
  },

  // Forward-looking guidance items, rendered as a small dl below the FY snapshot.
  // null is allowed and will simply not render the section.
  "guidance": [
    {"label": "2026 production guidance", "value": "19.5–21.5 Mlbs"}
  ],

  // Leadership block. Anything null renders as "—".
  "leadership": {
    "ceo":                 "Tim Gitzel",
    "ceo_since":           2011,
    "chair":               null,
    "succession_visible":  false,
    "note":                "Visible at executive level but not concentrated in one named successor."
  },

  // Bullet list under "What we track". Strings, no HTML.
  "what_we_track": [
    "All-in mining cost",
    "Westinghouse contribution",
    "Long-term contract book",
    "Capital discipline vs. peers"
  ],

  // Checklist scorecard. The 10 questions live in /checklist.html and are
  // numbered 1..10, matching the pillars (1-4 = Business, 5-8 = People,
  // 9-10 = Cycle). The build script reads the question text from the
  // canonical questions.json snapshot below; only `status` and `note` are
  // operator-specific.
  //
  //   status: "pass" | "not_yet" | "fail" | null
  //   note:   one-line operator-specific commentary, or null
  //
  // The principal owns these. null renders as a neutral dot + the standard
  // checklist note as a fallback, and never as a fabricated answer.
  "checklist": {
    "scoring": [
      {"q":  1, "status": null, "note": null},
      {"q":  2, "status": null, "note": null},
      {"q":  3, "status": null, "note": null},
      {"q":  4, "status": null, "note": null},
      {"q":  5, "status": null, "note": null},
      {"q":  6, "status": null, "note": null},
      {"q":  7, "status": null, "note": null},
      {"q":  8, "status": null, "note": null},
      {"q":  9, "status": null, "note": null},
      {"q": 10, "status": null, "note": null}
    ],

    // The verbatim Pillar I/II/III commentary from the principal, rendered
    // below the scorecard grid. These ARE the existing "Applying the Halvren
    // Checklist" paragraphs from the live site, lifted verbatim.
    // HTML is allowed; <em>, <strong> are common.
    "pillar_commentary": {
      "I":   "<strong>Pillar I. The business.</strong> ...",
      "II":  "<strong>Pillar II. The people.</strong> ...",
      "III": "<strong>Pillar III. The cycle.</strong> ..."
    }
  },

  // Header dates and disclosure
  "last_reviewed_iso": "2026-04-18",
  "next_earnings_iso": null,                   // null renders as "—" + no countdown

  // position_disclosure: "may_hold" | "holds" | "none"
  // Used both in the disclosure footer prose and in the JSON-LD
  // FinancialProduct.disclosure block.
  "position_disclosure": "may_hold",

  // Two related operator slugs, rendered as the two cards at the bottom of the page.
  "related_slugs": ["canadian-natural-cnq", "enbridge-enb"]
}
```

## Markdown body shape

The body file is the principal's prose between the byline and the
"Applying the Halvren Checklist" section, rendered into the "The Note"
section of the page. The first paragraph is the lead.

Supported syntax (kept deliberately small — see `scripts/build_operators.py`):

```markdown
First paragraph is the lead. Inline <em>html</em>, <strong>html</strong>,
<a href="...">html</a>, and HTML entities pass through verbatim.

Second paragraph.

## Section heading
Renders as <h2 class="doc-h2">.

### Subsection heading
Renders as <h3 class="doc-h3">.

- bullet
- bullet

> Pull quote text.
```

Everything else is treated as a paragraph (`<p class="doc-p">`).

## The 10 checklist questions

Snapshot of the canonical question text. Source: `/checklist.html`.
The build script imports `scripts/checklist_questions.json`, which is
generated from the same source so both stay in sync.

| # | Pillar | Question (short) |
|---|--------|------------------|
| 1 | I. The business | FCF through the full cycle |
| 2 | I. The business | Unit economics at worst price |
| 3 | I. The business | Balance sheet at trough |
| 4 | I. The business | ROIC on incremental capital |
| 5 | II. The people  | Bought-not-granted insider ownership |
| 6 | II. The people  | Behaviour in 2015 and 2020 |
| 7 | II. The people  | Comp tied to per-share value |
| 8 | II. The people  | Succession visible |
| 9 | III. The cycle  | Cost curve that matters |
|10 | III. The cycle  | Normal-decade pricing |

## How to add a new operator

1. Pick a slug, e.g. `imperial-oil-imo`.
2. Copy `data/operators/cameco-cco.json` to `data/operators/imperial-oil-imo.json`
   and fill in. Leave any unknown field as `null`.
3. Copy `content/operators/cameco-cco.md` to `content/operators/imperial-oil-imo.md`
   and write the body.
4. Run `python3 scripts/build_operators.py`.
5. The script writes `research/imperial-oil-imo.html` and exits 0.
   It exits non-zero if a required field is missing.
6. The new operator does **not** appear on the homepage watchlist or in
   the related cards of other operators automatically — those still
   reference `related_slugs` lists explicitly.

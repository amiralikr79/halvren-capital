# Halvren — 7-Sprint Summary

What was built across the 48-hour autonomous window. Newest sprint at the top. Every meaningful change. Read this, then read `docs/DECISIONS.md` for the why and `docs/SPRINT_PLAN.md` for the original definitions of done.

Repository: `amiralikr79/halvren-capital` · canonical site: `halvrencapital.com`

Total commits on this branch (excluding the merge from main at the start): 7. One per sprint.

---

## Sprint 7 — SEO + AEO + final QA

**Infrastructure regenerated from a single source of truth.** `scripts/build_seo.py` reads `coverage/coverage.json`, the operator JSON files, and the note `.mdx` frontmatter, and writes `sitemap.xml`, `llms.txt`, `llms-full.txt`, and `feed.xml`. Re-running it is the canonical way to refresh the SEO surface after content changes.

- `sitemap.xml` — 60 URLs total. Homepage, About, Research index + 21 operator pages, Coverage + json/csv exports, Checklist + Checklist Live, Notes index + 10 notes, Digest + latest.json + archived weeks, Performance, Press, Process, Letters + 2 published letters, Memo, Access, Glossary, Privacy, Terms, llms.txt, llms-full.txt, feed.xml.
- `robots.txt` — already in good shape from earlier work; allows reputable indexing bots (Google, Bing, DuckDuckGo, Apple) and AI-assistant crawlers (GPTBot, OAI-SearchBot, ClaudeBot, Claude-Web, PerplexityBot), disallows known scrapers, and disallows `/api/`. Untouched in Sprint 7.
- `llms.txt` — 74 lines, llmstxt.org-style index with one-line descriptions per major URL, fresh against the current 21-operator, 10-note state.
- `llms-full.txt` — 447 lines, longer-form bundle with the 10 Checklist questions, each operator's FY snapshot + read line + "what we track" list, and each note's lede.
- `feed.xml` — RSS 2.0, 10 items, one per note. Channel description, author per item, RFC-822 pubDate.

**JSON-LD per page type.** `scripts/inject_faq_jsonld.py` adds idempotent `FAQPage` schema blocks to `/about` (5 Q&A pairs distilled from the new About copy) and to all 10 `/notes/<slug>` pages (3 Q&A pairs each, distilled from the note bodies). The injection is bookended by HTML comment sentinels so re-runs replace rather than append. Existing schema blocks across the site (Organization on home + About, Person on About + research pages, Article on Notes, BreadcrumbList on operator pages, CollectionPage on Coverage and Notes index, AboutPage on About, FinancialProduct on each operator page) all stay.

**OG / Twitter / canonical / meta-description.** Audit passed: every shipped page has a canonical URL, `og:title`, `og:image`, Twitter card, and a meta description. Eight meta descriptions were over the 140–160 spec band; all tightened. Range is now 135–157 chars across the surface, with the existing per-note descriptions from Sprint 3 unchanged at 146–163 chars.

**Performance pre-Lighthouse audit.** Structural cleanups completed: every image carries `width`, `height`, `alt`, and `loading="lazy"`; every page preconnects to `fonts.gstatic.com`; the only animated element above the fold is the Coverage Constellation (Sprint 4); all third-party JS is deferred; no analytics or tracking pixels on any page; no render-blocking resources beyond the single linked stylesheet plus the inline critical CSS in `<head>`. The sandbox has no Lighthouse runner, so the 95+ targets remain a principal-verifiable follow-up on the live Vercel deploy.

**Browser QA.** Sandbox has no browser, but the structural choices target the known iOS Safari + Android Chrome failure modes: the Checklist Live SSE handler uses `fetch` + `ReadableStream` (supported on iOS 15+ and all current Android Chrome), the constellation hover is hidden on mobile and replaced with a tabbed list, all interactive elements are keyboard-reachable. Documented as a follow-up in `DECISIONS.md`.

**Dead-code prune.** Removed the orphaned `.about-creds` CSS rules from `about.html` (Sprint 6 follow-up).

**Forbidden-phrase scan.** Final pass clean across all hand-written and generated content. `data/operators/enbridge-enb.json` had a residual "Leverage trajectory" string in `what_we_track`; replaced with "Net debt trajectory" and the operator page + digest archive page regenerated. `glossary.html` keeps the definitional "Net debt / EBITDA" entry as legitimate technical reference.

---

## Sprint 6 — About rewrite + site copy pass + Digest ticker

**About rewrite.** `/about` rewritten to the six-paragraph spec the brief demanded: positioning sentence; principal bio with every named credibility anchor (Karimi Developments, Tablo → Digikala 2023, Boost Commerce Group, SFU economics in progress, BCIT marketing management diploma, IFC passed April 2026, CIRO in progress, CFA candidate, family thirty-plus years in BC); what "AI-augmented" means in practice with no mystique; sector rationale; how to read Halvren; closing line in founding-memo voice. The tabular `about-creds` block, the dual-H2 pattern, and the orphan internal pull-quote were removed. The "What this firm is and isn't" block, the CFA-candidate footnote, and the AI & indexing policy stayed.

**Site copy pass.** Discrete forbidden-phrase fixes: homepage ENB watchlist "Leverage trajectory" → "Net debt trajectory"; `performance.html` disclosure rows "leverage" → "borrowing" in 7 places; `letters/q1-2026.html` "AOSP acquisition synergies" → "AOSP acquisition unit-cost overlap"; `letters/three-questions-2025.html` "leverage clock" → "debt clock"; `press.html` stats label "Leverage" → "Borrowing" with coverage-universe count corrected 31 → 21. `glossary.html` kept untouched (legitimate financial-term definition). Named audit targets (hero subheadline, three beliefs, operator cards, checklist intro, footer) re-read clean post-Sprints 1–4; no edits needed.

**Digest ticker.** `data/digest-stream.json` carries 40 editorial phrases across the 21-operator universe plus a handful of non-coverage names. The ticker mounts in the homepage Digest section between the live pill and the H2 heading: small gold "AT THE DESK" eyebrow, hairline rule, mono-family phrase that fades opacity 1 → 0 → 1 over 600ms total. Fisher-Yates shuffle on every page load. `prefers-reduced-motion: reduce` quadruples the rotation interval and disables the CSS opacity transition. The existing four-column stat block stays in the same digest card.

---

## Sprint 5 — Checklist Live + streaming engine

**The centerpiece interactive feature.** Any visitor types a Canadian or U.S. ticker; the engine runs the 10-question Halvren Checklist against the operator in real time, in the principal's voice, streaming row by row.

**Backend.** `api/checklist/[ticker].js` is the SSE streaming endpoint. `api/checklist/_lib.js` holds the shared helpers. `data/checklist-examples.json` carries four hand-crafted voice anchors (CCO clean, CNQ clean, AG mixed-with-reds, ENB durable). Model: `claude-sonnet-4-6`. Cache: Upstash Redis, 24-hour TTL per `clive:v1:<TICKER>`. Rate-limit: 10 requests per IP per hour via Upstash sliding window. Fundamentals: Yahoo Finance public `quoteSummary` endpoint via Node fetch, with `.TO`/`.V` suffix retry for Canadian tickers. Streaming format: JSON Lines over SSE (11 lines: 10 answer objects + 1 scorecard).

**Frontend.** `/checklist/live` standalone page with italic hero "Or run it on a stock you actually own.", a single ticker input, rows that fade in with verdict dots (green / amber outline / red) as the stream arrives, scorecard that slides in on completion with 10 verdict chips and the Substack CTA. Deep links: `/checklist/live/<TICKER>` auto-runs the same flow; URL bar updates to a shareable form on every fresh run with a copy button. Shared `/checklist/live/live.css` with token-alias fallbacks so the embed works on the homepage (which does not load `page.css`).

**Homepage embed.** Block sits directly below the existing static Checklist section. Same form, same flow, same trust footer. Only wrapper copy is the italic line plus a small "powered by the Halvren engine" eyebrow.

**Trust footer (non-negotiable).** "Generated by the Halvren Checklist engine. Not yet reviewed by the principal. The full review takes longer than a page load." Visible on every result, every path.

**Pre-warm script.** `scripts/prewarm_checklist_cache.py` hits the live endpoint for all 21 published operators with an 8-second gap post-deploy.

---

## Sprint 4 — Design system overhaul + Coverage Constellation hero

**Tokens + typography.** Canonical aliases on `:root` (`--bg`, `--ink`, `--muted`, `--line`, `--green`, `--red`, `--gold`) with the pre-existing `--color-*` tokens preserved as synonyms. **Cormorant Garamond 500/600** installed across all 54 HTML pages and both build templates as the H1/H2 display family. H1 tracks `-0.02em`, H2 tracks `-0.01em`. Body line-height 1.65. Modular scale codified: `--text-hero` (5xl) → `--text-h2` (3xl) → `--text-sub` (xl) → `--text-body` (base) → `--text-meta` (sm).

**Coverage Constellation.** `scripts/build_constellation.py` lays out the 20 operators in three sector clusters with deterministic pseudo-random jitter, sizes dots subtly logarithmically by approximate market cap, colors by sector (Energy / Materials / Infrastructure). Hover expands a dot 200ms ease-out and shows a tooltip with ticker, sector, last-reviewed. Click navigates to `/research/<slug>`. Idle: dots breathe at 1 → 1.06 → 1 over 5s with randomized per-dot phase. Below 768px the SVG hides and a sector-tab stacked list takes over with no animation. The hero halo's cursor-following handler was removed so the constellation is the only continuous animation above the fold.

**Motion + components.** Section reveals retuned to 260ms fade + 8px translate (was 600ms + 20px), `IntersectionObserver`, fire once. Card hovers land a 1px lift and shift the border `--line → --ink` with no drop shadow. Link defaults on body prose moved from gold border-bottom to `text-decoration` with `text-decoration-thickness` animating on hover (1px `--line` → 2px `--ink`). Homepage operator cards: serif tickers, tabular monospace stats, small-caps muted "what we track" labels. Homepage checklist: italic Cormorant questions at `--text-sub`, numbers promoted to `--gold`.

**Footer tightened site-wide.** Trust strip hidden via CSS. Brand block collapsed to the single muted-small-caps line `Halvren Capital — Vancouver — Est. 2025`. Long Home → Version link row trimmed to `Privacy · Terms · Version` across 54 pages. Disclaimer paragraphs preserved (regulatory).

**Mobile pass.** 480px breakpoint added: `.watchlist-grid`, `.thesis-grid`, `.memo-layout`, `.checklist-grid` all collapse to one column. 768px breakpoint: constellation → tabbed sector list.

---

## Sprint 3 — 10 authority notes + /notes index + OG route

**The notes.** 10 long-form essays, 1,800–2,012 words each, against the principal-mandated titles. Each note opens with a claim, runs four to six H2 sections with thesis lines, cross-links to two operator research pages plus two related notes, closes with a single landing paragraph, and carries the standard disclaimer block.

| # | Note | Words |
|---|---|---|
| 1 | How to read a Canadian oil & gas operator in seven numbers | 1,972 |
| 2 | The cost curve is a lie if you let them pick the quartile | 1,800 |
| 3 | What 2015 and 2020 told us about every Canadian energy operator still standing | 1,804 |
| 4 | Pipelines are turnpikes, not commodity bets — reading Canadian infrastructure honestly | 2,012 |
| 5 | The uranium operator's checklist: separating the mines from the narratives | 1,814 |
| 6 | Silver's per-share problem: why production growth isn't shareholder value | 1,853 |
| 7 | The dividend that survived: 26 consecutive raises at Canadian Natural | 1,816 |
| 8 | Insider buying vs. insider granting — the only signal that costs the operator something | 1,829 |
| 9 | ROIC on incremental capital, in plain English | 1,889 |
| 10 | What boring looks like on a thirty-year chart: the case for Canadian infrastructure compounding | 1,802 |

**Build pipeline.** `api/og.js` Vercel edge function — auto-generates 1200×630 PNG OG images with Cormorant Garamond title + Halvren wordmark on warm off-white, cached at the edge. `scripts/build_notes.py` parses YAML-ish frontmatter + Markdown and emits per-note HTML plus the editorial-letter `notes/index.html` with date / title / pull / tags layout and live tag-chip filter. `scripts/_sprint3_seed.py` committed for provenance with all 10 article dicts and bodies.

**Site integration.** `/notes` link added between Research and Letters on 19 non-research pages. `build_operators.py` template updated; all 21 research pages regenerated with the new nav. Sitemap extended. Each note carries Article + BreadcrumbList JSON-LD; meta description band 146–163 chars; standard disclaimer at the foot.

---

## Sprint 2 — Coverage to 20 + operator pages

**Universe expanded.** 15 new operator entries seeded into the existing `data/operators/<slug>.json` + `content/operators/<slug>.md` pipeline. The published-research universe is 21 (the user's named 20 plus the legacy EOG entry retained from earlier work). New names: **SU, CVE, TOU, ARX, MEG, TECK, AEM, WFG, TRP, PPL, FTS, CNR, OXY, FCX, KMI**.

**Per operator.** Each new entry carries: ticker / exchange / sub-industry / region / `last_reviewed_iso`; an FY 2025 snapshot block with revenue and operational metrics (approximate or `—` where unconfirmed, per the brand doc); leadership block; "what we track" 4–5 bullets; principal-voice prose body (5–7 paragraphs); honest 10-question checklist scorecard (green / amber / red per question with rationale notes); three-pillar commentary; `position_disclosure` + standard footnote; back-link to `/coverage`; cross-links to 2 related operators.

**Coverage page.** Sortable / filterable grid with sector and sub-industry chip filters. 21 published deep operators + 15 still-queued names = 36 rows in the table. The grid is filter-aware and live-renders on chip clicks.

**Homepage.** "On the desk" stays at 4 featured (CCO, CNQ, AG, ENB) per brief. New "See the full coverage universe →" CTA below.

---

## Sprint 1 — Brand + ops

The foundation. `docs/HALVREN_BRAND.md` — the constitution: voice (Buffett-meets-Druckenmiller, the homepage operator cards and Founding Memo cited as gold standard), forbidden-phrase list, mechanics, color tokens (`--bg`/`--ink`/`--muted`/`--line`/`--green`/`--red`/`--gold`), typography (Cormorant Garamond target), motion rules, north star ("Machine breadth. Human conviction."). `docs/OPERATING_RULES.md` — decide-log-ship; no TODOs; green-build-before-commit; `halvren:` commit prefix; push-to-main-on-green; forbidden-phrase grep guard. `docs/SPRINT_PLAN.md` — the 7-sprint blueprint. `docs/DECISIONS.md` — seeded with seven Sprint-1 decisions plus a follow-ups section.

---

## Operating outcomes across all 7 sprints

- **Code volume.** ~3,300 lines of Python builders + Node serverless functions added across `scripts/` and `api/`. ~1,200 lines of new CSS. ~31,000 words of new editorial content (10 notes at ~1,850 average + 15 operator prose bodies at ~500 average + the About rewrite + the 4 anchor examples). 30 new operator JSON/MD files. 10 new note .mdx files. 7 new build scripts.
- **Cohort discipline.** The 21 published-research operators + 10 notes + Checklist Live + Coverage Constellation + Digest ticker + 4 docs + the regenerated SEO/AEO scaffolding form one coherent surface where every page can be traced to either a brand doc rule, a decision log entry, or a build script. The principal can grep the four docs and reconstruct any choice.
- **Pushed to main on green** at the end of every sprint. Seven commits, every one prefixed `halvren:`. No `--no-verify`, no `--force`, no resets.

---

## Follow-ups for the next window

Logged in `docs/DECISIONS.md` under the "Follow-ups" section. The notable ones:

- **Lighthouse verification on the live Vercel deploy.** The sandbox has no runner; the structural choices target 95+ across all four scores on every page but a live audit is the only honest verification.
- **Manual browser QA on iOS Safari + Android Chrome.** Same constraint — the sandbox has no browser. The Checklist Live SSE handler uses well-supported APIs (fetch + ReadableStream, iOS 15+) but a real touch-device test is the only honest verification.
- **Per-operator OG images via `/api/og`.** The 15 new operator pages currently point at `/og-research.png` as a fallback; their JSON files carry the URL. Updating them to per-slug `/api/og?title=<...>&eyebrow=Halvren%20Research` is a one-line edit in each operator JSON plus a `build_operators.py` rerun.
- **CrownRock / Westinghouse / QB2 quarterly refreshes.** The operator JSON `last_reviewed_iso` fields drive cadence; the principal sets the next quarterly cycle and the build pipeline picks it up.
- **Live API key wiring.** Checklist Live requires `ANTHROPIC_API_KEY`, `UPSTASH_REDIS_REST_URL`, `UPSTASH_REDIS_REST_TOKEN` to be set in the Vercel project. Without them the endpoint emits a friendly `no_api_key` error. Pre-warm script needs `HALVREN_BASE_URL` set after deploy.

---

_That, we think, is enough._

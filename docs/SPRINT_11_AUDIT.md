# Sprint 11 — Phase A Audit

Generated 2026-05-15 against the live `main` branch (commit `c68c968`).

This audit walks the deployed surface and maps it against what Sprints 9 and 10 promised. **Source of truth for Sprint 9 / 10 specs:** the corresponding sections of `docs/SHIPPED.md`, since `docs/SPRINT_PLAN.md` only documents Sprints 1–7.

The brief asked to verify "⌘K command palette, earnings tape, status bar." None of these exist in the codebase. They were on commit `e67a153` ("dark mode + type system + command palette + trading card + earnings tape"), which was reverted in `ac649e6` long before Sprint 8 began. They are not part of any committed sprint definition. Audit lists them as **out-of-scope (reverted)** and does not flag them as broken.

## Sprint 9 — five core data visualizations

| # | SPEC'D (per SHIPPED.md Sprint 9) | ACTUAL | Status |
|---|---|---|---|
| 1 | Cycle Map at `/cycle-map` + homepage hero, mounted via `data-viz="cycle-map"` | `cycle-map/index.html` exists with `data-viz="cycle-map"`; homepage `index.html` line 603 mounts the same widget above the constellation | shipped |
| 2 | Watchlist Spread at `/coverage` above the legacy table, sortable, mobile card view | `coverage/index.html` mounts both `data-viz="watchlist-spread"` and `data-viz="dividend-ladder"` (2 hits via grep) | shipped |
| 3 | Dividend Ladder at `/coverage` above the spread | Mounted in `coverage/index.html` via `data-viz="dividend-ladder"` | shipped |
| 4 | Trough Test sparkline on every `/research/<slug>` page | `data-viz="trough-test"` present on every operator page (verified on `canadian-natural-cnq.html`) | shipped |
| 5 | Cost Curves at `/cost-curves`, tabbed by commodity | `cost-curves/index.html` exists with three `data-viz="cost-curve"` mounts (uranium, wcs_heavy, silver) | shipped |
| 6 | Build pipeline `scripts/build_viz_data.py` → `data/viz-data.json` (20 operators) | Present, regenerates 20 operators with all derived fields including `halvren_read` (Sprint 10 addition) | shipped |
| 7 | Sitemap entries for `/cycle-map` and `/cost-curves` | Both in `sitemap.xml` | shipped |

## Sprint 10 — conversion layer

| # | SPEC'D (per SHIPPED.md Sprint 10) | ACTUAL | Status |
|---|---|---|---|
| 1 | Halvren Read 0–100 computed from checklist verdicts on every operator | `halvren_read` field on all 20 operator JSONs; range AEM 100 → AG 36 | shipped |
| 2 | Halvren Read on operator hero strip | Renders via `op-header-read` block on every `/research/<slug>` page | shipped (visual bug — see Phase B #2) |
| 3 | Halvren Read on homepage operator cards | `watch-read` blocks on the 4 watch cards (CCO 80, CNQ 96, AG 36, ENB 86) | shipped (same visual bug — see Phase B #2) |
| 4 | Halvren Read in Watchlist Spread (sortable column) | New "Halvren Read" column in `viz.js` sortable table with band-coloured cells | shipped |
| 5 | Halvren Read in Cycle Map tooltip | `viz.js` `showTip` adds the "Halvren Read: NN / 100" line | shipped |
| 6 | `/methodology` page with formula + disclaimer | `methodology.html` exists with the three pillars, formula block, and "not a rating" disclaimer | shipped |
| 7 | `/compare` engine, 2 or 3 operators, autocomplete pickers | `compare/index.html` + `compare/compare.js`; Vercel rewrite `/compare/:tickers` | shipped |
| 8 | `/api/og/compare/[tickers]` for compare share images | `api/og/compare/[tickers].js` | shipped (untestable in sandbox; code parses) |
| 9 | Glossary at `/glossary` with 50+ terms | `glossary.html` regenerated from `data/glossary.json` (52 terms) | shipped |
| 10 | Inline glossary popovers on research + note pages | `glossary.js` runtime DOM-walker, mounted on every research and note page via build templates | shipped |
| 11 | `/diary` Cycle Diary index | `diary/index.html` with 25 entries and chip filters | shipped |
| 12 | `/diary/[id]` per-entry pages | 25 per-entry HTML files in `diary/` | shipped |
| 13 | `/diary/feed.xml` RSS 2.0 | Present, 25 items | shipped |
| 14 | `/api/og/diary/[id]` per-entry OG images | `api/og/diary/[id].js` | shipped (untestable in sandbox; code parses) |
| 15 | Homepage "Latest from the desk" component, 3 newest entries | `desk-latest` aside on `index.html` line 910 | **broken** — defaults to "Loading the diary…" and only hydrates after a successful client-side fetch. See Phase B #1. |
| 16 | `/start` onboarding page, 5 steps, linked from hero + nav | `start/index.html` exists; "Start here →" link in homepage hero; nav item added | shipped |
| 17 | `/api/og/operator/[ticker]` Trading Card PNG | `api/og/operator/[ticker].js`; "Save the card" block on every `/research/<slug>` | shipped (untestable in sandbox; code parses) |
| 18 | Sitemap, llms.txt, llms-full.txt updated for all new routes | All four files include `/methodology`, `/compare`, `/diary`, `/start`, `/glossary` | shipped |

## Out-of-scope items mentioned in Phase A brief

| Item | Status | Note |
|---|---|---|
| Dark mode toggle | **shipped** | `data-theme` attribute on `<html>`, `theme-toggle` button in nav; localStorage `halvren-theme` key. Tokens defined for both themes in `index.html` `:root` and `[data-theme="dark"]` blocks. |
| ⌘K command palette | **out-of-scope (reverted)** | Belongs to commit `e67a153`, reverted in `ac649e6`. Not part of any active sprint. |
| Earnings tape | **out-of-scope (reverted)** | Same. |
| Status bar | **out-of-scope (reverted)** | Same. |
| `/data/operators.ts`, `/data/performance.ts` | **out-of-scope** | This site is static HTML + JSON; there are no `.ts` files. The brief's references are a mental model from a different stack. Operator data lives in `data/operators/<slug>.json`; performance data lives in `performance.html` only (no separate JSON yet). |

## Bugs / partial work flagged for Phase B

1. **Diary widget on homepage stuck on "Loading the diary…"** — the SSR HTML defaults to the loading message; only the client-side fetch can replace it. Any failure (network, CORS, slow CDN, JS disabled) leaves the loading text visible permanently. **Fix:** server-render the three newest entries at build time; let JS re-render later for fresh data.

2. **Halvren Read renders as concatenated text in non-CSS contexts.** Both `op-header-read` (operator hero) and `watch-read` (homepage cards) use `display:inline-flex` with two child `<span>` elements that have no whitespace between them. With CSS applied this stacks vertically as intended. With CSS disabled, in screen-reader plain-text mode, or in any text-content extraction, the spans concatenate to "96Halvren Read · 96 / 100" / "80Halvren Read". **Fix:** switch to block-level flex, add explicit gap, ensure label is visible separately, and harden the markup so the text content reads cleanly even without CSS.

3. **Hero stat strip renders without numeric content before JS animates.** The `.big-num` spans are initialised with only `<span class="big-num-suffix">+</span>` or `%` — the count animates from 0 only on viewport entry. Pre-JS, server-rendered, or no-JS users see "+ Operators in the working universe" and "% Annualized return since 2019" with no number. **Fix:** bake the target number into the static text content; let JS reset to 0 and animate from there only when JS is available.

4. **Constellation cluster labels concatenate when extracted as text.** The three SVG `<text>` elements at the top of the constellation are positioned at fixed x coordinates (visually correct) but read as `ENERGYMATERIALSINFRASTRUCTURE` when scraped as text content (LLMs, screen readers, page-text extractors). **Fix:** add a semantic HTML structure above the SVG that lists the three sectors as discrete elements with whitespace, while keeping the SVG labels for visual rendering.

## Routes verified

| Route | Resolves | Notes |
|---|---|---|
| `/cycle-map` | ✓ | `cycle-map/index.html`, mounts cycle map viz |
| `/cost-curves` | ✓ | `cost-curves/index.html`, three commodity tabs |
| `/coverage` | ✓ | `coverage/index.html` with Watchlist Spread + Dividend Ladder |
| `/compare` | ✓ | `compare/index.html`; `/compare/CNQ-vs-ENB` resolves via Vercel rewrite |
| `/glossary` | ✓ | `glossary.html`, 52 terms, A-Z layout, type-ahead filter |
| `/diary` | ✓ | `diary/index.html`, 25 entries, chip filters |
| `/diary/[id]` | ✓ | 25 HTML files in `diary/` |
| `/start` | ✓ | `start/index.html`, 5 numbered steps |
| `/methodology` | ✓ | `methodology.html`, formula + disclaimer |
| `/research/canadian-natural-cnq` | ✓ | Halvren Read 96 (green) renders in hero |
| `/research/first-majestic-ag` | ✓ | Halvren Read 36 (red) renders in hero |
| `/research/enbridge-enb` | ✓ | Halvren Read 86 (green) renders in hero |

## Halvren Read computed on every operator

20/20 operators carry `halvren_read` in their JSON. Distribution:

```
AEM 100  ARX 96   CNQ 96   FTS 96   TOU 96
CNR 91   KMI 91   NTR 91   PPL 91   WFG 88
ENB 86   CVE 84   TRP 82   CCO 80   SU 76
FCX 71   OXY 70   TECK 70  MEG 68   AG 36
```

## OG endpoints

Untestable in this sandbox (no Vercel runtime, no edge function execution). Code-level checks:

- `api/og/operator/[ticker].js` — parses, fetches `/data/viz-data.json` to map ticker → slug, then `/data/operators/<slug>.json`, computes Halvren Read from scoring as a fallback, renders 1200×630 PNG.
- `api/og/compare/[tickers].js` — parses, splits on `-`, requires ≥ 2 valid tickers, renders side-by-side columns with Halvren Read per operator.
- `api/og/diary/[id].js` — parses, fetches `/data/diary.json`, finds entry by ID, renders date + ticker + action chip + summary.

Each function uses `@vercel/og` (already in `package.json`), `runtime: "edge"`, and a 24-hour cache header. Live verification requires hitting the deployed URLs.

## Phase B priority order

1. Diary widget pre-build (highest impact: visible on every homepage view)
2. Halvren Read display markup
3. Stat strip numeric content
4. Constellation sector labels semantic HTML

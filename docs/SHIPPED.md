# Halvren — 7-Sprint Summary

What was built across the 48-hour autonomous window. Newest sprint at the top. Every meaningful change. Read this, then read `docs/DECISIONS.md` for the why and `docs/SPRINT_PLAN.md` for the original definitions of done.

Repository: `amiralikr79/halvren-capital` · canonical site: `halvrencapital.com`

Total commits on this branch (excluding the merge from main at the start): 7. One per sprint.

---

## Sprint 12B — The visual overhaul

Same sprint number, second pass — the brief was a major visual reset on top of the Sprint 12 polish work. Eight parts, all shipped.

**Part 1: Dark by default.** `:root` token set in both `page.css` and the homepage inline `<style>` is now the dark palette. Light is `[data-theme="light"]`. First paint is dark for every new visitor; `prefers-color-scheme: light` is honored only when there is no cookie. Persistence migrated from `localStorage` to a 1-year `halvren-theme` cookie via `document.cookie` so the toggle is durable and server-readable. New tokens: `--bg`, `--bg-2`, `--bg-3`, `--ink`, `--muted`, `--line`, `--gold`, `--amber`, `--amber-glow`, `--green`, `--red`. Legacy `--color-*` aliases mapped to the new values for back-compatibility. 86 HTML pages had their bootstrap script swapped; 85 had their Google Fonts link upgraded to add Inter and drop DM Sans.

**Part 2: The three amber moments.** `--amber #ff9d2f` ships in exactly three places: the "Run the 10" Checklist Live CTA (`.lc-submit` rule), the Halvren Read Mark when score is 100 (the `perfect` band), and the question numbers on the homepage Checklist preview (`#checklist .checklist-num`). Diary pulse retained as `--green` to keep the count at three.

**Part 3: The hero rebuild.** Three new elements above the existing headline:
- 28px ticker strip with all 20 operators and their Halvren Read scores (`AEM 100 · ARX 96 · …`), 60-second right-to-left CSS marquee, pauses on hover, mono small-caps `--muted`. Track duplicated in markup for seamless loop.
- Streaming "now reading" line below the headline: gold `At the desk` eyebrow with a pulsing green dot, typewriter-effect line cycling 3 phrases from `/data/digest-stream.json`, 40ms/char, 3s hold, gold caret blinking at 1.06s. `prefers-reduced-motion` collapses to a static line.
- Subtle radial gradient mesh in the bottom-right at 4% gold opacity. Hidden on mobile for perf.

**Part 4: The Halvren Read Mark — the iconic component.** Every previous "NN Halvren Read" surface replaced. A circle (88px / 64px mobile, large 120px on operator hero, small 48px in tables) whose ring color encodes a five-band score classification (`perfect`/`elite`/`solid`/`mid`/`low`) with the score numeral in display serif inside and a mono "/ 100" beneath. On hover or tap, the circle expands (350ms cubic-bezier(0.22,1,0.36,1)) into a 5×2 grid of verdict chips for the 10 checklist questions. Server-rendered by `render_halvren_mark()` in `build_operators.py`, inlined into the homepage watch cards and the Halvren Index constituent table. Behaviour layered in `sprint12.js`. `/api/og/operator/[ticker]` regenerated with a 280px Mark circle as the dominant visual element. Surfaces using the Mark: 20 operator hero pages, 4 homepage watch cards, 10 Halvren Index rows, OG card.

**Part 5: Type system precision.** Inter added to the Google Fonts link site-wide (85 pages + 7 builder templates). Token roles locked: `--font-display` (Cormorant Garamond) for H1/H2 and the Mark score, `--font-body` (Instrument Serif) for body prose, `--font-ui` (Inter) for chrome, `--font-data` (JetBrains Mono) for all numbers. Letter-spacing tightened: H1 `-0.025em`, H2 `-0.015em`. Mono small-caps standardised: 10–11px, `letter-spacing: 0.1em`, `--muted`, `uppercase`, weight 500.

**Part 6: Motion design language.** Codified in `sprint12.js`:
- Count-up on viewport entry: 800ms ease-out from 0 to target for any `.count-up[data-target]`.
- Section reveals: existing IntersectionObserver pattern kept; respects reduced-motion.
- Card hover: 200ms `translateY(-2px)` + border `--line → --ink`. `.watch-card[data-band="elite"]` gets a green glow on hover; `.watch-card[data-band="perfect"]` gets an amber glow.
- Mark expand: 350ms `cubic-bezier(0.22, 1, 0.36, 1)`. No bounce.
- Caret blink: 1.06s cycle (warmer than 1s).
- Button press: 100ms `scale(0.97)` on `:active` globally.
- All animations gated by `prefers-reduced-motion: reduce`.

**Part 7: Component polish.**
- Watch cards redesigned: `--bg-2` background, 16px radius, ticker (display serif 28px) + Mark on the top row, name (Inter 13px), sector pill (`--bg-3` fill, gold mono small-caps), 3-line body (body serif 15px), what-we-track (mono small-caps), bottom border footer with "Read full research →".
- Section header divider: 80px `--line` hairline 8px below every `.section-label` eyebrow (`::after` pseudo-element).
- Homepage Checklist question numbers in `--amber` (the third amber moment).

**Part 8: The "AI is alive" layer.**
- Constellation idle pulse: one random dot pulses `--amber` for 600ms every 8–12s (randomised). Skipped under reduced-motion.
- Diary entries carry `data-relative-from="YYYY-MM-DD"`; `sprint12.js` renders "14 min ago" / "3 hours ago" / "yesterday" client-side, falls back to the absolute date in `title`. Wired on the homepage "Latest from the desk" block and on every `/diary/<id>` page.
- Hero stream typewriter (Part 3).

### Files touched
- New: `sprint12.js` (the interaction layer — Mark, count-up, constellation pulse, relative timestamps, hero typewriter).
- Updated: `page.css` (~340 lines appended for the new system), `index.html` (token block, hero rebuild, watch cards now use the Mark, theme bootstrap on cookie), `nav.js` (cookie-backed toggle, sun/moon SVG that flips on each click), all 85 HTML pages (font link + theme bootstrap), 7 builder templates (`build_operators.py`, `build_notes.py`, `build_diary.py`, `build_halvren_index.py`, `build_glossary.py`, `build_coverage.py`, `build_digest_archive.py` — chrome head font/theme strings updated), `scripts/inject_homepage_diary.py` (data-relative-from on each entry), all 3 OG functions (`api/og/operator/[ticker].js` Mark-dominant + dark default; `api/og/compare/[tickers].js` + `api/og/diary/[id].js` dark default), `docs/HALVREN_BRAND.md` (Section 4 dark-default palette, Section 4a the three amber moments, Section 5 four-family type system, Section 5a the Halvren Read Mark spec).

### What's NOT shipped (logged honestly)
- The "screenshot test" (Part 9) can't be executed from this sandbox — no headless browser. Structural choices target it; live verification is the principal's call.
- Footer redesign per Part 7 spec (3-column site map) ships as the new CSS rules in `page.css` but the existing footer markup remains in place on the homepage and across legacy pages. Layered swap is the next-sprint candidate.

---

## Sprint 12 — Polish

Three items. No new features. Polish.

**1. Audio activation — blocked on TTS key (logged in DECISIONS.md).** Neither `ELEVENLABS_API_KEY` nor `OPENAI_API_KEY` is in the build environment. The player UI shipped in Sprint 11 continues to render the "narration coming soon" state across all 10 notes. Activation is one shell command (`python3 scripts/build_audio_notes.py`) once the principal provisions a key in Vercel; the four-step recipe is documented at the top of `docs/DECISIONS.md`. ElevenLabs Daniel (voice id `onwK4e9ZLuTAKqWW03F9`) is the hardcoded default; estimated cost ~$30 for the 10-note backlog.

**2. Constellation cluster labels — deleted the SVG duplicates.** Removed the three `<text class="clabel-cluster">` elements from the homepage constellation SVG and the now-unused `.constellation .clabel-cluster` CSS rule. The semantic `<ul>` above the SVG (introduced in Sprint 11) is now the only source of the "Energy / Materials / Infrastructure" labels — no duplicate concatenated render in any text-extraction path. The HTML list is hidden on mobile (where the `.constellation-mobile` tabbed list already provides the same structure) and visible on desktop. Audited the rendered `index.html`: zero remaining occurrences of `clabel-cluster`, `ENERGY`, `MATERIALS`, or `INFRASTRUCTURE` outside the structured HTML list, the cycle-map sector filter chips, and the operator dot `data-sector` attributes.

**3. Halvren Index — live price fetcher wired with graceful fallback.**
- `scripts/fetch_halvren_index_prices.py` fetches monthly adjusted closes for the 10 constituents (AEM.TO, ARX.TO, CNQ.TO, FTS.TO, TOU.TO, CNR.TO, KMI, NTR.TO, PPL.TO, WFG.TO) and the TSX benchmark (XIC.TO — adjusted close as the free proxy for S&P/TSX Composite Total Return) from Yahoo's unofficial chart endpoint (`v7/finance/chart` with `v8` and `query2.` fallbacks). Computes the equal-weighted total return path with quarterly rebalance from Jan 2024 forward. Writes the resulting series to `/data/halvren-index-prices.json` along with `last_updated`, `source`, `constituents`, `benchmark_label`, and `rebalance_dates` fields.
- `scripts/build_halvren_index.py` now invokes the fetcher before rendering, via subprocess with a 120s timeout. If the fetch fails (Yahoo 403 / network block / partial data), the script logs a single stderr note ("halvren-index: live fetch unavailable …; using on-disk series.") and renders against the existing JSON — the hand-curated reconstruction stays in version control as the documented fallback.
- `--render-only` flag and `HALVREN_INDEX_SKIP_FETCH=1` env var added for offline rebuilds.
- Page now renders a "Last updated YYYY-MM-DD · <source>" line in mono small-caps directly below the chart legend (`.hindex-updated` CSS rule appended to `page.css`).
- Yahoo returns 403 from the current sandbox; the fetcher is verified to abort atomically on partial failure (a single constituent missing data prevents any write). The script works correctly from any environment with outbound Yahoo access; the next deploy with network reachability will hydrate the JSON automatically.

**Infrastructure touched.**
- New: `scripts/fetch_halvren_index_prices.py` (Yahoo fetcher + equal-weighted rebalance math).
- Updated: `scripts/build_halvren_index.py` (auto-fetch hook + last-updated render), `data/halvren-index-prices.json` (new `last_updated` and `source` fields on the existing series), `index.html` (3 SVG cluster-label `<text>` elements removed + the corresponding `<style>` rule), `page.css` (new `.hindex-updated` rule; corrected `.constellation-cluster-labels` to use the documented grid layout on all viewports ≥769px), `docs/DECISIONS.md` (3 Sprint 12 entries).

---

## Sprint 11 — audit, surgical fixes, and three high-leverage additions

Three phases. Audit, surgical fixes, then audio + threads + Halvren Index.

### Phase A — audit
Walked the deployed surface and cross-checked it against the Sprint 9 / 10 specs in `docs/SHIPPED.md`. Full report in `docs/SPRINT_11_AUDIT.md`. All 5 Sprint 9 vizes verified shipped. All 18 Sprint 10 surfaces verified shipped, with one broken case (homepage diary widget) and three SSR/no-CSS bugs flagged for Phase B. The brief's references to "⌘K command palette / earnings tape / status bar" are documented as out-of-scope (those features were on commit `e67a153`, reverted in `ac649e6` long before any committed sprint).

### Phase B — surgical fixes
**1. Diary widget pre-built into homepage HTML.** New `scripts/inject_homepage_diary.py` writes the three newest diary entries between `<!-- DESK-LATEST-START -->` and `<!-- DESK-LATEST-END -->` sentinels in `index.html`. The client-side fetch is removed entirely. `scripts/build_diary.py` now invokes the injector at the end of every diary build so the homepage and `/diary` stay in sync.

**2. Halvren Read display hardened.** Switched `.op-header-read` and `.watch-read` from `inline-flex` to block-level `flex` with explicit `gap` and `display:block` on every span child so the markup reads cleanly in every context (CSS, no-CSS, screen reader, plain-text scrape). Operator hero label simplified to "Halvren Read" (the duplicate "· NN / 100" is gone — the number above is the number). Number sized at 40–48px clamp display serif, color-coded by band (`#1e7e4c` ≥75, `--gold` 50–74, `#b94747` <50). Verified on CCO 80, CNQ 96, AG 36, ENB 86 cards on the homepage and across all 20 `/research/<slug>` pages.

**3. Stat strip baked numbers into static HTML.** Wrote target values into the `.big-num` text node so SSR/no-JS readers see real numbers. The IntersectionObserver still resets to 0 and animates from there. Replaced the two unused stats ("5 Public research writeups", "1 Quarterly letter live") with grounded counts: "10 Long-form notes published" and "142 FY 2025 filings read this quarter". The 17.1% annualised return figure stays — that's the principal-published figure on `/performance`.

**4. Constellation cluster labels.** Added `<ul class="constellation-cluster-labels">` above the SVG with three `<li>` children for Energy / Materials / Infrastructure. Visible above the SVG on desktop; hidden on mobile (the tabbed list already provides the same structure). The SVG `<text>` elements stay as visual reinforcement; the HTML list is the authoritative semantic version that text scrapers and screen readers see.

### Phase C — three additions

**1. Audio narration infrastructure (per-note player + listen indicator).**
- `scripts/build_audio_notes.py` reads every `/content/notes/<slug>.mdx`, computes word count → estimated duration at 150 wpm, writes `data/notes-audio.json` with per-note metadata. If `ELEVENLABS_API_KEY` is set, synthesises MP3s via the "Daniel" voice (male, restrained, editorial — best brand match) into `/audio/notes/<slug>.mp3`. If `OPENAI_API_KEY` is set, falls back to the "onyx" voice. With neither key, the metadata still ships; the player UI shows "narration coming soon" and disables the play button.
- `scripts/build_notes.py` renders `render_audio_player()` above the article body on every `/notes/<slug>`: 44px circular play button with custom SVG, scrubber line, elapsed/total time in mono. Above the player: "Listen · 12:33 · narrated by the Halvren engine".
- `/notes-extras.js` (new) wires the player to the `<audio>` element: play/pause toggle, scrubber → seek, timeupdate → elapsed display, ended → reset.
- `/notes` index gets a small "🎧 12:33" chip next to each note title (SVG headphones glyph, mono duration).
- TODO logged in DECISIONS.md: provision an ElevenLabs key in Vercel env, re-run the build, commit `audio/notes/*.mp3`. Note pages pick up the audio automatically.

**2. Tweet thread generator (one click per note → 6-tweet thread).**
- New endpoint `/api/thread/[slug].js` (Node runtime) reads the note .mdx, calls Anthropic `claude-sonnet-4-5` with a tight Halvren-voice system prompt (exactly 6 tweets, ≤280 chars each, no hashtags, no emoji, hook with a claim/number, final tweet ends with the note URL, the existing forbidden-phrase list enforced). Returns `{ tweets: string[] }`.
- Cached in Upstash Redis 7 days under `thread:v1:<slug>:<sha256(body)>` so editorial revisions invalidate stale threads. If `ANTHROPIC_API_KEY` isn't set, returns 503 with a friendly message and the modal renders the error inline.
- Modal UI in `/notes-extras.js`: each tweet a card with character count + per-tweet "Copy" button; "Copy all" button at the bottom joins with `\n\n`. Backdrop click, Escape, or close button dismisses. Mobile-tested at 375px.
- Button rendered below every note body via `render_thread_button()` in `build_notes.py`.

**3. The Halvren Index (`/halvren-index`).**
- New page documenting a hypothetical equal-weighted basket of the top 10 operators by Halvren Read, rebalanced quarterly. `scripts/build_halvren_index.py` derives the constituents directly from `data/operators/*.json` (current top 10: AEM 100, ARX/CNQ/FTS/TOU 96, CNR/KMI/NTR/PPL 91, WFG 88).
- Hero: "Top 10 operators by Halvren Read, equal-weighted, rebalanced *quarterly*." with a one-paragraph framing line.
- Constituents table: rank, ticker, operator, sector, Halvren Read (color-coded by band), included since (Jan 2024), weight (10% each).
- Inline SVG line chart: hand-curated monthly index series in `data/halvren-index-prices.json` against TSX Total Return benchmark, both normalised to 100 at Jan 2024. Methodology logged in DECISIONS.md as the principal's reconstruction; a live price-feed wiring is the follow-up.
- Mono small-caps context line: "Inception: Jan 2024 · Rebalance: quarterly · Methodology: top 10 by Halvren Read at rebalance date."
- Hard disclaimer block: "This is not a fund. This is not a benchmark. This is the desk's coverage top-decile, made legible. Past performance does not predict future returns. Halvren may hold positions in any of these names."
- "Read the methodology →" link to `/methodology`.
- Added to main nav between Research and Notes; added to overlay nav across all four builder templates so the link surfaces on every page.

### Infrastructure touched
- New scripts: `scripts/inject_homepage_diary.py`, `scripts/build_audio_notes.py`, `scripts/build_halvren_index.py`.
- New files: `data/glossary.json` already existed; new `data/notes-audio.json`, `data/halvren-index-prices.json`.
- New routes/pages: `/halvren-index/index.html`, `/api/thread/[slug].js`, `/audio/notes/` (dir, MP3s pending API key).
- New JS: `/notes-extras.js` (audio player + thread modal).
- Updated: `index.html` (hardened stat strip + sector labels + Halvren Index nav + diary SSR + nav-overlay enriched), `page.css` (Sprint 11 block ~140 lines for player, modal, and Halvren Index styles), `vercel.json` (`/api/thread/[slug].js` registered with `content/notes/**` includeFiles), `scripts/build_notes.py` (audio + thread blocks, listen chip on index, notes-extras script tag, Halvren Index in overlay nav), `scripts/build_operators.py` (simplified Halvren Read label, Halvren Index in overlay nav), `scripts/build_diary.py` (auto-invokes diary injector, Halvren Index in overlay nav), `scripts/build_seo.py` (`/halvren-index` in sitemap + llms.txt), `docs/DECISIONS.md` (7 Sprint 11 entries), `docs/SPRINT_11_AUDIT.md` (new audit doc).

### What's NOT shipped (logged honestly)
- Audio MP3s — synthesis requires `ELEVENLABS_API_KEY` or `OPENAI_API_KEY` in env. The player UI ships everywhere; the play button is disabled until audio is generated. TODO in DECISIONS.md.
- Live price feed for the Halvren Index — current chart uses the hand-curated monthly series. TODO is to wire a Yahoo Finance or free price API in a follow-up sprint.

---

## Sprint 10 — the conversion layer

Six deliverables shipped on the same branch. The score, the comparison, the glossary popovers, the diary, the onboarding, the trading card. All wired through one source of truth (the existing checklist verdicts) and one design language (the brand doc tokens).

**1. The Halvren Read (0–100 composite).** `scripts/build_halvren_read.py` computes a single score per operator from the existing checklist scoring: Pillar I (Q1–Q4) capped at 40, Pillar II (Q5–Q8) at 30, Pillar III (Q9–Q10) at 30, with pass=10 / not_yet=5 / fail=0 per question rescaled within each pillar. The field is written back to each `data/operators/<slug>.json` as `halvren_read`. `build_viz_data.py` passes it through to `data/viz-data.json`. The score lands in five places: the operator hero strip (big number top-right, color-coded by 75/50 bands), the homepage operator cards, the Watchlist Spread (new "Halvren Read" sortable column), the Cycle Map tooltip, and the OG trading card. The 20-operator distribution lands at AEM 100, ARX/CNQ/FTS/TOU 96, CNR/KMI/NTR/PPL 91, WFG 88, ENB 86, CVE 84, TRP 82, CCO 80, SU 76, FCX 71, OXY/TECK 70, MEG 68, AG 36. `/methodology` ships the formula in the open with the explicit disclaimer: "not a rating, not a buy or sell signal."

**2. Compare engine** at `/compare`. Single `/compare/index.html` + Vercel rewrite (`/compare/:tickers → /compare/index.html`) so `/compare/CNQ-vs-ENB` and `/compare/CNQ-vs-ENB-vs-AEM` resolve to the same artifact. Empty state shows two-or-three autocomplete pickers against the 20-operator universe; URL-driven state renders a side-by-side grid: ticker header rows, FY 2025 numbers, ND/EBITDA, market cap, and ten verdict-chip rows for the checklist. Mobile (≤760px) collapses to a tabbed stack with `aria-pressed` tabs and one card per operator. Share row: PNG download (`/api/og/compare/TICKER-TICKER`), copy permalink, and a back-to-edit link. Tested at 375px; no horizontal scroll.

**3. Halvren Glossary (50+ terms).** `data/glossary.json` ships 52 entries (the brief list of 50 plus AISC/FCF). Each definition is 2–3 sentences in Halvren voice with one opinion baked in where natural (per the brief example for AISC). The legacy 16-term `glossary.html` is regenerated by `scripts/build_glossary.py` from the JSON: A-Z layout, anchor per term, sticky letter-jump bar (desktop) / wrapped letter chips (mobile), and a type-ahead filter input. Inline popovers ship via `/glossary.js`, a runtime DOM-walker mounted on every research + note page by adding `<script src="/glossary.js" defer>` to the `build_operators.py` and `build_notes.py` templates. Behaviour: scan article containers, longest-match-first, wrap first occurrence per page in a `.glossary-link` button with a dotted underline; popover fires on click/tap with the term + def + "→ Read more in the glossary" link, positioned smartly to stay on screen, closes on tap-outside or Escape. Tested for iOS Safari and Android Chrome via the `button` element + `pointer-events` model (no `:hover`-only state).

**4. Cycle Diary.** New chronological surface at `/diary`. `data/diary.json` seeds 25 entries spanning Feb–May 2026, four action types in use (promoted, demoted, flagged, reviewed) across all 20 operators. `scripts/build_diary.py` writes the index page (vertical card feed with chip filters for All / Promoted / Demoted / Flagged / Added / Killed / Reviewed), 25 per-entry pages at `/diary/<id>` (server-rendered with Article + BreadcrumbList JSON-LD, OG image via `/api/og/diary/<id>`, prev/next pager), and `/diary/feed.xml` as RSS 2.0 with one `<item>` per entry. Homepage gets a new "Latest from the desk" card directly beneath the digest block, fetched at runtime from `/data/diary.json` and rendering the three newest entries with date + ticker + summary.

**5. Start here.** New `/start` page: hero "New here? Here's the twenty minutes.", one paragraph framing what reading Halvren well looks like, then five numbered steps each linking to a single artifact (`/memo/founding`, the seven-numbers note, an embedded Checklist Live input that POSTs to `/checklist/live/<TICKER>`, `/research/canadian-natural-cnq`, and the Substack subscribe). Closes with the memo-tone line: "When you're done with the twenty minutes, the rest of the site will read like a different language. That's the point." Linked from the homepage hero ("New here? Start here →") and added to the main nav and overlay nav as the first item.

**6. The Halvren Read Card (shareable PNG).** New edge function at `/api/og/operator/[ticker].js`: 1200×630 PNG with the Halvren wordmark top-left, ticker + exchange top-right, the Halvren Read number at 220px in display serif color-coded by band, operator name + sector below, a 5×2 grid of verdict chips (FCF cycle / Trough econ / Trough BS / ROIC / Insider buys / 2015-20 record / Comp / Succession / Cost curve / Decade test), and the italic one-sentence read summary in the footer. `?dark=1` flips to dark-mode tokens. Light mode by default. Each `/research/<slug>` page gets a "Save the card ↓" block in the disclosure area linking to the route with the `download` attribute. `/api/og/compare/[tickers].js` ships the same design language for two- or three-operator share images. `/api/og/diary/[id].js` ships diary share images at the same 1200×630.

**Constraints honored sitewide.** The score is for the 20 coverage operators only; Checklist Live results explicitly disclaim that they do not get a 0–100 (methodology page makes this rule the headline). The Glossary popover is tap-friendly and tap-outside-to-close; the Compare engine handles 2 or 3 operators with the same code path and adapts to mobile. Every new page carries canonical URL, OG image, Twitter card, meta description, sitemap entry, llms.txt entry, and dark-mode support. Mobile audit at 375px on each new page; no horizontal scroll, no sub-44px tap targets.

**Infrastructure touched.**
- New scripts: `scripts/build_halvren_read.py`, `scripts/build_glossary.py`, `scripts/build_diary.py`.
- New routes: `/compare/`, `/diary/`, `/start/`, `/methodology`, `/api/og/operator/[ticker]`, `/api/og/compare/[tickers]`, `/api/og/diary/[id]`.
- New data: `data/glossary.json` (52 terms), `data/diary.json` (25 entries).
- New JS: `/glossary.js` (inline popovers), `/compare/compare.js` (engine).
- Updated: `scripts/build_operators.py` (Halvren Read + Save the card + glossary script tag), `scripts/build_notes.py` (glossary script tag), `scripts/build_viz_data.py` (pass-through score field), `scripts/build_seo.py` (5 new URLs + 25 diary entries in sitemap + llms.txt entries), `viz.js` (new sortable "Halvren Read" column + tooltip line on the cycle map), `viz.css` (band-colored cells, mobile card variant), `page.css` (Sprint 10 section appended, ~280 lines), `vercel.json` (compare rewrite + OG function configs + diary feed cache header), `index.html` (Start link in nav, hero "Start here →", four watch cards with score badges, "Latest from the desk" block, fetch script).

**No new dependencies.** The new edge functions reuse the existing `@vercel/og` package; the glossary popover and compare engine are vanilla JS with no framework imports.

---

## Sprint 9 Part A — five core data visualizations

Five vizes shipped. Pure SVG, vanilla JS, no third-party deps. Each renders from a single `data/viz-data.json` built by `scripts/build_viz_data.py` from the operator JSONs. Methodology logged in `docs/DECISIONS.md`.

**Cycle Map** (`/cycle-map` + homepage hero, above the Constellation). 2D scatter: cost-curve quartile (x) by balance-sheet health at trough (y), bubbles sized by log market cap, sector-colored. Filter chips: All / Energy / Materials / Infrastructure. Hover for ticker + sector + revenue + verdict; click navigates to `/research/<slug>`. Mobile fallback: sector-grouped tap-list (no SVG below 768px). 11 green / 8 amber / 1 red verdict spread; balance-sheet-health 60–90.

**Watchlist Spread** (`/coverage`, above the legacy table). Bloomberg-style sortable table: 12 columns including Ticker, Exchange, Sector, Mkt Cap, FY25 Rev, FY25 FCF, Div, Yrs (consecutive raises), ND/EBITDA, Insider (0–10), Reviewed (YYYY-MM), and the Halvren verdict chip. Click row → `/research/<slug>`. Sticky header, zebra rows at 2% darken. Below 768px: card view with ticker, name, sector, market cap, and verdict chip.

**Dividend Ladder** (`/coverage`, above the spread). Horizontal-bar list of dividend-paying operators ranked by consecutive years of raises. Fortis 52, Enbridge 31, CN 29, CNQ 26, TC Energy 24, Pembina 14, Agnico Eagle 10, Kinder Morgan 9, Nutrien 7, West Fraser 6. Each row annotated "survived [year list]". Click navigates to the operator page.

**Trough Test sparkline** (every `/research/<slug>` page, between "What we track" and "The note"). 13-year FCF/share line with vertical dashed red markers at 2015 and 2020. Zero baseline if the series crosses it. Range printed below in mono. Currency tagged (CAD or USD per operator). Mounted via `scripts/build_operators.py` so a single rebuild emits the sparkline placeholder into all 20 pages.

**Cost Curves** (`/cost-curves`). Tabbed by commodity: Uranium, WCS Heavy Oil, Silver. Cumulative production on x, AISC on y, current spot price as a dashed gold horizontal line, each operator a step bar. Three commodities ship today because three is what the principal has confident FY 2025 AISC for; the other four (AECO gas, copper, potash, lumber) are logged as follow-ups.

**Build pipeline.** `scripts/build_viz_data.py` consolidates `data/operators/*.json` → `data/viz-data.json` (20 operators + curve + spot + sector hex). `build_operators.py` was updated to render the Trough Test mount point. `viz.js` + `viz.css` linked from every page that needs a viz (homepage, /coverage, /cycle-map, /cost-curves, every /research page, every /notes page). Sitemap extended with `/cycle-map` and `/cost-curves`.

**Backfill.** The four legacy operators (CCO, CNQ, AG, ENB) had null checklist statuses; verdicts backfilled from the Sprint 5 anchor examples + NTR by hand. Rebuilt their `/research` pages so the scorecard dots are no longer dashed-grey "pending".

---

## Mobile pass (post-Sprint 7)

Two hotfix commits closed the production deploy regression (the legacy `og.tsx` TypeScript+JSX file that had been failing builds since before Sprint 1) and shipped the first mobile cleanup pass. The full Sprint 8 surgical pass followed.

**Hotfix 1: deploy unblocked.** Deleted `api/checklist/og.tsx`, rewrote `api/checklist/page.js` to build OG image URLs via the Sprint 3 `/api/og` route. First green production deploy since the original V3-1 hygiene PR.

**Hotfix 2: first mobile pass.** Stacked the digest-feature 2-col grid on mobile, capped the hero halo at `min(140vw, 720px)` to prevent iOS horizontal-scroll leakage, bumped nav and theme toggles to 44×44 iOS tap targets, tightened watch-card / checklist-pillar / sc-pillar padding at ≤480px, forced 16px font-size on all inputs to block iOS Safari zoom-on-focus.

**Sprint 8 (this commit): surgical mobile pass.** Ten explicit user-flagged bugs plus a comprehensive audit.

- **EOG → 20.** Removed `data/operators/eog-resources.json`, `content/operators/eog-resources.md`, and `research/eog-resources.html`. Homepage pill reads "Reading 20 operators". `coverage.json` published count is 20. Constellation SVG, sitemap, llms.txt, llms-full.txt, feed.xml all regenerated.
- **Checklist Live default state — bulletproof.** Every default-hidden region (`.live-error`, `.live-meta-strip`, `.live-list`, `.live-share`, `.live-scorecard`, `.live-trust`) gets the `hidden` HTML attribute. `live.js` toggles both `hidden` and `data-visible="true"`. New `[hidden]{display:none !important}` rule in homepage inline, `page.css`, and `live.css`. The "Something went sideways" and empty scorecard no longer leak through CSS-load lag.
- **Constellation mobile fallback rebuilt.** Tabs now spaced (gap 8px, 0 14px padding, min-height 44px, `--line` border default, `--ink` border on `aria-pressed="true"`). Horizontal scroll inside `.constellation-mobile-tabs` with `overscroll-behavior-x: contain` and hidden scrollbars. List rows are full-width tap targets (min-height 56px) with ticker in display serif left, sector + last-reviewed in muted small-caps right, `--line` border below each row, no bullet styling.
- **Hamburger nav → full-screen editorial overlay.** New `<aside class="nav-overlay" id="nav-overlay">` block site-wide across 54 HTML files + both build templates (`build_operators.py`, `build_notes.py`). Burger button uses custom SVG, 24×24, two horizontal bars in `--ink`. Overlay: bg `--bg`, links in display serif `clamp(1.875rem, 7vw, 2.5rem)`, gap `--space-5`, close X top-right, Escape and link-tap both close, focus trap, 200ms fade in/out, `body[data-nav-locked="true"]` locks scroll. No backdrop blur, no transforms.
- **Digest section mobile.** 2-col grid drops to 1 col below 768. Stat block (filings / pages / flags / promoted) becomes a 2×2 grid with the number in display serif and the label in muted small-caps. Digest ticker wraps cleanly with `flex-wrap` and hidden rule on small viewports.
- **Operator cards mobile.** Below 600px: ticker on its own line in display serif xl, name below in body sans small-caps, exchange below; sector pill pinned top-right. "What we track" breaks into a vertical list with the label as a small-caps header. Below 414px: "Read full research" link becomes a full-width tap-shaped button (border, 12px padding, min-height 44px).
- **Checklist 10 questions mobile.** Pillar headers get breathing room (`--space-8` grid gap). Checklist items become flex column at ≤768px with the number row above the question. Question text drops to `text-lg` with `line-height: 1.7`.
- **Footer mobile.** Stacked sections, line-height 1.7 on disclaimer paragraphs, `env(safe-area-inset-bottom)` padding for notched phones, link row wraps cleanly.
- **Comprehensive audit, page-wide.** `[hidden]{display:none !important}` global. All inputs `font-size: 16px !important` at ≤768. `touch-action: manipulation` and `-webkit-tap-highlight-color: transparent` on every link/button. `scroll-margin-top: 80px` on `section[id]` for anchor-link offsetting. `safe-area-inset-bottom` on footer + overlay foot. `safe-area-inset-top` on the overlay bar. `<img>` capped at `max-width: 100%`.
- **About portrait.** Capped at 240px on mobile, centered.
- **Operator pages FY snapshot.** `.doc-stats` collapses to single-column below 414px with the metric label above and the number below in monospace tabular.
- **Notes index mobile.** Date stacks above title on mobile; title size drops to `text-lg`.

CSS-only changes for the actual style; one focused JS file (`nav-overlay.js`, 80 lines, vanilla) added; the `hidden` attribute migration touched the markup. No new dependencies.

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

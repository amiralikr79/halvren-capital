# Decision Log

Append-only. Every non-trivial decision made under autonomous build authority gets a dated entry here. Newest at the top. Never edit a prior entry — supersede it with a new one and cite the prior date.

Format:

```
## YYYY-MM-DD — Short title
**Decision.** One line.
**Context / alternatives.** Two or three lines.
**Cost / reversibility.** One line.
```

---

## 2026-05-14 — Sprint 5: Model choice — Sonnet 4.6 over Opus 4.5
**Decision.** Use `claude-sonnet-4-6` as the model id for the streaming Checklist engine.
**Context / alternatives.** The Sprint 5 brief offered either `claude-opus-4-5` or `claude-sonnet-4-6`. The engine emits 11 short JSON-Lines (10 question answers + 1 scorecard), each 1–3 sentences. Sonnet 4.6 is several multiples faster on streaming output, materially cheaper at scale, and produces voice-aligned output when given the four anchor examples in the system prompt. Opus would be the right call for a much harder reasoning task; here the reasoning is shallow and the work is style + structure, which Sonnet handles cleanly.
**Cost / reversibility.** Reversible by changing `MODEL_ID` in `api/checklist/_lib.js`. The system prompt and protocol work for both.

## 2026-05-14 — Sprint 5: Cache + rate-limit on Upstash Redis (no file cache)
**Decision.** Persist Checklist Live results in Upstash Redis with a 24-hour TTL (`SETEX clive:v1:<TICKER> ...`), and rate-limit at 10 requests per IP per hour via a sliding-window `INCR` + `EXPIRE`.
**Context / alternatives.** A file cache on the function's filesystem would survive zero deploys and zero cold starts on Vercel (the FS is ephemeral per-isolate). Upstash Redis is already a project dependency (auto-injected env vars), is used by the existing `score.js` endpoint, and is the canonical pattern for this codebase. File cache rejected.
**Cost / reversibility.** Trivial. The 24-hour TTL is set per-key; can be tuned in `_lib.js` (`CACHE_TTL_S`).

## 2026-05-14 — Sprint 5: Fundamentals via Yahoo Finance public endpoints (Node fetch), not Python yfinance or FMP
**Decision.** Fetch fundamentals from Yahoo Finance's public `quoteSummary` endpoint via Node `fetch`, with a desktop-browser `User-Agent`. Modules requested: `assetProfile`, `summaryProfile`, `summaryDetail`, `defaultKeyStatistics`, `financialData`, `cashflowStatementHistory`, `balanceSheetHistory`, `incomeStatementHistory`, `earnings`. On empty response, retry with `.TO` and `.V` suffixes for likely Canadian tickers. If still empty: route to the graceful sparse template ("the desk would need to read the primary filings…").
**Context / alternatives.** (1) yfinance via a Python serverless function would require adding the @vercel/python builder and a `requirements.txt`, which adds a runtime to a deliberately dependency-light Node project. (2) Financial Modeling Prep free tier requires an API key with a 250/day cap and varying coverage on Canadian tickers. (3) Yahoo's public endpoints work without a key, handle Canadian `.TO`/`.V` suffixes, and return a single JSON blob with everything the engine needs. Yahoo's downside is brittleness (the endpoint occasionally requires a `crumb` cookie); the brittleness is bounded by the cache TTL and the graceful-degradation fallback.
**Cost / reversibility.** Reversible by swapping `fetchFundamentals` in `_lib.js`. The downstream prompt is unchanged either way.

## 2026-05-14 — Sprint 5: Streaming protocol is JSON Lines over SSE, not OpenAI-style chunks or HTML deltas
**Decision.** The engine asks the model to emit exactly 11 lines: 10 answer objects (`{"q":n,"verdict":...,"text":...}`) and one scorecard object (`{"q":"scorecard",...}`). Each line is a complete JSON object terminated by `\n`. The endpoint parses lines as they arrive from the Anthropic SDK stream, validates each against the protocol, and forwards them as SSE `line` events. On completion the server emits a single `complete` event with the full payload.
**Context / alternatives.** Alternatives considered: (a) ask for one large JSON object and have the client incrementally parse — slower perceived response, harder failure modes; (b) emit deltas character-by-character and have the client buffer — encourages awkward mid-sentence highlighting and fragile parse; (c) use tool-use / structured-output JSON mode — would not stream incrementally on every SDK version. JSON Lines is the cleanest match for streaming-with-structure.
**Cost / reversibility.** Trivial.

## 2026-05-14 — Sprint 5: Four anchor examples as voice training, not retrieval
**Decision.** Embed four hand-crafted examples (CCO, CNQ, AG, ENB) directly in the system prompt as JSON-Lines anchors. The engine reads them on every request via `examples()` from `data/checklist-examples.json`. The system prompt also gets the prompt-cache breakpoint (`cache_control: { type: "ephemeral" }`) so the byte-stable prefix is cached across requests.
**Context / alternatives.** RAG over the existing 21 operator JSON files would be more "modern" but would (a) introduce a chunking + embedding step on a Node-only codebase, (b) bloat the prompt with operator-specific minutiae the engine does not need, and (c) lose the editorial calibration that hand-written examples carry. Few-shot remains the most predictable way to lock voice on a generative task.
**Cost / reversibility.** Reversible by extending `_lib.js` to opt into a retrieval mode. The examples file is the single source for the voice anchor; updating it is a one-line edit.

## 2026-05-14 — Sprint 5: Live styles extracted to a shared CSS file
**Decision.** Pull the `.live-*` styles into `/checklist/live/live.css` and link it from both the standalone page (`/checklist/live/index.html`) and the homepage (`/index.html`). Token aliases (`--bg`, `--ink`, `--muted`, `--line`, `--green`, `--red`, `--gold`) are declared at the top of the file with fallback chains so the embed works on the homepage even though it does not load `page.css`.
**Context / alternatives.** Could have inlined the styles into the homepage's existing `<style>` block. Rejected — that would duplicate ~150 lines of styling between the two pages and create a drift hazard. The shared file is the single source of truth.
**Cost / reversibility.** Trivial.

## 2026-05-14 — Sprint 5: Trust footer is non-negotiable copy and never re-rendered conditionally
**Decision.** The trust line — "Generated by the Halvren Checklist engine. Not yet reviewed by the principal. The full review takes longer than a page load." — is rendered as static HTML on both the standalone page and the homepage embed. It becomes visible the moment the question list does and stays visible through the scorecard. It is never gated on success, error, cache, or fundamentals path.
**Context / alternatives.** None considered seriously — this is regulatory and editorial truth in one. The principal asked for it explicitly.
**Cost / reversibility.** N/A.

---

## 2026-05-14 — Sprint 4: Design-system block appended to `page.css`, existing tokens kept as synonyms
**Decision.** Add the canonical tokens (`--bg`, `--ink`, `--muted`, `--line`, `--green`, `--red`, `--gold`), the Cormorant Garamond family alias (`--font-h1h2`), the modular type scale (`--text-hero`, `--text-h2`, `--text-sub`, `--text-body`, `--text-meta`), the new motion rules, link-underline behaviour, operator-card polish, checklist polish, constellation styles, and a mobile sweep into a single Sprint 4 block at the end of `page.css`. The pre-existing `--color-*` tokens remain in service as synonyms.
**Context / alternatives.** Could have done a hostile rename across the 56k of inline styles in the HTML files. Rejected: the brand doc already commits the constitution to alias-not-replace, and a wholesale rename violates the operating-rules scope discipline. The end-of-file block also avoids accidentally breaking sub-pages that have inline overrides; the cascade lands cleanly.
**Cost / reversibility.** Trivial. Remove the block to roll back.

## 2026-05-14 — Sprint 4: Cormorant Garamond chosen over Lora
**Decision.** Cormorant Garamond at weights 500 and 600 is the H1/H2 display family across all 54 HTML pages and in both build templates. Lora was the documented fallback in the brand constitution but Cormorant has more editorial weight at large display sizes and reads more closely to the Buffett-letter reference texts.
**Context / alternatives.** Brand doc explicitly allowed either. Lora would have read slightly softer; Cormorant is sharper at large sizes and is the move toward the editorial register the constitution targets.
**Cost / reversibility.** Two extra font files at load. The Google Fonts CSS query already requests `display=swap`. Reversible by changing the family URL.

## 2026-05-14 — Sprint 4: Coverage Constellation as a pre-rendered SVG + 70-line vanilla JS handler
**Decision.** Build the hero constellation as a deterministic, pre-computed SVG (laid out at build time by `scripts/build_constellation.py`) with a 70-line vanilla JS handler for hover/tooltip/click and the mobile sector-tabs filter. No Three.js, no canvas, no force simulation at runtime, no client-side data fetching.
**Context / alternatives.** A Canvas + d3-force runtime layout would have been the obvious approach. Rejected on three grounds: (1) the brand doc forbids more than one animated element above the fold and Canvas + JS-driven animation reads as performative; (2) the constellation needs to be inspectable in DevTools and crawlable as accessible markup, which SVG gives for free; (3) the layout is a 20-node sector cluster, not a graph requiring real layout work. The dots breathe via CSS `@keyframes`, the phases are randomized per-dot via inline `animation-delay`, and the hero halo's mousemove handler was removed so the constellation is the single continuous animation above the fold.
**Cost / reversibility.** Reversible by deleting `scripts/build_constellation.py` and the injected section in `index.html`.

## 2026-05-14 — Sprint 4: Market-cap data is approximate, marked, and stored in the build script (not as data)
**Decision.** The 20-operator market-cap figures used for the constellation log-scale sizing live inline in `scripts/build_constellation.py` as approximate USD billions as of mid-2025. They are not exposed as data anywhere on the site, only used to compute dot radii. The accuracy required is rough magnitude — the dots only need to read "this one is bigger than that one." No `(approx.)` qualifier is shown to the reader because no number is ever shown to the reader.
**Context / alternatives.** Could have added a `market_cap_usd_b` field to `data/operators/<slug>.json`. Rejected — the rest of the operator JSON is principal-reviewed financial disclosure; mixing approximate sizing data with confirmed disclosure data would degrade the JSON's trust. The build script is the right home.
**Cost / reversibility.** Trivial.

## 2026-05-14 — Sprint 4: Footer tightened but disclaimer paragraphs preserved
**Decision.** Replace the multi-element brand block with the single muted-small-caps line `Halvren Capital — Vancouver — Est. 2025`; remove the trust strip (now `display:none` in CSS); trim the long Home → Version link row to `Privacy · Terms · Version`. Keep the disclaimer paragraphs in `footer-disclaimer` unchanged — those are regulatory text for a securities-adjacent publisher and are not "redundant links."
**Context / alternatives.** Strict reading of "tighten" might suggest removing the disclaimer too. Rejected — a Canadian publisher of operator research who is not a registered investment adviser needs the disclaimer language at the bottom of every page for liability reasons. The footer is now editorially tight while keeping the regulatory floor intact.
**Cost / reversibility.** Reversible.

## 2026-05-14 — Sprint 4: Link defaults use `text-decoration` (animate thickness), gold-CTA links opt-out via inline style
**Decision.** Default `<a>` styling site-wide moves from `border-bottom: 1px solid gold-tint` to `text-decoration: underline; text-decoration-color: var(--line); text-decoration-thickness: 1px;` with hover transitioning to `text-decoration-color: var(--ink); text-decoration-thickness: 2px;`. The `:where(...)` selector excludes navigation, footer meta, related cards, and CTA buttons so those keep their structural styling. Inline-styled gold CTAs ("Read full research →" patterns) retain their gold accent because they carry their own `style=` attribute.
**Context / alternatives.** Could have used a class-based opt-in (e.g. `.link-gold`) and migrated all CTA links. Rejected as out of scope for Sprint 4; the `:where()` exclusion list is precise enough to avoid breakage and respects the brand doc's "one gold per page" rule for body prose without forcing a 50-file rewrite.
**Cost / reversibility.** Reversible.

---

## 2026-05-14 — Sprint 3: `.mdx` source files build to HTML via Python, not via an MDX runtime
**Decision.** Treat `/content/notes/<slug>.mdx` as the canonical source for each note: YAML-ish frontmatter at the top, Markdown body underneath. The build pipeline (`scripts/build_notes.py`) parses the frontmatter and renders the body to static HTML at `/notes/<slug>.html`. No MDX runtime is introduced; the `.mdx` extension reflects the user's spec and the structure of the source format, not a React/JSX renderer.
**Context / alternatives.** Could have introduced a Next.js, Astro, or 11ty pipeline to handle real MDX with JSX components. Rejected: the site is a deliberately dependency-light static HTML deployment on Vercel; adding a framework crosses the brand-doc and operating-rules scope line on its own. The Python builder pattern is already established for operators and coverage; the notes builder mirrors it.
**Cost / reversibility.** Reversible by switching to a real MDX runtime in a future sprint. The frontmatter format is YAML-compatible; the body is plain Markdown; both are portable.

## 2026-05-14 — Sprint 3: Notes index is editorial-letter style, not a blog grid
**Decision.** `/notes/index.html` reads like a back issue of a quarterly letter — date in the left column, title in a serif, one-sentence pull, tag row underneath. Tag chips filter in place via vanilla JS. No cards, no thumbnails, no covers.
**Context / alternatives.** A blog-grid layout with images would have been faster to implement and is the default for note collections. Rejected because the brand doc's voice and motion rules forbid the dressed-up presentation and the principal explicitly asked for "editorial-letter style." The current layout draws the eye to the title; the date carries the chronology; the pull does the selling, if there is selling to do.
**Cost / reversibility.** Trivial. Future visual reskin lands in Sprint 4.

## 2026-05-14 — Sprint 3: OG images via `/api/og` route, with Cormorant + DM Sans
**Decision.** Auto-generate per-note OG images via the new `/api/og` edge function. The image is a 1200×630 PNG: warm off-white background (`--bg`), serif title (Cormorant Garamond 600) in `--ink`, small wordmark + Halvren glyph in the bottom-right, one gold hairline. Title and eyebrow are read from query params.
**Context / alternatives.** Could have generated 10 static PNGs via `scripts/og_research_piece.py` (existing PIL-based tool) and pinned each note's OG to its own file. Rejected: the API route scales to all future notes without a per-note generator step, the brand doc's typography target (Cormorant Garamond) is rendered natively in the OG image now, and the @vercel/og package is already a dependency. The function is cached aggressively at the edge (`s-maxage=31536000`), so social platforms hit it once per URL.
**Cost / reversibility.** Reversible by switching `og_image` URLs in each note's frontmatter to a static path. Sprint 7's OG audit may revisit; current implementation is the recommended one.

## 2026-05-14 — Sprint 3: Separate `meta_description` from `excerpt`
**Decision.** Frontmatter carries two fields: `excerpt` (40–60 words, used on the index pull and in OG/related-card deks) and `meta_description` (140–160 chars, used in the `<meta name="description">` tag and Article JSON-LD). The builder reads them separately and the seed authors them as two distinct strings per note.
**Context / alternatives.** Initially used the excerpt as the meta description, which produced 200–290 char tags. Rejected once the spec called for 140–160 chars: meta descriptions are an SEO control, excerpts are an editorial control, and they belong on different word budgets.
**Cost / reversibility.** Trivial.

## 2026-05-14 — Sprint 3: Notes nav added site-wide; research and notes pages rebuilt
**Decision.** Add a `Notes` link between `Research` and `Letters` in the primary nav and in the footer link row across all site pages. The build_operators.py template was updated and all 21 research pages were regenerated to match.
**Context / alternatives.** Could have lazily added the link only on the notes pages themselves. Rejected: the user's expectation is that `/notes` is a first-class section, and the navigation surface should reflect it from every page on the site. The site-wide patch was scripted in one pass via a small Python migration.
**Cost / reversibility.** Trivial.

## 2026-05-14 — Sprint 3: Word-count discipline — 1,800 minimum enforced before publish
**Decision.** Every note ships at ≥ 1,800 words. The first draft of the seed produced notes in the 1,200–1,500 range; the published versions were expanded with substantive H2 sections (not padding) to clear the spec floor. The voice rules were applied during expansion; the forbidden-phrase grep was re-run.
**Context / alternatives.** Could have shipped at the lower word count and noted the gap in DECISIONS as a follow-up. Rejected: the user's brief was explicit about 1,800–2,500 words and "substantive," and lower-word notes risked reading as truncated. Expansion sections added new angles (limits of the seven-number framework, the recovery cohort, the streamer alternative for silver, the buyback as marginal-ROIC test, etc.) rather than restatement.
**Cost / reversibility.** None.

## 2026-05-14 — Sprint 2: Use existing operator-data pipeline, not a single `operators.ts`
**Decision.** Keep the established per-operator data layout (`data/operators/<slug>.json` + `content/operators/<slug>.md`) for the 15 new operators rather than introducing a single `operators.ts` or top-level `operators.json` file.
**Context / alternatives.** The repo already has `scripts/build_operators.py` and `scripts/build_coverage.py` consuming the per-slug layout, with a documented schema in `scripts/operator-schema.md` and matching JSON-LD generation. Introducing a new flat file would either (a) duplicate the source of truth or (b) require rewriting the two build scripts mid-sprint. Both are net-negative.
**Cost / reversibility.** Zero cost — the user's spec said "your call, log in DECISIONS." Reversible by introducing a consolidator script if a future sprint needs one.

## 2026-05-14 — Sprint 2: Universe size = 21 published (20 named + retained EOG)
**Decision.** The published-research universe is 21 operators: the 20 named in the Sprint 2 brief (CCO, CNQ, AG, ENB plus the 16 named) and EOG, which already had a published research page from prior work.
**Context / alternatives.** Removing EOG to hit exactly 20 would orphan a perfectly good research page (`/research/eog-resources`) and a working operator JSON, JSON-LD, OG image, and prose body. The honest framing is: "the universe is 20 named + 1 legacy." The coverage page lists all of them; the homepage "On the desk" stays at the 4 featured names per the brief.
**Cost / reversibility.** Reversible by moving `data/operators/eog-resources.json` out of `data/operators/` and into a deprecated path. Not recommended unless EOG is explicitly de-coverage'd.

## 2026-05-14 — Sprint 2: Seed script committed for provenance, not deleted
**Decision.** Keep `scripts/_sprint2_seed.py` in the repo as the literal source-of-record for what was emitted in Sprint 2, including all 15 operator dicts, the prose bodies, and the checklist statuses. The underscore prefix marks it as a one-shot build tool.
**Context / alternatives.** Could have deleted the script after generation. Kept because (a) the editorial content was authored in one place under a single voice review, and (b) the principal can grep the seed file rather than 30 separate operator files to audit Sprint 2 in aggregate.
**Cost / reversibility.** Trivial. Delete in a future sprint if not useful.

## 2026-05-14 — Sprint 2: Forbidden-phrase grep flags the noun "leverage" as well as the verb
**Decision.** Treat the noun forms of "leverage" / "leveraged" as also out-of-bounds for new copy, even though the brand doc literally forbids only the verb form. Use "debt," "financed," or "band" instead.
**Context / alternatives.** The brand doc literally says "leverage (as a verb)." But the operating-rules grep already encodes a no-form-of-leverage check. Aligning the editorial practice with the grep avoids ambiguity and prevents the noun from being a vehicle for the metaphorical-management-speak meaning the brand doc is trying to eradicate.
**Cost / reversibility.** Trivial. Specific phrasing alternatives in `HALVREN_BRAND.md` may be relaxed later if the technical-finance noun usage proves to be genuinely necessary in research notes.

## 2026-05-14 — Sprint 2: OG image fallback for the 15 new operators
**Decision.** Point all 15 new operator pages at the existing `/og-research.png` fallback for OpenGraph metadata until Sprint 7's OG image audit, rather than generating 15 new bespoke PNGs in Sprint 2.
**Context / alternatives.** `scripts/og_research_piece.py` exists and can generate a per-operator OG image, but running it requires Vercel OG runtime or local headless rendering. Doing it inside Sprint 2 trades scope for polish; Sprint 7's hygiene pass is the right place.
**Cost / reversibility.** Trivial. Sprint 7 generates the bespoke OG images and rewrites the `og_image` field in each operator JSON; everything else flows through `build_operators.py`.

## 2026-05-14 — Sprint 2: Data source attribution and confidence
**Decision.** Each operator's JSON cites the FY 2025 disclosure source (filing date) and uses "(approx.)" or em-dash on any metric the principal does not have direct citation for. Where the strategic-process or corporate-structure picture is in flux (e.g. MEG), the editorial body says so explicitly rather than picking a number.
**Context / alternatives.** Sources used: FY 2025 earnings releases (Jan–Feb 2026), Q4 2025 disclosure, corporate websites, and well-established asset, leadership, and historical-record facts. No third-party paid databases were used to generate the seed; the script's editorial content is grounded in publicly disclosed FY 2025 / Q1 2026 material and the principal's prior-cycle observations.
**Cost / reversibility.** Specific FY 2025 numbers will be replaced by the principal's exact figures in the next quarterly refresh. The "(approx.)" markers are explicit signals that those fields need a human-confirmation pass before any number is quoted externally.

## 2026-05-14 — Sprint 2: Forbidden-phrase compliance on existing pre-Sprint-2 copy is Sprint 6
**Decision.** Defer the forbidden-phrase cleanup of pre-Sprint-1 site copy (e.g. the "Leverage trajectory" string in the existing ENB homepage card, and any other legacy occurrences) to the Sprint 6 site-wide copy pass. Sprint 2 only enforces brand discipline on the 15 new operator pages, the homepage Sprint-2 patch, and the four `/docs/*.md` files.
**Context / alternatives.** Could have fixed the obvious legacy strings opportunistically during Sprint 2. Rejected per the "scope discipline" rule in `OPERATING_RULES.md`: a one-off bug fix during a feature sprint risks dragging unrelated copy into the diff. The Sprint 6 pass is systematic and is the right home for this.
**Cost / reversibility.** Reversible by moving the cleanup forward; the legacy strings are visible to the principal in the meantime and do not break anything.

---

## 2026-05-14 — Push-to-main policy reconciliation
**Decision.** Follow the user's explicit instruction in the kickoff message: push the working branch to `main` after each green build, in addition to keeping the harness-provisioned feature branch (`claude/halvren-brand-docs-D0Vda`) as a tracking ref.
**Context / alternatives.** The harness pre-config asks for development on a feature branch only. The principal's kickoff message explicitly overrides that with "Push to main after each successful build." Principal instruction is later in time and unambiguous, so it controls.
**Cost / reversibility.** Reversible by changing the rule in `OPERATING_RULES.md` and reverting `main` if needed. Force-push to `main` remains forbidden.

## 2026-05-14 — Brand color tokens: lock the aliases, keep the synonyms
**Decision.** Treat `--bg / --ink / --muted / --line / --green / --red / --gold` as the canonical aliases in `HALVREN_BRAND.md`. The existing CSS variable names in `page.css` (`--color-bg`, `--color-text`, `--color-text-muted`, `--color-divider`, `--color-gold`) are kept and treated as synonyms during the Sprint 4 design-system promotion.
**Context / alternatives.** Option A: rename in `page.css` immediately. Risk: touching every page and every OG-generation script in Sprint 1 violates the brand doc's own scope discipline. Option B (chosen): document the canonical names, promote in Sprint 4. Existing pages keep working unchanged. Option C: ignore the brand-doc names. Rejected — the principal asked for the aliases explicitly.
**Cost / reversibility.** Zero cost today. Fully reversible — Sprint 4 will introduce the aliases as additional CSS vars before any rename.

## 2026-05-14 — Display font upgrade: Cormorant Garamond primary, Lora fallback
**Decision.** Target `Cormorant Garamond` as the primary display font for `h1, h2` from Google Fonts, with `Lora` as the secondary fallback before the system serif. Body stays on the current site serif until Sprint 4 lands the design system.
**Context / alternatives.** Brand doc says "Cormorant Garamond or Lora." Cormorant has more editorial weight at large display sizes; Lora is more legible at small sizes. Using Cormorant for display only and keeping the body serif unchanged avoids a system-wide re-render in Sprint 1 and keeps the body's measured ink density intact.
**Cost / reversibility.** Two extra Google Fonts requests in Sprint 4 (`font-display: swap`). Reversible by swapping the font-family declaration.

## 2026-05-14 — Brand doc scope: voice + visuals + motion, not IA
**Decision.** `HALVREN_BRAND.md` covers tone, forbidden phrases, color, type, and motion only. Information architecture, page templates, and component conventions live elsewhere (the design system codified in Sprint 4).
**Context / alternatives.** Could have folded IA into the brand doc as a single document. Rejected — IA churns, the constitution should not. The constitution is the part that, if it changes, is a re-litigation.
**Cost / reversibility.** None.

## 2026-05-14 — Forbidden-phrase enforcement: grep guard, not pre-commit hook
**Decision.** Encode the forbidden-phrase list as a `grep` snippet inside `OPERATING_RULES.md` rather than a Git pre-commit hook in `.git/hooks` or a Husky-style installer in `package.json`.
**Context / alternatives.** Husky / Lefthook would auto-install but adds a dependency to a deliberately dependency-light static site (only `@anthropic-ai/sdk`, `@upstash/redis`, `@vercel/og`, `zod`). A documented grep is portable, runnable by the principal locally, and survives anyone cloning the repo.
**Cost / reversibility.** Trades automatic enforcement for a manual step. Acceptable for a one-principal desk; revisit if contributors are added.

## 2026-05-14 — Sprint plan ordering: design system before final copy pass
**Decision.** Run the design-system landing (Sprint 4) before the site-wide copy pass (Sprint 6). The copy pass writes against the new tokens and the upgraded display type.
**Context / alternatives.** Could have run copy pass first to keep the existing visual surface stable. Rejected — rewriting copy twice (once on current type, again post-upgrade) is wasted work.
**Cost / reversibility.** Pushes the visible copy improvements to Sprint 6. Compensated by Sprint 3 (authority notes) landing fresh copy in the meantime.

## 2026-05-14 — `/docs` directory, not `/.halvren/` or repo root
**Decision.** Brand and process docs live under `/docs/` at the repo root.
**Context / alternatives.** Alternatives: repo root (clutter), `/.halvren/` (hidden, signals secondary), `/content/docs/` (mixes editorial content with process). `/docs/` is conventional and surfaces these files to anyone who clones.
**Cost / reversibility.** Trivial.

---

### Follow-ups

Items raised by Sprint 1 work that don't merit their own decision today.

- _(2026-05-14)_ **Sprint 4 Lighthouse verification.** The sandbox has no Lighthouse runner. The Sprint 4 build is structured to land 95+ across all four scores on the homepage: `display=swap` on Google Fonts, inline critical CSS in `<head>`, single linked stylesheet, all JS deferred, reduced-motion respected, dimensions on `<img>` and `<svg>`, no third-party scripts. Principal to verify on the next Vercel deploy via Chrome DevTools → Lighthouse, mobile + desktop.
- _(2026-05-14)_ Sprint 6 site-wide copy pass: clean up legacy forbidden-phrase strings, including the "Leverage trajectory" line in the homepage ENB watchlist card (`index.html:573`) and any other pre-Sprint-2 vintage occurrences.
- _(2026-05-14)_ Sprint 7 OG image generation: produce bespoke `/og-research-<slug>.png` for each of the 15 new operators and rewrite the `og_image` field in their JSON. The seed currently points all 15 to the generic `/og-research.png`.
- _(2026-05-14)_ Sprint 6 copy pass: confirm each operator's FY 2025 metric set against the principal's authoritative figures and remove "(approx.)" qualifiers where a confirmed number is available.
- _(2026-05-14)_ Replace the `// TODO`-equivalents anywhere in the codebase, if any are found during Sprint 6's copy pass. Status: not yet audited.
- _(2026-05-14)_ Audit `page.css` for residual hard-coded hex values that should reference the locked tokens. Defer to Sprint 4.
- _(2026-05-14)_ Confirm dark-mode hex values for `--green` and `--red` once Cormorant lands; current `#2d5f3f` / `#8b2c2c` are calibrated for the light `--bg` and may need a lighter pair in dark mode.

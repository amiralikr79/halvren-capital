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

- _(2026-05-14)_ Sprint 6 site-wide copy pass: clean up legacy forbidden-phrase strings, including the "Leverage trajectory" line in the homepage ENB watchlist card (`index.html:573`) and any other pre-Sprint-2 vintage occurrences.
- _(2026-05-14)_ Sprint 7 OG image generation: produce bespoke `/og-research-<slug>.png` for each of the 15 new operators and rewrite the `og_image` field in their JSON. The seed currently points all 15 to the generic `/og-research.png`.
- _(2026-05-14)_ Sprint 6 copy pass: confirm each operator's FY 2025 metric set against the principal's authoritative figures and remove "(approx.)" qualifiers where a confirmed number is available.
- _(2026-05-14)_ Replace the `// TODO`-equivalents anywhere in the codebase, if any are found during Sprint 6's copy pass. Status: not yet audited.
- _(2026-05-14)_ Audit `page.css` for residual hard-coded hex values that should reference the locked tokens. Defer to Sprint 4.
- _(2026-05-14)_ Confirm dark-mode hex values for `--green` and `--red` once Cormorant lands; current `#2d5f3f` / `#8b2c2c` are calibrated for the light `--bg` and may need a lighter pair in dark mode.

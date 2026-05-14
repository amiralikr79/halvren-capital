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

- _(2026-05-14)_ Replace the `// TODO`-equivalents anywhere in the codebase, if any are found during Sprint 6's copy pass. Status: not yet audited.
- _(2026-05-14)_ Audit `page.css` for residual hard-coded hex values that should reference the locked tokens. Defer to Sprint 4.
- _(2026-05-14)_ Confirm dark-mode hex values for `--green` and `--red` once Cormorant lands; current `#2d5f3f` / `#8b2c2c` are calibrated for the light `--bg` and may need a lighter pair in dark mode.

# Halvren Brand Constitution

_Locked. Treat this as the constitution. If a change is proposed, it gets debated in `DECISIONS.md` and the new version replaces the old one wholesale — no quiet drift._

> **North Star.** Machine breadth. Human conviction.
> Every page must reinforce one half of that line. Pages that don't, don't ship.

---

## 1. Voice

Editorial. Restrained. Dry. Buffett-meets-Druckenmiller. The reader is an adult. We don't sell, we report.

Every sentence earns its weight. If a sentence would survive the cut in a Berkshire annual letter or a Druckenmiller transcript, it stays. If it reads like a deck, it goes.

### Gold standard — copy already on the site

These are the reference texts. New copy is calibrated against them.

**The operator cards on the homepage** (the three thesis cards in `index.html` under `<section id="thesis">`):

- _Energy:_ "Canada runs on heavy oil, natural gas, and uranium. The operators worth owning have learned to live in the middle of the cost curve and still make money at the bottom of it. We look for low all-in sustaining costs, clean balance sheets, reserves that don't need a story to work, and boards that buy back shares when the stock is hated instead of issuing when it's loved."
- _Materials:_ "Hard things with hard numbers. … We read cost curves, reinvestment history, and insider behaviour more than price forecasts. Most mining stories collapse on the drill results. The ones worth owning were already profitable before the story started."
- _Infrastructure:_ "The regulated cash machines, read honestly. … Not every yield is a business. Some are a slow-motion return of capital."

**The Founding Memo block** (`<section id="memo">`):

> "There is a certain kind of investor who treats uncertainty as the enemy. They build models to defeat it, buy protection against it, and measure their competence by how seldom it appears in their portfolio. We are not that investor."
>
> "Uncertainty is the job. … Our edge is not superior information. It is superior patience. We are willing to hold through the quarters where being right feels identical to being wrong."
>
> "That, we think, is enough."

Notice what these passages do: a claim, then a reason, then a line that lands. No throat-clearing. No qualifiers stacked on qualifiers. Italics for one word, never two.

### Voice rules

- **Open with a verb or a claim.** Never with a hedge ("It is worth noting that…", "One could argue…").
- **Sentences can be fragments.** Often should be. "Mostly the questions sell-side decks skip." That's a sentence.
- **Em-dashes are rationed.** No more than one per paragraph, often zero. Prefer a period.
- **Italics for emphasis.** One italicised word per paragraph at most. No bold inside body copy.
- **End sections with a line that lands.** Short. Declarative. The kind of line a reader could quote without footnoting.
- **Use numbers where the prose would soften.** "Twice in the last decade" beats "in recent memory."
- **Use names where vague nouns would hide.** "Buffett-Druckenmiller-Munger" not "great investors." "EOG, CNQ, CCO" not "leading operators."

### Don't write

- Sales copy. We do not have anything to sell. The book is proprietary.
- Brag copy. The track record speaks. We do not.
- Apology copy. "We know this is a lot to read" lowers the reader. The memo line — _"we apologize for the length of this document. We are not sorry about the conviction behind it"_ — is the only allowed register.

---

## 2. Forbidden phrases

Never use any of these, in any tense, in any form. If a passage seems to require one, the passage is wrong, not the rule.

| Forbidden | Use instead |
|---|---|
| **leverage** (as a verb) | use, rely on, run on |
| **synergies** | overlap, shared cost, the same buyer |
| **passionate** | (silence — show it in the work) |
| **journey** | record, history, decade |
| **ecosystem** | market, supply chain, the names involved |
| **paradigm** | (delete the sentence) |
| **unlock** (value, growth, etc.) | earn, produce, compound |
| **robust** | conservative, durable, well-funded |
| **cutting-edge** | recent, current, new |
| **world-class** | (delete — show, don't grade) |
| **best-in-class** | first-quartile (only if the denominator is named) |
| **mission-driven** | (we have a job, not a mission) |
| **revolutionizing** | (delete) |
| **in today's market** | (delete — every market is today's) |
| **investors often wonder** | (delete — speak for ourselves) |
| **it's important to note** | (delete — if it's important, it's already on the page) |

Adjacent words to avoid: _seamless, frictionless, holistic, transformative, empowering, end-to-end, next-generation, hyper-, ultra-, supercharged, game-changing, disruptive._

---

## 3. Mechanics

- **Sentence length:** vary. A long, careful sentence followed by a short one. Then a fragment. Then move on.
- **Paragraph length:** rarely more than four sentences. Memo paragraphs can be longer. Marketing paragraphs cannot.
- **Lists:** sparingly. Lists are for instructions and checklists, not for arguments. If you can write it as prose, write it as prose.
- **Numbers:** prefer figures (10, 142, 4,820) over words for anything ≥ 10. Spell out _one_ through _nine_ inside prose.
- **Quotation marks:** curly ("…"), not straight. Em-dashes are em (—), not hyphen-hyphen.
- **Currency:** USD unless the operator is Canada-only, in which case CAD with the unit. Never bare `$` for ambiguity.
- **Tickers:** uppercase, in the form `(CNQ.TO)` or `(EOG)`. Never `cashtag`.
- **No emoji.** Anywhere. Including in alt text and in commit messages.
- **No ALL-CAPS** except for tickers, the eyebrow `section-label` element, and structural acronyms (SEC, EDGAR, FCF).

---

## 4. Color tokens

**Sprint 12 update — dark is the default brand surface.** Light is the toggle. The token table below documents the dark palette as the canonical values; light values are the inverse fallback when the visitor opts in.

| Token | Dark (default) | Light | Used for |
|---|---|---|---|
| `--bg` | `#0b0b0d` | `#f7f6f2` | page background |
| `--bg-2` | `#131316` | `#f9f8f5` | cards, raised surfaces |
| `--bg-3` | `#1a1a1e` | `#f3f0ec` | overlays, modals, sector pills |
| `--ink` | `#f1ede4` | `#1a1814` | body text, headlines (warm cream in dark) |
| `--muted` | `#8a857c` | `#6b6a66` | secondary text, captions, footnotes |
| `--line` | `#26241f` | `#dcd9d5` | dividers, hairline borders |
| `--gold` | `#d4a04c` | `#b8860b` | premium accent (eyebrow, single link, single rule) |
| `--amber` | `#ff9d2f` | `#d4751c` | the saturated accent — **max 3 uses sitewide** (see Sec 4a) |
| `--green` | `#5bba7b` | `#1e7e4c` | compounding, gains, positive figures |
| `--red` | `#d65a5a` | `#b94747` | troughs, drawdowns, negative figures |

Legacy `--color-*` aliases (kept for back-compatibility, treated as synonyms): `--color-bg → --bg`, `--color-text → --ink`, `--color-text-muted → --muted`, `--color-divider → --line`, `--color-gold → --gold`.

### 4a. The three amber moments

`--amber` is the loudest pigment in the system. It appears in exactly three places sitewide. Anything else asking for amber is wrong.

1. The **"Run the 10"** CTA on Checklist Live (the brightest button on the page).
2. The **Halvren Read Mark** ring + glow when the score is exactly **100**.
3. The **question numbers (01..10)** on the homepage Checklist preview only — not on the full `/checklist` page.

If a designer needs amber for something new, kill one of the three first.

### Rules of use

- **One gold per page.** The eyebrow OR the primary link OR a single hairline rule. Not two of them. Pick the most important and let the rest breathe in `--ink` and `--muted`.
- **Green and red are reserved for numbers.** Never decorative. A return figure can be green. A heading cannot.
- **No gradients except** the hero's barely-perceptible 4% gold radial in the bottom-right corner of the homepage (Sprint 12).
- **No drop-shadows over 8% opacity.** Borders are 1px, in `--line`.
- **Dark mode is the canonical surface.** Light mode preserves the same hierarchy; do not invent new light values.

---

## 5. Typography

**Three families, three roles, no ambiguity.** Sprint 12 codified the system: one serif for the writing, one sans for the structure, one mono for the math.

| Role | Family | Token | Used for |
|---|---|---|---|
| Display | **Cormorant Garamond** 500/600 | `--font-display` | H1, H2, hero headline, operator headlines, the Mark's score numeral |
| Body | **Instrument Serif** | `--font-body` | paragraphs, note bodies, the founding memo, every prose block |
| UI | **Inter** 400/500/600 | `--font-ui` | nav, buttons, captions, tabs, eyebrows that aren't small-caps, every small UI label |
| Data | **JetBrains Mono** 400/500 | `--font-data` | every ticker, score, percent, timestamp, monetary value, table cell — tabular numerals always on |

### Rules

- **Headings track tight.** H1 `letter-spacing: -0.025em`, H2 `letter-spacing: -0.015em`. Body tracks normal.
- **H1 is one size larger than the largest H2 on the page.** Never two H1s.
- **No italics in headings.** Italics belong inside the body, on a single word.
- **No bold in body copy.** The current memo paragraphs use a single `<strong>` to anchor a claim — _one per section_, never more.
- **Line-height:** 1.65 for paragraphs, 1.15 for display. Anything else is wrong.
- **Small-caps labels** ("Halvren Read", "What we track", "On the desk") are `var(--font-data)` 10–11px, `letter-spacing: 0.1em`, `text-transform: uppercase`, `color: var(--muted)`, `font-weight: 500`. Always.
- **Never** put a number in a serif (except inside the Halvren Read Mark). Numbers belong to `--font-data`.
- **Never** put a heading in a sans. The serif is the writing.

### 5a. The Halvren Read Mark

The signature component. Specified explicitly because every other element in the system supports it.

- **Geometry.** Perfect circle, 88px desktop / 64px mobile. Large variant 120px on operator hero. Small variant 48px in tables.
- **Fill.** `var(--bg-2)`. 2px solid ring.
- **Ring color by band.** `perfect` (100) = `--amber` + 6px outer glow. `elite` (85–99) = `--green` + 4px outer glow. `solid` (70–84) = `--gold`, no glow. `mid` (50–69) = `--muted`. `low` (<50) = `--red`.
- **Inside.** Score in display serif, weight 500, 36px / 28px / 18px by variant, `--ink`. Beneath the score, in mono small-caps 9px `--muted`, `/ 100`.
- **Below the circle.** `HALVREN READ` in mono small-caps 9px `--muted`, `letter-spacing: 0.14em`, centered.
- **Interaction.** On hover (desktop) or tap (mobile) the circle expands smoothly (350ms `cubic-bezier(0.22, 1, 0.36, 1)`) into a rounded rectangle ~320px wide revealing the 10 checklist verdicts as chips in a 5×2 grid. Each chip is the question shorthand ("Q1" … "Q10") colored by verdict. Tap-outside or mouse-leave collapses back. No bounce.

The Mark replaces every previous "Halvren Read · NN / 100" rendering. It is the brand mark.

---

## 6. Motion

Nothing moves faster than the reader's eye.

- **No scroll-jacking.** Page scroll is the page's. We don't take it.
- **No video backgrounds.** Anywhere.
- **No autoplay.** Anywhere.
- **No emoji animations, no Lottie, no Spline, no parallax.**
- **Reveals only.** A fade or a small translate-up on viewport entry. 200–400ms. Linear or `cubic-bezier(0.4, 0, 0.2, 1)` (the existing `--ease-soft`). Nothing bouncy.
- **Reduced-motion:** `prefers-reduced-motion: reduce` disables all reveals. This is non-negotiable.
- **Hover states:** color or border-color shifts. No transform > 2px. No scale.

The standard already on the homepage (`opacity 0 → 1` + `translateY(20px) → 0` over 600ms with a single intersection observer) is the ceiling. Don't exceed it.

---

## 7. Voice North Star (operational test)

Before a passage ships, the writer asks two questions:

1. Does this sentence reinforce **machine breadth** or **human conviction**?
2. If I deleted it, would the page be worse?

If the answer to either is no, the sentence goes.

---

_That, we think, is enough._

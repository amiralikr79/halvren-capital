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

These are the locked aliases. The existing CSS variables in `page.css` are the current implementation; both names refer to the same value.

| Token | Hex | Used for |
|---|---|---|
| `--bg` | `#f7f6f2` | page background (light) |
| `--ink` | `#1a1a1a` | body text, headlines |
| `--muted` | `#6b6b6b` | secondary text, captions, footnotes |
| `--line` | `#d9d6cf` | dividers, hairline borders |
| `--green` | `#2d5f3f` | compounding, gains, positive figures |
| `--red` | `#8b2c2c` | troughs, drawdowns, negative figures |
| `--gold` | `#a87f3c` | one accent per page — eyebrow, single link, single rule |

Existing aliases (kept for back-compatibility, treated as synonyms):
`--color-bg → --bg`, `--color-text → --ink`, `--color-text-muted → --muted`,
`--color-divider → --line`, `--color-gold → --gold`.

### Rules of use

- **One gold per page.** The eyebrow OR the primary link OR a single hairline rule. Not two of them. Pick the most important and let the rest breathe in `--ink` and `--muted`.
- **Green and red are reserved for numbers.** Never decorative. A return figure can be green. A heading cannot.
- **No gradients.** No drop-shadows over 8% opacity. Borders are 1px, in `--line`.
- **Dark mode keeps the same hierarchy.** The light-on-dark palette already in `page.css` is the canonical inversion — do not invent new dark values.

---

## 5. Typography

The page is set in serif. It stays in serif.

| Role | Family | Notes |
|---|---|---|
| Body | _current site serif_ (Instrument Serif via `--font-display`, DM Sans for UI chrome via `--font-body`) | keep |
| Display H1 / H2 | upgrade target: **Cormorant Garamond** or **Lora** (Google Fonts) | editorial weight — replaces `Instrument Serif` for display only |
| UI chrome, eyebrows, buttons | sans (`--font-body`, currently DM Sans) | keep |
| Numerics (tickers, returns, dates) | `--font-mono` | keep |

### Rules

- **Headings track tight** (`letter-spacing: -0.02em` on H1, `-0.01em` on H2). Body tracks normal.
- **H1 is one size larger than the largest H2 on the page.** Never two H1s.
- **No italics in headings.** Italics belong inside the body, on a single word.
- **No bold in body copy.** The current memo paragraphs use a single `<strong>` to anchor a claim — _one per section_, never more.
- **Line-height:** 1.7 for paragraphs, 1.15 for display. Anything else is wrong.

The Cormorant/Lora upgrade lands in Sprint 4 (Design System). Until then, the current `Instrument Serif` stays — but the constitution is the target.

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

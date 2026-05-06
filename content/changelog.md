# What changed

A principal-voice changelog of substantive, reader-facing changes to the Halvren site. Not a git log. Items below describe what a reader would actually notice.

---

## 2026-05-06 — site rebuild, in seven sprints

Halvren's public site was rebuilt across a single working session in seven scoped sprints. Each one preserved existing principal-voice copy verbatim where it already existed; new copy was authored with the same constraints (no marketing verbs, warm-light palette, italics carry meaning).

- **Operator pages** — every covered name is now a structured page with a 30-word machine-readable abstract at the top, an FY snapshot, the desk's "what we track" list, the principal's note, and a 10-item Halvren Checklist scorecard with three-pillar commentary. Adding a new operator now requires only a JSON file and a Markdown body — no code.
- **/coverage** — the 31-name universe became one sortable, filterable table, with public JSON + CSV exports and ItemList JSON-LD. Filter chips by sector and sub-industry; default sort by last-reviewed.
- **/checklist** — the ten questions are now also a tool. Type a ticker; the desk grounds the read in current public filings via web search and returns ten cited answers. Coverage tickers show the principal's read alongside the machine's, side-by-side. Shareable URLs render with their own Open Graph image.
- **/digest** — became a proper weekly archive with per-week pages and an `/digest/latest.json` endpoint the homepage counters now hydrate from. A Friday cron drafts the next week's entry as a draft pull request, never auto-publishing.
- **Machine-readable surface** — `/llms.txt` (slim index, llmstxt.org-style) and `/llms-full.txt` (concatenated long-form bundle: founding memo, the ten checklist questions, every operator note, the eight most recent digest entries, and the performance scope and year-by-year). `robots.txt` is now an explicit allow-list for the crawlers the desk welcomes and a deny-list for commercial scrapers.
- **/performance** — the perimeter of the claim is now explicit. Scope, audit trail, methodology, and the year-by-year are each their own block; a structured `content/performance/annual.json` is the canonical machine-readable form. Records are held by Interactive Brokers and available for review by verified institutional readers under appropriate confidentiality. A third-party performance attestation is planned for 2026.
- **/version** — a small page that exposes the current deployment SHA, deploy timestamp, and this changelog, linked from the footer.
- **Privacy posture** — analytics is Plausible (no cookies, no personal data), Substack handles every email subscription off-site, the per-IP rate limit on the Checklist tool stores a hashed counter only. The detail is on `/privacy`.

A handful of items remain outside this rebuild and live as their own follow-ups: the Checklist tool's five-ticker manual review, the first Friday cron run on the deployed preview, and the 2026 third-party performance attestation. None of those gate the public site.

---

_The changelog is written in the principal's voice and updated when something a reader would actually care about changes. The git log records the rest._

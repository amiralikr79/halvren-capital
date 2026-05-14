# Operating Rules — 7 Sprints

These are the rules of engagement for the 48-hour autonomous build window across all seven sprints. They apply to every commit, every page, every script.

---

## 1. Decide. Log. Ship.

**Never ask clarifying questions.** Make the best call from the brand constitution, the existing codebase, and the sprint plan. If the call is non-trivial — a file structure, a library pick, a copy choice, a data source — log it in `DECISIONS.md` with the date, the alternatives considered, and the reason. Append-only. One-line summary, two-to-three-line rationale.

The principal reviews the log on day three. Not before. Do not page him for approval.

---

## 2. No TODOs in production code.

If something needs follow-up, it goes in `DECISIONS.md` under a `### Follow-ups` heading at the bottom of the file, with a date and the file path. Never:

- `// TODO: …`
- `// FIXME: …`
- `<!-- placeholder -->`
- `lorem ipsum` of any flavour
- empty `<a>` tags pointing to `#`
- "Coming soon" labels without a date

If a feature is half-built, it doesn't merge. Either finish it or revert it.

---

## 3. Build is green before commit.

Run, in this order, before every commit that touches code:

```bash
# If/when package.json gains scripts:
npm run lint       # if defined
npm run typecheck  # if defined
npm run build      # if defined

# Today the site is static HTML/CSS + Vercel functions. The minimum bar:
node --check api/**/*.js                       # syntax sanity on serverless
python3 -m py_compile scripts/*.py             # syntax sanity on build scripts
# Open the changed page in a local server and visually confirm.
```

If a check fails, fix it before pushing. **Never** push with `--no-verify` or any other hook-skip flag. If a hook fails, the hook is correct and the commit is wrong.

---

## 4. Commit message convention.

Every commit message starts with `halvren:` followed by a short, lowercase, imperative description. No emoji. No trailing punctuation.

```
halvren: lock brand constitution + sprint plan
halvren: add cco research piece, push coverage to 16
halvren: rewrite about page, tighten copy pass
```

Body (optional) gives context, references the sprint number, and lists files of interest. Never dump diff into the body.

---

## 5. Push to main on green.

After each successful build, push to `main`. If the working branch is a feature branch, fast-forward `main` to the branch tip — never force-push, never reset.

```bash
git push origin <working-branch>
git push origin <working-branch>:main
```

Network errors get four retries with exponential backoff (2s, 4s, 8s, 16s). Anything else stops the loop and goes in `DECISIONS.md` under follow-ups.

---

## 6. Brand discipline overrides taste.

`HALVREN_BRAND.md` is the constitution. If a copy choice conflicts with the brand doc, the brand doc wins. If the brand doc itself feels wrong, that goes in `DECISIONS.md` as a proposed amendment — and the existing rule still applies until the principal accepts the change.

The forbidden-phrase list is mechanical. Grep before committing copy:

```bash
git diff --cached -- '*.html' '*.md' '*.json' | \
  grep -E -i '\b(leverage|synergies|passionate|journey|ecosystem|paradigm|unlock|robust|cutting-edge|world-class|best-in-class|mission-driven|revolutionizing|in todays market|investors often wonder|its important to note)\b' \
  && echo "Forbidden phrase in staged copy" && exit 1 || true
```

---

## 7. Scope discipline.

Don't add features outside the sprint. Don't refactor adjacent files because they're nearby. A bug fix is a bug fix. A feature is a feature. Cross-cutting cleanups get their own commit, their own line in `DECISIONS.md`, and a sentence of justification.

Three similar lines beat a premature abstraction.

---

_If a rule conflicts with another rule, the earlier-numbered rule wins._

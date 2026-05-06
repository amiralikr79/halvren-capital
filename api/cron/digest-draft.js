// /api/cron/digest-draft
//
// Friday cron at 14:00 UTC (07:00 PT). Drafts the next week's digest entry
// by creating two files (data/digest/<YYYY-WW>.json + content/digest/<YYYY-WW>.md)
// in a new branch (digest-draft/<YYYY-WW>) and opening a draft PR. Does not
// auto-merge; the principal reviews + edits + merges.
//
// Counter values are placeholders calibrated to the homepage range (140s /
// 4-5K / 6-8). Real values land via the ingestion pipeline in a later sprint.
//
// Required env (Vercel project settings):
//   CRON_SECRET    Vercel sends this in the Authorization header on cron-
//                  triggered requests. The function rejects 401 if missing
//                  or mismatched.
//   GITHUB_TOKEN   PAT or fine-grained token with `contents:write` and
//                  `pull_requests:write` on amiralikr79/halvren-capital.
//   GITHUB_REPO    Optional override for the target repo. Defaults to
//                  amiralikr79/halvren-capital.
//
// If the function is invoked without env config (e.g. the user hasn't yet
// connected the integration) it returns 200 with not_configured: true so
// the deploy stays clean.

const DEFAULT_REPO = "amiralikr79/halvren-capital";
const BASE_BRANCH = "main";

export default async function handler(req, res) {
  // Vercel cron sends GET; we also allow POST for manual trigger via dashboard
  if (req.method !== "GET" && req.method !== "POST") {
    return res.status(405).json({ error: { code: "method_not_allowed", message: "Use GET or POST." } });
  }

  // CRON_SECRET auth — Vercel auto-attaches Authorization: Bearer <CRON_SECRET>
  // on cron-triggered requests. Manual dashboard "Run" button does the same.
  const auth = req.headers.authorization || "";
  const expected = process.env.CRON_SECRET ? `Bearer ${process.env.CRON_SECRET}` : null;
  if (!expected) {
    return res.status(200).json({
      not_configured: true,
      reason: "CRON_SECRET env var is not set on this deployment. Set it in Vercel project settings (Settings → Environment Variables) and re-deploy.",
    });
  }
  if (auth !== expected) {
    return res.status(401).json({ error: { code: "unauthorized", message: "Invalid or missing CRON_SECRET." } });
  }

  if (!process.env.GITHUB_TOKEN) {
    return res.status(200).json({
      not_configured: true,
      reason: "GITHUB_TOKEN env var is not set. Add a PAT or fine-grained token with contents:write + pull_requests:write on the target repo.",
    });
  }

  const repo = process.env.GITHUB_REPO || DEFAULT_REPO;
  const week = isoWeek(new Date());
  const slug = `${week.year}-W${String(week.week).padStart(2, "0")}`;
  const branch = `digest-draft/${slug}`;

  try {
    const { json, md } = buildDraftFiles(slug, week);
    const result = await openDraftPr({
      repo,
      branch,
      slug,
      json,
      md,
      token: process.env.GITHUB_TOKEN,
    });
    return res.status(200).json({
      ok: true,
      slug,
      branch,
      pr_url: result.pr_url,
      pr_number: result.pr_number,
      ...result.notes,
    });
  } catch (e) {
    return res.status(500).json({
      error: {
        code: "draft_failed",
        message: e.message,
      },
      slug,
      branch,
    });
  }
}

// ISO 8601 week number (week 1 contains Jan 4)
function isoWeek(date) {
  const d = new Date(Date.UTC(date.getUTCFullYear(), date.getUTCMonth(), date.getUTCDate()));
  const dayOfWeek = d.getUTCDay() || 7; // Mon=1 ... Sun=7
  d.setUTCDate(d.getUTCDate() + 4 - dayOfWeek); // shift to Thursday of the same week
  const yearStart = new Date(Date.UTC(d.getUTCFullYear(), 0, 1));
  const week = Math.ceil(((d - yearStart) / 86_400_000 + 1) / 7);
  return { year: d.getUTCFullYear(), week };
}

function buildDraftFiles(slug, week) {
  // The Friday immediately preceding (or equal to) today.
  const now = new Date();
  const daysSinceFriday = (now.getUTCDay() + 2) % 7; // Fri=0, Sat=1, ..., Thu=6
  const friday = new Date(Date.UTC(now.getUTCFullYear(), now.getUTCMonth(), now.getUTCDate() - daysSinceFriday));
  const monday = new Date(friday);
  monday.setUTCDate(friday.getUTCDate() - 4);
  const fmt = (d) => d.toLocaleString("en-US", { month: "short", day: "numeric", timeZone: "UTC" });
  const labelDates = `${fmt(monday)} – ${fmt(friday)}, ${friday.getUTCFullYear()}`;
  const weekLabel = `Week ${week.week} · ${labelDates}`;

  const data = {
    $comment: "Auto-drafted by /api/cron/digest-draft. Counter values are placeholders calibrated to the homepage range. Replace with real ingestion data before merging.",
    week_of: friday.toISOString().slice(0, 10),
    week_iso: slug,
    week_label: weekLabel,
    week_label_short: `Week ${week.week} · ${friday.getUTCFullYear()}`,
    updated_iso: friday.toISOString().replace(/\.\d{3}Z$/, "-07:00"),
    updated_human: fmt(friday) + `, ${friday.getUTCFullYear()}`,
    backfilled: false,
    filings_ingested: 142,
    pages_read: 4820,
    audio_hours: 7.0,
    stats: {
      filings_ingested: 142,
      filings_breakdown: "transcripts · 10-Q · 8-K · SEDI/Form 4",
      pages_read: 4820,
      pages_breakdown: "incl. 7.0 hrs of call audio",
      checklist_evaluated: 70,
      checklist_breakdown: "10 questions · 7 calls",
      model_flags: 0,
      promoted_to_desk: 0,
      filter_pct: 80,
    },
    model_flags: [],
    promoted_to_desk: [],
    next_week: [],
  };

  const json = JSON.stringify(data, null, 2) + "\n";
  const md =
    `_PRINCIPAL: write the week's intro line in italics here._\n` +
    `\n` +
    `<!-- Auto-drafted by /api/cron/digest-draft. Replace counters and arrays with real values, then write the principal note above. -->\n`;

  return { json, md };
}

// ---------------------------------------------------------------------------
// GitHub REST helpers — minimal, no external deps
// ---------------------------------------------------------------------------

async function gh(token, method, path, body) {
  const r = await fetch(`https://api.github.com${path}`, {
    method,
    headers: {
      Authorization: `Bearer ${token}`,
      Accept: "application/vnd.github+json",
      "X-GitHub-Api-Version": "2022-11-28",
      "Content-Type": "application/json",
      "User-Agent": "halvren-capital-digest-cron",
    },
    body: body ? JSON.stringify(body) : undefined,
  });
  const text = await r.text();
  let data;
  try { data = text ? JSON.parse(text) : {}; }
  catch { data = { _raw: text }; }
  if (!r.ok) {
    const msg = data.message ? `${r.status} ${data.message}` : `${r.status} ${text.slice(0, 200)}`;
    const err = new Error(`github ${method} ${path}: ${msg}`);
    err.status = r.status;
    err.body = data;
    throw err;
  }
  return data;
}

async function openDraftPr({ repo, branch, slug, json, md, token }) {
  const notes = {};

  // 1. Get the SHA of BASE_BRANCH so we can branch off it
  const baseRef = await gh(token, "GET", `/repos/${repo}/git/ref/heads/${BASE_BRANCH}`);
  const baseSha = baseRef.object.sha;

  // 2. Create the new branch — tolerate "already exists" so re-runs don't 422
  try {
    await gh(token, "POST", `/repos/${repo}/git/refs`, {
      ref: `refs/heads/${branch}`,
      sha: baseSha,
    });
  } catch (e) {
    if (e.status !== 422) throw e;
    notes.branch_existed = true;
  }

  // 3. Create or update the JSON + MD files on the new branch
  const dataPath = `data/digest/${slug}.json`;
  const bodyPath = `content/digest/${slug}.md`;
  await putFile(token, repo, branch, dataPath, json, `chore(digest): draft ${slug} JSON snapshot`);
  await putFile(token, repo, branch, bodyPath, md,   `chore(digest): draft ${slug} body MD`);

  // 4. Open the draft PR — tolerate "already exists" so re-runs return the live PR
  let pr;
  try {
    pr = await gh(token, "POST", `/repos/${repo}/pulls`, {
      title: `chore(digest): draft for ${slug}`,
      head: branch,
      base: BASE_BRANCH,
      draft: true,
      body: [
        `_Auto-drafted by \`/api/cron/digest-draft\` on Friday cron._`,
        ``,
        `### What's here`,
        `- \`${dataPath}\` — JSON snapshot with placeholder counters (140s / 4-5K / 6-8).`,
        `- \`${bodyPath}\` — empty body with a \`PRINCIPAL: write\` placeholder.`,
        ``,
        `### What to do before merging`,
        `1. Replace the placeholder \`stats\` and arrays in the JSON with the week's real ingestion numbers.`,
        `2. Write the principal note in the body MD (italic intro + short prose).`,
        `3. Convert this PR out of draft, then merge.`,
        ``,
        `On merge, \`scripts/build_digest_archive.py\` regenerates \`/digest\` and \`/digest/latest.json\`. The homepage counters hydrate from the latter.`,
      ].join("\n"),
    });
  } catch (e) {
    if (e.status === 422) {
      const existing = await gh(token, "GET", `/repos/${repo}/pulls?state=open&head=${encodeURIComponent(repo.split("/")[0] + ":" + branch)}`);
      if (Array.isArray(existing) && existing.length) {
        pr = existing[0];
        notes.pr_existed = true;
      } else {
        throw e;
      }
    } else {
      throw e;
    }
  }

  return { pr_url: pr.html_url, pr_number: pr.number, notes };
}

async function putFile(token, repo, branch, path, content, message) {
  // need the existing SHA if the file already exists on the branch
  let sha;
  try {
    const existing = await gh(token, "GET", `/repos/${repo}/contents/${path}?ref=${encodeURIComponent(branch)}`);
    sha = existing.sha;
  } catch (e) {
    if (e.status !== 404) throw e;
  }
  await gh(token, "PUT", `/repos/${repo}/contents/${path}`, {
    message,
    branch,
    content: Buffer.from(content, "utf-8").toString("base64"),
    sha,
  });
}

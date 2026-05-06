// /api/version
//
// Renders /version: the current deployment SHA, deploy timestamp, and the
// principal-voice changelog from /content/changelog.md. Vercel rewrites
// /version to this function (see vercel.json).
//
// Read-only, no auth, no secrets. Cache 5 min at the edge so a flood of
// hits doesn't spin the function up unnecessarily.

import { readFileSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const HERE = dirname(fileURLToPath(import.meta.url));
const ROOT = join(HERE, "..");

let CHANGELOG_CACHE = null;
let SITE_META_CACHE = null;

function loadChangelog() {
  if (CHANGELOG_CACHE) return CHANGELOG_CACHE;
  try {
    CHANGELOG_CACHE = readFileSync(join(ROOT, "content", "changelog.md"), "utf-8");
  } catch {
    CHANGELOG_CACHE = "_Changelog not yet authored._";
  }
  return CHANGELOG_CACHE;
}

function loadSiteMeta() {
  if (SITE_META_CACHE) return SITE_META_CACHE;
  try {
    SITE_META_CACHE = JSON.parse(readFileSync(join(ROOT, "content", "site-meta.json"), "utf-8"));
  } catch {
    SITE_META_CACHE = {};
  }
  return SITE_META_CACHE;
}

function escapeHtml(s) {
  return String(s == null ? "" : s)
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;");
}

// minimal markdown -> HTML — same subset as scripts/build_operators.py
function renderMd(src) {
  const lines = src.replace(/\r\n/g, "\n").split("\n");
  const normalized = [];
  for (const ln of lines) {
    const stripped = ln.trimStart();
    const isBlock = stripped.startsWith("## ") || stripped.startsWith("### ") || stripped.startsWith("> ") || stripped.startsWith("- ");
    if (isBlock && normalized.length && normalized[normalized.length - 1].trim() !== "") {
      normalized.push("");
    }
    normalized.push(ln);
  }
  const final = [];
  for (let i = 0; i < normalized.length; i++) {
    final.push(normalized[i]);
    const isHeading = normalized[i].trimStart().startsWith("## ") || normalized[i].trimStart().startsWith("### ");
    const next = normalized[i + 1] || "";
    if (isHeading && next.trim() && !next.trimStart().match(/^(##|###|>|-)\s/)) {
      final.push("");
    }
  }
  const src2 = final.join("\n");

  const out = [];
  let pendingList = [];
  const flush = () => {
    if (pendingList.length) {
      out.push('<ul class="doc-ul">');
      for (const li of pendingList) out.push(`  <li>${inline(li.trim())}</li>`);
      out.push("</ul>");
      pendingList = [];
    }
  };
  const blocks = src2.trim().split(/\n\s*\n/);
  for (const raw of blocks) {
    const block = raw.replace(/\s+$/, "");
    if (!block) continue;
    const blockLines = block.split("\n");
    if (blockLines.every((l) => l.trimStart().startsWith("- "))) {
      for (const l of blockLines) pendingList.push(l.trimStart().slice(2));
      continue;
    }
    flush();
    if (block.startsWith("# "))   { out.push(`<h1 class="doc-h1">${inline(block.slice(2).trim())}</h1>`); continue; }
    if (block.startsWith("## "))  { out.push(`<h2 class="doc-h2">${inline(block.slice(3).trim())}</h2>`); continue; }
    if (block.startsWith("### ")) { out.push(`<h3 class="doc-h3">${inline(block.slice(4).trim())}</h3>`); continue; }
    if (block === "---")          { out.push('<hr class="doc-divider">'); continue; }
    if (block.startsWith("> ")) {
      const t = blockLines.map((l) => l.replace(/^>\s?/, "").trimEnd()).join(" ");
      out.push(`<p class="doc-pullquote">${inline(t)}</p>`);
      continue;
    }
    const t = blockLines.map((l) => l.trim()).join(" ");
    if (t.startsWith("_") && t.endsWith("_") && t.split("_").length === 3) {
      out.push(`<p class="doc-p doc-p--italic"><em>${inline(t.slice(1, -1))}</em></p>`);
    } else {
      out.push(`<p class="doc-p">${inline(t)}</p>`);
    }
  }
  flush();
  return out.join("\n");
}

function inline(s) {
  // very minimal: backticks → <code>, **bold** → <strong>, [text](url) → <a>
  // (intentionally narrow — the changelog uses these and nothing else)
  s = s.replace(/`([^`]+)`/g, "<code>$1</code>");
  s = s.replace(/\*\*([^*]+)\*\*/g, "<strong>$1</strong>");
  s = s.replace(/\[([^\]]+)\]\(([^)]+)\)/g, '<a href="$2">$1</a>');
  return s;
}

export default function handler(req, res) {
  const sha = process.env.VERCEL_GIT_COMMIT_SHA || "(no SHA — running outside Vercel)";
  const shortSha = sha.length > 7 ? sha.slice(0, 7) : sha;
  const branch = process.env.VERCEL_GIT_COMMIT_REF || "(unknown branch)";
  const commitMsg = process.env.VERCEL_GIT_COMMIT_MESSAGE || "";
  const repoSlug = process.env.VERCEL_GIT_REPO_SLUG || "halvren-capital";
  const repoOwner = process.env.VERCEL_GIT_REPO_OWNER || "amiralikr79";
  const env = process.env.VERCEL_ENV || "(unknown)";
  const region = process.env.VERCEL_REGION || "(unknown)";
  const renderedAt = new Date().toISOString();
  const meta = loadSiteMeta();
  const changelog = renderMd(loadChangelog());

  const commitUrl = sha.match(/^[0-9a-f]{40}$/)
    ? `https://github.com/${repoOwner}/${repoSlug}/commit/${sha}`
    : null;

  const html = `<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0, viewport-fit=cover">
<title>Version — Halvren Capital</title>
<meta name="description" content="Current deployment SHA, deploy timestamp, and reader-facing changelog for halvrencapital.com.">
<meta name="theme-color" content="#111010" media="(prefers-color-scheme: dark)">
<meta name="theme-color" content="#f7f6f2" media="(prefers-color-scheme: light)">
<meta name="color-scheme" content="dark light">
<script>(function(){try{var s=localStorage.getItem('halvren-theme');var p=window.matchMedia('(prefers-color-scheme: light)').matches?'light':'dark';document.documentElement.setAttribute('data-theme',s||p);}catch(e){document.documentElement.setAttribute('data-theme','dark');}})();</script>
<link rel="canonical" href="https://halvrencapital.com/version">
<meta name="robots" content="noindex,follow">
<link rel="icon" type="image/svg+xml" href="data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 32 32'><rect width='32' height='32' rx='6' fill='%23111010'/><path d='M7 8 L7 24 M7 16 L15 16 M15 8 L15 24' stroke='%23e8e6e2' stroke-width='2.5' stroke-linecap='round' stroke-linejoin='round' fill='none'/><path d='M19 8 L19 24 M19 8 L26 16 L19 24' stroke='%23c9a84c' stroke-width='2.5' stroke-linecap='round' stroke-linejoin='round' fill='none'/></svg>">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Instrument+Serif:ital@0;1&family=DM+Sans:wght@300;400;500&family=JetBrains+Mono:wght@400;500&display=swap" rel="stylesheet">
<link rel="stylesheet" href="/page.css">
</head>
<body>
<a href="#main" class="skip-link">Skip to content</a>
<nav>
  <a href="/" class="nav-logo" aria-label="Halvren Capital — home">
    <svg class="nav-logo-mark" viewBox="0 0 32 32" fill="none" aria-hidden="true">
      <rect width="32" height="32" rx="4" fill="none"/>
      <path d="M6 6 L6 26 M6 16 L16 16 M16 6 L16 26" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"/>
      <path d="M20 6 L20 26 M20 6 L28 16 L20 26" stroke="var(--color-gold)" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"/>
    </svg>
    <span class="nav-logo-name">Halvren Capital</span>
  </a>
  <div class="nav-links" id="nav-links" data-open="false">
    <a href="/research">Research</a>
    <a href="/letters">Letters</a>
    <a href="/process">Process</a>
    <a href="/access">Access</a>
    <a href="/about">About</a>
  </div>
  <div class="nav-right">
    <a href="/" class="nav-back">Back to home</a>
    <button class="theme-toggle" data-theme-toggle aria-label="Toggle theme" type="button">
      <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"/></svg>
    </button>
    <button class="nav-toggle" data-nav-toggle aria-label="Open menu" aria-controls="nav-links" aria-expanded="false" type="button">
      <span class="nav-toggle-open"><svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><path d="M4 7h16M4 12h16M4 17h16"/></svg></span>
      <span class="nav-toggle-close"><svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><path d="M6 6 L18 18 M18 6 L6 18"/></svg></span>
    </button>
  </div>
</nav>

<main id="main" class="doc-main">
  <article class="doc-article">
    <p class="doc-breadcrumb"><a href="/">Home</a><span class="doc-breadcrumb-sep">/</span><span>Version</span></p>
    <p class="section-label">Build provenance</p>
    <h1 class="doc-h1">What's deployed, <em>right now.</em></h1>
    <p class="doc-p" style="max-width:64ch">A small page so anyone can confirm what's actually live, when it was deployed, and what changed in this build. The reader-facing changelog is below; the git log lives <a href="https://github.com/${escapeHtml(repoOwner)}/${escapeHtml(repoSlug)}" target="_blank" rel="noopener noreferrer">on GitHub</a>.</p>

    <dl class="version-stat">
      <div><dt>Commit</dt><dd>${commitUrl ? `<a href="${escapeHtml(commitUrl)}" target="_blank" rel="noopener noreferrer"><code>${escapeHtml(shortSha)}</code></a>` : `<code>${escapeHtml(shortSha)}</code>`}</dd></div>
      <div><dt>Branch</dt><dd><code>${escapeHtml(branch)}</code></dd></div>
      <div><dt>Environment</dt><dd><code>${escapeHtml(env)}</code></dd></div>
      <div><dt>Region</dt><dd><code>${escapeHtml(region)}</code></dd></div>
      <div><dt>Rendered</dt><dd>${escapeHtml(renderedAt)}</dd></div>
      <div><dt>Last full-site review</dt><dd>${escapeHtml(meta.last_full_site_review_human || meta.last_full_site_review || "—")}</dd></div>
      ${commitMsg ? `<div><dt>Last commit</dt><dd style="font-family:var(--font-mono);font-size:11px">${escapeHtml(commitMsg.split("\n")[0].slice(0, 200))}</dd></div>` : ""}
    </dl>

    <hr class="doc-divider">

    <section aria-labelledby="changelog-h">
      <h2 class="doc-h2" id="changelog-h">Changelog</h2>
      ${changelog}
    </section>

    <p style="margin-top:var(--space-12);font-size:var(--text-sm);color:var(--color-text-faint);max-width:64ch;line-height:1.7">
      <strong>About this page.</strong> Rendered by <code>/api/version</code> at request time using the Vercel build environment. SHA is the current production deployment's git commit; rendered timestamp is when this exact response was generated. The page is <code>noindex</code> — it's a debugging surface, not content for crawlers. The changelog above lives at <a href="https://github.com/${escapeHtml(repoOwner)}/${escapeHtml(repoSlug)}/blob/main/content/changelog.md" target="_blank" rel="noopener noreferrer"><code>content/changelog.md</code></a> and is written in the principal's voice.
    </p>
  </article>
</main>

<footer>
  <div class="footer-trust">
    <span class="footer-trust-item">Canadian &amp; U.S. markets</span>
    <span class="footer-trust-sep">&middot;</span>
    <span class="footer-trust-item">AI-augmented &middot; human-reviewed</span>
    <span class="footer-trust-sep">&middot;</span>
    <span class="footer-trust-item">Proprietary capital</span>
    <span class="footer-trust-sep">&middot;</span>
    <span class="footer-trust-item">Public research is free</span>
  </div>
  <div class="footer-inner">
    <div class="footer-brand">Halvren Capital<span>Vancouver, BC &middot; Est. 2025</span></div>
    <div class="footer-disclaimer">
      <p>Halvren Capital publishes research and commentary for informational and educational purposes only. Nothing on this site constitutes an offer, solicitation, or recommendation to buy or sell any security.</p>
    </div>
  </div>
  <div class="footer-inner footer-meta">
    <span>&copy; 2025–2026 Halvren Capital. All rights reserved.</span>
    <span><a href="/">Home</a> &middot; <a href="/research">Research</a> &middot; <a href="/coverage">Coverage</a> &middot; <a href="/digest">Digest</a> &middot; <a href="/checklist">Checklist</a> &middot; <a href="/letters">Letters</a> &middot; <a href="/about">About</a> &middot; <a href="/privacy">Privacy</a> &middot; <a href="/terms">Terms</a> &middot; <a href="/version" aria-current="page">Version</a></span>
  </div>
</footer>
<script src="/nav.js" defer></script>
</body>
</html>
`;

  res.setHeader("Content-Type", "text/html; charset=utf-8");
  res.setHeader("Cache-Control", "public, s-maxage=300, stale-while-revalidate=3600");
  res.setHeader("X-Robots-Tag", "noindex, follow");
  res.status(200).send(html);
}

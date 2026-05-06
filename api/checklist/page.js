// /api/checklist/page?ticker=CCO  →  served at /checklist/score/<ticker>
//
// Returns the result page HTML with per-ticker OG meta baked in so social
// crawlers see the right preview. The page itself loads /api/checklist/score
// client-side and renders the response. If the ticker is on coverage, it also
// fetches /data/operators/<slug>.json to render the principal's column for
// the side-by-side "Two voices on the same name" view.

import { Redis } from "@upstash/redis";

const TICKER_RE = /^[A-Z][A-Z0-9.\-]{0,9}$/;

let REDIS_SINGLETON = null;
function redis() {
  if (REDIS_SINGLETON) return REDIS_SINGLETON;
  if (!process.env.UPSTASH_REDIS_REST_URL || !process.env.UPSTASH_REDIS_REST_TOKEN) {
    return null;
  }
  REDIS_SINGLETON = Redis.fromEnv();
  return REDIS_SINGLETON;
}

function cacheKey(ticker) {
  const d = new Date();
  const ym = `${d.getUTCFullYear()}-${String(d.getUTCMonth() + 1).padStart(2, "0")}`;
  return `cscore:${ticker}:${ym}`;
}

function escapeHtml(s) {
  return String(s == null ? "" : s)
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;");
}

export default async function handler(req, res) {
  const tickerRaw = String(req.query?.ticker || "").toUpperCase();
  const ticker = TICKER_RE.test(tickerRaw) ? tickerRaw : null;

  // try cache for a precomputed pass count to power the OG image preview;
  // not blocking — if Redis is down we fall through with `?pass=` unset.
  let passCount = null;
  if (ticker) {
    const r = redis();
    if (r) {
      try {
        const hit = await r.get(cacheKey(ticker));
        if (hit) {
          const cached = typeof hit === "string" ? JSON.parse(hit) : hit;
          if (typeof cached.pass_count === "number") passCount = cached.pass_count;
        }
      } catch { /* swallow — the page still works without it */ }
    }
  }

  const ogQuery = ticker
    ? `?ticker=${encodeURIComponent(ticker)}${passCount != null ? `&pass=${passCount}` : ""}`
    : "";
  const ogImage = `https://halvrencapital.com/api/checklist/og${ogQuery}`;
  const canonical = ticker
    ? `https://halvrencapital.com/checklist/score/${encodeURIComponent(ticker)}`
    : `https://halvrencapital.com/checklist/score`;
  const titleSuffix = ticker
    ? `${ticker} on the Halvren Checklist`
    : "Halvren Checklist score";

  const html = renderPage({
    ticker,
    titleSuffix: escapeHtml(titleSuffix),
    canonical: escapeHtml(canonical),
    ogImage: escapeHtml(ogImage),
  });

  res.setHeader("Content-Type", "text/html; charset=utf-8");
  res.setHeader("Cache-Control", "public, s-maxage=60, stale-while-revalidate=600");
  res.status(200).send(html);
}

function renderPage({ ticker, titleSuffix, canonical, ogImage }) {
  const tickerLiteral = ticker ? `"${ticker}"` : "null";
  return `<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0, viewport-fit=cover">
<title>${titleSuffix} | Halvren Capital</title>
<meta name="description" content="Live machine read of one operator against the ten Halvren Checklist questions. Cited public filings only. Not principal-reviewed.">
<meta name="theme-color" content="#111010" media="(prefers-color-scheme: dark)">
<meta name="theme-color" content="#f7f6f2" media="(prefers-color-scheme: light)">
<meta name="color-scheme" content="dark light">
<script>(function(){try{var s=localStorage.getItem('halvren-theme');var p=window.matchMedia('(prefers-color-scheme: light)').matches?'light':'dark';document.documentElement.setAttribute('data-theme',s||p);}catch(e){document.documentElement.setAttribute('data-theme','dark');}})();</script>
<link rel="canonical" href="${canonical}">
<meta property="og:type" content="article">
<meta property="og:title" content="${titleSuffix} | Halvren Capital">
<meta property="og:description" content="Live machine read against the Halvren Checklist. Cited public filings only. Not principal-reviewed.">
<meta property="og:url" content="${canonical}">
<meta property="og:image" content="${ogImage}">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:image" content="${ogImage}">
<meta name="robots" content="noindex,follow">
<link rel="icon" type="image/svg+xml" href="data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 32 32'><rect width='32' height='32' rx='6' fill='%23111010'/><path d='M7 8 L7 24 M7 16 L15 16 M15 8 L15 24' stroke='%23e8e6e2' stroke-width='2.5' stroke-linecap='round' stroke-linejoin='round' fill='none'/><path d='M19 8 L19 24 M19 8 L26 16 L19 24' stroke='%23c9a84c' stroke-width='2.5' stroke-linecap='round' stroke-linejoin='round' fill='none'/></svg>">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Instrument+Serif:ital@0;1&family=DM+Sans:wght@300;400;500&family=JetBrains+Mono:wght@400;500&display=swap" rel="stylesheet">
<link rel="stylesheet" href="/page.css">
</head>
<body>
<div class="progress-bar" aria-hidden="true"><div class="progress-bar-fill"></div></div>
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
    <a href="/checklist" class="nav-back">Back to the Checklist</a>
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
  <article class="doc-article" data-checklist-result>
    <p class="doc-breadcrumb"><a href="/">Home</a><span class="doc-breadcrumb-sep">/</span><a href="/checklist">Checklist</a><span class="doc-breadcrumb-sep">/</span><span data-slot="ticker-crumb">Score</span></p>
    <p class="section-label">Live machine read</p>
    <h1 class="doc-h1" data-slot="headline">Scoring <em data-slot="ticker">…</em></h1>

    <div class="cscore-header" data-slot="header" hidden>
      <div class="cscore-header-row">
        <span class="cscore-header-tkr" data-slot="ticker-mono"></span>
        <span class="op-header-sep">·</span>
        <span class="cscore-header-listing" data-slot="exchange"></span>
        <span class="op-header-sep">·</span>
        <span class="cscore-header-meta" data-slot="generated-at"></span>
        <span class="op-header-sep">·</span>
        <span class="cscore-header-pass" data-slot="pass-count"></span>
      </div>
      <div class="cscore-header-row" data-slot="watermark-row">
        <span class="cscore-watermark" data-slot="watermark">Machine read. Not principal-reviewed.</span>
      </div>
    </div>

    <p class="doc-p cscore-status" data-slot="status">Reading filings via web search…</p>

    <section class="cscore-twovoices" data-slot="twovoices" hidden>
      <h2 class="doc-h2">Two voices on the same name.</h2>
      <p class="doc-p" style="max-width:64ch">The principal's quarterly read of this operator sits next to a live machine read of the same questions. Neither is the other; both are the work.</p>
    </section>

    <section class="cscore-grid" data-slot="grid" hidden>
      <!-- machine and principal columns rendered by JS into [data-slot="machine-col"] and [data-slot="principal-col"] -->
    </section>

    <section class="cscore-share" data-slot="share" hidden>
      <h2 class="doc-h2">Share this read</h2>
      <div class="cscore-share-row">
        <button type="button" class="cscore-share-btn" data-share="copy">Copy link</button>
        <a class="cscore-share-btn" data-share="x" target="_blank" rel="noopener noreferrer">Share on X</a>
        <a class="cscore-share-btn" data-share="linkedin" target="_blank" rel="noopener noreferrer">Share on LinkedIn</a>
      </div>
    </section>

    <section class="subscribe" id="subscribe" hidden data-slot="subscribe-block">
      <p class="subscribe-eyebrow">When this lands on coverage</p>
      <h2 class="subscribe-h">Want the <em>principal-reviewed</em> version when this name earns the writeup?</h2>
      <p class="subscribe-p">Halvren publishes one quarterly letter and a small, irregular cadence of single-name research. Subscribe on Substack — emails are not collected on this page.</p>
      <p class="subscribe-meta"><a href="https://substack.com/@halvrencapital" target="_blank" rel="noopener noreferrer">Subscribe on Substack →</a></p>
    </section>

    <p class="doc-p" style="font-size:var(--text-sm);color:var(--color-text-faint);margin-top:var(--space-12)" data-slot="footnote">
      <strong>Method.</strong> The ten checklist questions live in <a href="/checklist">/checklist</a>. The machine read uses Claude Sonnet 4.6 with web search restricted to public filings (SEDAR+, EDGAR, IR pages). It returns a citation per answer and defaults to <em>not yet</em> when a claim cannot be verified from filings within the call. Output is cached per ticker per month and is not investment advice. See the <a href="/terms">Terms of Use</a>.
    </p>
  </article>
</main>

<footer>
  <div class="footer-trust">
    <span class="footer-trust-item">Canadian &amp; U.S. markets</span>
    <span class="footer-trust-sep">·</span>
    <span class="footer-trust-item">AI-augmented · human-reviewed</span>
    <span class="footer-trust-sep">·</span>
    <span class="footer-trust-item">Proprietary capital</span>
    <span class="footer-trust-sep">·</span>
    <span class="footer-trust-item">Public research is free</span>
  </div>
  <div class="footer-inner">
    <div class="footer-brand">Halvren Capital<span>Vancouver, BC · Est. 2025</span></div>
    <div class="footer-disclaimer">
      <p>Halvren Capital publishes research and commentary for informational and educational purposes only. Nothing on this site constitutes an offer, solicitation, or recommendation to buy or sell any security.</p>
      <p>Halvren manages proprietary capital and is not a registered investment adviser, broker-dealer, or portfolio manager. The author may hold positions in securities discussed and may transact in them at any time without notice.</p>
    </div>
  </div>
  <div class="footer-inner footer-meta">
    <span>&copy; 2025–2026 Halvren Capital. All rights reserved.</span>
    <span><a href="/">Home</a> · <a href="/research">Research</a> · <a href="/coverage">Coverage</a> · <a href="/checklist">Checklist</a> · <a href="/letters">Letters</a> · <a href="/process">Process</a> · <a href="/access">Access</a> · <a href="/about">About</a> · <a href="/privacy">Privacy</a> · <a href="/terms">Terms</a></span>
  </div>
</footer>

<script>window.__HALVREN_TICKER__ = ${tickerLiteral};</script>
<script src="/checklist/score/result.js" defer></script>
<script src="/nav.js" defer></script>
</body>
</html>
`;
}

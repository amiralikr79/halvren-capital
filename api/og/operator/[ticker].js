// /api/og/operator/[ticker]
//
// Halvren Read trading card — 1200x630 PNG for an operator in coverage.
// The PNG renders the Halvren wordmark, ticker, the Halvren Read number
// (color-coded by band), operator name + sector, a 5x2 grid of verdict
// chips for the 10 checklist questions, and a one-sentence summary.
//
// Light mode by default. Pass ?dark=1 for the dark variant.
//
// Cached aggressively at the edge.

import { ImageResponse } from "@vercel/og";

export const config = { runtime: "edge" };

// brand tokens
const TOKENS = {
  light: { bg: "#f7f6f2", ink: "#1a1814", muted: "#6b6a66", line: "#d4d1ca", gold: "#b8860b", green: "#22c55e", red: "#b94747" },
  dark:  { bg: "#0d0c0a", ink: "#ece8df", muted: "#8a8780", line: "#2a2823", gold: "#bf9c5b", green: "#22c55e", red: "#d96b6b" },
};

const CORMORANT_600 = "https://fonts.gstatic.com/s/cormorantgaramond/v16/co3YmX5slCNuHLi8bLeY9MK7whWMhyjornFLsS6V7w.ttf";
const CORMORANT_500I = "https://fonts.gstatic.com/s/cormorantgaramond/v16/co3WmX5slCNuHLi8bLeY8KO7uxe1eFRr2v0.ttf";
const DMSANS_500 = "https://fonts.gstatic.com/s/dmsans/v15/rP2tp2ywxg089UriI5-g7vN_lwgZhbA.ttf";
const JETBRAINS_500 = "https://fonts.gstatic.com/s/jetbrainsmono/v18/tDbY2o-flEEny0FZhsfKu5WU4zr3E_BX0PnT8RD8yKxjPVmUsaaDhw.ttf";

let CACHE = { corm: null, cormi: null, sans: null, mono: null };

async function loadFont(url) {
  const res = await fetch(url, { cache: "force-cache" });
  if (!res.ok) throw new Error(`font fetch failed: ${url}`);
  return res.arrayBuffer();
}

function h(type, props, ...children) {
  const kids = children.flat().filter((c) => c !== null && c !== undefined && c !== false);
  return { type, props: { ...(props || {}), children: kids.length === 1 ? kids[0] : kids } };
}

const PILLAR_RANGES = [
  ["I", [1, 2, 3, 4], 40],
  ["II", [5, 6, 7, 8], 30],
  ["III", [9, 10], 30],
];
const PTS = { pass: 10, not_yet: 5, fail: 0 };

function computeRead(scoring) {
  const by = {};
  scoring.forEach((s) => { by[s.q] = s.status; });
  let total = 0;
  for (const [, qs, cap] of PILLAR_RANGES) {
    const raw = qs.reduce((a, q) => a + (PTS[by[q]] || 0), 0);
    const max = 10 * qs.length;
    total += (raw / max) * cap;
  }
  return Math.max(0, Math.min(100, Math.round(total)));
}

function band(score, t) {
  if (score == null) return t.muted;
  if (score >= 75) return t.green;
  if (score >= 50) return t.gold;
  return t.red;
}

// Q-shorthand labels (5x2 grid) — mirror the brief
const Q_SHORT = {
  1: "FCF cycle",
  2: "Trough econ",
  3: "Trough BS",
  4: "ROIC",
  5: "Insider buys",
  6: "2015-20 record",
  7: "Comp",
  8: "Succession",
  9: "Cost curve",
  10: "Decade test",
};

async function fetchOperator(origin, ticker) {
  // /data/operators/<slug>.json — the slug isn't the ticker, so we fall
  // through /data/viz-data.json to map ticker → slug + grab numbers.
  const tkr = String(ticker || "").toUpperCase();
  const viz = await fetch(`${origin}/data/viz-data.json`, { cache: "force-cache" }).then((r) => r.json());
  const row = (viz.operators || []).find((o) => o.ticker.toUpperCase() === tkr);
  if (!row) return null;
  const op = await fetch(`${origin}/data/operators/${row.slug}.json`, { cache: "force-cache" }).then((r) => r.json());
  return { row, op };
}

function clamp(s, n) {
  if (!s) return "";
  return s.length > n ? s.slice(0, n - 1).trimEnd() + "…" : s;
}

export default async function handler(req) {
  try {
    const url = new URL(req.url);
    const parts = url.pathname.split("/").filter(Boolean); // [api, og, operator, <ticker>]
    const ticker = (parts[parts.length - 1] || "").toUpperCase();
    const dark = url.searchParams.get("dark") === "1";
    const t = dark ? TOKENS.dark : TOKENS.light;
    const origin = url.origin;

    if (!CACHE.corm)  CACHE.corm  = await loadFont(CORMORANT_600);
    if (!CACHE.cormi) CACHE.cormi = await loadFont(CORMORANT_500I);
    if (!CACHE.sans)  CACHE.sans  = await loadFont(DMSANS_500);
    if (!CACHE.mono)  CACHE.mono  = await loadFont(JETBRAINS_500);

    const opData = await fetchOperator(origin, ticker);
    if (!opData) {
      // Render an honest fallback
      return new ImageResponse(
        h("div", { style: { width: "100%", height: "100%", background: t.bg, color: t.ink, display: "flex", alignItems: "center", justifyContent: "center", fontFamily: "Cormorant", fontSize: 64 } }, "Not in coverage."),
        { width: 1200, height: 630, fonts: [{ name: "Cormorant", data: CACHE.corm, weight: 600, style: "normal" }] }
      );
    }

    const { row, op } = opData;
    const scoring = (op.checklist && op.checklist.scoring) || [];
    const score = op.halvren_read != null ? op.halvren_read : computeRead(scoring);
    const summary = (op.the_read && op.the_read.summary) || "";

    // 10 chips — 5 cols × 2 rows
    const chipsRow1 = [1,2,3,4,5].map((q) => buildChip(q, scoring, t));
    const chipsRow2 = [6,7,8,9,10].map((q) => buildChip(q, scoring, t));

    const mark = h("svg", { width: 28, height: 28, viewBox: "0 0 32 32", fill: "none", style: { display: "block" } },
      h("path", { d: "M6 6 L6 26 M6 16 L16 16 M16 6 L16 26", stroke: t.ink, strokeWidth: 2.5, strokeLinecap: "round", strokeLinejoin: "round" }),
      h("path", { d: "M20 6 L20 26 M20 6 L28 16 L20 26", stroke: t.gold, strokeWidth: 2.5, strokeLinecap: "round", strokeLinejoin: "round" }),
    );

    const tree = h("div", {
        style: { width: "100%", height: "100%", display: "flex", flexDirection: "column", justifyContent: "space-between", backgroundColor: t.bg, padding: "56px 72px", fontFamily: "DM Sans", color: t.ink },
      },
      // Top row: wordmark left, ticker + exchange right
      h("div", { style: { display: "flex", alignItems: "center", justifyContent: "space-between" } },
        h("div", { style: { display: "flex", alignItems: "center", gap: "12px" } },
          mark,
          h("div", { style: { display: "flex", fontFamily: "Cormorant", fontSize: 32, color: t.ink, fontWeight: 600, letterSpacing: "-0.01em" } }, "Halvren Capital"),
        ),
        h("div", { style: { display: "flex", flexDirection: "column", alignItems: "flex-end", gap: 4 } },
          h("div", { style: { display: "flex", fontFamily: "JetBrains Mono", fontSize: 24, color: t.gold, letterSpacing: "0.04em" } }, row.ticker),
          h("div", { style: { display: "flex", fontFamily: "DM Sans", fontSize: 13, color: t.muted, letterSpacing: "0.08em", textTransform: "uppercase" } }, row.exchange || ""),
        ),
      ),
      // Center: HALVREN READ number + sub
      h("div", { style: { display: "flex", flexDirection: "column", alignItems: "center", gap: 8, marginTop: 8 } },
        h("div", { style: { display: "flex", fontFamily: "DM Sans", fontSize: 14, color: t.gold, letterSpacing: "0.18em", textTransform: "uppercase" } }, "Halvren Read"),
        h("div", { style: { display: "flex", fontFamily: "Cormorant", fontSize: 220, lineHeight: 0.95, color: band(score, t), fontWeight: 600, letterSpacing: "-0.04em" } }, String(score)),
        h("div", { style: { display: "flex", fontFamily: "DM Sans", fontSize: 16, color: t.muted, letterSpacing: "0.06em" } }, score + " / 100"),
        h("div", { style: { display: "flex", fontFamily: "Cormorant", fontSize: 32, color: t.ink, marginTop: 14, letterSpacing: "-0.01em" } }, clamp(op.short_name + " — " + (op.sub_industry || op.sector), 64)),
      ),
      // 5x2 chip grid
      h("div", { style: { display: "flex", flexDirection: "column", gap: 8 } },
        h("div", { style: { display: "flex", gap: 8, justifyContent: "center" } }, chipsRow1),
        h("div", { style: { display: "flex", gap: 8, justifyContent: "center" } }, chipsRow2),
      ),
      // Footer: italic summary clip + URL right
      h("div", { style: { display: "flex", alignItems: "flex-end", justifyContent: "space-between", borderTop: `1px solid ${t.line}`, paddingTop: 14, gap: 24 } },
        h("div", { style: { display: "flex", fontFamily: "Cormorant", fontSize: 18, fontStyle: "italic", color: t.muted, maxWidth: 780, lineHeight: 1.35 } }, clamp(summary, 180)),
        h("div", { style: { display: "flex", fontFamily: "DM Sans", fontSize: 12, color: t.muted, letterSpacing: "0.12em", textTransform: "uppercase" } }, "halvrencapital.com/research/" + row.slug),
      ),
    );

    return new ImageResponse(tree, {
      width: 1200, height: 630,
      fonts: [
        { name: "Cormorant", data: CACHE.corm, weight: 600, style: "normal" },
        { name: "Cormorant", data: CACHE.cormi, weight: 500, style: "italic" },
        { name: "DM Sans", data: CACHE.sans, weight: 500, style: "normal" },
        { name: "JetBrains Mono", data: CACHE.mono, weight: 500, style: "normal" },
      ],
      headers: { "Cache-Control": "public, max-age=86400, s-maxage=31536000, immutable" },
    });
  } catch (e) {
    return new Response("og operator render error: " + (e && e.message), { status: 500 });
  }
}

function buildChip(q, scoring, t) {
  const entry = scoring.find((s) => s.q === q);
  const status = entry ? entry.status : null;
  const palette = status === "pass"
    ? { bg: "rgba(34,197,94,0.18)", fg: "#1e7e4c", border: "transparent" }
    : status === "fail"
    ? { bg: "rgba(184,71,71,0.18)", fg: t.red, border: "transparent" }
    : status === "not_yet"
    ? { bg: "transparent", fg: t.gold, border: t.gold }
    : { bg: "transparent", fg: t.muted, border: t.line };
  const label = Q_SHORT[q] || ("Q" + q);
  return h("div", {
    style: { display: "flex", alignItems: "center", justifyContent: "center", padding: "10px 18px", borderRadius: 999, backgroundColor: palette.bg, border: `1px solid ${palette.border}`, fontFamily: "DM Sans", fontSize: 14, letterSpacing: "0.06em", color: palette.fg, fontWeight: 500, minWidth: 168 },
  }, label);
}

// /api/og/compare/[tickers]
//
// 1200x630 PNG showing two or three operators side-by-side, both
// Halvren Reads visible. Tickers are dash-separated in the URL:
//   /api/og/compare/CNQ-ENB         → 2 ops
//   /api/og/compare/CNQ-ENB-AEM     → 3 ops
//
// Same design language as the operator card; light by default,
// ?dark=1 flips to dark mode.

import { ImageResponse } from "@vercel/og";

export const config = { runtime: "edge" };

const TOKENS = {
  light: { bg: "#f7f6f2", ink: "#1a1814", muted: "#6b6a66", line: "#d4d1ca", gold: "#b8860b", green: "#22c55e", red: "#b94747" },
  dark:  { bg: "#0d0c0a", ink: "#ece8df", muted: "#8a8780", line: "#2a2823", gold: "#bf9c5b", green: "#22c55e", red: "#d96b6b" },
};

const CORMORANT_600 = "https://fonts.gstatic.com/s/cormorantgaramond/v16/co3YmX5slCNuHLi8bLeY9MK7whWMhyjornFLsS6V7w.ttf";
const DMSANS_500 = "https://fonts.gstatic.com/s/dmsans/v15/rP2tp2ywxg089UriI5-g7vN_lwgZhbA.ttf";
const JETBRAINS_500 = "https://fonts.gstatic.com/s/jetbrainsmono/v18/tDbY2o-flEEny0FZhsfKu5WU4zr3E_BX0PnT8RD8yKxjPVmUsaaDhw.ttf";

let CACHE = { corm: null, sans: null, mono: null };
async function loadFont(url) { const r = await fetch(url, { cache: "force-cache" }); if (!r.ok) throw new Error("font"); return r.arrayBuffer(); }
function h(type, props, ...children) { const kids = children.flat().filter((c) => c !== null && c !== undefined && c !== false); return { type, props: { ...(props || {}), children: kids.length === 1 ? kids[0] : kids } }; }

function band(score, t) {
  if (score == null) return t.muted;
  if (score >= 75) return t.green;
  if (score >= 50) return t.gold;
  return t.red;
}

export default async function handler(req) {
  try {
    const url = new URL(req.url);
    const parts = url.pathname.split("/").filter(Boolean);
    const tickerKey = decodeURIComponent(parts[parts.length - 1] || "");
    const tickers = tickerKey.split("-").map((s) => s.trim().toUpperCase()).filter(Boolean).slice(0, 3);
    const light = url.searchParams.get("light") === "1";
    const t = light ? TOKENS.light : TOKENS.dark;

    if (tickers.length < 2) return new Response("need >= 2 tickers", { status: 400 });

    if (!CACHE.corm) CACHE.corm = await loadFont(CORMORANT_600);
    if (!CACHE.sans) CACHE.sans = await loadFont(DMSANS_500);
    if (!CACHE.mono) CACHE.mono = await loadFont(JETBRAINS_500);

    const viz = await fetch(`${url.origin}/data/viz-data.json`, { cache: "force-cache" }).then((r) => r.json());
    const ops = tickers.map((tk) => (viz.operators || []).find((o) => o.ticker.toUpperCase() === tk)).filter(Boolean);
    if (ops.length < 2) return new Response("operators not in coverage", { status: 404 });

    const mark = h("svg", { width: 28, height: 28, viewBox: "0 0 32 32", fill: "none" },
      h("path", { d: "M6 6 L6 26 M6 16 L16 16 M16 6 L16 26", stroke: t.ink, strokeWidth: 2.5, strokeLinecap: "round", strokeLinejoin: "round" }),
      h("path", { d: "M20 6 L20 26 M20 6 L28 16 L20 26", stroke: t.gold, strokeWidth: 2.5, strokeLinecap: "round", strokeLinejoin: "round" }),
    );

    const cols = ops.map((o) =>
      h("div", { style: { flex: 1, display: "flex", flexDirection: "column", alignItems: "center", justifyContent: "center", padding: "32px 16px", borderRight: `1px solid ${t.line}`, gap: 14 } },
        h("div", { style: { display: "flex", fontFamily: "JetBrains Mono", fontSize: 28, color: t.gold, letterSpacing: "0.04em" } }, o.ticker),
        h("div", { style: { display: "flex", fontFamily: "Cormorant", fontSize: 24, color: t.ink, textAlign: "center", maxWidth: 320, lineHeight: 1.15 } }, o.short_name),
        h("div", { style: { display: "flex", fontFamily: "DM Sans", fontSize: 12, color: t.muted, letterSpacing: "0.08em", textTransform: "uppercase" } }, o.sector + " · " + (o.sub_industry || "")),
        h("div", { style: { display: "flex", fontFamily: "Cormorant", fontSize: 160, lineHeight: 0.95, color: band(o.halvren_read, t), fontWeight: 600, letterSpacing: "-0.04em", marginTop: 10 } }, String(o.halvren_read == null ? "—" : o.halvren_read)),
        h("div", { style: { display: "flex", fontFamily: "DM Sans", fontSize: 12, color: t.muted, letterSpacing: "0.12em", textTransform: "uppercase" } }, (o.halvren_read == null ? "—" : o.halvren_read) + " / 100"),
      )
    );
    // strip the trailing border on the last column
    cols[cols.length - 1].props.style.borderRight = "none";

    const tree = h("div", {
        style: { width: "100%", height: "100%", display: "flex", flexDirection: "column", justifyContent: "space-between", backgroundColor: t.bg, padding: "40px 48px", fontFamily: "DM Sans", color: t.ink },
      },
      // Top
      h("div", { style: { display: "flex", alignItems: "center", justifyContent: "space-between" } },
        h("div", { style: { display: "flex", alignItems: "center", gap: 12 } }, mark, h("div", { style: { display: "flex", fontFamily: "Cormorant", fontSize: 28, color: t.ink, fontWeight: 600 } }, "Halvren Compare")),
        h("div", { style: { display: "flex", fontFamily: "DM Sans", fontSize: 12, color: t.gold, letterSpacing: "0.18em", textTransform: "uppercase" } }, "Side by side"),
      ),
      // Center: columns
      h("div", { style: { display: "flex", flex: 1, border: `1px solid ${t.line}`, borderRadius: 8, marginTop: 20 } }, cols),
      // Bottom
      h("div", { style: { display: "flex", justifyContent: "space-between", alignItems: "center", marginTop: 18, fontFamily: "DM Sans", fontSize: 12, color: t.muted, letterSpacing: "0.12em", textTransform: "uppercase" } },
        h("div", null, "Halvrencapital.com/compare"),
        h("div", null, tickers.join(" · vs · ")),
      ),
    );

    return new ImageResponse(tree, {
      width: 1200, height: 630,
      fonts: [
        { name: "Cormorant", data: CACHE.corm, weight: 600, style: "normal" },
        { name: "DM Sans", data: CACHE.sans, weight: 500, style: "normal" },
        { name: "JetBrains Mono", data: CACHE.mono, weight: 500, style: "normal" },
      ],
      headers: { "Cache-Control": "public, max-age=86400, s-maxage=31536000, immutable" },
    });
  } catch (e) {
    return new Response("compare og render error: " + (e && e.message), { status: 500 });
  }
}

// /api/og/diary/[id]
//
// 1200x630 PNG for a single Cycle Diary entry. Renders date, ticker,
// action label, and the one-sentence summary in Halvren voice.

import { ImageResponse } from "@vercel/og";

export const config = { runtime: "edge" };

const TOKENS = {
  light: { bg: "#f7f6f2", ink: "#1a1814", muted: "#6b6a66", line: "#d4d1ca", gold: "#b8860b", green: "#1e7e4c", red: "#b94747" },
  dark:  { bg: "#0d0c0a", ink: "#ece8df", muted: "#8a8780", line: "#2a2823", gold: "#bf9c5b", green: "#22c55e", red: "#d96b6b" },
};

const CORMORANT_600 = "https://fonts.gstatic.com/s/cormorantgaramond/v16/co3YmX5slCNuHLi8bLeY9MK7whWMhyjornFLsS6V7w.ttf";
const CORMORANT_500I = "https://fonts.gstatic.com/s/cormorantgaramond/v16/co3WmX5slCNuHLi8bLeY8KO7uxe1eFRr2v0.ttf";
const DMSANS_500 = "https://fonts.gstatic.com/s/dmsans/v15/rP2tp2ywxg089UriI5-g7vN_lwgZhbA.ttf";
const JETBRAINS_500 = "https://fonts.gstatic.com/s/jetbrainsmono/v18/tDbY2o-flEEny0FZhsfKu5WU4zr3E_BX0PnT8RD8yKxjPVmUsaaDhw.ttf";

let CACHE = { corm: null, cormi: null, sans: null, mono: null };
async function loadFont(url) { const r = await fetch(url, { cache: "force-cache" }); if (!r.ok) throw new Error("font"); return r.arrayBuffer(); }
function h(type, props, ...children) { const kids = children.flat().filter((c) => c !== null && c !== undefined && c !== false); return { type, props: { ...(props || {}), children: kids.length === 1 ? kids[0] : kids } }; }

const ACTION_COLOR = (a, t) => {
  if (a === "promoted" || a === "added") return t.green;
  if (a === "demoted" || a === "killed") return t.red;
  return t.gold;
};

export default async function handler(req) {
  try {
    const url = new URL(req.url);
    const parts = url.pathname.split("/").filter(Boolean);
    const id = decodeURIComponent(parts[parts.length - 1] || "");
    const dark = url.searchParams.get("dark") === "1";
    const t = dark ? TOKENS.dark : TOKENS.light;

    if (!CACHE.corm)  CACHE.corm  = await loadFont(CORMORANT_600);
    if (!CACHE.cormi) CACHE.cormi = await loadFont(CORMORANT_500I);
    if (!CACHE.sans)  CACHE.sans  = await loadFont(DMSANS_500);
    if (!CACHE.mono)  CACHE.mono  = await loadFont(JETBRAINS_500);

    const diary = await fetch(`${url.origin}/data/diary.json`, { cache: "force-cache" }).then((r) => r.json());
    const entry = (diary.entries || []).find((e) => e.id === id);
    if (!entry) return new Response("entry not found", { status: 404 });

    const mark = h("svg", { width: 28, height: 28, viewBox: "0 0 32 32", fill: "none" },
      h("path", { d: "M6 6 L6 26 M6 16 L16 16 M16 6 L16 26", stroke: t.ink, strokeWidth: 2.5, strokeLinecap: "round", strokeLinejoin: "round" }),
      h("path", { d: "M20 6 L20 26 M20 6 L28 16 L20 26", stroke: t.gold, strokeWidth: 2.5, strokeLinecap: "round", strokeLinejoin: "round" }),
    );

    const tree = h("div", {
        style: { width: "100%", height: "100%", display: "flex", flexDirection: "column", justifyContent: "space-between", backgroundColor: t.bg, padding: "64px 80px", fontFamily: "DM Sans", color: t.ink },
      },
      // Top: wordmark + diary eyebrow
      h("div", { style: { display: "flex", alignItems: "center", justifyContent: "space-between" } },
        h("div", { style: { display: "flex", alignItems: "center", gap: 12 } }, mark, h("div", { style: { display: "flex", fontFamily: "Cormorant", fontSize: 28, color: t.ink, fontWeight: 600 } }, "Halvren Cycle Diary")),
        h("div", { style: { display: "flex", fontFamily: "JetBrains Mono", fontSize: 16, color: t.muted, letterSpacing: "0.08em" } }, entry.date),
      ),
      // Center: ticker + action chip + summary
      h("div", { style: { display: "flex", flexDirection: "column", gap: 18 } },
        h("div", { style: { display: "flex", alignItems: "center", gap: 18 } },
          h("div", { style: { display: "flex", fontFamily: "JetBrains Mono", fontSize: 44, color: t.gold, letterSpacing: "0.04em" } }, entry.ticker),
          h("div", { style: { display: "flex", padding: "8px 18px", borderRadius: 999, backgroundColor: ACTION_COLOR(entry.action, t), color: t.bg, fontFamily: "DM Sans", fontSize: 14, letterSpacing: "0.18em", textTransform: "uppercase", fontWeight: 500 } }, entry.action),
        ),
        h("div", { style: { display: "flex", fontFamily: "Cormorant", fontStyle: "italic", fontSize: 56, color: t.ink, lineHeight: 1.15, letterSpacing: "-0.01em", maxWidth: 1040 } }, entry.summary.replace(/&[a-z]+;/g, "—")),
      ),
      // Bottom
      h("div", { style: { display: "flex", justifyContent: "space-between", alignItems: "center", fontFamily: "DM Sans", fontSize: 12, color: t.muted, letterSpacing: "0.12em", textTransform: "uppercase", borderTop: `1px solid ${t.line}`, paddingTop: 16 } },
        h("div", null, "halvrencapital.com/diary/" + id),
        h("div", null, "Public log of desk actions"),
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
    return new Response("diary og render error: " + (e && e.message), { status: 500 });
  }
}

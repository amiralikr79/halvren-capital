// /api/og
//
// Auto-generated OG image for /notes/<slug> and other long-form pages.
// Renders the article title in a serif over the Halvren warm off-white,
// with the small wordmark + glyph tucked in the corner. One gold hairline.
// No marketing language. The page does the rest.
//
// Usage:
//   /api/og?title=<URL-encoded title>
//   /api/og?title=<title>&eyebrow=<small label>
//
// Returns: 1200x630 PNG. Cached aggressively at the edge so social
// platforms hit the function once per URL.

import { ImageResponse } from "@vercel/og";

export const config = { runtime: "edge" };

// --- token values (from /docs/HALVREN_BRAND.md) -------------------------- //
const BG = "#f7f6f2";   // --bg
const INK = "#1a1a1a";  // --ink
const MUTED = "#6b6b6b"; // --muted
const LINE = "#d9d6cf"; // --line
const GOLD = "#a87f3c"; // --gold

// Cormorant Garamond 600 — the brand doc's display target. Pinned to a
// specific Google Fonts file URL so the edge function doesn't have to
// resolve a CSS index at request time.
const CORMORANT_600 =
  "https://fonts.gstatic.com/s/cormorantgaramond/v16/co3YmX5slCNuHLi8bLeY9MK7whWMhyjornFLsS6V7w.ttf";
// DM Sans 500 for the eyebrow + wordmark sans chrome.
const DMSANS_500 =
  "https://fonts.gstatic.com/s/dmsans/v15/rP2tp2ywxg089UriI5-g7vN_lwgZhbA.ttf";

let CORMORANT_CACHE = null;
let DMSANS_CACHE = null;

async function loadFont(url, cache) {
  if (cache.value) return cache.value;
  const res = await fetch(url, { cache: "force-cache" });
  if (!res.ok) throw new Error(`font fetch failed: ${url}`);
  cache.value = await res.arrayBuffer();
  return cache.value;
}

// Vercel functions run a fresh isolate per region; the in-memory cache
// is sticky for warm invocations and a no-op for cold ones.
const cormCache = (CORMORANT_CACHE ||= { value: null });
const sansCache = (DMSANS_CACHE   ||= { value: null });

// h() — tiny React-element factory so we don't need a JSX build step. //
function h(type, props, ...children) {
  const kids = children.flat().filter((c) => c !== null && c !== undefined && c !== false);
  return {
    type,
    props: {
      ...(props || {}),
      children: kids.length === 1 ? kids[0] : kids,
    },
  };
}

function clamp(s, max) {
  if (!s) return "";
  return s.length > max ? s.slice(0, max - 1).trimEnd() + "…" : s;
}

export default async function handler(req) {
  const url = new URL(req.url);
  const titleRaw = url.searchParams.get("title") || "Halvren Capital";
  const eyebrowRaw = url.searchParams.get("eyebrow") || "Halvren Notes";
  const title = clamp(titleRaw, 140);
  const eyebrow = clamp(eyebrowRaw, 48).toUpperCase();

  const [cormorant, dmsans] = await Promise.all([
    loadFont(CORMORANT_600, cormCache),
    loadFont(DMSANS_500, sansCache),
  ]);

  // Halvren mark: the H + arrow glyph already in nav.js / favicon.
  const mark = h(
    "svg",
    {
      width: 36,
      height: 36,
      viewBox: "0 0 32 32",
      fill: "none",
      style: { display: "block" },
    },
    h("path", {
      d: "M6 6 L6 26 M6 16 L16 16 M16 6 L16 26",
      stroke: INK,
      strokeWidth: 2.5,
      strokeLinecap: "round",
      strokeLinejoin: "round",
    }),
    h("path", {
      d: "M20 6 L20 26 M20 6 L28 16 L20 26",
      stroke: GOLD,
      strokeWidth: 2.5,
      strokeLinecap: "round",
      strokeLinejoin: "round",
    }),
  );

  const tree = h(
    "div",
    {
      style: {
        width: "100%",
        height: "100%",
        display: "flex",
        flexDirection: "column",
        justifyContent: "space-between",
        backgroundColor: BG,
        padding: "88px 96px",
        fontFamily: "DM Sans",
        color: INK,
      },
    },
    // Top row: eyebrow + gold hairline beneath
    h(
      "div",
      { style: { display: "flex", flexDirection: "column", gap: "14px" } },
      h(
        "div",
        {
          style: {
            display: "flex",
            fontFamily: "DM Sans",
            fontSize: 22,
            letterSpacing: "0.18em",
            color: GOLD,
            fontWeight: 500,
          },
        },
        eyebrow,
      ),
      h("div", {
        style: {
          width: "112px",
          height: "1px",
          backgroundColor: GOLD,
        },
      }),
    ),
    // Title block, centered vertically by space-between
    h(
      "div",
      {
        style: {
          display: "flex",
          fontFamily: "Cormorant",
          fontSize: 76,
          lineHeight: 1.08,
          letterSpacing: "-0.015em",
          color: INK,
          maxWidth: "100%",
          fontWeight: 600,
        },
      },
      title,
    ),
    // Bottom row: wordmark + glyph on the right, hairline rule on the left
    h(
      "div",
      {
        style: {
          display: "flex",
          alignItems: "center",
          justifyContent: "space-between",
          borderTop: `1px solid ${LINE}`,
          paddingTop: "28px",
        },
      },
      h(
        "div",
        {
          style: {
            display: "flex",
            fontFamily: "DM Sans",
            fontSize: 20,
            color: MUTED,
            letterSpacing: "0.04em",
          },
        },
        "halvrencapital.com",
      ),
      h(
        "div",
        { style: { display: "flex", alignItems: "center", gap: "14px" } },
        h(
          "div",
          {
            style: {
              display: "flex",
              fontFamily: "Cormorant",
              fontSize: 28,
              color: INK,
              letterSpacing: "-0.01em",
              fontWeight: 600,
            },
          },
          "Halvren Capital",
        ),
        mark,
      ),
    ),
  );

  return new ImageResponse(tree, {
    width: 1200,
    height: 630,
    fonts: [
      { name: "Cormorant", data: cormorant, weight: 600, style: "normal" },
      { name: "DM Sans",   data: dmsans,    weight: 500, style: "normal" },
    ],
    headers: {
      "Cache-Control": "public, max-age=86400, s-maxage=31536000, immutable",
    },
  });
}

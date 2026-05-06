// /api/checklist/og?ticker=CCO&pass=7
//
// Dynamic Open Graph image for /checklist/score/<ticker>. Returns 1200x630 PNG.
// Reads `ticker` and `pass` (0-10) from query string. If `pass` is missing,
// renders an "—/10" placeholder so the URL works for crawlers before the
// score has been generated.
//
// Edge runtime: required by @vercel/og.

import { ImageResponse } from "@vercel/og";

export const config = { runtime: "edge" };

const SAFE_TICKER = /^[A-Z][A-Z0-9.\-]{0,9}$/;
const SAFE_PASS = /^(?:[0-9]|10)$/;

export default function handler(req) {
  const url = new URL(req.url);
  const tickerRaw = (url.searchParams.get("ticker") || "").toUpperCase();
  const passRaw = url.searchParams.get("pass") || "";

  const ticker = SAFE_TICKER.test(tickerRaw) ? tickerRaw : null;
  const passCount = SAFE_PASS.test(passRaw) ? parseInt(passRaw, 10) : null;

  // warm-light palette (matches /page.css :root tokens)
  const COLORS = {
    bg: "#f7f6f2",
    surface: "#f9f8f5",
    text: "#1a1814",
    textMuted: "#6b6a66",
    textFaint: "#bab9b4",
    border: "#d4d1ca",
    divider: "#dcd9d5",
    gold: "#b8860b",
    goldLight: "#d4a017",
  };

  const passLabel = passCount === null ? "—" : String(passCount);
  const eyebrow = "The Halvren Checklist · Machine read";
  const tickerDisplay = ticker || "—";

  return new ImageResponse(
    (
      <div
        style={{
          width: "100%",
          height: "100%",
          display: "flex",
          flexDirection: "column",
          background: COLORS.bg,
          fontFamily: "Georgia, serif",
          color: COLORS.text,
          padding: "72px 88px",
          position: "relative",
        }}
      >
        {/* warm radial halo (subtle, matches hero on /) */}
        <div
          style={{
            position: "absolute",
            inset: 0,
            background:
              "radial-gradient(ellipse 70% 55% at 65% 30%, rgba(184,134,11,0.08), transparent 70%)",
          }}
        />

        {/* top: wordmark + eyebrow */}
        <div
          style={{
            display: "flex",
            justifyContent: "space-between",
            alignItems: "center",
          }}
        >
          <div style={{ display: "flex", alignItems: "center", gap: 18 }}>
            {/* H + arrow logo, scaled from the site nav SVG */}
            <svg
              width="56"
              height="56"
              viewBox="0 0 32 32"
              xmlns="http://www.w3.org/2000/svg"
            >
              <path
                d="M6 6 L6 26 M6 16 L16 16 M16 6 L16 26"
                stroke={COLORS.text}
                strokeWidth="2.5"
                strokeLinecap="round"
                strokeLinejoin="round"
                fill="none"
              />
              <path
                d="M20 6 L20 26 M20 6 L28 16 L20 26"
                stroke={COLORS.gold}
                strokeWidth="2.5"
                strokeLinecap="round"
                strokeLinejoin="round"
                fill="none"
              />
            </svg>
            <div
              style={{
                fontSize: 36,
                color: COLORS.text,
                letterSpacing: "-0.01em",
                display: "flex",
              }}
            >
              Halvren Capital
            </div>
          </div>
          <div
            style={{
              fontSize: 18,
              color: COLORS.gold,
              letterSpacing: "0.18em",
              textTransform: "uppercase",
              fontFamily: "ui-monospace, monospace",
              display: "flex",
            }}
          >
            CHECKLIST · {ticker ? "MACHINE READ" : "INPUT REQUIRED"}
          </div>
        </div>

        {/* spacer */}
        <div style={{ flexGrow: 1 }} />

        {/* center: ticker + score */}
        <div
          style={{
            display: "flex",
            flexDirection: "column",
            gap: 12,
          }}
        >
          <div
            style={{
              fontSize: 24,
              color: COLORS.textFaint,
              letterSpacing: "0.15em",
              textTransform: "uppercase",
              fontFamily: "ui-monospace, monospace",
              display: "flex",
            }}
          >
            {eyebrow}
          </div>
          <div
            style={{
              display: "flex",
              alignItems: "baseline",
              gap: 36,
            }}
          >
            <div
              style={{
                fontSize: 168,
                fontFamily: "ui-monospace, monospace",
                color: COLORS.gold,
                letterSpacing: "-0.02em",
                lineHeight: 1,
                display: "flex",
              }}
            >
              {tickerDisplay}
            </div>
            <div
              style={{
                fontSize: 96,
                fontFamily: "ui-monospace, monospace",
                color: COLORS.text,
                letterSpacing: "-0.02em",
                lineHeight: 1.1,
                display: "flex",
              }}
            >
              {passLabel}/10
            </div>
            <div
              style={{
                fontSize: 22,
                color: COLORS.textMuted,
                fontFamily: "ui-monospace, monospace",
                letterSpacing: "0.12em",
                textTransform: "uppercase",
                paddingBottom: 18,
                display: "flex",
              }}
            >
              questions
              <br />
              passed
            </div>
          </div>
        </div>

        <div style={{ flexGrow: 1 }} />

        {/* footer: disclaimer + URL */}
        <div
          style={{
            display: "flex",
            justifyContent: "space-between",
            alignItems: "flex-end",
            paddingTop: 28,
            borderTop: `1px solid ${COLORS.divider}`,
          }}
        >
          <div
            style={{
              fontSize: 18,
              color: COLORS.textMuted,
              maxWidth: 720,
              lineHeight: 1.45,
              display: "flex",
            }}
          >
            Machine read against the Halvren Checklist using public filings and web search. Not principal-reviewed.
          </div>
          <div
            style={{
              fontSize: 18,
              color: COLORS.gold,
              fontFamily: "ui-monospace, monospace",
              letterSpacing: "0.04em",
              display: "flex",
            }}
          >
            halvrencapital.com/checklist
          </div>
        </div>
      </div>
    ),
    {
      width: 1200,
      height: 630,
      headers: {
        // 1h browser cache, 1d CDN cache; cache key is keyed off the full URL
        "Cache-Control":
          "public, max-age=3600, s-maxage=86400, stale-while-revalidate=604800",
      },
    },
  );
}

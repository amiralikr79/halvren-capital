#!/usr/bin/env bash
# scripts/quality_gate.sh
#
# V3-2 Checklist Tool quality gate. Hits the live /api/checklist/score endpoint
# on a given preview deployment with five tickers and writes the full JSON
# responses to a folder so the principal can verify each citation against the
# actual filing.
#
# Usage:
#   HALVREN_PREVIEW=https://halvren-capital-<sha>-<scope>.vercel.app \
#     bash scripts/quality_gate.sh
#
#   # or override the tickers:
#   HALVREN_PREVIEW=https://... HALVREN_TICKERS="CCO CNQ" bash scripts/quality_gate.sh
#
# What it does:
#   1. POSTs /api/checklist/score for each ticker, sequentially with a small
#      delay so the server's rate limit is exercised but not exceeded
#      (5/IP/hour — this script does 5 in one run).
#   2. Writes pretty-printed JSON to ./quality-gate-output/<ticker>.json.
#   3. Prints a one-line summary per ticker: status code, pass count, on_coverage,
#      whether each of the 10 sources has a non-empty url.
#
# What it does NOT do:
#   - Verify citations against the actual filings (that is the principal's job).
#   - Test the OG image preview on x.com / linkedin (manual).
#   - Run Lighthouse (manual: `npx lighthouse <url>`).

set -euo pipefail

PREVIEW="${HALVREN_PREVIEW:-}"
TICKERS="${HALVREN_TICKERS:-CCO CNQ RY BNS NTR}"
OUT_DIR="${HALVREN_OUT_DIR:-./quality-gate-output}"
DELAY_S="${HALVREN_DELAY_S:-3}"

if [[ -z "$PREVIEW" ]]; then
  echo "error: set HALVREN_PREVIEW=https://your-preview.vercel.app" >&2
  exit 1
fi

mkdir -p "$OUT_DIR"

echo "Quality gate against: $PREVIEW"
echo "Tickers:              $TICKERS"
echo "Output dir:           $OUT_DIR"
echo "Delay between calls:  ${DELAY_S}s"
echo

for t in $TICKERS; do
  echo "── $t ──"
  out="$OUT_DIR/$t.json"
  http_code=$(curl -sS -o "$out" -w "%{http_code}" \
    -H "Content-Type: application/json" \
    -X POST \
    -d "{\"ticker\":\"$t\"}" \
    "$PREVIEW/api/checklist/score") || http_code="curl-failed"

  if ! command -v jq >/dev/null 2>&1; then
    echo "  http=$http_code  (install jq for richer summary)"
    echo "  saved: $out"
    sleep "$DELAY_S"
    continue
  fi

  pass=$(jq -r '.overall.pass_count // .pass_count // "n/a"' "$out")
  on_cov=$(jq -r '.on_coverage // false' "$out")
  cached=$(jq -r '.cached // false' "$out")
  url_count=$(jq -r '[.answers[]?.source.url // empty | select(length>0)] | length' "$out")
  q_count=$(jq -r '.answers | length' "$out" 2>/dev/null || echo "0")
  err_code=$(jq -r '.error.code // empty' "$out")

  if [[ -n "$err_code" ]]; then
    err_msg=$(jq -r '.error.message // ""' "$out")
    echo "  http=$http_code  ERROR: $err_code — $err_msg"
  else
    echo "  http=$http_code  pass=$pass/10  questions=$q_count  on_coverage=$on_cov  cached=$cached  urls_present=$url_count/10"
  fi
  echo "  saved: $out"
  sleep "$DELAY_S"
done

echo
echo "Done. The principal must now:"
echo "  1. Open each $OUT_DIR/<ticker>.json and verify every cited filing exists and matches the claim."
echo "  2. Visit $PREVIEW/checklist/score/<ticker> for each ticker and confirm visual rendering."
echo "  3. Test the OG image: paste the URL into x.com's compose box and confirm preview."
echo "  4. Run Lighthouse: npx lighthouse $PREVIEW/checklist/score/CCO --view"
echo "  5. Test the rate limit: rerun this script immediately after; the 6th call (or the second batch) should return 429."

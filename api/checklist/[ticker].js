// /api/checklist/[ticker]
//
// Halvren Checklist Live — streaming engine.
//
// GET /api/checklist/CCO
//   → SSE stream of 11 JSON lines (10 question objects + 1 scorecard) in the
//     order the model emits them, each wrapped in an SSE 'line' event.
//   → On a cache hit (24h TTL), returns the cached result as a single
//     'complete' event followed by 'end'. The frontend handles both paths.
//
// Pipeline:
//   1. Normalise the ticker, apply rate limit (10/IP/hour via Upstash).
//   2. Check 24h Redis cache. Hit -> stream cached. Miss -> continue.
//   3. Fetch Yahoo Finance fundamentals.
//   4. Call Anthropic (sonnet-4-6) with streaming + JSON-Lines protocol.
//   5. Each completed JSON line is parsed, validated, emitted as SSE.
//   6. On completion, persist the result to Redis (24h TTL).
//
// SSE event shapes:
//   event: meta       data: {"ticker":"CCO","fromCache":false,"sparse":false,"identity":{...}}
//   event: line       data: {"q":1,"verdict":"green","text":"..."}
//   event: complete   data: {"answers":[...],"scorecard":{...},"fromCache":true}
//   event: end        data: {}
//   event: error      data: {"code":"rate_limited","message":"..."}

import Anthropic from "@anthropic-ai/sdk";
import {
  buildUserMessage,
  cacheGet,
  cacheSet,
  coverageIndex,
  fetchFundamentals,
  fundamentalsToText,
  MODEL_ID,
  normalizeTicker,
  rateLimit,
  SPARSE_RESPONSE_TEMPLATE,
  SYSTEM_PROMPT,
} from "./_lib.js";

export const config = { maxDuration: 60 };

// ---------------------------------------------------------------------------
// SSE helpers
// ---------------------------------------------------------------------------

function sseWrite(res, event, data) {
  res.write(`event: ${event}\n`);
  res.write(`data: ${JSON.stringify(data)}\n\n`);
}

function sseEnd(res) {
  try {
    res.write("event: end\ndata: {}\n\n");
    res.end();
  } catch {
    /* swallow */
  }
}

// ---------------------------------------------------------------------------
// JSON-Line parser — streams character deltas in, emits parsed objects out.
// Tolerant of leading whitespace and stray non-JSON characters between
// objects (the model occasionally emits a blank line).
// ---------------------------------------------------------------------------

function makeLineParser(onObject, onError) {
  let buf = "";
  return {
    feed(chunk) {
      buf += chunk;
      let idx;
      while ((idx = buf.indexOf("\n")) !== -1) {
        const line = buf.slice(0, idx).trim();
        buf = buf.slice(idx + 1);
        if (!line) continue;
        // strip a possible leading "data: " or markdown code fence garbage
        const cleaned = line.replace(/^```(?:json|jsonl)?$/i, "")
                            .replace(/^```$/, "")
                            .trim();
        if (!cleaned) continue;
        try {
          const obj = JSON.parse(cleaned);
          onObject(obj);
        } catch (e) {
          onError && onError(line, e);
        }
      }
    },
    flush() {
      const tail = buf.trim();
      buf = "";
      if (!tail) return;
      try {
        onObject(JSON.parse(tail));
      } catch (e) {
        onError && onError(tail, e);
      }
    },
  };
}

// ---------------------------------------------------------------------------
// validators — only accept lines that match the protocol shape
// ---------------------------------------------------------------------------

const VERDICTS = new Set(["green", "amber", "red"]);

function isAnswerLine(o) {
  return (
    o &&
    typeof o === "object" &&
    typeof o.q === "number" &&
    o.q >= 1 &&
    o.q <= 10 &&
    typeof o.verdict === "string" &&
    VERDICTS.has(o.verdict) &&
    typeof o.text === "string" &&
    o.text.length > 0
  );
}

function isScorecardLine(o) {
  return (
    o &&
    typeof o === "object" &&
    o.q === "scorecard" &&
    typeof o.verdict === "string" &&
    VERDICTS.has(o.verdict) &&
    typeof o.text === "string" &&
    o.text.length > 0
  );
}

// ---------------------------------------------------------------------------
// streaming flow
// ---------------------------------------------------------------------------

async function streamFresh({ ticker, coverageHit, exchange, res }) {
  // 1. fundamentals (Yahoo, may be sparse)
  const fund = await fetchFundamentals(ticker);
  const fundText = fundamentalsToText(fund);
  const sparse = !fund.ok || fund.sparse;

  // identity for the meta block
  const identity = coverageHit
    ? {
        ticker: coverageHit.ticker,
        name: coverageHit.name,
        sector: coverageHit.sector,
        subIndustry: coverageHit.sub_industry,
        exchange: coverageHit.exchange,
        coverageHit: true,
      }
    : fund.ok
      ? {
          ticker,
          name: ticker,
          sector: fund.profile.sector || "—",
          subIndustry: fund.profile.industry || "—",
          exchange: exchange || (fund.attempted?.find((t) => t.includes(".")) ? "TSX" : "—"),
          coverageHit: false,
        }
      : {
          ticker,
          name: ticker,
          sector: "—",
          subIndustry: "—",
          exchange: exchange || "—",
          coverageHit: false,
        };

  sseWrite(res, "meta", {
    ticker,
    fromCache: false,
    sparse,
    identity,
  });

  // 2. if Yahoo returned nothing at all, ship the graceful template and stop.
  if (!fund.ok) {
    const sparseAnswers = SPARSE_RESPONSE_TEMPLATE.answers.map((a) => ({ ...a }));
    for (const ans of sparseAnswers) {
      sseWrite(res, "line", ans);
      // small jitter so the UI animates; this is a 10-line burst
      await new Promise((r) => setTimeout(r, 30));
    }
    const scorecard = { ...SPARSE_RESPONSE_TEMPLATE.scorecard };
    sseWrite(res, "line", { q: "scorecard", verdict: scorecard.overall, text: scorecard.text });
    const completePayload = {
      ticker,
      identity,
      fromCache: false,
      sparse: true,
      answers: sparseAnswers,
      scorecard: { overall: scorecard.overall, text: scorecard.text },
      generated_at: new Date().toISOString(),
      model: "fallback",
    };
    await cacheSet(ticker, completePayload).catch(() => {});
    sseWrite(res, "complete", completePayload);
    return;
  }

  // 3. Anthropic stream
  if (!process.env.ANTHROPIC_API_KEY) {
    sseWrite(res, "error", {
      code: "no_api_key",
      message:
        "The Checklist engine is not configured on this deployment yet. " +
        "Set ANTHROPIC_API_KEY in the Vercel project to enable live runs.",
    });
    return;
  }

  const client = new Anthropic({ apiKey: process.env.ANTHROPIC_API_KEY });
  const userMessage = buildUserMessage({
    ticker,
    exchange: identity.exchange,
    coverageHit,
    fundamentalsText: fundText,
  });

  const answers = [];
  let scorecard = null;

  const parser = makeLineParser(
    (obj) => {
      if (isAnswerLine(obj)) {
        // dedupe — model may occasionally re-emit
        if (answers.find((a) => a.q === obj.q)) return;
        answers.push({ q: obj.q, verdict: obj.verdict, text: obj.text });
        sseWrite(res, "line", { q: obj.q, verdict: obj.verdict, text: obj.text });
      } else if (isScorecardLine(obj)) {
        scorecard = { overall: obj.verdict, text: obj.text };
        sseWrite(res, "line", { q: "scorecard", verdict: obj.verdict, text: obj.text });
      }
      // silently drop anything else (preamble, junk)
    },
    () => {
      /* swallow line parse errors */
    },
  );

  let stream;
  try {
    stream = client.messages.stream({
      model: MODEL_ID,
      max_tokens: 3000,
      system: [
        { type: "text", text: SYSTEM_PROMPT, cache_control: { type: "ephemeral" } },
      ],
      messages: [{ role: "user", content: userMessage }],
    });
  } catch (e) {
    sseWrite(res, "error", {
      code: "model_invoke_failed",
      message: e?.message || "Could not start the model stream.",
    });
    return;
  }

  try {
    for await (const event of stream) {
      if (event.type === "content_block_delta" && event.delta?.type === "text_delta") {
        parser.feed(event.delta.text);
      }
    }
    parser.flush();
  } catch (e) {
    sseWrite(res, "error", {
      code: "stream_error",
      message: e?.message || "Stream interrupted.",
    });
    return;
  }

  // ensure we have 10 answers + scorecard before caching
  if (answers.length < 10 || !scorecard) {
    sseWrite(res, "error", {
      code: "incomplete_stream",
      message: `Stream produced ${answers.length}/10 answers; scorecard=${scorecard ? "present" : "missing"}. Try again.`,
    });
    return;
  }

  // sort + cache
  answers.sort((a, b) => a.q - b.q);
  const payload = {
    ticker,
    identity,
    fromCache: false,
    sparse,
    answers,
    scorecard,
    generated_at: new Date().toISOString(),
    model: MODEL_ID,
  };
  await cacheSet(ticker, payload).catch(() => {});
  sseWrite(res, "complete", payload);
}

// ---------------------------------------------------------------------------
// HTTP handler
// ---------------------------------------------------------------------------

export default async function handler(req, res) {
  // Standard SSE response headers
  res.setHeader("Content-Type", "text/event-stream; charset=utf-8");
  res.setHeader("Cache-Control", "no-cache, no-transform");
  res.setHeader("Connection", "keep-alive");
  res.setHeader("X-Accel-Buffering", "no");
  res.setHeader("Access-Control-Allow-Origin", "*");
  if (typeof res.flushHeaders === "function") res.flushHeaders();

  if (req.method === "OPTIONS") {
    res.statusCode = 204;
    return res.end();
  }

  const tickerRaw =
    (req.query && (req.query.ticker || req.query.t)) ||
    (req.url || "").split("?")[0].split("/").filter(Boolean).pop();

  const ticker = normalizeTicker(tickerRaw);
  if (!ticker) {
    sseWrite(res, "error", {
      code: "bad_ticker",
      message: "Ticker must match ^[A-Z][A-Z0-9.\\-]{0,9}$",
    });
    return sseEnd(res);
  }

  // rate limit
  const rl = await rateLimit(req);
  if (!rl.ok) {
    sseWrite(res, "error", {
      code: "rate_limited",
      message:
        "The desk reads slowly. Come back in an hour, or read what we've already published.",
      retryAfterSeconds: rl.resetSeconds || 3600,
    });
    return sseEnd(res);
  }

  // cache hit?
  const cached = await cacheGet(ticker);
  if (cached && typeof cached === "object") {
    try {
      sseWrite(res, "meta", {
        ticker,
        fromCache: true,
        sparse: !!cached.sparse,
        identity: cached.identity,
      });
      for (const a of cached.answers || []) sseWrite(res, "line", a);
      if (cached.scorecard) {
        sseWrite(res, "line", {
          q: "scorecard",
          verdict: cached.scorecard.overall,
          text: cached.scorecard.text,
        });
      }
      sseWrite(res, "complete", { ...cached, fromCache: true });
      return sseEnd(res);
    } catch {
      /* fall through to fresh run */
    }
  }

  const coverageHit = coverageIndex()[ticker] || null;
  try {
    await streamFresh({
      ticker,
      coverageHit,
      exchange: (coverageHit && coverageHit.exchange) || null,
      res,
    });
  } catch (e) {
    sseWrite(res, "error", {
      code: "internal",
      message: e?.message || "Unhandled error in the streaming engine.",
    });
  } finally {
    sseEnd(res);
  }
}

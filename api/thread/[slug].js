// /api/thread/[slug]
//
// Distills a long-form note into a 6-tweet thread in Halvren voice.
//
//   - Reads the note's .mdx source by slug.
//   - Sends a system + user prompt to Anthropic (claude-sonnet-4-6).
//   - Returns { tweets: string[] } with exactly 6 entries on success.
//   - Caches the result in Upstash Redis for 7 days, keyed by the note
//     slug + sha256 of the note body so the cache invalidates if the
//     note changes.
//   - Returns { error: "..." } on failure.

import { Redis } from "@upstash/redis";
import { createHash } from "node:crypto";
import { readFileSync, existsSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const HERE = dirname(fileURLToPath(import.meta.url));
const ROOT = join(HERE, "..", "..");
const NOTES_DIR = join(ROOT, "content", "notes");
const NOTE_URL_BASE = "https://halvrencapital.com/notes/";

const CACHE_TTL_S = 7 * 24 * 3600;
const MODEL = "claude-sonnet-4-5"; // Halvren default; Sonnet 4.6 alias if available
const MAX_TOKENS = 1200;

let REDIS = null;
function redis() {
  if (REDIS) return REDIS;
  if (!process.env.UPSTASH_REDIS_REST_URL || !process.env.UPSTASH_REDIS_REST_TOKEN) return null;
  REDIS = Redis.fromEnv();
  return REDIS;
}

function ok(body, status = 200, headers = {}) {
  return new Response(JSON.stringify(body), {
    status,
    headers: { "content-type": "application/json", ...headers },
  });
}

function bad(error, status = 400) {
  return ok({ error }, status);
}

function readNote(slug) {
  const safe = String(slug || "").replace(/[^a-z0-9-]/gi, "");
  if (!safe || safe !== slug) return null;
  const path = join(NOTES_DIR, `${safe}.mdx`);
  if (!existsSync(path)) return null;
  const src = readFileSync(path, "utf-8");
  if (!src.startsWith("---\n")) return null;
  const end = src.indexOf("\n---\n", 4);
  if (end === -1) return null;
  const head = src.slice(4, end);
  const body = src.slice(end + 5).trim();
  const meta = {};
  for (const line of head.split("\n")) {
    if (!line.includes(":") || line.startsWith(" ")) continue;
    const [k, ...rest] = line.split(":");
    meta[k.trim()] = rest.join(":").trim().replace(/^['"]|['"]$/g, "");
  }
  return { slug: safe, meta, body };
}

const SYSTEM_PROMPT = `You are the Halvren Capital editorial desk. You write in the Buffett-meets-Druckenmiller voice already established on the site: editorial, restrained, dry, the reader is an adult.

Distill the supplied long-form note into a 6-tweet thread.

Rules — non-negotiable:
- Exactly 6 tweets. No more, no fewer.
- Each tweet ≤ 280 characters, including spaces.
- No hashtags. No emoji. No "🧵". No "1/" prefixes (the UI numbers them).
- No price targets, no buy/sell calls, no short-term forecasts.
- Tweet 1 hooks with a single concrete claim or number from the note. Never a hedge, never "Most investors don't realize…".
- Tweets 2–5 carry the through-line of the note in plain prose. One idea per tweet. Sentences can be fragments. Numbers over adjectives. Names over vague nouns.
- Tweet 6 ends with the note URL on its own line, preceded by one sentence that earns the click. The URL will be supplied; place it verbatim.
- Forbidden words: leverage (verb form), unlock, synergies, journey, ecosystem, paradigm, robust, world-class, best-in-class, mission-driven, revolutionizing, in today's market.

Return strict JSON of the shape: { "tweets": ["...", "...", "...", "...", "...", "..."] } and nothing else.`;

function userPrompt(meta, body, url) {
  const truncated = body.length > 12000 ? body.slice(0, 12000) + "\n[…note continues; abridged for context window]" : body;
  return `Note title: ${meta.title || ""}
Note URL (paste verbatim into tweet 6): ${url}

Note body (markdown):
${truncated}

Write the 6-tweet thread now. Return JSON only.`;
}

function extractJsonTweets(text) {
  if (!text) return null;
  const m = text.match(/\{[\s\S]*"tweets"[\s\S]*\}/);
  if (!m) return null;
  try {
    const parsed = JSON.parse(m[0]);
    const arr = parsed && Array.isArray(parsed.tweets) ? parsed.tweets : null;
    if (!arr || arr.length < 4 || arr.length > 8) return null;
    return arr.map((t) => String(t || "").trim()).filter(Boolean);
  } catch {
    return null;
  }
}

async function callAnthropic(meta, body, url, apiKey) {
  const res = await fetch("https://api.anthropic.com/v1/messages", {
    method: "POST",
    headers: {
      "x-api-key": apiKey,
      "anthropic-version": "2023-06-01",
      "content-type": "application/json",
    },
    body: JSON.stringify({
      model: MODEL,
      max_tokens: MAX_TOKENS,
      system: [{ type: "text", text: SYSTEM_PROMPT, cache_control: { type: "ephemeral" } }],
      messages: [{ role: "user", content: userPrompt(meta, body, url) }],
    }),
  });
  if (!res.ok) {
    const text = await res.text().catch(() => "");
    throw new Error(`anthropic ${res.status}: ${text.slice(0, 240)}`);
  }
  const json = await res.json();
  const content = (json.content || []).find((c) => c.type === "text");
  return content ? content.text : "";
}

export default async function handler(req) {
  try {
    if (req.method && req.method !== "GET" && req.method !== "POST") {
      return bad("method not allowed", 405);
    }

    // Pull slug from the URL path (Vercel passes [slug] in the path).
    const url = new URL(req.url);
    const parts = url.pathname.split("/").filter(Boolean);
    const slug = decodeURIComponent(parts[parts.length - 1] || "");
    const note = readNote(slug);
    if (!note) return bad("note not found", 404);

    const noteUrl = NOTE_URL_BASE + note.slug;
    const fingerprint = createHash("sha256").update(note.body).digest("hex").slice(0, 16);
    const cacheKey = `thread:v1:${note.slug}:${fingerprint}`;

    const r = redis();
    if (r) {
      try {
        const cached = await r.get(cacheKey);
        if (cached && Array.isArray(cached.tweets)) {
          return ok({ tweets: cached.tweets, cached: true });
        }
      } catch { /* ignore cache read errors */ }
    }

    const apiKey = process.env.ANTHROPIC_API_KEY;
    if (!apiKey) return bad("thread generator not configured (no ANTHROPIC_API_KEY)", 503);

    let raw;
    try {
      raw = await callAnthropic(note.meta, note.body, noteUrl, apiKey);
    } catch (e) {
      return bad(`upstream error: ${e.message}`, 502);
    }

    const tweets = extractJsonTweets(raw);
    if (!tweets || tweets.length < 4) {
      return bad("thread generator returned malformed JSON; please retry", 502);
    }

    if (r) {
      try { await r.set(cacheKey, { tweets }, { ex: CACHE_TTL_S }); } catch {}
    }

    return ok({ tweets });
  } catch (e) {
    return bad(`internal: ${e.message || e}`, 500);
  }
}

export const config = { runtime: "nodejs" };

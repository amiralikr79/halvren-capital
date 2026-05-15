// Halvren Checklist Live — streaming client. Vanilla. No framework.
//
// Handles both /checklist/live (form-submit) and /checklist/live/<TICKER>
// (direct-deep-link). The deep-link path auto-runs the same flow with the
// ticker from the URL.

(function () {
  "use strict";

  // The canonical 10 question texts. Identical to /docs/HALVREN_BRAND.md and
  // /content/checklist.json. Inlined here so the page renders the question
  // rail with no extra fetch.
  var QUESTIONS = [
    "Does it generate free cash flow through the <em>full</em> cycle, or only the top half of it?",
    "Do the unit economics still work at the <em>worst</em> price of the last decade?",
    "What does the balance sheet look like at <em>trough</em> pricing: net debt, covenants, maturity ladder?",
    "When they reinvest a dollar (capex, M&amp;A, or buyback), what actually <em>comes back</em>?",
    "How much of the operator's own net worth, <em>bought</em> and not granted, sits in this name?",
    "What did management actually <em>do</em> in 2015 and 2020: issue, buy back, or sit still?",
    "Is compensation tied to <em>per-share</em> value, or to production, revenue, and size?",
    "Who <em>succeeds</em> the operator, and is that person already visible on the page?",
    "Where are we on the cost curve that <em>matters</em>: the real one, not the one in the pitch deck?",
    "What does a “normal” year look like a <em>decade</em> from now, and does this business still work at that price?",
  ];

  function init(scope) {
    var root = scope || document.querySelector("[data-live-root]");
    if (!root) return;

    var form = root.querySelector("[data-live-form]");
    var inputRow = form;
    var input = root.querySelector("[data-live-input]");
    var submit = root.querySelector("[data-live-submit]");
    var listEl = root.querySelector("[data-live-list]");
    var metaEl = root.querySelector("[data-live-meta]");
    var errEl = root.querySelector("[data-live-error]");
    var scorecardEl = root.querySelector("[data-live-scorecard]");
    var trustEl = root.querySelector("[data-live-trust]");
    var shareEl = root.querySelector("[data-live-share]");

    var TICKER_RE = /^[A-Z][A-Z0-9.\-]{0,9}$/;

    function reset() {
      errEl.removeAttribute("data-visible");
      scorecardEl.removeAttribute("data-visible");
      trustEl.removeAttribute("data-visible");
      shareEl.removeAttribute("data-visible");
      metaEl.removeAttribute("data-visible");
      listEl.removeAttribute("data-visible");
      listEl.innerHTML = "";
    }

    function showError(title, body) {
      errEl.querySelector("[data-err-title]").textContent = title || "Something went sideways.";
      var bodyEl = errEl.querySelector("[data-err-body]");
      // body may contain a link; allow restricted HTML
      if (/<a /.test(body)) {
        bodyEl.innerHTML = body;
      } else {
        bodyEl.textContent = body || "";
      }
      errEl.setAttribute("data-visible", "true");
      inputRow.removeAttribute("data-collapsed");
      submit.disabled = false;
      submit.textContent = "Run the 10";
    }

    function renderRows() {
      listEl.innerHTML = "";
      for (var i = 0; i < 10; i++) {
        var li = document.createElement("li");
        li.className = "live-row";
        li.setAttribute("data-q", String(i + 1));
        li.innerHTML =
          '<span class="lr-num"><span class="lr-dot" data-dot></span>' +
          String(i + 1).padStart(2, "0") +
          "</span>" +
          '<div>' +
          '<p class="lr-q">' + QUESTIONS[i] + '</p>' +
          '<p class="lr-text" data-text></p>' +
          '</div>';
        listEl.appendChild(li);
      }
      listEl.setAttribute("data-visible", "true");
      trustEl.setAttribute("data-visible", "true");
    }

    function setRow(q, verdict, text, opts) {
      opts = opts || {};
      var row = listEl.querySelector('[data-q="' + q + '"]');
      if (!row) return;
      row.setAttribute("data-visible", "true");
      if (verdict) row.setAttribute("data-verdict", verdict);
      var textEl = row.querySelector("[data-text]");
      if (textEl) {
        textEl.textContent = text || "";
        if (opts.streaming) textEl.classList.add("streaming");
        else textEl.classList.remove("streaming");
      }
    }

    function setScorecard(identity, verdict, text, answers) {
      var h = scorecardEl.querySelector("[data-scorecard-h]");
      var tickerEl = scorecardEl.querySelector("[data-scorecard-ticker]");
      var textEl = scorecardEl.querySelector("[data-scorecard-text]");
      var chipsEl = scorecardEl.querySelector("[data-scorecard-chips]");
      tickerEl.textContent = (identity && identity.ticker) || "—";
      textEl.textContent = text || "";
      chipsEl.innerHTML = "";
      var verdictsOrdered = (answers || []).slice().sort(function (a, b) { return a.q - b.q; });
      for (var i = 0; i < 10; i++) {
        var v = (verdictsOrdered[i] && verdictsOrdered[i].verdict) || "amber";
        var chip = document.createElement("span");
        chip.className = "live-scorecard-chip";
        chip.setAttribute("data-verdict", v);
        chip.title = "Q" + (i + 1) + " — " + v;
        chipsEl.appendChild(chip);
      }
      scorecardEl.setAttribute("data-visible", "true");
    }

    function setMeta(ticker, identity, fromCache) {
      metaEl.querySelector("[data-meta-ticker]").textContent = ticker;
      metaEl.querySelector("[data-meta-name]").textContent = (identity && identity.name && identity.name !== ticker) ? identity.name : "";
      var sectorLine = [];
      if (identity && identity.sector && identity.sector !== "—") sectorLine.push(identity.sector);
      if (identity && identity.subIndustry && identity.subIndustry !== "—") sectorLine.push(identity.subIndustry);
      metaEl.querySelector("[data-meta-sector]").textContent = sectorLine.join(" · ");
      metaEl.querySelector("[data-meta-cache]").textContent = fromCache
        ? "Cached read · refreshed daily"
        : "Live engine · streaming";
      metaEl.setAttribute("data-visible", "true");
    }

    function setShare(ticker) {
      var url = window.location.origin + "/checklist/live/" + encodeURIComponent(ticker);
      shareEl.querySelector("[data-share-url]").textContent = url;
      var btn = shareEl.querySelector("[data-share-copy]");
      btn.onclick = function () {
        if (navigator.clipboard && navigator.clipboard.writeText) {
          navigator.clipboard.writeText(url).then(function () {
            btn.textContent = "Copied";
            setTimeout(function () { btn.textContent = "Copy"; }, 1800);
          });
        }
      };
      shareEl.setAttribute("data-visible", "true");
    }

    // ----- SSE parser (manual; fetch+ReadableStream) ------------------------
    async function runStream(ticker) {
      reset();
      inputRow.setAttribute("data-collapsed", "true");
      submit.disabled = true;
      submit.textContent = "Reading…";
      renderRows();

      var url = "/api/checklist/" + encodeURIComponent(ticker);
      var res;
      try {
        res = await fetch(url, { headers: { Accept: "text/event-stream" } });
      } catch (e) {
        showError("Connection failed.", "Try again in a moment. If this persists, the live engine may be offline.");
        return;
      }
      if (!res.ok || !res.body) {
        var ct = res.headers.get("content-type") || "";
        if (res.status === 429 || ct.includes("application/json")) {
          var body = await res.text().catch(function () { return ""; });
          showError("The desk reads slowly.", "Come back in an hour, or read what we've already published <a href='/research'>in the archive</a>.");
        } else {
          showError("The engine returned an error.", "HTTP " + res.status + ". Try a different ticker, or come back in a moment.");
        }
        return;
      }

      var reader = res.body.getReader();
      var decoder = new TextDecoder();
      var buf = "";

      function dispatch(event, payload) {
        if (event === "meta") {
          setMeta(payload.ticker, payload.identity, payload.fromCache);
          setShare(payload.ticker);
          // update URL bar (no reload)
          try {
            history.replaceState(null, "", "/checklist/live/" + payload.ticker);
          } catch (e) { /* ignore */ }
        } else if (event === "line") {
          if (payload.q === "scorecard") {
            // Hold for the 'complete' frame to fill chips + identity.
            // But also display the overall sentence immediately.
            // The scorecard is finalised by 'complete'.
          } else {
            setRow(payload.q, payload.verdict, payload.text, { streaming: false });
          }
        } else if (event === "complete") {
          // Finalise: clear streaming cursors and show the scorecard.
          var rows = listEl.querySelectorAll(".lr-text.streaming");
          rows.forEach(function (n) { n.classList.remove("streaming"); });
          setScorecard(payload.identity, (payload.scorecard || {}).overall || "amber",
                       (payload.scorecard || {}).text || "", payload.answers || []);
          submit.disabled = false;
          submit.textContent = "Run another";
          inputRow.removeAttribute("data-collapsed");
          input.value = "";
        } else if (event === "error") {
          if (payload.code === "rate_limited") {
            showError("The desk reads slowly.", "Come back in an hour, or read what we've already published <a href='/research'>in the archive</a>.");
          } else if (payload.code === "bad_ticker") {
            showError("Ticker not recognised.", "Use the exchange format: NVDA, SHOP, CIX.TO, ATD.TO. Letters, dots, and dashes only.");
          } else if (payload.code === "no_api_key") {
            showError("Engine offline.", payload.message);
          } else if (payload.code === "incomplete_stream") {
            showError("The stream ended early.", "Try the same ticker again — the cache will hold the cleaner run.");
          } else {
            showError("The engine returned an error.", payload.message || "Try a different ticker.");
          }
        }
      }

      function processBuffer() {
        // SSE frames separated by blank lines
        var idx;
        while ((idx = buf.indexOf("\n\n")) !== -1) {
          var frame = buf.slice(0, idx);
          buf = buf.slice(idx + 2);
          var event = "message";
          var dataLines = [];
          frame.split("\n").forEach(function (line) {
            if (line.startsWith("event:")) event = line.slice(6).trim();
            else if (line.startsWith("data:")) dataLines.push(line.slice(5).trim());
          });
          if (!dataLines.length) continue;
          var data = dataLines.join("\n");
          var parsed;
          try { parsed = JSON.parse(data); } catch (e) { continue; }
          dispatch(event, parsed);
        }
      }

      try {
        while (true) {
          var chunk = await reader.read();
          if (chunk.done) break;
          buf += decoder.decode(chunk.value, { stream: true });
          processBuffer();
        }
        buf += decoder.decode();
        processBuffer();
      } catch (e) {
        showError("The stream broke.", "Try again — the engine often recovers on the second run.");
      }
    }

    // wire submit
    form.addEventListener("submit", function (e) {
      e.preventDefault();
      var v = (input.value || "").trim().toUpperCase();
      if (!TICKER_RE.test(v)) {
        showError("Ticker not recognised.", "Use the exchange format: NVDA, SHOP, CIX.TO, ATD.TO. Letters, dots, and dashes only.");
        return;
      }
      runStream(v);
    });

    // deep-link: /checklist/live/<TICKER>
    var path = window.location.pathname || "";
    var m = path.match(/^\/checklist\/live\/([A-Z][A-Z0-9.\-]{0,9})\/?$/);
    if (m) {
      var deepTicker = m[1].toUpperCase();
      input.value = deepTicker;
      setTimeout(function () { runStream(deepTicker); }, 200);
    }
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", function () { init(); });
  } else {
    init();
  }

  // Expose for the homepage embed
  window.HalvrenChecklistLive = { init: init };
})();

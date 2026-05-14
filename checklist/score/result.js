// /checklist/score/result.js
//
// Client-side renderer for the /checklist/score/<ticker> page.
// 1. Reads window.__HALVREN_TICKER__ (set inline by api/checklist/page.js)
// 2. POSTs /api/checklist/score
// 3. Renders the V3-2 hero band, the 10-question machine column, and (if the
//    ticker is on coverage) the principal column side-by-side with gutter
//    agree/divergence indicators.
// 4. Wires share buttons (copy URL, X, LinkedIn).
//
// V3-2 schema:
//   overall: { pass_count, summary }, source: { label, url },
//   answers[].question, on_coverage: bool.
//
// No framework. No build step. ES2017+ (modern browsers only).

(function () {
  var ticker = window.__HALVREN_TICKER__;
  if (!ticker) return;

  var $ = function (selector, root) { return (root || document).querySelector(selector); };

  function escHtml(s) {
    return String(s == null ? "" : s)
      .replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;").replace(/"/g, "&quot;");
  }

  function formatDate(iso) {
    if (!iso) return "—";
    var d = new Date(iso);
    if (isNaN(d.getTime())) return "—";
    return d.toLocaleString("en-US", {
      year: "numeric", month: "short", day: "numeric",
      hour: "2-digit", minute: "2-digit", timeZone: "America/Vancouver",
    });
  }

  // ----- DOM bootstrap -----
  $("[data-slot=\"ticker\"]").textContent = ticker;
  $("[data-slot=\"ticker-crumb\"]").textContent = ticker;
  document.title = ticker + " on the Halvren Checklist | Halvren Capital";

  function setStatus(msg, isError) {
    var el = $("[data-slot=\"status\"]");
    if (!el) return;
    el.textContent = msg;
    el.classList.toggle("cscore-status--error", !!isError);
  }

  // ----- header (top metadata strip) -----
  function showHeader(payload) {
    var hdr = $("[data-slot=\"header\"]");
    hdr.hidden = false;
    $("[data-slot=\"ticker-mono\"]").textContent = payload.ticker;
    $("[data-slot=\"exchange\"]").textContent = payload.exchange || "Exchange unknown";
    $("[data-slot=\"generated-at\"]").textContent =
      "Generated " + formatDate(payload.generated_at) + " · " + (payload.model_version || "");

    var passEl = $("[data-slot=\"pass-count\"]");
    if (passEl) passEl.innerHTML = "";  // hero band carries the big pass count now

    var watermarkRow = $("[data-slot=\"watermark-row\"]");
    var watermark = $("[data-slot=\"watermark\"]");
    if (payload.on_coverage) {
      watermark.textContent = "On the desk";
      watermark.classList.add("cscore-watermark--coverage");
      watermarkRow.hidden = false;
    } else {
      watermark.textContent = "Machine read. Not principal-reviewed.";
      watermark.classList.remove("cscore-watermark--coverage");
      watermarkRow.hidden = false;
    }
  }

  // ----- hero band: large pass count + italic summary -----
  function renderHero(payload) {
    var hero = $("[data-slot=\"hero\"]");
    if (!hero) return;
    var pass = (payload.overall && typeof payload.overall.pass_count === "number")
      ? payload.overall.pass_count
      : (payload.answers || []).filter(function (a) { return a.status === "pass"; }).length;
    var summary = (payload.overall && payload.overall.summary) || "";
    hero.hidden = false;
    hero.innerHTML =
      '<div class="cscore-hero-band">' +
        '<div class="cscore-hero-passrow">' +
          '<span class="cscore-hero-num">' + escHtml(String(pass)) + '</span>' +
          '<span class="cscore-hero-slash">/</span>' +
          '<span class="cscore-hero-denom">10</span>' +
          '<span class="cscore-hero-label">PASS</span>' +
        '</div>' +
        (summary
          ? '<p class="cscore-hero-summary">' + escHtml(summary) + '</p>'
          : '') +
        (!payload.on_coverage
          ? '<p class="cscore-hero-watermark">Machine read. Not principal-reviewed.</p>'
          : '') +
      '</div>';
  }

  // ----- per-answer card -----
  function answerCard(a, sideAtt) {
    var status = (a.status === "pass" || a.status === "not_yet" || a.status === "fail") ? a.status : "null";
    var sideAttr = sideAtt ? ' data-side="' + sideAtt + '"' : '';
    var srcHtml = "";
    if (a.source) {
      var url = a.source.url || "";
      var label = a.source.label || (typeof a.source === "string" ? a.source : "");
      if (url) {
        srcHtml = '<a href="' + escHtml(url) + '" target="_blank" rel="noopener noreferrer">' + escHtml(label || url) + '</a>';
      } else if (label) {
        srcHtml = '<span class="cscore-source-ref">' + escHtml(label) + '</span>';
      }
    }
    return (
      '<div class="cscore-row" data-q="' + a.q + '"' + sideAttr + ' data-status="' + status + '">' +
        '<span class="cscore-q-num">' + String(a.q).padStart(2, "0") + '</span>' +
        '<div class="cscore-row-body">' +
          '<div class="cscore-row-head">' +
            '<span class="cscore-circle" data-status="' + status + '" aria-hidden="true"></span>' +
            '<p class="cscore-q-text" data-q-text="' + a.q + '">' + escHtml(a.question || "") + '</p>' +
          '</div>' +
          '<p class="cscore-note">' + escHtml(a.note || "") + '</p>' +
          (srcHtml ? '<p class="cscore-source"><span class="cscore-source-label">Source</span> ' + srcHtml + '</p>' : '') +
        '</div>' +
      '</div>'
    );
  }

  function principalCard(q, scoringByQ, qText) {
    var s = scoringByQ[q] || { q: q, status: null, note: null };
    var status = (s.status === "pass" || s.status === "not_yet" || s.status === "fail") ? s.status : "null";
    return (
      '<div class="cscore-row" data-q="' + q + '" data-side="principal" data-status="' + status + '">' +
        '<span class="cscore-q-num">' + String(q).padStart(2, "0") + '</span>' +
        '<div class="cscore-row-body">' +
          '<div class="cscore-row-head">' +
            '<span class="cscore-circle" data-status="' + status + '" aria-hidden="true"></span>' +
            '<p class="cscore-q-text" data-q-text="' + q + '">' + escHtml(qText || "") + '</p>' +
          '</div>' +
          '<p class="cscore-note">' + escHtml(s.note || "Pending principal review.") + '</p>' +
        '</div>' +
      '</div>'
    );
  }

  function renderMachineColumn(answers) {
    var sorted = answers.slice().sort(function (a, b) { return a.q - b.q; });
    return sorted.map(function (a) { return answerCard(a, "machine"); }).join("");
  }

  function renderPrincipalColumn(opData) {
    var scoring = (opData && opData.checklist && opData.checklist.scoring) || [];
    var byQ = {};
    scoring.forEach(function (s) { byQ[s.q] = s; });
    var qText = (window.__HALVREN_QUESTIONS__ || []).reduce(function (acc, q) {
      acc[q.q] = stripCanonicalHtml(q.question_html); return acc;
    }, {});
    var rows = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10].map(function (q) {
      return principalCard(q, byQ, qText[q]);
    }).join("");
    var commentary = (opData && opData.checklist && opData.checklist.pillar_commentary) || {};
    var commentaryHtml = ["I", "II", "III"].map(function (k) {
      return commentary[k] ? '<p class="doc-p" style="margin-bottom:var(--space-3)">' + commentary[k] + '</p>' : "";
    }).join("");
    return rows + (commentaryHtml ? '<div class="cscore-pillar-commentary">' + commentaryHtml + '</div>' : "");
  }

  // strip the principal's <em>...</em> for plain-text rendering inside cards;
  // the question text is intentionally not italicized in the result-page cards.
  function stripCanonicalHtml(s) {
    return String(s || "")
      .replace(/<em[^>]*>/g, "").replace(/<\/em>/g, "")
      .replace(/<[^>]+>/g, "")
      .replace(/&amp;/g, "&").replace(/&ldquo;|&rdquo;/g, "\"")
      .replace(/&mdash;/g, "—").replace(/&middot;/g, "·").replace(/&nbsp;/g, " ");
  }

  // ----- gutter ticks: agree (hairline tick) / diverge (diamond) -----
  function renderGutter(payload, opData) {
    if (!opData || !opData.checklist || !opData.checklist.scoring) return;
    var byQ = {};
    opData.checklist.scoring.forEach(function (s) { byQ[s.q] = s.status; });
    var machineByQ = {};
    (payload.answers || []).forEach(function (a) { machineByQ[a.q] = a.status; });

    var grid = $("[data-slot=\"grid\"]");
    if (!grid) return;
    grid.classList.add("cscore-grid--has-gutter");

    // Build a small column of marks aligned by q. Inserted between the two cols.
    var marks = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10].map(function (q) {
      var m = machineByQ[q];
      var p = byQ[q];
      var verdict = (m && p && m === p)
        ? "agree"
        : (m && p && m !== p) ? "diverge" : "missing";
      var glyph = verdict === "agree"
        ? '<span class="cscore-gutter-tick" aria-hidden="true"></span>'
        : verdict === "diverge"
          ? '<span class="cscore-gutter-diamond" aria-hidden="true"></span>'
          : '<span class="cscore-gutter-missing" aria-hidden="true"></span>';
      var label = verdict === "agree" ? "agree" : verdict === "diverge" ? "differ" : "no principal read yet";
      return (
        '<div class="cscore-gutter-row" data-q="' + q + '" data-verdict="' + verdict + '">' +
          glyph +
          '<span class="cscore-gutter-label sr-only">Q' + q + ': ' + label + '</span>' +
        '</div>'
      );
    }).join("");

    var gutter = document.createElement("div");
    gutter.className = "cscore-gutter";
    gutter.setAttribute("aria-label", "Per-question agreement between machine and principal");
    gutter.innerHTML = marks;

    var existing = grid.querySelector(".cscore-gutter");
    if (existing) existing.remove();
    grid.appendChild(gutter);
  }

  // ----- main render -----
  function render(payload, opData) {
    setStatus(""); $("[data-slot=\"status\"]").hidden = true;
    showHeader(payload);
    renderHero(payload);

    var grid = $("[data-slot=\"grid\"]");
    grid.hidden = false;

    var twovoices = $("[data-slot=\"twovoices\"]");
    var hasPrincipal = !!(opData && opData.checklist);
    if (hasPrincipal) twovoices.hidden = false;

    if (hasPrincipal) {
      grid.classList.add("cscore-grid--two");
      grid.classList.remove("cscore-grid--one");
      grid.innerHTML =
        '<div class="cscore-col cscore-col--machine">' +
          '<header class="cscore-col-head">' +
            '<p class="cscore-col-eyebrow">The read · Machine</p>' +
            '<p class="cscore-col-meta">' + escHtml(payload.model_version || "") + '</p>' +
          '</header>' +
          renderMachineColumn(payload.answers) +
        '</div>' +
        '<div class="cscore-col cscore-col--principal">' +
          '<header class="cscore-col-head">' +
            '<p class="cscore-col-eyebrow">The read · Principal</p>' +
            (payload.coverage_research_url
              ? '<p class="cscore-col-meta">Full writeup at <a href="' + escHtml(payload.coverage_research_url) + '">' + escHtml(payload.coverage_research_url) + '</a></p>'
              : '<p class="cscore-col-meta">Quarterly review</p>') +
          '</header>' +
          renderPrincipalColumn(opData) +
        '</div>';
      renderGutter(payload, opData);
      var breadth = $("[data-slot=\"breadth-line\"]");
      if (breadth) breadth.hidden = false;
    } else {
      grid.classList.add("cscore-grid--one");
      grid.classList.remove("cscore-grid--two");
      grid.innerHTML =
        '<div class="cscore-col cscore-col--machine">' +
          '<header class="cscore-col-head">' +
            '<p class="cscore-col-eyebrow">The read · Machine</p>' +
            '<p class="cscore-col-meta">' + escHtml(payload.model_version || "") + '</p>' +
          '</header>' +
          renderMachineColumn(payload.answers) +
        '</div>';
    }

    setupShare(payload);
    $("[data-slot=\"share\"]").hidden = false;
    $("[data-slot=\"subscribe-block\"]").hidden = false;
  }

  function setupShare(payload) {
    var url = window.location.href;
    var pass = payload.overall && typeof payload.overall.pass_count === "number"
      ? payload.overall.pass_count
      : (payload.pass_count != null ? payload.pass_count : "?");
    var text = "Halvren Checklist — " + payload.ticker + ": " + pass + "/10 passed (machine read).";

    var copyBtn = document.querySelector('[data-share="copy"]');
    if (copyBtn) {
      copyBtn.addEventListener("click", function () {
        if (navigator.clipboard && navigator.clipboard.writeText) {
          navigator.clipboard.writeText(url).then(function () {
            copyBtn.textContent = "Copied";
            setTimeout(function () { copyBtn.textContent = "Copy link"; }, 2000);
          });
        } else {
          window.prompt("Copy this URL:", url);
        }
      });
    }
    var x = document.querySelector('[data-share="x"]');
    if (x) x.href = "https://twitter.com/intent/tweet?text=" + encodeURIComponent(text) + "&url=" + encodeURIComponent(url);
    var li = document.querySelector('[data-share="linkedin"]');
    if (li) li.href = "https://www.linkedin.com/sharing/share-offsite/?url=" + encodeURIComponent(url);
  }

  // ----- network -----
  function fetchScore() {
    return fetch("/api/checklist/score", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ ticker: ticker }),
    }).then(function (r) {
      return r.json().then(function (data) {
        if (!r.ok) throw Object.assign(new Error("score request failed"), { payload: data, status: r.status });
        return data;
      });
    });
  }

  function fetchPrincipal(payload) {
    if (!payload.on_coverage || !payload.coverage_research_url) return Promise.resolve(null);
    var slug = payload.coverage_research_url.replace(/^\/research\//, "").replace(/\/$/, "");
    if (!slug) return Promise.resolve(null);
    return fetch("/data/operators/" + slug + ".json")
      .then(function (r) { return r.ok ? r.json() : null; })
      .catch(function () { return null; });
  }

  function fetchQuestions() {
    return fetch("/content/checklist.json")
      .then(function (r) { return r.ok ? r.json() : null; })
      .then(function (j) { if (j && j.questions) window.__HALVREN_QUESTIONS__ = j.questions; })
      .catch(function () { /* silent */ });
  }

  // ----- run -----
  setStatus("Reading filings via web search…");
  fetchQuestions();
  fetchScore()
    .then(function (payload) {
      return fetchPrincipal(payload).then(function (opData) { render(payload, opData); });
    })
    .catch(function (err) {
      var msg = "The machine read did not complete.";
      if (err && err.payload && err.payload.error) {
        msg = err.payload.error.message || msg;
        if (err.payload.error.code === "rate_limited") {
          msg = "Rate limit reached: 5 scores per IP per hour. Try again in under an hour.";
        } else if (err.payload.error.code === "invalid_ticker") {
          msg = "Ticker did not validate. Use uppercase symbols like CCO, CNQ, RY, BNS, NTR, or NYSE/TSX-style suffixes (TECK.B, BIP.UN).";
        }
      }
      setStatus(msg, true);
    });
})();

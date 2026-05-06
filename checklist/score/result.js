// /checklist/score/result.js
//
// Client-side renderer for the /checklist/score/<ticker> page.
// 1. Reads window.__HALVREN_TICKER__ (set inline by api/checklist/page.js)
// 2. POSTs /api/checklist/score
// 3. Renders the 10-question machine column
// 4. If the ticker is on coverage, fetches /data/operators/<slug>.json and
//    renders the principal column side-by-side ("Two voices on the same name").
// 5. Wires share buttons (copy URL, X/Twitter, LinkedIn).
//
// No framework. No build step. ES2017+ syntax (modern browsers only).

(function () {
  var ticker = window.__HALVREN_TICKER__;
  if (!ticker) return;

  var $ = function (selector, root) {
    return (root || document).querySelector(selector);
  };

  var STATUS_LABEL = { pass: "Pass", not_yet: "Not yet", fail: "Fail" };

  function escHtml(s) {
    return String(s == null ? "" : s)
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;");
  }

  function formatDate(iso) {
    if (!iso) return "—";
    var d = new Date(iso);
    if (isNaN(d.getTime())) return "—";
    return d.toLocaleString("en-US", {
      year: "numeric",
      month: "short",
      day: "numeric",
      hour: "2-digit",
      minute: "2-digit",
      timeZone: "America/Vancouver",
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

  function showHeader(payload) {
    var hdr = $("[data-slot=\"header\"]");
    hdr.hidden = false;
    $("[data-slot=\"ticker-mono\"]").textContent = payload.ticker;
    $("[data-slot=\"exchange\"]").textContent = payload.exchange || "Exchange unknown";
    $("[data-slot=\"generated-at\"]").textContent = "Generated " + formatDate(payload.generated_at);

    var pass = typeof payload.pass_count === "number" ? payload.pass_count : null;
    if (pass == null) pass = (payload.answers || []).filter(function (a) { return a.status === "pass"; }).length;
    $("[data-slot=\"pass-count\"]").innerHTML = '<strong>' + pass + " / 10</strong> passed";

    var watermark = $("[data-slot=\"watermark\"]");
    if (payload.on_coverage) {
      watermark.textContent = "Machine read · Principal commentary below";
      watermark.classList.add("cscore-watermark--coverage");
    } else {
      watermark.textContent = "Machine read. Not principal-reviewed.";
    }
  }

  // ----- column renderers -----
  function statusPill(status) {
    var s = (status === "pass" || status === "not_yet" || status === "fail") ? status : "null";
    var label = STATUS_LABEL[s] || "Pending";
    return (
      '<span class="cscore-pill cscore-pill--' + s + '">' +
        '<span class="cscore-dot" data-status="' + s + '" aria-hidden="true"></span>' +
        escHtml(label) +
      '</span>'
    );
  }

  function renderMachineColumn(answers) {
    var sorted = answers.slice().sort(function (a, b) { return a.q - b.q; });
    var rows = sorted.map(function (a) {
      var src = String(a.source || "");
      var srcHtml;
      if (/^https?:\/\//.test(src)) {
        srcHtml = '<a href="' + escHtml(src) + '" target="_blank" rel="noopener noreferrer">' + escHtml(src) + '</a>';
      } else {
        srcHtml = '<span class="cscore-source-ref">' + escHtml(src) + '</span>';
      }
      return (
        '<div class="cscore-row">' +
          '<span class="cscore-q-num">' + String(a.q).padStart(2, "0") + '</span>' +
          '<div>' +
            '<p class="cscore-q-text" data-q="' + a.q + '"></p>' +
            '<div class="cscore-row-meta">' + statusPill(a.status) + '</div>' +
            '<p class="cscore-note">' + escHtml(a.note || "") + '</p>' +
            '<p class="cscore-source"><span class="cscore-source-label">Source</span> ' + srcHtml + '</p>' +
          '</div>' +
        '</div>'
      );
    }).join("");
    return rows;
  }

  function renderPrincipalColumn(opData) {
    var scoring = (opData && opData.checklist && opData.checklist.scoring) || [];
    var byQ = {};
    scoring.forEach(function (s) { byQ[s.q] = s; });

    var rows = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10].map(function (q) {
      var s = byQ[q] || { q: q, status: null, note: null };
      return (
        '<div class="cscore-row">' +
          '<span class="cscore-q-num">' + String(q).padStart(2, "0") + '</span>' +
          '<div>' +
            '<p class="cscore-q-text" data-q="' + q + '"></p>' +
            '<div class="cscore-row-meta">' + statusPill(s.status) + '</div>' +
            '<p class="cscore-note">' + escHtml(s.note || "Pending principal review.") + '</p>' +
          '</div>' +
        '</div>'
      );
    }).join("");

    var commentary = (opData && opData.checklist && opData.checklist.pillar_commentary) || {};
    var commentaryHtml = ['I', 'II', 'III'].map(function (k) {
      return commentary[k] ? '<p class="doc-p" style="margin-bottom:var(--space-3)">' + commentary[k] + '</p>' : '';
    }).join("");

    return rows + (commentaryHtml ? '<div class="cscore-pillar-commentary">' + commentaryHtml + '</div>' : '');
  }

  function fillQuestionText() {
    var qs = window.__HALVREN_QUESTIONS__ || [];
    if (!qs.length) return;
    var byQ = {};
    qs.forEach(function (q) { byQ[q.q] = q.question_html; });
    document.querySelectorAll('[data-q]').forEach(function (el) {
      var q = parseInt(el.getAttribute('data-q'), 10);
      if (byQ[q]) el.innerHTML = byQ[q];
    });
  }

  // ----- main render -----
  function render(payload, opData) {
    showHeader(payload);
    setStatus(""); $("[data-slot=\"status\"]").hidden = true;

    var grid = $("[data-slot=\"grid\"]");
    grid.hidden = false;

    var twovoices = $("[data-slot=\"twovoices\"]");
    var hasPrincipal = !!(opData && opData.checklist);
    if (hasPrincipal) twovoices.hidden = false;

    if (hasPrincipal) {
      grid.classList.add("cscore-grid--two");
      grid.innerHTML =
        '<div class="cscore-col cscore-col--machine">' +
          '<header class="cscore-col-head">' +
            '<p class="cscore-col-eyebrow">Machine read</p>' +
            '<p class="cscore-col-meta">Sonnet 4.6 · ' + escHtml(payload.model_version || "") + '</p>' +
          '</header>' +
          renderMachineColumn(payload.answers) +
        '</div>' +
        '<div class="cscore-col cscore-col--principal">' +
          '<header class="cscore-col-head">' +
            '<p class="cscore-col-eyebrow">Principal-reviewed</p>' +
            '<p class="cscore-col-meta">' + escHtml(payload.coverage_research_url ? 'Full writeup at ' : '') +
              (payload.coverage_research_url ? '<a href="' + escHtml(payload.coverage_research_url) + '">' + escHtml(payload.coverage_research_url) + '</a>' : '') +
            '</p>' +
          '</header>' +
          renderPrincipalColumn(opData) +
        '</div>';
    } else {
      grid.classList.add("cscore-grid--one");
      grid.innerHTML =
        '<div class="cscore-col cscore-col--machine">' +
          '<header class="cscore-col-head">' +
            '<p class="cscore-col-eyebrow">Machine read</p>' +
            '<p class="cscore-col-meta">Sonnet 4.6 · ' + escHtml(payload.model_version || "") + '</p>' +
          '</header>' +
          renderMachineColumn(payload.answers) +
        '</div>';
    }

    fillQuestionText();
    renderOverall(payload);
    setupShare(payload);
    $("[data-slot=\"share\"]").hidden = false;
    $("[data-slot=\"subscribe-block\"]").hidden = false;
  }

  function renderOverall(payload) {
    if (!payload.overall_summary) return;
    var status = $("[data-slot=\"status\"]");
    status.hidden = false;
    status.classList.add("cscore-overall");
    status.innerHTML =
      '<span class="cscore-overall-eyebrow">The read · machine block</span>' +
      '<span class="cscore-overall-text">' + escHtml(payload.overall_summary) + '</span>';
  }

  function setupShare(payload) {
    var url = window.location.href;
    var pass = payload.pass_count != null ? payload.pass_count : "?";
    var text = "Halvren Checklist — " + payload.ticker + ": " + pass + "/10 passed (machine read).";

    var copyBtn = document.querySelector('[data-share="copy"]');
    if (copyBtn) {
      copyBtn.addEventListener('click', function () {
        if (navigator.clipboard && navigator.clipboard.writeText) {
          navigator.clipboard.writeText(url).then(function () {
            copyBtn.textContent = "Copied ✓";
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
    return fetch('/api/checklist/score', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ ticker: ticker }),
    }).then(function (r) {
      return r.json().then(function (data) {
        if (!r.ok) throw Object.assign(new Error('score request failed'), { payload: data, status: r.status });
        return data;
      });
    });
  }

  function fetchPrincipal(payload) {
    if (!payload.on_coverage || !payload.coverage_research_url) return Promise.resolve(null);
    var slug = payload.coverage_research_url.replace(/^\/research\//, '').replace(/\/$/, '');
    if (!slug) return Promise.resolve(null);
    return fetch('/data/operators/' + slug + '.json')
      .then(function (r) { return r.ok ? r.json() : null; })
      .catch(function () { return null; });
  }

  function fetchQuestions() {
    return fetch('/content/checklist.json')
      .then(function (r) { return r.ok ? r.json() : null; })
      .then(function (j) { if (j && j.questions) window.__HALVREN_QUESTIONS__ = j.questions; })
      .catch(function () { /* silent — question text simply won't render inline */ });
  }

  // ----- run -----
  setStatus('Reading filings via web search…');

  // questions can load in parallel with the score request
  fetchQuestions();

  fetchScore()
    .then(function (payload) {
      return fetchPrincipal(payload).then(function (opData) {
        render(payload, opData);
      });
    })
    .catch(function (err) {
      var msg = 'The machine read did not complete.';
      if (err && err.payload && err.payload.error) {
        msg = err.payload.error.message || msg;
        if (err.payload.error.code === 'rate_limited') {
          msg = 'Rate limit reached: 5 scores per IP per hour. Try again in under an hour.';
        } else if (err.payload.error.code === 'invalid_ticker') {
          msg = 'Ticker did not validate. Use uppercase symbols like CCO, CNQ, RY, BNS, NTR, or NYSE/TSX-style suffixes (TECK.B, BIP.UN).';
        }
      }
      setStatus(msg, true);
    });
})();

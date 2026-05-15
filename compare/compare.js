// /compare/compare.js
//
// Halvren Compare engine. Vanilla JS, no framework.
//
// Reads /data/viz-data.json for the operator universe (ticker → slug,
// FY metrics, Halvren Read, sector, exchange, last_reviewed). If the
// URL contains tickers (/compare/CNQ-vs-ENB), parses them; otherwise
// renders the empty state with two or three autocomplete pickers.
//
// For the checklist verdicts, fetches /data/operators/<slug>.json on
// demand because viz-data.json doesn't carry the per-question text.

(function () {
  "use strict";

  var VIZ_URL = "/data/viz-data.json";
  var OP_URL = function (slug) { return "/data/operators/" + slug + ".json"; };
  var CHECKLIST_URL = "/content/checklist.json";

  var els = {
    empty: document.getElementById("cmp-empty"),
    loading: document.getElementById("cmp-loading"),
    error: document.getElementById("cmp-error"),
    result: document.getElementById("cmp-result"),
    tabs: document.getElementById("cmp-tabs"),
    table: document.getElementById("cmp-table"),
    stack: document.getElementById("cmp-stack"),
    shareImg: document.getElementById("cmp-share-img"),
    shareCopy: document.getElementById("cmp-share-copy"),
    shareEdit: document.getElementById("cmp-share-edit"),
    go: document.getElementById("cmp-go"),
    pickers: document.getElementById("cmp-pickers"),
  };

  var state = {
    universe: null,     // {operators: [...]}
    questions: null,    // [{q, question_html, default_note}, ...]
    picks: [null, null, null],
  };

  function show(el) { if (el) el.removeAttribute("hidden"); }
  function hide(el) { if (el) el.setAttribute("hidden", ""); }

  function fetchJSON(url) {
    return fetch(url, { credentials: "same-origin" }).then(function (r) {
      if (!r.ok) throw new Error("fetch failed: " + url);
      return r.json();
    });
  }

  function band(score) {
    if (score == null) return "amber";
    if (score >= 75) return "green";
    if (score >= 50) return "amber";
    return "red";
  }

  function tickersFromUrl() {
    var path = window.location.pathname.replace(/\/+$/, "");
    var m = path.match(/^\/compare\/(.+)$/);
    if (!m) return [];
    var raw = decodeURIComponent(m[1]);
    var parts = raw.split(/-vs-/i).map(function (s) { return s.trim().toUpperCase(); }).filter(Boolean);
    return parts;
  }

  function findByTicker(tkr) {
    if (!tkr || !state.universe) return null;
    var t = tkr.toUpperCase();
    var ops = state.universe.operators || [];
    for (var i = 0; i < ops.length; i++) {
      if (ops[i].ticker.toUpperCase() === t) return ops[i];
    }
    return null;
  }

  function escapeHtml(s) {
    return String(s == null ? "" : s).replace(/[&<>"']/g, function (c) {
      return { "&": "&amp;", "<": "&lt;", ">": "&gt;", "\"": "&quot;", "'": "&#39;" }[c];
    });
  }

  function pillKey(o) { return o.ticker; }

  function renderHeader(o) {
    var b = band(o.halvren_read);
    var read = o.halvren_read == null ? "—" : o.halvren_read;
    var rev = o.last_reviewed_iso ? o.last_reviewed_iso.slice(0, 7) : "—";
    return (
      '<div class="cmp-cell cmp-cell--head" data-op="' + escapeHtml(pillKey(o)) + '">' +
        '<span class="cmp-h-tkr">' + escapeHtml(o.ticker) + '</span>' +
        '<span class="cmp-h-name">' + escapeHtml(o.short_name) + '</span>' +
        '<span class="cmp-h-meta">' + escapeHtml(o.sector + " · " + (o.sub_industry || "")) + '</span>' +
        '<span class="cmp-h-meta">' + escapeHtml(o.exchange || "") + '</span>' +
        '<span class="cmp-h-meta">Last reviewed ' + escapeHtml(rev) + '</span>' +
        '<span class="cmp-h-read" data-band="' + b + '">' + read + '</span>' +
        '<span class="cmp-h-read-label">Halvren Read · ' + read + ' / 100</span>' +
      '</div>'
    );
  }

  function renderTableSection(ops, opData) {
    var n = ops.length;
    var grid = "cols-" + n;
    var rows = [];

    // top-left label cell + one head per op
    rows.push('<div class="cmp-cell cmp-cell--label">Operator</div>' + ops.map(renderHeader).join(""));

    // numeric rows
    var numericRows = [
      { label: "FY 2025 period",  key: function(o){ return o.fy25_period; } },
      { label: "Revenue",         key: function(o){ return o.fy25_revenue; } },
      { label: "FCF / earnings",  key: function(o){ return o.fy25_fcf || o.fy25_earnings; } },
      { label: "Dividend",        key: function(o){ return o.dividend_signal; } },
      { label: "Yrs of raises",   key: function(o){ return o.dividend_streak_years ? o.dividend_streak_years : "—"; } },
      { label: "ND / EBITDA",     key: function(o){ return o.net_debt_signal; } },
      { label: "Market cap",      key: function(o){ return o.market_cap_usd_b == null ? "—" : "$" + Math.round(o.market_cap_usd_b) + "B"; } },
    ];
    numericRows.forEach(function (r) {
      var cells = ops.map(function (o) {
        return '<div class="cmp-cell cmp-cell--num">' + escapeHtml(r.key(o) || "—") + '</div>';
      });
      rows.push('<div class="cmp-cell cmp-cell--label">' + escapeHtml(r.label) + '</div>' + cells.join(""));
    });

    // 10 checklist rows
    state.questions.forEach(function (q) {
      var cells = ops.map(function (o, i) {
        var data = opData[o.slug] || {};
        var scoring = (data.checklist && data.checklist.scoring) || [];
        var entry = scoring.find ? scoring.find(function (s) { return s.q === q.q; }) : null;
        var verdict = entry ? entry.status : null;
        var note = (entry && entry.note) || q.default_note;
        return (
          '<div class="cmp-cell cmp-cell--checklist">' +
            '<span class="cmp-chip" data-v="' + (verdict || "null") + '">' + (verdict === "pass" ? "Pass" : verdict === "not_yet" ? "Not yet" : verdict === "fail" ? "Fail" : "—") + '</span>' +
            '<p class="cmp-c-note">' + escapeHtml(note) + '</p>' +
          '</div>'
        );
      });
      rows.push('<div class="cmp-cell cmp-cell--label">Q' + q.q + ' · ' + stripHtml(q.question_html).slice(0, 64) + (stripHtml(q.question_html).length > 64 ? "…" : "") + '</div>' + cells.join(""));
    });

    els.table.className = "cmp-table " + grid;
    els.table.innerHTML = rows.join("");
  }

  function stripHtml(s) { var d = document.createElement("div"); d.innerHTML = s; return d.textContent || ""; }

  function renderMobileStack(ops, opData) {
    // Tabs
    els.tabs.innerHTML = ops.map(function (o, i) {
      return '<button type="button" role="tab" aria-pressed="' + (i === 0 ? "true" : "false") + '" data-idx="' + i + '">' + escapeHtml(o.ticker) + '</button>';
    }).join("");
    Array.prototype.forEach.call(els.tabs.querySelectorAll("button"), function (b) {
      b.addEventListener("click", function () {
        Array.prototype.forEach.call(els.tabs.querySelectorAll("button"), function (x) { x.setAttribute("aria-pressed", x === b ? "true" : "false"); });
        els.stack.setAttribute("data-active", b.getAttribute("data-idx"));
      });
    });

    // Stack cards
    var cards = ops.map(function (o, i) {
      var data = opData[o.slug] || {};
      var b = band(o.halvren_read);
      var read = o.halvren_read == null ? "—" : o.halvren_read;
      var rows = [
        ["Period", o.fy25_period],
        ["Revenue", o.fy25_revenue || "—"],
        ["FCF / earnings", o.fy25_fcf || o.fy25_earnings || "—"],
        ["Dividend", o.dividend_signal || "—"],
        ["Yrs of raises", o.dividend_streak_years ? o.dividend_streak_years : "—"],
        ["ND / EBITDA", o.net_debt_signal || "—"],
        ["Market cap", o.market_cap_usd_b == null ? "—" : "$" + Math.round(o.market_cap_usd_b) + "B"],
      ];
      var rowsHtml = rows.map(function (r) { return '<div class="cmp-card-row"><span class="cmp-card-row-l">' + escapeHtml(r[0]) + '</span><span class="cmp-card-row-r">' + escapeHtml(r[1]) + '</span></div>'; }).join("");
      // checklist
      var chk = state.questions.map(function (q) {
        var sc = (data.checklist && data.checklist.scoring) || [];
        var e = sc.find ? sc.find(function (s) { return s.q === q.q; }) : null;
        var v = e ? e.status : null;
        return '<div class="cmp-card-row"><span class="cmp-card-row-l">Q' + q.q + '</span><span class="cmp-chip" data-v="' + (v || "null") + '">' + (v === "pass" ? "Pass" : v === "not_yet" ? "Not yet" : v === "fail" ? "Fail" : "—") + '</span></div>';
      }).join("");
      return '<div class="cmp-card" data-op="' + i + '">' +
        '<div><span class="cmp-h-tkr" style="font-family:var(--font-mono);color:var(--color-gold);font-size:var(--text-base)">' + escapeHtml(o.ticker) + '</span></div>' +
        '<div class="cmp-h-name" style="font-family:var(--font-display);font-size:var(--text-lg);letter-spacing:-0.01em">' + escapeHtml(o.short_name) + '</div>' +
        '<div class="cmp-h-meta" style="font-size:11px;color:var(--color-text-muted)">' + escapeHtml(o.sector + " · " + (o.sub_industry || "")) + '</div>' +
        '<div class="cmp-h-read" data-band="' + b + '" style="font-family:var(--font-display);font-size:var(--text-3xl);line-height:1;letter-spacing:-0.02em;font-weight:600;margin:var(--space-3) 0">' + read + '</div>' +
        '<div style="font-size:10px;letter-spacing:0.12em;text-transform:uppercase;color:var(--color-text-muted);margin-bottom:var(--space-3)">Halvren Read · ' + read + ' / 100</div>' +
        rowsHtml +
        chk +
      '</div>';
    }).join("");
    els.stack.innerHTML = cards;
  }

  function render(ops, opData) {
    hide(els.empty); hide(els.loading); hide(els.error);
    renderTableSection(ops, opData);
    renderMobileStack(ops, opData);
    show(els.result);
    var tickers = ops.map(function (o) { return o.ticker; });
    var canonical = "/compare/" + tickers.join("-vs-");
    var ogPath = "/api/og/compare/" + tickers.join("-");
    els.shareImg.href = ogPath;
    els.shareImg.setAttribute("download", "halvren-compare-" + tickers.join("-") + ".png");
    els.shareCopy.onclick = function () {
      var url = window.location.origin + canonical;
      if (navigator.clipboard) {
        navigator.clipboard.writeText(url).then(function () {
          els.shareCopy.textContent = "Copied";
          setTimeout(function () { els.shareCopy.textContent = "Copy permalink"; }, 1600);
        });
      }
    };
    // Update browser URL
    if (window.location.pathname !== canonical) {
      try { window.history.replaceState({}, "", canonical); } catch (e) {}
    }
    document.title = "Compare " + tickers.join(" vs ") + " — Halvren Capital";
  }

  function loadOperators(slugs) {
    return Promise.all(slugs.map(function (s) { return fetchJSON(OP_URL(s)).catch(function () { return null; }); }))
      .then(function (arr) {
        var out = {};
        slugs.forEach(function (s, i) { if (arr[i]) out[s] = arr[i]; });
        return out;
      });
  }

  function showEmpty() {
    hide(els.loading); hide(els.error); hide(els.result);
    show(els.empty);
    initPickers();
  }

  function initPickers() {
    if (els.pickers.dataset.bound) return;
    els.pickers.dataset.bound = "1";
    var ops = (state.universe && state.universe.operators) || [];

    Array.prototype.forEach.call(els.pickers.querySelectorAll(".cmp-picker"), function (picker) {
      var slot = parseInt(picker.querySelector("input").getAttribute("data-slot"), 10);
      var input = picker.querySelector("input");
      var list = picker.querySelector(".cmp-results");

      input.addEventListener("input", function () {
        var q = (input.value || "").toLowerCase().trim();
        if (!q) { list.setAttribute("data-open", "false"); list.innerHTML = ""; state.picks[slot] = null; updateGo(); return; }
        var matches = ops.filter(function (o) {
          return o.ticker.toLowerCase().indexOf(q) === 0
              || o.short_name.toLowerCase().indexOf(q) !== -1
              || o.sector.toLowerCase().indexOf(q) === 0;
        }).slice(0, 8);
        list.innerHTML = matches.map(function (o) {
          return '<li role="option" data-ticker="' + escapeHtml(o.ticker) + '"><span class="cmp-r-tkr">' + escapeHtml(o.ticker) + '</span><span class="cmp-r-name">' + escapeHtml(o.short_name) + '</span></li>';
        }).join("");
        list.setAttribute("data-open", matches.length ? "true" : "false");
      });

      list.addEventListener("click", function (e) {
        var li = e.target.closest && e.target.closest("li");
        if (!li) return;
        var tkr = li.getAttribute("data-ticker");
        input.value = tkr;
        list.setAttribute("data-open", "false");
        state.picks[slot] = tkr;
        updateGo();
      });

      input.addEventListener("blur", function () {
        setTimeout(function () { list.setAttribute("data-open", "false"); }, 150);
      });
    });

    els.go.addEventListener("click", function () {
      var picks = state.picks.filter(Boolean);
      if (picks.length < 2) return;
      window.location.href = "/compare/" + picks.join("-vs-");
    });
  }

  function updateGo() {
    var n = state.picks.filter(Boolean).length;
    els.go.disabled = n < 2;
  }

  function showError() {
    hide(els.loading); hide(els.empty); hide(els.result);
    show(els.error);
  }

  function go(tickers) {
    show(els.loading);
    hide(els.empty); hide(els.error); hide(els.result);
    var resolved = tickers.map(findByTicker).filter(Boolean);
    if (resolved.length < 2) { showError(); return; }
    var slugs = resolved.map(function (o) { return o.slug; });
    loadOperators(slugs).then(function (opData) { render(resolved, opData); });
  }

  Promise.all([fetchJSON(VIZ_URL), fetchJSON(CHECKLIST_URL).catch(function () { return null; })])
    .then(function (res) {
      state.universe = res[0];
      // questions may be 404 if /content/ isn't public; fall back to a shipped copy
      state.questions = (res[1] && res[1].questions) || INLINE_QUESTIONS;
      var tk = tickersFromUrl();
      if (tk.length >= 2 && tk.length <= 3) go(tk);
      else showEmpty();
    })
    .catch(function () { showError(); });

  // Inline fallback so the page works even if /content/checklist.json
  // isn't reachable. Kept in sync by hand with /content/checklist.json.
  var INLINE_QUESTIONS = [
    { q: 1, question_html: "Full-cycle FCF",      default_note: "Reported earnings lie in commodities. Ten years of FCF tells the truth." },
    { q: 2, question_html: "Unit economics at trough", default_note: "If the thesis needs a new commodity regime to work, it isn't a business yet." },
    { q: 3, question_html: "Balance sheet at trough", default_note: "The next crisis won't ask what you projected. It asks what you owe and when." },
    { q: 4, question_html: "ROIC on incremental capital", default_note: "ROIC on incremental capital, not reported ROE on the whole book." },
    { q: 5, question_html: "Insider ownership, bought not granted", default_note: "Options are loyalty to a quarter. Open-market purchases are loyalty to a decade." },
    { q: 6, question_html: "Behaviour in 2015 and 2020", default_note: "Every operator on the desk has been stress-tested twice in the last decade. The record is public." },
    { q: 7, question_html: "Comp tied to per-share value", default_note: "Pay them for what owners earn, not for what the company spends." },
    { q: 8, question_html: "Visible succession", default_note: "If the next person is invisible, the current person is the whole thesis." },
    { q: 9, question_html: "Cost-curve position", default_note: "First-quartile producers survive the trough. Fourth-quartile are the marginal supply." },
    { q: 10, question_html: "The decade test", default_note: "If the answer in 2035 needs a story, it isn't a business." },
  ];
})();

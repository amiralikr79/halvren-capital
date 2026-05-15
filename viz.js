// Halvren visualization layer — vanilla JS, no deps.
//
// Five vizes, one module:
//   - Cycle Map      mount via data-viz="cycle-map" wrapper
//   - Watchlist      mount via data-viz="watchlist-spread"
//   - Dividend       mount via data-viz="dividend-ladder"
//   - Trough Test    mount via data-viz="trough-test" data-slug="<slug>"
//   - Cost Curve     mount via data-viz="cost-curve" data-commodity="<key>"
//
// Each mount fetches /data/viz-data.json once (cached per page load via
// a shared promise) and renders pure SVG. Hover tooltips, sortable
// columns, sector filters — all native browser, no library.
//
// Brand-doc compliant: no emoji, custom SVG only, --bg/--ink/--muted/
// --line/--green/--red/--gold tokens, mobile fallback per viz.

(function () {
  "use strict";

  // ----- shared data fetch ----------------------------------------------
  var DATA_PROMISE = null;
  function loadData() {
    if (DATA_PROMISE) return DATA_PROMISE;
    DATA_PROMISE = fetch("/data/viz-data.json", { credentials: "omit" })
      .then(function (r) { return r.ok ? r.json() : null; })
      .catch(function () { return null; });
    return DATA_PROMISE;
  }

  // ----- small helpers ---------------------------------------------------
  function svgEl(name, attrs, text) {
    var ns = "http://www.w3.org/2000/svg";
    var el = document.createElementNS(ns, name);
    if (attrs) for (var k in attrs) el.setAttribute(k, attrs[k]);
    if (text != null) el.textContent = text;
    return el;
  }
  function el(tag, cls, text) {
    var e = document.createElement(tag);
    if (cls) e.className = cls;
    if (text != null) e.textContent = text;
    return e;
  }
  function fmtBn(v) {
    if (v == null) return "—";
    if (typeof v === "string") return v;
    return v >= 100 ? Math.round(v) + "B" : (v.toFixed(1) + "B");
  }

  // ============================================================
  // 1. CYCLE MAP
  //   x = cost-curve quartile (1..4, left = best)
  //   y = balance-sheet-health (0..100, top = healthiest)
  //   r = log market cap
  // ============================================================
  function mountCycleMap(host, data) {
    if (!host) return;
    host.innerHTML = "";

    var operators = (data && data.operators) || [];
    var withData = operators.filter(function (o) {
      return o.cost_curve_quartile != null && o.balance_sheet_health != null;
    });
    var excluded = operators.length - withData.length;

    var sectors = ["All", "Energy", "Materials", "Infrastructure"];
    var activeSector = "All";

    // header + filter chips
    var head = el("div", "viz-cyclemap-head");
    var caption = el("p", "viz-eyebrow", "Halvren Cycle Map");
    var sub = el("p", "viz-sub");
    sub.innerHTML = 'Cost-curve quartile (x) versus balance-sheet health at trough pricing (y). Bubble size scales with market cap. <a href="/cycle-map">Full page →</a>';
    head.appendChild(caption);
    head.appendChild(sub);
    var chipRow = el("div", "viz-chips");
    sectors.forEach(function (s) {
      var b = el("button", "viz-chip", s);
      b.setAttribute("type", "button");
      b.setAttribute("data-sector", s);
      b.setAttribute("aria-pressed", s === activeSector ? "true" : "false");
      b.addEventListener("click", function () {
        activeSector = s;
        chipRow.querySelectorAll(".viz-chip").forEach(function (x) {
          x.setAttribute("aria-pressed", x.getAttribute("data-sector") === activeSector ? "true" : "false");
        });
        draw();
      });
      chipRow.appendChild(b);
    });
    head.appendChild(chipRow);
    host.appendChild(head);

    // SVG canvas
    var W = 1200, H = 360, PAD_L = 64, PAD_R = 24, PAD_T = 32, PAD_B = 56;
    var svg = svgEl("svg", {
      viewBox: "0 0 " + W + " " + H,
      preserveAspectRatio: "xMidYMid meet",
      role: "img",
      "aria-label": "Halvren Cycle Map: cost-curve quartile by balance-sheet health, sized by market cap.",
    });
    svg.classList.add("viz-cyclemap-svg");
    host.appendChild(svg);

    var note = el("p", "viz-foot", excluded > 0
      ? excluded + " operator" + (excluded === 1 ? "" : "s") + " excluded due to data gaps."
      : "All 20 operators plotted from public FY 2025 disclosure and the principal's checklist scoring.");
    host.appendChild(note);

    var tooltip = el("div", "viz-tooltip");
    tooltip.setAttribute("role", "tooltip");
    tooltip.setAttribute("aria-hidden", "true");
    host.appendChild(tooltip);

    function xFor(q) {
      // quartile 1 -> left, 4 -> right
      var inner = W - PAD_L - PAD_R;
      return PAD_L + (inner * (q - 0.5)) / 4;
    }
    function yFor(h) {
      // health 0 -> bottom, 100 -> top
      var inner = H - PAD_T - PAD_B;
      return PAD_T + inner * (1 - h / 100);
    }
    function rFor(capB) {
      if (capB == null) return 6;
      // log scale 5..120 -> radius 6..24
      var lo = Math.log10(2), hi = Math.log10(120);
      var t = (Math.log10(capB) - lo) / (hi - lo);
      return Math.max(6, 6 + t * 18);
    }

    function draw() {
      while (svg.firstChild) svg.removeChild(svg.firstChild);

      // axes — hairline in --line
      var axisStyle = { stroke: "var(--color-divider, #d9d6cf)", "stroke-width": 1, fill: "none" };
      svg.appendChild(svgEl("line", Object.assign({ x1: PAD_L, y1: H - PAD_B, x2: W - PAD_R, y2: H - PAD_B }, axisStyle)));
      svg.appendChild(svgEl("line", Object.assign({ x1: PAD_L, y1: PAD_T, x2: PAD_L, y2: H - PAD_B }, axisStyle)));

      // x-axis labels: Q1..Q4
      for (var i = 1; i <= 4; i++) {
        svg.appendChild(svgEl("text", {
          x: xFor(i), y: H - PAD_B + 24,
          "text-anchor": "middle",
          "font-family": "var(--font-body, system-ui)",
          "font-size": 11,
          "letter-spacing": "0.12em",
          fill: "var(--color-text-muted, #6b6b6b)",
        }, "Q" + i));
      }
      // x-axis title
      svg.appendChild(svgEl("text", {
        x: (PAD_L + (W - PAD_R)) / 2, y: H - 12,
        "text-anchor": "middle",
        "font-family": "var(--font-body, system-ui)",
        "font-size": 10,
        "letter-spacing": "0.14em",
        "text-transform": "uppercase",
        fill: "var(--color-text-faint, #bab9b4)",
      }, "COST CURVE — FIRST QUARTILE LEFT"));

      // y-axis ticks at 25/50/75
      [25, 50, 75].forEach(function (v) {
        svg.appendChild(svgEl("line", {
          x1: PAD_L, x2: W - PAD_R, y1: yFor(v), y2: yFor(v),
          stroke: "var(--color-divider, #d9d6cf)", "stroke-width": 1, "stroke-dasharray": "2 4", opacity: 0.5,
        }));
        svg.appendChild(svgEl("text", {
          x: PAD_L - 10, y: yFor(v) + 4,
          "text-anchor": "end",
          "font-family": "var(--font-mono, ui-monospace)",
          "font-size": 11,
          fill: "var(--color-text-muted, #6b6b6b)",
        }, v));
      });
      // y-axis title (rotated)
      svg.appendChild(svgEl("text", {
        x: 16, y: (PAD_T + (H - PAD_B)) / 2,
        "text-anchor": "middle",
        transform: "rotate(-90 16 " + ((PAD_T + (H - PAD_B)) / 2) + ")",
        "font-family": "var(--font-body, system-ui)",
        "font-size": 10,
        "letter-spacing": "0.14em",
        fill: "var(--color-text-faint, #bab9b4)",
      }, "BALANCE-SHEET HEALTH AT TROUGH"));

      // dots
      var hex = (data && data.sector_hex) || {};
      withData.forEach(function (o) {
        if (activeSector !== "All" && o.sector !== activeSector) return;
        var dot = svgEl("circle", {
          cx: xFor(o.cost_curve_quartile),
          cy: yFor(o.balance_sheet_health),
          r: rFor(o.market_cap_usd_b),
          fill: hex[o.sector] || "var(--color-text, #1a1a1a)",
          "fill-opacity": 0.78,
          stroke: "var(--color-bg, #f7f6f2)",
          "stroke-width": 1.5,
          tabindex: 0,
        });
        dot.classList.add("viz-dot");
        dot.setAttribute("data-slug", o.slug);
        dot.setAttribute("data-ticker", o.ticker);
        dot.setAttribute("data-sector", o.sector);
        dot.setAttribute("data-rev", o.fy25_revenue || "—");
        dot.setAttribute("data-verdict", o.halvren_verdict);
        dot.style.cursor = "pointer";
        dot.style.transition = "fill-opacity 200ms ease-out, r 200ms ease-out";
        var aria = o.ticker + " — " + o.sector + " — verdict " + o.halvren_verdict;
        dot.setAttribute("aria-label", aria);
        dot.addEventListener("mouseenter", function () { showTip(o, dot); });
        dot.addEventListener("focus",      function () { showTip(o, dot); });
        dot.addEventListener("mouseleave", hideTip);
        dot.addEventListener("blur",       hideTip);
        dot.addEventListener("click", function () {
          window.location.href = "/research/" + o.slug;
        });
        dot.addEventListener("keydown", function (e) {
          if (e.key === "Enter" || e.key === " ") {
            e.preventDefault();
            window.location.href = "/research/" + o.slug;
          }
        });
        svg.appendChild(dot);

        // ticker label
        var label = svgEl("text", {
          x: xFor(o.cost_curve_quartile) + rFor(o.market_cap_usd_b) + 4,
          y: yFor(o.balance_sheet_health) + 4,
          "font-family": "var(--font-mono, ui-monospace)",
          "font-size": 11,
          fill: "var(--color-text, #1a1a1a)",
          "pointer-events": "none",
        }, o.ticker);
        svg.appendChild(label);
      });
    }

    function showTip(o, dot) {
      var hostRect = host.getBoundingClientRect();
      var dotRect = dot.getBoundingClientRect();
      var readLine = o.halvren_read != null
        ? '<span class="vt-meta">Halvren Read: <em>' + o.halvren_read + ' / 100</em></span>'
        : '';
      tooltip.innerHTML =
        '<span class="vt-ticker">' + o.ticker + '</span>' +
        '<span class="vt-sector">' + o.sector + ' · ' + (o.sub_industry || "") + '</span>' +
        '<span class="vt-meta">Revenue ' + (o.fy25_revenue || "—") + '</span>' +
        '<span class="vt-meta">Verdict: <em>' + o.halvren_verdict + '</em></span>' +
        readLine;
      var x = dotRect.left - hostRect.left + dotRect.width / 2;
      var y = dotRect.top - hostRect.top - 8;
      tooltip.style.left = x + "px";
      tooltip.style.top  = y + "px";
      tooltip.style.transform = "translate(-50%, -100%)";
      tooltip.setAttribute("data-visible", "true");
      tooltip.removeAttribute("hidden");
      tooltip.setAttribute("aria-hidden", "false");
    }
    function hideTip() {
      tooltip.removeAttribute("data-visible");
      tooltip.setAttribute("hidden", "");
      tooltip.setAttribute("aria-hidden", "true");
    }

    // mobile fallback: sector-grouped list
    var mobile = el("div", "viz-cyclemap-mobile");
    var sectorList = ["Energy", "Materials", "Infrastructure"];
    sectorList.forEach(function (s) {
      var sec = el("section", "viz-mobile-sector");
      sec.appendChild(el("h3", "viz-mobile-sectorname", s));
      var ul = el("ul", "viz-mobile-list");
      withData.filter(function (o) { return o.sector === s; })
        .sort(function (a, b) {
          // first-quartile + healthiest first
          if (a.cost_curve_quartile !== b.cost_curve_quartile) return a.cost_curve_quartile - b.cost_curve_quartile;
          return b.balance_sheet_health - a.balance_sheet_health;
        })
        .forEach(function (o) {
          var li = el("li");
          var a = document.createElement("a");
          a.href = "/research/" + o.slug;
          a.innerHTML =
            '<span class="vm-tkr">' + o.ticker + '</span>' +
            '<span class="vm-meta">Q' + o.cost_curve_quartile + ' · ' +
            'BS ' + o.balance_sheet_health + ' · ' +
            '<em>' + o.halvren_verdict + '</em></span>';
          li.appendChild(a);
          ul.appendChild(li);
        });
      sec.appendChild(ul);
      mobile.appendChild(sec);
    });
    host.appendChild(mobile);

    draw();
  }

  // ============================================================
  // 2. WATCHLIST SPREAD — Bloomberg-style sortable table
  // ============================================================
  function mountWatchlist(host, data) {
    if (!host) return;
    host.innerHTML = "";

    var operators = (data && data.operators) || [];

    var head = el("div", "viz-spread-head");
    head.appendChild(el("p", "viz-eyebrow", "The Halvren Spread"));
    var sub = el("p", "viz-sub");
    sub.innerHTML = "Every operator in one frame. Click a column to sort, click a row to read the desk's writeup.";
    head.appendChild(sub);
    host.appendChild(head);

    var wrap = el("div", "viz-spread-wrap");
    var table = el("table", "viz-spread");
    var COLS = [
      { k: "ticker",   l: "Ticker",     mono: true,  key: function(o){ return o.ticker; } },
      { k: "exchange", l: "Exchange",   key: function(o){ return o.exchange; } },
      { k: "sector",   l: "Sector",     key: function(o){ return o.sector; } },
      { k: "mcap",     l: "Mkt Cap",    mono: true,  num: true, key: function(o){ return o.market_cap_usd_b; }, fmt: function(v){ return v == null ? "—" : "$" + (v >= 100 ? Math.round(v) : v.toFixed(0)) + "B"; } },
      { k: "rev",      l: "FY25 Rev",   mono: true,  key: function(o){ return o.fy25_revenue || ""; } },
      { k: "fcf",      l: "FY25 FCF",   mono: true,  key: function(o){ return o.fy25_fcf || ""; } },
      { k: "div",      l: "Div",        mono: true,  key: function(o){ return o.dividend_signal || ""; } },
      { k: "streak",   l: "Yrs",        mono: true,  num: true, key: function(o){ return o.dividend_streak_years || 0; }, fmt: function(v){ return v ? v : "—"; } },
      { k: "nd",       l: "ND/EBITDA",  mono: true,  key: function(o){ return o.net_debt_signal || ""; } },
      { k: "insider",  l: "Insider",    mono: true,  num: true, key: function(o){ return o.insider_score_0_10; }, fmt: function(v){ return v + "/10"; } },
      { k: "rev_iso",  l: "Reviewed",   mono: true,  key: function(o){ return o.last_reviewed_iso || ""; }, fmt: function(v){ return v ? v.slice(0, 7) : "—"; } },
      { k: "read",     l: "Halvren Read", mono: true, num: true, key: function(o){ return o.halvren_read; }, fmt: function(v){ return v == null ? "—" : v; }, band: true },
      { k: "verdict",  l: "Verdict",    chip: true,  key: function(o){ return o.halvren_verdict; } },
    ];

    var sortKey = "mcap", sortDir = -1;

    var thead = el("thead");
    var hr = el("tr");
    COLS.forEach(function (c) {
      var th = el("th", "viz-spread-th" + (c.mono ? " mono" : ""));
      th.textContent = c.l;
      th.setAttribute("data-key", c.k);
      th.setAttribute("tabindex", "0");
      th.style.cursor = "pointer";
      th.addEventListener("click", function () { setSort(c.k); });
      th.addEventListener("keydown", function (e) { if (e.key === "Enter" || e.key === " ") { e.preventDefault(); setSort(c.k); } });
      hr.appendChild(th);
    });
    thead.appendChild(hr);
    table.appendChild(thead);
    var tbody = el("tbody");
    table.appendChild(tbody);
    wrap.appendChild(table);
    host.appendChild(wrap);

    // mobile card view container
    var cards = el("div", "viz-spread-cards");
    host.appendChild(cards);

    function setSort(k) { sortDir = (sortKey === k) ? -sortDir : -1; sortKey = k; render(); }

    function render() {
      var col = COLS.find(function (c) { return c.k === sortKey; });
      var rows = operators.slice().sort(function (a, b) {
        var av = col.key(a), bv = col.key(b);
        if (av == null) return 1;
        if (bv == null) return -1;
        if (col.num) return (av - bv) * sortDir;
        return String(av).localeCompare(String(bv)) * sortDir;
      });

      // table body
      tbody.innerHTML = "";
      rows.forEach(function (o) {
        var tr = el("tr");
        tr.setAttribute("data-slug", o.slug);
        tr.style.cursor = "pointer";
        tr.addEventListener("click", function () { window.location.href = "/research/" + o.slug; });
        COLS.forEach(function (c) {
          var td = el("td", c.mono ? "mono" : "");
          if (c.chip) {
            var chip = el("span", "viz-chip-verdict");
            chip.setAttribute("data-verdict", c.key(o));
            chip.textContent = c.key(o);
            td.appendChild(chip);
          } else {
            var v = c.key(o);
            td.textContent = c.fmt ? c.fmt(v) : (v == null || v === "" ? "—" : v);
            if (c.band && v != null) {
              var b = v >= 75 ? "green" : (v >= 50 ? "amber" : "red");
              td.setAttribute("data-band", b);
            }
          }
          tr.appendChild(td);
        });
        tbody.appendChild(tr);
      });

      // mark sorted header
      thead.querySelectorAll("th").forEach(function (th) {
        if (th.getAttribute("data-key") === sortKey) {
          th.setAttribute("aria-sort", sortDir === -1 ? "descending" : "ascending");
        } else {
          th.removeAttribute("aria-sort");
        }
      });

      // mobile cards: two key metrics + verdict
      cards.innerHTML = "";
      rows.forEach(function (o) {
        var card = el("a", "viz-spread-card");
        card.href = "/research/" + o.slug;
        var readBand = o.halvren_read == null ? "" : (o.halvren_read >= 75 ? "green" : (o.halvren_read >= 50 ? "amber" : "red"));
        card.innerHTML =
          '<div class="card-row">' +
            '<span class="card-tkr">' + o.ticker + '</span>' +
            '<span class="viz-chip-verdict" data-verdict="' + o.halvren_verdict + '">' + o.halvren_verdict + '</span>' +
          '</div>' +
          '<div class="card-row card-name">' + o.short_name + '</div>' +
          '<div class="card-row card-meta">' +
            '<span>' + o.sector + ' · ' + o.sub_industry + '</span>' +
            '<span class="mono">$' + (o.market_cap_usd_b == null ? "—" : Math.round(o.market_cap_usd_b) + "B") + '</span>' +
          '</div>' +
          (o.halvren_read != null
            ? '<div class="card-row card-meta"><span>Halvren Read</span><span class="mono" data-band="' + readBand + '">' + o.halvren_read + ' / 100</span></div>'
            : '');
        cards.appendChild(card);
      });
    }

    render();
  }

  // ============================================================
  // 3. DIVIDEND LADDER — horizontal bars of consecutive raises
  // ============================================================
  function mountDividendLadder(host, data) {
    if (!host) return;
    host.innerHTML = "";

    var rows = ((data && data.operators) || [])
      .filter(function (o) { return o.dividend_streak_years && o.dividend_streak_years > 0; })
      .sort(function (a, b) { return b.dividend_streak_years - a.dividend_streak_years; });

    var head = el("div", "viz-ladder-head");
    head.appendChild(el("p", "viz-eyebrow", "The Dividend Ladder"));
    var sub = el("p", "viz-sub", "Consecutive years of dividend increases through end-2025. Sourced from public proxy filings.");
    head.appendChild(sub);
    host.appendChild(head);

    var maxYears = rows.length ? rows[0].dividend_streak_years : 1;
    var list = el("div", "viz-ladder-list");
    rows.forEach(function (o) {
      var item = el("a", "viz-ladder-row");
      item.href = "/research/" + o.slug;
      var pct = Math.max(8, Math.round((o.dividend_streak_years / maxYears) * 100));
      var troughs = (o.dividend_troughs || []).join(", ");
      item.innerHTML =
        '<span class="ld-tkr">' + o.ticker + '</span>' +
        '<span class="ld-name">' + o.short_name + '</span>' +
        '<span class="ld-bar"><span class="ld-bar-fill" style="width:' + pct + '%"></span></span>' +
        '<span class="ld-years mono">' + o.dividend_streak_years + " yrs" + '</span>' +
        '<span class="ld-troughs">' + (troughs ? "survived " + troughs : "") + '</span>';
      list.appendChild(item);
    });
    host.appendChild(list);
  }

  // ============================================================
  // 4. TROUGH TEST SPARKLINE — FCF/share over ~12 years, 2015/2020 marked
  // ============================================================
  function mountTroughTest(host, data, slug) {
    if (!host) return;
    var op = (data && data.operators || []).find(function (o) { return o.slug === slug; });
    if (!op || !op.fcf_per_share_series) {
      host.innerHTML = '<p class="viz-foot">FCF/share series not available for ' + (op ? op.ticker : slug) + '.</p>';
      return;
    }
    host.innerHTML = "";

    var series = op.fcf_per_share_series;
    var values = series.series.slice();
    var startYear = series.start_year;
    var currency = series.currency || "USD";
    var years = values.map(function (_, i) { return startYear + i; });

    head_block();

    var W = 600, H = 180, PAD_L = 36, PAD_R = 16, PAD_T = 16, PAD_B = 28;
    var nums = values.filter(function (v) { return v !== null; });
    var minV = Math.min.apply(null, nums.concat([0]));
    var maxV = Math.max.apply(null, nums);
    var range = maxV - minV;
    if (range === 0) range = 1;

    function x(i) { return PAD_L + (i / (values.length - 1)) * (W - PAD_L - PAD_R); }
    function y(v) { return PAD_T + (1 - (v - minV) / range) * (H - PAD_T - PAD_B); }

    var svg = svgEl("svg", {
      viewBox: "0 0 " + W + " " + H,
      preserveAspectRatio: "xMidYMid meet",
      role: "img",
      "aria-label": op.ticker + " FCF per share, " + startYear + " to " + (startYear + values.length - 1),
    });
    svg.classList.add("viz-trough-svg");

    // zero baseline if applicable
    if (minV < 0 && maxV > 0) {
      svg.appendChild(svgEl("line", {
        x1: PAD_L, x2: W - PAD_R, y1: y(0), y2: y(0),
        stroke: "var(--color-divider, #d9d6cf)", "stroke-width": 1, "stroke-dasharray": "2 4",
      }));
    }

    // vertical red lines at 2015 and 2020
    [2015, 2020].forEach(function (yr) {
      var idx = years.indexOf(yr);
      if (idx < 0) return;
      svg.appendChild(svgEl("line", {
        x1: x(idx), x2: x(idx), y1: PAD_T, y2: H - PAD_B,
        stroke: "var(--color-red, #8b2c2c)", "stroke-width": 1, opacity: 0.6, "stroke-dasharray": "3 3",
      }));
      svg.appendChild(svgEl("text", {
        x: x(idx), y: H - 8,
        "text-anchor": "middle",
        "font-family": "var(--font-mono, ui-monospace)",
        "font-size": 10,
        fill: "var(--color-red, #8b2c2c)",
      }, String(yr)));
    });

    // y-axis min/max ticks
    [minV, maxV].forEach(function (v, i) {
      svg.appendChild(svgEl("text", {
        x: PAD_L - 6, y: y(v) + (i === 0 ? -2 : 4),
        "text-anchor": "end",
        "font-family": "var(--font-mono, ui-monospace)",
        "font-size": 10,
        fill: "var(--color-text-muted, #6b6b6b)",
      }, (v >= 0 ? "" : "−") + Math.abs(v).toFixed(1)));
    });

    // build the path, breaking at nulls
    var segments = [], current = [];
    for (var i = 0; i < values.length; i++) {
      if (values[i] === null) {
        if (current.length) segments.push(current);
        current = [];
      } else {
        current.push({ i: i, v: values[i] });
      }
    }
    if (current.length) segments.push(current);

    segments.forEach(function (seg) {
      if (seg.length < 2) return;
      var d = "M " + seg.map(function (p) { return x(p.i) + " " + y(p.v); }).join(" L ");
      svg.appendChild(svgEl("path", {
        d: d,
        fill: "none",
        stroke: "var(--color-text, #1a1a1a)",
        "stroke-width": 1.5,
        "stroke-linecap": "round",
        "stroke-linejoin": "round",
      }));
    });

    // dot at each point
    for (var k = 0; k < values.length; k++) {
      if (values[k] === null) continue;
      svg.appendChild(svgEl("circle", {
        cx: x(k), cy: y(values[k]),
        r: 2.5,
        fill: "var(--color-text, #1a1a1a)",
      }));
    }

    host.appendChild(svg);
    host.appendChild(el("p", "viz-foot",
      "Range: " + (minV >= 0 ? "" : "−") + Math.abs(minV).toFixed(2) + " to " + maxV.toFixed(2) + " " + currency + "/share. " +
      "Source: Halvren reconstruction from public filings."));

    function head_block() {
      var h = el("div", "viz-trough-head");
      h.appendChild(el("p", "viz-eyebrow", "Trough Test"));
      h.appendChild(el("p", "viz-sub", "FCF per share through two full cycles. Red lines mark 2015 and 2020."));
      host.appendChild(h);
    }
  }

  // ============================================================
  // 5. COST CURVE — per-commodity AISC vs cumulative production
  // ============================================================
  function mountCostCurve(host, data, commodity) {
    if (!host) return;
    host.innerHTML = "";

    var curves = (data && data.aisc_curve) || {};
    var spots = (data && data.spot_prices) || {};
    var entries = curves[commodity] || [];
    var spot = spots[commodity];
    var ops = (data && data.operators) || [];
    var byslug = {}; ops.forEach(function (o) { byslug[o.slug] = o; });

    var head = el("div", "viz-cost-head");
    var caption = el("p", "viz-eyebrow", commodity.replace(/_/g, " ").toUpperCase());
    head.appendChild(caption);
    if (spot) {
      head.appendChild(el("p", "viz-sub", "Spot " + spot.price + " " + spot.unit + " (as of May 2026). Each dot is one disclosed operator on the curve."));
    }
    host.appendChild(head);

    if (!entries.length) {
      host.appendChild(el("p", "viz-foot", "No disclosed operators on the Halvren coverage list participate in this curve, or AISC data was not reconcilable from public filings."));
      return;
    }

    // build cumulative production buckets, sort by AISC ascending
    var sorted = entries.slice().sort(function (a, b) { return a.aisc - b.aisc; });
    var totalProd = sorted.reduce(function (sum, e) {
      var p = e.production_mlbs || e.production_mbpd || e.production_moz || 0;
      return sum + p;
    }, 0);
    var cumulative = 0;
    var W = 700, H = 320, PAD_L = 56, PAD_R = 24, PAD_T = 32, PAD_B = 56;
    var maxAisc = Math.max.apply(null, sorted.map(function (e) { return e.aisc; }).concat([spot ? spot.price * 1.3 : 0]));

    function x(prod) { return PAD_L + (prod / Math.max(totalProd, 1)) * (W - PAD_L - PAD_R); }
    function y(v)    { return PAD_T + (1 - v / maxAisc) * (H - PAD_T - PAD_B); }

    var svg = svgEl("svg", {
      viewBox: "0 0 " + W + " " + H,
      preserveAspectRatio: "xMidYMid meet",
      role: "img",
    });
    svg.classList.add("viz-cost-svg");

    // axes
    svg.appendChild(svgEl("line", { x1: PAD_L, y1: H - PAD_B, x2: W - PAD_R, y2: H - PAD_B, stroke: "var(--color-divider, #d9d6cf)", "stroke-width": 1 }));
    svg.appendChild(svgEl("line", { x1: PAD_L, y1: PAD_T, x2: PAD_L, y2: H - PAD_B, stroke: "var(--color-divider, #d9d6cf)", "stroke-width": 1 }));

    // y ticks
    for (var i = 0; i <= 4; i++) {
      var v = (maxAisc * i) / 4;
      svg.appendChild(svgEl("text", {
        x: PAD_L - 8, y: y(v) + 4,
        "text-anchor": "end",
        "font-family": "var(--font-mono, ui-monospace)",
        "font-size": 11,
        fill: "var(--color-text-muted, #6b6b6b)",
      }, Math.round(v)));
    }

    // spot price line
    if (spot) {
      svg.appendChild(svgEl("line", {
        x1: PAD_L, x2: W - PAD_R, y1: y(spot.price), y2: y(spot.price),
        stroke: "var(--color-gold, #a87f3c)", "stroke-width": 1.5, "stroke-dasharray": "4 3",
      }));
      svg.appendChild(svgEl("text", {
        x: W - PAD_R, y: y(spot.price) - 6,
        "text-anchor": "end",
        "font-family": "var(--font-mono, ui-monospace)",
        "font-size": 11,
        fill: "var(--color-gold, #a87f3c)",
      }, "spot " + spot.price));
    }

    // step bars per operator, AISC ascending
    cumulative = 0;
    sorted.forEach(function (e) {
      var prod = e.production_mlbs || e.production_mbpd || e.production_moz || 0;
      var op = byslug[e.slug];
      var xa = x(cumulative);
      var xb = x(cumulative + prod);
      var ya = y(e.aisc);
      var yb = y(0);
      svg.appendChild(svgEl("rect", {
        x: xa, y: ya, width: xb - xa, height: yb - ya,
        fill: "var(--color-text, #1a1a1a)",
        "fill-opacity": 0.78,
        stroke: "var(--color-bg, #f7f6f2)",
        "stroke-width": 1,
      }));
      svg.appendChild(svgEl("text", {
        x: (xa + xb) / 2, y: ya - 6,
        "text-anchor": "middle",
        "font-family": "var(--font-mono, ui-monospace)",
        "font-size": 11,
        fill: "var(--color-text, #1a1a1a)",
      }, op ? op.ticker : e.slug));
      cumulative += prod;
    });

    // x label
    svg.appendChild(svgEl("text", {
      x: (PAD_L + (W - PAD_R)) / 2, y: H - 12,
      "text-anchor": "middle",
      "font-family": "var(--font-body, system-ui)",
      "font-size": 10,
      "letter-spacing": "0.14em",
      fill: "var(--color-text-faint, #bab9b4)",
    }, "CUMULATIVE PRODUCTION →"));

    host.appendChild(svg);
    host.appendChild(el("p", "viz-foot", "Halvren coverage operators only. Curve excludes producers outside the coverage list; full global curve is wider. Disclosures reconciled to FY 2025."));
  }

  // ----- bootstrap -------------------------------------------------------
  function init() {
    var maps        = document.querySelectorAll('[data-viz="cycle-map"]');
    var spreads     = document.querySelectorAll('[data-viz="watchlist-spread"]');
    var ladders     = document.querySelectorAll('[data-viz="dividend-ladder"]');
    var troughs     = document.querySelectorAll('[data-viz="trough-test"]');
    var costCurves  = document.querySelectorAll('[data-viz="cost-curve"]');

    if (!maps.length && !spreads.length && !ladders.length && !troughs.length && !costCurves.length) return;

    loadData().then(function (d) {
      if (!d) {
        document.querySelectorAll('[data-viz]').forEach(function (h) {
          h.innerHTML = '<p class="viz-foot">Halvren data could not be loaded. Try a refresh.</p>';
        });
        return;
      }
      maps.forEach(function (h)       { mountCycleMap(h, d); });
      spreads.forEach(function (h)    { mountWatchlist(h, d); });
      ladders.forEach(function (h)    { mountDividendLadder(h, d); });
      troughs.forEach(function (h)    { mountTroughTest(h, d, h.getAttribute("data-slug")); });
      costCurves.forEach(function (h) { mountCostCurve(h, d, h.getAttribute("data-commodity")); });
    });
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }
})();

// /cost-curve.js
//
// V3-3: hand-written SVG horizontal bar chart for the Halvren cost curve.
//
// Renders into every <div class="cost-curve" data-cost-curve> element on the page.
// On the full /coverage and /coverage/cost-curve pages: renders a subsector toggle
// across all five subsectors. On operator pages: rendered with a single
// data-subsector="<slug>" and data-highlight="<TICKER>" to show one operator's
// position on its specific subsector curve.
//
// Data is fetched from /content/cost-curves/<slug>.json. The chart is empty
// (a "principal to populate" message) when the JSON has no data_points.
// Per the V3-3 no-invent rule: sourced or omitted. The chart degrades gracefully.
//
// No framework. No build step. ES2017+.

(function () {
  var SUBSECTORS = ["oil-sands", "uranium", "copper", "silver", "natural-gas-canada"];
  var SUBSECTOR_LABEL = {
    "oil-sands": "Oil sands",
    "uranium": "Uranium",
    "copper": "Copper",
    "silver": "Silver",
    "natural-gas-canada": "Canadian gas",
  };

  function esc(s) {
    return String(s == null ? "" : s)
      .replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;").replace(/"/g, "&quot;");
  }

  function el(tag, attrs, children) {
    var ns = (tag === "svg" || tag === "g" || tag === "rect" || tag === "line" || tag === "text" || tag === "path");
    var node = ns
      ? document.createElementNS("http://www.w3.org/2000/svg", tag)
      : document.createElement(tag);
    if (attrs) for (var k in attrs) {
      if (k === "className") node.setAttribute("class", attrs[k]);
      else node.setAttribute(k, attrs[k]);
    }
    if (children) for (var i = 0; i < children.length; i++) {
      var c = children[i];
      if (c == null) continue;
      if (typeof c === "string") node.appendChild(document.createTextNode(c));
      else node.appendChild(c);
    }
    return node;
  }

  // fetch + cache subsector JSON
  var cache = {};
  function loadSubsector(slug) {
    if (cache[slug]) return Promise.resolve(cache[slug]);
    return fetch("/content/cost-curves/" + slug + ".json")
      .then(function (r) { return r.ok ? r.json() : null; })
      .then(function (j) { cache[slug] = j; return j; })
      .catch(function () { return null; });
  }

  function renderChart(host, payload, opts) {
    opts = opts || {};
    var highlight = (opts.highlight || "").toUpperCase();

    // clear previous chart but keep the toggle
    var prevSvgWrap = host.querySelector(".cost-curve-svg-wrap");
    if (prevSvgWrap) prevSvgWrap.remove();
    var prevCaption = host.querySelector(".cost-curve-caption");
    if (prevCaption) prevCaption.remove();

    var wrap = document.createElement("div");
    wrap.className = "cost-curve-svg-wrap";
    host.appendChild(wrap);

    if (!payload || !Array.isArray(payload.data_points) || payload.data_points.length === 0) {
      var empty = document.createElement("p");
      empty.className = "cost-curve-empty";
      empty.innerHTML =
        "<strong>Awaiting principal-reviewed data.</strong> The schema for this subsector is in <code>/content/cost-curves/" + esc(payload && payload.subsector || "...") + ".json</code>; data points will be populated from FY 2025 filings before the chart renders.";
      wrap.appendChild(empty);
      addCaption(host, payload);
      return;
    }

    // sort lowest-cost to highest-cost
    var points = payload.data_points.slice().sort(function (a, b) {
      return (a.cost_metric_value || 0) - (b.cost_metric_value || 0);
    });

    // SVG geometry
    var W = 800;
    var leftPad = 80;
    var rightPad = 60;
    var topPad = 28;
    var bottomPad = 36;
    var rowH = 22;
    var H = topPad + bottomPad + rowH * points.length;

    var values = points.map(function (p) { return p.cost_metric_value || 0; });
    var maxV = Math.max.apply(null, values);
    if (payload.spot_value != null && payload.spot_value > maxV) maxV = payload.spot_value;
    maxV = maxV * 1.1; // 10% headroom
    var x = function (v) { return leftPad + (W - leftPad - rightPad) * (v / maxV); };

    var svg = el("svg", {
      "class": "cost-curve-svg",
      "viewBox": "0 0 " + W + " " + H,
      "preserveAspectRatio": "xMidYMid meet",
      "role": "img",
      "aria-label": "Halvren cost curve — " + (SUBSECTOR_LABEL[payload.subsector] || payload.subsector),
    });

    // x-axis baseline
    svg.appendChild(el("line", {
      x1: leftPad, y1: H - bottomPad + 0.5,
      x2: W - rightPad, y2: H - bottomPad + 0.5,
      stroke: "currentColor", "stroke-opacity": "0.18", "stroke-width": "1",
    }));

    // x-axis ticks at 0, 25%, 50%, 75%, 100%
    var ticks = 4;
    for (var i = 0; i <= ticks; i++) {
      var v = (maxV * i) / ticks;
      var tx = x(v);
      svg.appendChild(el("line", {
        x1: tx, y1: H - bottomPad,
        x2: tx, y2: H - bottomPad + 4,
        stroke: "currentColor", "stroke-opacity": "0.18", "stroke-width": "1",
      }));
      svg.appendChild(el("text", {
        x: tx, y: H - bottomPad + 18,
        "class": "cc-axis", "text-anchor": "middle",
      }, [v.toFixed(maxV < 10 ? 2 : (maxV < 100 ? 1 : 0))]));
    }
    // x-axis label
    svg.appendChild(el("text", {
      x: leftPad + (W - leftPad - rightPad) / 2,
      y: H - 4,
      "class": "cc-axis", "text-anchor": "middle",
    }, [payload.metric_label || "Cost"]));

    // bars
    points.forEach(function (p, idx) {
      var y = topPad + idx * rowH;
      var barX = x(0);
      var barW = Math.max(2, x(p.cost_metric_value || 0) - barX);
      var isHalvren = !!p.on_coverage;
      var isHighlight = highlight && p.ticker && p.ticker.toUpperCase() === highlight;
      var cls = "cc-bar " + (isHighlight ? "cc-bar--highlight" : (isHalvren ? "cc-bar--halvren" : "cc-bar--peer"));
      var barNode = el("rect", {
        x: barX, y: y + 4,
        width: barW, height: rowH - 8,
        rx: "1.5",
        "class": cls,
        "data-ticker": p.ticker || "",
        "data-name": p.name || p.ticker || "",
        "data-value": p.cost_metric_value != null ? p.cost_metric_value : "",
        "data-on-coverage": isHalvren ? "true" : "false",
      });
      svg.appendChild(barNode);
      // ticker label above bar (only for halvren names with position_visible !== false)
      if (isHalvren && p.position_visible !== false && p.ticker) {
        svg.appendChild(el("text", {
          x: barX + 4, y: y + 4 + (rowH - 8) / 2 + 3.5,
          "class": "cc-ticker",
        }, [p.ticker]));
      }
      // value at end of bar
      svg.appendChild(el("text", {
        x: x(p.cost_metric_value || 0) + 6,
        y: y + 4 + (rowH - 8) / 2 + 3.5,
        "class": "cc-value",
      }, [String(p.cost_metric_value != null ? p.cost_metric_value : "")]));
    });

    // spot price dashed line
    if (payload.spot_value != null) {
      var sx = x(payload.spot_value);
      svg.appendChild(el("line", {
        x1: sx, y1: topPad - 4,
        x2: sx, y2: H - bottomPad,
        "class": "cc-spot-line",
      }));
      svg.appendChild(el("text", {
        x: sx, y: topPad - 8,
        "class": "cc-spot-label", "text-anchor": "middle",
      }, [payload.spot_label || "Approx. spot"]));
    }

    wrap.appendChild(svg);

    // tooltip
    var tooltip = document.createElement("div");
    tooltip.className = "cost-curve-tooltip";
    tooltip.setAttribute("role", "status");
    wrap.appendChild(tooltip);
    wrap.querySelectorAll("rect.cc-bar").forEach(function (rect) {
      var on = function (ev) {
        var t = rect.getAttribute("data-ticker");
        var n = rect.getAttribute("data-name");
        var v = rect.getAttribute("data-value");
        var isHalv = rect.getAttribute("data-on-coverage") === "true";
        var bb = wrap.getBoundingClientRect();
        var rb = rect.getBoundingClientRect();
        tooltip.innerHTML =
          (t ? "<strong>" + esc(t) + "</strong>" : "<strong>Industry peer</strong>") +
          (n && n !== t ? esc(n) : "") +
          "<br><span>" + esc(v || "—") + " " + esc(payload.metric_short || "") + "</span>" +
          (isHalv && t ? "<br><a href=\"/research/" + esc(slugForTicker(t)) + "\">View research →</a>" : "");
        tooltip.style.left = Math.min(bb.width - 240, Math.max(0, (rb.left - bb.left) + rb.width + 8)) + "px";
        tooltip.style.top  = Math.max(0, (rb.top - bb.top) - 6) + "px";
        tooltip.setAttribute("data-show", "true");
      };
      rect.addEventListener("mouseenter", on);
      rect.addEventListener("focus", on);
      rect.addEventListener("mouseleave", function () { tooltip.removeAttribute("data-show"); });
      rect.addEventListener("blur", function () { tooltip.removeAttribute("data-show"); });
    });

    addCaption(host, payload);
  }

  function addCaption(host, payload) {
    var c = document.createElement("p");
    c.className = "cost-curve-caption";
    c.innerHTML =
      "Cost curve as disclosed in FY 2025 filings. Industry peer data sourced from public industry reporting; the Halvren names are the ones we read filings for. The dashed line is approximate spot. The chart is a teaching tool, not a pricing model.";
    host.appendChild(c);
  }

  // operator slug map (small set; expand as more come on coverage)
  function slugForTicker(t) {
    var T = (t || "").toUpperCase();
    var map = {
      "CCO": "cameco-cco",
      "CNQ": "canadian-natural-cnq",
      "AG":  "first-majestic-ag",
      "ENB": "enbridge-enb",
      "NTR": "nutrien-ntr",
      "EOG": "eog-resources",
    };
    return map[T] || "";
  }

  function buildToggle(host, current) {
    var existing = host.querySelector(".cost-curve-toggle");
    if (existing) existing.remove();
    var bar = document.createElement("div");
    bar.className = "cost-curve-toggle";
    bar.setAttribute("role", "tablist");
    bar.setAttribute("aria-label", "Subsector");
    SUBSECTORS.forEach(function (slug) {
      var b = document.createElement("button");
      b.type = "button";
      b.textContent = SUBSECTOR_LABEL[slug];
      b.setAttribute("data-subsector", slug);
      if (slug === current) b.classList.add("is-active");
      b.addEventListener("click", function () {
        host.setAttribute("data-subsector", slug);
        bar.querySelectorAll("button").forEach(function (x) { x.classList.remove("is-active"); });
        b.classList.add("is-active");
        loadSubsector(slug).then(function (payload) {
          renderChart(host, payload, { highlight: host.getAttribute("data-highlight") });
        });
      });
      bar.appendChild(b);
    });
    host.insertBefore(bar, host.firstChild);
  }

  function init(host) {
    var initial = host.getAttribute("data-subsector") || "uranium";
    var fixed = host.hasAttribute("data-fixed");  // operator-page mini: no toggle
    if (!fixed) buildToggle(host, initial);
    loadSubsector(initial).then(function (payload) {
      renderChart(host, payload, { highlight: host.getAttribute("data-highlight") });
    });
  }

  function bootstrap() {
    var hosts = document.querySelectorAll(".cost-curve[data-cost-curve], .cost-curve--mini");
    hosts.forEach(init);
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", bootstrap);
  } else {
    bootstrap();
  }
})();

// /glossary.js
//
// Halvren glossary inline popovers.
// Scans article text for terms (and aliases) from /data/glossary.json,
// wraps the first occurrence per page in a dotted-underline link, and
// renders a popover on hover (desktop) or tap (mobile, iOS Safari + Android Chrome).
//
// No build-time codegen — runs at page load. Pages opt in by including
// this script with `defer`. Skips inputs, headings, and code blocks so
// the markup stays clean.

(function () {
  "use strict";

  if (window.__halvrenGlossaryInit) return;
  window.__halvrenGlossaryInit = true;

  // Containers we DO scan. Everything outside these stays untouched.
  var SCAN_SELECTORS = [
    "main .doc-article p",
    "main .doc-article li",
    "main .doc-article .doc-pullquote",
    "main .doc-article .doc-p",
    "article .note-body p",
    "article .note-body li",
  ];

  // Elements we never descend into, even inside a scanned container.
  var SKIP_SELECTORS = "a,code,pre,kbd,h1,h2,h3,h4,h5,h6,.glossary-link,.no-glossary";

  var data = null;
  var byKey = null;        // lowercased lookup key → entry
  var sortedKeys = null;   // longest match first
  var seenOnPage = null;   // slugs already wrapped on this page
  var activePop = null;    // currently open popover
  var rootScope = null;    // the root element scanned, for outside-click

  function loadData() {
    return fetch("/data/glossary.json", { credentials: "same-origin" })
      .then(function (r) { return r.ok ? r.json() : null; })
      .then(function (j) {
        if (!j || !j.terms) return null;
        data = j;
        byKey = Object.create(null);
        var keys = [];
        j.terms.forEach(function (t) {
          var k = t.term.toLowerCase();
          byKey[k] = t;
          keys.push(k);
          (t.aliases || []).forEach(function (a) {
            var ak = a.toLowerCase();
            if (!byKey[ak]) {
              byKey[ak] = t;
              keys.push(ak);
            }
          });
        });
        // Longest first so "FCF per share" beats "FCF".
        keys.sort(function (a, b) { return b.length - a.length; });
        sortedKeys = keys;
        return data;
      })
      .catch(function () { return null; });
  }

  function escapeReg(s) {
    return s.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
  }

  function buildPattern() {
    if (!sortedKeys || !sortedKeys.length) return null;
    var parts = sortedKeys.map(function (k) {
      // Most terms are alphabetic. Some include `/` (ND/EBITDA) or numbers (U3O8).
      // Use word boundaries where possible; for terms ending in non-word chars
      // (rare here), fall back to lookarounds.
      return escapeReg(k);
    });
    // Case-insensitive, global. The boundaries are \b...\b which is fine for
    // alphanumeric terms. For terms containing `/`, allow start/end at non-word.
    return new RegExp("(?:\\b|(?<=[\\s,.;:()]))(" + parts.join("|") + ")(?=\\b|[\\s,.;:?!()])", "gi");
  }

  function walkText(root, pattern) {
    if (!root) return;
    var walker = document.createTreeWalker(root, NodeFilter.SHOW_TEXT, {
      acceptNode: function (n) {
        // skip empty
        if (!n.nodeValue || !n.nodeValue.trim()) return NodeFilter.FILTER_REJECT;
        // skip children of skipped elements
        var p = n.parentNode;
        while (p && p !== root) {
          if (p.nodeType === 1 && p.matches && p.matches(SKIP_SELECTORS)) return NodeFilter.FILTER_REJECT;
          p = p.parentNode;
        }
        return NodeFilter.FILTER_ACCEPT;
      },
    });
    var batch = [];
    var node;
    while ((node = walker.nextNode())) batch.push(node);
    batch.forEach(function (n) { replaceInTextNode(n, pattern); });
  }

  function replaceInTextNode(node, pattern) {
    var text = node.nodeValue;
    pattern.lastIndex = 0;
    var match = pattern.exec(text);
    if (!match) return;

    var frag = document.createDocumentFragment();
    var idx = 0;
    var consumed = false;
    do {
      var word = match[1];
      var entry = byKey[word.toLowerCase()];
      if (!entry || seenOnPage[entry.slug]) {
        // term not registered, or already wrapped once — advance
        continue;
      }
      seenOnPage[entry.slug] = true;
      consumed = true;
      // Emit pre-text.
      if (match.index > idx) frag.appendChild(document.createTextNode(text.slice(idx, match.index)));
      var span = document.createElement("button");
      span.type = "button";
      span.className = "glossary-link";
      span.setAttribute("data-glossary-slug", entry.slug);
      span.setAttribute("aria-expanded", "false");
      span.setAttribute("aria-haspopup", "dialog");
      span.textContent = word;
      frag.appendChild(span);
      idx = match.index + word.length;
    } while ((match = pattern.exec(text)));

    if (!consumed) return;
    if (idx < text.length) frag.appendChild(document.createTextNode(text.slice(idx)));
    node.parentNode.replaceChild(frag, node);
  }

  function openPop(btn) {
    var slug = btn.getAttribute("data-glossary-slug");
    var entry = byKey[slug] || null;
    // Build a fresh popover element so it can be re-positioned per anchor.
    if (activePop) closePop();
    if (!entry) return;
    var pop = document.createElement("div");
    pop.className = "glossary-pop";
    pop.setAttribute("role", "dialog");
    pop.setAttribute("data-open", "true");
    pop.innerHTML =
      '<p class="glossary-pop-term">' + escapeHtml(entry.term) + "</p>" +
      '<p class="glossary-pop-def">' + escapeHtml(entry.definition).replace(/&amp;/g, "&") + "</p>" +
      '<p class="glossary-pop-foot"><a href="/glossary#term-' + escapeHtml(entry.slug) + '">&rarr; Read more in the glossary</a></p>';
    document.body.appendChild(pop);
    activePop = { el: pop, anchor: btn };
    position(pop, btn);
    btn.setAttribute("aria-expanded", "true");
    window.addEventListener("scroll", onScroll, true);
    window.addEventListener("resize", onScroll);
  }

  function escapeHtml(s) {
    return String(s || "").replace(/[&<>"']/g, function (c) {
      return { "&": "&amp;", "<": "&lt;", ">": "&gt;", "\"": "&quot;", "'": "&#39;" }[c];
    });
  }

  function position(pop, anchor) {
    var r = anchor.getBoundingClientRect();
    var pw = pop.offsetWidth;
    var ph = pop.offsetHeight;
    var pad = 8;
    var left = r.left + window.scrollX + r.width / 2 - pw / 2;
    var top = r.top + window.scrollY - ph - pad;
    // Clamp to viewport
    var vw = document.documentElement.clientWidth;
    if (left < pad) left = pad;
    if (left + pw > vw - pad) left = vw - pw - pad;
    // If above the fold, flip below
    if (r.top - ph - pad < 8) top = r.bottom + window.scrollY + pad;
    pop.style.left = left + "px";
    pop.style.top = top + "px";
  }

  function onScroll() {
    if (!activePop) return;
    position(activePop.el, activePop.anchor);
  }

  function closePop() {
    if (!activePop) return;
    if (activePop.anchor) activePop.anchor.setAttribute("aria-expanded", "false");
    if (activePop.el && activePop.el.parentNode) activePop.el.parentNode.removeChild(activePop.el);
    activePop = null;
    window.removeEventListener("scroll", onScroll, true);
    window.removeEventListener("resize", onScroll);
  }

  function bind(root) {
    // Single delegated listener; covers desktop click + mobile tap.
    root.addEventListener("click", function (e) {
      var t = e.target;
      while (t && t !== root && !(t.matches && t.matches(".glossary-link"))) t = t.parentNode;
      if (t && t.matches && t.matches(".glossary-link")) {
        e.preventDefault();
        if (activePop && activePop.anchor === t) {
          closePop();
        } else {
          openPop(t);
        }
        return;
      }
      // Tap outside an open popover closes it.
      if (activePop) {
        var inPop = activePop.el.contains(e.target);
        if (!inPop) closePop();
      }
    });
    document.addEventListener("keydown", function (e) {
      if (e.key === "Escape" && activePop) closePop();
    });
  }

  function init() {
    rootScope = document.querySelector("main") || document.body;
    seenOnPage = Object.create(null);
    var pattern = buildPattern();
    if (!pattern) return;
    SCAN_SELECTORS.forEach(function (sel) {
      var nodes = rootScope.querySelectorAll(sel);
      nodes.forEach(function (el) { walkText(el, pattern); });
    });
    bind(document);
  }

  function ready(fn) {
    if (document.readyState === "loading") {
      document.addEventListener("DOMContentLoaded", fn);
    } else {
      fn();
    }
  }

  ready(function () { loadData().then(function () { if (sortedKeys) init(); }); });
})();

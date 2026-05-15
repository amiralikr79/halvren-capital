// Halvren mobile nav — full-screen editorial overlay.
//
// Sprint 8 rebuild. Replaces the prior side-drawer pattern. Below 768px:
//  - hamburger SVG opens a full-screen fade-in overlay
//  - links in display serif, generous spacing
//  - close X in top-right; Escape and link-tap both close
//  - focus trap inside the open overlay
//  - 200ms fade in / 200ms fade out
//
// No libraries. No emoji. Custom SVG only. Respects prefers-reduced-motion.

(function () {
  "use strict";

  function setup() {
    var burger = document.querySelector("[data-nav-open]");
    var overlay = document.getElementById("nav-overlay");
    if (!burger || !overlay) return;

    var closeBtn = overlay.querySelector("[data-nav-close]");
    var links = overlay.querySelectorAll(".nav-overlay-links a");
    var body = document.body;
    var lastFocus = null;

    function focusableInOverlay() {
      return overlay.querySelectorAll("a[href], button:not([disabled])");
    }

    function open() {
      lastFocus = document.activeElement;
      overlay.setAttribute("data-open", "true");
      overlay.removeAttribute("hidden");
      overlay.setAttribute("aria-hidden", "false");
      burger.setAttribute("aria-expanded", "true");
      body.setAttribute("data-nav-locked", "true");
      // focus the close button first so Escape feels natural
      setTimeout(function () {
        if (closeBtn) closeBtn.focus();
      }, 50);
      document.addEventListener("keydown", onKeyDown);
    }

    function close() {
      overlay.removeAttribute("data-open");
      overlay.setAttribute("aria-hidden", "true");
      burger.setAttribute("aria-expanded", "false");
      body.removeAttribute("data-nav-locked");
      document.removeEventListener("keydown", onKeyDown);
      // hide after the fade so it can't catch tab focus
      setTimeout(function () {
        if (!overlay.hasAttribute("data-open")) {
          overlay.setAttribute("hidden", "");
        }
      }, 220);
      if (lastFocus && typeof lastFocus.focus === "function") {
        try { lastFocus.focus(); } catch (e) { /* ignore */ }
      }
    }

    function onKeyDown(e) {
      if (e.key === "Escape" || e.key === "Esc") {
        e.preventDefault();
        close();
        return;
      }
      if (e.key === "Tab") {
        var f = focusableInOverlay();
        if (f.length === 0) return;
        var first = f[0];
        var last = f[f.length - 1];
        if (e.shiftKey && document.activeElement === first) {
          e.preventDefault();
          last.focus();
        } else if (!e.shiftKey && document.activeElement === last) {
          e.preventDefault();
          first.focus();
        }
      }
    }

    burger.addEventListener("click", function (e) {
      e.preventDefault();
      open();
    });

    if (closeBtn) {
      closeBtn.addEventListener("click", function (e) {
        e.preventDefault();
        close();
      });
    }

    links.forEach(function (a) {
      a.addEventListener("click", function () {
        // close immediately so the user sees the destination on its own
        close();
      });
    });

    // tap on the overlay background (the bar bg, links spacer) closes too,
    // but ignore clicks on actual interactive children
    overlay.addEventListener("click", function (e) {
      if (e.target === overlay) close();
    });
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", setup);
  } else {
    setup();
  }
})();

// /notes-extras.js
//
// Two interactions for /notes/<slug>:
//   1. Audio player — wires the play button, scrubber, and time display
//      to the underlying <audio> element. No-op if audio is not playable.
//   2. Tweet thread generator — POSTs to /api/thread/<slug>, renders the
//      6-tweet response in a modal with per-tweet copy + copy-all.
//
// Vanilla JS, no dependencies, defer-loaded.

(function () {
  "use strict";

  // -- Audio player ---------------------------------------------------- //
  function fmtTime(s) {
    if (!isFinite(s) || s < 0) return "0:00";
    var m = Math.floor(s / 60), sec = Math.floor(s % 60);
    return m + ":" + (sec < 10 ? "0" : "") + sec;
  }

  function initPlayer() {
    var section = document.querySelector(".note-audio");
    if (!section) return;
    if (section.getAttribute("data-playable") !== "true") return;
    var audio = section.querySelector(".note-audio-src");
    var play = section.querySelector(".note-audio-play");
    var scrub = section.querySelector(".note-audio-scrubber");
    var elapsed = section.querySelector(".note-audio-elapsed");
    var total = section.querySelector(".note-audio-total");
    if (!audio || !play || !scrub) return;

    play.addEventListener("click", function () {
      if (audio.paused) {
        audio.play().then(function () {
          play.setAttribute("data-state", "playing");
          play.setAttribute("aria-label", "Pause narration");
        }).catch(function () { /* autoplay blocked or load failed; UI stays paused */ });
      } else {
        audio.pause();
        play.setAttribute("data-state", "paused");
        play.setAttribute("aria-label", "Play narration");
      }
    });

    audio.addEventListener("loadedmetadata", function () {
      if (audio.duration && total) total.textContent = fmtTime(audio.duration);
    });
    audio.addEventListener("timeupdate", function () {
      if (!audio.duration) return;
      var pct = (audio.currentTime / audio.duration) * 100;
      scrub.value = String(pct);
      if (elapsed) elapsed.textContent = fmtTime(audio.currentTime);
    });
    audio.addEventListener("ended", function () {
      play.setAttribute("data-state", "paused");
      play.setAttribute("aria-label", "Play narration");
      scrub.value = "0";
      if (elapsed) elapsed.textContent = "0:00";
    });
    scrub.addEventListener("input", function () {
      if (!audio.duration) return;
      audio.currentTime = (parseFloat(scrub.value) / 100) * audio.duration;
    });
  }

  // -- Tweet thread generator ----------------------------------------- //
  function escapeHtml(s) {
    return String(s == null ? "" : s).replace(/[&<>"']/g, function (c) {
      return { "&": "&amp;", "<": "&lt;", ">": "&gt;", "\"": "&quot;", "'": "&#39;" }[c];
    });
  }

  function buildModal() {
    var existing = document.getElementById("thread-modal");
    if (existing) return existing;
    var backdrop = document.createElement("div");
    backdrop.className = "thread-modal-backdrop";
    backdrop.id = "thread-modal-backdrop";
    document.body.appendChild(backdrop);

    var modal = document.createElement("div");
    modal.className = "thread-modal";
    modal.id = "thread-modal";
    modal.setAttribute("role", "dialog");
    modal.setAttribute("aria-modal", "true");
    modal.setAttribute("aria-labelledby", "thread-modal-title");
    modal.innerHTML =
      '<div class="thread-modal-card">' +
        '<div class="thread-modal-head">' +
          '<h2 class="thread-modal-title" id="thread-modal-title">X thread</h2>' +
          '<button class="thread-modal-close" aria-label="Close" type="button">' +
            '<svg viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><path d="M6 6 L18 18 M18 6 L6 18"/></svg>' +
          '</button>' +
        '</div>' +
        '<div class="thread-modal-body" id="thread-modal-body"></div>' +
        '<div class="thread-modal-foot">' +
          '<button class="thread-modal-copy-all" id="thread-modal-copy-all" type="button">Copy all</button>' +
        '</div>' +
      '</div>';
    document.body.appendChild(modal);

    function close() {
      backdrop.setAttribute("data-open", "false");
      modal.setAttribute("data-open", "false");
      document.body.style.overflow = "";
    }
    backdrop.addEventListener("click", close);
    modal.querySelector(".thread-modal-close").addEventListener("click", close);
    modal.addEventListener("click", function (e) { if (e.target === modal) close(); });
    document.addEventListener("keydown", function (e) {
      if (e.key === "Escape" && modal.getAttribute("data-open") === "true") close();
    });
    return modal;
  }

  function openModal() {
    var m = buildModal();
    document.getElementById("thread-modal-backdrop").setAttribute("data-open", "true");
    m.setAttribute("data-open", "true");
    document.body.style.overflow = "hidden";
    return m;
  }

  function copyText(text, btn) {
    var done = function () {
      var orig = btn.textContent;
      btn.setAttribute("data-copied", "true");
      btn.textContent = "Copied";
      setTimeout(function () {
        btn.removeAttribute("data-copied");
        btn.textContent = orig;
      }, 1600);
    };
    if (navigator.clipboard && window.isSecureContext) {
      navigator.clipboard.writeText(text).then(done).catch(function () {});
    } else {
      var ta = document.createElement("textarea");
      ta.value = text;
      ta.style.position = "fixed";
      ta.style.left = "-9999px";
      document.body.appendChild(ta);
      ta.select();
      try { document.execCommand("copy"); done(); } catch (e) {}
      document.body.removeChild(ta);
    }
  }

  function renderTweets(modal, tweets, slug, title) {
    var body = modal.querySelector("#thread-modal-body");
    modal.querySelector("#thread-modal-title").textContent = title || "X thread";
    body.innerHTML = tweets.map(function (t, i) {
      var len = (t || "").length;
      return '<div class="thread-tweet" data-i="' + i + '">' +
        '<span class="thread-tweet-num">' + (i + 1) + ' / ' + tweets.length + '</span>' +
        '<p class="thread-tweet-text">' + escapeHtml(t) + '</p>' +
        '<div class="thread-tweet-foot">' +
          '<span>' + len + ' characters</span>' +
          '<button class="thread-tweet-copy" type="button">Copy</button>' +
        '</div>' +
      '</div>';
    }).join("");
    Array.prototype.forEach.call(body.querySelectorAll(".thread-tweet"), function (card, i) {
      card.querySelector(".thread-tweet-copy").addEventListener("click", function (e) {
        copyText(tweets[i], e.currentTarget);
      });
    });
    modal.querySelector("#thread-modal-copy-all").onclick = function (e) {
      copyText(tweets.join("\n\n"), e.currentTarget);
    };
  }

  function renderError(modal, message) {
    var body = modal.querySelector("#thread-modal-body");
    body.innerHTML = '<div class="thread-modal-error">' + escapeHtml(message || "Something went sideways. Try again in a moment.") + '</div>';
  }

  function initThreadButton() {
    var btn = document.querySelector(".note-thread-btn");
    if (!btn) return;
    btn.addEventListener("click", function () {
      var slug = btn.getAttribute("data-thread-slug");
      var title = btn.getAttribute("data-thread-title");
      if (!slug) return;
      var modal = openModal();
      modal.querySelector("#thread-modal-body").innerHTML =
        '<div class="thread-modal-error">Asking the desk to distill the note&hellip;</div>';
      btn.setAttribute("data-state", "loading");
      fetch("/api/thread/" + encodeURIComponent(slug), { headers: { "Accept": "application/json" } })
        .then(function (r) {
          return r.json().then(function (j) { return { ok: r.ok, body: j }; });
        })
        .then(function (out) {
          btn.removeAttribute("data-state");
          if (out.ok && out.body && Array.isArray(out.body.tweets) && out.body.tweets.length) {
            renderTweets(modal, out.body.tweets, slug, "X thread — " + (title || slug));
          } else {
            renderError(modal, (out.body && out.body.error) || "Couldn't generate the thread right now.");
          }
        })
        .catch(function () {
          btn.removeAttribute("data-state");
          renderError(modal, "Network glitch. Try again in a moment.");
        });
    });
  }

  function ready(fn) {
    if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", fn);
    else fn();
  }

  ready(function () { initPlayer(); initThreadButton(); });
})();

// /lc-sticky.js — dismissible mobile-only LetterCapture footer
//
// Pages that include <div class="lc-sticky" data-lc-sticky>...</div>
// + this script will render the bar on viewports < 768px (the CSS already
// hides it above that). Dismissal persists 30 days in localStorage under
// `halvren-lc-dismissed`. The bar is a quiet footer, not a popup or modal —
// it does not block content or interrupt reading.

(function () {
  var bar = document.querySelector('[data-lc-sticky]');
  if (!bar) return;

  var STORAGE_KEY = 'halvren-lc-dismissed';
  var DISMISS_DAYS = 30;
  var dismissedAt = 0;
  try {
    var raw = localStorage.getItem(STORAGE_KEY);
    if (raw) dismissedAt = parseInt(raw, 10) || 0;
  } catch (e) { /* localStorage blocked — proceed */ }

  var now = Date.now();
  var hideUntil = dismissedAt + DISMISS_DAYS * 24 * 60 * 60 * 1000;
  if (dismissedAt && now < hideUntil) {
    // dismissed within the window — do not show
    return;
  }

  // Show after a short delay so the bar doesn't pop in before page render
  setTimeout(function () {
    bar.setAttribute('data-show', 'true');
  }, 500);

  var dismiss = bar.querySelector('[data-lc-dismiss]');
  if (dismiss) {
    dismiss.addEventListener('click', function () {
      try { localStorage.setItem(STORAGE_KEY, String(Date.now())); }
      catch (e) { /* storage blocked — fall through, bar still hides */ }
      bar.setAttribute('data-show', 'false');
      // remove from tab order entirely after animation
      setTimeout(function () { bar.remove(); }, 200);
    });
  }
})();

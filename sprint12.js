// sprint12.js — visual overhaul interactions.
//   • Halvren Read Mark expand/collapse (hover desktop, tap mobile)
//   • Halvren Read count-up on viewport entry
//   • Constellation idle amber pulse (one random dot every 8-12s)
//   • Diary relative timestamps (client-side, falls back to absolute)
//   • Hero "now reading" typewriter — fetches /data/digest-stream.json
//
// Vanilla JS, no framework, no dependencies. Defer-loaded.
(function(){
"use strict";

var reducedMotion = window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches;

// ---------------------------------------------------------------- //
// 1. Halvren Read Mark — expand into the verdict grid on hover/tap.
// ---------------------------------------------------------------- //
function bindMark(mark){
  if (mark.dataset.markBound) return;
  mark.dataset.markBound = "1";
  var openTimer = null;
  function open(){ mark.setAttribute('data-expanded','true'); }
  function close(){ mark.removeAttribute('data-expanded'); }
  var isTouch = 'ontouchstart' in window || navigator.maxTouchPoints > 0;
  if (isTouch){
    mark.addEventListener('click', function(e){
      e.preventDefault();
      if (mark.getAttribute('data-expanded') === 'true') close();
      else { open(); positionGrid(mark); }
    });
  } else {
    mark.addEventListener('mouseenter', function(){
      clearTimeout(openTimer);
      openTimer = setTimeout(function(){ open(); positionGrid(mark); }, 80);
    });
    mark.addEventListener('mouseleave', function(){
      clearTimeout(openTimer);
      close();
    });
    mark.addEventListener('focus', function(){ open(); positionGrid(mark); });
    mark.addEventListener('blur', function(){ close(); });
  }
}

function positionGrid(mark){
  // No-op for now; if a future variant needs viewport-clamping we'd
  // measure the bounding rect and nudge the expanded card to stay
  // on-screen. Today the marks live inline with reasonable margins.
}

function bindAllMarks(){
  document.querySelectorAll('.hread-mark').forEach(bindMark);
  // Close any open mark on tap-outside.
  document.addEventListener('click', function(e){
    document.querySelectorAll('.hread-mark[data-expanded="true"]').forEach(function(m){
      if (!m.contains(e.target)) m.removeAttribute('data-expanded');
    });
  });
}

// ---------------------------------------------------------------- //
// 2. Count-up on viewport entry — generic for .count-up nodes.
// ---------------------------------------------------------------- //
function bindCountUps(){
  var nodes = document.querySelectorAll('.count-up[data-target]');
  if (!nodes.length || !window.IntersectionObserver) return;
  var io = new IntersectionObserver(function(entries){
    entries.forEach(function(e){
      if (!e.isIntersecting) return;
      var el = e.target;
      var target = parseFloat(el.getAttribute('data-target'));
      if (isNaN(target)) return;
      if (reducedMotion){ el.textContent = formatNum(target, el); io.unobserve(el); return; }
      var dur = 800;
      var start = performance.now();
      function tick(now){
        var p = Math.min(1, (now - start) / dur);
        var eased = 1 - Math.pow(1 - p, 3);
        el.textContent = formatNum(target * eased, el);
        if (p < 1) requestAnimationFrame(tick);
      }
      requestAnimationFrame(tick);
      io.unobserve(el);
    });
  }, { threshold: 0.4 });
  nodes.forEach(function(n){ io.observe(n); });
}

function formatNum(v, el){
  var raw = el.getAttribute('data-target');
  var decimals = raw.indexOf('.') >= 0 ? (raw.length - raw.indexOf('.') - 1) : 0;
  return v.toFixed(decimals);
}

// ---------------------------------------------------------------- //
// 3. Constellation idle pulse — one random dot every 8-12s.
// ---------------------------------------------------------------- //
function bindConstellationPulse(){
  if (reducedMotion) return;
  var dots = Array.prototype.slice.call(document.querySelectorAll('.constellation .cdot'));
  if (!dots.length) return;
  function pulse(){
    var d = dots[Math.floor(Math.random() * dots.length)];
    d.classList.add('is-pulse-amber');
    setTimeout(function(){ d.classList.remove('is-pulse-amber'); }, 600);
    var nextMs = 8000 + Math.floor(Math.random() * 4000);
    setTimeout(pulse, nextMs);
  }
  setTimeout(pulse, 4000 + Math.random() * 2000);
}

// ---------------------------------------------------------------- //
// 4. Relative timestamps. Targets nodes with data-relative-from="YYYY-MM-DD".
// ---------------------------------------------------------------- //
function relativeTime(iso){
  var d = new Date(iso + "T00:00:00Z");
  if (isNaN(d.getTime())) return null;
  var diffMs = Date.now() - d.getTime();
  var s = Math.floor(diffMs / 1000);
  if (s < 60) return s + "s ago";
  var m = Math.floor(s / 60);
  if (m < 60) return m + " min ago";
  var h = Math.floor(m / 60);
  if (h < 24) return h + (h === 1 ? " hour ago" : " hours ago");
  var days = Math.floor(h / 24);
  if (days === 1) return "yesterday";
  if (days < 30) return days + " days ago";
  var months = Math.floor(days / 30);
  if (months < 12) return months + (months === 1 ? " month ago" : " months ago");
  var years = Math.floor(days / 365);
  return years + (years === 1 ? " year ago" : " years ago");
}
function bindRelativeTimes(){
  document.querySelectorAll('[data-relative-from]').forEach(function(el){
    var iso = el.getAttribute('data-relative-from');
    var rel = relativeTime(iso);
    if (!rel) return;
    var holder = el.querySelector('.diary-entry-relative,.desk-latest-relative') || document.createElement('span');
    if (!holder.parentNode){
      holder.className = (el.className.indexOf('desk-latest') >= 0 ? 'desk-latest-relative' : 'diary-entry-relative');
      holder.setAttribute('title', iso);
      el.appendChild(document.createTextNode(' · '));
      el.appendChild(holder);
    }
    holder.textContent = rel;
    holder.setAttribute('title', iso);
  });
}

// ---------------------------------------------------------------- //
// 5. Hero "now reading" typewriter — 3 phrases from digest-stream.
// ---------------------------------------------------------------- //
function bindHeroStream(){
  var holder = document.getElementById('hero-stream-text');
  if (!holder) return;
  if (reducedMotion){ holder.textContent = "the desk is reading"; return; }
  fetch('/data/digest-stream.json', { credentials: 'omit' })
    .then(function(r){ return r.ok ? r.json() : null; })
    .then(function(j){
      var phrases = (j && Array.isArray(j.phrases)) ? j.phrases.slice() : null;
      if (!phrases || !phrases.length){
        // Fallback set — kept in code so the line never breaks.
        phrases = [
          "Reading the desk's queue.",
          "Cross-checking FY 2025 against prior 4Q.",
          "Re-running the checklist on the watchlist.",
        ];
      }
      // Fisher-Yates shuffle, pick 3.
      for (var i = phrases.length - 1; i > 0; i--){ var k = Math.floor(Math.random()*(i+1)); var t = phrases[i]; phrases[i] = phrases[k]; phrases[k] = t; }
      var picked = phrases.slice(0, 3);
      var caret = '<span class="hero-stream-caret" aria-hidden="true"></span>';
      var idx = 0;
      function typePhrase(text, done){
        holder.removeAttribute('data-done');
        var i = 0;
        var charDelay = 40;
        (function step(){
          if (i > text.length){ done && done(); return; }
          holder.innerHTML = text.slice(0, i) + caret;
          i++;
          setTimeout(step, charDelay);
        })();
      }
      function cycle(){
        var phrase = picked[idx % picked.length];
        typePhrase(phrase, function(){
          setTimeout(function(){
            idx++;
            cycle();
          }, 3000);
        });
      }
      cycle();
    })
    .catch(function(){ holder.textContent = "the desk is reading"; });
}

// ---------------------------------------------------------------- //
function ready(fn){ if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', fn); else fn(); }
ready(function(){
  bindAllMarks();
  bindCountUps();
  bindConstellationPulse();
  bindRelativeTimes();
  bindHeroStream();
});

// Expose for re-bind after late DOM updates (e.g. diary inject).
window.__halvrenSprint12 = { bindAllMarks: bindAllMarks, bindRelativeTimes: bindRelativeTimes };
})();

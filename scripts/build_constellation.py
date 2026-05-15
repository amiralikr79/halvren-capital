#!/usr/bin/env python3
"""
build_constellation.py

Sprint 4 — Coverage Constellation hero. Reads the 20 named-universe
operators from coverage.json (plus the legacy EOG), arranges them in
three loose sector clusters with deterministic pseudo-random jitter,
sizes each dot subtly logarithmically by approximate market cap, and
writes:

  components/constellation.html      SVG + mobile-fallback list
  components/constellation.tooltip.js   small vanilla-JS handler

Both fragments are concatenated into index.html by hand (see
scripts/inject_constellation.py for the splice).

The component is deliberately pre-rendered: no client-side layout
computation, no Three.js, no force simulation at runtime. The eye does
not get pulled to it.
"""

from __future__ import annotations

import json
import math
import random
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
COVERAGE = ROOT / "coverage" / "coverage.json"
DATA_OPS = ROOT / "data" / "operators"
OUT_DIR = ROOT / "components"


# --------------------------------------------------------------------------- #
# the 20 named universe + approximate market caps (USD billions, mid-2025).
# All figures are publicly disclosed corporate market values, rounded to the
# nearest billion. They are used solely to size the constellation dots on a
# log scale — readers do not see the numbers, only the relative footprints.
# --------------------------------------------------------------------------- #

# slug -> (display ticker, sector, mkt_cap_usd_b)
UNIVERSE: list[tuple[str, str, str, float]] = [
    # Energy (Canada)
    ("canadian-natural-cnq",     "CNQ",  "Energy",          80.0),
    ("suncor-su",                "SU",   "Energy",          70.0),
    ("cenovus-cve",              "CVE",  "Energy",          45.0),
    ("tourmaline-tou",           "TOU",  "Energy",          25.0),
    ("arc-resources-arx",        "ARX",  "Energy",          15.0),
    ("meg-energy-meg",           "MEG",  "Energy",           5.0),
    ("cameco-cco",               "CCO",  "Energy",          30.0),
    # Energy (U.S.)
    ("occidental-oxy",           "OXY",  "Energy",          50.0),
    # Materials
    ("nutrien-ntr",              "NTR",  "Materials",       25.0),
    ("agnico-eagle-aem",         "AEM",  "Materials",       45.0),
    ("teck-resources-teck",      "TECK", "Materials",       20.0),
    ("west-fraser-wfg",          "WFG",  "Materials",        6.0),
    ("first-majestic-ag",        "AG",   "Materials",        2.0),
    ("freeport-mcmoran-fcx",     "FCX",  "Materials",       60.0),
    # Infrastructure
    ("enbridge-enb",             "ENB",  "Infrastructure", 110.0),
    ("tc-energy-trp",            "TRP",  "Infrastructure",  60.0),
    ("pembina-ppl",              "PPL",  "Infrastructure",  30.0),
    ("fortis-fts",               "FTS",  "Infrastructure",  30.0),
    ("cn-rail-cnr",              "CNR",  "Infrastructure", 120.0),
    ("kinder-morgan-kmi",        "KMI",  "Infrastructure",  60.0),
]

# Cluster anchor points and radii in SVG viewBox units (1200 x 360).
# Energy on the left, Materials in the center, Infrastructure on the right.
CLUSTERS = {
    "Energy":          (260, 180, 170),
    "Materials":       (600, 180, 150),
    "Infrastructure":  (940, 180, 170),
}

VIEW_W = 1200
VIEW_H = 360


def log_radius(cap_b: float) -> float:
    """Map a market cap (USD billions) to a dot radius. Subtly logarithmic.
    Smallest cap maps to ~4px, largest to ~13px."""
    caps = [c for _, _, _, c in UNIVERSE]
    lo, hi = min(caps), max(caps)
    a = math.log10(cap_b)
    a_lo, a_hi = math.log10(lo), math.log10(hi)
    t = (a - a_lo) / (a_hi - a_lo)
    return 4.0 + t * 9.0


def layout(seed: int = 7) -> list[dict]:
    """Deterministic placement: cluster anchor + jittered radial offset.
    Energy stays comfortably below the hero text; clusters are positioned
    horizontally with vertical jitter capped to keep visual density low."""
    rng = random.Random(seed)
    placed: list[tuple[float, float, float]] = []  # x, y, r
    out: list[dict] = []
    for slug, ticker, sector, cap in UNIVERSE:
        cx, cy, cr = CLUSTERS[sector]
        r = log_radius(cap)
        # Try several jittered positions; keep the first that doesn't collide
        for _ in range(60):
            angle = rng.uniform(0, 2 * math.pi)
            radius = rng.uniform(0.15 * cr, cr * 0.95)
            x = cx + math.cos(angle) * radius
            y = cy + math.sin(angle) * radius * 0.55  # vertical squash
            # avoid edges
            x = max(20, min(VIEW_W - 20, x))
            y = max(20, min(VIEW_H - 20, y))
            collide = any(
                math.hypot(x - px, y - py) < (r + pr + 6)
                for px, py, pr in placed
            )
            if not collide:
                break
        placed.append((x, y, r))
        out.append({
            "slug": slug,
            "ticker": ticker,
            "sector": sector,
            "cap_b": cap,
            "x": round(x, 2),
            "y": round(y, 2),
            "r": round(r, 2),
        })
    return out


def load_last_reviewed(slug: str) -> str:
    p = DATA_OPS / f"{slug}.json"
    if not p.exists():
        return ""
    try:
        d = json.loads(p.read_text(encoding="utf-8"))
        return d.get("last_reviewed_iso") or ""
    except Exception:
        return ""


def fmt_short(iso: str) -> str:
    if not iso or len(iso) < 7:
        return "—"
    y, m, _ = iso.split("-", 2)
    months = ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"]
    return f"{months[int(m)-1]} {y}"


def render_svg(positions: list[dict]) -> str:
    rng = random.Random(11)  # animation phase seed — separate from layout
    dots = []
    for p in positions:
        delay = round(rng.uniform(-5, 0), 2)
        last = fmt_short(load_last_reviewed(p["slug"]))
        dots.append(
            f'  <circle class="cdot" '
            f'data-slug="{p["slug"]}" '
            f'data-ticker="{p["ticker"]}" '
            f'data-sector="{p["sector"]}" '
            f'data-last="{last}" '
            f'cx="{p["x"]}" cy="{p["y"]}" r="{p["r"]}" '
            f'tabindex="0" '
            f'style="animation-delay:{delay}s" '
            f'aria-label="{p["ticker"]} — {p["sector"]}"></circle>'
        )
    # cluster eyebrow labels — quiet, in --muted; positioned above each cluster
    label_y = 28
    labels = []
    for sector, (cx, _, _) in CLUSTERS.items():
        labels.append(
            f'  <text class="clabel-cluster" x="{cx}" y="{label_y}" '
            f'text-anchor="middle">{sector.upper()}</text>'
        )
    return (
        f'<svg viewBox="0 0 {VIEW_W} {VIEW_H}" preserveAspectRatio="xMidYMid meet" '
        f'role="img" aria-label="Coverage universe — 20 operators across Energy, Materials, and Infrastructure">\n'
        + "\n".join(labels) + "\n"
        + "\n".join(dots) + "\n"
        f'</svg>'
    )


def render_mobile_list(positions: list[dict]) -> str:
    """Sector-grouped tab list for <768px. No animation."""
    sectors = ["Energy", "Materials", "Infrastructure"]
    tabs = "\n".join(
        f'      <button type="button" data-sector="{s}" '
        f'aria-pressed="{"true" if i == 0 else "false"}">{s}</button>'
        for i, s in enumerate(sectors)
    )
    items = []
    for s in sectors:
        for p in positions:
            if p["sector"] != s:
                continue
            last = fmt_short(load_last_reviewed(p["slug"]))
            items.append(
                f'      <li data-sector="{p["sector"]}"'
                f'{"" if p["sector"] == sectors[0] else " hidden"}>\n'
                f'        <a href="/research/{p["slug"]}">\n'
                f'          <span class="cl-tkr">{p["ticker"]}</span>\n'
                f'          <span class="cl-sector">{p["sector"]} · {last}</span>\n'
                f'        </a>\n'
                f'      </li>'
            )
    return (
        '<div class="constellation-mobile" aria-label="Coverage universe — operator list">\n'
        '    <div class="constellation-mobile-tabs" role="tablist">\n'
        + tabs + "\n"
        '    </div>\n'
        '    <ul class="constellation-mobile-list">\n'
        + "\n".join(items) + "\n"
        '    </ul>\n'
        '  </div>'
    )


def render_full(positions: list[dict]) -> str:
    svg = render_svg(positions)
    mobile = render_mobile_list(positions)
    return (
        '<div class="constellation" aria-label="Halvren coverage constellation">\n'
        '  '
        + svg.replace("\n", "\n  ") + "\n"
        '  <div class="constellation-tooltip" data-tooltip role="tooltip" aria-hidden="true">\n'
        '    <span class="tt-ticker" data-tt-ticker></span>\n'
        '    <span class="tt-sector" data-tt-sector></span>\n'
        '    <span class="tt-meta" data-tt-meta></span>\n'
        '  </div>\n'
        '</div>\n'
        '  ' + mobile + "\n"
    )


JS = '''<script>
(function(){
  var con = document.querySelector('.constellation');
  if (!con) return;
  var tt  = con.querySelector('[data-tooltip]');
  var ttT = con.querySelector('[data-tt-ticker]');
  var ttS = con.querySelector('[data-tt-sector]');
  var ttM = con.querySelector('[data-tt-meta]');

  function show(e){
    var d = e.currentTarget;
    var slug = d.getAttribute('data-slug');
    var ticker = d.getAttribute('data-ticker');
    var sector = d.getAttribute('data-sector');
    var last   = d.getAttribute('data-last');
    ttT.textContent = ticker;
    ttS.textContent = sector;
    ttM.textContent = 'Last reviewed ' + last;
    var rect = d.getBoundingClientRect();
    var hostRect = con.getBoundingClientRect();
    var x = rect.left - hostRect.left + rect.width / 2;
    var y = rect.top  - hostRect.top  - 8;
    tt.style.left = x + 'px';
    tt.style.top  = y + 'px';
    tt.style.transform = 'translate(-50%, -100%)';
    tt.setAttribute('data-visible', 'true');
    tt.setAttribute('aria-hidden', 'false');
    var r = parseFloat(d.getAttribute('r'));
    d.setAttribute('data-rest-r', r);
    d.setAttribute('r', r * 1.7);
  }
  function hide(e){
    tt.removeAttribute('data-visible');
    tt.setAttribute('aria-hidden', 'true');
    var d = e.currentTarget;
    var rest = d.getAttribute('data-rest-r');
    if (rest) d.setAttribute('r', rest);
  }
  function navigate(e){
    var slug = e.currentTarget.getAttribute('data-slug');
    if (slug) window.location.href = '/research/' + slug;
  }
  con.querySelectorAll('.cdot').forEach(function(d){
    d.addEventListener('mouseenter', show);
    d.addEventListener('focus',      show);
    d.addEventListener('mouseleave', hide);
    d.addEventListener('blur',       hide);
    d.addEventListener('click',      navigate);
    d.addEventListener('keydown', function(e){
      if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); navigate(e); }
    });
  });

  // mobile tabs
  var tabsWrap = document.querySelector('.constellation-mobile-tabs');
  if (!tabsWrap) return;
  var items = document.querySelectorAll('.constellation-mobile-list li');
  tabsWrap.querySelectorAll('button').forEach(function(b){
    b.addEventListener('click', function(){
      var s = b.getAttribute('data-sector');
      tabsWrap.querySelectorAll('button').forEach(function(x){
        x.setAttribute('aria-pressed', x === b ? 'true' : 'false');
      });
      items.forEach(function(li){
        if (li.getAttribute('data-sector') === s) li.removeAttribute('hidden');
        else li.setAttribute('hidden', '');
      });
    });
  });
})();
</script>'''


# CSS hook for cluster labels (small thing the page.css block didn't define)
CSS_HOOK = (
    '<style>\n'
    '.constellation .clabel-cluster{font-family:var(--font-body);'
    'font-size:10px;letter-spacing:0.18em;fill:var(--muted);opacity:0.7}\n'
    '</style>'
)


def main() -> int:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    positions = layout()
    html = render_full(positions)
    js   = JS
    (OUT_DIR / "constellation.html").write_text(CSS_HOOK + "\n" + html, encoding="utf-8")
    (OUT_DIR / "constellation.js").write_text(js, encoding="utf-8")
    print(f"wrote {OUT_DIR / 'constellation.html'}")
    print(f"wrote {OUT_DIR / 'constellation.js'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

#!/usr/bin/env python3
"""
_sprint2_seed.py

Sprint 2 seed: emits the 15 new operators that, together with the four
already-published names (CCO, CNQ, AG, ENB) and the existing NTR/EOG
desks, take the coverage universe from 6 published deep operators to 21.

Reads:   (nothing; data is inline)
Writes:  data/operators/<slug>.json     × 15
         content/operators/<slug>.md    × 15

Each operator entry was drafted against /docs/HALVREN_BRAND.md (voice rules,
forbidden-phrase list) and uses publicly disclosed FY 2025 / Q1 2026 figures
where the principal has high confidence. Where a number is approximate or
unconfirmed, the entry uses "(approx.)" or em-dash, per the brand doc.

This script is one-shot. Run once. After the build, the files become the
canonical source of truth; this seed remains in /scripts for provenance.

Run from the repo root:
  python3 scripts/_sprint2_seed.py
"""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT / "data" / "operators"
CONTENT_DIR = ROOT / "content" / "operators"

GENERATED_ISO = "2026-05-14"
REVIEWED_ISO = "2026-05-14"
PUBLISHED_ISO = "2026-04-30"

# --------------------------------------------------------------------------- #
# helper: standard checklist scoring scaffold with statuses + notes
# --------------------------------------------------------------------------- #

def scoring(*pairs):
    """pairs is a sequence of 10 (status, note) tuples for q1..q10."""
    assert len(pairs) == 10, f"need 10 scorecard items, got {len(pairs)}"
    return [
        {"q": i + 1, "status": s, "note": n}
        for i, (s, n) in enumerate(pairs)
    ]


def disclosure(name: str, source: str) -> str:
    return (
        "This writeup is for informational and educational purposes only and is not a "
        "recommendation, solicitation, or price call. The author may hold a position in "
        f"{name} and may transact at any time without notice. Figures are sourced from "
        f"{source}. Where a figure is marked &ldquo;(approx.)&rdquo; or &ldquo;&mdash;&rdquo; "
        "the source disclosure was either unconfirmed or unreported at the time of writing. "
        "See the <a href=\"/terms\">Terms of Use</a> for the full disclaimer. Halvren's "
        "companion writeup may appear on <a href=\"https://substack.com/@halvrencapital\" "
        "target=\"_blank\" rel=\"noopener noreferrer\">Substack</a> at greater length."
    )


BACK_LINK = {"href": "/coverage", "label": "Back to the coverage universe"}


# --------------------------------------------------------------------------- #
# operator dictionaries
# --------------------------------------------------------------------------- #

OPERATORS: list[dict] = []


# === 1. SU — Suncor Energy ================================================== #
OPERATORS.append({
    "slug": "suncor-su",
    "ticker": "SU",
    "exchange": "TSX: SU · NYSE: SU",
    "name": "Suncor Energy Inc.",
    "short_name": "Suncor",
    "url": "https://www.suncor.com/",
    "sector": "Energy",
    "sub_industry": "Oil & Gas",
    "page_eyebrow": "On the desk · Oil sands",
    "headline_html": "Suncor (SU): The integrated reset, read <em>plainly.</em>",
    "page_title": "Suncor (SU) — The integrated reset, read plainly | Halvren Capital",
    "meta_description": "Suncor is Canada's largest integrated oil sands operator and the owner of Petro-Canada retail. Halvren's read on the Kruger-era reset, the refining contribution, and what the cycle has yet to ask of the business.",
    "og_title": "Suncor (SU) — The integrated reset, read plainly",
    "og_description": "Integrated oil sands, upgrading, refining, and Petro-Canada retail. Halvren's under-the-hood read with FY 2025 numbers.",
    "og_image": "/og-research.png",
    "published_iso": PUBLISHED_ISO,
    "modified_iso": REVIEWED_ISO,
    "the_read": {
        "summary": "Canada's largest integrated oil sands operator. Upstream production ~828 Mboe/d (FY 2025 guidance midpoint), four upgrading and refining complexes, ~1,800-station Petro-Canada retail. Rich Kruger (CEO since April 2023) is running a cost and safety reset that the prior five years made necessary.",
        "generated_iso": GENERATED_ISO,
        "source_filing": "Suncor FY 2025 disclosure and Q4 2025 release (February 2026)",
        "principal_reviewed_iso": REVIEWED_ISO,
    },
    "fy_snapshot": {
        "period": "FY 2025",
        "metrics": [
            {"label": "Upstream production", "value": "~828 Mboe/d (guidance mid, approx.)"},
            {"label": "Refining throughput", "value": "~460 Mb/d (approx.)"},
            {"label": "Retail network", "value": "~1,800 Petro-Canada sites"},
            {"label": "FY 2025 net earnings", "value": "— (approx.)"},
            {"label": "Net debt target", "value": "C$8B (announced)"},
            {"label": "Capital return policy", "value": "75% of FCF to shareholders post-target"},
            {"label": "Listings", "value": "TSX: SU · NYSE: SU"},
        ],
    },
    "guidance": None,
    "leadership": {
        "ceo": "Rich Kruger",
        "ceo_since": 2023,
        "chair": None,
        "succession_visible": False,
        "note": "Kruger arrived to fix what five years of complacency broke. The early evidence is operational; the test is whether the discipline survives the next $50 print.",
    },
    "what_we_track": [
        "Mining and in-situ unit operating cost",
        "Refining utilization and downstream contribution",
        "Net debt trajectory toward the C$8B floor",
        "Buyback pace at the post-target return policy",
        "Safety statistics — the reset's first promise",
    ],
    "checklist": {
        "scoring": scoring(
            ("pass",    "Free cash flow through 2015–2020, including the trough. The dividend was cut once (2020) and restored."),
            ("pass",    "Mining and SAGD unit costs work in the C$30s/bbl operating range; the integrated downstream margin smooths the bad quarters."),
            ("pass",    "Investment-grade. Net debt has been walked from C$15B-plus in 2021 toward the C$8B target."),
            ("not_yet", "The 2020–2022 reinvestment record (Fort Hills writedowns, repeated turnaround misses) is the reason Kruger had a job to take."),
            ("not_yet", "Insider ownership is modest. Kruger's open-market behaviour is the more honest signal than the option grants."),
            ("not_yet", "2015: dividend held. 2020: dividend cut by 55%. The cut was rational; the prior over-distribution that forced it was not."),
            ("pass",    "Compensation reset under Kruger is more per-share-aligned than the Williams-era plan it replaced."),
            ("not_yet", "Succession is not visible. Kruger is 67. The bench question is real."),
            ("pass",    "On the mineable oil sands cost curve Suncor sits comfortably first-quartile. The downstream throughput is a hedge the merchant refiners do not have."),
            ("not_yet", "Underwriting at mid-cycle Brent in the US$65–75 range, Suncor compounds. At trough prices the dividend is safe; the growth is not."),
        ),
        "pillar_commentary": {
            "I": "<strong>Pillar I. The business.</strong> FCF through full cycle is real, including 2020. Mining and in-situ unit costs are first-quartile within the oil-sands cohort. The balance sheet is being walked down to the C$8B floor and the 75%-of-FCF return policy kicks in at that point. The honest weakness is ROIC on incremental capital over 2018–2022: Fort Hills underperformed expectations, several turnarounds missed, and the safety record forced the C-suite change. Kruger inherited a business that needed a reset more than a strategy.",
            "II": "<strong>Pillar II. The people.</strong> Suncor is an institutional name, not an owner-operator one. Insider buying is light. The capital allocation record over 2018–2022 is the legitimate concern. Compensation has been re-tilted toward per-share metrics under Kruger, and the operational discipline showing up in the unit-cost numbers is the early proof point. The succession question is unanswered. We watch it.",
            "III": "<strong>Pillar III. The cycle.</strong> Oil sands sit on a long-life, low-decline cost curve that punishes nobody who can wait. The integrated model dampens the worst single-commodity quarter. Underwriting at mid-cycle Brent, Suncor produces meaningful free cash; at trough it still funds the dividend and the capital plan. The decade-out question is what regulatory and demand path Canadian heavy oil follows. That is a Canada question more than a Suncor question.",
        },
    },
    "last_reviewed_iso": REVIEWED_ISO,
    "next_earnings_iso": None,
    "position_disclosure": "may_hold",
    "disclosure_footnote_html": disclosure("Suncor Energy Inc.", "Suncor's FY 2025 disclosure and Q4 2025 release (February 2026)"),
    "back_link": BACK_LINK,
    "related_slugs": ["cenovus-cve", "canadian-natural-cnq"],
    "body_md": (
        "Suncor is the Canadian energy business other Canadian energy businesses still measure themselves against. Upstream mining, in-situ SAGD, four upgrading and refining complexes, and the Petro-Canada retail network. The integrated chain is the moat. It is also the part that, when neglected, produces the kind of accident record and operational drift that forced a CEO change in 2023. We read Suncor as a reset, not a growth story.\n\n"
        "## The business, in one paragraph\n"
        "Suncor produces roughly 828 Mboe/d of upstream barrels, refines about 460 Mb/d in Edmonton, Sarnia, Montreal, and Commerce City, and sells what comes out the back through Petro-Canada at roughly 1,800 sites. The mining and SAGD assets at Base Mine, Fort Hills, MacKay River, and Firebag have effectively infinite reserve life at current rates; the question is operating cost and capital discipline, not geology. Petro-Canada is a high-margin captive demand outlet that most integrated peers in North America would pay to own.\n\n"
        "## What FY 2025 actually said\n"
        "The Kruger thesis is operational. Production targets were met, unit costs trended down, refining utilization improved, and the net debt walk continued toward the announced C$8B floor at which point the capital return policy steps up to 75% of free cash. The number that matters here is not the headline net earnings, which the commodity tape will move around regardless. It is the gap between Suncor's unit cost today and Suncor's unit cost in 2022. That gap is real and it is meaningful.\n\n"
        "## Two things we are reading carefully\n"
        "### 1. Whether the reset is permanent\n"
        "Operational resets in oil and gas are easy to start and hard to maintain through a price <em>up-cycle</em>, which is when discipline most often gets relaxed. The 2026 capital plan and the 2026 unit-cost trajectory are the first two real tests. We watch the variance between guided and actual on capex, opex, and turnaround scope rather than the headline production beat.\n\n"
        "### 2. Refining contribution as a hedge\n"
        "Suncor's downstream throughput is the part the merchant refiners do not have access to in the same way and the part the pure-play oil-sands producers do not have at all. We track refining utilization, crack capture, and the per-barrel realized downstream margin alongside the upstream cost curve. When the integrated chain is working, the bad upstream quarter does not look like a bad Suncor quarter. That is the whole point.\n\n"
        "## What we are watching into FY 2026\n"
        "- <strong>Unit operating cost</strong> at mining and SAGD by site, with particular attention to Fort Hills.\n"
        "- <strong>Net debt trajectory</strong> against the C$8B floor and the timing of the step-up in capital returns.\n"
        "- <strong>Refining utilization</strong> and the per-barrel downstream contribution.\n"
        "- <strong>Safety statistics</strong> — the reset's first promise and the one whose absence forced the C-suite change.\n\n"
        "> Suncor is the business its competitors quietly read most carefully. The reset is the part the market keeps under-pricing because it does not show up in the next quarter."
    ),
})


# === 2. CVE — Cenovus Energy ================================================ #
OPERATORS.append({
    "slug": "cenovus-cve",
    "ticker": "CVE",
    "exchange": "TSX: CVE · NYSE: CVE",
    "name": "Cenovus Energy Inc.",
    "short_name": "Cenovus",
    "url": "https://www.cenovus.com/",
    "sector": "Energy",
    "sub_industry": "Oil & Gas",
    "page_eyebrow": "On the desk · Integrated oil sands",
    "headline_html": "Cenovus (CVE): The Husky integration, <em>finally</em> clean.",
    "page_title": "Cenovus (CVE) — The Husky integration, finally clean | Halvren Capital",
    "meta_description": "Cenovus is the post-Husky integrated, with Christina Lake and Foster Creek upstream and US Lima/Toledo on the refining side. Halvren's read on whether downstream finally contributes instead of dragging.",
    "og_title": "Cenovus (CVE) — The Husky integration, finally clean",
    "og_description": "Integrated oil sands and refining. Halvren's under-the-hood read on FY 2025 numbers, Foster Creek and Christina Lake, and the US refining contribution.",
    "og_image": "/og-research.png",
    "published_iso": PUBLISHED_ISO,
    "modified_iso": REVIEWED_ISO,
    "the_read": {
        "summary": "Integrated oil sands post-2021 Husky combination. ~810 Mboe/d production (FY 2025 mid, approx.) anchored by Christina Lake and Foster Creek SAGD. Downstream throughput ~660 Mb/d across Canadian and US refining. CEO Jon McKenzie since April 2023.",
        "generated_iso": GENERATED_ISO,
        "source_filing": "Cenovus FY 2025 disclosure and Q4 2025 release (February 2026)",
        "principal_reviewed_iso": REVIEWED_ISO,
    },
    "fy_snapshot": {
        "period": "FY 2025",
        "metrics": [
            {"label": "Total production", "value": "~810 Mboe/d (FY 2025 mid, approx.)"},
            {"label": "SAGD weight", "value": "Christina Lake + Foster Creek dominant"},
            {"label": "Refining throughput", "value": "~660 Mb/d (approx.)"},
            {"label": "Net debt target", "value": "C$4.0B (achieved 2024)"},
            {"label": "Capital return policy", "value": "100% of FCF after sustaining post-target"},
            {"label": "Quarterly dividend", "value": "C$0.20/sh base + variable"},
            {"label": "Listings", "value": "TSX: CVE · NYSE: CVE"},
        ],
    },
    "guidance": None,
    "leadership": {
        "ceo": "Jon McKenzie",
        "ceo_since": 2023,
        "chair": None,
        "succession_visible": False,
        "note": "McKenzie was the CFO who actually integrated Husky. The promotion was earned.",
    },
    "what_we_track": [
        "SAGD steam-oil ratios at Christina Lake and Foster Creek",
        "US refining utilization at Lima, Toledo, and Wood River",
        "Variable dividend pace under the 100%-of-FCF policy",
        "Insider behaviour — buys vs. grants",
        "Lower-decline assets vs. capex required to hold flat",
    ],
    "checklist": {
        "scoring": scoring(
            ("pass",    "FCF through 2015–2020. The 2020 dividend was cut to a token; the business survived without dilution."),
            ("pass",    "Christina Lake and Foster Creek have among the lowest SAGD operating costs in the industry. Mid-C$30s/bbl operating range."),
            ("pass",    "Net debt target of C$4B was achieved in 2024; the balance sheet is now in maintenance mode."),
            ("not_yet", "The Husky combination took longer to integrate cleanly than the deck promised. ROIC on incremental dollars is improving."),
            ("not_yet", "Insider ownership is modest. The behaviour we watch is McKenzie's open-market activity, not the prior CEO's grants."),
            ("not_yet", "2015: capital plan cut hard, dividend pre-Husky was modest. 2020: dividend reduced to a penny, no equity issued."),
            ("pass",    "Variable dividend ties payout directly to per-share cash, which is the right incentive structure."),
            ("not_yet", "Succession bench is real at the operating level. The CEO question is settled for now."),
            ("pass",    "SAGD cost curve places CVE first-quartile on Canadian heavy. US refining utilization is the swing variable, not the structural one."),
            ("pass",    "Mid-cycle Brent at US$65–75 produces meaningful FCF after sustaining. The thesis does not need a commodity peak."),
        ),
        "pillar_commentary": {
            "I": "<strong>Pillar I. The business.</strong> Christina Lake and Foster Creek are among the lowest-cost SAGD operations in Canada and have been since they were Encana assets. The Husky combination was the strategic decision that defines this management team; it was strategically right and operationally painful for three years. Net debt is at the target. The variable dividend distributes 100% of free cash above sustaining and base dividend.",
            "II": "<strong>Pillar II. The people.</strong> Jon McKenzie was the CFO during the Husky integration and was promoted to CEO in 2023 on the strength of what he actually delivered, not what the prior tenure promised. Insider ownership is modest. Compensation is per-share-aligned. The 2020 dividend cut was severe but did not require an equity raise. That second sentence is the one we keep coming back to.",
            "III": "<strong>Pillar III. The cycle.</strong> Cenovus sits on heavy-oil acreage that the merchant refiners' coking systems are configured to consume. The Lima, Toledo, and Wood River refining footprint is the physical hedge for the Western Canadian price differential. Underwriting at mid-cycle Brent, Cenovus compounds. The decade-out question is the same as for Suncor: what regulatory and demand path Canadian heavy follows. That is a Canada question, not a Cenovus question.",
        },
    },
    "last_reviewed_iso": REVIEWED_ISO,
    "next_earnings_iso": None,
    "position_disclosure": "may_hold",
    "disclosure_footnote_html": disclosure("Cenovus Energy Inc.", "Cenovus's FY 2025 disclosure and Q4 2025 release (February 2026)"),
    "back_link": BACK_LINK,
    "related_slugs": ["suncor-su", "canadian-natural-cnq"],
    "body_md": (
        "Cenovus is the integrated oil sands business the Husky combination was supposed to produce. It took three years longer than the deck promised, and the principal who promised it has since left, but the result is finally in front of us. Two of the lowest-cost SAGD operations in Canada, a 660 Mb/d refining throughput that consumes the heavy barrel the merchant refiners cannot, and a balance sheet at its target.\n\n"
        "## The business, in one paragraph\n"
        "Cenovus produces about 810 Mboe/d, of which the meaningful share is Christina Lake and Foster Creek SAGD. Downstream, Lima (Ohio), Toledo (Ohio), Wood River (Illinois, jointly held), Lloydminster (upgrader), and Superior (Wisconsin) refine and upgrade heavy barrels into clean product. The integrated chain is the thesis: a long-life, low-decline upstream feeding a downstream system configured to consume exactly the heavy barrel the upstream produces.\n\n"
        "## What FY 2025 actually said\n"
        "Net debt has been at the C$4B target for more than a year. The variable dividend, which distributes 100% of free cash above sustaining capex and the base dividend, was paid in every quarter of 2025. Operating cost at Christina Lake and Foster Creek printed in the mid-C$30s per barrel. The US refining segment, which dragged earnings through 2022 and 2023 because of repeated turnaround misses at Lima and Toledo, was substantially more reliable in 2025. That second sentence is the one we keep reading.\n\n"
        "## Two things we are reading carefully\n"
        "### 1. Whether US refining is finally a hedge instead of a drag\n"
        "From the 2020 close of Husky through 2023, the US refining footprint was structurally underutilized and operationally embarrassing. Toledo went offline twice in 2022 alone. Cenovus spent meaningful capital fixing the turnaround discipline, and 2024 and 2025 utilization printed much closer to design. If the system runs at 90%-plus utilization through 2026 and 2027, the integrated thesis works. If it does not, the SAGD upstream is doing all the work and Cenovus trades at a discount to that fact.\n\n"
        "### 2. The capital return policy at a $60 print\n"
        "The variable dividend is the right policy at the right oil price. The interesting test is what management does at trough: cut the variable to zero (correct), pause the buyback (also correct), and hold the base dividend. We watch the policy commentary at each quarter for any hint that growth capital is creeping back in front of returns. The 2020 record on that question is encouraging.\n\n"
        "## What we are watching into FY 2026\n"
        "- <strong>SAGD steam-oil ratios</strong> at Christina Lake and Foster Creek.\n"
        "- <strong>US refining utilization</strong> at Lima and Toledo specifically.\n"
        "- <strong>Variable dividend</strong> pace and the implied marginal payout ratio.\n"
        "- <strong>Insider activity</strong> — buys versus grants under the McKenzie compensation reset.\n\n"
        "> The Husky integration is no longer a story we tell to explain a discount. It is a chain we read for what it produces."
    ),
})


# === 3. TOU — Tourmaline Oil ================================================ #
OPERATORS.append({
    "slug": "tourmaline-tou",
    "ticker": "TOU",
    "exchange": "TSX: TOU",
    "name": "Tourmaline Oil Corp.",
    "short_name": "Tourmaline",
    "url": "https://www.tourmalineoil.com/",
    "sector": "Energy",
    "sub_industry": "Oil & Gas",
    "page_eyebrow": "On the desk · Natural gas",
    "headline_html": "Tourmaline (TOU): The owner-operator <em>special dividend.</em>",
    "page_title": "Tourmaline (TOU) — The owner-operator special dividend | Halvren Capital",
    "meta_description": "Tourmaline is Canada's largest natural gas producer and one of the country's last true owner-operator energy businesses. Halvren's read on Mike Rose's capital allocation record and the special-dividend model.",
    "og_title": "Tourmaline (TOU) — The owner-operator special dividend",
    "og_description": "Canada's largest gas producer, Montney and Deep Basin. Halvren's read with FY 2025 numbers, special-dividend cadence, and insider alignment.",
    "og_image": "/og-research.png",
    "published_iso": PUBLISHED_ISO,
    "modified_iso": REVIEWED_ISO,
    "the_read": {
        "summary": "Canada's largest natural gas producer with ~580 Mboe/d of Alberta and BC Montney and Deep Basin production. Owner-operator capital structure: Mike Rose (founder, CEO, chair) and management hold a material stake. Topaz Energy royalty spin (2019) retained alignment. Special dividends are the primary capital return.",
        "generated_iso": GENERATED_ISO,
        "source_filing": "Tourmaline FY 2025 disclosure and Q4 2025 release (March 2026)",
        "principal_reviewed_iso": REVIEWED_ISO,
    },
    "fy_snapshot": {
        "period": "FY 2025",
        "metrics": [
            {"label": "Production", "value": "~580 Mboe/d (FY 2025 mid, approx.)"},
            {"label": "Gas weighting", "value": "~80% natural gas"},
            {"label": "Topaz stake", "value": "~36% (royalty exposure retained)"},
            {"label": "Special dividends (FY 2025)", "value": "C$1.50–2.50/sh range (approx.)"},
            {"label": "Base dividend", "value": "C$0.35/sh quarterly"},
            {"label": "Net debt", "value": "Effectively zero to negative"},
            {"label": "Listings", "value": "TSX: TOU"},
        ],
    },
    "guidance": None,
    "leadership": {
        "ceo": "Michael Rose",
        "ceo_since": 2008,
        "chair": "Michael Rose",
        "succession_visible": False,
        "note": "Founder-chair-CEO. The succession question is real and known.",
    },
    "what_we_track": [
        "Special dividend cadence and absolute size",
        "Topaz Energy contribution and royalty stream",
        "Henry Hub vs. AECO realized price",
        "Insider ownership and Mike Rose's open-market activity",
        "Succession bench visibility",
    ],
    "checklist": {
        "scoring": scoring(
            ("pass",    "FCF every full year since IPO. 2020 was a stress test the dividend survived."),
            ("pass",    "Deep Basin and Montney unit costs work in the US$1.50–2.00/Mcf operating range. The marginal North American gas does not."),
            ("pass",    "Net debt is effectively zero. The business is over-capitalized for a gas producer."),
            ("pass",    "Reinvestment record is exceptional. Almost every dollar of growth capex has produced more dollars of long-life reserves."),
            ("pass",    "Insider ownership is high; Mike Rose's open-market activity is consistent. This is an owner-operator in the literal sense."),
            ("pass",    "2015: bought assets on sale. 2020: paid special dividends, did not cut the base. The record is in public."),
            ("pass",    "Compensation is per-share-aligned. Mike Rose's economic interest is the same as the next shareholder's."),
            ("not_yet", "Succession is not visible. This is the single most important Pillar II question on the desk."),
            ("pass",    "Montney sits in the first quartile of the global gas cost curve; Deep Basin is competitive."),
            ("pass",    "Underwriting at mid-cycle Henry Hub of US$3.50–4.00/Mcf and AECO at C$2.50–3.00/GJ, Tourmaline produces meaningful free cash."),
        ),
        "pillar_commentary": {
            "I": "<strong>Pillar I. The business.</strong> Tourmaline is the rare Canadian gas operator that has earned every dollar of growth on per-share-accretive terms. Deep Basin and Montney assets are first-quartile. The balance sheet is effectively unlevered. The Topaz spinout retained the royalty income as a separate listed vehicle; that decision was strategic, not financial, and was a soft governance signal worth recording.",
            "II": "<strong>Pillar II. The people.</strong> Mike Rose founded the business in 2008 and has run it as a literal owner-operator since. Insider ownership is high. Compensation is per-share-aligned. The capital allocation record is the most consistent on the desk. The single Pillar II weakness is succession: Rose is 70, the bench is not publicly named, and the business has been built around one capital allocator.",
            "III": "<strong>Pillar III. The cycle.</strong> Henry Hub at mid-cycle and AECO at mid-cycle is enough for Tourmaline to print meaningful free cash. The decade-out gas demand picture is favourable, particularly with Canadian LNG capacity coming online. The Pillar III risk is regulatory cost rather than commodity price. The Pillar I and II strength is what gets paid for sitting through that risk.",
        },
    },
    "last_reviewed_iso": REVIEWED_ISO,
    "next_earnings_iso": None,
    "position_disclosure": "may_hold",
    "disclosure_footnote_html": disclosure("Tourmaline Oil Corp.", "Tourmaline's FY 2025 disclosure and Q4 2025 release (March 2026)"),
    "back_link": BACK_LINK,
    "related_slugs": ["arc-resources-arx", "canadian-natural-cnq"],
    "body_md": (
        "Tourmaline is the cleanest expression of owner-operator capital allocation on the Canadian energy desk. Founded by Mike Rose in 2008, the business now produces about 580 Mboe/d, about 80% of which is natural gas. The balance sheet is effectively unlevered. The capital return is delivered in special dividends, paid when the business has more cash than it can reinvest at acceptable returns. The base dividend is held conservatively. That is a Pillar II that the rest of the sector quietly studies.\n\n"
        "## The business, in one paragraph\n"
        "Tourmaline produces from three core areas: the Alberta Deep Basin, the BC Montney (Sundown, Conroy), and the Peace River High. The acreage was assembled steadily over fifteen years, almost entirely on accretive terms, through a combination of small bolt-ons and the absorption of distressed operators in the 2015 and 2020 windows. The 2019 spinout of Topaz Energy carved out the royalty stream as a separate listed vehicle; Tourmaline retained the controlling stake, which has paid meaningful royalty income back to the parent in every year since.\n\n"
        "## What FY 2025 actually said\n"
        "Production is at the high end of guidance, unit costs continue to trend down with the Montney density program, and the base dividend was raised once more during the year. The special-dividend cadence in 2025 was paced rather than aggressive, which we read as conservative positioning into a gas price that has been more volatile than the underlying business. The Topaz contribution was meaningful and increasing.\n\n"
        "## Two things we are reading carefully\n"
        "### 1. The special-dividend cadence as a tell\n"
        "Special dividends are an alignment instrument when the operator owns a meaningful share of the stock, which Rose and management do. The pace of specials tells you what the principal thinks of intrinsic value relative to the share price; aggressive specials at a low share price imply a different signal than buybacks at the same price. We track the absolute size, the gap between specials, and what management says about reinvestment opportunities each quarter.\n\n"
        "### 2. Succession\n"
        "This is the open Pillar II question. Mike Rose is 70, the business has been built around one capital allocator, and the bench is not publicly named in the way a CNR or an Agnico Eagle would name it. We do not have a confident view on what Tourmaline looks like without Rose. We do have a view on what the previous fifteen years of his decisions have produced. Both can be true.\n\n"
        "## What we are watching into FY 2026\n"
        "- <strong>Special-dividend size</strong> and gap, particularly in any quarter the gas tape weakens.\n"
        "- <strong>Topaz royalty contribution</strong> to the parent.\n"
        "- <strong>Realized price gap</strong> between AECO and Henry Hub, and any LNG-export-driven narrowing.\n"
        "- <strong>Succession commentary</strong> — at the proxy, in interviews, in board composition changes.\n\n"
        "> Tourmaline is the operator we would underwrite at any reasonable gas price. The price we underwrite at is set by the succession question."
    ),
})


# === 4. ARX — ARC Resources ================================================= #
OPERATORS.append({
    "slug": "arc-resources-arx",
    "ticker": "ARX",
    "exchange": "TSX: ARX",
    "name": "ARC Resources Ltd.",
    "short_name": "ARC Resources",
    "url": "https://www.arcresources.com/",
    "sector": "Energy",
    "sub_industry": "Oil & Gas",
    "page_eyebrow": "On the desk · Montney condensate",
    "headline_html": "ARC Resources (ARX): The <em>condensate window,</em> read by the resource.",
    "page_title": "ARC Resources (ARX) — The condensate window, read by the resource | Halvren Capital",
    "meta_description": "ARC Resources is the largest pure-play Montney operator in Canada. Halvren's read on the Attachie development, capital discipline through the ramp, and condensate-weighted unit economics.",
    "og_title": "ARC Resources (ARX) — The condensate window, read by the resource",
    "og_description": "Montney condensate-and-gas. Halvren's read with FY 2025 numbers, Attachie Phase 2, and per-share growth discipline.",
    "og_image": "/og-research.png",
    "published_iso": PUBLISHED_ISO,
    "modified_iso": REVIEWED_ISO,
    "the_read": {
        "summary": "Largest pure-play Montney operator in Canada. ~370 Mboe/d production weighted toward condensate, NGLs, and gas (FY 2025 mid, approx.). Attachie Phase 2 ramp underway. Investment-grade balance sheet, conservative capital return policy.",
        "generated_iso": GENERATED_ISO,
        "source_filing": "ARC Resources FY 2025 disclosure and Q4 2025 release (February 2026)",
        "principal_reviewed_iso": REVIEWED_ISO,
    },
    "fy_snapshot": {
        "period": "FY 2025",
        "metrics": [
            {"label": "Production", "value": "~370 Mboe/d (FY 2025 mid, approx.)"},
            {"label": "Liquids weighting", "value": "~40% liquids (condensate + NGLs)"},
            {"label": "Attachie Phase 2", "value": "Ramp to full capacity 2025–26"},
            {"label": "Net debt / cash flow", "value": "<1.0× target"},
            {"label": "Capital return policy", "value": "50–80% of FCF after sustaining"},
            {"label": "Base dividend", "value": "C$0.18/sh quarterly"},
            {"label": "Listings", "value": "TSX: ARX"},
        ],
    },
    "guidance": None,
    "leadership": {
        "ceo": "Terry Anderson",
        "ceo_since": 2023,
        "chair": None,
        "succession_visible": True,
        "note": "Anderson was promoted from COO. The bench is visible.",
    },
    "what_we_track": [
        "Condensate netback vs. WTI",
        "Attachie Phase 2 ramp and unit-cost evidence",
        "Buyback execution velocity",
        "Capital intensity per BOE post-Attachie",
        "Per-share production growth, not absolute production growth",
    ],
    "checklist": {
        "scoring": scoring(
            ("pass",    "FCF every full year since the 2021 Seven Generations merger. 2020 (pre-merger ARC) survived intact."),
            ("pass",    "Montney condensate netbacks remain positive at WTI in the US$50s. The marginal Canadian gas does not."),
            ("pass",    "Investment-grade. Net debt under 1× cash flow target."),
            ("pass",    "Reinvestment record at Kakwa and Sunrise has been per-share-accretive. Attachie is the open test."),
            ("not_yet", "Insider ownership is modest. Management buys are the signal we watch, not the option grants."),
            ("pass",    "2015 (pre-merger): conservative, no equity raised. 2020: dividend reduced but maintained, capex cut hard."),
            ("pass",    "Compensation is increasingly per-share metrics post-2022 reset."),
            ("pass",    "Succession is visible at the executive level. Anderson came from inside; the next CEO is identifiable."),
            ("pass",    "Montney sits in the first quartile of North American liquids-rich gas economics."),
            ("pass",    "Underwriting at mid-cycle WTI of US$65–75 and AECO at C$2.50–3.50/GJ, ARC produces meaningful free cash."),
        ),
        "pillar_commentary": {
            "I": "<strong>Pillar I. The business.</strong> Kakwa, Sunrise, and Attachie are among the highest-quality Montney positions in Canada. Condensate weighting is the structural advantage: condensate prices with WTI; gas prices with the AECO tape; the blend smooths the worst commodity quarter. Reinvestment history is the cleanest in the Canadian gas patch outside Tourmaline. Attachie Phase 2 is the open test on incremental capital.",
            "II": "<strong>Pillar II. The people.</strong> Terry Anderson was promoted from COO in 2023, which means the operating discipline is continuous with the prior tenure. Insider ownership is modest; Anderson's open-market activity is consistent. Compensation is per-share-tilted. The 2020 record is good: dividend reduced, not eliminated, no equity raised. Succession is visible.",
            "III": "<strong>Pillar III. The cycle.</strong> Montney condensate has a structurally favourable demand picture (oil-sands diluent), and Canadian LNG export capacity is opening incremental gas markets. At mid-cycle WTI and AECO, ARC compounds. The decade-out question is the same as for Tourmaline: regulatory cost on Canadian gas, not commodity price.",
        },
    },
    "last_reviewed_iso": REVIEWED_ISO,
    "next_earnings_iso": None,
    "position_disclosure": "may_hold",
    "disclosure_footnote_html": disclosure("ARC Resources Ltd.", "ARC Resources's FY 2025 disclosure and Q4 2025 release (February 2026)"),
    "back_link": BACK_LINK,
    "related_slugs": ["tourmaline-tou", "canadian-natural-cnq"],
    "body_md": (
        "ARC is the largest pure-play Montney operator in Canada. The 2021 merger with Seven Generations created the position; the four years since have been the operational proof. Kakwa, Sunrise, and Attachie are the three pieces that matter, and Attachie Phase 2 is the part of the business the market has not yet seen at full ramp.\n\n"
        "## The business, in one paragraph\n"
        "ARC produces about 370 Mboe/d, of which roughly 40% is liquids (condensate plus NGLs). Condensate is the structural advantage: it prices with WTI, it has captive demand from oil-sands diluent, and the Montney condensate window is one of the best resource plays in North America by per-well economics. The remainder is gas, mostly sold into AECO with a meaningful share going to the BC Coast for either domestic use or LNG export. The balance sheet is investment-grade; net debt sits under one times cash flow.\n\n"
        "## What FY 2025 actually said\n"
        "Attachie Phase 2 started producing in late 2025, on time and at the unit-cost guidance management had set. Production beat the high end of guidance and unit costs continued to trend down. The capital return policy distributed 50–80% of free cash after sustaining capex, weighted toward buybacks for most of the year. Net debt finished the year below the 1× target.\n\n"
        "## Two things we are reading carefully\n"
        "### 1. Attachie Phase 2 unit economics at full ramp\n"
        "Phase 2 was the largest single capital project of the post-merger era. The early production data was promising; the question is what the per-well IP-365 and per-well decline curves look like through 2026 and 2027 once the development is at design rate. We track those numbers with more care than the headline production growth.\n\n"
        "### 2. Whether per-share growth replaces absolute growth\n"
        "ARC has historically grown both production and per-share production. The post-Attachie question is whether management resists the temptation to keep growing absolute production for its own sake and starts spending more of the marginal dollar on the share count instead. The 2025 buyback velocity was a positive signal. The 2026 capital plan is the next read.\n\n"
        "## What we are watching into FY 2026\n"
        "- <strong>Attachie Phase 2 per-well economics</strong> at full ramp.\n"
        "- <strong>Condensate netback</strong> vs. WTI, and the diluent-demand spread.\n"
        "- <strong>Buyback velocity</strong> against absolute production growth.\n"
        "- <strong>2027 development queue</strong> — what comes after Attachie matters more than Attachie itself.\n\n"
        "> ARC is the Montney franchise that does not need a commodity story to work. The story it needs is its own discipline."
    ),
})


# === 5. MEG — MEG Energy ==================================================== #
OPERATORS.append({
    "slug": "meg-energy-meg",
    "ticker": "MEG",
    "exchange": "TSX: MEG",
    "name": "MEG Energy Corp.",
    "short_name": "MEG Energy",
    "url": "https://www.megenergy.com/",
    "sector": "Energy",
    "sub_industry": "Oil & Gas",
    "page_eyebrow": "On the desk · SAGD pure-play",
    "headline_html": "MEG Energy (MEG): The pure-play <em>under strategic review.</em>",
    "page_title": "MEG Energy (MEG) — The pure-play under strategic review | Halvren Capital",
    "meta_description": "MEG is a Christina Lake SAGD pure-play and has been the subject of a strategic process. Halvren's read on the standalone economics, the buyback record, and the corporate-structure overhang.",
    "og_title": "MEG Energy (MEG) — The pure-play under strategic review",
    "og_description": "Christina Lake SAGD pure-play. Halvren's read on FY 2025 unit costs, the buyback record, and the strategic-process overhang.",
    "og_image": "/og-research.png",
    "published_iso": PUBLISHED_ISO,
    "modified_iso": REVIEWED_ISO,
    "the_read": {
        "summary": "Pure-play SAGD oil sands operator. ~100 Mbbl/d production at Christina Lake. Net debt walked down meaningfully over 2020–2024 with aggressive buybacks of a then-discounted share count. The corporate structure has been the subject of a strategic process; readers should consult current filings for the post-process structure.",
        "generated_iso": GENERATED_ISO,
        "source_filing": "MEG Energy FY 2025 disclosure (February 2026); strategic-process disclosure subject to change",
        "principal_reviewed_iso": REVIEWED_ISO,
    },
    "fy_snapshot": {
        "period": "FY 2025",
        "metrics": [
            {"label": "Production", "value": "~100 Mbbl/d (approx.)"},
            {"label": "Asset", "value": "Christina Lake SAGD (single project)"},
            {"label": "Steam-oil ratio", "value": "~2.3 (long-cycle competitive)"},
            {"label": "Net debt walk", "value": "Material reduction 2020–2024"},
            {"label": "Capital structure", "value": "Strategic process — consult current filings"},
            {"label": "Quarterly dividend", "value": "Initiated 2023"},
            {"label": "Listings", "value": "TSX: MEG"},
        ],
    },
    "guidance": None,
    "leadership": {
        "ceo": "Darlene Gates",
        "ceo_since": 2023,
        "chair": None,
        "succession_visible": False,
        "note": "Gates inherited a cleaned-up balance sheet and a single-asset operating cadence. The strategic process is the more material question.",
    },
    "what_we_track": [
        "Christina Lake steam-oil ratio quarter to quarter",
        "WCS-WTI heavy differential",
        "Buyback execution before any structural change",
        "Strategic-process commentary at each filing",
        "Per-share cash, not absolute cash",
    ],
    "checklist": {
        "scoring": scoring(
            ("not_yet", "FCF cleanly positive 2021–2025. The 2015 and 2020 cycle stress was severe and forced the deleveraging that came later."),
            ("pass",    "Christina Lake at a low-2s steam-oil ratio works at WTI in the US$50s. The standalone economics are real."),
            ("pass",    "Balance sheet today is conservatively levered. The 2018–2019 net debt position was painfully different."),
            ("not_yet", "ROIC on incremental capital has been heavily about the buyback. The geographic and operational concentration is the structural limit."),
            ("not_yet", "Insider ownership is modest; the more important read is what the strategic process implies about how management values the asset."),
            ("fail",    "2015 and 2020 were both near-existential. The dividend did not exist. The equity issued at distressed prices is a real Pillar II cost."),
            ("pass",    "Compensation is per-share-aligned. The buyback record is the cleanest of any Canadian pure-play oil-sands name."),
            ("not_yet", "Succession bench is thin by design; this is a single-asset operator."),
            ("pass",    "Christina Lake sits in the first quartile of SAGD operating costs."),
            ("not_yet", "Underwriting MEG at mid-cycle requires a view on the strategic-process outcome. Standalone economics are sound; structural risk is the open question."),
        ),
        "pillar_commentary": {
            "I": "<strong>Pillar I. The business.</strong> Christina Lake is among the lowest-cost SAGD operations in Canada. Steam-oil ratio is competitive. Reserve life is effectively infinite at current rates. The single-asset structure is both the operational strength (focus) and the strategic vulnerability (concentration). Reinvestment over the last five years has been concentrated in the buyback, which has been the right capital allocation choice at the prices the equity traded at.",
            "II": "<strong>Pillar II. The people.</strong> The 2015–2018 record is the Pillar II problem. Equity was issued at distressed prices; the dividend did not exist; the balance sheet nearly broke. The 2019–2025 record is the recovery: aggressive buybacks of a still-discounted share count, dividend initiation, and a cleaned-up capital structure. Darlene Gates inherited a fixed business in 2023. The open strategic process is the more material Pillar II read than insider ownership.",
            "III": "<strong>Pillar III. The cycle.</strong> SAGD operating economics work at mid-cycle WTI. The decade-out question is whether MEG remains an independent operator or is folded into one of the integrateds. Standalone, the math is sound. The premium to standalone, if any, depends on whoever wins the strategic-process auction.",
        },
    },
    "last_reviewed_iso": REVIEWED_ISO,
    "next_earnings_iso": None,
    "position_disclosure": "may_hold",
    "disclosure_footnote_html": disclosure("MEG Energy Corp.", "MEG's FY 2025 disclosure (February 2026); strategic-process disclosure subject to change"),
    "back_link": BACK_LINK,
    "related_slugs": ["cenovus-cve", "suncor-su"],
    "body_md": (
        "MEG is the cleanest expression of a single-asset SAGD pure-play on the Canadian energy desk. Christina Lake produces about 100 Mbbl/d at a steam-oil ratio that has trended down for five years. There are no upgraders, no refineries, and no other producing assets. The capital allocation since 2020 has been the recovery from a near-existential 2015–2018: aggressive buybacks of a discounted share count, the eventual initiation of a dividend, and a cleaned-up balance sheet. The corporate-structure question is the part the market has been pricing in 2025, not the operating book.\n\n"
        "## The business, in one paragraph\n"
        "Christina Lake is a high-quality SAGD development. The reservoir is well-understood, the operating discipline is mature, and the unit operating costs sit comfortably in the first quartile of the SAGD cohort. MEG sells its bitumen as WCS-equivalent blended barrels and is heavily exposed to the heavy-light differential. The midstream offtake commitments give the business stable apportionment exposure on the major heavy lines.\n\n"
        "## What FY 2025 actually said\n"
        "Standalone economics are sound. Steam-oil ratio printed in the low 2s. Operating costs were stable. Free cash was positive in every quarter. The buyback continued through the year at a measured pace. The more important disclosure is the strategic process, which has materially shaped how the equity has traded; readers should consult current filings for the post-process structure rather than rely on any prior comparable.\n\n"
        "## Two things we are reading carefully\n"
        "### 1. Standalone unit economics\n"
        "Whatever the strategic outcome, the underlying business is what determines the asset's intrinsic value. We track steam-oil ratio, unit operating cost, and free cash per barrel without reference to the corporate structure. Christina Lake at a low-2s SOR works at WTI in the US$50s; that is the base case.\n\n"
        "### 2. The capital-allocation tell during the process\n"
        "Management's behaviour during a strategic process is informative. Aggressive buybacks signal one view of intrinsic value; suspended buybacks signal another. We watch both the action and the commentary.\n\n"
        "## What we are watching into FY 2026\n"
        "- <strong>Steam-oil ratio</strong> at Christina Lake by quarter.\n"
        "- <strong>WCS-WTI heavy differential</strong> and apportionment exposure.\n"
        "- <strong>Strategic-process disclosure</strong> at each filing.\n"
        "- <strong>Buyback pace</strong> through the process window.\n\n"
        "> MEG is the SAGD operator whose standalone math is sound. The premium to standalone, if any, is the strategic process's to set."
    ),
})


# === 6. TECK — Teck Resources =============================================== #
OPERATORS.append({
    "slug": "teck-resources-teck",
    "ticker": "TECK",
    "exchange": "TSX: TECK.B · NYSE: TECK",
    "name": "Teck Resources Limited",
    "short_name": "Teck Resources",
    "url": "https://www.teck.com/",
    "sector": "Materials",
    "sub_industry": "Industrial Metals",
    "page_eyebrow": "On the desk · Copper",
    "headline_html": "Teck (TECK): The <em>copper company</em> the coal company became.",
    "page_title": "Teck (TECK) — The copper company the coal company became | Halvren Capital",
    "meta_description": "Teck Resources is post-coal-divestiture, copper-focused, with Quebrada Blanca 2 as the open ramp question. Halvren's read on Highland Valley, QB2, and the cleaner unit-cost arithmetic.",
    "og_title": "Teck (TECK) — The copper company the coal company became",
    "og_description": "Post-coal-divestiture copper miner. Halvren's read with FY 2025 numbers, QB2 ramp, and per-share capital discipline.",
    "og_image": "/og-research.png",
    "published_iso": PUBLISHED_ISO,
    "modified_iso": REVIEWED_ISO,
    "the_read": {
        "summary": "Post-coal-divestiture copper miner. Highland Valley (BC), Quebrada Blanca 2 (Chile), Antamina (22.5% Peru), Carmen de Andacollo (Chile). Zinc at Red Dog (Alaska) and Trail (BC). Coal business sold to Glencore in 2024.",
        "generated_iso": GENERATED_ISO,
        "source_filing": "Teck Resources FY 2025 disclosure and Q4 2025 release (February 2026)",
        "principal_reviewed_iso": REVIEWED_ISO,
    },
    "fy_snapshot": {
        "period": "FY 2025",
        "metrics": [
            {"label": "Copper production", "value": "~480 kt (FY 2025 mid, approx.)"},
            {"label": "QB2 share", "value": "Ramp to full capacity 2025–26"},
            {"label": "Zinc production", "value": "Red Dog + Trail; FY 2025 stable"},
            {"label": "Post-EVR proceeds", "value": "US$7B+ returned to shareholders (2024–25)"},
            {"label": "Capital return policy", "value": "30% of FCF base + supplemental"},
            {"label": "Net debt", "value": "Conservative post-divestiture"},
            {"label": "Listings", "value": "TSX: TECK.B · NYSE: TECK"},
        ],
    },
    "guidance": None,
    "leadership": {
        "ceo": "Jonathan Price",
        "ceo_since": 2022,
        "chair": "Sheila Murray",
        "succession_visible": True,
        "note": "Price led the coal divestiture and is now running a pure-play copper-and-zinc miner.",
    },
    "what_we_track": [
        "QB2 ramp throughput and unit cost",
        "Highland Valley mine-life extension capex",
        "Capital return execution post-EVR proceeds",
        "Zinc segment contribution at Red Dog and Trail",
        "Per-share economics, not absolute reserve growth",
    ],
    "checklist": {
        "scoring": scoring(
            ("not_yet", "FCF through the full cycle is better than the legacy reputation suggests; copper is more cyclical than people remember."),
            ("not_yet", "Copper at US$3/lb is comfortable; at US$2.50 the marginal mine economics are tighter."),
            ("pass",    "Post-EVR divestiture the balance sheet is conservative."),
            ("not_yet", "QB2 was a multi-billion dollar capex program whose ROIC has been below initial expectations. The ramp will determine the long-term verdict."),
            ("not_yet", "Insider ownership is modest. The Keevil family stake is meaningful but no longer dominant post-2023 dual-class collapse."),
            ("not_yet", "2015: deep stress; equity raised at distressed prices. 2020: dividend held; capital plan reduced. The record is mixed."),
            ("pass",    "Compensation is per-share-aligned. The 2023 dual-class collapse improved the governance materially."),
            ("pass",    "Succession is visible; Price came from inside, the executive team is named."),
            ("not_yet", "On the global copper cost curve Highland Valley and QB2 sit in the second quartile, not the first. Antamina is more competitive."),
            ("pass",    "Underwriting at mid-cycle copper of US$3.50–4.00/lb, Teck compounds meaningfully. The thesis works at mid-cycle, not just at peak."),
        ),
        "pillar_commentary": {
            "I": "<strong>Pillar I. The business.</strong> The coal divestiture cleaned the story. Teck is now a copper-and-zinc miner with a meaningful zinc segment at Red Dog and Trail. Highland Valley is a long-life Canadian mine. QB2 is the open question: a multi-billion dollar capex program whose ROIC has trailed initial expectations and whose full ramp will determine the long-term verdict on the prior management's signature decision. Antamina remains the cleanest single asset in the portfolio.",
            "II": "<strong>Pillar II. The people.</strong> Jonathan Price was promoted from inside in 2022 and led the coal divestiture cleanly. The 2023 dual-class share collapse was a meaningful governance upgrade. Insider ownership is modest. The Keevil family stake is still meaningful but no longer controlling. The capital allocation record on QB2 specifically is the legitimate Pillar II concern; the post-divestiture record is encouragingly per-share-aligned.",
            "III": "<strong>Pillar III. The cycle.</strong> Copper demand is structurally favourable on the decade-out picture: electrification, grid build, renewable demand. Teck's mines are not first-quartile on the global cost curve but they are durable. Underwriting at mid-cycle US$3.50–4.00/lb copper, Teck produces meaningful free cash. The decade-out question is whether QB2 was a generationally acquired asset or an over-spent one. The answer is in the ramp.",
        },
    },
    "last_reviewed_iso": REVIEWED_ISO,
    "next_earnings_iso": None,
    "position_disclosure": "may_hold",
    "disclosure_footnote_html": disclosure("Teck Resources Limited", "Teck's FY 2025 disclosure and Q4 2025 release (February 2026)"),
    "back_link": BACK_LINK,
    "related_slugs": ["freeport-mcmoran-fcx", "agnico-eagle-aem"],
    "body_md": (
        "Teck is the copper company the coal company became. The September 2024 sale of the steelmaking-coal business to Glencore closed a chapter that defined the prior generation of management, and the post-divestiture business is materially cleaner to underwrite. Highland Valley in BC, Quebrada Blanca 2 in Chile, 22.5% of Antamina in Peru, and Carmen de Andacollo. Zinc at Red Dog and Trail. That is the whole story.\n\n"
        "## The business, in one paragraph\n"
        "Copper production sits around 480 kt at QB2 full ramp. Highland Valley is a long-life Canadian mine that has been a Teck asset for decades; the mine-life extension capex is the part that determines whether HVC produces into the 2040s or not. Quebrada Blanca 2 was the previous management team's signature decision and a multi-billion dollar capex program; the ramp has been slower than the original schedule and is the question 2026 will answer. Antamina is the cleanest single asset in the portfolio. Red Dog and Trail are a smaller, decent zinc operation that prints reliable cash.\n\n"
        "## What FY 2025 actually said\n"
        "Coal divestiture proceeds were returned to shareholders in size during 2024 and 2025 — US$7B-plus across buybacks and special dividends. The capital return policy is 30% of free cash flow as a base, with supplementals tied to balance-sheet position. QB2 throughput continued to ramp; the unit-cost number remained higher than the original case. Highland Valley continues to produce on plan. The zinc segment was stable.\n\n"
        "## Two things we are reading carefully\n"
        "### 1. The QB2 ramp\n"
        "QB2 is the signature decision of the prior management. The capital was spent. The mine is producing. The ramp to full design throughput at the design unit cost is the part that is still in progress. We do not yet have a confident view on what the steady-state unit cost looks like; the 2026 quarterly data is the dataset that will settle the question.\n\n"
        "### 2. The post-divestiture capital allocation cadence\n"
        "Returning US$7B of proceeds to shareholders cleanly is the right answer to a divestiture. The harder question is what the post-cash business does with the next dollar of operating cash flow. The 30%-of-FCF base policy is reasonable. The marginal dollar above that policy is where the per-share story is made or unmade.\n\n"
        "## What we are watching into FY 2026\n"
        "- <strong>QB2 throughput and unit cost</strong> at design rate.\n"
        "- <strong>Highland Valley mine-life</strong> extension capex.\n"
        "- <strong>Capital return cadence</strong> versus any new project capex.\n"
        "- <strong>Zinc segment contribution</strong> at Red Dog and Trail.\n\n"
        "> The coal divestiture cleaned the story. What is left is a copper miner with one open ramp question."
    ),
})


# === 7. AEM — Agnico Eagle Mines ============================================ #
OPERATORS.append({
    "slug": "agnico-eagle-aem",
    "ticker": "AEM",
    "exchange": "TSX: AEM · NYSE: AEM",
    "name": "Agnico Eagle Mines Limited",
    "short_name": "Agnico Eagle",
    "url": "https://www.agnicoeagle.com/",
    "sector": "Materials",
    "sub_industry": "Gold",
    "page_eyebrow": "On the desk · Gold",
    "headline_html": "Agnico Eagle (AEM): The boring gold operator, <em>by design.</em>",
    "page_title": "Agnico Eagle (AEM) — The boring gold operator, by design | Halvren Capital",
    "meta_description": "Agnico Eagle is a tier-1-jurisdiction gold producer with a long record of disciplined capital allocation. Halvren's read on the Detour-LaRonde-Malartic cost curve and the operating reputation.",
    "og_title": "Agnico Eagle (AEM) — The boring gold operator, by design",
    "og_description": "Tier-1 gold operator. Halvren's read on FY 2025 numbers, Canadian Malartic, Detour Lake, and per-ounce discipline.",
    "og_image": "/og-research.png",
    "published_iso": PUBLISHED_ISO,
    "modified_iso": REVIEWED_ISO,
    "the_read": {
        "summary": "Tier-1-jurisdiction gold producer. ~3.4 Moz annual production from Canadian Malartic, Detour Lake, LaRonde, Meadowbank, Macassa, Fosterville (Australia), and Kittilä (Finland). Disciplined capital allocator; AISC consistently first-quartile within the senior gold cohort.",
        "generated_iso": GENERATED_ISO,
        "source_filing": "Agnico Eagle FY 2025 disclosure and Q4 2025 release (February 2026)",
        "principal_reviewed_iso": REVIEWED_ISO,
    },
    "fy_snapshot": {
        "period": "FY 2025",
        "metrics": [
            {"label": "Production", "value": "~3.4 Moz (FY 2025 mid, approx.)"},
            {"label": "AISC", "value": "US$1,200–1,300/oz (approx.)"},
            {"label": "Free cash flow", "value": "Strong at FY 2025 average gold price"},
            {"label": "Net debt", "value": "Conservative; investment-grade"},
            {"label": "Quarterly dividend", "value": "US$0.40/sh"},
            {"label": "Buybacks", "value": "Selective, opportunistic"},
            {"label": "Listings", "value": "TSX: AEM · NYSE: AEM"},
        ],
    },
    "guidance": None,
    "leadership": {
        "ceo": "Ammar Al-Joundi",
        "ceo_since": 2022,
        "chair": "Sean Boyd",
        "succession_visible": True,
        "note": "Boyd-to-Al-Joundi succession was prepared for years and executed cleanly. The bench is deep.",
    },
    "what_we_track": [
        "AISC by mine, particularly Detour and Malartic underground",
        "Reserve replacement at flat gold prices",
        "Free cash flow at consensus gold deck",
        "Insider behaviour — buys vs. grants",
        "Capital allocation: dividend vs. buyback vs. growth capex",
    ],
    "checklist": {
        "scoring": scoring(
            ("pass",    "FCF through the full cycle, including the 2013–2015 gold trough. The dividend was held."),
            ("pass",    "AISC works at US$1,200–1,400/oz across the portfolio. The 2015 stress was real but survived."),
            ("pass",    "Investment-grade. Net debt is conservative."),
            ("pass",    "Reinvestment record is exceptional; per-share reserves and per-share production both grew through the Kirkland Lake merger."),
            ("pass",    "Insider buying activity by the executive team has been consistent. Sean Boyd's open-market purchases are a reference signal."),
            ("pass",    "2015: dividend held, capital plan reduced. 2020: dividend raised, no equity raised. The record is unusually clean."),
            ("pass",    "Compensation is per-share-aligned. Reserve-per-share is a tracked metric."),
            ("pass",    "Succession is visible and was executed in 2022. The bench is deep."),
            ("pass",    "AISC sits in the first quartile of senior gold producers. Tier-1 jurisdictions reduce the political-risk discount."),
            ("pass",    "Underwriting at a US$1,700/oz mid-cycle gold deck, AEM compounds. The thesis does not require a peak."),
        ),
        "pillar_commentary": {
            "I": "<strong>Pillar I. The business.</strong> Agnico Eagle is the senior gold producer with the cleanest operating record. AISC is first-quartile within the cohort. The 2022 merger with Kirkland Lake added Detour Lake and Macassa and was the rare gold-sector deal that was per-share-accretive on day one. The reinvestment history is exceptional. Reserve replacement at flat gold prices is the metric we track most closely.",
            "II": "<strong>Pillar II. The people.</strong> Sean Boyd ran Agnico Eagle for two decades and built the capital allocation culture that defines the business. Ammar Al-Joundi was promoted from inside in 2022 in a succession that had been telegraphed for years. Insider buying activity has been consistent. Compensation is per-share-aligned. The 2015 record and the 2020 record are both unusually clean.",
            "III": "<strong>Pillar III. The cycle.</strong> Gold is a low-correlation commodity with structural demand support. Agnico's mines are not the lowest cost in absolute terms across the global cohort, but they are in tier-1 jurisdictions, which removes a meaningful political-risk discount that the higher-AISC competitors do not have. Underwriting at mid-cycle gold of US$1,700/oz, Agnico produces meaningful free cash. The decade-out question is the same as for any gold operator: what real interest rates do.",
        },
    },
    "last_reviewed_iso": REVIEWED_ISO,
    "next_earnings_iso": None,
    "position_disclosure": "may_hold",
    "disclosure_footnote_html": disclosure("Agnico Eagle Mines Limited", "Agnico Eagle's FY 2025 disclosure and Q4 2025 release (February 2026)"),
    "back_link": BACK_LINK,
    "related_slugs": ["first-majestic-ag", "teck-resources-teck"],
    "body_md": (
        "Agnico Eagle is the senior gold producer that has produced the cleanest operating record over the last two decades. We have written before about the difference between a mining business and a commodity bet. Agnico is squarely the first.\n\n"
        "## The business, in one paragraph\n"
        "Production sits at about 3.4 Moz per year from a portfolio that includes Canadian Malartic and Odyssey underground in Quebec, Detour Lake in Ontario, LaRonde in Quebec, Meadowbank in Nunavut, Macassa in Ontario, Fosterville in Australia, and Kittilä in Finland. The Canadian weighting is structural; tier-1 jurisdictions reduce the political-risk discount that the higher-AISC competitors in less stable geographies do not have. The 2022 merger with Kirkland Lake added Detour and Macassa and was the rare gold-sector deal that was per-share-accretive on day one.\n\n"
        "## What FY 2025 actually said\n"
        "Production met the high end of guidance. AISC printed in the US$1,200–1,300 range and the Detour Lake mill optimization program continued to take per-ounce costs down. Free cash flow at the FY 2025 average gold price was strong. The dividend was held; the buyback was selective and opportunistic rather than aggressive. Net debt remained conservative. The reserve replacement at flat gold prices was sufficient.\n\n"
        "## Two things we are reading carefully\n"
        "### 1. Detour Lake mill optimization\n"
        "Detour is the single largest production asset in the portfolio and the most important from a unit-cost perspective. The mill optimization program has been taking unit costs down steadily since the 2022 merger; the question is how far that compression can run and what the steady-state AISC at Detour looks like into 2027. Per-ounce mill throughput is the metric we track.\n\n"
        "### 2. Reserve replacement at flat gold prices\n"
        "It is very easy to grow gold reserves when the price is rising; the cost-cut-off curve does the work. The honest test of a senior gold producer is whether it can replace ounces at <em>flat</em> prices through brownfield exploration and step-out drilling. Agnico's track record on this metric is among the best in the senior cohort. We watch the per-asset reserve replacement and the consolidated number every year.\n\n"
        "## What we are watching into FY 2026\n"
        "- <strong>AISC at Detour Lake</strong> as the mill optimization progresses.\n"
        "- <strong>Canadian Malartic underground</strong> ramp at Odyssey.\n"
        "- <strong>Reserve replacement</strong> at flat gold prices.\n"
        "- <strong>Buyback velocity</strong> at any meaningful pullback in the share price.\n\n"
        "> Agnico is the gold operator we think about as a mining business first. The commodity is the part the market argues about; the operating record is the part we read."
    ),
})


# === 8. WFG — West Fraser Timber ============================================ #
OPERATORS.append({
    "slug": "west-fraser-wfg",
    "ticker": "WFG",
    "exchange": "TSX: WFG · NYSE: WFG",
    "name": "West Fraser Timber Co. Ltd.",
    "short_name": "West Fraser",
    "url": "https://www.westfraser.com/",
    "sector": "Materials",
    "sub_industry": "Forest Products",
    "page_eyebrow": "On the desk · Forest Products",
    "headline_html": "West Fraser (WFG): The lumber cycle, <em>read by the family.</em>",
    "page_title": "West Fraser (WFG) — The lumber cycle, read by the family | Halvren Capital",
    "meta_description": "West Fraser is the largest lumber and OSB producer in North America. Halvren's read on the post-Norbord business, family stewardship, and the cycle no one writes about.",
    "og_title": "West Fraser (WFG) — The lumber cycle, read by the family",
    "og_description": "Lumber and OSB. Halvren's read on FY 2025 numbers, the Ketcham stewardship record, and the cycle.",
    "og_image": "/og-research.png",
    "published_iso": PUBLISHED_ISO,
    "modified_iso": REVIEWED_ISO,
    "the_read": {
        "summary": "Largest North American lumber and OSB producer post-2021 Norbord acquisition. ~6.4 BBF lumber capacity, ~7.3 BSF OSB capacity. Operations concentrated in BC, Alberta, US South, and the US Midwest. Long-tenured Ketcham family stewardship influence on capital culture.",
        "generated_iso": GENERATED_ISO,
        "source_filing": "West Fraser FY 2025 disclosure and Q4 2025 release (February 2026)",
        "principal_reviewed_iso": REVIEWED_ISO,
    },
    "fy_snapshot": {
        "period": "FY 2025",
        "metrics": [
            {"label": "Lumber capacity", "value": "~6.4 BBF (FY 2025 footprint)"},
            {"label": "OSB capacity", "value": "~7.3 BSF post-Norbord"},
            {"label": "BC interior exposure", "value": "Reduced via curtailments 2023–24"},
            {"label": "US South weighting", "value": "Increasing share of total capacity"},
            {"label": "Net debt", "value": "Conservative; net cash periodic"},
            {"label": "Buybacks", "value": "Active when the cycle is generous"},
            {"label": "Listings", "value": "TSX: WFG · NYSE: WFG"},
        ],
    },
    "guidance": None,
    "leadership": {
        "ceo": "Sean McLaren",
        "ceo_since": 2024,
        "chair": "Robert Hagerman",
        "succession_visible": True,
        "note": "McLaren came from inside. Ketcham family influence at the board level remains material.",
    },
    "what_we_track": [
        "BC interior capacity curtailment trajectory",
        "US South mill utilization and unit cost",
        "OSB price realization vs. lumber",
        "Buyback execution at cyclical troughs",
        "Stumpage and log cost in BC",
    ],
    "checklist": {
        "scoring": scoring(
            ("not_yet", "FCF through full cycle is positive on average; lumber troughs are real and 2019 was uncomfortable."),
            ("pass",    "US South mills work at trough lumber prices. BC interior mills do not, which is why they are being closed."),
            ("pass",    "Balance sheet is consistently conservative; net cash through several recent years."),
            ("pass",    "Norbord was per-share-accretive at the price paid. The reinvestment record on incremental capex is encouragingly tight."),
            ("pass",    "Ketcham family influence on the board and the executive team is the structural alignment signal."),
            ("pass",    "2015: bought back stock during the cycle. 2020: bought back aggressively at the bottom; held the dividend. Record is clean."),
            ("pass",    "Compensation is per-share-aligned. The buyback record is the proof point."),
            ("pass",    "Succession is visible at the executive level; McLaren came from inside."),
            ("not_yet", "BC interior mills sit in the higher-cost half of the curve; US South mills are competitive. The mix is rebalancing."),
            ("pass",    "Underwriting at mid-cycle lumber of US$450/Mbf and mid-cycle OSB, West Fraser produces meaningful free cash."),
        ),
        "pillar_commentary": {
            "I": "<strong>Pillar I. The business.</strong> Lumber and OSB are commodity products with regional cost-curve dynamics. West Fraser's BC interior mills are higher-cost; the US South footprint that came in size with the 2021 Norbord acquisition is more competitive. The capital allocation through the cycle has been consistent: build conservative balance sheet at the top, buy back stock at the bottom. The Norbord transaction was per-share-accretive at the price paid and re-weighted the business toward better cost-curve geography.",
            "II": "<strong>Pillar II. The people.</strong> The Ketcham family stewardship is the structural Pillar II point. Sean McLaren was promoted from inside in 2024 and the operational discipline is continuous with the prior tenure. The 2020 record of aggressive buybacks at distressed lumber prices is the cleanest single capital allocation decision on the desk. Compensation is per-share-aligned.",
            "III": "<strong>Pillar III. The cycle.</strong> Lumber and OSB are housing-cycle exposures. North American housing demand has structural drivers (household formation, undersupply, demographic) and structural headwinds (affordability, interest rates). The mid-cycle is real and arrives every few years. Underwriting at mid-cycle prices, West Fraser produces meaningful free cash. The decade-out question is whether BC interior mills survive a regulatory environment that is not getting easier.",
        },
    },
    "last_reviewed_iso": REVIEWED_ISO,
    "next_earnings_iso": None,
    "position_disclosure": "may_hold",
    "disclosure_footnote_html": disclosure("West Fraser Timber Co. Ltd.", "West Fraser's FY 2025 disclosure and Q4 2025 release (February 2026)"),
    "back_link": BACK_LINK,
    "related_slugs": ["nutrien-ntr", "agnico-eagle-aem"],
    "body_md": (
        "Lumber is the cycle nobody writes about. The good lumber operator is not the one who picks the bottom; it is the one who has the balance sheet to buy back stock when everyone else is issuing it, and the cost position to keep the mills running when the marginal mill cannot. West Fraser is that operator.\n\n"
        "## The business, in one paragraph\n"
        "West Fraser produces about 6.4 billion board-feet of lumber and 7.3 billion square-feet of OSB across BC, Alberta, the US South, and the US Midwest. The 2021 Norbord acquisition added the OSB business at a price that has aged well. The Ketcham family has held a meaningful stake and a stewardship voice in the business for decades. Capital allocation through the cycle has been consistent: build conservative balance sheet at the top, buy back stock at the bottom. The 2020 buyback record is the cleanest single capital decision on the Halvren desk.\n\n"
        "## What FY 2025 actually said\n"
        "The lumber tape was mixed through the year. OSB held up better. BC interior curtailments continued through 2025, taking out higher-cost capacity and re-weighting the portfolio toward the US South. Free cash was positive on average. The balance sheet remained conservative. The buyback was modest, consistent with where in the cycle management reads the business.\n\n"
        "## Two things we are reading carefully\n"
        "### 1. The BC-to-US-South capacity rebalancing\n"
        "The BC interior cost curve has been moving in the wrong direction for a decade: stumpage cost, log supply, regulatory cost, and species mix have all worked against the operator. West Fraser has been quietly closing the highest-cost BC mills and shifting capacity to the US South where the cost position is materially better. We track the relative mill count and capacity by geography each year.\n\n"
        "### 2. Buyback velocity at the cycle\n"
        "The next lumber trough is when the family operator gets to demonstrate the capital allocation culture. We watch the share count quarter over quarter through any meaningful weakness in the lumber tape. The 2020 record is the reference; the 2025 modest pace is the current read.\n\n"
        "## What we are watching into FY 2026\n"
        "- <strong>BC interior capacity</strong> trajectory and stumpage developments.\n"
        "- <strong>US South utilization</strong> and unit cost.\n"
        "- <strong>OSB realized price</strong> vs. lumber.\n"
        "- <strong>Buyback velocity</strong> at any lumber-tape weakness.\n\n"
        "> The lumber cycle is the cycle no one writes about. The operators worth owning are the ones who have already lived through three of them."
    ),
})


# === 9. TRP — TC Energy ===================================================== #
OPERATORS.append({
    "slug": "tc-energy-trp",
    "ticker": "TRP",
    "exchange": "TSX: TRP · NYSE: TRP",
    "name": "TC Energy Corporation",
    "short_name": "TC Energy",
    "url": "https://www.tcenergy.com/",
    "sector": "Infrastructure",
    "sub_industry": "Pipelines",
    "page_eyebrow": "On the desk · Pipelines",
    "headline_html": "TC Energy (TRP): The <em>cleanup,</em> finished.",
    "page_title": "TC Energy (TRP) — The cleanup, finished | Halvren Capital",
    "meta_description": "TC Energy is post-Coastal-GasLink, post-South-Bow-spinout, and finally a pure-play gas pipeline and power operator. Halvren's read on the simplified structure, rate-base growth, and the dividend trajectory.",
    "og_title": "TC Energy (TRP) — The cleanup, finished",
    "og_description": "Gas pipelines + power, post-South-Bow spinout. Halvren's read with FY 2025 numbers, Coastal GasLink in the rear-view, and rate-base discipline.",
    "og_image": "/og-research.png",
    "published_iso": PUBLISHED_ISO,
    "modified_iso": REVIEWED_ISO,
    "the_read": {
        "summary": "Post-South-Bow-spinout pure-play North American gas pipeline operator with a small but real power segment. Coastal GasLink completed in late 2023. The 2024 spinout separated the liquids pipelines into a standalone (South Bow). Long-life regulated and contracted assets dominate.",
        "generated_iso": GENERATED_ISO,
        "source_filing": "TC Energy FY 2025 disclosure and Q4 2025 release (February 2026)",
        "principal_reviewed_iso": REVIEWED_ISO,
    },
    "fy_snapshot": {
        "period": "FY 2025",
        "metrics": [
            {"label": "Natural gas pipelines", "value": "~93 Bcf/d transported, NA-wide footprint"},
            {"label": "Power & energy solutions", "value": "Bruce Power (~48%) + smaller"},
            {"label": "Capital program", "value": "~C$6–7B annual run-rate"},
            {"label": "Dividend growth", "value": "Targeted 3–5% per year"},
            {"label": "Net debt / EBITDA", "value": "~4.8× target band"},
            {"label": "Take-or-pay / contracted share", "value": ">90% of EBITDA"},
            {"label": "Listings", "value": "TSX: TRP · NYSE: TRP"},
        ],
    },
    "guidance": None,
    "leadership": {
        "ceo": "François Poirier",
        "ceo_since": 2021,
        "chair": "Siim Vanaselja",
        "succession_visible": True,
        "note": "Poirier ran the cleanup; the simplified structure is the result. The bench is visible.",
    },
    "what_we_track": [
        "Rate-base growth across NGTL and US gas",
        "Bruce Power refurbishment progress",
        "Capital program at the C$6–7B run-rate, not above",
        "Dividend coverage at the 3–5% growth pace",
        "South Bow inter-company alignment, where any",
    ],
    "checklist": {
        "scoring": scoring(
            ("pass",    "FCF through the full cycle, every year. Regulated and contracted EBITDA dominates."),
            ("pass",    "Take-or-pay and cost-of-service contracts; unit economics are not commodity-price exposed in the way E&P is."),
            ("not_yet", "Net debt is at the high end of the target band post-Coastal GasLink. The South Bow spinout cleaned the picture."),
            ("not_yet", "Coastal GasLink was a multi-billion dollar over-run. ROIC on incremental capital across 2018–2023 trailed the original case meaningfully."),
            ("not_yet", "Insider ownership is modest. Capital allocation behaviour at the board is what we read, not direct insider buys."),
            ("pass",    "2015 and 2020: dividend held and raised in both years. The regulated cash flow did its job."),
            ("not_yet", "Compensation is partially per-share-aligned; the legacy plan was production-sized rather than capital-efficient."),
            ("pass",    "Succession is visible; Poirier was promoted from inside, and the executive team is named."),
            ("pass",    "NGTL and the US gas footprint sit on rate base that has rate-base-driven economics. The cost-curve discussion is largely irrelevant."),
            ("pass",    "Underwriting at any realistic North American gas demand path, the regulated and contracted base earns. The decade-out picture is favourable for gas pipeline rate-base."),
        ),
        "pillar_commentary": {
            "I": "<strong>Pillar I. The business.</strong> TC Energy is more than 90% take-or-pay or cost-of-service EBITDA. The post-South-Bow business is structurally simpler than the pre-2024 business. The Bruce Power refurbishment program is a real contributor and a long-life regulated asset in its own right. The legitimate Pillar I weakness is the 2018–2023 capital allocation record, anchored by Coastal GasLink's multi-billion dollar over-run.",
            "II": "<strong>Pillar II. The people.</strong> François Poirier led the cleanup, including the South Bow spinout and the post-Coastal-GasLink balance-sheet repair. The dividend was held and raised through both 2015 and 2020. Insider ownership is modest. The compensation reset post-2022 is incrementally per-share-aligned; the legacy plan was not.",
            "III": "<strong>Pillar III. The cycle.</strong> Natural gas pipeline rate base is structurally a long-cycle asset. The decade-out demand picture for North American natural gas — LNG export, gas-fired power generation, industrial — is favourable. The Pillar III risk is regulatory, not commodity. Underwriting at the targeted 3–5% dividend growth and rate-base expansion, TC Energy is a compounder. Not a fast one. A reliable one.",
        },
    },
    "last_reviewed_iso": REVIEWED_ISO,
    "next_earnings_iso": None,
    "position_disclosure": "may_hold",
    "disclosure_footnote_html": disclosure("TC Energy Corporation", "TC Energy's FY 2025 disclosure and Q4 2025 release (February 2026)"),
    "back_link": BACK_LINK,
    "related_slugs": ["enbridge-enb", "pembina-ppl"],
    "body_md": (
        "TC Energy is the pipeline business its critics finally stopped writing about. The two events that defined the last seven years — Coastal GasLink and the South Bow spinout — are both behind us. What is left is a North American gas pipeline and power business that earns more than 90% of EBITDA from take-or-pay and cost-of-service contracts.\n\n"
        "## The business, in one paragraph\n"
        "TC Energy moves roughly 93 Bcf/day of natural gas across a network that touches Canada, the US, and Mexico. The NGTL system in Alberta is one of the largest gas-gathering systems in the world. The US gas pipelines (Columbia, ANR, Northern Border) anchor the eastern and Midwest networks. Coastal GasLink, completed in late 2023, delivers feedstock to LNG Canada. The power segment, anchored by an approximately 48% interest in Bruce Power in Ontario, is a meaningful and growing contributor. The South Bow spinout in October 2024 carved out the liquids pipelines.\n\n"
        "## What FY 2025 actually said\n"
        "The simplified business reported cleanly. EBITDA grew at the targeted rate. The capital program continued at the C$6–7B annual run-rate that management has committed to. The dividend was raised in line with the 3–5% growth target. Net debt sits at the high end of the targeted band. The Coastal GasLink over-run is no longer a near-term cash drag.\n\n"
        "## Two things we are reading carefully\n"
        "### 1. Whether the capital program discipline holds\n"
        "The pre-2023 capital program was the problem. Coastal GasLink alone was a multi-billion dollar over-run. The post-spinout capital program at C$6–7B is sized appropriately for the rate base and the balance sheet. The honest test is whether management resists the temptation to chase the next mega-project. We track every new project announcement against the run-rate.\n\n"
        "### 2. Bruce Power refurbishment\n"
        "Bruce is a long-life, regulated, low-emissions power asset whose refurbishment program is one of the largest capital programs in Canadian power. TC Energy's interest is a meaningful and growing contributor to EBITDA. We track refurbishment unit progress and the regulated rate-of-return.\n\n"
        "## What we are watching into FY 2026\n"
        "- <strong>Capital program discipline</strong> at the C$6–7B run-rate.\n"
        "- <strong>Bruce Power refurbishment</strong> progress.\n"
        "- <strong>NGTL rate-base growth.</strong>\n"
        "- <strong>Net debt</strong> trajectory within the target band.\n\n"
        "> A pipeline is a toll-road. The honest version of TC Energy is the one with the cleanup finished."
    ),
})


# === 10. PPL — Pembina Pipeline ============================================= #
OPERATORS.append({
    "slug": "pembina-ppl",
    "ticker": "PPL",
    "exchange": "TSX: PPL · NYSE: PBA",
    "name": "Pembina Pipeline Corporation",
    "short_name": "Pembina",
    "url": "https://www.pembina.com/",
    "sector": "Infrastructure",
    "sub_industry": "Pipelines",
    "page_eyebrow": "On the desk · Midstream",
    "headline_html": "Pembina (PPL): The <em>Western Canadian</em> midstream, read plainly.",
    "page_title": "Pembina Pipeline (PPL) — The Western Canadian midstream, read plainly | Halvren Capital",
    "meta_description": "Pembina is the integrated Western Canadian midstream operator across liquids, gas processing, and NGL fractionation. Halvren's read on the contracted EBITDA share and the conservative capital culture.",
    "og_title": "Pembina Pipeline (PPL) — The Western Canadian midstream, read plainly",
    "og_description": "Liquids pipelines, gas processing, NGL fractionation. Halvren's read with FY 2025 numbers and capital discipline.",
    "og_image": "/og-research.png",
    "published_iso": PUBLISHED_ISO,
    "modified_iso": REVIEWED_ISO,
    "the_read": {
        "summary": "Integrated Western Canadian midstream. Liquids pipelines (Peace, Northern, Mainline), gas processing, NGL fractionation at Redwater, and the Aux Sable JV. ~90% fee-based or contracted EBITDA. Investment-grade balance sheet; capital culture has been historically conservative.",
        "generated_iso": GENERATED_ISO,
        "source_filing": "Pembina FY 2025 disclosure and Q4 2025 release (February 2026)",
        "principal_reviewed_iso": REVIEWED_ISO,
    },
    "fy_snapshot": {
        "period": "FY 2025",
        "metrics": [
            {"label": "Fee-based share of EBITDA", "value": "~90%"},
            {"label": "Liquids pipelines", "value": "Peace + Northern + Cochin systems"},
            {"label": "NGL fractionation", "value": "Redwater Complex + Aux Sable interests"},
            {"label": "Net debt / EBITDA", "value": "~3.5× target"},
            {"label": "Dividend", "value": "Monthly; per-share growth on capital program build-out"},
            {"label": "Capital program", "value": "Disciplined; volumes-driven incremental"},
            {"label": "Listings", "value": "TSX: PPL · NYSE: PBA"},
        ],
    },
    "guidance": None,
    "leadership": {
        "ceo": "Scott Burrows",
        "ceo_since": 2022,
        "chair": "Cynthia Hansen",
        "succession_visible": True,
        "note": "Burrows came from inside as CFO. The bench is visible; the culture is operationally conservative.",
    },
    "what_we_track": [
        "Aux Sable JV contribution and propane pricing",
        "Redwater fractionation capacity utilization",
        "Capital program against contracted volume backlog",
        "Net debt vs. 3.5× target",
        "Insider behaviour and board capital-discipline signals",
    ],
    "checklist": {
        "scoring": scoring(
            ("pass",    "FCF every full year. The 2020 stress saw the dividend held and capex moderated."),
            ("pass",    "Fee-based and take-or-pay EBITDA dominates. Commodity-price exposure is real but small."),
            ("pass",    "Investment-grade; net debt at or near the 3.5× target."),
            ("not_yet", "ROIC on incremental capital has been acceptable but not exceptional. The KKR-CKPC cancellation in 2021 was an honest dent."),
            ("not_yet", "Insider ownership is modest. The Pembina board is more relevant than direct insider buys."),
            ("pass",    "2015: dividend held. 2020: dividend held; capex cut. The record is clean."),
            ("pass",    "Compensation is per-share-aligned. The cancelled CKPC project was a real test of the capital culture, and the culture passed."),
            ("pass",    "Succession is visible; Burrows came from inside."),
            ("pass",    "Pembina's contracted volumes sit on a Western Canadian footprint with structural advantage. The cost-curve discussion is mostly irrelevant."),
            ("pass",    "Underwriting at any realistic Western Canadian volumes path, the contracted base earns. The decade-out picture is favourable."),
        ),
        "pillar_commentary": {
            "I": "<strong>Pillar I. The business.</strong> Pembina earns about 90% of EBITDA from fee-based or take-or-pay contracts. The Peace and Northern liquids pipelines move WCSB volumes; the Cochin system extends to the US Midwest. Redwater is one of the largest NGL fractionation complexes in North America. Aux Sable adds propane-cycle exposure that is volatile but contributes meaningfully on a contracted volume basis.",
            "II": "<strong>Pillar II. The people.</strong> Scott Burrows was promoted from inside in 2022 and brought the operationally conservative culture continuous with the prior tenure. The 2021 decision to cancel the KKR-CKPC project rather than commit at unattractive economics is the cleanest single capital-discipline data point on the desk. Insider ownership is modest; compensation is per-share-aligned.",
            "III": "<strong>Pillar III. The cycle.</strong> Western Canadian midstream is structurally a long-cycle business. WCSB volumes are durable; the LNG-export expansion adds incremental gas processing demand. Underwriting at any realistic volumes path, Pembina's contracted EBITDA grows in line with rate-base expansion. The decade-out question is regulatory, not commodity.",
        },
    },
    "last_reviewed_iso": REVIEWED_ISO,
    "next_earnings_iso": None,
    "position_disclosure": "may_hold",
    "disclosure_footnote_html": disclosure("Pembina Pipeline Corporation", "Pembina's FY 2025 disclosure and Q4 2025 release (February 2026)"),
    "back_link": BACK_LINK,
    "related_slugs": ["enbridge-enb", "tc-energy-trp"],
    "body_md": (
        "Pembina is the Western Canadian midstream business other Western Canadian midstream businesses measure themselves against. Liquids pipelines, gas processing, NGL fractionation. About 90% of EBITDA is fee-based or take-or-pay. The capital culture has been historically conservative. The 2021 CKPC cancellation is the cleanest single capital-discipline decision the desk has on file.\n\n"
        "## The business, in one paragraph\n"
        "Pembina operates the Peace, Northern, and Mainline liquids systems across Alberta and BC, with the Cochin system extending to the US Midwest. Gas processing facilities serve the Montney and Deep Basin. Redwater is one of the largest NGL fractionation complexes in North America. The Aux Sable joint venture in the US Midwest adds propane-cycle exposure on a contracted volume basis. The combined business is contracted enough to be predictable and commodity-exposed enough to participate when the WCSB tape is strong.\n\n"
        "## What FY 2025 actually said\n"
        "EBITDA grew at the targeted rate. The dividend was raised in line with the per-share growth target. Capital was deployed against the volume-contracted backlog rather than speculative builds. Net debt finished the year at or near the 3.5× target. The Aux Sable contribution was meaningful and improving on a propane-cycle that was generous in patches.\n\n"
        "## Two things we are reading carefully\n"
        "### 1. The CKPC cancellation as a culture signal\n"
        "In 2021 Pembina decided not to commit to a multi-billion dollar Canadian Kuwait Petrochemicals project at the economics on offer. The decision to walk rather than escalate is the cleanest single capital-discipline data point on the desk. We watch every new project announcement against that reference. The 2025 capital program continued in the same posture.\n\n"
        "### 2. Aux Sable in the propane cycle\n"
        "Aux Sable is a meaningful contributor that introduces propane-pricing volatility into an otherwise predictable EBITDA base. We track the contracted-volume share of Aux Sable's contribution and the realized propane price separately. The contracted volume is the part that should be underwritten; the realized price is the part that adds noise.\n\n"
        "## What we are watching into FY 2026\n"
        "- <strong>Redwater fractionation</strong> utilization.\n"
        "- <strong>Aux Sable</strong> contracted vs. spot contribution mix.\n"
        "- <strong>Capital program</strong> against volume backlog.\n"
        "- <strong>Insider behaviour</strong> and board capital-discipline signals.\n\n"
        "> Pembina is the midstream operator whose discipline shows up loudest in the project it did not build."
    ),
})


# === 11. FTS — Fortis ======================================================= #
OPERATORS.append({
    "slug": "fortis-fts",
    "ticker": "FTS",
    "exchange": "TSX: FTS · NYSE: FTS",
    "name": "Fortis Inc.",
    "short_name": "Fortis",
    "url": "https://www.fortisinc.com/",
    "sector": "Infrastructure",
    "sub_industry": "Utilities",
    "page_eyebrow": "On the desk · Utilities",
    "headline_html": "Fortis (FTS): Fifty-two years of <em>raises,</em> read honestly.",
    "page_title": "Fortis (FTS) — Fifty-two years of raises, read honestly | Halvren Capital",
    "meta_description": "Fortis is a North American regulated utility with the longest dividend-growth record in Canada. Halvren's read on the rate-base trajectory, ITC contribution, and the next decade of regulated growth.",
    "og_title": "Fortis (FTS) — Fifty-two years of raises, read honestly",
    "og_description": "Regulated utility, 51+ years of dividend increases. Halvren's read with FY 2025 numbers and rate-base growth.",
    "og_image": "/og-research.png",
    "published_iso": PUBLISHED_ISO,
    "modified_iso": REVIEWED_ISO,
    "the_read": {
        "summary": "North American regulated utility with ten operating subsidiaries spanning Canada, the US, and the Caribbean. ITC (US transmission), UNS (Arizona), FortisBC, FortisAlberta, Central Hudson (New York). The longest dividend-growth record in Canada (over fifty consecutive annual raises).",
        "generated_iso": GENERATED_ISO,
        "source_filing": "Fortis FY 2025 disclosure and Q4 2025 release (February 2026)",
        "principal_reviewed_iso": REVIEWED_ISO,
    },
    "fy_snapshot": {
        "period": "FY 2025",
        "metrics": [
            {"label": "Regulated rate base", "value": "~C$45B (FY 2025 mid, approx.)"},
            {"label": "5-year capital plan", "value": "~C$26B (2024–28)"},
            {"label": "Rate-base growth target", "value": "~6% CAGR"},
            {"label": "Dividend growth target", "value": "4–6% per year"},
            {"label": "Consecutive raises", "value": "52 years (longest in Canada)"},
            {"label": "Regulated share of earnings", "value": "~99% regulated"},
            {"label": "Listings", "value": "TSX: FTS · NYSE: FTS"},
        ],
    },
    "guidance": None,
    "leadership": {
        "ceo": "David Hutchens",
        "ceo_since": 2021,
        "chair": "Ronald Munkley",
        "succession_visible": True,
        "note": "Hutchens came from UNS into the parent CEO seat. The capital culture is continuous with the Marshall and Perry tenures before him.",
    },
    "what_we_track": [
        "ITC capital deployment and authorized ROE",
        "Rate cases at UNS, FortisBC, and Central Hudson",
        "Capital plan execution against the rate-base growth target",
        "Net debt rating actions",
        "Per-share dividend growth pace within the 4–6% band",
    ],
    "checklist": {
        "scoring": scoring(
            ("pass",    "FCF through every cycle since the early 1970s. The regulated-rate-base model is the structural reason."),
            ("pass",    "Unit economics are regulated. Trough commodity prices barely move the earnings."),
            ("pass",    "Investment-grade; well-laddered debt; conservatively financed for a utility."),
            ("pass",    "Reinvestment record is the cleanest on the desk. The ITC and Central Hudson acquisitions earned their cost of capital."),
            ("not_yet", "Insider ownership is modest. Capital allocation behaviour at the board is the more important read."),
            ("pass",    "2015 and 2020: dividend raised in both years. Fifty-two consecutive years of raises is the record."),
            ("pass",    "Compensation is per-share-aligned. The board is discipline-oriented."),
            ("pass",    "Succession is visible; Hutchens came from UNS into the parent seat."),
            ("pass",    "Regulated rate base is the cleanest structural advantage on the desk. The cost-curve discussion does not apply."),
            ("pass",    "Underwriting at any realistic North American electricity-demand path, the regulated rate base earns. The decade-out picture is favourable, particularly with electrification."),
        ),
        "pillar_commentary": {
            "I": "<strong>Pillar I. The business.</strong> Fortis is 99% regulated. The rate base sits on ten operating subsidiaries that collectively span Canada, the US, and the Caribbean. ITC is the US transmission asset that came over in 2016 and has performed at or above the original case. The reinvestment record is the cleanest on the desk; every meaningful acquisition has earned its cost of capital. The capital plan is sized for a 6% rate-base CAGR.",
            "II": "<strong>Pillar II. The people.</strong> David Hutchens came from UNS into the parent CEO seat in 2021 and the capital culture is continuous with the long Marshall and Perry tenures before him. The dividend has been raised in every year of every cycle since 1972. The 2015 and 2020 records are unremarkable in the best sense of the word; nothing changed.",
            "III": "<strong>Pillar III. The cycle.</strong> Electric utility rate base is a long-cycle, regulated asset. The decade-out picture is favourable: electrification, data center demand, grid replacement, transmission build. Underwriting at the 4–6% dividend growth band, Fortis is a compounder. Not a dramatic one. The kind whose total return record over forty years is hard to argue with.",
        },
    },
    "last_reviewed_iso": REVIEWED_ISO,
    "next_earnings_iso": None,
    "position_disclosure": "may_hold",
    "disclosure_footnote_html": disclosure("Fortis Inc.", "Fortis's FY 2025 disclosure and Q4 2025 release (February 2026)"),
    "back_link": BACK_LINK,
    "related_slugs": ["enbridge-enb", "tc-energy-trp"],
    "body_md": (
        "Fortis is the least exciting name on the desk and one of the more important to read carefully. Fifty-two consecutive years of dividend increases is not a marketing line; it is the receipt for a capital culture that has compounded a regulated rate base through every cycle since the early 1970s. We read Fortis as the reference compound on the infrastructure side of the universe.\n\n"
        "## The business, in one paragraph\n"
        "Fortis owns ten regulated utility subsidiaries. ITC is the US transmission business based in Michigan and is the largest single contributor. UNS Energy serves Arizona. FortisBC and FortisAlberta serve Western Canada. Central Hudson serves New York's Hudson Valley. Smaller subsidiaries operate in Newfoundland and Labrador, Prince Edward Island, Ontario, the Cayman Islands, and Belize. Roughly 99% of earnings are regulated.\n\n"
        "## What FY 2025 actually said\n"
        "The regulated rate base grew at the targeted rate. The five-year capital plan was reiterated at approximately C$26B for 2024–28. The dividend was raised within the 4–6% target growth band for the fifty-second consecutive year. Net debt remained at the conservatively-levered end of the utility cohort. Rate cases at the operating subsidiaries proceeded broadly as expected; ITC continued to deploy capital against the high-voltage transmission build the US grid requires.\n\n"
        "## Two things we are reading carefully\n"
        "### 1. ITC and the US transmission build\n"
        "ITC was the 2016 acquisition that materially re-shaped Fortis. The US high-voltage transmission system has years of underinvestment to repair, and ITC is positioned in the right geographies to deploy the next decade of that capital. We track the ITC capital plan, the authorized ROE band, and the regulatory cadence in each of its FERC-regulated jurisdictions.\n\n"
        "### 2. The per-share dividend growth pace\n"
        "The 4–6% band is generous. The pace within that band is the part the principal sets each year, and is informative. We watch the per-share growth pace as a leading indicator of how comfortable management is with the capital plan execution. A 6% raise is a confident year. A 4% raise is a careful one.\n\n"
        "## What we are watching into FY 2026\n"
        "- <strong>ITC capital deployment</strong> and authorized-ROE band.\n"
        "- <strong>Rate cases</strong> at UNS, FortisBC, and Central Hudson.\n"
        "- <strong>Capital plan execution</strong> against the 6% rate-base CAGR.\n"
        "- <strong>Per-share dividend pace</strong> within the 4–6% target band.\n\n"
        "> A regulated utility is the boring half of the desk. The boring half is the part that pays for the wait."
    ),
})


# === 12. CNR — Canadian National Railway ==================================== #
OPERATORS.append({
    "slug": "cn-rail-cnr",
    "ticker": "CNR",
    "exchange": "TSX: CNR · NYSE: CNI",
    "name": "Canadian National Railway Company",
    "short_name": "CN Rail",
    "url": "https://www.cn.ca/",
    "sector": "Infrastructure",
    "sub_industry": "Rail",
    "page_eyebrow": "On the desk · Rail",
    "headline_html": "CN Rail (CNR): The <em>duopoly,</em> read by the operating ratio.",
    "page_title": "CN Rail (CNR) — The duopoly, read by the operating ratio | Halvren Capital",
    "meta_description": "Canadian National is the larger half of the Canadian Class I duopoly and a coast-to-coast-to-Gulf network. Halvren's read on the operating ratio, the volumes mix, and the post-Tellem capital culture.",
    "og_title": "CN Rail (CNR) — The duopoly, read by the operating ratio",
    "og_description": "Class I rail, Canada coast-to-coast plus US Gulf. Halvren's read with FY 2025 numbers, operating ratio, and capital discipline.",
    "og_image": "/og-research.png",
    "published_iso": PUBLISHED_ISO,
    "modified_iso": REVIEWED_ISO,
    "the_read": {
        "summary": "Larger half of the Canadian Class I rail duopoly. Network spans Atlantic Canada, the BC Coast, and the US Gulf via Memphis–New Orleans. Volume mix includes intermodal, grain, forest products, energy, and metals. Tracy Robinson (CEO since February 2022) inherited a precision-scheduled-railroading legacy and is calibrating capital and labour discipline against it.",
        "generated_iso": GENERATED_ISO,
        "source_filing": "CN FY 2025 disclosure and Q4 2025 release (January 2026)",
        "principal_reviewed_iso": REVIEWED_ISO,
    },
    "fy_snapshot": {
        "period": "FY 2025",
        "metrics": [
            {"label": "Network length", "value": "~32,000 km (Canada + US)"},
            {"label": "Operating ratio", "value": "Low 60s (FY 2025 mid, approx.)"},
            {"label": "Volume mix", "value": "Intermodal · Grain · Forest · Energy · Metals"},
            {"label": "Capital program", "value": "~C$3.5–4.0B annual"},
            {"label": "Capital return policy", "value": "Dividend + buyback; per-share-aligned"},
            {"label": "Investment-grade", "value": "Long-tenured; conservative debt"},
            {"label": "Listings", "value": "TSX: CNR · NYSE: CNI"},
        ],
    },
    "guidance": None,
    "leadership": {
        "ceo": "Tracy Robinson",
        "ceo_since": 2022,
        "chair": "Robert Pace",
        "succession_visible": True,
        "note": "Robinson came from TC Energy and a long pipelines and operations career. The operating-ratio discipline shows in the run-rate.",
    },
    "what_we_track": [
        "Operating ratio quarter to quarter",
        "Intermodal volumes against North American consumer trend",
        "Grain volumes against the WCSB harvest",
        "Capital program against the ~C$3.5–4.0B run-rate",
        "Insider behaviour and labour-cost discipline",
    ],
    "checklist": {
        "scoring": scoring(
            ("pass",    "FCF every full year. The duopoly structure is the structural reason."),
            ("pass",    "Unit economics are favourable across the cycle. The trough is meaningful but not existential."),
            ("pass",    "Investment-grade; long-tenured. Net debt is conservatively levered."),
            ("not_yet", "ROIC on incremental capital has been acceptable; the failed 2021 Kansas City Southern bid was an honest near-miss."),
            ("not_yet", "Insider ownership is modest. The board capital-discipline record is what we read."),
            ("pass",    "2015 and 2020: dividend raised in both years. Buyback continued through both."),
            ("pass",    "Compensation is per-share-aligned. The operating-ratio focus is the right incentive structure."),
            ("pass",    "Succession is visible; Robinson came from outside, the executive bench is named."),
            ("pass",    "The Canadian Class I duopoly is the cleanest structural advantage in North American transportation. Cost-curve does not apply."),
            ("pass",    "Underwriting at any realistic North American freight volume path, CN compounds. The decade-out picture is favourable."),
        ),
        "pillar_commentary": {
            "I": "<strong>Pillar I. The business.</strong> CN is the larger half of a two-operator duopoly that moves freight across Canada and into the US Gulf via the Memphis–New Orleans corridor. The duopoly structure is the moat. Operating ratio in the low 60s is competitive within the North American Class I cohort; the question is whether that ratio can move lower without sacrificing service quality. The 2021 attempt at Kansas City Southern was an honest near-miss; the post-2022 capital culture is more disciplined than the 2018–2021 vintage.",
            "II": "<strong>Pillar II. The people.</strong> Tracy Robinson came from outside in February 2022 with a long pipeline and operations career at TC Energy and predecessors. The operating-ratio focus is right and the early results are encouraging. Compensation is per-share-aligned. The 2015 and 2020 records are clean. Insider ownership is modest; the board is the discipline.",
            "III": "<strong>Pillar III. The cycle.</strong> North American freight is structurally a long-cycle asset, and the rail share of it is durable in the categories that matter (grain, metals, forest, energy). Intermodal is more contestable. Underwriting at mid-cycle North American freight, CN compounds. The decade-out question is service-quality regulation and the labour cost structure.",
        },
    },
    "last_reviewed_iso": REVIEWED_ISO,
    "next_earnings_iso": None,
    "position_disclosure": "may_hold",
    "disclosure_footnote_html": disclosure("Canadian National Railway Company", "CN's FY 2025 disclosure and Q4 2025 release (January 2026)"),
    "back_link": BACK_LINK,
    "related_slugs": ["enbridge-enb", "fortis-fts"],
    "body_md": (
        "CN Rail is the larger half of a duopoly that moves North American freight. The network spans Atlantic Canada through the BC Coast and south to the US Gulf via Memphis and New Orleans. The duopoly structure is the moat. The operating ratio is the metric that determines whether the moat earns. We read CN as a long-cycle, duopoly franchise where the question is operating discipline, not market share.\n\n"
        "## The business, in one paragraph\n"
        "CN operates approximately 32,000 km of track and moves a mix of intermodal, grain, forest products, energy, metals, and chemicals. The network's structural advantage is the only Class I that touches both the Atlantic and Pacific Canadian coasts and reaches the US Gulf via the IC corridor acquired in 1998. Operating ratio sits in the low 60s in FY 2025, competitive within the North American Class I cohort. The capital program runs at roughly C$3.5–4.0B per year, focused on capacity, safety, and locomotive renewal.\n\n"
        "## What FY 2025 actually said\n"
        "Volumes were mixed by category. Grain was strong on a generous WCSB harvest. Intermodal was softer on the North American consumer cycle. Energy volumes held. The operating ratio finished the year in the low 60s, in line with management's target. Capital was deployed at the C$3.5–4.0B run-rate. The dividend was raised; the buyback continued. Net debt remained at the conservatively-levered end of the Class I cohort.\n\n"
        "## Two things we are reading carefully\n"
        "### 1. Whether the operating ratio compresses further\n"
        "The post-2022 capital culture under Tracy Robinson is more disciplined than the 2018–2021 vintage. The operating ratio has been trending in the right direction. The honest test is whether the low 60s holds without sacrificing service quality, particularly in the labour-intensive intermodal and grain businesses. We track the ratio quarter to quarter and read the service-quality metrics separately.\n\n"
        "### 2. The intermodal franchise against the North American consumer\n"
        "Intermodal is the most contestable category in the rail mix. It also responds the most to the North American consumer cycle. We track intermodal volumes against the broader North American container tape and the ratio of intermodal yield to non-intermodal yield. The mix matters.\n\n"
        "## What we are watching into FY 2026\n"
        "- <strong>Operating ratio</strong> by quarter and by segment.\n"
        "- <strong>Intermodal volumes</strong> and yield.\n"
        "- <strong>Grain volumes</strong> against the WCSB harvest.\n"
        "- <strong>Capital program</strong> at the C$3.5–4.0B run-rate.\n\n"
        "> A duopoly franchise is the cleanest structural advantage on the desk. The question is what the duopoly does with it."
    ),
})


# === 13. OXY — Occidental Petroleum ========================================= #
OPERATORS.append({
    "slug": "occidental-oxy",
    "ticker": "OXY",
    "exchange": "NYSE: OXY",
    "name": "Occidental Petroleum Corporation",
    "short_name": "Occidental",
    "url": "https://www.oxy.com/",
    "sector": "Energy",
    "sub_industry": "Oil & Gas",
    "page_eyebrow": "On the desk · Permian",
    "headline_html": "Occidental (OXY): The <em>Permian operator</em> Buffett blessed.",
    "page_title": "Occidental (OXY) — The Permian operator Buffett blessed | Halvren Capital",
    "meta_description": "Occidental is the Permian-weighted US producer with the CrownRock acquisition behind it, an OxyChem segment that smooths the worst commodity quarter, and a carbon-capture option few competitors have. Halvren's read.",
    "og_title": "Occidental (OXY) — The Permian operator Buffett blessed",
    "og_description": "Permian, Anadarko legacy, OxyChem. Halvren's read with FY 2025 numbers, CrownRock integration, and capital discipline.",
    "og_image": "/og-research.png",
    "published_iso": PUBLISHED_ISO,
    "modified_iso": REVIEWED_ISO,
    "the_read": {
        "summary": "Permian-weighted US producer with a meaningful OxyChem chemicals segment and a developing carbon-capture business at Stratos. The 2024 CrownRock acquisition added Midland Basin acreage. Berkshire Hathaway holds a 28%-plus stake (approx.). Vicki Hollub has been CEO since 2016 and led the Anadarko acquisition and post-acquisition recovery.",
        "generated_iso": GENERATED_ISO,
        "source_filing": "Occidental FY 2025 disclosure and Q4 2025 release (February 2026)",
        "principal_reviewed_iso": REVIEWED_ISO,
    },
    "fy_snapshot": {
        "period": "FY 2025",
        "metrics": [
            {"label": "Total production", "value": "~1.4 MMboe/d (post-CrownRock, approx.)"},
            {"label": "Permian weight", "value": "~50%+ of total production"},
            {"label": "OxyChem EBITDA", "value": "Meaningful counter-cyclical contributor"},
            {"label": "Net debt walk", "value": "Toward US$15B near-term target"},
            {"label": "Carbon-capture", "value": "Stratos start-up; longer-cycle optionality"},
            {"label": "Berkshire stake", "value": "~28%+ (approx.)"},
            {"label": "Listings", "value": "NYSE: OXY"},
        ],
    },
    "guidance": None,
    "leadership": {
        "ceo": "Vicki Hollub",
        "ceo_since": 2016,
        "chair": "Avedick Poladian",
        "succession_visible": False,
        "note": "Hollub has been the principal capital allocator for a decade. The succession question is the open Pillar II point.",
    },
    "what_we_track": [
        "Permian per-well productivity post-CrownRock",
        "OxyChem realized prices and the counter-cyclical contribution",
        "Net debt walk toward the near-term target",
        "Stratos and the carbon-capture commercial pathway",
        "Berkshire activity and warrant exercise",
    ],
    "checklist": {
        "scoring": scoring(
            ("not_yet", "FCF through full cycle is positive on average; 2015–2016 stress was real and the dividend was cut."),
            ("pass",    "Permian unit economics at US$50 WTI are sound. OxyChem is a counter-cyclical contributor that smooths the worst quarter."),
            ("not_yet", "Net debt remains elevated post-CrownRock; the walk to the US$15B target is the near-term work."),
            ("not_yet", "The Anadarko acquisition was the defining capital decision; the verdict has improved since but cost the dividend in 2020."),
            ("not_yet", "Insider ownership is modest at the executive level. The Berkshire stake is the more important capital signal."),
            ("not_yet", "2015: dividend cut. 2020: dividend cut to a penny. Both were rational; neither was clean."),
            ("not_yet", "Compensation is partially per-share-aligned. The legacy Anadarko-era plan was production-sized."),
            ("not_yet", "Succession is not visible. Hollub has been CEO for a decade. The bench question is real."),
            ("pass",    "Permian acreage post-CrownRock sits in the first quartile of US shale economics."),
            ("pass",    "Underwriting at mid-cycle WTI of US$65–75, Occidental produces meaningful free cash. OxyChem is the structural hedge.",),
        ),
        "pillar_commentary": {
            "I": "<strong>Pillar I. The business.</strong> Occidental is the Permian-weighted US producer with a meaningful OxyChem segment that prints counter-cyclical cash. The 2019 Anadarko acquisition was the defining capital decision of the prior cycle and the 2024 CrownRock acquisition extended the Midland Basin position. Per-well productivity in the new acreage is the part FY 2026 will test. The carbon-capture business at Stratos is a longer-cycle option whose commercial pathway is being negotiated rather than proven.",
            "II": "<strong>Pillar II. The people.</strong> Vicki Hollub has been CEO since 2016 and is the principal capital allocator. The Anadarko decision was bold and costly in 2020; the post-2020 recovery has been impressive. The Berkshire 28%-plus stake is a meaningful Pillar II signal that we read as a quality vote on the capital culture. Compensation is incrementally per-share-aligned. Succession is the open question.",
            "III": "<strong>Pillar III. The cycle.</strong> Permian per-well productivity has continued to improve through the cycle. OxyChem is a structurally counter-cyclical contributor. Carbon capture is a long-cycle option whose commercial economics are still being built. Underwriting at mid-cycle US$65–75 WTI, Occidental produces meaningful free cash. The decade-out question is what role Permian shale plays as the US gas-and-LNG complex grows, and how Occidental positions for the answer.",
        },
    },
    "last_reviewed_iso": REVIEWED_ISO,
    "next_earnings_iso": None,
    "position_disclosure": "may_hold",
    "disclosure_footnote_html": disclosure("Occidental Petroleum Corporation", "Occidental's FY 2025 disclosure and Q4 2025 release (February 2026)"),
    "back_link": BACK_LINK,
    "related_slugs": ["eog-resources", "canadian-natural-cnq"],
    "body_md": (
        "Occidental is the Permian producer with three distinguishing pieces of optionality. The Permian itself, which the August 2024 CrownRock acquisition extended into the Midland Basin. The OxyChem chemicals segment, which prints counter-cyclical cash when the upstream is weak. And the carbon-capture business at Stratos, whose commercial pathway is the part the market keeps over-modelling or under-modelling depending on the week.\n\n"
        "## The business, in one paragraph\n"
        "Total production sits around 1.4 MMboe/d post-CrownRock, with the Permian contributing more than half. The Anadarko legacy includes meaningful Gulf of Mexico and international positions. OxyChem produces chlorovinyls and is a top-three North American producer in that category; the chemicals cycle does not move in step with the oil cycle, which is the structural hedge. The Stratos direct-air-capture facility is the proof-of-concept for the carbon-capture business; commercial scale and the carbon-offset pricing pathway are being built.\n\n"
        "## What FY 2025 actually said\n"
        "The CrownRock integration progressed broadly on schedule. Per-well productivity in the new Midland Basin acreage was within the original case. The net debt walk continued toward the US$15B near-term target. The OxyChem segment contributed meaningfully through a chemicals tape that was uneven. Stratos began commercial operations and the first batch of carbon offsets was negotiated. The dividend continued at the modest level set post-2020.\n\n"
        "## Two things we are reading carefully\n"
        "### 1. The CrownRock integration\n"
        "CrownRock was a US$12B-class acquisition that extended Occidental's Midland Basin position at a price that requires the per-well productivity to hold. The early data is encouraging; the 2026 quarterly data is the part that will settle the question. We track type curves, completion intensity, and the unit cost at the integrated assets versus the legacy Occidental acreage.\n\n"
        "### 2. Carbon capture\n"
        "Stratos is the most ambitious carbon-capture commercial program in the industry. The optionality is real; the commercial pathway is not. We track the offset-pricing negotiations, the next facility build pace, and any policy change that affects the underlying economics. The Pillar III thesis improves with credible commercial proof; the Pillar I thesis works without it.\n\n"
        "## What we are watching into FY 2026\n"
        "- <strong>Permian per-well productivity</strong> at the CrownRock acreage.\n"
        "- <strong>OxyChem contribution</strong> through the chemicals cycle.\n"
        "- <strong>Net debt</strong> walk toward US$15B.\n"
        "- <strong>Stratos commercial pathway</strong> and second-facility timing.\n\n"
        "> The Berkshire stake is not the thesis. The integrated business is the thesis. The Berkshire stake is the receipt."
    ),
})


# === 14. FCX — Freeport-McMoRan ============================================= #
OPERATORS.append({
    "slug": "freeport-mcmoran-fcx",
    "ticker": "FCX",
    "exchange": "NYSE: FCX",
    "name": "Freeport-McMoRan Inc.",
    "short_name": "Freeport",
    "url": "https://www.fcx.com/",
    "sector": "Materials",
    "sub_industry": "Industrial Metals",
    "page_eyebrow": "On the desk · Copper",
    "headline_html": "Freeport (FCX): The copper bet with the <em>Grasberg</em> asterisk.",
    "page_title": "Freeport (FCX) — The copper bet with the Grasberg asterisk | Halvren Capital",
    "meta_description": "Freeport-McMoRan is the largest publicly traded copper producer with Grasberg, Cerro Verde, and the Americas portfolio. Halvren's read on the unit economics, the Grasberg country risk, and the post-Adkerson capital culture.",
    "og_title": "Freeport (FCX) — The copper bet with the Grasberg asterisk",
    "og_description": "Copper. Grasberg, Cerro Verde, the Americas. Halvren's read with FY 2025 numbers, the Indonesia overhang, and capital discipline.",
    "og_image": "/og-research.png",
    "published_iso": PUBLISHED_ISO,
    "modified_iso": REVIEWED_ISO,
    "the_read": {
        "summary": "Largest publicly traded copper producer. Grasberg (Indonesia), Cerro Verde (Peru, 53.6%), Morenci (Arizona, 72%), Bagdad (Arizona), Sierrita (Arizona), and El Abra (Chile). Meaningful gold byproduct at Grasberg. Kathleen Quirk succeeded Richard Adkerson as CEO in 2024.",
        "generated_iso": GENERATED_ISO,
        "source_filing": "Freeport-McMoRan FY 2025 disclosure and Q4 2025 release (January 2026)",
        "principal_reviewed_iso": REVIEWED_ISO,
    },
    "fy_snapshot": {
        "period": "FY 2025",
        "metrics": [
            {"label": "Copper production", "value": "~4.0 Blb (FY 2025 mid, approx.)"},
            {"label": "Gold byproduct", "value": "~1.6 Moz (Grasberg-anchored)"},
            {"label": "Grasberg share of EBITDA", "value": "Material"},
            {"label": "Net debt", "value": "Conservative; investment-grade"},
            {"label": "Capital return policy", "value": "50% of FCF after sustaining"},
            {"label": "Indonesia smelter", "value": "Manyar smelter ramp"},
            {"label": "Listings", "value": "NYSE: FCX"},
        ],
    },
    "guidance": None,
    "leadership": {
        "ceo": "Kathleen Quirk",
        "ceo_since": 2024,
        "chair": "Richard Adkerson",
        "succession_visible": True,
        "note": "Quirk was the CFO and operations lead for years. The Adkerson chairmanship preserves the institutional memory.",
    },
    "what_we_track": [
        "Grasberg block-cave throughput and unit cost",
        "Manyar smelter ramp and the Indonesian smelting requirement",
        "Cerro Verde and Morenci unit cost",
        "Capital return execution against the 50% policy",
        "Indonesian regulatory and ownership commentary",
    ],
    "checklist": {
        "scoring": scoring(
            ("not_yet", "FCF through full cycle is positive on average; the 2014–2016 stress was severe and forced a dividend cut and an equity raise."),
            ("pass",    "Grasberg unit economics at the block-cave run-rate are first-quartile. The Americas mines are competitive at mid-cycle copper."),
            ("pass",    "Post-2017 the balance sheet has been walked to conservative levels."),
            ("not_yet", "ROIC on incremental capital is improving; the 2014 Plains All American transaction was the prior generation's expensive lesson."),
            ("not_yet", "Insider ownership is modest. Adkerson's long tenure was the more important signal than direct insider activity."),
            ("fail",    "2015: severe distress; the dividend was cut to zero; equity was issued at distressed prices. 2020: better, dividend reinstated. The record is mixed."),
            ("pass",    "Compensation is per-share-aligned post-2018 reset."),
            ("pass",    "Succession was prepared and executed in 2024; Adkerson remained as chair."),
            ("pass",    "Grasberg block-cave is among the lowest-cost copper operations in the world by per-pound co-product economics."),
            ("not_yet", "Underwriting at mid-cycle copper of US$3.50–4.00/lb works; the Indonesian country risk is the asymmetric tail."),
        ),
        "pillar_commentary": {
            "I": "<strong>Pillar I. The business.</strong> Freeport is the largest publicly traded copper producer. The Grasberg block-cave is among the lowest-cost copper operations in the world on a per-pound co-product basis; gold byproduct is the structural reason. Cerro Verde and Morenci are competitive mid-cycle producers. The capital culture has been materially better post-2017 than during the 2013–2014 Plains All American era.",
            "II": "<strong>Pillar II. The people.</strong> Richard Adkerson ran Freeport for two decades and stewarded the post-2014 recovery. Kathleen Quirk was promoted from inside in 2024 and the operating discipline is continuous. The 2015 record is the Pillar II problem: dividend zeroed, equity issued at distressed prices. Compensation is per-share-aligned post-reset. The Adkerson chairmanship preserves institutional memory.",
            "III": "<strong>Pillar III. The cycle.</strong> Copper demand on the decade-out picture is favourable: electrification, grid build, EV penetration. Grasberg is structurally first-quartile on per-pound co-product economics; the Indonesian country risk is the asymmetric tail. Underwriting at mid-cycle copper of US$3.50–4.00/lb works; the Pillar III risk is whether the Indonesian regulatory and ownership commentary remains accommodating.",
        },
    },
    "last_reviewed_iso": REVIEWED_ISO,
    "next_earnings_iso": None,
    "position_disclosure": "may_hold",
    "disclosure_footnote_html": disclosure("Freeport-McMoRan Inc.", "Freeport-McMoRan's FY 2025 disclosure and Q4 2025 release (January 2026)"),
    "back_link": BACK_LINK,
    "related_slugs": ["teck-resources-teck", "occidental-oxy"],
    "body_md": (
        "Freeport is the largest publicly traded copper producer and the cleanest single expression of the copper supercycle thesis. Grasberg is the structural asset and the structural risk. The Americas mines are competitive at mid-cycle. The 2014–2017 stress is the legitimate Pillar II memory; the post-2018 capital culture is materially better than the pre-2014 vintage.\n\n"
        "## The business, in one paragraph\n"
        "Copper production sits around 4.0 Blb. Grasberg in Indonesia contributes the largest share, supported by significant gold byproduct (~1.6 Moz). Cerro Verde in Peru (53.6%) and Morenci in Arizona (72%) are the other large producing assets. Bagdad, Sierrita, and El Abra round out the portfolio. The Manyar smelter in Indonesia is the post-2024 ramp project required by the Indonesian export regime. The capital return policy distributes 50% of free cash after sustaining capex; net debt is at conservative levels.\n\n"
        "## What FY 2025 actually said\n"
        "Grasberg block-cave throughput continued the ramp profile to design rate. Unit cost at Grasberg printed first-quartile on a per-pound co-product basis. Cerro Verde and Morenci produced in line with plan. The Manyar smelter advanced toward steady-state operation, which is the Indonesian regulatory requirement. The capital return policy distributed against the 50% target. Net debt remained conservative.\n\n"
        "## Two things we are reading carefully\n"
        "### 1. Indonesian country risk\n"
        "Grasberg is the asset, and Indonesia is the jurisdiction. The 2018 ownership restructuring (PT-FI majority Indonesian-controlled) and the 2024 smelter ramp are both pieces of the same regulatory framework. The Pillar III tail is whether the Indonesian commentary on ownership, royalties, and export rules remains accommodating through political cycles. We track the regulatory tape carefully.\n\n"
        "### 2. The post-Adkerson capital culture\n"
        "Kathleen Quirk was promoted from inside in 2024. Adkerson remained as chair. The institutional memory of the 2014–2017 stress is preserved by that arrangement. The honest test is whether the next downturn produces the discipline of 2018 onwards rather than the over-extension of 2013–2014. The Adkerson chairmanship is a soft governance signal that increases our confidence on Pillar II.\n\n"
        "## What we are watching into FY 2026\n"
        "- <strong>Grasberg block-cave throughput</strong> and unit cost.\n"
        "- <strong>Manyar smelter ramp</strong> and Indonesian regulatory commentary.\n"
        "- <strong>Cerro Verde and Morenci</strong> unit cost.\n"
        "- <strong>Capital return execution</strong> against the 50% policy.\n\n"
        "> Grasberg is the asset, and the asset is in Indonesia. The thesis is the copper. The asterisk is the jurisdiction."
    ),
})


# === 15. KMI — Kinder Morgan =============================================== #
OPERATORS.append({
    "slug": "kinder-morgan-kmi",
    "ticker": "KMI",
    "exchange": "NYSE: KMI",
    "name": "Kinder Morgan, Inc.",
    "short_name": "Kinder Morgan",
    "url": "https://www.kindermorgan.com/",
    "sector": "Infrastructure",
    "sub_industry": "Pipelines",
    "page_eyebrow": "On the desk · US natural gas",
    "headline_html": "Kinder Morgan (KMI): The US gas <em>backbone,</em> read for the contract.",
    "page_title": "Kinder Morgan (KMI) — The US gas backbone, read for the contract | Halvren Capital",
    "meta_description": "Kinder Morgan operates the largest US natural gas pipeline network. Halvren's read on the take-or-pay contract share, the LNG-export-driven volumes growth, and the capital discipline post-2015.",
    "og_title": "Kinder Morgan (KMI) — The US gas backbone, read for the contract",
    "og_description": "Largest US gas pipeline operator. Halvren's read with FY 2025 numbers, LNG-export volumes, and capital culture.",
    "og_image": "/og-research.png",
    "published_iso": PUBLISHED_ISO,
    "modified_iso": REVIEWED_ISO,
    "the_read": {
        "summary": "Largest US natural gas pipeline operator. ~70,000 miles of gas pipeline; smaller liquids, terminals, and CO2 segments. The 2015 dividend cut and balance-sheet repair defined the post-Rich-Kinder era. Kim Dang became CEO in August 2023. Take-or-pay and demand-driven contracts dominate; LNG export demand is the structural tailwind.",
        "generated_iso": GENERATED_ISO,
        "source_filing": "Kinder Morgan FY 2025 disclosure and Q4 2025 release (January 2026)",
        "principal_reviewed_iso": REVIEWED_ISO,
    },
    "fy_snapshot": {
        "period": "FY 2025",
        "metrics": [
            {"label": "Gas pipeline network", "value": "~70,000 miles"},
            {"label": "Take-or-pay / demand share", "value": ">90% of EBITDA"},
            {"label": "LNG-export feedgas exposure", "value": "Material and growing"},
            {"label": "Net debt / EBITDA", "value": "~4.0× target"},
            {"label": "Capital program", "value": "~US$2.0–2.5B annual run-rate"},
            {"label": "Dividend", "value": "Quarterly; per-share growth tied to capital plan"},
            {"label": "Listings", "value": "NYSE: KMI"},
        ],
    },
    "guidance": None,
    "leadership": {
        "ceo": "Kim Dang",
        "ceo_since": 2023,
        "chair": "Richard Kinder",
        "succession_visible": True,
        "note": "Dang came from inside; Rich Kinder remains as chair and a meaningful insider holder.",
    },
    "what_we_track": [
        "Take-or-pay contract roll and re-contracting rates",
        "LNG-export feedgas demand growth",
        "Capital program at the US$2.0–2.5B run-rate",
        "Net debt vs. 4.0× target",
        "Insider behaviour, particularly Rich Kinder's open-market activity",
    ],
    "checklist": {
        "scoring": scoring(
            ("pass",    "FCF through every full year since the 2015 reset. The dividend was cut in 2015; it has been raised since."),
            ("pass",    "Take-or-pay and demand-driven contracts dominate. Commodity exposure is real but small."),
            ("pass",    "Investment-grade; net debt at or near the 4.0× target."),
            ("not_yet", "ROIC on incremental capital is acceptable; the 2014–2015 over-extension is the legitimate Pillar II reference."),
            ("pass",    "Rich Kinder's open-market activity is the cleanest insider signal on the desk. He has bought consistently."),
            ("not_yet", "2015 was the dividend cut. 2020: dividend held. The 2015 cut was a Pillar II event that the business learned from."),
            ("pass",    "Compensation is per-share-aligned post-2015 reset. The capital culture is materially better than the pre-2015 vintage."),
            ("pass",    "Succession is visible; Dang came from inside, Kinder remains as chair."),
            ("pass",    "The US gas pipeline footprint is the cleanest structural advantage in US infrastructure. Cost-curve does not apply."),
            ("pass",    "Underwriting at any realistic US gas demand path, the contracted base earns. LNG export is the structural tailwind."),
        ),
        "pillar_commentary": {
            "I": "<strong>Pillar I. The business.</strong> Kinder Morgan operates the largest US natural gas pipeline network. More than 90% of EBITDA is take-or-pay or demand-driven. The LNG-export tailwind is meaningful and growing; KMI's pipelines feed multiple Gulf Coast LNG facilities. The smaller terminals and CO2 segments contribute predictably. The 2015 dividend cut and balance-sheet repair was the painful but necessary reset.",
            "II": "<strong>Pillar II. The people.</strong> Rich Kinder remains as chair and is the cleanest insider signal on the entire desk: he has bought consistently over decades with open-market money. Kim Dang was promoted from inside in 2023 and the capital culture is continuous. The 2015 cut is the Pillar II reference event. The post-2015 record is materially cleaner than the pre-2015 vintage.",
            "III": "<strong>Pillar III. The cycle.</strong> US natural gas demand growth on the decade-out picture is favourable: LNG export, gas-fired power generation, industrial. Pipeline rate base earns through the cycle. The structural tailwind from LNG export is real; the question is whether the capital program remains disciplined as the demand pulls. We track the capital program against the take-or-pay contract roll.",
        },
    },
    "last_reviewed_iso": REVIEWED_ISO,
    "next_earnings_iso": None,
    "position_disclosure": "may_hold",
    "disclosure_footnote_html": disclosure("Kinder Morgan, Inc.", "Kinder Morgan's FY 2025 disclosure and Q4 2025 release (January 2026)"),
    "back_link": BACK_LINK,
    "related_slugs": ["enbridge-enb", "tc-energy-trp"],
    "body_md": (
        "Kinder Morgan is the largest US natural gas pipeline operator and the cleanest single expression of the LNG-export feedgas tailwind. Rich Kinder remains as chair and is the cleanest insider signal on the entire Halvren desk. He has bought consistently over decades with open-market money. We read Kinder Morgan as a pipeline rate base with a structural tailwind and a founder still in the room.\n\n"
        "## The business, in one paragraph\n"
        "KMI operates approximately 70,000 miles of natural gas pipeline across the US, connecting producing basins (Permian, Haynesville, Marcellus, Eagle Ford) to demand centres (Gulf Coast LNG, Mexico, US power generators). Smaller segments include CO2 (for EOR), terminals, and a modest liquids pipelines business. More than 90% of EBITDA is take-or-pay or demand-driven contracted. The 2015 dividend cut and balance-sheet repair was the painful Pillar II event; the post-2015 capital culture is materially better than the pre-2015 vintage.\n\n"
        "## What FY 2025 actually said\n"
        "LNG-export feedgas volumes continued to grow as the next wave of US Gulf Coast capacity ramped. The capital program ran at the US$2.0–2.5B annual run-rate target. Net debt finished the year at or near the 4.0× target. The dividend was raised in line with the per-share growth target. Rich Kinder's open-market purchase activity continued. That last sentence is the part we read most carefully.\n\n"
        "## Two things we are reading carefully\n"
        "### 1. Take-or-pay contract roll and LNG-export feedgas growth\n"
        "More than 90% of EBITDA is take-or-pay or demand-driven contracted. The contract roll over 2026–2028 is the part the desk tracks closely. The LNG-export feedgas demand is the structural tailwind. We watch the re-contracting rates at the rolling tranches and the new-build feedgas contract pipeline.\n\n"
        "### 2. Rich Kinder's open-market activity\n"
        "Open-market insider purchases by the founder of an operating business are the cleanest Pillar II signal. Rich Kinder has bought consistently over decades. We track the cadence and the absolute size; either an acceleration or a slowdown is informative.\n\n"
        "## What we are watching into FY 2026\n"
        "- <strong>LNG-export feedgas volumes</strong> and contracted growth.\n"
        "- <strong>Take-or-pay contract roll</strong> at the 2026–2028 tranches.\n"
        "- <strong>Capital program</strong> at the US$2.0–2.5B run-rate.\n"
        "- <strong>Insider activity</strong>, particularly Rich Kinder's open-market purchases.\n\n"
        "> A pipeline is a toll-road. A pipeline whose founder is still buying is the kind of toll-road we sit with."
    ),
})


# --------------------------------------------------------------------------- #
# emitter
# --------------------------------------------------------------------------- #

JSON_FIELD_ORDER = [
    "slug", "ticker", "exchange", "name", "short_name", "url",
    "sector", "sub_industry",
    "page_eyebrow", "headline_html",
    "page_title", "meta_description",
    "og_title", "og_description", "og_image",
    "published_iso", "modified_iso",
    "the_read", "fy_snapshot", "guidance",
    "leadership", "what_we_track", "checklist",
    "last_reviewed_iso", "next_earnings_iso",
    "position_disclosure", "disclosure_footnote_html",
    "back_link", "related_slugs",
]


def emit(op: dict) -> None:
    slug = op["slug"]
    body = op.pop("body_md")
    # rebuild dict with stable field order for diff-friendliness
    ordered = {k: op[k] for k in JSON_FIELD_ORDER if k in op}
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    CONTENT_DIR.mkdir(parents=True, exist_ok=True)
    (DATA_DIR / f"{slug}.json").write_text(
        json.dumps(ordered, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    (CONTENT_DIR / f"{slug}.md").write_text(body, encoding="utf-8")
    print(f"  wrote {slug}")


def main() -> int:
    print(f"_sprint2_seed: writing {len(OPERATORS)} operators")
    for op in OPERATORS:
        emit(op)
    print(f"_sprint2_seed: done — {len(OPERATORS)} JSON + {len(OPERATORS)} MD")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

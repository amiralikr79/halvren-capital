#!/usr/bin/env python3
"""
inject_faq_jsonld.py

Sprint 7 — inject FAQPage JSON-LD into:
  - /about.html               (5 Q&A pairs distilled from the new About copy)
  - /notes/<slug>.html        (3 Q&A pairs per note, distilled from each)

The FAQ payload sits inside a second <script type="application/ld+json">
block right after the existing Article / AboutPage block. Each script is
idempotent: re-running the script replaces the FAQ block, doesn't append.

No third-party deps. Run from repo root:
  python3 scripts/inject_faq_jsonld.py
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

ABOUT_FAQ = [
    (
        "What is Halvren Capital?",
        "Halvren Capital is a one-principal research desk in Vancouver. It covers twenty operators in Canadian and U.S. energy, materials, and infrastructure, deeply, with no managed product and no outside capital.",
    ),
    (
        "Who runs Halvren Capital?",
        "Amirali Karimi, principal and founder. Persian-Canadian, raised in Vancouver. A decade of work split between operating businesses (Karimi Developments in BC real estate; Tablo, a software venture sold to Digikala in 2023; and Boost Commerce Group, a Canadian digital holding) and investing on principal capital. IFC passed April 2026, CIRO exams in progress, CFA candidate.",
    ),
    (
        "What does 'AI-augmented' mean at Halvren?",
        "Models read filings, transcripts, and pricing across the coverage universe at a cadence one analyst could not match by hand. The principal reviews every conviction, signs every position, and writes every public letter. There is no proprietary model, no internal LLM, no algorithmic alpha. The desk uses widely available tools at the volume the work requires.",
    ),
    (
        "Why Canadian and U.S. energy, materials, and infrastructure?",
        "The sectors are chosen because they are where boring, long-cycle businesses still compound — Canadian heavy oil, gas pipelines, regulated utilities, copper, lumber, fertilizer, rail — and because they sit far enough from the institutional consensus that careful reading still pays. The Canadian weighting is structural: it is easier to know a Canadian operator from the inside than to guess at a Texan or an Australian one.",
    ),
    (
        "How does Halvren publish, and is it free?",
        "The public research is free, including the Halvren Checklist, the 20-operator coverage universe, the research archive, and Halvren Notes. The quarterly Halvren letter goes through Substack, where the email list lives; the site itself collects nothing. Halvren manages proprietary capital and is not currently accepting outside investors.",
    ),
]

NOTES_FAQ = {
    "how-to-read-canadian-oil-gas-operator-seven-numbers": [
        ("What are the seven numbers Halvren reads on a Canadian oil and gas operator?",
         "Sustaining capex per BOE, free-cash-flow break-even WTI, net debt over cash flow at strip, ten-year per-share production CAGR, insider open-market buys in the last four quarters, 2015 and 2020 dividend behaviour, and ten-year reserve replacement at flat prices."),
        ("Why is sustaining capex per BOE the first number?",
         "Because it tells you whether the business is real. A first-quartile Canadian operator pays under US$15 per barrel to keep production flat. The structurally disadvantaged sit at US$25-plus and have to issue equity in every downturn."),
        ("What does the 2015 and 2020 dividend record tell you?",
         "It is the cleanest single record of how the operator's capital culture performs under pressure. Operators that held the dividend in both stress windows include CNQ, ENB, TOU, and FTS. Most of the rest cut, issued equity at distressed prices, or both."),
    ],
    "cost-curve-is-a-lie-if-you-pick-the-quartile": [
        ("Why are first-quartile cost-curve claims often misleading?",
         "Every operator claims first-quartile. The denominator decides. The honest read starts with three questions: what is the denominator, who else is on the curve, and what was excluded from the unit cost. If the operator demurs on any of the three, the slide is decoration."),
        ("Which mining sector has the cleanest cost-curve disclosure?",
         "Uranium. The producer cohort is small enough to stack, the reported per-pound cash costs are reported on broadly comparable metrics, and operators have had to behave as if the curve were honest because the cycle has been so punishing."),
        ("Which sectors have the worst cost-curve disclosure?",
         "Silver and copper. Silver because of by-product credit gymnastics and the small pure-play universe. Copper because by-product gold credits at large operations like Grasberg can depress headline cash costs into negative territory if reported aggressively."),
    ],
    "what-2015-and-2020-told-us-canadian-energy": [
        ("What did 2015 and 2020 reveal about Canadian energy operators?",
         "The cohort sorts into four buckets: operators who held the dividend in both stress windows (CNQ, ENB, TOU, FTS); operators who held in one and cut in the other (Suncor); operators who cut in both; and operators that did not survive in their pre-2014 form. The record is public and the same management teams are largely still in place."),
        ("Why does Halvren read past stress windows so carefully?",
         "Capital culture is sticky. The CEO who cut the dividend at the bottom of 2020 is in many cases the CEO underwriting the 2026 capital plan. The 2015 and 2020 records are the cleanest single piece of evidence on how a management team behaves when its discipline is actually tested."),
        ("Which Canadian operator delivered the cleanest 2020 response?",
         "Canadian Natural Resources. CNQ raised the dividend in March 2020 — the same week the WTI front-month went briefly negative — held the buyback through the trough, and issued no equity at distressed prices."),
    ],
    "pipelines-are-turnpikes-not-commodity-bets": [
        ("Are Canadian pipeline equities a bet on the commodity price?",
         "No. The most important number on any pipeline operator is the percentage of EBITDA that comes from take-or-pay, cost-of-service, fee-based, or regulated rate-base contracts. Enbridge runs about 98% contracted; TC Energy is over 90%; Kinder Morgan is over 90%. The operating earnings are not commodity-price exposed in the way E&P is."),
        ("How does Halvren underwrite a pipeline operator's growth?",
         "Through two numbers: the targeted annual rate-base CAGR (typically 4–7% across the cohort) and the authorized return on equity (typically 8.5–10.5%). Multiplied, they produce the structural earnings growth that supports the dividend without expanding the payout ratio."),
        ("Where does the cycle still matter for pipeline equities?",
         "In the share price, not the EBITDA. Pipeline equities trade in correlation with the energy complex on a multi-quarter basis even when the contracted EBITDA is unchanged. Patient capital uses the correlation; it does not need to explain it away."),
    ],
    "uranium-operator-checklist": [
        ("How does Halvren separate uranium producers from developers?",
         "The first question is whether the operator produced more than two million pounds of U₃O₈ in the most recent year. If yes, it is a producer. If no, it is a developer — and the framework for developers is different (resource quality, permitting, equity-issuance velocity, milestone-based compensation)."),
        ("Why is Cameco's McArthur River shutdown the cleanest uranium capital decision?",
         "The mine was placed on care and maintenance from 2018 through 2022, when the spot price did not support producing into the market. Most high-cost producers kept producing through the bear market, destroying value on every pound. Cameco did not, and the restart in 2022 came at meaningfully better per-pound economics than the pre-shutdown vintage."),
        ("What stress test does the framework apply to uranium operators?",
         "A 40% spot drawdown. At the operator's current cost structure, contract book, and balance sheet, does the business still print free cash? Cameco passes; the marginal producers do not."),
    ],
    "silver-per-share-problem": [
        ("Why doesn't silver production growth equal shareholder value?",
         "The senior silver cohort has grown share counts by 60–200% over a decade through equity-funded acquisitions. Even where absolute ounces grew, per-share production has shrunk for most operators. The cohort median pattern is headline growth on top of meaningful per-share decline."),
        ("Why does the silver-producer problem persist?",
         "Compensation. Senior silver compensation plans, almost without exception, are weighted toward absolute production and reserve targets. The incentive is aligned with absolute growth, not per-share growth, and the cumulative result is the cohort's per-share decline."),
        ("What is the streamer alternative?",
         "Precious-metals streamers (Wheaton, Franco-Nevada, Royal Gold) buy contracted percentages of future production paid for upfront. The model is structurally per-share-accretive because the financing currency is the contract rather than the streamer's equity. Per-share total returns over a decade have meaningfully exceeded the senior silver producer cohort."),
    ],
    "dividend-that-survived-cnq": [
        ("Why does CNQ's twenty-six-year dividend record matter?",
         "It is a capital-allocation document, not a dividend story. The dividend was raised in every year of the last three macro stress windows: 2008–2009, 2015–2016, and 2020. The 2020 raise was announced the same week the WTI front-month went briefly negative."),
        ("What capital culture produced the record?",
         "Murray Edwards's. He has been on the board for thirty years and a meaningful shareholder throughout. The asset mix (long-life, low-decline), the cost discipline (low US$10s per barrel sustaining), and the capital allocation behaviour (no equity at distressed prices, modest buyback at the trough) together produced the dividend."),
        ("What is the open Pillar II question on CNQ?",
         "Cultural transmission past the Edwards era. Tim McKay's promotion to CEO in 2020 was continuity from the operational side. The harder question is what survives at the board level and in the compensation plan over the next decade. The 2026 base case is continuity; the tail is the question."),
    ],
    "insider-buying-vs-granting": [
        ("What's the difference between insider buying and insider granting?",
         "Granted equity (options, RSUs, restricted stock) is part of the compensation plan, negotiated at the proxy, with no out-of-pocket capital from the executive. Open-market purchases are real money — the executive could have spent it on anything else. The signal that costs the operator something is the only signal worth reading."),
        ("Who has the cleanest insider-buying record on the Halvren desk?",
         "Rich Kinder at Kinder Morgan. He has bought open-market consistently for two decades, including through the 2015 dividend cut and balance-sheet repair. The cumulative dollar value of his open-market purchases is the largest single insider position in U.S. midstream."),
        ("How does Halvren read the absence of insider buying?",
         "An absence during a meaningful share-price drawdown is informative. A new CEO who does not buy at any price in the first eight quarters is making an implicit signal. A founder who goes quiet for two consecutive years through weakness is communicating something. Sometimes the explanation is benign; often it is not."),
    ],
    "roic-incremental-capital-plain-english": [
        ("What is the difference between reported ROIC and marginal ROIC?",
         "Reported ROIC is the historical average across the whole capital base. Marginal ROIC is what the next dollar of capital earns. Most operators report the first and avoid the second. The second is the decision input that matters."),
        ("Why is the buyback often the cleanest marginal-ROIC test?",
         "A buyback earns the inverse of the price-to-earnings multiple at the moment of execution. At a 10x multiple, the buyback earns 10% pre-tax — typically competitive with brownfield capex and superior to most greenfield. An operator that buys back consistently at trough prices and pauses at peak prices is doing the math right."),
        ("Why won't most operators publish marginal-ROIC guidance?",
         "Because the disclosure invites accountability. A disclosed 12% marginal ROIC obliges the operator to explain every year the disclosed return falls below it. Most operators prefer a range of capital-allocation guidance with no point estimate; the range is harder to be wrong about."),
    ],
    "boring-thirty-year-chart-canadian-infrastructure": [
        ("What is the case for Canadian infrastructure as a compounder?",
         "A 6% earnings compounder plus a 4% dividend yield is a 10% total return at constant valuation. Compounded for thirty years that is 17.4x. The math is dull; the chart is dull; the aggregate is the point. Fortis has raised the dividend for fifty-two consecutive years."),
        ("Why is the Canadian infrastructure cohort so small?",
         "Three filters: asset durability (the underlying technology must survive thirty years), regulatory durability (the jurisdiction must grant a fair return through cycles), and capital culture (the operator must not erode the rate-base advantage through bad allocation). Across the listed universe, roughly half a dozen names pass all three."),
        ("Where can the case for Canadian infrastructure compounding break?",
         "Regulatory error, capital indiscipline (TC Energy's Coastal GasLink overspend is the recent reference), and stranded-asset risk on a long-cycle demand decline. The probability of the worst case is low; the probability of meaningful demand erosion over thirty years is non-trivial."),
    ],
}


# ---------------------------------------------------------------------------
# helpers
# ---------------------------------------------------------------------------

def faq_jsonld(pairs: list[tuple[str, str]]) -> str:
    payload = {
        "@context": "https://schema.org",
        "@type": "FAQPage",
        "mainEntity": [
            {
                "@type": "Question",
                "name": q,
                "acceptedAnswer": {"@type": "Answer", "text": a},
            }
            for q, a in pairs
        ],
    }
    return json.dumps(payload, ensure_ascii=False, separators=(",", ":"))


MARK_START = "<!-- FAQ_JSONLD:sprint7:start -->"
MARK_END   = "<!-- FAQ_JSONLD:sprint7:end -->"


def inject(html: str, payload: str) -> str:
    block = (
        MARK_START
        + '\n<script type="application/ld+json">\n'
        + payload
        + "\n</script>\n"
        + MARK_END
    )
    # idempotent: replace existing block if present
    if MARK_START in html and MARK_END in html:
        return re.sub(
            re.escape(MARK_START) + r".*?" + re.escape(MARK_END),
            block,
            html,
            flags=re.DOTALL,
        )
    # else insert right before </head>
    return html.replace("</head>", block + "\n</head>", 1)


def patch_about() -> None:
    p = ROOT / "about.html"
    s = p.read_text(encoding="utf-8")
    s2 = inject(s, faq_jsonld(ABOUT_FAQ))
    p.write_text(s2, encoding="utf-8")
    print(f"  patched about.html (5 Q&A)")


def patch_notes() -> None:
    for slug, pairs in NOTES_FAQ.items():
        p = ROOT / "notes" / f"{slug}.html"
        if not p.exists():
            print(f"  SKIP {slug}: file not found")
            continue
        s = p.read_text(encoding="utf-8")
        s2 = inject(s, faq_jsonld(pairs))
        p.write_text(s2, encoding="utf-8")
        print(f"  patched notes/{slug}.html ({len(pairs)} Q&A)")


def main() -> int:
    patch_about()
    patch_notes()
    print("inject_faq_jsonld: done.")
    return 0


if __name__ == "__main__":
    sys.exit(main())

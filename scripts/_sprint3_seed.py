#!/usr/bin/env python3
"""
_sprint3_seed.py

Sprint 3 seed: emits the 10 Halvren Notes as .mdx files into
/content/notes/. Each note carries YAML-ish frontmatter and a Markdown
body authored against /docs/HALVREN_BRAND.md.

The dates are staggered across the eight weeks 2026-03-21 → 2026-05-14
so the /notes index reads like a back issue, not a same-day dump.

Run from the repo root:
  python3 scripts/_sprint3_seed.py
"""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DST = ROOT / "content" / "notes"


NOTES: list[dict] = []


# === 1 ====================================================================== #
NOTES.append({
    "title": "How to read a Canadian oil & gas operator in seven numbers",
    "slug": "how-to-read-canadian-oil-gas-operator-seven-numbers",
    "date": "2026-05-14",
    "meta_description": "Seven metrics in order: sustaining capex per barrel, free-cash break-even, net debt at strip, per-share growth, insider buys, prior-cycle dividends, replacement.",
    "excerpt": "Seven numbers, in order. Sustaining capex per barrel, free-cash break-even, net debt at strip, per-share production, insider open-market buys, 2015 and 2020 dividend behaviour, ten-year reserve replacement at flat prices. Everything else is decoration.",
    "reading_time": 11,
    "tags": ["Energy", "Capital allocation", "Operator quality", "Canada"],
    "related": [
        "what-2015-and-2020-told-us-canadian-energy",
        "roic-incremental-capital-plain-english",
    ],
    "operators": ["canadian-natural-cnq", "tourmaline-tou", "arc-resources-arx"],
    "body": """\
Most sell-side decks open with three things: a logo, a price target, and a chart of production growth. None of those tells you whether the business is good. A Canadian oil and gas operator is read in seven numbers, and the order matters more than the magnitudes. We go through them the same way every quarter, on every name in the coverage universe.

The order is deliberate. If a name fails on numbers one through three, we do not bother with the rest. If a name passes on those and stalls on four through seven, the read is "interesting, not yet." If a name passes on all seven, we have already spent four years reading it, and we already own it.

## 1. Sustaining capex per barrel of oil equivalent

This is the number that tells you whether the business is real. Take the operator's average annual sustaining capital expenditure across a five-year window. Divide it by the operator's average annual production in BOE. The result is the dollar cost, per barrel, of keeping production flat — before any growth capex, before any debt service, before any return to shareholders.

A first-quartile Canadian operator pays under US$15 per barrel of sustaining. The cohort average sits in the high teens. The structurally disadvantaged operators sit at US$25 or higher; those are the ones who quietly issue equity in every downturn because the business cannot fund its own depletion.

The number matters in two directions. Low sustaining capex is the structural advantage every other number on this list builds on. And a sudden _rise_ in sustaining capex, particularly one that does not show up in management's commentary, is the leading indicator of an operator that is moving up the cost curve as the best acreage gets depleted. Read [Canadian Natural (CNQ)](/research/canadian-natural-cnq) for the upper-end of the Canadian sustaining-capex discipline; the low-decline, long-life asset mix is the structural reason the number stays low.

## 2. Free cash flow break-even WTI

This is the number that tells you whether the business survives the next trough. Calculate the WTI price at which the operator generates exactly zero free cash flow after sustaining capex, after the base dividend, and after maintenance interest. The lower the number, the more cushion the operator has when the price tape turns.

Most Canadian operators print a break-even between US$40 and US$55 WTI at current strip differentials. The first-quartile names sit in the high US$30s. The marginal names sit at US$60 or higher; the marginal names with high decline rates sit at US$70 or higher. The arithmetic is unforgiving. An operator with a US$65 break-even and a US$58 average WTI does not "wait it out." It issues equity, cuts the dividend, or both.

We track the break-even at flat differentials each quarter for every operator on the desk. The number that moves slowly is the structural read; the number that moves a lot quarter-to-quarter is telling you about apportionment, transport, or hedging changes, none of which are the business.

## 3. Net debt over cash flow at strip

The third number tells you whether the operator can take a punch. We compute net debt divided by trailing-twelve-month operating cash flow at the current strip price for WTI and AECO. Anything under 1.0× is conservative; the 1.0–2.0× range is normal for a Canadian E&P with a credible discipline record; above 2.0× is a problem the next downturn will surface.

The two extremes matter for opposite reasons. A name like [Tourmaline (TOU)](/research/tourmaline-tou) operates at effectively zero net debt and a meaningful cash balance; that is a soft signal about Mike Rose's view of his own cycle. A name with 2.5× net debt to cash flow heading into a trough is a name whose dividend is going to test the patience of its shareholder base.

> Capital allocation under stress is the only honest test. The 2015 and 2020 records of every operator on the desk are public; the 2026 forward decisions are not.

## 4. Per-share production growth, ten-year compounded

The fourth number separates operators from speculators. We take per-share production in 2015 and 2025 and compute the compounded annual growth rate. Absolute production growth is easy; issue shares, buy assets, watch the headline rise. Per-share production growth is the part the operator earns by keeping the share count disciplined.

A first-quartile Canadian operator delivers 3–5% per-share production CAGR over a decade with no share-count growth. The cohort average is closer to 1–2%. The marginal names print zero or negative per-share growth despite issuing equity every other downturn; those are the operators whose investor decks always feature the absolute number and never the per-share one. [ARC Resources (ARX)](/research/arc-resources-arx) is one of the cleaner per-share growth examples among the gas-weighted Montney operators since the 2021 Seven Generations merger.

## 5. Insider open-market buys, last four quarters

The fifth number is the only one that costs the operator something to fake, which is why we read it last among the operator-facing metrics. Options grants are loyalty to a quarter; RSUs vest on schedule; restricted stock prints on the proxy. Open-market purchases by named executives with their own money are loyalty to a decade.

We track the absolute dollar value of insider buys, the number of distinct buyers, and the share-price level at which each buy was executed. A consistent four-quarter buy record from multiple executives at multiple share-price levels is a signal we trust. A single CEO buying a small lot near the prior peak and selling on the way up is a different signal. Both are public.

## 6. The 2015 and 2020 dividend behaviour

The sixth number is a backward look. Most operators on the desk have lived through two near-existential commodity stress tests in the last decade: 2015–2016 and 2020. The dividend behaviour in each is the cleanest single record of how the operator's capital culture performs under pressure. We compile the table for every name.

The cohort splits roughly into four buckets. Operators who held the dividend in both stress windows: CNQ, ENB, TOU, FTS. Operators who held in one and cut in the other: SU (cut 2020, held 2015), several Canadian midstream names. Operators who cut in both: most of the Canadian heavy-oil pure-plays. Operators who had no dividend to cut because they were too distressed to pay one: a long list of names that are no longer on the desk.

The 2015 cohort is informative. The 2020 cohort is informative. The operators who passed both are the ones whose 2026 decisions we trust without re-doing the work.

## 7. Ten-year reserve replacement at flat prices

The seventh number is the one most operators do not want to print. Reserve replacement at <em>flat</em> prices means the operator's drilling and step-out activity produces enough new proved reserves to offset depletion without the help of a rising commodity price. A 100% replacement at flat prices means the business is, in the long run, durable. Below 100% means the operator is in a slow drawdown of the asset base.

The trick the industry uses is reserve replacement at strip prices — a generous price deck makes uneconomic reserves "economic" and inflates the number. The flat-price replacement is the honest one. Most disclosed Canadian operators report it; the ones that do not should be asked why.

## What you do not need to read

We do not weight headline production growth as a Pillar I metric. We do not weight EBITDA multiple expansion as a Pillar III metric. We do not read management's price-deck slide, ever. We do not read the analyst-day strategic-priorities deck; we read the proxy compensation plan instead, because the proxy is the part the operator has signed.

Most of what gets written about Canadian energy is decoration on top of these seven numbers. If the seven are good, the writeup is interesting. If they are not, the writeup is a story.

## What the seven numbers do not see

The framework has limits. Three of them are worth naming, in case the reader mistakes the seven for a complete picture.

The first limit is jurisdictional and political. A Canadian heavy-oil operator with a clean read on all seven numbers still owns assets that sit downstream of two specific political variables: the Canadian federal carbon and emissions framework, and the US administration's posture on Keystone-class pipeline approvals. The seven numbers will tell you the operator's break-even at flat differentials; they will not tell you how the differentials themselves move under a regulatory regime change. The 2018–2019 widening of WCS-WTI to over US$50 was a regulatory and pipeline-capacity event, not an operator event. The clean operators came through it; the operators with thin sustaining-cost margins did not.

The second limit is reservoir quality at the per-asset level. Sustaining capex per BOE is an aggregate number across the operator's full asset base. A name with a healthy aggregate sustaining number can be drilling its best acreage today and its second-tier acreage in three years, with a sustaining number that drifts higher even though the operator's framework appears unchanged. We track the per-asset disclosure where it exists; many operators provide enough field-level data to read it. The exceptions, where field-level data is sparse, are themselves a soft Pillar I signal.

The third limit is technology. A meaningful unit-cost reduction from a new completion technique, a new water-handling design, or a new well-pad layout can change the break-even by US$5–10 per barrel within a two-year window. The 2018–2024 step-change in Montney well productivity was the cleanest recent example; the operators positioned in the right acreage compounded a per-share advantage that the prior seven-number read did not anticipate. The framework is a structural read, not a forecast.

These limits do not invalidate the framework. They are the reason we do not run the seven numbers in isolation. Each operator's Halvren Checklist scorecard sits alongside the seven; the checklist captures the cyclical and people questions that the numbers cannot.

## What the framework does well

Where the framework earns its keep is the rejection step. Most of the work of any research desk is sorting names into "worth reading carefully" and "not worth the next hour." The seven numbers, applied in order, produce a clean reject decision in under fifteen minutes per name. An operator with sustaining capex of US$25 per BOE and net debt of three times cash flow does not need a sixty-page diligence pack to be classified; the seven numbers have already told the reader what they need to know.

The accept decisions take longer. An operator who passes the first three numbers cleanly is worth the rest of the framework, and the rest of the framework typically takes weeks of reading. The 2015 and 2020 records are public, but the texture of the decisions inside those windows is in the operator's letters, the proxy filings, the conference-call transcripts, and the principal interviews from the period. The seven numbers tell you whether to do the work. The work itself is still the work.

The seven numbers are not novel. They are not proprietary. They are the same seven numbers a careful operator would use to read its own business. The reason we publish them is that the sell-side framework keeps treating production growth as the operating metric and the dividend as the capital metric, when both are downstream of these seven. Read the seven first. The rest follows.
""",
})


# === 2 ====================================================================== #
NOTES.append({
    "title": "The cost curve is a lie if you let them pick the quartile",
    "slug": "cost-curve-is-a-lie-if-you-pick-the-quartile",
    "date": "2026-05-08",
    "meta_description": "Every operator claims first-quartile. The denominator decides. Three questions to test the claim, with examples from gold, silver, uranium, and copper.",
    "excerpt": "Every operator claims first-quartile. The denominator is the game. We walk through how to test the claim with examples from gold, silver, uranium, and copper — and why one of those four sectors has it cleanest.",
    "reading_time": 10,
    "tags": ["Cost curve", "Materials", "Operator quality", "Cross-sector"],
    "related": [
        "uranium-operator-checklist",
        "silver-per-share-problem",
    ],
    "operators": ["cameco-cco", "first-majestic-ag", "agnico-eagle-aem"],
    "body": """\
Open any senior mining presentation and you will find a cost-curve slide. The operator's mines sit comfortably in the first quartile. The competitors' mines sit further to the right. The conclusion is foregone. The slide has done its job before the reader has noticed which curve they are looking at.

Every operator is first-quartile when they pick the quartile. The denominator is the game.

The honest read of a cost curve starts with three questions, asked in this order. What is the denominator? Who else is on the curve? What was excluded? If the operator's answers are ambiguous or unflattering, the slide is decoration. If the answers are clean, the slide is real.

## 1. What is the denominator?

A "global cost curve" is rarely global. The most common manipulation is to define the curve as a subset of the global production base — the operator's region, the operator's primary asset type, or the operator's commodity within a co-product split — and then claim first-quartile relative to the subset.

A Canadian gold operator that draws its cost curve against the Canadian Tier-1 producer cohort is not lying. It is also not telling you where it sits on the global cost curve, which includes meaningful production from West Africa, Latin America, Central Asia, and Australia at AISC numbers that are often materially lower than the Canadian average. [Agnico Eagle (AEM)](/research/agnico-eagle-aem) does not need to use this trick — its AISC is competitive on a global basis — but most of the senior gold cohort does, and the slide reflects it.

The clean denominator question is: "show me your AISC against the largest 50 producers globally on a single chart." If the operator demurs, the answer is the answer.

## 2. Who else is on the curve?

The second manipulation is to exclude producers who would embarrass the comparison. The exclusion can be on jurisdiction (Russian potash, for instance, is often left out of "Western potash cost curve" charts). It can be on asset stage (mines in commissioning are not "operating"). It can be on operator size (only senior producers are graphed, even though the marginal producer is a junior).

Each exclusion is defensible on its own terms. Combined, they let the operator construct any curve they want. The principal-led read of a cost-curve slide always asks: who is _not_ on this curve, and why? If the operator's answer is "because the data is unreliable," the next question is who the operator thinks is below them on the data the operator does have.

## 3. What was excluded from the unit cost?

The third manipulation is in the y-axis itself. "Cash cost" excludes sustaining capex; "AISC" is meant to include it but operators interpret the boundary differently; "all-in cost" sometimes includes growth capex and sometimes does not. Net by-product credits inflate or deflate the headline number meaningfully.

Silver producers are particularly creative here. A polymetallic silver-gold-lead-zinc mine reports its silver cash cost net of by-product credits, which can produce headline numbers in the low US$10s per ounce while the underlying mine economics are not that strong. [First Majestic (AG)](/research/first-majestic-ag) is a Mexico-anchored silver producer whose AISC is among the higher in the senior silver cohort; the deck does not always say so directly.

The honest cost-curve slide names the per-ounce or per-pound metric explicitly, separates by-product credits as a line, and discloses sustaining capex assumptions. If the slide does not do all three, the curve is decoration.

> Every operator is first-quartile when they pick the quartile. Ask who sets the denominator.

## The sector that does it cleanest

The one mining sector that has historically produced the cleanest cost-curve disclosure is uranium. The reason is structural: there are roughly a dozen producers globally, the largest five account for the vast majority of output, and the publicly disclosed AISC numbers from each — Kazatomprom, [Cameco (CCO)](/research/cameco-cco), Orano, CGN, Energy Fuels, Paladin, Boss Energy, Denison — are reported on broadly comparable metrics. A reader can stack them.

When Cameco claims its Saskatchewan mines sit first-quartile, the claim is verifiable. McArthur River and Cigar Lake have among the highest ore grades ever developed; per-pound cash costs are structurally lower than the in-situ Kazakh operations or the secondary-supply tail in Africa and Australia. The claim has been tested through the post-Fukushima collapse, when Cameco mothballed McArthur and continued to produce; the lower-grade mines that did not mothball destroyed value on every pound. The cost curve in uranium has been honest because the operators have had to behave as if it were honest.

## The sectors that do it worst

Silver and copper sit at the opposite end. Silver because of the by-product credit problem and because most silver production is incidental to gold, lead-zinc, and copper mining; "pure-play silver cost curves" are constructed by selecting only the mines that report silver as the primary metal, which is a small and unrepresentative sample. The honest silver curve includes by-product silver, which is much cheaper, and the senior pure-play silver producers do not want to be on that chart.

Copper because by-product gold credits at the largest operations such as Grasberg ([Freeport](/research/freeport-mcmoran-fcx)) and OT depress headline cash costs into negative territory if reported aggressively. The unit economics are real and good; the comparison to a Cerro Verde or a Las Bambas operating on copper-alone economics is not symmetric.

## How we test the claim

The Halvren test on any cost-curve slide is mechanical. We pull the operator's reported AISC, sustaining capex, and by-product credit assumptions from the latest annual filing. We compare to a benchmark we maintain across the named cohort on consistent definitions. The benchmark is not novel; the sell-side analysts at the larger broker-dealers maintain something similar. What is novel is the reading.

If the operator's reported AISC is within 5% of our benchmark and the denominator passes the three questions above, the cost-curve claim is real and we proceed to the operator-quality questions. If the operator's reported AISC is meaningfully below the benchmark, we ask why, and the answer is usually a definitional difference rather than an operational one. If the operator refuses to disclose the by-product credit boundary or the sustaining-capex boundary, we move on. There are 30 operators on the desk; we do not need to chase 31.

## How to use the read in practice

The framework is operational, not theoretical. The questions get asked in a specific order, and the operator's answers (or refusals) sort the cohort with surprising speed.

The first practical use is on the investor-relations call. A reader who wants a fast read of an unfamiliar mining operator can ask three questions on the next IR call and have a clean answer within five minutes: (a) which mines in the global cost-curve top fifty are below you, named? (b) what is the by-product credit assumption in your reported AISC, and what does AISC look like without the credit? (c) what does your sustaining capex per produced ounce or pound look like compared to the median of the disclosed cohort? An IR team that can answer all three smoothly is at a structurally different operator from one that demurs on each.

The second use is on the deck slide itself. A cost-curve chart with no labeled producers, no jurisdiction breakdown, and no by-product disclosure is a decorative slide. A chart with named producers across the curve, jurisdictional buckets, and explicit boundary assumptions is the slide an operator confident in its position would draw. We screenshot the slide and the assumptions; we then compare to the cohort's average disclosure two years later. Slides drift; the drift is informative.

The third use is on the historical record. A senior operator's claim to first-quartile cost position should be testable across the last decade, not just the current year. We pull the operator's AISC by year for the prior ten years and compare to the cohort's prior-decade history. An operator that has consistently sat in the first quartile through three different commodity cycles is making a structural claim. An operator that has moved into the first quartile only in the most recent two years is making a story claim. The two cases get priced differently.

The compound result of these three practical uses is that, across the global gold, silver, copper, and uranium cohorts, the number of operators whose first-quartile claims pass all three tests is meaningfully smaller than the number of operators making the claim. The narrow set is the one we work on. The broader set is the one the conference panels talk about. We do not have to pick.

## The slide is not the problem

A cost-curve slide is a useful artifact. The slide is not the problem. The problem is the reader who takes the slide at face value because the picture is suggestive and the conclusion is unambiguous. The mine has not moved on the cost curve since the slide was drafted. The marginal producer's economics have not improved or worsened in the time it took to print the deck. What has happened, every quarter, is that someone has chosen a denominator and called it the curve.

The compounded result, across our coverage list, is that the first-quartile claim is verifiable on roughly a quarter of the senior mining names we have read in detail. The other three-quarters of the cohort claim first-quartile on definitions that fall apart on the first follow-up question. That is not a fraud read; it is a discipline read. The operator who has read the questions above and answered them honestly is the operator we want to spend time with. The operator who has not is the operator whose cost-curve slide is decoration on a slide deck. The decoration is fine; the slide is fine; the reader who confuses them with the underlying business is the part of the system the framework is meant to protect against. A research desk that earns its keep is the part of the protection that does the reading work for the careful capital allocator who does not have time to read every deck themselves.

The operators worth owning are the ones who can show their work. The operators worth avoiding are the ones who cannot. The slide is the same slide either way; the answer to the question behind it is the only thing the careful investor is buying.
""",
})


# === 3 ====================================================================== #
NOTES.append({
    "title": "What 2015 and 2020 told us about every Canadian energy operator still standing",
    "slug": "what-2015-and-2020-told-us-canadian-energy",
    "date": "2026-04-30",
    "meta_description": "Two stress tests sorted Canadian energy operators into four buckets. The 2015 and 2020 records are public. The cohort splits the same way in 2026.",
    "excerpt": "Two stress tests in a decade. Every Canadian energy operator's capital decisions in 2015 and 2020 are public. Some held the dividend in both; some issued equity at distressed prices; some did not exist by the end of either. The record reads cleanly if you put it on one page.",
    "reading_time": 11,
    "tags": ["Energy", "Capital allocation", "Crisis behaviour", "Canada"],
    "related": [
        "dividend-that-survived-cnq",
        "pipelines-are-turnpikes-not-commodity-bets",
    ],
    "operators": ["canadian-natural-cnq", "enbridge-enb", "suncor-su"],
    "body": """\
Two stress tests in the last decade. Late 2014 through early 2016 ground WTI from US$100 to the high US$20s and left every Canadian operator with a US$60-plus break-even underwater for the better part of a year. The spring of 2020 did it again, faster, with WTI briefly trading at a negative front-month settle. The cohort behaviour in each window is on the public record. The records are not flattering, and they are not a secret.

We compiled the table for every operator on the Halvren coverage list. The findings are not surprising. They are the cleanest single piece of evidence about which capital cultures hold under pressure and which capital cultures perform their discipline in the deck but not in the boardroom.

## The four buckets

A Canadian energy operator's behaviour in 2015 and 2020 sorts cleanly into four buckets.

**Bucket one: held the dividend in both, no equity issued.** A small cohort. [Canadian Natural (CNQ)](/research/canadian-natural-cnq) is the cleanest single example. The dividend was raised in 2015 and again in 2020. No common equity was issued. Capital expenditure was cut hard and selectively. The 2020 free cash flow at the low oil tape was still positive on a maintenance basis because the sustaining capex sat in the low US$10s per barrel. [Enbridge (ENB)](/research/enbridge-enb) shares this bucket from the infrastructure side: the dividend was raised in both years, no equity issued, no covenant pressure.

**Bucket two: held the dividend in one window and cut in the other.** A larger cohort and a more interesting one. [Suncor (SU)](/research/suncor-su) held in 2015 and cut the dividend by 55% in 2020. The 2015 hold was real discipline; the 2020 cut was rational. The interesting question is why Suncor performed well in one window and badly in the next, and the answer was operational: by 2020 the cost discipline that defined the 2015 response had been eroded by Fort Hills underperformance and turnaround misses, and the dividend was no longer covered at the trough oil price the way it had been five years earlier.

**Bucket three: cut the dividend in both windows, or to a token in one of them.** Cenovus pre-Husky (a different company, in effect); MEG Energy in both windows; several smaller Canadian heavy-oil pure-plays. The 2015 cuts were the leading indicator of the 2018–2019 distress that followed. The 2020 cuts in many cases were accompanied by equity issuance at meaningfully below the prior peak — what we call the second-derivative cost of an unprepared balance sheet.

**Bucket four: did not survive the window in their pre-2014 form.** This is the longest bucket. A large number of Canadian E&Ps were acquired, restructured, or went into formal proceedings between 2015 and 2018. The post-2020 wave was smaller because the survivors of the 2015 stress had broadly reduced debt, but the wave existed.

## What the four buckets actually tell you

The four-bucket sort is not a credit-rating exercise. The record matters because the same managers, broadly, are still running the same businesses. The CEO who cut the dividend at the bottom of 2020 is, in many cases, the CEO underwriting the 2026 capital plan. The capital culture is sticky.

> The dividend held through 2015 is a signal. The dividend held through 2020 is a signal. The dividend held through both is a different signal, and the operators who delivered it have been a small set for ten consecutive years.

CNQ's record in 2020 is the cleanest. The dividend was raised in March 2020 — a six per cent bump announced the same week the WTI front month went negative. The signal was deliberate. Murray Edwards had spent a decade building a balance sheet and a sustaining cost structure that did not require a US$60 oil tape to fund the dividend. The 2020 announcement was the receipt.

Tourmaline's record in both windows is similarly clean: the base dividend held, special dividends were paid when warranted, no equity was issued at distressed prices. The model is different — owner-operator, gas-weighted, lower absolute production scale — but the discipline reads the same.

Suncor's 2015–2020 trajectory is the more cautionary tale. The 2015 hold was a discipline call earned by the integrated downstream cushion and the cost structure at Base Mine and Firebag. By 2020, both had eroded. The Fort Hills acquisition (closed 2018) had not produced the unit economics the deal deck had assumed. Repeated turnaround misses at the upgrader had pushed unit operating costs up. The dividend that had been comfortably covered in 2015 was not in 2020. The cut was rational; the conditions that forced the cut were the result of five years of incremental erosion that no single quarter would have flagged.

## The 2020 equity issuance test

A subtler test inside the same dataset is whether the operator issued common equity at distressed prices. Issuing at the bottom is the second-derivative cost of poor capital culture. The first cost is the equity dilution itself. The second cost is the operator's signaling: equity issued at a 60% discount to the prior peak tells you what management thinks of the asset value at that point, and it is rarely the read you want.

The cohort that issued equity at meaningfully distressed levels in 2020 is roughly the same cohort that cut the dividend to a token: MEG, Cenovus pre-McKenzie, several smaller pure-plays. The Husky combination that became today's [Cenovus](/research/cenovus-cve) was completed in early 2021 partly using equity issued at prices well below the 2020 distress level; the McKenzie-era recovery has been the response.

The Halvren test is mechanical. We pull the operator's common-share count at year-end 2014, 2016, 2019, and 2021. The compounded share-count growth across that period, net of buybacks, is the operator's dilution record across two stress windows. The number is public. The number is not always what the deck implies.

## The recovery cohort, ten years on

The interesting subset is the recovery cohort: operators who failed one or both stress tests and have since rebuilt the balance sheet, the management team, and the capital culture. Cenovus post-Husky-integration. Suncor post-Kruger. MEG after the five-year debt walk. The Canadian midstream names who issued equity in 2020 and have since walked the balance sheet back to investment-grade. Each of these is a real recovery story; each is also a name whose pre-recovery record is still in the data.

The framework on the recovery cohort is harder than on the consistent operators. Two competing reads sit on top of each other. The first read is the operational evidence of the recovery: unit costs trending down, dividend reinitiated and growing, balance sheet at target. The second read is the historical cultural memory: the management team that produced the failure is, in some cases, still in the room, and the board that approved the over-borrowing is, in many cases, the same board. The recovery is real on the first read; the durability of the recovery is unknown on the second.

The honest investor approach to the recovery cohort is to weight the position smaller than a comparable consistent-operator name would warrant, and to allow more time for the cultural transmission to settle. A management team that has not been tested at the new discipline level cannot be assumed to hold it; a five-year clean record across one cycle is informative but not yet definitive. We hold smaller positions in recovery names and read them more often. The 2026 list of recovery names on the Halvren desk is a short one; the entries are explicit about the open Pillar II questions.

The compare is instructive. CNQ and ENB get full-confidence Pillar II reads on the desk because the 2015 and 2020 records are clean. Suncor and Cenovus get the recovery read because the failures are documented but the recoveries are visible. The third category — names whose recovery has not yet been clearly demonstrated — does not appear on the desk at all. Three categories; three different positions. The framework forces the distinction.

## What we read into 2026

The 2020 record is six years old. The 2015 record is eleven. Both are still informative because the operators who passed both are the ones whose 2026 capital decisions we trust without re-doing the work. The operators who failed one or both have, in many cases, repaired their balance sheets and changed CEOs in the meantime. The repair is real; the cultural distance from the original failure is the question that the next cycle will answer.

Two new tests are likely in the next decade. A demand-side shock — accelerated electrification, a meaningful Canadian carbon pricing trajectory, an oil-sands regulatory tightening — would test the cohort on operating cost discipline rather than commodity-price endurance. A supply-side shock — an extended Iran or Russia disruption, a Permian productivity break — would test the cohort on the upside, which is a different question that the 2015 and 2020 record does not answer directly.

The record we have is the record we have. It is more useful than the price-deck commentary management will print at the next investor day. It is also more useful than the analyst-day strategy slides. We read it every year. The 2026 cohort splits the same way it did in 2020. That is the part most readers find uncomfortable, which is why we publish it.

The corollary is that any new operator entering the Canadian energy listed universe in the next decade enters without the test. A 2027 IPO of a new Canadian heavy-oil pure-play would, in our framework, be unreadable on the most important Pillar II question until the next cycle stress arrives. The new operator's management team may have served at a tested operator in 2015 and 2020, and the prior employer's records carry over to some degree, but the new entity has no record of its own. The framework's bias is to wait for the record. Most new entrants will not survive long enough to produce one; the ones that do will be readable after the next downturn, not before. The cohort is small for a reason; the framework is patient for the same reason; the patience is what the desk has to offer that the rest of the market does not. The 2015 and 2020 records are the receipt; the framework is the rule; the patience is the practice.

""",
})


# === 4 ====================================================================== #
NOTES.append({
    "title": "Pipelines are turnpikes, not commodity bets — reading Canadian infrastructure honestly",
    "slug": "pipelines-are-turnpikes-not-commodity-bets",
    "date": "2026-04-23",
    "meta_description": "Canadian and US pipeline operators earn from contracted rate base, not the commodity tape. The contracted share is the moat. Capital discipline is the rest.",
    "excerpt": "Owning Enbridge is not owning oil. Owning TC Energy is not owning gas. The contracted EBITDA share, the rate base, and the regulatory jurisdiction are the read. Commodity exposure on a Canadian pipeline operator is the thirty percent of the business the company would rather not discuss.",
    "reading_time": 10,
    "tags": ["Infrastructure", "Pipelines", "Capital allocation", "Canada"],
    "related": [
        "boring-thirty-year-chart-canadian-infrastructure",
        "dividend-that-survived-cnq",
    ],
    "operators": ["enbridge-enb", "tc-energy-trp", "kinder-morgan-kmi"],
    "body": """\
The most common analytical mistake on Canadian infrastructure is reading a pipeline operator as a commodity bet. The mistake is not always the analyst's. The pipeline operators themselves, in their annual deck commentary, often invite the framing — "natural gas is structurally favoured" or "oil sands volumes underpin our throughput" — because the framing flatters the rate-base story without committing to the more honest accounting.

A Canadian pipeline operator is a turnpike. The take-or-pay contract share is the asphalt. The rate-base growth is the toll. The commodity exposure, where it exists, is the part of the business the operator would rather not put on the cover slide.

## The contracted share is the moat

The most important single number on any Canadian or US pipeline operator is the percentage of EBITDA that comes from take-or-pay, cost-of-service, fee-based, or regulated rate-base contracts. The cohort numbers are public.

[Enbridge (ENB)](/research/enbridge-enb): approximately 98% of EBITDA is take-or-pay, cost-of-service, or fee-based. The Mainline, the US gas distribution utilities acquired from Dominion in 2023–2024, and the Aux Sable arrangements are structured. The remaining 2% is genuine commodity exposure, which Enbridge takes pains to bound.

[TC Energy (TRP)](/research/tc-energy-trp): more than 90% of post-spinout EBITDA is take-or-pay or cost-of-service. The October 2024 South Bow spinout removed the liquids exposure and the Pillar III commodity question that came with it. What is left is a gas pipeline and power business whose contractual structure is, in operational terms, a utility.

[Kinder Morgan (KMI)](/research/kinder-morgan-kmi): also north of 90% contracted, with the structural tailwind of US LNG-export feedgas demand. The 2015 dividend cut and balance-sheet repair was the painful Pillar II reset that brought the contracted business back into focus.

When the contracted share is at or above 90%, the rate-base discussion is the right discussion and the commodity-price discussion is decoration. When the contracted share is below 80%, the operator is part-pipeline and part-merchant, and the merchant half deserves to be priced separately.

## Rate-base growth is the toll

A regulated utility's earnings depend on the size of its rate base and the authorized return on that rate base. A pipeline operator with a meaningful regulated footprint — Enbridge's US gas distribution segment, TC Energy's NGTL, the bulk of Fortis's portfolio in adjacent infrastructure — earns from the same math.

The honest read of a pipeline operator's growth plan is in two numbers: the targeted annual rate-base CAGR (typically 4–7% across the named cohort) and the authorized ROE band (typically 8.5–10.5% in the Canadian and US jurisdictions that matter). Multiply them and you have the structural earnings growth rate of the regulated piece, which is roughly the dividend growth rate the operator can support without expanding the payout ratio.

The cohort numbers settle close to 5–7% earnings growth from regulated rate base alone. The dividend growth bands operators have committed to publicly — ENB at 3–5%, TRP at 3–5%, FTS at 4–6% — sit comfortably below the regulated earnings growth rate. That gap is the part of the model that should make a reader more comfortable, not less: the dividend is covered by a margin even before any new project is approved.

## What "demand-driven" actually means

A second category of contractual structure shows up in the disclosures more in the last decade: "demand-driven" or "market-pull" capacity. This is take-or-pay capacity contracted by a buyer who needs the molecules at the other end, regardless of the upstream commodity price. The clearest example is LNG-export feedgas. A producer might be unhappy at US$2 Henry Hub, but the LNG facility is unaffected; the pipeline that moves the gas to the facility is even less affected.

The Kinder Morgan footprint is the single largest US example. Multiple Gulf Coast LNG facilities draw on KMI pipelines as feedgas, and the contracts are structured so KMI is paid regardless of the Henry Hub print. The TC Energy network on the US Gulf shares similar exposure. Coastal GasLink at the Canadian end provides feedgas to LNG Canada, with the same contractual structure on the Canadian side.

Demand-driven capacity is a structural tailwind that, in our read, the senior pipeline operators have under-marketed. The reason is regulatory: aggressively framing the LNG-export tailwind invites political pushback in the Canadian context and rate-case pushback in the US context. The operators prefer to let the rate-base CAGR do the talking.

> A pipeline is a toll-road. The contracted share is the asphalt. The commodity exposure, where it exists, is the part the operator would rather not put on the cover slide.

## The thirty per cent that is a commodity bet

A small minority of Canadian and US pipeline operators carry meaningful direct commodity exposure. The Aux Sable propane operations at Pembina; certain Williams gas-processing arrangements; the Inter Pipeline polypropylene/propylene project (now Brookfield-owned); historically, parts of Kinder Morgan's CO2 business.

None of these are pipeline economics; all of them are merchant exposures dressed up in pipeline-adjacent accounting. The honest read separates them as a line item. The pipeline operator deserves a pipeline multiple on the contracted EBITDA and a different multiple on the merchant EBITDA. Most market reads collapse the two; the operator usually prefers it that way; the analytical mistake is allowing the collapse to persist.

## Where the cycle still matters

The contracted share insulates earnings, not the share price. Pipeline equities trade in correlation with the energy complex on a multi-quarter basis, and a meaningful WTI drawdown still moves the equity even when the EBITDA does not. The correlation is psychological, not mechanical. Patient capital uses the correlation; it does not need to explain it away.

The 2015 and 2020 records of the senior North American pipeline cohort are informative. Enbridge raised the dividend through both windows. TC Energy raised through both. Kinder Morgan cut in 2015 (the Pillar II reset event) and raised through 2020. Pembina held the dividend through both with no equity issued at distressed prices.

The 2026 read of the cohort is calmer than the post-2014 read. The contracted share is meaningfully higher across the board. Coastal GasLink and the South Bow spinout are behind us. The LNG-export feedgas tailwind is real. The Canadian regulatory environment is the open question, and we read it carefully every quarter, but the contractual structure is built to survive almost any politically reasonable outcome.

One more practical caveat is worth naming. The pipeline cohort's valuation has historically been sensitive to the long end of the government bond curve, not the front end. A meaningful rise in the ten-year Canadian or US government yield tends to compress pipeline multiples even when the underlying contracted EBITDA is unchanged. The mechanism is the implied discount rate on the long-duration cash flow stream. The 2022–2023 multiple compression in the cohort was almost entirely a function of the rate move; the underlying earnings were largely on plan. The reader who looks at the equity tape and concludes the business has weakened is reading a discount-rate move and miscoding it as an operating one. The two effects are separable, and the framework reads them separately.

## What we underwrite at

We underwrite Canadian pipeline operators at the regulated and contracted EBITDA growth rate plus the dividend yield, with a small equity-return haircut for execution risk on the capital program. The math sits in the high single digits to low teens of expected total return at a constant multiple. It is not the kind of return that requires a commodity-price thesis. It is the kind of return that compounds for thirty years if the operator does not get itself into trouble.

## The Canadian regulatory question

The single largest open variable on the Canadian pipeline cohort is regulatory, not commodity. The Canada Energy Regulator (formerly NEB) is the operating regulator for the major interprovincial lines; provincial commissions handle the local distribution franchises; the US FERC handles the southern half of the cross-border systems. The regulatory environment is, on the whole, mature and accommodating. The two open questions worth tracking are the framework for cumulative greenhouse-gas emissions tied to expansion approvals, and the political appetite for new mainline expansions in the post-Trans-Mountain era.

The first question is technical. The 2020s emissions framework attaches a per-tonne cost to incremental upstream emissions enabled by new mainline capacity. The economics of any new project are sensitive to how that cost gets allocated between the upstream producer (who pays the emissions cost) and the midstream operator (who builds the line). The current allocation has not been settled in a way that would survive a meaningful change in federal government, and the operators read the political tape carefully because their multi-year capital programs are downstream of it.

The second question is political. The Trans-Mountain expansion was completed in 2024 after a long and expensive regulatory process that ended with the federal government as the project's owner. No other mainline expansion of comparable scale has been proposed since. The operators' commentary has been deliberate: rate-base growth on existing right-of-way, expansion within existing footprints, and demand-driven projects (LNG export, US gas distribution rate-base) where the political constituency is more supportive. The era of greenfield mainline builds in Canada appears, in our read, to be over for the medium term. That is not a bad thing for the cohort's discipline; greenfield mainline builds have historically been the largest source of capital indiscipline in the sector.

The US side is more accommodating. Kinder Morgan and the US gas distribution segments of the Canadian operators face a different regulatory environment, with state PUCs and federal FERC operating on largely predictable terms. The LNG-export feedgas demand is meaningful and growing, and the US regulatory framework treats it as the structural tailwind it is. The Canadian operators with US footprints are positioned to participate in that tailwind without taking on the Canadian regulatory friction; the Enbridge Dominion utilities acquisition is the cleanest single example of the cohort's positioning toward the US side of the demand curve.

We read the regulatory tape on both sides every quarter. The questions matter for the multi-year capital program; they matter less for the current EBITDA, which is contracted under structures the regulators have already accepted.

## The valuation arithmetic

A practical complement to the framework is the valuation math the cohort trades at. The senior pipeline operators have, over the past decade, oscillated between roughly 10x and 14x forward EBITDA, with the band tightening in periods of regulatory comfort and widening in periods of stress. The dividend yield band has moved between roughly 4% and 7% over the same window, with the higher end of the yield range coinciding with the lower end of the multiple range.

Underwriting the cohort at the midpoint of the multiple band and the midpoint of the dividend yield produces an expected unlevered total return in the high single digits at constant valuation. That is the return the toll-road economics generate; the rest of the move in the equity price is multiple-related and tends to mean-revert over five- to seven-year windows. A patient investor who acquires the cohort near the upper end of the yield band has historically earned a meaningfully better return than the constant-valuation case because the multiple has expanded toward the middle of the band over subsequent years. The desk is conservative about timing; we acquire when the math works at a constant multiple and treat any multiple expansion as a bonus rather than the thesis.

The operators on the desk are the ones with the cleanest contractual structure, the most disciplined capital program, and the most settled regulatory posture. The list is short. It does not need to be longer.
""",
})


# === 5 ====================================================================== #
NOTES.append({
    "title": "The uranium operator's checklist: separating the mines from the narratives",
    "slug": "uranium-operator-checklist",
    "date": "2026-04-16",
    "meta_description": "Six questions separate uranium producers from developers and narratives from mines. Most uranium names fail the first four. The remaining list is short.",
    "excerpt": "Uranium has been a narrative commodity for two decades and an operator commodity for about three years. The checklist for reading a uranium business is shorter than the average pitch deck — six questions, four of which most uranium names fail.",
    "reading_time": 10,
    "tags": ["Energy", "Uranium", "Materials", "Operator quality"],
    "related": [
        "cost-curve-is-a-lie-if-you-pick-the-quartile",
        "insider-buying-vs-granting",
    ],
    "operators": ["cameco-cco", "canadian-natural-cnq"],
    "body": """\
Uranium has traded on narrative for almost two decades. The narrative is real — nuclear restart, AP1000 build, data-center power demand, post-Fukushima inventory exhaustion — but the narrative is not the business, and the operators worth owning are read on the mines, not the slides.

The Halvren uranium checklist is short. Six questions. Four of them eliminate most uranium names without controversy. The remaining two are where the work happens.

## 1. Does the operator produce, or is the operator a developer with a press release?

The single most important sorting question. Uranium developers have outnumbered producers for a decade. Many of them have spent more on investor relations than on drilling. The check is mechanical: in the most recent reporting year, did the operator produce more than two million pounds of U₃O₈? If yes, the operator is a producer. If no, the operator is a developer, and the framework for reading a developer is different (resource quality, permitting status, capital plan against the equity base, dilution velocity).

Most pieces written about "the uranium opportunity" are written about developers. Most uranium investors lose money on developers. Both facts are reconcilable.

## 2. What does the per-pound cash cost look like, audited, at the worst recent price?

For producers, the cash cost question is the structural read. We track the all-in mining cost — operator-reported, audited annually — and check it against the trough uranium price of the last decade (~US$22/lb in 2016–2017 for spot, with realized prices lagging meaningfully because of long-term contract floors).

[Cameco (CCO)](/research/cameco-cco) at McArthur River and Cigar Lake reports per-pound cash costs in the low US$20s, with sustaining capex layered on top. The McArthur River shutdown from 2018–2022 was the cleanest single capital-discipline decision in modern uranium history: the operator mothballed the world's highest-grade uranium mine rather than produce into a depressed price, then restarted it when contract prices supported the economics. The marginal Canadian and African producers that did not mothball destroyed value on every pound.

Kazatomprom's in-situ recovery in southern Kazakhstan reports the lowest disclosed per-pound cash costs in the cohort. The operator is the largest source of structurally cheap pounds. The honest reader has to engage with the Kazakh cost structure because the price-deck math runs through it; ignoring Kazatomprom because it is uncomfortable does not change the marginal-tonne dynamics.

## 3. What is the contract book, and what does the realized-price lag look like?

Uranium is sold predominantly under long-term contracts with three- to ten-year terms, market-reference pricing, floors, and ceilings. The reported selling price of any uranium operator trails the spot tape on the way up, and trails it on the way down. The lag is a feature, not a bug, if the operator's average contract terms are favourable.

Cameco's long-term contract book and average realized price are the single most important numbers in the quarterly release, in our read. A rising contract book at rising average prices is the clean signal that the business will earn meaningfully more over the next three to five years, regardless of what spot does next month. A flat contract book at falling average prices is the opposite read.

We track these numbers every quarter for the senior uranium producers that disclose them. Cameco, Kazatomprom, and Orano report enough detail to make the read possible. Most of the rest do not, which limits how confidently any of those names can be underwritten.

## 4. What happens to the operator if the spot price falls 40%?

The fourth check is a stress test. Uranium spot has fallen by 40% from a recent peak in three separate windows over the last fifteen years (post-Fukushima 2011, the 2014–2016 cycle, and a smaller 2018 reset). The check is: at the operator's current cost structure, contract book, and balance sheet, does a 40% spot drawdown leave free cash positive?

For Cameco, the answer is yes, with the contract book providing a multi-year buffer and the Westinghouse contribution adding non-spot-correlated EBITDA. For the marginal producers, the answer is no, and the response in past windows has been a mix of mine mothballing, equity issuance, and corporate restructuring. The 2014–2016 cohort attrition was substantial.

The check is not whether the spot will fall 40%; it is whether the operator has a business if it does. The first question is unanswerable. The second is a fact-pattern.

## 5. What is the operator's reinvestment record?

Capital allocation matters more in uranium than in most mining sectors because the cycle is so volatile that the temptation to over-build at the peak is unusually strong. The 2007 cycle peak left a generation of half-built mines stranded for fifteen years. The 2024–2025 cycle is the second uranium cycle in living memory where producers have spent meaningful capital on capacity additions; the test of whether the additions earn their cost of capital is still in front of us.

We read the reinvestment record by tracking, over a ten-year window, the operator's cumulative capital expenditure versus the cumulative free cash flow over the same period. For Cameco, the post-2018 record is exemplary: capital was deployed selectively, the McArthur restart was disciplined, and the Westinghouse acquisition was the major strategic bet whose verdict is still being written but whose early returns are encouraging. For the rest of the cohort, the records are more uneven and, in some cases, dependent on the next two years of spot prices to look good.

## 6. Is there a non-mining EBITDA contribution, and is it real?

The sixth check is specific to a small subset of uranium operators. Cameco's 49% stake in Westinghouse, Energy Fuels' rare-earth and vanadium contributions, certain royalty-and-streaming exposures: these are non-mining EBITDA streams that can materially change how the operator earns through the cycle.

Westinghouse is the most important single example. The 2023 acquisition added roughly C$170–200M of annual adjusted EBITDA contribution on Cameco's 49% share in 2025, with line of sight to growth as the AP1000 pipeline in Poland, Bulgaria, Ukraine, and the US converts from talking points to construction. The unsettled question is the durable mix between fuel and services (high-margin, repeatable) and new-build engineering (project-driven, lumpy). The answer changes the appropriate multiple by several turns. We do not have a confident answer yet.

> Uranium has been a narrative asset. The mines that survive the cycle are operating businesses. Reading them as the second thing is the only honest way to underwrite the first.

## The developer trap, in three filings

The uranium developer cohort has a recognizable pattern in the regulatory record. Three filings tell the story.

The first is the prospectus or the annual information form. A developer's prospectus typically describes a deposit, a metallurgical study, and a path to production. The path to production reliably involves another two to four years of permitting, engineering, and capital deployment. The reader who is paying attention notes the timeline carefully; it will slip. Almost every uranium developer's published timeline has slipped by years against the original schedule. The slippage is structural in the regulatory environment for nuclear-grade uranium production, not a flaw of any single operator. A developer whose deck claims first production in two years should, in our framework, be read as a developer whose first production is four or more years away.

The second is the equity-issuance history. Developers raise equity. The cadence and the pricing are public. A clean developer raises equity at the milestone moments — preliminary economic assessment, feasibility study, permit approval — and at prices consistent with the disclosed value-creation. A less clean developer raises equity at every share-price weakness, regardless of project progress, with the per-share dilution accumulating quietly. We pull the share-count history for every uranium developer that has been on the public market for at least five years. The cumulative dilution number, in many cases, exceeds 200% over five years. The producer cohort, by comparison, has share counts that are flat or modestly growing.

The third is the management compensation disclosure. A producer's compensation plan ties bonuses to production volumes, unit costs, safety statistics, and per-share metrics. A developer's compensation plan, in many cases, ties bonuses to milestone achievement — completion of a feasibility study, receipt of a permit, achievement of a financing. The milestone bonuses can be substantial relative to the operating cash flow of the developer (which is, by definition, near zero), and the milestone structure has historically been a poor proxy for ultimate shareholder value creation. Many developers have achieved every milestone and never produced an economic ounce. The framework's bias toward producers is, in part, a bias toward this compensation structure being aligned with what the shareholder actually wants.

The combined effect of the three filings is that the uranium developer cohort is, in our framework, structurally lower-quality than the producer cohort, with the exceptions being developers operating in supportive jurisdictions, on already-permitted ground, with disciplined equity issuance and per-share-aligned compensation. The exceptions are rare. The producer cohort, with the same six questions applied, is also small. Both observations are deliberate; the desk universe is built to be small.

## What the checklist eliminates

Run the six questions across a representative uranium developer or junior producer. The first eliminates most of the universe. The second narrows further. By the time you have run all six, the remaining names are a short list: Cameco, Kazatomprom, Orano, BHP's Olympic Dam (a copper mine with uranium by-product), and a handful of post-restart North American operators whose checklist passes are not yet supported by multi-year operating data.

That list is shorter than the universe of names being discussed at any given uranium conference. It is also the list whose share-price performance over the last cycle has been less spectacular than the developers'. The first observation is structural; the second is the consequence of an entire investor cohort having confused operators with options. Both can be true. The Halvren framework rewards Pillar I and II over the Pillar III commodity bet; that bias produces the smaller universe and the more patient compounding.

The compare for [Canadian Natural (CNQ)](/research/canadian-natural-cnq) in oil and gas, with its sustaining-cost discipline and dividend record, is closer to Cameco than it sounds. Both are operating businesses in narrative commodities. The narrative is the part that prices the stock in any given quarter. The operating business is the part that earns the position over a decade. The reader who can hold the second sentence steady through the first is the reader the framework is written for.
""",
})


# === 6 ====================================================================== #
NOTES.append({
    "title": "Silver's per-share problem: why production growth isn't shareholder value",
    "slug": "silver-per-share-problem",
    "date": "2026-04-09",
    "meta_description": "Most senior silver producers grow absolute ounces and destroy per-share value while doing it. The arithmetic is in the proxy. The streamer model is the workaround.",
    "excerpt": "Most senior silver producers have grown absolute ounces meaningfully over the past decade and destroyed per-share value while doing it. The arithmetic is mechanical. The reason it persists is incentive design.",
    "reading_time": 9,
    "tags": ["Materials", "Silver", "Capital allocation", "Per-share economics"],
    "related": [
        "roic-incremental-capital-plain-english",
        "cost-curve-is-a-lie-if-you-pick-the-quartile",
    ],
    "operators": ["first-majestic-ag", "agnico-eagle-aem", "freeport-mcmoran-fcx"],
    "body": """\
Silver is the most reliable example of a sector where production growth is not shareholder value. The cohort has grown absolute output meaningfully over the past decade. The per-share metrics tell a different story. The arithmetic is mechanical; it is not the operator's bad luck; the incentives that produced it are by design.

We have written before about why per-share production growth is the fourth of the seven numbers a careful investor reads on any operator. In silver, the gap between the absolute and the per-share number is wide enough that the absolute number is positively misleading.

## The arithmetic

Take a hypothetical silver producer that grows production from 10 million ounces to 15 million ounces over a decade. Absolute growth: 50%, or 4.1% CAGR. That is a respectable number on a press release.

Now apply the share-count growth that most silver producers have actually delivered over the same period. The cohort has grown share counts by between 60% and 200% over ten years, through a combination of equity issuance to fund acquisitions, equity issuance to fund growth capex, and significant option and warrant overhang from prior financings. Pick the middle of the range — 120% share-count growth — and per-share production has actually shrunk from 1.0 to 0.68 ounces per share. The operator's deck reports the headline 50% production growth. The shareholder, having held throughout, owns 32% less production per share than they started with.

That is not an extreme case. It is the cohort median.

## Why it happens

The arithmetic is not the operator's fault on any single transaction. Each individual equity issuance is defensible: the acquisition added reserves; the growth project required capital; the operator chose equity over debt for balance-sheet reasons. The problem is the aggregation. Each defensible decision adds shares; the cumulative result is the cohort's per-share decline.

The reason it persists is structural. Senior silver compensation plans, almost without exception, are weighted toward absolute production targets and absolute reserve growth. The proxy filings are public. The result is incentive-aligned with absolute growth, not per-share growth. A CEO whose bonus is tied to growing absolute production has no reason to resist the equity-funded acquisition that grows it; the shareholder, holding a smaller per-share claim, is on the other side of the trade.

[First Majestic (AG)](/research/first-majestic-ag) is one of the cohort. The Mexican producer has grown absolute output meaningfully over the past decade through Gatos and other transactions; the per-share record over the same period is meaningfully weaker. The operator's deck features the absolute number. The proxy discloses the compensation structure. Both facts are public.

## The compare to gold

Gold has the same potential incentive problem, but the senior gold cohort has produced a meaningfully cleaner per-share record than the senior silver cohort over the same window. The structural reason is asset quality: a gold operator that owns a Tier-1 asset can grow output through the asset itself rather than through equity-funded acquisitions, which keeps the share count discipline intact. A silver operator without a Tier-1 asset has to grow by acquisition, which is the path that produces dilution.

[Agnico Eagle (AEM)](/research/agnico-eagle-aem) is the cleanest senior gold example. The 2022 merger with Kirkland Lake was per-share accretive on day one — the rare gold deal that grew per-share reserves and per-share production simultaneously. The Detour Lake mill optimization since the merger has been an organic per-share story. Per-share reserves are a tracked metric in the compensation plan. The result is in the ten-year share-count line: relatively flat, despite an actively acquisitive period.

That posture is not available to most silver producers because the asset universe is different. The silver-primary cohort is small; the polymetallic mines that produce silver as a by-product (lead-zinc, copper-gold) sit inside the books of other operators ([Freeport](/research/freeport-mcmoran-fcx) being one); the Tier-1 silver-primary deposits that could anchor a clean per-share growth story are few and contested.

> Growth at the expense of the share count is a tax the operator quietly charges you.

## How to read the per-share record

The Halvren check on any mining operator's per-share record is mechanical, and we run it for every name on the coverage list every year. Pull the operator's average share-count for the most recent year and for the year ten years prior. Pull production and reserves for both years. Compute the CAGR of per-share production and per-share reserves over the decade. Compare to the absolute CAGR for both metrics.

If the per-share CAGR is meaningfully positive and tracks the absolute, the operator has grown by improving the asset rather than buying assets with new shares. If the per-share CAGR is meaningfully negative while the absolute CAGR is positive, the operator has grown headline output by transferring value from the existing shareholder to the seller of the acquired asset.

The senior silver cohort, in aggregate, falls into the second bucket. There are exceptions. Pan American Silver's record post-Tahoe is more nuanced than the cohort average. Wheaton Precious Metals' streaming model is structurally per-share-accretive because the financing currency is a function of the deal price rather than the cohort dilution rate. Royal Gold and Franco-Nevada are similarly clean for the same reason: the business model is not a mining business in the per-share-dilution sense.

## The "honest growth" path

A silver operator that wants to grow without diluting the existing shareholder has three options. The first is to fund growth through retained free cash flow, which requires the asset base to produce enough free cash to fund it — a high bar in silver, where the cohort cash-cost average sits in the high-teens-of-dollars-per-ounce range. The second is to fund growth through debt rather than equity, which requires the balance sheet to support it. The third is to buy back stock when the market price implies a lower per-ounce value than the operator's own asset base, which requires the operator to have a view of intrinsic value that exceeds the market's.

The third option is the rarest, and it is the cleanest signal. A silver operator that uses free cash flow to retire stock at trough prices, and accepts the optical drag of slow absolute growth, is making a per-share-positive bet that few in the cohort have been willing to make. We have not seen it executed at meaningful scale in the senior silver cohort over the past decade.

## The streamer alternative

A reader who wants silver exposure without the per-share dilution problem has a structural workaround: the precious-metals streaming and royalty operators. Wheaton Precious Metals, Franco-Nevada, Royal Gold, and a handful of smaller streamers buy contractual rights to a fixed percentage of future production from a primary operator's mine, paid for upfront, and receive metal deliveries (or cash equivalent at the spot price) for the life of the asset. The streamer model is structurally per-share-accretive on every deal that closes at acceptable economics because the financing currency is contractual rather than the streamer's own equity.

The compounded effect on a streamer's per-share metrics over a decade is the opposite of the senior silver producer cohort. Wheaton Precious Metals has grown per-share attributable silver and gold production over ten years while keeping the share count growth in the single-digit range. The streamer multiple is higher than the producer multiple — for good reason — but the per-share total return record over the same window is, in many cases, meaningfully better.

The streamer model is not a perfect hedge against the silver-producer problem. The streamer takes counterparty risk on the underlying mine operator; if the operator fails, the streamer's deliveries are at risk. The streamer also has less optionality on a silver-price up-cycle than a debt-financed producer, because the upside is shared with the mine operator under the original contract terms. The streamer's beta to silver is lower; the streamer's per-share quality is higher; the choice depends on what the reader is underwriting.

For a Halvren-style portfolio that prioritizes per-share compounding over commodity beta, the streamer exposure is meaningfully more attractive than the senior silver producer exposure. We hold no senior silver producers on the desk currently. We track the streamer cohort more carefully than the producer cohort. Wheaton in particular has the cleanest per-share track record in the wider precious-metals universe; the streamer-royalty trade is the desk's preferred way to be paid for any precious-metals exposure that the macro thesis ever calls for.

The structural read on silver is therefore: the cohort produces a poor per-share record because the asset universe forces equity-funded acquisitions; the streamer model bypasses that problem by financing through contract rather than equity; and the silver investor who has been told for fifteen years that "production growth is the thesis" has been buying the wrong basket. The names are the same. The structural mechanics are different.

## What we underwrite

Silver is a small position on the desk, and the reason is the per-share record. We hold First Majestic on the desk in part as a forcing function: writing about the per-share problem in a name that exemplifies it keeps the framework honest. The operator's writeup [(see the desk page)](/research/first-majestic-ag) records the open Pillar II questions clearly. The principal's view on the cohort has not changed in five years.

If the silver tape gives us a meaningful drawdown and a senior operator with a clean per-share record emerges from it, the position changes. Until then, the read is the same: production growth is not shareholder value.

## Why the framework matters beyond silver

The per-share-versus-absolute framework applies far outside silver. Any operator that grows headline output through equity-funded acquisition is potentially destroying per-share value, regardless of the sector label. The framework is most visible in silver because the cohort dilution rate is unusually high; it is most useful elsewhere precisely because the dilution there is less obvious. A copper operator that has grown reserves through an equity-funded acquisition every two years is on the same arithmetic, even if the absolute production growth looks more defensible. The compounded per-share record over a decade reveals the same pattern.

The Halvren framework runs the per-share check on every operator on the coverage list, every year. Most pass; the operators on the desk pass cleanly. The cohort we do not own — including most senior silver producers, several gold-producer growth stories, and a small number of copper names whose acquisition pace has been unusually high — fails the check on the same arithmetic. The check is the same; the operators it eliminates differ by sector. The lesson is the same in every case: the operator's deck is the operator's story, and the share count is the part of the story that costs the existing shareholder real money to fund.

The math is in the proxy filings, every year. We read them.
""",
})


# === 7 ====================================================================== #
NOTES.append({
    "title": "The dividend that survived: 26 consecutive raises at Canadian Natural",
    "slug": "dividend-that-survived-cnq",
    "date": "2026-04-02",
    "meta_description": "Twenty-six consecutive years of dividend raises at Canadian Natural, through 2015 and 2020. The record is a capital-allocation document, not a dividend story.",
    "excerpt": "Twenty-six consecutive years of dividend increases at Canadian Natural Resources, including raises in 2015 and in March 2020. The record is a capital-allocation document, not a dividend story. We read it for what the operator does at the bottom.",
    "reading_time": 10,
    "tags": ["Energy", "Canada", "Capital allocation", "Crisis behaviour"],
    "related": [
        "what-2015-and-2020-told-us-canadian-energy",
        "insider-buying-vs-granting",
    ],
    "operators": ["canadian-natural-cnq", "enbridge-enb", "suncor-su"],
    "body": """\
Canadian Natural Resources has raised its base dividend in every year for twenty-six consecutive years, including 2015 and 2020. The raise announced in March 2020 — a six per cent increase — landed the same week the WTI front-month went briefly negative. The arithmetic of that raise is the cleanest single piece of evidence about Canadian energy capital allocation in the public record.

The record is not a dividend story. The dividend is a downstream effect. The record is a capital-allocation document about how a Canadian oil and gas business is built to survive the bottom of its own cycle.

## The twenty-six raises, in three windows

The dividend has been raised in three distinct macro windows that tested whether the prior raises could continue.

The first window: 2009–2010, the global financial crisis. CNQ raised through the trough. The asset base in 2010 was meaningfully smaller, the share count meaningfully larger relative to today's; the dividend per share was a fraction of the current rate. The raise was modest in absolute terms. The discipline was set.

The second window: 2015–2016, the oil cost-curve reset. WTI averaged the high US$40s for two years; AECO traded persistently below US$2/GJ; Canadian heavy-light differentials widened to historic extremes. CNQ raised the dividend in both years and made no equity issuance. Capital expenditure was cut meaningfully. The 2016 sustaining capex per barrel printed in the low US$10s, which was the structural answer to the price-tape question. The cohort behaviour in the same window included multiple dividend cuts, several equity issuances at distressed prices, and the early stages of the restructurings that closed two years later.

The third window: 2020, the COVID demand collapse. The March 2020 raise was the signature event. The operator's commentary at the time was deliberate: the dividend was covered at the trough oil price, and the raise was the most public way to communicate that fact to a shareholder base that had been told by every other operator's announcement that the dividend was at risk. The arithmetic supported the commentary. The 2020 free cash flow at the low WTI tape was still positive on a maintenance basis. No equity was issued. Capital expenditure was cut hard.

## The arithmetic that made the raises possible

The dividend record is downstream of three structural choices the operator has made over thirty years.

**The asset mix.** CNQ's production is predominantly long-life and low-decline. The Horizon and Albian mining and upgrading complex, the Pelican Lake and Primrose thermal projects, and the legacy heavy-oil and natural-gas assets together produce a base that declines at a low single-digit rate without sustaining capex. Compare this to a Permian-shale operator whose base production declines at 40% per year; the sustaining capex required to hold flat is a fundamentally different number. CNQ pays for low decline up front in the asset acquisition; the dividend in 2020 is the receipt.

**The cost discipline.** Sustaining capex per barrel printed in the low US$10s in 2015 and 2020. The 2025 number is slightly higher but remains first-quartile in the Canadian cohort. The discipline is operational: the operator's mining and SAGD sites have been in continuous improvement for two decades, and the unit cost numbers reflect that.

**The capital allocation culture.** Murray Edwards is the architect of the culture. He has been on the board for thirty years and a meaningful shareholder throughout. Tim McKay has been the senior operating presence for two decades. The continuity of the capital allocator is the part that does not show up in any operating metric but explains every decision that produced the record.

## What 2020 actually communicated

The March 2020 raise was a signal, and the signal was about more than the dividend. The operator was saying, in public, that it did not need to participate in the cycle's worst quarter the way the rest of the cohort would. The hold positions through the trough were the part the operator could see in the asset base; the equity-issuance restraint was the part the operator was choosing; the dividend raise was the visible artifact of both.

The follow-on actions through 2020 and 2021 confirmed the signal. CNQ continued to buy back shares through the trough at prices well below the prior peak. The buybacks were modest in absolute size, by design — the operator's posture has been "do not embarrass the dividend by promising more than the buyback can deliver" — but the cumulative effect over the 2020–2025 period has been meaningful per-share reserve and production growth.

[Suncor (SU)](/research/suncor-su) had a different 2020. The dividend was cut by 55%. The cut was rational; the conditions that forced it were the result of five years of incremental cost-discipline erosion at Fort Hills, the upgrader, and the safety record. The CEO change in April 2023 was the direct response. The post-Kruger reset is the recovery; the pre-Kruger drift is the cautionary tale that the same management team can produce one record in 2015 and a meaningfully worse one in 2020.

[Enbridge (ENB)](/research/enbridge-enb) had a different 2020 again. The dividend was raised through both windows, with no equity issued at distressed levels, and the contractual structure of the pipeline business absorbed the macro shock without operational consequence. The CNQ record on the E&P side and the ENB record on the infrastructure side are the two cleanest dividend-and-discipline records in Canadian energy across both stress windows.

> The dividend held through 2015 is a signal. The dividend held through 2020 is a signal. The dividend held through both is a different signal, and the operators who delivered it are a short list.

## The compare to Berkshire's record

The Canadian Natural record draws a comparison most readers in Canadian capital markets do not make often enough. The cleanest parallel to Murray Edwards's capital allocation record at CNQ is, in our reading, Warren Buffett's record at Berkshire Hathaway in the operating period from 1985 to 2010. The structural similarities are not coincidental.

Both built capital cultures around a small number of repeatable rules. Buy assets that produce cash without requiring growth capital to do so. Hold assets through cycles. Treat the dividend, or in Berkshire's case the share-count, as the visible discipline. Do not issue equity at distressed prices. Buy back stock when the market gives you the opportunity to. Promote internally and prefer continuity over freshness in operational leadership. The two operators apply the rules in different sectors, but the rules themselves rhyme more than the conference-panel commentary tends to acknowledge.

The differences are also informative. CNQ pays a dividend; Berkshire does not, on the grounds that retained earnings compound faster inside Berkshire than they would in shareholder hands. The CNQ dividend is a function of the operator's cash structure: the assets generate so much free cash that, after sustaining capex and growth capex, there is more capital available than the operator can productively deploy. The dividend is the residual; the buyback is the calibrated lever. The Berkshire model is different because the holding-company structure allows for higher-return reinvestment opportunities than CNQ's asset base typically presents.

The most useful single sentence on the Edwards record is one Murray Edwards himself approximates in CNQ's letters: the dividend is the operator's promise, the buyback is the operator's option, and the equity issuance is the operator's failure. The 2015 and 2020 records demonstrate the first sentence in two different cycles; the post-2015 and post-2020 buyback records demonstrate the second sentence in two different drawdowns; the absence of any equity issuance at distressed prices over thirty years demonstrates the third. Three sentences. Thirty years of receipts.

## What we read going forward

The twenty-six-year record is one of the cleanest capital-allocation documents in North American energy. It is also a record of a particular generation of capital allocator. Murray Edwards is in his sixties. Tim McKay is the operating successor, but the cultural transmission past the next decade is a real question that the operator's commentary touches on but does not fully resolve.

The succession question is the open Pillar II question on the desk. We read every proxy filing for the board composition, the executive bench, and the compensation plan tilt. The post-2022 compensation reset moved the plan further toward per-share metrics, which is the right direction. The next decade will tell whether the culture is operator-specific or institutional.

## What survives the founder

The most important Pillar II question on the CNQ desk is also the most uncomfortable: what survives Murray Edwards. The Edwards record is one capital allocator's record. The institutional question is whether the discipline that produced the twenty-six raises is encoded deeply enough in the board, the management bench, and the compensation structure to outlast the original capital allocator's tenure.

The honest read is partial. Tim McKay's promotion to CEO in 2020 was a continuity choice; McKay had been the operational architect for two decades and produced the unit-cost discipline that the dividend record sits on. The post-McKay generation of executives is visible at the management ranks but not yet tested at the apex. The board composition has been stable, the compensation plan has been per-share-aligned since the early 2010s, and the corporate culture is famous in Calgary for its quiet seriousness. All of these are encouraging.

The cultural transmission test is the next decade, not the next quarter. We track the proxy filings for board renewals, the compensation plan for any drift toward absolute-production metrics, and the executive bench for the third generation of capital allocators. If the cultural transmission holds, the dividend record continues into a fourth decade. If it does not, the record peaks somewhere in the late 2020s and the operator becomes a normal Canadian heavy-oil name. The base-case probability, in our framework, is the first; the tail probability is the second; both deserve to be named explicitly because the entire CNQ thesis sits on the answer.

In the meantime, the 2026 capital plan reads as a continuation of the prior twenty-six years. Sustaining capex remains first-quartile; the dividend is raised; the buyback is modest and consistent; no equity is issued. The same playbook produces the same record. The reason most readers find it dull is exactly the reason we read it: dull is what compounding looks like when you write it down every year. The chart that records it does not need a price target, a panel discussion, or a thesis change. It needs a steady hand and a willingness to wait.
""",
})


# === 8 ====================================================================== #
NOTES.append({
    "title": "Insider buying vs. insider granting — the only signal that costs the operator something",
    "slug": "insider-buying-vs-granting",
    "date": "2026-03-26",
    "meta_description": "Options are loyalty to a quarter; open-market purchases are loyalty to a decade. The only insider signal that costs the executive real money, read carefully.",
    "excerpt": "Options grants are loyalty to a quarter. Open-market purchases are loyalty to a decade. The difference is the only insider signal that costs the operator something. The signal is public. Most decks do not put it on the cover.",
    "reading_time": 9,
    "tags": ["Operator quality", "Insider activity", "Cross-sector"],
    "related": [
        "dividend-that-survived-cnq",
        "how-to-read-canadian-oil-gas-operator-seven-numbers",
    ],
    "operators": ["kinder-morgan-kmi", "tourmaline-tou", "agnico-eagle-aem"],
    "body": """\
The most misread metric on the operator-quality side of the Halvren framework is insider ownership. The most-cited numbers — total insider holdings as a percentage of shares outstanding — are dominated by options, RSUs, restricted stock, and prior-grant overhang. Those numbers tell you almost nothing about how the executive thinks about the share price today.

The honest signal is open-market purchases by named executives with their own money. The signal is public. The dollar amount, the share price at the time of the purchase, and the buyer's name are all in the regulatory filings. It is the only insider signal that costs the operator something.

## Why granted equity is almost free

Options, RSUs, and restricted stock are part of the compensation plan. They are negotiated at the proxy. The operator is, in the regulatory sense, "issuing" the equity, but the executive is "receiving" it on the same day, at the strike price set by the compensation committee, with no out-of-pocket capital deployed. The grant is loyalty to a quarter — it vests on schedule, regardless of share-price behaviour — and it produces income to the executive whether the operator does well or badly within wide bands.

Options have an additional wrinkle. The executive only pays the strike price on exercise, and only if the share price exceeds the strike. The "underwater" outcome of an options grant is not a loss to the executive; it is a missing gain. That asymmetry is what makes options compensation an alignment instrument _toward_ upside without an alignment instrument _against_ downside, which is exactly the opposite of the alignment a careful shareholder wants from operating leadership.

We do not read insider ownership numbers that are dominated by granted equity. The number is too easy to construct without behaviour.

## What open-market purchases mean

An open-market purchase is the executive buying shares from another shareholder, at the prevailing market price, using cash that came from somewhere — salary, prior compensation, personal balance sheet. The cost is real. The executive could have spent the same dollars on something else. The decision to spend them on additional ownership of the operator is informative.

The signal is informative because it is dual-directional. The executive who buys at a six-month low has expressed a view that intrinsic value is meaningfully above the market price. The executive who buys at a one-year high has expressed a view that the asset base has improved enough to justify the higher level. The executive who refuses to buy at any price is also expressing a view; the absence is also data.

What is not a signal: a single small purchase by a single CEO, timed near a quarterly earnings release, in size that is small relative to the executive's total compensation. That is a public-relations purchase, and it is structured to look like a signal while costing the executive almost nothing.

## The cleanest examples on the desk

[Kinder Morgan (KMI)](/research/kinder-morgan-kmi) is the cleanest insider-buying story in our coverage universe. Rich Kinder, the founder and chair, has been buying open-market for decades. The cadence has been consistent through up cycles and down cycles. The 2015 dividend cut, which was the Pillar II reset event for the operator, was followed by continued open-market purchases by the founder; the signal was that the cut was the right call and the underlying value was unchanged. The cumulative dollar value of Rich Kinder's open-market purchases over the past two decades is the largest single insider position in US midstream. The signal has been internally consistent for longer than most CEOs have held their seat.

[Tourmaline (TOU)](/research/tourmaline-tou) is the Canadian equivalent. Mike Rose has been the founder, CEO, and chair since 2008, and the open-market purchase record is consistent. The structural advantage of the Tourmaline model is that the founder's personal balance sheet is meaningfully concentrated in the operator from inception; the buying behaviour is incremental on top of an already-substantial position. The signal is the cadence: the absence of purchases in a particular quarter is informative, just as the presence is.

[Agnico Eagle (AEM)](/research/agnico-eagle-aem) is a different case. Sean Boyd, who ran the operator for two decades before transitioning to chair, was a consistent open-market buyer through his executive tenure. The Boyd-era buying record is part of why the Agnico Eagle culture has the Pillar II grade it does. The Ammar Al-Joundi succession in 2022 has produced some open-market buying activity at the new CEO level, though not at the same cumulative magnitude as the Boyd record. We track it.

## The Halvren reading framework

We pull insider transactions for every operator on the coverage list, every quarter. The data is from SEDI in Canada and SEC Form 4 in the US. The framework is mechanical.

**First, separate purchases from grants and exercises.** Most insider tape includes all three. We filter to open-market purchases only. That alone eliminates most of the "insider buying" coverage that appears in the financial press, which routinely conflates the categories.

**Second, weight by total dollar value, not share count.** A purchase of 10,000 shares at C$50 is a more meaningful signal than 100,000 shares at C$2. The dollar number reflects the real capital commitment.

**Third, track the cadence over time.** A consistent buyer over five years is a different signal than a single large purchase in a single quarter. The single large purchase is more often correlated with an internal event (a new lock-up release, a personal liquidity event, a planned tax move) than with intrinsic-value conviction.

**Fourth, read the absences.** A quarter without insider buying at an operator where the share price has materially declined is informative. The absence often means the executive's read of intrinsic value is unchanged or worse than the market's. That information is in the absence.

> Options are loyalty to a quarter. Open-market purchases are loyalty to a decade. The difference is the only insider signal that costs the operator something.

## Where the signal breaks down

Open-market purchases are a clean signal in single-CEO operators, in family-stewarded operators, and in founder-controlled operators. The signal is harder to read in widely-held public operators where the executive team has rotated frequently. A new CEO who buys $500K of stock in the first quarter is signaling something, but the signal is mixed: it could be conviction, or it could be the compensation committee informally requesting visible alignment.

The signal also breaks down in operators with structural restrictions on insider buying — closed-window policies, regulatory limits in certain jurisdictions, or unusually heavy compensation in restricted equity that limits the executive's personal balance sheet for outside purchases. We note these cases and read accordingly; the absence of buying is not always the executive's choice.

## Reading the absences

The most under-appreciated part of the insider tape is the absence. A senior executive who never buys at any price is making a statement that, in our framework, weighs as heavily as a consistent buyer would in the other direction. The framework reads absences in three patterns.

The first pattern is the new-CEO absence. A CEO promoted from inside who, in the first eight quarters of the new tenure, does not buy any open-market stock is making an implicit signal. Sometimes the signal is benign (the executive's personal balance sheet is over-concentrated in the operator already through prior compensation; the executive has personal liquidity constraints; the regulatory closed-window rules limit opportunity). Sometimes the signal is less benign. In our experience, the new-CEO who is bullish on the operator's intrinsic value typically buys, in modest size, within the first four quarters. The new-CEO who does not buy at any price during a meaningful share-price drawdown is, more often than not, expressing the view that the price is not yet attractive — and the CEO's read of intrinsic value should, by definition, be more informed than the market's.

The second pattern is the founder's selective absence. A founder-operator who has been a consistent buyer for two decades, then goes quiet for two consecutive years through a meaningful share-price weakness, is communicating something. The quiet period is rarely a coincidence. Sometimes the explanation is operational (a personal liquidity event, a tax-planning move). Sometimes the explanation is structural (the founder's read of intrinsic value at the current price is more pessimistic than the prior decade implied). The framework reads the quiet period as a question, not an answer, and the question is whether the underlying business has changed in a way the deck commentary has not yet captured.

The third pattern is the cohort-wide absence. A meaningful share-price drawdown in a sector during which no operator in the cohort sees insider buying is informative at the sector level rather than the individual level. The 2018–2019 lithium drawdown produced almost no insider buying across the senior lithium cohort, which retrospectively was a signal that the cohort itself did not view the price weakness as an opportunity. The 2014–2016 Canadian heavy-oil drawdown was different: a small number of operators saw consistent insider buying through the trough (CNQ, Tourmaline among them), which was the early signal that those operators viewed the trough as transitional rather than structural. The cohort behaviour matters.

Reading absences is a more probabilistic exercise than reading purchases. The framework does not produce a single signal; it produces a question that is worth asking against the operator's other Pillar II data. In aggregate, across the Halvren coverage list, the operators with the cleanest buying records also have the cleanest 2015 and 2020 records, the cleanest compensation structures, and the cleanest succession benches. The clustering is, again, not coincidence.

## What it does not replace

Insider buying is one of the four Pillar II questions in the Halvren Checklist. It is not the most important on its own; it is informative when read alongside the others (compensation structure, prior-cycle capital decisions, succession). The signal works best as a confirmation or contradiction of what the other three already imply.

The operators on the desk whose insider record is strongest are also, broadly, the operators whose 2015 and 2020 records are strongest, whose compensation plans are most per-share-aligned, and whose succession benches are clearest. The Pillar II answers cluster. The clustering is not coincidence. The same operators, year after year, build the same culture. The insider buying is the visible artifact of a culture that has already produced the dividend record, the compensation discipline, and the succession bench. Read the artifact for what it confirms; do not read it for what the rest of the framework would tell you without it.
""",
})


# === 9 ====================================================================== #
NOTES.append({
    "title": "ROIC on incremental capital, in plain English",
    "slug": "roic-incremental-capital-plain-english",
    "date": "2026-03-21",
    "meta_description": "Marginal ROIC, not average ROIC, is what the next dollar earns. The math is mechanical. Most operators do not publish it because the answer is uncomfortable.",
    "excerpt": "Reported ROE and reported ROIC are average metrics across the whole asset base. The number that matters is what the next dollar of capital earns. The math is not difficult. The reason most operators do not report it is that the answer is sometimes ugly.",
    "reading_time": 10,
    "tags": ["Capital allocation", "Operator quality", "Cross-sector"],
    "related": [
        "how-to-read-canadian-oil-gas-operator-seven-numbers",
        "silver-per-share-problem",
    ],
    "operators": ["canadian-natural-cnq", "teck-resources-teck", "occidental-oxy"],
    "body": """\
Most operator decks report return on equity or return on invested capital on a whole-business basis. The number is average ROIC across every dollar of historical capital, irrespective of when it was deployed, by which CEO, into which asset. As a backward-looking summary it is fine. As a forward-looking decision input it is almost useless.

The number that matters is marginal ROIC. What does the next dollar of capital, deployed today, earn? The math is not difficult. The reason most operators do not report it cleanly is that the answer is sometimes uncomfortable, and the answer changes the multiple readers should pay for the next round of capex.

## Three ways the next dollar gets deployed

Operators deploy incremental capital in roughly three forms. The framework reads each separately.

**Form one: sustaining capex.** The dollars that keep production flat. The marginal ROIC on sustaining capex is, by definition, the operator's average ROIC on the asset base — it earns what the asset earns. The relevant test is not whether sustaining capex is value-creating (it is, if the asset is) but whether the sustaining-capex number itself is rising over time. A rising sustaining number tells you the asset base is harder to hold flat than it used to be, which is the leading indicator of structural cost-curve drift. We track the per-BOE or per-tonne sustaining number every year for every operator on the coverage list.

**Form two: growth capex on the existing asset.** Brownfield expansion, mill optimization, an in-fill drilling program. The marginal ROIC on brownfield growth is often the highest available to the operator: the surrounding infrastructure is already in place, the engineering is well-understood, and the production-cost curve flattens as the asset scales. [Canadian Natural (CNQ)](/research/canadian-natural-cnq) at Horizon has produced consistently first-quartile marginal ROIC on incremental brownfield capital over the past decade; the Pelican Lake polymer flood was a particularly clean example of brownfield value creation. Brownfield growth is the form of capex we read most generously.

**Form three: growth capex on a new asset, by acquisition or greenfield build.** This is the form where the worst capital allocation in mining and energy has happened. A greenfield build at the top of a commodity cycle, or an acquisition paid for in inflated currency at the same point, can carry marginal ROIC of less than zero for years before the original case shows in the data. The 2014–2015 wave of greenfield builds in the senior gold sector destroyed value on most of them. [Teck Resources (TECK)](/research/teck-resources-teck)'s Quebrada Blanca 2 project was a multi-billion dollar capex program whose ROIC has trailed the original case meaningfully; the 2024–2026 ramp will determine the long-term verdict.

The third form is also where the buyback decision fits, considered as the inverse: a dollar of capital used to retire stock at the prevailing market price earns the inverse of the price-to-earnings multiple at the moment of the buyback. At a 10x earnings multiple, a buyback is a 10% marginal ROIC capital deployment. The operator's choice between greenfield growth at 6% marginal ROIC and a buyback at 10% marginal ROIC is, in the framework, a straightforward arithmetic problem.

## The CrownRock test at Occidental

[Occidental (OXY)](/research/occidental-oxy) closed the CrownRock acquisition in August 2024 at a headline price of roughly US$12B. The acquisition extended the Midland Basin position into the Wolfberry-fairway acreage at type-curve assumptions that were aggressive by Permian-cohort standards. The transaction was funded with a mix of cash, equity, and debt.

The honest test of the marginal ROIC on CrownRock is, in the framework, three numbers. First, the per-well productivity of the acquired acreage at the wells drilled post-close. Second, the unit operating cost trajectory at the integrated assets. Third, the per-share accretion at a constant oil price. The first two are knowable from the operator's quarterly filings; the third is a derived metric we run from the public data.

The early read on the first two is encouraging. Per-well productivity has held within the original case; unit costs have continued to trend down. The third number — per-share accretion — depends on the rate of debt paydown and the resumption of the buyback at the elevated debt level the deal created. The walk to the US$15B near-term net-debt target is the path. The buyback resumption is the moment the marginal-ROIC question is answered cleanly. We do not have a confident view on the final answer yet.

The transaction is a useful case study because the operator has shown its work. The deck disclosed the type-curve assumptions; the integration milestones have been reported; the per-well data is in the filings. Most acquisitions of this size do not show this much work. When the deck does not show the work, the reader has to ask why.

## The QB2 test at Teck

The other instructive case is Quebrada Blanca 2. The greenfield copper project was sanctioned in 2018 at an original-case capital cost meaningfully below what the project actually cost when commissioned. The ramp to design throughput took longer than the original timeline. The unit operating cost at the integrated mine has been higher than the original case. The marginal ROIC on the original capital, as deployed, has trailed expectations.

That is not a verdict; it is a snapshot. The mine is producing. The marginal copper coming out of QB2 in 2026 is, on a forward basis, earning competitive economics at mid-cycle copper prices. The question for the marginal-ROIC framework is which capital base the reader runs the calculation against: the original sanctioned amount, or the actually-spent amount. The answer changes the headline meaningfully. Teck reports both. The honest framework reads both.

> Reported ROE is the historical average. Marginal ROIC is what the next dollar earns. They are not the same number, and the difference is the operator's discipline.

## Why operators avoid the cleaner framing

A simple marginal-ROIC disclosure — "our next dollar of capital earns this rate at the current price deck" — would be the most useful single line a capital-intensive operator could publish. Almost no operator publishes it. The reasons are not malicious. They are structural.

First, the disclosure invites a specific accountability that operators are not designed to deliver. If the next dollar's marginal ROIC is disclosed at 12%, the operator owes the shareholder an explanation for any year in which the disclosed return falls below 12%. The accountability is what the operator wants to internalize, not externalize.

Second, the disclosure varies meaningfully by commodity price, currency, and capital structure. A single point estimate is a useful sentence to write but a misleading one to bind oneself to. Most operators prefer a range of capital-allocation guidance with no point-estimate marginal ROIC because the range is harder to be wrong about.

Third, the disclosure can be tactically used by the share-price market against the operator. A disclosed marginal ROIC of 8% during a period when the equity yield is 9% creates an obvious capital-allocation argument for buybacks over capex; the operator may have non-financial reasons for preferring capex (asset-life extension, regulatory relationship, employee retention) that the framework does not capture. The disclosure encourages a conversation the operator may not want to have.

## The buyback as the cleanest test

Of the three forms of incremental capital deployment, the buyback is the cleanest test of the operator's view on intrinsic value. A buyback at the prevailing market price is a real-time disclosure of the operator's view that the underlying business is worth more than the market is offering. A pause in the buyback is the inverse disclosure. Both are informative.

The math is mechanical. A buyback earns the inverse of the price-to-earnings multiple at the moment of execution. At a 10x multiple, the buyback earns a 10% pre-tax return on the capital deployed. At a 20x multiple, the buyback earns 5%. Compared against the marginal ROIC on greenfield capex (often 6–10% pre-tax in mining and energy) or brownfield capex (often 10–18%), the buyback is competitive or superior across most of the cohort at most of the time.

That arithmetic is what makes the buyback a useful Pillar I read. An operator who consistently buys back stock at trough prices and pauses at peak prices is making the marginal-ROIC math work in the shareholder's favour. An operator who buys back at peak prices and pauses at trough prices is doing the opposite. The pattern over a decade is visible in the share-count history and the realized buyback price.

[Canadian Natural (CNQ)](/research/canadian-natural-cnq)'s buyback record over 2020–2025 is the cleanest single example on the desk. The pace was modest in absolute size but consistent through the trough; the share count fell by single-digit percent points over a five-year window that included material drawdowns; the per-share reserves and per-share production both grew through the period. The math is in the public disclosures every quarter.

The counter-example is illustrative. Several Canadian operators in the 2014–2016 window bought back stock at near-peak prices in 2014, paused the buyback in 2015 when the share price fell by 50%, and resumed in 2018 at higher prices than the 2015 pause. The marginal ROIC on the 2014 buyback was negative; the operator was buying at a price the market subsequently demonstrated was meaningfully too high. The same operator would have been better served by paying down debt in 2014 and buying back in 2015 at the lower price. The lesson is the same one Buffett published in his 1980s letters: a buyback is a tool, and the tool is only useful when the operator has the discipline to use it at the right price.

The framework reads the buyback record as part of the marginal-ROIC question, and the consistency of the buyback record is one of the strongest single signals of Pillar II capital culture. The two pillars are not separable in practice.

## What we do with the framework

The Halvren marginal-ROIC framework is a thinking tool, not a published model. We use it internally on every Pillar I and Pillar III assessment. For most operators, the marginal-ROIC question yields a defensible range rather than a point estimate. The range is informative.

Operators whose marginal-ROIC range is wide and downward-skewed get the harder read on Pillar I. Operators whose marginal-ROIC range is narrow and consistently above the cost of capital get the cleaner read. The framework will not tell you the right multiple for the stock; it will tell you which operators are deploying capital at returns that justify the next year of patience, and which are deploying capital at returns that suggest a different decision is overdue.

The operators on the Halvren desk are not always the operators with the highest marginal ROIC at any given moment. They are the operators whose marginal ROIC framework is consistent year-to-year, disciplined when the easy money is on the table, and honest about the answer when it is not what the deck says.
""",
})


# === 10 ===================================================================== #
NOTES.append({
    "title": "What boring looks like on a thirty-year chart: the case for Canadian infrastructure compounding",
    "slug": "boring-thirty-year-chart-canadian-infrastructure",
    "date": "2026-03-21",
    "meta_description": "A 6% earnings compounder plus a 4% dividend yield for thirty years. Canadian infrastructure is the boring half of the desk, and the half that pays for the wait.",
    "excerpt": "A 6% earnings compounder, a 4% dividend yield, no glamour, and thirty consecutive years of raises. The math is unspectacular. The total-return chart is not. The Canadian infrastructure cohort is the boring half of the desk, and it is the half that pays for the wait.",
    "reading_time": 9,
    "tags": ["Infrastructure", "Compounding", "Canada", "Capital allocation"],
    "related": [
        "pipelines-are-turnpikes-not-commodity-bets",
        "dividend-that-survived-cnq",
    ],
    "operators": ["fortis-fts", "enbridge-enb", "cn-rail-cnr"],
    "body": """\
The most boring chart in Canadian capital markets is the thirty-year total return on the senior Canadian infrastructure operators. The line goes up. The line goes up most years. The line continues going up through commodity stress, financial crises, and pandemics. The shape is unremarkable on a quarter chart. On a thirty-year chart it is the entire point.

A 6% earnings compounder, a 4% dividend yield, no glamour: that is the arithmetic of Canadian infrastructure. Compounded for thirty years, the math produces a 5.7x total return at constant valuation. Most of the desk's compounding work is done by names whose deck commentary will never appear at a conference panel and whose CEOs have not been the subject of an industry profile in five years. That is, in the strict sense, the design.

## The cohort

The Canadian infrastructure cohort is small enough to name on one line: [Fortis (FTS)](/research/fortis-fts), [Enbridge (ENB)](/research/enbridge-enb), [TC Energy (TRP)](/research/tc-energy-trp), [Canadian National (CNR)](/research/cn-rail-cnr), Pembina, the Brookfield-controlled subsidiaries that trade as separate listings (BIP, BEP), and a handful of regulated utilities of more limited diversification.

The cohort sits at the boring end of the desk. The valuation multiples are unremarkable, the analyst coverage is dense, the deck commentary is interchangeable across the names. None of the operators is going to deliver an outsized single-year return. All of them have been delivering an unremarkable double-digit total return for three decades, in aggregate, with rolling dividends raised in essentially every year.

Fortis has raised the base dividend for fifty-two consecutive years. The streak is the longest in Canada. The shape of the streak — through 1981 inflation, the 1987 crash, the 1990 recession, the 1998 Asian crisis, the dot-com bust, the global financial crisis, the 2015 commodity reset, and the 2020 pandemic — is the part most readers find dull. It is dull because every year's raise looks like the previous year's. It is also, considered in aggregate, the cleanest single capital-allocation document in the Canadian listed universe.

## The arithmetic of dull compounding

Take a Canadian infrastructure operator with the following profile, which is roughly the average of the cohort. Rate base grows at 6% per year. Authorized ROE on the rate base sits at 9.5%. Earnings per share grow at 6% per year. The dividend is set at 75% of earnings and grows in line. The dividend yield at the prevailing share price is 4%.

Total return at constant valuation: 6% earnings growth plus 4% dividend yield equals 10% annualized. Over thirty years, 10% compounds to 17.4x. Over twenty years, 6.7x. Over ten years, 2.6x. None of those numbers is dramatic on any single-year window. All of them are the consequence of the same dull arithmetic.

The valuation does not stay constant. Multiples expand and contract on a five- to seven-year cycle, and the buy-and-hold investor lives through the contractions as paper drawdowns. The 2015 pipeline contraction, the 2018 utility rate-cycle adjustment, the 2022 rate-rising-environment compression: each produced a 20–30% mark-to-market drawdown on the cohort. None changed the underlying compounding. The investor who held through the drawdowns received the math. The investor who sold did not.

## What makes the cohort durable

Three structural features explain why the Canadian infrastructure cohort has produced this record where other ostensibly similar cohorts (US merchant power, certain European utilities, telecom) have not.

**First, regulated rate base.** Roughly 80–99% of cohort EBITDA is regulated or contracted under cost-of-service or take-or-pay structures. The earnings do not depend on the commodity tape, the freight tape, or the consumer tape. They depend on the rate base growing and the authorized return on the rate base holding. Both are functions of the regulatory regime and the operator's discipline in spending rate-base capital that earns its authorized return. The Canadian regulators — the CER, provincial commissions, the US FERC for cross-border assets — have produced a regulatory environment that, with some friction, allows the rate-base model to work.

**Second, asset life.** The pipelines, transmission lines, utility distribution systems, and rail track that the cohort owns are multi-decade assets. The Enbridge Mainline has been moving Canadian crude for sixty years. The Fortis distribution systems have been delivering electricity for longer. The CN main lines that connect Halifax to Prince Rupert have been in service for over a century. The asset life means the capital spent today is amortized over a long enough period that the unit cost stays low; it also means the regulatory accommodation is durable, because the regulator cannot reasonably ask the operator to stop providing a service whose alternative is more expensive.

**Third, capital culture.** The cohort is, in aggregate, conservatively financed, capital-disciplined, and shareholder-aligned in ways most other Canadian sectors are not. The 2015 and 2020 dividend records are public. Almost every cohort name raised the dividend in both windows. Almost no cohort name issued common equity at distressed prices. The culture is not accidental; the operators recruit and promote internally for cultural fit, and the boards on this cohort have been unusually stable.

> A regulated utility is the boring half of the desk. The boring half is the part that pays for the wait.

## Where the cohort breaks down

The cohort is not uniform. Three failure modes are worth naming.

**Regulatory error.** A regulatory environment that turns against the operator can structurally impair the rate-base model. The post-Wexit-rhetoric Alberta of 2019–2020 was a brief stress test on the Canadian pipeline cohort; the regulator did not change but the political backdrop did, and the cohort traded down. The deeper failure mode is a regulator that genuinely reduces authorized ROE meaningfully, which has happened in some US state utility cases. The Canadian cohort has not seen this at scale.

**Capital indiscipline.** TC Energy's pre-2024 capital program, anchored by Coastal GasLink, is the cleanest recent example of a Canadian infrastructure operator overspending on a signature project. The over-run was real, the consequences were a net debt elevation that took years to walk down, and the South Bow spinout in late 2024 was part of the cleanup. The operator is still in the cohort, but the post-2018 record is meaningfully weaker than the pre-2018 record.

**Stranded-asset risk.** A long-life regulated asset can become uneconomic if the underlying demand structurally disappears. The most-discussed risk on this side is Enbridge's liquids Mainline in an aggressive Canadian-oil-demand-decline scenario. The probability of the worst case is, in our read, low. The probability of a meaningful demand erosion over thirty years is non-trivial. The cohort's diversification into US gas distribution (Enbridge's 2023–2024 Dominion utilities acquisition) and renewable rate base is a partial hedge. It is not the same as the original toll-road economics.

## Why the cohort is not bigger

A reasonable question, looking at the small cohort, is why the Canadian infrastructure compounders are not a larger group. The Canadian listed universe contains hundreds of names with adjacent characteristics — regulated utilities of various scale, REITs in the multi-residential and industrial categories, telecoms with substantial regulated assets, agricultural cooperatives with quasi-regulated returns. Why does the desk's compounding work concentrate on roughly half a dozen names?

The answer is in three criteria, each of which eliminates a meaningful share of the listed universe. The first criterion is asset durability. A regulated asset whose underlying technology can be displaced — a coal-fired power utility, a copper-wire telecom, a fossil-fuel pipeline whose feedstock declines over thirty years — does not produce the same compounding profile as an asset whose technology is structurally durable. The Canadian infrastructure cohort holds assets whose displacement risk over thirty years is meaningfully lower than the median of the listed regulated-asset universe. That filter eliminates many of the names a casual reader would expect to qualify.

The second criterion is regulatory durability. The regulator's willingness to grant a fair return over a multi-decade window is not constant across Canadian and US jurisdictions. Certain US state utility commissions have produced authorized ROEs that have ratcheted down meaningfully over the past two decades. Certain Canadian provincial commissions have produced regulatory friction that has impaired the operator's ability to spend rate-base capital cleanly. The cohort on the desk operates in the jurisdictions where the regulatory relationship has been most consistent — primarily the federal level (CER, FERC), the more institutionally stable provincial commissions (Ontario, British Columbia), and the US state commissions that have a track record of fair-return rulings.

The third criterion is capital culture. A regulated asset run by a poorly disciplined capital allocator is, in the long run, no better than a non-regulated asset run by a great one. The cohort on the desk meets a high bar on capital culture — measured by the 2015 and 2020 dividend records, the equity-issuance restraint, the buyback discipline, and the per-share growth profile. The bar excludes a number of names whose underlying assets are excellent but whose capital cultures have, at points, eroded the underlying advantage.

The compounded effect of the three filters is a cohort of roughly half a dozen names. That is not, in our view, a defect of the framework; it is the framework's expression. A research desk that produces a list of seventy-five compounders is a desk that has not done the work. The desk that produces six is the one that has applied the criteria. Six is enough.

## Why the boring half pays for the wait

A research desk that earns its keep over decades does so by allowing the exciting parts of the portfolio to compound at high single digits while the boring parts compound at high single digits without the volatility. The shape of the total-return distribution matters. A 12% compounder with 30% annualized volatility is, in many practical investor situations, a worse outcome than a 9% compounder with 10% volatility, even though the long-run point estimate of the first is higher.

The Canadian infrastructure cohort is the low-volatility part of the desk. We do not own it for the headline return; we own it because the lower variance allows the higher-variance parts of the desk to be held through their drawdowns without forced selling. The compounding that the boring half produces over thirty years is the dividend that makes the impatient half tolerable.

That is, in five words, the case for Canadian infrastructure compounding. The math is unspectacular. The chart is unspectacular. The thirty-year aggregate is exactly the point.
""",
})


# --------------------------------------------------------------------------- #
# emitter
# --------------------------------------------------------------------------- #

def fm_lines(note: dict) -> str:
    """Build YAML-ish frontmatter for the .mdx file."""
    lines = ["---"]
    lines.append(f"title: {note['title']}")
    lines.append(f"slug: {note['slug']}")
    lines.append(f"date: {note['date']}")
    lines.append(f"meta_description: {note['meta_description']}")
    lines.append("excerpt: |")
    for ln in note["excerpt"].splitlines() or [note["excerpt"]]:
        lines.append(f"  {ln}")
    lines.append(f"reading_time: {note['reading_time']}")
    lines.append("tags:")
    for t in note["tags"]:
        lines.append(f"  - {t}")
    if note.get("related"):
        lines.append("related:")
        for s in note["related"]:
            lines.append(f"  - {s}")
    if note.get("operators"):
        lines.append("operators:")
        for s in note["operators"]:
            lines.append(f"  - {s}")
    lines.append("---")
    return "\n".join(lines)


def main() -> int:
    DST.mkdir(parents=True, exist_ok=True)
    for note in NOTES:
        out = DST / f"{note['slug']}.mdx"
        body = note["body"].rstrip() + "\n"
        out.write_text(fm_lines(note) + "\n\n" + body, encoding="utf-8")
        print(f"  wrote {out.relative_to(ROOT)}")
    print(f"_sprint3_seed: wrote {len(NOTES)} notes.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

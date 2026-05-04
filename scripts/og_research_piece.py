#!/usr/bin/env python3
"""Generate per-research-piece OG cards (1200x630).

Usage:
    python3 og_research_piece.py <ticker> <slug>

Configure each piece in the PIECES dict at the bottom; this writes to
/home/user/halvren-capital/og-research-<slug>.png.
"""
from PIL import Image, ImageDraw, ImageFont
from pathlib import Path
import sys

W, H = 1200, 630
ROOT = Path("/home/user/halvren-capital")

BG = (13, 12, 10)
TEXT = (236, 232, 223)
TEXT_MUTED = (138, 135, 128)
TEXT_FAINT = (74, 72, 67)
GOLD = (191, 156, 91)
DIVIDER = (38, 36, 30)
GRID = (24, 22, 18)

F_DIR = "/tmp/fonts"
def font(name, size):
    return ImageFont.truetype(f"{F_DIR}/{name}", size)

f_eyebrow = font("JetBrainsMono-Medium.ttf", 14)
f_mono_sm = font("JetBrainsMono-Regular.ttf", 16)
f_mono_md = font("JetBrainsMono-Medium.ttf", 22)
f_mono_lg = font("JetBrainsMono-Medium.ttf", 26)
f_brand = font("InstrumentSerif-Regular.ttf", 32)
f_h1 = font("InstrumentSerif-Italic.ttf", 60)
f_h1_reg = font("InstrumentSerif-Regular.ttf", 60)
f_ticker_huge = font("InstrumentSerif-Regular.ttf", 130)
f_label = font("JetBrainsMono-Medium.ttf", 13)
f_section = font("JetBrainsMono-Medium.ttf", 13)
f_dek = font("InstrumentSerif-Regular.ttf", 22)


def render(piece: dict):
    img = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(img)

    # Subtle gold radial in top-left
    glow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    gdraw = ImageDraw.Draw(glow)
    for r in range(380, 0, -4):
        a = int((1 - r/380) ** 2 * 22)
        gdraw.ellipse([60-r, 60-r, 60+r, 60+r], fill=(GOLD[0], GOLD[1], GOLD[2], a))
    img.paste(glow, (0, 0), glow)
    d = ImageDraw.Draw(img)

    # Vertical grid
    for x in range(120, W, 80):
        for y in range(60, H-60):
            if y % 6 == 0:
                d.point((x, y), fill=GRID)

    # Top accent line
    d.rectangle([60, 60, 108, 62], fill=GOLD)

    # === TOP ROW ===
    mx, my = 60, 84
    sw = 3; mh = 30
    # H glyph
    d.rectangle([mx, my, mx+sw, my+mh], fill=TEXT)
    d.rectangle([mx+15, my, mx+15+sw, my+mh], fill=TEXT)
    d.rectangle([mx, my+mh//2-1, mx+18, my+mh//2+1], fill=TEXT)
    # Triangle (Halvren mark)
    d.rectangle([mx+27, my, mx+27+sw, my+mh], fill=GOLD)
    d.polygon([(mx+30, my), (mx+45, my+mh//2), (mx+30, my+mh)], fill=GOLD)
    d.text((mx+58, my-2), "Halvren Capital", font=f_brand, fill=TEXT)

    # Top-right pill — "RESEARCH · <SECTOR>"
    pill_text = f"RESEARCH  ·  {piece['sector_pill'].upper()}"
    pill_w = d.textlength(pill_text, font=f_eyebrow)
    ppx, ppy = W - 60 - int(pill_w) - 36, 90
    d.rounded_rectangle(
        [ppx, ppy-6, ppx+int(pill_w)+30, ppy+22],
        radius=18, fill=(20, 19, 14), outline=(40, 38, 32), width=1,
    )
    d.ellipse([ppx+10, ppy+5, ppx+18, ppy+13], fill=GOLD)
    d.text((ppx+24, ppy), pill_text, font=f_eyebrow, fill=TEXT_MUTED)

    # === LEFT: Big ticker + title + dek ===
    # Ticker, oversized
    tk_x, tk_y = 56, 175
    d.text((tk_x, tk_y), piece["ticker"], font=f_ticker_huge, fill=GOLD)

    # Caption right under ticker
    cap_y = tk_y + 142
    d.text((60, cap_y), piece["caption"].upper(), font=f_section, fill=TEXT_FAINT)

    # === RIGHT: Stat panel ===
    rx = 660
    ry = 175

    # Card panel
    card_h = 320
    d.rounded_rectangle(
        [rx, ry, W - 60, ry + card_h],
        radius=10, fill=(20, 19, 14), outline=(40, 38, 32), width=1,
    )

    d.text((rx + 24, ry + 18), "FY 2025  ·  AT A GLANCE", font=f_section, fill=GOLD)

    # Up to 4 stats
    sy = ry + 50
    row_h = (card_h - 70) // max(1, len(piece["stats"]))
    for label, value in piece["stats"][:4]:
        d.text((rx + 24, sy + 4), value, font=f_mono_lg, fill=TEXT)
        d.text((rx + 24, sy + 36), label.upper(), font=f_label, fill=TEXT_MUTED)
        if sy + row_h < ry + card_h - 10:
            d.line([rx + 24, sy + row_h - 6, W - 84, sy + row_h - 6],
                   fill=DIVIDER, width=1)
        sy += row_h

    # === BOTTOM: title row spans the bottom ===
    title_y = 425
    # Title — two lines, with em-color second line
    d.text((60, title_y), piece["title_line1"], font=f_h1_reg, fill=TEXT)
    d.text((60, title_y + 58), piece["title_line2"], font=f_h1, fill=GOLD)

    # === BOTTOM BAR ===
    bot_y = H - 50
    d.rectangle([0, bot_y - 1, W, bot_y], fill=DIVIDER)
    d.text((60, bot_y + 14), piece["footer_left"].upper(),
           font=f_section, fill=TEXT_FAINT)
    url = piece["url"]
    uw = d.textlength(url, font=f_mono_sm)
    d.text((W - 60 - int(uw), bot_y + 12), url, font=f_mono_sm, fill=GOLD)

    out = ROOT / f"og-research-{piece['slug']}.png"
    img.save(out, "PNG", optimize=True)
    print(f"OK: {out.name}  ({out.stat().st_size:,} bytes)")


# === Per-piece configuration ===
PIECES = {
    "eog": {
        "slug": "eog",
        "ticker": "EOG",
        "sector_pill": "Oil & Gas · First U.S.",
        "caption": "EOG Resources  ·  NYSE: EOG  ·  May 2026",
        "title_line1": "The shale producer",
        "title_line2": "that doesn't act like one.",
        "stats": [
            ("Production", "1,090 MBOE/d"),
            ("Adj. EBITDA", "US$11.4B"),
            ("FCF", "US$5.4B"),
            ("Buybacks", "US$2.3B"),
        ],
        "footer_left": "FY 2025 PRINT  ·  PREMIUM DRILLING  ·  PROPRIETARY READ",
        "url": "halvrencapital.com/research/eog-resources",
    },
    "cco": {
        "slug": "cco",
        "ticker": "CCO",
        "sector_pill": "Uranium · Saskatchewan",
        "caption": "Cameco  ·  TSX:CCO / NYSE:CCJ  ·  Apr 2026",
        "title_line1": "A mine with a cost structure,",
        "title_line2": "read honestly.",
        "stats": [
            ("FY Revenue", "C$3.5B"),
            ("U₃O₈ output", "20.6 Mlbs"),
            ("Westinghouse", "49% stake"),
            ("Net debt", "negative"),
        ],
        "footer_left": "FY 2025 PRINT  ·  CONTRACT BOOK  ·  PROPRIETARY READ",
        "url": "halvrencapital.com/research/cameco-cco",
    },
    "cnq": {
        "slug": "cnq",
        "ticker": "CNQ",
        "sector_pill": "Oil & Gas · Owner-operator",
        "caption": "Canadian Natural  ·  TSX/NYSE: CNQ  ·  Apr 2026",
        "title_line1": "The owner-operator",
        "title_line2": "arithmetic.",
        "stats": [
            ("Production", "1,571 MBOE/d"),
            ("Adj. funds flow", "C$15.5B"),
            ("Shareholder returns", "C$9.0B"),
            ("Dividend streak", "26 years"),
        ],
        "footer_left": "FY 2025 PRINT  ·  LOW-DECLINE  ·  PROPRIETARY READ",
        "url": "halvrencapital.com/research/canadian-natural-cnq",
    },
    "ag": {
        "slug": "ag",
        "ticker": "AG",
        "sector_pill": "Silver · Mexico",
        "caption": "First Majestic Silver  ·  NYSE/TSX: AG  ·  Apr 2026",
        "title_line1": "The honest",
        "title_line2": "skeptic's read.",
        "stats": [
            ("Revenue", "US$1,257M"),
            ("AISC / AgEq oz", "US$21.17"),
            ("Realized price", "US$38–43/oz"),
            ("Status", "Not yet"),
        ],
        "footer_left": "FY 2025 PRINT  ·  JURISDICTION OVERHANG  ·  PROPRIETARY READ",
        "url": "halvrencapital.com/research/first-majestic-ag",
    },
    "ntr": {
        "slug": "ntr",
        "ticker": "NTR",
        "sector_pill": "Fertilizers · Saskatchewan",
        "caption": "Nutrien  ·  NYSE/TSX: NTR  ·  Apr 2026",
        "title_line1": "The boring oligopoly",
        "title_line2": "Canada built.",
        "stats": [
            ("Sales", "US$26.9B"),
            ("Adj. EBITDA", "US$6.05B"),
            ("Buybacks", "US$551M"),
            ("Potash position", "1st quartile"),
        ],
        "footer_left": "FY 2025 PRINT  ·  RETAIL READ  ·  PROPRIETARY READ",
        "url": "halvrencapital.com/research/nutrien-ntr",
    },
    "enb": {
        "slug": "enb",
        "ticker": "ENB",
        "sector_pill": "Infrastructure · Mainline",
        "caption": "Enbridge  ·  TSX/NYSE: ENB  ·  Apr 2026",
        "title_line1": "The toll-road,",
        "title_line2": "read honestly.",
        "stats": [
            ("Adj. EBITDA", "C$18.2B"),
            ("Backlog secured", "~C$28B"),
            ("Mainline apport.", "6%"),
            ("Leverage", "4.7x → 4.6x"),
        ],
        "footer_left": "FY 2025 PRINT  ·  TOLL-ROAD  ·  PROPRIETARY READ",
        "url": "halvrencapital.com/research/enbridge-enb",
    },
}


if __name__ == "__main__":
    if len(sys.argv) > 1:
        slug = sys.argv[1]
        if slug == "all":
            for p in PIECES.values():
                render(p)
        elif slug in PIECES:
            render(PIECES[slug])
        else:
            sys.exit(f"unknown slug: {slug}; known: {', '.join(PIECES)}")
    else:
        # Default: just EOG
        render(PIECES["eog"])

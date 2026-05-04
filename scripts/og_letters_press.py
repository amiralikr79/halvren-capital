#!/usr/bin/env python3
"""Generate OG cards for /press, /letters archive, and individual letters.

Usage:
    python3 scripts/og_letters_press.py [press|letters|q1|three-questions|all]
"""
from PIL import Image, ImageDraw, ImageFont
from pathlib import Path
import sys

W, H = 1200, 630
ROOT = Path(__file__).resolve().parent.parent

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
f_h1_big = font("InstrumentSerif-Italic.ttf", 84)
f_h1_reg = font("InstrumentSerif-Regular.ttf", 84)
f_h1 = font("InstrumentSerif-Italic.ttf", 60)
f_h1r = font("InstrumentSerif-Regular.ttf", 60)
f_section = font("JetBrainsMono-Medium.ttf", 13)
f_label = font("JetBrainsMono-Medium.ttf", 13)


def _frame(d, top_pill_text, brand="Halvren Capital"):
    # Subtle gold radial top-left
    glow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    gd = ImageDraw.Draw(glow)
    for r in range(380, 0, -4):
        a = int((1 - r/380) ** 2 * 22)
        gd.ellipse([60-r, 60-r, 60+r, 60+r], fill=(GOLD[0], GOLD[1], GOLD[2], a))
    return glow

def _draw_brand(d):
    d.rectangle([60, 60, 108, 62], fill=GOLD)
    mx, my = 60, 84
    sw = 3; mh = 30
    d.rectangle([mx, my, mx+sw, my+mh], fill=TEXT)
    d.rectangle([mx+15, my, mx+15+sw, my+mh], fill=TEXT)
    d.rectangle([mx, my+mh//2-1, mx+18, my+mh//2+1], fill=TEXT)
    d.rectangle([mx+27, my, mx+27+sw, my+mh], fill=GOLD)
    d.polygon([(mx+30, my), (mx+45, my+mh//2), (mx+30, my+mh)], fill=GOLD)
    d.text((mx+58, my-2), "Halvren Capital", font=f_brand, fill=TEXT)

def _draw_pill(d, text):
    pill_w = d.textlength(text, font=f_eyebrow)
    ppx, ppy = W - 60 - int(pill_w) - 36, 90
    d.rounded_rectangle(
        [ppx, ppy-6, ppx+int(pill_w)+30, ppy+22],
        radius=18, fill=(20, 19, 14), outline=(40, 38, 32), width=1,
    )
    d.ellipse([ppx+10, ppy+5, ppx+18, ppy+13], fill=GOLD)
    d.text((ppx+24, ppy), text, font=f_eyebrow, fill=TEXT_MUTED)

def _draw_grid(d):
    for x in range(120, W, 80):
        for y in range(60, H-60):
            if y % 6 == 0:
                d.point((x, y), fill=GRID)

def _draw_footer(d, left, url):
    d.rectangle([0, H-51, W, H-50], fill=DIVIDER)
    d.text((60, H-36), left.upper(), font=f_section, fill=TEXT_FAINT)
    uw = d.textlength(url, font=f_mono_sm)
    d.text((W - 60 - int(uw), H-38), url, font=f_mono_sm, fill=GOLD)


def render_press():
    img = Image.new("RGB", (W, H), BG)
    img.paste(_frame(None, None), (0,0), _frame(None,None))
    d = ImageDraw.Draw(img)
    _draw_grid(d)
    _draw_brand(d)
    _draw_pill(d, "PRESS KIT  ·  ONE-PAGER")

    # Eyebrow + H1 — "Halvren Capital, in one page."
    d.text((60, 200), "FOR JOURNALISTS  ·  ALLOCATORS  ·  COUNTERPARTIES", font=f_section, fill=GOLD)
    d.text((54, 235), "Halvren Capital,", font=f_h1_reg, fill=TEXT)
    d.text((54, 335), "in ", font=f_h1_reg, fill=TEXT)
    iw = d.textlength("in ", font=f_h1_reg)
    d.text((54 + iw, 335), "one page.", font=f_h1_big, fill=GOLD)

    # Right side: 3 quick stats — kept tight so it doesn't overlap the sub-text
    rx = 700; ry = 200
    rows = [
        ("17.1%", "ANNUALIZED · SINCE 2019"),
        ("7 / 7", "YEARS POSITIVE · NO DOWN YEAR"),
        ("31",    "OPERATORS ON COVERAGE"),
    ]
    card_h = 240
    d.rounded_rectangle([rx, ry, W-60, ry+card_h], radius=10,
                        fill=(20,19,14), outline=(40,38,32), width=1)
    d.text((rx+24, ry+18), "AT A GLANCE", font=f_section, fill=GOLD)
    sy = ry + 50
    row_h = (card_h - 65) // len(rows)
    for val, lbl in rows:
        d.text((rx+24, sy+4), val, font=f_mono_lg, fill=TEXT)
        d.text((rx+24, sy+36), lbl, font=f_label, fill=TEXT_MUTED)
        if sy + row_h < ry + card_h - 10:
            d.line([rx+24, sy+row_h-6, W-84, sy+row_h-6], fill=DIVIDER, width=1)
        sy += row_h

    # Sub-line under H1
    d.text((60, 460), "Founder bio  ·  performance anchor  ·  coverage  ·  press contact",
           font=f_mono_md, fill=TEXT_MUTED)
    d.text((60, 495), "Print → Save as PDF for the offline factsheet.",
           font=f_mono_md, fill=TEXT_MUTED)

    _draw_footer(d, "AMIRALI KARIMI  ·  VANCOUVER, BC  ·  EST. 2025",
                 "halvrencapital.com/press")
    out = ROOT / "og-press.png"
    img.save(out, "PNG", optimize=True)
    print(f"OK: {out.name}  ({out.stat().st_size:,} bytes)")


def render_letters_archive():
    img = Image.new("RGB", (W, H), BG)
    img.paste(_frame(None, None), (0,0), _frame(None,None))
    d = ImageDraw.Draw(img)
    _draw_grid(d)
    _draw_brand(d)
    _draw_pill(d, "QUARTERLY LETTERS  ·  EST. 2026")

    d.text((60, 200), "FOUR LETTERS A YEAR  ·  PUBLIC ARCHIVE", font=f_section, fill=GOLD)
    d.text((54, 235), "What changed", font=f_h1_reg, fill=TEXT)
    d.text((54, 320), "our ", font=f_h1_reg, fill=TEXT)
    iw = d.textlength("our ", font=f_h1_reg)
    d.text((54 + iw, 320), "minds.", font=f_h1_big, fill=GOLD)

    d.text((60, 440), "What we wrote, what we passed on, what's on the desk.",
           font=f_mono_md, fill=TEXT_MUTED)
    d.text((60, 475), "Same voice as the Substack. Free to read.",
           font=f_mono_md, fill=TEXT_MUTED)

    # Right: small index of published
    rx = 760; ry = 200
    d.rounded_rectangle([rx, ry, W-60, ry+260], radius=10,
                        fill=(20,19,14), outline=(40,38,32), width=1)
    d.text((rx+24, ry+18), "PUBLISHED", font=f_section, fill=GOLD)
    rows = [
        ("Q1 2026", "Earnings season · 4 names"),
        ("FIELD",   "Three questions · 2025"),
    ]
    sy = ry + 50
    row_h = 90
    for val, lbl in rows:
        d.text((rx+24, sy+4), val, font=f_mono_lg, fill=GOLD)
        d.text((rx+24, sy+36), lbl, font=f_label, fill=TEXT_MUTED)
        if sy + row_h < ry + 260 - 10:
            d.line([rx+24, sy+row_h-6, W-84, sy+row_h-6], fill=DIVIDER, width=1)
        sy += row_h

    _draw_footer(d, "QUARTERLY  ·  HALVREN CAPITAL  ·  PROPRIETARY READ",
                 "halvrencapital.com/letters")
    out = ROOT / "og-letters.png"
    img.save(out, "PNG", optimize=True)
    print(f"OK: {out.name}  ({out.stat().st_size:,} bytes)")


def render_letter_q1():
    img = Image.new("RGB", (W, H), BG)
    img.paste(_frame(None, None), (0,0), _frame(None,None))
    d = ImageDraw.Draw(img)
    _draw_grid(d)
    _draw_brand(d)
    _draw_pill(d, "Q1 2026 LETTER  ·  APR 2026")

    d.text((60, 200), "QUARTERLY LETTER  ·  EARNINGS-SEASON QUARTER", font=f_section, fill=GOLD)
    d.text((54, 235), "The earnings", font=f_h1_reg, fill=TEXT)
    d.text((54, 335), "season ", font=f_h1_reg, fill=TEXT)
    iw = d.textlength("season ", font=f_h1_reg)
    d.text((54 + iw, 335), "quarter.", font=f_h1_big, fill=GOLD)

    d.text((60, 460), "CCO · CNQ · AG · NTR — what FY 2025 actually said.",
           font=f_mono_md, fill=TEXT_MUTED)
    d.text((60, 495), "What changed our minds, what we declined.",
           font=f_mono_md, fill=TEXT_MUTED)

    # Right ticker chips
    rx = 770; ry = 200
    d.rounded_rectangle([rx, ry, W-60, ry+260], radius=10,
                        fill=(20,19,14), outline=(40,38,32), width=1)
    d.text((rx+24, ry+18), "FOUR NAMES  ·  ONE QUARTER", font=f_section, fill=GOLD)
    rows = [
        ("CCO", "Cameco · negative net debt"),
        ("CNQ", "Canadian Natural · 26 yr div"),
        ("AG",  "First Majestic · not yet"),
        ("NTR", "Nutrien · partial clarity"),
    ]
    sy = ry + 50
    row_h = (260 - 65) // len(rows)
    for tk, lbl in rows:
        d.text((rx+24, sy+4), tk, font=f_mono_lg, fill=GOLD)
        d.text((rx+96, sy+10), lbl, font=f_label, fill=TEXT_MUTED)
        if sy + row_h < ry + 260 - 10:
            d.line([rx+24, sy+row_h-6, W-84, sy+row_h-6], fill=DIVIDER, width=1)
        sy += row_h

    _draw_footer(d, "AMIRALI KARIMI  ·  APRIL 2026  ·  ~10 MIN READ",
                 "halvrencapital.com/letters/q1-2026")
    out = ROOT / "og-letter-q1-2026.png"
    img.save(out, "PNG", optimize=True)
    print(f"OK: {out.name}  ({out.stat().st_size:,} bytes)")


def render_letter_three_questions():
    img = Image.new("RGB", (W, H), BG)
    img.paste(_frame(None, None), (0,0), _frame(None,None))
    d = ImageDraw.Draw(img)
    _draw_grid(d)
    _draw_brand(d)
    _draw_pill(d, "FIELD NOTE  ·  DEC 2025")

    d.text((60, 200), "FIELD NOTE  ·  YEAR-END 2025", font=f_section, fill=GOLD)
    d.text((54, 235), "Three questions", font=f_h1_reg, fill=TEXT)
    d.text((54, 335), "for ", font=f_h1_reg, fill=TEXT)
    iw = d.textlength("for ", font=f_h1_reg)
    d.text((54 + iw, 335), "Canada.", font=f_h1_big, fill=GOLD)

    d.text((60, 460), "Pipeline takeaway, AECO basis, Saskatchewan capital.",
           font=f_mono_md, fill=TEXT_MUTED)
    d.text((60, 495), "What honest 2026 underwriting demands answers to.",
           font=f_mono_md, fill=TEXT_MUTED)

    # Right: the three questions
    rx = 770; ry = 200
    d.rounded_rectangle([rx, ry, W-60, ry+260], radius=10,
                        fill=(20,19,14), outline=(40,38,32), width=1)
    d.text((rx+24, ry+18), "THREE QUESTIONS", font=f_section, fill=GOLD)
    rows = [
        ("01", "Pipeline takeaway"),
        ("02", "AECO basis & LNG"),
        ("03", "Capital allocation"),
    ]
    sy = ry + 50
    row_h = (260 - 65) // len(rows)
    for n, lbl in rows:
        d.text((rx+24, sy+4), n, font=f_mono_lg, fill=GOLD)
        d.text((rx+96, sy+10), lbl, font=f_label, fill=TEXT_MUTED)
        if sy + row_h < ry + 260 - 10:
            d.line([rx+24, sy+row_h-6, W-84, sy+row_h-6], fill=DIVIDER, width=1)
        sy += row_h

    _draw_footer(d, "AMIRALI KARIMI  ·  DECEMBER 2025  ·  FIELD NOTE",
                 "halvrencapital.com/letters/three-questions-2025")
    out = ROOT / "og-letter-three-questions-2025.png"
    img.save(out, "PNG", optimize=True)
    print(f"OK: {out.name}  ({out.stat().st_size:,} bytes)")


if __name__ == "__main__":
    arg = sys.argv[1] if len(sys.argv) > 1 else "all"
    if arg in ("press", "all"):           render_press()
    if arg in ("letters", "all"):         render_letters_archive()
    if arg in ("q1", "all"):              render_letter_q1()
    if arg in ("three-questions", "all"): render_letter_three_questions()

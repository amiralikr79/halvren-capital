#!/usr/bin/env python3
"""Generate /og-research.png — Halvren Research archive share card 1200x630."""
from PIL import Image, ImageDraw, ImageFont
from pathlib import Path

W, H = 1200, 630
ROOT = Path("/home/user/halvren-capital")
OUT = ROOT / "og-research.png"

BG = (13, 12, 10)
TEXT = (236, 232, 223)
TEXT_MUTED = (138, 135, 128)
TEXT_FAINT = (74, 72, 67)
GOLD = (191, 156, 91)
GREEN = (34, 197, 94)
DIVIDER = (38, 36, 30)
GRID = (24, 22, 18)

F_DIR = "/tmp/fonts"
def font(name, size):
    return ImageFont.truetype(f"{F_DIR}/{name}", size)

f_eyebrow = font("JetBrainsMono-Medium.ttf", 14)
f_mono_sm = font("JetBrainsMono-Regular.ttf", 16)
f_mono_md = font("JetBrainsMono-Medium.ttf", 22)
f_mono_lg = font("JetBrainsMono-Medium.ttf", 32)
f_brand = font("InstrumentSerif-Regular.ttf", 32)
f_h1 = font("InstrumentSerif-Italic.ttf", 70)
f_h1_reg = font("InstrumentSerif-Regular.ttf", 70)
f_ticker = font("JetBrainsMono-Medium.ttf", 28)
f_label = font("JetBrainsMono-Medium.ttf", 13)
f_section = font("JetBrainsMono-Medium.ttf", 13)
f_dek = font("InstrumentSerif-Regular.ttf", 18)

img = Image.new("RGB", (W, H), BG)
d = ImageDraw.Draw(img)

# Subtle gold radial
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
d.rectangle([mx, my, mx+sw, my+mh], fill=TEXT)
d.rectangle([mx+15, my, mx+15+sw, my+mh], fill=TEXT)
d.rectangle([mx, my+mh//2-1, mx+18, my+mh//2+1], fill=TEXT)
d.rectangle([mx+27, my, mx+27+sw, my+mh], fill=GOLD)
d.polygon([(mx+30, my), (mx+45, my+mh//2), (mx+30, my+mh)], fill=GOLD)
d.text((mx+58, my-2), "Halvren Capital", font=f_brand, fill=TEXT)

# Top-right pill
pill_text = "RESEARCH ARCHIVE  ·  OPERATOR-LED"
pill_w = d.textlength(pill_text, font=f_eyebrow)
ppx, ppy = W - 60 - int(pill_w) - 36, 90
d.rounded_rectangle([ppx, ppy-6, ppx+int(pill_w)+30, ppy+22], radius=18, fill=(20, 19, 14), outline=(40, 38, 32), width=1)
d.ellipse([ppx+10, ppy+5, ppx+18, ppy+13], fill=GOLD)
d.text((ppx+24, ppy), pill_text, font=f_eyebrow, fill=TEXT_MUTED)

# === LEFT: headline ===
d.text((60, 200), "FULL WRITEUPS  ·  CANADIAN & U.S.", font=f_section, fill=GOLD)

# H1 — "Six names." "Read deeply."
d.text((54, 234), "Six names.", font=f_h1_reg, fill=TEXT)
d.text((54, 312), "Read ", font=f_h1_reg, fill=TEXT)
hw = d.textlength("Read ", font=f_h1_reg)
d.text((54 + hw, 312), "deeply.", font=f_h1, fill=GOLD)

# Sub copy
d.text((60, 425), "FY 2025 data, business analysis, and the Halvren", font=f_mono_md, fill=TEXT_MUTED)
d.text((60, 458), "Checklist applied at the end of every piece.", font=f_mono_md, fill=TEXT_MUTED)

# === RIGHT: name list ===
rx = 730

# Card panel
card_top = ry = 200
card_h = 320
d.rounded_rectangle([rx, ry, W - 60, ry + card_h], radius=10, fill=(20, 19, 14), outline=(40, 38, 32), width=1)

d.text((rx + 24, ry + 18), "PUBLISHED", font=f_section, fill=GOLD)

# 6 names listed with sector
names = [
    ("CCO", "Cameco", "Uranium"),
    ("CNQ", "Canadian Natural", "Oil & Gas"),
    ("AG",  "First Majestic", "Silver"),
    ("NTR", "Nutrien", "Fertilizers"),
    ("ENB", "Enbridge", "Infrastructure"),
    ("EOG", "EOG Resources", "U.S. Oil & Gas"),
]
sy = ry + 48
row_h = (card_h - 65) // len(names)
for tkr, name, sector in names:
    d.text((rx + 24, sy), tkr, font=f_ticker, fill=GOLD)
    d.text((rx + 110, sy + 4), name, font=f_mono_md, fill=TEXT)
    sw_ = d.textlength(sector.upper(), font=f_label)
    d.text((W - 84 - int(sw_), sy + 12), sector.upper(), font=f_label, fill=TEXT_FAINT)
    if sy + row_h < ry + card_h - 10:
        d.line([rx + 24, sy + row_h - 6, W - 84, sy + row_h - 6], fill=DIVIDER, width=1)
    sy += row_h

# Below card: U.S. monitoring
ticky = ry + card_h + 22
d.text((rx, ticky), "U.S. ON THE WATCH", font=f_section, fill=TEXT_FAINT)
d.text((rx, ticky + 24), "COP  ·  CF  ·  NEM  ·  WMB  ·  KMI  ·  NEE", font=f_mono_md, fill=TEXT_MUTED)

# === BOTTOM BAR ===
bot_y = H - 50
d.rectangle([0, bot_y - 1, W, bot_y], fill=DIVIDER)
d.text((60, bot_y + 14), "OPERATOR-LED  ·  BALANCE-SHEET-DRIVEN  ·  FREE  ·  REVIEWED QUARTERLY", font=f_section, fill=TEXT_FAINT)
url = "halvrencapital.com/research"
uw = d.textlength(url, font=f_mono_sm)
d.text((W - 60 - int(uw), bot_y + 12), url, font=f_mono_sm, fill=GOLD)

img.save(OUT, "PNG", optimize=True)
print(f"OK: {OUT}  ({OUT.stat().st_size:,} bytes)")

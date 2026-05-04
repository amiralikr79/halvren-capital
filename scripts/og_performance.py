#!/usr/bin/env python3
"""Generate /og-performance.png — Halvren performance share card 1200x630."""
from PIL import Image, ImageDraw, ImageFont
from pathlib import Path

W, H = 1200, 630
ROOT = Path("/home/user/halvren-capital")
OUT = ROOT / "og-performance.png"

# Halvren brand palette (dark)
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
f_mono_lg = font("JetBrainsMono-Medium.ttf", 28)
f_brand = font("InstrumentSerif-Regular.ttf", 32)
f_huge_num = font("JetBrainsMono-Medium.ttf", 240)
f_pct = font("JetBrainsMono-Medium.ttf", 160)
f_section = font("JetBrainsMono-Medium.ttf", 13)
f_section_lg = font("JetBrainsMono-Medium.ttf", 14)

img = Image.new("RGB", (W, H), BG)
d = ImageDraw.Draw(img)

# Subtle gold-tinted radial glow top-left
glow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
gdraw = ImageDraw.Draw(glow)
for r in range(380, 0, -4):
    a = int((1 - r/380) ** 2 * 22)
    gdraw.ellipse([60-r, 60-r, 60+r, 60+r], fill=(GOLD[0], GOLD[1], GOLD[2], a))
img.paste(glow, (0, 0), glow)
d = ImageDraw.Draw(img)

# Subtle vertical grid (Palantir density)
for x in range(120, W, 80):
    for y in range(60, H-60):
        if y % 6 == 0:
            d.point((x, y), fill=GRID)

# Top accent line
d.rectangle([60, 60, 108, 62], fill=GOLD)

# === TOP ROW ===
# Halvren H|> mark — properly drawn
mx, my = 60, 84
sw = 3   # stroke width
mh = 30  # mark height
# H: two verticals + horizontal
d.rectangle([mx, my, mx+sw, my+mh], fill=TEXT)
d.rectangle([mx+15, my, mx+15+sw, my+mh], fill=TEXT)
d.rectangle([mx, my+mh//2-1, mx+18, my+mh//2+1], fill=TEXT)
# |>: vertical + triangle
d.rectangle([mx+27, my, mx+27+sw, my+mh], fill=GOLD)
# Right-pointing triangle
tri = [(mx+30, my), (mx+45, my+mh//2), (mx+30, my+mh)]
d.polygon(tri, fill=GOLD)

# Brand wordmark
d.text((mx+58, my-2), "Halvren Capital", font=f_brand, fill=TEXT)

# Top-right pill
pill_text = "PERFORMANCE  ·  THE BOOK  ·  SINCE 2019"
pill_w = d.textlength(pill_text, font=f_eyebrow)
ppx, ppy = W - 60 - int(pill_w) - 36, 90
d.rounded_rectangle([ppx, ppy-6, ppx+int(pill_w)+30, ppy+22], radius=18, fill=(20, 19, 14), outline=(40, 38, 32), width=1)
d.ellipse([ppx+10, ppy+5, ppx+18, ppy+13], fill=GREEN)
d.text((ppx+24, ppy), pill_text, font=f_eyebrow, fill=TEXT_MUTED)

# === LEFT SIDE: Headline number ===
# Section caption
d.text((60, 200), "ANNUALIZED  ·  NET OF FEES & COSTS", font=f_section_lg, fill=GOLD)

# 17.1% — fits in left half (max width ~600px before vertical divider at 720)
# 17.1 rendered as one string for tight kerning
num_text = "17.1"
nx = 56
ny = 220
# Draw the digits in TEXT color
d.text((nx, ny), num_text, font=f_huge_num, fill=TEXT)
nw = d.textlength(num_text, font=f_huge_num)
# % in gold, smaller, positioned right after with tight gap
pct_x = nx + int(nw) + 4
pct_y = ny + 36
d.text((pct_x, pct_y), "%", font=f_pct, fill=GOLD)

# Below the number: meta line
d.text((60, 480), "seven years  ·  every year positive  ·  IBKR-custodied", font=f_mono_md, fill=TEXT_MUTED)

# Validation pills below number
val_y = 528
val_x = 60
pills = [
    ("IBKR CUSTODIAN", GOLD),
    ("TIME-WEIGHTED", TEXT_MUTED),
    ("NO LEVERAGE", TEXT_MUTED),
]
for txt, col in pills:
    tw = d.textlength(txt, font=f_section)
    d.rounded_rectangle([val_x, val_y, val_x + int(tw) + 24, val_y + 26], radius=14,
                        outline=(50, 48, 42), width=1, fill=None)
    if col == GOLD:
        d.ellipse([val_x + 10, val_y + 9, val_x + 18, val_y + 17], fill=GOLD)
        d.text((val_x + 24, val_y + 5), txt, font=f_section, fill=GOLD)
    else:
        d.text((val_x + 12, val_y + 5), txt, font=f_section, fill=col)
    val_x += int(tw) + 38

# === Vertical divider ===
d.rectangle([720, 200, 721, 470], fill=DIVIDER)

# === RIGHT SIDE: comparison ===
rx = 750
ry = 200
d.text((rx, ry), "VS  ·  BENCHMARK  ·  NET", font=f_section_lg, fill=GOLD)

# Header divider
d.line([rx, ry + 30, W - 60, ry + 30], fill=DIVIDER, width=1)

# Row 1: TSX
y = ry + 55
d.text((rx, y), "TSX Composite TR", font=f_mono_sm, fill=TEXT_MUTED)
val = "+13.0%"
vw = d.textlength(val, font=f_mono_lg)
d.text((W - 60 - int(vw), y - 4), val, font=f_mono_lg, fill=TEXT)
d.line([rx, y + 38, W - 60, y + 38], fill=DIVIDER, width=1)

# Row 2: Excess vs TSX
y = ry + 105
d.text((rx, y), "Excess  ·  vs TSX", font=f_mono_sm, fill=TEXT_MUTED)
val = "+4.1 pp"
vw = d.textlength(val, font=f_mono_lg)
d.text((W - 60 - int(vw), y - 4), val, font=f_mono_lg, fill=GOLD)
d.line([rx, y + 38, W - 60, y + 38], fill=DIVIDER, width=1)

# Row 3: S&P 500
y = ry + 155
d.text((rx, y), "S&P 500 TR", font=f_mono_sm, fill=TEXT_MUTED)
val = "+16.9%"
vw = d.textlength(val, font=f_mono_lg)
d.text((W - 60 - int(vw), y - 4), val, font=f_mono_lg, fill=TEXT)
d.line([rx, y + 38, W - 60, y + 38], fill=DIVIDER, width=1)

# Row 4: Excess vs S&P
y = ry + 205
d.text((rx, y), "Excess  ·  vs S&P 500", font=f_mono_sm, fill=TEXT_MUTED)
val = "+0.2 pp"
vw = d.textlength(val, font=f_mono_lg)
d.text((W - 60 - int(vw), y - 4), val, font=f_mono_lg, fill=GOLD)

# Cumulative emphasis
y = ry + 248
d.text((rx, y), "Cumulative  ·  7 yrs", font=f_mono_sm, fill=TEXT_MUTED)
val = "+202%"
vw = d.textlength(val, font=f_mono_lg)
d.text((W - 60 - int(vw), y - 4), val, font=f_mono_lg, fill=GOLD)

# === BOTTOM BAR ===
bot_y = H - 50
d.rectangle([0, bot_y - 1, W, bot_y], fill=DIVIDER)
d.text((60, bot_y + 14), "PROPRIETARY EQUITY BOOK  ·  CUSTODIED AT INTERACTIVE BROKERS  ·  CANADIAN & U.S.", font=f_section, fill=TEXT_FAINT)
url = "halvrencapital.com/performance"
uw = d.textlength(url, font=f_mono_sm)
d.text((W - 60 - int(uw), bot_y + 12), url, font=f_mono_sm, fill=GOLD)

img.save(OUT, "PNG", optimize=True)
print(f"OK: {OUT}  ({OUT.stat().st_size:,} bytes)")

#!/usr/bin/env python3
"""Generate /og-digest.png — Halvren Digest share card 1200x630."""
from PIL import Image, ImageDraw, ImageFont
from pathlib import Path

W, H = 1200, 630
ROOT = Path("/home/user/halvren-capital")
OUT = ROOT / "og-digest.png"

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
f_h1 = font("InstrumentSerif-Italic.ttf", 80)
f_h1_reg = font("InstrumentSerif-Regular.ttf", 80)
f_huge_num = font("JetBrainsMono-Medium.ttf", 200)
f_label = font("JetBrainsMono-Medium.ttf", 13)
f_section = font("JetBrainsMono-Medium.ttf", 13)

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

# Top-right pill — LIVE INGEST
pill_text = "LIVE INGEST  ·  THE DIGEST  ·  WEEKLY"
pill_w = d.textlength(pill_text, font=f_eyebrow)
ppx, ppy = W - 60 - int(pill_w) - 36, 90
d.rounded_rectangle([ppx, ppy-6, ppx+int(pill_w)+30, ppy+22], radius=18, fill=(20, 19, 14), outline=(40, 38, 32), width=1)
d.ellipse([ppx+10, ppy+5, ppx+18, ppy+13], fill=GREEN)
d.text((ppx+24, ppy), pill_text, font=f_eyebrow, fill=TEXT_MUTED)

# === LEFT: headline ===
d.text((60, 200), "WHAT THE DESK IS READING  ·  THIS WEEK", font=f_section, fill=GOLD)

# H1 — "Machine breadth," "Human read."
d.text((54, 235), "Machine breadth.", font=f_h1_reg, fill=TEXT)
d.text((54, 320), "Human ", font=f_h1_reg, fill=TEXT)
hw = d.textlength("Human ", font=f_h1_reg)
d.text((54 + hw, 320), "read.", font=f_h1, fill=GOLD)

# Sub copy
d.text((60, 425), "An AI-augmented read of every Canadian and U.S. operator", font=f_mono_md, fill=TEXT_MUTED)
d.text((60, 458), "earnings call on the Halvren coverage list.", font=f_mono_md, fill=TEXT_MUTED)

# === RIGHT: live data tile ===
rx = 730
ry = 200

# Card panel
d.rounded_rectangle([rx, ry, W - 60, ry + 280], radius=10, fill=(20, 19, 14), outline=(40, 38, 32), width=1)

d.text((rx + 24, ry + 18), "THIS WEEK", font=f_section, fill=GOLD)

# Big stat
def stat(y, num, label, num_color=TEXT):
    d.text((rx + 24, y), num, font=f_mono_lg, fill=num_color)
    d.text((rx + 24, y + 38), label, font=f_label, fill=TEXT_FAINT)

# 4 stats stacked
sy = ry + 50
d.text((rx + 24, sy), "142", font=f_mono_lg, fill=TEXT)
d.text((rx + 100, sy + 8), "FILINGS INGESTED", font=f_label, fill=TEXT_MUTED)
d.line([rx + 24, sy + 38, W - 84, sy + 38], fill=DIVIDER, width=1)

sy += 50
d.text((rx + 24, sy), "8", font=f_mono_lg, fill=TEXT)
d.text((rx + 100, sy + 8), "EARNINGS CALLS", font=f_label, fill=TEXT_MUTED)
d.line([rx + 24, sy + 38, W - 84, sy + 38], fill=DIVIDER, width=1)

sy += 50
d.text((rx + 24, sy), "11", font=f_mono_lg, fill=GOLD)
d.text((rx + 100, sy + 8), "MODEL FLAGS", font=f_label, fill=TEXT_MUTED)
d.line([rx + 24, sy + 38, W - 84, sy + 38], fill=DIVIDER, width=1)

sy += 50
d.text((rx + 24, sy), "2", font=f_mono_lg, fill=GOLD)
d.text((rx + 100, sy + 8), "PROMOTED TO DESK", font=f_label, fill=TEXT_MUTED)

# Below card: tickers being read
ticky = ry + 310
d.text((rx, ticky), "READING NOW", font=f_section, fill=TEXT_FAINT)
d.text((rx, ticky + 22), "CNQ  ·  ENB  ·  SU  ·  CCO  ·  TOU  ·  NTR  ·  EOG  ·  AG", font=f_mono_md, fill=TEXT)

# === BOTTOM BAR ===
bot_y = H - 50
d.rectangle([0, bot_y - 1, W, bot_y], fill=DIVIDER)
d.text((60, bot_y + 14), "SEDAR+  ·  SEC EDGAR  ·  100% PUBLIC FILINGS  ·  HUMAN-REVIEWED", font=f_section, fill=TEXT_FAINT)
url = "halvrencapital.com/digest"
uw = d.textlength(url, font=f_mono_sm)
d.text((W - 60 - int(uw), bot_y + 12), url, font=f_mono_sm, fill=GOLD)

img.save(OUT, "PNG", optimize=True)
print(f"OK: {OUT}  ({OUT.stat().st_size:,} bytes)")

"""Draws the social card shown when a page is shared on Discord, Reddit or a social network.

    python scripts/figures/social/build.py

One image for the whole site, in the site's colours: the range grid, the wordmark, the tagline and an
accent rule. Written to docs/assets/images/social-card.png at 1200x630, the size those services crop
to. Rerun it after changing the wordmark or the tagline.
"""
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[3]
OUT = ROOT / "docs" / "assets" / "images" / "social-card.png"
W, H = 1200, 630

# The site's dark scheme: night chrome, light ink, the coral accent and the faint range grid.
NIGHT = (11, 13, 18)
INK = (232, 234, 240)
MUTED = (174, 180, 192)
ACCENT = (227, 130, 104)
GRID = (255, 255, 255, 12)
# Chakra Petch is a web font, so the card uses the closest face installed on the machine.
DISPLAY = "C:/Windows/Fonts/seguisb.ttf"
BODY = "C:/Windows/Fonts/segoeui.ttf"

TAGLINE = "Aim training concepts, routines, and the best existing resources."


def main():
    card = Image.new("RGBA", (W, H), NIGHT)
    grid = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    pen = ImageDraw.Draw(grid)
    for x in range(0, W, 48):
        pen.line([(x, 0), (x, H)], fill=GRID)
    for y in range(0, H, 48):
        pen.line([(0, y), (W, y)], fill=GRID)
    card = Image.alpha_composite(card, grid)

    pen = ImageDraw.Draw(card)
    # A crosshair sits behind the wordmark, as on the landing page.
    cx, cy, r = W - 250, H / 2, 150
    pen.ellipse((cx - r, cy - r, cx + r, cy + r), outline=(227, 130, 104, 64), width=3)
    for dx, dy in ((-1, 0), (1, 0), (0, -1), (0, 1)):
        pen.line([(cx + dx * (r - 40), cy + dy * (r - 40)), (cx + dx * (r + 60), cy + dy * (r + 60))],
                 fill=(227, 130, 104, 64), width=3)

    pen.text((90, 250), "AIM", font=ImageFont.truetype(DISPLAY, 150), fill=INK)
    pen.line([(96, 420), (300, 420)], fill=ACCENT, width=5)
    pen.text((92, 455), TAGLINE, font=ImageFont.truetype(BODY, 30), fill=MUTED)

    OUT.parent.mkdir(parents=True, exist_ok=True)
    card.convert("RGB").save(OUT, quality=92)
    print(f"card written to {OUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()

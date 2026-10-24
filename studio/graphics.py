"""Code-made graphics drawn with Pillow: title cards and text overlays.

Palette follows the AI character: charcoal suit, burgundy tie, antique gold paisley.
"""
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

W, H = 1920, 1080
FONTS = Path(__file__).resolve().parent.parent / "assets" / "fonts"

CHARCOAL = (27, 28, 32)
OFF_WHITE = (238, 234, 226)
GREY = (150, 148, 144)
BURGUNDY = (128, 30, 48)
GOLD = (190, 156, 94)

MARGIN = 160  # left edge of all text


def font(name: str, size: int) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(str(FONTS / name), size)


def wrap(draw: ImageDraw.ImageDraw, text: str, fnt, max_width: int) -> list[str]:
    lines, line = [], ""
    for word in text.split():
        trial = f"{line} {word}".strip()
        if draw.textlength(trial, font=fnt) <= max_width or not line:
            line = trial
        else:
            lines.append(line)
            line = word
    return lines + [line] if line else lines


def spaced(draw, xy, text, fnt, fill, tracking=4):
    """Draw text with extra letter spacing (for small uppercase labels)."""
    x, y = xy
    for ch in text:
        draw.text((x, y), ch, font=fnt, fill=fill)
        x += draw.textlength(ch, font=fnt) + tracking


def charcoal_background() -> Image.Image:
    """Charcoal with a soft lighter glow towards the upper right."""
    img = Image.new("RGB", (W, H), CHARCOAL)
    glow = Image.radial_gradient("L").resize((W * 2, H * 2)).crop((W // 2, 0, W // 2 + W, H))
    lighter = Image.new("RGB", (W, H), (44, 45, 50))
    img = Image.composite(img, lighter, glow)
    # A little grain hides banding in the dark gradient after video compression.
    grain = Image.effect_noise((W, H), 24).convert("RGB")
    return Image.blend(img, grain, 0.04)


def title_card(title: str, subtitle: str, out: Path) -> Path:
    img = charcoal_background()
    d = ImageDraw.Draw(img)
    spaced(d, (MARGIN, 300), "TEMPERATURA CERO", font("Inter-SemiBold.ttf", 26), GOLD, tracking=6)
    title_font = font("InterDisplay-SemiBold.ttf", 92)
    y = 370
    for line in wrap(d, title, title_font, W - 2 * MARGIN):
        d.text((MARGIN, y), line, font=title_font, fill=OFF_WHITE)
        y += 116
    y += 30
    d.rectangle((MARGIN, y, MARGIN + 120, y + 6), fill=BURGUNDY)
    d.text((MARGIN, y + 40), subtitle, font=font("InterDisplay-Light.ttf", 52), fill=GOLD)
    img.save(out)
    return out


def _left_shade() -> Image.Image:
    """Transparent layer that darkens the left side so text reads on any photo."""
    fade_end = int(W * 0.62)
    row = [int(225 * max(0.0, 1 - x / fade_end) ** 0.8) for x in range(W)]
    alpha = Image.new("L", (W, 1))
    alpha.putdata(row)
    shade = Image.new("RGBA", (W, H), CHARCOAL + (0,))
    shade.putalpha(alpha.resize((W, H)))
    return shade


def overlay_card(overlay: dict, out: Path, on_photo: bool) -> Path:
    """Text block on the left third. Transparent PNG if on_photo, else on charcoal.

    overlay keys: kicker, and one of
      title + body          (a named thing with a description)
      items                 (a short list)
      from + to (+ body)    (a shift, e.g. 2030s -> 2040s - 2050s)
    """
    img = _left_shade() if on_photo else charcoal_background().convert("RGBA")
    d = ImageDraw.Draw(img)
    x, y, width = MARGIN, 300, 820

    d.rectangle((x, y, x + 6, y + 34), fill=BURGUNDY)
    spaced(d, (x + 26, y), overlay["kicker"].upper(), font("Inter-SemiBold.ttf", 30), GOLD, tracking=5)
    y += 90

    if "items" in overlay:
        item_font = font("InterDisplay-SemiBold.ttf", 54)
        for n, item in enumerate(overlay["items"], 1):
            d.text((x, y), f"{n:02d}", font=font("Inter-SemiBold.ttf", 30), fill=GOLD)
            for line in wrap(d, item, item_font, width - 90):
                d.text((x + 90, y - 14), line, font=item_font, fill=OFF_WHITE)
                y += 68
            y += 34
    elif "from" in overlay:
        old_font = font("InterDisplay-Light.ttf", 84)
        d.text((x, y), overlay["from"], font=old_font, fill=GREY)
        left, top, right, bottom = d.textbbox((x, y), overlay["from"], font=old_font)
        mid = (top + bottom) // 2
        d.line((left - 8, mid, right + 8, mid), fill=BURGUNDY, width=8)
        y += 140
        to_font, arrow_font = font("InterDisplay-SemiBold.ttf", 120), font("InterDisplay-Light.ttf", 90)
        to_box = d.textbbox((x + 110, y), overlay["to"], font=to_font)
        d.text((x, (to_box[1] + to_box[3]) // 2), "→", font=arrow_font, fill=GOLD, anchor="lm")
        d.text((x + 110, y), overlay["to"], font=to_font, fill=GOLD)
        y += 190
        if overlay.get("body"):
            d.text((x, y), overlay["body"], font=font("Inter-Regular.ttf", 44), fill=OFF_WHITE)
    else:
        title_font = font("InterDisplay-SemiBold.ttf", 76)
        for line in wrap(d, overlay["title"], title_font, width):
            d.text((x, y), line, font=title_font, fill=OFF_WHITE)
            y += 92
        y += 24
        body_font = font("Inter-Regular.ttf", 40)
        for line in wrap(d, overlay.get("body", ""), body_font, width):
            d.text((x, y), line, font=body_font, fill=OFF_WHITE)
            y += 56

    img.save(out)
    return out

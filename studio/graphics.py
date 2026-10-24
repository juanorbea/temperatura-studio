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
    Full-frame graphics on charcoal (shots without a photo):
      pillars + active      (four connected blocks, one highlighted)
      events (+ highlight)  (a timeline of median years)
      columns (+ show)      (two cards side by side)
      rows                  (a table of milestones and years)
    """
    for kind, draw in FULL_FRAME.items():
        if kind in overlay:
            if on_photo:
                raise ValueError(f"a {kind!r} graphic fills the frame; give the shot no prompt")
            img = charcoal_background().convert("RGBA")
            draw(ImageDraw.Draw(img), overlay)
            img.save(out)
            return out
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


# ---- Full-frame graphics -------------------------------------------------------------

def _kicker(d: ImageDraw.ImageDraw, text: str, y: int = 150) -> None:
    d.rectangle((MARGIN, y, MARGIN + 6, y + 34), fill=BURGUNDY)
    spaced(d, (MARGIN + 26, y), text.upper(), font("Inter-SemiBold.ttf", 30), GOLD, tracking=5)


def _centered(d, cx: int, y: int, text: str, fnt, fill, width: int, line: int) -> int:
    for row in wrap(d, text, fnt, width):
        d.text((cx, y), row, font=fnt, fill=fill, anchor="ma")
        y += line
    return y


def _pillars(d: ImageDraw.ImageDraw, o: dict) -> None:
    """Four connected blocks; the active one in burgundy and gold, the rest dimmed."""
    _kicker(d, o["kicker"])
    names, active = o["pillars"], o.get("active", 0)
    gap = 40
    box_w = (W - 2 * MARGIN - gap * (len(names) - 1)) // len(names)
    top, bottom = 380, 760
    mid = (top + bottom) // 2
    d.line((MARGIN + box_w // 2, mid, W - MARGIN - box_w // 2, mid), fill=(70, 68, 66), width=3)
    for i, name in enumerate(names, 1):
        x0 = MARGIN + (i - 1) * (box_w + gap)
        on = i == active
        d.rounded_rectangle((x0, top, x0 + box_w, bottom), radius=18,
                            fill=(48, 26, 34) if on else (36, 37, 42),
                            outline=GOLD if on else (66, 66, 70), width=4 if on else 2)
        d.text((x0 + 40, top + 40), f"{i:02d}", font=font("InterDisplay-SemiBold.ttf", 64),
               fill=GOLD if on else GREY)
        y = top + 160
        name_font = font("InterDisplay-SemiBold.ttf", 46)
        for row in wrap(d, name, name_font, box_w - 80):
            d.text((x0 + 40, y), row, font=name_font, fill=OFF_WHITE if on else GREY)
            y += 58
    if o.get("caption"):
        d.text((MARGIN, 840), o["caption"], font=font("Inter-Regular.ttf", 42), fill=OFF_WHITE)


def _timeline(d: ImageDraw.ImageDraw, o: dict) -> None:
    """Median years on an axis; the highlighted one large in gold."""
    _kicker(d, o["kicker"])
    start, end = o.get("start", 2035), o.get("end", 2060)
    x0, x1, axis = MARGIN + 40, W - MARGIN - 40, 600
    px = lambda year: x0 + (x1 - x0) * (year - start) / (end - start)
    d.line((x0, axis, x1, axis), fill=GREY, width=3)
    tick_font = font("Inter-Regular.ttf", 30)
    for year in range(start, end + 1, 5):
        d.line((px(year), axis - 12, px(year), axis + 12), fill=GREY, width=3)
        d.text((px(year), axis + 30), str(year), font=tick_font, fill=GREY, anchor="ma")
    highlight = o.get("highlight", len(o["events"]) - 1)
    for i, ev in enumerate(o["events"]):
        on = i == highlight
        x = px(ev["year"])
        up = ev.get("above", i % 2 == 0)
        r = 18 if on else 11
        d.ellipse((x - r, axis - r, x + r, axis + r), fill=GOLD if on else (120, 118, 114),
                  outline=CHARCOAL, width=3)
        stem_end = axis - 120 if up else axis + 110
        d.line((x, axis - r if up else axis + r, x, stem_end), fill=GOLD if on else (90, 89, 86), width=2)
        year_font = font("InterDisplay-SemiBold.ttf", 72 if on else 44)
        label_font = font("Inter-SemiBold.ttf" if on else "Inter-Regular.ttf", 32 if on else 28)
        if up:
            label_rows = wrap(d, ev["label"], label_font, 380)
            y = stem_end - 18 - 40 * len(label_rows)
            for row in label_rows:
                d.text((x, y), row, font=label_font, fill=OFF_WHITE if on else GREY, anchor="ma")
                y += 40
            d.text((x, stem_end - 26 - 40 * len(label_rows)), str(ev["year"]), font=year_font,
                   fill=GOLD if on else GREY, anchor="md")
        else:
            d.text((x, stem_end + 12), str(ev["year"]), font=year_font, fill=GOLD if on else GREY, anchor="ma")
            _centered(d, x, stem_end + 22 + (84 if on else 54), ev["label"], label_font,
                      OFF_WHITE if on else GREY, 380, 40)
    if o.get("caption"):
        d.text((MARGIN, 960), o["caption"], font=font("Inter-Regular.ttf", 34), fill=GREY)


def _columns(d: ImageDraw.ImageDraw, o: dict) -> None:
    """Two cards side by side (e.g. an agreement without and with China); show hides the second."""
    _kicker(d, o["kicker"])
    cols, show = o["columns"], o.get("show", len(o["columns"]))
    gap = 80
    card_w = (W - 2 * MARGIN - gap) // 2
    for i, col in enumerate(cols):
        x0, top, bottom = MARGIN + i * (card_w + gap), 280, 930
        if i >= show:
            d.rounded_rectangle((x0, top, x0 + card_w, bottom), radius=18, outline=(56, 56, 60), width=2)
            continue
        d.rounded_rectangle((x0, top, x0 + card_w, bottom), radius=18, fill=(36, 37, 42),
                            outline=GOLD if i == show - 1 else (66, 66, 70), width=3)
        x, y = x0 + 56, top + 50
        title_font = font("InterDisplay-SemiBold.ttf", 50)
        for row in wrap(d, col["title"], title_font, card_w - 112):
            d.text((x, y), row, font=title_font, fill=OFF_WHITE)
            y += 62
        y += 20
        for item in col.get("rows", []):
            d.text((x, y), "·  " + item, font=font("Inter-Regular.ttf", 38), fill=GREY)
            y += 54
        d.text((x, bottom - 270), "Fecha mediana", font=font("Inter-SemiBold.ttf", 28), fill=GREY)
        d.text((x, bottom - 230), str(col["year"]), font=font("InterDisplay-SemiBold.ttf", 120), fill=GOLD)
        if col.get("note"):
            d.text((x, bottom - 80), col["note"], font=font("Inter-Regular.ttf", 36), fill=OFF_WHITE)


def _table(d: ImageDraw.ImageDraw, o: dict) -> None:
    """Milestones with their median year, sorted by year, with a dot on a 2035-2060 strip."""
    _kicker(d, o["kicker"], y=110)
    rows = sorted(o["rows"], key=lambda r: r[1])
    y, row_h = 210, 76
    label_font, year_font = font("Inter-Regular.ttf", 36), font("InterDisplay-SemiBold.ttf", 44)
    strip0, strip1 = 1260, W - MARGIN
    for k, (label, year) in enumerate(rows):
        if k % 2 == 0:
            d.rectangle((MARGIN - 20, y - 14, W - MARGIN + 20, y + row_h - 22), fill=(34, 35, 40))
        d.text((MARGIN, y), label, font=label_font, fill=OFF_WHITE)
        d.text((1120, y - 4), str(year), font=year_font, fill=GOLD)
        cy = y + 24
        d.line((strip0, cy, strip1, cy), fill=(70, 68, 66), width=2)
        x = strip0 + (strip1 - strip0) * (year - 2035) / 25
        d.ellipse((x - 10, cy - 10, x + 10, cy + 10), fill=BURGUNDY if year >= 2050 else GOLD)
        y += row_h
    for year in (2035, 2040, 2045, 2050, 2055, 2060):
        x = strip0 + (strip1 - strip0) * (year - 2035) / 25
        d.text((x, y + 4), str(year), font=font("Inter-Regular.ttf", 26), fill=GREY, anchor="ma")


FULL_FRAME = {"pillars": _pillars, "events": _timeline, "columns": _columns, "rows": _table}

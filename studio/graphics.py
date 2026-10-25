"""Code-made graphics drawn with Pillow: title cards and text overlays.

Two themes; a storyboard picks one with `theme:`.
  charcoal   (default, video 1) palette of the AI character: charcoal suit, burgundy tie,
             antique gold paisley.
  blueprint  (from video 2) technical-blueprint editorial: off-white paper with a fine grid,
             bold dark navy titles, copper accent lines and labels, light grey maps and
             blueprint dimension marks. Reference: Juan's NotebookLM-style slides.
"""
import json
import math
from dataclasses import dataclass
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


def title_card(title: str, subtitle: str, out: Path, theme: str = "charcoal") -> Path:
    if _theme(theme) is BLUEPRINT:
        return _bp_title_card(title, subtitle, out)
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


def overlay_card(overlay: dict, out: Path, on_photo: bool, theme: str = "charcoal") -> Path:
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
    The blueprint theme has its own graphics; see _bp_overlay_card.
    """
    if _theme(theme) is BLUEPRINT:
        return _bp_overlay_card(overlay, out, on_photo)
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


# ---- Themes --------------------------------------------------------------------------

@dataclass(frozen=True)
class Theme:
    name: str
    paper: tuple          # background
    grid: tuple           # fine grid lines
    grid_major: tuple     # every fifth grid line
    ink: tuple            # titles and big numbers
    text: tuple           # body text
    muted: tuple          # secondary labels, axes
    accent: tuple         # accent lines, highlighted values, kickers
    accent_soft: tuple    # pale accent fills
    line: tuple           # thin construction and dimension lines
    land: tuple           # map land
    panel: tuple          # cards on top of the paper


CHARCOAL_THEME = Theme("charcoal", CHARCOAL, (44, 45, 50), (56, 57, 62), OFF_WHITE, OFF_WHITE, GREY,
                       GOLD, (60, 52, 40), (90, 89, 86), (60, 61, 66), (36, 37, 42))
BLUEPRINT = Theme("blueprint",
                  paper=(246, 245, 241), grid=(229, 231, 234), grid_major=(214, 218, 224),
                  ink=(20, 33, 66), text=(44, 54, 78), muted=(118, 126, 142),
                  accent=(193, 108, 48), accent_soft=(240, 214, 190), line=(150, 160, 178),
                  land=(206, 210, 216), panel=(252, 252, 250))
THEMES = {t.name: t for t in (CHARCOAL_THEME, BLUEPRINT)}


def _theme(name: str) -> Theme:
    if name not in THEMES:
        raise ValueError(f"unknown graphics theme {name!r}; use one of: {', '.join(THEMES)}")
    return THEMES[name]


# ---- Blueprint theme -----------------------------------------------------------------

T = BLUEPRINT
BP_MARGIN = 140
MAPS = Path(__file__).resolve().parent.parent / "assets" / "maps"


def blueprint_paper(width: int = W, height: int = H) -> Image.Image:
    """Off-white paper with a fine 40 px grid, darker every 200 px, and corner registration marks."""
    img = Image.new("RGB", (width, height), T.paper)
    d = ImageDraw.Draw(img)
    for x in range(0, width, 40):
        d.line((x, 0, x, height), fill=T.grid_major if x % 200 == 0 else T.grid, width=1)
    for y in range(0, height, 40):
        d.line((0, y, width, y), fill=T.grid_major if y % 200 == 0 else T.grid, width=1)
    for cx, cy in ((60, 60), (width - 60, 60), (60, height - 60), (width - 60, height - 60)):
        d.line((cx - 18, cy, cx + 18, cy), fill=T.line, width=2)
        d.line((cx, cy - 18, cx, cy + 18), fill=T.line, width=2)
    return img


def dimension(d: ImageDraw.ImageDraw, x0: int, y0: int, x1: int, y1: int, label: str = "",
              color: tuple | None = None) -> None:
    """A blueprint dimension mark: a thin line with end ticks and a small label in the middle."""
    color = color or T.line
    d.line((x0, y0, x1, y1), fill=color, width=2)
    ang = math.atan2(y1 - y0, x1 - x0) + math.pi / 2
    dx, dy = 12 * math.cos(ang), 12 * math.sin(ang)
    for x, y in ((x0, y0), (x1, y1)):
        d.line((x - dx, y - dy, x + dx, y + dy), fill=color, width=2)
    if label:
        f = font("Inter-Medium.ttf", 22)
        mx, my = (x0 + x1) / 2, (y0 + y1) / 2
        box = d.textbbox((mx, my), label, font=f, anchor="mm")
        d.rectangle((box[0] - 8, box[1] - 4, box[2] + 8, box[3] + 4), fill=T.paper)
        d.text((mx, my), label, font=f, fill=color, anchor="mm")


def _bp_kicker(d, text: str, x: int = BP_MARGIN, y: int = 96) -> None:
    d.rectangle((x, y + 4, x + 40, y + 10), fill=T.accent)
    spaced(d, (x + 56, y - 6), text.upper(), font("Inter-SemiBold.ttf", 26), T.accent, tracking=4)


def _bp_title(d, text: str, x: int = BP_MARGIN, y: int = 140, size: int = 76, width: int = W - 2 * BP_MARGIN) -> int:
    f = font("InterDisplay-Bold.ttf", size)
    for row in wrap(d, text, f, width):
        d.text((x, y), row, font=f, fill=T.ink)
        y += int(size * 1.15)
    return y


def _bp_caption(d, text: str, y: int = 980) -> None:
    if text:
        d.line((BP_MARGIN, y - 22, BP_MARGIN + 60, y - 22), fill=T.accent, width=3)
        d.text((BP_MARGIN, y), text, font=font("Inter-Regular.ttf", 32), fill=T.text)


def _bp_title_card(title: str, subtitle: str, out: Path) -> Path:
    img = blueprint_paper()
    d = ImageDraw.Draw(img)
    spaced(d, (BP_MARGIN, 300), "TEMPERATURA CERO", font("Inter-SemiBold.ttf", 26), T.accent, tracking=6)
    y = _bp_title(d, title, y=360, size=92, width=1120)
    y += 30
    d.rectangle((BP_MARGIN, y, BP_MARGIN + 140, y + 7), fill=T.accent)
    d.text((BP_MARGIN, y + 40), subtitle, font=font("Inter-Medium.ttf", 46), fill=T.muted)
    _chip_schematic(d, 1560, 600, 300)
    dimension(d, BP_MARGIN, 250, W - BP_MARGIN, 250, "")
    img.save(out)
    return out


def _chip_schematic(d, cx: int, cy: int, size: int) -> None:
    """Line drawing of a chip package seen from above, with pins and dimension marks."""
    h = size // 2
    d.rectangle((cx - h, cy - h, cx + h, cy + h), outline=T.ink, width=3)
    d.rectangle((cx - h // 2, cy - h // 2, cx + h // 2, cy + h // 2), outline=T.accent, width=3)
    for k in range(-h + 30, h - 20, 30):
        for x0, y0, x1, y1 in ((cx + k, cy - h, cx + k, cy - h - 24), (cx + k, cy + h, cx + k, cy + h + 24),
                               (cx - h, cy + k, cx - h - 24, cy + k), (cx + h, cy + k, cx + h + 24, cy + k)):
            d.line((x0, y0, x1, y1), fill=T.ink, width=3)
    for g in range(-h // 2 + 25, h // 2, 25):
        d.line((cx - h // 2, cy + g, cx + h // 2, cy + g), fill=T.accent_soft, width=1)
    dimension(d, cx - h, cy + h + 70, cx + h, cy + h + 70, "")
    dimension(d, cx + h + 70, cy - h, cx + h + 70, cy + h, "")


def _bp_overlay_card(overlay: dict, out: Path, on_photo: bool) -> Path:
    """Blueprint graphics. Full frame on paper: one of the BP_FULL_FRAME kinds.
    On a photo: a paper card on the left with kicker, title and body (or from + to)."""
    for kind, draw in BP_FULL_FRAME.items():
        if kind in overlay:
            if on_photo:
                raise ValueError(f"a {kind!r} graphic fills the frame; give the shot no prompt")
            img = blueprint_paper()
            draw(ImageDraw.Draw(img), overlay)
            img.save(out)
            return out
    if on_photo:
        img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        card = blueprint_paper(780, 760).convert("RGBA")
        card.putalpha(242)
        img.alpha_composite(card, (BP_MARGIN - 40, 160))
        x, y, width = BP_MARGIN, 220, 690
    else:
        img = blueprint_paper().convert("RGBA")
        x, y, width = BP_MARGIN, 300, 1200
    d = ImageDraw.Draw(img)
    d.rectangle((x, y + 4, x + 40, y + 10), fill=T.accent)
    spaced(d, (x + 56, y - 6), overlay["kicker"].upper(), font("Inter-SemiBold.ttf", 26), T.accent, tracking=4)
    y += 70
    if "from" in overlay:
        old = font("InterDisplay-Bold.ttf", 96)
        d.text((x, y), overlay["from"], font=old, fill=T.muted)
        box = d.textbbox((x, y), overlay["from"], font=old)
        mid = (box[1] + box[3]) // 2
        d.line((box[0] - 6, mid, box[2] + 6, mid), fill=T.accent, width=7)
        y += 150
        new = font("InterDisplay-Bold.ttf", 132)
        d.text((x, y + 70), "→", font=font("InterDisplay-Light.ttf", 96), fill=T.accent, anchor="lm")
        d.text((x + 110, y), overlay["to"], font=new, fill=T.ink)
        y += 200
        for row in wrap(d, overlay.get("body", ""), font("Inter-Regular.ttf", 38), width):
            d.text((x, y), row, font=font("Inter-Regular.ttf", 38), fill=T.text)
            y += 52
    else:
        y = _bp_title(d, overlay["title"], x=x, y=y, size=68, width=width)
        y += 20
        d.line((x, y, x + 80, y), fill=T.accent, width=3)
        y += 30
        body = font("Inter-Regular.ttf", 38)
        for row in wrap(d, overlay.get("body", ""), body, width):
            d.text((x, y), row, font=body, fill=T.text)
            y += 54
    img.save(out)
    return out


def _bp_chain(d, o: dict) -> None:
    """The chain of a chip as connected links; the active link shows its share as a big counter.
    o: kicker, title, links: [{label, value, companies}], active (1-based), caption."""
    _bp_kicker(d, o["kicker"])
    _bp_title(d, o["title"], size=64)
    links, active = o["links"], o.get("active", 0)
    n = len(links)
    gap = 36
    w = (W - 2 * BP_MARGIN - gap * (n - 1)) // n
    top, bottom = 330, 900
    cy = 440
    d.line((BP_MARGIN, cy, W - BP_MARGIN, cy), fill=T.line, width=3)
    for i, link in enumerate(links, 1):
        x0 = BP_MARGIN + (i - 1) * (w + gap)
        on = i == active
        done = active and i < active
        d.rectangle((x0, top, x0 + w, bottom), fill=T.panel if on else T.paper,
                    outline=T.accent if on else T.line, width=4 if on else 2)
        d.ellipse((x0 + w / 2 - 16, cy - 16, x0 + w / 2 + 16, cy + 16),
                  fill=T.accent if on or done else T.paper, outline=T.accent if on or done else T.line, width=3)
        d.text((x0 + 28, top + 24), f"{i:02d}", font=font("Inter-SemiBold.ttf", 26), fill=T.accent if on else T.muted)
        y = cy + 50
        lf = font("InterDisplay-Bold.ttf", 38)
        while any(d.textlength(word, font=lf) > w - 56 for word in link["label"].split()):
            lf = font("InterDisplay-Bold.ttf", lf.size - 2)
        for row in wrap(d, link["label"], lf, w - 56):
            d.text((x0 + 28, y), row, font=lf, fill=T.ink if on or done else T.muted)
            y += 46
        if on or done:
            vf = font("InterDisplay-Bold.ttf", 120 if on else 64)
            d.text((x0 + 28, bottom - (250 if on else 190)), link["value"], font=vf, fill=T.accent if on else T.ink)
        cf = font("Inter-Regular.ttf", 26)
        y = bottom - 80
        for row in reversed(wrap(d, link.get("companies", ""), cf, w - 56)):
            d.text((x0 + 28, y), row, font=cf, fill=T.text if on or done else T.muted)
            y -= 34
    dimension(d, BP_MARGIN, bottom + 40, W - BP_MARGIN, bottom + 40, o.get("dimension", ""))
    _bp_caption(d, o.get("caption", ""), y=990)


def _bp_bars(d, o: dict) -> None:
    """Horizontal bars. o: kicker, title, bars: [{label, value, text, note}], max, caption, highlight."""
    _bp_kicker(d, o["kicker"])
    y = _bp_title(d, o["title"], size=64)
    bars = o["bars"]
    vmax = o.get("max", max(b["value"] for b in bars))
    x0, x1 = BP_MARGIN + 430, W - BP_MARGIN - 260
    row = 190
    top = max(y + 70, 360 + (560 - row * len(bars)) // 2)
    hi = o.get("highlight", 0)
    for i, b in enumerate(bars):
        yy = top + i * row
        on = i == hi
        d.text((BP_MARGIN, yy + 6), b["label"], font=font("InterDisplay-Bold.ttf", 42), fill=T.ink)
        if b.get("note"):
            d.text((BP_MARGIN, yy + 60), b["note"], font=font("Inter-Regular.ttf", 26), fill=T.muted)
        bw = max(6, (x1 - x0) * b["value"] / vmax)
        d.rectangle((x0, yy, x1, yy + 80), outline=T.grid_major, width=1)
        d.rectangle((x0, yy, x0 + bw, yy + 80), fill=T.accent if on else T.ink)
        d.text((x0 + bw + 24, yy + 40), b["text"], font=font("InterDisplay-Bold.ttf", 52),
               fill=T.accent if on else T.ink, anchor="lm")
    bottom = top + len(bars) * row - 30
    dimension(d, x0, bottom, x1, bottom, o.get("dimension", ""))
    _bp_caption(d, o.get("caption", ""))


def _bp_share(d, o: dict) -> None:
    """Two (or more) points of a share over time, joined by a dashed line: no invented curve.
    o: kicker, title, points: [{x, year_label, value, text}], ymax, caption."""
    _bp_kicker(d, o["kicker"])
    _bp_title(d, o["title"], size=64)
    pts = o["points"]
    xs = [p["x"] for p in pts]
    lo, hi = o.get("xmin", min(xs) - 4), o.get("xmax", max(xs) + 4)
    left, right, top, base = BP_MARGIN + 80, W - BP_MARGIN - 80, 360, 860
    ymax = o.get("ymax", 60)
    px = lambda x: left + (right - left) * (x - lo) / (hi - lo)
    py = lambda v: base - (base - top) * v / ymax
    d.line((left, base, right, base), fill=T.ink, width=3)
    d.line((left, base, left, top - 20), fill=T.ink, width=3)
    for v in range(0, ymax + 1, 10):
        d.line((left - 10, py(v), left, py(v)), fill=T.ink, width=2)
        d.line((left, py(v), right, py(v)), fill=T.grid_major, width=1)
        d.text((left - 20, py(v)), f"{v} %", font=font("Inter-Regular.ttf", 24), fill=T.muted, anchor="rm")
    coords = [(px(p["x"]), py(p["value"])) for p in pts]
    for (ax, ay), (bx, by) in zip(coords, coords[1:]):
        steps = int(math.hypot(bx - ax, by - ay) // 24)
        for k in range(0, steps, 2):
            d.line((ax + (bx - ax) * k / steps, ay + (by - ay) * k / steps,
                    ax + (bx - ax) * (k + 1) / steps, ay + (by - ay) * (k + 1) / steps), fill=T.accent, width=6)
    for p, (cx, cy) in zip(pts, coords):
        d.ellipse((cx - 16, cy - 16, cx + 16, cy + 16), fill=T.ink)
        d.line((cx, cy + 16, cx, base), fill=T.line, width=2)
        d.text((cx, base + 24), p["year_label"], font=font("Inter-SemiBold.ttf", 30), fill=T.text, anchor="ma")
        d.text((cx + 30, cy - 30), p["text"], font=font("InterDisplay-Bold.ttf", 56), fill=T.ink, anchor="ls")
    dimension(d, coords[0][0], top - 10, coords[-1][0], top - 10, o.get("dimension", ""))
    _bp_caption(d, o.get("caption", ""))


def _bp_steps(d, o: dict) -> None:
    """Dated milestones on a horizontal line; past ones solid, the highlighted one in copper.
    o: kicker, title, steps: [{date, label}], highlight (0-based), caption."""
    _bp_kicker(d, o["kicker"])
    _bp_title(d, o["title"], size=64)
    steps = o["steps"]
    hi = o.get("highlight", len(steps) - 1)
    left, right, axis = BP_MARGIN + 40, W - BP_MARGIN - 40, 600
    d.line((left - 40, axis, right + 40, axis), fill=T.ink, width=4)
    step = (right - left) / max(1, len(steps) - 1)
    for i, s in enumerate(steps):
        x = left + i * step
        on, past = i == hi, i < hi
        r = 22 if on else 14
        d.ellipse((x - r, axis - r, x + r, axis + r), fill=T.accent if on else (T.ink if past else T.paper),
                  outline=T.accent if on else T.ink, width=4)
        up = i % 2 == 0
        y_stem = axis - 70 if up else axis + 70
        d.line((x, axis - r if up else axis + r, x, y_stem), fill=T.line, width=2)
        df = font("InterDisplay-Bold.ttf", 44 if on else 36)
        lf = font("Inter-Medium.ttf" if on else "Inter-Regular.ttf", 28)
        rows = wrap(d, s["label"], lf, int(step) + 40)
        color = T.ink if on or past else T.muted
        if up:
            y = y_stem - 12 - 36 * len(rows)
            for row in rows:
                d.text((x, y), row, font=lf, fill=T.text if on or past else T.muted, anchor="ma")
                y += 36
            d.text((x, y_stem - 22 - 36 * len(rows)), s["date"], font=df, fill=T.accent if on else color, anchor="md")
        else:
            d.text((x, y_stem + 10), s["date"], font=df, fill=T.accent if on else color, anchor="ma")
            y = y_stem + 70
            for row in rows:
                d.text((x, y), row, font=lf, fill=T.text if on or past else T.muted, anchor="ma")
                y += 36
    _bp_caption(d, o.get("caption", ""))


def _bp_lot(d, o: dict) -> None:
    """A lot of 25 wafers moving together versus single wafers moving one by one.
    o: kicker, title, left, right (column titles), caption."""
    _bp_kicker(d, o["kicker"])
    _bp_title(d, o["title"], size=64)
    mid = W // 2
    d.line((mid, 340, mid, 900), fill=T.line, width=2)
    tf = font("InterDisplay-Bold.ttf", 44)
    d.text((BP_MARGIN, 350), o.get("left", "Lote convencional"), font=tf, fill=T.ink)
    d.text((mid + 60, 350), o.get("right", "Oblea a oblea"), font=tf, fill=T.ink)
    # 25 wafers stacked in a carrier, seen side-on
    x0, y0 = BP_MARGIN + 80, 470
    d.rectangle((x0 - 20, y0 - 20, x0 + 420, y0 + 25 * 15 + 10), outline=T.ink, width=3)
    for k in range(25):
        y = y0 + k * 15
        d.ellipse((x0, y, x0 + 400, y + 12), fill=T.panel, outline=T.ink, width=2)
    dimension(d, x0 + 470, y0, x0 + 470, y0 + 25 * 15 - 3, "25")
    d.text((x0, y0 + 25 * 15 + 40), o.get("left_note", "25 obleas juntas"), font=font("Inter-Regular.ttf", 32), fill=T.text)
    # single wafers in a row, each with a data mark
    for k in range(4):
        cx, cy = mid + 140 + k * 175, 640
        d.ellipse((cx - 70, cy - 70, cx + 70, cy + 70), fill=T.panel, outline=T.ink, width=3)
        for g in range(-50, 60, 20):
            d.line((cx + g, cy - 50, cx + g, cy + 50), fill=T.grid_major, width=1)
        d.line((cx + 70, cy, cx + 105, cy), fill=T.accent, width=4)
        d.rectangle((cx - 30, cy - 130, cx + 30, cy - 100), outline=T.accent, width=3)
        d.text((cx, cy - 115), "datos", font=font("Inter-Medium.ttf", 18), fill=T.accent, anchor="mm")
    d.text((mid + 60, 830), o.get("right_note", "una a una, con datos de cada oblea"), font=font("Inter-Regular.ttf", 32), fill=T.text)
    _bp_caption(d, o.get("caption", ""))


def _bp_map(d, o: dict) -> None:
    """Light grey map of Japan with copper markers. o: kicker, title, places: [{name, lon, lat, note}],
    regions: [{name, lon, lat}] (grey labels), caption."""
    _bp_kicker(d, o["kicker"])
    _bp_title(d, o["title"], size=64, width=760)
    rings = json.loads((MAPS / "japan.json").read_text())
    lon0, lon1, lat0, lat1 = 128.8, 146.0, 30.8, 45.8
    box = (980, 60, 1840, 1030)  # x0, y0, x1, y1
    k = min((box[2] - box[0]) / (lon1 - lon0), (box[3] - box[1]) / ((lat1 - lat0) * 1.2))
    proj = lambda lon, lat: (box[0] + (lon - lon0) * k, box[3] - (lat - lat0) * k * 1.2)
    for ring in rings:
        d.polygon([proj(x, y) for x, y in ring], fill=T.land, outline=T.line)
    for r in o.get("regions", []):
        x, y = proj(r["lon"], r["lat"])
        spaced(d, (x, y), r["name"].upper(), font("Inter-SemiBold.ttf", 26), T.muted, tracking=4)
    places = sorted(o["places"], key=lambda p: -p["lat"])
    ly = 400
    for p in places:
        x, y = proj(p["lon"], p["lat"])
        d.ellipse((x - 28, y - 28, x + 28, y + 28), outline=T.accent, width=3)
        d.ellipse((x - 12, y - 12, x + 12, y + 12), fill=T.accent)
        d.text((x + 40, y - 18), p["name"], font=font("Inter-SemiBold.ttf", 30), fill=T.ink)
        d.line((BP_MARGIN + 700, ly + 28, x - 28, y), fill=T.accent, width=2)
        d.ellipse((BP_MARGIN + 690, ly + 18, BP_MARGIN + 710, ly + 38), fill=T.accent)
        d.text((BP_MARGIN, ly), p["name"], font=font("InterDisplay-Bold.ttf", 48), fill=T.ink)
        for j, row in enumerate(wrap(d, p.get("note", ""), font("Inter-Regular.ttf", 30), 520)):
            d.text((BP_MARGIN, ly + 64 + j * 40), row, font=font("Inter-Regular.ttf", 30), fill=T.text)
        ly += 260
    dimension(d, box[0], box[3] + 20, box[2], box[3] + 20, "")
    _bp_caption(d, o.get("caption", ""))


def _bp_numbers(d, o: dict) -> None:
    """Up to four big figures side by side. o: kicker, title, figures: [{value, label}], highlight, caption."""
    _bp_kicker(d, o["kicker"])
    _bp_title(d, o["title"], size=64)
    figs = o["figures"]
    hi = o.get("highlight", -1)
    gap = 60
    w = (W - 2 * BP_MARGIN - gap * (len(figs) - 1)) // len(figs)
    for i, f in enumerate(figs):
        x = BP_MARGIN + i * (w + gap)
        on = i == hi
        d.line((x, 420, x + w, 420), fill=T.accent if on else T.line, width=4 if on else 2)
        size = 140 if len(figs) <= 2 else 104
        vf = font("InterDisplay-Bold.ttf", size)
        while d.textlength(f["value"], font=vf) > w and size > 60:
            size -= 6
            vf = font("InterDisplay-Bold.ttf", size)
        d.text((x, 460), f["value"], font=vf, fill=T.accent if on else T.ink)
        y = 460 + size + 40
        for row in wrap(d, f["label"], font("Inter-Regular.ttf", 34), w):
            d.text((x, y), row, font=font("Inter-Regular.ttf", 34), fill=T.text)
            y += 46
    _bp_caption(d, o.get("caption", ""))


BP_FULL_FRAME = {"links": _bp_chain, "bars": _bp_bars, "points": _bp_share, "steps": _bp_steps,
                 "lot": _bp_lot, "places": _bp_map, "figures": _bp_numbers}

"""The pizarra theme (video 5): a minimalist 2D whiteboard cartoon.

Very light blue paper (#e4f4fd) with one continuous ground line and a pale blue band
(#c9e9fc) under it at the same height on every card, so cuts read as a pan along one
landscape. Thin black outlines, muted earthy colours (browns for horses, slate blue for
machines and AI, greens and tans for land, red only to strike text out, gold for the
share certificate), and a handwritten sans (Kalam, SIL OFL) for words and numbers.
Kinetic typography is done shot by shot: consecutive cards add a word, a strike or a
number, so each new card "pops" the next piece on.
"""
import math
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

W, H = 1920, 1080
FONTS = Path(__file__).resolve().parent.parent / "assets" / "fonts"
HAND, HAND_BOLD = "Kalam-Regular.ttf", "Kalam-Bold.ttf"

PAPER = (228, 244, 253)       # #e4f4fd
SOFT = (201, 233, 252)        # #c9e9fc: ground band, panels, secondary fills
INK = (34, 34, 38)
TEXT = (58, 62, 70)
MUTED = (120, 132, 146)
RED = (204, 56, 46)
GOLD, GOLD_SOFT = (212, 166, 48), (246, 228, 172)
BROWN, BROWN_DARK = (156, 104, 62), (102, 68, 42)
SLATE, SLATE_SOFT = (76, 104, 140), (164, 186, 210)
GREEN, GREEN_SOFT = (128, 160, 98), (194, 212, 166)
TAN = (222, 194, 140)
COLORS = {"ink": INK, "brown": BROWN, "slate": SLATE, "red": RED, "gold": GOLD, "green": GREEN}

GROUND = 950       # y of the ground line on every card
MARGIN = 190       # wide: cards may get a slow pan, which crops ~140 px at one side


def font(name: str, size: int) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(str(FONTS / name), size)


def _wrap(d, text: str, fnt, width: int) -> list[str]:
    lines, line = [], ""
    for word in text.split():
        trial = f"{line} {word}".strip()
        if d.textlength(trial, font=fnt) <= width or not line:
            line = trial
        else:
            lines.append(line)
            line = word
    return lines + [line] if line else lines


def _wobble(x0, y0, x1, y1, amp=1.6, seed=0.0):
    """Points of a hand-drawn line: straight on average, with a small fixed wobble."""
    n = max(2, int(math.hypot(x1 - x0, y1 - y0) // 24))
    nx, ny = -(y1 - y0), x1 - x0
    norm = math.hypot(nx, ny) or 1
    return [(x0 + (x1 - x0) * t / n + nx / norm * amp * math.sin(t * 1.7 + seed),
             y0 + (y1 - y0) * t / n + ny / norm * amp * math.sin(t * 1.7 + seed)) for t in range(n + 1)]


def hand_line(d, x0, y0, x1, y1, fill=INK, width=3, seed=0.0, amp=1.6):
    d.line(_wobble(x0, y0, x1, y1, amp, seed), fill=fill, width=width, joint="curve")


def paper(width: int = W, height: int = H, ground: bool = True) -> Image.Image:
    img = Image.new("RGB", (width, height), PAPER)
    if ground:
        d = ImageDraw.Draw(img)
        d.rectangle((0, GROUND, width, height), fill=SOFT)
        hand_line(d, -10, GROUND, width + 10, GROUND, INK, 3, amp=1.2)
    return img


def kicker(d, text: str, x: int = MARGIN, y: int = 96) -> None:
    f = font(HAND_BOLD, 38)
    d.text((x, y), text, font=f, fill=SLATE)
    hand_line(d, x, y + 58, x + min(d.textlength(text, font=f), 420), y + 58, SLATE, 3, seed=2)


def title(d, text: str, x: int = MARGIN, y: int = 150, size: int = 72, width: int = W - 2 * MARGIN,
          fill=INK, anchor: str = "la") -> int:
    f = font(HAND_BOLD, size)
    for row in _wrap(d, text, f, width):
        d.text((x, y), row, font=f, fill=fill, anchor=anchor)
        y += int(size * 1.12)
    return y


def caption(d, text: str, y: int = 975) -> None:
    if text:
        d.text((W // 2, y), text, font=font(HAND, 40), fill=TEXT, anchor="ma")


def strike(d, box, seed=0.0, width=9) -> None:
    """A red hand-drawn line through a text box, slightly rising to the right."""
    x0, y0, x1, y1 = box
    mid = (y0 + y1) / 2 + (y1 - y0) * 0.06
    hand_line(d, x0 - 14, mid + 6, x1 + 14, mid - 8, RED, width, seed=seed, amp=2.2)


# ---- Doodles: drawn on the ground, (x, y) is the bottom centre, s the size ---------------

def horse(d, x, y, s, fill=BROWN, outline=INK, face=1):
    """Side view cartoon horse facing right (face=-1: left)."""
    def P(px, py):
        return (x + face * px * s, y - py * s)
    w = max(2, int(s / 30))
    for lx in (-0.34, -0.2, 0.16, 0.3):                      # legs, brown with a thin outline
        a, b = P(lx - 0.035, 0.5), P(lx + 0.035, 0.0)
        d.rectangle((min(a[0], b[0]), a[1], max(a[0], b[0]), b[1]), fill=fill, outline=outline, width=max(1, w // 2 + 1))
        h0, h1 = P(lx - 0.045, 0.06), P(lx + 0.045, 0.0)
        d.rectangle((min(h0[0], h1[0]), h0[1], max(h0[0], h1[0]), h1[1]), fill=BROWN_DARK, outline=outline)
    d.line((P(-0.42, 0.62), P(-0.55, 0.36)), fill=BROWN_DARK, width=max(2, int(s / 16)))  # tail
    body = [P(-0.45, 0.72), P(0.4, 0.40)]
    d.ellipse((min(body[0][0], body[1][0]), body[0][1], max(body[0][0], body[1][0]), body[1][1]),
              fill=fill, outline=outline, width=w)
    d.polygon([P(0.22, 0.66), P(0.36, 0.98), P(0.5, 0.95), P(0.42, 0.56)], fill=fill, outline=outline)  # neck
    hx0, hx1 = sorted((P(0.34, 0)[0], P(0.66, 0)[0]))
    d.ellipse((hx0, P(0, 1.06)[1], hx1, P(0, 0.86)[1]), fill=fill, outline=outline, width=w)  # head
    d.polygon([P(0.38, 1.02), P(0.40, 1.16), P(0.46, 1.03)], fill=fill, outline=outline)    # ear
    ex, ey = P(0.5, 0.98)
    r = max(2, s * 0.04)
    d.ellipse((ex - r, ey - r, ex + r, ey + r), fill=(255, 255, 255), outline=outline, width=max(1, w // 2))
    d.ellipse((ex - r / 2, ey - r / 2, ex + r / 2, ey + r / 2), fill=outline)
    d.line((P(0.30, 0.96), P(0.22, 0.70)), fill=BROWN_DARK, width=max(2, int(s / 18)))     # mane


def tractor(d, x, y, s, fill=SLATE, outline=INK):
    w = max(2, int(s / 30))
    d.rectangle((x - 0.05 * s, y - 0.55 * s, x + 0.45 * s, y - 0.25 * s), fill=fill, outline=outline, width=w)  # hood
    d.rectangle((x - 0.42 * s, y - 0.95 * s, x - 0.05 * s, y - 0.3 * s), fill=SLATE_SOFT, outline=outline, width=w)  # cab
    d.rectangle((x - 0.36 * s, y - 0.88 * s, x - 0.11 * s, y - 0.62 * s), fill=PAPER, outline=outline, width=w)
    d.line((x + 0.3 * s, y - 0.55 * s, x + 0.3 * s, y - 0.78 * s), fill=outline, width=max(2, w))  # exhaust
    for cx, r in ((x - 0.25 * s, 0.25 * s), (x + 0.33 * s, 0.14 * s)):
        d.ellipse((cx - r, y - 2 * r, cx + r, y), fill=INK, outline=outline)
        d.ellipse((cx - r * 0.45, y - r * 1.45, cx + r * 0.45, y - r * 0.55), fill=SLATE_SOFT)


def truck(d, x, y, s, fill=SLATE, outline=INK):
    w = max(2, int(s / 30))
    d.rectangle((x - 0.6 * s, y - 0.7 * s, x + 0.15 * s, y - 0.16 * s), fill=PAPER, outline=outline, width=w)
    d.polygon([(x + 0.18 * s, y - 0.16 * s), (x + 0.18 * s, y - 0.62 * s), (x + 0.42 * s, y - 0.62 * s),
               (x + 0.56 * s, y - 0.4 * s), (x + 0.56 * s, y - 0.16 * s)], fill=fill, outline=outline)
    d.polygon([(x + 0.24 * s, y - 0.4 * s), (x + 0.24 * s, y - 0.56 * s), (x + 0.4 * s, y - 0.56 * s),
               (x + 0.5 * s, y - 0.4 * s)], fill=SLATE_SOFT, outline=outline)
    for cx in (x - 0.45 * s, x - 0.2 * s, x + 0.38 * s):
        r = 0.1 * s
        d.ellipse((cx - r, y - 2 * r, cx + r, y), fill=INK)


def car(d, x, y, s, fill=SLATE, outline=INK):
    """A generic driverless car: rounded body, empty front seat, a small sensor dome on the roof."""
    w = max(2, int(s / 30))
    d.rounded_rectangle((x - 0.5 * s, y - 0.38 * s, x + 0.5 * s, y - 0.1 * s), radius=int(0.1 * s), fill=fill,
                        outline=outline, width=w)
    d.polygon([(x - 0.3 * s, y - 0.38 * s), (x - 0.18 * s, y - 0.62 * s), (x + 0.22 * s, y - 0.62 * s),
               (x + 0.36 * s, y - 0.38 * s)], fill=SLATE_SOFT, outline=outline)
    d.line((x + 0.02 * s, y - 0.62 * s, x + 0.02 * s, y - 0.38 * s), fill=outline, width=w)
    d.ellipse((x - 0.07 * s, y - 0.72 * s, x + 0.07 * s, y - 0.6 * s), fill=SLATE_SOFT, outline=outline, width=w)
    for cx in (x - 0.3 * s, x + 0.3 * s):
        r = 0.11 * s
        d.ellipse((cx - r, y - 2 * r, cx + r, y), fill=INK)


def worker(d, x, y, s, on=True):
    """Stick figure: round head, floating hands, white shirt and green tie (muted when off)."""
    ink = INK if on else MUTED
    w = max(2, int(s / 22))
    d.ellipse((x - 0.13 * s, y - s, x + 0.13 * s, y - 0.74 * s), fill=PAPER, outline=ink, width=w)
    d.polygon([(x - 0.15 * s, y - 0.7 * s), (x + 0.15 * s, y - 0.7 * s), (x + 0.12 * s, y - 0.38 * s),
               (x - 0.12 * s, y - 0.38 * s)], fill=(255, 255, 255) if on else PAPER, outline=ink)
    if on:
        d.polygon([(x, y - 0.68 * s), (x + 0.035 * s, y - 0.5 * s), (x, y - 0.44 * s), (x - 0.035 * s, y - 0.5 * s)],
                  fill=GREEN)
    d.line((x - 0.07 * s, y - 0.38 * s, x - 0.1 * s, y), fill=ink, width=w)
    d.line((x + 0.07 * s, y - 0.38 * s, x + 0.1 * s, y), fill=ink, width=w)
    for hx in (-0.25, 0.25):
        r = 0.035 * s
        d.ellipse((x + hx * s - r, y - 0.52 * s - r, x + hx * s + r, y - 0.52 * s + r), fill=ink)


def building(d, x0, y, w, h, seed=0):
    d.rectangle((x0, y - h, x0 + w, y), fill=SOFT, outline=INK, width=3)
    for k, yy in enumerate(range(int(y - h + 24), int(y - 30), 44)):
        for xx in range(int(x0 + 16), int(x0 + w - 30), 38):
            if (k + xx // 38 + seed) % 3:
                d.rectangle((xx, yy, xx + 18, yy + 22), fill=PAPER, outline=INK, width=2)


ICONS = {"horse": horse, "tractor": tractor, "truck": truck, "car": car,
         "worker": lambda d, x, y, s, fill=None, outline=None: worker(d, x, y, s)}


def _fit(d, text, name, size, width, minimum=40):
    f = font(name, size)
    while d.textlength(text, font=f) > width and size > minimum:
        size -= 6
        f = font(name, size)
    return f


# ---- Cards -------------------------------------------------------------------------------

def title_card(text: str, subtitle: str, out: Path) -> Path:
    img = paper()
    d = ImageDraw.Draw(img)
    d.text((MARGIN, 250), "Temperatura Cero", font=font(HAND_BOLD, 40), fill=SLATE)
    y = title(d, text, y=320, size=96, width=1050)
    hand_line(d, MARGIN, y + 24, MARGIN + 180, y + 24, BROWN, 7, seed=1)
    d.text((MARGIN, y + 60), subtitle, font=font(HAND, 52), fill=TEXT)
    # a white fence and a horse on the ground line, on the right
    for k in range(7):
        px = 1300 + k * 80
        d.rectangle((px, GROUND - 150, px + 16, GROUND), fill=(255, 255, 255), outline=INK, width=2)
    for yy in (GROUND - 120, GROUND - 60):
        d.rectangle((1290, yy, 1300 + 6 * 80 + 26, yy + 14), fill=(255, 255, 255), outline=INK, width=2)
    horse(d, 1560, GROUND, 330)
    img.save(out)
    return out


def _phrase(d, o):
    """Big handwritten phrase, centred; o.strike (a word or part of it) gets a red line through it.
    o.quote wraps it in « »; o.note is a smaller line under it."""
    if o.get("kicker"):
        kicker(d, o["kicker"])
    text = o["phrase"]
    if o.get("quote"):
        text = f"«{text}»"
    size = o.get("size", 120)
    while True:  # long phrases wrap onto up to three lines before the letters get smaller
        f = font(HAND_BOLD, size)
        rows = _wrap(d, text, f, W - 2 * MARGIN)
        if size <= 60 or (len(rows) <= 3 and all(d.textlength(r, font=f) <= W - 2 * MARGIN for r in rows)):
            break
        size -= 6
    line_h = int(f.size * 1.2)
    y = 470 - line_h * len(rows) // 2
    hit = o.get("strike", "")
    for k, row in enumerate(rows):
        x = (W - d.textlength(row, font=f)) / 2
        d.text((x, y), row, font=f, fill=COLORS.get(o.get("color", "ink"), INK))
        if hit and hit in row:
            i = row.index(hit)
            sx = x + d.textlength(row[:i], font=f)
            box = d.textbbox((sx, y), hit, font=f)
            strike(d, box, seed=k)
        y += line_h
    if o.get("note"):
        nf = font(HAND_BOLD, o.get("note_size", 64))
        d.text((W // 2, y + 40), o["note"], font=nf, fill=COLORS.get(o.get("note_color", "brown"), BROWN), anchor="ma")
    caption(d, o.get("caption", ""))


def _stat(d, o):
    """A number pops on: big figure, a label, an optional small line and a row of doodles on the ground."""
    if o.get("kicker"):
        kicker(d, o["kicker"])
    color = COLORS.get(o.get("color", "brown"), BROWN)
    f = _fit(d, o["big"], HAND_BOLD, o.get("size", 230), W - 2 * MARGIN, 80)
    y = 240 if o.get("icon") else 300
    d.text((W // 2, y), o["big"], font=f, fill=color, anchor="ma")
    box = d.textbbox((W // 2, y), o["big"], font=f, anchor="ma")
    if o.get("strike_big"):
        strike(d, box, width=12)
    y = box[3] + 40
    for row in _wrap(d, o.get("label", ""), font(HAND, 56), 1300):
        d.text((W // 2, y), row, font=font(HAND, 56), fill=INK, anchor="ma")
        y += 66
    if o.get("small"):
        d.text((W // 2, y + 14), o["small"], font=font(HAND_BOLD, 52), fill=SLATE, anchor="ma")
    icon, n = o.get("icon"), o.get("icons", 1)
    if icon:
        s = o.get("icon_size", 150)
        step = s * 1.15
        x0 = W // 2 - step * (n - 1) / 2
        for k in range(n):
            ICONS[icon](d, x0 + k * step, GROUND, s)
    caption(d, o.get("caption", ""))


def _gauge(d, o):
    """A dial gauge filling to o.gauge percent, with the needle and the figure."""
    kicker(d, o["kicker"])
    title(d, o.get("title", ""), size=64)
    cx, cy, r = W // 2, 800, 420
    box = (cx - r, cy - r, cx + r, cy + r)
    d.pieslice(box, 180, 360, fill=SOFT, outline=INK, width=4)
    v = max(0, min(100, o["gauge"]))
    d.pieslice(box, 180, 180 + 180 * v / 100, fill=BROWN, outline=INK, width=4)
    d.pieslice((cx - r * 0.62, cy - r * 0.62, cx + r * 0.62, cy + r * 0.62), 180, 360, fill=PAPER, outline=INK, width=3)
    for k in range(0, 101, 10):
        a = math.radians(180 + 180 * k / 100)
        d.line((cx + r * 1.0 * math.cos(a), cy + r * math.sin(a), cx + r * 1.07 * math.cos(a), cy + r * 1.07 * math.sin(a)),
               fill=INK, width=3)
    a = math.radians(180 + 180 * v / 100)
    d.line((cx, cy, cx + r * 0.9 * math.cos(a), cy + r * 0.9 * math.sin(a)), fill=INK, width=8)
    d.ellipse((cx - 22, cy - 22, cx + 22, cy + 22), fill=INK)
    d.rectangle((cx - r - 40, cy + 2, cx + r + 40, cy + 40), fill=PAPER)
    d.text((cx, cy - 70), o.get("big", f"{o['gauge']} %"), font=font(HAND_BOLD, 130), fill=BROWN_DARK, anchor="ms")
    d.text((cx - r, cy + 20), "0", font=font(HAND, 40), fill=MUTED, anchor="ma")
    d.text((cx + r, cy + 20), "100", font=font(HAND, 40), fill=MUTED, anchor="ma")
    caption(d, o.get("caption", ""), y=975)


def _parcels(d, o):
    """Farmland seen from above: cols x rows parcels; with o.feed the first column turns to oats and hay."""
    kicker(d, o["kicker"])
    title(d, o.get("title", ""), size=64)
    cols, rows = o.get("cols", 4), o.get("rows", 3)
    x0, y0, x1, y1 = 330, 270, 1590, 830
    pw, ph = (x1 - x0) / cols, (y1 - y0) / rows
    feed = o.get("feed", False)
    for c in range(cols):
        for r in range(rows):
            px, py = x0 + c * pw, y0 + r * ph
            hay = feed and c == 0
            d.rectangle((px + 6, py + 6, px + pw - 6, py + ph - 6), fill=TAN if hay else GREEN_SOFT, outline=INK, width=3)
            for k in range(1, 6):  # furrows
                yy = py + 6 + k * (ph - 12) / 6
                hand_line(d, px + 24, yy, px + pw - 24, yy, BROWN if hay else GREEN, 3, seed=c + r + k, amp=1.0)
            if hay:  # a hay bale
                bx, by = px + pw / 2, py + ph / 2
                d.ellipse((bx - 40, by - 30, bx + 40, by + 30), fill=GOLD_SOFT, outline=INK, width=3)
                d.ellipse((bx - 18, by - 14, bx + 18, by + 14), outline=BROWN, width=2)
    if feed:
        d.rectangle((x0 - 4, y0 - 4, x0 + pw + 4, y1 + 4), outline=BROWN_DARK, width=6)
        d.text((x0 + pw / 2, y1 + 18), o.get("feed_label", "avena y heno"), font=font(HAND_BOLD, 46),
               fill=BROWN_DARK, anchor="ma")
        horse(d, x0 - 110, y1 + 10, 150, face=1)
    caption(d, o.get("caption", ""), y=985)


def _manure(d, o):
    """A mountain of manure next to city buildings; o.pile (0..1) sets its height."""
    kicker(d, o["kicker"])
    title(d, o.get("title", ""), size=64, width=900)
    g = max(0.05, min(1.0, o.get("pile", 1.0)))
    for k, (bx, bw, bh) in enumerate(((1180, 150, 330), (1345, 120, 470), (1480, 170, 280), (1665, 140, 400))):
        building(d, bx, GROUND, bw, bh, seed=k)
    peak = GROUND - 30 - 560 * g
    base0, base1 = 260, 1120
    pts = [(base0, GROUND)]
    for k in range(1, 20):
        t = k / 20
        bump = 14 * math.sin(k * 2.3)
        pts.append((base0 + (base1 - base0) * t, GROUND - (GROUND - peak) * math.sin(math.pi * t) ** 1.3 + bump))
    pts.append((base1, GROUND))
    d.polygon(pts, fill=BROWN, outline=INK)
    d.line(pts, fill=INK, width=3, joint="curve")
    for k in range(5):  # stink lines
        sx = 420 + k * 150
        sy = peak - 40 + 30 * math.sin(k)
        d.arc((sx - 20, sy - 70, sx + 20, sy), 100, 260, fill=GREEN, width=4)
        d.arc((sx - 20, sy - 130, sx + 20, sy - 60), -80, 80, fill=GREEN, width=4)
    if o.get("value"):
        f = _fit(d, o["value"], HAND_BOLD, 120, 880)
        d.text((690, GROUND - 120 - (GROUND - peak) * 0.45), o["value"], font=f, fill=PAPER, anchor="mm",
               stroke_width=4, stroke_fill=INK)
    caption(d, o.get("caption", ""))


def _herd(d, o):
    """Horses shrink while tractors multiply: one doodle = o.unit (default 1 million).
    o.rows: [{label, value, text, icon}]; partial values draw a cropped doodle, ghost lost ones."""
    kicker(d, o["kicker"])
    title(d, o.get("title", ""), size=64)
    y = 470
    for row in o["rows"]:
        icon = ICONS[row["icon"]]
        n, ghost = row["value"], row.get("ghost", 0)
        s = row.get("size", 84 if row["icon"] == "horse" else 130)
        per_line = row.get("per_line", 14 if row["icon"] == "horse" else 7)
        step = s * 0.98 if row["icon"] == "horse" else s * 1.18
        lines = math.ceil(max(n, ghost) / per_line)
        x0 = 640
        d.text((MARGIN, y - s * 0.9), row["label"], font=font(HAND_BOLD, 52), fill=INK)
        d.text((MARGIN, y - s * 0.9 + 64), row["text"], font=font(HAND_BOLD, 60),
               fill=COLORS.get(row.get("color", "brown"), BROWN))
        for k in range(math.ceil(max(n, ghost))):
            line, col = divmod(k, per_line)
            x, yy = x0 + col * step, y + line * s * 1.15 - (lines - 1) * s * 0.55
            if k >= n:
                icon(d, x, yy, s, fill=PAPER, outline=SLATE_SOFT)
                continue
            frac = min(1.0, n - k)
            if frac >= 0.999:
                icon(d, x, yy, s)
            else:  # a cropped doodle for the remainder (e.g. 0,7 of a horse)
                tmp = Image.new("RGBA", (int(s * 2), int(s * 1.4)), (0, 0, 0, 0))
                icon(ImageDraw.Draw(tmp), s, int(s * 1.3), s)
                keep = tmp.crop((0, 0, int(s * 0.4 + s * 1.2 * frac), tmp.height))
                d._image.paste(keep, (int(x - s), int(yy - s * 1.3)), keep)
        y += max(1, lines) * s * 1.15 + 170
    d.text((W - MARGIN, 900), o.get("unit_label", "1 dibujo = 1 millón"), font=font(HAND, 38), fill=MUTED, anchor="ra")
    caption(d, o.get("caption", ""))


def _jobs(d, o):
    """Before/after bars: a dashed ghost for before, a filled bar for after, and the change written next to it.
    o.bars: [{label, before, after, text, color}]; each bar is scaled to its own larger value."""
    kicker(d, o["kicker"])
    title(d, o.get("title", ""), size=64)
    bars = o["bars"]
    x0, x1 = 760, W - MARGIN - o.get("text_room", 300)
    row = 190
    top = 360 + (560 - row * len(bars)) // 2
    for i, b in enumerate(bars):
        y = top + i * row
        m = max(b["before"], b["after"])
        color = COLORS.get(b.get("color", "red"), RED)
        for row_k, t in enumerate(_wrap(d, b["label"], font(HAND_BOLD, 46), 520)):
            d.text((MARGIN, y + row_k * 52), t, font=font(HAND_BOLD, 46), fill=INK)
        bw = (x1 - x0) * b["before"] / m
        for xx in range(x0, int(x0 + bw), 30):
            d.line((xx, y, min(xx + 16, x0 + bw), y), fill=MUTED, width=3)
            d.line((xx, y + 80, min(xx + 16, x0 + bw), y + 80), fill=MUTED, width=3)
        d.line((x0 + bw, y, x0 + bw, y + 80), fill=MUTED, width=3)
        if b.get("show", True):
            aw = max(8, (x1 - x0) * b["after"] / m)
            d.rectangle((x0, y + 10, x0 + aw, y + 70), fill=color, outline=INK, width=3)
            d.text((max(x0 + aw, x0 + bw) + 30, y + 40), b["text"], font=font(HAND_BOLD, o.get("text_size", 64)), fill=color, anchor="lm")
    caption(d, o.get("caption", ""))


DAYS = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes"]


def _week(d, o):
    """A Monday-Friday calendar filled in slate blue, day by day, up to o.value percent of the week."""
    kicker(d, o["kicker"])
    title(d, o.get("title", ""), size=64)
    v = o.get("value", 57) / 100 * len(DAYS)
    x0, top, bottom = MARGIN + 40, 330, 790
    w = (W - 2 * MARGIN - 80) / len(DAYS)
    for i, day in enumerate(DAYS):
        x = x0 + i * w
        d.rectangle((x + 10, top, x + w - 10, bottom), fill=PAPER, outline=INK, width=3)
        d.rectangle((x + 10, top, x + w - 10, top + 70), fill=SOFT, outline=INK, width=3)
        d.text((x + w / 2, top + 35), day, font=font(HAND_BOLD, 44), fill=INK, anchor="mm")
        fill = max(0.0, min(1.0, v - i))
        if fill > 0:
            fy = top + 70 + (bottom - top - 70) * fill
            d.rectangle((x + 14, top + 74, x + w - 14, fy), fill=SLATE)
            if fill < 1:
                hand_line(d, x + 14, fy, x + w - 14, fy, INK, 4, seed=i)
        for k in range(1, 8):
            yy = top + 70 + k * (bottom - top - 70) / 8
            d.line((x + 22, yy, x + 44, yy), fill=MUTED if fill * 8 < k else SLATE_SOFT, width=2)
    d.text((W // 2, bottom + 8), o.get("big", f"{o.get('value', 57)} %"), font=font(HAND_BOLD, 110), fill=SLATE,
           anchor="ma")
    caption(d, o.get("caption", ""), y=990)


def _ratio(d, o):
    """o.hit of o.of highlighted: stick-figure workers up to 20, else a 10 x 10 grid of squares."""
    kicker(d, o["kicker"])
    title(d, o.get("title", ""), size=64)
    total, hit = o["of"], o["hit"]
    if total <= 20:
        s, step = 250, 150
        x0 = W // 2 - step * (total - 1) / 2
        for k in range(total):
            worker(d, x0 + k * step, 860, s, on=k < hit)
        d.text((W // 2, 250), o.get("big", f"{hit} de {total}"), font=font(HAND_BOLD, 170), fill=SLATE, anchor="ma")
    else:
        cell, x0, y0 = 50, MARGIN + 40, 330
        for k in range(total):
            r, c = divmod(k, 10)
            x, y = x0 + c * cell, y0 + r * cell
            d.rectangle((x, y, x + cell - 10, y + cell - 10), fill=SLATE if k < hit else PAPER, outline=INK, width=2)
        d.text((x0 + 10 * cell + 120, 360), o.get("big", f"{hit} %"), font=font(HAND_BOLD, 220), fill=SLATE)
        for j, row in enumerate(_wrap(d, o.get("label", ""), font(HAND, 52), W - MARGIN - (x0 + 10 * cell + 120))):
            d.text((x0 + 10 * cell + 120, 640 + j * 62), row, font=font(HAND, 52), fill=INK)
        return caption(d, o.get("caption", ""))
    if o.get("label"):
        d.text((W // 2, 500), o["label"], font=font(HAND, 54), fill=INK, anchor="ma")
    caption(d, o.get("caption", ""))


def _list(d, o):
    """A handwritten checklist; o.show items are ticked so far (kinetic: one more per shot)."""
    kicker(d, o["kicker"])
    items, show = o["list"], o.get("show", len(o["list"]))
    step = 118 if len(items) <= 4 else 104
    y = title(d, o.get("title", ""), size=80) + 30 if o.get("title") else 520 - step * len(items) // 2
    f = font(HAND_BOLD, 78 if len(items) <= 4 else 70)
    x = MARGIN + 120
    for i, item in enumerate(items):
        on = i < show
        d.rectangle((x + 10, y + 22, x + 76, y + 88), fill=PAPER, outline=INK if on else MUTED, width=4)
        if on:
            d.line([(x + 20, y + 52), (x + 44, y + 80), (x + 92, y + 8)], fill=SLATE, width=9, joint="curve")
        d.text((x + 130, y), item, font=f, fill=INK if on else (190, 204, 216))
        y += step
    caption(d, o.get("caption", ""))


def _text(d, o, on_photo):
    """Fallback card: kicker, a big handwritten title and a body line."""
    if on_photo:
        x, y, width = 120, 90, 900
        d.rounded_rectangle((x - 40, y - 30, x + width + 40, y + 300), radius=30, fill=SOFT + (235,), outline=INK, width=3)
        kicker(d, o.get("kicker", ""), x=x, y=y)
        y = title(d, o.get("title", ""), x=x, y=y + 80, size=64, width=width)
        for row in _wrap(d, o.get("body", ""), font(HAND, 42), width):
            d.text((x, y), row, font=font(HAND, 42), fill=TEXT)
            y += 50
        return
    if o.get("kicker"):
        kicker(d, o["kicker"])
    y = title(d, o.get("title", ""), x=W // 2, y=360, size=104, width=W - 2 * MARGIN, anchor="ma")
    for row in _wrap(d, o.get("body", ""), font(HAND, 54), W - 2 * MARGIN - 200):
        d.text((W // 2, y + 30), row, font=font(HAND, 54), fill=TEXT, anchor="ma")
        y += 66
    caption(d, o.get("caption", ""))


def _placard(d, o):
    """Text written on a blank placard in a picture: o.placard text, o.box [x0, y0, x1, y1] in frame
    pixels, optional o.strike word in red."""
    x0, y0, x1, y1 = o["box"]
    text = o["placard"]
    size = 90
    while size > 24:
        f = font(HAND_BOLD, size)
        rows = _wrap(d, text, f, x1 - x0 - 20)
        if len(rows) * size * 1.1 <= y1 - y0 - 10 and all(d.textlength(r, font=f) <= x1 - x0 - 20 for r in rows):
            break
        size -= 4
    line_h = size * 1.1
    y = (y0 + y1) / 2 - line_h * len(rows) / 2
    for k, row in enumerate(rows):
        x = (x0 + x1) / 2 - d.textlength(row, font=f) / 2
        d.text((x, y), row, font=f, fill=INK)
        hit = o.get("strike", "")
        if hit and f" {hit} " in f" {row} ":
            i = f" {row} ".index(f" {hit} ")
            sx = x + d.textlength(row[:i], font=f)
            strike(d, d.textbbox((sx, y), hit, font=f), seed=k, width=max(4, size // 10))
        y += line_h


def _note(d, o):
    """A handwritten phrase or number on top of a picture, in the empty sky: o.note, o.at [x, y], o.color."""
    x, y = o.get("at", [W // 2, 110])
    f = font(HAND_BOLD, o.get("size", 96))
    color = COLORS.get(o.get("color", "ink"), INK)
    d.text((x, y), o["note"], font=f, fill=color, anchor="ma", stroke_width=6, stroke_fill=PAPER)
    if o.get("strike"):
        box = d.textbbox((x, y), o["note"], font=f, anchor="ma")
        if o["strike"] != o["note"]:
            i = o["note"].index(o["strike"])
            left = box[0] + d.textlength(o["note"][:i], font=f)
            box = (left, box[1], left + d.textlength(o["strike"], font=f), box[3])
        strike(d, box)
    if o.get("sub"):
        d.text((x, y + f.size * 1.25), o["sub"], font=font(HAND, 52), fill=TEXT, anchor="ma",
               stroke_width=5, stroke_fill=PAPER)


FULL_FRAME = {"phrase": _phrase, "big": _stat, "gauge": _gauge, "parcels": _parcels, "pile": _manure,
              "rows": _herd, "bars": _jobs, "week": _week, "of": _ratio, "list": _list}
ON_PHOTO = {"placard": _placard, "note": _note}


def overlay_card(o: dict, out: Path, on_photo: bool) -> Path:
    for kind, draw in FULL_FRAME.items():
        if kind in o:
            if on_photo:
                raise ValueError(f"a {kind!r} graphic fills the frame; give the shot no prompt")
            img = paper()
            draw(ImageDraw.Draw(img), o)
            img.save(out)
            return out
    if on_photo:
        img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        d = ImageDraw.Draw(img)
        for kind, draw in ON_PHOTO.items():
            if kind in o:
                draw(d, o)
                break
        else:
            _text(d, o, True)
        img.save(out)
        return out
    for kind in ON_PHOTO:
        if kind in o:
            raise ValueError(f"a {kind!r} overlay goes on a picture; give the shot a prompt")
    img = paper()
    _text(ImageDraw.Draw(img), o, False)
    img.save(out)
    return out

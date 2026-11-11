"""Write storyboards/sparseup/moduleN.yaml for the SPARSEUP paper-breakdown (video 9).

The script follows /workspace/direction/sparseup/storyboard.md. Graphics already drawn
at 1920×1080 live in /workspace/direction/sparseup/assets/; this copies or crops them
into assets/images/sparseup/moduleN/<id>.png (or .jpg for the character stills).
CARD shots are editorial text_overlay (no photo). Module 1 has no title card; modules
2-11 open with a 2 s title card. The last module ends with 2 s of silence and the
series card. On screen, only figures that appear in the script.

Run from the repo root:
  .venv/bin/python -m scripts.make_sparseup_boards
"""
from __future__ import annotations

import shutil
from pathlib import Path

import yaml
from PIL import Image, ImageDraw, ImageEnhance, ImageFilter, ImageFont

from scripts.make_japon_boards import NoAliases
from studio.parse import parse_script
from studio.storyboard import check_coverage, load as load_board

ROOT = Path(__file__).resolve().parents[1]
SRC = Path("/workspace/direction/sparseup/assets")
PIC = ROOT / "assets/images/sparseup/pictures"
OUT = ROOT / "storyboards/sparseup"
IMAGES = ROOT / "assets/images/sparseup"
SCRIPT = ROOT / "examples/sparseup.md"
FONTS = ROOT / "assets/fonts"
W, H = 1920, 1080

STYLE = (
    "Cinematic photorealistic still, 16:9, shot on 35 mm film, warm muted natural window light, "
    "low saturation, fine film grain, light haze, calm quiet mood, generous negative space. "
    "No text, no letters, no numbers, no logos, no brand marks, no real people."
)
CHARACTER = (
    "The recurring AI character from the reference image: a person whose head is a faceless smooth "
    "matte white mannequin head with no eyes, no mouth and no facial features; charcoal bespoke suit "
    "in a fine birdseye weave; burgundy silk tie with a small gold-cream paisley pattern; burgundy "
    "and antique-gold ornate paisley silk pocket square in the left breast pocket of the jacket "
    "(the wearer's left, which is the viewer's right); under the jacket a vivid koi fish watercolour "
    "Hawaiian shirt in blue, gold and orange. Hands always in plain white cotton archival gloves, "
    "or kept out of frame; never bare skin on the hands."
)

# Scene prompts (for the YAML; the files themselves are already generated).
P = {
    "pj01": "The character, in white archival gloves, stands at a tall wooden library card catalog and takes out a blank index card. Subject in the right two thirds, calm empty wall on the left.",
    "pj02": "The character stands at a wooden table beside the library card catalog and places three blank index cards in a row. Medium shot, subject on the right, empty wall on the left. White archival gloves on both hands.",
    "pj03": "The character looks closely at a small antique pocket chronometer held in white archival gloves, wooden desk, library card catalog behind. Subject on the right, empty wall on the left.",
    "pj04": "The character, medium shot, holds a blank index card in a gloved hand, mannequin head turned toward camera, standing beside the wooden card catalog. Empty band at the bottom for a caption.",
    "pj05": "Close-up of two hands in white archival gloves closing a wooden library card-catalog drawer; polished brass handle, warm afternoon light.",
    "graf": "Editorial cream-paper graphic, no photo.",
}


# Confirmed v2 wording (Juan, 11 Nov 2026). These shots are the only narration
# that differs from v1; the voice cache of every other line is reused:
#   m8-11a  legal/finanzas, with «sin destilación» / «esa comparación»
#   m11-02  BRIGHT-Pro y FreshStack, frente al modelo denso con los mismos datos
#   m11-03a/b  receta habitual de SPLADE → encoders dispersos eficaces
# The Tabla 2 legal graphic (a18a_tabla2_legal.png) already shows «sin destilación».

TITLES = {
    2: "Cómo busca un sistema de IA",
    3: "El atasco",
    4: "Tres cambios",
    5: "1 · Desplazar las puntuaciones",
    6: "2 · Limitar el abanico de cada palabra",
    7: "3 · Plegar el vocabulario",
    8: "Los resultados",
    9: "Los límites",
    10: "Para qué puede servir",
    11: "Final: dos décimas",
}


def _open(name: str) -> Image.Image:
    path = SRC / name
    if not path.exists():
        path = PIC / name
    return Image.open(path).convert("RGB")


def _save(im: Image.Image, dest: Path) -> None:
    dest.parent.mkdir(parents=True, exist_ok=True)
    if dest.suffix.lower() in {".jpg", ".jpeg"}:
        im.resize((W, H), Image.Resampling.LANCZOS).save(dest, quality=92, subsampling=0)
    else:
        im.resize((W, H), Image.Resampling.LANCZOS).save(dest)


def copy_full(name: str, dest: Path) -> None:
    _save(_open(name), dest)


def focus(name: str, box: tuple[int, int, int, int], dest: Path, margin: int = 40) -> None:
    """Crop the largest 16:9 window inside box=(x0,y0,x1,y1) and scale to 1920×1080."""
    im = _open(name)
    iw, ih = im.size
    sx, sy = iw / W, ih / H
    x0, y0, x1, y1 = box
    x0, y0, x1, y1 = x0 * sx, y0 * sy, x1 * sx, y1 * sy
    x0, y0 = max(0, x0 - margin * sx), max(0, y0 - margin * sy)
    x1, y1 = min(iw, x1 + margin * sx), min(ih, y1 + margin * sy)
    bw, bh = x1 - x0, y1 - y0
    # Largest 16:9 rectangle *inside* the box, so a left-column crop does not
    # leak the right-hand column when the box is taller than 16:9.
    if bw / bh > 16 / 9:
        nw = bh * 16 / 9
        cx = (x0 + x1) / 2
        x0, x1 = cx - nw / 2, cx + nw / 2
    else:
        nh = bw * 9 / 16
        cy = (y0 + y1) / 2
        y0, y1 = cy - nh / 2, cy + nh / 2
    crop = im.crop((int(x0), int(y0), int(min(iw, x1)), int(min(ih, y1))))
    _save(crop, dest)


def tighter(name: str, dest: Path, zoom: float = 1.22, cx: float = 0.68, cy: float = 0.52) -> None:
    """A closer 16:9 crop of a character still, around (cx, cy) as fractions."""
    im = _open(name)
    iw, ih = im.size
    nw, nh = iw / zoom, ih / zoom
    x0 = min(max(cx * iw - nw / 2, 0), iw - nw)
    y0 = min(max(cy * ih - nh / 2, 0), ih - nh)
    _save(im.crop((int(x0), int(y0), int(x0 + nw), int(y0 + nh))), dest)


def highlight_labels(name: str, active: int, dest: Path, boxes: list[tuple[int, int, int, int]]) -> None:
    """Dim every label box except `active` (0-based) on the 1920×1080 layout."""
    im = _open(name).resize((W, H), Image.Resampling.LANCZOS).convert("RGBA")
    shade = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(shade)
    for i, (x0, y0, x1, y1) in enumerate(boxes):
        if i == active:
            d.rectangle((x0 - 16, y0, x0 - 6, y1), fill=(186, 102, 48, 255))
        else:
            d.rectangle((x0, y0, x1, y1), fill=(244, 239, 227, 150))
    _save(Image.alpha_composite(im, shade).convert("RGB"), dest)


# Label blocks on a05_fig1_izquierda.png (right-hand annotations).
A05_LABELS = [
    (1288, 330, 1860, 500),  # Más a la izquierda
    (1288, 520, 1860, 680),  # Más a la derecha
    (1288, 700, 1860, 900),  # El más desplazado
]



def copy_padded(name: str, dest: Path, pad: float = 0.05) -> None:
    """Place the full graphic on a cream field so an 8 % Ken Burns still leaves a margin."""
    im = _open(name).resize((W, H), Image.Resampling.LANCZOS)
    canvas = Image.new("RGB", (W, H), im.getpixel((2, 2)))
    nw, nh = int(W * (1 - 2 * pad)), int(H * (1 - 2 * pad))
    canvas.paste(im.resize((nw, nh), Image.Resampling.LANCZOS), ((W - nw) // 2, (H - nh) // 2))
    _save(canvas, dest)


# White cards on a17_tabla2_bright_freshstack.png (BRIGHT-Pro, then FreshStack).
A17_CARDS = [
    (122, 332, 1798, 578),
    (122, 622, 1798, 868),
]

# Rows on a13_ficha_modelo.png: base+data, authors, weights.
A13_ROWS = [
    (80, 350, 1840, 520),   # red de base + datos
    (80, 530, 1840, 790),   # autores, dónde, publicado
    (80, 800, 1840, 890),   # pesos
]


def lotte_columns(dest: Path) -> None:
    """Blow up LoTTE Forum / LoTTE Search next to the model names, keeping the title."""
    im = _open("a19_lotte_tabla2.png").resize((W, H), Image.Resampling.LANCZOS)
    paper = im.getpixel((20, 20))
    canvas = Image.new("RGB", (W, H), paper)
    # Tight title band (kicker + heading).
    canvas.paste(im.crop((0, 80, W, 320)), (0, 50))
    # Model names only (no CURE-en figures) + the LoTTE columns, all five rows.
    model = im.crop((108, 410, 318, 694))
    lotte = im.crop((1158, 410, 1466, 694))
    gap = 0
    stitched = Image.new("RGB", (model.width + gap + lotte.width, model.height), paper)
    stitched.paste(model, (0, 0))
    stitched.paste(lotte, (model.width + gap, 0))
    # Fit between the title (~y=50-290) and the caption (~y=820).
    max_h, max_w = 500, 1500
    scale = min(max_w / stitched.width, max_h / stitched.height)
    nw, nh = int(stitched.width * scale), int(stitched.height * scale)
    stitched = stitched.resize((nw, nh), Image.Resampling.LANCZOS)
    x, y = (W - nw) // 2, 300
    canvas.paste(stitched, (x, y))
    canvas.paste(im.crop((0, 800, W, 1080)), (0, 800))
    _save(canvas, dest)


def caption_bottom(name: str, title: str, body: str, dest: Path) -> None:
    """Write a two-line caption into the empty cream band at the bottom of pj04."""
    im = _open(name).resize((W, H), Image.Resampling.LANCZOS)
    d = ImageDraw.Draw(im)
    # The generated still has a solid cream band in roughly the lower 18 %.
    band_top = 900
    title_font = ImageFont.truetype(str(FONTS / "DMSerifDisplay-Regular.ttf"), 44)
    body_font = ImageFont.truetype(str(FONTS / "Inter-Regular.ttf"), 28)
    # Center in the band.
    tw = d.textlength(title, font=title_font)
    bw = d.textlength(body, font=body_font)
    d.text(((W - tw) / 2, band_top + 28), title, font=title_font, fill=(33, 35, 37))
    d.text(((W - bw) / 2, band_top + 86), body, font=body_font, fill=(130, 125, 112))
    _save(im, dest)


def title_shot(shot_id: str, title: str) -> dict:
    return {"id": shot_id, "type": "title_card", "lead_in": 2.0, "title": title,
            "subtitle": "SPARSEUP", "text": "", "motion": "none"}


def card(shot_id: str, text: str, overlay: dict, motion: str = "none") -> dict:
    return {"id": shot_id, "type": "text_overlay", "overlay": overlay, "text": text, "motion": motion}


def photo(shot_id: str, text: str, prompt: str, motion: str = "none", character: bool = False,
          lead_in: float = 0.0, tail: float = 0.0, overlay: dict | None = None) -> dict:
    d: dict = {"id": shot_id, "type": "text_overlay" if overlay else "image",
               "prompt": prompt, "text": text, "motion": motion}
    if character:
        d["character"] = True
    if lead_in:
        d["lead_in"] = lead_in
    if tail:
        d["tail"] = tail
    if overlay:
        d["overlay"] = overlay
    return d


def graf(shot_id: str, text: str, motion: str = "none") -> dict:
    return photo(shot_id, text, P["graf"], motion=motion)


# -------------------------------------------------------------------------------------------
# Shot plan: (module, shot dict, image-builder). image-builder is a callable(dest) or None.
# -------------------------------------------------------------------------------------------

def _plan() -> list[tuple[int, dict, object]]:
    L, R = (80, 200, 940, 1020), (980, 200, 1840, 1020)  # two-column cards
    shots: list[tuple[int, dict, object]] = []

    def add(module: int, shot: dict, builder=None):
        shots.append((module, shot, builder))

    # ----- Módulo 1 · Gancho (sin title_card) -----
    add(1, graf("m1-01a", "Si tomas RoBERTa-Large y lo entrenas como buscador al estilo SPLADE,"),
        lambda d: copy_full("a02a_gancho_sin_remate.png", d))
    add(1, graf("m1-01b", "el entrenamiento no arranca."),
        lambda d: copy_full("a02_gancho_no_entrena.png", d))
    add(1, graf("m1-02", "Sin un ajuste en las puntuaciones iniciales, ese modelo no entrena.", "zoom_in"),
        lambda d: copy_full("a05_fig1_izquierda.png", d))
    add(1, graf("m1-03a", "Los buscadores por vectores sí han pasado a redes más nuevas."),
        lambda d: copy_full("a04a_atasco_sin_dispersa.png", d))
    add(1, graf("m1-03b", "Los de palabras, no."),
        lambda d: copy_full("a04_atasco.png", d))
    add(1, graf("m1-04", "Un equipo de Linkup, en París, explica por qué, y cómo se arregla con tres cambios.",
                "zoom_in"),
        lambda d: copy_full("a01_portada_paper.png", d))

    # ----- Módulo 2 · Cómo busca -----
    add(2, title_shot("m2-00", TITLES[2]))
    add(2, photo("m2-01a",
                 "Hoy, cuando un agente de IA consulta un archivo, no se lee todos los documentos.",
                 P["pj01"], "pan_left", character=True),
        lambda d: copy_full("pj/pj01_fichero.jpg", d))
    add(2, photo("m2-01b", "Primero busca los trozos que parecen pertinentes.",
                 P["pj01"], "zoom_in", character=True),
        lambda d: tighter("pj/pj01_fichero.jpg", d, zoom=1.28, cx=0.72, cy=0.52))
    add(2, card("m2-02", "Esa primera búsqueda es el retriever, el buscador.",
                {"kicker": "El retriever", "title": "Retriever = el buscador", "body": ""}))
    add(2, graf("m2-03a", "Lo habitual es la búsqueda densa:"),
        lambda d: focus("a03_densa_vs_dispersa.png", L, d))
    add(2, graf("m2-03b",
                "cada texto se convierte en un vector, un punto en un espacio, y se buscan los más cercanos.",
                "zoom_in"),
        lambda d: focus("a03_densa_vs_dispersa.png", L, d))
    add(2, graf("m2-04a",
                "La búsqueda dispersa aprendida hace otra cosa. Representa cada texto como un conjunto de palabras con un peso."),
        lambda d: focus("a03_densa_vs_dispersa.png", R, d))
    add(2, graf("m2-04b",
                "Es un índice invertido, como el de toda la vida, pero el modelo aprende qué términos importan y cuáles añadir.",
                "zoom_in"),
        lambda d: focus("a03_densa_vs_dispersa.png", R, d))
    add(2, card("m2-05",
                "Según el artículo, eso permite coincidir con precisión en palabras raras, y buscar con la eficiencia de un índice.",
                {"kicker": "Según el artículo",
                 "title": "Coincidir con precisión en palabras raras",
                 "body": "Y buscar con la eficiencia de un índice"}))

    # ----- Módulo 3 · El atasco -----
    add(3, title_shot("m3-00", TITLES[3]))
    add(3, card("m3-01",
                "Durante años, la referencia ha sido la familia SPLADE, de Formal y sus coautores. Formal firma también este trabajo.",
                {"kicker": "SPLADE",
                 "from": "Formal y coautores",
                 "to": "Formal firma también este trabajo"}))
    add(3, card("m3-02a",
                "Mientras tanto, la búsqueda densa y la de interacción tardía, late interaction, del estilo ColBERT,",
                {"kicker": "Densa y tardía (ColBERT)",
                 "title": "ModernBERT · Ettin · datos más recientes",
                 "body": ""}))
    add(3, graf("m3-02b",
                "han seguido mejorando con redes de base más nuevas (backbones), como ModernBERT o Ettin, y con datos más recientes."),
        lambda d: copy_full("a04a_atasco_sin_dispersa.png", d))
    add(3, graf("m3-03",
                "La dispersa no ha dado ese salto. Esos modelos no se transfieren bien a la receta de SPLADE."),
        lambda d: copy_full("a04_atasco.png", d))
    add(3, card("m3-04",
                "Dos trabajos recientes apuntaban al vocabulario de los tokenizadores modernos, o a la escala de las cabezas del modelo.",
                {"kicker": "Dos explicaciones previas",
                 "title": "El vocabulario de los tokenizadores",
                 "body": "O la escala de las cabezas del modelo"},
                "zoom_in"))
    add(3, card("m3-05a",
                "Este artículo mira otra cosa: cómo están repartidas, al empezar, las puntuaciones que el modelo asigna a cada término del vocabulario.",
                {"kicker": "Este artículo",
                 "title": "Cómo están repartidas, al empezar, las puntuaciones",
                 "body": "Esas puntuaciones se llaman logits"},
                "zoom_out"))
    add(3, card("m3-05b", "Esas puntuaciones se llaman logits.",
                {"kicker": "Este artículo",
                 "title": "Logits",
                 "body": "Las puntuaciones que el modelo asigna a cada término"},
                "zoom_in"))
    add(3, card("m3-06a",
                "En el preentrenamiento habitual, sumar una constante a todas no cambia el resultado. El modelo no tiene por qué dejarlas en un rango concreto.",
                {"kicker": "Preentrenamiento",
                 "title": "Sumar una constante no cambia nada",
                 "body": ""},
                "zoom_out"))
    add(3, card("m3-06b",
                "Pero SPLADE convierte esas puntuaciones de una forma que sí depende de la escala.",
                {"kicker": "SPLADE",
                 "from": "Sumar una constante no cambia nada",
                 "to": "Sí depende de la escala"},
                "zoom_in"))
    add(3, graf("m3-07a",
                "Si la mayoría salen positivas, el vector inicial es denso: se activan demasiados términos."),
        lambda d: focus("a06_mecanismo_denso.png", (80, 80, 1840, 620), d))
    add(3, graf("m3-07b", "Las diferencias se comprimen, y la señal para aprender se debilita."),
        lambda d: focus("a06_mecanismo_denso.png", (80, 520, 1840, 1040), d))
    add(3, graf("m3-08", "La figura 1 lo mide en 200.000 pasajes de MS MARCO."),
        lambda d: copy_full("a05_fig1_izquierda.png", d))
    add(3, graf("m3-09a",
                "Los BERT clásicos están más a la izquierda: menos puntuaciones positivas, una representación ya en parte dispersa.",
                "zoom_in"),
        lambda d: highlight_labels("a05_fig1_izquierda.png", 0, d, A05_LABELS))
    add(3, graf("m3-09b", "ModernBERT y Ettin están más a la derecha.", "zoom_in"),
        lambda d: highlight_labels("a05_fig1_izquierda.png", 1, d, A05_LABELS))
    add(3, graf("m3-09c", "RoBERTa-Large es el más desplazado.", "zoom_in"),
        lambda d: highlight_labels("a05_fig1_izquierda.png", 2, d, A05_LABELS))
    add(3, graf("m3-10", "Y es con el que el entrenamiento no arranca, si no se corrige."),
        lambda d: copy_full("a02_gancho_no_entrena.png", d))

    # ----- Módulo 4 · Tres cambios -----
    add(4, title_shot("m4-00", TITLES[4]))
    add(4, photo("m4-01",
                 "Los autores proponen una receta de tres piezas, para esas redes modernas, sin una fase extra de preentrenamiento.",
                 P["pj02"], "zoom_in", character=True,
                 overlay={"kicker": "La receta",
                          "title": "Tres cambios",
                          "body": "Sin preentrenamiento extra"}),
        lambda d: copy_full("pj/pj02_tres_fichas.jpg", d))

    # ----- Módulo 5 · Desplazar -----
    add(5, title_shot("m5-00", TITLES[5]))
    add(5, card("m5-01",
                "La primera es el desplazamiento de logits. Antes de convertir las puntuaciones en pesos, se resta un umbral.",
                {"kicker": "1 · Desplazar las puntuaciones",
                 "title": "Se resta un umbral",
                 "body": "Antes de convertir las puntuaciones en pesos"}))
    add(5, graf("m5-02a",
                "La regla práctica: situarlo alrededor del percentil 99,9 de la distribución inicial."),
        lambda d: copy_full("a08_umbral.png", d))
    add(5, graf("m5-02b", "En ModernBERT y Ettin, usan 15. En RoBERTa-Large, 56."),
        lambda d: copy_full("a08_umbral.png", d))
    add(5, graf("m5-03",
                "Con eso, la representación arranca más dispersa, y RoBERTa-Large vuelve a entrenar.",
                "zoom_in"),
        lambda d: focus("a07_fig1_derecha.png", (80, 80, 1840, 700), d))
    add(5, graf("m5-04a", "El truco no es nuevo: ya aparecía en el trabajo de Geng y Yang."),
        lambda d: focus("a07_fig1_derecha.png", (80, 480, 1840, 1040), d))
    add(5, graf("m5-04b",
                "Aquí muestran cómo fijar el umbral, y que basta para desbloquear redes que antes fallaban o rendían por debajo.",
                "zoom_in"),
        lambda d: focus("a07_fig1_derecha.png", (80, 480, 1840, 1040), d))

    # ----- Módulo 6 · Fan-out -----
    add(6, title_shot("m6-00", TITLES[6]))
    add(6, graf("m6-01a", "La segunda es el control de abanico, el fan-out."),
        lambda d: copy_full("a09_fanout.png", d))
    add(6, graf("m6-01b",
                "Cada palabra de entrada solo puede activar, como mucho, doce términos del vocabulario, antes de agrupar el documento."),
        lambda d: copy_full("a09_fanout.png", d))
    add(6, graf("m6-02",
                "Si se deja libre, cada posición puede disparar una cola larga de términos que no aportan, y eso mete ruido.",
                "pan_right"),
        lambda d: focus("a09_fanout.png", (700, 200, 1880, 980), d))
    add(6, graf("m6-03", "Un límite de 8 o de 12 gana a no poner ninguno.", "zoom_in"),
        lambda d: focus("a10_fig2_fanout.png", (80, 200, 1000, 980), d))
    add(6, graf("m6-04a", "Y gana también a limitarse a apretar el regularizador de escasez:"),
        lambda d: focus("a10_fig2_fanout.png", (920, 200, 1860, 980), d))
    add(6, graf("m6-04b",
                "ese camino sí deja vectores más dispersos, pero pierde más calidad a igual escasez.",
                "zoom_in"),
        lambda d: focus("a10_fig2_fanout.png", (920, 200, 1860, 980), d))

    # ----- Módulo 7 · Plegado -----
    add(7, title_shot("m7-00", TITLES[7]))
    add(7, graf("m7-01a", "La tercera es el plegado del vocabulario.", "zoom_in"),
        lambda d: copy_full("a11a_paris_cuatro.png", d))
    add(7, graf("m7-01b",
                "Los tokenizadores modernos, BPE a nivel de byte, distinguen mayúsculas de minúsculas, y si un token empieza palabra o va en medio.",
                "zoom_out"),
        lambda d: copy_full("a11a_paris_cuatro.png", d))
    add(7, graf("m7-02",
                "Una sola palabra, «Paris», puede ocupar hasta cuatro entradas: paris, Paris, y las dos con la marca de inicio de palabra.",
                "zoom_in"),
        lambda d: copy_full("a11a_paris_cuatro.png", d))
    add(7, card("m7-03a", "En un buscador denso, esa redundancia queda en segundo plano.",
                {"kicker": "Densa", "title": "Queda en segundo plano", "body": ""},
                "zoom_in"))
    add(7, card("m7-03b", "En uno disperso, un término de la consulta solo coincide con la forma exacta.",
                {"kicker": "Dispersa",
                 "from": "Queda en segundo plano",
                 "to": "Solo la forma exacta"},
                "zoom_out"))
    add(7, graf("m7-04",
                "El modelo tiene que repartir el peso entre variantes, o aceptar que se le escapen coincidencias.",
                "zoom_in"),
        lambda d: copy_full("a11a_paris_cuatro.png", d))
    add(7, card("m7-05", "Geng y Yang lo resolvían cambiando el vocabulario y reentrenando.",
                {"kicker": "Geng y Yang",
                 "title": "Cambiar el vocabulario y reentrenar",
                 "body": ""}))
    add(7, graf("m7-06",
                "Aquí lo resuelven solo en la salida, sin parámetros nuevos, en el entrenamiento y en la inferencia."),
        lambda d: copy_full("a11b_paris_plegado.png", d))
    add(7, graf("m7-07", "En ModernBERT, el espacio pasa de unas 50.000 dimensiones a unas 34.000."),
        lambda d: copy_full("a11c_paris_dimensiones.png", d))
    add(7, graf("m7-08", "Sin ese plegado, el resultado medio en BEIR-13 baja de 56,4 a 55,0."),
        lambda d: copy_full("a12_sin_plegado.png", d))

    # ----- Módulo 8 · Resultados -----
    add(8, title_shot("m8-00", TITLES[8]))
    add(8, graf("m8-01",
                "Aplican la receta a la red de base de LateOn, una variante de ModernBERT, y al conjunto abierto Embeddings-Fine-Tuning.",
                "zoom_in"),
        lambda d: highlight_labels("a13_ficha_modelo.png", 0, d, A13_ROWS))
    add(8, graf("m8-02a",
                "El modelo se llama SPARSEUP. Lo firman Thibault Formal, Pierre Erbacher y Cosimo Rulli, de Linkup, en París, con contribución igual.",
                "zoom_in"),
        lambda d: copy_full("a01_portada_paper.png", d))
    add(8, graf("m8-02b", "Se publicó en arXiv el 6 de noviembre de 2026.", "zoom_in"),
        lambda d: copy_full("a01_portada_paper.png", d))
    add(8, graf("m8-03", "Los pesos están en Hugging Face."),
        lambda d: highlight_labels("a13_ficha_modelo.png", 2, d, A13_ROWS))
    add(8, graf("m8-04a",
                "En BEIR-13, trece pruebas de búsqueda, el nDCG a diez medio, que mide si lo pertinente sale arriba en la lista, es 56,4."),
        lambda d: copy_full("a14a_tabla1_solo_sparseup.png", d))
    add(8, graf("m8-04b",
                "Es, según los autores, el mejor resultado que conocen entre los encoders dispersos públicos de vocabulario, por debajo de 150 millones de parámetros."),
        lambda d: copy_full("a14a_tabla1_solo_sparseup.png", d))
    add(8, graf("m8-05",
                "1,8 puntos por encima del comparable más fuerte, OS-NSE doc-v3. Sin destilación."),
        lambda d: copy_full("a14_tabla1_dispersos.png", d))
    add(8, graf("m8-06a", "Como comparten red y datos con DenseOn y LateOn, la comparación es justa."),
        lambda d: copy_full("a15_comparacion_justa.png", d))
    add(8, graf("m8-06b",
                "SPARSEUP queda a 1,5 puntos de DenseOn, que saca 57,9, y a 2,5 de LateOn, que saca 58,9."),
        lambda d: copy_full("a15_comparacion_justa.png", d))
    add(8, card("m8-07",
                "Hay un matiz: el entrenamiento incluye particiones de algunas colecciones de evaluación.",
                {"kicker": "Un matiz",
                 "title": "El entrenamiento incluye particiones de algunas colecciones de evaluación",
                 "body": ""}))
    add(8, graf("m8-08a",
                "En la BEIR descontaminada, sin las consultas que ya estaban en el entrenamiento, SPARSEUP saca 57,5 y DenseOn 57,7."),
        lambda d: copy_full("a16_descontaminada.png", d))
    add(8, graf("m8-08b", "Quedan casi empatados."),
        lambda d: copy_full("a16_descontaminada.png", d))
    add(8, graf("m8-09a", "En BRIGHT-Pro, una batería de búsqueda que exige razonamiento,"),
        lambda d: highlight_labels("a17_tabla2_bright_freshstack.png", 0, d, A17_CARDS))
    add(8, graf("m8-09b",
                "saca 34,5 de nDCG a diez, 4,9 puntos por encima de DenseOn, sin destilación."),
        lambda d: highlight_labels("a17_tabla2_bright_freshstack.png", 0, d, A17_CARDS))
    add(8, graf("m8-10",
                "En FreshStack, documentos técnicos, 23,3 frente a 19,6 en alfa-nDCG a diez."),
        lambda d: highlight_labels("a17_tabla2_bright_freshstack.png", 1, d, A17_CARDS))
    add(8, graf("m8-11a",
                "En el bloque legal y financiero de MTEB obtiene, sin destilación, el mejor nDCG a diez de esa comparación, 50,3,"),
        lambda d: copy_full("a18a_tabla2_legal.png", d))
    add(8, graf("m8-11b", "frente a 49,9 de DenseOn."),
        lambda d: copy_full("a18a_tabla2_legal.png", d))
    add(8, graf("m8-12a",
                "En química, ChemTEB, gana en exhaustividad, el recall a cien documentos, con 97,5 frente a 96,9."),
        lambda d: focus("a18b_chemteb_dos_metricas.png", L, d))
    add(8, graf("m8-12b", "No gana en nDCG: DenseOn saca 76,4 y SPARSEUP, 70,8.", "pan_right"),
        lambda d: focus("a18b_chemteb_dos_metricas.png", R, d))

    # ----- Módulo 9 · Límites -----
    add(9, title_shot("m9-00", TITLES[9]))
    add(9, graf("m9-01a",
                "No gana en todas partes. En LoTTE, tanto en foros como en búsqueda, queda por detrás de los modelos densos y de interacción tardía."),
        lambda d: lotte_columns(d))
    add(9, graf("m9-01b", "El artículo no explica el motivo.", "zoom_in"),
        lambda d: lotte_columns(d))
    add(9, graf("m9-02a", "Las representaciones tampoco son limpias.", "zoom_in"),
        lambda d: copy_padded("a20_fig4_cleaver.png", d, 0.05))
    add(9, graf("m9-02b",
                "Como el tokenizador parte las palabras en subpiezas, a veces se activan términos que no vienen a cuento.",
                "zoom_in"),
        lambda d: copy_padded("a20_fig4_cleaver.png", d, 0.05))
    add(9, graf("m9-03",
                "En un ejemplo, el trozo «cle», de «cleaver», dispara también «cleavage», «Cole» o «cane». Son los llamados wacky weights, pesos disparatados."),
        lambda d: copy_padded("a20_fig4_cleaver.png", d, 0.05))
    add(9, card("m9-04a", "El abanico lo mitiga en parte, pero no lo quita.",
                {"kicker": "Los límites",
                 "title": "El abanico lo mitiga, no lo quita",
                 "body": ""}))
    add(9, card("m9-04b",
                "Las representaciones se ven menos limpias que las de Splade-v3, dicen, aunque el modelo rinde más.",
                {"kicker": "Los límites",
                 "title": "Menos limpias que Splade-v3, pero rinde más",
                 "body": ""}))
    add(9, graf("m9-05a", "El punto de partida también cuenta."),
        lambda d: copy_full("a21_sin_preentrenamiento.png", d))
    add(9, graf("m9-05b",
                "Si arrancan de un ModernBERT sin el preentrenamiento de LateOn, el resultado en BEIR-13 baja a 54,3."),
        lambda d: copy_full("a21_sin_preentrenamiento.png", d))
    add(9, graf("m9-06", "El dato de velocidad hay que tomarlo con lo que hay."),
        lambda d: copy_full("a22_latencia.png", d))
    add(9, graf("m9-07a",
                "El artículo afirma que recupera en menos de un milisegundo por consulta, con el motor Seismic."),
        lambda d: copy_full("a22_latencia.png", d))
    add(9, graf("m9-07b",
                "No detalla el hardware, el tamaño de la colección ni el protocolo de esa medida."),
        lambda d: copy_full("a22_latencia.png", d))
    add(9, graf("m9-08a", "Tampoco es el único enfoque disperso reciente."),
        lambda d: focus("a23_otros_enfoques.png", L, d))
    add(9, graf("m9-08b",
                "SlideOn supera a DenseOn y a SPARSEUP en BEIR-13, con más dimensiones distintas de cero."),
        lambda d: focus("a23_otros_enfoques.png", L, d))
    add(9, graf("m9-09",
                "Laconic, con alrededor de mil millones de parámetros, le saca 2,3 puntos.",
                "pan_right"),
        lambda d: focus("a23_otros_enfoques.png", R, d))

    # ----- Módulo 10 · Para qué puede servir -----
    add(10, title_shot("m10-00", TITLES[10]))
    add(10, graf("m10-01a",
                 "Si añaden destilación a partir de un reranker, el salto en BEIR-13 es de solo una décima."),
        lambda d: focus("a24_destilacion.png", L, d))
    add(10, graf("m10-01b",
                 "Fuera de dominio sí se nota: en legal y finanzas, el nDCG a diez sube de 50,3 a 52,6.",
                 "pan_right"),
        lambda d: focus("a24_destilacion.png", R, d))
    add(10, card("m10-02a", "El artículo no prescribe usos.",
                 {"kicker": "Para qué puede servir",
                  "title": "El artículo no prescribe usos",
                  "body": ""}))
    add(10, card("m10-02b",
                 "Sí muestra, a igualdad de datos y de red, que esta búsqueda aguanta el tipo en la búsqueda general y gana en varias pruebas técnicas, jurídicas y financieras.",
                 {"kicker": "A igualdad de datos y de red",
                  "from": "El artículo no prescribe usos",
                  "to": "Aguanta en búsqueda general; gana a DenseOn en varias pruebas técnicas, jurídicas y financieras"}))
    add(10, card("m10-02c",
                 "Encaja con lo que recuerdan al principio: coincidir con precisión en palabras raras.",
                 {"kicker": "Según el artículo",
                  "title": "Coincidir con precisión en palabras raras",
                  "body": ""}))
    add(10, photo("m10-03", "Un ejemplo, solo ilustrativo, no una afirmación del artículo.",
                  P["pj04"], character=True),
        lambda d: caption_bottom("pj/pj04_ficha_camara.jpg",
                                 "Ejemplo ilustrativo",
                                 "No es una afirmación del artículo", d))
    add(10, graf("m10-04a",
                 "En derecho, el nombre de una sentencia. En finanzas, el ticker de una empresa."),
        lambda d: focus("a25_ejemplo_ilustrativo.png", (80, 80, 1840, 760), d))
    add(10, graf("m10-04b", "Son términos que o están o no están."),
        lambda d: focus("a25_ejemplo_ilustrativo.png", (80, 80, 1840, 760), d))
    add(10, graf("m10-05",
                 "Un vector denso puede aproximarlos. Un índice de palabras puede exigir la coincidencia exacta."),
        lambda d: focus("a25_ejemplo_ilustrativo.png", (80, 700, 1840, 1040), d))
    add(10, photo("m10-06a",
                  "Para un agente que lanza muchas subconsultas sobre un corpus, el tiempo de cada búsqueda cuenta.",
                  P["pj01"], "zoom_in", character=True),
        lambda d: tighter("pj/pj01_fichero.jpg", d, zoom=1.35, cx=0.74, cy=0.55))
    add(10, photo("m10-06b", "El artículo habla de menos de un milisegundo.",
                  P["pj01"], "zoom_in", character=True,
                  overlay={"kicker": "El artículo",
                           "title": "Menos de un milisegundo",
                           "body": ""}),
        lambda d: tighter("pj/pj01_fichero.jpg", d, zoom=1.45, cx=0.76, cy=0.55))

    # ----- Módulo 11 · Final -----
    add(11, title_shot("m11-00", TITLES[11]))
    add(11, graf("m11-01a", "En la BEIR descontaminada, con los mismos datos y la misma red de base,"),
        lambda d: copy_full("a26a_final_sin_bright.png", d))
    add(11, graf("m11-01b", "la diferencia con la búsqueda densa es de dos décimas."),
        lambda d: copy_full("a26a_final_sin_bright.png", d))
    add(11, graf("m11-02",
                 "En BRIGHT-Pro y en FreshStack, queda por delante del modelo denso entrenado con los mismos datos."),
        lambda d: copy_full("a26_final_dos_decimas.png", d))
    add(11, photo("m11-03a",
                  "Con la receta habitual de SPLADE, esas redes modernas rendían por debajo o ni siquiera entrenaban.",
                  P["pj05"], character=True),
        lambda d: tighter("pj/pj05_cierra_cajon.jpg", d, zoom=2.35, cx=0.83, cy=0.26))
    add(11, photo("m11-03b",
                  "Con esta, el artículo las convierte en encoders dispersos eficaces.",
                  P["pj05"], character=True, tail=2.0),
        lambda d: tighter("pj/pj05_cierra_cajon.jpg", d, zoom=2.35, cx=0.83, cy=0.26))
    add(11, {"id": "m11-04", "type": "title_card", "lead_in": 4.0,
             "title": "temperaturacero", "subtitle": "SPARSEUP", "text": "", "motion": "none"})

    return shots


def main() -> None:
    plan = _plan()
    modules = {m.number: m for m in parse_script(SCRIPT.read_text(encoding="utf-8"))}
    OUT.mkdir(parents=True, exist_ok=True)
    for n in modules:
        shutil.rmtree(IMAGES / f"module{n}", ignore_errors=True)
        (IMAGES / f"module{n}").mkdir(parents=True, exist_ok=True)
        shots = []
        for module, shot, builder in plan:
            if module != n:
                continue
            if builder is not None:
                ext = ".jpg" if shot.get("character") else ".png"
                dest = IMAGES / f"module{n}" / f"{shot['id']}{ext}"
                builder(dest)
                if not dest.exists():
                    raise SystemExit(f"missing image for {shot['id']}: {dest}")
            shots.append(shot)
        board = {"module": n, "voice": "es-ES-AlvaroNeural", "theme": "editorial",
                 "style": STYLE, "character": CHARACTER, "shots": shots}
        header = (f"# SPARSEUP, module {n}: {modules[n].title}. Generated by scripts/make_sparseup_boards.py;\n"
                  f"# edit the plan there. Images are in assets/images/sparseup/module{n}/.\n")
        path = OUT / f"module{n}.yaml"
        path.write_text(header + yaml.dump(board, Dumper=NoAliases, allow_unicode=True,
                                           sort_keys=False, width=110), encoding="utf-8")
        check_coverage(load_board(path), modules[n])
        voiced = sum(1 for s in shots if s["text"])
        print(f"module {n}: {len(shots)} shots ({voiced} voiced)  {path}")


if __name__ == "__main__":
    main()

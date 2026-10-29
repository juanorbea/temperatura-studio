"""The full-frame graphics render at video size, and refuse to go on top of a photo."""
import pytest
from PIL import Image, ImageDraw

from studio import graphics

PILLARS = ["Inercia Institucional", "Rivalidad Geopolítica", "Modelos Históricos", "Eventos Detonantes"]
CASES = {
    "pillars": {"kicker": "Pilar 2", "pillars": PILLARS, "active": 2},
    "timeline": {"kicker": "Fecha mediana", "events": [{"year": 2039, "label": "Directrices"},
                                                       {"year": 2050, "label": "China se une"}]},
    "columns": {"kicker": "Chips for Peace", "columns": [{"title": "Sin China", "year": 2052},
                                                         {"title": "Con China", "year": 2056}], "show": 1},
    "table": {"kicker": "Diez hitos", "rows": [["Agencia", 2051], ["Directrices", 2039]]},
}


@pytest.mark.parametrize("name", CASES)
def test_full_frame_graphic_renders(tmp_path, name):
    out = graphics.overlay_card(CASES[name], tmp_path / f"{name}.png", on_photo=False)
    with Image.open(out) as img:
        assert img.size == (1920, 1080)


@pytest.mark.parametrize("name", CASES)
def test_full_frame_graphic_is_not_an_overlay(tmp_path, name):
    with pytest.raises(ValueError):
        graphics.overlay_card(CASES[name], tmp_path / "x.png", on_photo=True)


BLUEPRINT = {
    "links": {"kicker": "Cuota", "title": "La cadena", "active": 2,
              "links": [{"label": "Obleas", "value": "53 %"}, {"label": "Coater/developer", "value": "88 %"}]},
    "bars": {"kicker": "PIB", "title": "Gasto público", "bars": [{"label": "Japón", "value": 0.71, "text": "0,71 %"},
                                                                 {"label": "Alemania", "value": 0.41, "text": "0,41 %"}]},
    "points": {"kicker": "Cuota", "title": "Japón", "points": [{"x": 1988, "year_label": "80", "value": 50, "text": "50 %"},
                                                               {"x": 2024, "year_label": "Hoy", "value": 10, "text": "10 %"}]},
    "steps": {"kicker": "Rapidus", "title": "Hitos", "steps": [{"date": "2022", "label": "Nace"},
                                                              {"date": "AF 2027", "label": "Producción"}]},
    "lot": {"kicker": "Lotes", "title": "25 obleas", "lot": True},
    "places": {"kicker": "Mapa", "title": "Plantas", "places": [{"name": "Chitose", "lon": 141.65, "lat": 42.82}]},
    "path": {"kicker": "Soberanía", "title": "Un camino estrecho", "sides": ["Inacción", "Proyectos caros"],
             "path": "Tercera vía", "highlight": 2},
    "figures": {"kicker": "Dinero", "title": "Rapidus", "figures": [{"value": "5 billones ¥", "label": "necesarios"}]},
}


@pytest.mark.parametrize("name", BLUEPRINT)
def test_blueprint_graphics_render_on_paper(tmp_path, name):
    out = graphics.overlay_card(BLUEPRINT[name], tmp_path / f"{name}.png", on_photo=False, theme="blueprint")
    with Image.open(out) as img:
        assert img.size == (1920, 1080)
        assert img.convert("RGB").getpixel((10, 10)) == graphics.BLUEPRINT.paper  # off-white paper, not charcoal
    with pytest.raises(ValueError):
        graphics.overlay_card(BLUEPRINT[name], tmp_path / "x.png", on_photo=True, theme="blueprint")


def test_blueprint_title_card_and_photo_overlay(tmp_path):
    card = graphics.title_card("Los eslabones invisibles", "Bloque 3", tmp_path / "t.png", theme="blueprint")
    with Image.open(card) as img:
        assert img.convert("RGB").getpixel((10, 10)) == graphics.BLUEPRINT.paper
    over = graphics.overlay_card({"kicker": "Ajinomoto", "title": "Película ABF", "body": "Aislante"},
                                 tmp_path / "o.png", on_photo=True, theme="blueprint")
    with Image.open(over) as img:
        assert img.mode == "RGBA" and img.getpixel((1900, 1060))[3] == 0  # photo shows through on the right


def test_unknown_theme_is_refused(tmp_path):
    with pytest.raises(ValueError, match="unknown graphics theme"):
        graphics.title_card("x", "y", tmp_path / "t.png", theme="neon")


def test_charcoal_stays_the_default(tmp_path):
    card = graphics.title_card("Título", "Módulo 1", tmp_path / "t.png")
    with Image.open(card) as img:
        r, g, b = img.convert("RGB").getpixel((10, 10))
        assert max(r, g, b) < 80  # dark charcoal


EDITORIAL = {
    "people": {"kicker": "2025", "title": "Plazos", "highlight": 1,
               "people": [{"name": "A", "org": "X", "quote": "Ya", "when": "2-3 años"}, {"name": "B", "org": "Y"}]},
    "lit": {"kicker": "Mapa", "title": "Consenso", "lit": [{"name": "San Francisco", "lon": -122.4, "lat": 37.8}],
            "regions": [{"name": "Europa", "lon": 10, "lat": 50}]},
    "loop": {"kicker": "Bucle", "title": "La IA mejora a la IA", "loop": ["a", "b", "c"], "step": 2},
    "icons": {"kicker": "Energía", "title": "Centrales", "icons": 92, "shown": 40},
    "jcurve": {"kicker": "Cuándo", "title": "Curva en J", "jcurve": ["Baja", "Sube"], "phase": 1},
    "contrast": {"kicker": "Crecimiento", "contrast": "+0,5", "big": "20-30 %", "grow": 0.5},
    "bars": BLUEPRINT["bars"],
}


@pytest.mark.parametrize("theme", ["editorial", "blueprint"])
@pytest.mark.parametrize("name", EDITORIAL)
def test_paper_graphics_render_in_both_paper_themes(tmp_path, theme, name):
    out = graphics.overlay_card(EDITORIAL[name], tmp_path / f"{name}.png", on_photo=False, theme=theme)
    with Image.open(out) as img:
        assert img.size == (1920, 1080)


def test_editorial_theme_does_not_leak_into_blueprint(tmp_path):
    graphics.title_card("Título", "Introducción", tmp_path / "e.png", theme="editorial")
    graphics.title_card("Título", "Introducción", tmp_path / "b.png", theme="blueprint")
    with Image.open(tmp_path / "e.png") as e, Image.open(tmp_path / "b.png") as b:
        assert e.getpixel((5, 5)) == graphics.EDITORIAL.paper
        assert b.getpixel((5, 5)) != graphics.EDITORIAL.paper


PIZARRA = {
    "phrase": {"phrase": "las personas no somos caballos", "quote": True, "strike": "no", "note": "Se equivocan"},
    "stat": {"big": "6,6 millones", "label": "de caballos", "icon": "horse", "icons": 3},
    "gauge": {"gauge": 89, "kicker": "1920", "title": "Fuerza de tiro"},
    "parcels": {"parcels": True, "kicker": "1880-1920", "feed": True},
    "manure": {"pile": 1.0, "value": "900-1.800 t", "kicker": "Nueva York"},
    "herd": {"kicker": "Granjas", "rows": [{"label": "Caballos", "text": "3 M", "icon": "horse", "value": 3, "ghost": 26.7},
                                           {"label": "Tractores", "text": "4,5 M", "icon": "tractor", "value": 4.5}]},
    "jobs": {"kicker": "1910-1930", "bars": [{"label": "Mozos", "before": 100, "after": 10, "text": "-90 %"}]},
    "week": {"week": True, "value": 57, "kicker": "Semana"},
    "ratio": {"of": 10, "hit": 8, "kicker": "Ocupaciones"},
    "grid": {"of": 100, "hit": 59, "kicker": "Empleos"},
    "list": {"kicker": "Eran", "list": ["mejores", "más rápidas"], "show": 1},
    "text": {"kicker": "Tesis", "title": "Tú eres el próximo caballo"},
}


@pytest.mark.parametrize("name", PIZARRA)
def test_pizarra_graphics_render_on_light_blue_with_the_ground_line(tmp_path, name):
    out = graphics.overlay_card(PIZARRA[name], tmp_path / f"{name}.png", on_photo=False, theme="pizarra")
    with Image.open(out) as img:
        rgb = img.convert("RGB")
        assert img.size == (1920, 1080)
        assert rgb.getpixel((10, 10)) == (228, 244, 253)     # #e4f4fd paper
        assert rgb.getpixel((10, 1070)) == (201, 233, 252)   # #c9e9fc band under the ground line


def test_pizarra_overlays_on_a_picture_are_transparent_and_full_frame_ones_refuse(tmp_path):
    over = graphics.overlay_card({"placard": "las personas no somos caballos", "box": [100, 100, 600, 400],
                                  "strike": "no"}, tmp_path / "p.png", on_photo=True, theme="pizarra")
    with Image.open(over) as img:
        assert img.mode == "RGBA" and img.getpixel((1900, 1060))[3] == 0
    with pytest.raises(ValueError):
        graphics.overlay_card(PIZARRA["gauge"], tmp_path / "x.png", on_photo=True, theme="pizarra")
    with pytest.raises(ValueError):
        graphics.overlay_card({"note": "hola"}, tmp_path / "x.png", on_photo=False, theme="pizarra")
    card = graphics.title_card("Tú eres el próximo caballo", "Introducción", tmp_path / "t.png", theme="pizarra")
    with Image.open(card) as img:
        assert img.convert("RGB").getpixel((10, 10)) == (228, 244, 253)


def _glyph(text):
    img = Image.new("RGB", (200, 120), "white")
    graphics.draw_text(ImageDraw.Draw(img), (20, 20), text, graphics.font("Inter-Bold.ttf", 80), "black")
    return img


def test_chinese_characters_draw_with_the_cjk_font():
    # with a font that lacks them, both would be the same empty box
    assert _glyph("禁").tobytes() != _glyph("限").tobytes()
    assert graphics.cjk_font(graphics.font("Inter-Bold.ttf", 40)).path.endswith("NotoSerifCJKsc-Bold.otf")
    assert graphics.cjk_font(graphics.font("Inter-Regular.ttf", 40)).path.endswith("NotoSerifCJKsc-Regular.otf")


def test_text_without_chinese_draws_exactly_as_before():
    a = Image.new("RGB", (400, 120), "white")
    b = a.copy()
    f = graphics.font("Inter-Regular.ttf", 40)
    ImageDraw.Draw(a).text((10, 10), "Catálogo «J»", font=f, fill="black")
    graphics.draw_text(ImageDraw.Draw(b), (10, 10), "Catálogo «J»", f, "black")
    assert a.tobytes() == b.tobytes()


def test_opinion_tab_in_copper_only_when_asked(tmp_path):
    card = {"kicker": "Idea 1", "title": "De defenderse a imponer"}
    plain = graphics.overlay_card(card, tmp_path / "a.png", on_photo=False, theme="blueprint")
    tab = graphics.overlay_card({**card, "opinion": True}, tmp_path / "b.png", on_photo=False, theme="blueprint")
    with Image.open(plain) as a, Image.open(tab) as b:
        assert a.convert("RGB").getpixel((1700, 20)) != graphics.BLUEPRINT.accent
        assert b.convert("RGB").getpixel((1700, 20)) == graphics.BLUEPRINT.accent
    only = graphics.overlay_card({"opinion": True}, tmp_path / "c.png", on_photo=True, theme="blueprint")
    with Image.open(only) as c:
        assert c.getpixel((960, 540))[3] == 0 and c.getpixel((1700, 20))[3] == 255


def test_vermilion_is_the_one_new_colour():
    assert graphics.VERMILION == (178, 52, 40)
    assert graphics.VERMILION not in {getattr(graphics.BLUEPRINT, f) for f in graphics.BLUEPRINT.__dataclass_fields__}

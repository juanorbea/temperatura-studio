"""The full-frame graphics render at video size, and refuse to go on top of a photo."""
import pytest
from PIL import Image

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

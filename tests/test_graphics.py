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

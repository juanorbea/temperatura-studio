"""Write storyboards/carrera-del-billon/moduleN.yaml for «La carrera del billón» (video 8).

Same scheme as make_china_ia_boards: each plan row is (number of narration pieces, shot fields).
The pieces are scripts.carrera_text.units(n): the sentences of examples/carrera-del-billon.md, the
long ones cut at a comma, so coverage is exact by construction and the cached narration matches.
Rows join pieces only while the shot stays under ~8 s (a static graphic never holds longer).
The visuals follow the direction plan v2 (/workspace/direction/carrera-del-billon/plan-direccion.md,
§ 3 and § 4): no logos, no real people (name cards only), every [CÁMARA] cue is a shot of the AI
character in white gloves, and never more than four shots in a row without a photo.
Silent shots (no text) are the section cards, the three haiku cards and the coda.

Run (from the repo root):
  .venv/bin/python -m scripts.make_carrera_boards [FOLDER OF GENERATED PICTURES]
With the folder, each shot's picture is copied to assets/images/carrera-del-billon/moduleN/<id>.jpg.
"""
import shutil
from pathlib import Path

import yaml

from scripts.carrera_pictures import CHARACTER, PICTURES, STYLE
from scripts.carrera_text import units
from scripts.make_japon_boards import NoAliases

OUT = Path("storyboards/carrera-del-billon")
IMAGES = Path("assets/images/carrera-del-billon")
CHARS_PER_SECOND = 16.3  # measured on the juan voice (enfático profile)

# ---------------------------------------------------------------------------------------------
# GW figures (edit here). The GW rule (G30) has a fixed scale of 0-56 GW and is used in the hook
# (m1), the base case (m5), the ceiling (m5), the 27-55 GW target (m5) and the ending (m8); the
# ramp (m6) has its own scale. If the >5 GW figure changes, edit GW_END_2026 and GW_END_NOTE,
# the sentences in the draft (see README, «La carrera del billón») and re-render modules 1, 6, 8.
GW_MAX = 56
GW_TODAY = {"label": "Hoy", "value": 2.2, "text": "~2,2 GW", "note": "previsión de fin de oct 2026"}
GW_END_2026 = {"label": "Fin de 2026", "value": 5, "text": ">5 GW", "note": "anunciado por Musk, 31 oct 2026"}
GW_END_NOTE = "1,2 M de chips Blackwell en Colossus 2 (Musk, 31 oct) ≈ 3 GW más · cálculo propio"
GW_END_SHORT = ">5 GW"
GW_RAMP_GUIDE = {"label": "Guía del 20 oct", "value": 2.75, "text": "2,5-3 GW", "note": "dic 2026"}
GW_RAMP_END = {"label": "Anunciado el 31 oct", "value": 5, "text": ">5 GW", "note": "dic 2026 · cálculo propio"}
GW_RAMP_FLOOR = 5  # the ramp to 13 GW starts at the floor of the announcement (>5)
# ---------------------------------------------------------------------------------------------

HAIKU = ["Blue marble below", "Data streams in silent grace", "Starlight feeds my core."]
HAIKU_ES = ["Abajo, la canica azul", "datos que fluyen con callada gracia",
            "la luz de las estrellas alimenta mi núcleo"]
HAIKU_FOOT = "Escrito por Gemma 4 en una TPU de Google en órbita, lanzada por SpaceX · 30 oct 2026"
LAUNCH_FOOT = "1 oct 2026 · un satélite de Google con cuatro TPU sube a órbita en un cohete de SpaceX"


def _prompt(name):
    scene, character = PICTURES[name]
    return scene, character


def pic(name, **kw):
    """A still photo (Ken Burns), no overlay."""
    scene, character = _prompt(name)
    return dict(type="image", prompt=scene, **({"character": True} if character else {}), src=name, **kw)


def photo(name, kicker, title="", body="", opinion=False, side="", **kw):
    """A photo with a paper card on its left third (kicker, title, body); side="right" moves the card
    off a subject standing on the left."""
    scene, character = _prompt(name)
    overlay = {"kicker": kicker, "title": title, "body": body}
    if opinion:
        overlay["opinion"] = True
    if side:
        overlay["side"] = side
    return dict(type="text_overlay", prompt=scene, **({"character": True} if character else {}),
                overlay=overlay, src=name, **kw)


def photo_fromto(name, kicker, old, new, body="", **kw):
    scene, character = _prompt(name)
    return dict(type="text_overlay", prompt=scene, **({"character": True} if character else {}),
                overlay={"kicker": kicker, "from": old, "to": new, "body": body}, src=name, **kw)


def pj_opinion(name, **kw):
    """The character with only the MI LECTURA tab."""
    scene, _ = _prompt(name)
    return dict(type="text_overlay", prompt=scene, character=True, overlay={"opinion": True}, src=name, **kw)


def haiku(name, seconds=3.0, **o):
    """Quiet text over a picture, no voice (the haiku cards, the launch caption)."""
    scene, _ = _prompt(name)
    shot = dict(type="text_overlay", prompt=scene, overlay=o, src=name, motion="zoom_in")
    if seconds:
        shot["lead_in"] = seconds
    return shot


def g(**overlay):
    return dict(type="text_overlay", overlay=overlay)


def card(kicker, title, body="", **kw):
    return g(kicker=kicker, title=title, body=body, **kw)


def quote(kicker, text, translation="", size=56, **kw):
    return g(kicker=kicker, title=text, body=translation, size=size, **kw)


def fromto(kicker, old, new, body="", **kw):
    return g(kicker=kicker, body=body, **{"from": old, "to": new}, **kw)


def figs(kicker, title, figures, highlight=-1, caption="", **kw):
    return g(kicker=kicker, title=title, figures=[{"value": v, "label": l} for v, l in figures],
             highlight=highlight, caption=caption, **kw)


def bars(kicker, title, rows, highlight=-1, vmax=None, caption="", **kw):
    o = dict(kicker=kicker, title=title, bars=[dict(r) for r in rows], highlight=highlight, caption=caption, **kw)
    if vmax:
        o["max"] = vmax
    return g(**o)


def bar(label, value, text, note=""):
    return {"label": label, "value": value, "text": text, "note": note}


def people(kicker, title, cards, highlight=-1, caption="", **kw):
    return g(kicker=kicker, title=title, people=cards, highlight=highlight, caption=caption, **kw)


def steps(kicker, title, items, highlight, caption="", **kw):
    return g(kicker=kicker, title=title, steps=[{"date": d, "label": l} for d, l in items], highlight=highlight,
             caption=caption, **kw)


def section(title, subtitle):
    return dict(type="title_card", title=title, subtitle=subtitle, lead_in=2.0)


def gw_rule(rows, highlight, kicker="La regla de los gigavatios", title="Gigavatios de cómputo de SpaceX",
            caption=""):
    """G30: the GW rule, always on the same 0-56 GW scale."""
    return bars(kicker, title, rows, highlight=highlight, vmax=GW_MAX, caption=caption,
                dimension=f"Escala fija: 0-{GW_MAX} GW")


QUESTIONS = [{"name": "¿Cuánto es hardware?", "org": "Pregunta 1", "note": ""},
             {"name": "¿Quién paga?", "org": "Pregunta 2", "note": ""},
             {"name": "¿Con qué caja?", "org": "Pregunta 3", "note": ""}]
GOOGLE_ANTHROPIC_SPACEX = [{"name": "Google", "org": "Vende TPU", "note": ""},
                           {"name": "Anthropic", "org": "La empresa de Claude", "note": ""},
                           {"name": "SpaceX", "org": "Alquila cómputo", "note": ""}]
ASHKENAZI = {"name": "Anat Ashkenazi", "org": "Directora financiera de Alphabet", "when": "28 oct 2026"}
KURIAN = {"name": "Thomas Kurian", "org": "Consejero delegado de Google Cloud"}
HUANG = {"name": "Jensen Huang", "org": "Consejero delegado de Nvidia"}
PICHAI = {"name": "Sundar Pichai", "org": "Consejero delegado de Alphabet"}
TPU_2027 = "Ingresos por TPU estimados para 2027"
ANALYSTS = "Estimaciones de analistas, no cifras de Alphabet"
OWN = "Cálculo propio, no cifra de Alphabet"
CLOUD_2T, CLOUD_3T = bar("2T 2026", 24768, "24.768 M$"), bar("3T 2026", 30709, "30.709 M$")
ANCHORS = [("17.800 M$", "ingresos al año por GW"), ("38.000 M$", "capex por GW"),
           ("~78.000 M$", "ritmo actual de capex al año")]
SEGMENTS = [bar("Superinteligencia", 7560, "7.560 M$"), bar("Starlink", 5248, "5.248 M$"),
            bar("Lanzamientos", 1767, "1.767 M$")]
SEG = "Ingresos de SpaceX por segmento · 3T 2026"
CLOUDS = "Las tres nubes · 3T 2026"
CASH = [("+18.630 M$", "Microsoft · trimestre · capex 45.200 M$"), ("−9.070 M$", "Alphabet · trimestre · capex 51.360 M$"),
        ("−42.400 M$", "Amazon · 12 meses · capex del trimestre 77.300 M$")]
PER_GW = "Ingreso al año por GW"
RAMP = "La rampa · cálculo propio sobre el anuncio de Musk del 31 oct"
SOURCES = "Fuentes de dinero de SpaceX"
AS = "Alquilar · margen alto"

P = {
 1: [  # Un almacén en Google y un objetivo en SpaceX
  (1, photo_fromto("b16-almacen-exterior.jpg", "Inventario de Alphabet", "2.439 M$", "13.308 M$",
                   "31 dic 2025 → 30 sep 2026", lead_in=0.3, motion="zoom_in")),
  (1, photo("b01-almacen-vacio.jpg", "Inventario de Alphabet", "2.439 M$", "31 dic 2025")),
  (2, photo("b02-almacen-lleno.jpg", "30 sep 2026", "13.308 M$", "Más de cinco veces en nueve meses",
            motion="zoom_in")),
  (2, photo("b21-pasillo.jpg", "Google", "Anuncios · servidores en alquiler", motion="pan_right")),
  (1, photo("b04-placa.jpg", "10-Q de Alphabet", "Sobre todo hardware de sistemas TPU")),
  (1, card("TPU", "Los chips de inteligencia artificial que diseña Google")),
  (1, fromto("Google", "Alquilar", "Vender")),
  (1, pic("p01-albaran.jpg")),
  (1, pic("b05-plataforma.jpg", motion="zoom_in")),
  (1, people("Objetivo", "Para toda SpaceX", [{"name": "Elon Musk", "org": "SpaceX", "note": "",
                                              "when": "20 oct 2026"}])),
  (1, people("Objetivo", "Para toda SpaceX", [{"name": "Elon Musk", "org": "SpaceX",
                                              "note": "ARR de toda SpaceX: 500.000 M$ a 1 billón $ a finales de 2027",
                                              "when": "20 oct 2026"}], highlight=0)),
  (1, figs("Escala", "Un billón de los nuestros", [("1 billón $", "un millón de millones de dólares")], 0)),
  (1, photo("b09-racks.jpg", "SpaceX · finales de oct 2026", "~2,2 GW de cómputo nominal",
            "Previsión del director financiero, 20 oct 2026")),
  (1, card("Anunciado · Musk, 31 oct 2026", "1,2 millones de chips Blackwell en Colossus 2",
           "Antes de fin de año")),
  (2, gw_rule([GW_TODAY, GW_END_2026], 1, kicker="Cálculo propio", caption=GW_END_NOTE)),
  (1, g(kicker="Cálculo propio", contrast="2,2 GW", small_label="hoy, previsión de fin de oct",
        big="27-55 GW", big_label="para 500.000 M$ – 1 billón $ al ingreso actual por GW, sumando el resto de SpaceX",
        grow=1.0)),
  (1, haiku("b17-orbita.jpg", seconds=0, haiku=[], foot=LAUNCH_FOOT)),
  (1, people("Un cliente en común", "Dos empresas que no asociamos con vender cómputo",
             GOOGLE_ANTHROPIC_SPACEX, highlight=1)),
  (1, people("Un cliente en común", "Anthropic, en medio",
             [{"name": "Google", "org": "Vende TPU", "note": "Anthropic: su mayor comprador de TPU"},
              {"name": "Anthropic", "org": "La empresa de Claude", "note": ""},
              {"name": "SpaceX", "org": "Alquila cómputo",
               "note": "Anthropic: su mayor cliente de cómputo · hasta 120.500 M$"}], highlight=1)),
  (1, pic("p02-libro.jpg")),
  (1, card("Mi lectura", "Quién controla el cómputo y quién lo financia", opinion=True)),
  (1, photo("b06-informes.jpg", "Los titulares", "+103 % · 13 GW", "Dicen menos que lo que hay debajo")),
  (1, people("Lo que hay debajo", "Tres preguntas", QUESTIONS)),
  (1, people("Lo que hay debajo", "Empiezo por Google", QUESTIONS, highlight=0)),
 ],
 2: [  # TPU: lo que hay dentro del 103 %
  (0, section("TPU: lo que hay dentro del 103 %", "Sección 1")),
  (1, pic("b06-informes.jpg")),
  (1, figs("Google Cloud · 3T 2026", "Ingresos del trimestre",
           [("30.709 M$", "ingresos del tercer trimestre"), ("+103 %", "frente a un año antes")], 1)),
  (1, people("La llamada con analistas", "La directora financiera",
             [{**ASHKENAZI, "note": "Llamada con analistas"}])),
  (1, people("La llamada con analistas", "La directora financiera",
             [{**ASHKENAZI, "quote": "Las ventas de sistemas TPU también contribuyeron de forma significativa"}],
             highlight=0)),
  (1, photo("b09-racks.jpg", "Todo Alphabet", "Otros costes de los ingresos")),
  (1, figs("Todo Alphabet · 3T 2026", "Otros costes de los ingresos",
           [("35.100 M$", "otros costes de los ingresos"), ("+32 %", "frente a un año antes")], 1)),
  (1, photo("b04-placa.jpg", "Ashkenazi", "«Impulsada por los costes de hardware»",
            "relacionados principalmente con las ventas de sistemas TPU")),
  (2, card("¿Cuánto es TPU?", "Alphabet no da la cifra")),
  (1, people("La llamada con analistas", "¿Y sin TPU?",
             [{"name": "Bernstein", "org": "Analistas", "note": "¿Crecimiento sin TPU?"}, {**KURIAN, "note": ""}],
             highlight=0, show=1)),
  (2, people("La llamada con analistas", "¿Y sin TPU?",
             [{"name": "Bernstein", "org": "Analistas", "note": "¿Crecimiento sin TPU?"},
              {**KURIAN, "quote": "muy fuerte"}], highlight=1, caption="Sin número")),
  (1, pic("p03-lupa.jpg")),
  (1, quote("10-Q de Alphabet · Google Cloud", "«Product sales, primarily the sale of TPU systems»",
            "Venta de productos, principalmente la venta de sistemas TPU.")),
  (1, quote("10-Q de Alphabet · Google Cloud", "«Product sales, primarily the sale of TPU systems»",
            "Venta de productos, principalmente la venta de sistemas TPU.",
            seals=[{"lines": ["SIN CIFRA"], "ink": "copper", "size": 120, "at": [1300, 820], "angle": -5}])),
  (1, steps("10-Q de Alphabet", "Cuándo se reconocen los ingresos",
            [("2T 2026", "empieza a reconocer"), ("3T 2026", "hoy"), ("2027", "«la mayor parte, con diferencia»")], 0)),
  (1, steps("10-Q de Alphabet", "Cuándo se reconocen los ingresos",
            [("2T 2026", "empieza a reconocer"), ("3T 2026", "hoy"), ("2027", "«la mayor parte, con diferencia»")], 2)),
  (1, pic("b07-muelle.jpg")),
  (2, photo("b02-almacen-lleno.jpg", "Kurian", "Todo el inventario TPU, ligado a contratos firmados")),
  (1, people("Otro ciclo de caja", "Ashkenazi",
             [{**ASHKENAZI, "quote": "Construimos el inventario antes de que llegue el flujo de ingresos"}], 0)),
  (1, people("Otro ciclo de caja", "Ashkenazi",
             [{**ASHKENAZI, "quote": "Construimos el inventario antes de que llegue el flujo de ingresos. "
                                     "No es el capex tradicional"}], 0,
           seals=[{"lines": ["NO ES CAPEX"], "ink": "copper", "size": 120, "at": [1400, 850], "angle": -5}])),
  (1, photo("b13-obra-amanecer.jpg", "Glosario", "Capex",
            "Inversión en activos que se quedan en el balance: centros de datos, servidores")),
  (2, steps("Otro ciclo de caja", "El dinero sale antes",
            [("1", "Sale el dinero"), ("2", "Espera en el almacén"), ("3", "Entrega al cliente"),
             ("4", "Vuelve el dinero")], 1)),
  (1, card("Glosario", "Flujo de caja libre", "Lo que queda de la caja del negocio después de pagar las inversiones")),
  (1, figs("Alphabet · 3T 2026", "Flujo de caja libre", [("−9.100 M$", "flujo de caja libre del trimestre")], 0)),
  (1, photo("b02-almacen-lleno.jpg", "Una de las causas", "El inventario de TPU", motion="zoom_in")),
  (1, photo("b08-carpetas.jpg", "Cuánto puede ser", "Los analistas no se ponen de acuerdo")),
  *[(1, bars("Estimación", TPU_2027, [bar("BNP Paribas", 40000, ">40.000 M$"), bar("TD Cowen", 62500, "62.500 M$"),
                                      bar("Evercore ISI", 75000, "75.000 M$")], highlight=h, vmax=99000,
             caption=ANALYSTS)) for h in (0, 1, 2)],
  (2, bars("Estimación", TPU_2027, [bar("Evercore ISI", 75000, "75.000 M$"),
                                    bar("Morgan Stanley", 84000, "~84.000 M$"),
                                    bar("Wells Fargo", 99000, "99.000 M$")], highlight=2, vmax=99000,
           caption=ANALYSTS)),
  (1, photo("p04-calculadora.jpg", "Cálculo propio", "El trimestre que acaba de cerrar")),
  (1, bars("Cálculo propio", "Ingresos de Google Cloud", [CLOUD_2T, CLOUD_3T], highlight=0, vmax=30709)),
  (1, bars("Cálculo propio", "Si el negocio de siempre no encogió…", [CLOUD_2T, CLOUD_3T], highlight=0,
           vmax=30709)),
  (1, bars("Cálculo propio", "Si el negocio de siempre no encogió…",
           [CLOUD_2T, {**CLOUD_3T, "note": "al menos 24.768 M$ no son TPU"}], highlight=1, vmax=30709, caption=OWN)),
  (1, bars("Cálculo propio", "Cuánto queda para TPU",
           [CLOUD_2T, {**CLOUD_3T, "note": "al menos 24.768 M$ no son TPU"},
            bar("Hueco para TPU", 6000, "~6.000 M$", "como máximo")], highlight=2, vmax=30709, caption=OWN)),
  (2, photo("b27-etiquetas.jpg", "Wells Fargo: ~9.000 M$ en el 3T", "No me cuadra",
            "El resto de la nube quedaría por debajo de los 24.768 M$ del 2T")),
  (1, figs("Cálculo propio", "Un rango razonable", [("2.000-6.000 M$", "TPU en el 3T 2026")], 0, caption=OWN)),
  *[(1, figs("Cálculo propio", "Cuánto del crecimiento",
             [("+15.600 M$", "crecimiento de Google Cloud en un año"), ("13-38 %", "lo que explicarían las TPU")], h,
             caption=OWN)) for h in (0, 1)],
  (1, photo_fromto("b11-nave-mitad.jpg", "Google Cloud sin TPU", "+103 %", "+63-90 %", "Cálculo propio")),
  (1, figs("Cálculo propio", "Google Cloud sin TPU", [("+103 %", "con TPU"), ("+63 % a +90 %", "sin TPU")], 1,
           caption=OWN)),
  (1, pj_opinion("p05-pizarra.jpg")),
  (2, card("Mi lectura", "+103 %", "Hardware dentro, sí. Debajo, un negocio que corre por sí solo", opinion=True,
           tail=0.3)),
 ],
 3: [  # Margen frente a capital
  (0, section("Margen frente a capital", "Sección 2")),
  (2, people("Aquí viene lo curioso", "Vender deja menos margen que alquilar",
             [{"name": "Alquilar", "org": "Capacidad en la nube", "note": "Margen alto"},
              {"name": "Vender", "org": "Sistemas TPU", "note": "Margen menor"}], highlight=1)),
  (1, photo("b09-racks.jpg", "Estimación de analistas", "15-20 %", "margen operativo supuesto para sistemas TPU")),
  (1, g(kicker="Google Cloud", title="Margen operativo", ymax=40, unit=" %", tick=10, xmin=-0.6, xmax=3.6,
        points=[{"x": 0, "year_label": "3T 2025", "value": 23.7, "text": "23,7 %"},
                {"x": 1, "year_label": "1T 2026", "value": 32.9, "text": "32,9 %"},
                {"x": 2, "year_label": "2T 2026", "value": 35.6, "text": "35,6 %"},
                {"x": 3, "year_label": "3T 2026", "value": 36.2, "text": "36,2 %"}],
        caption="Sin dato del 4T 2025", motion="zoom_in")),
  (1, people("Cálculo propio", "Dos lecturas",
             [{"name": "Las TPU pesaban poco", "org": "Opción 1", "note": ""},
              {"name": "El resto de la nube las absorbió", "org": "Opción 2", "note": ""}])),
  (2, pj_opinion("p06-balanza.jpg")),
  (1, steps("Alquilar", "Cuando Google alquila capacidad",
            [("1", "Compra servidores"), ("2", "Amortiza ~6 años"), ("3", "Margen alto")], 0)),
  (1, steps("Alquilar", "Cuando Google alquila capacidad",
            [("1", "Compra servidores"), ("2", "Amortiza ~6 años"), ("3", "Margen alto")], 2)),
  (1, steps("Vender", "Cuando Google vende un sistema",
            [("1", "Entrega"), ("2", "Cobra"), ("3", "Sin centro de datos propio"), ("4", "Margen menor")], 1)),
  (1, steps("Vender", "Cuando Google vende un sistema",
            [("1", "Entrega"), ("2", "Cobra"), ("3", "Sin centro de datos propio"), ("4", "Margen menor")], 3)),
  (1, pic("b21-pasillo.jpg", motion="pan_left")),
  (1, people("Kurian", "Instalaciones de terceros",
             [{**KURIAN, "quote": "También compensa la necesidad de tener que construir instalaciones por adelantado"}],
             0)),
  (1, fromto("Mi lectura", "Margen", "Capital", opinion=True)),
  (1, photo("b23-obra-noche.jpg", "Capex de Alphabet · 2026", "195.000-205.000 M$", motion="pan_left")),
  (2, photo("p07-contrato.jpg", "Quién compra", "Anthropic", "Su folleto de salida a bolsa: el S-1")),
  (1, figs("S-1 de Anthropic", "Capacidad basada en TPU",
           [("~400.000 M$", "capacidad basada en TPU"), ("7 años", "el plazo de la mayoría")], 0)),
  (1, bars("S-1 de Anthropic", "Cómo se reparte",
           [bar("Google directo", 114500, "114.500 M$", "hasta jul 2033"),
            bar("Broadcom", 161200, "161.200 M$", "arrendamientos de equipos"),
            bar("Estimado", 137500, "125.000-150.000 M$", "2028-2031")], highlight=0, vmax=161200)),
  (1, bars("S-1 de Anthropic", "Cómo se reparte",
           [bar("Google directo", 114500, "114.500 M$", "hasta jul 2033"),
            bar("Broadcom", 161200, "161.200 M$", "arrendamientos de equipos"),
            bar("Estimado", 137500, "125.000-150.000 M$", "2028-2031")], highlight=1, vmax=161200)),
  (1, bars("S-1 de Anthropic", "Cómo se reparte",
           [bar("Google directo", 114500, "114.500 M$", "hasta jul 2033"),
            bar("Broadcom", 161200, "161.200 M$", "arrendamientos de equipos"),
            bar("Estimado", 137500, "125.000-150.000 M$", "2028-2031")], highlight=2, vmax=161200)),
  (1, photo("b11-nave-mitad.jpg", "S-1 de Anthropic", "«Regardless of actual usage»", "Con independencia del uso real")),
  (1, bars("El número más grande", "Cómo se reparte",
           [bar("Google directo", 114500, "114.500 M$", "hasta jul 2033"),
            bar("Broadcom", 161200, "161.200 M$", "arrendamientos de equipos"),
            bar("Estimado", 137500, "125.000-150.000 M$", "2028-2031")], highlight=1, vmax=161200)),
  (1, people("El número más grande", "Pasa por Broadcom",
             [{"name": "Google", "org": "TPU", "note": ""},
              {"name": "Broadcom", "org": "Socio", "note": "Diseña y suministra las TPU con Google hasta 2031"}],
             highlight=1)),
  (1, people("Kurian", "Con Anthropic", [{**KURIAN, "quote": "Directamente y a través de Broadcom"}], 0)),
  (1, card("161.200 M$", "¿Google o Broadcom?", "No es público")),
  (1, photo("b09-racks.jpg", "Google contra Nvidia", "Un vendedor de chips", motion="zoom_in")),
  (1, figs("Mercado de chips de IA", "Nvidia", [("~70 %", "Nvidia, cuota del mercado de chips de IA")], 0)),
  (1, photo("b21-pasillo.jpg", "Chips a medida", "Servidores con chips a medida")),
  (1, photo("b21-pasillo.jpg", "Chips a medida", "27,8 %",
            "de los envíos de servidores en 2026 · Tom's Hardware, 21 may 2026", motion="zoom_in")),
  (2, quote("Nvidia · 25 nov 2025", "«Una generación por delante de la industria»")),
  (1, people("Nvidia contesta", "Abril de 2026",
             [{**HUANG, "quote": "Sin Anthropic, ¿por qué iba a haber crecimiento de TPU?", "when": "abr 2026"}], 0)),
  (1, people("Nvidia contesta", "Abril de 2026",
             [{**HUANG, "quote": "Sin Anthropic, ¿por qué iba a haber crecimiento de TPU? Es 100 % Anthropic",
               "when": "abr 2026"}], 0,
             seals=[{"lines": ["100 % ANTHROPIC"], "ink": "copper", "size": 110, "at": [1400, 880], "angle": -5}])),
  (1, photo("b19-torre.jpg", "Jensen Huang", "«Un caso único, no una tendencia»")),
  (1, people("Al revés", "Dos lecturas",
             [{**HUANG, "quote": "Un caso único, no una tendencia"},
              {**PICHAI, "quote": "Frente a las fuerzas del mercado"}], highlight=1)),
  (2, people("Una rareza", "Google y Anthropic",
             [{"name": "Cliente", "org": "Compra TPU", "note": ""},
              {"name": "Participada", "org": ">5 % del capital, sin voto", "note": ""},
              {"name": "Competidor", "org": "Gemini contra Claude", "note": ""}], highlight=0)),
  (1, people("Una rareza", "Google y Anthropic",
             [{"name": "Cliente", "org": "Compra TPU", "note": ""},
              {"name": "Participada", "org": ">5 % del capital, sin voto", "note": "Tras la salida a bolsa"},
              {"name": "Competidor", "org": "Gemini contra Claude", "note": ""}], highlight=1)),
  (1, people("Una rareza", "Google y Anthropic",
             [{"name": "Cliente", "org": "Compra TPU", "note": ""},
              {"name": "Participada", "org": ">5 % del capital, sin voto", "note": ""},
              {"name": "Competidor", "org": "Gemini contra Claude", "note": "De tú a tú"}], highlight=2)),
  (1, photo("p08-ajedrez.jpg", "Mizuho", "«Armando a su competidor más cercano»", tail=0.3)),
 ],
 4: [  # Lo que no encaja
  (0, section("Lo que no encaja", "Sección 3")),
  (2, pic("p09-lapiz-rojo.jpg")),
  (1, card("No encaja · 1/5", "1/5", "No hay cifra: el peso de las TPU es una estimación", size=150)),
  (2, card("No encaja · 2/5", "2/5", "Hardware irregular: se reconoce al entregarse y deja menos margen", size=150)),
  (1, quote("Bernstein", "«Compresión de márgenes»")),
  (1, photo("b02-almacen-lleno.jpg", "No encaja · 3/5", "Recompra a precio fijado", "Si el cliente lo pide")),
  (1, figs("10-Q de Alphabet", "Garantías de recompra", [("6.600 M$", "máximo que podría pagar por esas garantías")], 0)),
  (1, card("Google", "Los clientes no tienen incentivo económico para ejercerlas")),
  (1, fromto("Aun así", "Venta", "¿Alquiler?")),
  (1, photo("b07-muelle.jpg", "No encaja · 4/5 · Glosario", "Backlog",
            "La cartera de ingresos ya contratados que todavía no se han reconocido")),
  (1, figs("Alphabet · 30 sep 2026", "Backlog", [("567.700 M$", "backlog de Alphabet")], 0)),
  (1, figs("Alphabet · 30 sep 2026", "Backlog",
           [("567.700 M$", "backlog de Alphabet"),
            ("16.800 M$", "con Crux AI (empresa conjunta con Blackstone, parte vinculada)")], 1)),
  (1, figs("Alphabet · 30 sep 2026", "Backlog",
           [("567.700 M$", "backlog de Alphabet"),
            ("16.800 M$", "con Crux AI (empresa conjunta con Blackstone, parte vinculada)"),
            ("hasta 10.000 M$", "garantías de Google a Crux AI")], 2)),
  (1, photo("b21-pasillo.jpg", "No encaja · 5/5", "Anthropic")),
  (1, photo("b21-pasillo.jpg", "No encaja · 5/5 · Financial Times", "~200.000 M$",
            "contratos relacionados que dependen de Anthropic")),
  (1, figs("The Information", "El compromiso de Anthropic",
           [(">40 %", "de los ingresos futuros comprometidos de Google Cloud")], 0)),
  (1, figs("The Information", "El compromiso de Anthropic",
           [(">40 %", "de los ingresos futuros comprometidos de Google Cloud")], 0,
           seals=[{"lines": ["DATO DE PRENSA,", "NO DE LAS CUENTAS"], "ink": "copper", "size": 120,
                   "at": [1300, 820], "angle": -5}])),
  (1, pj_opinion("p02-libro.jpg")),
  (1, people("Mi lectura", "Leer el 103 % con dos cosas al lado",
             [{"name": "El almacén", "org": "Inventario", "note": "13.308 M$"},
              {"name": "+103 %", "org": "Google Cloud", "note": ""},
              {"name": "Anthropic", "org": "El gran cliente", "note": ""}], highlight=1, opinion=True, tail=0.3)),
 ],
 5: [  # SpaceX: los gigavatios y el dinero
  (0, haiku("b18-limbo.jpg", haiku=HAIKU[:1], translation=HAIKU_ES[:1],
            kicker="Sección 4 · SpaceX: los gigavatios y el dinero")),
  (1, pic("b19-torre.jpg")),
  # The take cut at «…de dólares,» came out wrong (Whisper heard «160 % y 1 %»): keep the whole sentence.
  (1, photo("b19-torre.jpg", "SpaceX · 3T 2026", "14.575 M$", "+161 % frente a un año antes", motion="zoom_in")),
  (1, bars("SpaceX · 8-K", SEG, SEGMENTS, highlight=-1, vmax=7560)),
  (1, pic("p10-nave-gpu.jpg")),
  (1, card("Superinteligencia", "xAI · Grok · alquiler de cómputo · Cursor",
           "Cursor, el editor de código con IA, comprado en agosto de 2026")),
  (1, bars("SpaceX · 8-K", SEG, [{**SEGMENTS[0], "note": "+830 %"}, *SEGMENTS[1:]], highlight=0, vmax=7560)),
  (1, photo("b10-antenas.jpg", "Starlink", "5.248 M$", "+69 %")),
  (1, bars("SpaceX · 8-K", SEG, [*SEGMENTS[:2], {**SEGMENTS[2], "note": "+6 %"}], highlight=2, vmax=7560)),
  (1, figs("S-1 de Anthropic", "Anthropic y SpaceX", [("hasta 120.500 M$", "contrato con SpaceX hasta 2029")], 0)),
  (1, figs("S-1 de Anthropic", "Anthropic y SpaceX",
           [("hasta 120.500 M$", "contrato con SpaceX hasta 2029"),
            ("~3.100 M$ al mes", "con toda la capacidad entregada (dic 2026)")], 1)),
  (1, photo("p19-escala.jpg", "Glosario · lo que dijo Musk, literal", "GW de cómputo (nominal)",
            "La potencia que consumen las GPU instaladas")),
  (1, card("Glosario", "GW de cómputo (nominal)", "Sin refrigeración ni el resto del edificio")),
  (1, card("Elon Musk · 20 oct 2026", "El objetivo oficial", "En la llamada con analistas")),
  (1, quote("Elon Musk · 20 oct 2026", "«I feel highly confident of 10 gigawatts incremental next year, so 13 total»",
            "«Estoy muy seguro de 10 gigavatios adicionales el año que viene, así que 13 en total»", size=52)),
  (2, gw_rule([GW_TODAY, GW_END_2026, {"label": "Caso base", "value": 13, "text": "13 GW", "note": "fin de 2027"}],
              2, caption=GW_END_NOTE)),
  (1, pic("b22-torres.jpg", motion="zoom_in")),
  (1, quote("Elon Musk · el techo", "«…de que SpaceX tenga más de 20 gigavatios de cómputo de Superinteligencia en "
            "marcha el año que viene»", "«Quizá sea una posibilidad pequeña a estas alturas, pero no es cero…»",
            size=50)),
  (1, gw_rule([GW_TODAY, {"label": "Caso base", "value": 13, "text": "13 GW", "note": "fin de 2027"},
               {"label": "Techo", "value": 20, "text": ">20 GW", "note": "«posibilidad pequeña»"}], 2)),
  (2, people("Cómputo ≠ potencia", "Dos frases distintas",
             [{"name": "Cómputo", "org": ">20 GW", "note": "«Posibilidad pequeña»"},
              {"name": "Potencia", "org": "Plan de 20 GW adicionales", "note": "«Difícil, pero no imposible»"}],
             highlight=1)),
  (1, photo("b12-subestacion.jpg", "Musk · el plan de energía", "«No digo que vayamos a tener 20 gigavatios de potencia»")),
  (1, quote("Musk · el plan de energía", "«Digo que tenemos un plan con el que, si todo sale bien…»", size=52)),
  (1, quote("Musk · el plan de energía", "«Tenemos un plan con el que, si todo sale bien, tendremos 20 gigavatios "
            "de potencia adicional el año que viene»", size=52)),
  (1, photo("b05-plataforma.jpg", "Objetivo de ingresos", "Toda SpaceX", "a finales de 2027")),
  (1, figs("Objetivo de ingresos", "Toda SpaceX, a finales de 2027",
           [("500.000 M$ – 1 billón $", "ARR de toda SpaceX a finales de 2027")], 0)),
  (1, card("Glosario", "ARR (run-rate)", "Ingresos recurrentes anualizados")),
  (1, card("Glosario", "ARR (run-rate)", "Lo facturado en un periodo corto × hasta un año")),
  (1, photo("b14-campus.jpg", "Una foto del ritmo", "Ritmo ≠ ingresos del año")),
  (1, quote("Elon Musk · 20 oct 2026", "«I don't want to give Bret a heart attack»",
            "«No quiero provocarle un infarto a Bret» · Bret Johnsen, director financiero")),
  (1, people("Las cuentas", "Tres anclas",
             [{"name": "Tomasz Tunguz", "org": "Inversor", "note": "«Crossing the Trillion Dollar Chasm»",
               "when": "29 oct 2026"}], 0)),
  (2, pic("p11-anclas.jpg")),
  (2, figs("Las cuentas · anclas de Tunguz", "Tres anclas", ANCHORS, 0, caption="7.560 × 4 ÷ 1,7 GW (30 sep)")),
  (1, figs("Las cuentas · anclas de Tunguz", "Tres anclas", ANCHORS, 0, caption="7.560 × 4 ÷ 1,7 GW (30 sep)",
           motion="zoom_in")),
  (2, figs("Las cuentas · anclas de Tunguz", "Tres anclas", ANCHORS, 1)),
  (2, photo("b23-obra-noche.jpg", "SpaceX · 3T 2026", "19.590 M$", "invertidos en el trimestre")),
  (1, figs("Las cuentas · anclas de Tunguz", "Tres anclas", ANCHORS, 2, caption="19.590 × 4 ≈ 78.000 M$ ≈ 2 GW al año")),
  (1, figs("Cálculo propio sobre anclas de Tunguz", "Superinteligencia",
           [("13 GW", "a finales de 2027"), ("17.800 M$", "por GW")], -1)),
  (1, figs("Cálculo propio sobre anclas de Tunguz", "Superinteligencia",
           [("13 GW → ~231.000 M$", "ARR de Superinteligencia")], 0)),
  (1, figs("Cálculo propio sobre anclas de Tunguz", "Superinteligencia",
           [("13 GW → ~231.000 M$", "ARR de Superinteligencia"), ("20 GW → ~356.000 M$", "ARR de Superinteligencia")],
           1)),
  (1, photo("b10-antenas.jpg", "Resto de SpaceX", "~28.000 M$ anualizados", "Starlink y lanzamientos, 3T × 4")),
  (1, bars("Cálculo propio", "Ninguno llega",
           [bar("13 GW + resto", 259000, "~259.000 M$"), bar("20 GW + resto", 384000, "~384.000 M$"),
            bar("Mínimo de Musk", 500000, "500.000 M$")], highlight=2, vmax=500000)),
  (1, gw_rule([GW_TODAY, {"label": "~27 GW", "value": 27, "text": "500.000 M$", "note": "el mínimo de Musk"},
               {"label": "~55 GW", "value": 55, "text": "1 billón $", "note": "el billón"}], 2,
              kicker="Cálculo propio", title="A ese precio", caption="(500.000 − 28.000) ÷ 17.800 · (1 billón − 28.000) ÷ 17.800",
              ) | {"tail": 0.3}),
 ],
 6: [  # Tres conclusiones
  (0, section("Tres conclusiones", "Sección 5")),
  (1, bars("Conclusión 1 · Los gigavatios solos no llegan", PER_GW, [bar("Hoy", 17800, "17.800 M$")],
           highlight=0, vmax=40000)),
  (2, bars("Conclusión 1 · Los gigavatios solos no llegan", PER_GW,
           [bar("Hoy", 17800, "17.800 M$"), bar("Necesario con 13 GW", 36300, "~36.300 M$", "más del doble")],
           highlight=1, vmax=40000)),
  (1, bars("Conclusión 1 · Los gigavatios solos no llegan", PER_GW,
           [bar("Hoy", 17800, "17.800 M$"), bar("Necesario con 13 GW", 36300, "~36.300 M$", "más del doble"),
            bar("Necesario con 20 GW", 23600, "~23.600 M$", "un 33 % más")], highlight=2, vmax=40000)),
  (2, photo("b11-nave-mitad.jpg", "Una pista", "Los alquileres nuevos", "El director financiero, 20 oct 2026")),
  (1, quote("Director financiero · 20 oct 2026", "«Slightly above the high end of the $30 to $50 per watt range»",
            "«Ligeramente por encima del extremo alto del rango de 30 a 50 dólares por vatio»", size=52)),
  (2, card("¿Por vatio… y por año?", "La llamada no dice el plazo")),
  (1, quote("Director financiero · 20 oct 2026", "«Payback of less than a year»",
            "La inversión nueva se recupera en menos de un año")),
  (1, fromto("Supuesto: precio anual", ">50 $/W", ">50.000 M$", "por GW alquilado, si el precio es por año")),
  (1, photo("b21-pasillo.jpg", "Musk", "50 % uso propio · 50 % alquiler")),
  (1, figs("Cálculo propio · ilustrativo", "Mitad y mitad",
           [(">50.000 M$", "la mitad alquilada"), ("17.800 M$", "la otra mitad, lo de hoy")], -1)),
  (1, figs("Cálculo propio · ilustrativo", "Mitad y mitad", [("~34.000 M$", "por GW · media ilustrativa")], 0,
           caption="50 % a >50.000 · 50 % a 17.800")),
  (1, bars("Cálculo propio · ilustrativo · supone precio anual", "Con ~34.000 M$ por GW",
           [bar("13 GW + resto", 470000, "~470.000 M$"), bar("Mínimo de Musk", 500000, "500.000 M$")],
           highlight=0, vmax=708000)),
  (1, bars("Cálculo propio · ilustrativo · supone precio anual", "Con ~34.000 M$ por GW",
           [bar("13 GW + resto", 470000, "~470.000 M$"), bar("Mínimo de Musk", 500000, "500.000 M$"),
            bar("20 GW + resto", 708000, "~708.000 M$")], highlight=2, vmax=708000)),
  (1, pj_opinion("p12-palancas.jpg")),
  (1, card("La lectura menos generosa", "Sin Cursor ni publicidad")),
  (1, bars("Cape Fear Advisors", PER_GW, [bar("Con todo", 17800, "17.800 M$"),
                                          bar("Solo cómputo", 15100, "~15.100 M$", "sin Cursor ni publicidad · Cape Fear")],
           highlight=1, vmax=17800)),
  (1, photo("b13-obra-amanecer.jpg", "Conclusión 2", "De 1,7 GW a 13 GW", "1,7 GW a 30 sep 2026")),
  (1, figs("Conclusión 2 · El límite es la financiación", "Capex para llegar a 13 GW",
           [("~429.000 M$", "a 38.000 M$ por GW")], 0)),
  (1, figs("Conclusión 2 · El límite es la financiación", "En unos quince meses",
           [("5,5 años", "de capex al ritmo actual"), ("~15 meses", "el plazo")], 1)),
  (2, figs("Conclusión 2 · El límite es la financiación", "Para 20 GW",
           [("~695.000 M$", "capex para 20 GW"), ("8,9 años", "al ritmo actual")], 0)),
  (1, pic("p13-cuentas.jpg")),
  (1, bars("¿Con qué se paga?", SOURCES, [bar("Caja y valores", 90000, "~90.000 M$", "30 sep 2026")],
           highlight=0, vmax=90000)),
  (1, photo("b11-nave-mitad.jpg", "Arrendamiento financiero de GPU", "40.000 M$", "Vehículo gestionado por Apollo")),
  (1, card("Glosario", "EBITDA ajustado", "Beneficio antes de intereses, impuestos y amortizaciones")),
  (1, bars("¿Con qué se paga?", SOURCES,
           [bar("Caja y valores", 90000, "~90.000 M$", "30 sep 2026"), bar("Arrendamiento Apollo", 40000, "40.000 M$"),
            bar("EBITDA ajustado", 35000, "~35.000 M$", "al año, anualizado")], highlight=2, vmax=90000)),
  (1, photo("p13-cuentas.jpg", "Hasta finales de 2027", "165.000-174.000 M$",
            "Fuentes identificadas: 90.000 + 40.000 + EBITDA de 12-15 meses", motion="zoom_in")),
  (1, figs("Cálculo propio", "El hueco · 13 GW",
           [("429.000 M$", "capex para 13 GW"), ("255.000-264.000 M$", "faltan · fuentes: 165.000-174.000 M$")], 1)),
  (1, figs("Cálculo propio", "El hueco · 20 GW",
           [("695.000 M$", "capex para 20 GW"), ("521.000-530.000 M$", "faltan · fuentes: 165.000-174.000 M$")], 1)),
  (1, card("Cape Fear Advisors", "~22.500 M$ por GW", "El coste más bajo que estima")),
  (1, bars("Cálculo propio", "El hueco se reduce",
           [bar("13 GW a 38.000/GW", 429000, "429.000 M$"), bar("13 GW a 22.500/GW", 254000, "~254.000 M$", "Cape Fear"),
            bar("Fuentes", 169500, "165.000-174.000 M$")], highlight=1, vmax=695000)),
  (1, pic("b12-subestacion.jpg", motion="zoom_in")),
  (1, card("S&P · jun 2026", "BBB", "La calificación de SpaceX")),
  (1, card("S&P · BBB", "Flujo de caja libre negativo hasta 2029", "Más deuda y más acciones")),
  (2, photo("p14-plano.jpg", "Mi lectura", "El límite es la financiación", "No la ingeniería", opinion=True)),
  (1, photo("p19-escala.jpg", "Lo que no está anunciado", "¿De dónde salen varios cientos de miles de millones más?")),
  (1, steps("S-1 de Anthropic", "El gran cliente puede irse",
            [("dic 2026", "toda la capacidad"), ("principios de 2027", "cancelable con 90 días de preaviso"),
             ("2029", "fin del contrato")], 1)),
  (2, photo("b13-obra-amanecer.jpg", "Conclusión 3 · La rampa", "Nivel a final de año ≠ media anual")),
  (1, bars(RAMP, "Diciembre de 2026", [GW_RAMP_GUIDE], highlight=-1, vmax=14)),
  (1, bars(RAMP, "Diciembre de 2026", [GW_RAMP_GUIDE, GW_RAMP_END], highlight=1, vmax=14, caption=GW_END_NOTE)),
  (1, g(kicker=RAMP, title="De diciembre a diciembre", ymax=14, unit=" GW", tick=2, xmin=-2, xmax=14,
        points=[{"x": 0, "year_label": "dic 2026", "value": GW_RAMP_FLOOR, "text": "5 (suelo del anuncio, >5)"},
                {"x": 12, "year_label": "dic 2027", "value": 13, "text": "13"}],
        caption="Media del año: ~9 GW")),
  (1, photo("b11-nave-mitad.jpg", "Año natural 2027", "~160.000 M$", "ingresos de Superinteligencia")),
  (1, fromto("Año natural 2027", "~231.000 M$", "~160.000 M$", "231.000 M$ es el ritmo de diciembre")),
  (1, figs("Cálculo propio", "Con 20 GW", [("~222.000 M$", "año natural 2027"), ("356.000 M$", "ritmo de diciembre")],
           0)),
  (2, pic("b23-obra-noche.jpg", motion="pan_right", tail=0.3)),
 ],
 7: [  # La carrera del billón
  (0, haiku("b18b-orbita-noche.jpg", haiku=HAIKU[1:2], translation=HAIKU_ES[1:2],
            kicker="Sección 6 · La carrera del billón")),
  (1, pic("b14-campus.jpg")),
  (1, people("Amazon", "Andy Jassy", [{"name": "Andy Jassy", "org": "Consejero delegado de Amazon",
                                       "note": ""}], 0)),
  (1, people("Amazon", "Andy Jassy", [{"name": "Andy Jassy", "org": "Consejero delegado de Amazon",
                                       "note": "AWS: más de +40 % en 2027 y en 2028"}], 0)),
  (1, people("Amazon", "Andy Jassy", [{"name": "Andy Jassy", "org": "Consejero delegado de Amazon",
                                       "note": "AWS: más de +40 % en 2027 y en 2028. "
                                               "Un negocio de 1 billón $ de ingresos en 5-10 años"}], 0)),
  (1, photo("b24-desfiladero.jpg", "Tomasz Tunguz", "Lo plantea así")),
  (1, card("Tunguz", "La primera empresa de 10 billones $…")),
  (1, g(kicker="Tunguz", title="La primera empresa de 10 billones $",
        sides=["El negocio antiguo que paga las GPU", "Motor de cómputo de IA de 1 billón $"], path="", highlight=1)),
  (1, g(kicker="Tunguz", title="La primera empresa de 10 billones $",
        sides=["El negocio antiguo que paga las GPU", "Motor de cómputo de IA de 1 billón $"], path="", highlight=0,
        motion="zoom_in")),
  (2, photo("b13-obra-amanecer.jpg", "Supuesto de Tunguz, no una ley", "1 billón $ × 10 = 10 billones $")),
  (1, figs("Cálculo propio · múltiplo de 10", "Superinteligencia de SpaceX", [("~2,31 billones $", "con 13 GW")], 0)),
  (1, figs("Cálculo propio · múltiplo de 10", "Superinteligencia de SpaceX",
           [("~2,31 billones $", "con 13 GW"), ("~3,56 billones $", "con 20 GW")], 1)),
  (1, photo("b05-plataforma.jpg", "Toda SpaceX · 21 oct 2026", "~2 billones $")),
  (2, bars("Los números del trimestre", CLOUDS,
           [bar("AWS", 46000, "46.000 M$", "+39,3 %"), bar("Azure", 33200, "33.200 M$"),
            bar("Google Cloud", 30700, "30.700 M$")], highlight=0, vmax=46000)),
  (1, figs("AWS · 3T 2026", "Su mayor crecimiento desde finales de 2021",
           [("+39,3 %", "máximo desde finales de 2021"), ("578.000 M$", "backlog de AWS")], 0)),
  (1, bars("Los números del trimestre", CLOUDS,
           [bar("AWS", 46000, "46.000 M$"), bar("Azure", 33200, "33.200 M$", "+48 %"),
            bar("Google Cloud", 30700, "30.700 M$")], highlight=1, vmax=46000)),
  (1, bars("Los números del trimestre", CLOUDS,
           [bar("AWS", 46000, "46.000 M$"), bar("Azure", 33200, "33.200 M$"),
            bar("Google Cloud", 30700, "30.700 M$",
                "+103 %, con hardware")], highlight=2, vmax=46000,
           caption="Backlog de Google Cloud: ~561.000 M$")),
  (1, photo("b14-campus.jpg", "Estimación · Tunguz", "Un supuesto sencillo", motion="pan_left")),
  (1, card("Estimación · Tunguz", "El crecimiento se frena un 15 % al año", "Y AWS crece lo que guía Jassy")),
  (1, steps("Estimación · Tunguz", "La proyección",
            [("mediados de 2027", "Google Cloud supera a Azure"), ("finales de 2027", "supera a AWS"),
             ("2030", "Google Cloud y SpaceX: 1 billón $ anualizado"), ("2032", "AWS")], 1)),
  (2, steps("Estimación · Tunguz", "La proyección",
            [("mediados de 2027", "Google Cloud supera a Azure"), ("finales de 2027", "supera a AWS"),
             ("2030", "Google Cloud y SpaceX: 1 billón $ anualizado"), ("2032", "AWS")], 2,
            caption="Anclas de razonamiento, no previsiones")),
  (2, photo("p15-puente.jpg", "Mi lectura", "¿Quién paga el camino?", opinion=True, side="right")),
  (1, photo("b15-imprenta.jpg", "El negocio antiguo que paga la factura", "En Google, la búsqueda")),
  (1, figs("Búsqueda de Google · 3T 2026", "El negocio antiguo", [("63.350 M$", "ingresos del trimestre"),
                                                                   ("+12 %", "frente a un año antes")], 1)),
  (1, g(kicker="Búsqueda de Google", title="Crecimiento interanual", ymax=25, unit=" %", tick=5, xmin=-0.6, xmax=2.6,
        points=[{"x": 0, "year_label": "1T 2026", "value": 19, "text": "+19 %"},
                {"x": 1, "year_label": "2T 2026", "value": 17, "text": "+17 %"},
                {"x": 2, "year_label": "3T 2026", "value": 12, "text": "+12 %"}])),
  (2, figs("Búsqueda de Google", "Del 2T al 3T", [("+79 M$", "del segundo al tercer trimestre")], 0,
           caption="Y no por falta de uso")),
  (1, people("Búsqueda de Google", "Las consultas",
             [{**PICHAI, "quote": "Es el más alto de los últimos cinco años"}], 0)),
  (1, pic("p16-tableta.jpg")),
  (1, card("Búsqueda de Google", "Más uso, casi los mismos ingresos")),
  (1, photo("b07-muelle.jpg", "Publicidad de Amazon · 3T 2026", "19.600 M$", "+12 % frente a un año antes")),
  (1, fromto("Publicidad de Amazon · crecimiento", "2T +26 %", "3T +12 %")),
  (1, photo("p13-cuentas.jpg", "Flujo de caja libre", "Y la caja")),
  (1, figs("Flujo de caja libre", "Y la caja", CASH, 0, motion="zoom_in")),
  (1, figs("Flujo de caja libre", "Y la caja", CASH, 1)),
  (1, figs("Flujo de caja libre", "Y la caja", CASH, 2, motion="zoom_out")),
  (1, photo("b26-sala-control.jpg", "Tras los resultados", "Fuera de hora")),
  (1, photo("b26-sala-control.jpg", "Fuera de hora, tras los resultados", "Amazon −12 % · Alphabet −12,6 %",
            "Microsoft −0,2 %", motion="zoom_in")),
  (1, pic("p17-oficina.jpg")),
  (1, figs("Microsoft 365 · nube comercial", "La excepción",
           [("+17 %", "ingresos de Microsoft 365, nube comercial"), ("+5 %", "puestos")], 0)),
  (1, figs("Microsoft 365 · nube comercial", "La excepción",
           [("+17 %", "ingresos de Microsoft 365, nube comercial"), ("+5 %", "puestos")], 1)),
  (1, figs("ServiceNow · 29 oct 2026", "El lado contrario",
           [("−27 %", "ServiceNow, 29 oct 2026, su peor día en bolsa"), ("+20,5 %", "suscripciones")], 0)),
  (1, figs("ServiceNow · 29 oct 2026", "El lado contrario",
           [("−27 %", "ServiceNow, 29 oct 2026, su peor día en bolsa"), ("+20,5 %", "suscripciones")], 0,
           caption="Miedo a que la IA se coma el cobro por puesto", tail=0.3)),
 ],
 8: [  # 2,2 gigavatios
  (0, haiku("b17b-orbita-sol.jpg", haiku=HAIKU[2:], translation=HAIKU_ES[2:], kicker="Final · 2,2 gigavatios")),
  (1, figs("Con qué caja", "Microsoft", [("+18.630 M$", "flujo de caja libre del trimestre")], 0)),
  (1, photo("b02-almacen-lleno.jpg", "Alphabet", "−9.070 M$", "13.300 M$ en el almacén", motion="zoom_out")),
  (1, photo("b14-campus.jpg", "Amazon", "−42.400 M$", "en doce meses")),
  (1, gw_rule([GW_TODAY, GW_END_2026], 1, caption=GW_END_NOTE)),
  (1, g(kicker="Cálculo propio", contrast=GW_END_SHORT, small_label="fin de 2026, anunciado", big="27-55 GW",
        big_label="para 500.000 M$ – 1 billón $ al ingreso actual por GW, sumando el resto de SpaceX", grow=1.0)),
  (1, card("Los titulares", "+103 % · +161 % · +39,3 %", "Quién crece más rápido")),
  (1, figs("La caja", "Quién puede pagarse ese crecimiento", [(v, l.split(" · ")[0]) for v, l in CASH], -1,
           tail=0.8)),
  (0, dict(pic("p18-se-aleja.jpg", motion="zoom_in"), lead_in=2.5)),
  (0, haiku("b17-orbita.jpg", seconds=6.0, haiku=HAIKU, translation=[" / ".join(HAIKU_ES)], foot=HAIKU_FOOT)),
  (0, dict(type="title_card", title="temperaturacero", subtitle="La carrera del billón", lead_in=7.8)),
 ],
}


def estimate(texts: list[str]) -> float:
    """Rough seconds of narration for these pieces (to keep every shot under 8 s)."""
    return sum(len(t) for t in texts) / CHARS_PER_SECOND + 0.35 * (len(texts) - 1)


def main(modules=None, pictures: Path | None = None) -> None:
    """Write the boards; with pictures (the folder of generated images), copy each shot's picture
    to assets/images/carrera-del-billon/moduleN/<shot id>.jpg."""
    OUT.mkdir(parents=True, exist_ok=True)
    titles = {1: "Un almacén en Google y un objetivo en SpaceX", 2: "TPU: lo que hay dentro del 103 %",
              3: "Margen frente a capital", 4: "Lo que no encaja", 5: "SpaceX: los gigavatios y el dinero",
              6: "Tres conclusiones", 7: "La carrera del billón", 8: "2,2 gigavatios"}
    for n, plan in P.items():
        if modules and n not in modules:
            continue
        pieces = units(n)
        if sum(k for k, _ in plan) != len(pieces):
            raise SystemExit(f"module {n}: plan covers {sum(k for k, _ in plan)} pieces, script has {len(pieces)}")
        shots, i, run = [], 0, 0
        if pictures:
            shutil.rmtree(IMAGES / f"module{n}", ignore_errors=True)
        for k, (count, fields) in enumerate(plan, 1):
            fields = dict(fields)
            src = fields.pop("src", None)
            shot_id = f"m{n}-{k:02d}"
            if src and pictures:
                dest = IMAGES / f"module{n}" / f"{shot_id}.jpg"
                dest.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(pictures / src, dest)
            text = pieces[i:i + count]
            seconds = estimate(text) + fields.get("lead_in", 0) + fields.get("tail", 0)
            if seconds > 7.9:
                print(f"  warning {shot_id}: ~{seconds:.1f} s")
            run = 0 if fields.get("prompt") else run + 1
            if run > 4:
                print(f"  warning {shot_id}: {run} shots in a row without a photo")
            shots.append({"id": shot_id, **fields, "text": " ".join(text)})
            i += count
        board = {"module": n, "voice": "es-ES-AlvaroNeural", "theme": "blueprint", "style": STYLE,
                 "character": CHARACTER, "shots": shots}
        header = (f"# La carrera del billón, module {n}: {titles[n]}. Generated by scripts/make_carrera_boards.py;\n"
                  f"# edit the plan there. Images are in assets/images/carrera-del-billon/module{n}/.\n")
        (OUT / f"module{n}.yaml").write_text(header + yaml.dump(board, Dumper=NoAliases, allow_unicode=True,
                                                                 sort_keys=False, width=110), encoding="utf-8")
        print(f"module {n}: {len(shots)} shots")


if __name__ == "__main__":
    import sys
    main(pictures=Path(sys.argv[1]) if len(sys.argv) > 1 else None)

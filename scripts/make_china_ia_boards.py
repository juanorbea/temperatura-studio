"""Write storyboards/china-ia-01/moduleN.yaml for «China y la IA #1» from a compact shot plan.

Same scheme as make_japon_boards: each plan row is (number of sentences, shot fields); shot texts
are whole sentences of the parsed build copy, so coverage is exact by construction. The script's
visual cues are replaced by the direction plan (/workspace/direction/.../plan-direccion.md):
no logos, no real people (name cards only), no summit, official buildings or WeChat, and every
[CÁMARA] cue is a shot of the AI character. Graphics come from scripts/china_ia_01_charts.py.
Run: .venv/bin/python -m scripts.make_china_ia_boards [FOLDER OF GENERATED PICTURES]  (from the repo root)
"""
import shutil
from pathlib import Path

import yaml

from scripts import china_ia_01_charts as G
from scripts.make_japon_boards import NoAliases, graphic, img
from studio.parse import parse_script, split_sentences

SCRIPT = Path("examples/china-ia-01.md")
OUT = Path("storyboards/china-ia-01")
IMAGES = Path("assets/images/china-ia-01")
STYLE = yaml.safe_load(Path("storyboards/module1.yaml").read_text(encoding="utf-8"))
NO_TEXT = " Plain unbranded objects with no logos and no readable text."
LEFT = " Calm, uncluttered left third of the frame."

# Image prompts (the generated pictures are in assets/images/china-ia-01/moduleN/<shot id>.jpg).
P1 = ("Close-up: the character holds up a plain wooden rubber stamp with a blank unmarked rubber face, about to "
      "stamp a blank sheet of paper on a clean desk in a bright archive office.")
P2 = "Medium shot: the character sits at a wooden desk by a window and opens a plain buff case folder with blank pages."
P3 = ("Wide shot: the character stands in a quiet study with window light, one hand on a tall stack of plain buff "
      "folders and loose papers on a wooden table.")
WAFER = ("A single polished silicon wafer with a grid of iridescent chip dies resting on a clean white laboratory "
         "bench, macro photograph.")
STREET = ("A generic quiet street in a large modern East Asian city at dawn: plane trees, a few cyclists seen from "
          "behind, shop signs out of focus and unreadable, no monuments, no landmarks, no flags, no official buildings.")


def g(overlay):
    return graphic(**overlay)


def pj(prompt, opinion=False, **kw):
    """A shot of the AI character (what every [CÁMARA] cue becomes); opinion adds the MI LECTURA tab."""
    if opinion:
        return dict(type="text_overlay", prompt=prompt + NO_TEXT, character=True, overlay={"opinion": True}, **kw)
    return dict(type="image", prompt=prompt + NO_TEXT, character=True, **kw)


def photo(prompt, kicker, title, body="", **kw):
    return dict(type="text_overlay", prompt=prompt + LEFT + NO_TEXT,
                overlay={"kicker": kicker, "title": title, "body": body}, **kw)


def pic(prompt, src, **kw):
    """A still photo with no overlay; src is the picture's file name in the images folder."""
    return dict(type="image", prompt=prompt + NO_TEXT, src=src, **kw)


def card(**o):
    return g(o)


def people(kicker, title, cards, highlight=-1, **kw):
    return g(dict(kicker=kicker, title=title, people=cards, highlight=highlight, **kw))


def quote(kicker, text, size=50, **kw):
    return g(dict(kicker=kicker, title=text, size=size, **kw))


def plain_text(**o):
    return g(o)


def ficha(**kw):
    return g(G.g03_card(**kw))


DATA_OR_OPINION = dict(kicker="Cómo leer este vídeo", title="Datos primero, y luego mi lectura", highlight=1,
                       opinion=True, people=[
                           {"name": "Dato", "org": "Sin pestaña", "note": "Lo que dicen las fuentes"},
                           {"name": "Mi lectura", "org": "Pestaña cobre", "note": "Mi opinión, no la verdad"}])
NOT_FITTING = {"lines": ["VER: LO QUE NO ENCAJA"], "ink": "copper", "size": 44, "at": [1540, 1010]}
CONCORDIA = "Concordia AI · boletín #31"
P4 = "Medium shot in a bright archive office: the character pushes a thick plain bound document aside and points off-frame."
P5 = "Medium shot in a quiet archive room: the character holds a plain cardboard archive box with a blank label."
P6 = "Medium shot: the character holds one plain buff folder in each hand at the same height, like a balance scale."
P7 = "Wide shot: the character sits alone in an empty waiting room holding a blank paper queue ticket."
P8 = ("Medium shot at a service counter window: the character slides a sheet through; an anonymous hand in a navy "
      "cuff (no face) stamps it.")
P9 = "The character stands in a pale corridor before a closed plain door, holding a blank form and a pen."
P10 = "Wide shot: the character sits at a long negotiation table; the chair opposite is empty. No flags, no emblems."
P11 = "A seminar room seen from the back rows: an audience seen only from behind, the character among them."
P12 = "The character at a desk leans over a sheet with a blank ruled table, a red pen in hand."
P13 = ("Wide shot down the aisle of a quiet archive: the character, from behind, walks away with a closed folder "
       "under his arm.")
HAND = ("Close-up: an anonymous hand in a navy suit cuff (no face, no insignia) holds a blank rubber stamp raised "
        "and still above a sheet with a blank ruled table.")
MOFCOM_SECURITY_12 = " ".join(G.MOFCOM_SECURITY[:2])
MOFCOM_OPEN_23 = "«" + " ".join(G.MOFCOM_OPEN[1:]).lstrip("«")
SEAL_TEETH = {"lines": ["DIENTES"], "ink": "ink", "size": 96, "at": [1450, 640]}

P = {
 1: [  # Gancho: una J y una X (cold open, no title card; ~4 s a shot until 0:30)
  (1, dict(g(G.g01_catalogue(rows=1)), lead_in=0.6)),
  (1, g(G.g01_catalogue(rows=2))),
  (1, g(G.g01_catalogue(focus=True))),
  (2, g(G.g01_catalogue(focus=True, heading=True))),
  (1, g(G.g01_catalogue(focus=True, heading=True, seals=1))),
  (1, g(G.g01_catalogue(focus=True, heading=True, seals=2))),
  (1, g(G.g02_doors(1))),
  (1, g(G.g02_doors(2))),
  (1, g(G.g05_types(1))),
  (1, g(G.g05_types(2))),
  (1, photo(WAFER, "Durante años", "EE. UU. → China", "Chips avanzados, prohibidos", src="oblea.jpg")),
  (1, pj(P1, src="p01-tampon.jpg")),
 ],
 2: [  # Mi lectura, de entrada
  (1, pj(P2, opinion=True, src="p02-carpeta.jpg")),
  (1, ficha(shown=1)), (1, ficha(shown=2)), (1, ficha(shown=3)), (1, ficha(shown=4)), (1, ficha(shown=5)),
  (1, ficha(shown=5)),
  (1, g(DATA_OR_OPINION)),
  (1, g({**G.g03_card(shown=5), "seals": [NOT_FITTING]})),
 ],
 3: [  # Una serie sobre China y la IA
  (1, dict(g(G.opener(1)), lead_in=0.4)),
  (1, card(kicker="Cómo solemos mirar la IA china", **{"from": "Una amenaza"}, to="Una copia barata", opinion=True)),
  (1, card(kicker="Cómo solemos mirar la IA china", **{"from": "Una copia barata"}, to="¿Quién decide?",
           body="Cómo se decide allí qué se puede hacer con ella", opinion=True)),
  (1, card(kicker="DeepSeek · modelos abiertos · principios de 2025", title="Mucho más cerca de la frontera",
           lit=[{"name": "Pekín", "lon": 116.4, "lat": 39.9}])),
  (1, people("La otra mitad de la historia", "Modelos, y quién decide sobre ellos", [
      {"name": "Modelos", "org": "Lo que llegó", "note": "DeepSeek y los modelos abiertos"},
      {"name": "Ministerios · reglas · juristas", "org": "Lo que llegó con menos fuerza",
       "note": "Quién decide qué se hace con ellos"}], highlight=1)),
  (1, pj(P3, src="p03-pila.jpg")),
  (1, photo(STREET, "Fuentes", "Análisis de Concordia AI", "Gabriel Wagner y Erik Lindblad · boletines #30 y #31",
            src="calle.jpg")),
  (1, g(G.g01_catalogue(heading=True))),
 ],
 4: [  # Qué ha propuesto China
  (1, g({**G.g01_catalogue(heading=True), "caption": "Borrador de revisión · 16 de octubre de 2026"})),
  (1, people("Borrador de revisión", "Lo firman dos ministerios", [
      {"name": "MOFCOM", "org": "Ministerio de Comercio", "note": "Firma el borrador"},
      {"name": "MOST", "org": "Ministerio de Ciencia y Tecnología", "note": "Firma el borrador"}])),
  (2, g(G.g04_bars(1))),
  (2, g(G.g04_bars(2))),
  (1, pj(P4, opinion=True, src="p04-aparta.jpg")),
  (2, g(G.g06_who(1))),
  (1, g(G.g06_who(2))),
  (4, card(kicker="Lo que regula", title="La tecnología en sí",
           body="Pesos del modelo · puntos de control intermedios · arquitectura · software que envuelve al agente")),
  (1, card(kicker="Y cuándo", title="Cuando sale de China")),
  (1, quote(CONCORDIA, "«Una herramienta nueva en su caja de herramientas de IA», no un martillo para aplastar a los "
            "modelos abiertos de frontera a corto plazo", size=56)),
  (1, pic("An open tidy metal toolbox on a pale workbench with one new unused precision tool on top.",
          "caja-herramientas.jpg")),
 ],
 5: [  # De defenderse a imponer
  (1, photo(WAFER, "Desde 2022", "EE. UU. restringe", "La venta a China de chips avanzados y de las máquinas "
            "para fabricarlos", src="oblea.jpg")),
  (1, g(G.g08_cctv())),
  (1, g(G.g07_precedents(1))),
  (2, g(G.g07_precedents(2))),
  (3, card(kicker="Lo nuevo es el objeto", stamp=[{"lines": ["MATERIAS PRIMAS"], "ink": "muted", "size": 84},
                                                  {"lines": ["ALGORITMO"], "ink": "muted", "size": 84},
                                                  {"lines": ["MODELOS Y AGENTES", "DE FRONTERA"], "ink": "ink", "size": 84}],
           arrows=True)),
  (1, pj(P5, opinion=True, src="p05-caja.jpg")),
  (2, ficha(argued=1)),
 ],
 6: [  # La seguridad es un motivo real
  (2, photo("An empty modern cybersecurity operations room with abstract network graphs on the screens.",
            "¿Por qué lo hace?", "Por seguridad", "Lo dice el Ministerio de Comercio, de forma explícita",
            src="ciberseguridad.jpg")),
  (1, quote(f"MOFCOM · {G.CONCORDIA_EN}", MOFCOM_SECURITY_12, size=48)),
  (1, g(G.g09_mofcom_security(3))),
  (2, card(kicker="El miedo concreto", **{"from": "EE. UU. copia un modelo chino"}, to="No es eso")),
  (1, card(kicker="El miedo concreto", title="Un grupo criminal con una herramienta que escribe código malicioso "
           "que se modifica solo")),
  (2, card(kicker="Concordia AI", title="Meses de preocupación",
           body="Ciberataques con IA: hasta ahora, solo en declaraciones de intenciones")),
  (1, g({**G.g01_catalogue(focus=True, heading=True), "seals": [SEAL_TEETH]})),
  (2, dict(photo("The empty control room of a power plant with gauges and switches.", "Mi lectura",
                 "Un motivo real, no una excusa", src="sala-control.jpg"),
           overlay={"kicker": "Mi lectura", "title": "Un motivo real, no una excusa", "body": "", "opinion": True})),
 ],
 7: [  # Pero no el único
  (2, photo("A generic container port at dawn with unmarked containers and cranes.", "Pero no el único",
            "Más motivos", "Seguridad económica · cadenas de suministro · tecnología estratégica", src="puerto.jpg")),
  (2, people("Un caso", "Meta y Manus", [
      {"name": "Meta", "org": "Compradora", "note": ""},
      {"name": "Manus", "org": "Agentes de IA", "note": "Origen chino · constituida en Singapur"}], highlight=1)),
  (1, g(G.g10_manus(0))),
  (3, g(G.g10_manus(1))),
  (2, g(G.g06_who(3))),
  (1, pj(P6, opinion=True, src="p06-balanza.jpg")),
  (4, ficha(argued=2)),
 ],
 8: [  # Lo que pesa una licencia: TikTok
  (2, card(title="¿Solo restringido?", stamp=[G.X])),
  (1, card(kicker="El caso", title="TikTok", body="Propiedad de ByteDance")),
  (2, g(dict(doc=G.CATALOGUE + " · revisión de 2020", columns=[{"label": "Código", "width": 420},
             {"label": "Tecnología", "width": 1000}, {"label": "Nivel"}],
             rows=[[None, "Recomendación de servicios de información personalizada basada en el análisis de datos",
                    {"label": "Con licencia"}]], highlight=0, caption="El código de la entrada no está en las fuentes"))),
  (1, photo("A generic unbranded smartphone on a pale desk showing a blurred abstract video feed.", "Con esa línea",
            "Veto de facto", "Sobre cualquier venta del negocio de TikTok en EE. UU.", src="movil.jpg")),
  (2, g(G.g11_tiktok(0))),
  (1, g(G.g11_tiktok(2))),
  (2, pj(P7, src="p07-espera.jpg")),
  (2, card(title="Alguien en Pekín tiene la llave", stamp=[G.X], opinion=True)),
  (3, card(kicker="Para ser justos · Concordia AI", title="La mayoría será mucho más fluida",
           body="TikTok fue un caso extremo. Pero enseña hasta dónde puede llegar la herramienta")),
 ],
 9: [  # Lo que ya está en vigor: DeepSeek y MiniMax
  (4, g(G.g12_register(1))),
  (1, card(kicker="Nota al margen", title="¿Suspender exportaciones?",
           body="Algunos abogados creen que el registro podría usarse para eso")),
  (3, g({**G.g12_register(2), "caption": "Según una cuenta de redes sociales afiliada al Estado chino"})),
  (3, pj(P8, src="p08-ventanilla.jpg")),
  (3, people("Un mensaje en dos direcciones", "Registraos, y tranquilos", [
      {"name": "Hacia dentro", "org": "Esto va en serio", "note": "Registraos"},
      {"name": "Hacia fuera", "org": "Tranquilos", "note": "Los modelos siguen saliendo"}], opinion=True)),
  (1, pic("A large origami elephant of plain grey paper in an empty bright room.", "elefante.jpg")),
 ],
 10: [  # Los modelos abiertos: protegidos, por ahora
  (1, photo("Server racks in a clean data centre with soft translucent download bars.", "Modelos abiertos",
            "Pesos que cualquiera puede descargar", src="servidores.jpg")),
  (2, card(kicker=CONCORDIA, title="¿Se acabó publicar en abierto?",
           seals=[{"lines": ["NO ES EL FIN"], "ink": "ink", "size": 150, "at": [1300, 700]}])),
  (1, g(G.g13_mofcom_open(1))),
  (1, quote(f"MOFCOM · {G.CONCORDIA_EN}", MOFCOM_OPEN_23, size=54, highlight=["dominio público"])),
  (2, g(G.g14_lockers(1))),
  (2, g(G.g14_lockers(2))),
  (1, g(G.g14_lockers(3))),
  (1, pj(P9, src="p09-puerta.jpg")),
  (2, g(G.g15_three_ways())),
  (1, g(G.g16_scale())),
  (1, g(G.g16_lawyer())),
 ],
 11: [  # Cuatro caminos hacia la X o la J
  (1, g(G.g17_ways(0))),
  (3, g(G.g17_ways(1))),
  (5, g(G.g17_ways(2))),
  (3, g(G.g17_ways(3))),
  (4, g(G.g17_ways(4))),
  (1, card(kicker="Un ejemplo", title="ARTEX", body="Agente de pruebas de penetración. Su desarrollador chino lo pasó "
           "a código cerrado en octubre de 2026, tras varios casos de mal uso")),
  (2, g(G.g17_ways(4, conclusion=True))),
  (3, ficha(argued=3)),
 ],
 12: [  # Mientras tanto, en Washington
  (1, g(G.g18_map())),
  (1, g(G.g18_names())),
  (2, g(G.g19_summit(1))),
  (2, g(G.g19_summit(2))),
  (3, g(G.g20_notes(1))),
  (2, g(G.g20_notes(2))),
  (4, card(kicker="Yuyuan Tantian 玉渊谭天 · cuenta de WeChat que depende de CCTV", title="¿Y en noviembre?",
           body="No hay agenda oficial. Esta cuenta propone una; no es una postura oficial")),
  (1, g(G.g21_agenda(1))),
  (3, g(G.g21_agenda(2))),
  (1, g(G.g21_agenda(3))),
  (3, pj(P10, opinion=True, src="p10-mesa.jpg")),
  (3, g(G.g06_who(4))),
  (2, g(G.g22_folders())),
  (2, pj(P4, src="p04-aparta.jpg")),
 ],
 13: [  # Una China menos monolítica de lo que parece
  (1, g({**G.g03_card(argued=4), "highlight": 4})),
  (2, card(kicker="Cómo solemos imaginarla", **{"from": "Una sola voz que baja de arriba"}, to="Un debate")),
  (3, g(G.g23_rules(1))),
  (2, g(G.g23_rules(2))),
  (1, photo("A generic modern university campus in an East Asian city in autumn.", "Mediados de octubre de 2026",
            "Dos borradores no oficiales", "De una posible ley nacional de IA", src="campus.jpg")),
  (1, g(G.g24_drafts(0))),
  (2, g(G.g24_drafts(1))),
  (1, g(G.g17_ways(4))),
  (1, pj(P11, src="p11-seminario.jpg")),
  (2, g(G.g25_jurists(1))),
  (1, g(G.g25_jurists(2))),
  (2, card(kicker="Concordia AI", title="Lejos de ser monolítico",
           body="Universidades, despachos y académicos empujan en direcciones distintas")),
  (3, ficha(argued=5)),
 ],
 14: [  # Lo que no encaja con mi lectura
  (3, pj(P12, src="p12-boli-rojo.jpg")),
  (4, ficha(argued=5, nuances=1, footer="Matiz 1 · Es un borrador: comentarios hasta el 15 de noviembre")),
  (4, ficha(argued=5, nuances=2, footer="Matiz 2 · Mucho ruido para un formulario")),
  (3, ficha(argued=5, nuances=3, footer="Matiz 3 · La J es poco probable, no está descartada")),
  (5, ficha(argued=5, nuances=4, footer="Matiz 4 · El catálogo ya existía en 2020; a Manus lo frenó la NDRC")),
  (3, ficha(argued=5, nuances=5, footer="Matiz 5 · Poco tiempo, agenda sin confirmar, ni el mismo nombre")),
  (2, ficha(argued=5, nuances=6, footer="Matiz 6 · Muchas voces no es decidir de forma descentralizada")),
  (3, g(G.g24_drafts())),
  (4, ficha(argued=5, nuances=6, footer="Misma dirección, camino más lento")),
 ],
 15: [  # Final: cinco años o «presentar y salir»
  (3, g(G.g26_columns(1))),
  (2, g(G.g26_columns(2))),
  (3, g(G.g26_scale())),
  (1, g({**G.g01_catalogue(focus=True, heading=True), "opinion": True})),
  (1, dict(type="text_overlay", prompt=HAND + NO_TEXT, overlay={"opinion": True}, src="mano-tampon.jpg", tail=0.5)),
  (1, g(G.g01_catalogue(focus=True, heading=True, seals=2))),
 ],
}
# After the last sentence (scripts/china_ia_coda.py): 1.5 s of silence on «EXPEDIENTE 01 · CERRADO» and the
# character walking away (P13), then the end screen «EXPEDIENTE 02 · PRÓXIMAMENTE».
CODA = [("cierre", G.opener(1, "CERRADO"), 1.5), ("pasillo", "p13-pasillo.jpg", 2.5),
        ("pantalla-final", G.opener(2, "PRÓXIMAMENTE"), 8.0)]


def main(modules=None, pictures: Path | None = None) -> None:
    """Write the boards; with pictures (the folder of generated images), copy each shot's picture
    to assets/images/china-ia-01/moduleN/<shot id>.jpg."""
    script = {m.number: m for m in parse_script(SCRIPT.read_text(encoding="utf-8"))}
    OUT.mkdir(parents=True, exist_ok=True)
    for n, plan in P.items():
        if modules and n not in modules:
            continue
        module = script[n]
        sentences = [s for p in module.narration.split("\n\n") for s in split_sentences(p)]
        if sum(k for k, _ in plan) != len(sentences):
            raise SystemExit(f"module {n}: plan covers {sum(k for k, _ in plan)} sentences, script has {len(sentences)}")
        shots, i = [], 0
        for k, (count, fields) in enumerate(plan, 1):
            fields = dict(fields)
            src = fields.pop("src", None)
            shot_id = f"c{n}-{k:02d}"
            if src and pictures:
                dest = IMAGES / f"module{n}" / f"{shot_id}.jpg"
                dest.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(pictures / src, dest)
            shots.append({"id": shot_id, **fields, "text": " ".join(sentences[i:i + count])})
            i += count
        board = {"module": n, "voice": "es-ES-AlvaroNeural", "theme": "blueprint", "style": STYLE["style"],
                 "character": STYLE["character"], "shots": shots}
        header = (f"# China y la IA #1, module {n}: {module.title}. Generated by scripts/make_china_ia_boards.py;\n"
                  f"# edit the plan there. Images are in assets/images/china-ia-01/module{n}/.\n")
        (OUT / f"module{n}.yaml").write_text(header + yaml.dump(board, Dumper=NoAliases, allow_unicode=True,
                                                                 sort_keys=False, width=110), encoding="utf-8")
        print(f"module {n}: {len(shots)} shots")


if __name__ == "__main__":
    import sys
    main(pictures=Path(sys.argv[1]) if len(sys.argv) > 1 else None)

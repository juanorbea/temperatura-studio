"""Write storyboards/china-ia-01/moduleN.yaml for «China y la IA #1» from a compact shot plan.

Same scheme as make_japon_boards: each plan row is (number of sentences, shot fields); shot texts
are whole sentences of the parsed build copy (a few long ones cut at a comma, see SPLITS), so
coverage is exact by construction. No graphic holds more than ~8 s (review 01). The script's
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
NOT_FITTING = {"lines": ["VER: LO QUE NO ENCAJA"], "ink": "copper", "size": 110, "at": [1300, 960], "angle": -5}
CONCORDIA = "Concordia AI · boletín #31"
GLOVES = " White cotton archival gloves on both hands."
P4 = ("Medium shot in a bright archive office: the character pushes a thick plain bound document aside and points "
      "off-frame." + GLOVES)
P5 = "Medium shot in a quiet archive room: the character holds a plain cardboard archive box with a blank label." + GLOVES
P6 = "Medium shot: the character holds one plain buff folder in each hand at the same height, like a balance scale." + GLOVES
P7 = "Wide shot: the character sits alone in an empty waiting room holding a blank paper queue ticket." + GLOVES
P8 = ("Medium shot at a service counter window: the character slides a sheet through; an anonymous gloved hand in a "
      "navy cuff (no face) stamps it." + GLOVES)
P9 = "The character stands in a pale corridor before a closed plain door, holding a blank form and a pen." + GLOVES
P10 = ("Wide shot: the character sits at a long negotiation table with two small desk microphones; the chair "
       "opposite is empty. No flags, no emblems." + GLOVES)
P11 = ("A seminar room seen from the very back: an audience seen only from behind, no faces, the character among "
       "them, also from behind.")
P12 = "The character at a desk leans over a sheet with a blank ruled table, a red pen in hand." + GLOVES
P13 = ("Wide shot down the aisle of a quiet archive: the character, from behind, walks away with a closed folder "
       "under his arm.")
P14 = "The character slides one plain folder to the side of the desk, setting a topic aside." + GLOVES
P15 = "The character pulls a plain folder halfway out of an open grey filing-cabinet drawer." + GLOVES
SEAL_TEETH = {"lines": ["DIENTES"], "ink": "ink", "size": 130, "at": [1400, 760]}
KB = "zoom_in"  # the five slow pushes the review allows: hook codes, map, a MATIZ on the card, G26 to scale, last stamps

# Sentences longer than ~9.5 s on a graphic are cut in two (or three) at a comma, so no graphic holds
# more than ~8 s. Each entry is the start of a sentence up to the cut; the narration is made per piece.
SPLITS = [
    "23 son de inteligencia artificial:",
    "Lo publicado es un borrador de revisión,",
    "Concordia AI lo resume así: China añade una herramienta nueva a su caja de herramientas de IA,",
    "Un comentario vinculado a CCTV, la televisión estatal china, lo dice casi así:",
    "a medida que China llega a la frontera en más campos, gestionar su propia tecnología se ha convertido en una "
    "nueva prioridad,",
    "Te leo lo esencial, traducido:",
    "«Tecnologías como la generación y mutación autónoma de código malicioso "
    "impulsada por IA pueden usarse para atacar infraestructuras críticas de información,",
    "Según Concordia AI, la preocupación por los ciberataques con IA",
    "llevaba meses creciendo dentro de la administración china,",
    "Según Concordia AI, la preocupación por los ciberataques con IA llevaba meses creciendo dentro de la "
    "administración china,",
    "En 2020, China revisó este mismo catálogo y añadió, entre otras cosas,",
    "La bloqueó la Comisión Nacional de Desarrollo y Reforma, la NDRC,",
    "El Ministerio de Comercio lo dice así: «Para apoyar la construcción de un ecosistema de innovación de código "
    "abierto en IA,",
    "Se propone no incluir en el ámbito de la gestión de exportaciones las tecnologías que ya hayan entrado en el "
    "dominio público mediante el código abierto,",
    "Una licencia de código abierto, como la MIT o la Apache, es una licencia de propiedad intelectual,",
    "Un abogado se lo explicaba a Caixin, una de las principales revistas económicas chinas:",
    "«Si los modelos abiertos de frontera se trataran como prohibidos para la exportación,",
    "Todas están en una categoría aparte, la de «contramedidas informáticas»,",
    "Algo como ARTEX, un agente de pruebas de penetración que su desarrollador chino pasó a código cerrado en "
    "octubre de 2026,",
    "Primero, concretar el canal de incidentes, que «no puede quedarse en un acuerdo verbal»:",
    "El Ministerio de Comercio, el que firma el borrador,",
    "En mayo de 2026, el plan legislativo del Consejo de Estado, el Gobierno chino,",
    "El de la Universidad de Zhejiang gira en torno a la idoneidad:",
    "si un sistema es apto para una tarea,",
    "Zhang Wenxian, un jurista veterano, dijo que las autoridades ya han empezado formalmente a redactar una «Ley "
    "de IA»,",
    "En el otro lado, Shou Bu, de la Universidad Jiao Tong de Shanghái, lee el plan legislativo justo al revés:",
    "En Washington casi no hubo tiempo,",
    "Hoy la cuento apoyándome en dos análisis de Concordia AI,",
    "Cuando le preguntaron, un portavoz del Ministerio de Exteriores chino respondió",
]


def split_long(sentences: list[str]) -> list[str]:
    """Apply SPLITS (repeatedly, so a sentence can be cut twice)."""
    out = []
    for s in sentences:
        while True:
            head = next((h for h in SPLITS if s.startswith(h) and len(s) > len(h)), None)
            if not head:
                out.append(s)
                break
            out.append(head)
            s = s[len(head):].strip()
    return out


def punch(overlay, x, y, zoom=1.45):
    """The same graphic, cut in closer around (x, y)."""
    return {**overlay, "punch": {"zoom": zoom, "at": [x, y]}}


def stamps(*seals, **o):
    return g(dict(stamp=list(seals), **o))


L2, R2 = (560, 640), (1360, 640)          # centres of the two cards of a people graphic
L3, M3, R3 = (420, 640), (960, 640), (1500, 640)
CAT = G.g01_catalogue
BOTH = CAT(focus=True, heading=True, seals=2)
ROW = [395, 545, 695, 845]                # centres of the four rows of the ways matrix
MOFCOM_OPEN_1 = "«Para apoyar la construcción de un ecosistema de innovación de código abierto en IA, […]»"
LAWYER_1 = "«Si los modelos abiertos de frontera se trataran como prohibidos para la exportación, […]»"
CCTV_1 = ("«A medida que China llega a la frontera en más campos, gestionar su propia tecnología se ha convertido "
          "en una nueva prioridad […]»")
WAYS = G.g17_ways

P = {
 1: [  # Gancho: los dos códigos sellados en los primeros segundos; luego el contexto
  (1, dict(g(BOTH), lead_in=0.3, motion=KB)),
  (1, g(punch(BOTH, 960, 430, zoom=1.3))),
  (1, g(CAT(rows=2))),
  (2, g(CAT(focus=True, heading=True))),
  (1, g(G.g02_seals("j"))),
  (1, g(G.g02_seals("both"))),
  (1, g(G.g02_doors(1))),
  (1, g(G.g02_doors(2))),
  (1, g(G.g05_types(1))),
  (1, g(G.g04_bars(1))),
  (1, g(G.g05_types(2, date_stamp=False))),
  (1, photo(WAFER, "Durante años", "EE. UU. → China", "Chips avanzados, prohibidos", src="oblea.jpg")),
  (1, pj(P1 + GLOVES, src="p01-tampon.jpg")),
 ],
 2: [  # Mi lectura: un plano por idea, cada una con su sello
  (1, pj(P2 + GLOVES, opinion=True, src="p02-carpeta.jpg")),
  (1, g(G.g03_idea(1))), (1, g(G.g03_idea(2))), (1, g(G.g03_idea(3))), (1, g(G.g03_idea(4))),
  (1, g(G.g03_idea(5))),
  (1, ficha(shown=5)),
  (1, g(DATA_OR_OPINION)),
  (1, g({**G.g03_card(shown=5), "seals": [NOT_FITTING]})),
 ],
 3: [  # Una serie sobre China y la IA
  (1, dict(g(G.opener(1)), lead_in=0.4)),
  (1, card(kicker="Cómo solemos mirar la IA china", **{"from": "Amenaza · copia barata"}, to="", opinion=True)),
  (1, card(kicker="Cómo solemos mirar la IA china", **{"from": "Amenaza · copia barata"}, to="¿Cómo se decide allí?",
           opinion=True)),
  (1, dict(card(kicker="DeepSeek · modelos abiertos · principios de 2025", title="Mucho más cerca de la frontera",
                lit=[{"name": "Pekín", "lon": 116.4, "lat": 39.9}]), motion=KB)),
  (1, people("La otra mitad de la historia", "Modelos, y quién decide sobre ellos", [
      {"name": "Modelos", "org": "Lo que se vio", "note": "DeepSeek y los modelos abiertos"},
      {"name": "Ministerios · reglas · juristas", "org": "Lo que se vio menos",
       "note": "Quién decide qué se hace con ellos"}], highlight=1)),
  (1, pj(P3, src="p03-pila.jpg")),
  (1, photo(STREET, "Fuentes", "Análisis de Concordia AI", "Gabriel Wagner y Erik Lindblad · boletines #30 y #31",
            src="calle.jpg")),
  (1, photo(STREET, "Fuentes", "Análisis de Concordia AI", "Gabriel Wagner y Erik Lindblad · boletines #30 y #31",
            src="calle-cerca.jpg")),  # the same street, cut in closer: no still holds more than 8 s
  (1, g(CAT(heading=True))),
 ],
 4: [  # Qué ha propuesto China
  (1, g({**CAT(heading=True), "caption": G.CATALOGUE_ZH + " · borrador de revisión · 16 de octubre de 2026"})),
  (1, card(kicker="16 de octubre de 2026", title="Un borrador de revisión", body="Abierto a comentarios")),
  (1, people("Borrador de revisión", "Lo firman dos ministerios", [
      {"name": "MOFCOM", "org": "Ministerio de Comercio", "note": "Firma el borrador"},
      {"name": "MOST", "org": "Ministerio de Ciencia y Tecnología", "note": "Firma el borrador"}])),
  (2, g(G.g04_bars(1))),
  (2, g(G.g04_bars(2))),
  (1, pj(P4, opinion=True, src="p04-aparta.jpg")),
  (1, g(G.g06_who(1))),
  (1, g(punch(G.g06_who(1), *L3))),
  (1, g(G.g06_who(2))),
  (1, card(kicker="Lo que regula", title="La tecnología en sí", body="Los pesos del modelo")),
  (2, card(kicker="Lo que regula", title="La tecnología en sí",
           body="Pesos del modelo · puntos de control intermedios · arquitectura")),
  (1, card(kicker="Lo que regula", title="La tecnología en sí",
           body="Pesos del modelo · puntos de control intermedios · arquitectura · software que envuelve al agente")),
  (1, card(kicker="Y cuándo", title="Cuando sale de China")),
  (1, quote(CONCORDIA, "«Una herramienta nueva en su caja de herramientas de IA»", size=72)),
  (1, quote(CONCORDIA, "No un martillo para aplastar a los modelos abiertos de frontera a corto plazo", size=64,
            highlight=["a corto plazo"])),
  (1, pic("An open tidy metal toolbox on a pale workbench with one new unused precision tool on top.",
          "caja-herramientas.jpg")),
 ],
 5: [  # De defenderse a imponer
  (1, photo(WAFER, "Desde 2022", "EE. UU. restringe", "La venta a China de chips avanzados y de las máquinas "
            "para fabricarlos", src="oblea.jpg")),
  (1, card(kicker="Fuente", title="Un comentario vinculado a CCTV", body="La televisión estatal china")),
  (1, quote("Comentario vinculado a CCTV · traducción", CCTV_1, size=56,
            highlight=["gestionar su propia tecnología"])),
  (1, g(G.g08_cctv())),
  (1, g(G.g07_precedents(1))),
  (1, g(G.g07_precedents(2))),
  (1, g(punch(G.g07_precedents(2), 700, 640, zoom=1.5))),
  (2, stamps({"lines": ["MATERIAS PRIMAS"], "ink": "muted", "size": 84},
             {"lines": ["ALGORITMO"], "ink": "muted", "size": 84}, kicker="Lo nuevo es el objeto", arrows=True)),
  (1, stamps({"lines": ["MATERIAS PRIMAS"], "ink": "muted", "size": 84}, {"lines": ["ALGORITMO"], "ink": "muted",
             "size": 84}, {"lines": ["MODELOS Y AGENTES", "DE FRONTERA"], "ink": "ink", "size": 84},
             kicker="Lo nuevo es el objeto", arrows=True)),
  (1, pj(P5, opinion=True, src="p05-caja.jpg")),
  (1, g(G.g03_idea(1))),
  (1, g(G.g03_idea(1, "argumentada"))),
 ],
 6: [  # La seguridad es un motivo real
  (2, photo("An empty modern cybersecurity operations room with abstract network graphs on the screens.",
            "¿Por qué lo hace?", "Por seguridad", "Lo dice el Ministerio de Comercio, de forma explícita",
            src="ciberseguridad.jpg")),
  (1, card(kicker="Ministerio de Comercio · traducción", title="Lo esencial")),
  (1, g(G.g09_mofcom_security(1))),
  (1, g(G.g09_mofcom_security(2))),
  (1, g(G.g09_mofcom_security(3))),
  (2, card(kicker="El miedo concreto", **{"from": "EE. UU. copia un modelo chino"}, to="No es eso")),
  (1, card(kicker="El miedo concreto", title="Un grupo criminal con una herramienta que escribe código malicioso "
           "que se modifica solo")),
  (1, card(kicker="Concordia AI", title="No sale de la nada")),
  (1, card(kicker="Concordia AI", title="Meses de preocupación", body="Dentro de la administración china")),
  (1, card(kicker="Concordia AI", title="Meses de preocupación", body="Dentro de la administración china",
           punch={"zoom": 1.35, "at": [700, 540]})),
  (1, card(kicker="Concordia AI", title="Meses de preocupación",
           body="Ciberataques con IA: hasta ahora, solo en declaraciones de intenciones")),
  (1, g({**CAT(focus=True, heading=True), "seals": [SEAL_TEETH]})),
  (2, dict(photo("The empty control room of a power plant with gauges and switches.", "Mi lectura",
                 "Un motivo real, no una excusa", src="sala-control.jpg"),
           overlay={"kicker": "Mi lectura", "title": "Un motivo real, no una excusa", "body": "", "opinion": True})),
 ],
 7: [  # Pero no el único
  (2, photo("A generic container port at dawn with unmarked containers and cranes.", "Pero no el único",
            "Más motivos", "Seguridad económica · cadenas de suministro · tecnología estratégica", src="puerto.jpg")),
  (1, people("Un caso", "Meta y Manus", [
      {"name": "Meta", "org": "Quiso comprarla", "note": ""},
      {"name": "Manus", "org": "Agentes de IA", "note": ""}])),
  (1, people("Un caso", "Meta y Manus", [
      {"name": "Meta", "org": "Quiso comprarla", "note": ""},
      {"name": "Manus", "org": "Agentes de IA", "note": "Origen chino · constituida en Singapur"}], highlight=1)),
  (1, g(G.g10_manus(0))),
  (2, g(G.g10_manus(1))),
  (1, card(kicker="Quién la bloqueó", title="La NDRC", body="Comisión Nacional de Desarrollo y Reforma")),
  (1, card(kicker="Quién la bloqueó", title="La NDRC", body="El gran organismo de planificación económica de "
           "China · revisión de seguridad de inversión extranjera")),
  (1, g(G.g06_who(3))),
  (1, g(punch(G.g06_who(2), *M3))),
  (1, pj(P6, opinion=True, src="p06-balanza.jpg")),
  (1, g(G.g03_idea(2))),
  (3, g(G.g03_idea(2, "argumentada"))),
 ],
 8: [  # Lo que pesa una licencia: TikTok
  (2, card(title="¿Solo restringido?", stamp=[G.X])),
  (1, card(kicker="El caso", title="TikTok", body="Propiedad de ByteDance")),
  (1, g(G.g08b_row2020(level=False))),
  (1, g(G.g08b_row2020())),
  (1, card(kicker="Dicho en castellano", title="El algoritmo que decide qué vídeo ves después")),
  (1, photo("A generic unbranded smartphone on a pale desk showing a blurred abstract video feed.", "Con esa línea",
            "Veto de facto", "Sobre cualquier venta del negocio de TikTok en EE. UU.", src="movil.jpg")),
  (1, g(G.g11_tiktok(0))),
  (1, g(G.g11_tiktok(1))),
  (1, g(G.g11_tiktok(2))),
  (2, pj(P7, src="p07-espera.jpg")),
  (2, card(title="Alguien en Pekín tiene la llave", stamp=[G.X], opinion=True)),
  (1, card(kicker="Para ser justos · Concordia AI", title="La mayoría será mucho más fluida")),
  (2, card(kicker="Para ser justos · Concordia AI", title="TikTok fue un caso extremo",
           body="Pero enseña hasta dónde puede llegar la herramienta")),
 ],
 9: [  # Lo que ya está en vigor: DeepSeek y MiniMax
  (1, g(G.g12_register(1))),
  (1, g(punch(G.g12_register(1), *R2))),
  (2, g(punch(G.g12_register(1), *L2))),
  (1, card(kicker="Nota al margen", title="¿Suspender exportaciones?",
           body="Algunos abogados creen que el registro podría usarse para eso")),
  (1, card(kicker="Fuente", title="Una cuenta de redes sociales afiliada al Estado chino")),
  (1, g(G.g12_register(2))),
  (1, card(kicker="Concordia AI supone", title="Para sus últimos modelos", body="Los publicados después del borrador")),
  (3, pj(P8, src="p08-ventanilla.jpg")),
  (2, people("Un mensaje en dos direcciones", "Registraos, y tranquilos", [
      {"name": "Hacia dentro", "org": "Esto va en serio", "note": "Registraos"},
      {"name": "Hacia fuera", "org": "Tranquilos", "note": "Los modelos siguen saliendo"}], show=1, highlight=0,
      opinion=True)),
  (1, people("Un mensaje en dos direcciones", "Registraos, y tranquilos", [
      {"name": "Hacia dentro", "org": "Esto va en serio", "note": "Registraos"},
      {"name": "Hacia fuera", "org": "Tranquilos", "note": "Los modelos siguen saliendo"}], highlight=1,
      opinion=True)),
  (1, pic("A large origami elephant of plain grey paper in an empty bright room.", "elefante.jpg")),
 ],
 10: [  # Los modelos abiertos: protegidos, por ahora
  (1, photo("Server racks in a clean data centre with soft translucent download bars.", "Modelos abiertos",
            "Pesos que cualquiera puede descargar", src="servidores.jpg")),
  (1, card(kicker=CONCORDIA, title="¿Se acabó publicar en abierto?")),
  (1, card(kicker=CONCORDIA, title="¿Se acabó publicar en abierto?",
           seals=[{"lines": ["NO ES EL FIN"], "ink": "ink", "size": 170, "at": [1250, 720]}])),
  (1, quote(f"MOFCOM · {G.CONCORDIA_EN}", MOFCOM_OPEN_1, size=60)),
  (1, g(G.g13_mofcom_open(1))),
  (1, g(G.g13_mofcom_open(2))),
  (1, g(G.g13_mofcom_open(3))),
  (2, g(G.g14_lockers(1))),
  (1, g(G.g14_lockers(2))),
  (1, g(punch(G.g14_lockers(2), *M3))),
  (1, g(G.g14_lockers(3))),
  (1, pj(P9, src="p09-puerta.jpg")),
  (1, g({**G.g15_three_ways(), "highlight": -1})),
  (1, card(kicker="MIT · Apache", title="Licencias de código abierto", body="Son licencias de propiedad intelectual")),
  (1, g(G.g15_three_ways())),
  (1, g(G.g16_scale())),
  (1, card(kicker="Caixin", title="Un abogado", body="En una de las principales revistas económicas chinas")),
  (1, quote("Un abogado, vía Caixin · traducción", LAWYER_1, size=60)),
  (1, g(G.g16_lawyer())),
 ],
 11: [  # Cuatro caminos hacia la X o la J
  (1, g(WAYS(0))),
  (2, g(WAYS(1))),
  (1, g(punch(WAYS(1), 1300, ROW[0]))),
  (2, g(WAYS(2))),
  (1, g(punch(WAYS(2), 1300, ROW[1]))),
  (2, pj(P15, src="p15-archivador.jpg")),
  (3, g(WAYS(3))),
  (2, g(WAYS(4))),
  (1, g(punch(WAYS(4), 1300, ROW[3]))),
  (1, card(kicker="Una categoría aparte", title="«Contramedidas informáticas»", body="信息对抗技术")),
  (1, card(kicker="Una categoría aparte", title="¿Un modelo generalista puede caer ahí?",
           body="¿O solo las herramientas hechas para atacar?")),
  (1, card(kicker="Un ejemplo", title="ARTEX", body="Agente de pruebas de penetración. Su desarrollador chino lo "
           "pasó a código cerrado en octubre de 2026")),
  (1, card(kicker="Un ejemplo", title="ARTEX", body="Tras varios casos de mal uso",
           seals=[{"lines": ["CÓDIGO CERRADO"], "ink": "ink", "size": 130, "at": [1250, 700]}])),
  (1, g(WAYS(4, conclusion=True))),
  (1, g(punch(WAYS(4, conclusion=True), 1300, 900))),
  (2, g(G.g03_idea(3, "argumentada"))),
  (1, card(title="La letra la pone el ministerio", stamp=[G.J, G.X], opinion=True)),
 ],
 12: [  # Mientras tanto, en Washington
  (1, dict(g(G.g18_map()), motion=KB)),
  (1, g(G.g18_names())),
  (1, g({**G.g19_summit(1), "show": 1, "highlight": 0})),
  (1, g(G.g19_summit(1))),
  (2, g(G.g19_summit(2))),
  (2, g({**G.g20_notes(1), "highlight": 0})),
  (1, g({**G.g20_notes(1), "highlight": 1})),
  (1, g(G.g20_notes(2))),
  (1, g(punch(G.g20_notes(2), 760, 540, zoom=1.3))),
  (1, card(kicker="Traducción libre", title="«Llamadlo como queráis»", opinion=True)),
  (2, card(kicker="¿Y en noviembre?", title="No hay agenda oficial")),
  (1, card(kicker="Una propuesta", title="Yuyuan Tantian 玉渊谭天", body="Cuenta de WeChat que depende de CCTV")),
  (1, card(kicker="Una propuesta", title="Yuyuan Tantian 玉渊谭天", body="Cuenta de WeChat que depende de CCTV",
           seals=[{"lines": ["NO ES POSTURA OFICIAL"], "ink": "muted", "size": 110, "at": [1250, 760]}])),
  (1, quote("Punto 1 · el canal de incidentes", "«No puede quedarse en un acuerdo verbal»", size=80)),
  (1, g(G.g21_agenda(1))),
  (3, quote("Punto 2 · las definiciones", "«¿Qué cuenta como un riesgo grave? ¿Qué comportamientos de un modelo "
            "constituyen una pérdida de control seria?»", size=60)),
  (1, g(G.g21_agenda(3))),
  (3, pj(P10, opinion=True, src="p10-mesa.jpg")),
  (2, g(punch(G.g06_who(2), *M3))),
  (1, g(G.g06_who(4))),
  (1, card(kicker="Mi lectura", title="El ministerio que habla con Washington decide qué IA sale de China",
           opinion=True)),
  (1, card(kicker="Las dos notas de la cumbre", title="Ni rastro de los controles de exportación")),
  (1, g(G.g22_folders())),
  (2, pj(P14, src="p14-aparta-carpeta.jpg")),
 ],
 13: [  # Una China menos monolítica de lo que parece
  (1, g(G.g03_idea(5))),
  (1, card(kicker="Cómo solemos imaginarla", **{"from": "Una sola voz que baja de arriba"}, to="")),
  (1, card(kicker="Cómo solemos imaginarla", **{"from": "Una sola voz que baja de arriba"}, to="Un debate")),
  (1, g(G.g23_rules(1))),
  (1, g({**G.g23_rules(1), "highlight": 1})),
  (1, g(punch({**G.g23_rules(1), "highlight": 1}, *R2))),
  (1, card(kicker="Mayo de 2026", title="Plan legislativo del Consejo de Estado", body="El Gobierno chino")),
  (2, g(G.g23_rules(2))),
  (1, photo("A generic modern university campus in an East Asian city in autumn.", "Mediados de octubre de 2026",
            "Dos borradores no oficiales", "De una posible ley nacional de IA", src="campus.jpg")),
  (1, g(G.g24_drafts(0))),
  (1, card(kicker="Universidad de Zhejiang", title="¿Es apto para la tarea?")),
  (1, stamps({"lines": ["CAPACIDAD", "DE ACTUAR"], "ink": "ink", "size": 80},
             {"lines": ["FIABILIDAD"], "ink": "ink", "size": 80},
             {"lines": ["QUÉ HAY", "EN JUEGO"], "ink": "ink", "size": 80}, kicker="Universidad de Zhejiang",
             title="Gobernanza por idoneidad")),
  (1, g(G.g24_drafts(1))),
  (1, card(kicker="Lin Qianduo · artículo 22", title="Controles a los modelos abiertos con capacidad de ciberataque")),
  (1, g(punch(WAYS(4), 1300, ROW[3], zoom=1.3))),
  (2, pj(P11, src="p11-seminario.jpg")),
  (1, g(G.g25_jurists(1))),
  (1, quote("Zhang Wenxian", "«Avanza en todos los frentes y se acelera»", size=80)),
  (1, g(G.g25_jurists(2))),
  (1, card(kicker="Shou Bu", **{"from": "Una ley de IA independiente"}, to="¿«Legislación integral»?",
           body="Nombre, rango y contenido, todavía abiertos")),
  (1, stamps({"lines": ["UNIVERSIDADES"], "ink": "muted", "size": 84, "angle": 4},
             {"lines": ["DESPACHOS"], "ink": "ink", "size": 84, "angle": -7},
             {"lines": ["ACADÉMICOS"], "ink": "copper", "size": 84, "angle": 6},
             kicker="Quién empuja", title="Cada uno en una dirección")),
  (1, card(kicker="Concordia AI", title="Lejos de ser monolítico")),
  (2, g(G.g03_idea(5, "argumentada"))),
  (1, ficha(argued=5)),
 ],
 14: [  # Lo que no encaja con mi lectura
  (3, pj(P12, src="p12-boli-rojo.jpg")),
  (2, g(G.g03_idea(state="argumentada", nuance=1))),
  (1, card(kicker="Matiz 1 · es un borrador", title="Comentarios hasta el 15 de noviembre",
           body="Concordia AI: las líneas generales no cambiarán mucho; los detalles, quizá")),
  (1, dict(ficha(argued=5, nuances=1), motion=KB)),
  (1, g(G.g03_idea(state="argumentada", nuance=2))),
  (1, card(kicker="Matiz 2 · el impacto inmediato", title="Lo dicen ellos mismos", body="Fuente: Concordia AI")),
  (1, card(kicker="Matiz 2 · lo dicen ellos mismos", title="Para DeepSeek, quizá un trámite más",
           body="Si los modelos acaban en la X y la licencia es automática")),
  (1, ficha(argued=5, nuances=2)),
  (2, g(G.g03_idea(state="argumentada", nuance=3))),
  (1, card(kicker="Mi lectura", title="«Por ahora», no «para siempre»", opinion=True)),
  (1, g(G.g03_idea(state="argumentada", nuance=4))),
  (1, g(G.g08b_row2020())),
  (1, g(G.g10_manus(1))),
  (2, g(G.g06_who(3))),
  (2, g(G.g03_idea(state="argumentada", nuance=5))),
  (1, card(kicker="Matiz 5 · las conversaciones", title="Agenda sin confirmar",
           body="La propuesta viene de una cuenta estatal, no del Gobierno")),
  (1, g(G.g20_notes(1))),
  (1, g(G.g03_idea(state="argumentada", nuance=6))),
  (1, card(kicker="Matiz 6", **{"from": "Muchas voces"}, to="≠ decisión descentralizada")),
  (1, g(G.g23_rules(2))),
  (1, g(G.g24_drafts())),
  (1, card(kicker="Matiz 6", title="Debate entre juristas, no pluralismo político",
           body="Puede acabar en una decisión tomada en el mismo sitio de siempre")),
  (3, ficha(argued=5, nuances=6)),
  (1, card(kicker="Mi lectura", title="Misma dirección, camino más lento",
           body="Y más negociado de lo que sugieren los titulares", opinion=True)),
 ],
 15: [  # Final: cinco años o «presentar y salir»
  (1, g(G.g26_columns(1))),
  (2, g(punch(G.g26_columns(1), *L2, zoom=1.3))),
  (1, g(G.g26_columns(2))),
  (1, g(punch(G.g26_columns(2), *R2, zoom=1.3))),
  (2, dict(g(G.g26_scale()), motion=KB)),
  (1, g(G.g26_columns(2))),
  (1, g({**G.g26_columns(2, tiktok_grey=True), "opinion": True,
         "seals": [{"lines": ["LA MISMA NORMA"], "ink": "ink", "size": 110, "at": [960, 950]}]})),
  (1, dict(stamps({"lines": ["LA VOLUNTAD", "DE QUIEN", "LA APLICA"], "ink": "ink"}, opinion=True), tail=0.5)),
  (1, dict(g(G.g02_seals("both")), motion=KB)),
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
        sentences = split_long([s for p in module.narration.split("\n\n") for s in split_sentences(p)])
        if sum(k for k, _ in plan) != len(sentences):
            raise SystemExit(f"module {n}: plan covers {sum(k for k, _ in plan)} sentences, script has {len(sentences)}")
        shots, i = [], 0
        if pictures:
            shutil.rmtree(IMAGES / f"module{n}", ignore_errors=True)
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

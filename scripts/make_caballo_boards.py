"""Write storyboards/caballo/module1-5.yaml from a compact shot plan (pizarra theme).

Same scheme as make_consenso_boards: each plan row is (number of sentences, shot fields);
sentences are split one paragraph at a time, the way 'narrate' splits them, and a shot
never crosses a paragraph. Pictures are few and reused: each image shot names a picture
in IMAGES; every shot that shows it gets its own copy in assets/images/caballo/moduleN/
(git stores the bytes once), with its own pan. Picture prompts are full prompts: style
and cast are spelled out the same way every time. No real people, no logos.
Run: .venv/bin/python -m scripts.make_caballo_boards  (from the repo root)
     add --pictures DIR to copy DIR/KEY.jpg to every shot that shows picture KEY.
"""
import json
import shutil
import sys
from pathlib import Path

import yaml

from scripts.make_japon_boards import NoAliases
from studio.parse import parse_script, split_sentences

SCRIPT = Path("examples/caballo.md")
OUT = Path("storyboards/caballo")
PICTURES = Path("storyboards/caballo/pictures.json")   # shot id -> picture key, for copying the files

STYLE = ("Flat 2D hand-drawn vector cartoon in a minimalist whiteboard-animation style, thin black outlines,"
         " muted earthy colours (browns, slate blue, soft greens and tans), plain flat very light blue background"
         " (#e4f4fd) with lots of empty space, a single thin ground line near the bottom, gently humorous, not dark."
         " No text, no letters, no numbers, no logos, no brand marks, no watermark. Wide 16:9 frame.")
HORSE = ("The Horse: a friendly brown cartoon horse with a darker brown mane and tail, oversized expressive round"
         " eyes, mobile ears, a simple rounded body and thin black outlines.")
WORKER = ("The Human Worker: a simple black stick figure with a round white head and a simple face, small floating"
          " hands with no arms, wearing a small white shirt and a green tie.")
ECON = ("Economists: simple stick figures with round glasses and small bowties.")
AI = ("The AI: a cartoon figure in the same flat style with a faceless smooth white mannequin head (no eyes, no"
      " mouth, no features), a charcoal bird's-eye weave suit, a burgundy tie with a small gold paisley pattern, a"
      " burgundy and gold paisley pocket square, and a koi-fish watercolour Hawaiian shirt in blue, gold and orange"
      " under the suit jacket.")
ROBOT = "A generic machine: a sleek white stick-figure robot with a glowing blue visor and a small antenna."
SKY = " Keep the upper third of the frame empty."

# picture key -> (scene, cast). Cast text is appended verbatim so every prompt describes them the same way.
IMAGES = {
    "grazing": ("The Horse grazing peacefully on soft green grass behind a simple white wooden fence, a small tree,"
                " calm sunny day." + SKY, [HORSE]),
    "plough": ("The Horse sweating with effort, pulling a heavy old wooden plough through brown furrows of a field,"
               " drops of sweat flying, a farmer stick figure guiding the plough." + SKY, [HORSE]),
    "capstan": ("The Horse walking in a circle on a dirt track, harnessed to a long wooden pole that turns a simple"
                " old wooden hay press and grinding mill on a farm, a dotted circular path behind it." + SKY, [HORSE]),
    "placards": ("Three economists standing side by side on the ground line, together holding up one large wide"
                 " blank white rectangular placard on two wooden sticks above their heads, the placard completely"
                 " empty and facing the viewer, confident smiles.", [ECON]),
    "hooves": ("The Human Worker sitting at a simple office desk with a computer, wearing brown rubber horse-hoof"
               " puppets on both hands, typing clumsily on the keyboard, a stack of papers, looking slightly"
               " worried." + SKY, [WORKER]),
    "street": ("A busy old city street around the year 1900 drawn simply: a horse-drawn delivery wagon, a"
               " horse-drawn tram and a horse-drawn carriage with brown horses, simple generic brick buildings"
               " behind, stick-figure pedestrians.", []),
    "steam": ("The Horse standing next to an old black steam engine on wheels, both the same size, the horse"
              " looking at the machine sideways with suspicion, a little puff of steam.", [HORSE]),
    "manure": ("An old city street with small brown piles of manure on the cobbles, a stick-figure pedestrian"
               " holding his nose and tiptoeing between them, The Horse looking embarrassed with its ears down,"
               " little wavy stink lines.", [HORSE]),
    "tractors": ("The Horse in a field, shocked with huge eyes and ears straight up, as a line of three generic"
                 " unbranded green tractors drives in from the right towards it." + SKY, [HORSE]),
    "cars": ("An old city street around 1912 crowded with generic unbranded vintage automobiles in slate blue and"
             " dark green, and The Horse standing among them confused and squeezed, looking around.", [HORSE]),
    "collar": ("The Horse in a simple wooden barn, hanging its leather work collar on a wooden peg on the wall,"
               " like clocking out for the last time, a calm resigned look, a little wooden bench." + SKY, [HORSE]),
    "trucker": ("The Human Worker happily driving a generic unbranded slate-blue 1920s truck along a road, waving"
                " from the open cab, while The Horse stands at the roadside watching it go.", [WORKER, HORSE]),
    "horsecab": ("The Horse awkwardly trying to sit in the small cab of a generic unbranded slate-blue truck,"
                 " squeezed in, legs sticking out of the window, hooves unable to hold the steering wheel, funny"
                 " embarrassed look.", [HORSE]),
    "oats": ("The Horse looking thin and sad in front of a nearly empty small bucket with a few oats, next to a"
             " generic unbranded green tractor that stands strong and shiny." + SKY, [HORSE]),
    "stairs": ("A big simple staircase of three wide steps rising from left to right: on the lowest step a small"
               " farm with a barn and wheat, on the middle step a simple factory with a chimney, on the top step a"
               " simple office building; small stick-figure workers with white shirts and green ties climbing up"
               " the steps.", [WORKER]),
    "aidesk": ("The AI sitting at a simple office desk working at great speed with four floating screens showing"
               " simple charts, code lines and documents, papers flying out finished, while The Human Worker"
               " stands beside it with an empty desk, scratching its head." + SKY, [AI, WORKER]),
    "piggyback": ("The Human Worker riding piggyback on the shoulders of The AI, holding on happily and pointing"
                  " forward, The AI walking calmly along the ground line carrying it.", [AI, WORKER]),
    "meme": ("The Horse sitting proudly in the seat of a generic unbranded green tractor in front of a red wooden"
             " barn, front hooves on the steering wheel, while a farmer stick figure with a straw hat stands"
             " next to it talking to it reassuringly.", [HORSE]),
    "selfdriving": ("A generic unbranded green tractor driving itself across a field with its seat completely"
                    " empty, while The Horse and a farmer stick figure with a straw hat stand side by side at the"
                    " edge of the field watching it, both out of work." + SKY, [HORSE]),
    "robotaxi": ("A generic unbranded slate-blue driverless car with a small sensor dome on the roof driving along"
                 " the ground line, the driver seat empty, a relaxed stick-figure passenger sitting in the back"
                 " seat reading." + SKY, []),
    "aidriver": ("A generic unbranded slate-blue car seen from the side, facing right, driving along the road:"
                 " The AI alone in the front driver seat with both hands on the real steering wheel, driving"
                 " confidently; The Human Worker sits in the back seat holding a small detached toy steering"
                 " wheel that is connected to nothing, puzzled.", [AI, WORKER]),
    "therapy": ("A small happy child stick figure riding The Horse slowly along a path, a parent stick figure"
                " walking beside holding the reins, flowers, a peaceful leisure and therapy ride." + SKY, [HORSE]),
    "essential": ("Two small scenes side by side on the same ground line: on the left a nurse stick figure holding"
                  " the hand of a patient in a hospital bed; on the right a musician stick figure sweating as he"
                  " plays guitar on a small wooden stage for a few clapping stick figures." + SKY, []),
    "horseshare": ("The Horse standing at a wooden easel, proudly holding up a large gold share certificate with"
                   " an ornate border and no writing, the certificate crumbling and collapsing into pieces,"
                   " the horse looking surprised." + SKY, [HORSE]),
    "workershare": ("The Human Worker standing next to a wooden easel holding a large gold share certificate with"
                    " an ornate border and no writing; a dotted gold arrow runs from the certificate to a generic"
                    " unbranded self-driving green tractor with an empty seat that is stacking hay bales in a"
                    " field on the right." + SKY, [WORKER]),
    "machines": ("A wide landscape along one ground line: generic white robots and a generic self-driving green"
                 " tractor working a field and a small factory with a chimney, busy and productive, while The"
                 " Human Worker sits relaxed on a bench in the foreground reading a book.", [WORKER, ROBOT]),
}


def prompt(key: str) -> str:
    scene, cast = IMAGES[key]
    return " ".join([scene, *cast])  # the storyboard adds STYLE (Storyboard.image_prompt)


def img(key, motion="pan_right", **kw):
    return dict(type="image", picture=key, prompt=prompt(key), motion=motion, **kw)


def note(key, text, motion="pan_right", **o):
    """A picture with a handwritten phrase in its empty sky (the text stays still while the picture pans)."""
    return dict(type="text_overlay", picture=key, prompt=prompt(key), motion=motion, overlay={"note": text, **o})


def placard(key, text, box, strike=""):
    """Words written on the blank placard of a picture; the picture does not move, so they stay on it."""
    o = {"placard": text, "box": box}
    if strike:
        o["strike"] = strike
    return dict(type="text_overlay", picture=key, prompt=prompt(key), motion="none", overlay=o)


def card(kicker, title, body="", **o):
    return dict(type="text_overlay", overlay={"kicker": kicker, "title": title, "body": body, **o})


def gfx(**overlay):
    return dict(type="text_overlay", overlay=overlay)


def phrase(text, **o):
    return gfx(phrase=text, **o)


def stat(big, label, **o):
    return gfx(big=big, label=label, **o)


def herd(title, horses=None, tractors=None):
    rows = []
    if horses is not None:
        rows.append({"label": "Caballos y mulas", "text": horses[1], "icon": "horse", "value": horses[0],
                     "ghost": 26.7 if horses[0] < 26.7 else 0})
    if tractors is not None:
        rows.append({"label": "Tractores", "text": tractors[1], "icon": "tractor", "value": tractors[0], "color": "slate"})
    return gfx(kicker="Granjas de Estados Unidos", title=title, rows=rows)


def jobs(drivers=False, grooms=False, trucks=False):
    bars = [{"label": "Conductores de carruajes", "before": 100, "after": 25, "text": "-75 %", "show": drivers},
            {"label": "Mozos de cuadra", "before": 100, "after": 10, "text": "-90 %", "show": grooms}]
    if trucks:
        bars.append({"label": "Chóferes y camioneros", "before": 46000, "after": 800000, "text": "de 46.000 a 800.000",
                     "color": "slate"})
    return gfx(kicker="1910-1930", title="Los oficios del caballo", bars=bars, text_room=470, text_size=54)


def parcels(feed, caption=""):
    return gfx(parcels=True, kicker="1880-1920", title="Uno de cada cuatro acres", feed=feed, caption=caption)


def week(caption=""):
    return gfx(week=True, value=57, kicker="McKinsey, noviembre de 2025", title="Lo que la tecnología actual ya podría automatizar",
               caption=caption)


WHY = ["mejores", "más rápidas", "más baratas", "más seguras"]
TRACTOR = ["No se cansa a mitad de la tarde", "No se asusta con un ruido fuerte", "No come en invierno"]
NOT_A_HORSE = "las personas no somos caballos"

TITLES = {1: "Tú eres el próximo caballo", 2: "El imperio del caballo", 3: "Cómo las máquinas reemplazaron al caballo",
          4: "Por qué los humanos son el próximo caballo", 5: "Demanda derivada, demanda esencial y economía post-laboral"}
SUBTITLES = {1: "El caballo moderno y la gran mentira económica"}

P = {
 1: [
  (1, dict(type="title_card", lead_in=1.2)),
  (1, img("grazing")),
  (2, img("grazing", motion="pan_left")),
  (1, stat("6,6 millones", "de caballos en Estados Unidos, hoy", kicker="Hoy", icon="horse", icons=3, icon_size=170)),
  (1, gfx(kicker="Según el Consejo Ecuestre Estadounidense", title="Para qué los mantenemos", list=["el deporte", "la recreación", "la terapia"])),
  (1, phrase("no porque la economía los necesite", strike="la economía los necesite", note="porque nos gustan")),
  (1, card("Si mañana dejaran de trabajar...", "Las cadenas de suministro ni se inmutarían")),
  (1, note("plough", "Hace apenas un siglo")),
  (1, stat("26,7 millones", "de caballos y mulas en las granjas", kicker="1918", icon="horse", icons=5, icon_size=150)),
  (1, gfx(gauge=89, kicker="1920", title="La fuerza de tiro del campo", caption="la ponían caballos y mulas")),
  (2, note("capstan", "El motor del mundo", color="brown")),
  (1, img("tractors")),
  (1, phrase("indispensable", strike="indispensable", note="irrelevante en una sola vida", size=150)),
  (1, card("Mi tesis", "Lo mismo le va a ocurrir a la mayoría de los trabajadores humanos")),
  (1, placard("placards", NOT_A_HORSE, [0, 0, 0, 0])),
  (1, phrase(NOT_A_HORSE, quote=True)),
  (1, phrase(NOT_A_HORSE, quote=True, strike="no", note="Yo creo que se equivocan")),
  (1, note("hooves", "Tú eres el próximo caballo", tail=1.0)),
 ],
 2: [
  (1, dict(type="title_card", lead_in=1.2)),
  (1, note("street", "La infraestructura de la sociedad", at=[960, 60], size=80)),
  (1, img("plough", motion="pan_left")),
  (1, img("street", motion="pan_left")),
  (1, img("capstan")),
  (2, img("steam")),
  (1, phrase("«caballos de fuerza»", color="brown", note="el fantasma del animal", note_color="slate")),
  (1, card("Una economía entera", "Organizada alrededor del caballo")),
  (1, stat("440.000", "personas conducían carros, vagones y carruajes", kicker="1910", icon="worker", icons=5, icon_size=170, color="slate")),
  (1, stat("Más de 100.000", "mozos de cuadra, herreros, talabarteros y constructores de carruajes", kicker="1910", color="slate")),
  (1, parcels(False, "la fuerza laboral de cuatro patas tenía que comer")),
  (1, parcels(True, "para alimentar caballos y mulas")),
  (1, parcels(True, "avena y heno, en lugar de comida para las personas")),
  (2, img("manure")),
  (1, stat("130.000", "caballos en la ciudad de Nueva York", kicker="1900", icon="horse", icons=5, icon_size=150)),
  (1, stat("7 a 14 kilos", "de estiércol al día, cada caballo", kicker="Nueva York, 1900")),
  (1, gfx(pile=1.0, value="900-1.800 t", kicker="Nueva York, 1900 · 130.000 caballos", title="Estiércol cada día")),
  (1, img("manure", motion="pan_left")),
  (2, stat("15.000", "cadáveres de caballos retirados de la vía pública", kicker="Nueva York, 1880", color="ink")),
  (1, stat("15.000", "cadáveres de caballos retirados de la vía pública", kicker="Nueva York, 1880", color="ink",
           small="unos 41 al día")),
  (1, phrase("Y eran peligrosos", size=140)),
  (1, stat("200", "personas muertas por caballos y sus vehículos", kicker="Nueva York, 1900", color="ink")),
  (1, card("Ajustado por población", "Más mortal que los coches", "que los accidentes de coche en la misma ciudad en 2003")),
  (1, gfx(kicker="El caballo era", title="", list=["sucio", "caro de alimentar", "frágil", "peligroso"])),
  (1, note("capstan", "Pero no había alternativa", motion="pan_left")),
 ],
 3: [
  (1, dict(type="title_card", lead_in=1.2)),
  (1, note("tractors", "Tarea a tarea, oficio a oficio")),
  (1, img("cars")),
  (1, stat("1912", "más automóviles que caballos en el tráfico de Nueva York", kicker="Nueva York", icon="car", icons=4, icon_size=190, color="slate")),
  (1, stat("1922", "el último camión de bomberos tirado por caballos sale por última vez", kicker="Nueva York")),
  (1, phrase("el rey de la calle", strike="el rey de la calle", note="una reliquia", size=140)),
  (1, img("tractors", motion="pan_left")),
  (1, herd("1920", horses=(26.7, "26,7 M"), tractors=(0.246, "246.000"))),
  (1, herd("1960", tractors=(4.5, "4,5 M"))),
  (1, herd("1960", horses=(3, "3 M"), tractors=(4.5, "4,5 M"))),
  (1, img("collar")),
  (2, note("collar", "Simplemente dejaron de nacer", motion="pan_left")),
  (1, card("1940", "Menos de la mitad de los potros necesarios", "para mantener estable la población")),
  (1, jobs()),
  (1, jobs(drivers=True)),
  (1, jobs(drivers=True, grooms=True)),
  (1, card("El milagro de los economistas", "El trabajo nuevo se trasladó a las máquinas nuevas")),
  (1, jobs(drivers=True, grooms=True, trucks=True)),
  (1, card("Teamsters, 1903", "Hombres que conducían equipos de caballos")),
  (1, stat("Hoy", "el mismo sindicato representa a los conductores de camiones pesados", icon="truck", icons=3, icon_size=200, color="slate")),
  (1, img("trucker")),
  (1, img("horsecab")),
  (1, gfx(kicker="¿Por qué ganaron las máquinas?", title="Eran...", list=WHY, show=0)),
  (1, gfx(kicker="¿Por qué ganaron las máquinas?", title="Eran...", list=WHY)),
  (1, card("La regla de hierro", "de cualquier automatización")),
  (1, gfx(kicker="Un tractor", title="", list=TRACTOR, show=1)),
  (1, gfx(kicker="Un tractor", title="", list=TRACTOR, show=2)),
  (1, gfx(kicker="Un tractor", title="", list=TRACTOR, show=3)),
  (1, note("oats", "Bajar el «salario» del caballo")),
  (1, img("oats", motion="pan_left")),
  (1, card("1983", "Wassily Leontief", "economista y premio Nobel")),
  (1, phrase("las raciones tienen límites biológicos", note="y los salarios humanos también")),
  (1, gfx(kicker="Un trabajador necesita un mínimo", title="", list=["para comer", "para vestirse", "para tener un techo"])),
  (1, card("Leontief predijo", "Primero disminuyeron su papel", "y luego lo eliminaron por completo")),
 ],
 4: [
  (1, dict(type="title_card", lead_in=1.2)),
  (1, placard("placards", "¿Seguirán los humanos el camino de los caballos?", [0, 0, 0, 0])),
  (1, placard("placards", "los humanos no somos caballos", [0, 0, 0, 0])),
  (1, phrase("Tú no eres un caballo", quote=True)),
  (1, card("Para ser justos", "Han tenido razón durante 200 años")),
  (2, img("stairs")),
  (1, note("stairs", "Siempre hubo un escalón superior", motion="pan_left", at=[960, 50], size=80)),
  (1, phrase("hoy sí somos caballos", note="por dos razones")),
  (1, img("hooves")),
  (1, phrase("grunt work", note="trabajo rutinario y repetitivo", size=150)),
  (1, gfx(of=10, hit=8, kicker="Las 10 ocupaciones más grandes de EE. UU.", label="pagan menos que el salario medio nacional")),
  (1, gfx(kicker="Entre ellas", title="", list=["cajero", "trabajador de comida rápida", "vendedor de tienda",
                                                  "reponedor", "oficinista"])),
  (1, gfx(of=100, hit=59, kicker="Empleos en Estados Unidos", label="piden secundaria o ninguna credencial formal")),
  (1, phrase("astrofísicos, cirujanos y poetas", strike="astrofísicos, cirujanos y poetas",
             note="tareas estructuradas, predecibles y repetitivas")),
  (1, placard("placards", "Pero espera", [0, 0, 0, 0])),
  (1, card("La segunda razón", "Trabajo de pensamiento")),
  (1, gfx(kicker="Trabajo de pensamiento", title="", list=["redactar informes", "programar", "analizar datos",
                                                            "atender clientes"])),
  (1, img("aidesk")),
  (1, phrase("del músculo al cerebro")),
  (1, phrase("del músculo al cerebro", strike="cerebro", note="¿y ahora, a qué órgano?")),
  (1, card("McKinsey, noviembre de 2025", "Solo tecnología ya demostrada", "sin especular con inventos futuros")),
  (1, week()),
  (1, week("todo el lunes, todo el martes y la mayor parte del miércoles")),
  (1, gfx(kicker="Si una máquina lo hace", title="", list=["mejor", "más rápido", "más barato", "más seguro"])),
  (1, phrase("el mercado elegirá a la máquina", note="Siempre.", note_size=110)),
  (1, phrase("La IA no te quitará el trabajo; alguien que use IA te quitará el trabajo", quote=True, size=100)),
  (1, img("piggyback")),
  (1, img("meme")),
  (1, img("meme", motion="pan_left")),
  (1, phrase("El meme es absurdo", size=140)),
  (1, img("selfdriving")),
  (1, note("selfdriving", "Mil granjas, una sola operación", motion="pan_left")),
  (1, img("trucker", motion="pan_left")),
  (1, img("trucker")),
  (2, card("Durante un siglo, funcionó", "Empleos de clase media", "y poder de negociación")),
  (1, img("robotaxi")),
  (1, stat("500.000", "viajes pagados por semana, sin conductor", kicker="Marzo de 2026", icon="car", icons=3, icon_size=190, color="slate")),
  (1, stat("500.000", "viajes pagados por semana, sin conductor", kicker="Marzo de 2026", icon="car", icons=3, icon_size=190, color="slate",
           small="unas 50 veces por minuto")),
  (1, phrase("alguien usando IA te quitará el trabajo", quote=True, strike="alguien usando", size=96)),
  (1, img("aidriver")),
 ],
 5: [
  (1, dict(type="title_card", lead_in=1.2)),
  (1, img("collar", motion="pan_left")),
  (1, card("La verdad incómoda", "A la economía nunca le importó el caballo")),
  (1, phrase("un mamífero de media tonelada", strike="un mamífero de media tonelada", note="querían tracción")),
  (1, img("plough")),
  (1, phrase("el mejor contenedor para esa fuerza", note="... hasta que dejó de serlo")),
  (1, card("En economía", "Demanda derivada")),
  (1, card("Demanda derivada", "La de caballos derivaba de la de transporte", "y de fuerza agrícola")),
  (1, stat("0", "demanda derivada del caballo", kicker="Cuando apareció algo mejor", size=300)),
  (1, note("therapy", "6,6 millones de caballos de ocio", size=84)),
  (2, img("therapy", motion="pan_left")),
  (1, card("La llamo", "Demanda esencial")),
  (1, card("Demanda esencial", "También para los seres humanos")),
  (1, img("essential")),
  (2, note("essential", "Es real. No va a desaparecer.", motion="pan_left", size=84)),
  (2, phrase("una demanda delgada", note="Es un nicho.")),
  (1, card("Un pequeño porcentaje", "Nunca un mercado laboral masivo", "para miles de millones de personas")),
  (2, card("Investigadores del MIT", "Una diferencia que importa")),
  (1, card("La diferencia", "Las personas pueden poseer capital", "y los caballos no")),
  (1, img("horseshare")),
  (2, img("horseshare", motion="pan_left")),
  (1, card("Economía post-laboral", "La propiedad del capital", "la otra mitad")),
  (1, img("workershare")),
  (1, phrase("vender nuestras horas", strike="vender nuestras horas", note="su precio va hacia el suelo")),
  (1, card("Economía post-laboral", "El trabajo humano deja de ser una restricción vinculante")),
  (2, note("plough", "Más caballos, más trabajadores", motion="pan_left")),
  (1, note("selfdriving", "Sin importar cuántos caballos hubiera")),
  (1, img("machines")),
  (1, img("machines", motion="pan_left")),
  (1, note("hooves", "Tú eres el próximo caballo", motion="pan_left")),
  (1, img("oats")),
  (1, img("meme")),
  (1, phrase("Aprender a conducir el tractor", strike="conducir el tractor", note="no te salvará")),
  (1, note("workershare", "Ser dueño de una parte de ese tractor", motion="pan_left", color="gold", tail=2.0)),
 ],
}

# picture key -> where its blank placard is, in frame pixels [x0, y0, x1, y1] (measured on the picture)
PLACARD_BOXES = {"placards": [585, 140, 1335, 440]}


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    modules = {m.number: m for m in parse_script(SCRIPT.read_text(encoding="utf-8"))}
    pictures = {}
    for n, plan in P.items():
        paragraphs = [split_sentences(p) for p in modules[n].narration.split("\n\n")]
        sentences = [s for p in paragraphs for s in p]
        para_of = [k for k, p in enumerate(paragraphs) for _ in p]
        if sum(k for k, _ in plan) != len(sentences):
            raise SystemExit(f"module {n}: plan covers {sum(k for k, _ in plan)} of {len(sentences)} sentences")
        shots, i = [], 0
        for j, (k, fields) in enumerate(plan, 1):
            if para_of[i] != para_of[i + k - 1]:
                raise SystemExit(f"module {n} shot {j}: crosses a paragraph ({sentences[i][:40]!r})")
            fields = dict(fields)
            shot = {"id": f"h{n}-{j:02d}"}
            if key := fields.pop("picture", None):
                pictures[shot["id"]] = key
                if "placard" in fields.get("overlay", {}):
                    fields["overlay"] = {**fields["overlay"], "box": PLACARD_BOXES[key]}
            shot.update(fields)
            if shot["type"] == "title_card":
                shot["title"] = TITLES[n]
                shot["subtitle"] = SUBTITLES.get(n, "Introducción" if n == 1 else f"Parte {n - 1}")
            shot["text"] = " ".join(sentences[i:i + k])
            i += k
            shots.append(shot)
        board = {"module": n, "voice": "es-ES-AlvaroNeural", "theme": "pizarra", "style": STYLE,
                 "character": "", "shots": shots}
        head = (f"# Tú eres el próximo caballo, module {n}. Generated by scripts/make_caballo_boards.py; edit the "
                "plan there.\n# Shots are whole sentences. Images are in assets/images/caballo/"
                f"module{n}/ (pictures reused across shots: see storyboards/caballo/pictures.json).\n")
        (OUT / f"module{n}.yaml").write_text(head + yaml.dump(board, Dumper=NoAliases, allow_unicode=True,
                                                               sort_keys=False, width=110), encoding="utf-8")
        print(f"module {n}: {len(shots)} shots, {sum('prompt' in s for s in shots)} with pictures")
    PICTURES.write_text(json.dumps(pictures, indent=1) + "\n", encoding="utf-8")
    if "--pictures" in sys.argv:
        src = Path(sys.argv[sys.argv.index("--pictures") + 1])
        for shot_id, key in pictures.items():
            n = shot_id[1:].split("-")[0]
            dest = Path("assets/images/caballo") / f"module{n}" / f"{shot_id}.jpg"
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(src / f"{key}.jpg", dest)
        print(f"copied pictures for {len(pictures)} shots")
    used = set(pictures.values())
    print(f"{len(used)} distinct pictures; unused: {sorted(set(IMAGES) - used)}")


if __name__ == "__main__":
    main()

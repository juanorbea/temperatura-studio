"""Write storyboards/consenso-sf/module1-9.yaml from a compact shot plan (editorial theme).

Same scheme as make_potencias_boards: sentences split one paragraph at a time, the way
'narrate' splits them; each plan row is (number of sentences, shot fields).
Real people appear only as text cards, never as images. No logos.
Run: .venv/bin/python -m scripts.make_consenso_boards  (from the repo root)
"""
from pathlib import Path

import yaml

from scripts.make_japon_boards import NoAliases, card, graphic, img, photo_card
from studio.parse import parse_script, split_sentences

SCRIPT = Path("examples/consenso-sf.md")
OUT = Path("storyboards/consenso-sf")
STYLE = yaml.safe_load(Path("storyboards/module1.yaml").read_text(encoding="utf-8"))
HERO = (" Vivid warm sunset over a calm sea, thin luminous streams of data light flowing over the water"
        " towards the horizon, wide cinematic hero shot.")


def bars(hi):
    return graphic(kicker="En dólares de hoy", title="Más caro que ir a la Luna", highlight=hi, bars=[
        {"label": "Apolo", "note": "más de una década", "value": 180000, "text": "~180.000 M$"},
        {"label": "IA privada EE. UU.", "note": "solo 2024", "value": 109100, "text": "109.100 M$"},
        {"label": "Proyecto Manhattan", "note": "", "value": 11600, "text": "~11.600 M$"}])


def bosses(hi):
    return graphic(kicker="2025 · Lo dicen en voz alta", title="Los jefes de la IA y sus plazos", highlight=hi, people=[
        {"name": "Sam Altman", "org": "OpenAI", "quote": "Sabemos cómo construir la AGI", "when": "Ya"},
        {"name": "Demis Hassabis", "org": "DeepMind",
         "quote": "Todas las capacidades cognitivas que tienen los humanos", "when": "3-5 años"},
        {"name": "Dario Amodei", "org": "Anthropic", "quote": "IA poderosa", "when": "2-3 años"}])


def ideas(hi, caption=""):
    return graphic(kicker="El Consenso de San Francisco", title="Tres ideas en las que casi todos están de acuerdo",
                   highlight=hi, caption=caption, figures=[
                       {"value": "1", "label": "Leyes de escalado"},
                       {"value": "2", "label": "Superinteligencia en 2-5 años"},
                       {"value": "3", "label": "Beneficios sin precedentes"}])


def world():
    return graphic(kicker="Un consenso local", title="Dónde se lo creen", caption="Fuera de Silicon Valley, el consenso no es tan consenso",
                   lit=[{"name": "San Francisco", "lon": -122.4, "lat": 37.8}],
                   regions=[{"name": "Europa · más escéptica", "lon": 12, "lat": 50},
                            {"name": "China · aplicaciones prácticas", "lon": 104, "lat": 34}])


LOOP = ["La IA mejora a la IA", "Cada versión hace una mejor", "La IA mejora a la IA más rápido"]


def loop(step, curve=""):
    return graphic(kicker="Auto-mejora recursiva", title="Un bucle que se acelera", loop=LOOP, step=step, curve=curve)


def revs(hi, caption=""):
    return graphic(kicker="Según Schmidt", title="Tres revoluciones", highlight=hi, caption=caption, figures=[
        {"value": "Lenguaje", "label": "Hecho"}, {"value": "Agentes", "label": "En marcha"},
        {"value": "Razonamiento", "label": "La gran apuesta"}])


def plants(shown):
    return graphic(kicker="El límite material", title="La energía cuesta mucho más de escalar", icons=92, shown=shown,
                   label="centrales nucleares más que podría necesitar Estados Unidos para la IA")


def growth(hi):
    return graphic(kicker="La economía", title="Los números del consenso", highlight=hi, figures=[
        {"value": "+0,5", "label": "puntos de crecimiento al año: deuda federal bajo control (CBO)"},
        {"value": "x2", "label": "productividad de cada trabajador"},
        {"value": "20-30 %", "label": "de crecimiento anual"}])


def jcurve(phase):
    return graphic(kicker="Primera pregunta · ¿Cuándo?", title="Una curva en J", jcurve=["Años de inversión", "Los frutos"],
                   phase=phase, baseline="Sin IA", time="Tiempo")


def camps(hi):
    return graphic(kicker="Segunda pregunta · ¿Para quién?", title="Dos lecturas de la IA", highlight=hi, people=[
        {"name": "David Autor · Erik Brynjolfsson", "org": "Optimistas", "note": "Prosperidad compartida"},
        {"name": "Joseph Stiglitz · Daron Acemoglu", "org": "Escépticos", "note": "Más desigualdad, más concentración"}])


def close(grow, caption=""):
    return graphic(kicker="Las cuentas", contrast="+0,5", big="20-30 %", grow=grow, caption=caption,
                   small_label="puntos: deuda bajo control", big_label="de crecimiento al año")


TITLES = {1: "El Consenso de San Francisco", 2: "Tres ideas en las que casi todos están de acuerdo",
          3: "Los que no se lo creen", 4: "Cinco años que valen más que mil", 5: "Tres revoluciones",
          6: "Quedarse sin todo", 7: "La gran aceleración", 8: "Las grietas", 9: "Quién escribe este consenso"}
SUBTITLES = {1: "Economía de la IA transformadora · 1", 9: "Conclusión"}

P = {
 1: [
  (1, dict(type="title_card", lead_in=1.2)),
  (1, img("A heroic rocket launch at dawn, a tall white generic rocket rising on a column of fire and white smoke from a coastal launch pad, crowd silhouettes far away, epic and hopeful.")),
  (2, bars(1)),
  (2, bars(2)),
  (2, bosses(-1)),
  (2, bosses(0)),
  (2, bosses(1)),
  (2, bosses(2)),
  (3, img("The AI character at a wooden desk in a quiet library, reading a thick open economics report with simple line charts, warm lamp light.", character=True)),
  (2, photo_card("A generic hardcover book with a plain cream cover lying on a desk, its pages fanning as if turning, soft window light, a cup of coffee nearby.",
                 "El libro", "The Digitalist Papers · Vol. 2", "Inspirado en los Federalist Papers")),
  (4, card("La definición", "IA transformadora (TAI)",
           "Una transformación económica comparable a la Revolución Industrial, pero mucho más rápida.")),
  (4, card("La regla del libro", "La TAI llega pronto", "No se discute si llega ni cuándo: qué pasa cuando llegue y qué hacemos")),
  (3, photo_card("Morning view over San Francisco from a hill, steep streets, bay windows and the bay with fog rolling in, calm and bright.",
                 "Ensayo 1 · Eric Schmidt", "El Consenso de San Francisco", "Ex-CEO de Google")),
  (4, img("The AI character seen from behind on a terrace by the sea at sunset, looking at the horizon." + HERO, character=True)),
 ],
 2: [
  (1, dict(type="title_card", lead_in=1.2)),
  (1, img("A bright modern San Francisco startup office with large whiteboards full of hand-drawn graphs and arrows, people seen from behind arguing in front of them.")),
  (2, ideas(-1)),
  (3, ideas(0)),
  (2, ideas(1)),
  (2, ideas(2, "La gráfica en forma de palo de hockey")),
  (1, card("Así lo llama Schmidt", "El Consenso de San Francisco")),
  (3, card("¿Qué es un consenso?", "Creencias que comparte una gran mayoría de expertos",
           "Tecnólogos · científicos · emprendedores")),
  (2, img("A 1950s post-war scene recreated in colour: a busy factory floor and a new concrete dam under construction, workers seen from afar, optimistic light.")),
  (1, img("A 1990s international financial summit recreated: a grand conference hall with a long table, delegates in suits seen from behind, small blank flags.")),
  (3, card("En palabras de Schmidt", "Un consenso aceptado no es un consenso verdadero",
           "«El hecho de que un consenso esté ampliamente aceptado no lo hace, por supuesto, verdadero»")),
  (3, card("Silicon Valley, años 2000", "Demasiado optimistas con internet",
           "Después: desinformación · uso como arma · crisis de salud mental")),
 ],
 3: [
  (1, dict(type="title_card", lead_in=1.2)),
  (2, card("Los escépticos", "¿Los LLM llevan a la TAI?", "Ni a la AGI, su primo más ambicioso")),
  (3, graphic(kicker="Investigadores de primera fila", title="Otros caminos", highlight=-1, people=[
      {"name": "Yann LeCun", "org": "Uno de los «padrinos de la IA»",
       "note": "Los LLM son, en el fondo, incapaces de inventar algo creativo"},
      {"name": "Fei-Fei Li", "org": "Investigadora puntera", "note": "Prueba enfoques completamente nuevos"}])),
  (1, img("A sleek retro-futuristic flying car hovering over a sunny modern city boulevard, science-fiction concept art turned photoreal, playful and optimistic.")),
  (3, card("Peter Thiel, en palabras de Schmidt", "¿Coches voladores o 140 caracteres?",
           "Una receta de 140 caracteres al estilo de Emily Dickinson: el límite que tenía Twitter")),
  (4, world()),
 ],
 4: [
  (1, dict(type="title_card", lead_in=1.2)),
  (1, img("A large elegant hourglass on a desk in a modern office at dusk, sand running, city lights glowing beyond the window.")),
  (1, loop(1)),
  (1, loop(2)),
  (1, loop(3)),
  (1, loop(3, "Explosión de inteligencia")),
  (3, img("Aerial view of a long straight running track at dawn, one lone runner far ahead of a distant group, long shadows.")),
  (2, card("Para los creyentes del consenso", "Los próximos 5 años", "serán los más importantes de los próximos 1.000")),
  (1, img("The AI character standing on a green hill above San Francisco bay at dusk, seen from behind, the city lights below.", character=True)),
 ],
 5: [
  (1, dict(type="title_card", lead_in=1.2)),
  (1, revs(-1)),
  (2, revs(0)),
  (1, revs(1)),
  (2, img("A laptop screen with a grid of apartment listing photos scrolling at high speed, motion blur, modern desk, no readable text.")),
  (3, img("The AI character standing in front of a bright modern house for sale, holding a set of house keys, a tablet under its arm, sunny afternoon.", character=True)),
  (2, card("Agentes", "Funcionales, no creativos", "Moverán el conocimiento más rápido, sin crear conocimiento nuevo")),
  (2, revs(2, "«La más trascendental y, por extensión, la más especulativa»")),
  (3, card("La apuesta", "Más escala", "Modelos más grandes · más datos · más cálculo → razonamiento y AGI")),
 ],
 6: [
  (1, dict(type="title_card", lead_in=1.2)),
  (2, img("Cooling towers of a nuclear power plant at dawn releasing white steam into a pastel sky, green fields in front, calm and clean.")),
  (1, img("A huge data center campus at night, long lit buildings and power lines under a deep blue sky.")),
  (1, plants(31)),
  (1, plants(92)),
  (2, card("Límite 2", "Los datos", "Los grandes modelos ya se han tragado casi todo el internet público")),
  (1, img("A small child kneeling in a sunny garden, examining a leaf with a magnifying glass, curious, seen from the side.")),
  (3, card("Límite 3", "Los algoritmos", "¿Basta con pulir los LLM? Yann LeCun y Fei-Fei Li no lo tienen tan claro")),
 ],
 7: [
  (1, dict(type="title_card", lead_in=1.2)),
  (1, card("La tercera idea", "Un progreso humano sin precedentes", "En todos los ámbitos de la vida")),
  (3, img("A bright biology laboratory, a hand with a pipette over sample plates, large screens showing colourful 3D protein structures.")),
  (2, img("A remote mountain village at golden hour, a teenage girl seen from the side holding a smartphone and asking it a question, stone houses behind.")),
  (2, photo_card("A remote village street at golden hour, a smartphone glowing in a hand in the foreground.",
                 "Un polímata en el bolsillo", "Alguien que sabe de todo", "Para cualquiera, en cualquier pueblo")),
  (2, growth(-1)),
  (2, growth(0)),
  (2, growth(1)),
  (2, growth(2)),
  (1, card("Un matiz", "Muchas de estas mejoras no necesitan AGI")),
 ],
 8: [
  (1, dict(type="title_card", lead_in=1.2)),
  (1, card("Dos preguntas abiertas", "¿Cuándo? ¿Para quién?")),
  (1, jcurve(1)),
  (2, jcurve(2)),
  (1, camps(-1)),
  (1, camps(0)),
  (1, camps(1)),
  (1, camps(0)),
  (1, camps(1)),
 ],
 9: [
  (1, dict(type="title_card", lead_in=1.2)),
  (1, img("An empty grand wood-panelled hall of an old financial institution, long table with leather chairs, chandeliers, solemn but warm.")),
  (1, img("A bright modern tech office with engineers seen from behind at standing desks, large monitors with abstract code and diagrams, plants.")),
  (1, card("Schmidt", "Merece una consideración seria", "Y una crítica rigurosa")),
  (1, card("Sus últimas palabras", "Silicon Valley no puede responder sola",
           "A las profundas preguntas económicas, sociales y, francamente, existenciales que traerá esta transformación")),
  (2, close(0.0)),
  (1, close(1.0)),
  (1, close(1.0, "¿Y si tienen razón? Casi nadie ha hecho las cuentas")),
  (2, img("A wide empty seashore at sunset." + HERO, tail=2.0)),
 ],
}


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    modules = {m.number: m for m in parse_script(SCRIPT.read_text(encoding="utf-8"))}
    for n, plan in P.items():
        sentences = [s for p in modules[n].narration.split("\n\n") for s in split_sentences(p)]
        if sum(k for k, _ in plan) != len(sentences):
            raise SystemExit(f"module {n}: plan covers {sum(k for k, _ in plan)} of {len(sentences)} sentences")
        shots, i = [], 0
        for j, (k, fields) in enumerate(plan, 1):
            shot = {"id": f"c{n}-{j:02d}", **fields}
            if shot["type"] == "title_card":
                shot["title"] = TITLES[n]
                shot["subtitle"] = SUBTITLES.get(n, "Introducción" if n == 1 else f"Sección {n - 1}")
            shot["text"] = " ".join(sentences[i:i + k])
            i += k
            shots.append(shot)
        board = {"module": n, "voice": STYLE["voice"], "theme": "editorial", "style": STYLE["style"],
                 "character": STYLE["character"], "shots": shots}
        head = (f"# El Consenso de San Francisco, module {n}. Generated by "
                "scripts/make_consenso_boards.py; edit the plan there.\n# Shots are whole sentences. "
                f"Images are in assets/images/consenso-sf/module{n}/.\n")
        (OUT / f"module{n}.yaml").write_text(head + yaml.dump(board, Dumper=NoAliases, allow_unicode=True,
                                                               sort_keys=False, width=110), encoding="utf-8")
        print(f"module {n}: {len(shots)} shots, {sum('prompt' in s for s in shots)} with images")


if __name__ == "__main__":
    main()

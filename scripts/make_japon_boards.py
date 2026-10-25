"""Write storyboards/japon-chips/module1-7.yaml from a compact shot plan.

Shot texts are whole sentences taken from the parsed script, in order, so coverage is
exact by construction. Each plan row: (number of sentences, shot fields).
Run: .venv/bin/python -m scripts.make_japon_boards  (from the repo root)
"""
from pathlib import Path

import yaml

from studio.parse import parse_script, split_sentences

SCRIPT = Path("examples/japon-chips.md")
OUT = Path("storyboards/japon-chips")
STYLE = yaml.safe_load(Path("storyboards/module1.yaml").read_text(encoding="utf-8"))
NO_TEXT = " Plain unbranded objects with no logos and no readable text."
LEFT = " Calm, uncluttered left third of the frame."


class NoAliases(yaml.SafeDumper):
    def ignore_aliases(self, data):
        return True


def img(prompt, **kw):
    return dict(type="image", prompt=prompt + NO_TEXT, **kw)


def photo_card(prompt, kicker, title, body="", **kw):
    return dict(type="text_overlay", prompt=prompt + LEFT + NO_TEXT,
                overlay={"kicker": kicker, "title": title, "body": body}, **kw)


def card(kicker, title, body=""):
    return dict(type="text_overlay", overlay={"kicker": kicker, "title": title, "body": body})


def graphic(**overlay):
    return dict(type="text_overlay", overlay=overlay)


LINKS = [{"label": "Obleas de silicio", "value": "53 %", "companies": "Shin-Etsu · Sumco"},
         {"label": "Fotorresina", "value": "50 %", "companies": "Shin-Etsu · JSR · Tokyo Ohka Kogyo"},
         {"label": "Fotorresina para EUV", "value": ">90 %", "companies": "Empresas japonesas"},
         {"label": "Coater / developer", "value": "88 %", "companies": "Tokyo Electron · Screen"},
         {"label": "Sustrato del encapsulado", "value": "Clave", "companies": "Ibiden · película ABF de Ajinomoto"}]


def chain(active):
    return graphic(kicker="Cuota de mercado de las empresas japonesas", title="Los eslabones de un chip",
                   links=LINKS, active=active)


STEPS = [{"date": "2022", "label": "Nace Rapidus"}, {"date": "Jul 2024", "label": "Rehace la estrategia"},
         {"date": "Dic 2024", "label": "Llega la máquina EUV"}, {"date": "1 abr 2025", "label": "Arranca la línea piloto"},
         {"date": "18 jul 2025", "label": "Soul Lot: la primera oblea"}, {"date": "AF 2027", "label": "Producción en masa"}]


def steps(hi, caption=""):
    return graphic(kicker="Rapidus", title="De 2022 a la producción en masa", steps=STEPS, highlight=hi, caption=caption)


KUMAMOTO = {"label": "Kumamoto", "value": 37, "text": "37 meses", "note": "Chips de 12 a 28 nm"}
ARIZONA = {"label": "Arizona", "value": 54, "text": "53-55 meses", "note": "Chips de 4 nm"}


def build_time(bars, hi, caption=""):
    return graphic(kicker="Del anuncio a la producción", title="Japón construye rápido", bars=bars, max=60,
                   highlight=hi, caption=caption)


TITLES = {1: "Una empresa de condimentos dentro de un chip de IA", 2: "El mito", 3: "Los eslabones invisibles",
          4: "¿Por qué en Japón?", 5: "Por qué siguen siendo críticos en la era de la IA",
          6: "Y ahora Japón quiere volver arriba", 7: "Cierre"}
SUBTITLES = {1: "Bloque 1 · Gancho", 7: "Japón y los eslabones invisibles de los chips"}

P = {
 1: [
  (1, dict(type="title_card", lead_in=1.2)),
  (1, photo_card("A translucent amber sheet of thin resin film being peeled from a roll on a clean laboratory bench, macro.",
                 "Ajinomoto", "Ajinomoto Build-up Film (ABF)", "Una película de resina aislante")),
  (1, img("Macro of a modern AI chip package: a large central processor die with stacks of memory around it, mounted on a dark green substrate, gold contacts, on a lab bench.")),
  (1, graphic(kicker="Ajinomoto en bolsa", title="Por la película ABF", figures=[{"value": "×3", "label": "su valor en bolsa se ha más que triplicado"}], highlight=0)),
  (1, img("A small plain glass seasoning shaker with white crystals on a light wooden counter in a calm modern Japanese kitchen, steam from a bowl of soup in the soft background.")),
  (2, img("Macro of a modern AI chip package: a large central processor die with stacks of memory around it, mounted on a dark green substrate, gold contacts, on a lab bench.", motion="zoom_out")),
  (1, img("The AI character standing at a tall window, looking out over a sunny valley of glass tech office buildings on one side and a large semiconductor factory by the sea on the other.", character=True)),
  (1, img("Rows of sealed wooden crates and wrapped precision machine parts in a clean, quiet industrial warehouse, soft daylight from high windows.")),
  (1, img("The AI character at a drafting table studying a large technical blueprint of a chain of connected links, desk lamp, calm studio.", character=True)),
  (2, card("La tesis", "Taiwán fabrica los chips del mundo", "Muchas de las máquinas y los materiales con los que lo hace vienen de Japón")),
 ],
 2: [
  (2, dict(type="title_card", lead_in=1.2)),
  (2, img("Black and white 1980s archive-style photo of a large Tokyo electronics factory floor, workers in caps at long assembly lines of circuit boards, slight film grain, no signage.")),
  (2, img("A formal signing table in a 1980s government office, two sets of documents and fountain pens, two small blank desk flags, people seen only from behind, vintage film look.")),
  (2, graphic(kicker="1987 · aranceles", title="No a los chips, a la electrónica japonesa", figures=[{"value": "100 %", "label": "arancel sobre unos 300 millones de dólares"}], highlight=0)),
  (1, img("Stacks of 1980s televisions, beige personal computers and power tools in cardboard boxes on pallets in a port warehouse, vintage film look.")),
  (2, graphic(kicker="Cuota mundial de semiconductores", title="Japón: de la mitad a una décima parte",
              points=[{"x": 1988, "year_label": "Finales de los 80", "value": 50, "text": "≈50 %"},
                      {"x": 2024, "year_label": "Hoy", "value": 10, "text": "≈10 %"}],
              caption="En 2024, lo más avanzado que se fabricaba en Japón: chips de 40 nm")),
  (2, img("A lone rocky volcanic island in a calm grey-blue sea under a soft overcast sky, seen from a distance.")),
  (4, img("The AI character walking calmly along a long, bright aisle of a supply warehouse lined with sealed containers of materials and machine parts.", character=True)),
 ],
 3: [
  (1, dict(type="title_card", lead_in=1.2)),
  (3, img("A polished ultrapure silicon wafer reflecting soft light, held by a gloved hand in a cleanroom, macro, mirror-like surface.")),
  (2, chain(1)),
  (2, img("Amber photoresist liquid being dispensed onto a spinning silicon wafer inside a cleanroom machine, macro, soft yellow safe light.")),
  (1, chain(2)),
  (1, chain(3)),
  (2, img("A large white cleanroom track machine with a robotic arm moving a wafer between coating and developing modules, engineers in white suits in the background.")),
  (1, chain(4)),
  (3, photo_card("Extreme macro cross-section of a chip package substrate, many thin layers of dark insulating film and copper wiring stacked like a cake.",
                 "Ajinomoto", "Película ABF", "Aislante en capas dentro del sustrato del encapsulado")),
  (2, img("Tweezers holding a small chip package substrate like a miniature motherboard with a processor and memory mounted side by side, macro on a lab bench.")),
  (1, chain(5)),
  (1, card("METI · ministerio de Industria japonés", "«Sin Ibiden, habría sido imposible atraer a TSMC a Japón»")),
 ],
 4: [
  (3, dict(type="title_card", lead_in=1.2)),
  (2, img("A 1980s corporate showroom of one Japanese conglomerate displaying a vacuum cleaner, a scale model of a power plant and trays of memory chips side by side, vintage film look.")),
  (1, graphic(kicker="El mercado cambió", **{"from": "Memoria", "to": "Lógica"}, body="De un juego de fabricación a un juego de diseño y software")),
  (2, img("A design office with drafting tables separated by a glass wall from a busy semiconductor factory floor, late 1980s, vintage film look.")),
  (2, img("A hardback book with a plain dark blue cover lying on a wooden desk next to a small silicon microchip and reading glasses.")),
  (2, card("Chris Miller · dos errores", "Cuota de mercado en vez de rentabilidad", "Y poca atención al software")),
  (3, img("A modern memory chip factory complex at dusk with lit windows and wide roads, generic, seen from a hill.")),
  (2, img("Precision machined metal parts and components of semiconductor equipment laid out neatly on a grey workbench.")),
  (2, photo_card("Close-up of an older craftsman's hands adjusting a precision metal part with a fine gauge in a quiet workshop.",
                 "Monozukuri", "Conocimiento tácito", "Lo que en Japón llaman monozukuri: el oficio de fabricar")),
  (4, card("Morris Chang · fundador de TSMC", "«El aprendizaje es local»", "La curva de experiencia solo funciona en un mismo sitio")),
  (2, img("Engineers in white cleanroom suits tuning a large semiconductor machine together, laptops with data next to it, soft cool light.")),
  (2, graphic(kicker="Tokyo Electron en Albany, Nueva York", title="Su centro de I+D principal", figures=[{"value": "2003", "label": "allí desde"}, {"value": "80", "label": "máquinas propias"}], highlight=1)),
  (2, img("A team of engineers in white cleanroom suits standing in a circle for a morning safety briefing, seen from behind, bright cleanroom.")),
  (2, img("The AI character holding a small precision gauge and studying it closely in a quiet workshop full of fine tools.", character=True, tail=0.8)),
 ],
 5: [
  (1, dict(type="title_card", lead_in=1.2)),
  (3, img("Exploded isometric view of an advanced chip package floating in layers: processor die, stacks of high-bandwidth memory, interposer and substrate, studio lighting.")),
  (3, card("El encapsulado de TSMC", "Proveedores japoneses", "Ajinomoto e Ibiden, entre otros, además de Sony")),
  (1, photo_card("A large new semiconductor factory in a green rural valley with mountains, rice fields in the foreground, soft morning light.",
                 "Kumamoto", "44 empresas", "siguieron a TSMC con inversiones propias")),
  (1, graphic(kicker="Kyushu · plantas nuevas 2021-2023", title="La isla del silicio", places=[
      {"name": "Kumamoto", "lon": 130.74, "lat": 32.80, "note": "TSMC. Y plantas nuevas de Sumco, Ebara, Tokyo Electron y Tokyo Ohka Kogyo en Kyushu"}],
      regions=[{"name": "Kyushu", "lon": 128.9, "lat": 31.25}])),
  (1, graphic(kicker="Shin-Etsu · Gunma", title="Una planta nueva", figures=[{"value": "56 años", "label": "desde su anterior planta nueva"}], highlight=0)),
  (4, build_time([KUMAMOTO], 0)),
  (3, build_time([KUMAMOTO, ARIZONA], 1)),
  (3, build_time([KUMAMOTO, ARIZONA], -1, caption="Ojo: no es una comparación limpia (12-28 nm frente a 4 nm)")),
  (2, graphic(kicker="Dinero público · 2022-2025", title="Japón pone en chips", figures=[{"value": "3,9 billones ¥", "label": "entre 2022 y 2025"}], highlight=0)),
  (3, graphic(kicker="Gasto público en chips", title="En porcentaje del PIB", bars=[
      {"label": "Japón", "value": 0.71, "text": "0,71 %"}, {"label": "Alemania", "value": 0.41, "text": "0,41 %"},
      {"label": "Estados Unidos", "value": 0.21, "text": "0,21 %"}], max=0.8, highlight=0)),
 ],
 6: [
  (3, dict(type="title_card", lead_in=1.2)),
  (1, steps(0)),
  (2, graphic(kicker="El objetivo de Rapidus", **{"from": "40 nm", "to": "2 nm"}, body="Saltarse dos décadas de golpe")),
  (2, img("Cinematic 3D render of three transistor structures side by side on a dark surface: a flat planar one, a fin-shaped one, and one with stacked horizontal nanosheets wrapped by a gate, glowing copper accents.")),
  (2, card("IBM", "Pone conocimiento y diseños", "Dinero, no")),
  (2, graphic(kicker="Rapidus en Albany", title="Aprender con IBM", figures=[{"value": "150", "label": "ingenieros"}, {"value": "500", "label": "personas, con las familias"}], highlight=0)),
  (1, photo_card("A group of engineers in white cleanroom suits walking together down a bright cleanroom corridor, seen from behind.",
                 "Rapidus en Albany", "Proyecto «Titans»", "por una película")),
  (2, steps(1)),
  (1, img("A huge crated lithography machine module being unloaded from a truck at a factory loading dock at dusk, snow on the ground, work lights.")),
  (1, graphic(kicker="Tras la llegada de la máquina EUV", title="Instalación en Chitose", figures=[{"value": "200+", "label": "equipos instalados"}, {"value": "2,5", "label": "meses"}], highlight=0)),
  (3, steps(3)),
  (2, photo_card("A single silicon wafer glowing with iridescent patterns, held by a robotic end effector inside a cleanroom tool, macro.",
                 "18 de julio de 2025", "Soul Lot", "La primera oblea de la planta, con transistores de 2 nm")),
  (4, img("A giant oil supertanker and a small fast speedboat side by side on a calm grey sea, seen from above.")),
  (3, graphic(kicker="Días para procesar una oblea", title="Velocidad frente a volumen", bars=[
      {"label": "Lotes convencionales", "value": 120, "text": "120 días"}, {"label": "Rapidus", "value": 50, "text": "50 días"},
      {"label": "Pedidos urgentes", "value": 15, "text": "15 días", "note": "hot lots"}], max=130, highlight=1)),
  (4, graphic(kicker="¿Cómo?", title="Lote de 25 obleas frente a oblea a oblea", lot=True)),
  (3, img("Engineer's bench with several unbranded AI accelerator boards with large heatsinks and test cables, laptop with charts, soft light.")),
  (3, graphic(kicker="Rapidus · los números", title="Para la producción en masa plena", figures=[{"value": "5 billones ¥", "label": "harán falta, unos 34.000 millones de dólares"}], highlight=0)),
  (2, graphic(kicker="Rapidus · el dinero", title="Lo que hace falta y lo que hay", bars=[
      {"label": "Necesario", "value": 5.0, "text": "5 billones ¥"}, {"label": "Estado", "value": 1.7, "text": ">1,7 billones ¥", "note": "comprometido"},
      {"label": "Empresas privadas", "value": 0.0073, "text": "7.300 M¥", "note": "datos de 2024"}], max=5.6, highlight=1)),
  (1, graphic(kicker="Estimación de analistas", title="Producción en 2026", figures=[{"value": "25.000", "label": "obleas al mes"}], highlight=0)),
  (2, card("Para que haya clientes", "Pago por adelantado a proveedores de propiedad intelectual",
           "Arm · Synopsys · Cadence. GlobalFoundries hizo algo parecido y acabó abandonando la vanguardia.")),
  (3, steps(5, caption="Para entonces, TSMC e Intel ya tendrán un nodo nuevo")),
  (2, graphic(kicker="Hokkaido", title="La planta de Rapidus", places=[
      {"name": "Chitose", "lon": 141.65, "lat": 42.82, "note": "Cerca abrirán bases imec, ASML, Lam Research y Applied Materials"}],
      regions=[{"name": "Hokkaido", "lon": 143.0, "lat": 44.6}])),
 ],
 7: [
  (2, dict(type="title_card", lead_in=1.2)),
  (2, img("The AI character seen from behind on a snowy hill at blue-hour dusk, looking at a large semiconductor factory with its lights on in a wide valley, calm.", character=True, tail=2.0)),
 ],
}


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    modules = {m.number: m for m in parse_script(SCRIPT.read_text(encoding="utf-8"))}
    for n, plan in P.items():
        sentences = split_sentences(modules[n].narration)
        if sum(k for k, _ in plan) != len(sentences):
            raise SystemExit(f"module {n}: plan covers {sum(k for k, _ in plan)} of {len(sentences)} sentences")
        shots, i = [], 0
        for j, (k, fields) in enumerate(plan, 1):
            shot = {"id": f"j{n}-{j:02d}", **fields}
            if shot["type"] == "title_card":
                shot["title"] = TITLES[n]
                shot["subtitle"] = SUBTITLES.get(n, f"Bloque {n}")
            shot["text"] = " ".join(sentences[i:i + k])
            i += k
            shots.append(shot)
        board = {"module": n, "voice": STYLE["voice"], "theme": "blueprint", "style": STYLE["style"],
                 "character": STYLE["character"], "shots": shots}
        head = (f"# Japón y los eslabones invisibles de los chips, block {n}. Generated by "
                "scripts/make_japon_boards.py; edit the plan there.\n# Shots are whole sentences. "
                "Images are in assets/images/japon-chips/module{n}/.\n")
        (OUT / f"module{n}.yaml").write_text(head + yaml.dump(board, Dumper=NoAliases, allow_unicode=True,
                                                               sort_keys=False, width=110), encoding="utf-8")
        print(f"module {n}: {len(shots)} shots, {sum(s['type'] == 'image' or 'prompt' in s for s in shots)} with images")


if __name__ == "__main__":
    main()

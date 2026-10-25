"""Write storyboards/potencias-medias/module1-7.yaml from a compact shot plan.

Like make_japon_boards, but sentences are split one paragraph at a time, the way
'narrate' splits them, so a shot never joins the end of one paragraph to the next
("tres canales informales:" / "1. El uso...") and build reuses the narrated takes.
Run: .venv/bin/python -m scripts.make_potencias_boards  (from the repo root)
"""
from pathlib import Path

import yaml

from scripts.make_japon_boards import NoAliases, card, graphic, img, photo_card
from studio.parse import parse_script, split_sentences

SCRIPT = Path("examples/potencias-medias.md")
OUT = Path("storyboards/potencias-medias")
STYLE = yaml.safe_load(Path("storyboards/module1.yaml").read_text(encoding="utf-8"))


def path(hi, caption=""):
    return graphic(kicker="Potencias medias", title="Un camino estrecho hacia la soberanía",
                   sides=["Inacción y dependencia", "Proyectos nacionales hipercostosos e inútiles"],
                   path="La tercera vía", highlight=hi, caption=caption)


def fronts(hi):
    return graphic(kicker="¿Por qué el primer nivel?", title="Tres frentes de competencia", highlight=hi, figures=[
        {"value": "1", "label": "Competencia económica"}, {"value": "2", "label": "Capacidad gubernamental"},
        {"value": "3", "label": "Seguridad y defensa nacional"}])


TRAP = [{"date": "1", "label": "Inversión inicial"}, {"date": "2", "label": "Resultados mediocres"},
        {"date": "3", "label": "Coste político de admitir el fracaso"}, {"date": "4", "label": "Proteccionismo y regulación"},
        {"date": "5", "label": "Retraso económico"}]


def trap(hi, caption=""):
    return graphic(kicker="Campeones nacionales", title="La trampa política", steps=TRAP, highlight=hi, caption=caption)


def channels(hi, caption=""):
    return graphic(kicker="Cómo se importa hoy", title="Tres canales informales", highlight=hi, caption=caption, figures=[
        {"value": "1", "label": "Modelos de código abierto extranjeros"},
        {"value": "2", "label": "API comerciales B2B"}, {"value": "3", "label": "Suscripciones individuales"}])


def levels(hi):
    return graphic(kicker="Riesgo geopolítico", title="Los tres niveles de riesgo", highlight=hi, figures=[
        {"value": "Nivel 1", "label": "Abuso comercial y sobreprecios: proveedores predatorios"},
        {"value": "Nivel 2", "label": "Estrangulamiento del suministro: la OPEP de la IA"},
        {"value": "Nivel 3", "label": "Corte total del suministro: el escenario extremo"}])


TITLES = {1: "El manifiesto de las potencias medias", 2: "¿Por qué necesitan la IA de frontera?",
          3: "La cruda realidad: no pueden construirla", 4: "El peligro de los campeones nacionales",
          5: "La importación como materia de Estado", 6: "Los tres niveles de riesgo", 7: "Conclusión"}
SUBTITLES = {1: "Cómo importar la IA de frontera", 7: "Hoja de ruta estratégica"}

P = {
 1: [
  (1, dict(type="title_card", lead_in=1.2)),
  (3, img("A modern government ministry meeting room in Paris with tall classical windows, officials seen from behind around a long table, a wall screen showing a stuck video call with a loading spinner, one person lifting an old desk telephone handset.")),
  (2, card("La fuente", "Anton Leicht", "Lo que pasa cuando un país protege a sus campeones nacionales a toda costa")),
  (1, img("The AI character sitting alone at the end of a long ministry conference table, a vintage desk telephone in front of it and a laptop showing an endless loading circle, soft window light.", character=True)),
  (3, card("Francia", "Mistral, su campeón en IA", "Un buen laboratorio que va por detrás de Estados Unidos y China")),
  (4, card("La pregunta incómoda", "¿Fabricar su propia IA de frontera?", "No: aprender a importarla bien")),
  (1, path(-1)),
  (2, path(0, "Mendigar acceso a última hora, en condiciones coercitivas")),
  (2, path(1, "Construir modelos propios a cualquier coste")),
  (2, path(2, "Capacidad sub-frontera propia + importación diversificada por capas")),
 ],
 2: [
  (1, dict(type="title_card", lead_in=1.2)),
  (2, img("Wide view of a bright automated industrial plant with robotic arms, next to a modern data center hall with long rows of server racks, clean and calm.")),
  (3, img("A modern research laboratory with scientists in white coats seen from behind, examining material samples and molecular models on large screens, soft daylight.")),
  (3, card("La pregunta", "¿Basta con una IA «suficientemente buena»?", "No: la competencia estratégica opera en márgenes muy estrechos")),
  (2, fronts(-1)),
  (1, fronts(0)),
  (3, img("A calm modern financial trading room with large unbranded screens of abstract line charts, and through the window a huge logistics hub with cranes and containers.")),
  (1, fronts(1)),
  (2, img("A modern government office with civil servants seen from behind at desks, tall stacks of paper files next to a glass wall revealing a large room of data processing machines.")),
  (1, fronts(2)),
  (3, img("A calm cybersecurity operations center with analysts seen from behind facing a wall of unbranded screens showing abstract network maps, blue and copper light.")),
 ],
 3: [
  (1, dict(type="title_card", lead_in=1.2)),
  (2, card("Los insumos de la frontera", "Colosales",
           "Capital masivo · energía en gigavatios · chips de última generación · talento de élite · un bucle comercial que pague la siguiente generación")),
  (2, img("Aerial view of an enormous data center campus in a desert plain with a large electrical substation and high-voltage power lines, at golden hour.")),
  (2, card("Un objetivo en movimiento", "Apuntan a lo que Estados Unidos tenía el año pasado", "Y ese objetivo acelera")),
  (3, img("The AI character at a drafting table studying a large technical blueprint of a steep rising curve, desk lamp, calm studio.", character=True)),
 ],
 4: [
  (1, dict(type="title_card", lead_in=1.2)),
  (2, photo_card("A bright European AI research lab, engineers seen from behind at desks with large monitors of abstract model diagrams, a small rack of servers behind glass.",
                 "Sub-frontera", "Seguidores rápidos", "Mistral · Cohere: replican lo que funciona en la frontera, más barato")),
  (1, card("Un error peligroso", "Sub-frontera no es frontera")),
  (1, trap(0)),
  (1, trap(2)),
  (2, trap(2, "«Nuestra iniciativa nacional de IA está trabajando en ello»")),
  (1, img("A government office corridor with tall stacks of paper forms on desks and an old beige desktop computer showing a frozen progress bar, calm light.")),
  (1, trap(3)),
  (1, trap(4)),
  (2, card("La regla", "Apoyo limitado", "Que jamás entre en conflicto con la importación de modelos de frontera")),
 ],
 5: [
  (1, dict(type="title_card", lead_in=1.2)),
  (1, channels(-1)),
  (1, channels(0)),
  (1, channels(1)),
  (1, channels(2)),
  (1, img("A clean cloud data center aisle with glowing server racks, and a monitor in the foreground showing abstract blurred lines of program code.")),
  (2, channels(0, "Una generación por detrás de la frontera real")),
  (1, channels(1, "A merced de cambios de precios, privacidad y modelos")),
  (2, photo_card("A formal signing table in a modern government hall, two leather folders and fountain pens, small blank desk flags, people seen only from behind.",
                 "La importación como política de Estado", "Acuerdos marco intergubernamentales",
                 "Con los grandes desarrolladores e hiperescaladores")),
  (1, graphic(kicker="Lo que deben garantizar", title="Acuerdos marco de importación", highlight=0, figures=[
      {"value": "1", "label": "Suministro directo de IA de frontera para el gobierno y la seguridad nacional"},
      {"value": "2", "label": "Condiciones estables para que las empresas contraten con desarrolladores extranjeros"}])),
  (1, graphic(kicker="Lo que deben garantizar", title="Acuerdos marco de importación", highlight=1, figures=[
      {"value": "1", "label": "Suministro directo de IA de frontera para el gobierno y la seguridad nacional"},
      {"value": "2", "label": "Condiciones estables para que las empresas contraten con desarrolladores extranjeros"}])),
 ],
 6: [
  (1, dict(type="title_card", lead_in=1.2)),
  (2, levels(0)),
  (2, photo_card("Close-up of modular server blades being slid in and out of a rack by a hand, interchangeable units with copper handles.",
                 "Nivel 1 · Solución", "Opcionalidad y competencia", "Una capa de software nacional intercambiable para cambiar de proveedor sin rehacerlo todo")),
  (2, levels(1)),
  (2, photo_card("Night view of the globe from orbit with thin glowing lines connecting several data center sites across continents, calm and elegant.",
                 "Nivel 2 · Solución", "Diversificación geográfica", "Varios proveedores, centros locales y nodos en regiones aliadas: el Golfo, Noruega")),
  (2, levels(2)),
  (2, photo_card("A high-security data center entrance built into a hillside, heavy steel doors open onto a clean lit server hall, calm daylight.",
                 "Nivel 3 · Solución", "Centros de datos soberanos", "Más licencias especiales y campeones de sub-frontera como red de seguridad")),
 ],
 7: [
  (1, dict(type="title_card", lead_in=1.2)),
  (2, img("The AI character seated at a modern negotiation table, signing one of two leather folders with a fountain pen, bright calm conference room, the other side of the table empty.", character=True)),
  (1, card("Bazas para negociar", "Lo que tienen las potencias medias",
           "Eslabones clave de la cadena industrial · energía · talento · coaliciones de compradores")),
  (1, img("Slow aerial shot over large white cylindrical tanks of a strategic oil reserve, full and orderly, soft morning light.")),
  (1, img("An empty, clean server room with bare racks and a polished floor, a single ceiling light, quiet.")),
  (2, graphic(kicker="Petróleo frente a IA", title="No hay reserva estratégica de inteligencia", highlight=1, figures=[
      {"value": "Petróleo", "label": "Se guarda en depósitos para aguantar una crisis"},
      {"value": "IA", "label": "No se puede almacenar capacidad"}])),
  (1, card("La única reserva", "Un buen contrato", "Firmado antes de que haga falta")),
  (2, img("The AI character seen from behind at a tall window at blue-hour dusk, a signed contract folder on the desk beside it, city lights of Paris in the distance, calm.", character=True, tail=2.0)),
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
            shot = {"id": f"p{n}-{j:02d}", **fields}
            if shot["type"] == "title_card":
                shot["title"] = TITLES[n]
                shot["subtitle"] = SUBTITLES.get(n, "Introducción" if n == 1 else f"Sección {n - 1}")
            shot["text"] = " ".join(sentences[i:i + k])
            i += k
            shots.append(shot)
        board = {"module": n, "voice": STYLE["voice"], "theme": "blueprint", "style": STYLE["style"],
                 "character": STYLE["character"], "shots": shots}
        head = (f"# El manifiesto de las potencias medias, module {n}. Generated by "
                "scripts/make_potencias_boards.py; edit the plan there.\n# Shots are whole sentences. "
                f"Images are in assets/images/potencias-medias/module{n}/.\n")
        (OUT / f"module{n}.yaml").write_text(head + yaml.dump(board, Dumper=NoAliases, allow_unicode=True,
                                                               sort_keys=False, width=110), encoding="utf-8")
        print(f"module {n}: {len(shots)} shots, {sum(s['type'] == 'image' or 'prompt' in s for s in shots)} with images")


if __name__ == "__main__":
    main()

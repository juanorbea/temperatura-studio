"""Write storyboards/anthropic/module1-7.yaml from a compact shot plan (blueprint theme).

Same scheme as make_potencias_boards: sentences split one paragraph at a time.
Real people appear only as text cards, never as images. No logos.
Run: .venv/bin/python -m scripts.make_anthropic_boards  (from the repo root)
"""
from pathlib import Path

import yaml

from scripts.make_japon_boards import NoAliases, card, graphic, img, photo_card
from studio.parse import parse_script, split_sentences

SCRIPT = Path("examples/anthropic.md")
OUT = Path("storyboards/anthropic")
STYLE = yaml.safe_load(Path("storyboards/module1.yaml").read_text(encoding="utf-8"))


def bars_loss(hi=-1):
    return graphic(
        kicker="1.er semestre 2026", title="La pérdida que no es", highlight=hi,
        bars=[
            {"label": "Pérdida neta", "note": "contable", "value": 80700, "text": "80.700 M$"},
            {"label": "Pérdida operativa", "note": "negocio", "value": 693, "text": "693 M$"},
            {"label": "Flujo de caja operativo", "note": "positivo", "value": 3900, "text": "+3.900 M$"},
        ], max=80700)


def quote_mtm():
    return card(
        "S-1 · p.147",
        "«Because these instruments are marked to market, increases in our enterprise valuation drive increases in this expense.»",
        "Traducción: como se valoran a precio de mercado, cuanto más vale la empresa, más crece este gasto.")


def quote_forward():
    return card(
        "Carta de los fundadores · p.7",
        "«Anthropic will often make forward investments (especially in compute) that may seem irresponsibly large at first glance.»",
        "Traducción: Anthropic hará a menudo inversiones por adelantado, sobre todo en cómputo, que a primera vista pueden parecer irresponsablemente grandes.")


def revenue_bars(hi=-1):
    return graphic(
        kicker="Ingresos", title="De 41 M$ a 16.300 M$", highlight=hi,
        bars=[
            {"label": "2023", "value": 41, "text": "41 M$"},
            {"label": "2024", "value": 386, "text": "386 M$"},
            {"label": "2025", "value": 4600, "text": "4.600 M$"},
            {"label": "1.er sem. 2026", "value": 16300, "text": "16.300 M$"},
        ], max=16300)


def compute_ratio(hi=-1):
    return graphic(
        kicker="Gasto en cómputo / ingresos", title="De 1.056 % a 55 %", highlight=hi,
        points=[
            {"x": 2023, "year_label": "2023", "value": 100, "text": "1.056 %"},
            {"x": 2026, "year_label": "1.er sem. 2026", "value": 5, "text": "55 %"},
        ], ymax=100,
        caption="Ingresos por dólar de cómputo: 0,40 $ (1T 2025) → 2,08 $ (2T 2026)")


def spend_bars(hi=-1):
    return graphic(
        kicker="1.er semestre 2026", title="Servir frente a investigar", highlight=hi,
        bars=[
            {"label": "Servir a clientes", "value": 2400, "text": "2.400 M$"},
            {"label": "I+D de modelos", "value": 9700, "text": "9.700 M$"},
        ], max=9700,
        caption="Del cómputo total (~8.900 M$): ~27 % servir / ~73 % resto")


def commitments(hi=-1):
    return graphic(
        kicker="Compromisos de cómputo", title="Las cifras dejan de parecer reales", highlight=hi,
        figures=[
            {"value": "≥114.500 M$", "label": "Google (+125.000-150.000 M$ en TPU)"},
            {"value": "≥110.000 M$", "label": "Amazon"},
            {"value": "≤120.500 M$", "label": "SpaceXAI"},
            {"value": "≥44.900 M$", "label": "Microsoft"},
        ])


def commitments2(hi=-1):
    return graphic(
        kicker="Más compromisos", title="Nscale · Lambda · AMD", highlight=hi,
        figures=[
            {"value": "~44.600 M$", "label": "Nscale"},
            {"value": "~41.300 M$", "label": "Lambda"},
            {"value": ">20.000 M$", "label": "AMD"},
        ])


def revenue_mix(hi=-1):
    return graphic(
        kicker="De dónde salen los ingresos", title="Consumo frente a suscripciones", highlight=hi,
        figures=[
            {"value": "80 %", "label": "Consumo (tokens)"},
            {"value": "20 %", "label": "Suscripciones"},
        ],
        caption="~48 % vía marketplaces de la nube")


def clients_ladder(hi=-1):
    return graphic(
        kicker="A 30 de septiembre de 2026", title="Escalera de clientes", highlight=hi,
        figures=[
            {"value": ">11.900", "label": "más de 100.000 $/año"},
            {"value": ">1.900", "label": "más de 1 M$/año"},
            {"value": "~250", "label": "más de 10 M$/año"},
        ])


def fortune_spend(hi=-1):
    return graphic(
        kicker="Fortune 500", title="Cuánto pesan en sus gastos", highlight=hi,
        bars=[
            {"label": "Gasto total de la empresa", "value": 1000, "text": "100 %"},
            {"label": "Anthropic (media)", "value": 1, "text": "<0,1 %"},
            {"label": "Top 10 clientes", "value": 10, "text": "<1 %"},
        ], max=1000)


def openrouter_points():
    return graphic(
        kicker="OpenRouter · media 7 días", title="Tokens diarios de modelos Anthropic",
        points=[
            {"x": 6, "year_label": "Jun 2026", "value": 27, "text": "~600.000 M"},
            {"x": 10, "year_label": "Oct 2026", "value": 100, "text": "~2,2 billones"},
        ], ymax=100,
        caption="1 jun – 24 oct 2026 · sin etiquetas de modelo no verificadas")


def ornn_index(hi=-1):
    return graphic(
        kicker="Ornn · índice de precios de tokens", title="Mínimo histórico, oct. 2026", highlight=hi,
        figures=[
            {"value": "0,80", "label": "Anthropic (índice)"},
            {"value": "0,44", "label": "OpenAI (índice)"},
        ],
        caption="Valores del índice, sin base publicada")


def obligations(hi=-1):
    return graphic(
        kicker="Tras junio de 2026", title="Nuevos pagos mínimos", highlight=hi,
        figures=[
            {"value": "~245.000 M$", "label": "Pagos mínimos (sobre todo cómputo)"},
            {"value": "~3.100 M$/mes", "label": "SpaceXAI a plena capacidad"},
            {"value": "~161.200 M$", "label": "Broadcom · alquileres"},
        ])


def treadmill():
    return graphic(
        kicker="3.er trimestre 2026", title="La cinta de correr",
        figures=[{"value": ">80 %", "label": "ingresos de modelos de menos de seis meses"}],
        highlight=0)


def governance(hi=-1):
    return graphic(
        kicker="Gobierno societario", title="Quién decide", highlight=hi,
        figures=[
            {"value": "50,1 %", "label": "1 acción clase F (cofundadores) · del voto"},
            {"value": "4 de 7", "label": "Clase T · Long-Term Benefit Trust elige consejeros"},
            {"value": "1 voto", "label": "Clase A (inversores) · por acción"},
        ])


TITLES = {
    1: "La pérdida que no es",
    2: "Una apuesta a la curva",
    3: "En qué se va el dinero",
    4: "No es concentración",
    5: "Bajar el precio, subir los ingresos",
    6: "Lo que podría salir mal",
    7: "El minuto cinco",
}
SUBTITLES = {
    1: "Anthropic sale a bolsa",
    2: "Sección 1",
    3: "Sección 2",
    4: "Sección 3 · Las primeras entradas",
    5: "Sección 4",
    6: "Sección 5",
    7: "Conclusión",
}

# Reusable cinematic stills (generated once, copied to several shot ids).
S1_COVER = img(
    "Close-up of a generic legal prospectus cover page on cream paper, large centered heading "
    "reading only Form S-1 in plain black sans-serif type, no seals, no logos, no company name, "
    "soft desk lamp light, shallow depth of field.")
FOUNDERS_LETTER = img(
    "Open illustrated founders letter pages of a formal prospectus on a wooden desk, elegant "
    "typography with decorative margin drawings of abstract curves and chips, no logos, no readable "
    "brand marks, pages turning slowly feel, warm lamp light.")
DATACENTER = img(
    "Wide aisle inside a vast modern data center with rows of unmarked server racks glowing soft "
    "blue, polished floor reflections, calm cool light, no logos.")
CHIPS = img(
    "Macro of several unbranded accelerator chips and bare silicon dies on a clean antistatic mat, "
    "copper heat spreaders, no logos, no readable markings, soft lab light.")
STADIUM = img(
    "Almost empty baseball stadium in soft afternoon light, a few scattered spectators, a simple "
    "analog scoreboard showing the first inning with no team names and no logos, wide cinematic shot.")
CODE_AGENT = img(
    "Over-the-shoulder view of a desk with two large monitors showing abstract blurred code and a "
    "terminal cursor, a robotic arm silhouette reflected faintly, no logos, no readable brand text, "
    "cool desk lamp.")
MINUTE5 = img(
    "Close-up of a simple stadium scoreboard at night under floodlights reading only minute 5 in "
    "plain digits, no team names, no logos, cinematic.")
AI_CURVE = img(
    "The AI character at a drafting table studying a large technical blueprint of a steep rising "
    "exponential curve, desk lamp, calm studio.", character=True)
AI_AGENT = img(
    "The AI character seated at a modern desk facing dual monitors of abstract code, charcoal suit "
    "and koi shirt visible, calm focused posture, soft window light.", character=True)
AI_GAME = img(
    "The AI character standing alone on the edge of an almost empty baseball field at golden hour, "
    "faceless white mannequin head, looking toward a distant first-inning scoreboard, hopeful mood.",
    character=True)
AI_CLOSE = img(
    "Medium shot of the AI character in a bright modern office, holding an open prospectus, "
    "faceless white mannequin head, charcoal birdseye suit and burgundy paisley tie, calm and "
    "analytical mood.", character=True)


P = {
 1: [
  (1, dict(type="title_card", lead_in=1.2)),
  (2, S1_COVER),
  (1, S1_COVER),
  (1, bars_loss(0)),
  (1, bars_loss(1)),
  (1, bars_loss(2)),
  (2, card("Apuntes contables", "No mueven dinero", "Notas convertibles, derivados y SAFE")),
  (1, card("SAFE", "Acuerdos de inversión", "Se convierten en acciones más adelante")),
  (1, card("Más revalorización", "8.700 M$", "Acuerdos de compra de notas")),
  (1, card("Total contable", "~81.000 M$", "Que no han salido de ninguna cuenta bancaria")),
  (2, quote_mtm()),
  (1, graphic(kicker="En X", title="Nicolas Bustamante",
              people=[{"name": "Nicolas Bustamante", "org": "X",
                       "note": "La operación perdió solo unos 700 M$"}], highlight=0)),
  (3, AI_CLOSE),
 ],
 2: [
  (1, dict(type="title_card", lead_in=1.2)),
  (1, FOUNDERS_LETTER),
  (1, quote_forward()),
  (1, quote_forward()),
  (1, AI_CURVE),
  (2, AI_CURVE),
  (1, card("Leyes de escalado", "Más datos + más cómputo", "Modelos mejores")),
  (2, card("Como una farmacéutica", "Inviertes muchísimo antes", "Aquí pasa mucho más rápido y a mucha más escala")),
  (1, card("Su fórmula", "«Audaces pero sensatos»")),
  (3, card("Dos lecturas", "Si te crees la curva → inversión", "Si no → un agujero")),
  (2, AI_CLOSE),
  (5, revenue_bars(-1)),
  (1, graphic(kicker="2T 2026", title="Crecimiento interanual",
              figures=[{"value": "1.368 %", "label": "11.600 M$ de ingresos"}], highlight=0)),
  (1, card("El dato de la apuesta", "Cómputo / ingresos")),
  (2, compute_ratio(0)),
  (2, compute_ratio(1)),
  (2, card("Factura primero", "Clientes después", "Contratos de 12 a 18 meses")),
  (2, graphic(kicker="2T 2026", title="Primer trimestre en positivo",
              figures=[{"value": "974 M$", "label": "beneficio operativo"}], highlight=0)),
 ],
 3: [
  (1, dict(type="title_card", lead_in=1.2)),
  (2, DATACENTER),
  (1, card("Sin margen bruto publicado", "Gastos por tipo, no por función")),
  (4, graphic(kicker="Margen bruto implícito", title="Una cuenta mía", highlight=-1, figures=[
      {"value": "85 %", "label": "1.er semestre 2026"},
      {"value": "12 %", "label": "1.er semestre 2025"},
  ], caption="Servir a clientes 2.400 M$ · ingresos 16.300 M$")),
  (1, card("El gasto grande", "Investigación y desarrollo")),
  (2, spend_bars(1)),
  (2, spend_bars(-1)),
  (1, card("¿Por qué tanto entrenamiento?", "Los clientes compran el modelo más nuevo")),
  (1, graphic(kicker="3.er trimestre", title="Modelos recientes",
              figures=[{"value": ">80 %", "label": "ingresos de modelos de menos de seis meses"}], highlight=0)),
  (3, card("Casi nada se compra", "482 M$ en equipos propios", "El resto se alquila")),
  (1, CHIPS),
  (1, card("Las cifras dejan de parecer reales", "Compromisos plurianuales")),
  (3, commitments(0)),
  (3, commitments(2)),
  (1, revenue_mix(-1)),
  (2, revenue_mix(0)),
  (1, revenue_mix(1)),
  (1, card("Los mismos", "Alquilan los chips y venden el producto")),
  (2, graphic(kicker="Productividad", title="5.300 empleados",
              figures=[{"value": "6,6 M$", "label": "ingresos por cabeza · 12 meses"}], highlight=0)),
  (1, graphic(kicker="Financiación", title="Caja y capital levantado", figures=[
      {"value": "141.100 M$", "label": "levantados"},
      {"value": "112.400 M$", "label": "en caja · fin de junio"},
  ])),
 ],
 4: [
  (1, dict(type="title_card", lead_in=1.2)),
  (3, STADIUM),
  (3, card("Riesgo del S-1", "Top 5 ≈ 25 % de ingresos", "Muchos sin contratos largos")),
  (4, AI_GAME),
  (1, card("Te explico por qué", "Tres argumentos")),
  (1, clients_ladder(-1)),
  (3, clients_ladder(0)),
  (1, card("A finales de 2023", "~20 clientes >100.000 $")),
  (1, card("Segundo", "La dependencia baja")),
  (4, graphic(kicker="Concentración", title="Ningún cliente >10 %", highlight=-1, figures=[
      {"value": "64 %", "label": "fuera del top 5 · 1T 2026"},
      {"value": "79 %", "label": "fuera del top 5 · 3T 2026"},
  ])),
  (2, graphic(kicker="Retención neta", title="~900 %",
              figures=[{"value": "×9", "label": "gasto de clientes que ya estaban (sin Pro y Max)"}],
              highlight=0)),
  (1, card("El dato que más me convence", "Fortune 500")),
  (3, fortune_spend(1)),
  (3, card("La pregunta", "No cuánto depende de ellas", "Sino cuánto les queda por gastar")),
  (1, card("Un ejemplo concreto", "Claude Enterprise frente a Claude Code")),
  (2, graphic(kicker="3T 2026 · Claude Enterprise", title="Hueco de uso", figures=[
      {"value": "<75 $/mes", "label": "sin Claude Code"},
      {"value": "×20", "label": "top 5 % con Claude Code"},
  ])),
  (1, card("Cowork", "Si el oficinista gasta 1/4", "Ingreso por puesto ×5")),
  (2, card("Expansión dentro del cliente", "Plataforma + apps propias", ">50 % frente a 30 % a finales de 2025")),
 ],
 5: [
  (1, dict(type="title_card", lead_in=1.2)),
  (1, AI_AGENT),
  (2, CODE_AGENT),
  (1, card("«Preservando nuestros márgenes»", "Opus 5.5 · −40 % coste por tarea")),
  (1, card("Ya lo había probado", "Opus 4.5 · nov. 2025")),
  (2, graphic(kicker="Tras Opus 4.5", title="Crecimiento trimestral", figures=[
      {"value": "48 % → 132 %", "label": "ingresos trimestrales"},
  ], highlight=0)),
  (1, card("Apuesta en X", "El −40 % de Opus 5.5", "Acelera de nuevo el 4T")),
  (1, card("OpenRouter", "Tokens diarios de Anthropic")),
  (3, openrouter_points()),
  (1, card("Ornn", "Índice de precios de tokens")),
  (2, ornn_index(-1)),
  (1, card("En X", "Alquiler de GPU ↑ · precio de tokens ↓")),
  (2, AI_AGENT),
 ],
 6: [
  (1, dict(type="title_card", lead_in=1.2)),
  (2, AI_CLOSE),
  (2, card("Uno", "Las obligaciones")),
  (3, obligations(-1)),
  (1, card("Si la demanda se frena", "La factura no se frena")),
  (2, card("Dos", "El entrenamiento")),
  (2, spend_bars(-1)),
  (1, card("En X", "Beneficios finos hasta 2027")),
  (2, card("Tres", "El beneficio es nuevo y pequeño")),
  (3, graphic(kicker="Un solo trimestre en positivo", title="Márgenes", figures=[
      {"value": "8 %", "label": "margen operativo"},
      {"value": "19 %", "label": "ajustado (sin remuneración en acciones)"},
      {"value": "2.200 M$", "label": "remuneración en acciones · semestre"},
  ])),
  (1, card("Y el 85 %", "Es una cuenta mía")),
  (2, card("Cuatro", "La cinta de correr")),
  (2, treadmill()),
  (2, card("Cinco", "Clientes que no cumplen las normas")),
  (1, graphic(kicker="9 primeros meses de 2026", title="Ingresos de clientes incumplidores",
              figures=[{"value": "5–7 %", "label": "según Anthropic"}], highlight=0)),
  (1, card("Vigilancia reforzada", "Agosto y septiembre")),
  (1, card("En X", "¿Explica el frenazo del 3T?")),
  (2, card("Seis", "La política")),
  (2, card("Junio 2026", "Fable 5 y Mythos 5 restringidos", "Desactivados hasta levantar la restricción")),
  (2, card("Siete", "El control")),
  (2, governance(0)),
  (2, governance(1)),
  (2, card("Quien compra pone el dinero", "Las decisiones las toman otros")),
  (2, AI_CURVE),
  (2, compute_ratio(-1)),
  (2, AI_CURVE),
 ],
 7: [
  (1, dict(type="title_card", lead_in=1.2)),
  (1, S1_COVER),
  (1, fortune_spend(2)),
  (1, obligations(0)),
  (2, card("Prueba de Navidad", "El año pasado el gasto cayó un 20 %", "Si este año cae menos, quizá los agentes ya no esperan")),
  (1, MINUTE5),
 ],
}


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    modules = {m.number: m for m in parse_script(SCRIPT.read_text(encoding="utf-8"))}
    for n, plan in P.items():
        sentences = [s for p in modules[n].narration.split("\n\n") for s in split_sentences(p)]
        covered = sum(k for k, _ in plan)
        if covered != len(sentences):
            raise SystemExit(f"module {n}: plan covers {covered} of {len(sentences)} sentences")
        shots, i = [], 0
        for j, (k, fields) in enumerate(plan, 1):
            shot = {"id": f"a{n}-{j:02d}", **fields}
            if shot["type"] == "title_card":
                shot["title"] = TITLES[n]
                shot["subtitle"] = SUBTITLES[n]
            shot["text"] = " ".join(sentences[i:i + k])
            i += k
            shots.append(shot)
        board = {"module": n, "voice": STYLE["voice"], "theme": "blueprint", "style": STYLE["style"],
                 "character": STYLE["character"], "shots": shots}
        head = (f"# Anthropic IPO, module {n}. Generated by scripts/make_anthropic_boards.py; "
                "edit the plan there.\n# Shots are whole sentences. "
                f"Images are in assets/images/anthropic/module{n}/.\n")
        (OUT / f"module{n}.yaml").write_text(
            head + yaml.dump(board, Dumper=NoAliases, allow_unicode=True, sort_keys=False, width=110),
            encoding="utf-8")
        n_img = sum(1 for s in shots if s["type"] == "image" or "prompt" in s)
        print(f"module {n}: {len(shots)} shots, {n_img} with images, {len(sentences)} sentences")


if __name__ == "__main__":
    main()

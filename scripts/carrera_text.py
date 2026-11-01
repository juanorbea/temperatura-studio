"""Shot texts of «La carrera del billón»: the sentences of the build copy, with long ones cut at a comma.

SPLITS are the cuts (✂) of the direction plan; any piece still longer than AUTO_CHARS is cut at the
comma nearest its middle, so no shot holds more than ~8 s of voice (Juan's cloned voice says about
16 characters a second). Used by scripts/make_carrera_boards.py.
"""
import re
from pathlib import Path

from studio.parse import parse_script, split_sentences

SCRIPT = Path("examples/carrera-del-billon.md")
AUTO_CHARS = 118

# The start of a sentence up to the cut (the plan's ✂).
SPLITS = [
    "El 20 de octubre, ocho días antes de que Alphabet presentara esas cuentas,",
    "Elon Musk puso un objetivo para toda SpaceX:",
    "Pero los servidores con chips a medida, como las TPU,",
    "Los titulares, como el crecimiento de la nube de Google o los gigavatios de Musk,",
    "Antes, al repasar los costes de todo Alphabet, había dicho que la partida de «otros costes de los ingresos» "
    "subió un 32 %, hasta 35.100 millones,",
    "Bernstein preguntó por el crecimiento sin TPU,",
    "Y una frase que importa: Google empezó a reconocer ingresos de estos contratos en el segundo trimestre de 2026,",
    "El flujo de caja libre de Alphabet, lo que queda de la caja del negocio después de pagar las inversiones,",
    "Cuando Google alquila capacidad, pone el dinero:",
    "Kurian lo dijo así: poner sistemas TPU en instalaciones de terceros y de clientes",
    "De ellos, 16.800 son con Crux AI, una empresa conjunta con Blackstone que es parte vinculada",
    "Viene del segmento que llaman Superinteligencia:",
    "Y aquí vuelve Anthropic: ha contratado con SpaceX hasta 120.500 millones de dólares hasta 2029,",
    "El objetivo oficial lo dio Musk en la llamada con analistas:",
    "Luego, el techo: «Quizá sea una posibilidad pequeña a estas alturas, pero no es cero,",
    "La frase «20 es difícil, pero no imposible» no habla de cómputo.",
    "Habla del plan de energía:",
    "Si anualizas los ingresos de Superinteligencia del trimestre, 7.560 millones por cuatro,",
    "Aunque les sumes el resto de SpaceX, Starlink y lanzamientos, unos 28.000 millones anualizados,",
    "Para llegar a 500.000 millones con 13 gigavatios, contando el resto de SpaceX,",
    "Si es por año, que es lo que encaja con otra frase suya,",
    "que la inversión nueva se recupera en menos de un año,",
    "Pasar de los 1,7 gigavatios de septiembre a 13,",
    "Los ingresos de Superinteligencia en el año natural 2027 rondarían los 160.000 millones,",
    "Y su EBITDA ajustado, el beneficio antes de intereses, impuestos y amortizaciones, anualizado,",
    "S&P, que califica a SpaceX con BBB,",
    "Andy Jassy, el consejero delegado de Amazon,",
    "dice que AWS puede crecer más de un 40 % en 2027 y en 2028,",
    "Tunguz lo plantea así:",
    "la primera empresa de 10 billones de dólares",
    "será la primera que construya un motor de cómputo de IA de un billón de ingresos",
    "Con ese múltiplo, la Superinteligencia de SpaceX valdría unos 2,31 billones de dólares con 13 gigavatios",
    "El director financiero dijo que los alquileres nuevos se firman",
    "AWS ingresó 46.000 millones, un 39,3 % más,",
    "En Amazon, la publicidad ingresó 19.600 millones, un 12 % más,",
    "Tras los resultados, en la negociación fuera de hora,",
    "Los ingresos de Microsoft 365 en la nube comercial crecen un 17 %",
    "ServiceNow muestra el lado contrario: se hundió un 27 % el 29 de octubre, al día siguiente de sus resultados,",
]

# Sentences that use the [check] GW figure of 31 Oct (>5 GW at the end of 2026). They are voiced last,
# from the latest draft; see the PR for how to re-render only them.
GW_RE = re.compile(r"Blackwell|Acabaría 2026|unos 3 gigavatios|más de 5(?![\d.,])|Musk anunció|anunció Musk")


def _auto(piece: str) -> list[str]:
    if len(piece) <= AUTO_CHARS:
        return [piece]
    cuts = [m.end() for m in re.finditer(r"[,:;](?=\s)", piece)]
    cuts = [c for c in cuts if c >= 30 and len(piece) - c >= 30]
    if not cuts:
        return [piece]
    c = min(cuts, key=lambda c: abs(c - len(piece) / 2))
    return _auto(piece[:c]) + _auto(piece[c:].strip())


def split_long(sentences: list[str]) -> list[str]:
    out = []
    for s in sentences:
        while True:
            head = next((h for h in SPLITS if s.startswith(h) and len(s) > len(h)), None)
            if not head:
                out.extend(_auto(s))
                break
            out.extend(_auto(head))
            s = s[len(head):].strip()
    return out


def units(number: int) -> list[str]:
    """The pieces of module `number`, in order: each shot takes one or more of them."""
    module = {m.number: m for m in parse_script(SCRIPT.read_text(encoding="utf-8"))}[number]
    return split_long([s for p in module.narration.split("\n\n") for s in split_sentences(p)])


def is_gw(piece: str) -> bool:
    return bool(GW_RE.search(piece))

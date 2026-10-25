"""Reading the script: modules, paragraphs and sentences."""
from studio.parse import parse_script, split_sentences

SCRIPT = """[MÓDULO 2: PILARES]

[ESCENA / VISUAL]
Cuatro bloques.

[NARRADOR / PRESENTADOR - EN CÁMARA]
Hay cuatro temas [9]:

1. Inercia: La historia muestra algo [9, 10].
2. Rivalidad: Entre EE. UU. y China [10]. Otra frase.
"""


def test_numbered_list_items_are_paragraphs_and_citations_go():
    module = parse_script(SCRIPT)[0]
    assert module.narration.split("\n\n") == [
        "Hay cuatro temas:",
        "1. Inercia: La historia muestra algo.",
        "2. Rivalidad: Entre EE. UU. y China. Otra frase.",
    ]


def test_abbreviations_and_list_numbers_do_not_end_sentences():
    text = "1. Inercia: algo. Entre EE. UU. y la UE, además. ¿Cuándo? Hoy."
    assert split_sentences(text) == ["1. Inercia: algo.", "Entre EE. UU. y la UE, además.", "¿Cuándo?", "Hoy."]


BLOCKS = """Guion temperaturacero – Prueba (v7)
Versión 7 · las etiquetas entre corchetes son fuentes
BLOQUE 1: GANCHO. UNA EMPRESA DE CONDIMENTOS
[INDICACIÓN VISUAL / B-ROLL] Un bote de condimento. Rótulo: "ABF".
[LOCUCIÓN / GUION] Ajinomoto es japonesa [Brookings].
A finales de los 80 tenía la mitad [Brookings][JapanGov]. Hoy ronda el 10 %.
BLOQUE 2: EL MITO
[INDICACIÓN VISUAL / B-ROLL] Archivo de los 80.
[LOCUCIÓN / GUION] Reagan puso aranceles del 100 % [Biblioteca Reagan, fuera de las fuentes de Juan].
Unas 25.000 obleas al mes en 2026. [SemiWiki].
¿Para qué diseñar algo que no vas a fabricar tú? [ensayo Juan]
CIERRE
[INDICACIÓN VISUAL / B-ROLL] Planos finales.
[LOCUCIÓN / GUION] Japón nunca se fue [ensayo Juan].
"""


def test_block_format_gives_one_module_per_block_and_cierre_comes_last():
    modules = parse_script(BLOCKS)
    assert [(m.number, m.title) for m in modules] == [
        (1, "GANCHO. UNA EMPRESA DE CONDIMENTOS"), (2, "EL MITO"), (3, "Cierre")]
    assert modules[0].visual == 'Un bote de condimento. Rótulo: "ABF".'


def test_block_format_lines_are_paragraphs_and_every_source_tag_goes():
    modules = parse_script(BLOCKS)
    assert modules[0].narration.split("\n\n") == [
        "Ajinomoto es japonesa.", "A finales de los 80 tenía la mitad. Hoy ronda el 10 %."]
    assert modules[1].narration.split("\n\n") == [
        "Reagan puso aranceles del 100 %.",
        "Unas 25.000 obleas al mes en 2026.",          # no "2026.." left behind by the tag
        "¿Para qué diseñar algo que no vas a fabricar tú?"]
    assert all("[" not in m.narration and "]" not in m.narration for m in modules)


def test_juans_japan_script_parses_cleanly():
    from pathlib import Path
    modules = parse_script(Path("examples/japon-chips.md").read_text(encoding="utf-8"))
    assert [m.number for m in modules] == [1, 2, 3, 4, 5, 6, 7]
    text = " ".join(m.narration for m in modules)
    assert "[" not in text and ".." not in text
    assert modules[-1].narration.endswith("Japón fabrica lo que Taiwán necesita para fabricarlos.")


def test_old_format_still_drops_numeric_citations():
    assert parse_script(SCRIPT)[0].narration.startswith("Hay cuatro temas:")

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

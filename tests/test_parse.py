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


def test_each_script_can_have_its_own_storyboard_and_image_folders(tmp_path, monkeypatch):
    from pathlib import Path
    from studio.build import script_folders
    monkeypatch.chdir(tmp_path)
    assert script_folders(Path("examples/gobernanza-ia.md")) == (Path("storyboards"), Path("assets/images"))
    (tmp_path / "storyboards" / "japon-chips").mkdir(parents=True)
    assert script_folders(Path("examples/japon-chips.md")) == (
        Path("storyboards/japon-chips"), Path("assets/images/japon-chips"))


def test_a_number_that_ends_a_sentence_is_a_real_end():
    assert split_sentences("Arizona, de 4. Detrás hay dinero. Pasar de 40 a 2. Saltarse dos décadas.") == [
        "Arizona, de 4.", "Detrás hay dinero.", "Pasar de 40 a 2.", "Saltarse dos décadas."]


SECTIONS = """Guion temperaturacero – Prueba (v4)
Versión 4 · las etiquetas entre corchetes son fuentes
Duración estimada: 15-18 minutos
Tono: Analítico
Formato: Vídeo ensayo con indicaciones de cámara
INTRODUCCIÓN Y EL FALSO DILEMA
[VFX / TÍTULO EN PANTALLA: "EL MANIFIESTO"]
[CÁMARA EN PLANO MEDIO] NARRADOR: Una reunión cualquiera [Leicht].
No me lo invento [opinión Juan].
SECCIÓN 1: ¿POR QUÉ?
[B-ROLL: Centros de cómputo.]
NARRADOR: Hay tres canales [16]:
1. El código abierto [16].
2. Las API comerciales [16, 17].
CONCLUSIÓN Y HOJA DE RUTA
NARRADOR: Necesita ese contrato.
"""


def test_section_format_numbers_sections_and_keeps_direction_tags_out_of_the_voice():
    modules = parse_script(SECTIONS)
    assert [(m.number, m.title) for m in modules] == [
        (1, "INTRODUCCIÓN Y EL FALSO DILEMA"), (2, "¿POR QUÉ?"), (3, "CONCLUSIÓN Y HOJA DE RUTA")]
    assert modules[0].visual == 'VFX / TÍTULO EN PANTALLA: "EL MANIFIESTO" CÁMARA EN PLANO MEDIO'
    assert modules[0].narration.split("\n\n") == ["Una reunión cualquiera.", "No me lo invento."]
    assert modules[1].narration.split("\n\n") == [
        "Hay tres canales:", "1. El código abierto.", "2. Las API comerciales."]


def test_a_list_number_after_a_colon_starts_a_sentence():
    assert split_sentences("Hay tres canales: 1. El código abierto. 2. Las API.") == [
        "Hay tres canales: 1. El código abierto.", "2. Las API."]


BRACKETED = """GUION DE VÍDEO: Tú Eres el Próximo Caballo

[INTRODUCCIÓN: El caballo moderno]
¿Cuándo fue la última vez que viste un caballo en persona?
Piénsalo por un segundo. Hoy quedan 6,6 millones (American Horse Council).

[PARTE 1: El Imperio del Caballo]
Los caballos lo movían todo.

[PARTE 2: Cómo las máquinas reemplazaron al caballo]
Entonces llegaron las máquinas.
"""


def test_bracketed_headers_give_one_module_each_and_the_title_after_the_colon():
    modules = parse_script(BRACKETED)
    assert [(m.number, m.title) for m in modules] == [
        (1, "El caballo moderno"), (2, "El Imperio del Caballo"),
        (3, "Cómo las máquinas reemplazaron al caballo")]
    assert modules[0].narration.split("\n\n") == [
        "¿Cuándo fue la última vez que viste un caballo en persona?",
        "Piénsalo por un segundo. Hoy quedan 6,6 millones (American Horse Council)."]
    assert "GUION" not in modules[0].narration and "[" not in modules[1].narration
    assert modules[2].narration == "Entonces llegaron las máquinas."


def test_a_closing_quote_stays_with_its_sentence_and_a_bracketed_gloss_does_not_start_one():
    text = ("Un ensayo titulado «¿Seguirán los humanos el camino de los caballos?» (Will humans go the way of horses?). "
            "Su respuesta fue no: «no somos caballos». Otro dijo «Tú no eres un caballo».")
    assert split_sentences(text) == [
        "Un ensayo titulado «¿Seguirán los humanos el camino de los caballos?» (Will humans go the way of horses?).",
        "Su respuesta fue no: «no somos caballos».", "Otro dijo «Tú no eres un caballo»."]
    assert split_sentences("¿Dijo «basta»? Sí.") == ["¿Dijo «basta»?", "Sí."]


ANTHROPIC = """Anthropic sale a bolsa: una apuesta a la curva (guion v2)
Versión 2 · 27 oct 2026 · fuente principal: S-1 de Anthropic (SEC)
Duración estimada: 13-15 minutos
Tono: Divulgativo, directo, con opinión propia
Formato: Vídeo ensayo con indicaciones de cámara
INTRODUCCIÓN: LA PÉRDIDA QUE NO ES
[B-ROLL: Portada del S-1.]
[CÁMARA EN PLANO MEDIO] NARRADOR: 80.700 millones de dólares [S-1 p.64].
Y lo publica [S-1].
[VFX / GRÁFICO EN PANTALLA: Cita «Because these instruments are marked to market.»]
NARRADOR: La pérdida es contable [cálculo]. Lo dijo Nicolas Bustamante [X: Bustamante].
SECCIÓN 1: UNA APUESTA A LA CURVA
[B-ROLL: Carta de los fundadores.]
NARRADOR: Los cofundadores firman una carta [S-1, carta de los fundadores].
Yo me la creo [opinión Juan].
SECCIÓN 2: EN QUÉ SE VA EL DINERO
NARRADOR: En una nota sí separa el coste [S-1 p.F-40].
SECCIÓN 3: NO ES CONCENTRACIÓN
NARRADOR: Unos 250 clientes [S-1 p.9-10].
SECCIÓN 4: BAJAR EL PRECIO
[VFX / GRÁFICO EN PANTALLA: Gráfico de OpenRouter. [check etiquetas: verificar "Sonnet 5.5"]]
NARRADOR: Viene de OpenRouter [OpenRouter]. El índice de Ornn [Ornn] [check base del índice].
Un comentario en X [X] [check].
SECCIÓN 5: LO QUE PODRÍA SALIR MAL
NARRADOR: Pagos mínimos [S-1 nota 17]. Un analista [X: hilo S-1] [check: cifra de crecimiento Q3].
CONCLUSIÓN: EL MINUTO CINCO
[CÁMARA EN PLANO MEDIO] NARRADOR: Mirado en el minuto cinco.
"""


def test_anthropic_section_headers_make_seven_modules_and_skip_meta():
    modules = parse_script(ANTHROPIC)
    assert [(m.number, m.title) for m in modules] == [
        (1, "INTRODUCCIÓN: LA PÉRDIDA QUE NO ES"),
        (2, "UNA APUESTA A LA CURVA"),
        (3, "EN QUÉ SE VA EL DINERO"),
        (4, "NO ES CONCENTRACIÓN"),
        (5, "BAJAR EL PRECIO"),
        (6, "LO QUE PODRÍA SALIR MAL"),
        (7, "CONCLUSIÓN: EL MINUTO CINCO"),
    ]
    joined = " ".join(m.narration for m in modules)
    assert "Versión" not in joined and "Duración" not in joined and "Formato" not in joined
    assert "guion v2" not in joined


def test_anthropic_nested_vfx_check_tag_stays_out_of_the_voice():
    modules = parse_script(ANTHROPIC)
    assert all("[" not in m.narration and "]" not in m.narration for m in modules)
    assert "check" not in modules[4].narration.lower()
    assert "OpenRouter" in modules[4].visual
    assert "check etiquetas" in modules[4].visual
    assert modules[4].narration.split("\n\n")[0].startswith("Viene de OpenRouter")


def test_anthropic_source_tags_and_cam_narrator_on_same_line():
    modules = parse_script(ANTHROPIC)
    assert modules[0].narration.split("\n\n") == [
        "80.700 millones de dólares.",
        "Y lo publica.",
        "La pérdida es contable. Lo dijo Nicolas Bustamante.",
    ]
    assert "CÁMARA EN PLANO MEDIO" in modules[0].visual
    assert "«Because these instruments are marked to market.»" in modules[0].visual


def test_juans_anthropic_script_parses_cleanly():
    from pathlib import Path
    modules = parse_script(Path("examples/anthropic.md").read_text(encoding="utf-8"))
    assert len(modules) == 7
    text = " ".join(m.narration for m in modules)
    assert "[" not in text and "]" not in text
    assert "opinión Juan" not in text and "cálculo" not in text
    assert "OpenRouter" in text  # the word stays; only the [OpenRouter] tag goes
    assert modules[0].narration.startswith("80.700 millones")

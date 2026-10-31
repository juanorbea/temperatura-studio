"""What the cloned voice is asked to read, and what Whisper is expected to hear."""
from pathlib import Path

import pytest

from studio.textprep import Lexicon, heard_text, load_lexicon, number_words, numbers_to_words, voice_text

LEX = Lexicon(
    translate={"Chips for Peace": "Chips para la Paz", "EE. UU.": "Estados Unidos", "AI": "IA",
               "Global AI Governance Forecasts 2025-2060": "Pronósticos de la IA, de 2025 a 2060"},
    respell={"IA": "í a", "Good Judgment Inc.": "Gud Yóchment", "Nvidia": "Envídia"},
)


@pytest.mark.parametrize("n, words", [
    (0, "cero"), (16, "dieciséis"), (21, "veintiuno"), (30, "treinta"), (79, "setenta y nueve"),
    (100, "cien"), (101, "ciento uno"), (1000, "mil"), (2039, "dos mil treinta y nueve"),
    (2050, "dos mil cincuenta"), (2100, "dos mil cien"),
])
def test_number_words(n, words):
    assert number_words(n) == words


@pytest.mark.parametrize("text, said", [
    ("no llegará en los 2030s", "no llegará en los años dos mil treinta"),
    ("El 0,71 % de su PIB", "El cero coma setenta y uno por ciento de su PIB"),
    ("unos 34.000 millones y 7.300 millones", "unos treinta y cuatro mil millones y siete mil trescientos millones"),
    ("Pronósticos 2025-2060", "Pronósticos dos mil veinticinco a dos mil sesenta"),
    ("con un 79% de probabilidad", "con un setenta y nueve por ciento de probabilidad"),
    ("entre 10 y 20 años", "entre diez y veinte años"),
    ("las décadas de 2040 y 2050.", "las décadas de dos mil cuarenta y dos mil cincuenta."),
    ("un 1,5 por mil", "un uno coma cinco por mil"),
])
def test_numbers_are_written_out(text, said):
    assert numbers_to_words(text) == said


def test_translations_and_respellings_go_to_the_voice():
    text = 'el informe de Good Judgment Inc., titulado "Global AI Governance Forecasts 2025-2060".'
    assert voice_text(text, LEX) == ("el informe de Gud Yóchment, titulado Pronósticos de la í a, "
                                     "de dos mil veinticinco a dos mil sesenta.")


def test_whisper_is_expected_to_hear_translations_but_not_respellings():
    text = "una IA segura, firmada por EE. UU. y gigantes como Nvidia"
    assert heard_text(text, LEX) == "una IA segura, firmada por Estados Unidos y gigantes como Nvidia"
    assert voice_text(text, LEX) == "una í a segura, firmada por Estados Unidos y gigantes como Envídia"


def test_whole_words_only_and_case_sensitive():
    assert voice_text("AIDA y la ia", LEX) == "AIDA y la ia"


def test_list_numbers_quotes_dashes_and_parentheses_are_tidied():
    text = '1. Inercia: el "mando humano" —un fallo sistémico— y la Energía Atómica (OIEA).'
    assert voice_text(text, Lexicon()) == ("Primero: Inercia: el mando humano, un fallo sistémico, "
                                           "y la Energía Atómica, OIEA.")


def test_juans_lexicon_loads_and_covers_the_script_terms():
    text = "la IA de EE. UU. y Chips for Peace en EuroHPC con poder de cómputo (compute)"
    f5 = load_lexicon(Path("voices/juan/pronunciations.yaml"), "f5-tts")
    assert voice_text(text, f5) == "la í a de Estados Unidos y Chips para la Paz en Euro hache pe ce con poder de cómputo"
    omni = load_lexicon(Path("voices/juan/pronunciations.yaml"), "omnivoice")
    assert voice_text(text, omni) == "la ía de Estados Unidos y Chips para la Paz en Euro hache pe ce con poder de cómputo"


def test_juans_omnivoice_lexicon_keeps_spanish_spellings_of_english_names():
    omni = load_lexicon(Path("voices/juan/pronunciations.yaml"), "omnivoice")
    said = voice_text("la AGI según Good Judgment Inc., la OPCW y el OIEA", omni)
    assert said == "la ía general según Gud Yóchment, la o pe ce uve doble y el OIEA"


def test_question_mark_left_before_a_removed_citation_is_cleaned():
    assert voice_text("¿similar al OIEA?.", Lexicon()) == "¿similar al OIEA?"


def test_juans_lexicon_covers_the_japan_script():
    omni = load_lexicon(Path("voices/juan/pronunciations.yaml"), "omnivoice")
    said = voice_text("Lo hacen unas máquinas que se llaman coater/developer, con TSMC y EUV de ASML "
                      "en un encapsulado 3D, el CoWoS, y el 0,71 % de su PIB.", omni)
    assert said == ("Lo hacen unas máquinas que se llaman recubridoras y reveladoras, con te ese eme ce y e u uve "
                    "de a ese eme ele en un encapsulado tres de, el Cóuos, y el cero coma setenta y uno por ciento "
                    "de su pe i be.")
    assert voice_text("Chris Miller, el autor de Chip War, y los hot lots.", omni) == \
        "Cris Míler, el autor de La guerra de los chips, y los lotes prioritarios."


def test_decimal_with_leading_zero_keeps_the_zero():
    assert numbers_to_words("unos 2,08 dólares y 0,40") == "unos dos coma cero ocho dólares y cero coma cuarenta"


def test_juans_lexicon_covers_the_anthropic_script():
    omni = load_lexicon(Path("voices/juan/pronunciations.yaml"), "omnivoice")
    said = voice_text(
        "Anthropic bajó con Opus 5.5 frente a Opus 4.5 y Fable 5.1; Mythos 5 y el S-1 de la SEC. "
        "Claude Code y Claude Enterprise en Amazon Bedrock y Google Vertex. "
        "SpaceXAI, la antigua xAI de Elon Musk. SAFE, Trainium, TPU, GPU de NVIDIA y AMD. "
        "OpenRouter, Ornn, Broadcom, Nscale, Lambda, Fortune 500, Cowork, tokens y marketplaces. "
        "El Long-Term Benefit Trust. Nicolas Bustamante. Un 1.368 % y 2,08 dólares. La IA.",
        omni)
    assert "Ánzropic" in said and "Clod Coud" in said and "Clod Énterprais" in said
    assert "Ópus cinco coma cinco" in said and "Féibol cinco coma uno" in said and "Mízos cinco" in said
    assert "ese uno" in said and "ese e ce" in said and "séif" in said
    assert "Ámazon Bédrok" in said and "Gúgel Vértex" in said
    assert "Spéis ex ei ai" in said and "ex ei ai" in said and "Ílon Mask" in said
    assert "Treínium" in said and "te pe u" in said and "ge pe u" in said and "Envídia" in said
    assert "Ópen ráuter" in said and "Orn" in said and "Bródcom" in said and "En squéil" in said
    assert "Fórchun quinientas" in said and "Cóuork" in said and "tókens" in said and "marquetpleisis" in said
    assert "fideicomiso de beneficio a largo plazo" in said and "Nicolás Bustamante" in said
    assert "mil trescientos sesenta y ocho por ciento" in said and "dos coma cero ocho" in said
    assert "ía" in said
    assert "Anthropic" not in said and "Claude" not in said and "S-1" not in said
    assert "5.5" not in said and "2,08" not in said

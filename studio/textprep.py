"""Turn narration into the text a cloned voice reads, and the text it should be heard as.

Only the voice input changes; the script and storyboard keep their wording.
The lexicon (voices/NAME/pronunciations.yaml) has two tables:
  translate: English terms -> Spanish (Whisper should hear the Spanish)
  respell:   names and acronyms -> how to spell them so the voice says them right
"""
import re
from dataclasses import dataclass, field
from pathlib import Path

import yaml

UNITS = ("cero uno dos tres cuatro cinco seis siete ocho nueve diez once doce trece catorce "
         "quince dieciséis diecisiete dieciocho diecinueve veinte veintiuno veintidós veintitrés "
         "veinticuatro veinticinco veintiséis veintisiete veintiocho veintinueve").split()
TENS = {3: "treinta", 4: "cuarenta", 5: "cincuenta", 6: "sesenta", 7: "setenta", 8: "ochenta", 9: "noventa"}
HUNDREDS = {1: "ciento", 2: "doscientos", 3: "trescientos", 4: "cuatrocientos", 5: "quinientos",
            6: "seiscientos", 7: "setecientos", 8: "ochocientos", 9: "novecientos"}
ORDINALS = {1: "Primero", 2: "Segundo", 3: "Tercero", 4: "Cuarto", 5: "Quinto",
            6: "Sexto", 7: "Séptimo", 8: "Octavo", 9: "Noveno", 10: "Décimo"}


def number_words(n: int) -> str:
    """Spanish words for 0 <= n < 1,000,000."""
    if n < 30:
        return UNITS[n]
    if n < 100:
        tens, unit = divmod(n, 10)
        return TENS[tens] + ("" if unit == 0 else " y " + UNITS[unit])
    if n < 1000:
        if n == 100:
            return "cien"
        hundreds, rest = divmod(n, 100)
        return HUNDREDS[hundreds] + ("" if rest == 0 else " " + number_words(rest))
    thousands, rest = divmod(n, 1000)
    head = "mil" if thousands == 1 else number_words(thousands) + " mil"
    return head + ("" if rest == 0 else " " + number_words(rest))


def numbers_to_words(text: str) -> str:
    """Write numbers the way they are said: 2030s, 2025-2060, 79%, 1,5 and plain numbers."""
    text = re.sub(r"\b(\d{1,4})s\b", lambda m: f"años {number_words(int(m[1]))}", text)
    text = re.sub(r"\b(\d{1,6})\s*-\s*(\d{1,6})\b",
                  lambda m: f"{number_words(int(m[1]))} a {number_words(int(m[2]))}", text)
    text = re.sub(r"\b(\d{1,6}),(\d{1,2})\b",
                  lambda m: f"{number_words(int(m[1]))} coma {number_words(int(m[2]))}", text)
    text = re.sub(r"\b(\d{1,6})\s*%", lambda m: f"{number_words(int(m[1]))} por ciento", text)
    return re.sub(r"\b\d{1,6}\b", lambda m: number_words(int(m[0])), text)


@dataclass
class Lexicon:
    translate: dict[str, str] = field(default_factory=dict)
    respell: dict[str, str] = field(default_factory=dict)


def load_lexicon(path: Path) -> Lexicon:
    data = yaml.safe_load(Path(path).read_text(encoding="utf-8")) or {}
    return Lexicon(data.get("translate") or {}, data.get("respell") or {})


def replace_terms(text: str, table: dict[str, str]) -> str:
    """Whole-word, case-sensitive replacement; longer terms first, each spot replaced once."""
    if not table:
        return text
    terms = sorted(table, key=len, reverse=True)
    pattern = re.compile("|".join(rf"(?<!\w){re.escape(t)}(?!\w)" for t in terms))
    return pattern.sub(lambda m: table[m[0]], text)


def _tidy(text: str) -> str:
    """Punctuation the voice should not see: list numbers, quotes, dashes, parentheses."""
    text = re.sub(r"^(\d{1,2})\.\s+", lambda m: ORDINALS.get(int(m[1]), m[1]) + ": ", text)
    text = re.sub(r'["“”«»]', "", text)
    text = re.sub(r"\s*[—–]\s*", ", ", text)
    text = re.sub(r"\s*\(\s*", ", ", text).replace(")", ",")
    text = re.sub(r",\s*([,.:;?!])", r"\1", text)
    text = re.sub(r"([?!])\.", r"\1", text)  # "OIEA? [13]." leaves "?." once citations go
    text = re.sub(r"([:;])\s*,", r"\1", text)
    return " ".join(text.split()).strip(" ,")


def heard_text(text: str, lexicon: Lexicon) -> str:
    """What a listener (Whisper) should hear: translations applied, numbers in words."""
    return numbers_to_words(_tidy(replace_terms(text, lexicon.translate)))


def voice_text(text: str, lexicon: Lexicon) -> str:
    """What the voice model reads: translations, then respellings, then numbers in words."""
    return numbers_to_words(_tidy(replace_terms(replace_terms(text, lexicon.translate), lexicon.respell)))

"""Read a script and split it into modules.

Two script formats are understood.

Modules (gobernanza-ia), with numeric citations like [8, 30]:
  [MÓDULO N: TITLE]
  [ESCENA / VISUAL]
  visual direction...
  [NARRADOR / PRESENTADOR - EN CÁMARA]
  narration...          (blank lines separate paragraphs)

Blocks (japon-chips), with source tags in words like [Brookings] or [ensayo Juan]:
  BLOQUE N: TITLE       (and a last block called CIERRE, numbered after the others)
  [INDICACIÓN VISUAL / B-ROLL] visual direction...
  [LOCUCIÓN / GUION] narration...
  more narration...     (each line is a paragraph)

Sections (potencias-medias), with tags like [3], [12, 13], [Leicht] or [opinión Juan]:
  INTRODUCCIÓN ...      (then SECCIÓN N: TITLE, and a last CONCLUSIÓN ...; numbered in order)
  or, in brackets (caballo): [INTRODUCCIÓN: TITLE], [PARTE N: TITLE]
  [VFX ...] [B-ROLL ...] [CÁMARA ...] visual direction, at the start of a line
  NARRADOR: narration...  (the prefix is optional; each line is a paragraph)

Every bracketed citation or source tag is removed from the narration.
"""
import re
from dataclasses import dataclass

MODULE_RE = re.compile(r"^\[MÓDULO\s+(\d+):\s*(.+?)\]\s*$", re.MULTILINE)
VISUAL_TAG = "[ESCENA / VISUAL]"
NARRATION_TAG = "[NARRADOR / PRESENTADOR - EN CÁMARA]"
# Citation markers like [8] or [8, 30, 131], and source tags like [Brookings][JapanGov]
# or [Biblioteca Reagan, fuera de las fuentes de Juan]. Section tags are read before this runs.
CITATION_RE = re.compile(r"\s*\[[^\[\]\n]+\]")
BLOCK_RE = re.compile(r"^(?:BLOQUE\s+(\d+):\s*(.+?)|(CIERRE))\s*$", re.MULTILINE)
BLOCK_VISUAL_TAG = "[INDICACIÓN VISUAL / B-ROLL]"
BLOCK_NARRATION_TAG = "[LOCUCIÓN / GUION]"
SECTION_RE = re.compile(
    r"^(?:INTRODUCCIÓN\b.*|SECCIÓN\s+\d+:.*|CONCLUSIÓN\b.*"
    r"|\[(?:INTRODUCCIÓN|PARTE\s+\d+|CONCLUSIÓN)\b[^\]\n]*\])$", re.MULTILINE)
SECTION_PREFIX_RE = re.compile(r"^SECCIÓN\s+\d+:\s*")
# Bracketed headers (caballo): [INTRODUCCIÓN: title], [PARTE N: title]; the title is what follows the colon.
BRACKET_HEADER_RE = re.compile(r"^\[(?:INTRODUCCIÓN|PARTE\s+\d+|CONCLUSIÓN)\s*:?\s*(.*?)\]$")
# Direction tags open a line: [VFX / ...], [B-ROLL: ...], [CÁMARA EN PLANO MEDIO].
# A cue may nest one bracketed note, e.g. [VFX ... [check etiquetas: ...]].
DIRECTION_OPEN_RE = re.compile(r"^\s*\[((?:VFX|B-ROLL|CÁMARA)\b)")
# A sentence ends at . ? ! (optionally followed by a closing quote, which it keeps) before whitespace.
SENTENCE_END_RE = re.compile(r'(?<=[.?!])\s+|(?<=[.?!]["»”])\s+')
# ...but not after "EE." (of "EE. UU.") or a list number like "1." that starts the sentence,
# nor before a lowercase word or a bracketed gloss ("«¿...?» (Will humans...?).").
# A number ending a sentence ("Arizona, de 4.") is a real end.
# A list number after a colon ("tres canales: 1. El uso...") does not end one either.
NOT_AN_END_RE = re.compile(r"(?:(?:^|\s)EE\.|^\d{1,2}\.|:\s\d{1,2}\.)$")


@dataclass
class Module:
    number: int
    title: str
    visual: str
    narration: str  # citation markers removed, paragraphs separated by blank lines



def match_direction(line: str) -> tuple[str, str] | None:
    """If line starts with a VFX/B-ROLL/CÁMARA cue, return (inner text, remainder).

    Handles one level of nested brackets inside the cue (a [check ...] note)."""
    m = DIRECTION_OPEN_RE.match(line)
    if not m:
        return None
    start = line.find("[")
    depth = 0
    for i in range(start, len(line)):
        if line[i] == "[":
            depth += 1
        elif line[i] == "]":
            depth -= 1
            if depth == 0:
                return line[start + 1:i].strip(), line[i + 1:]
    # Unclosed: treat the rest of the line as the cue so nothing leaks into narration.
    return line[start + 1:].strip(), ""


def strip_citations(text: str) -> str:
    return CITATION_RE.sub("", text)


def strip_source_tags(text: str) -> str:
    """Block format: remove source tags, and the doubled full stop a tag can leave ("2026. [X].")."""
    return re.sub(r"\.\.(?=\s|$)", ".", strip_citations(text)).strip()


def split_sentences(text: str) -> list[str]:
    """Split narration into sentences, keeping punctuation."""
    flat = " ".join(text.split())
    sentences = []
    for part in (p.strip() for p in SENTENCE_END_RE.split(flat)):
        if not part:
            continue
        if sentences and (NOT_AN_END_RE.search(sentences[-1]) or part[0].islower()
                          or part[0] == "("):
            sentences[-1] += " " + part
        else:
            sentences.append(part)
    return sentences


def parse_script(text: str) -> list[Module]:
    if MODULE_RE.search(text):
        pass
    elif BLOCK_RE.search(text):
        return _parse_blocks(text)
    elif SECTION_RE.search(text):
        return _parse_sections(text)
    matches = list(MODULE_RE.finditer(text))
    modules = []
    for i, m in enumerate(matches):
        end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
        body = text[m.end():end]
        visual, _, narration = body.partition(NARRATION_TAG)
        visual = visual.replace(VISUAL_TAG, "").strip()
        # Blank lines separate paragraphs; so does each item of a numbered list ("1. ...").
        blocks = re.split(r"\n\s*\n|\n(?=\d{1,2}\.\s)", narration.strip())
        paragraphs = [" ".join(p.split()) for p in blocks]
        narration = "\n\n".join(strip_citations(p) for p in paragraphs if p)
        modules.append(Module(int(m.group(1)), m.group(2).strip(), visual, narration))
    return modules


def _parse_blocks(text: str) -> list[Module]:
    """BLOQUE N / CIERRE format: one module per block, one paragraph per narration line."""
    matches = list(BLOCK_RE.finditer(text))
    modules = []
    for i, m in enumerate(matches):
        end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
        body = text[m.end():end]
        if BLOCK_NARRATION_TAG not in body:
            raise ValueError(f"block {m.group(0)!r} has no {BLOCK_NARRATION_TAG} section")
        visual, _, narration = body.partition(BLOCK_NARRATION_TAG)
        visual = " ".join(visual.replace(BLOCK_VISUAL_TAG, "").split())
        paragraphs = [strip_source_tags(" ".join(line.split())) for line in narration.strip().splitlines()]
        number = int(m.group(1)) if m.group(1) else (modules[-1].number + 1 if modules else 1)
        title = (m.group(2) or "Cierre").strip()
        modules.append(Module(number, title, visual, "\n\n".join(p for p in paragraphs if p)))
    return modules


def _parse_sections(text: str) -> list[Module]:
    """INTRODUCCIÓN / SECCIÓN N / CONCLUSIÓN format: one module per section, numbered in order.

    Header lines before the first section (version, duration, tone, format) are not narration."""
    matches = list(SECTION_RE.finditer(text))
    modules = []
    for i, m in enumerate(matches):
        end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
        visuals, paragraphs = [], []
        for line in text[m.end():end].splitlines():
            while pair := match_direction(line):
                visuals.append(pair[0])
                line = pair[1]
            line = re.sub(r"^\s*NARRADOR:\s*", "", line)
            if paragraph := strip_source_tags(" ".join(line.split())):
                paragraphs.append(paragraph)
        header = BRACKET_HEADER_RE.match(m.group(0))
        title = header.group(1).strip() if header else SECTION_PREFIX_RE.sub("", m.group(0)).strip()
        modules.append(Module(i + 1, title, " ".join(visuals), "\n\n".join(paragraphs)))
    return modules

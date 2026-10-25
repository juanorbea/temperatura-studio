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
# A sentence ends at . ? ! (optionally followed by a closing quote) before whitespace.
SENTENCE_END_RE = re.compile(r'(?<=[.?!])["»”]?\s+')
# ...but not after "EE." (of "EE. UU.") or a list number like "1.", nor before a lowercase word
NOT_AN_END_RE = re.compile(r"(?:^|\s)(?:EE\.|\d{1,2}\.)$")


@dataclass
class Module:
    number: int
    title: str
    visual: str
    narration: str  # citation markers removed, paragraphs separated by blank lines


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
        if sentences and (NOT_AN_END_RE.search(sentences[-1]) or part[0].islower()):
            sentences[-1] += " " + part
        else:
            sentences.append(part)
    return sentences


def parse_script(text: str) -> list[Module]:
    if BLOCK_RE.search(text) and not MODULE_RE.search(text):
        return _parse_blocks(text)
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

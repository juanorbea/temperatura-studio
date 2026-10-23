"""Read a script and split it into modules.

Script format:
  [MÓDULO N: TITLE]
  [ESCENA / VISUAL]
  visual direction...
  [NARRADOR / PRESENTADOR - EN CÁMARA]
  narration...
"""
import re
from dataclasses import dataclass

MODULE_RE = re.compile(r"^\[MÓDULO\s+(\d+):\s*(.+?)\]\s*$", re.MULTILINE)
VISUAL_TAG = "[ESCENA / VISUAL]"
NARRATION_TAG = "[NARRADOR / PRESENTADOR - EN CÁMARA]"
# Citation markers like [8] or [8, 30, 131].
CITATION_RE = re.compile(r"\s*\[\d+(?:\s*,\s*\d+)*\]")
# A sentence ends at . ? ! (optionally followed by a closing quote) before whitespace.
SENTENCE_END_RE = re.compile(r'(?<=[.?!])["»”]?\s+')


@dataclass
class Module:
    number: int
    title: str
    visual: str
    narration: str  # citation markers removed, paragraphs separated by blank lines


def strip_citations(text: str) -> str:
    return CITATION_RE.sub("", text)


def split_sentences(text: str) -> list[str]:
    """Split narration into sentences, keeping punctuation."""
    flat = " ".join(text.split())
    parts = SENTENCE_END_RE.split(flat)
    return [p.strip() for p in parts if p.strip()]


def parse_script(text: str) -> list[Module]:
    matches = list(MODULE_RE.finditer(text))
    modules = []
    for i, m in enumerate(matches):
        end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
        body = text[m.end():end]
        visual, _, narration = body.partition(NARRATION_TAG)
        visual = visual.replace(VISUAL_TAG, "").strip()
        paragraphs = [" ".join(p.split()) for p in narration.strip().split("\n\n")]
        narration = "\n\n".join(strip_citations(p) for p in paragraphs if p)
        modules.append(Module(int(m.group(1)), m.group(2).strip(), visual, narration))
    return modules

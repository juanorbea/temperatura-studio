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

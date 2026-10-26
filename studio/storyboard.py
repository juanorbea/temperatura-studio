"""Load a storyboard YAML file and check it against the script."""
from dataclasses import dataclass, field
from pathlib import Path

import yaml

from studio.parse import CITATION_RE, Module, split_sentences  # CITATION_RE also matches source tags

SHOT_TYPES = {"image", "title_card", "text_overlay"}


@dataclass
class Shot:
    id: str
    type: str
    text: str
    prompt: str = ""           # scene description for image and text_overlay shots
    character: bool = False    # the AI character appears in this shot
    title: str = ""            # title_card only
    subtitle: str = ""         # title_card only
    overlay: dict = field(default_factory=dict)  # text_overlay only
    lead_in: float = 0.0       # seconds of silence before the voice
    tail: float = 0.0          # seconds of silence after the voice
    motion: str = ""           # zoom_in | zoom_out | pan_left | pan_right | none


@dataclass
class Storyboard:
    module: int
    voice: str
    style: str
    character: str
    shots: list[Shot]
    theme: str = "charcoal"    # graphics theme (studio/graphics.py): charcoal, blueprint, editorial or pizarra

    def image_prompt(self, shot: Shot) -> str:
        """Full prompt for an image provider: scene + character + locked style."""
        parts = [shot.prompt]
        if shot.character:
            parts.append(self.character)
        parts.append(self.style)
        return " ".join(" ".join(parts).split())


def load(path: Path) -> Storyboard:
    data = yaml.safe_load(Path(path).read_text(encoding="utf-8"))
    shots = [Shot(**s) for s in data["shots"]]
    for s in shots:
        if s.type not in SHOT_TYPES:
            raise ValueError(f"{s.id}: unknown shot type {s.type!r}")
    return Storyboard(data["module"], data["voice"], data["style"], data["character"], shots,
                      data.get("theme", "charcoal"))


def check_coverage(board: Storyboard, module: Module) -> None:
    """Fail unless the shots, in order, cover the module narration exactly once."""
    for s in board.shots:
        if CITATION_RE.search(s.text):
            raise ValueError(f"{s.id}: citation or source tag left in voice text: {s.text!r}")
    joined = " ".join(s.text.strip() for s in board.shots)
    expected = " ".join(module.narration.split())
    if joined != expected:
        i = next((k for k, (a, b) in enumerate(zip(joined, expected)) if a != b),
                 min(len(joined), len(expected)))
        raise ValueError(
            "storyboard text does not match the narration near:\n"
            f"  storyboard: ...{joined[max(0, i - 40):i + 40]}...\n"
            f"  script:     ...{expected[max(0, i - 40):i + 40]}..."
        )
    for sentence in split_sentences(module.narration):
        if joined.count(sentence) != 1:
            raise ValueError(f"sentence not covered exactly once: {sentence!r}")

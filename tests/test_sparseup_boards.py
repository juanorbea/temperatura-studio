"""SPARSEUP storyboards cover the converted script exactly once."""
from pathlib import Path

from studio.parse import parse_script
from studio.storyboard import check_coverage, load

SCRIPT = Path("examples/sparseup.md")
BOARDS = Path("storyboards/sparseup")


def test_sparseup_boards_cover_the_script():
    modules = {m.number: m for m in parse_script(SCRIPT.read_text(encoding="utf-8"))}
    paths = sorted(BOARDS.glob("module*.yaml"), key=lambda p: int(p.stem.replace("module", "")))
    assert [int(p.stem.replace("module", "")) for p in paths] == list(modules)
    for path in paths:
        n = int(path.stem.replace("module", ""))
        check_coverage(load(path), modules[n])

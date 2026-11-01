"""«La carrera del billón» (video 8): the boards cover the script exactly, silent shots are
allowed, and no shot is planned longer than ~8 s or leaves more than four shots without a photo."""
from pathlib import Path

import pytest

from scripts import make_carrera_boards as B
from scripts.carrera_text import GW_RE, units
from studio import storyboard
from studio.parse import parse_script

SCRIPT = Path("examples/carrera-del-billon.md")


@pytest.mark.parametrize("n", sorted(B.P))
def test_plan_covers_every_piece_once(n):
    assert sum(k for k, _ in B.P[n]) == len(units(n))


@pytest.mark.parametrize("n", sorted(B.P))
def test_written_boards_cover_the_narration(n):
    board = storyboard.load(Path(f"storyboards/carrera-del-billon/module{n}.yaml"))
    module = {m.number: m for m in parse_script(SCRIPT.read_text(encoding="utf-8"))}[n]
    storyboard.check_coverage(board, module)
    for shot in board.shots:
        if shot.prompt:
            assert Path(f"assets/images/carrera-del-billon/module{n}/{shot.id}.jpg").exists(), shot.id


@pytest.mark.parametrize("n", sorted(B.P))
def test_no_shot_is_planned_over_eight_seconds_or_without_photos_for_long(n):
    pieces, i, run = units(n), 0, 0
    for count, fields in B.P[n]:
        seconds = B.estimate(pieces[i:i + count]) + fields.get("lead_in", 0) + fields.get("tail", 0)
        assert seconds <= 8.0, (n, pieces[i:i + count])
        run = 0 if fields.get("prompt") else run + 1
        assert run <= 4, (n, pieces[i])
        i += count


def test_silent_shots_are_allowed_but_text_must_still_match():
    module = {m.number: m for m in parse_script(SCRIPT.read_text(encoding="utf-8"))}[8]
    board = storyboard.load(Path("storyboards/carrera-del-billon/module8.yaml"))
    assert any(not s.text for s in board.shots)
    board.shots[1].text = "Una frase que no está en el guion."
    with pytest.raises(ValueError):
        storyboard.check_coverage(board, module)


def test_gw_sentences_are_found_where_the_hook_ramp_and_ending_say_them():
    found = {n: [u for u in units(n) if GW_RE.search(u)] for n in (1, 6, 8)}
    assert all(found.values())
    assert any("Blackwell" in u for u in found[1]) and any("Blackwell" in u for u in found[6])
    assert any("más de 5" in u for u in found[8])


@pytest.mark.parametrize("n", sorted(B.P))
def test_build_cuts_the_voice_into_the_same_pieces_as_the_cache(n):
    """The narration is generated ahead per piece of units(n); the build must ask for the same pieces."""
    from studio import clone
    board = storyboard.load(Path(f"storyboards/carrera-del-billon/module{n}.yaml"))
    assert [p.text for p in clone.pieces_for_shots(board.shots, set(), 160)] == units(n)

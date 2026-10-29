"""The Markdown converter makes a build copy the section parser reads, without touching the original."""
import pytest

from scripts.convert_markdown_script import convert
from studio.parse import parse_script

DRAFT = """# China y la IA (1): Título

Duración estimada: 22-23 minutos
Serie: China y la IA, episodio 1

## Gancho: una J y una X

*[B-ROLL: Primer plano de un documento.]*

*[CÁMARA EN PLANO MEDIO]* **NARRADOR:** 266402J. 266404X.

Parecen números de serie [1].

## En medio

*[VFX / GRÁFICO EN PANTALLA: "J = 禁 (jìn): prohibido".]*

**NARRADOR:** La J viene de 禁, prohibido [1] [2].

## Final: cinco años

*[CÁMARA EN PLANO MEDIO]* **NARRADOR:** El mismo catálogo.

Lo que separa los dos casos no es la norma [opinión Juan].

*[VFX / GRÁFICO EN PANTALLA: La X en blanco.]*

**NARRADOR:** Y desde ahora, la letra la escribe Pekín.
"""


def test_sections_cues_and_narration():
    modules = parse_script(convert(DRAFT))
    assert [(m.number, m.title) for m in modules] == [(1, "Gancho: una J y una X"), (2, "En medio"),
                                                      (3, "Final: cinco años")]
    assert modules[0].narration == "266402J. 266404X.\n\nParecen números de serie."
    assert modules[1].narration == "La J viene de 禁, prohibido."
    assert "Duración" not in modules[0].narration and "*" not in convert(DRAFT)


def test_camera_cues_become_ai_character_shots():
    modules = parse_script(convert(DRAFT))
    assert "CÁMARA EN PLANO MEDIO → PERSONAJE IA" in modules[0].visual
    assert "B-ROLL: Primer plano de un documento." in modules[0].visual


def test_pending_lines_are_kept_as_cues_and_not_voiced():
    final = parse_script(convert(DRAFT, pending="Lo que separa"))[-1]
    assert final.narration == "El mismo catálogo."
    assert "PENDIENTE DE JUAN, sin locución todavía: «Lo que separa los dos casos no es la norma.»" in final.visual
    assert "«Y desde ahora, la letra la escribe Pekín.»" in final.visual
    with pytest.raises(ValueError, match="not found"):
        convert(DRAFT, pending="No está en el guion")


def test_the_original_is_never_overwritten(tmp_path):
    from scripts import convert_markdown_script as conv
    src = tmp_path / "draft.md"
    src.write_text(DRAFT, encoding="utf-8")
    import sys
    sys.argv = ["x", str(src), str(src)]
    with pytest.raises(SystemExit):
        conv.main()
    assert src.read_text(encoding="utf-8") == DRAFT

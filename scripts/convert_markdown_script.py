"""Make a build copy of a script written in Markdown, in the section format studio/parse.py reads.

The writers' drafts (e.g. writing/china-ia-01-exportaciones/draft.md) look like this:
  # Title                                   -> dropped (the lines before the first ## are header notes)
  ## Gancho: una J y una X                  -> [INTRODUCCIÓN: ...], [PARTE N: ...], ..., [CONCLUSIÓN: ...]
  *[B-ROLL: ...]*  *[VFX / ...]*            -> [B-ROLL: ...]  [VFX / ...]  (visual direction)
  *[CÁMARA EN PLANO MEDIO]*                 -> [CÁMARA EN PLANO MEDIO → PERSONAJE IA: ...]
  **NARRADOR:** text                        -> NARRADOR: text
  ### Subheading                            -> dropped (put it in a shot's kicker), unless --section
                                               names it: then it starts a module of its own

--section "Subheading" (repeatable) promotes a ### subheading to a module; --title "Heading=New title"
(repeatable) renames a module in the copy (the title of its section header).

The channel never shows Juan on camera, so every CÁMARA cue becomes a shot of the AI
character (Juan's mannequin); the converted cue says so and the storyboard follows it.
Lines that are not ready to be voiced (--pending) become a visual cue marked PENDIENTE, so
they stay visible in the copy but are not narrated. The original file is never changed.

Run from the repo root:
  .venv/bin/python -m scripts.convert_markdown_script DRAFT.md examples/NAME.md \
      [--pending "first words of the first line still pending"]
"""
import argparse
import re
from pathlib import Path

HEADING_RE = re.compile(r"^##\s+(.+?)\s*$")
SUBHEADING_RE = re.compile(r"^###\s+(.+?)\s*$")
CUE_RE = re.compile(r"\*\[((?:VFX|B-ROLL|CÁMARA)\b[^\]]*)\]\*")
NARRATOR_RE = re.compile(r"\*\*NARRADOR:\*\*\s*")
TAG_RE = re.compile(r"\s*\[[^\[\]\n]+\]")  # source tags like [1] or [opinión Juan]
CHARACTER = "PERSONAJE IA: el maniquí de Juan; el canal no sale a cámara"


def _cue(text: str) -> str:
    text = " ".join(text.split())
    if text.startswith("CÁMARA"):
        text = f"{text} → {CHARACTER}"
    return f"[{text}]"


def convert(markdown: str, pending: str = "", promote: tuple[str, ...] = (),
            titles: dict[str, str] | None = None) -> str:
    """Return the build copy. pending: the start of the first narration line that must not be
    voiced yet; it and every narration line after it become PENDIENTE cues. promote: ###
    subheadings that start a module of their own (every other ### line is dropped). titles:
    heading text -> title to use in the copy."""
    sections: list[tuple[str, list[str]]] = []
    titles = titles or {}
    held = False
    missing = set(promote) | set(titles)
    for raw in markdown.splitlines():
        m = HEADING_RE.match(raw)
        sub = SUBHEADING_RE.match(raw)
        if m or (sub and sub.group(1) in promote):
            heading = (m or sub).group(1)
            missing.discard(heading)
            sections.append((titles.get(heading, heading).replace("]", ")"), []))
            continue
        if sub:
            continue  # a subchapter: its name goes in a shot's kicker, not in the voice
        if not sections:
            continue  # title and header notes
        line = CUE_RE.sub(lambda m: _cue(m.group(1)), raw.strip())
        line = NARRATOR_RE.sub("NARRADOR: ", line)
        if "**" in line or re.search(r"(?<!\w)\*(?!\s)", line):
            raise ValueError(f"unexpected Markdown emphasis in: {raw!r}")
        cues = re.match(r"^(?:\[[^\]]*\]\s*)*", line).group(0)
        speech = line[len(cues):]
        if pending and speech.replace("NARRADOR: ", "").startswith(pending):
            held = True
        if held and speech:
            words = TAG_RE.sub("", speech.replace("NARRADOR: ", "")).strip()
            line = f"{cues}[B-ROLL: PENDIENTE DE JUAN, sin locución todavía: «{words}»]"
        sections[-1][1].append(line)
    if missing:
        raise ValueError(f"headings not found: {sorted(missing)}")
    if pending and not held:
        raise ValueError(f"--pending text not found in the narration: {pending!r}")
    if len(sections) < 2:
        raise ValueError("expected at least two ## sections")
    out = []
    for i, (title, lines) in enumerate(sections):
        kind = "INTRODUCCIÓN" if i == 0 else "CONCLUSIÓN" if i == len(sections) - 1 else f"PARTE {i}"
        out.append(f"[{kind}: {title}]")
        out.extend(lines)
    return re.sub(r"\n{3,}", "\n\n", "\n".join(out)).strip() + "\n"


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("source", type=Path)
    ap.add_argument("out", type=Path)
    ap.add_argument("--pending", default="", help="start of the first narration line not to voice yet")
    ap.add_argument("--section", action="append", default=[], help="### subheading that starts a module")
    ap.add_argument("--title", action="append", default=[], help="'Heading=New title' for a module")
    args = ap.parse_args()
    titles = dict(t.split("=", 1) for t in args.title)
    if args.source.resolve() == args.out.resolve():
        raise SystemExit("the build copy must be a different file; the original is never changed")
    header = (f"<!-- Build copy of {args.source.name}, made by scripts/convert_markdown_script.py. "
              "Edit the original and convert again. -->\n")
    args.out.write_text(header + convert(args.source.read_text(encoding="utf-8"), args.pending,
                                     tuple(args.section), titles), encoding="utf-8")
    print(f"{args.out}")


if __name__ == "__main__":
    main()

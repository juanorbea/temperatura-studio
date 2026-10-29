"""Write the Chinese font of the repo: Noto Serif CJK SC, cut down to the common characters.

The full font is about 26 MB per weight. This keeps the 3,755 most common simplified
characters (GB2312 level 1), CJK punctuation, Latin, and any extra characters a script needs,
which comes to about 2.6 MB per weight. Noto CJK is under the SIL Open Font License 1.1
(assets/fonts/NotoSerifCJK-LICENSE.txt); a subset is allowed under the same licence and
keeps the name, since "Noto Serif CJK" is not a reserved font name.

Needs fonttools (pip install fonttools) and the font from the system (Debian/Ubuntu package
fonts-noto-cjk, or https://github.com/notofonts/noto-cjk). Run from the repo root:
  python3 -m scripts.subset_cjk_font                       # common characters only
  python3 -m scripts.subset_cjk_font --text "龘"           # plus characters a new script needs
If a character draws as an empty box, add it with --text and run again.
"""
import argparse
import subprocess
from pathlib import Path

SOURCE = Path("/usr/share/fonts/opentype/noto")
OUT = Path("assets/fonts")
FACE_SC = 2  # face number of Noto Serif CJK SC inside the .ttc collection (JP, KR, SC, TC, HK)
# Latin, Latin-1, general punctuation (dashes, quotes, ellipsis), CJK punctuation, full-width forms
UNICODES = "U+0020-007E,U+00A0-00FF,U+2010-2027,U+3000-303F,U+FF01-FF5E"


def common_characters() -> str:
    """The 3,755 level-1 characters of GB2312 (rows 0xB0-0xD7), the most used in simplified Chinese."""
    chars = []
    for hi in range(0xB0, 0xD8):
        for lo in range(0xA1, 0xFF):
            try:
                chars.append(bytes([hi, lo]).decode("gb2312"))
            except UnicodeDecodeError:
                pass
    return "".join(chars)


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--text", default="", help="extra characters to keep")
    ap.add_argument("--source", type=Path, default=SOURCE, help="folder with NotoSerifCJK-*.ttc")
    args = ap.parse_args()
    keep = OUT / "NotoSerifCJK-characters.txt"
    keep.write_text("".join(sorted(set(common_characters() + args.text))) + "\n", encoding="utf-8")
    for weight in ("Regular", "Bold"):
        out = OUT / f"NotoSerifCJKsc-{weight}.otf"
        subprocess.run(["pyftsubset", str(args.source / f"NotoSerifCJK-{weight}.ttc"), f"--font-number={FACE_SC}",
                        f"--text-file={keep}", f"--unicodes={UNICODES}", "--layout-features=*",
                        "--name-IDs=*", "--name-languages=*", f"--output-file={out}"], check=True)
        print(f"{out}: {out.stat().st_size / 1e6:.1f} MB")


if __name__ == "__main__":
    main()

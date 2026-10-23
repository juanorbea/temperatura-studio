"""Command line: python -m studio build SCRIPT --module N"""
import argparse
import sys
from pathlib import Path

from studio.build import build_module
from studio.images import FolderProvider, MissingImages


def main() -> int:
    parser = argparse.ArgumentParser(prog="python -m studio")
    sub = parser.add_subparsers(dest="command", required=True)
    b = sub.add_parser("build", help="build one module of a script into a video")
    b.add_argument("script", type=Path)
    b.add_argument("--module", type=int, required=True)
    b.add_argument("--storyboard", type=Path, help="default: storyboards/moduleN.yaml")
    b.add_argument("--images", type=Path, help="default: assets/images/moduleN")
    b.add_argument("--out", type=Path, default=Path("output"))
    b.add_argument("--cache", type=Path, default=Path("cache"))
    args = parser.parse_args()

    n = args.module
    board = args.storyboard or Path(f"storyboards/module{n}.yaml")
    images = FolderProvider(args.images or Path(f"assets/images/module{n}"))
    try:
        build_module(args.script, n, board, images, args.out, args.cache)
    except MissingImages as e:
        print(e, file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())

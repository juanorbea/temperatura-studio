"""Render a table of overlays (a CHARTS dict) to PNG files, to look at graphics without a build.

Run: .venv/bin/python -m scripts.render_charts scripts.china_ia_01_charts OUT_DIR [--theme blueprint]
"""
import argparse
import importlib
from pathlib import Path

from studio import graphics


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("module", help="Python module with a CHARTS dict, e.g. scripts.china_ia_01_charts")
    ap.add_argument("out", type=Path)
    ap.add_argument("--theme", default="blueprint")
    args = ap.parse_args()
    charts = importlib.import_module(args.module).CHARTS
    args.out.mkdir(parents=True, exist_ok=True)
    for name, overlay in charts.items():
        graphics.overlay_card(overlay, args.out / f"{name}.png", on_photo=False, theme=args.theme)
    print(f"{len(charts)} graphics in {args.out}")


if __name__ == "__main__":
    main()

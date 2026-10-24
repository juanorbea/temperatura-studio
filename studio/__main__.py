"""Command line: python -m studio build SCRIPT --module N [--audio FILE | --voice NAME]
               python -m studio build SCRIPT --module all [--voice NAME]   (one video of all modules)
               python -m studio narrate SCRIPT --module N --voice NAME"""
import argparse
import sys
from pathlib import Path

from studio.build import build_module, build_script, narrate_module
from studio.clone import VoiceError
from studio.align import AlignmentError
from studio.images import FolderProvider, MissingImages
from studio.parse import parse_script
from studio.recording import WHISPER_MODEL


def main() -> int:
    parser = argparse.ArgumentParser(prog="python -m studio")
    sub = parser.add_subparsers(dest="command", required=True)
    b = sub.add_parser("build", help="build one module of a script into a video")
    b.add_argument("script", type=Path)
    b.add_argument("--module", required=True,
                   help="module number, or 'all' to build every module and join them into one video")
    b.add_argument("--storyboard", type=Path, help="default: storyboards/moduleN.yaml")
    b.add_argument("--images", type=Path,
                   help="default: assets/images/moduleN (with --module all: the folder holding moduleN/)")
    b.add_argument("--audio", type=Path,
                   help="your own recording of the module narration (m4a, mp3, wav); "
                        "default: synthesized voice")
    b.add_argument("--voice", help="narrate with a cloned voice profile from voices/NAME (e.g. juan)")
    b.add_argument("--voice-device", default="cpu", help="device for the cloned voice: cpu or cuda")
    b.add_argument("--whisper-model", default=WHISPER_MODEL,
                   help=f"faster-whisper model for --audio and for checking --voice (default: {WHISPER_MODEL})")
    b.add_argument("--out", type=Path, default=Path("output"))
    b.add_argument("--cache", type=Path, default=Path("cache"))
    v = sub.add_parser("narrate", help="generate a module's narration in a cloned voice (no video); "
                                       "fills the same cache that build --voice uses")
    v.add_argument("script", type=Path)
    v.add_argument("--module", type=int, nargs="+", required=True)
    v.add_argument("--voice", required=True)
    v.add_argument("--voice-device", default="cpu")
    v.add_argument("--whisper-model", default=WHISPER_MODEL)
    v.add_argument("--out", type=Path, default=Path("output"))
    v.add_argument("--cache", type=Path, default=Path("cache"))
    args = parser.parse_args()

    if args.command == "narrate":
        try:
            for n in args.module:
                narrate_module(args.script, n, args.voice, args.out, args.cache,
                               args.voice_device, args.whisper_model)
        except VoiceError as e:
            print(e, file=sys.stderr)
            return 1
        return 0

    if args.module == "all":
        if args.audio or args.storyboard:
            print("--module all takes no --audio or --storyboard", file=sys.stderr)
            return 1
        numbers = [m.number for m in parse_script(args.script.read_text(encoding="utf-8"))]
        try:
            build_script(args.script, numbers, args.images or Path("assets/images"), args.out,
                         args.cache, args.whisper_model, args.voice, args.voice_device)
        except (MissingImages, VoiceError) as e:
            print(e, file=sys.stderr)
            return 1
        return 0

    n = int(args.module)
    board = args.storyboard or Path(f"storyboards/module{n}.yaml")
    images = FolderProvider(args.images or Path(f"assets/images/module{n}"))
    try:
        build_module(args.script, n, board, images, args.out, args.cache,
                     args.audio, args.whisper_model, args.voice, args.voice_device)
    except (MissingImages, AlignmentError, VoiceError) as e:
        print(e, file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())

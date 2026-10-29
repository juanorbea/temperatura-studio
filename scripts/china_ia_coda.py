"""The silent coda of «China y la IA #1»: after the last sentence, «EXPEDIENTE 01 · CERRADO» and the
character walking away down the archive (1.5 s of silence in the plan, plus the walk), then the end
screen «EXPEDIENTE 02 · PRÓXIMAMENTE». The pipeline has no shot without narration, so the coda is
rendered here and appended to module 15 with the same join the build uses.

Run (after building module 15 into OUT): .venv/bin/python -m scripts.china_ia_coda OUT
Writes OUT/module15_coda.mp4 (module 15 followed by the coda) and OUT/coda/voice.wav (silence), so
OUT/module15_coda.mp4 and OUT/coda/ can stand in for module 15 when joining the whole video.
"""
import subprocess
import sys
import wave
from pathlib import Path

from PIL import Image

from scripts.make_china_ia_boards import CODA, IMAGES
from studio import assemble, graphics
from studio.timeline import FPS

RATE = 48000


def still(src, png: Path) -> Path:
    if isinstance(src, dict):
        return graphics.overlay_card(src, png, on_photo=False, theme="blueprint")
    Image.open(IMAGES / "coda" / src).convert("RGB").resize((assemble.W, assemble.H), Image.LANCZOS).save(png)
    return png


def main(out: Path) -> None:
    work = out / "coda"
    work.mkdir(parents=True, exist_ok=True)
    clips, total = [], 0
    for name, src, seconds in CODA:
        frames = round(seconds * FPS)
        png = still(src, work / f"{name}.png")
        motion = "none" if isinstance(src, dict) else "zoom_in"
        clip = work / f"{name}.mp4"
        assemble._run(["-loop", "1", "-i", str(png), "-filter_complex",
                       f"[0:v]{assemble._ken_burns(motion, frames)},setsar=1[v]", "-map", "[v]",
                       "-frames:v", str(frames), "-r", str(FPS), "-c:v", "libx264", "-preset", "medium",
                       "-crf", "18", "-pix_fmt", "yuv420p", str(clip)])
        clips.append(clip)
        total += frames
    listing = work / "clips.txt"
    listing.write_text("".join(f"file '{c.resolve()}'\n" for c in clips))
    video = work / "video.mp4"
    assemble._run(["-f", "concat", "-safe", "0", "-i", str(listing), "-c", "copy", str(video)])
    voice = out / "module15" / "voice.wav"
    with wave.open(str(voice)) as w:
        rate, channels, width = w.getframerate(), w.getnchannels(), w.getsampwidth()
    with wave.open(str(work / "voice.wav"), "wb") as w:
        w.setnchannels(channels); w.setsampwidth(width); w.setframerate(rate)
        w.writeframes(b"\0" * (round(total / FPS * rate) * channels * width))
    assemble.join_modules([out / "module15.mp4", video], [voice, work / "voice.wav"], out / "module15_coda.mp4")
    print(f"{out / 'module15_coda.mp4'}: module 15 + {total / FPS:.1f} s of coda")


if __name__ == "__main__":
    main(Path(sys.argv[1]))

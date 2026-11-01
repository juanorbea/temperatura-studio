"""Join the module videos already built in an output folder and bring the mix to the channel's
loudness: -16 LUFS integrated, true peak at most -1 dBTP (two-pass ffmpeg loudnorm, linear).
A faint room tone (soft brown noise at ROOM_TONE_LUFS) runs under the whole mix, so the silent
shots (chapter cards, haiku cards, the coda) are never digital silence; under the voice it is inaudible.
Use it after rebuilding only some modules, e.g. for «La carrera del billón»:
  .venv/bin/python -m studio build examples/carrera-del-billon.md --module 6 --voice juan --out output/carrera-del-billon
  .venv/bin/python -m scripts.finish_video examples/carrera-del-billon.md output/carrera-del-billon
Writes OUT/STEM_full.mp4 (joined) and OUT/STEM_final.mp4 (normalised) and prints the measurement."""
import json
import re
import subprocess
import sys
from pathlib import Path

from studio import assemble
from studio.parse import parse_script

TARGET_I, TARGET_TP, TARGET_LRA = -16.0, -1.5, 11.0
ROOM_TONE_LUFS = -40.0  # the plan asks for -30 LUFS or lower in the silences
ROOM_TONE = "anoisesrc=color=brown:amplitude=0.5:seed=7:sample_rate=48000,highpass=f=80,lowpass=f=900"


def _loudnorm_json(stderr: str) -> dict:
    return json.loads(stderr[stderr.rindex("{"):stderr.rindex("}") + 1])


def measure(video: Path) -> dict:
    """Integrated loudness (LUFS) and true peak (dBTP) of a file's audio, by ffmpeg ebur128."""
    err = subprocess.run(["ffmpeg", "-hide_banner", "-nostats", "-i", str(video), "-map", "0:a",
                          "-af", "ebur128=peak=true", "-f", "null", "-"], capture_output=True, text=True).stderr
    summary = err[err.rindex("Summary:"):]
    return {"lufs": float(re.search(r"I:\s+(-?[\d.]+) LUFS", summary).group(1)),
            "dbtp": float(re.search(r"Peak:\s+(-?[\d.]+) dBFS", summary).group(1))}


def _lufs(args: list[str]) -> float:
    err = subprocess.run(["ffmpeg", "-hide_banner", "-nostats", *args, "-af", "ebur128", "-f", "null", "-"],
                         capture_output=True, text=True, check=True).stderr
    return float(re.search(r"I:\s+(-?[\d.]+) LUFS", err[err.rindex("Summary:"):]).group(1))


def add_room_tone(src: Path, out: Path) -> Path:
    """src with the room tone mixed under its audio (video copied, audio kept lossless as PCM)."""
    gain = ROOM_TONE_LUFS - _lufs(["-f", "lavfi", "-i", ROOM_TONE, "-t", "20"])
    graph = f"{ROOM_TONE},volume={gain:.2f}dB[rt];[0:a][rt]amix=inputs=2:duration=first:normalize=0[a]"
    subprocess.run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-y", "-i", str(src), "-filter_complex", graph,
                    "-map", "0:v", "-map", "[a]", "-c:v", "copy", "-c:a", "pcm_s16le", str(out)], check=True)
    return out


def normalise(src: Path, out: Path) -> Path:
    first = subprocess.run(["ffmpeg", "-hide_banner", "-nostats", "-i", str(src), "-map", "0:a", "-af",
                            f"loudnorm=I={TARGET_I}:TP={TARGET_TP}:LRA={TARGET_LRA}:print_format=json",
                            "-f", "null", "-"], capture_output=True, text=True, check=True).stderr
    m = _loudnorm_json(first)
    af = (f"loudnorm=I={TARGET_I}:TP={TARGET_TP}:LRA={TARGET_LRA}:measured_I={m['input_i']}:"
          f"measured_TP={m['input_tp']}:measured_LRA={m['input_lra']}:measured_thresh={m['input_thresh']}:"
          f"offset={m['target_offset']}:linear=true,aresample=48000")
    subprocess.run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-y", "-i", str(src), "-map", "0:v", "-map", "0:a",
                    "-c:v", "copy", "-af", af, "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart", str(out)],
                   check=True)
    return out


def main(script: Path, out_dir: Path) -> None:
    numbers = [m.number for m in parse_script(script.read_text(encoding="utf-8"))]
    joined = assemble.join_modules([out_dir / f"module{n}.mp4" for n in numbers],
                                   [out_dir / f"module{n}" / "voice.wav" for n in numbers],
                                   out_dir / f"{script.stem}_full.mp4")
    toned = add_room_tone(joined, out_dir / f"{script.stem}_full_tone.mkv")
    final = normalise(toned, out_dir / f"{script.stem}_final.mp4")
    toned.unlink()
    print(final, measure(final))


if __name__ == "__main__":
    main(Path(sys.argv[1]), Path(sys.argv[2]))

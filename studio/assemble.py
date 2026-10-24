"""Render each shot to a clip with ffmpeg, then join clips and add the voice."""
import subprocess
from pathlib import Path

from studio.timeline import FPS, Timing

W, H = 1920, 1080
ZOOM = 0.08  # Ken Burns: how much the image grows or travels over one shot
MOTIONS = ["zoom_in", "pan_right", "zoom_out", "pan_left"]


def _run(args: list[str]) -> None:
    subprocess.run(["ffmpeg", "-v", "error", "-y", *args], check=True)


def _ken_burns(motion: str, frames: int) -> str:
    """zoompan filter for a slow zoom or pan over exactly `frames` frames."""
    t = f"(on/{max(frames - 1, 1)})"  # goes 0 -> 1 across the shot
    center_x, center_y = "(iw-iw/zoom)/2", "(ih-ih/zoom)/2"
    z, x, y = {
        "zoom_in": (f"1+{ZOOM}*{t}", center_x, center_y),
        "zoom_out": (f"1+{ZOOM}-{ZOOM}*{t}", center_x, center_y),
        "pan_right": (f"1+{ZOOM}", f"(iw-iw/zoom)*{t}", center_y),
        "pan_left": (f"1+{ZOOM}", f"(iw-iw/zoom)*(1-{t})", center_y),
        "none": ("1", "0", "0"),
    }[motion]
    # Upscale first so the 1-pixel steps of zoompan are not visible.
    return (f"scale={W * 2}:{H * 2}:flags=lanczos,"
            f"zoompan=z='{z}':x='{x}':y='{y}':d={frames}:s={W}x{H}:fps={FPS}")


def render_clip(timing: Timing, background: Path, overlay: Path | None, motion: str, out: Path) -> Path:
    frames = timing.frames
    filters = f"[0:v]{_ken_burns(motion, frames)},setsar=1[bg]"
    inputs = ["-i", str(background)]
    if overlay:
        inputs += ["-i", str(overlay)]
        filters += ";[bg][1:v]overlay=0:0[v]"
    else:
        filters += ";[bg]null[v]"
    _run([*inputs, "-filter_complex", filters, "-map", "[v]", "-frames:v", str(frames),
          "-r", str(FPS), "-c:v", "libx264", "-preset", "medium", "-crf", "18",
          "-pix_fmt", "yuv420p", str(out)])
    return out


def join(clips: list[Path], audio: Path, out: Path) -> Path:
    listing = out.with_suffix(".txt")
    listing.write_text("".join(f"file '{c.resolve()}'\n" for c in clips))
    _run(["-f", "concat", "-safe", "0", "-i", str(listing), "-i", str(audio),
          "-map", "0:v", "-map", "1:a", "-c:v", "copy", "-c:a", "aac", "-b:a", "192k",
          "-movflags", "+faststart", str(out)])
    listing.unlink()
    return out

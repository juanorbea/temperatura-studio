"""Own-voice mode: time the video to a recording of the narration.

clean the recording -> transcribe it locally (faster-whisper) -> find pauses
-> align the words to the shots (studio.align).
"""
import hashlib
import json
import subprocess
from pathlib import Path

import numpy as np

from studio.align import ShotAlignment, Word, align
from studio.storyboard import Storyboard
from studio.timeline import RATE, Timing, snap_and_write

WHISPER_MODEL = "medium"   # "small" is ~3x faster and a bit less accurate
FRAME = 0.01               # seconds per loudness frame when looking for pauses
MIN_PAUSE = 0.15           # shortest gap that counts as a pause


def clean(src: Path, wav_out: Path) -> bytes:
    """48 kHz mono, gentle high-pass, loudness to about -16 LUFS. Returns 16-bit PCM."""
    subprocess.run(
        ["ffmpeg", "-v", "error", "-y", "-i", str(src),
         "-af", "highpass=f=70,loudnorm=I=-16:TP=-1.5:LRA=11",
         "-ar", str(RATE), "-ac", "1", "-c:a", "pcm_s16le", str(wav_out)],
        check=True)
    return subprocess.run(
        ["ffmpeg", "-v", "error", "-i", str(wav_out), "-f", "s16le", "-"],
        check=True, capture_output=True).stdout


def transcribe(src: Path, cache_dir: Path, model_size: str = WHISPER_MODEL) -> list[Word]:
    """Spanish words with start/end times, cached by recording content and model."""
    cache_dir.mkdir(parents=True, exist_ok=True)
    digest = hashlib.sha1(Path(src).read_bytes()).hexdigest()[:16]
    cached = cache_dir / f"{digest}-{model_size}.json"
    if not cached.exists():
        from faster_whisper import WhisperModel  # slow import, only when needed

        # Decode with ffmpeg ourselves: 16 kHz mono float, what Whisper expects.
        audio = np.frombuffer(subprocess.run(
            ["ffmpeg", "-v", "error", "-i", str(src), "-f", "f32le", "-ac", "1", "-ar", "16000", "-"],
            check=True, capture_output=True).stdout, np.float32)
        model = WhisperModel(model_size, device="cpu", compute_type="int8")
        segments, _ = model.transcribe(audio, language="es", word_timestamps=True, vad_filter=True)
        words = [{"text": w.word.strip(), "start": w.start, "end": w.end}
                 for seg in segments for w in seg.words]
        cached.write_text(json.dumps(words, ensure_ascii=False, indent=1))
    return [Word(**w) for w in json.loads(cached.read_text())]


def loudness_db(pcm: bytes) -> np.ndarray:
    """Loudness in dB of each FRAME-long slice of 16-bit PCM at RATE."""
    samples = np.frombuffer(pcm, np.int16).astype(np.float32) / 32768
    n = int(RATE * FRAME)
    frames = samples[: len(samples) // n * n].reshape(-1, n)
    return 20 * np.log10(np.sqrt((frames ** 2).mean(axis=1)) + 1e-6)


def pause_threshold(db: np.ndarray) -> float:
    """Halfway (in dB) between the room noise and the voice, set from this recording."""
    floor, voice = np.percentile(db, 10), np.percentile(db, 90)
    return float(floor + 0.5 * (voice - floor))


def find_pauses(pcm: bytes) -> list[tuple[float, float]]:
    db = loudness_db(pcm)
    quiet = db < pause_threshold(db)
    pauses, start = [], None
    for i, q in enumerate(np.append(quiet, False)):
        if q and start is None:
            start = i
        elif not q and start is not None:
            if (i - start) * FRAME >= MIN_PAUSE:
                pauses.append((start * FRAME, i * FRAME))
            start = None
    return pauses


def timings_from_recording(board: Storyboard, src: Path, cache: Path, wav_out: Path,
                           model_size: str = WHISPER_MODEL) -> tuple[list[Timing], list[ShotAlignment]]:
    """Clean the recording, align it to the shots, write the soundtrack to wav_out."""
    pcm = clean(src, wav_out.with_name("recording_clean.wav"))
    audio_end = len(pcm) / 2 / RATE
    heard = transcribe(src, cache / "transcripts", model_size)
    shots = align([s.text for s in board.shots], heard, find_pauses(pcm), audio_end)
    timings = snap_and_write(board.shots, [a.end for a in shots], pcm, wav_out)
    return timings, shots

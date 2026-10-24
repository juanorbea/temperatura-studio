"""Turn storyboard shots + voice into exact shot timings and one audio track.

Narration is synthesized one paragraph at a time (natural intonation), then
each shot's start and end are taken from the TTS word timings. Cuts land on
video frame boundaries, and the audio track is built to the exact same length.
"""
import re
import subprocess
import wave
from dataclasses import dataclass
from pathlib import Path

from studio import voice
from studio.parse import Module
from studio.storyboard import Shot, Storyboard

FPS = 30
RATE = 48000                  # audio samples per second
SAMPLES_PER_FRAME = RATE // FPS
PARAGRAPH_GAP = 0.6           # seconds of silence between paragraphs


@dataclass
class Timing:
    shot: Shot
    start_frame: int
    frames: int

    @property
    def seconds(self) -> float:
        return self.frames / FPS


def _words(text: str) -> list[str]:
    """Spoken tokens: whitespace-split, ignoring tokens with no letter or digit."""
    return [t for t in text.split() if re.search(r"\w", t)]


def _group_by_paragraph(shots: list[Shot], module: Module) -> list[tuple[str, list[Shot]]]:
    groups, pending = [], list(shots)
    for paragraph in module.narration.split("\n\n"):
        members, text = [], ""
        while pending and len(text) < len(paragraph):
            members.append(pending.pop(0))
            text = " ".join(s.text.strip() for s in members)
        if text != paragraph:
            raise ValueError(f"shots do not line up with this paragraph: {paragraph[:60]!r}")
        groups.append((paragraph, members))
    return groups


def _decode(mp3: Path) -> bytes:
    """mp3 -> raw 16-bit mono PCM at RATE."""
    return subprocess.run(
        ["ffmpeg", "-v", "error", "-i", str(mp3), "-f", "s16le", "-ac", "1", "-ar", str(RATE), "-"],
        check=True, capture_output=True,
    ).stdout


def _silence(seconds: float) -> bytes:
    return b"\x00\x00" * int(round(seconds * RATE))


def build(board: Storyboard, module: Module, cache: Path, wav_out: Path) -> list[Timing]:
    """Synthesize the voice, write the full audio track to wav_out, return shot timings."""
    pcm = bytearray()
    ends = []  # end time in seconds of each shot, in order
    groups = _group_by_paragraph(board.shots, module)
    for g, (paragraph, members) in enumerate(groups):
        mp3, words = voice.synthesize(paragraph, board.voice, cache)
        expected = _words(paragraph)
        if len(words) != len(expected):
            raise RuntimeError(f"TTS returned {len(words)} words, expected {len(expected)}: {paragraph[:60]!r}")
        first = members[0]
        pcm += _silence(first.lead_in)
        offset = len(pcm) / 2 / RATE  # where this paragraph's audio starts
        audio = _decode(mp3)
        pcm += audio
        audio_len = len(audio) / 2 / RATE

        index = 0
        for k, shot in enumerate(members):
            index += len(_words(shot.text))
            if k < len(members) - 1:
                # cut halfway through the pause before the next shot's first word
                ends.append(offset + (words[index - 1].end + words[index].start) / 2)
        last = members[-1]
        pcm += _silence(last.tail)
        if g < len(groups) - 1:
            pcm += _silence(PARAGRAPH_GAP)
        ends.append(len(pcm) / 2 / RATE)
        if offset + audio_len > ends[-1] + 1e-6:
            raise RuntimeError("paragraph audio longer than its shots")

    return snap_and_write(board.shots, ends, bytes(pcm), wav_out)


def snap_and_write(shots: list[Shot], ends: list[float], pcm: bytes, wav_out: Path) -> list[Timing]:
    """Snap shot end times to frames and write the audio exactly as long as the video.

    pcm is 16-bit mono audio at RATE. Returns one Timing per shot.
    """
    timings, start = [], 0
    for shot, end in zip(shots, ends):
        end_frame = round(end * FPS)
        if end_frame <= start:
            raise RuntimeError(f"{shot.id}: shot would have no frames (ends at {end:.2f}s)")
        timings.append(Timing(shot, start, end_frame - start))
        start = end_frame
    total_bytes = start * SAMPLES_PER_FRAME * 2
    pcm = pcm[:total_bytes] + b"\x00" * max(0, total_bytes - len(pcm))

    with wave.open(str(wav_out), "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(RATE)
        w.writeframes(pcm)
    return timings

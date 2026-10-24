"""Spanish text-to-speech with edge-tts (free Microsoft neural voices).

Each call returns an mp3 and word timings, cached on disk by voice + text.
"""
import asyncio
import hashlib
import json
from dataclasses import dataclass
from pathlib import Path

import edge_tts


@dataclass
class Word:
    text: str
    start: float  # seconds from the start of the clip
    end: float


async def _synthesize(text: str, voice: str, mp3: Path) -> list[Word]:
    words = []
    comm = edge_tts.Communicate(text, voice, boundary="WordBoundary")
    with open(mp3, "wb") as f:
        async for chunk in comm.stream():
            if chunk["type"] == "audio":
                f.write(chunk["data"])
            elif chunk["type"] == "WordBoundary":
                start = chunk["offset"] / 1e7  # edge-tts uses 100 ns ticks
                words.append(Word(chunk["text"], start, start + chunk["duration"] / 1e7))
    return words


def synthesize(text: str, voice: str, cache_dir: Path) -> tuple[Path, list[Word]]:
    cache_dir.mkdir(parents=True, exist_ok=True)
    key = hashlib.sha1(f"{voice}\n{text}".encode()).hexdigest()[:16]
    mp3, meta = cache_dir / f"{key}.mp3", cache_dir / f"{key}.json"
    if not (mp3.exists() and meta.exists()):
        words = asyncio.run(_synthesize(text, voice, mp3))
        meta.write_text(json.dumps([w.__dict__ for w in words], ensure_ascii=False, indent=1))
    return mp3, [Word(**w) for w in json.loads(meta.read_text())]

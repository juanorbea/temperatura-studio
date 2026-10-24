"""Narrate with a cloned voice (F5-TTS) from a saved voice profile.

A profile is a folder voices/NAME/ with:
  profile.yaml          model and generation settings
  ref.txt               the exact words spoken in the reference clip
  pronunciations.yaml   synthesis-only lexicon (see studio/textprep.py)
  ref.wav               the reference clip itself; personal, kept out of git

Narration is generated one sentence at a time (long sentences are split at commas),
and never across a shot boundary, so every cut falls exactly in a pause we put there.
Each piece is checked with Whisper; if words are wrong or the end is missing it is
generated again with another seed (up to 3) and the best take is kept.
Every take is cached under cache/voice/ by a hash of everything that shapes it.
"""
import hashlib
import json
import os
import re
import subprocess
import sys
import time
from dataclasses import dataclass
from difflib import SequenceMatcher
from pathlib import Path

import numpy as np
import yaml

from studio.align import normalize
from studio.parse import Module, split_sentences
from studio.storyboard import Shot, Storyboard
from studio.textprep import Lexicon, heard_text, load_lexicon, numbers_to_words, voice_text

RATE = 48000
SENTENCE_GAP, PARAGRAPH_GAP, CHUNK_GAP = 0.35, 0.7, 0.15
GOOD_WER = 0.10
SEEDS = (0, 1, 2)
DEFAULT_F5_PYTHON = Path(".venv-f5/bin/python")


class VoiceError(Exception):
    pass


@dataclass
class Profile:
    name: str
    folder: Path
    ref_audio: Path
    ref_text: str
    checkpoint: str
    lexicon: Lexicon
    settings: dict

    def fingerprint(self) -> str:
        """Changes whenever anything that shapes the generated audio changes."""
        h = hashlib.sha256()
        h.update(self.ref_audio.read_bytes())
        h.update(json.dumps([self.ref_text, self.checkpoint, self.settings], sort_keys=True).encode())
        return h.hexdigest()[:16]


def load_profile(name: str, voices: Path = Path("voices")) -> Profile:
    folder = voices / name
    if not (folder / "profile.yaml").exists():
        raise VoiceError(f"no voice profile {name!r}: {folder}/profile.yaml not found")
    data = yaml.safe_load((folder / "profile.yaml").read_text(encoding="utf-8"))
    ref_audio = Path(os.path.expanduser(data["reference"]["audio"]))
    if not ref_audio.is_absolute():
        ref_audio = folder / ref_audio
    if not ref_audio.exists():
        raise VoiceError(
            f"reference audio for voice {name!r} not found at {ref_audio}.\n"
            "It is a personal recording and is not in git: copy the reference clip there "
            "(see README, 'Cloned voice').")
    ref_text = (folder / data["reference"]["text"]).read_text(encoding="utf-8").strip()
    lexicon = load_lexicon(folder / data["lexicon"])
    return Profile(name, folder, ref_audio, ref_text, data["checkpoint"], lexicon, data["generation"])


def cache_key(fingerprint: str, text: str, seconds: float, seed: int) -> str:
    """Same profile + same voice text + same length + same seed = same audio."""
    raw = json.dumps([fingerprint, text, round(seconds, 2), seed], ensure_ascii=False)
    return hashlib.sha256(raw.encode()).hexdigest()[:20]


def estimate_seconds(text: str, settings: dict) -> float:
    """Length to ask F5 for: letters at the speaker's pace plus a little room to finish."""
    letters = len(re.findall(r"[^\W\d_]", text))
    return max(1.0, letters / settings["letters_per_second"] + settings["pad_seconds"])


def split_chunks(sentence: str, max_chars: int) -> list[str]:
    """Split a long sentence at commas, colons or semicolons into pieces of at most max_chars."""
    if len(sentence) <= max_chars:
        return [sentence]
    chunks, current = [], ""
    for part in re.split(r"(?<=[,:;])\s+", sentence):
        if current and len(current) + 1 + len(part) > max_chars:
            chunks.append(current)
            current = part
        else:
            current = f"{current} {part}".strip()
    return chunks + [current]


@dataclass
class Piece:
    shot: int          # index of the shot this piece belongs to
    text: str          # script text (for reports)
    gap: float         # silence after it


def pieces_for_shots(shots: list[Shot], paragraph_ends: set[int], max_chars: int) -> list[Piece]:
    """Cut each shot's text into sentences and chunks; the pause after each depends on what ends there."""
    out = []
    for k, shot in enumerate(shots):
        sentences = split_sentences(shot.text)
        for s, sentence in enumerate(sentences):
            chunks = split_chunks(sentence, max_chars)
            for c, chunk in enumerate(chunks):
                last_in_shot = s == len(sentences) - 1 and c == len(chunks) - 1
                if c < len(chunks) - 1:
                    gap = CHUNK_GAP
                elif last_in_shot and k in paragraph_ends:
                    gap = PARAGRAPH_GAP
                elif re.search(r"[.?!:]['\"»”]?$", chunk):
                    gap = SENTENCE_GAP
                else:
                    gap = CHUNK_GAP  # shot ends mid-sentence
                out.append(Piece(k, chunk, gap))
    return out


def word_error_rate(expected: str, heard: str) -> tuple[float, bool]:
    """Word error rate of what Whisper heard, and whether the last word was heard at the end."""
    ref, hyp = normalize(expected), normalize(numbers_to_words(heard))
    if not ref:
        return 0.0, True
    ops = SequenceMatcher(None, ref, hyp, autojunk=False).get_opcodes()
    errors = sum(max(i2 - i1, j2 - j1) for op, i1, i2, j1, j2 in ops if op != "equal")
    return errors / len(ref), bool(hyp) and ref[-1] in hyp[-3:]


class _Worker:
    """The F5 model in its own virtualenv, started only if something is not cached yet."""

    def __init__(self, profile: Profile, device: str, log: Path):
        python = Path(os.environ.get("STUDIO_F5_PYTHON", DEFAULT_F5_PYTHON))
        if not python.exists():
            raise VoiceError(f"F5 virtualenv not found ({python}); see README, 'Cloned voice', "
                             "or set STUDIO_F5_PYTHON")
        script = Path(__file__).with_name("f5_worker.py")
        self.log = open(log, "a")
        self.proc = subprocess.Popen([str(python), str(script)], stdin=subprocess.PIPE,
                                     stdout=subprocess.PIPE, stderr=self.log, text=True)
        s = profile.settings
        self._send({"checkpoint": profile.checkpoint, "ref_audio": str(profile.ref_audio),
                    "ref_text": profile.ref_text, "device": device, "nfe_step": s["nfe_step"],
                    "cfg_strength": s["cfg_strength"], "sway_sampling_coef": s["sway_sampling_coef"]})

    def _send(self, msg: dict) -> dict:
        self.proc.stdin.write(json.dumps(msg, ensure_ascii=False) + "\n")
        self.proc.stdin.flush()
        line = self.proc.stdout.readline()
        if not line:
            raise VoiceError(f"F5 worker stopped; see {self.log.name}")
        return json.loads(line)

    def generate(self, text: str, seconds: float, seed: int, out: Path) -> dict:
        return self._send({"text": text, "seconds": seconds, "seed": seed, "out": str(out)})

    def close(self) -> None:
        self.proc.stdin.close()
        self.proc.wait()
        self.log.close()


class _Checker:
    """Whisper, made repeatable (no random retries), loaded on first use."""

    def __init__(self, model_size: str):
        self.model_size, self.model = model_size, None

    def heard(self, wav: Path) -> str:
        import ctranslate2
        from faster_whisper import WhisperModel
        from studio.recording import decode_16k
        if self.model is None:
            self.model = WhisperModel(self.model_size, device="cpu", compute_type="int8")
        ctranslate2.set_random_seed(0)
        segments, _ = self.model.transcribe(decode_16k(wav), language="es", beam_size=5,
                                            condition_on_previous_text=False)
        return " ".join(s.text.strip() for s in segments)


class Narrator:
    def __init__(self, profile: Profile, cache: Path, device: str = "cpu", whisper_model: str = "medium"):
        self.profile, self.cache, self.device = profile, cache, device
        self.cache.mkdir(parents=True, exist_ok=True)
        self.fingerprint = profile.fingerprint()
        self.checker = _Checker(whisper_model)
        self.worker = None
        self.generated = self.reused = 0
        self.gen_seconds = 0.0

    def take(self, text: str) -> dict:
        """Best take for one piece of narration: cached, or generated and checked."""
        lex, s = self.profile.lexicon, self.profile.settings
        say, expect = voice_text(text, lex), heard_text(text, lex)
        seconds = estimate_seconds(say, s)
        takes = []
        for seed in SEEDS:
            key = cache_key(self.fingerprint, say, seconds, seed)
            wav, meta = self.cache / f"{key}.wav", self.cache / f"{key}.json"
            if wav.exists() and meta.exists():
                take = json.loads(meta.read_text(encoding="utf-8"))
                if take["expect"] != expect:  # lexicon changed what should be heard: re-score
                    take["expect"] = expect
                    take["wer"], take["tail_ok"] = word_error_rate(expect, take["heard"])
                    take["wer"] = round(take["wer"], 3)
                self.reused += 1
            else:
                if self.worker is None:
                    self.worker = _Worker(self.profile, self.device, self.cache / "f5_worker.log")
                result = self.worker.generate(say, seconds, seed, wav)
                heard = self.checker.heard(wav)
                wer, tail_ok = word_error_rate(expect, heard)
                take = {"text": text, "say": say, "expect": expect, "seed": seed, "heard": heard,
                        "wer": round(wer, 3), "tail_ok": tail_ok, "seconds": result["seconds"],
                        "took": result["took"]}
                meta.write_text(json.dumps(take, ensure_ascii=False, indent=1), encoding="utf-8")
                self.generated += 1
                self.gen_seconds += result["took"]
                print(f"  generated seed {seed} in {result['took']:5.1f}s, wer {wer:.2f}"
                      f"{'' if tail_ok else ' END MISSING'}: {text[:60]}", flush=True)
            take["wav"] = str(wav)
            takes.append(take)
            if take["tail_ok"] and take["wer"] <= GOOD_WER:
                break
        return min(takes, key=lambda t: (not t["tail_ok"], t["wer"], t["seed"]))

    def close(self) -> None:
        if self.worker:
            self.worker.close()


def _pcm(wav: str) -> np.ndarray:
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", wav, "-f", "s16le", "-ac", "1", "-ar", str(RATE), "-"],
                         check=True, capture_output=True).stdout
    return np.frombuffer(raw, np.int16)


def loudnorm(pcm: np.ndarray, work: Path) -> np.ndarray:
    """Two-pass loudness normalisation to -16 LUFS (true peak -1.5 dB); length unchanged."""
    raw = work / "narration_raw.wav"
    write_wav(pcm, raw)
    target = "I=-16:TP=-1.5:LRA=11"
    measure = subprocess.run(["ffmpeg", "-hide_banner", "-i", str(raw), "-af", f"loudnorm={target}:print_format=json",
                              "-f", "null", "-"], capture_output=True, text=True, check=True).stderr
    start = measure.rindex("{")
    m = json.loads(measure[start:measure.index("}", start) + 1])  # ffmpeg may log more after it
    af = (f"loudnorm={target}:measured_I={m['input_i']}:measured_TP={m['input_tp']}:"
          f"measured_LRA={m['input_lra']}:measured_thresh={m['input_thresh']}:"
          f"offset={m['target_offset']}:linear=true")
    out = subprocess.run(["ffmpeg", "-v", "error", "-i", str(raw), "-af", af, "-ar", str(RATE), "-ac", "1",
                          "-f", "s16le", "-"], check=True, capture_output=True).stdout
    out = np.frombuffer(out, np.int16)[: len(pcm)]
    return np.pad(out, (0, len(pcm) - len(out)))


def write_wav(pcm: np.ndarray, path: Path) -> None:
    import wave
    with wave.open(str(path), "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(RATE)
        w.writeframes(pcm.astype(np.int16).tobytes())


def narrate_shots(narrator: Narrator, shots: list[Shot], paragraph_ends: set[int],
                  work: Path) -> tuple[np.ndarray, list[float], list[dict]]:
    """Whole narration as 48 kHz PCM, each shot's end time, and a per-piece report."""
    pieces = pieces_for_shots(shots, paragraph_ends, narrator.profile.settings["max_chunk_chars"])
    audio, ends, report, pos = [], [], [], 0
    silence = lambda sec: np.zeros(int(round(sec * RATE)), np.int16)
    start = time.time()
    for k, shot in enumerate(shots):
        audio.append(silence(shot.lead_in)); pos += len(audio[-1])
        mine = [p for p in pieces if p.shot == k]
        for i, piece in enumerate(mine):
            take = narrator.take(piece.text)
            pcm = _pcm(take["wav"])
            report.append({"shot": shot.id, "start": round(pos / RATE, 3), **{
                key: take[key] for key in ("text", "say", "seed", "heard", "wer", "tail_ok")}})
            audio.append(pcm); pos += len(pcm)
            if i < len(mine) - 1:
                audio.append(silence(piece.gap)); pos += len(audio[-1])
        gap = mine[-1].gap if mine else 0.0
        audio.append(silence(shot.tail + gap / 2)); pos += len(audio[-1])
        ends.append(pos / RATE)                       # cut halfway through the pause
        audio.append(silence(gap / 2)); pos += len(audio[-1])
    print(f"voice: {narrator.generated} takes generated ({narrator.gen_seconds:.0f}s), "
          f"{narrator.reused} reused from cache, {time.time() - start:.0f}s", flush=True)
    pcm = np.concatenate(audio)
    ends[-1] = len(pcm) / RATE
    return loudnorm(pcm, work), ends, report


def paragraph_ends(shots: list[Shot], module: Module) -> set[int]:
    """Indexes of shots whose text finishes a paragraph of the narration."""
    ends, done = set(), ""
    paragraphs = [" ".join(p.split()) for p in module.narration.split("\n\n")]
    targets, joined = set(), ""
    for p in paragraphs:
        joined = f"{joined} {p}".strip()
        targets.add(len(joined))
    for k, shot in enumerate(shots):
        done = f"{done} {shot.text.strip()}".strip()
        if len(done) in targets:
            ends.add(k)
    return ends


def timings_from_voice(board: Storyboard, module: Module, profile: Profile, cache: Path, wav_out: Path,
                       device: str = "cpu", whisper_model: str = "medium"):
    """Narrate the storyboard with the cloned voice; write the soundtrack; return timings and report."""
    from studio.timeline import snap_and_write
    narrator = Narrator(profile, cache, device, whisper_model)
    try:
        pcm, ends, report = narrate_shots(narrator, board.shots, paragraph_ends(board.shots, module),
                                          wav_out.parent)
    finally:
        narrator.close()
    timings = snap_and_write(board.shots, ends, pcm.tobytes(), wav_out)
    return timings, report

"""Match a transcribed recording to storyboard shots and choose the cuts.

Pure functions, no audio: input is the shot texts, the recognised words with
times, and the pauses found in the recording.
"""
import re
import unicodedata
from dataclasses import dataclass
from difflib import SequenceMatcher

WINDOW_SLACK = 0.3   # seconds: recognised word times are not exact
MIN_BLOCK = 2        # ignore single-word matches, they are often chance hits (de, la, y)
FLAG_MISSING = 3     # warn when a shot has this many script words not heard...
FLAG_EXTRA = 3       # ...or this many heard words not in the script
FLAG_RATIO = 0.7     # ...or matches less than this share of its words
FAIL_RATIO = 0.5     # below this for the whole module, it is probably the wrong recording


@dataclass
class Word:
    text: str
    start: float
    end: float


@dataclass
class ShotAlignment:
    start: float
    end: float
    words: int        # words in the shot's script text
    matched: int      # of those, heard in the recording
    extra: int        # heard words in this shot that are not in the script
    cut_in_pause: bool  # the cut at the start of this shot is inside a pause

    @property
    def ratio(self) -> float:
        return self.matched / self.words if self.words else 1.0

    @property
    def flagged(self) -> bool:
        return (self.words - self.matched >= FLAG_MISSING or self.extra >= FLAG_EXTRA
                or self.ratio < FLAG_RATIO)


class AlignmentError(Exception):
    pass


def normalize(text: str) -> list[str]:
    """Lowercase, drop accents and punctuation, split into tokens."""
    text = unicodedata.normalize("NFKD", text.lower())
    text = "".join(c for c in text if not unicodedata.combining(c))
    return re.findall(r"[a-z0-9]+", text)


def _split_words(words: list[Word]) -> list[Word]:
    """One recognised word may hold several tokens ("2025-2060"); share its time."""
    out = []
    for w in words:
        tokens = normalize(w.text)
        step = (w.end - w.start) / max(len(tokens), 1)
        out += [Word(t, w.start + i * step, w.start + (i + 1) * step) for i, t in enumerate(tokens)]
    return out


def _script_times(n_ref: int, match: dict[int, int], hyp: list[Word], audio_end: float):
    """Start/end time for every script token; unheard tokens are interpolated."""
    starts, ends = [0.0] * n_ref, [0.0] * n_ref
    known = sorted(match)
    for i in range(n_ref):
        if i in match:
            starts[i], ends[i] = hyp[match[i]].start, hyp[match[i]].end
            continue
        prev = max((k for k in known if k < i), default=None)
        nxt = min((k for k in known if k > i), default=None)
        t0 = hyp[match[prev]].end if prev is not None else 0.0
        t1 = hyp[match[nxt]].start if nxt is not None else audio_end
        p = prev if prev is not None else -1
        n = nxt if nxt is not None else n_ref
        starts[i] = ends[i] = t0 + (t1 - t0) * (i - p) / (n - p)
    return starts, ends


def _choose_cut(after: float, before: float, pauses: list[tuple[float, float]]):
    """Cut between the end of one shot's speech and the start of the next.

    Picks the pause nearest to the next shot's first word inside that window
    and cuts in its middle. Returns (time, in_pause).
    """
    lo, hi = min(after, before) - WINDOW_SLACK, max(after, before) + WINDOW_SLACK
    inside = [(a, b) for a, b in pauses if b > lo and a < hi]
    if not inside:
        return (after + before) / 2, False
    def distance(p):
        a, b = p
        return 0.0 if a <= before <= b else min(abs(a - before), abs(b - before))
    a, b = min(inside, key=distance)
    a, b = max(a, lo), min(b, hi)
    return (a + b) / 2, True


def align(shot_texts: list[str], heard: list[Word], pauses: list[tuple[float, float]],
          audio_end: float) -> list[ShotAlignment]:
    ref, owner = [], []
    for k, text in enumerate(shot_texts):
        tokens = normalize(text)
        ref += tokens
        owner += [k] * len(tokens)
    hyp = _split_words(heard)

    matcher = SequenceMatcher(None, ref, [w.text for w in hyp], autojunk=False)
    match = {}
    for block in matcher.get_matching_blocks():
        if block.size >= MIN_BLOCK:
            match.update({block.a + i: block.b + i for i in range(block.size)})
    if len(match) < FAIL_RATIO * len(ref):
        raise AlignmentError(
            f"only {len(match)} of {len(ref)} script words were heard in the recording; "
            "is it the right module?")

    starts, ends = _script_times(len(ref), match, hyp, audio_end)
    first = [owner.index(k) for k in range(len(shot_texts))]
    last = [len(owner) - 1 - owner[::-1].index(k) for k in range(len(shot_texts))]

    cuts, in_pause = [0.0], [True]
    for k in range(1, len(shot_texts)):
        t, ok = _choose_cut(ends[last[k - 1]], starts[first[k]], pauses)
        cuts.append(max(t, cuts[-1] + 0.2))  # keep every shot at least a little long
        in_pause.append(ok)
    cuts.append(audio_end)

    unmatched = set(range(len(hyp))) - set(match.values())
    result = []
    for k in range(len(shot_texts)):
        lo, hi = cuts[k], cuts[k + 1]
        extra = sum(1 for j in unmatched if lo <= hyp[j].start < hi)
        matched = sum(1 for i in range(first[k], last[k] + 1) if i in match)
        result.append(ShotAlignment(lo, hi, last[k] - first[k] + 1, matched, extra, in_pause[k]))
    return result

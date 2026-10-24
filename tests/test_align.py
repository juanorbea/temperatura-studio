"""Alignment of a recording to shots, with made-up word timings (no audio)."""
import pytest

from studio.align import AlignmentError, Word, align

SHOTS = [
    "Hola a todos y bienvenidos.",
    "Hoy hablamos de la gobernanza global de la inteligencia artificial,",
    "y de por qué los tratados tardan décadas en llegar.",
    "Acompáñame a desglosarlo.",
]


def speak(pieces, word_time=0.3, start=1.0):
    """Fake a recording. pieces: list of (text, pause after in seconds).

    Returns (words, pauses, audio_end) like the transcriber and pause finder would.
    """
    words, pauses, t = [], [(0.0, start)], start
    for text, pause in pieces:
        for w in text.split():
            words.append(Word(w, t, t + word_time))
            t += word_time
        if pause:
            pauses.append((t, t + pause))
            t += pause
    return words, pauses, t


def pause_containing(pauses, t):
    return next((p for p in pauses if p[0] <= t <= p[1]), None)


def test_clean_reading_cuts_in_the_middle_of_each_pause():
    words, pauses, end = speak([(s, 0.8) for s in SHOTS])
    shots = align(SHOTS, words, pauses, end)

    assert shots[0].start == 0.0
    assert shots[-1].end == end
    for prev, nxt in zip(shots, shots[1:]):
        assert prev.end == nxt.start
        a, b = pause_containing(pauses, nxt.start)
        assert nxt.start == pytest.approx((a + b) / 2)
        assert nxt.cut_in_pause
    assert not any(s.flagged for s in shots)
    assert all(s.ratio == 1.0 for s in shots)


def test_long_pauses_and_slow_reading_do_not_move_cuts_out_of_pauses():
    pieces = [(SHOTS[0], 2.0), (SHOTS[1], 0.4), (SHOTS[2], 1.5), (SHOTS[3], 0.5)]
    words, pauses, end = speak(pieces, word_time=0.45, start=3.0)
    shots = align(SHOTS, words, pauses, end)
    assert all(pause_containing(pauses, s.start) for s in shots[1:])


def test_skipped_phrase_is_flagged_but_cuts_stay_right():
    pieces = [(SHOTS[0], 0.8),
              ("Hoy hablamos de la inteligencia artificial,", 0.8),  # skips "gobernanza global de la"
              (SHOTS[2], 0.8), (SHOTS[3], 0.8)]
    words, pauses, end = speak(pieces)
    shots = align(SHOTS, words, pauses, end)

    assert [s.flagged for s in shots] == [False, True, False, False]
    assert shots[1].words - shots[1].matched == 4
    assert all(s.cut_in_pause for s in shots[1:])


def test_ad_lib_is_counted_as_extra_words_and_flagged():
    pieces = [(SHOTS[0], 0.8), (SHOTS[1], 0.8),
              ("y de por qué los tratados", 0.4),
              ("bueno es una pregunta muy interesante", 0.4),      # ad-lib inside shot 3
              ("tardan décadas en llegar.", 0.8), (SHOTS[3], 0.8)]
    words, pauses, end = speak(pieces)
    shots = align(SHOTS, words, pauses, end)

    assert shots[2].extra == 6
    assert shots[2].flagged
    assert not shots[1].flagged and not shots[3].flagged


def test_one_misheard_word_is_tolerated():
    pieces = [(SHOTS[0], 0.8),
              ("Hoy hablamos de la gobernanza global de la inteligencia artística,", 0.8),
              (SHOTS[2], 0.8), (SHOTS[3], 0.8)]
    words, pauses, end = speak(pieces)
    shots = align(SHOTS, words, pauses, end)
    assert not any(s.flagged for s in shots)


def test_accents_case_and_punctuation_do_not_matter():
    pieces = [("HOLA a todos, y bienvenidos", 0.8), (SHOTS[1].upper(), 0.8),
              ("y de por que los tratados tardan decadas en llegar", 0.8), ("acompaname a desglosarlo", 0.8)]
    words, pauses, end = speak(pieces)
    shots = align(SHOTS, words, pauses, end)
    assert all(s.ratio == 1.0 for s in shots)


def test_no_pause_between_shots_cuts_between_the_words():
    pieces = [(SHOTS[0], 0.8), (SHOTS[1] + " " + SHOTS[2], 0.8), (SHOTS[3], 0.8)]
    words, pauses, end = speak(pieces)
    shots = align(SHOTS, words, pauses, end)

    assert not shots[2].cut_in_pause
    last_of_shot2 = next(w for w in words if w.text == "artificial,")
    assert shots[2].start == pytest.approx(last_of_shot2.end)


def test_wrong_recording_fails():
    words, pauses, end = speak([("esto no tiene nada que ver con el guion de hoy", 0.5)] * 3)
    with pytest.raises(AlignmentError):
        align(SHOTS, words, pauses, end)

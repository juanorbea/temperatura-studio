"""Cloned-voice cache keys and how narration is cut into pieces (no model needed)."""
from studio.clone import CHUNK_GAP, PARAGRAPH_GAP, SENTENCE_GAP, cache_key, estimate_seconds, pieces_for_shots, split_chunks
from studio.storyboard import Shot

FP = "abc123"


def test_same_inputs_same_key():
    assert cache_key(FP, "Hola a todos.", 2.0, 0) == cache_key(FP, "Hola a todos.", 2.0, 0)


def test_any_change_gives_a_new_key():
    base = cache_key(FP, "Hola a todos.", 2.0, 0)
    assert cache_key("other-profile", "Hola a todos.", 2.0, 0) != base
    assert cache_key(FP, "Hola a todos", 2.0, 0) != base
    assert cache_key(FP, "Hola a todos.", 2.5, 0) != base
    assert cache_key(FP, "Hola a todos.", 2.0, 1) != base


def test_length_estimate_counts_letters_not_spaces_or_punctuation():
    s = {"letters_per_second": 10.0, "pad_seconds": 0.5}
    assert estimate_seconds("abcde fghij.", s) == 1.5
    assert estimate_seconds("hola", s) == 1.0  # never shorter than a second


def test_long_sentences_split_at_commas():
    sentence = "uno dos tres, cuatro cinco seis, siete ocho nueve, diez once doce."
    assert split_chunks(sentence, 35) == ["uno dos tres, cuatro cinco seis,", "siete ocho nueve, diez once doce."]
    assert split_chunks("corta.", 30) == ["corta."]


def test_pieces_follow_shots_and_get_the_right_pause():
    shots = [Shot("a", "image", "Primera frase. Segunda frase que sigue"),
             Shot("b", "image", "en este plano."),
             Shot("c", "image", "Nuevo párrafo.")]
    pieces = pieces_for_shots(shots, paragraph_ends={1, 2}, max_chars=160)
    assert [(p.shot, p.text, p.gap) for p in pieces] == [
        (0, "Primera frase.", SENTENCE_GAP),
        (0, "Segunda frase que sigue", CHUNK_GAP),   # the shot cuts mid-sentence
        (1, "en este plano.", PARAGRAPH_GAP),
        (2, "Nuevo párrafo.", PARAGRAPH_GAP),
    ]


def test_a_respelled_name_heard_as_respelled_is_not_flagged():
    from studio.clone import score
    expect, say = "Su fuerte era la memoria DRAM.", "Su fuerte era la memoria de ram."
    assert score(expect, say, "Su fuerte era la memoria de Ram.") == (0.0, True)
    assert score(expect, say, "Su fuerte era la memoria DRAM.") == (0.0, True)
    wer, tail_ok = score(expect, say, "Su fuerte era la memoria.")
    assert wer > 0 and not tail_ok

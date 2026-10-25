"""Voice engine selection, per-engine lexicons and engine-aware cache keys (no model needed)."""
from pathlib import Path

import pytest

from studio.clone import DEFAULT_ENGINE, ENGINES, VoiceError, cache_key, engine_python, estimate_seconds, load_profile
from studio.textprep import load_lexicon, voice_text

PROFILE = """
engine: {engine}
reference: {{audio: ref.wav, text: ref.txt}}
lexicon: pronunciations.yaml
engines:
  omnivoice:
    model: k2-fsa/OmniVoice
    generation: {{language: es, num_step: 32, max_chunk_chars: 160}}
  f5-tts:
    model: hf://jpgallegoar/F5-Spanish/model_1250000.safetensors
    generation: {{nfe_step: 24, cfg_strength: 2.0, sway_sampling_coef: -1.0,
                 letters_per_second: 13.5, pad_seconds: 0.35, max_chunk_chars: 160}}
"""
LEXICON = """
translate: {AGI: IA general}
respell: {Good Judgment: Gud Yóchment}
engine_respell:
  f5-tts: {IA: í a, OIEA: o i e a}
"""


def make_voice(tmp_path: Path, engine: str = "omnivoice") -> Path:
    folder = tmp_path / "juan"
    folder.mkdir()
    (folder / "profile.yaml").write_text(PROFILE.format(engine=engine), encoding="utf-8")
    (folder / "pronunciations.yaml").write_text(LEXICON, encoding="utf-8")
    (folder / "ref.txt").write_text("Hola, soy Juan.", encoding="utf-8")
    (folder / "ref.wav").write_bytes(b"RIFF fake audio")
    return tmp_path


def test_omnivoice_is_the_default_engine():
    assert DEFAULT_ENGINE == "omnivoice"
    assert set(ENGINES) == {"omnivoice", "f5-tts"}


def test_profile_chooses_the_engine_and_the_caller_can_override_it(tmp_path):
    voices = make_voice(tmp_path, engine="omnivoice")
    omni = load_profile("juan", voices)
    assert (omni.engine, omni.model) == ("omnivoice", "k2-fsa/OmniVoice")
    f5 = load_profile("juan", voices, engine="f5-tts")
    assert f5.engine == "f5-tts" and f5.model.startswith("hf://jpgallegoar/F5-Spanish")
    assert f5.settings["nfe_step"] == 24


def test_profile_without_engine_line_uses_omnivoice(tmp_path):
    voices = make_voice(tmp_path)
    path = voices / "juan" / "profile.yaml"
    path.write_text(path.read_text().replace("engine: omnivoice\n", ""))
    assert load_profile("juan", voices).engine == "omnivoice"


def test_unknown_or_unconfigured_engine_fails_clearly(tmp_path):
    voices = make_voice(tmp_path)
    with pytest.raises(VoiceError, match="unknown voice engine"):
        load_profile("juan", voices, engine="xtts")
    path = voices / "juan" / "profile.yaml"
    path.write_text(path.read_text().split("  f5-tts:")[0])
    with pytest.raises(VoiceError, match="no settings for engine 'f5-tts'"):
        load_profile("juan", voices, engine="f5-tts")


def test_worker_config_matches_each_worker(tmp_path):
    voices = make_voice(tmp_path)
    omni = load_profile("juan", voices).worker_config("cpu")
    assert omni["model"] == "k2-fsa/OmniVoice" and omni["language"] == "es" and omni["num_step"] == 32
    f5 = load_profile("juan", voices, engine="f5-tts").worker_config("cpu")
    assert {"checkpoint", "nfe_step", "cfg_strength", "sway_sampling_coef"} <= set(f5)
    assert f5["device"] == omni["device"] == "cpu"


def test_engines_never_share_cache_entries(tmp_path):
    voices = make_voice(tmp_path)
    omni, f5 = load_profile("juan", voices), load_profile("juan", voices, engine="f5-tts")
    assert omni.fingerprint() != f5.fingerprint()
    assert cache_key(omni.fingerprint(), "Hola.", None, 0) != cache_key(f5.fingerprint(), "Hola.", None, 0)
    assert omni.fingerprint() == load_profile("juan", voices).fingerprint()  # stable between runs


def test_engine_name_alone_changes_the_fingerprint(tmp_path):
    voices = make_voice(tmp_path)
    a = load_profile("juan", voices)
    b = load_profile("juan", voices)
    b.engine = "f5-tts"   # same model, settings and reference: only the engine differs
    assert a.fingerprint() != b.fingerprint()


def test_omnivoice_picks_its_own_length():
    assert estimate_seconds("Hola a todos.", {"num_step": 32}) is None
    assert cache_key("fp", "Hola.", None, 0) == cache_key("fp", "Hola.", None, 0)
    assert cache_key("fp", "Hola.", None, 0) != cache_key("fp", "Hola.", 1.0, 0)


def test_lexicon_respellings_are_per_engine(tmp_path):
    path = make_voice(tmp_path) / "juan" / "pronunciations.yaml"
    text = "La AGI de la IA, según Good Judgment y el OIEA."
    assert voice_text(text, load_lexicon(path, "omnivoice")) == "La IA general de la IA, según Gud Yóchment y el OIEA."
    assert voice_text(text, load_lexicon(path, "f5-tts")) == "La í a general de la í a, según Gud Yóchment y el o i e a."
    assert load_lexicon(path).respell == {"Good Judgment": "Gud Yóchment"}  # no engine: shared tables only


def test_engine_python_can_be_overridden(monkeypatch):
    monkeypatch.delenv("STUDIO_OMNIVOICE_PYTHON", raising=False)
    assert engine_python(ENGINES["omnivoice"]) == Path(".venv-omnivoice/bin/python")
    monkeypatch.setenv("STUDIO_OMNIVOICE_PYTHON", "/opt/omni/bin/python")
    assert engine_python(ENGINES["omnivoice"]) == Path("/opt/omni/bin/python")

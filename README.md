# temperatura-studio

Turns a Spanish narration script into a narrated video for the YouTube channel
@temperaturacero: a Spanish voiceover, a new image every few seconds in one
consistent look, and simple code-made graphics, cut to the voice with ffmpeg.

Five scripts have storyboards and images: `examples/gobernanza-ia.md` (video 1),
`examples/japon-chips.md` (video 2), `examples/potencias-medias.md` (video 3),
`examples/consenso-sf.md` (video 4, first of the series "Economía de la IA transformadora")
and `examples/caballo.md` (video 5, "Tú eres el próximo caballo", headers like
`[PARTE 1: ...]`, pizarra theme; 26 pictures reused across 57 shots).

## How it works

1. **Parse** the script: split it into modules, keep the visual direction,
   take the narration and drop citation markers. Two formats:
   - `MÓDULO N: título` with `Dirección visual:` and `Locución:` (video 1);
     markers like `[8, 30]` are dropped.
   - `BLOQUE N: TÍTULO` and a final `CIERRE`, each with `[INDICACIÓN VISUAL / B-ROLL]`
     and `[LOCUCIÓN / GUION]` (video 2). Each block is one module, `CIERRE` the
     last one, and every bracketed source tag such as `[Reuters]` is dropped from
     the narration and the on-screen text.
   - `INTRODUCCIÓN ...`, `SECCIÓN N: TÍTULO` and `CONCLUSIÓN ...` (video 3), one module
     each, numbered in order. `[VFX ...]`, `[B-ROLL ...]` and `[CÁMARA ...]` at the start
     of a line are visual direction; `NARRADOR:` is optional; every other line is a
     paragraph. Header lines (Versión, Duración, Tono, Formato) are skipped and source
     tags such as `[3]`, `[12, 13]` or `[opinión Juan]` are dropped.
2. **Storyboard** (`storyboards/module1.yaml`): a list of shots. Each shot
   covers a piece of the narration and is an `image`, a `title_card` or a
   `text_overlay`. Shots cut only at sentence ends.
   A storyboard may set `theme: blueprint` (Juan's paper-and-grid slide look,
   navy ink and a copper accent) instead of the default `charcoal`. Blueprint
   overlays can also be full-frame data graphics, picked by one key:
   `links` (chain of links with a share counter), `bars`, `points` (a share
   going from one value to another), `steps` (dated timeline), `lot` (a 25-wafer
   lot against single wafers), `places` (map of Japan), `figures` (big
   numbers) and `path` (a narrow path between two cliffs). See `storyboards/japon-chips/` for examples.
   Series «China y la IA» (video 7) adds to blueprint one colour only, seal vermilion
   (`graphics.VERMILION`, used only for the J level / «prohibido»), and a copper «MI LECTURA»
   tab for Juan's opinion shots: `opinion: true` on any blueprint overlay (on a picture, an
   overlay with only `opinion: true` draws just the tab). Chinese characters in any blueprint
   text are drawn with Noto Serif CJK SC (SIL OFL; a 2.6 MB subset per weight of the 3,755
   common characters, rebuilt with `python3 -m scripts.subset_cjk_font --text "..."`).
   Its graphics: `stamp` (one to three rubber stamps; `ink: j` vermilion, `x` hollow navy,
   `ink`, `copper`), `seals: [{..., at: [x, y]}]` to stamp on top of any blueprint graphic,
   `doc` (a ruled document: catalogue rows with codes and grey bars where the text is not
   known, the case-file card of Juan's ideas with ARGUMENTADA / MATIZ stamps, the four-ways
   matrix; rows revealed one per shot) and `expediente` (the series ident
   «CHINA Y LA IA · EXPEDIENTE 0N», `graphics.opener(n, status)`). Quote cards take
   `highlight: [phrases]` and `size`; `people` takes `show` and a `seal` per card; `steps`
   takes `muted` and `span`; a bar can be `ink: j`; `lit` takes `link` (an arc).
   `theme: editorial` (video 4) draws the same graphics on cream paper with serif
   titles (DM Serif Display), copper numbers, olive stat boxes and a line-art
   skyline. Extra full-frame graphics in both paper themes: `people` (text cards
   for real people: name, company, quote, timeline; never portraits), `lit`
   (world map with lit places), `loop` (a self-improvement loop and a take-off
   curve), `icons` (a grid of power-plant icons, some shown), `jcurve` and
   `contrast` (a small figure next to a big one that grows).
   `theme: pizarra` (video 5, `studio/pizarra.py`) is a minimalist whiteboard
   cartoon: very light blue paper (#e4f4fd), a ground line with a pale blue band
   (#c9e9fc) at the same height on every card, thin black outlines, handwritten
   Kalam (SIL OFL) and red only to strike text out. Its full-frame graphics:
   `phrase` (a big phrase, optionally with a red `strike` through part of it),
   `big` (a number that pops on, with doodles on the ground), `gauge` (a dial),
   `parcels` (farmland, one column of oats and hay), `pile` (manure against
   buildings), `rows` (horses and tractors as doodles, one per million),
   `bars` (before/after bars), `week` (Monday to Friday filled up to a percent),
   `of` + `hit` (8 of 10 figures, or a 10 x 10 grid) and `list` (a checklist
   ticked one item per shot). On a picture: `note` (handwritten words in the
   empty sky) and `placard` (words written on a blank placard at `box`).
   Kinetic typography is done shot by shot: the next card adds the strike, the
   tick or the number. Picture shots pan with `motion: pan_right`/`pan_left`.
3. **Voice**: either your own recording (see below), or a free Microsoft neural
   voice through edge-tts (`es-ES-AlvaroNeural`), one paragraph at a time.
   Word timings decide where each shot starts and ends.
4. **Images and graphics**: images are read from `assets/images/moduleN/`
   (or `assets/images/STEM/moduleN/`, see below), named by shot id. Title cards and text overlays are drawn with Pillow.
5. **Assemble**: ffmpeg renders each shot with a slow zoom or pan, joins them
   with clean cuts and adds the voice. 1920x1080, 30 fps.

## Setup

Needs Python 3.11+ and ffmpeg.

```
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
```

## Build module 1

With the synthesized voice:

```
.venv/bin/python -m studio build examples/gobernanza-ia.md --module 1
```

With your own recording:

```
.venv/bin/python -m studio build examples/gobernanza-ia.md --module 1 --audio grabaciones/modulo1.m4a
```

Output: `output/module1.mp4`. Per-shot timings: `output/module1/timings.json`.
Voice audio is cached in `cache/`, so a rebuild only calls the TTS service for
paragraphs that changed.

## Build the whole script

```
.venv/bin/python -m studio build examples/gobernanza-ia.md --module all --voice juan
```

Builds every module from `storyboards/moduleN.yaml` and `assets/images/moduleN/`,
then joins them, in order, into `output/gobernanza-ia_full.mp4`. Each module
starts with its own title card.

A script with its own folder `storyboards/STEM/` (STEM is the file name without
`.md`) uses that folder and `assets/images/STEM/` instead:

```
.venv/bin/python -m studio build examples/japon-chips.md --module all --voice juan --out output/japon-chips
```

The Japan storyboards are written by `scripts/make_japon_boards.py`
(`.venv/bin/python -m scripts.make_japon_boards`), which also checks that each
block's shots cover its sentences. `scripts/make_potencias_boards.py` and
`scripts/make_consenso_boards.py` do the same for videos 3 and 4.

If a shot has no image yet, the build stops and prints the shot id and the
full prompt to generate it with.

## Your own voice

Record the narration of one module and pass it with `--audio` (m4a, mp3 or
wav). The tool transcribes it on your computer with faster-whisper (free, no
upload), matches the words to the storyboard shots, and cuts between shots in
your pauses. Your recording, lightly cleaned up (gentle high-pass, loudness to
about -16 LUFS), becomes the soundtrack.

How to record:

- A quiet room with soft things around (sofa, curtains), not a bare kitchen.
- Phone voice memo app, phone 20-30 cm from your mouth, a bit to the side so
  you don't blow into it.
- Read the module once, straight through, from the script.
- Pausing is fine, and helps: cuts land in your pauses.
- If you stumble, stop, pause for a second, and read the whole sentence again.
  No need to start over.

The first run downloads the Whisper model (about 1.5 GB for `medium`).
Transcribing takes roughly a quarter of the recording's length on an 8-core
CPU; `--whisper-model small` is about three times faster and a bit less
accurate. The transcript is cached, so rebuilding with the same recording is quick.

After the build, check the table it prints (also saved as
`output/moduleN_alignment.json`). For each shot it shows how many script words
were heard and how many extra words were said. Shots marked `check` probably
have a skipped phrase, an ad-lib or a misheard word: watch those cuts. `IN SPEECH`
means there was no pause where that shot starts, so the cut falls between two
words. The build stops only if the recording barely matches the module, for
example when it is a different module.

## Cloned voice (`--voice juan`)

Narrates any script in Juan's cloned voice, without recording it. Juan recorded one
reference clip once; every script after that is generated from it. Two voice engines:

- **OmniVoice** (default): [k2-fsa/OmniVoice](https://huggingface.co/k2-fsa/OmniVoice),
  a multilingual zero-shot model. In Juan's A/B test it sounded clearly better than F5 and
  says Spanish acronyms such as IA, OIEA or ONU without help. Code Apache-2.0, weights CC-BY-NC.
- **F5-TTS**: [F5-TTS](https://github.com/SWivid/F5-TTS) with the Spanish fine-tune
  [F5-Spanish](https://huggingface.co/jpgallegoar/F5-Spanish), weights CC-BY-NC-4.0.

Both licences are non-commercial: fine for a non-monetized channel only.

```
.venv/bin/python -m studio build examples/gobernanza-ia.md --module 1 --voice juan
.venv/bin/python -m studio build examples/gobernanza-ia.md --module 1 --voice juan --voice-engine f5-tts
```

The profile's `engine:` line picks the engine; `--voice-engine` overrides it for one run.

A voice profile is a folder `voices/NAME/`:

- `profile.yaml`: the engine, and under `engines:` each engine's model and generation
  settings.
- `ref.txt`: the exact words spoken in the reference clip.
- `pronunciations.yaml`: text changes for the voice only. `translate` turns English
  into Spanish ("Chips for Peace" -> "Chips para la Paz", "AGI" -> "IA general") for
  every engine. `respell` spells names the way they are said ("Good Judgment Inc." ->
  "Gud Yóchment") for every engine; `engine_respell` adds respellings that only one
  engine needs (F5 needs "IA" -> "í a", OmniVoice does not). Numbers are written out:
  2030s, 2025-2060, 79%. The script is never changed.
- `ref.wav`: the reference clip. **Not in git**: it is a personal recording. Copy it
  into `voices/juan/` before the first run; the build says so if it is missing.

How it works: the narration is generated one sentence at a time (long sentences are
split at commas), never across a shot boundary, so cuts land exactly in the pauses:
0.35 s between sentences, 0.7 s between paragraphs. F5 is asked for about as long as
Juan would take to say each piece, which stops it from cutting sentence endings;
OmniVoice picks the length itself. Whisper then listens to every piece; if words are
wrong or the end is missing, it is generated again with another seed (up to 3) and
the best take is kept. A take counts as right if it matches either the script (with
translations) or the respelled text the engine was given, since Whisper often writes
a well-said "de ram" as spelled. The whole narration is normalized to -16 LUFS. Per-piece
results (what Whisper heard, word error rate, seed) go to `output/moduleN_voice.json`.

Every take is cached in `cache/voice/` by a hash of the engine and the profile
(reference audio, its text, model, settings), the text and the seed. Takes from the
two engines never mix (F5 takes cached before the engine was part of the hash are not
reused). A rebuild only generates sentences that changed; an
interrupted run picks up where it stopped.

To hear the narration of a module without building the video (fills the same cache):

```
.venv/bin/python -m studio narrate examples/gobernanza-ia.md --module 2 3 --voice juan
```

### Setup

Each engine has its own virtualenv (their dependencies clash with studio's). Studio
runs the engine as a separate process (`studio/omnivoice_worker.py` or
`studio/f5_worker.py`) and talks to it over stdin/stdout.

OmniVoice (CPU PyTorch; add `--cuda` for an NVIDIA GPU):

```
scripts/setup_omnivoice.sh
```

F5:

```
python3.11 -m venv .venv-f5
.venv-f5/bin/pip install f5-tts==1.1.22 "pyarrow<20" soundfile
```

Put them elsewhere with `STUDIO_OMNIVOICE_PYTHON=/path/to/python` or
`STUDIO_F5_PYTHON=/path/to/python`. The first run downloads the model (OmniVoice about
3.3 GB, F5-Spanish about 1.3 GB) and the Whisper model. OmniVoice needs about 4 GB of RAM.

Speed on an 8-core CPU: both engines take about 7-9 seconds per second of speech, so a
12-minute script takes 1.5-2 hours. With an NVIDIA GPU add `--voice-device cuda` (a
rented RTX 4090 does a whole script in minutes, for well under 1 EUR).

## Tests

```
.venv/bin/pip install -r requirements-dev.txt
.venv/bin/python -m pytest
```

`scripts/make_test_recording.py` makes a stand-in recording of module 1 (another
voice, slower, with long pauses, a false start, a skipped phrase and an ad-lib)
to try `--audio` without a real recording.

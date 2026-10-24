# temperatura-studio

Turns a Spanish narration script into a narrated video for the YouTube channel
@temperaturacero: a Spanish voiceover, a new image every few seconds in one
consistent look, and simple code-made graphics, cut to the voice with ffmpeg.

Right now it builds one module at a time, and only module 1 has a storyboard
and images.

## How it works

1. **Parse** the script (`examples/gobernanza-ia.md`): split it into modules,
   keep the visual direction, take the narration and drop citation markers
   like `[8, 30]`.
2. **Storyboard** (`storyboards/module1.yaml`): a list of shots. Each shot
   covers a piece of the narration and is an `image`, a `title_card` or a
   `text_overlay`. Written by hand for now.
3. **Voice**: either your own recording (see below), or a free Microsoft neural
   voice through edge-tts (`es-ES-AlvaroNeural`), one paragraph at a time.
   Word timings decide where each shot starts and ends.
4. **Images and graphics**: images are read from `assets/images/moduleN/`,
   named by shot id. Title cards and text overlays are drawn with Pillow.
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

## Tests

```
.venv/bin/pip install -r requirements-dev.txt
.venv/bin/python -m pytest
```

`scripts/make_test_recording.py` makes a stand-in recording of module 1 (another
voice, slower, with long pauses, a false start, a skipped phrase and an ad-lib)
to try `--audio` without a real recording.

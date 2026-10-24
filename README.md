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
3. **Voice**: free Microsoft neural voice through edge-tts (`es-ES-AlvaroNeural`),
   one paragraph at a time. Word timings decide where each shot starts and ends.
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

```
.venv/bin/python -m studio build examples/gobernanza-ia.md --module 1
```

Output: `output/module1.mp4`. Per-shot timings: `output/module1/timings.json`.
Voice audio is cached in `cache/`, so a rebuild only calls the TTS service for
paragraphs that changed.

If a shot has no image yet, the build stops and prints the shot id and the
full prompt to generate it with.

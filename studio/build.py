"""Build one module of a script into a video."""
import json
from pathlib import Path

from studio import assemble, graphics, storyboard, timeline
from studio.images import ImageProvider, MissingImages
from studio.parse import parse_script


def build_module(script: Path, number: int, board_path: Path, provider: ImageProvider,
                 out_dir: Path, cache: Path) -> Path:
    modules = {m.number: m for m in parse_script(script.read_text(encoding="utf-8"))}
    module = modules[number]
    board = storyboard.load(board_path)
    storyboard.check_coverage(board, module)

    # Find every image first, so a missing one fails before any slow work.
    backgrounds, missing = {}, []
    for shot in board.shots:
        if shot.prompt:
            path = provider.get(shot, board.image_prompt(shot))
            if path is None:
                missing.append(f"{shot.id}: {board.image_prompt(shot)}")
            backgrounds[shot.id] = path
    if missing:
        raise MissingImages("no image for these shots:\n" + "\n".join(missing))

    work = out_dir / f"module{number}"
    work.mkdir(parents=True, exist_ok=True)
    audio = work / "voice.wav"
    timings = timeline.build(board, module, cache / "voice", audio)

    clips = []
    for i, t in enumerate(timings):
        shot = t.shot
        overlay = None
        if shot.type == "title_card":
            background = graphics.title_card(shot.title, shot.subtitle, work / f"{shot.id}.png")
        elif shot.type == "text_overlay" and not shot.prompt:
            background = graphics.overlay_card(shot.overlay, work / f"{shot.id}.png", on_photo=False)
        else:
            background = backgrounds[shot.id]
            if shot.type == "text_overlay":
                overlay = graphics.overlay_card(shot.overlay, work / f"{shot.id}_overlay.png", on_photo=True)
        still = shot.type == "title_card" or (shot.type == "text_overlay" and not shot.prompt)
        motion = shot.motion or ("none" if still else assemble.MOTIONS[i % len(assemble.MOTIONS)])
        clips.append(assemble.render_clip(t, background, overlay, motion, work / f"{shot.id}.mp4"))
        print(f"{shot.id:7} {shot.type:12} {t.start_frame / timeline.FPS:6.2f}s  {t.seconds:5.2f}s  {shot.text[:60]}")

    (work / "timings.json").write_text(json.dumps(
        [{"id": t.shot.id, "type": t.shot.type, "start": round(t.start_frame / timeline.FPS, 3),
          "seconds": round(t.seconds, 3), "text": t.shot.text} for t in timings],
        ensure_ascii=False, indent=1))
    out = assemble.join(clips, audio, out_dir / f"module{number}.mp4")
    total = sum(t.frames for t in timings) / timeline.FPS
    print(f"\n{out}: {len(timings)} shots, {total:.2f}s, voice {board.voice}")
    return out

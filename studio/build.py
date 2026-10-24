"""Build one module of a script into a video."""
import json
from pathlib import Path

from studio import assemble, clone, graphics, recording, storyboard, timeline
from studio.images import ImageProvider, MissingImages
from studio.parse import parse_script


def build_module(script: Path, number: int, board_path: Path, provider: ImageProvider,
                 out_dir: Path, cache: Path, audio: Path | None = None,
                 whisper_model: str = recording.WHISPER_MODEL, voice: str | None = None,
                 voice_device: str = "cpu") -> Path:
    """Build the module video. With audio (a recording of the narration) the video
    is timed to it; with voice (a cloned-voice profile name) the narration is generated
    in that voice; otherwise the voice is synthesized with edge-tts."""
    if audio and voice:
        raise ValueError("use either a recording (--audio) or a cloned voice (--voice), not both")
    profile = clone.load_profile(voice) if voice else None  # fail early if files are missing
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
    soundtrack = work / "voice.wav"
    if profile:
        timings, report = clone.timings_from_voice(board, module, profile, cache / "voice",
                                                   soundtrack, voice_device, whisper_model)
        (out_dir / f"module{number}_voice.json").write_text(
            json.dumps(report, ensure_ascii=False, indent=1), encoding="utf-8")
        voice_name = f"cloned voice {voice}"
    elif audio is None:
        timings = timeline.build(board, module, cache / "voice", soundtrack)
        voice_name = board.voice
    else:
        timings, aligned = recording.timings_from_recording(
            board, audio, cache, soundtrack, whisper_model)
        _alignment_report(timings, aligned, out_dir / f"module{number}_alignment.json")
        voice_name = f"recording {audio.name}"

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
    out = assemble.join(clips, soundtrack, out_dir / f"module{number}.mp4")
    total = sum(t.frames for t in timings) / timeline.FPS
    print(f"\n{out}: {len(timings)} shots, {total:.2f}s, voice {voice_name}")
    return out


def _alignment_report(timings, aligned, path: Path) -> None:
    """Print a short table and save the full report as JSON."""
    rows = []
    print(f"{'shot':7} {'start':>7} {'end':>7} {'match':>6} {'extra':>5}  cut")
    for t, a in zip(timings, aligned):
        start, end = t.start_frame / timeline.FPS, (t.start_frame + t.frames) / timeline.FPS
        cut = "pause" if a.cut_in_pause else "IN SPEECH"
        warn = "  <- check: words differ from the script" if a.flagged else ""
        print(f"{t.shot.id:7} {start:7.2f} {end:7.2f} {a.matched:3}/{a.words:<3} {a.extra:4}   {cut}{warn}")
        rows.append({"id": t.shot.id, "start": round(start, 3), "end": round(end, 3),
                     "words": a.words, "matched": a.matched, "ratio": round(a.ratio, 3),
                     "extra_words": a.extra, "cut_in_pause": a.cut_in_pause, "flagged": a.flagged})
    matched, words = sum(a.matched for a in aligned), sum(a.words for a in aligned)
    print(f"overall: {matched}/{words} script words heard ({matched / words:.0%}); "
          f"{sum(r['flagged'] for r in rows)} shot(s) to check\n")
    path.write_text(json.dumps({"overall_ratio": round(matched / words, 3), "shots": rows},
                               ensure_ascii=False, indent=1))


def narrate_module(script: Path, number: int, voice: str, out_dir: Path, cache: Path,
                   device: str = "cpu", whisper_model: str = recording.WHISPER_MODEL) -> Path:
    """Only the narration of one module, in a cloned voice, one paragraph after another.
    Pieces are the same sentences a storyboard cut at sentence ends uses, so a later
    build --voice reuses them from the cache."""
    module = {m.number: m for m in parse_script(script.read_text(encoding="utf-8"))}[number]
    profile = clone.load_profile(voice)
    shots = [storyboard.Shot(id=f"p{i + 1}", type="image", text=p)
             for i, p in enumerate(module.narration.split("\n\n"))]
    work = out_dir / f"module{number}"
    work.mkdir(parents=True, exist_ok=True)
    narrator = clone.Narrator(profile, cache / "voice", device, whisper_model)
    try:
        pcm, _, report = clone.narrate_shots(narrator, shots, set(range(len(shots))), work)
    finally:
        narrator.close()
    out = out_dir / f"module{number}_{voice}.wav"
    clone.write_wav(pcm, out)
    (out_dir / f"module{number}_{voice}.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"{out}: {len(pcm) / clone.RATE:.1f}s")
    return out

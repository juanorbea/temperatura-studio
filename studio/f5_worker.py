"""F5-TTS worker. Runs inside the F5 virtualenv (not studio's), talks JSON lines on stdin/stdout.

First line: {"checkpoint", "ref_audio", "ref_text", "device", "nfe_step", "cfg_strength",
             "sway_sampling_coef"}
Then one request per line: {"text", "seconds", "seed", "out"} -> writes a 24 kHz mono wav,
answers {"ok": true, "seconds": <audio length>, "took": <generation time>}.
Kept free of studio imports on purpose: it only needs f5_tts, numpy, soundfile.
"""
import json
import sys
import time

import numpy as np
import soundfile as sf

SR = 24000


def trim(w: np.ndarray, thr_db: float = -40, frame: int = 240) -> np.ndarray:
    """Cut silence at both ends, and a short stray sound after a pause at the very end."""
    db = 20 * np.log10(np.sqrt(np.convolve(w ** 2, np.ones(frame) / frame, "same")) + 1e-9)
    loud = np.where(db > thr_db)[0]
    if len(loud) == 0:
        return w
    lo, hi = max(loud[0] - 2400, 0), loud[-1] + 2400
    w, quiet = w[lo:hi], db[lo:hi] < thr_db
    run = 0
    for j in range(len(w) - 1, max(len(w) - SR, 0), -1):
        if quiet[j]:
            run += 1
            continue
        if run >= 0.25 * SR and len(w) - (j + run) < 0.45 * SR and j + run < len(w) - 2400:
            return w[: j + 1 + 2400]
        run = 0
    return w


def main() -> None:
    out = sys.stdout
    sys.stdout = sys.stderr  # f5_tts prints progress; keep stdout for answers only
    from huggingface_hub import hf_hub_download
    from f5_tts.api import F5TTS
    from f5_tts.infer.utils_infer import preprocess_ref_audio_text

    cfg = json.loads(sys.stdin.readline())
    ckpt = cfg["checkpoint"]
    if ckpt.startswith("hf://"):
        repo, _, filename = ckpt[5:].rpartition("/")
        ckpt = hf_hub_download(repo, filename)
    tts = F5TTS(model="F5TTS_Base", ckpt_file=ckpt, device=cfg["device"])
    ref_audio, ref_text = preprocess_ref_audio_text(cfg["ref_audio"], cfg["ref_text"], show_info=lambda *a: None)
    ref_seconds = sf.info(ref_audio).duration
    print(json.dumps({"ok": True, "ready": True}), file=out, flush=True)

    for line in sys.stdin:
        req = json.loads(line)
        start = time.time()
        wav, _, _ = tts.infer(ref_audio, ref_text, req["text"], nfe_step=cfg["nfe_step"],
                              cfg_strength=cfg["cfg_strength"], sway_sampling_coef=cfg["sway_sampling_coef"],
                              fix_duration=ref_seconds + req["seconds"], seed=req["seed"],
                              show_info=lambda *a: None, progress=None)
        wav = trim(np.asarray(wav, np.float32))
        sf.write(req["out"], wav, SR)
        print(json.dumps({"ok": True, "seconds": round(len(wav) / SR, 3),
                          "took": round(time.time() - start, 1)}), file=out, flush=True)


if __name__ == "__main__":
    main()

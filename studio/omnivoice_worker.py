"""OmniVoice worker. Runs inside the OmniVoice virtualenv (not studio's), talks JSON lines on stdin/stdout.

First line: {"model", "ref_audio", "ref_text", "device", "language", and optional
             OmniVoice generation settings: "num_step", "guidance_scale", "t_shift", ...}
Then one request per line: {"text", "seconds", "seed", "out"} -> writes a 24 kHz mono wav,
answers {"ok": true, "seconds": <audio length>, "took": <generation time>}.
"seconds" may be null: OmniVoice then picks the length itself (it does not cut endings like F5).
OmniVoice already trims silence and fades the edges of what it generates.
Kept free of studio imports on purpose: it only needs omnivoice, torch, soundfile.
"""
import json
import sys
import time

import soundfile as sf

SR = 24000
GENERATION_KEYS = ("num_step", "guidance_scale", "t_shift", "layer_penalty_factor",
                   "position_temperature", "class_temperature")


def main() -> None:
    out = sys.stdout
    sys.stdout = sys.stderr  # keep stdout for answers only
    import torch
    from omnivoice import OmniVoice
    from omnivoice.models.omnivoice import OmniVoiceGenerationConfig

    cfg = json.loads(sys.stdin.readline())
    device = cfg["device"]
    dtype = torch.float32 if device == "cpu" else torch.float16
    model = OmniVoice.from_pretrained(cfg["model"], device_map=device, dtype=dtype)
    prompt = model.create_voice_clone_prompt(ref_audio=cfg["ref_audio"], ref_text=cfg["ref_text"])
    generation = OmniVoiceGenerationConfig.from_dict({k: cfg[k] for k in GENERATION_KEYS if k in cfg})
    print(json.dumps({"ok": True, "ready": True}), file=out, flush=True)

    for line in sys.stdin:
        req = json.loads(line)
        start = time.time()
        torch.manual_seed(req["seed"])
        wav = model.generate(text=req["text"], language=cfg.get("language"), voice_clone_prompt=prompt,
                             duration=req.get("seconds"), generation_config=generation)[0]
        sf.write(req["out"], wav, SR)
        print(json.dumps({"ok": True, "seconds": round(len(wav) / SR, 3),
                          "took": round(time.time() - start, 1)}), file=out, flush=True)


if __name__ == "__main__":
    main()

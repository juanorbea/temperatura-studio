"""Make a stand-in 'human' recording of module 1 for testing --audio.

It differs from the storyboard on purpose: another voice, slower, long pauses,
one false start that is read again, one skipped phrase and one ad-lib.

    .venv/bin/python scripts/make_test_recording.py output/test_recording.m4a
"""
import asyncio
import subprocess
import sys
import tempfile
from pathlib import Path

import edge_tts

VOICE, RATE = "es-MX-JorgeNeural", "-12%"

# (text, seconds of silence after it)
PIECES = [
    ("Hola a todos y bienvenidos.", 0.5),
    ("En los últimos años hemos presenciado una avalancha de cumbres internacionales, "
     "declaraciones multilaterales y discursos sobre la necesidad urgente de regular "
     "la Inteligencia Artificial de frontera.", 1.6),                                  # long pause
    ("Frecuentemente escuchamos que los gobiernos están a punto de coordinarse para "
     "evitar riesgos catastróficos y garantizar una IA segura para la humanidad.", 0.5),
    ("Sin embargo, ¿qué dicen realmente los datos e investigaciones cuando analizamos "
     "las probabilidades a largo plazo?", 1.2),
    ("Hoy nos adentramos en un análisis basado en el informe de superpronósticos de "
     "Good Judgment Inc., titulado \"Global AI Governance and Strategic Cooperation "
     "Forecasts 2025-2060\".", 0.6),
    ("Este estudio reúne las predicciones de un grupo de", 1.2),                         # false start
    ("Este estudio reúne las predicciones de un grupo de superpronosticadores "
     "internacionales sobre diez hitos clave en la regulación mundial de la IA, control "
     "de semiconductores, tratados militares y agencias regulatorias.", 2.0),          # long pause
    ("Y la conclusión central del informe es reveladora: la verdadera cooperación "
     "vinculante no llegará en los 2030s, sino que se postergará hacia las décadas "
     "de 2040 y 2050.", 0.9),                                                           # skips "como muchos desearían"
    ("¿Por qué ocurre esto?", 0.5),
    ("Bueno, es una pregunta muy interesante.", 0.4),                                  # ad-lib
    ("¿Qué frena la diplomacia tecnológica y qué eventos podrían acelerar estos plazos?", 0.7),
    ("Acompáñame a desglosarlo.", 1.0),
]
LEAD_IN = 1.2  # a voice memo starts with a moment of silence


async def tts(text: str, out: Path) -> None:
    await edge_tts.Communicate(text, VOICE, rate=RATE).save(str(out))


def main(out: Path) -> None:
    tmp = Path(tempfile.mkdtemp())
    parts = []
    silence = lambda s: ["-f", "lavfi", "-t", str(s), "-i", "anullsrc=r=48000:cl=mono"]
    args, n = silence(LEAD_IN), 1
    for i, (text, pause) in enumerate(PIECES):
        mp3 = tmp / f"{i:02d}.mp3"
        asyncio.run(tts(text, mp3))
        args += ["-i", str(mp3)] + silence(pause)
        n += 2
    concat = "".join(f"[{k}:a]aresample=48000,aformat=channel_layouts=mono[a{k}];" for k in range(n))
    concat += "".join(f"[a{k}]" for k in range(n)) + f"concat=n={n}:v=0:a=1[speech];"
    # Quiet room noise under everything, like a phone recording.
    concat += "anoisesrc=r=48000:color=pink:amplitude=0.003[noise];" \
              "[speech][noise]amix=inputs=2:duration=first:normalize=0[out]"
    subprocess.run(["ffmpeg", "-v", "error", "-y", *args, "-filter_complex", concat,
                    "-map", "[out]", "-c:a", "aac", "-b:a", "128k", str(out)], check=True)
    print(out)


if __name__ == "__main__":
    main(Path(sys.argv[1]))

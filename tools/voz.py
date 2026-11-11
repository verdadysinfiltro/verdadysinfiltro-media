#!/usr/bin/env python3
"""Locución de un reel en dos golpes con Supertonic 3 (voces F5 = mujer, M5 = hombre).

Uso:
  python3 tools/voz.py salida.wav F5|M5 "Golpe 1" "Golpe 2"
Imprime JSON: {"t2": segundo en que empieza el golpe 2, "dur": duración total recomendada del reel}.

El modelo (~380 MB) se descarga una vez de Hugging Face a ~/.cache/sinfiltro/supertonic3.
Licencia OpenRAIL: obliga a avisar de que la voz está generada por máquina
(línea "Voz generada con IA." en el caption).
"""
import json
import os
import subprocess
import sys

REPO = "https://huggingface.co/Supertone/supertonic-3/resolve/724fb5abbf5502583fb520898d45929e62f02c0b/"
DIR = os.path.expanduser("~/.cache/sinfiltro/supertonic3")
ARCHIVOS = {
    "onnx/duration_predictor.onnx": 3700147, "onnx/text_encoder.onnx": 36416150,
    "onnx/tts.json": 8253, "onnx/unicode_indexer.json": 277676,
    "onnx/vector_estimator.onnx": 256534781, "onnx/vocoder.onnx": 101424195,
    "voice_styles/F5.json": 291479, "voice_styles/M5.json": 291469,
}
SR = 44100
INICIO = 0.4      # silencio antes del golpe 1
PAUSA = 0.6       # silencio entre golpes
COLA = 1.2        # tiempo con la frase entera tras acabar la voz
VELOCIDAD = 0.9
PASOS = 16


def preparar():
    for ruta, tam in ARCHIVOS.items():
        destino = os.path.join(DIR, ruta)
        if os.path.exists(destino) and os.path.getsize(destino) == tam:
            continue
        os.makedirs(os.path.dirname(destino), exist_ok=True)
        subprocess.run(["curl", "-sSfL", "--retry", "2", "-m", "900", "-o", destino, REPO + ruta], check=True)
        if os.path.getsize(destino) != tam:
            sys.exit(f"Descarga incompleta: {ruta}")
    try:
        import supertonic  # noqa: F401
    except ImportError:
        subprocess.run([sys.executable, "-m", "pip", "install", "-q", "supertonic", "soundfile"], check=True)


def main():
    if len(sys.argv) != 5 or sys.argv[2] not in ("F5", "M5"):
        sys.exit(__doc__)
    salida, voz, g1, g2 = sys.argv[1:]
    preparar()
    import logging
    logging.disable(logging.CRITICAL)
    import numpy as np
    import soundfile as sf
    from supertonic import TTS

    tts = TTS(model="supertonic-3", model_dir=DIR, auto_download=False)
    estilo = tts.get_voice_style(voz)
    trozos = []
    for texto in (g1, g2):
        onda, _ = tts.synthesize(texto, voice_style=estilo, lang="es", speed=VELOCIDAD, total_steps=PASOS)
        trozos.append(np.asarray(onda, dtype=np.float32).reshape(-1))
    silencio = lambda s: np.zeros(int(SR * s), dtype=np.float32)
    t2 = INICIO + len(trozos[0]) / SR + PAUSA
    audio = np.concatenate([silencio(INICIO), trozos[0], silencio(PAUSA), trozos[1], silencio(COLA)])
    pico = float(np.max(np.abs(audio))) or 1.0
    sf.write(salida, audio * (0.89 / pico), SR)
    print(json.dumps({"t2": round(t2, 2), "dur": round(max(len(audio) / SR, 6.5), 2)}))


if __name__ == "__main__":
    main()

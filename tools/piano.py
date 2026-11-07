#!/usr/bin/env python3
"""Genera un fondo de piano triste original (sin derechos) para reels.

Uso: python3 tools/piano.py salida.wav [segundos=8] [semilla]
Cada semilla da una progresión y un tempo distintos, para que los reels no suenen iguales.
"""
import random
import sys
import wave

import numpy as np

SR = 44100
# Progresiones menores típicas de piano melancólico (grados en semitonos desde la tónica)
PROGRESIONES = [
    [[0, 3, 7], [-4, 0, 3], [-9, -5, -2], [-2, 2, 5]],     # i  VI  III  VII
    [[0, 3, 7], [-7, -4, 0], [-4, 0, 3], [-2, 2, 5]],      # i  iv  VI  VII
    [[-4, 0, 3], [-2, 2, 5], [0, 3, 7], [0, 3, 7]],        # VI VII i  i
    [[0, 3, 7], [-2, 2, 5], [-4, 0, 3], [-5, -1, 2]],      # i  VII VI V
]
TONICAS = [57, 55, 52, 50, 53]  # La, Sol, Mi, Re, Fa (MIDI)


def nota(midi, dur, vel=0.5):
    t = np.arange(int(SR * dur)) / SR
    f = 440 * 2 ** ((midi - 69) / 12)
    onda = sum(a * np.sin(2 * np.pi * f * k * t) for k, a in [(1, 1), (2, .45), (3, .2), (4, .1), (5, .05)])
    env = np.exp(-t * (2.2 + midi / 60)) * (1 - np.exp(-t * 300))
    return vel * onda * env


def main():
    salida = sys.argv[1]
    segs = float(sys.argv[2]) if len(sys.argv) > 2 else 8
    rnd = random.Random(sys.argv[3] if len(sys.argv) > 3 else None)
    prog, ton = rnd.choice(PROGRESIONES), rnd.choice(TONICAS)
    compas = rnd.choice([1.8, 2.0, 2.2])
    mezcla = np.zeros(int(SR * (segs + 3)))
    t0, i = 0.0, 0
    while t0 < segs:
        acorde = prog[i % len(prog)]
        ini = int(t0 * SR)
        bajo = nota(ton - 12 + acorde[0], compas + 2, .35)
        mezcla[ini:ini + len(bajo)] += bajo[:len(mezcla) - ini]
        for j, g in enumerate(acorde):  # arpegio suave
            s = int((t0 + j * compas / 6) * SR)
            n = nota(ton + g, compas + 1.5, .22)
            mezcla[s:s + len(n)] += n[:len(mezcla) - s]
        mel = ton + 12 + rnd.choice(acorde)
        s = int((t0 + compas / 2) * SR)
        n = nota(mel, compas, .18)
        mezcla[s:s + len(n)] += n[:len(mezcla) - s]
        t0 += compas
        i += 1
    # reverb sencilla con ecos
    for d, a in [(0.11, .35), (0.23, .25), (0.37, .18), (0.53, .12)]:
        k = int(d * SR)
        mezcla[k:] += a * mezcla[:-k]
    mezcla = mezcla[:int(SR * segs)]
    fade = int(SR * 1.2)
    mezcla[-fade:] *= np.linspace(1, 0, fade)
    mezcla = mezcla / (np.abs(mezcla).max() + 1e-9) * 0.5
    est = np.stack([mezcla, np.roll(mezcla, 300)], 1)
    with wave.open(salida, "wb") as w:
        w.setnchannels(2)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes((est * 32767).astype("<i2").tobytes())
    print(salida)


if __name__ == "__main__":
    main()

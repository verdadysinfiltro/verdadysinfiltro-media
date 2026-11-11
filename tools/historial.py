#!/usr/bin/env python3
"""Comprueba frases contra docs/historial.md sin tener que leerlo entero, y añade filas.

Uso:
  python3 tools/historial.py check "frase 1" "frase 2" ...
      Imprime solo las frases repetidas o casi iguales (parecido >= 0,72) a algo publicado
      o entre ellas. Si no imprime nada, todas son nuevas.
  python3 tools/historial.py add AAAA-MM-DD "formato" "frase" "archivos"
"""
import difflib
import os
import re
import sys
import unicodedata

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
HIST = os.path.join(RAIZ, "docs", "historial.md")
UMBRAL = 0.72


def norm(t):
    t = unicodedata.normalize("NFD", t.lower())
    t = "".join(c for c in t if unicodedata.category(c) != "Mn")
    return re.sub(r"[^a-zñ0-9 ]+", " ", t).split()


def publicadas():
    out = []
    for linea in open(HIST, encoding="utf-8"):
        if not linea.startswith("|") or linea.startswith("| Fecha") or linea.startswith("|---"):
            continue
        celdas = [c.strip() for c in linea.strip().strip("|").split("|")]
        if len(celdas) < 3:
            continue
        for trozo in re.split(r"→|/", celdas[2]):
            trozo = trozo.strip()
            if len(norm(trozo)) >= 3:
                out.append(trozo)
    return out


def parecido(a, b):
    return difflib.SequenceMatcher(None, norm(a), norm(b)).ratio()


def check(frases):
    pub = publicadas()
    for i, f in enumerate(frases):
        mejor = max(((parecido(f, p), p) for p in pub), default=(0, ""))
        if mejor[0] >= UMBRAL:
            print(f"REPETIDA ({mejor[0]:.2f}): «{f}» ≈ «{mejor[1]}»")
        for g in frases[i + 1:]:
            r = parecido(f, g)
            if r >= UMBRAL:
                print(f"PARECIDAS ENTRE SÍ ({r:.2f}): «{f}» ≈ «{g}»")


def add(fecha, formato, frase, archivos):
    with open(HIST, "a", encoding="utf-8") as h:
        h.write(f"| {fecha} | {formato} | {frase} | {archivos} |\n")


if __name__ == "__main__":
    if len(sys.argv) >= 3 and sys.argv[1] == "check":
        check(sys.argv[2:])
    elif len(sys.argv) == 6 and sys.argv[1] == "add":
        add(*sys.argv[2:])
    else:
        sys.exit(__doc__)

#!/usr/bin/env python3
"""Dónde viven los archivos que se publican (imágenes y vídeos de cada día).

Van en un repositorio PÚBLICO aparte, verdadysinfiltro/assets-vs, porque Instagram solo puede
descargarlos desde una URL pública. Este repositorio (código, marca y documentos) puede ser privado.
La carpeta local se espera junto a este repo (…/assets-vs); si falta, se clona sola.
Misma estructura de siempre: posts/AAAA-MM-DD/…
"""
import os
import subprocess

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REPO = "verdadysinfiltro/assets-vs"
ASSETS = os.environ.get("ASSETS_DIR", os.path.join(os.path.dirname(RAIZ), "assets-vs"))
RAW = f"https://raw.githubusercontent.com/{REPO}/main/"


def asegurar():
    """Clona assets-vs si no está y, si ya está, lo pone al día."""
    if os.path.isdir(os.path.join(ASSETS, ".git")):
        subprocess.run(["git", "-C", ASSETS, "pull", "-q", "--rebase", "origin", "main"], capture_output=True)
    else:
        subprocess.run(["git", "clone", "-q", "--depth", "1", f"https://github.com/{REPO}", ASSETS], check=True)
    return ASSETS


def local(ruta):
    """'posts/AAAA-MM-DD/x.mp4' → ruta real en el disco (dentro de assets-vs)."""
    return ruta if os.path.isabs(ruta) else os.path.join(ASSETS, ruta.lstrip("./"))

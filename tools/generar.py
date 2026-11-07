#!/usr/bin/env python3
"""Genera imágenes de @verdadysinfiltro sobre la plantilla oficial.

Uso:
  python3 tools/generar.py salida.png "Frase del post."
  python3 tools/generar.py --carrusel carpeta/ "Gancho" "Frase 2" ... "Cierre"
  python3 tools/generar.py --story salida.jpg "Frase"        (1080x1920)
Instagram solo acepta JPEG por API: usar extensión .jpg para publicar.
"""
import os
import sys

from PIL import Image, ImageDraw, ImageFont

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PLANTILLA = os.path.join(RAIZ, "brand", "plantilla.png")
FUENTE = os.path.join(RAIZ, "brand", "fonts", "MoreSugar-Thin.ttf")

ANCHO_MAX = 820      # ancho máximo del bloque de texto (px)
TAM = 88             # tamaño calibrado con los posts originales
TAM_MIN = 60
INTERLINEADO = 1.25
TRACKING = 2        # espaciado extra entre letras (px)
COLOR = (230, 230, 230)
CENTRO_Y = 663       # centro vertical del texto (calibrado con los originales)


def largo(texto, fuente):
    return fuente.getlength(texto) + TRACKING * max(len(texto) - 1, 0)


def escribir(dibujo, x, y, texto, fuente):
    for c in texto:
        dibujo.text((x, y), c, font=fuente, fill=COLOR)
        x += fuente.getlength(c) + TRACKING


def partir(texto, fuente, ancho):
    lineas, actual = [], ""
    for palabra in texto.split():
        prueba = (actual + " " + palabra).strip()
        if largo(prueba, fuente) <= ancho or not actual:
            actual = prueba
        else:
            lineas.append(actual)
            actual = palabra
    if actual:
        lineas.append(actual)
    return lineas


def lienzo(formato):
    base = Image.open(PLANTILLA).convert("RGB")
    if formato == "story":
        img = Image.new("RGB", (1080, 1920), (0, 0, 0))
        offset = (1920 - base.height) // 2
        img.paste(base, (0, offset))
        return img, offset
    return base, 0


def render(texto, salida, formato="post"):
    img, offset = lienzo(formato)
    dibujo = ImageDraw.Draw(img)
    tam = TAM
    while True:
        fuente = ImageFont.truetype(FUENTE, tam)
        lineas = partir(texto, fuente, ANCHO_MAX)
        alto_linea = int(tam * INTERLINEADO)
        if len(lineas) <= 5 or tam <= TAM_MIN:
            break
        tam -= 4
    y = offset + CENTRO_Y - (alto_linea * len(lineas)) // 2
    for linea in lineas:
        escribir(dibujo, (img.width - largo(linea, fuente)) / 2, y, linea, fuente)
        y += alto_linea
    os.makedirs(os.path.dirname(os.path.abspath(salida)), exist_ok=True)
    if salida.lower().endswith((".jpg", ".jpeg")):
        img.save(salida, quality=95)
    else:
        img.save(salida, optimize=True)
    return salida


if __name__ == "__main__":
    args = sys.argv[1:]
    if not args:
        sys.exit(__doc__)
    if args[0] == "--carrusel":
        carpeta, frases = args[1], args[2:]
        for i, frase in enumerate(frases, 1):
            print(render(frase, os.path.join(carpeta, f"{i:02d}.jpg")))
    elif args[0] == "--story":
        print(render(" ".join(args[2:]), args[1], "story"))
    else:
        print(render(" ".join(args[1:]), args[0]))

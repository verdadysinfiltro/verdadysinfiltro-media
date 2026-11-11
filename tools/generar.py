#!/usr/bin/env python3
"""Genera imágenes de @verdadysinfiltro sobre la plantilla oficial.

Uso:
  python3 tools/generar.py salida.png "Frase del post."
  python3 tools/generar.py --carrusel carpeta/ "Gancho" "Frase 2" ... "Cierre"
  python3 tools/generar.py --story salida.jpg "Frase"        (1080x1920)
  python3 tools/generar.py --reel prefijo "Golpe 1" "Golpe 2"  (1080x1920, dos imágenes:
      prefijo-a.jpg solo con el golpe 1 y prefijo-b.jpg con la frase entera y el cierre)
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


FIRMA = "- Vera"                       # seudónimo de la autora (decidido el 2026-11-11)
USUARIO = "@verdadysinfiltro"
FUENTE_FIRMA = os.path.join(RAIZ, "brand", "fonts", "MoreSugar-Regular.ttf")


def firmar(base):
    """Sustituye la firma '- @verdadysinfiltro' de la plantilla por "- Vera" y, debajo, el usuario."""
    d = ImageDraw.Draw(base)
    d.rectangle((0, 1270, 560, base.height), fill=(0, 0, 0))
    grande, chica = ImageFont.truetype(FUENTE_FIRMA, 50), ImageFont.truetype(FUENTE_FIRMA, 28)
    d.text((26, 1236), FIRMA, font=grande, fill=(205, 205, 205))
    d.text((30, 1298), USUARIO, font=chica, fill=(140, 140, 140))
    return base


def lienzo(formato):
    base = firmar(Image.open(PLANTILLA).convert("RGB"))
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


CIERRE = "Una frase cada noche. Sígueme."
TAM_CIERRE = 46
COLOR_CIERRE = (150, 150, 150)
HUECO = 0.45         # separación entre los dos golpes (en alturas de línea)


def render_reel(golpe1, golpe2, prefijo):
    """Reel en dos golpes: -a.jpg muestra solo el primero (mismo sitio que en -b.jpg)."""
    tam = TAM
    while True:
        fuente = ImageFont.truetype(FUENTE, tam)
        l1, l2 = partir(golpe1, fuente, ANCHO_MAX), partir(golpe2, fuente, ANCHO_MAX)
        alto_linea = int(tam * INTERLINEADO)
        if len(l1) + len(l2) <= 6 or tam <= TAM_MIN:
            break
        tam -= 4
    hueco = int(alto_linea * HUECO)
    alto = alto_linea * (len(l1) + len(l2)) + hueco
    salidas = []
    for sufijo, completo in (("a", False), ("b", True)):
        img, offset = lienzo("story")
        dibujo = ImageDraw.Draw(img)
        y = offset + CENTRO_Y - alto // 2
        for linea in l1:
            escribir(dibujo, (img.width - largo(linea, fuente)) / 2, y, linea, fuente)
            y += alto_linea
        y += hueco
        if completo:
            for linea in l2:
                escribir(dibujo, (img.width - largo(linea, fuente)) / 2, y, linea, fuente)
                y += alto_linea
            chica = ImageFont.truetype(FUENTE, TAM_CIERRE)
            ancho = chica.getlength(CIERRE)
            dibujo.text(((img.width - ancho) / 2, offset + CENTRO_Y + alto // 2 + 110), CIERRE,
                        font=chica, fill=COLOR_CIERRE)
        salida = f"{prefijo}-{sufijo}.jpg"
        os.makedirs(os.path.dirname(os.path.abspath(salida)), exist_ok=True)
        img.save(salida, quality=95)
        salidas.append(salida)
    return salidas


if __name__ == "__main__":
    args = sys.argv[1:]
    if not args:
        sys.exit(__doc__)
    if args[0] == "--carrusel":
        carpeta, frases = args[1], args[2:]
        for i, frase in enumerate(frases, 1):
            print(render(frase, os.path.join(carpeta, f"{i:02d}.jpg")))
    elif args[0] == "--reel":
        if len(args) != 4:
            sys.exit('Uso: generar.py --reel prefijo "Golpe 1" "Golpe 2"')
        print("\n".join(render_reel(args[2], args[3], args[1])))
    elif args[0] == "--story":
        print(render(" ".join(args[2:]), args[1], "story"))
    else:
        print(render(" ".join(args[1:]), args[0]))

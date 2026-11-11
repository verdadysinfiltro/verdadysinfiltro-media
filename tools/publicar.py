#!/usr/bin/env python3
"""Publica en Instagram (Graph API) usando las URLs raw públicas de assets-vs (ver tools/medios.py).

El token lo inyecta el proxy del entorno en graph.facebook.com; solo hace falta IG_USER_ID.

Uso:
  python3 tools/publicar.py imagen   posts/AAAA-MM-DD/x.jpg  caption.txt
  python3 tools/publicar.py carrusel posts/AAAA-MM-DD/carrusel/  caption.txt
  python3 tools/publicar.py story    posts/AAAA-MM-DD/x.jpg
  python3 tools/publicar.py reel     posts/AAAA-MM-DD/x.mp4  caption.txt
"""
import json
import os
import sys
import time
import urllib.parse
import urllib.request

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import medios  # noqa: E402

API = "https://graph.facebook.com/v21.0"
RAW = medios.RAW
IG = os.environ["IG_USER_ID"]


def llamar(metodo, ruta, **params):
    datos = urllib.parse.urlencode(params).encode() if metodo == "POST" else None
    url = f"{API}/{ruta}" + ("" if datos else "?" + urllib.parse.urlencode(params))
    req = urllib.request.Request(url, data=datos, method=metodo)
    try:
        with urllib.request.urlopen(req, timeout=120) as r:
            return json.load(r)
    except urllib.error.HTTPError as e:
        sys.exit(f"Error {e.code}: {e.read().decode()}")


MAX_HASHTAGS = 5


def limpiar_caption(texto):
    """Deja como máximo 5 hashtags y quita #verdadysinfiltro (nadie lo busca)."""
    vistos, salida = 0, []
    for linea in texto.splitlines():
        palabras = []
        for palabra in linea.split(" "):
            if palabra.startswith("#"):
                if palabra.lower().rstrip(".,") == "#verdadysinfiltro" or vistos >= MAX_HASHTAGS:
                    continue
                vistos += 1
            palabras.append(palabra)
        salida.append(" ".join(palabras).rstrip())
    return "\n".join(salida).strip()


def url_publica(ruta):
    return RAW + ruta.lstrip("./")


def esperar(contenedor, maximo=300):
    for _ in range(maximo // 5):
        estado = llamar("GET", contenedor, fields="status_code,status").get("status_code")
        if estado == "FINISHED":
            return
        if estado == "ERROR":
            sys.exit(f"Contenedor {contenedor} con error: {llamar('GET', contenedor, fields='status')}")
        time.sleep(5)
    sys.exit(f"Contenedor {contenedor} no terminó a tiempo")


def publicar(contenedor):
    esperar(contenedor)
    r = llamar("POST", f"{IG}/media_publish", creation_id=contenedor)
    enlace = llamar("GET", r["id"], fields="permalink").get("permalink", "")
    print(json.dumps({"id": r["id"], "permalink": enlace}))


def main():
    tipo, ruta = sys.argv[1], sys.argv[2]
    caption = limpiar_caption(open(medios.local(sys.argv[3]), encoding="utf-8").read()) if len(sys.argv) > 3 else ""
    if tipo == "imagen":
        c = llamar("POST", f"{IG}/media", image_url=url_publica(ruta), caption=caption)["id"]
    elif tipo == "story":
        c = llamar("POST", f"{IG}/media", image_url=url_publica(ruta), media_type="STORIES")["id"]
    elif tipo == "reel":
        extra = {}
        portada = ruta[:-4] + "-cover.jpg"
        if os.path.exists(medios.local(portada)):
            extra["cover_url"] = url_publica(portada)
        c = llamar("POST", f"{IG}/media", video_url=url_publica(ruta), media_type="REELS",
                   caption=caption, share_to_feed="true", **extra)["id"]
    elif tipo == "carrusel":
        hijos = []
        for f in sorted(os.listdir(medios.local(ruta))):
            if f.lower().endswith((".jpg", ".jpeg")):
                h = llamar("POST", f"{IG}/media", image_url=url_publica(os.path.join(ruta, f)),
                           is_carousel_item="true")["id"]
                esperar(h)
                hijos.append(h)
        c = llamar("POST", f"{IG}/media", media_type="CAROUSEL", children=",".join(hijos),
                   caption=caption)["id"]
    else:
        sys.exit(__doc__)
    publicar(c)


if __name__ == "__main__":
    main()

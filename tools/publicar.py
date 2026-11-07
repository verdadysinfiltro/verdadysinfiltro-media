#!/usr/bin/env python3
"""Publica en Instagram (Graph API) usando las URLs raw públicas de este repo.

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

API = "https://graph.facebook.com/v21.0"
RAW = "https://raw.githubusercontent.com/verdadysinfiltro/verdadysinfiltro-media/main/"
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
    caption = open(sys.argv[3], encoding="utf-8").read().strip() if len(sys.argv) > 3 else ""
    if tipo == "imagen":
        c = llamar("POST", f"{IG}/media", image_url=url_publica(ruta), caption=caption)["id"]
    elif tipo == "story":
        c = llamar("POST", f"{IG}/media", image_url=url_publica(ruta), media_type="STORIES")["id"]
    elif tipo == "reel":
        c = llamar("POST", f"{IG}/media", video_url=url_publica(ruta), media_type="REELS",
                   caption=caption, share_to_feed="true")["id"]
    elif tipo == "carrusel":
        hijos = []
        for f in sorted(os.listdir(ruta)):
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

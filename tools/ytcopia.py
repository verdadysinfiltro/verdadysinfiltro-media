#!/usr/bin/env python3
"""Resume la oficina de YouTube en el documento yt/estado de la oficina de Instagram.

Uso: python3 tools/ytcopia.py CARPETA salida.json
  CARPETA es el out_dir donde ArtifactData guardó el "query" de runs y el "list" de agents
  de la oficina de YouTube (subcarpetas runs/ y agents/). Escribe el JSON listo para un "set".
"""
import datetime
import glob
import json
import os
import sys


def leer(f):
    d = json.load(open(f, encoding="utf-8"))
    return d.get("data", d)


def main():
    carpeta, salida = sys.argv[1], sys.argv[2]
    runs = []
    for f in sorted(glob.glob(os.path.join(carpeta, "runs", "*.json")), reverse=True)[:10]:
        r = leer(f)
        runs.append({"date": r.get("date"), "label": r.get("label"),
                     "shorts": [{k: s.get(k) for k in ("title", "tipo", "format", "privacy", "url", "topic")}
                                for s in r.get("shorts", [])]})
    agentes = {}
    for f in glob.glob(os.path.join(carpeta, "agents", "*.json")):
        a = leer(f)
        agentes[os.path.basename(f)[:-5]] = {k: a.get(k) for k in ("status", "task", "updated")}
    ahora = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    json.dump({"agentes": agentes, "runs": runs, "updated": ahora,
               "fuente": "https://claude.ai/artifact/AuYQ4RurWfo27vi7K6vSSE"},
              open(salida, "w", encoding="utf-8"), ensure_ascii=False)
    print(f"{len(runs)} tandas, {len(agentes)} agentes -> {salida}")


if __name__ == "__main__":
    main()

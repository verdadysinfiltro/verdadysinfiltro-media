#!/usr/bin/env python3
"""Trabajo mecánico de la rutina de la noche (Instagram Graph API; el proxy pone el token).

Uso:
  python3 tools/noche.py publicar AAAA-MM-DD
      Publica posts/AAAA-MM-DD/reel-2035.mp4 (con su .txt) y story-2035.jpg; reintenta una vez.
  python3 tools/noche.py publicar1335 AAAA-MM-DD
      Igual, solo el reel de las 13:35 (rutina de mediodía).
  python3 tools/noche.py comentarios
      Lista en JSON compacto los comentarios recientes que la cuenta aún no ha respondido.
  python3 tools/noche.py responder respuestas.json
      respuestas.json = [{"id": "<comment-id>", "message": "..."}]. Publica las respuestas.
  python3 tools/noche.py metricas PERFIL.json METRICAS.json AAAA-MM-DD
      PERFIL.json y METRICAS.json son cuenta/perfil y metricas/actual guardados con out_dir
      (METRICAS.json puede no existir). Deja en /tmp/noche/batch/ metricas.json, perfil.json y
      serie.json para un "set", e imprime seguidores, mejor reel de 7 días, embudo e hitos.
      metricas.json lleva además:
        dias:   [{fecha, reach, visitas, seguidores?}] de 14 días (alcance y visitas al perfil de la
                cuenta por día; Instagram no da visitas ni seguidores por reel).
        embudo: {reach, visitas, visitas_por_1000, seguidores_ganados, seguidores_por_1000, dias}:
                cuánta gente pasa de ver un reel a entrar al perfil y a seguir.
      Cada reel lleva "estilo" (cine o clasico, ver tools/estilo.py).
"""
import datetime
import json
import os
import subprocess
import sys
import urllib.error
import urllib.parse
import urllib.request

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from estilo import MAD, estilo_de_fecha  # noqa: E402
import medios  # noqa: E402
API = "https://graph.facebook.com/v21.0"
IG = os.environ.get("IG_USER_ID", "")
CUENTA = "verdadysinfiltro"
OUT = "/tmp/noche/batch"
UMBRALES = [10, 25, 50, 100, 250, 500, 1000, 2500, 5000, 10000]
FASES = {1000: 2, 5000: 3, 10000: 4}


def api(ruta, metodo="GET", **p):
    datos = urllib.parse.urlencode(p).encode() if metodo == "POST" else None
    url = f"{API}/{ruta}" + ("" if datos else "?" + urllib.parse.urlencode(p))
    try:
        with urllib.request.urlopen(urllib.request.Request(url, data=datos, method=metodo), timeout=60) as r:
            return json.load(r)
    except urllib.error.HTTPError as e:
        raise RuntimeError(f"{e.code}: {e.read().decode()[:200]}")


def ahora():
    return datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def pub(tipo, ruta, cap=None):
    cmd = ["python3", "tools/publicar.py", tipo, ruta] + ([cap] if cap else [])
    err = ""
    for _ in range(2):
        r = subprocess.run(cmd, cwd=RAIZ, capture_output=True, text=True)
        if r.returncode == 0:
            return json.loads(r.stdout.strip().splitlines()[-1])
        err = (r.stderr or r.stdout)[-200:]
    return {"error": err}


def publicar(hoy, solo1335=False):
    medios.asegurar()   # los archivos del día están en assets-vs
    d = f"posts/{hoy}"
    res = {}
    piezas = [("reel-1335", "reel", f"{d}/reel-1335.mp4", f"{d}/reel-1335.txt")] if solo1335 else [
        ("reel-2035", "reel", f"{d}/reel-2035.mp4", f"{d}/reel-2035.txt"), ("story-2035", "story", f"{d}/story-2035.jpg", None)]
    for clave, tipo, ruta, cap in piezas:
        if not os.path.exists(medios.local(ruta)):
            res[clave] = {"error": f"falta {ruta}"}
            continue
        res[clave] = pub(tipo, ruta, cap)
        res[clave]["epoch"] = int(datetime.datetime.now().timestamp())
    print(json.dumps(res, ensure_ascii=False))


def medios(n=40):
    return api(f"{IG}/media", fields="id,timestamp,media_product_type,media_type,permalink,caption", limit=n).get("data", [])


def comentarios():
    pend = []
    for m in medios(15):
        for c in api(f"{m['id']}/comments", fields="id,text,username,timestamp,replies{username}").get("data", []):
            if c.get("username") == CUENTA:
                continue
            if any(r.get("username") == CUENTA for r in c.get("replies", {}).get("data", [])):
                continue
            pend.append({"id": c["id"], "user": c.get("username"), "text": (c.get("text") or "")[:220], "post": m.get("permalink")})
    print(json.dumps(pend, ensure_ascii=False))


def responder(fichero):
    ok, err = 0, []
    for r in json.load(open(fichero, encoding="utf-8")):
        try:
            api(f"{r['id']}/replies", "POST", message=r["message"])
            ok += 1
        except Exception as e:  # noqa: BLE001
            err.append(f"{r['id']}: {e}")
    print(json.dumps({"respondidos": ok, "errores": err}, ensure_ascii=False))


def insights(m):
    base = ["reach", "views", "shares", "saved", "likes", "comments"]
    if m.get("media_product_type") == "REELS":
        base.append("ig_reels_avg_watch_time")
    try:
        datos = api(f"{m['id']}/insights", metric=",".join(base)).get("data", [])
    except RuntimeError:
        datos = []
        for k in base:
            try:
                datos += api(f"{m['id']}/insights", metric=k).get("data", [])
            except RuntimeError:
                pass
    return {d["name"]: (d.get("values") or [{}])[0].get("value", d.get("total_value", {}).get("value", 0)) for d in datos}


def embudo(prev, seg, hoy):
    """Alcance y visitas al perfil de la cuenta por día (14 días) y seguidores de cada noche."""
    antes = {d["fecha"]: d for d in prev.get("dias", [])}
    fin = datetime.date.fromisoformat(hoy)
    dias = []
    for k in range(13, -1, -1):
        f = fin - datetime.timedelta(days=k)
        ini = datetime.datetime.combine(f, datetime.time(0), MAD)
        d = dict(antes.get(f.isoformat(), {}), fecha=f.isoformat())
        try:
            r = api(f"{IG}/insights", metric="reach,profile_views", period="day", metric_type="total_value",
                    since=int(ini.timestamp()), until=int((ini + datetime.timedelta(days=1)).timestamp()))
            v = {x["name"]: int(x.get("total_value", {}).get("value") or 0) for x in r.get("data", [])}
            # Instagram tarda en cerrar el día: no se pisa un dato bueno con un cero.
            d["reach"] = max(v.get("reach", 0), d.get("reach", 0))
            d["visitas"] = max(v.get("profile_views", 0), d.get("visitas", 0))
        except RuntimeError:
            d.setdefault("reach", 0)
            d.setdefault("visitas", 0)
        dias.append(d)
    dias[-1]["seguidores"] = seg
    reach, vis = sum(d["reach"] for d in dias), sum(d["visitas"] for d in dias)
    con = [d["seguidores"] for d in dias if "seguidores" in d]
    gan = con[-1] - con[0] if len(con) > 1 else 0
    por = lambda n: round(1000 * n / reach, 1) if reach else 0  # noqa: E731
    return dias, {"reach": reach, "visitas": vis, "visitas_por_1000": por(vis), "seguidores_ganados": gan,
                  "seguidores_por_1000": por(gan), "dias": len(con)}


def leer(f):
    if not f or not os.path.exists(f):
        return {}
    d = json.load(open(f, encoding="utf-8"))
    return d.get("data", d)


def metricas(perfil_f, metr_f, hoy):
    perfil, prev = leer(perfil_f), leer(metr_f)
    yo = api(IG, fields="followers_count,follows_count,media_count")
    seg, pubs = yo.get("followers_count", 0), yo.get("media_count", 0)
    lim = datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(days=14)
    items = []
    tipos = {"REELS": "reel", "CAROUSEL_ALBUM": "carrusel", "IMAGE": "imagen", "VIDEO": "reel"}
    for m in medios(40):
        t = datetime.datetime.strptime(m["timestamp"][:19], "%Y-%m-%dT%H:%M:%S").replace(tzinfo=datetime.timezone.utc)
        if t < lim or m.get("media_product_type") == "STORY":
            continue
        i = insights(m)
        reach = int(i.get("reach") or 0)
        sh, sv = int(i.get("shares") or 0), int(i.get("saved") or 0)
        items.append({"id": m["id"], "permalink": m.get("permalink"), "tipo": tipos.get(m.get("media_product_type"), tipos.get(m.get("media_type"), "imagen")),
                      "titulo": ((m.get("caption") or "").strip().splitlines() or [""])[0][:90], "fecha": m["timestamp"][:19] + "Z",
                      "reach": reach, "views": int(i.get("views") or 0), "shares": sh, "saved": sv, "likes": int(i.get("likes") or 0),
                      "comments": int(i.get("comments") or 0), "avg_watch_ms": int(i.get("ig_reels_avg_watch_time") or 0),
                      "nota": round((2 * sh + sv) / reach, 4) if reach else 0})
        if items[-1]["tipo"] == "reel":
            items[-1]["estilo"] = estilo_de_fecha(m["timestamp"])
    rec = prev.get("records", {"reach": 0, "shares": 0})
    for it in prev.get("items", []):
        rec["reach"] = max(rec.get("reach", 0), it.get("reach", 0))
        rec["shares"] = max(rec.get("shares", 0), it.get("shares", 0))
    hitos = []
    reels = [x for x in items if x["tipo"] == "reel"]
    if reels:
        top_r = max(reels, key=lambda x: x["reach"])
        top_s = max(reels, key=lambda x: x["shares"])
        if top_r["reach"] > rec.get("reach", 0) and rec.get("reach", 0) > 0:
            hitos.append(f"Récord de alcance: «{top_r['titulo']}» con {top_r['reach']} (antes {rec['reach']}) {top_r['permalink']}")
        if top_s["shares"] > rec.get("shares", 0) and top_s["shares"] >= 3:
            hitos.append(f"Récord de envíos: «{top_s['titulo']}» con {top_s['shares']} (antes {rec.get('shares', 0)}) {top_s['permalink']}")
        rec = {"reach": max(rec.get("reach", 0), top_r["reach"]), "shares": max(rec.get("shares", 0), top_s["shares"])}
    antes = int(perfil.get("seguidores") or 0)
    for u in UMBRALES:
        if antes < u <= seg:
            hitos.append(f"Seguidores: {seg} (has pasado de {u})" + (f" · empieza la fase {FASES[u]} de la hoja de ruta" if u in FASES else ""))
    os.makedirs(OUT, exist_ok=True)
    dias, emb = embudo(prev, seg, hoy)
    json.dump({"items": items, "records": rec, "dias": dias, "embudo": emb, "medido": ahora()},
              open(f"{OUT}/metricas.json", "w"), ensure_ascii=False)
    perfil.update({"seguidores": seg, "seguidos": yo.get("follows_count", perfil.get("seguidos", 0)),
                   "publicaciones": pubs, "updated": ahora()})
    json.dump(perfil, open(f"{OUT}/perfil.json", "w"), ensure_ascii=False)
    json.dump({"seguidores": seg, "publicaciones": pubs}, open(f"{OUT}/serie.json", "w"))
    semana = datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(days=7)
    rec7 = [x for x in reels if x["fecha"] >= semana.strftime("%Y-%m-%dT%H:%M:%S")]
    mejor = max(rec7, key=lambda x: x["nota"]) if rec7 else None
    print(json.dumps({"seguidores": seg, "antes": antes, "piezas_medidas": len(items), "hitos": hitos, "embudo": emb,
                      "mejor_reel_7d": mejor and {k: mejor[k] for k in ("titulo", "reach", "shares", "saved", "nota")}}, ensure_ascii=False))


if __name__ == "__main__":
    a = sys.argv[1:]
    if a[:1] == ["publicar"] and len(a) == 2:
        publicar(a[1])
    elif a[:1] == ["publicar1335"] and len(a) == 2:
        publicar(a[1], True)
    elif a == ["comentarios"]:
        comentarios()
    elif a[:1] == ["responder"] and len(a) == 2:
        responder(a[1])
    elif a[:1] == ["metricas"] and len(a) == 4:
        metricas(*a[1:])
    else:
        sys.exit(__doc__)

#!/usr/bin/env python3
"""Hace todo lo mecánico del día a partir del plan de la semana (rutina de la mañana).

Uso:
  python3 tools/dia.py preparar PLAN.json AAAA-MM-DD
      Imágenes (carrusel si toca, story, bases de reel), voz de Vera (F5), piano, reels y captions
      en posts/AAAA-MM-DD/, y un mosaico /tmp/dia/mosaico.jpg para revisar. Imprime un resumen JSON.
  python3 tools/dia.py publicar PLAN.json AAAA-MM-DD
      Añade las piezas a docs/historial.md, hace commit y push, publica el carrusel si toca y
      deja en /tmp/dia/batch/ los documentos para la oficina (posts y plan con done).
PLAN.json es plan/actual guardado con out_dir. Cada reel del plan: {g1, g2, tema, caption, hashtags};
el día puede llevar story, carrusel (7 frases), carrusel_caption y carrusel_hashtags.
"""
import datetime
import json
import os
import subprocess
import sys
import time
from zoneinfo import ZoneInfo

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TMP = "/tmp/dia"
MAD = ZoneInfo("Europe/Madrid")
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from estilo import estilo  # noqa: E402

VOZ_LINEA = "Voz generada con IA."


def sh(cmd, env=None, check=True):
    r = subprocess.run(cmd, cwd=RAIZ, capture_output=True, text=True, env={**os.environ, **(env or {})})
    if check and r.returncode:
        raise RuntimeError(f"{cmd[0]} {cmd[1] if len(cmd) > 1 else ''}: {(r.stderr or r.stdout)[-300:]}")
    return r.stdout.strip()


def leer_plan(ruta, hoy):
    d = json.load(open(ruta, encoding="utf-8"))
    d = d.get("data", d)
    dia = d.get("dias", {}).get(hoy)
    if not dia:
        sys.exit(json.dumps({"error": f"El plan no tiene el día {hoy}"}))
    return d, dia


def voces(hoy):
    # Desde el 2026-11-12 la cuenta tiene autora (Vera): todos los reels con voz de mujer.
    return ("F5", "F5")


def caption(texto, hashtags, con_voz):
    partes = [texto.strip()]
    if con_voz:
        partes.append(VOZ_LINEA)
    if hashtags:
        partes.append(hashtags.strip())
    return "\n\n".join(partes) + "\n"


def lleva_carrusel(hoy, dia):
    return bool(dia.get("carrusel")) and datetime.date.fromisoformat(hoy).isoweekday() in (1, 3, 7)


def preparar(plan, hoy):
    _, dia = leer_plan(plan, hoy)
    reels = dia.get("reels") or []
    faltan = [f"reels[{i}].{k}" for i, r in enumerate(reels) for k in ("g1", "g2", "caption", "hashtags") if not r.get(k)]
    if len(reels) < 2:
        faltan.append("reels (hacen falta 2)")
    if not dia.get("story"):
        faltan.append("story")
    if lleva_carrusel(hoy, dia) and not dia.get("carrusel_caption"):
        faltan.append("carrusel_caption")
    if faltan:
        sys.exit(json.dumps({"error": "Faltan campos en el plan: " + ", ".join(faltan)}, ensure_ascii=False))
    out = os.path.join("posts", hoy)
    os.makedirs(os.path.join(RAIZ, out), exist_ok=True)
    os.makedirs(TMP, exist_ok=True)
    res = {"dia": hoy, "voz": {}, "estilo": {}, "errores": [], "archivos": []}
    if lleva_carrusel(hoy, dia):
        sh(["python3", "tools/generar.py", "--carrusel", f"{out}/carrusel", *dia["carrusel"]])
        open(os.path.join(RAIZ, out, "carrusel.txt"), "w", encoding="utf-8").write(
            caption(dia["carrusel_caption"], dia.get("carrusel_hashtags", ""), False))
        res["archivos"].append(f"{out}/carrusel/")
    sh(["python3", "tools/generar.py", "--story", f"{out}/story-2035.jpg", dia["story"]])
    res["archivos"].append(f"{out}/story-2035.jpg")
    for n, (r, hora, voz, seg) in enumerate(zip(reels[:2], ("1335", "2035"), voces(hoy), (7, 11)), 1):
        base = f"{TMP}/r{n}"
        sh(["python3", "tools/generar.py", "--reel", base, r["g1"], r["g2"]])
        sh(["python3", "tools/piano.py", f"{TMP}/p{n}.wav", str(seg), f"{hoy}-{hora}"])
        env, con_voz = None, False
        for intento in range(2):
            try:
                j = json.loads(sh(["python3", "tools/voz.py", f"{TMP}/v{n}.wav", voz, r["g1"], r["g2"]]).splitlines()[-1])
                env, con_voz = {"VOZ": f"{TMP}/v{n}.wav", "T2": str(j["t2"]), "DUR": str(j["dur"])}, True
                break
            except Exception as e:  # noqa: BLE001
                err = str(e)
        if not con_voz:
            res["errores"].append(f"voz del reel {hora} ({voz}): {err[-200:]}")
        est = estilo(hoy, hora)
        if est == "cine":
            # Mitad de los reels: palabra a palabra sobre fondo en movimiento. Si falla, sale el clásico.
            try:
                sh(["python3", "tools/cine.py", f"{out}/reel-{hora}.mp4", f"{TMP}/p{n}.wav", f"{hoy}-{hora}", r["g1"], r["g2"], base], env=env)
            except Exception as e:  # noqa: BLE001
                res["errores"].append(f"reel cine {hora}: {str(e)[-200:]} (se montó el clásico)")
                sh(["python3", "tools/generar.py", "--reel", base, r["g1"], r["g2"]])
                est = "clasico"
        if est == "clasico":
            sh(["tools/reel.sh", f"{base}-a.jpg", f"{out}/reel-{hora}.mp4", f"{TMP}/p{n}.wav", "auto", f"{hoy}-{hora}", f"{base}-b.jpg"], env=env)
        res["estilo"][hora] = est
        open(os.path.join(RAIZ, out, f"reel-{hora}.txt"), "w", encoding="utf-8").write(
            caption(r["caption"], r["hashtags"], con_voz))
        res["voz"][hora] = voz if con_voz else "no"
        res["archivos"].append(f"{out}/reel-{hora}.mp4")
    frases = [f"{r['g1']} {r['g2']}" for r in reels[:2]] + [dia["story"]] + (dia["carrusel"][1:6] if lleva_carrusel(hoy, dia) else [])
    rep = sh(["python3", "tools/historial.py", "check", *frases])
    if rep:
        res["repetidas"] = rep.splitlines()
    mosaico(out, hoy, dia)
    res["mosaico"] = f"{TMP}/mosaico.jpg"
    json.dump(res, open(f"{TMP}/resumen.json", "w"), ensure_ascii=False)
    print(json.dumps(res, ensure_ascii=False))


def mosaico(out, hoy, dia):
    from PIL import Image
    fotos = [f"{TMP}/r1-a.jpg", f"{TMP}/r1-b.jpg", f"{TMP}/r2-a.jpg", f"{TMP}/r2-b.jpg", os.path.join(RAIZ, out, "story-2035.jpg")]
    car = os.path.join(RAIZ, out, "carrusel")
    if lleva_carrusel(hoy, dia) and os.path.isdir(car):
        fotos += [os.path.join(car, f) for f in sorted(os.listdir(car)) if f.endswith(".jpg")]
    w, h = 216, 384
    cols = 6
    filas = (len(fotos) + cols - 1) // cols
    lienzo = Image.new("RGB", (cols * w, filas * h), (40, 40, 40))
    for i, f in enumerate(fotos):
        im = Image.open(f).convert("RGB")
        im.thumbnail((w - 6, h - 6))
        lienzo.paste(im, ((i % cols) * w + 3, (i // cols) * h + 3))
    lienzo.save(f"{TMP}/mosaico.jpg", quality=80)


def utc(hoy, hm):
    h, m = map(int, hm.split(":"))
    d = datetime.datetime.combine(datetime.date.fromisoformat(hoy), datetime.time(h, m), MAD)
    return d.astimezone(datetime.timezone.utc)


def publicar(plan, hoy):
    datos, dia = leer_plan(plan, hoy)
    res = json.load(open(f"{TMP}/resumen.json"))
    out = f"posts/{hoy}"
    reels = dia["reels"]
    est = res.get("estilo", {})
    hist = [(f"reel 13:35 ({res['voz'].get('1335')}, {est.get('1335', 'clasico')})", f"{reels[0]['g1']} / {reels[0]['g2']}", f"{out}/reel-1335.mp4"),
            (f"reel 20:35 ({res['voz'].get('2035')}, {est.get('2035', 'clasico')})", f"{reels[1]['g1']} / {reels[1]['g2']}", f"{out}/reel-2035.mp4"),
            ("story 20:35", dia["story"], f"{out}/story-2035.jpg")]
    car = lleva_carrusel(hoy, dia)
    if car:
        hist.insert(0, ("carrusel 7:45", f"{dia['carrusel'][0]} → " + " / ".join(dia["carrusel"][1:]), f"{out}/carrusel/"))
    for formato, frase, archivo in hist:
        sh(["python3", "tools/historial.py", "add", hoy, formato, frase.replace("|", "/"), archivo])
    sh(["git", "add", out, "docs/historial.md"])
    sh(["git", "commit", "-q", "-m", f"Contenido del {hoy}"], check=False)
    for i in range(4):
        if subprocess.run(["git", "push", "-q", "origin", "HEAD:main"], cwd=RAIZ).returncode == 0:
            break
        subprocess.run(["git", "pull", "-q", "--rebase", "origin", "main"], cwd=RAIZ)
        time.sleep(2 ** (i + 1))
    else:
        res["errores"].append("git push falló 4 veces")
    piezas = []
    if car:
        time.sleep(20)
        estado, enlace = "publicado", ""
        try:
            r = json.loads(sh(["python3", "tools/publicar.py", "carrusel", f"{out}/carrusel", f"{out}/carrusel.txt"]))
            enlace = r.get("permalink", "")
        except Exception as e:  # noqa: BLE001
            try:
                r = json.loads(sh(["python3", "tools/publicar.py", "carrusel", f"{out}/carrusel", f"{out}/carrusel.txt"]))
                enlace = r.get("permalink", "")
            except Exception as e2:  # noqa: BLE001
                estado = "error"
                res["errores"].append(f"carrusel: {str(e2)[-200:]}")
        res["carrusel"] = {"estado": estado, "permalink": enlace}
        piezas.append(("carrusel", "carrusel", dia["carrusel"][0], dia.get("carrusel_tema", ""), None, "07:45", estado, f"{out}/carrusel/", enlace))
    piezas += [("reel-1335", "reel", f"{reels[0]['g1']} {reels[0]['g2']}", reels[0].get("tema", ""), res["voz"].get("1335"), "13:35", "programado", f"{out}/reel-1335.mp4", ""),
               ("reel-2035", "reel", f"{reels[1]['g1']} {reels[1]['g2']}", reels[1].get("tema", ""), res["voz"].get("2035"), "20:35", "programado", f"{out}/reel-2035.mp4", ""),
               ("story-2035", "story", dia["story"], "", None, "20:35", "programado", f"{out}/story-2035.jpg", "")]
    os.makedirs(f"{TMP}/batch", exist_ok=True)
    ids = []
    for sufijo, tipo, titulo, tema, voz, hm, estado, archivo, enlace in piezas:
        f = utc(hoy, hm)
        doc = {"titulo": titulo, "tipo": tipo, "tema": tema, "fecha": f.strftime("%Y-%m-%dT%H:%M:%SZ"),
               "estado": estado, "archivo": archivo, "orden": 2000000000 - int(f.timestamp())}
        if voz:
            doc["voz"] = voz
        if tipo == "reel":
            doc["estilo"] = res.get("estilo", {}).get(sufijo[-4:], "clasico")
        if enlace:
            doc["permalink"] = enlace
        ruta = f"{TMP}/batch/post-{hoy}-{sufijo}.json"
        json.dump(doc, open(ruta, "w", encoding="utf-8"), ensure_ascii=False)
        ids.append({"doc_id": f"{hoy}-{sufijo}", "file_path": ruta})
    dia["done"] = sorted(set(dia.get("done", []) + [p[0] for p in piezas]))
    json.dump(datos, open(f"{TMP}/batch/plan.json", "w", encoding="utf-8"), ensure_ascii=False)
    res["batch"] = {"posts": ids, "plan": f"{TMP}/batch/plan.json"}
    print(json.dumps(res, ensure_ascii=False))


if __name__ == "__main__":
    if len(sys.argv) != 4 or sys.argv[1] not in ("preparar", "publicar"):
        sys.exit(__doc__)
    {"preparar": preparar, "publicar": publicar}[sys.argv[1]](sys.argv[2], sys.argv[3])

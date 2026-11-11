#!/usr/bin/env python3
"""Clip: reel "cine" 1080x1920. La frase aparece palabra a palabra (al ritmo de la voz si la hay)
sobre un fondo en movimiento, con las estrellas y la firma de la plantilla.

Uso:
  python3 tools/cine.py salida.mp4 piano.wav SEMILLA "Golpe 1" "Golpe 2" [prefijo-previa]
  Con voz: VOZ=locucion.wav T2=<segundo del golpe 2> DUR=<duración> delante (los da tools/voz.py).
Guarda también <salida sin .mp4>-cover.jpg (frase entera) y, si se da prefijo-previa,
prefijo-a.jpg (primer fotograma) y prefijo-b.jpg (último) para el mosaico de revisión.

Fondo: si hay vídeos en brand/fondos/*.mp4 se usa uno (elegido por la semilla, oscurecido);
si no, luces desenfocadas que se mueven despacio (tres paletas, elegidas por la semilla).
"""
import glob
import os
import random
import subprocess
import sys
import wave
import zlib

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import generar as G  # noqa: E402

W, H, FPS = 1080, 1920, 30
FUNDIDO = 0.22            # segundos que tarda en aparecer cada palabra
PALETAS = {
    "ambar": [(255, 170, 80), (255, 120, 60), (255, 210, 140), (200, 90, 60)],
    "azul": [(90, 140, 255), (120, 200, 255), (150, 110, 255), (70, 110, 200)],
    "ciudad": [(255, 160, 90), (110, 160, 255), (255, 90, 120), (240, 220, 170)],
}


def duracion_wav(ruta):
    with wave.open(ruta) as w:
        return w.getnframes() / w.getframerate()


def maquetar(g1, g2):
    """Devuelve [(palabra, x, y, golpe)] y la geometría, con el mismo encaje que generar.py."""
    tam = G.TAM
    while True:
        fuente = ImageFont.truetype(G.FUENTE, tam)
        l1, l2 = G.partir(g1, fuente, G.ANCHO_MAX), G.partir(g2, fuente, G.ANCHO_MAX)
        alto_linea = int(tam * G.INTERLINEADO)
        if len(l1) + len(l2) <= 6 or tam <= G.TAM_MIN:
            break
        tam -= 4
    hueco = int(alto_linea * G.HUECO)
    alto = alto_linea * (len(l1) + len(l2)) + hueco
    offset = (H - Image.open(G.PLANTILLA).height) // 2
    y = offset + G.CENTRO_Y - alto // 2
    palabras = []
    espacio = fuente.getlength(" ") + G.TRACKING
    for golpe, lineas in ((1, l1), (2, l2)):
        for linea in lineas:
            x = (W - G.largo(linea, fuente)) / 2
            for p in linea.split():
                palabras.append((p, x, y, golpe))
                x += G.largo(p, fuente) + G.TRACKING + espacio
            y += alto_linea
        y += hueco if golpe == 1 else 0
    y_cierre = offset + G.CENTRO_Y + alto // 2 + 110
    return palabras, fuente, y_cierre


def mascara(texto, x, y, fuente, tracking=True):
    img = Image.new("L", (W, H), 0)
    d = ImageDraw.Draw(img)
    if tracking:
        for c in texto:
            d.text((x, y), c, font=fuente, fill=255)
            x += fuente.getlength(c) + G.TRACKING
    else:
        d.text((x, y), texto, font=fuente, fill=255)
    return np.asarray(img, dtype=np.uint16)


def tiempos(palabras, voz, t2, dur):
    """Segundo en que empieza a aparecer cada palabra (la primera, ya en el fotograma 0)."""
    if voz:
        fin1 = max(t2 - 0.6, 0.9)
        fin2 = max(min(duracion_wav(voz), dur) - 1.2, t2 + 0.6)
        tramos = {1: (0.4, fin1), 2: (t2, fin2)}
    else:
        tramos = {1: (0.0, 1.1), 2: (1.5, 2.9)}
    ts = []
    for g in (1, 2):
        ps = [p for p in palabras if p[3] == g]
        pesos = [len(p[0]) + 2 for p in ps]
        ini, fin = tramos[g]
        acum = 0
        for peso in pesos:
            ts.append(ini + (fin - ini) * acum / sum(pesos))
            acum += peso
    ts[0] = -1.0
    return ts, tramos[2][1]


class FondoLuces:
    """Dos capas de luces desenfocadas que se deslizan a distinta velocidad (paralaje)."""
    MX, MY = 200, 280     # margen de las capas (a media resolución) para poder moverlas

    def __init__(self, rnd, dur):
        self.nombre = rnd.choice(sorted(PALETAS))
        colores = PALETAS[self.nombre]
        self.capas = []
        for radios, n, brillo, desenfoque in (((7, 16), 46, 0.55, 2.5), ((26, 60), 16, 0.30, 5)):
            cw, ch = W // 2 + 2 * self.MX, H // 2 + 2 * self.MY
            capa = Image.new("RGB", (cw, ch), (0, 0, 0))
            for _ in range(n):
                r = rnd.randint(*radios)
                x, y = rnd.randint(-r, cw + r), rnd.randint(-r, ch + r)
                c = rnd.choice(colores)
                k = brillo * rnd.uniform(0.45, 1.0)
                luz = Image.new("RGB", (cw, ch), (0, 0, 0))
                ImageDraw.Draw(luz).ellipse((x - r, y - r, x + r, y + r), fill=tuple(int(v * k) for v in c))
                capa = Image.fromarray(np.maximum(np.asarray(capa), np.asarray(luz)))
            self.capas.append(capa.filter(ImageFilter.GaussianBlur(desenfoque)))
        ang = rnd.uniform(0, 6.283)
        # la capa lejana va despacio y la cercana, al revés y más rápido; nunca se sale del margen
        k = min(1.0, (self.MX - 10) / (22 * dur))
        self.vel = [(np.cos(ang) * 9 * k, np.sin(ang) * 14 * k), (-np.cos(ang) * 22 * k, -np.sin(ang) * 30 * k)]
        # viñeta: más oscuro en el centro, donde va el texto
        yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
        d = ((xx - W / 2) / (W * 0.62)) ** 2 + ((yy - H * 0.47) / (H * 0.40)) ** 2
        self.vin = (np.clip(0.30 + 0.70 * d, 0.30, 1.0) * 256).astype(np.uint16)[..., None]

    def frame(self, t):
        suma = np.zeros((H, W, 3), dtype=np.uint16)
        for capa, (vx, vy) in zip(self.capas, self.vel):
            dx, dy = self.MX + vx * t, self.MY + vy * t
            suma += np.asarray(capa.transform((W, H), Image.AFFINE, (0.5, 0, dx, 0, 0.5, dy), resample=Image.BILINEAR))
        respira = 0.92 + 0.08 * np.sin(t * 1.3)
        return (np.minimum(suma, 255) * self.vin * respira).astype(np.uint32) >> 8

    def cerrar(self):
        pass


class FondoVideo:
    """Un vídeo de brand/fondos/ recortado a 9:16, oscurecido y en bucle."""

    def __init__(self, ruta):
        self.nombre = os.path.basename(ruta)
        vf = f"scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H},fps={FPS},eq=brightness=-0.22:saturation=0.75,gblur=sigma=1.5"
        self.p = subprocess.Popen(["ffmpeg", "-loglevel", "error", "-stream_loop", "-1", "-i", ruta, "-vf", vf, "-an",
                                   "-f", "rawvideo", "-pix_fmt", "rgb24", "-"], stdout=subprocess.PIPE)

    def frame(self, t):
        crudo = self.p.stdout.read(W * H * 3)
        if len(crudo) < W * H * 3:
            raise RuntimeError(f"el fondo {self.nombre} no dio fotogramas")
        return (np.frombuffer(crudo, dtype=np.uint8).reshape(H, W, 3).astype(np.uint32) * 150) >> 8

    def cerrar(self):
        self.p.kill()


def main():
    if len(sys.argv) not in (6, 7):
        sys.exit(__doc__)
    salida, piano, semilla, g1, g2 = sys.argv[1:6]
    previa = sys.argv[6] if len(sys.argv) == 7 else None
    voz = os.environ.get("VOZ") or None
    t2 = float(os.environ.get("T2") or 1.5)
    dur = float(os.environ.get("DUR") or 6.5)
    rnd = random.Random(zlib.crc32(semilla.encode()))

    palabras, fuente, y_cierre = maquetar(g1, g2)
    ts, fin_voz = tiempos(palabras, voz, t2, dur)
    masc = [mascara(p, x, y, fuente) for p, x, y, _ in palabras]
    chica = ImageFont.truetype(G.FUENTE, G.TAM_CIERRE)
    m_cierre = mascara(G.CIERRE, (W - chica.getlength(G.CIERRE)) / 2, y_cierre, chica, tracking=False)
    t_cierre = fin_voz + 0.25
    lienzo, _ = G.lienzo("story")
    plantilla = np.asarray(lienzo, dtype=np.uint32)          # estrellas y firma sobre negro
    color = np.array(G.COLOR, dtype=np.int32)
    gris = np.array(G.COLOR_CIERRE, dtype=np.int32)

    videos = sorted(glob.glob(os.path.join(G.RAIZ, "brand", "fondos", "*.mp4")))
    fondo = FondoVideo(rnd.choice(videos)) if videos else FondoLuces(rnd, dur)

    fade = max(dur - 1, 0)
    if voz:
        audio = ["-i", piano, "-i", voz, "-filter_complex",
                 f"[1:a]aresample=44100,volume=0.3,afade=t=out:st={fade}:d=1[p];[2:a]aresample=44100[z];[p][z]amix=inputs=2:duration=first:normalize=0[a]",
                 "-map", "0:v", "-map", "[a]", "-b:a", "160k"]
    else:
        audio = ["-i", piano, "-map", "0:v", "-map", "1:a", "-af", f"afade=t=out:st={fade}:d=1", "-b:a", "128k"]
    os.makedirs(os.path.dirname(os.path.abspath(salida)), exist_ok=True)
    ff = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}",
                           "-r", str(FPS), "-i", "-", *audio, "-vf", "noise=alls=6:allf=t,format=yuv420p", "-t", str(dur),
                           "-r", str(FPS), "-c:v", "libx264", "-preset", "slow", "-crf", "20", "-c:a", "aac",
                           "-movflags", "+faststart", salida], stdin=subprocess.PIPE)
    n = round(dur * FPS)
    primero = ultimo = None
    try:
        for i in range(n):
            t = i / FPS
            f = np.maximum(fondo.frame(t), plantilla).astype(np.int32)
            m = np.zeros((H, W), dtype=np.uint16)
            for mk, t0 in zip(masc, ts):
                a = min(max((t - t0) / FUNDIDO, 0.0), 1.0)
                if a > 0:
                    m = np.maximum(m, (mk * a).astype(np.uint16))
            f += ((color - f) * m[..., None].astype(np.int32)) >> 8
            a = min(max((t - t_cierre) / 0.4, 0.0), 1.0)
            if a > 0:
                f += ((gris - f) * (m_cierre * a).astype(np.int32)[..., None]) >> 8
            cuadro = np.clip(f, 0, 255).astype(np.uint8)
            if i == 0:
                primero = cuadro
            ultimo = cuadro
            ff.stdin.write(cuadro.tobytes())
    finally:
        fondo.cerrar()
        ff.stdin.close()
    if ff.wait():
        sys.exit("ffmpeg falló al montar el reel cine")
    Image.fromarray(ultimo).save(salida[:-4] + "-cover.jpg", quality=92)
    if previa:
        Image.fromarray(primero).save(f"{previa}-a.jpg", quality=90)
        Image.fromarray(ultimo).save(f"{previa}-b.jpg", quality=90)
    print(f"{salida} (cine, fondo {fondo.nombre}, {dur}s)")


if __name__ == "__main__":
    main()

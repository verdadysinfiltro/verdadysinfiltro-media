#!/usr/bin/env python3
"""Qué estilo lleva cada reel: "cine" (texto palabra a palabra sobre fondo en movimiento,
tools/cine.py) o "clasico" (fondo negro en dos golpes, tools/reel.sh).

La mitad de los reels va en cada estilo. El hueco "cine" cambia cada dos días, así en cuatro
días se cruzan todas las combinaciones de hora (13:35/20:35), voz (F5/M5) y estilo, y Lupa
puede comparar estilos sin que se mezclen con la hora ni con la voz.

Uso: python3 tools/estilo.py AAAA-MM-DD   → {"1335": "cine", "2035": "clasico"}
"""
import datetime
import json
import sys
from zoneinfo import ZoneInfo

INICIO = "2026-11-12"   # primer día con reels "cine"
MAD = ZoneInfo("Europe/Madrid")


def estilo(hoy, hora):
    """hoy = AAAA-MM-DD (Madrid); hora = "1335" o "2035"."""
    if hoy < INICIO:
        return "clasico"
    cine = "1335" if (datetime.date.fromisoformat(hoy).timetuple().tm_yday // 2) % 2 == 0 else "2035"
    return "cine" if hora == cine else "clasico"


def estilo_de_fecha(iso_utc):
    """Estilo de un reel ya publicado a partir de su fecha UTC (la que da Instagram)."""
    t = datetime.datetime.strptime(iso_utc[:19], "%Y-%m-%dT%H:%M:%S").replace(tzinfo=datetime.timezone.utc).astimezone(MAD)
    return estilo(t.strftime("%Y-%m-%d"), "1335" if t.hour < 17 else "2035")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    print(json.dumps({h: estilo(sys.argv[1], h) for h in ("1335", "2035")}))

# verdadysinfiltro-media

Repo de la cuenta de Instagram @verdadysinfiltro: marca, estrategia, generador de imágenes e imágenes publicadas (URLs públicas raw).

Antes de crear contenido, leer:
- `docs/marca.md`: estética, voz, hashtags y caption.
- `docs/estrategia.md`: frecuencia, horarios, formatos y flujo de trabajo.
- `docs/historial.md`: todo lo publicado. No repetir, y añadir cada post nuevo.
- `docs/oficina.md`: agentes, calendario, rutinas y esquema de la base de datos de la oficina Sin Filtro HQ.

Imágenes: `tools/generar.py` (post, carrusel, story; JPEG para publicar). Reels: `tools/reel.sh`. Publicar: `tools/publicar.py` (token inyectado por el proxy en graph.facebook.com, necesita `IG_USER_ID`). Todo va en `posts/AAAA-MM-DD/`, con caption en un `.txt` del mismo nombre.

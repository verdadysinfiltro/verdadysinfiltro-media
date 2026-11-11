# verdadysinfiltro-media

Repo de la cuenta de Instagram @verdadysinfiltro: marca, estrategia, generador de imágenes e imágenes publicadas (URLs públicas raw).

**Rutina de la mañana: seguir `docs/rutina-manana.md` (manda sobre cualquier lista de pasos anterior).**

Antes de crear contenido, leer:
- `docs/marca.md`: estética, voz, hashtags y caption.
- `docs/estrategia.md`: frecuencia, horarios, formatos y flujo de trabajo.
- `docs/historial.md`: todo lo publicado. No repetir, y añadir cada post nuevo.
- `docs/oficina.md`: agentes, calendario, rutinas y esquema de la base de datos de la oficina Sin Filtro HQ.

Imágenes: `tools/generar.py` (carrusel, story y `--reel` para las dos imágenes de un reel en dos golpes; JPEG para publicar). Reels (agente Clip): `tools/piano.py` + `tools/reel.sh` (6,5 s, golpe 2 a los 1,5 s, variante de movimiento por semilla, grano, portada `-cover.jpg`); locución del reel de noche con `tools/voz.py` (Supertonic 3, voces F5 y M5; el caption debe decir "Voz generada con IA."). Publicar: `tools/publicar.py` (token inyectado por el proxy en graph.facebook.com, necesita `IG_USER_ID`; recorta el caption a 5 hashtags). Todo va en `posts/AAAA-MM-DD/`, con caption en un `.txt` del mismo nombre.

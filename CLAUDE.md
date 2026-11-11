# verdadysinfiltro-media

Repo de la cuenta de Instagram @verdadysinfiltro: marca, estrategia, generador de imágenes e imágenes publicadas (URLs públicas raw).

**Una sola fuente de reglas.** Cada rutina tiene su procedimiento completo en `docs/`: `rutina-manana.md`, `rutina-mediodia.md`, `rutina-noche.md` y `rutina-semanal.md`. Las tareas programadas solo dicen "clona el repo y sigue tu documento"; si algo cambia, se cambia en el documento, no en la tarea. Lo que debe cumplirse siempre (límite de palabras, carruseles en pausa) lo hace cumplir el código (`tools/dia.py`).

Antes de crear contenido, leer:
- `docs/marca.md`: estética, voz, hashtags y caption.
- `docs/estrategia.md`: frecuencia, horarios, formatos y flujo de trabajo.
- `docs/historial.md`: todo lo publicado. No leerlo entero: comprobar frases con `python3 tools/historial.py check "frase" …`.
- `docs/oficina.md`: agentes, calendario, rutinas y esquema de la base de datos de la oficina Sin Filtro HQ.
- `docs/ordenes.md`: órdenes que Rodrigo da al CEO desde la oficina y cómo las atiende cada rutina (`tools/ordenes.py`).

La autora de la cuenta es **Vera** (seudónimo): firma "- Vera" + @verdadysinfiltro en todas las imágenes. Imágenes: `tools/generar.py` (carrusel, story y `--reel` para las dos imágenes de un reel en dos golpes; JPEG para publicar). Reels (agente Clip): `tools/piano.py` + `tools/reel.sh` (6,5 s, golpe 2 a los 1,5 s, variante de movimiento por semilla, grano, portada `-cover.jpg`); la mitad de los reels son "cine" (`tools/cine.py`: palabra a palabra sobre fondo en movimiento; el reparto lo decide `tools/estilo.py`); locución de los dos reels con `tools/voz.py` con la voz de Vera, la autora (Supertonic 3, voz F5 de mujer; el caption debe decir "Voz generada con IA."). Publicar: `tools/publicar.py` (token inyectado por el proxy en graph.facebook.com, necesita `IG_USER_ID`; recorta el caption a 5 hashtags). Todo va en `posts/AAAA-MM-DD/`, con caption en un `.txt` del mismo nombre, pero esa carpeta vive en el repo público aparte `verdadysinfiltro/assets-vs` (carpeta `../assets-vs`; `tools/medios.py`), no en este.

Scripts que ahorran tokens: `tools/dia.py` (todo lo mecánico de la mañana desde el plan), `tools/noche.py` (publicar, comentarios, métricas y embudo de seguidores), `tools/historial.py` (repetidas) y `tools/ytcopia.py` (resumen de la oficina de YouTube). Leer la oficina con `out_dir` y mostrar solo el final de las salidas largas.

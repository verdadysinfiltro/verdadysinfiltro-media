# Rutina de la mañana (7:45, hora de Madrid)

Vigente desde el 2026-11-12. Sustituye a cualquier lista anterior. Nadie mira: decide tú, no preguntes, no lances subagentes y gasta poco: no leas documentación salvo que un paso lo pida, y muestra solo el final de las salidas largas (`| tail -3`).

Las frases, captions y hashtags de la semana los escribe Pluma el domingo en `plan/actual`. Esta rutina solo produce, revisa y publica.

1. `cd /home/user/verdadysinfiltro-media && git checkout -q main && git pull -q --rebase origin main`; `HOY=$(TZ=Europe/Madrid date +%F)`.
2. Oficina (ArtifactData, https://claude.ai/artifact/MsamUDTLQzWhcwz7qg2d2x), a la vez y con `out_dir: "/tmp/of"`: "get" de `plan/actual` y de `rutinas/manana`, y "list" de `agents` y de `ordenes`, y "get" de `flujo/actual`. Apunta las versiones que da el listado (sirven para `if_version`).
3. `python3 tools/dia.py preparar /tmp/of/plan/actual.json $HOY | tail -1` (unos 3 min: imágenes, voces alternas, piano, un reel clásico y otro "cine", y captions en `posts/$HOY/`).
   - Si dice "Faltan campos": escribe solo lo que falta en `/tmp/of/plan/actual.json` siguiendo `docs/marca.md` (lee solo las secciones necesarias) y repite.
   - Si trae "repetidas": cambia esas frases en el JSON por otras nuevas siguiendo `docs/marca.md` y repite.
4. Mira `/tmp/dia/mosaico.jpg` una sola vez. En las imágenes `-a` solo tiene que verse el golpe 1 (en el reel "cine", el de fondo con luces, solo la primera palabra: es normal); en `-b`, la frase entera y "Una frase cada noche. Sígueme." sin pisar la firma; nada cortado y como mucho 6 líneas. Si algo falla, acorta la frase en el JSON y repite el paso 3 (una vez como mucho).
5. `python3 tools/dia.py publicar /tmp/of/plan/actual.json $HOY | tail -1`. Añade al historial, sube al repositorio, publica el carrusel si toca y deja los documentos en `/tmp/dia/batch/`.
6. UN batch final:
   - Cada `posts/<doc_id>` con `file_path` de `batch.posts` (son nuevos: sin `if_version`).
   - `plan/actual` con "set" y `file_path` = `batch.plan`.
   - `rutinas/manana` con "set" {ultima: `date -u +%Y-%m-%dT%H:%M:%SZ`, estado: "ok" (o "error" si `errores` no está vacío), resumen: una línea}.
   - pluma, tinta y clip con "update" {status: "done", task: resumen de una línea, updated}.
   - Una entrada en `log` {t, agente: "clip", msg}, con id = la hora.
   - Si `errores` no está vacío, un documento nuevo en `correo` {t, de: "clip", tipo: "error", asunto, texto: qué falló y qué se hizo, leido: false}, con id = la hora cambiando ":" por "-" y "-error" al final.

7. Órdenes del CEO: sigue `docs/ordenes.md` con agentes `pluma,tinta,clip` (los ficheros ya están en `/tmp/of`) y añade sus documentos a un segundo batch.

Nunca muestres tokens. Termina con una sola línea: qué quedó listo y qué se publicó.

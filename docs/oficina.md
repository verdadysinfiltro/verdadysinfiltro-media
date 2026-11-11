# Oficina virtual: Grupo Iberu HQ (planta 42)

Oficina 3D dentro de una nave espacial oscura en órbita de la Tierra (cámara en perspectiva, sin techo). Cada departamento está en su sala de cristal a medida, con puertas automáticas y paredes con colisión; mesas en grupos enfrentadas; los trabajadores pasan casi todo el tiempo en su mesa y alguna vez van a la cafetería, al mirador o a un sofá, sin cruzarse. Texturas, muebles 3D (modelos glTF convertidos a `.json` con el búfer dentro, porque los artefactos no sirven `.gltf`/`.bin`) y cielo de reflejos `studio_env.jpg` en `oficina/assets/` (Poly Haven, CC0; Tierra y Luna de la NASA vía los ejemplos de Three.js); se publican junto a la página como `assets/...`. A la izquierda, el **correo** estilo Outlook (carpetas, búsqueda, lectura a panel completo, no leídos con borde neón verde); a la derecha, la **hoja de ruta** desplegable, la **agenda de hoy**, la **salud de las rutinas** y el **rendimiento de la semana**. Departamentos: **Departamento Meta** (Instagram, los agentes de abajo), **Departamento YouTube** (Organizador, Guionista, Miniaturista y Analista; sus datos se copian de la oficina de YouTube), **Tienda online** (Marco, Nora, Iris, Teo, Sol y Bruno, en pausa: Marco y Teo se activan en la fase 3, el resto en la fase 4 de `docs/hoja-de-ruta.md`), despacho del CEO (decorativo), recepción, cafetería, sala de reuniones y pantallas en vivo.

Oficina: https://claude.ai/artifact/MsamUDTLQzWhcwz7qg2d2x (se lee y escribe con la herramienta ArtifactData, url de arriba).
Copia del HTML: `oficina/index.html`.

## Agentes y qué hace cada uno
| Agente | Rol | Cuándo trabaja |
|---|---|---|
| Pluma | Frases en dos golpes siguiendo `docs/marca.md`. Plan semanal en `plan/actual` (domingo) y frases nuevas si faltan. Nunca repite (mira `docs/historial.md`). | Domingo y cada mañana |
| Tinta | Carruseles y story (`tools/generar.py`) y las dos imágenes base de cada reel (`--reel`). | Cada mañana |
| Clip | Editor de reels: 6,5 s en dos golpes, movimiento distinto por semilla, piano original y portada. Revisa primer fotograma (solo golpe 1) y último (frase entera + cierre). | Cada mañana |
| Eco | Caption (a quién enviarlo + 3–5 hashtags) y publicación con `tools/publicar.py`. | 7:45, 13:35 y 20:35 |
| Luna | Story de la noche y respuesta a comentarios nuevos. | 20:35 |
| Lupa | Métricas de cada pieza y seguidores cada noche; informe y aprendizajes el domingo. | Cada noche + domingo |
| Marco | En pausa hasta lanzar los cuadros. Solo apunta candidatas a cuadro. | — |

## Calendario (hora de Madrid)
| Día | 7:45 | 13:35 | 20:35 |
|---|---|---|---|
| Lunes | Carrusel | Reel | Reel + story |
| Martes | — | Reel | Reel + story |
| Miércoles | Carrusel | Reel | Reel + story |
| Jueves | — | Reel | Reel + story |
| Viernes | — | Reel | Reel + story |
| Sábado | — | Reel | Reel + story |
| Domingo | Carrusel | Reel | Reel + story |

Semana: 14 reels, 3 carruseles, 7 stories.

## Archivos de cada día (`posts/AAAA-MM-DD/`)
`reel-1335.mp4`, `reel-2035.mp4` (cada uno con `-cover.jpg` y `.txt` de caption), `story-2035.jpg` y, si toca, `carrusel/01.jpg…07.jpg` + `carrusel.txt`.

## Cómo se monta un reel
```
python3 tools/generar.py --reel /tmp/r1 "Golpe 1" "Golpe 2"      # crea /tmp/r1-a.jpg y /tmp/r1-b.jpg
python3 tools/piano.py /tmp/p1.wav 7 $HOY-1335                    # semilla distinta por reel
tools/reel.sh /tmp/r1-a.jpg posts/$HOY/reel-1335.mp4 /tmp/p1.wav auto $HOY-1335 /tmp/r1-b.jpg
```

## Rutinas en la nube (tareas programadas, todas con Sonnet)
- **Sin Filtro · mañana** (diaria 7:45): crea TODO el contenido del día, lo sube a `posts/AAAA-MM-DD/` y publica el carrusel si toca.
- **Sin Filtro · mediodía** (diaria 13:35): publica `reel-1335`.
- **Sin Filtro · noche** (diaria 20:35): publica `reel-2035` y la story, responde comentarios y guarda métricas.
- **Sin Filtro · semanal** (domingo 7:15, antes de la de mañana): informe, aprendizajes y plan de la semana siguiente.

## Base de datos de la oficina
- `agents/<id>`: {status: working|done|idle, task, updated (ISO UTC)}.
- `posts/<id>`: {titulo, tipo: carrusel|reel|story, tema, fecha (ISO UTC), estado: programado|publicado|emitida|error, orden, archivo, permalink, metricas: {reach, views, shares, saved, likes, comments, avg_watch_ms, nota, medido}}. En reels, `titulo` = "Golpe 1 Golpe 2". `orden`: fijadas 1–3; nuevos = 2000000000 − epoch(segundos) (lo más nuevo sale primero en el muro).
- `cuenta/perfil`: {seguidores, publicaciones, cuadros, meta}.
- `log/<id>`: {t (ISO UTC), agente, msg}; id = hora.
- `cerebro/marca`, `cerebro/estrategia`, `cerebro/publicar`, `cerebro/reels`, `cerebro/aprendizajes`: reglas (mandan sobre lo demás si chocan; `aprendizajes` lo actualiza Lupa).
- `yt/estado`: copia de solo lectura de la oficina de YouTube (https://claude.ai/artifact/AuYQ4RurWfo27vi7K6vSSE): {agentes: {organizador|guionista|miniaturista|analista: {status, task, updated}}, runs: [últimas 10 tandas {date, label, shorts: [{title, tipo, format, privacy, url, topic}]}], updated, fuente}. La reescribe con "set" la rutina de la noche (`tools/ytcopia.py`). Nunca se escribe en la oficina de YouTube.
- `correo/<hora-con-guiones>-<palabra>`: {t, de (id del agente), tipo: error|hito|informe|tarea, asunto, texto, leido}. Lo escriben las rutinas solo cuando hay algo importante (errores, hitos, informe del domingo, tareas para Rodrigo); la página marca `leido`.
- `rutinas/{manana|mediodia|noche|semanal}`: {ultima (ISO UTC), estado: ok|error, resumen}. Cada rutina lo reescribe al terminar; la salud de YouTube se deduce de `yt/estado`.
- `metricas/actual`: {items: [{id, permalink, tipo, titulo, fecha, reach, views, shares, saved, likes, comments, avg_watch_ms, nota}] de las piezas de 14 días, records: {reach, shares}, medido}. Lo reescribe `tools/noche.py metricas` cada noche (sustituye a guardar métricas post por post).
- `serie/AAAA-MM-DD`: {seguidores, publicaciones}; un punto por noche (rutina de noche) para la gráfica de seguidores.
- `plan/actual`: {week (domingo AAAA-MM-DD), dias: {AAAA-MM-DD: {carrusel?: [7 frases], reels: [{g1, g2, tema}, {g1, g2, tema}] (mediodía, noche), story: frase, done: []}}}.

## Sesión de trabajo
- **Sin Filtro · mañana** se ejecuta en la sesión fija "Sin Filtro · oficina (no borrar)" (`session_01THrf6QwLmYWXKRir16LpNz`), la única con permiso de push a `main` (lo necesita para subir las imágenes del día y que tengan URL pública). No borrar ni archivar esa sesión.
- Mediodía, noche y semanal abren una sesión nueva cada vez: clonan el repo (público), publican con lo ya subido y escriben en la oficina; no necesitan push.

## Preferencia de Rodrigo
Las rutinas trabajan en silencio: no responder con resúmenes, avisos ni mensajes finales (gastan tokens). Solo ejecutar y dejar el registro en la oficina (`log`, `agents`, `posts`).

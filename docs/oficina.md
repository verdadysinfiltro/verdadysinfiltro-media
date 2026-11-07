# Oficina virtual: Sin Filtro HQ

Oficina: https://claude.ai/artifact/MsamUDTLQzWhcwz7qg2d2x (se lee y escribe con la herramienta ArtifactData, url de arriba).
Copia del HTML: `oficina/index.html`.

## Agentes y qué hace cada uno
| Agente | Rol | Cuándo trabaja |
|---|---|---|
| Pluma | Frases. Plan semanal en `plan/actual` (domingo) y frases nuevas si faltan. Nunca repite (mira `docs/historial.md`). | Domingo y cada mañana |
| Tinta | Imágenes (`tools/generar.py`) y reels (`tools/piano.py` + `tools/reel.sh`) hasta que exista un editor de vídeo. | Cada mañana |
| Eco | Caption de 1–3 líneas + llamada a la acción + 8–15 hashtags inventados según la frase. Publica con `tools/publicar.py`. | 7:45, 13:30 y 20:30 |
| Luna | 3 stories al día y respuesta a comentarios nuevos (cada noche). Encuestas y cajas de preguntas: a mano (la API no lo permite). | 7:45, 13:30 y 20:30 |
| Lupa | Métricas: seguidores en `cuenta/perfil`, alcance, guardados y envíos de cada post; aprendizajes en `cerebro/aprendizajes`. | Cada noche + informe del domingo |
| Marco | En pausa hasta lanzar los cuadros (y la serie 01). Solo apunta candidatas a cuadro. | — |

## Calendario (hora de Madrid)
| Día | 7:45 | 13:30 | 20:30 |
|---|---|---|---|
| Lunes | Carrusel + story | Story | Reel + story |
| Martes | Story | Imagen + story | Reel + story |
| Miércoles | Carrusel + story | Story | Reel + story |
| Jueves | Carrusel + story | Story | Reel + story |
| Viernes | Story | Story | Reel + story |
| Sábado | Story | Story | Reel + story |
| Domingo | Carrusel + story | Story | Reel + story |

Semana: 7 reels, 4 carruseles, 1 imagen, 21 stories (≈ 58% / 33% / 8% del feed).

## Rutinas en la nube (tareas programadas)
- **Sin Filtro · mañana** (diaria 7:45): crea TODO el contenido del día, lo sube a `posts/AAAA-MM-DD/`, publica carrusel (si toca) y story de la mañana.
- **Sin Filtro · mediodía** (diaria 13:30): imagen (martes) y story de mediodía.
- **Sin Filtro · noche** (diaria 20:30): reel, story de noche, respuestas a comentarios y métricas.
- **Sin Filtro · semanal** (domingo 7:15, antes de la de mañana): informe, aprendizajes y plan de la semana siguiente.

## Base de datos de la oficina
- `agents/<id>`: {status: working|done|idle, task, updated (ISO UTC)}.
- `posts/<id>`: {titulo, tipo: carrusel|imagen|reel|story, fecha (ISO UTC), estado: programado|publicado|error, orden, archivo, url, permalink, metricas}. `orden`: fijadas 1–3; nuevos = 2000000000 − epoch(segundos) (lo más nuevo sale primero en el muro).
- `cuenta/perfil`: {seguidores, publicaciones, cuadros, meta}.
- `log/<id>`: {t (ISO UTC), agente, msg}; id = hora.
- `cerebro/marca`, `cerebro/estrategia`, `cerebro/publicar`, `cerebro/aprendizajes`: reglas (mandan sobre lo demás si chocan; `aprendizajes` lo actualiza Lupa).
- `plan/actual`: {week (lunes AAAA-MM-DD), dias: {lun..dom: {carrusel?: [frases], imagen?: frase, reel: frase, stories: [3 frases]}}, done por pieza}.

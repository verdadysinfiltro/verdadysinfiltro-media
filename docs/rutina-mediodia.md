# Rutina del mediodía (13:35, hora de Madrid)

> Los comandos `git clone` y `python3 tools/…` de este documento están también escritos en la tarea programada "Sin Filtro · mediodía" y se ejecutan desde allí (si solo estuvieran aquí, el sistema los bloquearía). Si cambias uno, cámbialo en los dos sitios.

Procedimiento completo de la tarea programada "Sin Filtro · mediodía". Nadie mira: no preguntes, no narres, no lances subagentes, no leas más documentación (salvo `docs/ordenes.md` en el paso 3b) y muestra solo el final de las salidas largas. Nunca muestres tokens.

1. `HOY=$(TZ=Europe/Madrid date +%F)` (el repo ya está clonado en `/home/user/verdadysinfiltro-media`).
2. `python3 tools/noche.py publicar1335 $HOY` → JSON con `reel-1335`: {id, permalink, epoch} o {error} (ya reintenta solo).
3. Carga ArtifactData con ToolSearch ("select:ArtifactData"). Oficina: https://claude.ai/artifact/MsamUDTLQzWhcwz7qg2d2x. A la vez: "get" de `posts/$HOY-reel-1335`, `agents/eco` y `rutinas/mediodia` (para sus versiones), y con `out_dir: "/tmp/of"`: "list" de `ordenes` y "get" de `flujo/actual`.
3b. Órdenes del CEO: lee `docs/ordenes.md` y haz sus pasos 2 a 4 con el agente `eco` (los ficheros ya están en `/tmp/of`); sus documentos entran en el batch del paso 4.
4. UN batch (`if_version` en los que existen; hora real con `date -u +%Y-%m-%dT%H:%M:%SZ`):
   - `posts/$HOY-reel-1335` "update" {estado: "publicado", permalink, media_id: id, orden: 2000000000 − epoch} o {estado: "error"}. Si no existía, "set" con {titulo: "reel 13:35", tipo: "reel", estado, permalink, orden}.
   - `agents/eco` "update" {status: "idle", task: "Siguiente: reel 20:35", updated}.
   - `rutinas/mediodia` "set" {ultima, estado: "ok" o "error", resumen: una línea}.
   - `log/<hora>` {t, agente: "eco", msg}.
   - Solo si hubo error: `correo/<hora con ":" cambiados por "-">-error` con {t, de: "eco", tipo: "error", asunto, texto: qué falló, leido: false}.

No escribas ningún mensaje final.

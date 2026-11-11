# Rutina de la noche (20:35, hora de Madrid)

Procedimiento completo de la tarea programada "Sin Filtro · noche". Nadie mira: no preguntes, no narres, no lances subagentes, no leas más documentación (salvo `docs/ordenes.md` en el paso 5b) y muestra solo el final de las salidas largas. Nunca muestres tokens.

1. `HOY=$(TZ=Europe/Madrid date +%F)` (el repo ya está clonado en `/home/user/verdadysinfiltro-media`).
2. Carga ArtifactData con ToolSearch ("select:ArtifactData"). Oficina: https://claude.ai/artifact/MsamUDTLQzWhcwz7qg2d2x. A la vez, todo con `out_dir: "/tmp/of"`: "get" de `cuenta/perfil`, `metricas/actual`, `rutinas/noche`, `yt/estado`, `flujo/actual`, `posts/$HOY-reel-2035` y `posts/$HOY-story-2035`, y "list" de `agents` y de `ordenes`. En la oficina de YouTube (https://claude.ai/artifact/AuYQ4RurWfo27vi7K6vSSE, solo lectura, NUNCA escribas en ella), con `out_dir: "/tmp/yt"`: "query" de `runs` (limit 10, order_by date desc) y "list" de `agents`. Apunta las versiones de los listados.
3. Eco y Luna publican: `python3 tools/noche.py publicar $HOY` → JSON con reel-2035 y story-2035 ({id, permalink, epoch} o {error}).
4. Luna: `python3 tools/noche.py comentarios` da los comentarios sin responder. Para cada uno (salvo spam, insultos o la propia cuenta) escribe una respuesta corta, cercana, de tú, en español de España, distinta de las demás y con un emoji como mucho; si preguntan por cuadros o láminas: "Todavía no, pero te aviso cuando salgan". Guárdalas en `/tmp/resp.json` como `[{"id","message"}]` y ejecuta `python3 tools/noche.py responder /tmp/resp.json`.
5. Lupa: `python3 tools/noche.py metricas /tmp/of/cuenta/perfil.json /tmp/of/metricas/actual.json $HOY` (deja `/tmp/noche/batch/metricas.json`, `perfil.json` y `serie.json`, e imprime seguidores, mejor reel de 7 días e hitos). Luego `python3 tools/ytcopia.py /tmp/yt /tmp/noche/batch/yt.json`.
5b. Órdenes del CEO: lee `docs/ordenes.md` y haz sus pasos 2 a 4 con los agentes `eco,luna,lupa` (los ficheros ya están en `/tmp/of`); sus documentos entran en el batch del paso 6.
6. UN batch final (`if_version` en los que existen; hora real con `date -u +%Y-%m-%dT%H:%M:%SZ`):
   - `posts/$HOY-reel-2035` "update" {estado: "publicado", permalink, media_id, orden: 2000000000 − epoch} o {estado: "error"}; `posts/$HOY-story-2035` "update" {estado: "emitida"} o {estado: "error"}.
   - `metricas/actual`, `cuenta/perfil`, `serie/$HOY` (nuevo) y `yt/estado` con "set" y `file_path` de `/tmp/noche/batch/` (metricas.json, perfil.json, serie.json, yt.json).
   - `rutinas/noche` "set" {ultima, estado: "ok" o "error", resumen: una línea}.
   - eco, luna y lupa "update" {status: "idle", task: "Siguiente: mañana 7:45", updated}; clip "update" {status: "idle", task: "Esperando las frases de mañana", updated}.
   - `log/<hora>-luna` {t, agente: "luna", msg: cuántos comentarios respondió} y `log/<hora>-lupa` {t, agente: "lupa", msg: seguidores y mejor reel de 7 días con alcance, envíos y guardados}.
   - Correo (id = hora con ":" cambiados por "-" más "-" y una palabra; datos {t, de, tipo, asunto, texto, leido: false}) SOLO si: tipo "error" (de eco: algo no se publicó o falló, qué y qué se hizo); tipo "hito" (de lupa: uno por cada hito que imprimió el paso 5, con las cifras); tipo "tarea" (de luna: un comentario que pregunta por cuadros o que Rodrigo debería leer, citándolo con el enlace del post). Si todo fue normal, ningún correo. Los correos de las órdenes del paso 5b van además.

No escribas ningún mensaje final.

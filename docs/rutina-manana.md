# Rutina de la mañana (7:45, hora de Madrid)

Procedimiento vigente desde el 2026-11-10. **Sustituye a cualquier lista de pasos anterior** (ya no hay imagen suelta ni stories de mañana y mediodía; son 2 reels en dos golpes, 1 story de noche y carrusel lunes, miércoles y domingo). Nadie está mirando: decide tú, no hagas preguntas, sé breve y no lances subagentes.

## Preparación
1. `cd /home/user/verdadysinfiltro-media && git checkout -q main && git pull -q --rebase origin main`.
2. Lee `docs/marca.md`, `docs/oficina.md` y `docs/historial.md`.
3. Oficina (ArtifactData, https://claude.ai/artifact/MsamUDTLQzWhcwz7qg2d2x): a la vez, "get" de `cerebro/aprendizajes` y `plan/actual`, y "list" de `agents`. Pasa siempre `if_version` al escribir documentos existentes.
4. `HOY=$(TZ=Europe/Madrid date +%F)`, `DIA=$(TZ=Europe/Madrid date +%u)`. Horas de registro SIEMPRE con `date -u +%Y-%m-%dT%H:%M:%SZ`. Hora UTC de una hora de Madrid: `date -u -d "TZ=\"Europe/Madrid\" $HOY 20:35" +%Y-%m-%dT%H:%M:%SZ`.

## Pasos
a) **Oficina:** UN batch con pluma, tinta y clip en working.
b) **Pluma:** piezas de hoy = 2 reels (mediodía y noche, cada uno `{g1, g2, tema}`), 1 story de noche y, si DIA es 1, 3 o 7, un carrusel de 7 diapositivas. Usa lo que haya en `plan/actual.dias[HOY]` que no esté en `done`; lo que falte, escríbelo siguiendo "Cómo se escribe una frase de reel" de `docs/marca.md`. Comprueba cada frase contra `docs/historial.md`: ni repetida ni casi igual. Si una frase del plan incumple las reglas, mejórala. Aplica `cerebro/aprendizajes`.
c) **Tinta:** en `posts/$HOY/`: `carrusel/` si toca (`python3 tools/generar.py --carrusel posts/$HOY/carrusel "f1" … "f7"`), `story-2035.jpg` (`--story`) y las bases de los reels: `python3 tools/generar.py --reel /tmp/r1 "g1" "g2"` y lo mismo con `/tmp/r2`.
d) **Clip**, para cada reel (1 = 1335, 2 = 2035): `python3 tools/piano.py /tmp/p1.wav 7 $HOY-1335` y `tools/reel.sh /tmp/r1-a.jpg posts/$HOY/reel-1335.mp4 /tmp/p1.wav auto $HOY-1335 /tmp/r1-b.jpg` (igual con r2, p2 y 2035). Deben durar 6,5 s y dejar `reel-XXXX-cover.jpg`.
e) **Revisión**, una sola ronda: UN mosaico con las cuatro bases de reel, la story y las diapositivas. En `-a` solo el golpe 1; en `-b` la frase entera y "Una frase cada noche. Sígueme." sin pisar la firma; texto legible, sin cortes, máximo 6 líneas. Corrige lo que falle (acorta la frase si hace falta).
f) **Eco:** captions `carrusel.txt`, `reel-1335.txt` y `reel-2035.txt`: línea 1 dice a quién enviárselo (concreto, sin repetir la frase), línea 2 opcional "Guárdalo…", línea en blanco y 3–5 hashtags del tema. Nunca #verdadysinfiltro.
g) Añade las piezas a `docs/historial.md` (reels como `reel 13:35 | g1 / g2`), commit y `git push origin HEAD:main` (`git pull --rebase` si falla). Espera 20 s.
h) Si hay carrusel: `python3 tools/publicar.py carrusel posts/$HOY/carrusel posts/$HOY/carrusel.txt`. Si falla, reintenta una vez y anota el error.
i) **Oficina**, UN batch final: `posts/<id>` (ids: `HOY-carrusel`, `HOY-reel-1335`, `HOY-reel-2035`, `HOY-story-2035`) con `{titulo (reels: "g1 g2"), tipo, tema, fecha UTC de su hora, estado ("publicado" con permalink para el carrusel; "programado" lo demás; "error" si falló), archivo, orden = 2000000000 − epoch de su fecha}`; `plan/actual` con las piezas hechas en `done`; una entrada en `log` por agente `{t, agente, msg}`; pluma, tinta y clip en done con resumen de una línea; eco en idle con "Siguiente: reel 13:35"; luna y lupa en idle con "Siguiente: 20:35".

Nunca muestres tokens. Termina con una sola línea: qué quedó listo y qué se publicó.

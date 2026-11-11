# Estrategia de publicación

Decidida el 2026-11-10 con los datos reales de la cuenta (6 seguidores): los reels llegan a 130–200 personas que no siguen la cuenta; fotos y carruseles, a 0–3. Casi nadie envía ni guarda y solo 5 de 664 personas visitaron el perfil. Objetivo: reels que se vean enteros, se envíen y den motivo para seguir.

## Frecuencia (hora de Madrid)
- **Reels:** 2 al día, 13:35 y 20:35.
- **Carruseles:** 3 por semana (lunes, miércoles y domingo, 7:45).
- **Imágenes sueltas:** ninguna.
- **Stories:** 1 al día, 20:35 (solo las ven los seguidores; subir a 3 cuando haya más de 500).

## Reel (Clip)
- 6,5 s, 1080×1920, frase en dos golpes: el golpe 1 se ve desde el primer fotograma; a los 1,5 s aparece el golpe 2 y, debajo, "Una frase cada noche. Sígueme.".
- `tools/generar.py --reel` + `tools/piano.py` + `tools/reel.sh` (ver `docs/oficina.md`).
- Portada: la frase entera (`-cover.jpg`).
- **Dos estilos, mitad y mitad (desde el 2026-11-12):** cada día un reel es "clásico" (lo de arriba: fondo negro, dos golpes, `tools/reel.sh`) y el otro "cine" (`tools/cine.py`): la frase aparece palabra a palabra al ritmo de la voz sobre un fondo de luces desenfocadas en movimiento, con las estrellas y la firma de siempre. Qué hueco lleva cada estilo lo decide `tools/estilo.py` (cambia cada dos días para cruzarse con la hora y con la voz); `tools/dia.py` lo aplica solo y, si el cine falla, monta el clásico. Si se dejan vídeos propios en `brand/fondos/*.mp4` (verticales, sin gente reconocible, con licencia para usarlos), el cine los usa de fondo en lugar de las luces.
- **Voz (desde el 2026-11-12):** todos los reels llevan locución con la voz de Vera: mujer F5 (`tools/voz.py`, Supertonic 3). Ya no se alterna con la voz de hombre. El golpe 2 aparece cuando lo dice la voz. El caption lleva la línea "Voz generada con IA." (condición de la licencia OpenRAIL del modelo).

## Qué se mide (Lupa)
- Por pieza: alcance, visualizaciones, envíos, guardados, likes, comentarios y, en reels, tiempo medio de visionado.
- **Nota de una pieza = (2 × envíos + guardados) / alcance.** Es lo que decide qué se repite.
- **Embudo de seguidores (lo que importa en la fase 1):** de cada 1.000 personas alcanzadas, cuántas entran al perfil y cuántas siguen. Instagram no da visitas ni seguidores por reel, así que se mide por día en la cuenta: `metricas/actual.dias` ({fecha, reach, visitas, seguidores}) y `metricas/actual.embudo` ({visitas_por_1000, seguidores_por_1000, seguidores_ganados}), que escribe `tools/noche.py metricas` cada noche. Punto de partida (7–10 nov): 7,5 visitas por 1.000 de alcance. Objetivo: 15 visitas y 3 seguidores nuevos por cada 1.000.
- **Informe del domingo (Lupa), además de lo de siempre:** (1) el embudo de la semana y qué días tuvieron más visitas al perfil por alcance, con los reels de esos días; (2) cine contra clásico (campo `estilo` de cada reel en `metricas/actual.items`): alcance, tiempo medio de visionado y nota, sin sacar conclusiones con menos de 2 semanas.
- Señales de que va bien: tiempo medio ≥ 5 s en reels de 6,5 s; 1–2 envíos por cada 100 de alcance; algún reel por encima de 1.000 de alcance; 15 visitas al perfil por cada 1.000 de alcance.
- Revisión de la estrategia: 2026-12-10 (30 días). No descartar tema ni formato con menos de 2 semanas de datos.

## Publicación
- Los archivos del día (`posts/AAAA-MM-DD/…`) NO viven en este repo sino en el repositorio público **verdadysinfiltro/assets-vs** (junto a este, en `../assets-vs`; los scripts lo clonan solos: `tools/medios.py`). Este repo es privado: código, marca y documentos. URL pública: `https://raw.githubusercontent.com/verdadysinfiltro/assets-vs/main/<ruta>`. `tools/dia.py publicar` hace el `git push` a assets-vs ANTES de publicar.
- `python3 tools/publicar.py carrusel|story|reel <ruta> [caption.txt]` (las rutas `posts/…` se buscan en assets-vs) (token inyectado por el proxy en graph.facebook.com; `IG_USER_ID`; nunca mostrar tokens).
- Si falla, reintentar una vez y anotar el error en `log` y en `posts` (estado "error").

## Cuadros
En pausa. Se retoma con ~5.000 seguidores o cuando alguien pregunte dónde comprar una frase: 3 láminas de las frases más guardadas, impresión bajo demanda, envío solo a España.

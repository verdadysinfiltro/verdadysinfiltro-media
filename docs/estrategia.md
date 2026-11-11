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
- **Voz (desde el 2026-11-12):** los dos reels llevan locución (`tools/voz.py`, Supertonic 3) y alternan entre mujer F5 y hombre M5: los días pares del año, mediodía M5 y noche F5; los impares, al revés. El golpe 2 aparece cuando lo dice la voz. El caption lleva la línea "Voz generada con IA." (condición de la licencia OpenRAIL del modelo). Lupa compara mujer contra hombre por alcance, tiempo de visionado y nota, y lo cuenta en el informe del domingo.

## Qué se mide (Lupa)
- Por pieza: alcance, visualizaciones, envíos, guardados, likes, comentarios y, en reels, tiempo medio de visionado.
- **Nota de una pieza = (2 × envíos + guardados) / alcance.** Es lo que decide qué se repite.
- Señales de que va bien: tiempo medio ≥ 5 s en reels de 6,5 s; 1–2 envíos por cada 100 de alcance; algún reel por encima de 1.000 de alcance.
- Revisión de la estrategia: 2026-12-10 (30 días). No descartar tema ni formato con menos de 2 semanas de datos.

## Publicación
- Archivos en `posts/AAAA-MM-DD/`; URL pública `https://raw.githubusercontent.com/verdadysinfiltro/verdadysinfiltro-media/main/<ruta>`. Hacer `git push` ANTES de publicar.
- `python3 tools/publicar.py carrusel|story|reel <ruta> [caption.txt]` (token inyectado por el proxy en graph.facebook.com; `IG_USER_ID`; nunca mostrar tokens).
- Si falla, reintentar una vez y anotar el error en `log` y en `posts` (estado "error").

## Cuadros
En pausa. Se retoma con ~5.000 seguidores o cuando alguien pregunte dónde comprar una frase: 3 láminas de las frases más guardadas, impresión bajo demanda, envío solo a España.

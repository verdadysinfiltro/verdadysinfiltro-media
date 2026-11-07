# Estrategia de publicación

## Frecuencia
- **Reels:** 1 al día (lo que más alcance da a cuentas nuevas). Prueba inicial: 2 al día durante 30 días.
- **Carruseles:** 3–4 por semana (se guardan y comparten).
- **Imagen única:** 1–2 por semana como mucho.
- **Stories:** 3–7 al día (vínculo con seguidores, no traen nuevos).
- Reparto del feed: 55% reels · 35% carruseles · 10% posts sueltos.

## Horarios (hora local del público, España)
- Reels: 19:00–22:00.
- Carruseles: 7:00–9:00 o 13:00–14:00.
- Stories: repartidas; una a primera hora y otra por la noche.
- Mejores días: domingo a jueves por la noche. Viernes y sábado rinden menos.

## Claves por formato
- **Reels:** la frase visible en el primer segundo, texto grande sobre vídeo estético (lluvia, ciudad de noche, mar), audio en tendencia o piano triste, 5–9 s para que se repita.
- **Carruseles:** diapositiva 1 = gancho; 3–6 de desarrollo; la última pide guardar o enviar ("Envíaselo a quien necesite leer esto").
- **Stories:** encuestas ("¿Te ha pasado?"), cajas de preguntas, compartir los propios posts.
- Misma tipografía y paleta siempre.
- Lo que más pesa: envíos por privado y guardados.
- Revisar estadísticas a las 2 semanas y repetir lo que tenga más guardados y envíos antes de borrar nada.

## Flujo de trabajo
1. Claude crea las frases (comprobando `docs/historial.md` para no repetir) y genera las imágenes con `tools/generar.py`.
2. Las imágenes se suben a `posts/AAAA-MM-DD/` de este repo (público).
3. URL pública: `https://raw.githubusercontent.com/verdadysinfiltro/verdadysinfiltro-media/main/posts/AAAA-MM-DD/<archivo>`.
4. Claude publica en Instagram usando esas URLs y apunta cada post en `docs/historial.md`.

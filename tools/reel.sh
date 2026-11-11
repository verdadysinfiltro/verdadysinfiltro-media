#!/usr/bin/env bash
# Clip: crea un reel 1080x1920 a partir de imágenes story.
# Uso: tools/reel.sh A.jpg salida.mp4 [audio.wav] [variante: in|out|pan|auto] [semilla] [B.jpg]
# - Con B.jpg (reel en dos golpes, 6,5 s): A (solo el golpe 1) se ve desde el primer
#   fotograma y a los 1,5 s aparece B (frase entera + cierre) con un fundido corto.
#   Así hay que esperar al remate y el reel se ve entero y se repite.
# - Sin B.jpg (7 s): la imagen A fija, como antes.
# - Movimiento distinto según la variante (auto = elegida por la semilla).
# - Grano de película suave. Si hay audio, se usa; si no, pista silenciosa.
# - Con voz: VOZ=locucion.wav T2=<segundo del golpe 2> DUR=<duración> delante del comando
#   (los da tools/voz.py). El golpe 2 aparece cuando lo dice la voz y el piano baja de volumen.
# Además guarda la portada junto al vídeo: <salida sin .mp4>-cover.jpg (la frase entera)
set -euo pipefail
IN=$1; OUT=$2; AUDIO=${3:-}; VAR=${4:-auto}; SEED=${5:-$(date +%F)}; B=${6:-}
if [ "$VAR" = auto ]; then
  n=$(( $(printf '%s' "$SEED" | cksum | cut -d' ' -f1) % 3 ))
  VAR=$(echo "in out pan" | cut -d' ' -f$((n+1)))
fi
VOZ=${VOZ:-}; T2=${T2:-1.5}
if [ -n "$B" ]; then DUR=${DUR:-6.5}; else DUR=7; fi
N=$(python3 -c "print(round($DUR*30))")
case $VAR in
  in)  Z="min(1+0.06*on/$N,1.06)"; X="iw/2-(iw/zoom/2)"; Y="ih/2-(ih/zoom/2)";;
  out) Z="max(1.06-0.06*on/$N,1)"; X="iw/2-(iw/zoom/2)"; Y="ih/2-(ih/zoom/2)";;
  pan) Z="1.04"; X="(iw-iw/zoom)*(0.5+0.4*(on/$N-0.5))"; Y="ih/2-(ih/zoom/2)";;
  *) echo "variante desconocida: $VAR" >&2; exit 1;;
esac
MOV="scale=2160:3840,zoompan=z='$Z':x='$X':y='$Y':d=1:s=1080x1920:fps=30,noise=alls=6:allf=t,format=yuv420p"
ENT=(-loop 1 -framerate 30 -t "$DUR" -i "$IN")
if [ -n "$B" ]; then
  ENT+=(-loop 1 -framerate 30 -t "$DUR" -i "$B")
  # En RGB para que el negro no cambie al aparecer el golpe 2 (en YUV el fundido lo volvía gris).
  FC="[0:v]format=rgba[a];[1:v]format=rgba,fade=t=in:st=$T2:d=0.3:alpha=1[b];[a][b]overlay=shortest=1:format=rgb,$MOV[v]"
  PORTADA=$B; AI=2
else
  FC="[0:v]$MOV[v]"
  PORTADA=$IN; AI=1
fi
FADE=$(python3 -c "print($DUR-1)")
if [ -n "$AUDIO" ] && [ -n "$VOZ" ]; then
  ffmpeg -y -loglevel error "${ENT[@]}" -i "$AUDIO" -i "$VOZ" -filter_complex "$FC;[$AI:a]aresample=44100,volume=0.3,afade=t=out:st=$FADE:d=1[p];[$((AI+1)):a]aresample=44100[z];[p][z]amix=inputs=2:duration=first:normalize=0[a]" -map "[v]" -map "[a]" -t "$DUR" -r 30 -c:v libx264 -preset slow -crf 20 -c:a aac -b:a 160k -movflags +faststart "$OUT"
elif [ -n "$AUDIO" ]; then
  ffmpeg -y -loglevel error "${ENT[@]}" -i "$AUDIO" -filter_complex "$FC" -map "[v]" -map $AI:a -t "$DUR" -r 30 -c:v libx264 -preset slow -crf 20 -c:a aac -b:a 128k -af "afade=t=out:st=$FADE:d=1" -movflags +faststart "$OUT"
else
  ffmpeg -y -loglevel error "${ENT[@]}" -f lavfi -i anullsrc=r=44100:cl=stereo -filter_complex "$FC" -map "[v]" -map $AI:a -t "$DUR" -r 30 -c:v libx264 -preset slow -crf 20 -c:a aac -b:a 128k -movflags +faststart "$OUT"
fi
python3 -c "import sys; from PIL import Image; Image.open(sys.argv[1]).convert('RGB').save(sys.argv[2], quality=92)" "$PORTADA" "${OUT%.mp4}-cover.jpg"
echo "$OUT ($VAR, ${DUR}s)"

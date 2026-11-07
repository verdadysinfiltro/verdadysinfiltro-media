#!/usr/bin/env bash
# Clip: crea un reel 1080x1920 de 7 s a partir de una imagen story.
# Uso: tools/reel.sh entrada.jpg salida.mp4 [audio.wav] [variante: in|out|pan|auto] [semilla]
# - Frase visible desde el primer fotograma (sin fundido desde negro).
# - Movimiento distinto según la variante (auto = elegida por la semilla).
# - Grano de película suave. Si hay audio, se usa; si no, pista silenciosa.
# Además guarda la portada junto al vídeo: <salida sin .mp4>-cover.jpg
set -euo pipefail
IN=$1; OUT=$2; AUDIO=${3:-}; VAR=${4:-auto}; SEED=${5:-$(date +%F)}
if [ "$VAR" = auto ]; then
  n=$(( $(printf '%s' "$SEED" | cksum | cut -d' ' -f1) % 3 ))
  VAR=$(echo "in out pan" | cut -d' ' -f$((n+1)))
fi
case $VAR in
  in)  Z="min(1+0.0007*on,1.06)"; X="iw/2-(iw/zoom/2)"; Y="ih/2-(ih/zoom/2)";;
  out) Z="max(1.06-0.0007*on,1)"; X="iw/2-(iw/zoom/2)"; Y="ih/2-(ih/zoom/2)";;
  pan) Z="1.04"; X="(iw-iw/zoom)*(0.5+0.4*(on/210-0.5))"; Y="ih/2-(ih/zoom/2)";;
  *) echo "variante desconocida: $VAR" >&2; exit 1;;
esac
VF="scale=2160:3840,zoompan=z='$Z':x='$X':y='$Y':d=210:s=1080x1920:fps=30,noise=alls=6:allf=t,format=yuv420p"
if [ -n "$AUDIO" ]; then
  ffmpeg -y -loglevel error -loop 1 -i "$IN" -i "$AUDIO" -vf "$VF" -t 7 -c:v libx264 -preset slow -crf 20 -c:a aac -b:a 128k -af "afade=t=out:st=6:d=1" -shortest -movflags +faststart "$OUT"
else
  ffmpeg -y -loglevel error -loop 1 -i "$IN" -f lavfi -i anullsrc=r=44100:cl=stereo -vf "$VF" -t 7 -c:v libx264 -preset slow -crf 20 -c:a aac -b:a 128k -shortest -movflags +faststart "$OUT"
fi
python3 -c "from PIL import Image; Image.open('$IN').convert('RGB').save('${OUT%.mp4}-cover.jpg', quality=92)"
echo "$OUT ($VAR)"

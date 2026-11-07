#!/usr/bin/env bash
# Crea un reel 1080x1920 de 7 s a partir de una imagen story (zoom lento + fundido).
# Uso: tools/reel.sh entrada.jpg salida.mp4 [audio.mp3]
set -euo pipefail
IN=$1; OUT=$2; AUDIO=${3:-}
VF="scale=2160:3840,zoompan=z='min(zoom+0.0006,1.05)':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d=210:s=1080x1920:fps=30,fade=t=in:st=0:d=0.4,format=yuv420p"
if [ -n "$AUDIO" ]; then
  ffmpeg -y -loglevel error -loop 1 -i "$IN" -i "$AUDIO" -vf "$VF" -t 7 -c:v libx264 -preset slow -crf 20 -c:a aac -b:a 128k -shortest -movflags +faststart "$OUT"
else
  ffmpeg -y -loglevel error -loop 1 -i "$IN" -f lavfi -i anullsrc=r=44100:cl=stereo -vf "$VF" -t 7 -c:v libx264 -preset slow -crf 20 -c:a aac -b:a 128k -shortest -movflags +faststart "$OUT"
fi
echo "$OUT"

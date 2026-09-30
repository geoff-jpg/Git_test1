#!/usr/bin/env bash
# Renders Sonardyne_Brazil_v2.pdf to 1080p frames, then builds an MP4 with a slow
# zoom on each slide and 1 s crossfades. Needs ffmpeg and pdftoppm.
set -euo pipefail
cd "$(dirname "$0")/.."
D=(6 8 10 9 9 11 10 9 9 9 8 7)   # seconds per slide
tmp=$(mktemp -d)
pdftoppm -png -scale-to-x 1920 -scale-to-y 1080 Sonardyne_Brazil_v2.pdf "$tmp/f"
inputs=""
for i in $(seq 1 12); do
  n=$(printf %02d "$i"); fr=$(( D[i-1] * 30 ))
  ffmpeg -loglevel error -y -loop 1 -i "$tmp/f-$n.png" \
    -vf "scale=3840:2160,zoompan=z='1+0.035*on/$fr':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d=$fr:s=1920x1080:fps=30,format=yuv420p" \
    -frames:v "$fr" -c:v libx264 -crf 18 "$tmp/c$n.mp4"
  inputs="$inputs -i $tmp/c$n.mp4"
done
fc=""; prev="[0:v]"; off=0
for i in $(seq 1 11); do
  off=$(( off + D[i-1] - 1 )); fc="$fc$prev[$i:v]xfade=transition=fade:duration=1:offset=$off[v$i];"; prev="[v$i]"
done
fc="${fc}${prev}fade=t=in:st=0:d=0.8,setsar=1,format=yuv420p[vout]"
ffmpeg -loglevel error -y $inputs -filter_complex "$fc" -map "[vout]" -c:v libx264 -preset slow -crf 21 -movflags +faststart Sonardyne_Brazil.mp4
rm -rf "$tmp"

# Add the synthesised soundtrack (see make_music.py) as a second version
python3 source/make_music.py "$tmp.wav" 94
ffmpeg -loglevel error -y -i Sonardyne_Brazil.mp4 -i "$tmp.wav" -map 0:v -map 1:a -c:v copy \
  -c:a aac -b:a 192k -shortest -movflags +faststart Sonardyne_Brazil_with_music.mp4
rm -f "$tmp.wav"

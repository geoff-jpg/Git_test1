#!/usr/bin/env bash
# Builds the movie from an 11-slide render of the deck (the Sources slide is
# left out of the video), with a slow zoom on each slide, 1 s crossfades and
# the synthesised soundtrack. Needs node, LibreOffice, pdftoppm and ffmpeg.
set -euo pipefail
cd "$(dirname "$0")"
MOVIE=1 node build.js                        # -> movie.pptx (no Sources slide)
soffice --headless --convert-to pdf movie.pptx
cd ..
D=(6 8 10 9 9 11 10 9 9 11 12)   # seconds per slide; 94 s total with overlaps
tmp=$(mktemp -d)
pdftoppm -png -scale-to-x 1920 -scale-to-y 1080 source/movie.pdf "$tmp/f"
inputs=""
for i in $(seq 1 11); do
  n=$(printf %02d "$i"); fr=$(( D[i-1] * 30 ))
  ffmpeg -loglevel error -y -loop 1 -i "$tmp/f-$n.png" \
    -vf "scale=3840:2160,zoompan=z='1+0.035*on/$fr':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d=$fr:s=1920x1080:fps=30,format=yuv420p" \
    -frames:v "$fr" -c:v libx264 -crf 18 "$tmp/c$n.mp4"
  inputs="$inputs -i $tmp/c$n.mp4"
done
fc=""; prev="[0:v]"; off=0
for i in $(seq 1 10); do
  off=$(( off + D[i-1] - 1 )); fc="$fc$prev[$i:v]xfade=transition=fade:duration=1:offset=$off[v$i];"; prev="[v$i]"
done
fc="${fc}${prev}fade=t=in:st=0:d=0.8,setsar=1,format=yuv420p[vout]"
python3 source/make_music.py "$tmp/music.wav" 94
ffmpeg -loglevel error -y $inputs -i "$tmp/music.wav" -filter_complex "$fc" -map "[vout]" -map 11:a \
  -c:v libx264 -preset slow -crf 21 -c:a aac -b:a 192k -movflags +faststart Sonardyne_Brazil_with_music.mp4
ffmpeg -loglevel error -y -i Sonardyne_Brazil_with_music.mp4 -an -c:v copy -movflags +faststart Sonardyne_Brazil.mp4
rm -rf "$tmp" source/movie.pptx source/movie.pdf

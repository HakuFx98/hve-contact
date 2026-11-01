#!/usr/bin/env bash
# Rebuild THE EMPTY LAP ep.001 from source: picture, sound, mux, thumbnail.
# Requires: python3 with pycairo, numpy, pillow; ffmpeg with libx264.
set -euo pipefail
cd "$(dirname "$0")/src"
OUT=../output
mkdir -p "$OUT" ../build
python3 render.py video ../build/picture.mp4
python3 audio.py ../build/mix.wav
ffmpeg -y -loglevel error -i ../build/picture.mp4 -i ../build/mix.wav \
  -map 0:v -map 1:a -c:v copy -af "volume=-0.6dB" -c:a aac -b:a 256k -ar 48000 \
  -movflags +faststart -shortest "$OUT/the_empty_lap_ep001.mp4"
python3 thumbnail.py "$OUT/the_empty_lap_ep001_thumbnail.png"
echo "done -> $OUT"

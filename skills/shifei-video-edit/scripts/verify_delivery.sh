#!/bin/zsh
set -euo pipefail

if [[ $# -ne 1 ]]; then
  print -u2 'Usage: verify_delivery.sh <master.mp4>'
  exit 64
fi

master="$1"
[[ -f "$master" ]] || { print -u2 "Missing file: $master"; exit 66; }

ffprobe -v error -show_entries format=duration,size -show_entries stream=codec_type,codec_name,width,height,r_frame_rate,sample_rate -of default=nw=1 "$master"
ffmpeg -v error -ss 0 -i "$master" -frames:v 1 -f null -
print 'Technical check passed. Still inspect subtitles, cards, speakers, sound and ending visually.'

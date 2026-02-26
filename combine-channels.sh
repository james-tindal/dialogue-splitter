#!/bin/bash

splits_dir="splits"
output_dir="video-output"
video_dir="videos"

for filepath in "$video_dir"/*.mov; do
  # Extract the filename and base name (without extension)
  filename=$(basename "$filepath")
  base="${filename%.*}"

  input_0=$filepath
  input_1="$splits_dir/${base}_(Vocals).flac"
  input_2="$splits_dir/${base}_(Instrumental).flac"

  output_file="$output_dir/$base.mov"

  # Make sure output directory exists
  mkdir -p $output_dir

  ffmpeg \
    -i "$input_0" -i "$input_1" -i "$input_2" \
    -map 0:v -map 1:a -map 2:a \
    -c:v copy -c:a aac -b:a 180k \
    -metadata:s:a:0 title="Voice" \
    -metadata:s:a:1 title="Ambient" \
    -write_tmcd 0 \
    "$output_file"

  echo "✅ Processed: $output_file"
done

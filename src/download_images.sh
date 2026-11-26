#!/bin/bash
export PATH="/c/Windows/System32:/c/Windows:/usr/local/bin:/usr/bin:/bin"
BASE="C:/Users/a11607/WorkBuddy/2026-11-23-08-45-13/calamity-assistant"
IMGDIR="$BASE/images"
mkdir -p "$IMGDIR"
TSV="$BASE/image_urls.tsv"
count=0
while IFS=$'\t' read -r name url; do
  fn=$(printf '%s' "$name" | sed 's/ /_/g' | sed 's/[\\/:*?"<>|]/_/g')
  out="$IMGDIR/$fn.png"
  if [ -s "$out" ]; then count=$((count+1)); continue; fi
  curl -s --max-time 12 -o "$out" "$url"
  # remove tiny/error pages
  sz=$(wc -c < "$out" 2>/dev/null || echo 0)
  if [ "$sz" -lt 50 ]; then rm -f "$out"; fi
  count=$((count+1))
  if [ $((count % 100)) -eq 0 ]; then echo "processed $count"; fi
done < "$TSV"
echo "DONE $count"
echo "downloaded files: $(find "$IMGDIR" -type f | wc -l)"

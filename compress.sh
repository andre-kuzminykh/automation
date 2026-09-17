#!/usr/bin/env bash
# Compress videos already on disk, in place. Use after a render that produced
# oversized files — re-rendering only to shrink them would cost real credits.
#
# Usage (on human-1):
#   bash compress.sh levels_en        # one dataset
#   bash compress.sh                  # every dataset
set -u
cd "$(dirname "$0")"

MIN_BYTES="${MIN_BYTES:-5242880}"   # leave anything already small alone
TARGETS=("$@")
[ "${#TARGETS[@]}" -eq 0 ] && TARGETS=(l1 l2 l3 l7 l8 mt mte levels levels_en app intro)

total_before=0
total_after=0
touched=0

for lec in "${TARGETS[@]}"; do
  [ -d "$lec/videos" ] || continue
  for src in "$lec"/videos/*.mp4; do
    [ -e "$src" ] || continue
    before=$(stat -c%s "$src")
    [ "$before" -lt "$MIN_BYTES" ] && continue

    tmp="${src%.mp4}.compressing.mp4"
    printf "  %-44s %6s MB -> " "$src" "$((before / 1048576))"
    if ffmpeg -y -i "$src" \
         -vcodec libx264 -crf 28 -preset fast \
         -acodec aac -b:a 96k -movflags +faststart \
         "$tmp" >/dev/null 2>&1; then
      after=$(stat -c%s "$tmp")
      # Only keep the result if it actually helped.
      if [ "$after" -gt 0 ] && [ "$after" -lt "$before" ]; then
        mv "$tmp" "$src"
        echo "$((after / 1048576)) MB"
        total_before=$((total_before + before))
        total_after=$((total_after + after))
        touched=$((touched + 1))
      else
        rm -f "$tmp"
        echo "no gain, kept original"
      fi
    else
      rm -f "$tmp"
      echo "ffmpeg FAILED, kept original"
    fi
  done
done

echo
if [ "$touched" -eq 0 ]; then
  echo "nothing needed compressing"
else
  echo "compressed $touched file(s): $((total_before / 1048576)) MB -> $((total_after / 1048576)) MB"
fi

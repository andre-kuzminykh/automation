#!/usr/bin/env bash
# Render a single lecture-3 slide and leave it uncommitted, for listening to
# before committing to a full run. Use this whenever voice settings change.
#
# Usage (on human-1):
#   bash l3/run_one.sh 20
set -u
cd "$(dirname "$0")/.."   # repo root

AI_MODEL_ID="26f0fc66-152b-40ab-abed-76c43df99bc8"
VOICE_ID="8e7544c8-a37b-4315-9599-55bad6bfbb7b"

SLIDE="${1:?usage: bash l3/run_one.sh <slide-id>}"

python3 -m l7.service.generate --lecture l3 \
  --regenerate "$SLIDE" --from "$SLIDE" --to "$SLIDE" \
  --ai-model-id "$AI_MODEL_ID" \
  --voice-id "$VOICE_ID" \
  --poll-timeout 1800 \
  --no-git

echo
if [ -s "l3/videos/$SLIDE.mp4" ]; then
  echo "wrote l3/videos/$SLIDE.mp4 ($(du -h "l3/videos/$SLIDE.mp4" | cut -f1))"
  echo "listen to it, then run the rest with: PAR=4 bash l3/run_parallel.sh 20 40"
else
  echo "NO video produced for slide $SLIDE — see the log above."
  exit 1
fi

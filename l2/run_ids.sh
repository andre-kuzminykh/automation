#!/usr/bin/env bash
# Regenerate specific lecture-2 slides by id (non-contiguous allowed), pushing each.
# Usage:
#   git pull --rebase origin claude/setup-gcloud-video-service-XKVf0
#   bash l2/run_ids.sh 3 7 12
set -u
cd "$(dirname "$0")/.."   # repo root

AI_MODEL_ID="26f0fc66-152b-40ab-abed-76c43df99bc8"
VOICE_ID="8e7544c8-a37b-4315-9599-55bad6bfbb7b"

if [ "$#" -eq 0 ]; then
  echo "usage: bash l2/run_ids.sh <id> [<id> ...]"
  exit 1
fi

for i in "$@"; do
  echo "================ SLIDE $i ================"
  python3 -m l7.service.generate --lecture l2 \
    --regenerate "$i" --from "$i" --to "$i" \
    --ai-model-id "$AI_MODEL_ID" --voice-id "$VOICE_ID" \
    --poll-timeout 1800 \
    || echo ">>> SLIDE $i FAILED (continuing)"
done

echo "================ DONE ($*) ================"

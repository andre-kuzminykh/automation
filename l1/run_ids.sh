#!/usr/bin/env bash
# Regenerate specific lecture-1 slides by id (non-contiguous allowed), pushing
# each as soon as it is ready. Same voice/settings as the rest of lecture 1.
#
# Usage (on human-1, venv active, HEDRA_API_KEY exported):
#   git pull --rebase origin claude/setup-gcloud-video-service-XKVf0
#   bash l1/run_ids.sh 0 7 15 20 32
set -u

cd "$(dirname "$0")/.."   # repo root

AI_MODEL_ID="26f0fc66-152b-40ab-abed-76c43df99bc8"
VOICE_ID="8e7544c8-a37b-4315-9599-55bad6bfbb7b"

if [ "$#" -eq 0 ]; then
  echo "usage: bash l1/run_ids.sh <id> [<id> ...]"
  exit 1
fi

for i in "$@"; do
  echo "================ SLIDE $i ================"
  python3 -m l7.service.generate --lecture l1 \
    --regenerate "$i" --from "$i" --to "$i" \
    --ai-model-id "$AI_MODEL_ID" --voice-id "$VOICE_ID" \
    --poll-timeout 1800 \
    || echo ">>> SLIDE $i FAILED (continuing)"
done

echo "================ DONE ($*) ================"

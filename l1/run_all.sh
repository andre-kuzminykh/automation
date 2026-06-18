#!/usr/bin/env bash
# Regenerate every lecture-1 talking head one slide at a time, pushing each
# to git as soon as it is ready (so they can be reviewed in parallel).
#
# Usage (on human-1, with venv active and HEDRA_API_KEY exported):
#   git pull --rebase origin claude/setup-gcloud-video-service-XKVf0
#   bash l1/run_all.sh                 # all slides 0..42
#   bash l1/run_all.sh 5               # only slide 5
#   bash l1/run_all.sh 10 20           # slides 10..20 inclusive
set -u

cd "$(dirname "$0")/.."   # repo root

AI_MODEL_ID="26f0fc66-152b-40ab-abed-76c43df99bc8"
VOICE_ID="8e7544c8-a37b-4315-9599-55bad6bfbb7b"

START="${1:-0}"
END="${2:-42}"

for i in $(seq "$START" "$END"); do
  echo "================ SLIDE $i ================"
  python3 -m l7.service.generate --lecture l1 \
    --regenerate "$i" --from "$i" --to "$i" \
    --ai-model-id "$AI_MODEL_ID" \
    --voice-id "$VOICE_ID" \
    || echo ">>> SLIDE $i FAILED (continuing)"
done

echo "================ ALL DONE ($START..$END) ================"

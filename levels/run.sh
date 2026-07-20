#!/usr/bin/env bash
# Generate the 4 AI-maturity-level talking heads (test conclusion):
#   1 AI-Enabled, 2 AI-Driven, 3 AI-First, 4 AI-Native.
# Same voice/settings as the rest (Andre [RUS], speed 0.75, 1:1, 540p).
# Idempotent: re-running skips levels that already exist; pass ids to force a subset.
#
# Usage (on human-1, venv active, HEDRA_API_KEY exported):
#   git pull --rebase origin claude/setup-gcloud-video-service-XKVf0
#   bash levels/run.sh          # all 4
#   bash levels/run.sh 3 4      # only AI-First and AI-Native
set -u
cd "$(dirname "$0")/.."   # repo root

AI_MODEL_ID="26f0fc66-152b-40ab-abed-76c43df99bc8"
VOICE_ID="8e7544c8-a37b-4315-9599-55bad6bfbb7b"
BRANCH="claude/setup-gcloud-video-service-XKVf0"
IDS="${*:-1 2 3 4}"
TIMEOUT=1800

for i in $IDS; do
  for attempt in 1 2; do
    [ -f "levels/videos/$i.mp4" ] && break
    echo "---- level $i (attempt $attempt) ----"
    python3 -m l7.service.generate --lecture levels \
      --regenerate "$i" --from "$i" --to "$i" \
      --ai-model-id "$AI_MODEL_ID" --voice-id "$VOICE_ID" \
      --poll-timeout "$TIMEOUT" --no-git || true
  done
done

# stage + push whatever exists
git add levels/data/slides.json levels/data/config.json levels/run.sh 2>/dev/null
git checkout -- intro/data/manifest.json l1/data/manifest.json l2/data/manifest.json \
                mt/data/manifest.json mte/data/manifest.json 2>/dev/null || true
ok=1
for i in $IDS; do
  if [ -f "levels/videos/$i.mp4" ]; then
    git add "levels/videos/$i.mp4"; echo "[ok] levels/videos/$i.mp4"
  else
    echo "[MISSING] level $i — re-run: bash levels/run.sh $i"; ok=0
  fi
done
git add levels/data/manifest.json 2>/dev/null

if git diff --cached --quiet; then
  echo "[push] nothing to commit"
else
  git commit -m "feat(levels): AI-maturity level videos $IDS"
  for attempt in 1 2 3 4; do
    if git pull --rebase origin "$BRANCH" && git push -u origin "$BRANCH"; then
      echo "[push] ok"; break
    fi
    echo "[push] retry $attempt"; sleep $((2 ** attempt))
  done
fi

[ "$ok" = 1 ] && echo "================ LEVELS DONE ($IDS) ================" \
             || echo "================ SOME MISSING — see above ================"

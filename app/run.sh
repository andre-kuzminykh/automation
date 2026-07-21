#!/usr/bin/env bash
# Generate the 2 platform-onboarding talking heads:
#   1 — кабинет руководителя (AI-стратегия), 2 — кабинет сотрудника (описание процессов).
# Same voice/settings as the rest (Andre [RUS], speed 0.75, 1:1, 540p).
# Idempotent: re-run skips existing; pass ids to force a subset.
#
# Usage (on human-1, venv active, HEDRA_API_KEY exported):
#   git pull --rebase origin claude/setup-gcloud-video-service-XKVf0
#   bash app/run.sh          # both
#   bash app/run.sh 1        # only leader cabinet
set -u
cd "$(dirname "$0")/.."   # repo root

AI_MODEL_ID="26f0fc66-152b-40ab-abed-76c43df99bc8"
VOICE_ID="8e7544c8-a37b-4315-9599-55bad6bfbb7b"
BRANCH="claude/setup-gcloud-video-service-XKVf0"
IDS="${*:-1 2}"
TIMEOUT=1800

for i in $IDS; do
  for attempt in 1 2; do
    [ -f "app/videos/$i.mp4" ] && break
    echo "---- app slide $i (attempt $attempt) ----"
    python3 -m l7.service.generate --lecture app \
      --regenerate "$i" --from "$i" --to "$i" \
      --ai-model-id "$AI_MODEL_ID" --voice-id "$VOICE_ID" \
      --poll-timeout "$TIMEOUT" --no-git || true
  done
done

git add app/data/slides.json app/data/config.json app/run.sh 2>/dev/null
git checkout -- intro/data/manifest.json l1/data/manifest.json l2/data/manifest.json \
                mt/data/manifest.json mte/data/manifest.json levels/data/manifest.json 2>/dev/null || true
ok=1
for i in $IDS; do
  if [ -f "app/videos/$i.mp4" ]; then git add "app/videos/$i.mp4"; echo "[ok] app/videos/$i.mp4";
  else echo "[MISSING] app slide $i — re-run: bash app/run.sh $i"; ok=0; fi
done
git add app/data/manifest.json 2>/dev/null

if git diff --cached --quiet; then
  echo "[push] nothing to commit"
else
  git commit -m "feat(app): onboarding videos $IDS"
  for attempt in 1 2 3 4; do
    if git pull --rebase origin "$BRANCH" && git push -u origin "$BRANCH"; then echo "[push] ok"; break; fi
    echo "[push] retry $attempt"; sleep $((2 ** attempt))
  done
fi

[ "$ok" = 1 ] && echo "================ APP DONE ($IDS) ================" \
             || echo "================ SOME MISSING — see above ================"

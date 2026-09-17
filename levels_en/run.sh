#!/usr/bin/env bash
# English AI-maturity level narrations (4 videos, shown at the end of the test).
#
# Usage (on human-1, venv active):
#   unset HEDRA_API_KEY                     # env var shadows ~/.hedra_key
#   git pull --rebase origin claude/setup-gcloud-video-service-XKVf0
#   bash levels_en/run.sh                   # all four
#   bash levels_en/run.sh 1                 # just AI-Enabled, to listen first
#
# Output is named by slug, not id: 01_level_ai_enabled.mp4 … 04_level_ai_native.mp4
set -u
cd "$(dirname "$0")/.."   # repo root

AI_MODEL_ID="26f0fc66-152b-40ab-abed-76c43df99bc8"
# Voice ids are per-account. Leave this empty to let the run resolve the voice
# by name against whatever account the key belongs to; set it only to pin a
# specific uuid you have confirmed exists there.
VOICE_ID="${VOICE_ID:-}"
BRANCH="claude/setup-gcloud-video-service-XKVf0"

FROM="${1:-1}"
TO="${2:-${1:-4}}"

echo "[preflight] credits:"
python3 -m l7.service.generate --lecture levels_en --check-credits 2>&1 | tail -12

# The mismatch warning above is not enough on its own: the previous run printed
# it and then submitted 5 doomed requests anyway. --credits-available reports 0
# when this config's workspace_id is not one the key's account owns, so gate on it.
have="$(python3 -m l7.service.generate --lecture levels_en --credits-available 2>/dev/null | tail -1)"
case "$have" in
  ''|*[!0-9]*)
    echo "[preflight] could not read the balance — continuing anyway" ;;
  *)
    if [ "$have" -lt 20 ]; then
      echo "[preflight] ABORT: $have credits usable for workspace_id in levels_en/data/config.json."
      echo "            Either the money is in a different workspace or the key is for a"
      echo "            different account. See the mismatch note above; nothing was submitted."
      exit 2
    fi
    echo "[preflight] $have credits available" ;;
esac

for i in $(seq "$FROM" "$TO"); do
  echo "================ SLIDE $i ================"
  python3 -m l7.service.generate --lecture levels_en \
    --regenerate "$i" --from "$i" --to "$i" \
    --ai-model-id "$AI_MODEL_ID" \
    ${VOICE_ID:+--voice-id "$VOICE_ID"} \
    --poll-timeout 1800 \
    --no-git \
    || echo ">>> SLIDE $i FAILED (continuing)"
done

echo
echo "================ RESULT ================"
missing=(); produced=0
for f in 01_level_ai_enabled 02_level_ai_driven 03_level_ai_first 04_level_ai_native; do
  if [ -s "levels_en/videos/$f.mp4" ]; then
    echo "  ok      $f.mp4  ($(du -h "levels_en/videos/$f.mp4" | cut -f1))"
    produced=$((produced + 1))
  else
    echo "  MISSING $f.mp4"
    missing+=("$f")
  fi
done

if [ "${#missing[@]}" -gt 0 ]; then
  echo "${#missing[@]} missing — not pushing. Fix and re-run."
# A run that produced nothing leaves only status="failed" rows in the manifest.
# Those are worthless (the console already showed the errors) and they dirty the
# tree, which makes the NEXT `git pull --rebase` refuse to start — that is how
# this VM stayed on stale code across three runs against a dead workspace.
if git diff --quiet -- levels_en/data/manifest.json; then :; else
  if [ "$produced" -eq 0 ]; then
    echo "[cleanup] nothing rendered; reverting manifest so the next pull is not blocked"
    git checkout -- levels_en/data/manifest.json
  fi
fi
  exit 1
fi

git add levels_en/videos/ levels_en/data/manifest.json
if git diff --cached --quiet; then
  echo "[push] nothing new to commit"
  exit 0
fi
git commit -m "feat(levels_en): english AI-maturity level narrations" >/dev/null
for attempt in 1 2 3 4; do
  if git pull --rebase origin "$BRANCH" && git push -u origin "$BRANCH"; then
    echo "[push] ok"
    exit 0
  fi
  echo "[push] retry $attempt"; sleep $((2 ** attempt))
done
echo "[push] FAILED — videos are on disk, push manually"
exit 1

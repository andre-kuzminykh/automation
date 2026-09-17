#!/usr/bin/env bash
# Russian AI-maturity level narrations (4 videos, end of the test).
#
# Re-record after the ИИ -> AI rename. The existing 1..4.mp4 carry the old
# wording; the pipeline sees the changed text_sha256 and re-renders rather
# than skipping.
#
# Usage (on human-1):
#   unset HEDRA_API_KEY                     # env var shadows ~/.hedra_key
#   git pull --rebase origin claude/setup-gcloud-video-service-XKVf0
#   bash levels/run.sh                      # all four
#   bash levels/run.sh 1                    # just AI-Enabled, to listen first
set -u
cd "$(dirname "$0")/.."   # repo root

AI_MODEL_ID="26f0fc66-152b-40ab-abed-76c43df99bc8"
VOICE_ID="8e7544c8-a37b-4315-9599-55bad6bfbb7b"
BRANCH="claude/setup-gcloud-video-service-XKVf0"

FROM="${1:-1}"
TO="${2:-${1:-4}}"

echo "[preflight] credits:"
python3 -m l7.service.generate --lecture levels --check-credits 2>&1 | tail -12

for i in $(seq "$FROM" "$TO"); do
  echo "================ SLIDE $i ================"
  python3 -m l7.service.generate --lecture levels \
    --regenerate "$i" --from "$i" --to "$i" \
    --ai-model-id "$AI_MODEL_ID" \
    --voice-id "$VOICE_ID" \
    --poll-timeout 1800 \
    --no-git \
    || echo ">>> SLIDE $i FAILED (continuing)"
done

echo
echo "================ RESULT ================"
# A stale text_sha256 in the manifest means that slide still holds the old
# ИИ wording, whatever is on disk. status must be checked too: a failed slide
# records the NEW text_sha256 alongside status="failed", so matching hashes
# alone would report a slide that never rendered as fresh.
python3 - <<'PY'
import json, sys, os
sys.path.insert(0, '.')
from l7.service.slide_repository import SlideRepository

man = json.load(open("levels/data/manifest.json", encoding="utf-8"))["slides"]
stale = []
for s in SlideRepository("levels/data/slides.json").iter_slides():
    rec = man.get(str(s.id), {})
    path = f"levels/videos/{s.id}.mp4"
    fresh = (rec.get("status") == "ok"
             and rec.get("text_sha256") == s.text_sha256
             and os.path.exists(path) and os.path.getsize(path) > 0)
    why = "" if fresh else f"  [status={rec.get('status')!r}]"
    print(f"  {'ok     ' if fresh else 'STALE  '} {path}  ({s.title}){why}")
    if not fresh:
        stale.append(s.id)
sys.exit(1 if stale else 0)
PY
if [ $? -ne 0 ]; then
  echo "Some slides still carry the old wording — not pushing."
  exit 1
fi

git add levels/videos/ levels/data/slides.json levels/data/manifest.json
if git diff --cached --quiet; then
  echo "[push] nothing new to commit"
  exit 0
fi
git commit -m "feat(levels): re-record russian level narrations with AI naming" >/dev/null
for attempt in 1 2 3 4; do
  if git pull --rebase origin "$BRANCH" && git push -u origin "$BRANCH"; then
    echo "[push] ok"
    exit 0
  fi
  echo "[push] retry $attempt"; sleep $((2 ** attempt))
done
echo "[push] FAILED — videos are on disk, push manually"
exit 1

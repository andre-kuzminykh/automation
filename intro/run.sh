#!/usr/bin/env bash
# Generate the 3 course-intro "circle" talking heads and place them in
# l1/videos/ as _1.mp4 / _2.mp4 / _3.mp4.
#
# Same voice/settings as lecture 1 (Andre [RUS], speed 0.75, 1:1, 540p).
# Reuses the already-uploaded avatar asset (seeded in intro/data/manifest.json),
# so no avatar.jpg download is needed.
#
# Usage (on human-1, venv active, HEDRA_API_KEY exported):
#   git pull --rebase origin claude/setup-gcloud-video-service-XKVf0
#   bash intro/run.sh
set -u

cd "$(dirname "$0")/.."   # repo root

AI_MODEL_ID="26f0fc66-152b-40ab-abed-76c43df99bc8"
VOICE_ID="8e7544c8-a37b-4315-9599-55bad6bfbb7b"
BRANCH="claude/setup-gcloud-video-service-XKVf0"

# 1) Render the 3 intro slides (ids 1..3) into intro/videos/.
python3 -m l7.service.generate --lecture intro \
  --ai-model-id "$AI_MODEL_ID" --voice-id "$VOICE_ID" --no-git || true

# 2) Copy to l1/videos/_1.mp4 .. _3.mp4
ok=1
for n in 1 2 3; do
  if [ -f "intro/videos/$n.mp4" ]; then
    cp "intro/videos/$n.mp4" "l1/videos/_$n.mp4"
    echo "[ok] intro/videos/$n.mp4 -> l1/videos/_$n.mp4"
  else
    echo "[MISSING] intro/videos/$n.mp4 — re-run: python3 -m l7.service.generate --lecture intro --regenerate $n --from $n --to $n --ai-model-id $AI_MODEL_ID --voice-id $VOICE_ID --no-git"
    ok=0
  fi
done

# 3) Commit + push (source data + the 3 circle files; not the intro/videos dupes)
git add l1/videos/_1.mp4 l1/videos/_2.mp4 l1/videos/_3.mp4 \
        intro/data/slides.json intro/data/config.json intro/run.sh 2>/dev/null
if git diff --cached --quiet; then
  echo "[push] nothing to commit"
else
  git commit -m "feat(l1): 3 course-intro circle videos (_1.._3)"
  for attempt in 1 2 3 4; do
    if git pull --rebase origin "$BRANCH" && git push -u origin "$BRANCH"; then
      echo "[push] ok"
      break
    fi
    echo "[push] retry $attempt"; sleep $((2 ** attempt))
  done
fi

[ "$ok" = 1 ] && echo "================ ALL 3 CIRCLES DONE ================" \
             || echo "================ SOME MISSING — see above ================"

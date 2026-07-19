#!/usr/bin/env bash
# Generate course "circle" talking heads and place them in l1/videos/ as _N.mp4.
#   1 — welcome, 2 — for whom, 3 — what you'll learn, 4 — AI-maturity test promo.
#
# By default only circle 4 is generated; pass ids to do others:
#   bash intro/run.sh          # circle 4 only
#   bash intro/run.sh 1 2 3    # circles 1..3
#
# Same voice/settings as the lectures (Andre [RUS], speed 0.75, 1:1, 540p).
# Reuses the already-uploaded avatar asset — no avatar.jpg download needed.
# Idempotent: re-running skips circles that already exist.
set -u

cd "$(dirname "$0")/.."   # repo root

AI_MODEL_ID="26f0fc66-152b-40ab-abed-76c43df99bc8"
VOICE_ID="8e7544c8-a37b-4315-9599-55bad6bfbb7b"
BRANCH="claude/setup-gcloud-video-service-XKVf0"
CIRCLES="${*:-4}"

# Hedra's queue can be slow — give each slide up to 30 min; one retry each.
TIMEOUT=1800

for n in $CIRCLES; do
  for attempt in 1 2; do
    [ -f "intro/videos/$n.mp4" ] && break
    echo "---- circle $n (attempt $attempt) ----"
    python3 -m l7.service.generate --lecture intro \
      --regenerate "$n" --from "$n" --to "$n" \
      --ai-model-id "$AI_MODEL_ID" --voice-id "$VOICE_ID" \
      --poll-timeout "$TIMEOUT" --no-git || true
  done
done

# Copy to l1/videos/_N.mp4 and stage what exists.
ok=1
git add intro/data/slides.json intro/data/config.json intro/run.sh 2>/dev/null
for n in $CIRCLES; do
  if [ -f "intro/videos/$n.mp4" ]; then
    cp "intro/videos/$n.mp4" "l1/videos/_$n.mp4"
    git add "l1/videos/_$n.mp4"
    echo "[ok] intro/videos/$n.mp4 -> l1/videos/_$n.mp4"
  else
    echo "[MISSING] circle $n — re-run: bash intro/run.sh $n"
    ok=0
  fi
done

if git diff --cached --quiet; then
  echo "[push] nothing to commit"
else
  git commit -m "feat(intro): circle video(s) $CIRCLES"
  for attempt in 1 2 3 4; do
    if git pull --rebase origin "$BRANCH" && git push -u origin "$BRANCH"; then
      echo "[push] ok"
      break
    fi
    echo "[push] retry $attempt"; sleep $((2 ** attempt))
  done
fi

[ "$ok" = 1 ] && echo "================ CIRCLES DONE ($CIRCLES) ================" \
             || echo "================ SOME MISSING — see above ================"

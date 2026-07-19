#!/usr/bin/env bash
# Parallel ENGLISH AI-maturity-test head generation (36 videos: 0=promo, 1..35).
#
# Usage (on human-1, venv active, HEDRA_API_KEY exported):
#   git pull --rebase origin claude/setup-gcloud-video-service-XKVf0
#   PAR=4 bash mte/run_parallel.sh           # all slides 0..35, 4 in parallel
#   bash mte/run_parallel.sh 10 20           # subset
set -u

cd "$(dirname "$0")/.."   # repo root

AI_MODEL_ID="26f0fc66-152b-40ab-abed-76c43df99bc8"
VOICE_ID="8e7544c8-a37b-4315-9599-55bad6bfbb7b"
BRANCH="claude/setup-gcloud-video-service-XKVf0"

PAR="${PAR:-3}"
START="${1:-0}"
END="${2:-35}"

render_one() {
  local i="$1"
  echo "---- start slide $i ----"
  python3 -m l7.service.generate --lecture mte \
    --regenerate "$i" --from "$i" --to "$i" \
    --ai-model-id "$AI_MODEL_ID" \
    --voice-id "$VOICE_ID" \
    --poll-timeout 1800 \
    --no-git \
    2>&1 | sed -u "s/^/[s$i] /"
  echo "---- done slide $i ----"
}
export -f render_one
export AI_MODEL_ID VOICE_ID

push_chunk() {
  local label="$1"
  # Reset stray unstaged manifest edits so pull --rebase never blocks the push.
  git add mte/videos/ mte/data/manifest.json 2>/dev/null
  git checkout -- intro/data/manifest.json l1/data/manifest.json \
                  l2/data/manifest.json mt/data/manifest.json 2>/dev/null || true
  if git diff --cached --quiet; then
    echo "[push] nothing to commit ($label)"
    return
  fi
  git commit -m "feat(mte): hedra EN videos for $label" >/dev/null
  for attempt in 1 2 3 4; do
    if git pull --rebase origin "$BRANCH" && git push -u origin "$BRANCH"; then
      echo "[push] ok ($label)"
      return
    fi
    echo "[push] retry $attempt"; sleep $((2 ** attempt))
  done
  echo "[push] FAILED ($label) — videos still on disk, push manually later"
}

i=$START
while [ "$i" -le "$END" ]; do
  chunk_end=$(( i + PAR - 1 ))
  [ "$chunk_end" -gt "$END" ] && chunk_end="$END"

  echo "================ CHUNK $i..$chunk_end (par=$PAR) ================"
  pids=()
  for s in $(seq "$i" "$chunk_end"); do
    render_one "$s" &
    pids+=($!)
  done
  for pid in "${pids[@]}"; do
    wait "$pid" || true
  done

  push_chunk "slides $i..$chunk_end"
  i=$(( chunk_end + 1 ))
done

echo "================ ALL DONE ($START..$END) ================"

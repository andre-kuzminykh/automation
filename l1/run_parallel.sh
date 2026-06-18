#!/usr/bin/env bash
# Parallel lecture-1 head regeneration.
#
# Renders N slides concurrently, then pushes the chunk to git, repeats.
# Compared to l1/run_all.sh: ~3-4x faster but loses some manifest entries
# (the video files themselves are unaffected).
#
# Usage (on human-1, venv active, HEDRA_API_KEY exported):
#   bash l1/run_parallel.sh                  # all slides 0..42, 3 in parallel
#   PAR=4 bash l1/run_parallel.sh            # 4 in parallel
#   bash l1/run_parallel.sh 2 42             # subset
#   PAR=4 bash l1/run_parallel.sh 2 42
set -u

cd "$(dirname "$0")/.."   # repo root

AI_MODEL_ID="26f0fc66-152b-40ab-abed-76c43df99bc8"
VOICE_ID="8e7544c8-a37b-4315-9599-55bad6bfbb7b"
BRANCH="claude/setup-gcloud-video-service-XKVf0"

PAR="${PAR:-3}"
START="${1:-0}"
END="${2:-42}"

render_one() {
  local i="$1"
  echo "---- start slide $i ----"
  python3 -m l7.service.generate --lecture l1 \
    --regenerate "$i" --from "$i" --to "$i" \
    --ai-model-id "$AI_MODEL_ID" \
    --voice-id "$VOICE_ID" \
    --no-git \
    2>&1 | sed -u "s/^/[s$i] /"
  echo "---- done slide $i ----"
}
export -f render_one
export AI_MODEL_ID VOICE_ID

push_chunk() {
  local label="$1"
  git add l1/videos/ l1/data/manifest.json 2>/dev/null
  if git diff --cached --quiet; then
    echo "[push] nothing to commit ($label)"
    return
  fi
  git commit -m "feat(l1): hedra videos for $label" >/dev/null
  for attempt in 1 2 3 4; do
    if git pull --rebase origin "$BRANCH" && \
       git push -u origin "$BRANCH"; then
      echo "[push] ok ($label)"
      return
    fi
    echo "[push] retry $attempt"
    sleep $((2 ** attempt))
  done
  echo "[push] FAILED ($label) — videos still on disk, push manually later"
}

# Process slides in chunks of $PAR.
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

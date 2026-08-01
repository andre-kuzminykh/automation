#!/usr/bin/env bash
# Parallel lecture-3 head generation (chunked, with batched push).
# Renders PAR slides concurrently, pushes the chunk, repeats.
#
# Usage (on human-1, venv active, key in ~/.hedra_key or HEDRA_API_KEY exported):
#   git pull --rebase origin claude/setup-gcloud-video-service-XKVf0
#   bash l3/run_parallel.sh                  # all slides 1..40, 3 in parallel
#   PAR=4 bash l3/run_parallel.sh            # 4 in parallel
#   bash l3/run_parallel.sh 20 40            # subset
#
# Exits non-zero if any slide failed, and prints the exact ids to re-run.
set -u

cd "$(dirname "$0")/.."   # repo root

AI_MODEL_ID="26f0fc66-152b-40ab-abed-76c43df99bc8"
VOICE_ID="8e7544c8-a37b-4315-9599-55bad6bfbb7b"
BRANCH="claude/setup-gcloud-video-service-XKVf0"

PAR="${PAR:-3}"
START="${1:-1}"
END="${2:-40}"

# Per-slide outcome markers: the previous version printed "ALL DONE" even when
# every slide in the run had failed, which hid 21 missing videos last time.
STATUS_DIR="$(mktemp -d)"
trap 'rm -rf "$STATUS_DIR"' EXIT
export STATUS_DIR

render_one() {
  local i="$1"
  local log="$STATUS_DIR/$i.log"
  echo "---- start slide $i ----"
  python3 -m l7.service.generate --lecture l3 \
    --regenerate "$i" --from "$i" --to "$i" \
    --ai-model-id "$AI_MODEL_ID" \
    --voice-id "$VOICE_ID" \
    --poll-timeout 1800 \
    --no-git \
    > "$log" 2>&1
  local rc=$?
  sed -u "s/^/[s$i] /" "$log"

  # The generator exits 0 even when a slide fails, so trust the artifact.
  if [ "$rc" -eq 0 ] && [ -s "l3/videos/$i.mp4" ]; then
    echo "ok" > "$STATUS_DIR/$i.status"
  else
    echo "fail" > "$STATUS_DIR/$i.status"
    if grep -q "INSUFFICIENT_BALANCE" "$log"; then
      touch "$STATUS_DIR/BROKE"
    fi
  fi
  echo "---- done slide $i ----"
}
export -f render_one
export AI_MODEL_ID VOICE_ID

push_chunk() {
  local label="$1"
  git add l3/videos/ l3/data/manifest.json 2>/dev/null
  # Other lectures' manifests may be dirty from earlier runs; a dirty tree
  # blocks `git pull --rebase` and would strand this chunk locally.
  for m in intro l1 l2 mt mte levels app; do
    git checkout -- "$m/data/manifest.json" 2>/dev/null || true
  done
  if git diff --cached --quiet; then
    echo "[push] nothing to commit ($label)"
    return
  fi
  git commit -m "feat(l3): hedra videos for $label" >/dev/null
  for attempt in 1 2 3 4; do
    if git pull --rebase origin "$BRANCH" && git push -u origin "$BRANCH"; then
      echo "[push] ok ($label)"
      return
    fi
    echo "[push] retry $attempt"; sleep $((2 ** attempt))
  done
  echo "[push] FAILED ($label) — videos still on disk, push manually later"
}

# Preflight: a run that cannot afford a single slide should not submit anything.
# Observed cost is ~273 credits/slide (5189 credits bought slides 1..19).
COST_PER_SLIDE=273
want=$(( (END - START + 1) * COST_PER_SLIDE ))
have="$(python3 -m l7.service.generate --lecture l3 --credits-available 2>"$STATUS_DIR/preflight.err" | tail -1)"
[ -s "$STATUS_DIR/preflight.err" ] && sed 's/^/[preflight] /' "$STATUS_DIR/preflight.err"
case "$have" in
  ''|*[!0-9]*)
    echo "[preflight] could not read credit balance — continuing anyway" ;;
  *)
    echo "[preflight] credits available: $have | needed for $((END - START + 1)) slides: ~$want"
    if [ "$have" -lt "$COST_PER_SLIDE" ]; then
      echo "[preflight] ABORT: not enough for even one slide. Top up workspace 58237 first."
      exit 2
    fi
    if [ "$have" -lt "$want" ]; then
      echo "[preflight] WARNING: enough for roughly $((have / COST_PER_SLIDE)) of $((END - START + 1)) slides."
    fi ;;
esac

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

  # Out of credits: every remaining slide would fail the same way and each one
  # still burns a submit + poll cycle. Stop and report instead of grinding on.
  if [ -e "$STATUS_DIR/BROKE" ]; then
    echo "!!! Hedra returned INSUFFICIENT_BALANCE — stopping at slide $((i - 1))."
    break
  fi
done

failed=()
for s in $(seq "$START" "$END"); do
  [ "$(cat "$STATUS_DIR/$s.status" 2>/dev/null)" = "ok" ] || failed+=("$s")
done

echo "================ SUMMARY ($START..$END) ================"
if [ "${#failed[@]}" -eq 0 ]; then
  echo "all $((END - START + 1)) slides OK"
  exit 0
fi
echo "OK: $((END - START + 1 - ${#failed[@]}))   MISSING: ${#failed[@]} -> ${failed[*]}"
echo "re-run with:  bash l3/run_ids.sh ${failed[*]}"
exit 1

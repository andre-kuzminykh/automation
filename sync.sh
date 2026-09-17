#!/usr/bin/env bash
# Pull the working branch, clearing the one thing that reliably blocks it.
#
# A failed slide records status/error into <lecture>/data/manifest.json, so any
# aborted run leaves the tree dirty and `git pull --rebase` refuses to start —
# which silently strands the VM on old code. That has bitten this project
# repeatedly, including a whole run against a dead workspace_id.
#
# Usage (on human-1):
#   bash sync.sh
set -u
cd "$(dirname "$0")"

BRANCH="claude/setup-gcloud-video-service-XKVf0"

dirty_manifests="$(git diff --name-only -- '*/data/manifest.json')"
if [ -n "$dirty_manifests" ]; then
  echo "[sync] discarding manifest changes left by an aborted run:"
  echo "$dirty_manifests" | sed 's/^/  /'
  # Safe to drop: the manifest is a record of what rendered, and the videos on
  # disk are the ground truth. A failed entry carries nothing worth keeping.
  git checkout -- '*/data/manifest.json'
fi

if ! git diff --quiet; then
  echo "[sync] tree still has changes beyond manifests — NOT pulling."
  echo "       Review these, then commit or discard them yourself:"
  git status --short | sed 's/^/  /'
  exit 1
fi

for attempt in 1 2 3 4; do
  if git pull --rebase origin "$BRANCH"; then
    echo "[sync] ok -> $(git rev-parse --short HEAD)"
    echo "[sync] workspace_id in use: $(python3 -c "
import json; print(json.load(open('levels/data/config.json'))['hedra']['workspace_id'])" 2>/dev/null)"
    exit 0
  fi
  echo "[sync] retry $attempt"; sleep $((2 ** attempt))
done
echo "[sync] FAILED to pull"
exit 1

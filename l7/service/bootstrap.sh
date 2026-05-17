#!/usr/bin/env bash
# Bootstrap the gcloud VM `human-1` to run the l7 video generation pipeline.
# Covers NR-F5-1..3, NFR-F5-1..4.
#
# Usage (inside the VM):
#   bash l7/service/bootstrap.sh
#
# Idempotent: safe to re-run.

set -euo pipefail

REPO_URL="${REPO_URL:-https://github.com/andre-kuzminykh/automation.git}"
BRANCH="${BRANCH:-claude/setup-gcloud-video-service-XKVf0}"
WORKDIR="${WORKDIR:-$HOME/automation}"

log() { printf '[bootstrap] %s\n' "$*"; }

require_no_sudo() {
  # NFR-F5-4: prefer running without sudo if possible
  if command -v python3 >/dev/null 2>&1 && command -v ffmpeg >/dev/null 2>&1; then
    log "python3 and ffmpeg already present, skipping apt install"
    return 0
  fi
  if [[ $EUID -ne 0 ]] && ! command -v sudo >/dev/null 2>&1; then
    log "ERROR: need root or sudo to install packages"
    exit 1
  fi
  return 1
}

install_packages() {
  if require_no_sudo; then return 0; fi
  local SUDO=""
  if [[ $EUID -ne 0 ]]; then SUDO=sudo; fi

  log "apt update + install python3, pip, venv, git, ffmpeg, curl"
  $SUDO DEBIAN_FRONTEND=noninteractive apt-get update -y
  $SUDO DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
    python3 python3-pip python3-venv git ffmpeg curl ca-certificates
}

clone_repo() {
  if [[ -d "$WORKDIR/.git" ]]; then
    log "repo exists at $WORKDIR, fetching"
    git -C "$WORKDIR" fetch --depth=50 origin "$BRANCH"
    git -C "$WORKDIR" checkout "$BRANCH"
    git -C "$WORKDIR" pull --ff-only origin "$BRANCH" || true
  else
    log "cloning $REPO_URL into $WORKDIR (branch $BRANCH)"
    git clone --branch "$BRANCH" --depth=50 "$REPO_URL" "$WORKDIR"
  fi
}

setup_venv() {
  cd "$WORKDIR"
  if [[ ! -d ".venv" ]]; then
    log "creating venv"
    python3 -m venv .venv
  fi
  # shellcheck disable=SC1091
  . .venv/bin/activate
  log "installing python deps"
  pip install --upgrade pip
  pip install -r l7/service/requirements.txt
}

main() {
  install_packages
  clone_repo
  setup_venv

  cat <<EOF
[bootstrap] READY
[bootstrap] Next:
  cd $WORKDIR
  source .venv/bin/activate
  export HEDRA_API_KEY=sk_hedra_xxx     # do NOT commit this
  python -m l7.service.generate --lecture l7

EOF
}

main "$@"

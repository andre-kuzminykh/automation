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

# Returns 0 if every required dependency is already installed; 1 otherwise.
deps_ready() {
  command -v python3 >/dev/null 2>&1 || return 1
  command -v ffmpeg  >/dev/null 2>&1 || return 1
  command -v git     >/dev/null 2>&1 || return 1
  command -v curl    >/dev/null 2>&1 || return 1
  # python3-venv is a separate Debian package; the only reliable check is
  # to actually try `python3 -m venv` (it errors with ensurepip otherwise).
  python3 -c "import venv, ensurepip" >/dev/null 2>&1 || return 1
  # python-is-python3 / `python` shim — nice-to-have, not required.
  return 0
}

install_packages() {
  if deps_ready; then
    log "all deps present (python3, python3-venv, pip, git, ffmpeg, curl) — skipping apt install"
    return 0
  fi
  if [[ $EUID -ne 0 ]] && ! command -v sudo >/dev/null 2>&1; then
    log "ERROR: need root or sudo to install packages"
    exit 1
  fi
  local SUDO=""
  if [[ $EUID -ne 0 ]]; then SUDO=sudo; fi

  log "apt update + install python3, pip, venv, git, ffmpeg, curl, python-is-python3"
  $SUDO DEBIAN_FRONTEND=noninteractive apt-get update -y
  $SUDO DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
    python3 python3-pip python3-venv python-is-python3 \
    git ffmpeg curl ca-certificates
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
  # If a previous run left a broken venv (missing bin/activate), drop it.
  if [[ -d ".venv" && ! -f ".venv/bin/activate" ]]; then
    log "removing broken .venv from previous run"
    rm -rf .venv
  fi
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

fetch_avatar() {
  cd "$WORKDIR"
  local DEST="l7/data/avatar.jpg"
  local URL="${AVATAR_URL:-https://i.ibb.co/VcCKP5Kg/photo-2026-05-18-01-41-54.jpg}"
  if [[ -s "$DEST" ]]; then
    log "avatar already present at $DEST ($(stat -c %s "$DEST") bytes)"
    return 0
  fi
  log "downloading avatar from $URL"
  curl -fsSL "$URL" -o "$DEST"
  log "avatar saved to $DEST ($(stat -c %s "$DEST") bytes)"
}

main() {
  install_packages
  clone_repo
  setup_venv
  fetch_avatar

  cat <<EOF
[bootstrap] READY
[bootstrap] Next (paste line by line):
  cd $WORKDIR
  source .venv/bin/activate
  export HEDRA_API_KEY=sk_hedra_xxx     # do NOT commit this
  python3 -m l7.service.generate --lecture l7 --limit 1     # smoke 1 slide
  python3 -m l7.service.generate --lecture l7               # full 50-slide run

EOF
}

main "$@"

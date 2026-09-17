#!/usr/bin/env bash
# Run a long job detached from the SSH session, so closing the laptop does not
# kill it. Without this, the shell gets SIGHUP when the connection drops and
# takes the render with it — the credits for the slide in flight are already
# spent by then, and nothing gets pushed.
#
# Usage (on human-1):
#   bash bg.sh levels_en/run.sh          # start, returns immediately
#   bash bg.sh levels/run.sh
#   tail -f logs/levels_en-run.log       # watch it
#   pkill -f levels_en/run.sh            # stop it
set -u
cd "$(dirname "$0")"

SCRIPT="${1:?usage: bash bg.sh <script.sh> [args...]}"
shift || true
[ -f "$SCRIPT" ] || { echo "no such script: $SCRIPT"; exit 1; }

mkdir -p logs
LOG="logs/$(echo "${SCRIPT%.sh}" | tr '/' '-').log"

nohup setsid bash "$SCRIPT" "$@" > "$LOG" 2>&1 < /dev/null &
PID=$!
sleep 1
if kill -0 "$PID" 2>/dev/null; then
  echo "[bg] started $SCRIPT  pid=$PID"
  echo "[bg] log: $LOG"
  echo "[bg] watch:  tail -f $LOG"
  echo "[bg] stop:   kill $PID"
  echo "[bg] safe to close the laptop now"
else
  echo "[bg] FAILED to start — see $LOG"; tail -5 "$LOG"; exit 1
fi

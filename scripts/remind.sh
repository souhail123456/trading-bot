#!/usr/bin/env bash
# One-task-at-a-time reminder. Advances on 👍 reaction. Resends hourly if no reaction.
# Usage:
#   bash scripts/remind.sh set "<task>"  — queue a task
#   bash scripts/remind.sh check         — check for 👍, advance or resend
#   bash scripts/remind.sh clear         — wipe everything

set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
ENV_FILE="$ROOT/.env"
PENDING="$ROOT/memory/PENDING-REMINDERS.md"
STATE="$ROOT/memory/REMIND-STATE.txt"   # format: message_id\nsent_at

[[ -f "$ENV_FILE" ]] && { set -a; source "$ENV_FILE"; set +a; }

MODE="${1:-check}"
MSG="${2:-}"

tg_send() {
  # Sends a message, prints message_id
  local text="$1"
  [[ -z "${TELEGRAM_BOT_TOKEN:-}" || -z "${TELEGRAM_CHAT_ID:-}" ]] && {
    echo "[remind] Telegram not configured" >&2; echo "0"; return 0
  }
  local payload result msg_id
  payload=$(python3 -c 'import json,sys; print(json.dumps({"chat_id":sys.argv[1],"text":sys.argv[2]}))' \
            "$TELEGRAM_CHAT_ID" "$text")
  result=$(curl -fsS -X POST \
    "https://api.telegram.org/bot${TELEGRAM_BOT_TOKEN}/sendMessage" \
    -H "Content-Type: application/json" \
    -d "$payload")
  msg_id=$(python3 -c 'import json,sys; print(json.loads(sys.argv[1])["result"]["message_id"])' "$result")
  echo "$msg_id"
}

check_reaction() {
  # Returns 0 if user replied "done" in the last 4 hours
  [[ -z "${TELEGRAM_BOT_TOKEN:-}" ]] && return 1
  local since=$(( $(date +%s) - 14400 ))
  local result
  result=$(curl -fsS "https://api.telegram.org/bot${TELEGRAM_BOT_TOKEN}/getUpdates?limit=100")
  python3 - "$result" "$since" <<'EOF'
import json, sys
data = json.loads(sys.argv[1])
since = int(sys.argv[2])
for u in data.get("result", []):
    msg = u.get("message", {})
    if msg.get("date", 0) >= since and "done" in msg.get("text", "").lower():
        sys.exit(0)
sys.exit(1)
EOF
}

send_current_task() {
  local task
  task=$(head -1 "$PENDING")
  local remaining
  remaining=$(wc -l < "$PENDING" | tr -d ' ')
  local suffix=""
  [[ "$remaining" -gt 1 ]] && suffix=" ($((remaining - 1)) more after this)"
  local msg_id
  msg_id=$(tg_send "$(printf 'TO DO%s:\n\n%s\n\nReply DONE when finished.' "$suffix" "$task")")
  printf '%s\n%s\n' "$msg_id" "$(date +%s)" > "$STATE"
  echo "[remind] sent task (msg_id=$msg_id): $task"
}

advance() {
  # Remove first task, send next or close out
  tail -n +2 "$PENDING" > "${PENDING}.tmp" && mv "${PENDING}.tmp" "$PENDING"
  if [[ ! -s "$PENDING" ]]; then
    > "$STATE"
    tg_send "All done!" > /dev/null
    echo "[remind] all tasks complete"
  else
    send_current_task
  fi
}

case "$MODE" in
  set)
    [[ -z "$MSG" ]] && { echo "usage: remind.sh set <task>" >&2; exit 1; }
    was_empty=false
    [[ ! -f "$PENDING" || ! -s "$PENDING" ]] && was_empty=true
    echo "$MSG" >> "$PENDING"
    if $was_empty; then
      send_current_task
    else
      remaining=$(wc -l < "$PENDING" | tr -d ' ')
      echo "[remind] queued as task #${remaining}"
    fi
    ;;

  check)
    [[ ! -f "$PENDING" || ! -s "$PENDING" ]] && { echo "[remind] nothing pending"; exit 0; }

    # Send if no state yet
    if [[ ! -f "$STATE" || ! -s "$STATE" ]]; then
      send_current_task
      exit 0
    fi

    msg_id=$(sed -n '1p' "$STATE")
    sent_at=$(sed -n '2p' "$STATE")
    now=$(date +%s)

    if check_reaction "$msg_id"; then
      advance
    elif (( now - sent_at >= 3600 )); then
      echo "[remind] no 👍 after 1h — resending"
      send_current_task
    else
      echo "[remind] waiting for 👍 on msg_id=$msg_id ($(( (now - sent_at) / 60 ))min ago)"
    fi
    ;;

  clear)
    > "$PENDING"
    > "$STATE" 2>/dev/null || true
    echo "[remind] cleared"
    ;;
esac

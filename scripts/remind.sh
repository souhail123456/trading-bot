#!/usr/bin/env bash
# Reminder manager with Telegram acknowledgment.
# Usage:
#   bash scripts/remind.sh set "<message>"  — queue a reminder and send first alert
#   bash scripts/remind.sh check            — resend if not yet acknowledged
#   bash scripts/remind.sh clear            — force-clear all pending

set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
ENV_FILE="$ROOT/.env"
PENDING="$ROOT/memory/PENDING-REMINDERS.md"

if [[ -f "$ENV_FILE" ]]; then
  set -a
  # shellcheck disable=SC1090
  source "$ENV_FILE"
  set +a
fi

MODE="${1:-check}"
MSG="${2:-}"

tg_send() {
  local text="$1"
  [[ -z "${TELEGRAM_BOT_TOKEN:-}" || -z "${TELEGRAM_CHAT_ID:-}" ]] && {
    echo "[remind] Telegram not configured — skipping" >&2; return 0
  }
  local payload
  payload=$(python3 -c 'import json,sys; print(json.dumps({"chat_id":sys.argv[1],"text":sys.argv[2]}))' \
            "$TELEGRAM_CHAT_ID" "$text")
  curl -fsS -X POST \
    "https://api.telegram.org/bot${TELEGRAM_BOT_TOKEN}/sendMessage" \
    -H "Content-Type: application/json" \
    -d "$payload"
  echo
}

check_done() {
  # Returns 0 if user sent "done" (case-insensitive) in the last 4 hours
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

case "$MODE" in
  set)
    [[ -z "$MSG" ]] && { echo "usage: remind.sh set <message>" >&2; exit 1; }
    echo "$MSG" >> "$PENDING"
    tg_send "ACTION NEEDED: $MSG

Reply DONE when handled."
    echo "[remind] queued and sent"
    ;;

  check)
    [[ ! -f "$PENDING" || ! -s "$PENDING" ]] && { echo "[remind] nothing pending"; exit 0; }
    if check_done; then
      > "$PENDING"
      tg_send "Got it — all reminders cleared."
      echo "[remind] acknowledged — cleared"
    else
      echo "[remind] no 'done' reply — resending $(wc -l < "$PENDING" | tr -d ' ') reminder(s)"
      while IFS= read -r line; do
        [[ -n "$line" ]] && tg_send "REMINDER (reply DONE when handled):

$line"
      done < "$PENDING"
    fi
    ;;

  clear)
    > "$PENDING"
    echo "[remind] cleared"
    ;;
esac

#!/usr/bin/env bash
# Telegram notification wrapper.
# Usage: bash scripts/telegram.sh "<message>"
# Requires TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID in env.

set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
ENV_FILE="$ROOT/.env"

if [[ -f "$ENV_FILE" ]]; then
  set -a
  # shellcheck disable=SC1090
  source "$ENV_FILE"
  set +a
fi

if [[ $# -gt 0 ]]; then
  msg="$*"
else
  msg="$(cat)"
fi

if [[ -z "${msg// /}" ]]; then
  echo "usage: bash scripts/telegram.sh \"<message>\"" >&2
  exit 1
fi

if [[ -z "${TELEGRAM_BOT_TOKEN:-}" || -z "${TELEGRAM_CHAT_ID:-}" ]]; then
  echo "[telegram] TELEGRAM_BOT_TOKEN or TELEGRAM_CHAT_ID not set — skipping" >&2
  exit 2
fi

# --- Proxy support ---
if [[ -n "${PROXY_URL:-}" && -n "${PROXY_TOKEN:-}" ]]; then
  payload="$(python3 -c "
import json, sys
print(json.dumps({'bot_token': sys.argv[1], 'chat_id': sys.argv[2], 'text': sys.argv[3], 'parse_mode': 'Markdown'}))
" "$TELEGRAM_BOT_TOKEN" "$TELEGRAM_CHAT_ID" "$msg")"

  curl -fsS -X POST \
    "${PROXY_URL%/}/telegram" \
    -H "Content-Type: application/json" \
    -H "x-proxy-token: $PROXY_TOKEN" \
    -d "$payload"
else
  payload="$(python3 -c "
import json, sys
print(json.dumps({'chat_id': sys.argv[1], 'text': sys.argv[2], 'parse_mode': 'Markdown'}))
" "$TELEGRAM_CHAT_ID" "$msg")"

  curl -fsS -X POST \
    "https://api.telegram.org/bot${TELEGRAM_BOT_TOKEN}/sendMessage" \
    -H "Content-Type: application/json" \
    -d "$payload"
fi

echo

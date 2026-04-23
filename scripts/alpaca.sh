#!/usr/bin/env bash
# Alpaca API wrapper. All trading API calls go through here.
# Usage: bash scripts/alpaca.sh <subcommand> [args...]

set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
ENV_FILE="$ROOT/.env"

if [[ -f "$ENV_FILE" ]]; then
  set -a
  # shellcheck disable=SC1090
  source "$ENV_FILE"
  set +a
fi

: "${ALPACA_API_KEY:?ALPACA_API_KEY not set in environment}"
: "${ALPACA_SECRET_KEY:?ALPACA_SECRET_KEY not set in environment}"

API="${ALPACA_ENDPOINT:-https://paper-api.alpaca.markets/v2}"
DATA="${ALPACA_DATA_ENDPOINT:-https://data.alpaca.markets/v2}"

H_KEY="APCA-API-KEY-ID: $ALPACA_API_KEY"
H_SEC="APCA-API-SECRET-KEY: $ALPACA_SECRET_KEY"

# --- Proxy support ---
# If PROXY_URL is set, route all calls through the Railway proxy.
if [[ -n "${PROXY_URL:-}" ]]; then
  PROXY="${PROXY_URL%/}"
  H_TOK="x-proxy-token: ${PROXY_TOKEN:?PROXY_TOKEN required when PROXY_URL is set}"
  # For trading API calls, tell the proxy which Alpaca base to use
  H_BASE_API="x-alpaca-base: $API"
  H_BASE_DATA="x-alpaca-base: $DATA"

  alpaca_trade() {
    local method="$1" path="$2"; shift 2
    curl -fsS -X "$method" \
      -H "$H_KEY" -H "$H_SEC" -H "$H_TOK" -H "$H_BASE_API" \
      "$@" "${PROXY}/alpaca/${path}"
  }
  alpaca_data() {
    local method="$1" path="$2"; shift 2
    curl -fsS -X "$method" \
      -H "$H_KEY" -H "$H_SEC" -H "$H_TOK" -H "$H_BASE_DATA" \
      "$@" "${PROXY}/alpaca/${path}"
  }
else
  alpaca_trade() {
    local method="$1" path="$2"; shift 2
    curl -fsS -X "$method" -H "$H_KEY" -H "$H_SEC" "$@" "${API}/${path}"
  }
  alpaca_data() {
    local method="$1" path="$2"; shift 2
    curl -fsS -X "$method" -H "$H_KEY" -H "$H_SEC" "$@" "${DATA}/${path}"
  }
fi

cmd="${1:-}"
shift || true

case "$cmd" in
  account)
    alpaca_trade GET account
    ;;
  positions)
    alpaca_trade GET positions
    ;;
  position)
    sym="${1:?usage: position SYM}"
    alpaca_trade GET "positions/$sym"
    ;;
  quote)
    sym="${1:?usage: quote SYM}"
    alpaca_data GET "stocks/$sym/quotes/latest"
    ;;
  orders)
    status="${1:-open}"
    alpaca_trade GET "orders?status=$status"
    ;;
  order)
    body="${1:?usage: order '<json>'}"
    alpaca_trade POST orders -H "Content-Type: application/json" -d "$body"
    ;;
  cancel)
    oid="${1:?usage: cancel ORDER_ID}"
    alpaca_trade DELETE "orders/$oid"
    ;;
  cancel-all)
    alpaca_trade DELETE orders
    ;;
  close)
    sym="${1:?usage: close SYM}"
    alpaca_trade DELETE "positions/$sym"
    ;;
  close-all)
    alpaca_trade DELETE positions
    ;;
  *)
    echo "Usage: bash scripts/alpaca.sh <account|positions|position|quote|orders|order|cancel|cancel-all|close|close-all> [args]" >&2
    exit 1
    ;;
esac

echo

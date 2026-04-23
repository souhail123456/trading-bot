#!/usr/bin/env bash
set -euo pipefail

ROUTINE="${1:?Usage: run-routine.sh <routine-name>}"
ROUTINE_FILE="routines/${ROUTINE}.md"

if [[ ! -f "$ROUTINE_FILE" ]]; then
  echo "Routine not found: $ROUTINE_FILE" >&2
  exit 1
fi

# Configure git auth for push-back
git remote set-url origin "https://x-token:${GITHUB_TOKEN}@github.com/souhail123456/trading-bot.git"
git config user.email "bot@railway.app"
git config user.name "Trading Bot"

# Pull latest state (previous runs may have committed memory updates)
git fetch origin main
git reset --hard origin/main

# Run the routine via Claude Code CLI
claude -p "$(cat "$ROUTINE_FILE")" \
  --allowedTools "Bash,Read,Write,Edit,WebSearch,WebFetch"

# Push any commits the routine made
git push origin main || true

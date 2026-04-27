#!/usr/bin/env bash
# Call Groq API with automatic fallback to smaller model if rate-limited.
# Usage: bash scripts/call_groq.sh /tmp/prompt.json /tmp/groq_response.json
set -euo pipefail

PROMPT_FILE="${1:-/tmp/prompt.json}"
OUTPUT_FILE="${2:-/tmp/groq_response.json}"

# First try with the model specified in the prompt
HTTP=$(curl -s -o "$OUTPUT_FILE" -w "%{http_code}" \
  -X POST "https://api.groq.com/openai/v1/chat/completions" \
  -H "Authorization: Bearer $GROQ_API_KEY" \
  -H "Content-Type: application/json" \
  -d @"$PROMPT_FILE")

if [ "$HTTP" = "200" ]; then
  echo "Groq OK (primary model)"
  exit 0
fi

# Check if rate limited
if grep -q "rate_limit" "$OUTPUT_FILE" 2>/dev/null; then
  echo "Rate limited on primary model — falling back to llama-3.1-8b-instant"

  # Swap model in prompt
  sed -i 's/llama-3.3-70b-versatile/llama-3.1-8b-instant/g' "$PROMPT_FILE"

  HTTP=$(curl -s -o "$OUTPUT_FILE" -w "%{http_code}" \
    -X POST "https://api.groq.com/openai/v1/chat/completions" \
    -H "Authorization: Bearer $GROQ_API_KEY" \
    -H "Content-Type: application/json" \
    -d @"$PROMPT_FILE")

  if [ "$HTTP" = "200" ]; then
    echo "Groq OK (fallback: 8b)"
    exit 0
  fi
fi

echo "Groq FAILED — HTTP $HTTP"
cat "$OUTPUT_FILE"
exit 1

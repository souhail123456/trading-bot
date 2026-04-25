#!/usr/bin/env python3
"""Parse Groq response into trade-log entry and telegram message."""
import json

resp = json.load(open("/tmp/groq_response.json"))
content = resp["choices"][0]["message"]["content"]

parts = content.split("===TELEGRAM===")
trade_log_entry = parts[0].strip()
telegram_msg = parts[1].strip() if len(parts) > 1 else "EOD summary generated - check git for details"

with open("/tmp/trade_log_entry.md", "w") as f:
    f.write(trade_log_entry)

with open("/tmp/telegram_msg.txt", "w") as f:
    f.write(telegram_msg)

print("=== Trade Log Entry ===")
print(trade_log_entry)
print()
print("=== Telegram Message ===")
print(telegram_msg)

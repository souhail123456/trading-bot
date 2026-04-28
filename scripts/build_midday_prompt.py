#!/usr/bin/env python3
"""Build the Groq prompt JSON for midday scan."""
import json, os, sys
sys.path.insert(0, os.path.dirname(__file__))
from prompt_utils import recent_trade_log, recent_research_log, compact_strategy

account = json.load(open("/tmp/account.json"))
positions = json.load(open("/tmp/positions.json"))
orders = json.load(open("/tmp/orders.json"))

with open("memory/TRADE-LOG.md") as f:
    trade_log = f.read()
with open("memory/RESEARCH-LOG.md") as f:
    research_log = f.read()
with open("memory/TRADING-STRATEGY.md") as f:
    strategy = f.read()

date = os.popen("date -u +%Y-%m-%d").read().strip()

system_msg = """You are an autonomous AI trading bot managing a paper ~$100,000 Alpaca account.
You run the midday scan — cut losers, tighten stops, check theses. Be ultra-concise.

Output a JSON action plan, then ===TELEGRAM===, then a Telegram message (only if action taken).

ACTION PLAN FORMAT (valid JSON):
{
  "cuts": [
    {"symbol": "SYM", "reason": "-7% rule or thesis broken", "unrealized_plpc": "-0.08"}
  ],
  "stop_tightens": [
    {"symbol": "SYM", "old_trail": "10", "new_trail": "7", "reason": "up 15%+", "cancel_order_id": "xxx"}
  ],
  "thesis_checks": [
    {"symbol": "SYM", "status": "intact or broken", "notes": "..."}
  ],
  "trade_log_entry": "markdown to append if any action taken, or empty string"
}

===TELEGRAM===
<action summary or "Midday scan — no action needed">

RULES:
- Cut any position with unrealized_plpc <= -0.07
- Cut if thesis is broken even if not at -7%
- Tighten trail to 7% at +15%, to 5% at +20%
- Never tighten within 3% of current price
- Never move a stop down"""

user_msg = f"""Date: {date}

=== ACCOUNT ===
{json.dumps(account, indent=2)}

=== POSITIONS ===
{json.dumps(positions, indent=2)}

=== OPEN ORDERS (check for existing stops) ===
{json.dumps(orders, indent=2)}

=== RECENT TRADE LOG ===
{recent_trade_log(trade_log, 800)}

=== TODAY'S RESEARCH ===
{recent_research_log(research_log, 800)}

=== STRATEGY ===
{compact_strategy(strategy)}

Run the midday scan. For each position: check P&L vs -7% cut rule, check if stop needs tightening, check if thesis still holds."""

payload = {
    "model": "llama-3.3-70b-versatile",
    "messages": [
        {"role": "system", "content": system_msg},
        {"role": "user", "content": user_msg}
    ],
    "max_tokens": 1500,
    "temperature": 0.2
}

with open("/tmp/prompt.json", "w") as f:
    json.dump(payload, f)
print("Midday prompt built")

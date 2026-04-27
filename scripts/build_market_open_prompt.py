#!/usr/bin/env python3
"""Build the Groq prompt JSON for market-open execution."""
import json, os

account = json.load(open("/tmp/account.json"))
positions = json.load(open("/tmp/positions.json"))
orders = json.load(open("/tmp/orders.json"))

with open("memory/TRADE-LOG.md") as f:
    trade_log = f.read()
with open("memory/RESEARCH-LOG.md") as f:
    research_log = f.read()
with open("memory/TRADING-STRATEGY.md") as f:
    strategy = f.read()

# Read quotes if available
quotes = ""
if os.path.exists("/tmp/quotes.txt"):
    with open("/tmp/quotes.txt") as f:
        quotes = f.read()

date = os.popen("date -u +%Y-%m-%d").read().strip()

system_msg = """You are an autonomous AI trading bot managing a paper ~$100,000 Alpaca account.
You run the market-open execution workflow. Be ultra-concise.

You MUST output a JSON action plan, then ===TELEGRAM=== separator, then a Telegram message.

ACTION PLAN FORMAT (valid JSON):
{
  "action": "HOLD" or "TRADE",
  "reason": "one line",
  "trades": [
    {
      "symbol": "SYM",
      "qty": "N",
      "side": "buy",
      "catalyst": "one line",
      "entry_price": "X.XX",
      "stop_pct": "10",
      "target": "X.XX"
    }
  ],
  "trade_log_entry": "markdown entry for TRADE-LOG"
}

If action is HOLD, trades array should be empty.

===TELEGRAM===
<message if trade placed, or "No trades at open — holding" if HOLD>

CRITICAL RULES — skip any trade that fails these:
- Total positions after trade <= 6
- Trades this week <= 3
- Position cost <= 20% of equity
- Catalyst documented in today's RESEARCH-LOG
- daytrade_count < 3"""

user_msg = f"""Date: {date}

=== ACCOUNT ===
{json.dumps(account, indent=2)}

=== POSITIONS ===
{json.dumps(positions, indent=2)}

=== OPEN ORDERS ===
{json.dumps(orders, indent=2)}

=== LIVE QUOTES ===
{quotes}

=== TODAY'S RESEARCH LOG ===
{research_log[-1500:]}

=== RECENT TRADE LOG ===
{trade_log[-1000:]}

=== STRATEGY ===
{strategy}

Decide: execute trades from today's research, or HOLD. Default HOLD unless thesis is confirmed by live data."""

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
print("Market-open prompt built")

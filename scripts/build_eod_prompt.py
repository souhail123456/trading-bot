#!/usr/bin/env python3
"""Build the Groq prompt JSON for EOD summary."""
import json
import os
from datetime import datetime

account = json.load(open("/tmp/account.json"))
positions = json.load(open("/tmp/positions.json"))
orders = json.load(open("/tmp/orders.json"))

with open("memory/TRADE-LOG.md") as f:
    trade_log = f.read()

with open("memory/TRADING-STRATEGY.md") as f:
    strategy = f.read()

date = os.popen("date -u +%Y-%m-%d").read().strip()
day_of_week = os.popen("date -u +%A").read().strip()

phase_start = datetime(2026, 4, 21)
today = datetime.strptime(date, "%Y-%m-%d")
day_num = (today - phase_start).days + 1

system_msg = """You are an autonomous AI trading bot managing a paper ~$100,000 Alpaca account.
You produce EOD (end-of-day) summaries. Be ultra-concise: short bullets, no fluff.
Output EXACTLY two sections separated by ===TELEGRAM===:

SECTION 1: The TRADE-LOG entry to append (markdown, matching the format below exactly)
SECTION 2: A Telegram message (plain text, <=15 lines)

TRADE-LOG format:
### MMM DD — EOD Snapshot (Day N, Weekday)
**Portfolio:** $X | **Cash:** $X (X%) | **Day P&L:** +$X (+X%) | **Phase P&L:** +$X (+X%)

| Ticker | Shares | Entry | Close | Day Chg | Unrealized P&L | Stop |
|--------|--------|-------|-------|---------|----------------|------|
| ... |

**Notes:** one-paragraph summary of the day.

---

Telegram format:
EOD MMM DD
Portfolio: $X (+X% day, +X% phase)
Cash: $X
Trades today: <list or none>
Open positions:
  SYM +X.X% (stop $X)
Tomorrow: <one-line plan>"""

user_msg = f"""Date: {date} ({day_of_week}), Day {day_num} of trading phase.
Starting equity (phase): $100,000

=== ACCOUNT DATA ===
{json.dumps(account, indent=2)}

=== POSITIONS ===
{json.dumps(positions, indent=2)}

=== OPEN ORDERS ===
{json.dumps(orders, indent=2)}

=== RECENT TRADE LOG ===
{trade_log[-1500:]}

=== STRATEGY RULES ===
{strategy}

Produce the EOD summary now. Remember:
- Day P&L = today equity minus last EOD equity (find it in the trade log)
- Phase P&L = today equity minus $100,000
- For stops: check open orders for trailing_stop orders
- Include ALL open positions in the table
- Keep Telegram message <=15 lines"""

payload = {
    "model": "llama-3.3-70b-versatile",
    "messages": [
        {"role": "system", "content": system_msg},
        {"role": "user", "content": user_msg}
    ],
    "max_tokens": 1500,
    "temperature": 0.3
}

with open("/tmp/prompt.json", "w") as f:
    json.dump(payload, f)

print("Prompt built successfully")

#!/usr/bin/env python3
"""Update the machine-readable SUMMARY comment at the top of TRADE-LOG.md."""
import json, re, os
from datetime import datetime, timezone

account = json.load(open("/tmp/account.json"))
positions = json.load(open("/tmp/positions.json"))

equity = float(account["equity"])
cash = float(account["cash"])
total_pnl = equity - 100000.0

# Build open_positions array
open_pos = []
for p in positions:
    open_pos.append({
        "symbol": p["symbol"],
        "shares": int(p["qty"]),
        "entry": float(p["avg_entry_price"]),
        "side": "BUY" if p["side"] == "long" else "SELL",
        "unrealized_pnl": round(float(p["unrealized_pl"]), 2)
    })

# Read existing file to preserve closed_trades
trade_log_path = "memory/TRADE-LOG.md"
with open(trade_log_path) as f:
    content = f.read()

# Extract existing closed_trades from old summary
closed_trades = []
m = re.search(r'closed_trades:\s*(\[.*?\])', content)
if m:
    try:
        closed_trades = json.loads(m.group(1))
    except json.JSONDecodeError:
        closed_trades = []

# Merge any newly closed trades from midday/market-open
if os.path.exists("/tmp/closed_trades_new.json"):
    with open("/tmp/closed_trades_new.json") as f:
        new_closed = json.load(f)
    closed_trades.extend(new_closed)

now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

summary = f"""<!-- SUMMARY
portfolio_value: {equity:.2f}
cash: {cash:.2f}
total_pnl: {total_pnl:.2f}
open_positions: {json.dumps(open_pos)}
closed_trades: {json.dumps(closed_trades)}
last_updated: {now}
-->"""

# Replace existing summary or prepend
if content.startswith("<!-- SUMMARY"):
    # Replace everything up to and including -->
    content = re.sub(r'<!-- SUMMARY.*?-->', summary, content, count=1, flags=re.DOTALL)
else:
    content = summary + "\n\n" + content

with open(trade_log_path, "w") as f:
    f.write(content)

print(f"Summary updated: ${equity:.2f} | P&L: ${total_pnl:.2f} | Positions: {len(open_pos)} open, {len(closed_trades)} closed")

#!/usr/bin/env python3
"""Update the machine-readable SUMMARY comment at the top of TRADE-LOG.md."""
import json, re, os, urllib.request
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

# Detect vanished positions (trailing stop / stop-loss triggered by Alpaca)
prev_open = []
pm = re.search(r'open_positions:\s*(\[.*?\])', content)
if pm:
    try:
        prev_open = json.loads(pm.group(1))
    except json.JSONDecodeError:
        prev_open = []

current_syms = {p["symbol"] for p in positions}
closed_syms = {ct["symbol"] for ct in closed_trades}

for prev in prev_open:
    sym = prev["symbol"]
    if sym in current_syms or sym in closed_syms:
        continue
    # Position vanished — query Alpaca for the filled sell order
    reason = "stop_triggered"
    exit_price = None
    try:
        api_key = os.environ.get("ALPACA_API_KEY", "")
        secret_key = os.environ.get("ALPACA_SECRET_KEY", "")
        url = f"https://paper-api.alpaca.markets/v2/orders?status=closed&symbols={sym}&limit=5&direction=desc"
        req = urllib.request.Request(url, headers={
            "APCA-API-KEY-ID": api_key,
            "APCA-API-SECRET-KEY": secret_key,
        })
        with urllib.request.urlopen(req, timeout=10) as resp:
            orders = json.loads(resp.read().decode())
        for order in orders:
            if order.get("side") == "sell" and order.get("status") == "filled":
                exit_price = float(order["filled_avg_price"])
                otype = order.get("type", "unknown")
                if otype == "trailing_stop":
                    reason = "trailing_stop"
                elif otype == "stop":
                    reason = "stop_loss"
                else:
                    reason = otype
                break
    except Exception as e:
        print(f"Warning: could not query Alpaca orders for {sym}: {e}")

    entry_price = prev.get("entry", 0)
    shares = prev.get("shares", 0)
    pnl = round((exit_price - entry_price) * shares, 2) if exit_price else None
    closed_trades.append({
        "symbol": sym,
        "entry": entry_price,
        "exit": exit_price,
        "shares": shares,
        "pnl": pnl,
        "reason": reason,
        "date": datetime.now(timezone.utc).strftime("%Y-%m-%d"),
    })
    print(f"Vanished position detected: {sym} — {reason}, exit={exit_price}, pnl={pnl}")

# Merge any newly closed trades from midday/market-open (deduplicated)
if os.path.exists("/tmp/closed_trades_new.json"):
    with open("/tmp/closed_trades_new.json") as f:
        new_closed = json.load(f)
    already = {ct["symbol"] for ct in closed_trades}
    for nc in new_closed:
        if nc["symbol"] not in already:
            closed_trades.append(nc)

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

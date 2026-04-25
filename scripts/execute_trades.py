#!/usr/bin/env python3
"""Execute trades from Groq's market-open action plan."""
import json, os, subprocess, sys, time

resp = json.load(open("/tmp/groq_response.json"))
content = resp["choices"][0]["message"]["content"]

# Split into action plan and telegram
parts = content.split("===TELEGRAM===")
plan_text = parts[0].strip()
telegram_msg = parts[1].strip() if len(parts) > 1 else "No trades at open — holding"

# Save telegram message
with open("/tmp/telegram_msg.txt", "w") as f:
    f.write(telegram_msg)

# Try to parse JSON from the plan
# Find JSON block
json_start = plan_text.find("{")
json_end = plan_text.rfind("}") + 1
if json_start == -1:
    print("No JSON action plan found — defaulting to HOLD")
    with open("/tmp/trade_log_entry.md", "w") as f:
        f.write("")
    sys.exit(0)

try:
    plan = json.loads(plan_text[json_start:json_end])
except json.JSONDecodeError as e:
    print(f"Failed to parse action plan JSON: {e}")
    print("Defaulting to HOLD")
    with open("/tmp/trade_log_entry.md", "w") as f:
        f.write("")
    sys.exit(0)

action = plan.get("action", "HOLD")
print(f"Action: {action} — {plan.get('reason', 'no reason')}")

if action == "HOLD" or not plan.get("trades"):
    print("HOLD — no trades to execute")
    with open("/tmp/trade_log_entry.md", "w") as f:
        f.write(plan.get("trade_log_entry", ""))
    sys.exit(0)

# Execute trades
API_KEY = os.environ["ALPACA_API_KEY"]
API_SECRET = os.environ["ALPACA_SECRET_KEY"]
BASE = "https://paper-api.alpaca.markets/v2"

def alpaca(method, path, data=None):
    import urllib.request
    url = f"{BASE}/{path}"
    body = json.dumps(data).encode() if data else None
    req = urllib.request.Request(url, data=body, method=method)
    req.add_header("APCA-API-KEY-ID", API_KEY)
    req.add_header("APCA-API-SECRET-KEY", API_SECRET)
    if data:
        req.add_header("Content-Type", "application/json")
    try:
        resp = urllib.request.urlopen(req)
        return json.loads(resp.read())
    except Exception as e:
        print(f"Alpaca API error: {e}")
        return None

executed = []
for trade in plan["trades"]:
    sym = trade["symbol"]
    qty = str(trade["qty"])
    side = trade.get("side", "buy")

    print(f"\nExecuting: {side} {qty} {sym}")

    # Place market order
    order = alpaca("POST", "orders", {
        "symbol": sym,
        "qty": qty,
        "side": side,
        "type": "market",
        "time_in_force": "day"
    })

    if not order:
        print(f"FAILED to place {side} order for {sym}")
        continue

    print(f"Order placed: {order.get('id')} — status: {order.get('status')}")

    # Wait briefly for fill
    time.sleep(3)

    # Check fill
    filled = alpaca("GET", f"orders/{order['id']}")
    if filled and filled.get("status") == "filled":
        fill_price = filled.get("filled_avg_price", trade.get("entry_price", "?"))
        print(f"FILLED: {sym} {qty}sh @ ${fill_price}")

        # Place trailing stop
        stop_pct = trade.get("stop_pct", "10")
        stop_order = alpaca("POST", "orders", {
            "symbol": sym,
            "qty": qty,
            "side": "sell",
            "type": "trailing_stop",
            "trail_percent": stop_pct,
            "time_in_force": "gtc"
        })
        if stop_order:
            print(f"Trailing stop placed: {stop_pct}% — order {stop_order.get('id')}")
        else:
            # Fallback: fixed stop
            try:
                stop_price = round(float(fill_price) * (1 - float(stop_pct)/100), 2)
                stop_order = alpaca("POST", "orders", {
                    "symbol": sym,
                    "qty": qty,
                    "side": "sell",
                    "type": "stop",
                    "stop_price": str(stop_price),
                    "time_in_force": "gtc"
                })
                print(f"Fixed stop placed at ${stop_price}")
            except:
                print(f"WARNING: No stop set for {sym} — set manually!")

        executed.append({"symbol": sym, "qty": qty, "price": fill_price, "stop_pct": stop_pct})
    else:
        print(f"Order not yet filled — status: {filled.get('status') if filled else 'unknown'}")
        executed.append({"symbol": sym, "qty": qty, "price": "pending", "stop_pct": trade.get("stop_pct", "10")})

# Save trade log entry
with open("/tmp/trade_log_entry.md", "w") as f:
    entry = plan.get("trade_log_entry", "")
    if executed and not entry:
        lines = []
        for t in executed:
            lines.append(f"- BUY {t['qty']}sh {t['symbol']} @ ${t['price']}, {t['stop_pct']}% trailing stop")
        entry = "\n".join(lines)
    f.write(entry)

# Update telegram with actual fills
if executed:
    fills = ", ".join([f"{t['symbol']} {t['qty']}sh @${t['price']}" for t in executed])
    with open("/tmp/telegram_msg.txt", "w") as f:
        f.write(f"Market Open — Trades executed:\n{fills}\n{plan.get('reason', '')}")

print(f"\nDone — {len(executed)} trades executed")

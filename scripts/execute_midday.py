#!/usr/bin/env python3
"""Execute midday scan actions — cut losers, tighten stops."""
import json, os, sys

resp = json.load(open("/tmp/groq_response.json"))
content = resp["choices"][0]["message"]["content"]

parts = content.split("===TELEGRAM===")
plan_text = parts[0].strip()
telegram_msg = parts[1].strip() if len(parts) > 1 else "Midday scan — no action needed"

with open("/tmp/telegram_msg.txt", "w") as f:
    f.write(telegram_msg)

# Parse JSON
json_start = plan_text.find("{")
json_end = plan_text.rfind("}") + 1
if json_start == -1:
    print("No JSON — no action needed")
    with open("/tmp/trade_log_entry.md", "w") as f:
        f.write("")
    sys.exit(0)

try:
    plan = json.loads(plan_text[json_start:json_end])
except json.JSONDecodeError as e:
    print(f"JSON parse error: {e} — no action")
    with open("/tmp/trade_log_entry.md", "w") as f:
        f.write("")
    sys.exit(0)

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
        print(f"Alpaca error: {e}")
        return None

actions_taken = []
closed_trades_new = []

# Cut losers
for cut in plan.get("cuts", []):
    sym = cut["symbol"]
    print(f"CUTTING {sym}: {cut['reason']}")

    # Get position details before closing
    pos = alpaca("GET", f"positions/{sym}")
    entry_price = float(pos["avg_entry_price"]) if pos else 0
    current_price = float(pos["current_price"]) if pos else 0
    qty = int(pos["qty"]) if pos else 0

    result = alpaca("DELETE", f"positions/{sym}")
    if result:
        print(f"Closed {sym}")
        actions_taken.append(f"CUT {sym} ({cut['reason']})")
        realized_pnl = round((current_price - entry_price) * qty, 2)
        closed_trades_new.append({
            "symbol": sym, "shares": qty, "entry": entry_price,
            "exit": current_price, "realized_pnl": realized_pnl,
            "reason": cut["reason"]
        })

    # Cancel its stop order
    cancel_id = cut.get("cancel_order_id")
    if cancel_id:
        alpaca("DELETE", f"orders/{cancel_id}")
        print(f"Cancelled stop order {cancel_id}")

# Tighten stops
for tighten in plan.get("stop_tightens", []):
    sym = tighten["symbol"]
    old_id = tighten.get("cancel_order_id")
    new_trail = tighten["new_trail"]

    print(f"TIGHTENING {sym}: {tighten['old_trail']}% -> {new_trail}%")

    # Cancel old stop
    if old_id:
        alpaca("DELETE", f"orders/{old_id}")
        print(f"Cancelled old stop {old_id}")

    # Get current position qty
    pos = alpaca("GET", f"positions/{sym}")
    if pos:
        qty = pos["qty"]
        stop_order = alpaca("POST", "orders", {
            "symbol": sym,
            "qty": qty,
            "side": "sell",
            "type": "trailing_stop",
            "trail_percent": str(new_trail),
            "time_in_force": "gtc"
        })
        if stop_order:
            print(f"New {new_trail}% trailing stop: {stop_order['id']}")
            actions_taken.append(f"TIGHTEN {sym} stop {tighten['old_trail']}%->{new_trail}%")

# Save trade log entry
with open("/tmp/trade_log_entry.md", "w") as f:
    entry = plan.get("trade_log_entry", "")
    f.write(entry)

# Save closed trades for summary updater
if closed_trades_new:
    with open("/tmp/closed_trades_new.json", "w") as f:
        json.dump(closed_trades_new, f)

# Update telegram if actions were taken
if actions_taken:
    with open("/tmp/telegram_msg.txt", "w") as f:
        f.write("Midday scan actions:\n" + "\n".join(actions_taken))

print(f"\nDone — {len(actions_taken)} actions taken")

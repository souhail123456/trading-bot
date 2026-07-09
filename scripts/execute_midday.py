#!/usr/bin/env python3
"""Execute midday scan actions — cut losers, tighten stops.

Hardened with:
- Clamp sells: never sell more than held qty, block sells with no position
- Verified fills: poll order status before recording
- client_order_id for idempotent retries
- Cash guard on any new buys
"""
import json, os, sys, uuid

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
    except urllib.request.HTTPError as e:
        body_text = e.read().decode() if e.fp else ""
        print(f"Alpaca error: {e.code} {e.reason} — {body_text[:300]}")
        return None
    except Exception as e:
        print(f"Alpaca error: {e}")
        return None


def wait_for_fill(order_id, max_retries=30, delay=2):
    """Poll order status until filled/rejected/canceled."""
    import time
    for i in range(max_retries):
        order = alpaca("GET", f"orders/{order_id}")
        if not order:
            time.sleep(delay)
            continue
        status = order.get("status", "unknown")
        if status == "filled":
            return order
        if status in ("rejected", "canceled", "expired", "done_for_day", "replaced"):
            return order
        if i < max_retries - 1:
            time.sleep(delay)
    return order


def close_position(sym):
    """Close position using DELETE /v2/positions/{sym} endpoint."""
    import urllib.request
    url = f"{BASE}/positions/{sym}"
    req = urllib.request.Request(url, method="DELETE")
    req.add_header("APCA-API-KEY-ID", API_KEY)
    req.add_header("APCA-API-SECRET-KEY", API_SECRET)
    try:
        resp = urllib.request.urlopen(req)
        return json.loads(resp.read())
    except urllib.request.HTTPError as e:
        body_text = e.read().decode() if e.fp else ""
        print(f"DELETE /positions/{sym} error: {e.code} {e.reason} — {body_text[:300]}")
        return None
    except Exception as e:
        print(f"DELETE /positions/{sym} error: {e}")
        return None

actions_taken = []
closed_trades_new = []

# Safety net: detect "cut" mentions in trade_log_entry that aren't in the cuts array
trade_log_text = plan.get("trade_log_entry", "").lower()
cuts_symbols = {c["symbol"].upper() for c in plan.get("cuts", [])}

# Load current positions to cross-check
positions_file = "/tmp/positions.json"
held_symbols = set()
if os.path.exists(positions_file):
    for p in json.load(open(positions_file)):
        held_symbols.add(p["symbol"].upper())

import re
for sym in held_symbols:
    # Only match explicit "cut MSFT", "close MSFT", "exit MSFT", "closed MSFT", "cutting MSFT"
    pattern = rf'\b(cut|cuts|cutting|close|closed|closing|exit|exiting)\s+{re.escape(sym)}\b'
    if re.search(pattern, trade_log_text, re.IGNORECASE):
        if sym not in cuts_symbols:
            print(f"WARNING: trade_log_entry mentions cutting {sym} but it's NOT in cuts array — forcing cut")
            plan.setdefault("cuts", []).append({"symbol": sym, "reason": "auto-detected from trade_log_entry (LLM omitted from cuts)"})

# Also enforce: if thesis_checks says "broken", force into cuts
for check in plan.get("thesis_checks", []):
    if check.get("status", "").lower() == "broken":
        sym = check["symbol"].upper()
        if sym not in cuts_symbols and sym in held_symbols:
            print(f"WARNING: thesis broken for {sym} but NOT in cuts — forcing cut")
            plan.setdefault("cuts", []).append({"symbol": sym, "reason": f"thesis broken: {check.get('notes', '')}"})

# Cut losers
for cut in plan.get("cuts", []):
    sym = cut["symbol"]
    print(f"CUTTING {sym}: {cut['reason']}")

    # Get position details before closing
    pos = alpaca("GET", f"positions/{sym}")
    entry_price = float(pos["avg_entry_price"]) if pos else 0
    current_price = float(pos["current_price"]) if pos else 0
    qty = int(pos["qty"]) if pos else 0

    # Cancel ALL open orders for this symbol (trailing stops lock shares)
    if pos and qty > 0:
        # Fetch fresh open orders for this symbol directly from API
        open_orders = alpaca("GET", f"orders?status=open&symbols={sym}") or []
        if isinstance(open_orders, list):
            for o in open_orders:
                print(f"  Cancelling order {o['id']} ({o.get('type','?')}) holding {sym} shares...")
                alpaca("DELETE", f"orders/{o['id']}")
        else:
            # Fallback: cancel all orders for symbol from cached file
            try:
                all_orders = json.load(open("/tmp/orders.json")) if os.path.exists("/tmp/orders.json") else []
                for o in all_orders:
                    if o.get("symbol") == sym and o.get("status") in ("new", "accepted", "held"):
                        print(f"  Cancelling order {o['id']} ({o.get('type','?')}) holding {sym} shares...")
                        alpaca("DELETE", f"orders/{o['id']}")
            except Exception as e:
                print(f"  Warning: could not cancel orders for {sym}: {e}")

        # Now close via market sell order, fallback to DELETE /positions/{sym}
        import time; time.sleep(0.5)  # brief pause for cancel to propagate
        side = "sell" if pos.get("side", "long") == "long" else "buy"
        client_id = f"tb-cut-{sym}-{uuid.uuid4().hex[:8]}"
        result = alpaca("POST", "orders", {
            "symbol": sym,
            "qty": str(qty),
            "side": side,
            "type": "market",
            "time_in_force": "day",
            "client_order_id": client_id
        })
        if not result or not result.get("id"):
            print(f"POST /orders failed for {sym}, trying DELETE /positions/{sym}...")
            result = close_position(sym)
        if result and result.get("id"):
            # Wait for fill confirmation
            filled = wait_for_fill(result["id"], max_retries=30, delay=2)
            if filled and filled.get("status") == "filled":
                actual_exit = float(filled.get("filled_avg_price", current_price))
                actual_qty = int(filled.get("filled_qty", qty))
                print(f"Closed {sym}: CONFIRMED FILL {actual_qty}sh @ ${actual_exit}")
                actions_taken.append(f"CUT {sym} ({cut['reason']})")
                realized_pnl = round((actual_exit - entry_price) * actual_qty, 2)
                closed_trades_new.append({
                    "symbol": sym, "shares": actual_qty, "entry": entry_price,
                    "exit": actual_exit, "realized_pnl": realized_pnl,
                    "reason": cut["reason"]
                })
            else:
                print(f"Close order for {sym} not filled — status: {filled.get('status') if filled else 'unknown'}")
        elif result and result.get("status"):
            # DELETE /positions fallback succeeded
            print(f"Closed {sym} via DELETE: {result.get('status', 'ok')}")
            actions_taken.append(f"CUT {sym} ({cut['reason']})")
            realized_pnl = round((current_price - entry_price) * qty, 2)
            closed_trades_new.append({
                "symbol": sym, "shares": qty, "entry": entry_price,
                "exit": current_price, "realized_pnl": realized_pnl,
                "reason": cut["reason"]
            })
        else:
            print(f"Failed to close {sym} via both methods")
    else:
        print(f"No position found for {sym}")

    # Cancel its stop order
    cancel_id = cut.get("cancel_order_id")
    if cancel_id:
        alpaca("DELETE", f"orders/{cancel_id}")
        print(f"Cancelled stop order {cancel_id}")

# Partial profit takes (sell half at +8%)
for take in plan.get("partial_takes", []):
    sym = take["symbol"]
    sell_qty = int(take.get("sell_qty", 0))
    if sell_qty <= 0:
        print(f"SKIP partial take {sym}: invalid qty {sell_qty}")
        continue

    print(f"PARTIAL TAKE {sym}: selling {sell_qty} shares ({take.get('reason', '')})")

    # Get position details
    pos = alpaca("GET", f"positions/{sym}")
    if not pos:
        print(f"No position found for {sym}")
        continue

    entry_price = float(pos["avg_entry_price"])
    current_price = float(pos["current_price"])
    total_qty = int(pos["qty"])

    if sell_qty > total_qty:
        sell_qty = total_qty  # safety: don't sell more than we have

    # Clamp sell: never sell more than held (already checked above, but double-check)
    if sell_qty > total_qty:
        print(f"  CLAMPED: sell_qty {sell_qty} > total_qty {total_qty} — clamping")
        sell_qty = total_qty

    # Sell the partial qty with client_order_id
    client_id = f"tb-partial-{sym}-{uuid.uuid4().hex[:8]}"
    result = alpaca("POST", "orders", {
        "symbol": sym,
        "qty": str(sell_qty),
        "side": "sell",
        "type": "market",
        "time_in_force": "day",
        "client_order_id": client_id
    })

    if result and result.get("id"):
        # Wait for fill confirmation
        filled = wait_for_fill(result["id"], max_retries=30, delay=2)
        if filled and filled.get("status") == "filled":
            actual_exit = float(filled.get("filled_avg_price", current_price))
            actual_qty = int(filled.get("filled_qty", sell_qty))
            print(f"Partial sell {sym}: CONFIRMED FILL {actual_qty} shares @ ${actual_exit}")
            actions_taken.append(f"PARTIAL TAKE {sym} ({actual_qty}sh at +{take.get('unrealized_plpc', '?')})")
            realized_pnl = round((actual_exit - entry_price) * actual_qty, 2)
            closed_trades_new.append({
                "symbol": sym, "shares": actual_qty, "entry": entry_price,
                "exit": actual_exit, "realized_pnl": realized_pnl,
                "reason": f"partial profit take ({take.get('reason', '')})"
            })
        else:
            print(f"Partial sell {sym} not filled — status: {filled.get('status') if filled else 'unknown'}")
            continue  # skip stop replacement if sell didn't fill

        # Cancel existing stop and replace with tighter one for remaining shares
        remaining = total_qty - sell_qty
        if remaining > 0:
            # Find and cancel existing stop order for this symbol
            try:
                all_orders = json.load(open("/tmp/orders.json")) if os.path.exists("/tmp/orders.json") else []
                for o in all_orders:
                    if o.get("symbol") == sym and o.get("type") in ("trailing_stop", "stop") and o.get("status") in ("new", "accepted", "held"):
                        alpaca("DELETE", f"orders/{o['id']}")
                        print(f"Cancelled old stop {o['id']} for {sym}")
                        break
            except Exception as e:
                print(f"Warning: could not cancel old stop for {sym}: {e}")

            # Place new 5% trailing stop on remaining shares
            stop_order = alpaca("POST", "orders", {
                "symbol": sym,
                "qty": str(remaining),
                "side": "sell",
                "type": "trailing_stop",
                "trail_percent": "5",
                "time_in_force": "gtc"
            })
            if stop_order and stop_order.get("id"):
                print(f"New 5% trailing stop on remaining {remaining}sh of {sym}")
                actions_taken.append(f"TIGHTEN {sym} stop to 5% (remaining {remaining}sh)")
    else:
        print(f"Failed to submit partial sell for {sym}: {result}")

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

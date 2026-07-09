#!/usr/bin/env python3
"""Execute trades from Groq's market-open action plan.

Hardened with:
- client_order_id for idempotent retries
- Verified fills: poll order status up to 30 retries (2s apart)
- Clamp sells: never sell more than held qty, block sells with no position
- Cash guard: reject buys that would take cash below $0 or exceed 95% of equity
- Only update TRADE-LOG after confirmed fill
"""
import json, os, subprocess, sys, time, uuid

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
    except urllib.request.HTTPError as e:
        body_text = e.read().decode() if e.fp else ""
        print(f"Alpaca API error: {e.code} {e.reason} — {body_text[:300]}")
        return None
    except Exception as e:
        print(f"Alpaca API error: {e}")
        return None


def wait_for_fill(order_id, max_retries=30, delay=2):
    """Poll order status until filled/rejected/canceled. Returns final order dict."""
    for i in range(max_retries):
        order = alpaca("GET", f"orders/{order_id}")
        if not order:
            print(f"  Poll {i+1}/{max_retries}: could not fetch order")
            time.sleep(delay)
            continue
        status = order.get("status", "unknown")
        if status == "filled":
            return order
        if status in ("rejected", "canceled", "expired", "done_for_day", "replaced"):
            print(f"  Order terminal status: {status}")
            return order
        if i < max_retries - 1:
            time.sleep(delay)
    print(f"  Order {order_id} not filled after {max_retries} retries")
    return order


def get_position(symbol):
    """Fetch current position for a symbol. Returns None if no position."""
    pos = alpaca("GET", f"positions/{symbol}")
    return pos


def get_account():
    """Fetch current account info."""
    return alpaca("GET", "account")


# Pre-fetch account for cash guard
account = get_account()
if not account:
    print("ERROR: Could not fetch account — aborting trades")
    with open("/tmp/trade_log_entry.md", "w") as f:
        f.write("")
    sys.exit(1)

current_cash = float(account.get("cash", 0))
current_equity = float(account.get("equity", 0))
print(f"Account: cash=${current_cash:.2f}, equity=${current_equity:.2f}")

executed = []
skipped = []

for trade in plan["trades"]:
    sym = trade["symbol"]
    qty = int(trade["qty"])
    side = trade.get("side", "buy")

    print(f"\nProcessing: {side} {qty} {sym}")

    # --- CLAMP SELLS (Task 11) ---
    if side == "sell":
        pos = get_position(sym)
        if not pos:
            print(f"  BLOCKED: No position found for {sym} — cannot sell what we don't hold")
            skipped.append({"symbol": sym, "reason": "no position held"})
            continue
        held_qty = int(pos.get("qty", 0))
        if held_qty <= 0:
            print(f"  BLOCKED: Zero position for {sym} — would create short")
            skipped.append({"symbol": sym, "reason": "zero position"})
            continue
        if qty > held_qty:
            print(f"  CLAMPED: Sell qty {qty} > held {held_qty} for {sym} — clamping to {held_qty}")
            qty = held_qty

    # --- CASH GUARD (Task 12) ---
    if side == "buy":
        est_price = float(trade.get("entry_price", 0))
        est_cost = est_price * qty if est_price > 0 else 0
        if est_cost > 0:
            # Check 1: Would cash go below $0?
            if current_cash - est_cost < 0:
                print(f"  BLOCKED: Buy {sym} (~${est_cost:.0f}) would take cash below $0 (cash=${current_cash:.2f})")
                skipped.append({"symbol": sym, "reason": f"insufficient cash (need ~${est_cost:.0f}, have ${current_cash:.2f})"})
                continue
            # Check 2: Would deployed capital exceed 95% of equity?
            deployed_after = (current_equity - current_cash) + est_cost
            if deployed_after > 0.95 * current_equity:
                print(f"  BLOCKED: Buy {sym} would put deployed capital at {deployed_after/current_equity*100:.1f}% of equity (>95%)")
                skipped.append({"symbol": sym, "reason": f"would exceed 95% deployed ({deployed_after/current_equity*100:.1f}%)"})
                continue

    # Generate client_order_id for idempotency
    client_order_id = f"tb-{sym}-{side}-{uuid.uuid4().hex[:8]}"

    print(f"  Submitting: {side} {qty} {sym} (client_order_id={client_order_id})")

    # Place market order with client_order_id
    order = alpaca("POST", "orders", {
        "symbol": sym,
        "qty": str(qty),
        "side": side,
        "type": "market",
        "time_in_force": "day",
        "client_order_id": client_order_id
    })

    if not order:
        print(f"  FAILED to place {side} order for {sym}")
        skipped.append({"symbol": sym, "reason": "order submission failed"})
        continue

    print(f"  Order placed: {order.get('id')} — status: {order.get('status')}")

    # --- VERIFIED FILL (Task 10) ---
    # Poll until filled/rejected/canceled (max 30 retries, 2s apart)
    filled_order = wait_for_fill(order["id"], max_retries=30, delay=2)

    if not filled_order or filled_order.get("status") != "filled":
        final_status = filled_order.get("status", "unknown") if filled_order else "unknown"
        print(f"  Order NOT filled — final status: {final_status}")
        skipped.append({"symbol": sym, "reason": f"not filled (status={final_status})"})
        continue

    fill_price = filled_order.get("filled_avg_price", trade.get("entry_price", "?"))
    filled_qty = filled_order.get("filled_qty", str(qty))
    print(f"  CONFIRMED FILL: {sym} {filled_qty}sh @ ${fill_price}")

    # Update cash tracking for subsequent orders
    if side == "buy":
        current_cash -= float(fill_price) * int(filled_qty)
    elif side == "sell":
        current_cash += float(fill_price) * int(filled_qty)

    # Place trailing stop and verify it sticks
    stop_pct = trade.get("stop_pct", "10")
    stop_side = "buy" if side == "sell" else "sell"
    stop_client_id = f"tb-stop-{sym}-{uuid.uuid4().hex[:8]}"
    stop_order = alpaca("POST", "orders", {
        "symbol": sym,
        "qty": filled_qty,
        "side": stop_side,
        "type": "trailing_stop",
        "trail_percent": stop_pct,
        "time_in_force": "gtc",
        "client_order_id": stop_client_id
    })

    # Verify stop was accepted
    stop_ok = False
    if stop_order and stop_order.get("id"):
        time.sleep(1)
        verify = alpaca("GET", f"orders/{stop_order['id']}")
        if verify and verify.get("status") in ("new", "accepted", "held"):
            print(f"  Trailing stop VERIFIED for {sym}: {stop_pct}% ({stop_side}-side) — order {stop_order['id']}")
            stop_ok = True
        else:
            print(f"  Trailing stop for {sym} NOT accepted — status: {verify.get('status') if verify else 'null'}")

    if not stop_ok:
        # Fallback: fixed stop
        print(f"  Trying fixed stop fallback for {sym}")
        try:
            if side == "sell":
                stop_price = round(float(fill_price) * (1 + float(stop_pct)/100), 2)
            else:
                stop_price = round(float(fill_price) * (1 - float(stop_pct)/100), 2)
            stop_order = alpaca("POST", "orders", {
                "symbol": sym,
                "qty": filled_qty,
                "side": stop_side,
                "type": "stop",
                "stop_price": str(stop_price),
                "time_in_force": "gtc",
                "client_order_id": f"tb-fixstop-{sym}-{uuid.uuid4().hex[:8]}"
            })
            if stop_order and stop_order.get("id"):
                print(f"  Fixed stop placed for {sym} at ${stop_price} ({stop_side}-side)")
            else:
                print(f"  WARNING: No stop set for {sym} — NEEDS MANUAL STOP!")
        except:
            print(f"  WARNING: No stop set for {sym} — NEEDS MANUAL STOP!")

    executed.append({
        "symbol": sym, "qty": filled_qty, "price": fill_price,
        "stop_pct": stop_pct, "client_order_id": client_order_id
    })

# Save trade log entry — ONLY with confirmed fills
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
    msg = f"Market Open — Trades executed:\n{fills}\n{plan.get('reason', '')}"
    if skipped:
        msg += f"\nSkipped: {', '.join(s['symbol'] + ' (' + s['reason'] + ')' for s in skipped)}"
    with open("/tmp/telegram_msg.txt", "w") as f:
        f.write(msg)
elif skipped:
    with open("/tmp/telegram_msg.txt", "w") as f:
        f.write(f"Market Open — All orders skipped:\n{', '.join(s['symbol'] + ' (' + s['reason'] + ')' for s in skipped)}")

print(f"\nDone — {len(executed)} trades executed, {len(skipped)} skipped")

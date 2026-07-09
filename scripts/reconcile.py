#!/usr/bin/env python3
"""
Reconciliation: compare broker positions with TRADE-LOG.md SUMMARY.

Run at the START of every trading cycle. If mismatch detected:
1. Send Telegram alert with the diff
2. Overwrite TRADE-LOG.md SUMMARY with broker positions
3. Write /tmp/reconcile_skip flag to skip new orders this cycle
"""
import json, os, re, sys, urllib.request
from datetime import datetime, timezone

API_KEY = os.environ.get("ALPACA_API_KEY", "")
API_SECRET = os.environ.get("ALPACA_SECRET_KEY", "")
BASE = "https://paper-api.alpaca.markets/v2"
TRADE_LOG = "memory/TRADE-LOG.md"


def alpaca_get(path):
    """GET request to Alpaca API."""
    url = f"{BASE}/{path}"
    req = urllib.request.Request(url, method="GET")
    req.add_header("APCA-API-KEY-ID", API_KEY)
    req.add_header("APCA-API-SECRET-KEY", API_SECRET)
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            return json.loads(resp.read())
    except Exception as e:
        print(f"Alpaca API error ({path}): {e}")
        return None


def send_telegram(msg):
    """Send Telegram alert."""
    bot_token = os.environ.get("TELEGRAM_BOT_TOKEN", "")
    chat_id = os.environ.get("TELEGRAM_CHAT_ID", "")
    if not bot_token or not chat_id:
        print(f"[telegram] No credentials — skipping alert")
        return
    data = json.dumps({"chat_id": chat_id, "text": msg}).encode()
    req = urllib.request.Request(
        f"https://api.telegram.org/bot{bot_token}/sendMessage",
        data=data,
        headers={"Content-Type": "application/json"},
    )
    try:
        urllib.request.urlopen(req, timeout=10)
        print("Telegram reconciliation alert sent")
    except Exception as e:
        print(f"Telegram send failed: {e}")


def parse_summary_positions():
    """Read open_positions from TRADE-LOG.md SUMMARY block."""
    if not os.path.exists(TRADE_LOG):
        return []
    with open(TRADE_LOG) as f:
        content = f.read()
    m = re.search(r'open_positions:\s*(\[.*?\])', content)
    if not m:
        return []
    try:
        return json.loads(m.group(1))
    except json.JSONDecodeError:
        return []


def main():
    print("=== RECONCILIATION CHECK ===")

    # 1. Fetch broker positions — MUST fail closed: if broker is unreachable,
    # skip the entire trading cycle (never trade blind)
    broker_positions = alpaca_get("positions")
    if broker_positions is None:
        print("ERROR: Broker unreachable — BLOCKING trading cycle (fail closed)")
        with open("/tmp/reconcile_skip", "w") as f:
            f.write("broker_unreachable")
        send_telegram(
            "🚨 RECONCILIATION BLOCKED\n\n"
            "Cannot reach Alpaca broker — trading cycle SKIPPED.\n"
            "No orders will be placed until broker connectivity is restored."
        )
        sys.exit(1)

    # Also fetch account for summary update
    account = alpaca_get("account")
    if account is None:
        print("ERROR: Broker account unreachable — BLOCKING trading cycle")
        with open("/tmp/reconcile_skip", "w") as f:
            f.write("broker_unreachable")
        send_telegram(
            "🚨 RECONCILIATION BLOCKED\n\n"
            "Cannot fetch Alpaca account — trading cycle SKIPPED."
        )
        sys.exit(1)

    # Save to /tmp for downstream scripts
    with open("/tmp/positions.json", "w") as f:
        json.dump(broker_positions, f)
    with open("/tmp/account.json", "w") as f:
        json.dump(account, f)

    # 2. Read internal state from TRADE-LOG.md
    internal_positions = parse_summary_positions()

    # 3. Compare
    broker_map = {}
    for p in broker_positions:
        sym = p["symbol"]
        broker_map[sym] = {
            "symbol": sym,
            "shares": int(p["qty"]),
            "side": "BUY" if p["side"] == "long" else "SELL",
            "entry": float(p["avg_entry_price"]),
            "unrealized_pnl": round(float(p.get("unrealized_pl", 0)), 2),
        }

    internal_map = {}
    for p in internal_positions:
        sym = p["symbol"]
        internal_map[sym] = {
            "symbol": sym,
            "shares": int(p.get("shares", 0)),
            "side": p.get("side", "BUY"),
            "entry": float(p.get("entry", 0)),
        }

    # Find mismatches
    mismatches = []
    all_syms = set(list(broker_map.keys()) + list(internal_map.keys()))

    for sym in sorted(all_syms):
        broker_pos = broker_map.get(sym)
        internal_pos = internal_map.get(sym)

        if broker_pos and not internal_pos:
            mismatches.append(f"  MISSING IN LOG: {sym} ({broker_pos['shares']}sh @ ${broker_pos['entry']}) — exists at broker only")
        elif internal_pos and not broker_pos:
            mismatches.append(f"  GHOST IN LOG: {sym} ({internal_pos['shares']}sh @ ${internal_pos['entry']}) — exists in log but NOT at broker")
        elif broker_pos and internal_pos:
            if broker_pos["shares"] != internal_pos["shares"]:
                mismatches.append(f"  QTY MISMATCH: {sym} — broker={broker_pos['shares']}sh, log={internal_pos['shares']}sh")
            if broker_pos["side"] != internal_pos["side"]:
                mismatches.append(f"  SIDE MISMATCH: {sym} — broker={broker_pos['side']}, log={internal_pos['side']}")

    if not mismatches:
        print("Reconciliation OK — broker and TRADE-LOG.md match")
        # Clean up any previous skip flag
        if os.path.exists("/tmp/reconcile_skip"):
            os.remove("/tmp/reconcile_skip")
        sys.exit(0)

    # 4. Mismatch detected
    print(f"RECONCILIATION MISMATCH — {len(mismatches)} issues found:")
    for m in mismatches:
        print(m)

    # 4a. Send Telegram alert
    alert = f"RECONCILIATION ALERT\n\nBroker vs TRADE-LOG.md mismatch detected:\n"
    alert += "\n".join(mismatches)
    alert += f"\n\nBroker positions: {len(broker_positions)}"
    alert += f"\nLog positions: {len(internal_positions)}"
    alert += "\n\nOverwriting log with broker reality. Skipping new orders this cycle."
    send_telegram(alert)

    # 4b. Overwrite TRADE-LOG.md SUMMARY with broker positions
    # Build new open_positions from broker
    open_pos = []
    for p in broker_positions:
        open_pos.append({
            "symbol": p["symbol"],
            "shares": int(p["qty"]),
            "entry": float(p["avg_entry_price"]),
            "side": "BUY" if p["side"] == "long" else "SELL",
            "unrealized_pnl": round(float(p.get("unrealized_pl", 0)), 2),
        })

    equity = float(account["equity"])
    cash = float(account["cash"])
    total_pnl = equity - 100000.0
    now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    # Preserve closed_trades
    with open(TRADE_LOG) as f:
        content = f.read()
    closed_trades = []
    cm = re.search(r'closed_trades:\s*(\[.*?\])', content)
    if cm:
        try:
            closed_trades = json.loads(cm.group(1))
        except json.JSONDecodeError:
            pass

    summary = f"""<!-- SUMMARY
portfolio_value: {equity:.2f}
cash: {cash:.2f}
total_pnl: {total_pnl:.2f}
open_positions: {json.dumps(open_pos)}
closed_trades: {json.dumps(closed_trades)}
last_updated: {now}
-->"""

    if content.startswith("<!-- SUMMARY"):
        content = re.sub(r'<!-- SUMMARY.*?-->', summary, content, count=1, flags=re.DOTALL)
    else:
        content = summary + "\n\n" + content

    with open(TRADE_LOG, "w") as f:
        f.write(content)

    print("TRADE-LOG.md SUMMARY overwritten with broker positions")

    # 4c. Set skip flag
    with open("/tmp/reconcile_skip", "w") as f:
        f.write("mismatch_detected")

    print("Skip flag set — new orders will be blocked this cycle")


if __name__ == "__main__":
    main()

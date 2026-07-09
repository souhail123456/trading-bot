#!/usr/bin/env python3
"""
Broker-Sourced P&L: compute realized P&L from Alpaca fill history.

Fetches GET /v2/account/activities?activity_types=FILL to get actual fills,
then reconstructs closed trades and updates TRADE-LOG.md SUMMARY's
closed_trades section with broker reality.

Run this during EOD or as needed for reconciliation.
"""
import json, os, re, sys, urllib.request
from datetime import datetime, timezone
from collections import defaultdict

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
        with urllib.request.urlopen(req, timeout=30) as resp:
            return json.loads(resp.read())
    except Exception as e:
        print(f"Alpaca API error ({path}): {e}")
        return None


def fetch_all_fills():
    """Fetch all FILL activities, paginating if needed."""
    all_fills = []
    page_token = None

    for _ in range(20):  # max 20 pages safety
        path = "account/activities?activity_types=FILL&direction=asc&page_size=100"
        if page_token:
            path += f"&page_token={page_token}"

        data = alpaca_get(path)
        if not data or not isinstance(data, list):
            break

        all_fills.extend(data)

        if len(data) < 100:
            break  # last page

        # Use the last activity ID as page token
        page_token = data[-1].get("id")
        if not page_token:
            break

    return all_fills


def compute_realized_pnl(fills):
    """
    Compute realized P&L from fill history using FIFO cost basis.

    Returns a list of closed trade dicts for TRADE-LOG.md SUMMARY.
    """
    # Group fills by symbol
    fills_by_sym = defaultdict(list)
    for f in fills:
        fills_by_sym[f["symbol"]].append(f)

    closed_trades = []

    for sym, sym_fills in fills_by_sym.items():
        # Sort by timestamp
        sym_fills.sort(key=lambda x: x.get("transaction_time", x.get("timestamp", "")))

        # FIFO queue of open lots: [(qty, price, date), ...]
        open_lots = []

        for fill in sym_fills:
            side = fill.get("side", "")
            qty = int(float(fill.get("qty", 0)))
            price = float(fill.get("price", 0))
            date = fill.get("transaction_time", fill.get("timestamp", ""))[:10]
            order_id = fill.get("order_id", "")

            if qty <= 0 or price <= 0:
                continue

            if side == "buy":
                # Add to open lots
                open_lots.append({"qty": qty, "price": price, "date": date})
            elif side == "sell":
                # Match against open lots (FIFO)
                remaining_sell = qty
                total_cost_basis = 0.0
                total_matched = 0

                while remaining_sell > 0 and open_lots:
                    lot = open_lots[0]
                    match_qty = min(remaining_sell, lot["qty"])
                    total_cost_basis += match_qty * lot["price"]
                    total_matched += match_qty
                    remaining_sell -= match_qty
                    lot["qty"] -= match_qty
                    if lot["qty"] <= 0:
                        open_lots.pop(0)

                if total_matched > 0:
                    avg_entry = total_cost_basis / total_matched
                    realized = round((price - avg_entry) * total_matched, 2)
                    closed_trades.append({
                        "symbol": sym,
                        "shares": total_matched,
                        "entry": round(avg_entry, 4),
                        "exit": price,
                        "realized_pnl": realized,
                        "reason": "broker_fill",
                        "date": date,
                    })

                if remaining_sell > 0:
                    # Short sell — track as negative lot
                    open_lots.append({"qty": -remaining_sell, "price": price, "date": date})

    return closed_trades


def update_trade_log(closed_trades):
    """Update the closed_trades section in TRADE-LOG.md SUMMARY."""
    if not os.path.exists(TRADE_LOG):
        print("TRADE-LOG.md not found")
        return

    with open(TRADE_LOG) as f:
        content = f.read()

    # Replace closed_trades in SUMMARY
    new_ct_json = json.dumps(closed_trades)
    if re.search(r'closed_trades:\s*\[.*?\]', content):
        content = re.sub(
            r'closed_trades:\s*\[.*?\]',
            f'closed_trades: {new_ct_json}',
            content,
            count=1,
        )
    else:
        print("WARNING: closed_trades not found in SUMMARY — not updating")
        return

    # Update last_updated
    now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    content = re.sub(r'last_updated:.*', f'last_updated: {now}', content, count=1)

    with open(TRADE_LOG, "w") as f:
        f.write(content)


def main():
    print("=== BROKER-SOURCED P&L ===")

    if not API_KEY or not API_SECRET:
        print("ERROR: ALPACA_API_KEY/ALPACA_SECRET_KEY not set")
        sys.exit(1)

    # Fetch all fill activities
    fills = fetch_all_fills()
    if not fills:
        print("No fill activities found")
        sys.exit(0)

    print(f"Fetched {len(fills)} fill activities")

    # Compute realized P&L from fills
    closed_trades = compute_realized_pnl(fills)
    print(f"Computed {len(closed_trades)} closed trades from broker fills")

    # Show summary
    total_pnl = sum(t.get("realized_pnl", 0) for t in closed_trades)
    print(f"Total realized P&L (broker-sourced): ${total_pnl:.2f}")

    for ct in closed_trades:
        pnl_str = f"+${ct['realized_pnl']}" if ct['realized_pnl'] >= 0 else f"-${abs(ct['realized_pnl'])}"
        print(f"  {ct['symbol']}: {ct['shares']}sh, entry=${ct['entry']}, exit=${ct['exit']}, P&L={pnl_str} ({ct['date']})")

    # Save to /tmp for other scripts
    with open("/tmp/broker_closed_trades.json", "w") as f:
        json.dump(closed_trades, f, indent=2)

    # Update TRADE-LOG.md
    update_trade_log(closed_trades)
    print("TRADE-LOG.md closed_trades updated with broker-sourced P&L")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Snapshot portfolio state to memory/PORTFOLIO-HISTORY.csv for stats tracking.
Appends one row per run: date, equity, cash, positions, unrealized P&L, phase P&L."""
import json, os, csv
from datetime import datetime

account = json.load(open("/tmp/account.json"))
positions = json.load(open("/tmp/positions.json"))

date = datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")
equity = float(account["equity"])
cash = float(account["cash"])
phase_start = 100000.0
phase_pnl = equity - phase_start
phase_pct = (phase_pnl / phase_start) * 100

# Build positions summary
pos_summary = []
for p in positions:
    sym = p["symbol"]
    qty = p["qty"]
    entry = p["avg_entry_price"]
    current = p["current_price"]
    pnl = p["unrealized_pl"]
    pnl_pct = float(p["unrealized_plpc"]) * 100
    pos_summary.append(f"{sym}:{qty}@{entry}>{current}({pnl_pct:+.1f}%)")

positions_str = "; ".join(pos_summary) if pos_summary else "CASH"

# Count open/closed from orders
orders = json.load(open("/tmp/orders.json")) if os.path.exists("/tmp/orders.json") else []
open_orders = len(orders)

csv_path = "memory/PORTFOLIO-HISTORY.csv"
file_exists = os.path.exists(csv_path)

with open(csv_path, "a", newline="") as f:
    writer = csv.writer(f)
    if not file_exists:
        writer.writerow(["timestamp", "equity", "cash", "deployed_pct", "positions", "unrealized_pnl", "phase_pnl", "phase_pct", "open_orders"])
    deployed_pct = ((equity - cash) / equity * 100) if equity > 0 else 0
    unrealized = sum(float(p["unrealized_pl"]) for p in positions)
    writer.writerow([
        date,
        f"{equity:.2f}",
        f"{cash:.2f}",
        f"{deployed_pct:.1f}",
        positions_str,
        f"{unrealized:.2f}",
        f"{phase_pnl:.2f}",
        f"{phase_pct:.2f}",
        open_orders
    ])

print(f"Snapshot: ${equity:.2f} | Cash: ${cash:.2f} ({deployed_pct:.1f}% deployed) | Phase: {phase_pct:+.2f}% | Positions: {positions_str}")

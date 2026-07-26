#!/usr/bin/env python3
"""
Strategy 18 — Asset Class Trend-Following
==========================================
Mechanical, systematic strategy. NO LLM involved.

Universe: SPY (US stocks), EFA (foreign stocks), TLT (bonds), VNQ (REITs),
          DBC (commodities) — one ETF per major asset class.

Rules (backtested "10-month SMA" / Meb Faber style trend-following):
  Entry:  close > 200-day SMA  -> hold the ETF (long)
  Exit:   close < 200-day SMA  -> go to cash on that ETF
  Rebalance: monthly, equal weight (20% of allocated capital per ETF)
  Sizing: 1/5 of allocated capital per ETF (allocated = allocation% of
          total account equity)

This script is self-contained: it downloads its own data via yfinance,
compares against live Alpaca positions, computes buy/sell orders, and
(unless --dry-run) executes them directly against the Alpaca paper API.

Usage:
  python3 scripts/asset_class_tf.py --dry-run
  python3 scripts/asset_class_tf.py --allocation 0.6
"""
import argparse
import json
import os
import sys
import time
import urllib.error
import urllib.request
from datetime import datetime, timezone

UNIVERSE = ["SPY", "EFA", "TLT", "VNQ", "DBC"]
SMA_PERIOD = 200          # ~10 trading months
LOOKBACK_DAYS = 250        # enough daily bars to compute the 200d SMA
SLIPPAGE_BPS = 5            # ~5bps transaction cost buffer (informational)
POSITION_WEIGHT = 1.0 / len(UNIVERSE)  # 20% of allocated capital per ETF

ALPACA_BASE = "https://paper-api.alpaca.markets/v2"

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
STATE_FILE = os.path.join(SCRIPT_DIR, "..", "memory", "asset_class_tf_state.json")
LOG_FILE = os.path.join(SCRIPT_DIR, "..", "memory", "ASSET-CLASS-TF-LOG.md")


# ---------------------------------------------------------------------------
# HTTP helpers (stdlib only for Alpaca + Telegram; yfinance for market data)
# ---------------------------------------------------------------------------

def alpaca_request(method, path, api_key, api_secret, data=None):
    url = f"{ALPACA_BASE}/{path}"
    body = json.dumps(data).encode() if data else None
    req = urllib.request.Request(url, data=body, method=method)
    req.add_header("APCA-API-KEY-ID", api_key)
    req.add_header("APCA-API-SECRET-KEY", api_secret)
    if data:
        req.add_header("Content-Type", "application/json")
    try:
        resp = urllib.request.urlopen(req, timeout=20)
        raw = resp.read()
        return json.loads(raw) if raw else {}
    except urllib.error.HTTPError as e:
        body_text = e.read().decode() if e.fp else ""
        print(f"  Alpaca API error: {e.code} {e.reason} — {body_text[:300]}")
        return None
    except Exception as e:
        print(f"  Alpaca API error: {e}")
        return None


def send_telegram(msg, bot_token, chat_id):
    if not bot_token or not chat_id:
        print("[telegram] No credentials — skipping")
        return
    data = json.dumps({"chat_id": chat_id, "text": msg}).encode()
    req = urllib.request.Request(
        f"https://api.telegram.org/bot{bot_token}/sendMessage",
        data=data,
        headers={"Content-Type": "application/json"},
    )
    try:
        urllib.request.urlopen(req, timeout=10)
        print("[telegram] Summary sent")
    except Exception as e:
        print(f"[telegram] Send failed: {e}")


# ---------------------------------------------------------------------------
# Ownership ledger — prevents cross-strategy position conflicts
# ---------------------------------------------------------------------------

def load_state():
    if os.path.exists(STATE_FILE):
        try:
            with open(STATE_FILE) as f:
                return json.load(f)
        except Exception as e:
            print(f"Warning: could not read state file: {e}", file=sys.stderr)
    return {"positions": {}, "last_rebalance": None}


def save_state(state):
    state["last_rebalance"] = datetime.now(timezone.utc).isoformat()
    os.makedirs(os.path.dirname(STATE_FILE), exist_ok=True)
    with open(STATE_FILE, "w") as f:
        json.dump(state, f, indent=2)


def append_log(text):
    os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)
    header_needed = not os.path.exists(LOG_FILE)
    with open(LOG_FILE, "a") as f:
        if header_needed:
            f.write("# Asset Class Trend-Following Log — Strategy 18\n\n")
        f.write(text.rstrip() + "\n\n---\n\n")


# ---------------------------------------------------------------------------
# Market hours check
# ---------------------------------------------------------------------------

def market_is_open(api_key, api_secret):
    """Query Alpaca's clock endpoint. Returns True/False, or None if unreachable."""
    clock = alpaca_request("GET", "clock", api_key, api_secret)
    if clock is None:
        return None
    return bool(clock.get("is_open"))


# ---------------------------------------------------------------------------
# Market data via yfinance
# ---------------------------------------------------------------------------

def fetch_sma_status(symbols, period=SMA_PERIOD, lookback_days=LOOKBACK_DAYS):
    """Download daily closes for each symbol and compute close vs SMA-200.

    Returns dict: symbol -> {"close": float, "sma": float, "above": bool}
    Symbols that fail to download or have insufficient data are omitted.
    """
    import yfinance as yf

    print(f"Downloading {lookback_days}d of daily data for {symbols} via yfinance...")
    data = yf.download(
        symbols,
        period=f"{lookback_days}d",
        interval="1d",
        auto_adjust=True,
        progress=False,
        group_by="ticker",
    )

    results = {}
    for sym in symbols:
        try:
            if len(symbols) == 1:
                closes = data["Close"].dropna()
            else:
                closes = data[sym]["Close"].dropna()
        except Exception as e:
            print(f"  {sym}: could not extract closes ({e}) — SKIPPING")
            continue

        if len(closes) < period:
            print(f"  {sym}: only {len(closes)} bars available, need {period} — SKIPPING")
            continue

        last_close = float(closes.iloc[-1])
        sma_val = float(closes.tail(period).mean())
        above = last_close > sma_val
        results[sym] = {"close": last_close, "sma": sma_val, "above": above}
        state = "ABOVE" if above else "BELOW"
        pct = (last_close / sma_val - 1) * 100
        print(f"  {sym}: close=${last_close:.2f}  SMA200=${sma_val:.2f}  [{state} SMA, {pct:+.1f}%]")

    return results


# ---------------------------------------------------------------------------
# Order placement
# ---------------------------------------------------------------------------

def wait_for_fill(order_id, api_key, api_secret, max_retries=30, delay=2):
    for i in range(max_retries):
        order = alpaca_request("GET", f"orders/{order_id}", api_key, api_secret)
        if not order:
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
    return None


def place_market_order(symbol, side, notional=None, qty=None, api_key=None, api_secret=None):
    """Place a market order by notional (buys) or qty (sells)."""
    import uuid
    client_order_id = f"actf-{symbol}-{side}-{uuid.uuid4().hex[:8]}"
    order_data = {
        "symbol": symbol,
        "side": side,
        "type": "market",
        "time_in_force": "day",
        "client_order_id": client_order_id,
    }
    if notional is not None:
        order_data["notional"] = f"{notional:.2f}"
    elif qty is not None:
        order_data["qty"] = str(qty)
    else:
        raise ValueError("place_market_order requires notional or qty")

    print(f"  Submitting: {side} {symbol} ({'notional $' + str(round(notional, 2)) if notional else 'qty ' + str(qty)}) [client_order_id={client_order_id}]")
    order = alpaca_request("POST", "orders", api_key, api_secret, order_data)
    if not order:
        print(f"  FAILED to place {side} order for {symbol}")
        return None

    print(f"  Order placed: {order.get('id')} — status: {order.get('status')}")
    filled = wait_for_fill(order["id"], api_key, api_secret)
    if not filled or filled.get("status") != "filled":
        status = filled.get("status", "unknown") if filled else "unknown"
        print(f"  Order NOT filled — final status: {status}")
        return None

    fill_price = filled.get("filled_avg_price")
    filled_qty = filled.get("filled_qty")
    print(f"  CONFIRMED FILL: {symbol} {filled_qty}sh @ ${fill_price}")
    return filled


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description="Strategy 18 — Asset Class Trend-Following")
    parser.add_argument("--dry-run", action="store_true", help="Show planned actions without executing")
    parser.add_argument("--allocation", type=float, default=0.6, help="Fraction of total account equity allocated to this strategy (default 0.6)")
    args = parser.parse_args()

    print("=" * 70)
    print("STRATEGY 18 — ASSET CLASS TREND-FOLLOWING")
    print(f"Run time (UTC): {datetime.now(timezone.utc).isoformat()}")
    print(f"Universe: {UNIVERSE}")
    print(f"Allocation: {args.allocation * 100:.0f}% of account equity")
    print(f"Dry run: {args.dry_run}")
    print("=" * 70)

    api_key = os.environ.get("ALPACA_API_KEY", "")
    api_secret = os.environ.get("ALPACA_SECRET_KEY", "")
    tg_token = os.environ.get("TELEGRAM_BOT_TOKEN", "")
    tg_chat = os.environ.get("TELEGRAM_CHAT_ID", "")

    if not api_key or not api_secret:
        print("ERROR: ALPACA_API_KEY / ALPACA_SECRET_KEY not set — aborting")
        sys.exit(1)

    # --- Market hours check ---
    is_open = market_is_open(api_key, api_secret)
    if is_open is None:
        print("WARNING: Could not determine market status — proceeding cautiously (will still check per-order)")
    elif not is_open:
        msg = "Asset Class TF — market is closed, skipping this run."
        print(msg)
        send_telegram(f"📊 {msg}", tg_token, tg_chat)
        sys.exit(0)
    else:
        print("Market is OPEN — proceeding")

    # --- Account & positions ---
    account = alpaca_request("GET", "account", api_key, api_secret)
    if not account:
        print("ERROR: Could not fetch Alpaca account — aborting")
        sys.exit(1)

    positions = alpaca_request("GET", "positions", api_key, api_secret)
    if positions is None:
        print("ERROR: Could not fetch Alpaca positions — aborting")
        sys.exit(1)

    equity = float(account.get("equity", 0))
    cash = float(account.get("cash", 0))
    print(f"\nAccount: equity=${equity:.2f}  cash=${cash:.2f}")

    alpaca_held = {p["symbol"]: p for p in positions if p["symbol"] in UNIVERSE}
    print(f"Alpaca positions (in universe): {sorted(alpaca_held.keys()) or 'none'}")

    state = load_state()
    tracked = state.get("positions", {})
    print(f"Tracked by this strategy (ownership ledger): {sorted(tracked.keys()) or 'none'}")

    allocated_capital = equity * args.allocation
    per_etf_capital = allocated_capital * POSITION_WEIGHT
    print(f"Allocated capital: ${allocated_capital:.2f} ({args.allocation*100:.0f}% of equity)")
    print(f"Per-ETF target size: ${per_etf_capital:.2f} (1/{len(UNIVERSE)} equal weight)")

    # --- Compute SMA status ---
    print("\n--- SMA-200 STATUS ---")
    sma_status = fetch_sma_status(UNIVERSE)

    if not sma_status:
        print("ERROR: No SMA data available for any symbol — aborting")
        sys.exit(1)

    # --- Determine actions (using ownership ledger, not raw Alpaca positions) ---
    print("\n--- DECISION ---")
    actions = []  # list of dicts: {symbol, action, reason}
    skipped_external = []
    for sym in UNIVERSE:
        status = sma_status.get(sym)
        owned_by_us = sym in tracked
        if status is None:
            print(f"  {sym}: no data — SKIP (holding current state)")
            continue

        above = status["above"]
        if above and not owned_by_us:
            if sym in alpaca_held:
                print(f"  {sym}: SKIP BUY — above SMA but held externally (not opened by this strategy)")
                skipped_external.append(sym)
            else:
                actions.append({"symbol": sym, "action": "BUY", "reason": f"close ${status['close']:.2f} > SMA200 ${status['sma']:.2f}, not held"})
                print(f"  {sym}: BUY — above SMA, not held by this strategy")
        elif not above and owned_by_us:
            actions.append({"symbol": sym, "action": "SELL", "reason": f"close ${status['close']:.2f} < SMA200 ${status['sma']:.2f}, held — exit to cash"})
            print(f"  {sym}: SELL — below SMA, held by this strategy")
        elif above and owned_by_us:
            print(f"  {sym}: HOLD — above SMA, already held by this strategy")
        elif not above and not owned_by_us:
            print(f"  {sym}: HOLD (cash) — below SMA, not held")
        else:
            print(f"  {sym}: no action")

    if not actions:
        msg = "Asset Class TF — no rebalance needed. All positions aligned with trend."
        print(f"\n{msg}")
        send_telegram(f"📊 {msg}", tg_token, tg_chat)
        sys.exit(0)

    print(f"\n{len(actions)} action(s) to take: {[(a['symbol'], a['action']) for a in actions]}")

    # --- Execute (sells first to free up cash, then buys) ---
    sells = [a for a in actions if a["action"] == "SELL"]
    buys = [a for a in actions if a["action"] == "BUY"]

    executed = []
    skipped = []

    for a in sells:
        sym = a["symbol"]
        tracked_qty = int(tracked.get(sym, {}).get("qty", 0))
        broker_pos = alpaca_held.get(sym)
        broker_qty = int(float(broker_pos.get("qty", 0))) if broker_pos else 0
        sell_qty = min(tracked_qty, broker_qty) if broker_qty > 0 else 0

        if sell_qty <= 0:
            print(f"SELL {sym}: nothing to sell (tracked={tracked_qty}, broker={broker_qty}) — clearing from ledger")
            if not args.dry_run:
                state.get("positions", {}).pop(sym, None)
            skipped.append({**a, "detail": "no position at broker to sell"})
            continue

        if args.dry_run:
            print(f"[DRY RUN] Would SELL {sell_qty}sh {sym} (tracked={tracked_qty}, broker={broker_qty}) — {a['reason']}")
            executed.append({**a, "qty": sell_qty, "dry_run": True})
            continue

        print(f"\nSELL {sym}: closing {sell_qty}sh (tracked={tracked_qty}, broker={broker_qty}) — {a['reason']}")
        filled = place_market_order(sym, "sell", qty=sell_qty, api_key=api_key, api_secret=api_secret)
        if filled:
            executed.append({
                **a,
                "qty": filled.get("filled_qty"),
                "price": filled.get("filled_avg_price"),
            })
            state.get("positions", {}).pop(sym, None)
        else:
            skipped.append({**a, "detail": "sell order failed or not filled"})

    for a in buys:
        sym = a["symbol"]
        notional = per_etf_capital

        # Cash guard: don't buy if it would take cash below $0 or exceed 95% deployed
        if notional > cash:
            print(f"BUY {sym}: insufficient cash (need ${notional:.2f}, have ${cash:.2f}) — skipping")
            skipped.append({**a, "detail": f"insufficient cash (need ${notional:.2f}, have ${cash:.2f})"})
            continue

        deployed_after = (equity - cash) + notional
        if deployed_after > 0.95 * equity:
            print(f"BUY {sym}: would exceed 95% deployed ({deployed_after/equity*100:.1f}%) — skipping")
            skipped.append({**a, "detail": f"would exceed 95% deployed ({deployed_after/equity*100:.1f}%)"})
            continue

        if args.dry_run:
            print(f"[DRY RUN] Would BUY ~${notional:.2f} of {sym} — {a['reason']}")
            executed.append({**a, "notional": notional, "dry_run": True})
            continue

        print(f"\nBUY {sym}: ${notional:.2f} notional — {a['reason']}")
        filled = place_market_order(sym, "buy", notional=notional, api_key=api_key, api_secret=api_secret)
        if filled:
            fill_price = float(filled.get("filled_avg_price", 0) or 0)
            filled_qty = filled.get("filled_qty")
            cash -= fill_price * float(filled_qty) if fill_price and filled_qty else notional
            executed.append({
                **a,
                "qty": filled_qty,
                "price": filled.get("filled_avg_price"),
            })
            state.setdefault("positions", {})[sym] = {
                "qty": int(float(filled_qty)) if filled_qty else 0,
                "entry_price": fill_price,
                "opened": datetime.now(timezone.utc).strftime("%Y-%m-%d"),
            }
        else:
            skipped.append({**a, "detail": "buy order failed or not filled"})

    # --- Save state & log ---
    if not args.dry_run:
        save_state(state)

        log_lines = [f"## {datetime.now(timezone.utc).strftime('%Y-%m-%d')} — Rebalance"]
        above_syms = [s for s, v in sma_status.items() if v["above"]]
        below_syms = [s for s, v in sma_status.items() if not v["above"]]
        log_lines.append(f"Above SMA200: {', '.join(above_syms) or 'none'}")
        log_lines.append(f"Below SMA200: {', '.join(below_syms) or 'none'}")
        for e in executed:
            detail = f"${e.get('notional', 0):.0f}" if "notional" in e else f"{e.get('qty', '?')}sh @ ${e.get('price', '?')}"
            log_lines.append(f"- {e['action']} {e['symbol']} ({detail})")
        if skipped_external:
            log_lines.append(f"Skipped (external): {', '.join(skipped_external)}")
        append_log("\n".join(log_lines))

    # --- Summary ---
    print("\n" + "=" * 70)
    print(f"SUMMARY: {len(executed)} action(s) executed, {len(skipped)} skipped")
    for e in executed:
        detail = f"~${e.get('notional', 0):.2f}" if "notional" in e else f"{e.get('qty', '?')}sh"
        prefix = "[DRY RUN] " if e.get("dry_run") else ""
        print(f"  {prefix}{e['action']} {e['symbol']} {detail}")
    for s in skipped:
        print(f"  SKIPPED {s['action']} {s['symbol']}: {s['detail']}")
    print("=" * 70)

    # --- Telegram summary ---
    tag = "[DRY RUN] " if args.dry_run else ""
    lines = [f"📊 {tag}Asset Class Trend-Following — Rebalance"]
    above_syms = [s for s, v in sma_status.items() if v["above"]]
    below_syms = [s for s, v in sma_status.items() if not v["above"]]
    lines.append(f"Above SMA200: {', '.join(above_syms) or 'none'}")
    lines.append(f"Below SMA200: {', '.join(below_syms) or 'none'}")
    lines.append("")
    if executed:
        for e in executed:
            detail = f"${e.get('notional', 0):.0f}" if "notional" in e else f"{e.get('qty', '?')}sh"
            lines.append(f"{e['action']} {e['symbol']} ({detail})")
    else:
        lines.append("No actions executed.")
    if skipped:
        lines.append("")
        lines.append("Skipped: " + ", ".join(f"{s['symbol']} ({s['detail']})" for s in skipped))
    lines.append("")
    lines.append(f"Equity: ${equity:.2f} | Allocation: {args.allocation*100:.0f}%")

    send_telegram("\n".join(lines), tg_token, tg_chat)

    print("\nDone.")


if __name__ == "__main__":
    main()

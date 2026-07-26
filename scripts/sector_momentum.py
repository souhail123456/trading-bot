#!/usr/bin/env python3
"""
Strategy 5 — Sector Momentum (SPDR sector ETF rotation)
=========================================================
Mechanical, monthly rebalance. No LLM, no discretion.

Rules:
  Universe: 10 SPDR sector ETFs (XLB, XLE, XLF, XLI, XLK, XLP, XLRE, XLU,
            XLV, XLY)
  Signal:   Rank all 10 by 12-month (252 trading-day) trailing return
  Entry:    Buy top 3 sectors by momentum
  Exit:     Sell when a sector drops out of the top 3
  Rebal:    Monthly, first trading day of month
  Sizing:   Equal weight among top 3 (1/3 of allocated capital each)

IMPORTANT — shared-account safety:
  This bot trades the SAME Alpaca paper account as the trend-following
  strategy (scripts/strategy_signals.py), which also trades some of these
  sector ETFs (XLE, XLF, XLI, XLK, XLV...). Alpaca positions are aggregated
  per-symbol at the broker — there is no way to split one symbol's position
  by strategy. To avoid this bot liquidating shares it never bought (or
  double-buying a symbol another strategy already holds), it keeps its own
  ownership ledger in memory/sector_momentum_state.json and:
    - only SELLS quantity it tracked itself opening (never more than that,
      and never more than is actually held),
    - SKIPS buying a top-3 symbol that Alpaca already shows a position in
      but that this bot didn't open (avoids accidental doubling-up).

Output: /tmp/sector_momentum_signals.json
State:  memory/sector_momentum_state.json (committed by the workflow)
Log:    memory/SECTOR-MOMENTUM-LOG.md (committed by the workflow)
"""
import argparse
import json
import math
import os
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
import uuid
from datetime import datetime, timedelta, timezone

try:
    import yfinance as yf
except ImportError:
    yf = None

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------

SECTOR_ETFS = {
    "XLB": "Materials",
    "XLE": "Energy",
    "XLF": "Financials",
    "XLI": "Industrials",
    "XLK": "Technology",
    "XLP": "Consumer Staples",
    "XLRE": "Real Estate",
    "XLU": "Utilities",
    "XLV": "Health Care",
    "XLY": "Consumer Discretionary",
}

LOOKBACK_TRADING_DAYS = 260   # bars to keep after download
RETURN_WINDOW = 252           # 12-month trailing return window
TOP_N = 3
DEFAULT_ALLOCATION = 0.4      # 40% of total account equity

ALPACA_TRADE_BASE = "https://paper-api.alpaca.markets/v2"
ALPACA_DATA_BASE = "https://data.alpaca.markets/v2"

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
STATE_FILE = os.path.join(SCRIPT_DIR, "..", "memory", "sector_momentum_state.json")
LOG_FILE = os.path.join(SCRIPT_DIR, "..", "memory", "SECTOR-MOMENTUM-LOG.md")
OUT_FILE = "/tmp/sector_momentum_signals.json"

API_KEY = os.environ.get("ALPACA_API_KEY", "")
API_SECRET = os.environ.get("ALPACA_SECRET_KEY", "")


# ---------------------------------------------------------------------------
# Alpaca helpers (stdlib urllib — matches execute_trades.py / reconcile.py)
# ---------------------------------------------------------------------------

def alpaca(method, path, data=None, base=ALPACA_TRADE_BASE, params=None):
    url = f"{base}/{path}"
    if params:
        url += "?" + urllib.parse.urlencode(params)
    body = json.dumps(data).encode() if data else None
    req = urllib.request.Request(url, data=body, method=method)
    req.add_header("APCA-API-KEY-ID", API_KEY)
    req.add_header("APCA-API-SECRET-KEY", API_SECRET)
    if data:
        req.add_header("Content-Type", "application/json")
    try:
        resp = urllib.request.urlopen(req, timeout=20)
        raw = resp.read()
        return json.loads(raw) if raw else {}
    except urllib.error.HTTPError as e:
        body_text = e.read().decode() if e.fp else ""
        print(f"  Alpaca API error: {e.code} {e.reason} — {body_text[:300]}", file=sys.stderr)
        return None
    except Exception as e:
        print(f"  Alpaca API error: {e}", file=sys.stderr)
        return None


def get_account():
    return alpaca("GET", "account")


def get_positions():
    result = alpaca("GET", "positions")
    return result if isinstance(result, list) else []


def get_clock():
    return alpaca("GET", "clock")


def get_latest_price(symbol):
    """Best-effort current price: Alpaca latest quote, else None."""
    q = alpaca("GET", f"stocks/{symbol}/quotes/latest", base=ALPACA_DATA_BASE)
    if q and isinstance(q, dict):
        quote = q.get("quote", {})
        ask = quote.get("ap")
        bid = quote.get("bp")
        if ask and bid and ask > 0 and bid > 0:
            return (ask + bid) / 2
        if ask:
            return ask
        if bid:
            return bid
    return None


def wait_for_fill(order_id, max_retries=30, delay=2):
    """Poll order status until filled/rejected/canceled. Returns final order dict."""
    for i in range(max_retries):
        order = alpaca("GET", f"orders/{order_id}")
        if not order:
            print(f"    Poll {i+1}/{max_retries}: could not fetch order")
            time.sleep(delay)
            continue
        status = order.get("status", "unknown")
        if status == "filled":
            return order
        if status in ("rejected", "canceled", "expired", "done_for_day", "replaced"):
            print(f"    Order terminal status: {status}")
            return order
        if i < max_retries - 1:
            time.sleep(delay)
    print(f"    Order {order_id} not filled after {max_retries} retries")
    return order


# ---------------------------------------------------------------------------
# Telegram
# ---------------------------------------------------------------------------

def send_telegram(msg):
    bot_token = os.environ.get("TELEGRAM_BOT_TOKEN", "")
    chat_id = os.environ.get("TELEGRAM_CHAT_ID", "")
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
        print("Telegram summary sent")
    except Exception as e:
        print(f"Telegram send failed: {e}")


# ---------------------------------------------------------------------------
# State (ownership ledger — see module docstring)
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
            f.write("# Sector Momentum Log — Strategy 5\n\n")
        f.write(text.rstrip() + "\n\n---\n\n")


# ---------------------------------------------------------------------------
# Data — 12-month trailing return per sector ETF via yfinance
# ---------------------------------------------------------------------------

def _closes_from_history(hist):
    if hist is None or hist.empty or "Close" not in hist:
        return None
    closes = hist["Close"].dropna()
    return closes.tail(LOOKBACK_TRADING_DAYS)


def fetch_sector_data():
    """Returns dict: symbol -> {'last_price': float, 'return_252': float, 'bars': int}"""
    if yf is None:
        print("ERROR: yfinance not installed", file=sys.stderr)
        return {}

    tickers = list(SECTOR_ETFS.keys())
    end = datetime.now(timezone.utc)
    start = end - timedelta(days=400)  # generous buffer for 260+ trading days

    data = {}
    bulk = None
    try:
        bulk = yf.download(
            tickers,
            start=start.strftime("%Y-%m-%d"),
            end=(end + timedelta(days=1)).strftime("%Y-%m-%d"),
            auto_adjust=True,
            progress=False,
            group_by="ticker",
            threads=True,
        )
    except Exception as e:
        print(f"  Bulk yfinance download failed: {e}", file=sys.stderr)

    for symbol in tickers:
        closes = None
        try:
            if bulk is not None and not bulk.empty:
                if hasattr(bulk.columns, "levels") and symbol in bulk.columns.get_level_values(0):
                    closes = _closes_from_history(bulk[symbol])
                elif len(tickers) == 1:
                    closes = _closes_from_history(bulk)
        except Exception as e:
            print(f"  {symbol}: error reading bulk frame — {e}", file=sys.stderr)

        if closes is None or len(closes) < RETURN_WINDOW + 1:
            # Fallback: fetch individually
            try:
                hist = yf.Ticker(symbol).history(period="15mo", auto_adjust=True)
                closes = _closes_from_history(hist)
            except Exception as e:
                print(f"  {symbol}: individual fetch failed — {e}", file=sys.stderr)
                closes = None

        if closes is None or len(closes) < RETURN_WINDOW + 1:
            n = 0 if closes is None else len(closes)
            print(f"  {symbol}: insufficient data ({n} bars) — excluded from ranking", file=sys.stderr)
            continue

        last_price = float(closes.iloc[-1])
        base_price = float(closes.iloc[-RETURN_WINDOW])
        if base_price <= 0:
            continue
        ret_252 = (last_price / base_price) - 1.0

        data[symbol] = {
            "last_price": last_price,
            "return_252": ret_252,
            "bars": len(closes),
        }

    return data


# ---------------------------------------------------------------------------
# Ranking
# ---------------------------------------------------------------------------

def rank_sectors(sector_data):
    """Returns list of dicts sorted by return_252 desc, with 'rank' assigned."""
    rows = []
    for symbol, sector_name in SECTOR_ETFS.items():
        if symbol not in sector_data:
            continue
        d = sector_data[symbol]
        rows.append({
            "symbol": symbol,
            "sector": sector_name,
            "return_252": d["return_252"],
            "last_price": d["last_price"],
        })
    rows.sort(key=lambda r: r["return_252"], reverse=True)
    for i, r in enumerate(rows):
        r["rank"] = i + 1
    return rows


def print_ranking(ranked):
    print(f"\n{'Rank':<5}{'Symbol':<8}{'Sector':<24}{'12mo Return':<14}{'Status'}")
    print("-" * 70)
    for r in ranked:
        top3 = r["rank"] <= TOP_N
        marker = "TOP 3" if top3 else ""
        print(
            f"{r['rank']:<5}{r['symbol']:<8}{r['sector']:<24}"
            f"{r['return_252']*100:>+8.2f}%     {marker}"
        )
    print("-" * 70)


# ---------------------------------------------------------------------------
# Decision logic
# ---------------------------------------------------------------------------

def decide_actions(ranked, alpaca_positions, state):
    """
    Returns dict with keys: buys, sells, holds, skips (each list of dicts).
    alpaca_positions: {symbol: position_dict} for symbols in SECTOR_ETFS.
    state['positions']: {symbol: {"qty":.., "entry_price":.., "opened":..}}
    """
    top3 = [r["symbol"] for r in ranked[:TOP_N]]
    tracked = state.get("positions", {})

    buys, sells, holds, skips = [], [], [], []

    for symbol in top3:
        if symbol in tracked:
            holds.append({"symbol": symbol, "reason": "in top 3, already held by this strategy"})
        elif symbol in alpaca_positions:
            skips.append({
                "symbol": symbol,
                "reason": "in top 3 but already held externally (not opened by sector-momentum) — "
                          "skipping buy to avoid double exposure",
            })
        else:
            buys.append({"symbol": symbol, "reason": "entered top 3, not currently held"})

    for symbol in list(tracked.keys()):
        if symbol not in top3:
            sells.append({"symbol": symbol, "reason": "dropped out of top 3"})

    return {"buys": buys, "sells": sells, "holds": holds, "skips": skips}


# ---------------------------------------------------------------------------
# Execution
# ---------------------------------------------------------------------------

def execute_buy(symbol, notional, ranked_price, dry_run):
    price = get_latest_price(symbol) or ranked_price
    if not price or price <= 0:
        print(f"  {symbol}: BUY skipped — no price available")
        return None

    qty = math.floor(notional / price)
    if qty < 1:
        print(f"  {symbol}: BUY skipped — notional ${notional:.2f} too small at ${price:.2f}/sh")
        return None

    if dry_run:
        print(f"  [DRY RUN] Would BUY {qty}sh {symbol} (~${notional:.2f} @ ~${price:.2f})")
        return {"symbol": symbol, "qty": qty, "price": price, "dry_run": True}

    client_order_id = f"sm-{symbol}-buy-{uuid.uuid4().hex[:8]}"
    print(f"  Submitting BUY {qty}sh {symbol} (client_order_id={client_order_id})")
    order = alpaca("POST", "orders", {
        "symbol": symbol,
        "qty": str(qty),
        "side": "buy",
        "type": "market",
        "time_in_force": "day",
        "client_order_id": client_order_id,
    })
    if not order:
        print(f"  {symbol}: BUY order submission failed")
        return None

    filled = wait_for_fill(order["id"])
    if not filled or filled.get("status") != "filled":
        status = filled.get("status", "unknown") if filled else "unknown"
        print(f"  {symbol}: BUY not filled — status={status}")
        return None

    fill_price = float(filled.get("filled_avg_price") or price)
    filled_qty = int(float(filled.get("filled_qty") or qty))
    print(f"  {symbol}: CONFIRMED FILL {filled_qty}sh @ ${fill_price:.2f}")
    return {"symbol": symbol, "qty": filled_qty, "price": fill_price, "dry_run": False}


def execute_sell(symbol, tracked_qty, held_qty, dry_run):
    sell_qty = min(tracked_qty, held_qty) if held_qty > 0 else 0

    if sell_qty <= 0:
        print(f"  {symbol}: nothing to sell on broker (held={held_qty}, tracked={tracked_qty}) — clearing from ledger")
        return {"symbol": symbol, "qty": 0, "cleared_only": True}

    if dry_run:
        print(f"  [DRY RUN] Would SELL {sell_qty}sh {symbol} (tracked={tracked_qty}, held={held_qty})")
        return {"symbol": symbol, "qty": sell_qty, "dry_run": True}

    params = {} if sell_qty >= held_qty else {"qty": str(sell_qty)}
    print(f"  Closing {symbol}: selling {sell_qty}sh (held={held_qty})")
    order = alpaca("DELETE", f"positions/{symbol}", params=params)
    if not order or not order.get("id"):
        print(f"  {symbol}: SELL/close request failed")
        return None

    filled = wait_for_fill(order["id"])
    if not filled or filled.get("status") != "filled":
        status = filled.get("status", "unknown") if filled else "unknown"
        print(f"  {symbol}: SELL not confirmed filled — status={status}")
        # Still clear from ledger conservatively only if terminal-failed states differ; be safe and keep tracked.
        return None

    fill_price = float(filled.get("filled_avg_price") or 0)
    filled_qty = int(float(filled.get("filled_qty") or sell_qty))
    print(f"  {symbol}: CONFIRMED SELL {filled_qty}sh @ ${fill_price:.2f}")
    return {"symbol": symbol, "qty": filled_qty, "price": fill_price, "dry_run": False}


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description="Strategy 5 — Sector Momentum rebalance")
    parser.add_argument("--dry-run", action="store_true", help="Compute and print only, no orders/state/telegram")
    parser.add_argument("--allocation", type=float, default=DEFAULT_ALLOCATION,
                         help="Fraction of total account equity allocated to this strategy (default 0.4)")
    args = parser.parse_args()

    if not (0 < args.allocation <= 1):
        print(f"ERROR: --allocation must be in (0, 1], got {args.allocation}", file=sys.stderr)
        sys.exit(1)

    print("=== Strategy 5 — Sector Momentum ===")
    print(f"Allocation: {args.allocation*100:.0f}% of equity | Dry run: {args.dry_run}")

    if not API_KEY or not API_SECRET:
        print("ERROR: ALPACA_API_KEY / ALPACA_SECRET_KEY not set", file=sys.stderr)
        sys.exit(1)

    # --- Data: 12mo trailing returns for the 10 sector ETFs ---
    print(f"\nFetching {len(SECTOR_ETFS)} sector ETFs via yfinance (last ~{LOOKBACK_TRADING_DAYS} trading days)...")
    sector_data = fetch_sector_data()
    if len(sector_data) < TOP_N:
        print(f"ERROR: only {len(sector_data)} sectors had usable data — aborting", file=sys.stderr)
        sys.exit(1)

    ranked = rank_sectors(sector_data)
    print_ranking(ranked)
    top3 = [r["symbol"] for r in ranked[:TOP_N]]
    print(f"\nTop 3: {', '.join(top3)}")

    # --- Account + positions ---
    account = get_account()
    if not account or "equity" not in account:
        print("ERROR: could not fetch Alpaca account — aborting", file=sys.stderr)
        sys.exit(1)
    equity = float(account["equity"])
    print(f"\nAccount equity: ${equity:,.2f}")

    positions = get_positions()
    alpaca_positions = {p["symbol"]: p for p in positions if p["symbol"] in SECTOR_ETFS}
    print(f"Current sector-ETF positions on Alpaca: {sorted(alpaca_positions.keys()) or 'none'}")

    state = load_state()
    tracked = state.get("positions", {})
    print(f"Tracked by this strategy (memory/sector_momentum_state.json): {sorted(tracked.keys()) or 'none'}")

    # --- Decide ---
    decisions = decide_actions(ranked, alpaca_positions, state)
    print(f"\nDecisions: BUY={len(decisions['buys'])} SELL={len(decisions['sells'])} "
          f"HOLD={len(decisions['holds'])} SKIP={len(decisions['skips'])}")
    for b in decisions["buys"]:
        print(f"  BUY  {b['symbol']:<6} — {b['reason']}")
    for s in decisions["sells"]:
        print(f"  SELL {s['symbol']:<6} — {s['reason']}")
    for h in decisions["holds"]:
        print(f"  HOLD {h['symbol']:<6} — {h['reason']}")
    for sk in decisions["skips"]:
        print(f"  SKIP {sk['symbol']:<6} — {sk['reason']}")

    # --- Market hours ---
    clock = get_clock()
    market_open = bool(clock and clock.get("is_open"))
    if not args.dry_run and not market_open:
        print("\nMarket is CLOSED — not submitting orders this run. Rankings/decisions shown above only.")
        msg = (
            f"Sector Momentum — market closed, rebalance deferred.\n"
            f"Top 3: {', '.join(top3)}\n"
            f"Planned: BUY {[b['symbol'] for b in decisions['buys']]}, "
            f"SELL {[s['symbol'] for s in decisions['sells']]}"
        )
        send_telegram(msg)
        write_output(ranked, decisions, equity, args, executed={"buys": [], "sells": []})
        return

    notional_per_slot = (equity * args.allocation) / TOP_N
    print(f"\nPer-slot notional (equal weight, 1/3 of {args.allocation*100:.0f}% allocation): ${notional_per_slot:,.2f}")

    executed_buys = []
    executed_sells = []

    if decisions["buys"] or decisions["sells"]:
        print("\n--- Execution ---")

    for b in decisions["buys"]:
        symbol = b["symbol"]
        price_hint = next((r["last_price"] for r in ranked if r["symbol"] == symbol), 0)
        result = execute_buy(symbol, notional_per_slot, price_hint, args.dry_run)
        if result:
            executed_buys.append(result)
            if not args.dry_run:
                state.setdefault("positions", {})[symbol] = {
                    "qty": result["qty"],
                    "entry_price": result["price"],
                    "opened": datetime.now(timezone.utc).strftime("%Y-%m-%d"),
                }

    for s in decisions["sells"]:
        symbol = s["symbol"]
        tracked_qty = int(tracked.get(symbol, {}).get("qty", 0))
        held_qty = int(float(alpaca_positions.get(symbol, {}).get("qty", 0)))
        result = execute_sell(symbol, tracked_qty, held_qty, args.dry_run)
        if result:
            executed_sells.append(result)
            if not args.dry_run:
                state.get("positions", {}).pop(symbol, None)

    if not args.dry_run:
        save_state(state)

        log_lines = [f"## {datetime.now(timezone.utc).strftime('%Y-%m-%d')} — Rebalance"]
        log_lines.append(f"Top 3: {', '.join(top3)}")
        for r in ranked:
            log_lines.append(f"- #{r['rank']} {r['symbol']} ({r['sector']}): {r['return_252']*100:+.2f}%")
        if executed_buys:
            log_lines.append("**Bought:** " + ", ".join(f"{e['symbol']} {e['qty']}sh @ ${e['price']:.2f}" for e in executed_buys))
        if executed_sells:
            log_lines.append("**Sold:** " + ", ".join(f"{e['symbol']} {e.get('qty', 0)}sh" for e in executed_sells))
        if decisions["skips"]:
            log_lines.append("**Skipped:** " + ", ".join(f"{sk['symbol']} ({sk['reason']})" for sk in decisions["skips"]))
        append_log("\n".join(log_lines))

        msg_lines = ["Sector Momentum — monthly rebalance"]
        msg_lines.append(f"Top 3: {', '.join(top3)}")
        if executed_buys:
            msg_lines.append("Bought: " + ", ".join(f"{e['symbol']} {e['qty']}sh @${e['price']:.2f}" for e in executed_buys))
        if executed_sells:
            msg_lines.append("Sold: " + ", ".join(f"{e['symbol']} {e.get('qty', 0)}sh" for e in executed_sells))
        if decisions["skips"]:
            msg_lines.append("Skipped: " + ", ".join(sk["symbol"] for sk in decisions["skips"]))
        if not executed_buys and not executed_sells:
            msg_lines.append("No changes — top 3 unchanged from last rebalance.")
        send_telegram("\n".join(msg_lines))
    else:
        print("\n[DRY RUN] No orders submitted, no state/log/telegram side effects.")

    write_output(ranked, decisions, equity, args, {"buys": executed_buys, "sells": executed_sells})
    print("\nDone.")


def write_output(ranked, decisions, equity, args, executed):
    output = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "dry_run": args.dry_run,
        "allocation": args.allocation,
        "equity": equity,
        "ranking": ranked,
        "top3": [r["symbol"] for r in ranked[:TOP_N]],
        "decisions": decisions,
        "executed": executed,
    }
    with open(OUT_FILE, "w") as f:
        json.dump(output, f, indent=2)
    print(f"\nSaved to {OUT_FILE}")


if __name__ == "__main__":
    main()

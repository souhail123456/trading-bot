#!/usr/bin/env python3
"""
Trend ETF — Validated Long-Only Trend-Following (SPY / QQQ / GLD)
=================================================================
Mechanical, systematic strategy. NO LLM involved.

This is the ONLY strategy the reactivated bot runs. It replaces the older,
weaker strategies (market-open / midday / afternoon / asset_class_tf /
sector_momentum), which remain in the repo but DISABLED.

Universe (all three passed an out-of-sample backtest with Profit Factor > 1.5
over full daily history — see the workflow / TASKS notes):
  SPY, QQQ  — broad US equity ETFs
  GLD       — gold ETF (needs the extra trend-strength gate, see below)

Rules (daily bars, long-only, one position per symbol):
  Entry:  Close > SMA(200)  AND  MACD_hist(12,26,9) > 0
          GLD ONLY also requires ADX(14) > 25 (gold needs the trend-strength
          gate; SPY/QQQ do not).
  Exit:   Close < SMA(200)  -> close the position (the "SMA-recross" exit).
          LET WINNERS RUN — there is no fixed take-profit.
  Stop:   a protective STOP resting 2 x ATR(14) below the entry price,
          attached atomically to the entry via an Alpaca OTO order (so the
          stop can never be orphaned).
  Sizing: risk 1% of account equity per trade across the 2*ATR stop distance
          -> shares = floor( (0.01 * equity) / (2 * ATR) ).
          Then CAP each position's notional so the sum of new buys never
          exceeds available buying power (a tight ATR stop can imply a huge
          notional). If a buy would exceed remaining buying power, scale the
          share count down and log it. Positions needing < 1 share are skipped.

Source of truth = ALPACA. Positions, orders and account are always read live
from the broker (GET /positions, /orders, /account). There is NO local ledger
or parallel DB that could diverge from the broker (the reconciliation lesson).

Self-contained: downloads its own daily OHLC via yfinance, reads/writes Alpaca
via stdlib urllib with APCA header auth (same pattern as the rest of the bot).

Usage:
  python3 scripts/trend_etf.py --dry-run     # show decisions, place nothing
  python3 scripts/trend_etf.py               # live (paper) — place orders

Env: ALPACA_API_KEY, ALPACA_SECRET_KEY  (paper account, in GitHub secrets).
     TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID (optional summary).
"""
import argparse
import json
import math
import os
import sys
import time
import urllib.error
import urllib.request
import uuid
from datetime import datetime, timezone

# Deployable universe. ADX_GATE symbols require ADX(14) > 25 in addition to the
# Close>SMA200 + MACD>0 entry. (Only GLD, per the validation backtest.)
UNIVERSE = ["SPY", "QQQ", "GLD"]
ADX_GATE = {"GLD"}

SMA_PERIOD = 200
MACD_FAST, MACD_SLOW, MACD_SIGNAL = 12, 26, 9
ATR_PERIOD = 14
ADX_PERIOD = 14
ADX_THRESHOLD = 25.0
ATR_STOP_MULT = 2.0
RISK_PCT = 0.01               # risk 1% of equity per trade
LOOKBACK_DAYS = 420           # enough daily bars for a stable 200d SMA

ALPACA_BASE = "https://paper-api.alpaca.markets/v2"


# ---------------------------------------------------------------------------
# Alpaca / Telegram HTTP helpers (stdlib only)
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
        print(f"  Alpaca API error: {e.code} {e.reason} — {body_text[:400]}")
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
        data=data, headers={"Content-Type": "application/json"})
    try:
        urllib.request.urlopen(req, timeout=10)
        print("[telegram] Summary sent")
    except Exception as e:
        print(f"[telegram] Send failed: {e}")


# ---------------------------------------------------------------------------
# Indicators (pure-python over lists of floats; Wilder smoothing for ATR/ADX)
# ---------------------------------------------------------------------------

def sma(values, period):
    if len(values) < period:
        return None
    return sum(values[-period:]) / period


def ema_series(values, span):
    k = 2.0 / (span + 1.0)
    out = []
    prev = values[0]
    for v in values:
        prev = v * k + prev * (1 - k)
        out.append(prev)
    return out


def macd_hist(closes):
    if len(closes) < MACD_SLOW + MACD_SIGNAL:
        return None
    fast = ema_series(closes, MACD_FAST)
    slow = ema_series(closes, MACD_SLOW)
    macd_line = [f - s for f, s in zip(fast, slow)]
    signal = ema_series(macd_line, MACD_SIGNAL)
    return macd_line[-1] - signal[-1]


def _wilder(values, period):
    """Wilder's RMA smoothing. Returns full smoothed series."""
    if len(values) < period:
        return []
    out = [None] * (period - 1)
    seed = sum(values[:period]) / period
    out.append(seed)
    prev = seed
    for v in values[period:]:
        prev = (prev * (period - 1) + v) / period
        out.append(prev)
    return out


def true_ranges(highs, lows, closes):
    tr = [highs[0] - lows[0]]
    for i in range(1, len(closes)):
        tr.append(max(
            highs[i] - lows[i],
            abs(highs[i] - closes[i - 1]),
            abs(lows[i] - closes[i - 1]),
        ))
    return tr


def atr(highs, lows, closes, period=ATR_PERIOD):
    tr = true_ranges(highs, lows, closes)
    series = _wilder(tr, period)
    return series[-1] if series and series[-1] is not None else None


def adx(highs, lows, closes, period=ADX_PERIOD):
    n = len(closes)
    if n < 2 * period + 1:
        return None
    tr = true_ranges(highs, lows, closes)
    plus_dm, minus_dm = [0.0], [0.0]
    for i in range(1, n):
        up = highs[i] - highs[i - 1]
        down = lows[i - 1] - lows[i]
        plus_dm.append(up if (up > down and up > 0) else 0.0)
        minus_dm.append(down if (down > up and down > 0) else 0.0)
    atr_s = _wilder(tr, period)
    plus_s = _wilder(plus_dm, period)
    minus_s = _wilder(minus_dm, period)
    dx = []
    for i in range(len(atr_s)):
        a = atr_s[i]
        if a is None or a == 0 or plus_s[i] is None or minus_s[i] is None:
            dx.append(None)
            continue
        pdi = 100 * plus_s[i] / a
        mdi = 100 * minus_s[i] / a
        denom = pdi + mdi
        dx.append(100 * abs(pdi - mdi) / denom if denom else 0.0)
    valid = [d for d in dx if d is not None]
    adx_s = _wilder(valid, period)
    return adx_s[-1] if adx_s and adx_s[-1] is not None else None


# ---------------------------------------------------------------------------
# Market data via yfinance -> per-symbol indicator snapshot
# ---------------------------------------------------------------------------

def fetch_signals(symbols):
    """Download daily OHLC and compute the latest indicator snapshot per symbol.

    Returns dict: symbol -> {close, sma200, macd_hist, atr, adx, entry(bool),
                             above_sma(bool)}  (symbols with insufficient data omitted)
    """
    import yfinance as yf

    print(f"Downloading {LOOKBACK_DAYS}d daily OHLC for {symbols} via yfinance...")
    data = yf.download(symbols, period=f"{LOOKBACK_DAYS}d", interval="1d",
                       auto_adjust=True, progress=False, group_by="ticker")

    out = {}
    for sym in symbols:
        try:
            if len(symbols) == 1:
                sub = data
            else:
                sub = data[sym]
            sub = sub.dropna()
            closes = [float(x) for x in sub["Close"].tolist()]
            highs = [float(x) for x in sub["High"].tolist()]
            lows = [float(x) for x in sub["Low"].tolist()]
        except Exception as e:
            print(f"  {sym}: could not extract OHLC ({e}) — SKIPPING")
            continue

        if len(closes) < SMA_PERIOD:
            print(f"  {sym}: only {len(closes)} bars, need {SMA_PERIOD} — SKIPPING")
            continue

        close = closes[-1]
        s200 = sma(closes, SMA_PERIOD)
        mh = macd_hist(closes)
        a = atr(highs, lows, closes)
        adx_v = adx(highs, lows, closes)
        if None in (s200, mh, a) or (sym in ADX_GATE and adx_v is None):
            print(f"  {sym}: indicator computation incomplete — SKIPPING")
            continue

        above = close > s200
        entry = above and mh > 0
        if sym in ADX_GATE:
            entry = entry and adx_v > ADX_THRESHOLD

        out[sym] = {"close": close, "sma200": s200, "macd_hist": mh,
                    "atr": a, "adx": adx_v, "entry": entry, "above_sma": above}
        gate = f" ADX={adx_v:.1f}(need>{ADX_THRESHOLD:.0f})" if sym in ADX_GATE else ""
        print(f"  {sym}: close=${close:.2f} SMA200=${s200:.2f} "
              f"MACDh={mh:+.3f} ATR={a:.2f}{gate} -> "
              f"{'ENTRY-OK' if entry else ('above-SMA/no-MACD' if above else 'below-SMA')}")
    return out


# ---------------------------------------------------------------------------
# Order placement
# ---------------------------------------------------------------------------

def wait_for_fill(order_id, api_key, api_secret, max_retries=15, delay=2):
    """Poll an order. Returns (order, filled_bool). When the market is closed the
    entry is 'accepted'/queued and never fills within our window — that is NOT a
    failure (the OTO stop is attached and it will fill at the next open)."""
    last = None
    for i in range(max_retries):
        order = alpaca_request("GET", f"orders/{order_id}", api_key, api_secret)
        if order:
            last = order
            st = order.get("status")
            if st == "filled":
                return order, True
            if st in ("rejected", "canceled", "expired"):
                print(f"  Order terminal status: {st}")
                return order, False
        if i < max_retries - 1:
            time.sleep(delay)
    return last, False


def place_entry_with_stop(symbol, shares, stop_price, api_key, api_secret):
    """Submit an OTO (one-triggers-other): a MARKET buy that, once filled, leaves
    a resting GTC protective STOP at stop_price. Atomic — the stop can't orphan."""
    coid = f"trend-{symbol}-{uuid.uuid4().hex[:8]}"
    order = {
        "symbol": symbol,
        "qty": str(int(shares)),
        "side": "buy",
        "type": "market",
        "time_in_force": "gtc",
        "order_class": "oto",
        "stop_loss": {"stop_price": f"{stop_price:.2f}"},
        "client_order_id": coid,
    }
    print(f"  Submitting OTO BUY {symbol} qty={int(shares)} "
          f"protective stop @ ${stop_price:.2f} [coid={coid}]")
    resp = alpaca_request("POST", "orders", api_key, api_secret, order)
    if not resp:
        print(f"  FAILED to submit entry for {symbol}")
        return None
    print(f"  Order accepted: id={resp.get('id')} status={resp.get('status')}")
    filled_order, filled = wait_for_fill(resp["id"], api_key, api_secret)
    if filled:
        print(f"  CONFIRMED FILL: {symbol} {filled_order.get('filled_qty')}sh "
              f"@ ${filled_order.get('filled_avg_price')} (stop @ ${stop_price:.2f})")
    else:
        st = filled_order.get("status") if filled_order else "unknown"
        print(f"  Entry QUEUED (status={st}) — market likely closed; will fill at "
              f"next open. Protective stop is attached via OTO.")
    return resp


def close_position(symbol, api_key, api_secret):
    """Close a whole position at market and cancel its resting orders (the stop)."""
    print(f"  Closing {symbol} (DELETE positions/{symbol}?cancel_orders=true)")
    resp = alpaca_request("DELETE", f"positions/{symbol}?cancel_orders=true",
                          api_key, api_secret)
    if resp is None:
        print(f"  FAILED to close {symbol}")
        return False
    print(f"  Close order submitted for {symbol}")
    return True


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    ap = argparse.ArgumentParser(description="Trend ETF — SPY/QQQ/GLD long-only trend follower")
    ap.add_argument("--dry-run", action="store_true", help="Show decisions, place no orders")
    args = ap.parse_args()

    print("=" * 70)
    print("TREND ETF — LONG-ONLY TREND FOLLOWING (SPY / QQQ / GLD)")
    print(f"Run time (UTC): {datetime.now(timezone.utc).isoformat()}")
    print(f"Universe: {UNIVERSE}  | ADX gate: {sorted(ADX_GATE)}")
    print(f"Dry run: {args.dry_run}")
    print("=" * 70)

    api_key = os.environ.get("ALPACA_API_KEY", "")
    api_secret = os.environ.get("ALPACA_SECRET_KEY", "")
    tg_token = os.environ.get("TELEGRAM_BOT_TOKEN", "")
    tg_chat = os.environ.get("TELEGRAM_CHAT_ID", "")
    if not api_key or not api_secret:
        print("ERROR: ALPACA_API_KEY / ALPACA_SECRET_KEY not set — aborting")
        sys.exit(1)

    # --- Account (auth check + equity/buying power) ---
    account = alpaca_request("GET", "account", api_key, api_secret)
    if not account:
        print("ERROR: could not fetch Alpaca account (auth?) — aborting")
        sys.exit(1)
    equity = float(account.get("equity", 0))
    cash = float(account.get("cash", 0))
    # Long-only, no leverage: cap deployment to cash on hand (never margin).
    available_bp = min(cash, float(account.get("buying_power", cash) or cash))
    print(f"\nAuthenticated to Alpaca paper. equity=${equity:.2f} cash=${cash:.2f} "
          f"available_bp=${available_bp:.2f}")

    clock = alpaca_request("GET", "clock", api_key, api_secret)
    market_open = bool(clock.get("is_open")) if clock else None
    next_open = clock.get("next_open") if clock else "unknown"
    print(f"Market open now: {market_open} (next_open: {next_open})")
    if market_open is False:
        print("NOTE: market closed — any BUY/SELL is accepted & QUEUED to fill at "
              "the next open (OTO stops attach on fill). This is expected.")

    # --- Live positions & open orders (SOURCE OF TRUTH = Alpaca) ---
    positions = alpaca_request("GET", "positions", api_key, api_secret)
    if positions is None:
        print("ERROR: could not fetch positions — aborting")
        sys.exit(1)
    held = {p["symbol"]: p for p in positions if p["symbol"] in UNIVERSE}
    print(f"Held in universe: {sorted(held.keys()) or 'none'}")

    open_orders = alpaca_request("GET", "orders?status=open&limit=200",
                                 api_key, api_secret) or []
    pending_buy = {o["symbol"] for o in open_orders
                   if o.get("side") == "buy" and o.get("symbol") in UNIVERSE}
    if pending_buy:
        print(f"Pending BUY orders (won't duplicate): {sorted(pending_buy)}")

    # --- Signals ---
    print("\n--- SIGNALS ---")
    sig = fetch_signals(UNIVERSE)
    if not sig:
        print("ERROR: no signal data for any symbol — aborting")
        sys.exit(1)

    # --- Decisions: exits first (frees buying power), then entries ---
    print("\n--- DECISIONS ---")
    exits, entries, holds, skips = [], [], [], []
    for sym in UNIVERSE:
        s = sig.get(sym)
        is_held = sym in held
        if s is None:
            skips.append((sym, "no data")); print(f"  {sym}: SKIP (no data)"); continue
        if is_held:
            if not s["above_sma"]:
                exits.append(sym); print(f"  {sym}: EXIT — close < SMA200 (recross exit)")
            else:
                holds.append(sym); print(f"  {sym}: HOLD — held & above SMA200, let it run")
        else:
            if sym in pending_buy:
                skips.append((sym, "buy already pending")); print(f"  {sym}: SKIP — buy already pending")
            elif s["entry"]:
                entries.append(sym); print(f"  {sym}: ENTER — entry conditions met")
            else:
                skips.append((sym, "no entry signal")); print(f"  {sym}: no action (flat, no signal)")

    # --- Execute exits ---
    executed = []
    for sym in exits:
        if args.dry_run:
            print(f"[DRY RUN] would CLOSE {sym}"); executed.append(("EXIT", sym, "dry")); continue
        if close_position(sym, api_key, api_secret):
            executed.append(("EXIT", sym, "submitted"))

    # --- Execute entries with 1% risk sizing + buying-power cap ---
    remaining_bp = available_bp
    for sym in entries:
        s = sig[sym]
        price, a = s["close"], s["atr"]
        stop_price = price - ATR_STOP_MULT * a
        risk_money = RISK_PCT * equity
        raw_shares = math.floor(risk_money / (ATR_STOP_MULT * a))
        if raw_shares < 1:
            skips.append((sym, "risk-sized <1 share")); print(f"  {sym}: SKIP — 1% risk sizes < 1 share"); continue
        shares = raw_shares
        notional = shares * price
        # Cap notional to remaining buying power (tight ATR stop can imply a huge notional).
        if notional > remaining_bp:
            capped = math.floor(remaining_bp / price)
            print(f"  {sym}: notional ${notional:.0f} > available_bp ${remaining_bp:.0f} "
                  f"— scaling {shares} -> {capped} shares")
            shares = capped
            if shares < 1:
                skips.append((sym, "no buying power")); print(f"  {sym}: SKIP — no buying power left"); continue
            notional = shares * price
        risk_at_stop = shares * (ATR_STOP_MULT * a)
        print(f"  {sym}: BUY {shares}sh @ ~${price:.2f} (notional ${notional:.0f}, "
              f"stop ${stop_price:.2f}, risk ${risk_at_stop:.0f} = {risk_at_stop/equity*100:.2f}% equity)")
        if args.dry_run:
            executed.append(("ENTER", sym, f"{shares}sh dry")); remaining_bp -= notional; continue
        resp = place_entry_with_stop(sym, shares, stop_price, api_key, api_secret)
        if resp:
            executed.append(("ENTER", sym, f"{shares}sh")); remaining_bp -= notional
        else:
            skips.append((sym, "order failed"))

    # --- Summary ---
    print("\n" + "=" * 70)
    print(f"SUMMARY: {len(executed)} action(s), {len(holds)} hold(s), {len(skips)} skip(s)")
    for kind, sym, detail in executed:
        print(f"  {kind} {sym} ({detail})")
    for sym in holds:
        print(f"  HOLD {sym}")
    for sym, why in skips:
        print(f"  SKIP {sym} ({why})")
    print("=" * 70)

    # --- Telegram ---
    tag = "[DRY RUN] " if args.dry_run else ""
    lines = [f"📈 {tag}Trend ETF (SPY/QQQ/GLD)"]
    for kind, sym, detail in executed:
        lines.append(f"{kind} {sym} ({detail})")
    if holds:
        lines.append("HOLD: " + ", ".join(holds))
    if not executed and not holds:
        lines.append("No positions; no entry signals today.")
    lines.append(f"Equity ${equity:.0f} | cash ${cash:.0f}")
    send_telegram("\n".join(lines), tg_token, tg_chat)

    print("\nDone.")


if __name__ == "__main__":
    main()

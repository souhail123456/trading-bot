#!/usr/bin/env python3
"""
Trend-Following in Stocks — Signal Generator
=============================================
Implements a validated trend-following strategy for a universe of liquid
stocks and ETFs. Uses Alpaca market data API (no extra deps required).

Rules:
  Entry:  price > SMA-200 AND SMA-50 > SMA-200 (golden cross confirmation)
  Exit:   price < SMA-200 OR SMA-50 < SMA-200
  Sizing: equal weight, max 5 positions, ~20% of portfolio each
  Regime: if CRISIS regime → go to cash (no new entries)

Output: /tmp/strategy_signals.json
"""
import json
import os
import sys
import urllib.request
import urllib.parse
from datetime import datetime, timedelta, timezone

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------

UNIVERSE = [
    # Broad market ETFs
    "SPY", "QQQ", "IWM",
    # Mega-cap stocks
    "AAPL", "MSFT", "GOOGL", "AMZN", "NVDA", "META", "TSLA",
    # Sector ETFs
    "XLK", "XLF", "XLE", "XLV", "XLI",
]

SMA_FAST = 50
SMA_MEDIUM = 20
SMA_SLOW = 200
MAX_POSITIONS = 7
POSITION_SIZE_PCT = 15   # % of equity per position
SHORT_SIZE_PCT = 10      # % of equity per short position (smaller than longs)
DEFAULT_STOP_PCT = "10"  # trailing stop %
SHORT_STOP_PCT = "7"     # tighter stop for shorts

ALPACA_DATA_BASE = "https://data.alpaca.markets/v2"


# ---------------------------------------------------------------------------
# Alpaca data helpers (stdlib only — no yfinance, no pandas)
# ---------------------------------------------------------------------------

def _alpaca_get(path: str, params: dict | None = None) -> dict | list | None:
    api_key = os.environ.get("ALPACA_API_KEY", "")
    api_secret = os.environ.get("ALPACA_SECRET_KEY", "")

    url = f"{ALPACA_DATA_BASE}/{path}"
    if params:
        url += "?" + urllib.parse.urlencode(params)

    req = urllib.request.Request(url)
    req.add_header("APCA-API-KEY-ID", api_key)
    req.add_header("APCA-API-SECRET-KEY", api_secret)

    try:
        resp = urllib.request.urlopen(req, timeout=15)
        return json.loads(resp.read())
    except Exception as e:
        print(f"  Alpaca data error ({path}): {e}", file=sys.stderr)
        return None


def fetch_daily_closes(symbol: str, days: int = 260) -> list[float]:
    """Return list of daily close prices, oldest first. Returns empty list on error."""
    start = (datetime.now(timezone.utc) - timedelta(days=days + 30)).strftime("%Y-%m-%d")
    data = _alpaca_get(
        f"stocks/{symbol}/bars",
        {
            "timeframe": "1Day",
            "start": start,
            "limit": days + 30,
            "adjustment": "split",
            "feed": "iex",
        },
    )
    if not data or "bars" not in data:
        return []

    bars = data["bars"]
    closes = [bar["c"] for bar in bars if bar.get("c") is not None]
    return closes


def sma(closes: list[float], period: int) -> float | None:
    """Simple moving average of last `period` closes. None if insufficient data."""
    if len(closes) < period:
        return None
    return sum(closes[-period:]) / period


# ---------------------------------------------------------------------------
# Signal generation
# ---------------------------------------------------------------------------

def compute_signals(
    positions_held: list[dict],
    equity: float,
    regime: str,
) -> list[dict]:
    """
    For each symbol in UNIVERSE, compute entry/exit/hold signal.
    positions_held: list of dicts with 'symbol' and 'side' keys.
    Returns list of signal dicts with action='buy'/'sell'/'short'/'cover'/'hold'.
    """
    signals = []
    crisis = regime.upper() == "CRISIS"
    volatile = regime.upper() == "VOLATILE"

    # Build lookup sets for held positions by side
    held_long_symbols = {p["symbol"] for p in positions_held if p.get("side") == "long"}
    held_short_symbols = {p["symbol"] for p in positions_held if p.get("side") == "short"}

    for symbol in UNIVERSE:
        print(f"  Scanning {symbol}...", file=sys.stderr)
        closes = fetch_daily_closes(symbol, days=260)

        if len(closes) < SMA_SLOW + 5:
            print(f"    Insufficient data ({len(closes)} bars) — skip", file=sys.stderr)
            continue

        price = closes[-1]
        fast = sma(closes, SMA_FAST)
        slow = sma(closes, SMA_SLOW)

        if fast is None or slow is None:
            continue

        golden_cross = fast > slow
        above_slow = price > slow
        in_trend = golden_cross and above_slow

        # Trend strength: how far above SMA-200 (used for ranking)
        trend_strength = (price - slow) / slow if slow > 0 else 0.0

        # 20-day momentum (used for ranking and breakout detection)
        momentum_20d = (closes[-1] - closes[-SMA_MEDIUM]) / closes[-SMA_MEDIUM] if len(closes) >= SMA_MEDIUM else 0.0

        # 20-day high for momentum breakout detection
        high_20d = max(closes[-SMA_MEDIUM:]) if len(closes) >= SMA_MEDIUM else price

        # 20-day low for short breakdown detection
        low_20d = min(closes[-SMA_MEDIUM:]) if len(closes) >= SMA_MEDIUM else price

        death_cross = fast < slow
        below_slow = price < slow

        currently_held_long = symbol in held_long_symbols
        currently_held_short = symbol in held_short_symbols

        if currently_held_long:
            # Check long exit conditions
            if not above_slow or not golden_cross:
                reason_parts = []
                if not above_slow:
                    reason_parts.append(f"price ${price:.2f} < SMA-200 ${slow:.2f}")
                if not golden_cross:
                    reason_parts.append(f"SMA-50 ${fast:.2f} < SMA-200 ${slow:.2f} (death cross)")
                signals.append({
                    "symbol": symbol,
                    "action": "sell",
                    "reason": "Exit signal: " + "; ".join(reason_parts),
                    "entry_price": f"{price:.2f}",
                    "stop_pct": DEFAULT_STOP_PCT,
                    "price": price,
                    "trend_strength": round(trend_strength, 4),
                    "momentum_20d": round(momentum_20d, 4),
                    "sma_50": round(fast, 2),
                    "sma_200": round(slow, 2),
                })
            else:
                signals.append({
                    "symbol": symbol,
                    "action": "hold",
                    "reason": f"Trend intact: price ${price:.2f} > SMA-200 ${slow:.2f}, SMA-50 ${fast:.2f} > SMA-200",
                    "entry_price": f"{price:.2f}",
                    "stop_pct": DEFAULT_STOP_PCT,
                    "price": price,
                    "trend_strength": round(trend_strength, 4),
                    "momentum_20d": round(momentum_20d, 4),
                    "sma_50": round(fast, 2),
                    "sma_200": round(slow, 2),
                })
        elif currently_held_short:
            # Check short exit conditions — cover when trend recovering
            if price > fast:
                signals.append({
                    "symbol": symbol,
                    "action": "cover",
                    "reason": f"Cover short: price ${price:.2f} > SMA-50 ${fast:.2f} (trend recovering)",
                    "entry_price": f"{price:.2f}",
                    "stop_pct": SHORT_STOP_PCT,
                    "price": price,
                    "trend_strength": round(trend_strength, 4),
                    "momentum_20d": round(momentum_20d, 4),
                    "sma_50": round(fast, 2),
                    "sma_200": round(slow, 2),
                })
            else:
                signals.append({
                    "symbol": symbol,
                    "action": "hold",
                    "reason": f"Short intact: price ${price:.2f} < SMA-50 ${fast:.2f}, holding short",
                    "entry_price": f"{price:.2f}",
                    "stop_pct": SHORT_STOP_PCT,
                    "price": price,
                    "trend_strength": round(trend_strength, 4),
                    "momentum_20d": round(momentum_20d, 4),
                    "sma_50": round(fast, 2),
                    "sma_200": round(slow, 2),
                })
        else:
            # Check long entry conditions
            # Signal 1: Golden cross (original trend entry)
            golden_cross_entry = in_trend and not crisis
            # Signal 2: Momentum breakout — price > 20-day high AND above SMA-50
            momentum_breakout = (price >= high_20d) and (price > fast) and not crisis

            if golden_cross_entry or momentum_breakout:
                if golden_cross_entry:
                    reason = (
                        f"Trend entry: price ${price:.2f} > SMA-200 ${slow:.2f} "
                        f"(+{trend_strength*100:.1f}%), SMA-50 ${fast:.2f} > SMA-200 (golden cross)"
                    )
                else:
                    reason = (
                        f"Momentum breakout: price ${price:.2f} >= 20d high ${high_20d:.2f}, "
                        f"above SMA-50 ${fast:.2f} (+{momentum_20d*100:.1f}% 20d return)"
                    )
                signals.append({
                    "symbol": symbol,
                    "action": "buy",
                    "reason": reason,
                    "entry_price": f"{price:.2f}",
                    "stop_pct": DEFAULT_STOP_PCT,
                    "price": price,
                    "trend_strength": round(trend_strength, 4),
                    "momentum_20d": round(momentum_20d, 4),
                    "sma_50": round(fast, 2),
                    "sma_200": round(slow, 2),
                })
            elif (in_trend or momentum_breakout) and crisis:
                signals.append({
                    "symbol": symbol,
                    "action": "hold",  # would be buy, but regime blocks it
                    "reason": f"CRISIS regime — no new entries despite trend signal for {symbol}",
                    "entry_price": f"{price:.2f}",
                    "stop_pct": DEFAULT_STOP_PCT,
                    "price": price,
                    "trend_strength": round(trend_strength, 4),
                    "momentum_20d": round(momentum_20d, 4),
                    "sma_50": round(fast, 2),
                    "sma_200": round(slow, 2),
                })

            # Check short entry conditions (mirror of long)
            # Signal 1: Death cross short — price < SMA-200 AND SMA-50 < SMA-200
            death_cross_short = below_slow and death_cross and not crisis
            # Signal 2: Momentum breakdown — price <= 20-day low AND price < SMA-50
            momentum_breakdown = (price <= low_20d) and (price < fast) and not crisis

            if death_cross_short or momentum_breakdown:
                if death_cross_short:
                    reason = (
                        f"Death cross short: price ${price:.2f} < SMA-200 ${slow:.2f}, "
                        f"SMA-50 ${fast:.2f} < SMA-200"
                    )
                else:
                    reason = (
                        f"Momentum breakdown: price ${price:.2f} <= 20d low ${low_20d:.2f}, "
                        f"below SMA-50 ${fast:.2f} ({momentum_20d*100:.1f}% 20d return)"
                    )
                signals.append({
                    "symbol": symbol,
                    "action": "short",
                    "reason": reason,
                    "entry_price": f"{price:.2f}",
                    "stop_pct": SHORT_STOP_PCT,
                    "price": price,
                    "trend_strength": round(trend_strength, 4),
                    "momentum_20d": round(momentum_20d, 4),
                    "sma_50": round(fast, 2),
                    "sma_200": round(slow, 2),
                })
            elif (death_cross_short or momentum_breakdown) and crisis:
                signals.append({
                    "symbol": symbol,
                    "action": "hold",  # would be short, but regime blocks it
                    "reason": f"CRISIS regime — no new shorts despite bearish signal for {symbol}",
                    "entry_price": f"{price:.2f}",
                    "stop_pct": SHORT_STOP_PCT,
                    "price": price,
                    "trend_strength": round(trend_strength, 4),
                    "momentum_20d": round(momentum_20d, 4),
                    "sma_50": round(fast, 2),
                    "sma_200": round(slow, 2),
                })

    return signals


def rank_and_cap(signals: list[dict], current_position_count: int) -> list[dict]:
    """
    Cap buy+short signals to keep total positions (longs + shorts) <= MAX_POSITIONS.
    Rank buys by momentum (highest first), shorts by momentum (lowest/most negative first).
    Sells/covers always pass through. Holds always pass through.
    """
    sells  = [s for s in signals if s["action"] == "sell"]
    covers = [s for s in signals if s["action"] == "cover"]
    holds  = [s for s in signals if s["action"] == "hold"]
    buys   = [s for s in signals if s["action"] == "buy"]
    shorts = [s for s in signals if s["action"] == "short"]

    # After sells/covers, how many slots remain
    positions_after_exits = current_position_count - len(sells) - len(covers)
    open_slots = max(0, MAX_POSITIONS - positions_after_exits)

    # Rank buys by 20-day momentum (fall back to trend_strength)
    buys.sort(key=lambda s: s.get("momentum_20d", s["trend_strength"]), reverse=True)
    # Rank shorts by momentum ascending (most negative = strongest short signal)
    shorts.sort(key=lambda s: s.get("momentum_20d", 0))

    # Interleave: fill slots with best buys and shorts, alternating priority to buys
    capped_buys = []
    capped_shorts = []
    buy_idx = 0
    short_idx = 0
    slots_used = 0

    # First fill buys, then shorts with remaining slots
    for b in buys:
        if slots_used >= open_slots:
            break
        capped_buys.append(b)
        slots_used += 1
        buy_idx += 1

    for s in shorts:
        if slots_used >= open_slots:
            break
        capped_shorts.append(s)
        slots_used += 1
        short_idx += 1

    # Mark excess buys as filtered
    filtered = []
    for b in buys[buy_idx:]:
        b = dict(b)
        b["action"] = "filtered"
        b["reason"] = f"Capped at {MAX_POSITIONS} positions — lower trend strength"
        filtered.append(b)

    for s in shorts[short_idx:]:
        s = dict(s)
        s["action"] = "filtered"
        s["reason"] = f"Capped at {MAX_POSITIONS} positions — lower short momentum"
        filtered.append(s)

    return sells + covers + holds + capped_buys + capped_shorts + filtered


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    print("=== Strategy Signal Generator — Trend-Following in Stocks ===")

    # Load regime from shared global state
    regime = "UNKNOWN"
    vix = None
    if os.path.exists("/tmp/shared_global_state.json"):
        try:
            ctx = json.load(open("/tmp/shared_global_state.json"))
            regime = ctx.get("regime") or "UNKNOWN"
            vix = ctx.get("vix")
        except Exception as e:
            print(f"Warning: could not read shared_global_state.json: {e}", file=sys.stderr)

    print(f"Regime: {regime} | VIX: {vix}")

    # Load current positions
    positions_held = []
    equity = 100000.0  # fallback
    current_position_count = 0

    if os.path.exists("/tmp/positions.json"):
        try:
            positions = json.load(open("/tmp/positions.json"))
            for p in positions:
                # Determine side from qty: negative qty = short position
                qty = float(p.get("qty", p.get("quantity", 0)))
                side = p.get("side", "long" if qty >= 0 else "short")
                positions_held.append({"symbol": p["symbol"], "side": side})
            current_position_count = len(positions)
            print(f"Current positions ({current_position_count}): {[(p['symbol'], p['side']) for p in positions_held]}")
        except Exception as e:
            print(f"Warning: could not read positions.json: {e}", file=sys.stderr)

    if os.path.exists("/tmp/account.json"):
        try:
            account = json.load(open("/tmp/account.json"))
            equity = float(account.get("equity", equity))
        except Exception as e:
            print(f"Warning: could not read account.json: {e}", file=sys.stderr)

    print(f"Equity: ${equity:,.0f}")
    print(f"Scanning {len(UNIVERSE)} symbols...")

    # Compute signals
    signals = compute_signals(positions_held, equity, regime)

    # Rank and cap buys
    signals = rank_and_cap(signals, current_position_count)

    # Compute position size for buys and shorts
    # In VOLATILE regime, halve the position size
    long_size_pct = POSITION_SIZE_PCT / 2 if regime.upper() == "VOLATILE" else POSITION_SIZE_PCT
    short_size_pct = SHORT_SIZE_PCT / 2 if regime.upper() == "VOLATILE" else SHORT_SIZE_PCT
    for s in signals:
        if s["action"] == "buy":
            notional = equity * (long_size_pct / 100)
            price = s["price"]
            qty = int(notional / price) if price > 0 else 0
            s["qty"] = qty
            s["notional"] = round(notional, 2)
        elif s["action"] == "short":
            notional = equity * (short_size_pct / 100)
            price = s["price"]
            qty = int(notional / price) if price > 0 else 0
            s["qty"] = qty
            s["notional"] = round(notional, 2)
        else:
            s["qty"] = None
            s["notional"] = None

    # Build summary
    buys     = [s for s in signals if s["action"] == "buy"]
    shorts   = [s for s in signals if s["action"] == "short"]
    sells    = [s for s in signals if s["action"] == "sell"]
    covers   = [s for s in signals if s["action"] == "cover"]
    holds    = [s for s in signals if s["action"] == "hold"]
    filtered = [s for s in signals if s["action"] == "filtered"]

    print(f"\nResults:")
    print(f"  BUY signals:      {len(buys)}")
    print(f"  SHORT signals:    {len(shorts)}")
    print(f"  SELL signals:     {len(sells)}")
    print(f"  COVER signals:    {len(covers)}")
    print(f"  HOLD signals:     {len(holds)}")
    print(f"  Filtered (capped): {len(filtered)}")

    if buys:
        print("\n  BUY:")
        for s in buys:
            print(f"    {s['symbol']:>6} @ ${s['entry_price']}  trend_strength={s['trend_strength']:.3f}  qty={s['qty']}")
    if shorts:
        print("\n  SHORT:")
        for s in shorts:
            print(f"    {s['symbol']:>6} @ ${s['entry_price']}  momentum={s['momentum_20d']:.3f}  qty={s['qty']}")
    if sells:
        print("\n  SELL:")
        for s in sells:
            print(f"    {s['symbol']:>6} @ ${s['entry_price']}  reason: {s['reason']}")
    if covers:
        print("\n  COVER:")
        for s in covers:
            print(f"    {s['symbol']:>6} @ ${s['entry_price']}  reason: {s['reason']}")

    # Output
    output = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "regime": regime,
        "vix": vix,
        "equity": equity,
        "position_size_pct": long_size_pct,
        "short_size_pct": short_size_pct,
        "max_positions": MAX_POSITIONS,
        "signals": signals,
        "summary": {
            "buy_count": len(buys),
            "short_count": len(shorts),
            "sell_count": len(sells),
            "cover_count": len(covers),
            "hold_count": len(holds),
            "filtered_count": len(filtered),
        },
    }

    with open("/tmp/strategy_signals.json", "w") as f:
        json.dump(output, f, indent=2)

    print(f"\nSaved to /tmp/strategy_signals.json")
    return output


if __name__ == "__main__":
    main()

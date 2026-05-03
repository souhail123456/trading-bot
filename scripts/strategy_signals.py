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
SMA_SLOW = 200
MAX_POSITIONS = 5
POSITION_SIZE_PCT = 20   # % of equity per position
DEFAULT_STOP_PCT = "10"  # trailing stop %

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
    positions_held: list[str],
    equity: float,
    regime: str,
) -> list[dict]:
    """
    For each symbol in UNIVERSE, compute entry/exit/hold signal.
    Returns list of signal dicts with action='buy'/'sell'/'hold'.
    """
    signals = []
    crisis = regime.upper() == "CRISIS"
    volatile = regime.upper() == "VOLATILE"

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

        currently_held = symbol in positions_held

        if currently_held:
            # Check exit conditions
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
                    "sma_50": round(fast, 2),
                    "sma_200": round(slow, 2),
                })
        else:
            # Check entry conditions
            if in_trend and not crisis:
                signals.append({
                    "symbol": symbol,
                    "action": "buy",
                    "reason": (
                        f"Trend entry: price ${price:.2f} > SMA-200 ${slow:.2f} "
                        f"(+{trend_strength*100:.1f}%), SMA-50 ${fast:.2f} > SMA-200 (golden cross)"
                    ),
                    "entry_price": f"{price:.2f}",
                    "stop_pct": DEFAULT_STOP_PCT,
                    "price": price,
                    "trend_strength": round(trend_strength, 4),
                    "sma_50": round(fast, 2),
                    "sma_200": round(slow, 2),
                })
            elif in_trend and crisis:
                signals.append({
                    "symbol": symbol,
                    "action": "hold",  # would be buy, but regime blocks it
                    "reason": f"CRISIS regime — no new entries despite trend signal for {symbol}",
                    "entry_price": f"{price:.2f}",
                    "stop_pct": DEFAULT_STOP_PCT,
                    "price": price,
                    "trend_strength": round(trend_strength, 4),
                    "sma_50": round(fast, 2),
                    "sma_200": round(slow, 2),
                })

    return signals


def rank_and_cap(signals: list[dict], current_position_count: int) -> list[dict]:
    """
    Cap buy signals to keep total positions <= MAX_POSITIONS.
    Rank by trend_strength (strongest trend first).
    Sells always pass through. Holds always pass through.
    """
    sells = [s for s in signals if s["action"] == "sell"]
    holds = [s for s in signals if s["action"] == "hold"]
    buys  = [s for s in signals if s["action"] == "buy"]

    # After sells, how many slots remain
    positions_after_sells = current_position_count - len(sells)
    open_slots = max(0, MAX_POSITIONS - positions_after_sells)

    # Rank buys by trend strength, pick top open_slots
    buys.sort(key=lambda s: s["trend_strength"], reverse=True)
    capped_buys = buys[:open_slots]

    # Mark excess buys as filtered
    filtered_buys = []
    for b in buys[open_slots:]:
        b = dict(b)
        b["action"] = "filtered"
        b["reason"] = f"Capped at {MAX_POSITIONS} positions — lower trend strength"
        filtered_buys.append(b)

    return sells + holds + capped_buys + filtered_buys


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
            regime = ctx.get("regime", "UNKNOWN")
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
            positions_held = [p["symbol"] for p in positions]
            current_position_count = len(positions)
            print(f"Current positions ({current_position_count}): {positions_held}")
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

    # Compute position size for buys
    # In VOLATILE regime, halve the position size
    size_pct = POSITION_SIZE_PCT / 2 if regime.upper() == "VOLATILE" else POSITION_SIZE_PCT
    for s in signals:
        if s["action"] == "buy":
            notional = equity * (size_pct / 100)
            price = s["price"]
            qty = int(notional / price) if price > 0 else 0
            s["qty"] = qty
            s["notional"] = round(notional, 2)
        else:
            s["qty"] = None
            s["notional"] = None

    # Build summary
    buys  = [s for s in signals if s["action"] == "buy"]
    sells = [s for s in signals if s["action"] == "sell"]
    holds = [s for s in signals if s["action"] == "hold"]
    filtered = [s for s in signals if s["action"] == "filtered"]

    print(f"\nResults:")
    print(f"  BUY signals:      {len(buys)}")
    print(f"  SELL signals:     {len(sells)}")
    print(f"  HOLD signals:     {len(holds)}")
    print(f"  Filtered (capped): {len(filtered)}")

    if buys:
        print("\n  BUY:")
        for s in buys:
            print(f"    {s['symbol']:>6} @ ${s['entry_price']}  trend_strength={s['trend_strength']:.3f}  qty={s['qty']}")
    if sells:
        print("\n  SELL:")
        for s in sells:
            print(f"    {s['symbol']:>6} @ ${s['entry_price']}  reason: {s['reason']}")

    # Output
    output = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "regime": regime,
        "vix": vix,
        "equity": equity,
        "position_size_pct": size_pct,
        "max_positions": MAX_POSITIONS,
        "signals": signals,
        "summary": {
            "buy_count": len(buys),
            "sell_count": len(sells),
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

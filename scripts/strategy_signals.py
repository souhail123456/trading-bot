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
MAX_POSITIONS = 5        # hard cap — was 7, caused over-deployment
POSITION_SIZE_PCT = 15   # % of equity per position
DEFAULT_STOP_PCT = "10"  # wider trailing stop — 7% caused churn (28% WR, 65 trades in 2.5mo)

# Anti-churn: block re-entry into a symbol for N days after a loss
REENTRY_COOLDOWN_DAYS = 10

# Sector failure tracking: exit sector after 2 consecutive failed trades
SECTOR_MAP = {
    "XLK": "tech", "AAPL": "tech", "MSFT": "tech", "GOOGL": "tech",
    "AMZN": "tech", "NVDA": "tech", "META": "tech", "TSLA": "tech",
    "XLF": "financials", "XLE": "energy", "XLV": "healthcare",
    "XLI": "industrials", "SPY": "broad", "QQQ": "broad", "IWM": "broad",
}

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


def fetch_daily_closes(symbol: str, days: int = 400) -> list[float]:
    """Return list of daily close prices, oldest first. Paginates to get all bars."""
    start = (datetime.now(timezone.utc) - timedelta(days=days + 30)).strftime("%Y-%m-%d")
    all_bars = []
    page_token = None

    for _ in range(5):  # max 5 pages (~1000 bars)
        params = {
            "timeframe": "1Day",
            "start": start,
            "limit": 1000,
            "adjustment": "split",
        }
        if page_token:
            params["page_token"] = page_token

        data = _alpaca_get(f"stocks/{symbol}/bars", params)
        if not data or "bars" not in data:
            break

        all_bars.extend(data["bars"])
        page_token = data.get("next_page_token")
        if not page_token:
            break

    closes = [bar["c"] for bar in all_bars if bar.get("c") is not None]
    return closes


def sma(closes: list[float], period: int) -> float | None:
    """Simple moving average of last `period` closes. None if insufficient data."""
    if len(closes) < period:
        return None
    return sum(closes[-period:]) / period


def load_recent_losses():
    """Load recent closed trades to enforce cooldown and sector failure rules.
    Returns (cooldown_symbols: set, failed_sectors: set).
    """
    import re
    cooldown_symbols = set()
    sector_losses = {}  # sector -> list of recent loss dates

    trade_log_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "memory", "TRADE-LOG.md")
    if not os.path.exists(trade_log_path):
        return cooldown_symbols, set()

    with open(trade_log_path) as f:
        content = f.read()

    m = re.search(r'closed_trades:\s*(\[.*?\])', content)
    if not m:
        return cooldown_symbols, set()

    try:
        closed = json.loads(m.group(1))
    except json.JSONDecodeError:
        return cooldown_symbols, set()

    now = datetime.now(timezone.utc)

    for t in closed:
        pnl = t.get("realized_pnl", 0)
        sym = t.get("symbol", "")
        date_str = t.get("date", "")
        if pnl >= 0 or not date_str:
            continue

        try:
            trade_date = datetime.strptime(date_str, "%Y-%m-%d").replace(tzinfo=timezone.utc)
        except ValueError:
            continue

        days_ago = (now - trade_date).days

        # Anti-churn cooldown
        if days_ago <= REENTRY_COOLDOWN_DAYS:
            cooldown_symbols.add(sym)

        # Sector failure tracking (last 30 days)
        if days_ago <= 30:
            sector = SECTOR_MAP.get(sym, "other")
            if sector not in sector_losses:
                sector_losses[sector] = []
            sector_losses[sector].append(date_str)

    # A sector is "failed" if it has 2+ consecutive losses in the last 30 days
    failed_sectors = set()
    for sector, dates in sector_losses.items():
        if len(dates) >= 2:
            failed_sectors.add(sector)

    return cooldown_symbols, failed_sectors


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
    positions_held: list of dicts with 'symbol', 'side', and optional 'entry_price' keys.
    Returns list of signal dicts with action='buy'/'sell'/'cover'/'hold'.
    """
    signals = []
    crisis = regime.upper() == "CRISIS"
    volatile = regime.upper() == "VOLATILE"

    # Anti-churn: load recent losses for cooldown and sector failure
    cooldown_symbols, failed_sectors = load_recent_losses()
    if cooldown_symbols:
        print(f"  Cooldown active ({REENTRY_COOLDOWN_DAYS}d): {', '.join(sorted(cooldown_symbols))}", file=sys.stderr)
    if failed_sectors:
        print(f"  Failed sectors (2+ losses in 30d): {', '.join(sorted(failed_sectors))}", file=sys.stderr)

    # Build lookup sets for held positions by side
    held_long_symbols = {p["symbol"] for p in positions_held if p.get("side") == "long"}
    held_short_symbols = {p["symbol"] for p in positions_held if p.get("side") == "short"}
    # Build entry price lookup for loss detection (key: symbol, value: float or None)
    entry_price_map = {
        p["symbol"]: float(p["entry_price"]) if p.get("entry_price") is not None else None
        for p in positions_held
    }

    for symbol in UNIVERSE:
        print(f"  Scanning {symbol}...", file=sys.stderr)
        closes = fetch_daily_closes(symbol, days=400)

        if len(closes) < SMA_SLOW + 1:
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
                # Time-based cut: if price < SMA-20 AND position is in loss → cut the drag
                med = sma(closes, SMA_MEDIUM)
                entry_px = entry_price_map.get(symbol)
                in_loss = (entry_px is not None and price < entry_px) or (entry_px is None and momentum_20d < 0)
                if med is not None and price < med and in_loss:
                    loss_desc = (
                        f"entry ${entry_px:.2f}" if entry_px is not None
                        else f"momentum {momentum_20d*100:.1f}%"
                    )
                    signals.append({
                        "symbol": symbol,
                        "action": "sell",
                        "reason": (
                            f"Time-based cut: price ${price:.2f} below SMA-20 ${med:.2f} "
                            f"while in loss ({loss_desc})"
                        ),
                        "entry_price": f"{price:.2f}",
                        "stop_pct": DEFAULT_STOP_PCT,
                        "price": price,
                        "trend_strength": round(trend_strength, 4),
                        "momentum_20d": round(momentum_20d, 4),
                        "sma_50": round(fast, 2),
                        "sma_200": round(slow, 2),
                        "sma_20": round(med, 2),
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
            # Short positions exist from before — force cover to unwind
            signals.append({
                "symbol": symbol,
                "action": "cover",
                "reason": f"Cover short: shorting disabled — unwinding legacy short position",
                "entry_price": f"{price:.2f}",
                "stop_pct": DEFAULT_STOP_PCT,
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

            # Anti-churn: skip if recently lost on this symbol
            if symbol in cooldown_symbols:
                if golden_cross_entry or momentum_breakout:
                    signals.append({
                        "symbol": symbol,
                        "action": "filtered",
                        "reason": f"Cooldown: lost on {symbol} within last {REENTRY_COOLDOWN_DAYS} days — skipping re-entry",
                        "entry_price": f"{price:.2f}",
                        "stop_pct": DEFAULT_STOP_PCT,
                        "price": price,
                        "trend_strength": round(trend_strength, 4),
                        "momentum_20d": round(momentum_20d, 4),
                        "sma_50": round(fast, 2),
                        "sma_200": round(slow, 2),
                    })
                continue

            # Sector failure: skip if sector has 2+ consecutive losses
            sym_sector = SECTOR_MAP.get(symbol, "other")
            if sym_sector in failed_sectors:
                if golden_cross_entry or momentum_breakout:
                    signals.append({
                        "symbol": symbol,
                        "action": "filtered",
                        "reason": f"Sector '{sym_sector}' has 2+ losses in 30 days — blocking new entries",
                        "entry_price": f"{price:.2f}",
                        "stop_pct": DEFAULT_STOP_PCT,
                        "price": price,
                        "trend_strength": round(trend_strength, 4),
                        "momentum_20d": round(momentum_20d, 4),
                        "sma_50": round(fast, 2),
                        "sma_200": round(slow, 2),
                    })
                continue

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

            # Shorting DISABLED — broken accounting, zero evidence of edge.
            # Short signals were causing ghost trades and margin blowouts.
            # If bearish, we simply don't enter. Existing shorts get covered above.

    return signals


def rank_and_cap(signals: list[dict], current_position_count: int) -> list[dict]:
    """
    Cap buy signals to keep total positions <= MAX_POSITIONS.
    Rank buys by momentum (highest first).
    Sells always pass through. Holds always pass through.
    """
    sells  = [s for s in signals if s["action"] == "sell"]
    holds  = [s for s in signals if s["action"] == "hold"]
    buys   = [s for s in signals if s["action"] == "buy"]

    # After sells, how many slots remain
    positions_after_exits = current_position_count - len(sells)
    open_slots = max(0, MAX_POSITIONS - positions_after_exits)

    # Rank buys by 20-day momentum (fall back to trend_strength)
    buys.sort(key=lambda s: s.get("momentum_20d", s["trend_strength"]), reverse=True)

    capped_buys = buys[:open_slots]

    # Mark excess buys as filtered
    filtered = []
    for b in buys[open_slots:]:
        b = dict(b)
        b["action"] = "filtered"
        b["reason"] = f"Capped at {MAX_POSITIONS} positions — lower trend strength"
        filtered.append(b)

    return sells + holds + capped_buys + filtered


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
                entry_px = p.get("avg_entry_price") or p.get("entry_price")
                positions_held.append({
                    "symbol": p["symbol"],
                    "side": side,
                    "entry_price": float(entry_px) if entry_px is not None else None,
                })
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

    # Compute position size for buys
    # In VOLATILE regime, halve the position size
    long_size_pct = POSITION_SIZE_PCT / 2 if regime.upper() == "VOLATILE" else POSITION_SIZE_PCT
    for s in signals:
        if s["action"] == "buy":
            notional = equity * (long_size_pct / 100)
            price = s["price"]
            qty = int(notional / price) if price > 0 else 0
            s["qty"] = qty
            s["notional"] = round(notional, 2)
        else:
            s["qty"] = None
            s["notional"] = None

    # Build summary
    buys     = [s for s in signals if s["action"] == "buy"]
    sells    = [s for s in signals if s["action"] == "sell"]
    holds    = [s for s in signals if s["action"] == "hold"]
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
        "position_size_pct": long_size_pct,
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

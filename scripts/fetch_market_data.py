#!/usr/bin/env python3
"""Fetch real market data from Yahoo Finance (no API key needed).
Outputs market context to /tmp/market_context.txt for LLM prompts."""
import json, urllib.request, sys
from datetime import datetime, timezone

def yf_quote(symbol):
    """Get latest quote from Yahoo Finance v8 API."""
    url = f"https://query1.finance.yahoo.com/v8/finance/chart/{symbol}?range=5d&interval=1d"
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    try:
        resp = urllib.request.urlopen(req, timeout=10)
        data = json.loads(resp.read())
        result = data["chart"]["result"][0]
        meta = result["meta"]
        closes = result["indicators"]["quote"][0]["close"]
        # Filter out None values
        valid_closes = [c for c in closes if c is not None]
        prev_close = valid_closes[-2] if len(valid_closes) >= 2 else valid_closes[-1]
        last_close = valid_closes[-1]
        change_pct = ((last_close - prev_close) / prev_close) * 100
        return {
            "symbol": symbol,
            "price": round(last_close, 2),
            "prev_close": round(prev_close, 2),
            "change_pct": round(change_pct, 2),
            "market_state": meta.get("marketState", "unknown"),
            "exchange_tz": meta.get("exchangeTimezoneName", "")
        }
    except Exception as e:
        return {"symbol": symbol, "error": str(e)}

# Core market indicators
tickers = {
    "^GSPC": "S&P 500",
    "^IXIC": "Nasdaq",
    "^DJI": "Dow Jones",
    "^VIX": "VIX",
    "CL=F": "WTI Oil",
    "BZ=F": "Brent Oil",
    "^TNX": "10Y Treasury Yield",
    "GC=F": "Gold",
    "DX-Y.NYB": "US Dollar Index",
}

# Sector ETFs for momentum
sectors = {
    "XLK": "Technology",
    "XLE": "Energy",
    "XLV": "Healthcare",
    "XLF": "Financials",
    "XLI": "Industrials",
    "XLB": "Materials",
    "XLC": "Communications",
    "XLY": "Consumer Disc.",
    "XLP": "Consumer Staples",
    "XLRE": "Real Estate",
    "XLU": "Utilities",
}

output = []
output.append(f"=== MARKET DATA (real-time via Yahoo Finance) ===")
output.append(f"Fetched: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}\n")

# Market indices
output.append("--- Indices & Commodities ---")
for sym, name in tickers.items():
    q = yf_quote(sym)
    if "error" in q:
        output.append(f"{name}: unavailable ({q['error'][:50]})")
    else:
        output.append(f"{name}: {q['price']} ({q['change_pct']:+.2f}%) [mkt: {q['market_state']}]")

# Sector performance
output.append("\n--- Sector ETFs (1-day change) ---")
sector_data = []
for sym, name in sectors.items():
    q = yf_quote(sym)
    if "error" not in q:
        sector_data.append((name, q["change_pct"], q["price"]))

# Sort by performance
sector_data.sort(key=lambda x: x[1], reverse=True)
for name, chg, price in sector_data:
    output.append(f"{name}: {chg:+.2f}% (${price})")

# Get quotes for held positions (read from positions file if available)
try:
    positions = json.load(open("/tmp/positions.json"))
    if positions:
        output.append("\n--- Held Positions (Yahoo) ---")
        for p in positions:
            sym = p["symbol"]
            q = yf_quote(sym)
            if "error" not in q:
                output.append(f"{sym}: ${q['price']} ({q['change_pct']:+.2f}%)")
except:
    pass

text = "\n".join(output)
with open("/tmp/market_context.txt", "w") as f:
    f.write(text)

print(text)

#!/usr/bin/env python3
"""
News Sentiment Gate — blocks entries on bearish symbols.

Fetches news for each symbol in the universe, asks Gemini to score
sentiment as bullish/neutral/bearish. Saves to /tmp/news_sentiment.json.

Used by strategy_signals.py to filter out buy signals on bearish names.
"""
import json
import os
import sys
import urllib.request
from xml.etree import ElementTree
from datetime import datetime, timezone


GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "")


def fetch_yahoo_news(symbol, max_items=5):
    """Fetch recent headlines from Yahoo Finance RSS."""
    url = f"https://feeds.finance.yahoo.com/rss/2.0/headline?s={symbol}&region=US&lang=en-US"
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    try:
        resp = urllib.request.urlopen(req, timeout=10)
        tree = ElementTree.parse(resp)
        items = []
        for item in tree.getroot().findall(".//item")[:max_items]:
            title = item.find("title")
            if title is not None and title.text:
                items.append(title.text.strip())
        return items
    except Exception as e:
        print(f"  News fetch failed for {symbol}: {e}", file=sys.stderr)
        return []


def score_sentiment_batch(symbol_headlines: dict) -> dict:
    """Use Gemini to score sentiment for multiple symbols at once.
    Returns dict of {symbol: {"score": -1/0/1, "reason": "..."}}
    -1 = bearish, 0 = neutral, 1 = bullish
    """
    if not GEMINI_API_KEY:
        print("  No GEMINI_API_KEY — skipping sentiment scoring", file=sys.stderr)
        return {}

    # Build a compact prompt with all symbols
    lines = []
    for sym, headlines in symbol_headlines.items():
        if headlines:
            lines.append(f"{sym}: {' | '.join(headlines[:3])}")
        else:
            lines.append(f"{sym}: (no recent news)")

    prompt = f"""Score the stock market sentiment for each symbol based on these recent news headlines.
For each symbol, respond with exactly: SYMBOL:SCORE:REASON
Where SCORE is: bullish, neutral, or bearish.
REASON is max 10 words explaining why.

Headlines:
{chr(10).join(lines)}

Rules:
- bearish = negative catalysts (earnings miss, downgrade, sector crash, lawsuit, regulatory risk)
- neutral = no strong signal either way, or mixed signals
- bullish = positive catalysts (beat earnings, upgrade, new product, strong guidance)
- If no news, score as neutral
- Be conservative: only score bearish if headlines are clearly negative

Respond ONLY with the scores, one per line, format: SYMBOL:SCORE:REASON"""

    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={GEMINI_API_KEY}"
    payload = json.dumps({
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {"maxOutputTokens": 500, "temperature": 0.1},
    }).encode()

    req = urllib.request.Request(url, data=payload, headers={
        "Content-Type": "application/json",
        "User-Agent": "trading-bot/1.0",
    })

    try:
        resp = urllib.request.urlopen(req, timeout=20)
        data = json.loads(resp.read())
        text = data["candidates"][0]["content"]["parts"][0]["text"]
    except Exception as e:
        print(f"  Gemini sentiment call failed: {e}", file=sys.stderr)
        return {}

    # Parse response
    results = {}
    score_map = {"bullish": 1, "neutral": 0, "bearish": -1}
    for line in text.strip().splitlines():
        parts = line.strip().split(":", 2)
        if len(parts) >= 2:
            sym = parts[0].strip().upper()
            score_str = parts[1].strip().lower()
            reason = parts[2].strip() if len(parts) > 2 else ""
            if score_str in score_map:
                results[sym] = {"score": score_map[score_str], "label": score_str, "reason": reason}

    return results


def main():
    from strategy_signals import UNIVERSE

    print("=== News Sentiment Gate ===")

    # Fetch headlines for all symbols
    symbol_headlines = {}
    for sym in UNIVERSE:
        headlines = fetch_yahoo_news(sym)
        symbol_headlines[sym] = headlines
        status = f"{len(headlines)} headlines" if headlines else "no news"
        print(f"  {sym}: {status}")

    # Also fetch broad market sentiment
    for idx_sym in ["^GSPC", "^VIX"]:
        headlines = fetch_yahoo_news(idx_sym)
        symbol_headlines[idx_sym] = headlines

    # Score all at once (single Gemini call)
    scores = score_sentiment_batch(symbol_headlines)

    if not scores:
        print("  Sentiment scoring unavailable — all symbols marked neutral")
        scores = {sym: {"score": 0, "label": "neutral", "reason": "no sentiment data"} for sym in UNIVERSE}

    # Print results
    bearish = []
    print("\nSentiment scores:")
    for sym in UNIVERSE:
        s = scores.get(sym, {"score": 0, "label": "neutral", "reason": "not scored"})
        emoji = "🟢" if s["score"] > 0 else "🔴" if s["score"] < 0 else "⚪"
        print(f"  {emoji} {sym:>5}: {s['label']:>8} — {s['reason']}")
        if s["score"] < 0:
            bearish.append(sym)

    if bearish:
        print(f"\n⚠️  BEARISH BLOCK: {', '.join(bearish)} — buy signals will be filtered")
    else:
        print("\n✅ No bearish blocks — all buy signals clear")

    # Save to /tmp for strategy_signals.py to read
    output = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "scores": scores,
        "bearish_symbols": bearish,
    }

    with open("/tmp/news_sentiment.json", "w") as f:
        json.dump(output, f, indent=2)

    print(f"Saved to /tmp/news_sentiment.json")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Fetch news headlines from Yahoo Finance RSS for held positions + watchlist.
Outputs to /tmp/market_news.txt for inclusion in LLM prompts. Free, no API key."""
import json, urllib.request, re, sys
from xml.etree import ElementTree
from datetime import datetime, timezone

def yf_news(symbol, max_items=3):
    """Fetch news from Yahoo Finance RSS feed for a ticker."""
    url = f"https://feeds.finance.yahoo.com/rss/2.0/headline?s={symbol}&region=US&lang=en-US"
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    try:
        resp = urllib.request.urlopen(req, timeout=10)
        tree = ElementTree.parse(resp)
        root = tree.getroot()
        items = []
        for item in root.findall(".//item")[:max_items]:
            title = item.find("title").text or ""
            pub_date = item.find("pubDate").text or ""
            # Clean up date to just day + time
            short_date = pub_date[:16] if pub_date else ""
            items.append({"title": title.strip(), "date": short_date})
        return items
    except Exception as e:
        return [{"title": f"(fetch error: {str(e)[:60]})", "date": ""}]


# Get held positions
held_symbols = []
try:
    positions = json.load(open("/tmp/positions.json"))
    held_symbols = [p["symbol"] for p in positions]
except:
    pass

# General market news
general_tickers = ["^GSPC", "^IXIC"]

# Combine: held positions + general market
all_tickers = held_symbols + general_tickers

output = []
output.append("=== NEWS HEADLINES (Yahoo Finance RSS) ===")
output.append(f"Fetched: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}\n")

for sym in all_tickers:
    label = sym.replace("^", "")
    output.append(f"--- {sym} ---")
    news = yf_news(sym)
    if not news:
        output.append("  No news found")
    for item in news:
        output.append(f"  [{item['date']}] {item['title']}")
    output.append("")

text = "\n".join(output)

with open("/tmp/market_news.txt", "w") as f:
    f.write(text)

print(text)

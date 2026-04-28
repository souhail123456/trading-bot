#!/usr/bin/env python3
"""Build the Groq prompt JSON for pre-market research."""
import json, os, sys
from datetime import datetime
sys.path.insert(0, os.path.dirname(__file__))
from prompt_utils import recent_trade_log, recent_research_log, compact_strategy

account = json.load(open("/tmp/account.json"))
positions = json.load(open("/tmp/positions.json"))
orders = json.load(open("/tmp/orders.json"))

with open("memory/TRADE-LOG.md") as f:
    trade_log = f.read()
with open("memory/RESEARCH-LOG.md") as f:
    research_log = f.read()
with open("memory/TRADING-STRATEGY.md") as f:
    strategy = f.read()

date = os.popen("date -u +%Y-%m-%d").read().strip()
day_of_week = os.popen("date -u +%A").read().strip()

# Read market context from web search results
market_context = ""
if os.path.exists("/tmp/market_context.txt"):
    with open("/tmp/market_context.txt") as f:
        market_context = f.read()

# Read news headlines
market_news = ""
if os.path.exists("/tmp/market_news.txt"):
    with open("/tmp/market_news.txt") as f:
        market_news = f.read()

system_msg = """You are an autonomous AI trading bot managing a paper ~$100,000 Alpaca account.
You produce pre-market research. Be ultra-concise: short bullets, no fluff.
Output EXACTLY two sections separated by ===TELEGRAM===:

SECTION 1: A RESEARCH-LOG entry (markdown, matching format below exactly)
SECTION 2: A Telegram message (plain text, <=15 lines, only if there's an actionable trade idea)

RESEARCH-LOG format:
## YYYY-MM-DD — Pre-market Research

### Account
- Equity: $X
- Cash: $X
- Buying power: $X
- Daytrade count: N

### Market Context
- WTI / Brent: ...
- S&P 500 futures: ...
- VIX: ...
- Today's catalysts: ...
- Earnings before open: ...
- Economic calendar: ...
- Sector momentum: ...

### Trade Ideas
1. TICKER — catalyst, entry $X, stop $X, target $X, R:R X:1
2. ...

### Risk Factors
- ...

### Decision
TRADE or HOLD (default HOLD if no edge)

---"""

user_msg = f"""Date: {date} ({day_of_week})

=== ACCOUNT DATA ===
{json.dumps(account, indent=2)}

=== POSITIONS ===
{json.dumps(positions, indent=2)}

=== OPEN ORDERS ===
{json.dumps(orders, indent=2)}

=== MARKET CONTEXT (from web search) ===
{market_context}

=== NEWS HEADLINES (positions + market) ===
{market_news}

=== RECENT TRADE LOG (tail) ===
{recent_trade_log(trade_log, 800)}

=== RECENT RESEARCH LOG (tail) ===
{recent_research_log(research_log, 800)}

=== STRATEGY RULES ===
{compact_strategy(strategy)}

Produce pre-market research now. Key rules:
- Default to HOLD unless there's a clear edge
- Max 3 trades per week (check trade log for this week's count)
- Max 5-6 positions, max 20% per position
- Every trade idea needs: specific catalyst, entry, stop (7-10% below), target (min 2:1 R:R)
- Follow sector momentum
- Patience > activity"""

payload = {
    "model": "llama-3.3-70b-versatile",
    "messages": [
        {"role": "system", "content": system_msg},
        {"role": "user", "content": user_msg}
    ],
    "max_tokens": 1200,
    "temperature": 0.3
}

with open("/tmp/prompt.json", "w") as f:
    json.dump(payload, f)
print("Pre-market prompt built")

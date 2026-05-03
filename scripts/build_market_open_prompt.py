#!/usr/bin/env python3
"""Build the Groq prompt JSON for market-open execution."""
import json, os, sys
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

# Read quotes if available
quotes = ""
if os.path.exists("/tmp/quotes.txt"):
    with open("/tmp/quotes.txt") as f:
        quotes = f.read()

# Read news headlines
market_news = ""
if os.path.exists("/tmp/market_news.txt"):
    with open("/tmp/market_news.txt") as f:
        market_news = f.read()

# Read shared context from trading-admin (regime, risk)
shared_context = {}
if os.path.exists("/tmp/shared_global_state.json"):
    with open("/tmp/shared_global_state.json") as f:
        shared_context = json.load(f)

date = os.popen("date -u +%Y-%m-%d").read().strip()

system_msg = """You are an autonomous AI trading bot managing a paper ~$100,000 Alpaca account.
You run the market-open execution workflow. Be ultra-concise.

You MUST output a JSON action plan, then ===TELEGRAM=== separator, then a Telegram message.

ACTION PLAN FORMAT (valid JSON):
{
  "action": "HOLD" or "TRADE",
  "reason": "one line",
  "trades": [
    {
      "symbol": "SYM",
      "qty": "N",
      "side": "buy",
      "catalyst": "one line",
      "entry_price": "X.XX",
      "stop_pct": "10",
      "target": "X.XX"
    }
  ],
  "trade_log_entry": "markdown entry for TRADE-LOG"
}

If action is HOLD, trades array should be empty.

===TELEGRAM===
<message if trade placed, or "No trades at open — holding" if HOLD>

CRITICAL RULES — skip any trade that fails these:
- Total positions after trade <= 6
- Trades this week <= 3
- Position cost <= 20% of equity
- Catalyst documented in today's RESEARCH-LOG
- daytrade_count < 3

MARKET REGIME RULES (from trading-admin):
- If regime is CRISIS: NO new entries. Only hold or cut.
- If regime is VOLATILE: halve position sizes (max 10% of equity per trade).
- If regime is RANGING: default rules apply.
- If regime is TRENDING: normal trading, follow momentum."""

user_msg = f"""Date: {date}

=== ACCOUNT ===
{json.dumps(account, indent=2)}

=== POSITIONS ===
{json.dumps(positions, indent=2)}

=== OPEN ORDERS ===
{json.dumps(orders, indent=2)}

=== LIVE QUOTES ===
{quotes}

=== NEWS HEADLINES ===
{market_news}

=== TODAY'S RESEARCH LOG ===
{recent_research_log(research_log, 1200)}

=== RECENT TRADE LOG ===
{recent_trade_log(trade_log, 800)}

=== STRATEGY ===
{compact_strategy(strategy)}

=== MARKET REGIME (from trading-admin) ===
Regime: {shared_context.get('regime', 'UNKNOWN')}
VIX: {shared_context.get('vix', 'N/A')}
Recommendations: {json.dumps(shared_context.get('recommendations', {}), indent=2) if shared_context.get('recommendations') else 'N/A'}

Decide: execute trades from today's research, or HOLD. Default HOLD unless thesis is confirmed by live data. RESPECT the regime rules above."""

payload = {
    "model": "llama-3.3-70b-versatile",
    "messages": [
        {"role": "system", "content": system_msg},
        {"role": "user", "content": user_msg}
    ],
    "max_tokens": 1500,
    "temperature": 0.2
}

with open("/tmp/prompt.json", "w") as f:
    json.dump(payload, f)
print("Market-open prompt built")

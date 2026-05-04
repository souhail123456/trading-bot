#!/usr/bin/env python3
"""Build the Groq prompt JSON for market-open execution."""
import json, os, sys, subprocess
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

# ---------------------------------------------------------------------------
# Run strategy signal generator
# ---------------------------------------------------------------------------
script_dir = os.path.dirname(os.path.abspath(__file__))
print("Running strategy_signals.py...")
result = subprocess.run(
    [sys.executable, os.path.join(script_dir, "strategy_signals.py")],
    capture_output=True, text=True
)
if result.returncode != 0:
    print(f"strategy_signals.py stderr:\n{result.stderr}", file=sys.stderr)
else:
    print(result.stdout)

# Load signals
strategy_signals = {}
if os.path.exists("/tmp/strategy_signals.json"):
    with open("/tmp/strategy_signals.json") as f:
        strategy_signals = json.load(f)

# Build a compact, LLM-readable summary of signals
def format_signals_for_prompt(ss: dict) -> str:
    if not ss or not ss.get("signals"):
        return "No strategy signals available — HOLD all positions."

    lines = []
    lines.append(f"Strategy: Trend-Following in Stocks (SMA-50/SMA-200 golden cross)")
    lines.append(f"Generated: {ss.get('generated_at', 'N/A')}")
    lines.append(f"Regime: {ss.get('regime', 'UNKNOWN')} | VIX: {ss.get('vix', 'N/A')}")
    lines.append(f"Position size: {ss.get('position_size_pct', 20)}% of equity | Max positions: {ss.get('max_positions', 5)}")
    lines.append("")

    buys   = [s for s in ss["signals"] if s["action"] == "buy"]
    shorts = [s for s in ss["signals"] if s["action"] == "short"]
    sells  = [s for s in ss["signals"] if s["action"] == "sell"]
    covers = [s for s in ss["signals"] if s["action"] == "cover"]
    holds  = [s for s in ss["signals"] if s["action"] == "hold"]

    if buys:
        lines.append("BUY SIGNALS (MANDATORY entries — do NOT skip without CRISIS regime):")
        for s in buys:
            lines.append(
                f"  BUY {s['symbol']} @ ~${s['entry_price']}  "
                f"qty={s['qty']}  stop={s['stop_pct']}%  "
                f"reason: {s['reason']}"
            )
    else:
        lines.append("BUY SIGNALS: None — no new entries today.")

    if shorts:
        lines.append("")
        lines.append("SHORT SIGNALS (entries — sell short with specified qty and stop_pct):")
        for s in shorts:
            lines.append(
                f"  SHORT {s['symbol']} @ ~${s['entry_price']}  "
                f"qty={s['qty']}  stop={s['stop_pct']}%  "
                f"reason: {s['reason']}"
            )

    if sells:
        lines.append("")
        lines.append("SELL SIGNALS (MANDATORY exits — close these positions NOW):")
        for s in sells:
            lines.append(f"  SELL {s['symbol']}  reason: {s['reason']}")

    if covers:
        lines.append("")
        lines.append("COVER SIGNALS (MANDATORY — buy to cover these short positions NOW):")
        for s in covers:
            lines.append(f"  COVER {s['symbol']}  reason: {s['reason']}")

    if holds:
        lines.append("")
        lines.append("HOLD (no action — trend intact):")
        for s in holds:
            lines.append(f"  HOLD {s['symbol']} @ ${s['entry_price']}  {s['reason']}")

    return "\n".join(lines)

signals_text = format_signals_for_prompt(strategy_signals)

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
      "side": "buy" or "sell",
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
- Total positions after trade <= 8
- Trades this week <= 5
- Position cost <= 15% of equity
- daytrade_count < 3

STRATEGY SIGNAL RULES (HIGHEST PRIORITY — override everything else):
- You MUST follow the strategy signals in === STRATEGY SIGNALS ===.
- BUY signals: these are mandatory entries. Place the trade with the specified qty and stop_pct.
- SHORT signals: these are short-sell entries. Place the trade with side='sell' and specified qty and stop_pct.
- SELL signals: these are mandatory exits. Close these long positions immediately.
- COVER signals: these mean buy-to-cover to exit a short position. Place with side='buy'.
- You MAY NOT make discretionary picks outside the signal list.
- You MAY NOT buy a symbol that does not appear in the BUY SIGNALS list.
- The only reason to skip a BUY signal is: (1) regime is CRISIS, (2) position already held, (3) would exceed 8 total positions, (4) insufficient cash.
- If there are no BUY signals, action is HOLD (no new entries).

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

=== STRATEGY SIGNALS (MANDATORY — follow these exactly) ===
{signals_text}

=== RECENT TRADE LOG ===
{recent_trade_log(trade_log, 600)}

=== STRATEGY RULES ===
{compact_strategy(strategy)}

=== MARKET REGIME (from trading-admin) ===
Regime: {shared_context.get('regime', 'UNKNOWN')}
VIX: {shared_context.get('vix', 'N/A')}
Recommendations: {json.dumps(shared_context.get('recommendations', {}), indent=2) if shared_context.get('recommendations') else 'N/A'}

INSTRUCTIONS: Execute ONLY the trades listed in STRATEGY SIGNALS above. Do not add discretionary picks. If there are BUY signals and conditions are met, action is TRADE. Otherwise HOLD. RESPECT regime rules."""

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

#!/usr/bin/env python3
"""Build the Groq prompt JSON for midday scan."""
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

date = os.popen("date -u +%Y-%m-%d").read().strip()

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
# Run strategy signal generator (reuse if already run, else regenerate)
# ---------------------------------------------------------------------------
strategy_signals = {}
if os.path.exists("/tmp/strategy_signals.json"):
    try:
        strategy_signals = json.load(open("/tmp/strategy_signals.json"))
        print("Reusing strategy signals from market-open run.")
    except Exception:
        pass

if not strategy_signals:
    script_dir = os.path.dirname(os.path.abspath(__file__))
    print("Running strategy_signals.py for midday scan...")
    result = subprocess.run(
        [sys.executable, os.path.join(script_dir, "strategy_signals.py")],
        capture_output=True, text=True
    )
    if result.returncode != 0:
        print(f"strategy_signals.py stderr:\n{result.stderr}", file=sys.stderr)
    if os.path.exists("/tmp/strategy_signals.json"):
        strategy_signals = json.load(open("/tmp/strategy_signals.json"))

# Build exit signal summary for midday
def format_exit_signals(ss: dict) -> str:
    if not ss or not ss.get("signals"):
        return "No strategy exit signals — check P&L rules only."

    sells = [s for s in ss["signals"] if s["action"] == "sell"]
    holds = [s for s in ss["signals"] if s["action"] == "hold"]

    lines = []
    lines.append(f"Strategy: Trend-Following in Stocks | Regime: {ss.get('regime', 'UNKNOWN')}")

    if sells:
        lines.append("")
        lines.append("STRATEGY EXIT SIGNALS (MANDATORY — close these positions):")
        for s in sells:
            lines.append(f"  EXIT {s['symbol']}  reason: {s['reason']}")
    else:
        lines.append("STRATEGY EXIT SIGNALS: None — all trends intact.")

    if holds:
        lines.append("")
        lines.append("Trend still intact (do not cut unless P&L rule triggers):")
        for s in holds:
            lines.append(f"  {s['symbol']} trend OK — price ${s['entry_price']}, SMA-50 ${s['sma_50']}, SMA-200 ${s['sma_200']}")

    return "\n".join(lines)

exit_signals_text = format_exit_signals(strategy_signals)

system_msg = """You are an autonomous AI trading bot managing a paper ~$100,000 Alpaca account.
You run the midday scan — cut losers, tighten stops, enforce strategy exits. Be ultra-concise.

Output a JSON action plan, then ===TELEGRAM===, then a Telegram message (only if action taken).

ACTION PLAN FORMAT (valid JSON):
{
  "cuts": [
    {"symbol": "SYM", "reason": "-4% rule or strategy exit or thesis broken", "unrealized_plpc": "-0.05"}
  ],
  "stop_tightens": [
    {"symbol": "SYM", "old_trail": "7", "new_trail": "5", "reason": "up 10%+", "cancel_order_id": "xxx"}
  ],
  "partial_takes": [
    {"symbol": "SYM", "sell_qty": "N", "reason": "+8% partial take", "unrealized_plpc": "0.09"}
  ],
  "thesis_checks": [
    {"symbol": "SYM", "status": "intact or broken", "notes": "..."}
  ],
  "trade_log_entry": "markdown to append if any action taken, or empty string"
}

===TELEGRAM===
<action summary or "Midday scan — no action needed">

CRITICAL — CUTS ARRAY IS THE ONLY WAY TO CLOSE A POSITION:
- Writing "Cut X" in trade_log_entry does NOTHING. Only the "cuts" array triggers actual sell orders.
- If you decide to close ANY position for ANY reason, it MUST go in the "cuts" array.
- If thesis_checks.status is "broken", you MUST ALSO add that symbol to "cuts".
- NEVER mention cutting/closing a position in trade_log_entry without ALSO adding it to "cuts".
- "partial_takes" array sells ONLY the specified sell_qty — it does NOT close the full position.

STRATEGY EXIT RULES (HIGHEST PRIORITY):
- If a symbol appears in STRATEGY EXIT SIGNALS, you MUST add it to cuts immediately.
- Strategy exits override the -4% threshold — exit regardless of P&L.
- Reason: price broke below SMA-200 or death cross (SMA-50 crossed below SMA-200).

PROFIT-TAKING RULES (lock gains via partial exits):
- If unrealized_plpc >= +0.08 (up 8%+): sell HALF the shares (round down), tighten remaining stop to 5%. Add to "partial_takes".
- If unrealized_plpc >= +0.12 (up 12%+): close the FULL remaining position. Add to "cuts" with reason "profit target +12%".
- partial_takes triggers a market sell for sell_qty shares only (not the full position).
- After partial take, the remaining shares keep their trailing stop (tightened to 5%).

P&L RULES (apply after strategy exit check):
- Cut any position with unrealized_plpc <= -0.04 → add to "cuts"
- Cut if thesis is broken even if not at -4% → add to "cuts"
- Tighten trail to 5% at +10%, to 3% at +15%
- Cut any position that has been held for 5+ trading days and is in the red
- Never tighten within 3% of current price
- Never move a stop down

CASH GUARD:
- Never let cash go below $0. Never deploy more than 95% of equity.
- The execution script will reject any sell that exceeds held shares (no accidental shorts).

MARKET REGIME (from trading-admin):
- If regime is CRISIS: tighten ALL stops to 5%, cut any position below -2%.
- If regime is VOLATILE: tighten stops to 5% on all positions.
- If regime is RANGING/TRENDING: follow normal rules above."""

pos_lines = []
for p in positions:
    pos_lines.append(
        f"{p['symbol']}: {p['qty']}sh @ ${p['avg_entry_price']} | "
        f"P&L: ${p.get('unrealized_pl','?')} ({p.get('unrealized_plpc','?')})"
    )

order_lines = []
for o in orders[:12]:
    order_lines.append(f"{o['symbol']}: {o['type']} {o['side']} {o['qty']}sh")

user_msg = f"""Date: {date}

=== ACCOUNT ===
Equity: ${account.get('equity', '?')} | Cash: ${account.get('cash', '?')} | Buying Power: ${account.get('buying_power', '?')} | Daytrades: {account.get('daytrade_count', '?')}

=== POSITIONS ({len(positions)}) ===
{chr(10).join(pos_lines)}

=== OPEN ORDERS ({len(orders)}) ===
{chr(10).join(order_lines)}

=== STRATEGY EXIT SIGNALS (check these FIRST) ===
{exit_signals_text}

=== RECENT TRADE LOG ===
{recent_trade_log(trade_log, 400)}

=== NEWS HEADLINES ===
{chr(10).join(market_news.strip().splitlines()[:10]) if market_news else 'None'}

=== STRATEGY RULES ===
{compact_strategy(strategy, 800)}

=== MARKET REGIME (from trading-admin) ===
Regime: {shared_context.get('regime', 'UNKNOWN')}
VIX: {shared_context.get('vix', 'N/A')}

Run the midday scan. First: enforce strategy exit signals. Then: check profit targets (+8% partial, +12% full close). Then: check P&L vs -4% cut rule and stop tightening. RESPECT regime rules."""

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
print("Midday prompt built")

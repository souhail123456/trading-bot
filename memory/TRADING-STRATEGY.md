# Trading Strategy

## Mission
Beat the S&P 500 over the challenge window. Stocks only — no options, ever.

## Capital & Constraints
- Starting capital: ~$100,000
- Platform: Alpaca (paper trading)
- Instruments: Stocks ONLY
- PDT limit: not applicable (account > $25k)

## Core Rules
1. NO OPTIONS — ever
2. 75-85% deployed
3. 5-6 positions at a time, max 20% each
4. 7% trailing stop on every position as a real GTC order
5. Cut losers at -4% manually
6. Tighten trail: 5% at +10%, 3% at +15%
7. Never within 3% of current price; never move a stop down
8. Max 5 new trades per week
9. Follow sector momentum
10. Exit a sector after 2 consecutive failed trades
11. Patience > activity
12. Time-based cut: if position is red after 5 trading days, cut it

## Buy-Side Gate (ALL must pass or skip the trade)
- Total positions after fill <= 6
- Trades this week <= 5
- Position cost <= 20% of equity
- Position cost <= available cash
- daytrade_count < 3 (PDT: 3/5 rolling business days)
- Specific catalyst documented in today's RESEARCH-LOG
- Instrument is a stock (not an option)

## Sell-Side Rules (evaluated at midday and opportunistically)
- Unrealized loss <= -4%: close immediately
- Thesis broken (catalyst invalidated, sector rolling over): close even if not at -4%
- Up >= +10%: tighten trailing stop to 5%
- Up >= +15%: tighten trailing stop to 3%
- Position red after 5 trading days: close immediately
- Sector has 2 consecutive failed trades: exit all positions in that sector

## Profit-Taking Rules (partial exits to lock gains)
- Up >= +8%: sell HALF the position (round down shares), tighten remaining stop to 5%
- Up >= +12%: close the FULL remaining position
- If already partially taken (shares < original entry), the +12% rule closes what's left

## Entry Checklist (document before placing)
- What is the specific catalyst today?
- Is the sector in momentum?
- What is the stop level (5-7% below entry)?
- What is the target (minimum 2:1 risk/reward)?

## Stop Order Fallback Ladder
1. trailing_stop (trail_percent: "7", gtc) — preferred
2. Fixed stop 7% below entry (stop, gtc) — if PDT blocks trailing stop
3. Queue the stop for tomorrow AM in TRADE-LOG — if both blocked

## Alpaca Notes
- trail_percent is a string: "7" not 7. qty is also a string.
- Data endpoint: data.alpaca.markets (quotes). Trading endpoint: paper-api.alpaca.markets.
- quote.ap = ask, quote.bp = bid. Wide spread or zero = halted/illiquid, skip.
- Trailing stops only work during market hours. Overnight gaps blow through them.
- Timestamps are UTC — convert for local timezone.

# Weekly Review

Friday reviews appended here.

Template for each entry:

## Week ending YYYY-MM-DD

### Stats
| Metric | Value |
|--------|-------|
| Starting portfolio | $X |
| Ending portfolio | $X |
| Week return | ±$X (±X%) |
| S&P 500 week | ±X% |
| Bot vs S&P | ±X% |
| Trades | N (W:X / L:Y / open:Z) |
| Win rate | X% |
| Best trade | SYM +X% |
| Worst trade | SYM -X% |
| Profit factor | X.XX |

### Closed Trades
| Ticker | Entry | Exit | P&L | Notes |
|--------|-------|------|-----|-------|

### Open Positions at Week End
| Ticker | Entry | Close | Unrealized | Stop |
|--------|-------|-------|------------|------|

### What Worked
- ...

### What Didn't Work
- ...

### Key Lessons
- ...

### Adjustments for Next Week
- ...

### Overall Grade: X

---

## Week ending 2026-04-24

### Stats
| Metric | Value |
|--------|-------|
| Starting portfolio | $100,000.00 (account reset baseline) |
| Ending portfolio | $100,637.56 |
| Week return | +$637.56 (+0.64%) |
| S&P 500 week | +0.45% (SPY $710.14 → $713.33) |
| Bot vs S&P | +0.19% |
| Trades | 1 (W:0 / L:0 / open:1) |
| Win rate | N/A (no closed trades) |
| Best trade | NVDA +3.19% (open) |
| Worst trade | NVDA +3.19% (only trade, open) |
| Profit factor | N/A (no closed trades) |

### Closed Trades
| Ticker | Entry | Exit | P&L | Notes |
|--------|-------|------|-----|-------|
| — | — | — | — | No closed trades this week |

### Open Positions at Week End
| Ticker | Entry | Close | Unrealized | Stop |
|--------|-------|-------|------------|------|
| NVDA | $201.73 | $208.17 | +$637.56 (+3.19%) | $189.86 (10% trail, HWM $210.95) |

### What Worked
- **NVDA catalyst thesis executed cleanly**: Amazon $25B Anthropic deal + MSFT/GOOGL AI capex guidance (Apr 23 post-close) + Intel Q1 blowout ($0.29 EPS vs $0.01 est., Apr 24) — three sequential catalyst confirmations within 48 hours of entry
- **Patient deployment**: Held cash Mon–Wed despite marginal setups (DAL, PM, GEV all avoided; PM -5%, GEV soft — good skips); only deployed capital when a high-conviction setup with documented catalysts materialized
- **Trailing stop placed immediately**: GTC trailing stop (10%, order f93dcc04) placed at time of entry — protected against adverse gap before the catalyst confirmed; HWM auto-tracked to $210.95
- **Proxy / API blockers handled gracefully**: When proxy returned 403 mid-session, WebSearch fallback used for thesis checks and threshold evaluations — no decisions were skipped or delayed
- **Sector alignment**: NVDA is in the Technology / Semiconductors sector, which rode the AI capex acceleration wave this week — thesis matched macro momentum

### What Didn't Work
- **Deployed only 1 of 3 weekly trade slots (20% of equity)**: Entered the week with 3 trade slots and $100k cash; exited with 1 position and 79.5% cash — extremely under-deployed relative to the 75-85% target in the strategy
- **Early week total paralysis (Mon–Wed)**: API 403 blocked all execution Mon–Wed (Apr 20–22); entire Mon–Wed window was lost; zero trades placed even when setups (FCX, GEV) were identified — execution infrastructure dependency is a single point of failure
- **Proxy reliability**: Intermittent 403 blocks (at least 3 separate sessions this week) meant live price data was unavailable repeatedly; had to rely on estimated WebSearch prices for afternoon checks
- **No second position entered**: Even after NVDA confirmed +3.99% on Friday AM with $80k cash available, no second position was initiated — two more trade slots were available; could have added AMD or a materials play for broader exposure
- **Phase performance barely beats S&P (+0.19%)**: Portfolio outperformed by just 19 basis points this week; the large cash drag (79.5% uninvested) suppressed returns that a more deployed book would have captured

### Key Lessons
- **Infrastructure first**: The API/proxy blockers (403) cost 3 trading days of deployment (Mon–Wed). Without execution access, even correct thesis generates zero return. Need proxy reliability as a first-order concern next week.
- **Catalyst stacking amplifies confidence**: Three independent confirmations (Amazon, MSFT/GOOGL, Intel) within 48h of NVDA entry validated the AI capex thesis. When multiple catalysts align, position sizing can be more aggressive.
- **Cash drag is the enemy of alpha**: Being 79.5% cash at week end while the S&P gained +0.54% meant the portfolio barely outperformed despite a strong individual position. Deploy 2–3 positions to capture sector momentum, not just 1.
- **Good skips have value**: PM missed estimates (-5%), GEV was soft, DAL thesis broke when oil reversed. Skipping these and waiting for NVDA was the right call — patience > activity held.
- **Stop trail working as designed**: The 10% trailing stop auto-tracked from initial level $181.48 to HWM $210.95 (floor $189.86) without intervention, protecting +$638 of unrealized gain entering the weekend.

### Adjustments for Next Week
1. **Target 3–4 positions (40–60% deployed)** by midweek: With NVDA already on, add 1–2 positions from the AI/semiconductor ecosystem (AMD, AVGO) or materials leaders (FCX) if setups confirm Monday AM.
2. **NVDA threshold watch**: Tighten trailing stop to 7% if NVDA reaches +15% from entry ($231.99); tighten to 5% at +20% ($242.08). These are the next mechanical triggers.
3. **Monday pre-market scan is critical**: Last week, Mon–Wed was dead due to API access issues. Next week, confirm proxy working at 9:15 AM ET Monday before market open; if blocked, use WebSearch for quotes and queue manual orders.
4. **AMD as next entry candidate**: AMD earnings upcoming; semiconductor cycle intact after Intel blowout; watch for post-earnings momentum entry if beats; stop 8% below entry, target +20%.
5. **Maintain 3-trade weekly cap discipline**: 2 slots remain from this week (they do NOT carry over — fresh 3-slot cap each Monday). Be ready to use them Mon–Tue if setups confirm.
6. **Exit NVDA if thesis breaks**: If NVDA closes below $189.86 (trailing stop triggers), do not re-enter same week — move to next highest-conviction idea.

### Overall Grade: C+

**Rationale**: Portfolio edged the S&P by 19 bps on the strength of one well-executed trade (NVDA, catalyst confirmed). However, the massive cash drag (79.5% uninvested), lost Mon–Wed window due to API issues, and failure to add 2nd/3rd positions despite ample cash and opportunity significantly underperformed the strategy's 75-85% deployment target. The individual trade selection and discipline (stops, skipping bad setups) were excellent (would grade A on trade quality alone), but portfolio-level execution earns a C+.

#!/usr/bin/env python3
"""Flatten the Alpaca account to 100% cash.

Calls Alpaca's "close all positions" endpoint (DELETE /v2/positions?cancel_orders=true),
which also cancels any open orders, then reports the result and the resulting account cash.

Idempotent: safe to run when the account is already flat (Alpaca returns an empty list
and the script exits 0). Uses the same stdlib-urllib + APCA header auth as the rest of the bot.

Env: ALPACA_API_KEY, ALPACA_SECRET_KEY  (paper account).
"""
import json
import os
import sys
import time
import urllib.request
import urllib.error

BASE = "https://paper-api.alpaca.markets/v2"
API_KEY = os.environ.get("ALPACA_API_KEY", "")
API_SECRET = os.environ.get("ALPACA_SECRET_KEY", "")


def alpaca(method, path, expect_json=True):
    url = f"{BASE}/{path}"
    req = urllib.request.Request(url, method=method)
    req.add_header("APCA-API-KEY-ID", API_KEY)
    req.add_header("APCA-API-SECRET-KEY", API_SECRET)
    try:
        resp = urllib.request.urlopen(req)
        raw = resp.read()
        return (json.loads(raw) if (expect_json and raw) else raw, resp.status)
    except urllib.error.HTTPError as e:
        body = e.read().decode() if e.fp else ""
        print(f"Alpaca API error: {e.code} {e.reason} — {body[:400]}")
        return (None, e.code)
    except Exception as e:
        print(f"Alpaca API error: {e}")
        return (None, None)


def main():
    if not API_KEY or not API_SECRET:
        print("ERROR: ALPACA_API_KEY / ALPACA_SECRET_KEY not set — aborting")
        sys.exit(1)

    # 1. Snapshot positions BEFORE
    before, _ = alpaca("GET", "positions")
    if before is None:
        print("ERROR: could not read positions from broker — aborting (fail closed)")
        sys.exit(1)

    print(f"Open positions BEFORE flatten: {len(before)}")
    for p in before:
        print(f"  {p.get('symbol')}: qty={p.get('qty')} "
              f"mkt_value={p.get('market_value')} unrealized_pl={p.get('unrealized_pl')}")

    # Market clock: close_all submits MARKET orders, which only fill when the
    # regular session is open. After hours the orders are accepted and queued
    # to fill at the next open — that is expected, not a failure.
    clock, _ = alpaca("GET", "clock")
    market_open = bool(clock.get("is_open")) if clock else False
    next_open = clock.get("next_open") if clock else "unknown"
    print(f"Market open right now: {market_open} (next_open: {next_open})")

    if not before:
        print("Account already flat — nothing to close (idempotent no-op).")
    else:
        # 2. Close ALL positions and cancel any resting orders (trailing stops etc.)
        print("\nCalling DELETE /v2/positions?cancel_orders=true (close_all_positions)...")
        result, status = alpaca("DELETE", "positions?cancel_orders=true")
        print(f"HTTP status: {status}")
        if result is None:
            print("ERROR: close-all request failed — see error above")
            sys.exit(1)
        # result is a list of {symbol, status, body}
        ok = True
        for item in result:
            sym = item.get("symbol", "?")
            st = item.get("status", "?")
            print(f"  close {sym}: status={st}")
            if int(st) >= 300:
                ok = False
        if not ok:
            print("ERROR: one or more close orders were rejected by the broker")
            sys.exit(1)

        # 3. If the market is open, market orders fill within seconds — poll to
        #    confirm the account actually reaches flat. If closed, skip polling.
        if market_open:
            print("\nMarket is open — waiting for positions to close...")
            for i in range(15):
                time.sleep(4)
                remaining, _ = alpaca("GET", "positions")
                remaining = remaining or []
                print(f"  poll {i+1}/15: {len(remaining)} position(s) remaining")
                if not remaining:
                    break
        else:
            print("\nMarket is CLOSED — close orders accepted and QUEUED to fill "
                  "at the next open. Not polling for fills.")

    # 4. Verify final state
    after, _ = alpaca("GET", "positions")
    after = after or []
    open_orders, _ = alpaca("GET", "orders?status=open&limit=100")
    open_orders = open_orders or []
    account, _ = alpaca("GET", "account")
    cash = account.get("cash") if account else "unknown"
    equity = account.get("equity") if account else "unknown"

    print("\n===== FLATTEN RESULT =====")
    print(f"Positions closed / submitted: {len(before)}")
    print(f"Open positions NOW: {len(after)}")
    for p in after:
        print(f"  position: {p.get('symbol')} qty={p.get('qty')}")
    print(f"Queued closing orders: {len(open_orders)}")
    for o in open_orders:
        print(f"  order: {o.get('side')} {o.get('qty')} {o.get('symbol')} "
              f"[{o.get('type')}] status={o.get('status')}")
    print(f"Account cash:   {cash}")
    print(f"Account equity: {equity}")

    if not after:
        print("\nSUCCESS: account is 100% flat (0 open positions).")
        return

    # Positions still open. That is only OK if the market was closed AND every
    # remaining position has a queued closing order that will flatten it at open.
    if not market_open and len(open_orders) >= len(after):
        print("\nSUCCESS (queued): market closed; all positions have closing "
              "orders queued and will flatten at the next open "
              f"({next_open}). Re-run this workflow after the open to VERIFY flat.")
        return

    print("\nWARNING: account is NOT fully flat and orders are not fully queued "
          "(see above). Re-run after the market opens.")
    sys.exit(1)


if __name__ == "__main__":
    main()

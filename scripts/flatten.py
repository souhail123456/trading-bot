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

    if not before:
        print("Account already flat — nothing to close (idempotent no-op).")
    else:
        # 2. Close ALL positions and cancel open orders
        print("\nCalling DELETE /v2/positions?cancel_orders=true (close_all_positions)...")
        result, status = alpaca("DELETE", "positions?cancel_orders=true")
        print(f"HTTP status: {status}")
        if result is None:
            print("ERROR: close-all request failed — see error above")
            sys.exit(1)
        # result is a list of {symbol, status, body}
        for item in result:
            sym = item.get("symbol", "?")
            st = item.get("status", "?")
            print(f"  close {sym}: status={st}")

        # 3. Give fills a moment, then poll until flat (market orders on paper fill fast)
        print("\nWaiting for positions to close...")
        remaining = before
        for i in range(15):
            time.sleep(4)
            remaining, _ = alpaca("GET", "positions")
            if remaining is None:
                remaining = []
            print(f"  poll {i+1}/15: {len(remaining)} position(s) remaining")
            if not remaining:
                break

    # 4. Verify final state
    after, _ = alpaca("GET", "positions")
    after = after or []
    account, _ = alpaca("GET", "account")
    cash = account.get("cash") if account else "unknown"
    equity = account.get("equity") if account else "unknown"

    print("\n===== FLATTEN RESULT =====")
    print(f"Positions closed: {len(before)}")
    print(f"Open positions NOW: {len(after)}")
    if after:
        for p in after:
            print(f"  STILL OPEN: {p.get('symbol')} qty={p.get('qty')}")
    print(f"Account cash:   {cash}")
    print(f"Account equity: {equity}")

    if after:
        print("\nWARNING: account is NOT fully flat — some positions remain (see above).")
        sys.exit(1)
    print("\nSUCCESS: account is 100% flat (0 open positions).")


if __name__ == "__main__":
    main()

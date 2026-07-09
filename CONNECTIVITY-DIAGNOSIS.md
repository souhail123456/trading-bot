# Connectivity Diagnosis

## Date: 2026-07-08

## Alpaca API Status

**Current health check result (memory/health_status.json):**
- Alpaca: **OK** (45ms latency) as of 2026-07-06
- All 5 services (Alpaca, Groq, Gemini, Cerebras, Telegram) show status "ok"

**Conclusion: Alpaca is NOT down based on the latest health check.**

If trading-admin's health dashboard shows Alpaca as "down", this is likely a stale
read or a transient issue that has since resolved. The health check runs weekly
(Sunday 11 PM UTC) via `.github/workflows/health-check.yml`.

## API Key Configuration

- Keys are stored as GitHub Actions secrets: `ALPACA_API_KEY` and `ALPACA_SECRET_KEY`
- The endpoint is hardcoded to `https://paper-api.alpaca.markets/v2` (paper trading)
- No IP allowlist is configured in the codebase (Alpaca paper API doesn't typically
  require IP allowlisting)
- Historical note from TRADE-LOG.md: On Apr 22 (Day 1), Alpaca returned 403
  "host not in allowlist". This was resolved by Apr 23 using the proxy.

## Proxy Setup (proxy/ directory)

The `proxy/` directory contains a Node.js Express proxy server designed to bypass
IP allowlist restrictions:

- **proxy/server.js**: Express app that proxies requests to Alpaca and Telegram APIs
  - Listens on PORT 3000 (configurable)
  - Requires `PROXY_TOKEN` env var for authentication
  - Routes: `/alpaca/*` forwards to paper-api.alpaca.markets/v2
  - Routes: `/telegram` forwards to api.telegram.org
  - Health check at `/health`
- **proxy/Dockerfile**: Node 20 Alpine container
- **proxy/package.json**: Only dependency is express@^4.21.0

The proxy is meant to be deployed on Railway (or similar) to provide a fixed IP.
However, the current GitHub Actions workflows call Alpaca **directly** (not through
the proxy). The proxy is only used when `PROXY_URL` is set in `scripts/alpaca.sh`
or `scripts/telegram.sh`, which only happens for local/manual runs with `.env`.

## Why Trading-Admin Might Show "Down"

Possible reasons:
1. **Stale health check**: The health check runs only on Sundays. If Alpaca had a
   brief outage between checks, the dashboard might show stale "down" from a
   previous failed check that was later overwritten.
2. **Different health check source**: If trading-admin runs its own independent
   health check against the stock bot, it might be checking a different endpoint
   or using different credentials.
3. **403 errors on specific endpoints**: The main `/v2/account` endpoint works
   (confirmed by health check), but some endpoints might fail if the paper
   trading account has specific restrictions.
4. **Rate limiting**: Alpaca paper API has rate limits; concurrent workflow runs
   could trigger temporary 429 errors.

## Recommendations (no keys changed)

1. Increase health check frequency to daily instead of weekly
2. Add the proxy URL to GitHub secrets if IP allowlisting becomes an issue again
3. Verify that trading-admin's health check is reading the latest health_status.json
4. Check GitHub Actions run logs for any recent 403/401 errors from Alpaca

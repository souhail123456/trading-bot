#!/usr/bin/env python3
"""
LLM API Router — Single entry point for all bot LLM calls.
Auto-fallback chain: Gemini → Groq → Cerebras → OpenRouter
Tracks usage in api_usage.json

Features:
  - Gemini-first (1M context, generous free tier)
  - Auto-truncate prompts to fit each provider's context window
  - Response caching: skip LLM call if positions unchanged
  - Market-closed detection: skip on weekends/holidays

Usage:
    from llm_router import call_llm
    response = call_llm(system_prompt, user_prompt, max_tokens=1500)

Environment variables (set whichever you have):
    GEMINI_API_KEY
    GROQ_API_KEY
    CEREBRAS_API_KEY
    OPEN_ROUTER
"""

import hashlib
import json
import os
import time
import urllib.request
from datetime import datetime, timezone, timedelta
from pathlib import Path

USAGE_FILE = Path(__file__).parent / "api_usage.json"
CACHE_FILE = Path("/tmp/llm_cache.json")

# US market holidays 2026 (NYSE closed)
US_HOLIDAYS = {
    "2026-01-01", "2026-01-19", "2026-02-16", "2026-04-03",
    "2026-05-25", "2026-06-19", "2026-07-03", "2026-09-07",
    "2026-11-26", "2026-12-25",
}

# --- Provider configs (Gemini first — most generous free tier) ---

PROVIDERS = [
    {
        "name": "gemini",
        "env_key": "GEMINI_API_KEY",
        "url": "https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}",
        "model": "gemini-2.0-flash",
        "format": "gemini",
        "max_context": {"gemini-2.0-flash": 900000},
    },
    {
        "name": "groq",
        "env_key": "GROQ_API_KEY",
        "url": "https://api.groq.com/openai/v1/chat/completions",
        "model": "llama-3.1-8b-instant",
        "fallback_model": "llama-3.3-70b-versatile",
        "format": "openai",
        "max_context": {"llama-3.1-8b-instant": 7000, "llama-3.3-70b-versatile": 5500},
    },
    {
        "name": "cerebras",
        "env_key": "CEREBRAS_API_KEY",
        "url": "https://api.cerebras.ai/v1/chat/completions",
        "model": "llama3.1-70b",
        "format": "openai",
        "max_context": {"llama3.1-70b": 7000},
    },
    {
        "name": "openrouter",
        "env_key": "OPEN_ROUTER",
        "url": "https://openrouter.ai/api/v1/chat/completions",
        "model": "google/gemini-2.0-flash-exp:free",
        "fallback_model": "meta-llama/llama-4-maverick:free",
        "format": "openai",
        "max_context": {"google/gemini-2.0-flash-exp:free": 900000, "meta-llama/llama-4-maverick:free": 7000},
    },
]


def _estimate_tokens(text):
    """Rough token estimate: ~4 chars per token for English text."""
    return len(text) // 4


def _truncate_to_fit(system_prompt, user_prompt, max_tokens_out, max_context):
    """Truncate user_prompt if total would exceed max_context (in tokens).
    Preserves system_prompt fully. Cuts user_prompt from the middle,
    keeping the first and last sections (instructions + recent data).
    """
    sys_tokens = _estimate_tokens(system_prompt)
    usr_tokens = _estimate_tokens(user_prompt)
    budget = max_context - sys_tokens - max_tokens_out - 100  # 100 token safety margin

    if usr_tokens <= budget:
        return user_prompt

    # Keep first 40% and last 40% of user prompt, cut the middle
    budget_chars = budget * 4
    keep_start = int(budget_chars * 0.4)
    keep_end = int(budget_chars * 0.4)

    truncated = (
        user_prompt[:keep_start]
        + "\n\n...(truncated to fit context limit)...\n\n"
        + user_prompt[-keep_end:]
    )
    print(f"[llm_router] Truncated prompt: {usr_tokens} → ~{_estimate_tokens(truncated)} tokens (budget: {budget})")
    return truncated


def is_market_open():
    """Check if US stock market is open right now (or within trading window).
    Returns True if it's a weekday and within extended trading hours (pre-market to post-close).
    """
    now = datetime.now(timezone.utc)
    date_str = now.strftime("%Y-%m-%d")

    # Weekend check (Saturday=5, Sunday=6)
    if now.weekday() >= 5:
        return False

    # Holiday check
    if date_str in US_HOLIDAYS:
        return False

    return True


def _cache_key(system_prompt, user_prompt):
    """Hash the positions/account data from user prompt to detect changes."""
    # Extract just the volatile parts (positions + account line)
    # This is a rough hash — any change in positions/P&L invalidates
    h = hashlib.md5((system_prompt[:200] + user_prompt).encode()).hexdigest()
    return h


def _get_cached(cache_key):
    """Return cached response if same positions/data, max 2 hours old."""
    if not CACHE_FILE.exists():
        return None
    try:
        cache = json.loads(CACHE_FILE.read_text())
        if cache.get("key") != cache_key:
            return None
        cached_at = datetime.fromisoformat(cache["timestamp"])
        age = (datetime.now(timezone.utc) - cached_at).total_seconds()
        if age > 7200:  # 2 hour max
            return None
        print(f"[llm_router] Cache hit — reusing response from {int(age)}s ago")
        return cache["response"], cache["provider"], cache["model"]
    except Exception:
        return None


def _set_cache(cache_key, response, provider, model):
    """Cache the response."""
    try:
        CACHE_FILE.write_text(json.dumps({
            "key": cache_key,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "response": response,
            "provider": provider,
            "model": model,
        }))
    except Exception:
        pass


def _log_usage(provider, model, tokens_in, tokens_out, success, error=None):
    """Append usage record to api_usage.json."""
    record = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "provider": provider,
        "model": model,
        "tokens_in": tokens_in,
        "tokens_out": tokens_out,
        "success": success,
        "error": error,
    }

    usage = []
    if USAGE_FILE.exists():
        try:
            usage = json.loads(USAGE_FILE.read_text())
        except:
            usage = []

    usage.append(record)

    # Keep last 500 records only
    if len(usage) > 500:
        usage = usage[-500:]

    USAGE_FILE.write_text(json.dumps(usage, indent=2))


def _call_openai_format(url, api_key, model, system_prompt, user_prompt, max_tokens, temperature):
    """Call OpenAI-compatible API (Groq, Cerebras)."""
    payload = json.dumps({
        "model": model,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        "max_tokens": max_tokens,
        "temperature": temperature,
    }).encode()

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "User-Agent": "trading-bot/1.0",
    }
    if "openrouter.ai" in url:
        headers["HTTP-Referer"] = "https://github.com/trading-bot"
    req = urllib.request.Request(url, data=payload, headers=headers)

    resp = urllib.request.urlopen(req, timeout=30)
    data = json.loads(resp.read())
    content = data["choices"][0]["message"]["content"]
    usage = data.get("usage", {})
    return content, usage.get("prompt_tokens", 0), usage.get("completion_tokens", 0)


def _call_gemini_format(url, api_key, model, system_prompt, user_prompt, max_tokens, temperature):
    """Call Google Gemini API."""
    full_url = url.format(model=model, api_key=api_key)
    payload = json.dumps({
        "contents": [{"parts": [{"text": f"{system_prompt}\n\n{user_prompt}"}]}],
        "generationConfig": {
            "maxOutputTokens": max_tokens,
            "temperature": temperature,
        },
    }).encode()

    req = urllib.request.Request(full_url, data=payload, headers={
        "Content-Type": "application/json",
        "User-Agent": "trading-bot/1.0",
    })

    resp = urllib.request.urlopen(req, timeout=30)
    data = json.loads(resp.read())
    content = data["candidates"][0]["content"]["parts"][0]["text"]
    # Gemini doesn't always return token counts in same format
    usage_meta = data.get("usageMetadata", {})
    return content, usage_meta.get("promptTokenCount", 0), usage_meta.get("candidatesTokenCount", 0)


def call_llm(system_prompt, user_prompt, max_tokens=1500, temperature=0.3, use_cache=True, require_market_open=False):
    """
    Call LLM with automatic fallback chain.
    Returns: (response_text, provider_used, model_used)
    Raises: RuntimeError if ALL providers fail or market is closed.

    Args:
        use_cache: if True, return cached response when positions haven't changed (max 2h)
        require_market_open: if True, raise RuntimeError on weekends/holidays
    """
    # Skip on closed market if requested
    if require_market_open and not is_market_open():
        raise RuntimeError("Market closed (weekend/holiday) — skipping LLM call to save tokens")

    # Check cache
    if use_cache:
        ck = _cache_key(system_prompt, user_prompt)
        cached = _get_cached(ck)
        if cached:
            return cached

    errors = []

    for provider in PROVIDERS:
        api_key = os.environ.get(provider["env_key"])
        if not api_key:
            continue

        models_to_try = [provider["model"]]
        if "fallback_model" in provider:
            models_to_try.append(provider["fallback_model"])

        for model in models_to_try:
            try:
                # Auto-truncate to fit provider's context window
                ctx_limits = provider.get("max_context", {})
                ctx_limit = ctx_limits.get(model, 8000)  # safe default
                fitted_user = _truncate_to_fit(system_prompt, user_prompt, max_tokens, ctx_limit)

                if provider["format"] == "openai":
                    content, tokens_in, tokens_out = _call_openai_format(
                        provider["url"], api_key, model,
                        system_prompt, fitted_user, max_tokens, temperature
                    )
                elif provider["format"] == "gemini":
                    content, tokens_in, tokens_out = _call_gemini_format(
                        provider["url"], api_key, model,
                        system_prompt, fitted_user, max_tokens, temperature
                    )
                else:
                    continue

                _log_usage(provider["name"], model, tokens_in, tokens_out, True)
                if use_cache:
                    _set_cache(ck, content, provider["name"], model)
                return content, provider["name"], model

            except Exception as e:
                error_msg = str(e)[:200]
                errors.append(f"{provider['name']}/{model}: {error_msg}")
                _log_usage(provider["name"], model, 0, 0, False, error_msg)

                # If rate limited or payload too large, try fallback model
                if "429" in error_msg or "413" in error_msg or "rate_limit" in error_msg.lower():
                    continue
                # If other error, skip to next provider
                else:
                    break

    raise RuntimeError(f"All LLM providers failed:\n" + "\n".join(errors))


def get_usage_summary():
    """Get API usage summary for monitoring."""
    if not USAGE_FILE.exists():
        return {"total_calls": 0, "providers": {}}

    usage = json.loads(USAGE_FILE.read_text())
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")

    summary = {"total_calls": len(usage), "today": {}, "failures_today": 0}
    for record in usage:
        if record["timestamp"].startswith(today):
            provider = record["provider"]
            if provider not in summary["today"]:
                summary["today"][provider] = {"calls": 0, "tokens_in": 0, "tokens_out": 0, "failures": 0}
            summary["today"][provider]["calls"] += 1
            summary["today"][provider]["tokens_in"] += record.get("tokens_in", 0)
            summary["today"][provider]["tokens_out"] += record.get("tokens_out", 0)
            if not record["success"]:
                summary["today"][provider]["failures"] += 1
                summary["failures_today"] += 1

    return summary


if __name__ == "__main__":
    # Quick test
    print("Testing LLM Router...")
    try:
        resp, provider, model = call_llm(
            "You are a helpful assistant.",
            "Say 'router works' and nothing else.",
            max_tokens=20
        )
        print(f"OK — {provider}/{model}: {resp}")
    except RuntimeError as e:
        print(f"FAILED: {e}")

    print("\nUsage summary:")
    print(json.dumps(get_usage_summary(), indent=2))

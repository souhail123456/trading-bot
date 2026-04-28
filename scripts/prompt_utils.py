#!/usr/bin/env python3
"""Shared utilities for prompt builders — keeps prompts under Groq token limits."""


def tail_sections(text, max_chars=800):
    """Return the last N chars of text, cutting at a section boundary (---) if possible."""
    if len(text) <= max_chars:
        return text
    chunk = text[-max_chars:]
    # Try to cut at a clean section break
    idx = chunk.find("\n---")
    if idx > 0 and idx < len(chunk) // 2:
        chunk = chunk[idx + 1:]
    return "...(truncated)\n" + chunk


def recent_trade_log(trade_log, max_chars=800):
    """Extract SUMMARY block + last N chars of trade log."""
    summary = ""
    if "<!-- SUMMARY" in trade_log:
        start = trade_log.index("<!-- SUMMARY")
        end = trade_log.index("-->", start) + 3
        summary = trade_log[start:end] + "\n\n"
    tail = tail_sections(trade_log, max_chars)
    return summary + tail


def recent_research_log(research_log, max_chars=800):
    """Return last section(s) of research log."""
    return tail_sections(research_log, max_chars)


def compact_strategy(strategy, max_chars=1500):
    """Trim strategy if it's too long (unlikely but safety net)."""
    if len(strategy) <= max_chars:
        return strategy
    return strategy[:max_chars] + "\n...(truncated)"

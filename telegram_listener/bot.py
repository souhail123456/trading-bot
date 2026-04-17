#!/usr/bin/env python3
"""
Trading Bot — Telegram Live Chat Interface
Runs on Koyeb. Reads GitHub memory files, answers via Claude API.
Trade execution still requires Mac (/market-open locally).
"""

import os
import logging
import base64
import requests
import anthropic
from telegram import Update
from telegram.ext import (
    Application, CommandHandler, MessageHandler,
    filters, ContextTypes
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

BOT_TOKEN      = os.environ["TELEGRAM_BOT_TOKEN"]
ALLOWED_ID     = int(os.environ["TELEGRAM_CHAT_ID"])
ANTHROPIC_KEY  = os.environ["ANTHROPIC_API_KEY"]
GITHUB_TOKEN   = os.environ.get("GITHUB_TOKEN", "")
GITHUB_REPO    = os.environ.get("GITHUB_REPO", "souhail123456/trading-bot")


# ── GitHub helpers ────────────────────────────────────────────────────────────

def read_github_file(path: str) -> str:
    url = f"https://api.github.com/repos/{GITHUB_REPO}/contents/{path}"
    headers = {"Authorization": f"token {GITHUB_TOKEN}"} if GITHUB_TOKEN else {}
    r = requests.get(url, headers=headers, timeout=10)
    if r.status_code == 200:
        return base64.b64decode(r.json()["content"]).decode("utf-8")
    return f"[could not read {path} — {r.status_code}]"


def get_context() -> dict:
    trade_log    = read_github_file("memory/TRADE-LOG.md")
    research_log = read_github_file("memory/RESEARCH-LOG.md")
    strategy     = read_github_file("memory/TRADING-STRATEGY.md")
    return {
        "trade_log":    trade_log[-3000:],
        "research_log": research_log[-3000:],
        "strategy":     strategy[:2000],
    }


# ── Claude helper ─────────────────────────────────────────────────────────────

def ask_claude(question: str, ctx: dict) -> str:
    client = anthropic.Anthropic(api_key=ANTHROPIC_KEY)
    system = (
        "You are a trading bot assistant for a $10k Alpaca paper account. "
        "Be ultra-concise: short bullets, no fluff. "
        "For trade execution, remind user to run /market-open locally on their Mac."
    )
    prompt = (
        f"=== TRADE LOG (recent) ===\n{ctx['trade_log']}\n\n"
        f"=== RESEARCH LOG (recent) ===\n{ctx['research_log']}\n\n"
        f"=== STRATEGY ===\n{ctx['strategy']}\n\n"
        f"Question: {question}"
    )
    resp = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=500,
        system=system,
        messages=[{"role": "user", "content": prompt}],
    )
    return resp.content[0].text


# ── Auth guard ────────────────────────────────────────────────────────────────

def allowed(update: Update) -> bool:
    return update.effective_chat.id == ALLOWED_ID


# ── Handlers ──────────────────────────────────────────────────────────────────

async def cmd_start(update: Update, _: ContextTypes.DEFAULT_TYPE):
    if not allowed(update):
        return
    await update.message.reply_text(
        "Trading Bot online.\n\n"
        "/positions — open positions\n"
        "/research  — today's research\n"
        "/portfolio — latest snapshot\n"
        "/strategy  — trading rules\n"
        "/week      — weekly performance\n\n"
        "Or just ask anything in plain text."
    )


async def cmd_positions(update: Update, _: ContextTypes.DEFAULT_TYPE):
    if not allowed(update):
        return
    await update.message.reply_text("Reading positions...")
    reply = ask_claude(
        "What are my current open positions? Show ticker, entry price, stop, unrealized P&L.",
        get_context()
    )
    await update.message.reply_text(reply)


async def cmd_research(update: Update, _: ContextTypes.DEFAULT_TYPE):
    if not allowed(update):
        return
    await update.message.reply_text("Reading research...")
    reply = ask_claude(
        "Summarize today's pre-market research. Decision and top trade idea.",
        get_context()
    )
    await update.message.reply_text(reply)


async def cmd_portfolio(update: Update, _: ContextTypes.DEFAULT_TYPE):
    if not allowed(update):
        return
    reply = ask_claude(
        "Show the latest EOD portfolio snapshot: equity, cash, day P&L, phase P&L.",
        get_context()
    )
    await update.message.reply_text(reply)


async def cmd_strategy(update: Update, _: ContextTypes.DEFAULT_TYPE):
    if not allowed(update):
        return
    reply = ask_claude(
        "Summarize the key trading rules and hard limits.",
        get_context()
    )
    await update.message.reply_text(reply)


async def cmd_week(update: Update, _: ContextTypes.DEFAULT_TYPE):
    if not allowed(update):
        return
    reply = ask_claude(
        "Summarize this week's trades: wins, losses, P&L, current open positions.",
        get_context()
    )
    await update.message.reply_text(reply)


async def handle_text(update: Update, _: ContextTypes.DEFAULT_TYPE):
    if not allowed(update):
        return
    question = update.message.text
    await update.message.reply_text("...")
    reply = ask_claude(question, get_context())
    await update.message.reply_text(reply)


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start",     cmd_start))
    app.add_handler(CommandHandler("positions", cmd_positions))
    app.add_handler(CommandHandler("research",  cmd_research))
    app.add_handler(CommandHandler("portfolio", cmd_portfolio))
    app.add_handler(CommandHandler("strategy",  cmd_strategy))
    app.add_handler(CommandHandler("week",      cmd_week))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))
    logger.info("Bot polling...")
    app.run_polling(drop_pending_updates=True)


if __name__ == "__main__":
    main()

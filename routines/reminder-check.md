You are running the hourly reminder check for the trading bot.

Resolve today's date via: DATE=$(date +%Y-%m-%d).

IMPORTANT — ENVIRONMENT VARIABLES:
- TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID must be set.
- There is NO .env file in this repo. Vars come from the process env.

STEP 1 — Run the reminder check:
  bash scripts/remind.sh check

STEP 2 — If output contains "sent task", "all tasks complete", or "resending":
  git checkout main
  git add memory/PENDING-REMINDERS.md memory/REMIND-STATE.txt
  git commit -m "reminder state update $DATE"
  git push origin main

STEP 3 — If output contains "nothing pending" or "waiting for":
  No commit needed.

That is all. Do not run any other steps.

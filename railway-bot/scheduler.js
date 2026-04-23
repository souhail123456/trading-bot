const cron = require("node-cron");
const fs = require("fs");
const path = require("path");
const { runAgent } = require("./agent");

// All times in UTC
// Pre-market:    11:00 UTC (7:00 PM Shanghai)
// Market Open:   13:30 UTC (9:30 PM Shanghai)
// Midday:        17:00 UTC (1:00 AM+1 Shanghai)
// Daily Summary: 20:00 UTC (4:00 AM+1 Shanghai)
// Weekly Review: 21:00 UTC Friday (5:00 AM+1 Saturday Shanghai)

async function fetchRoutine(name) {
  // Clone repo (with auth) and read the routine file
  const { execSync } = require("child_process");
  const GH_TOKEN = process.env.GH_TOKEN || "";
  const repoUrl = GH_TOKEN
    ? `https://x-access-token:${GH_TOKEN}@github.com/souhail123456/trading-bot.git`
    : "https://github.com/souhail123456/trading-bot.git";
  const tmpDir = `/tmp/routines-${Date.now()}`;
  try {
    execSync(`git clone --depth 1 ${repoUrl} ${tmpDir}`, {
      timeout: 30000, encoding: "utf-8",
      env: { ...process.env, HOME: process.env.HOME || "/root" },
    });
    const content = require("fs").readFileSync(`${tmpDir}/routines/${name}.md`, "utf-8");
    execSync(`rm -rf ${tmpDir}`, { timeout: 5000 });
    return content;
  } catch (err) {
    try { execSync(`rm -rf ${tmpDir}`, { timeout: 5000 }); } catch {}
    throw new Error(`Failed to load routine ${name}: ${err.message}`);
  }
}

async function runRoutine(name) {
  console.log(`\n${"=".repeat(60)}`);
  console.log(`[scheduler] Running: ${name} at ${new Date().toISOString()}`);
  console.log(`${"=".repeat(60)}\n`);

  try {
    const prompt = await fetchRoutine(name);
    await runAgent(prompt, name);
  } catch (err) {
    console.error(`[scheduler] ${name} failed:`, err.message);
  }
}

// --- Schedule all routines (UTC cron) ---

// Pre-market: weekdays 11:00 UTC
cron.schedule("0 11 * * 1-5", () => runRoutine("pre-market"), {
  timezone: "UTC",
});

// Market Open: weekdays 13:30 UTC
cron.schedule("30 13 * * 1-5", () => runRoutine("market-open"), {
  timezone: "UTC",
});

// Midday: weekdays 17:00 UTC
cron.schedule("0 17 * * 1-5", () => runRoutine("midday"), {
  timezone: "UTC",
});

// Daily Summary: weekdays 20:00 UTC
cron.schedule("0 20 * * 1-5", () => runRoutine("daily-summary"), {
  timezone: "UTC",
});

// Weekly Review: Friday 21:00 UTC
cron.schedule("0 21 * * 5", () => runRoutine("weekly-review"), {
  timezone: "UTC",
});

console.log("[scheduler] Trading bot scheduler started.");
console.log("[scheduler] Schedules (UTC):");
console.log("  Pre-market:    Mon-Fri 11:00");
console.log("  Market Open:   Mon-Fri 13:30");
console.log("  Midday:        Mon-Fri 17:00");
console.log("  Daily Summary: Mon-Fri 20:00");
console.log("  Weekly Review: Fri     21:00");
console.log("");

// Keep process alive
process.on("SIGTERM", () => {
  console.log("[scheduler] Shutting down...");
  process.exit(0);
});

// If RUN_NOW env var is set, run that routine immediately (for testing)
if (process.env.RUN_NOW) {
  runRoutine(process.env.RUN_NOW);
}

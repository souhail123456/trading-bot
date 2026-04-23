const Anthropic = require("@anthropic-ai/sdk");
const { execSync, spawnSync } = require("child_process");
const fs = require("fs");
const path = require("path");

const client = new Anthropic();
const MODEL = process.env.CLAUDE_MODEL || "claude-sonnet-4-6";
// Build authenticated repo URL if GH_TOKEN is set
const GH_TOKEN = process.env.GH_TOKEN || "";
const REPO_BASE = "github.com/souhail123456/trading-bot.git";
const REPO_URL = GH_TOKEN
  ? `https://x-access-token:${GH_TOKEN}@${REPO_BASE}`
  : process.env.REPO_URL || `https://${REPO_BASE}`;
const MAX_TURNS = 80;

const tools = [
  {
    name: "bash",
    description: "Execute a bash command and return stdout/stderr. Working directory persists between calls.",
    input_schema: {
      type: "object",
      properties: {
        command: { type: "string", description: "The bash command to execute" },
      },
      required: ["command"],
    },
  },
  {
    name: "read_file",
    description: "Read a file and return its contents.",
    input_schema: {
      type: "object",
      properties: {
        path: { type: "string", description: "Path to the file to read" },
      },
      required: ["path"],
    },
  },
  {
    name: "write_file",
    description: "Write content to a file, creating it if needed.",
    input_schema: {
      type: "object",
      properties: {
        path: { type: "string", description: "Path to the file to write" },
        content: { type: "string", description: "Content to write" },
      },
      required: ["path", "content"],
    },
  },
];

function executeTool(name, input, workDir) {
  try {
    switch (name) {
      case "bash": {
        const result = spawnSync("bash", ["-c", input.command], {
          cwd: workDir,
          timeout: 120000,
          maxBuffer: 10 * 1024 * 1024,
          encoding: "utf-8",
          env: { ...process.env, HOME: process.env.HOME || "/root" },
        });
        const out = (result.stdout || "") + (result.stderr || "");
        const exitCode = result.status ?? -1;
        return `Exit code: ${exitCode}\n${out}`.slice(0, 50000);
      }
      case "read_file": {
        const filePath = path.isAbsolute(input.path)
          ? input.path
          : path.join(workDir, input.path);
        return fs.readFileSync(filePath, "utf-8").slice(0, 100000);
      }
      case "write_file": {
        const filePath = path.isAbsolute(input.path)
          ? input.path
          : path.join(workDir, input.path);
        fs.mkdirSync(path.dirname(filePath), { recursive: true });
        fs.writeFileSync(filePath, input.content, "utf-8");
        return "File written successfully.";
      }
      default:
        return `Unknown tool: ${name}`;
    }
  } catch (err) {
    return `Error: ${err.message}`;
  }
}

async function runAgent(prompt, routineName) {
  // Clone repo into a temp directory
  const workDir = `/tmp/trading-bot-${Date.now()}`;
  console.log(`[${routineName}] Cloning repo into ${workDir}...`);

  try {
    execSync(`git clone --depth 1 ${REPO_URL} ${workDir}`, {
      timeout: 60000,
      encoding: "utf-8",
      env: { ...process.env, HOME: process.env.HOME || "/root" },
    });
  } catch (err) {
    console.error(`[${routineName}] Clone failed:`, err.message);
    return;
  }

  // Configure git for commits
  try {
    execSync('git config user.email "bot@trading-bot.ai" && git config user.name "Trading Bot"', {
      cwd: workDir,
      encoding: "utf-8",
    });
  } catch {}

  const messages = [{ role: "user", content: prompt }];
  console.log(`[${routineName}] Starting agent loop (model: ${MODEL})...`);

  for (let turn = 0; turn < MAX_TURNS; turn++) {
    let response;
    try {
      response = await client.messages.create({
        model: MODEL,
        max_tokens: 16384,
        tools,
        messages,
      });
    } catch (err) {
      console.error(`[${routineName}] API error:`, err.message);
      break;
    }

    // Collect text output
    for (const block of response.content) {
      if (block.type === "text" && block.text) {
        console.log(`[${routineName}] ${block.text.slice(0, 500)}`);
      }
    }

    // If no tool use, we're done
    if (response.stop_reason === "end_turn") {
      console.log(`[${routineName}] Agent finished (${turn + 1} turns).`);
      break;
    }

    // Execute tool calls
    const toolResults = [];
    for (const block of response.content) {
      if (block.type === "tool_use") {
        console.log(`[${routineName}] Tool: ${block.name}(${JSON.stringify(block.input).slice(0, 200)})`);
        const result = executeTool(block.name, block.input, workDir);
        toolResults.push({
          type: "tool_result",
          tool_use_id: block.id,
          content: result,
        });
      }
    }

    messages.push({ role: "assistant", content: response.content });
    messages.push({ role: "user", content: toolResults });
  }

  // Cleanup
  try {
    execSync(`rm -rf ${workDir}`, { timeout: 10000 });
  } catch {}

  console.log(`[${routineName}] Done.`);
}

module.exports = { runAgent };

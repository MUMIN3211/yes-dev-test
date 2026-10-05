// Launches the Mailtrap MCP server (mcp-mailtrap) for Claude Code.
// The API token is read from backend/.env (gitignored) at startup, so no
// config file in the repo ever contains it. Registered in /.mcp.json.
import { spawn } from "node:child_process";
import { readFileSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const root = join(dirname(fileURLToPath(import.meta.url)), "..");

function readEnvFile(path) {
  const vars = {};
  for (const line of readFileSync(path, "utf8").split(/\r?\n/)) {
    const match = line.match(/^\s*([A-Z0-9_]+)\s*=\s*(.*)\s*$/);
    if (match) vars[match[1]] = match[2];
  }
  return vars;
}

const env = readEnvFile(join(root, "backend", ".env"));
if (!env.MAILTRAP_API_TOKEN) {
  console.error("MAILTRAP_API_TOKEN is missing in backend/.env");
  process.exit(1);
}

const child = spawn("npx", ["-y", "mcp-mailtrap"], {
  stdio: "inherit",
  shell: process.platform === "win32", // npx is a .cmd file on Windows
  env: {
    ...process.env,
    MAILTRAP_API_TOKEN: env.MAILTRAP_API_TOKEN,
    MAILTRAP_ACCOUNT_ID: env.MAILTRAP_ACCOUNT_ID || "2849372",
    MAILTRAP_TEST_INBOX_ID: env.MAILTRAP_TEST_INBOX_ID || "4944118",
    DEFAULT_FROM_EMAIL: env.MAILTRAP_FROM_EMAIL || "hello@demomailtrap.co",
  },
});
child.on("exit", (code) => process.exit(code ?? 0));

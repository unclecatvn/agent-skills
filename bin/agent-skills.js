#!/usr/bin/env node
"use strict";

const fs = require("fs");
const path = require("path");
const https = require("https");

const PACKAGE_ROOT = path.join(__dirname, "..");
const DEFAULT_AI = "cursor";
const DEFAULT_SKILL = "odoo";
const DEFAULT_VERSION = "18.0";
const EXCLUDED_DIRS = new Set(["bin", "node_modules"]);
const GITHUB_REPO = "unclecatvn/agent-skills";
const NPM_PACKAGE = "@unclecat/agent-skills-cli";

// Config file path for storing last update check
const CONFIG_DIR = path.join(require("os").homedir(), ".agent-skills");
const UPDATE_CHECK_FILE = path.join(CONFIG_DIR, "update-check.json");
const UPDATE_CHECK_INTERVAL = 24 * 60 * 60 * 1000; // 24 hours

function printHelp() {
  const text = `
agent-skills - Install agent skills docs by version

Usage:
  agent-skills init --ai <assistant> <skill> [version]
  agent-skills init --ai <assistant> <skill> --version <version>
  agent-skills versions [skill]
  agent-skills skills
  agent-skills update
  agent-skills help

Options:
  --ai <assistant>        cursor | claude | antigravity | kiro | docs | all
  --skill <skill>         Skill folder name (default: ${DEFAULT_SKILL})
  --version <version>     Version (default: ${DEFAULT_VERSION})
  --dest <path>           Destination directory (default: current directory)
  --force                 Overwrite existing files
  --dry-run               Show what would be copied
  --offline               Skip GitHub download, use bundled assets
  -V, --cli-version       Print CLI version
`;
  console.log(text.trim());
}

function printError(message) {
  console.error(`Error: ${message}`);
}

function getPackageVersion() {
  try {
    const pkg = require(path.join(PACKAGE_ROOT, "package.json"));
    return pkg.version || "0.0.0";
  } catch {
    return "0.0.0";
  }
}

// Get last update check timestamp from config file
function getLastUpdateCheck() {
  try {
    if (fs.existsSync(UPDATE_CHECK_FILE)) {
      const data = fs.readFileSync(UPDATE_CHECK_FILE, "utf8");
      const config = JSON.parse(data);
      return config.lastCheck || 0;
    }
  } catch {
    // Ignore errors
  }
  return 0;
}

// Set last update check timestamp
function setLastUpdateCheck() {
  try {
    if (!fs.existsSync(CONFIG_DIR)) {
      fs.mkdirSync(CONFIG_DIR, { recursive: true });
    }
    fs.writeFileSync(
      UPDATE_CHECK_FILE,
      JSON.stringify({ lastCheck: Date.now() }),
      "utf8"
    );
  } catch {
    // Ignore errors
  }
}

// Background update check - runs asynchronously and notifies if update available
async function checkForUpdatesInBackground() {
  const lastCheck = getLastUpdateCheck();
  const now = Date.now();

  // Only check once per day
  if (now - lastCheck < UPDATE_CHECK_INTERVAL) {
    return;
  }

  setLastUpdateCheck();

  try {
    const currentVersion = getPackageVersion();
    const npmVersion = await fetchLatestNpmVersion();

    if (npmVersion && npmVersion !== currentVersion) {
      // Show update notification after a short delay (so it doesn't interfere with command output)
      setTimeout(() => {
        console.error(
          `\n\x1b[33m\x1b[1m╔════════════════════════════════════════╗\x1b[0m`
        );
        console.error(
          `\x1b[33m\x1b[1m║  Update Available ${currentVersion} → ${npmVersion}  ║\x1b[0m`
        );
        console.error(
          `\x1b[33m\x1b[1m╚════════════════════════════════════════╝\x1b[0m`
        );
        console.error(
          `Run \x1b[36mnpm update -g ${NPM_PACKAGE}\x1b[0m to update.\n`
        );
      }, 500);
    }
  } catch {
    // Silently ignore errors - background check should never break the CLI
  }
}

function getSkillDirs() {
  return fs
    .readdirSync(PACKAGE_ROOT, { withFileTypes: true })
    .filter((entry) => entry.isDirectory())
    .map((entry) => entry.name)
    .filter((name) => !name.startsWith("."))
    .filter((name) => !EXCLUDED_DIRS.has(name))
    .filter((name) => {
      const full = path.join(PACKAGE_ROOT, name);
      const subdirs = fs.readdirSync(full, { withFileTypes: true });
      return subdirs.some((sub) => sub.isDirectory());
    })
    .sort();
}

function listSkills() {
  const skills = getSkillDirs();
  if (skills.length === 0) {
    console.log("No skills found.");
    return;
  }
  console.log("Available skills:");
  for (const skill of skills) console.log(`- ${skill}`);
}

function resolveSkillDir(skill) {
  const dir = path.join(PACKAGE_ROOT, skill);
  if (!fs.existsSync(dir)) {
    printError(`Skill not found: ${skill}`);
    console.log("");
    listSkills();
    process.exit(1);
  }
  return dir;
}

function listVersions(skill) {
  const skillDir = resolveSkillDir(skill);
  const versions = fs
    .readdirSync(skillDir, { withFileTypes: true })
    .filter((entry) => entry.isDirectory())
    .map((entry) => entry.name)
    .sort();

  if (versions.length === 0) {
    console.log("No versions found.");
    return;
  }

  console.log(`Available versions for ${skill}:`);
  for (const v of versions) console.log(`- ${v}`);
}

function resolveVersionDir(skill, version) {
  const skillDir = resolveSkillDir(skill);
  const dir = path.join(skillDir, version);
  if (!fs.existsSync(dir)) {
    printError(`Version not found: ${skill}/${version}`);
    console.log("");
    listVersions(skill);
    process.exit(1);
  }
  return dir;
}

function ensureDir(target) {
  fs.mkdirSync(target, { recursive: true });
}

function copyFile(source, dest, options) {
  const { force, dryRun } = options;
  if (!force && fs.existsSync(dest)) return false;
  if (dryRun) return true;
  ensureDir(path.dirname(dest));
  fs.copyFileSync(source, dest);
  return true;
}

function copyDir(sourceDir, destDir, options, renameExt) {
  const entries = fs.readdirSync(sourceDir, { withFileTypes: true });
  for (const entry of entries) {
    const sourcePath = path.join(sourceDir, entry.name);
    const destName = renameExt
      ? renameExt(entry.name, entry.isDirectory())
      : entry.name;
    const destPath = path.join(destDir, destName);
    if (entry.isDirectory()) {
      copyDir(sourcePath, destPath, options, renameExt);
      continue;
    }
    copyFile(sourcePath, destPath, options);
  }
}

function normalize(value) {
  return String(value || "").trim();
}

function parseArgs(argv) {
  const args = {
    command: null,
    ai: null,
    skill: null,
    version: DEFAULT_VERSION,
    dest: process.cwd(),
    force: false,
    dryRun: false,
    offline: false,
    positionals: [],
  };

  const tokens = argv.slice(2);

  // Handle version and help flags before processing command
  for (const token of tokens) {
    if (token === "-V" || token === "--cli-version") {
      console.log(getPackageVersion());
      process.exit(0);
    }
    if (token === "-h" || token === "--help") {
      args.command = "help";
      return args;
    }
  }

  // First pass: collect all non-flag tokens (commands and positionals)
  const nonFlagTokens = [];
  for (let i = 0; i < tokens.length; i++) {
    const token = tokens[i];
    if (token.startsWith("-")) {
      // Skip flag and its value
      if (
        token === "--ai" ||
        token === "--skill" ||
        token === "--version" ||
        token === "--dest"
      ) {
        i++; // Skip next token (flag value)
      }
    } else {
      nonFlagTokens.push(token);
    }
  }

  // Set command from first non-flag token
  args.command = nonFlagTokens[0] || "help";

  // Second pass: process all flags
  for (let i = 0; i < tokens.length; i++) {
    const token = tokens[i];
    if (token === "--ai") {
      args.ai = tokens[i + 1];
      i += 1;
      continue;
    }
    if (token === "--skill") {
      args.skill = tokens[i + 1];
      i += 1;
      continue;
    }
    if (token === "--version") {
      args.version = tokens[i + 1] || args.version;
      i += 1;
      continue;
    }
    if (token === "--dest") {
      args.dest = tokens[i + 1] || args.dest;
      i += 1;
      continue;
    }
    if (token === "--force") {
      args.force = true;
      continue;
    }
    if (token === "--dry-run") {
      args.dryRun = true;
      continue;
    }
    if (token === "--offline") {
      args.offline = true;
      continue;
    }
    if (token.startsWith("-")) {
      continue;
    }
    // Non-flag tokens after command go to positionals
    if (token !== args.command) {
      args.positionals.push(token);
    }
  }

  return args;
}

function writeFileIfAllowed(dest, content, options) {
  const { force, dryRun } = options;
  if (!force && fs.existsSync(dest)) return false;
  if (dryRun) return true;
  ensureDir(path.dirname(dest));
  fs.writeFileSync(dest, content);
  return true;
}

function buildCommandContent(skill, version) {
  return `# ${skill} (${version})

Use the docs in \`.shared/${skill}/${version}/\` as the source of truth for this skill.
`;
}

function installShared(skill, versionDir, destRoot, options) {
  const targetDir = path.join(destRoot, ".shared", skill, options.version);
  copyDir(versionDir, targetDir, options, null);
  return targetDir;
}

function installCursor(skill, versionDir, destRoot, options) {
  const sharedDir = installShared(skill, versionDir, destRoot, options);
  const commandPath = path.join(destRoot, ".cursor", "commands", `${skill}.md`);
  const content = buildCommandContent(skill, options.version);
  writeFileIfAllowed(commandPath, content, options);
  return { sharedDir, commandPath };
}

function installAntigravity(skill, versionDir, destRoot, options) {
  const sharedDir = installShared(skill, versionDir, destRoot, options);
  const workflowPath = path.join(destRoot, ".agent", "workflows", `${skill}.md`);
  const content = buildCommandContent(skill, options.version);
  writeFileIfAllowed(workflowPath, content, options);
  return { sharedDir, workflowPath };
}

function installKiro(skill, versionDir, destRoot, options) {
  const sharedDir = installShared(skill, versionDir, destRoot, options);
  const steeringPath = path.join(destRoot, ".kiro", "steering", `${skill}.md`);
  const content = buildCommandContent(skill, options.version);
  writeFileIfAllowed(steeringPath, content, options);
  return { sharedDir, steeringPath };
}

function installDocs(skill, versionDir, destRoot, options) {
  const targetDir = path.join(destRoot, "docs", skill, options.version);
  copyDir(versionDir, targetDir, options, null);
  return targetDir;
}

function installClaude(skill, versionDir, destRoot, options) {
  const targetDir = path.join(destRoot, ".claude", "skills", skill, options.version);
  copyDir(versionDir, targetDir, options, null);
  return targetDir;
}

function runInit(args) {
  const ai = normalize(args.ai || DEFAULT_AI).toLowerCase();
  const positional = args.positionals;
  const skill = normalize(args.skill || positional[0] || DEFAULT_SKILL);
  const version = normalize(args.version || positional[1] || DEFAULT_VERSION);
  const versionDir = resolveVersionDir(skill, version);

  const valid = new Set([
    "cursor",
    "claude",
    "antigravity",
    "kiro",
    "docs",
    "all",
  ]);
  if (!valid.has(ai)) {
    printError(`Unknown --ai value: ${ai}`);
    printHelp();
    process.exit(1);
  }

  const installArgs = { ...args, version };
  const results = [];
  if (ai === "cursor" || ai === "all") {
    const target = installCursor(skill, versionDir, args.dest, installArgs);
    results.push(`cursor -> ${target.commandPath}`);
    results.push(`shared -> ${target.sharedDir}`);
  }
  if (ai === "antigravity" || ai === "all") {
    const target = installAntigravity(skill, versionDir, args.dest, installArgs);
    results.push(`antigravity -> ${target.workflowPath}`);
    results.push(`shared -> ${target.sharedDir}`);
  }
  if (ai === "kiro" || ai === "all") {
    const target = installKiro(skill, versionDir, args.dest, installArgs);
    results.push(`kiro -> ${target.steeringPath}`);
    results.push(`shared -> ${target.sharedDir}`);
  }
  if (ai === "docs" || ai === "all") {
    const target = installDocs(skill, versionDir, args.dest, installArgs);
    results.push(`docs -> ${target}`);
  }
  if (ai === "claude" || ai === "all") {
    const target = installClaude(skill, versionDir, args.dest, installArgs);
    results.push(`claude -> ${target}`);
  }

  if (args.dryRun) {
    console.log("Dry run. Planned installs:");
  } else {
    console.log("Install complete:");
  }
  for (const line of results) console.log(`- ${line}`);
}

// Fetch latest version from npm registry
function fetchLatestNpmVersion() {
  return new Promise((resolve, reject) => {
    const options = {
      hostname: "registry.npmjs.org",
      path: `/${NPM_PACKAGE.replace("/", "%2F")}`,
      method: "GET",
      headers: { "User-Agent": "agent-skills-cli" },
    };

    https
      .get(options, (res) => {
        let data = "";
        res.on("data", (chunk) => (data += chunk));
        res.on("end", () => {
          try {
            const pkg = JSON.parse(data);
            resolve(pkg["dist-tags"]?.latest || null);
          } catch {
            resolve(null);
          }
        });
      })
      .on("error", () => resolve(null));
  });
}

// Fetch latest release from GitHub
function fetchLatestGitHubRelease() {
  return new Promise((resolve, reject) => {
    const options = {
      hostname: "api.github.com",
      path: `/repos/${GITHUB_REPO}/releases/latest`,
      method: "GET",
      headers: {
        "User-Agent": "agent-skills-cli",
        Accept: "application/vnd.github.v3+json",
      },
    };

    https
      .get(options, (res) => {
        let data = "";
        res.on("data", (chunk) => (data += chunk));
        res.on("end", () => {
          if (res.statusCode === 200) {
            try {
              const release = JSON.parse(data);
              resolve({ tag: release.tag_name, url: release.html_url });
            } catch {
              resolve(null);
            }
          } else {
            resolve(null);
          }
        });
      })
      .on("error", () => resolve(null));
  });
}

// Update command
async function runUpdate(args) {
  const currentVersion = getPackageVersion();
  console.log(`Current version: ${currentVersion}`);
  console.log("Checking for updates...\n");

  if (!args.offline) {
    const [npmVersion, githubRelease] = await Promise.all([
      fetchLatestNpmVersion(),
      fetchLatestGitHubRelease(),
    ]);

    if (npmVersion && npmVersion !== currentVersion) {
      console.log(`\x1b[33mNew version available on npm: ${npmVersion}\x1b[0m`);
      console.log(`To update, run: \x1b[36mnpm install -g ${NPM_PACKAGE}@latest\x1b[0m\n`);
    } else {
      console.log(`\x1b[32mCLI is up to date!\x1b[0m\n`);
    }

    if (githubRelease) {
      console.log(`Latest GitHub release: ${githubRelease.tag}`);
      console.log(`Release notes: ${githubRelease.url}\n`);
    }
  } else {
    console.log("Offline mode: Skipping update check.");
  }
}

function main() {
  const args = parseArgs(process.argv);
  const cmd = normalize(args.command).toLowerCase();

  // Background update check (async, non-blocking)
  // Skip for update command and offline mode
  if (cmd !== "update" && !args.offline) {
    checkForUpdatesInBackground();
  }

  if (cmd === "skills") {
    listSkills();
    return;
  }

  if (cmd === "versions") {
    const skill = normalize(args.positionals[0] || args.skill || DEFAULT_SKILL);
    listVersions(skill);
    return;
  }

  if (cmd === "init") {
    runInit(args);
    return;
  }

  if (cmd === "update") {
    runUpdate(args).catch(() => {
      printError("Failed to check for updates. Check your internet connection.");
    });
    return;
  }

  printHelp();
}

main();

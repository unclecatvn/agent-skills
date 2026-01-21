#!/usr/bin/env node
"use strict";

const fs = require("fs");
const path = require("path");

const PACKAGE_ROOT = path.join(__dirname, "..");
const SOURCE_ROOT = path.join(PACKAGE_ROOT, "odoo");

const DEFAULT_AI = "cursor";
const DEFAULT_VERSION = "18.0";

function printHelp() {
  const text = `
odoo-cli - Install Odoo AI agent docs by version

Usage:
  odoo-cli init --ai <assistant> --version <odoo-version>
  odoo-cli versions
  odoo-cli help

Options:
  --ai <assistant>        cursor | claude | docs | all
  --version <version>     Odoo version (default: ${DEFAULT_VERSION})
  --dest <path>           Destination directory (default: current directory)
  --force                 Overwrite existing files
  --dry-run               Show what would be copied
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

function listVersions() {
  if (!fs.existsSync(SOURCE_ROOT)) {
    printError(`Missing source directory: ${SOURCE_ROOT}`);
    process.exit(1);
  }
  const versions = fs
    .readdirSync(SOURCE_ROOT, { withFileTypes: true })
    .filter((entry) => entry.isDirectory())
    .map((entry) => entry.name)
    .sort();

  if (versions.length === 0) {
    console.log("No Odoo versions found.");
    return;
  }

  console.log("Available Odoo versions:");
  for (const v of versions) console.log(`- ${v}`);
}

function resolveVersionDir(version) {
  const dir = path.join(SOURCE_ROOT, version);
  if (!fs.existsSync(dir)) {
    printError(`Odoo version not found: ${version}`);
    console.log("");
    listVersions();
    process.exit(1);
  }
  return dir;
}

function ensureDir(target) {
  fs.mkdirSync(target, { recursive: true });
}

function shouldCopyFile(fileName) {
  return true;
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
    if (!shouldCopyFile(entry.name)) continue;
    copyFile(sourcePath, destPath, options);
  }
}

function normalizeAi(value) {
  return String(value || "").toLowerCase().trim();
}

function parseArgs(argv) {
  const args = {
    command: null,
    ai: null,
    version: DEFAULT_VERSION,
    dest: process.cwd(),
    force: false,
    dryRun: false,
  };

  const tokens = argv.slice(2);
  args.command = tokens[0] || "help";

  for (let i = 1; i < tokens.length; i += 1) {
    const token = tokens[i];
    if (token === "--ai") {
      args.ai = tokens[i + 1];
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
    if (token === "-V" || token === "--cli-version") {
      console.log(getPackageVersion());
      process.exit(0);
    }
    if (token === "-h" || token === "--help") {
      args.command = "help";
    }
  }

  return args;
}

function installCursor(versionDir, destRoot, options) {
  const targetDir = path.join(destRoot, ".cursor", "rules", "odoo", options.version);
  const rename = (name, isDir) => {
    if (isDir) return name;
    if (name.endsWith(".md")) return `${name.slice(0, -3)}.mdc`;
    return name;
  };
  copyDir(versionDir, targetDir, options, rename);
  return targetDir;
}

function installDocs(versionDir, destRoot, options) {
  const targetDir = path.join(destRoot, "docs", "odoo", options.version);
  copyDir(versionDir, targetDir, options, null);
  return targetDir;
}

function installClaude(versionDir, destRoot, options) {
  const claudeSrc = path.join(versionDir, "CLAUDE.md");
  const skillSrc = path.join(versionDir, "SKILL.md");
  const claudeDest = path.join(destRoot, "CLAUDE.md");
  const skillDest = path.join(destRoot, "SKILL.md");
  let changed = false;
  if (fs.existsSync(claudeSrc)) {
    changed = copyFile(claudeSrc, claudeDest, options) || changed;
  }
  if (fs.existsSync(skillSrc)) {
    changed = copyFile(skillSrc, skillDest, options) || changed;
  }
  return changed;
}

function runInit(args) {
  const ai = normalizeAi(args.ai || DEFAULT_AI);
  const versionDir = resolveVersionDir(args.version);

  const valid = new Set(["cursor", "claude", "docs", "all"]);
  if (!valid.has(ai)) {
    printError(`Unknown --ai value: ${ai}`);
    printHelp();
    process.exit(1);
  }

  const results = [];
  if (ai === "cursor" || ai === "all") {
    const target = installCursor(versionDir, args.dest, args);
    results.push(`cursor -> ${target}`);
  }
  if (ai === "docs" || ai === "all") {
    const target = installDocs(versionDir, args.dest, args);
    results.push(`docs -> ${target}`);
  }
  if (ai === "claude" || ai === "all") {
    installClaude(versionDir, args.dest, args);
    results.push(`claude -> ${path.join(args.dest, "CLAUDE.md")}`);
    results.push(`claude -> ${path.join(args.dest, "SKILL.md")}`);
  }

  if (args.dryRun) {
    console.log("Dry run. Planned installs:");
  } else {
    console.log("Install complete:");
  }
  for (const line of results) console.log(`- ${line}`);
}

function main() {
  const args = parseArgs(process.argv);
  const cmd = normalizeAi(args.command);

  if (cmd === "versions") {
    listVersions();
    return;
  }

  if (cmd === "init") {
    runInit(args);
    return;
  }

  printHelp();
}

main();

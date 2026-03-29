#!/usr/bin/env node
"use strict";

const fs = require("fs");
const path = require("path");

const repoRoot = path.resolve(__dirname, "..");
const sourceRoot = path.join(repoRoot, "skills");
const mirrorRoot = path.join(repoRoot, ".agents", "skills");

function usage() {
  console.error(
    "Usage: node scripts/sync-codex-skills.js --write | --check"
  );
}

function normalize(relPath) {
  return relPath.split(path.sep).join("/");
}

function listSkillDirs(root) {
  if (!fs.existsSync(root)) {
    return [];
  }
  return fs
    .readdirSync(root, { withFileTypes: true })
    .filter((entry) => entry.isDirectory())
    .map((entry) => entry.name)
    .sort();
}

function listFiles(root) {
  const files = [];

  function walk(currentDir, relativeDir) {
    const entries = fs.readdirSync(currentDir, { withFileTypes: true });
    entries.sort((a, b) => a.name.localeCompare(b.name));
    for (const entry of entries) {
      const nextRelative = relativeDir
        ? path.join(relativeDir, entry.name)
        : entry.name;
      const nextFull = path.join(currentDir, entry.name);
      if (entry.isDirectory()) {
        walk(nextFull, nextRelative);
      } else {
        files.push(normalize(nextRelative));
      }
    }
  }

  if (fs.existsSync(root)) {
    walk(root, "");
  }

  return files;
}

function fileBuffersEqual(a, b) {
  const left = fs.readFileSync(a);
  const right = fs.readFileSync(b);
  return left.equals(right);
}

function ensureDir(dirPath) {
  fs.mkdirSync(dirPath, { recursive: true });
}

function writeMirror() {
  ensureDir(mirrorRoot);

  const sourceSkills = listSkillDirs(sourceRoot);
  const mirrorSkills = listSkillDirs(mirrorRoot);

  for (const staleSkill of mirrorSkills) {
    if (!sourceSkills.includes(staleSkill)) {
      fs.rmSync(path.join(mirrorRoot, staleSkill), {
        recursive: true,
        force: true,
      });
    }
  }

  for (const skillName of sourceSkills) {
    const from = path.join(sourceRoot, skillName);
    const to = path.join(mirrorRoot, skillName);
    fs.rmSync(to, { recursive: true, force: true });
    fs.cpSync(from, to, { recursive: true });
  }

  console.log(`Mirrored ${sourceSkills.length} skill(s) into .agents/skills.`);
}

function checkMirror() {
  const sourceSkills = listSkillDirs(sourceRoot);
  const mirrorSkills = listSkillDirs(mirrorRoot);
  const errors = [];

  if (!fs.existsSync(mirrorRoot)) {
    errors.push("Missing .agents/skills directory.");
  }

  for (const skillName of sourceSkills) {
    if (!mirrorSkills.includes(skillName)) {
      errors.push(`Missing mirrored skill: ${skillName}`);
      continue;
    }

    const sourceSkillDir = path.join(sourceRoot, skillName);
    const mirrorSkillDir = path.join(mirrorRoot, skillName);
    const sourceFiles = listFiles(sourceSkillDir);
    const mirrorFiles = listFiles(mirrorSkillDir);

    for (const file of sourceFiles) {
      if (!mirrorFiles.includes(file)) {
        errors.push(`Missing mirrored file: ${skillName}/${file}`);
        continue;
      }
      const sourceFile = path.join(sourceSkillDir, file);
      const mirrorFile = path.join(mirrorSkillDir, file);
      if (!fileBuffersEqual(sourceFile, mirrorFile)) {
        errors.push(`Content mismatch: ${skillName}/${file}`);
      }
    }

    for (const file of mirrorFiles) {
      if (!sourceFiles.includes(file)) {
        errors.push(`Stale mirrored file: ${skillName}/${file}`);
      }
    }
  }

  for (const skillName of mirrorSkills) {
    if (!sourceSkills.includes(skillName)) {
      errors.push(`Stale mirrored skill: ${skillName}`);
    }
  }

  if (errors.length) {
    for (const error of errors) {
      console.error(error);
    }
    process.exit(1);
  }

  console.log("Codex skill mirror is in sync.");
}

function main() {
  const mode = process.argv[2];
  if (!mode || !["--write", "--check"].includes(mode)) {
    usage();
    process.exit(1);
  }

  if (mode === "--write") {
    writeMirror();
    return;
  }

  checkMirror();
}

main();

#!/usr/bin/env node

const fs = require("fs");
const path = require("path");

const repoRoot = path.resolve(__dirname, "..");

function exists(relativePath) {
  return fs.existsSync(path.join(repoRoot, relativePath));
}

function read(relativePath) {
  return fs.readFileSync(path.join(repoRoot, relativePath), "utf8");
}

function assert(condition, message) {
  if (!condition) {
    throw new Error(message);
  }
}

function assertExists(relativePath) {
  assert(exists(relativePath), `Missing required path: ${relativePath}`);
}

function assertContains(relativePath, expected) {
  const content = read(relativePath);
  assert(
    content.includes(expected),
    `Expected ${relativePath} to contain: ${expected}`
  );
}

function main() {
  const allSkills = [
    "brainstorming",
    "code-review",
    "dtg-base",
    "mcp-builder",
    "odoo-18.0",
    "odoo-19.0",
    "odoo-owl",
    "odoo-owl-testing",
    "odoo-webclient-extension",
    "payment-integration",
    "writing-skills",
  ];

  const standaloneSkills = [
    {
      base: "skills/odoo-owl",
      refs: [
        "references/component-basics.md",
        "references/qweb-templates.md",
        "references/assets-and-modules.md",
        "references/generic-components.md",
        "references/standalone-vs-webclient.md",
      ],
      scripts: ["scripts/scaffold_component.py"],
    },
    {
      base: "skills/odoo-webclient-extension",
      refs: [
        "references/registries.md",
        "references/client-actions.md",
        "references/services-and-hooks.md",
        "references/patching.md",
        "references/extension-checklist.md",
      ],
      scripts: ["scripts/scaffold_client_action.py"],
    },
    {
      base: "skills/odoo-owl-testing",
      refs: [
        "references/test-setup.md",
        "references/hoot.md",
        "references/web-test-helpers.md",
        "references/mock-server.md",
        "references/testing-checklist.md",
      ],
      scripts: ["scripts/scaffold_test.py"],
    },
  ];

  assert(!exists("skills/odoo"), "Old nested skills/odoo layout should not remain");
  assertExists("AGENTS.md");
  assertExists(".agents/skills");

  standaloneSkills.forEach((skill) => {
    assertExists(skill.base);
    assertExists(path.join(skill.base, "SKILL.md"));
    assertExists(path.join(skill.base, "AGENTS.md"));
    assertExists(path.join(skill.base, "CLAUDE.md"));
    skill.refs.forEach((relativePath) => {
      assertExists(path.join(skill.base, relativePath));
    });
    skill.scripts.forEach((relativePath) => {
      assertExists(path.join(skill.base, relativePath));
    });
    assert(
      !exists(path.join(skill.base, "agents", "openai.yaml")),
      `Legacy agents/openai.yaml should be removed from ${skill.base}`
    );
  });

  allSkills.forEach((skillName) => {
    assertExists(path.join("skills", skillName, "SKILL.md"));
    assertExists(path.join(".agents", "skills", skillName, "SKILL.md"));
  });

  [
    "README.md",
    "skills/odoo-18.0/SKILL.md",
    "skills/odoo-19.0/SKILL.md",
    "skills/odoo-18.0/references/odoo-18-owl-guide.md",
    "skills/odoo-19.0/references/odoo-19-owl-guide.md",
  ].forEach((relativePath) => {
    assertContains(relativePath, "skills/odoo-owl/");
    assertContains(relativePath, "skills/odoo-webclient-extension/");
    assertContains(relativePath, "skills/odoo-owl-testing/");
  });

  [
    "README.md",
    "AGENTS.md",
  ].forEach((relativePath) => {
    assertContains(relativePath, "Codex");
  });

  assertContains("README.md", ".agents/skills/");
  assertContains("README.md", "Codex App");
  assertContains("README.md", "Codex CLI");
  assertContains("README.md", "Codex IDE Extension");

  const plugin = JSON.parse(read(".claude-plugin/plugin.json"));
  assert(
    plugin.homepage === "https://github.com/milzamsz/odoo-agents",
    "Claude plugin homepage should point to milzamsz/odoo-agents"
  );
  assert(
    plugin.repository.url === "https://github.com/milzamsz/odoo-agents.git",
    "Claude plugin repository URL should point to milzamsz/odoo-agents.git"
  );
  assert(
    plugin.components.skills.includes("skills/odoo-owl/SKILL.md"),
    "Claude plugin metadata should include the odoo-owl skill"
  );

  const marketplace = JSON.parse(read(".claude-plugin/marketplace.json"));
  assert(
    marketplace.marketplaces["odoo-agents"].source.repo === "milzamsz/odoo-agents",
    "Marketplace metadata should point to milzamsz/odoo-agents"
  );

  console.log("Skill layout smoke test passed.");
}

try {
  main();
} catch (error) {
  console.error(error.message);
  process.exit(1);
}

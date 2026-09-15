#!/usr/bin/env node
/**
 * Structural validation for the agent-skills repo.
 *
 * Checks:
 *   1. Every skills/* and agents/* folder has a SKILL.md with
 *      valid `name` and `description` in its YAML frontmatter.
 *   2. Every component path listed in .claude-plugin/plugin.json exists
 *      and the manifest uses the field types Claude Code loads.
 *   2b. package.json, plugin.json and marketplace.json agree on the version.
 *   2c. The sudo() naming grep from the review agent flags exactly the
 *      tagged lines in tests/fixtures/sudo_naming.py.
 *   2d. The odoo-workflow Step 1 grep commands still appear verbatim in
 *      skills/odoo-workflow/SKILL.md and flag exactly the tagged lines in
 *      tests/fixtures/odoo_workflow/.
 *   3. package.json version has a matching section in CHANGELOG.md
 *   4. Versioned Odoo testing guides contain the generic testing guidance.
 *      (skipped if the version is still 0.x or under [Unreleased]).
 *
 * Exit code 0 on success, 1 on any failure.
 */
const fs = require("fs");
const path = require("path");
const { execSync } = require("child_process");

const ROOT = path.resolve(__dirname, "..");
const RED = "\x1b[31m";
const GREEN = "\x1b[32m";
const YELLOW = "\x1b[33m";
const RESET = "\x1b[0m";

const errors = [];
const warnings = [];

function fail(msg) {
  errors.push(msg);
  console.log(`${RED}✗${RESET} ${msg}`);
}

function warn(msg) {
  warnings.push(msg);
  console.log(`${YELLOW}!${RESET} ${msg}`);
}

function ok(msg) {
  console.log(`${GREEN}✓${RESET} ${msg}`);
}

function readFrontmatter(filePath) {
  const text = fs.readFileSync(filePath, "utf8");
  if (!text.startsWith("---")) return null;
  const end = text.indexOf("\n---", 3);
  if (end === -1) return null;
  const body = text.slice(3, end).replace(/^\r?\n/, "");
  const fields = {};
  for (const line of body.split(/\r?\n/)) {
    const m = /^([A-Za-z0-9_-]+)\s*:\s*(.*)$/.exec(line);
    if (m) fields[m[1]] = m[2].trim();
  }
  return fields;
}

function validateSkillDir(dir, label) {
  const entries = fs.readdirSync(dir, { withFileTypes: true });
  // A skill lives in <name>/SKILL.md; a plugin agent is a flat <name>.md
  // (the plugin loader does not scan agents/<name>/SKILL.md).
  const paths = [
    ...entries.filter((e) => e.isDirectory()).map((e) => path.join(dir, e.name, "SKILL.md")),
    ...entries
      .filter((e) => e.isFile() && e.name.endsWith(".md"))
      .map((e) => path.join(dir, e.name)),
  ];

  if (paths.length === 0) {
    warn(`${label}/ is empty`);
    return;
  }

  for (const skillPath of paths) {
    const rel = path.relative(ROOT, skillPath);
    if (!fs.existsSync(skillPath)) {
      fail(`missing ${rel}`);
      continue;
    }
    const fm = readFrontmatter(skillPath);
    if (!fm) {
      fail(`${rel}: no YAML frontmatter`);
      continue;
    }
    if (!fm.name) fail(`${rel}: frontmatter missing 'name'`);
    if (!fm.description) fail(`${rel}: frontmatter missing 'description'`);
    if (fm.name && fm.description) ok(rel);
  }
}

function validatePluginManifest() {
  const manifestPath = path.join(ROOT, ".claude-plugin", "plugin.json");
  if (!fs.existsSync(manifestPath)) {
    warn(".claude-plugin/plugin.json not found — skipping manifest check");
    return;
  }
  let manifest;
  try {
    manifest = JSON.parse(fs.readFileSync(manifestPath, "utf8"));
  } catch (err) {
    fail(`plugin.json: invalid JSON (${err.message})`);
    return;
  }

  // Component path fields per https://code.claude.com/docs/en/plugins-reference
  for (const kind of ["skills", "commands", "agents", "hooks", "outputStyles"]) {
    const value = manifest[kind];
    if (value === undefined) continue;
    const list = Array.isArray(value) ? value : typeof value === "string" ? [value] : [];
    for (const relPath of list) {
      if (!fs.existsSync(path.join(ROOT, relPath))) {
        fail(`plugin.json: ${kind} path does not exist: ${relPath}`);
      } else {
        ok(`plugin.json/${kind}: ${relPath}`);
      }
    }
  }
  if (typeof manifest.author === "string") {
    fail("plugin.json: author must be an object {name, email?, url?}");
  }
  if (manifest.repository !== undefined && typeof manifest.repository !== "string") {
    fail("plugin.json: repository must be a URL string");
  }
}

function validateVersionParity() {
  const read = (rel) => JSON.parse(fs.readFileSync(path.join(ROOT, rel), "utf8"));
  const marketplace = read(".claude-plugin/marketplace.json");
  const entry = (marketplace.plugins || []).find((p) => p.name === "agent-skills") || {};
  const versions = {
    "package.json": read("package.json").version,
    "plugin.json": read(".claude-plugin/plugin.json").version,
    "marketplace.json": entry.version,
  };
  const distinct = new Set(Object.values(versions));
  if (distinct.size === 1 && versions["package.json"]) {
    ok(`version ${versions["package.json"]} matches across package.json, plugin.json, marketplace.json`);
  } else {
    fail(`version mismatch: ${JSON.stringify(versions)}`);
  }
}

// Keep identical to the pipeline in agents/odoo-code-review/SKILL.md ("Security").
const SUDO_DETECTOR =
  "grep -nE '^[[:space:]]*[A-Za-z_][A-Za-z0-9_]*[[:space:]]*=[[:space:]]*[^=].*\\.sudo\\(' \"$FIXTURE\"" +
  " | grep -vE '^[0-9]+:[[:space:]]*[A-Za-z0-9_]*_sudo[[:space:]]*=' || true";

function validateSudoDetector() {
  const fixture = path.join(ROOT, "tests", "fixtures", "sudo_naming.py");
  if (!fs.existsSync(fixture)) {
    fail("missing tests/fixtures/sudo_naming.py");
    return;
  }
  const out = execSync(SUDO_DETECTOR, {
    encoding: "utf8",
    env: { ...process.env, FIXTURE: fixture },
  });
  const got = out.split("\n").filter(Boolean).map((l) => Number(l.split(":")[0]));
  const want = fs
    .readFileSync(fixture, "utf8")
    .split("\n")
    .map((line, i) => (line.includes("# FLAG") ? i + 1 : 0))
    .filter(Boolean);
  if (JSON.stringify(got) === JSON.stringify(want)) {
    ok(`sudo naming detector flags exactly lines ${want.join(",")} of the fixture`);
  } else {
    fail(`sudo naming detector: expected lines ${want.join(",")}, got ${got.join(",") || "none"}`);
  }
}

// Step 1 commands from skills/odoo-workflow/SKILL.md, verbatim. Placeholders are
// filled in for the fixture; the check fails if SKILL.md no longer contains the command.
const WORKFLOW_GREPS = [
  {
    tag: "model",
    cmd: `grep -rnE --include='*.py' "_name\\s*=\\s*([A-Za-z_]+\\s*=\\s*)?['\\"]MODEL['\\"]" $ROOTS`,
  },
  {
    tag: "inherit",
    cmd: `grep -rnE --include='*.py' "_inherit\\s*=.*['\\"]MODEL['\\"]" $ROOTS`,
  },
  {
    tag: "inherit-multi",
    cmd: `grep -rnE --include='*.py' -A12 "_inherit\\s*=\\s*[[(][^])]*$" $ROOTS | grep -E "['\\"]MODEL['\\"]"`,
  },
  {
    tag: "field",
    cmd: `grep -nE "^\\s+FIELD(\\s*:\\s*[A-Za-z_.]+)?\\s*=\\s*fields\\." MODEL_FILES`,
  },
  {
    tag: "view-inherit",
    cmd: `grep -rnE --include='*.xml' "name=['\\"]inherit_id['\\"] ref=['\\"](MODULE\\.)?VIEW['\\"]|inherit_id=['\\"](MODULE\\.)?VIEW['\\"]" $ROOTS`,
  },
];

function validateWorkflowGreps() {
  const skill = fs.readFileSync(path.join(ROOT, "skills", "odoo-workflow", "SKILL.md"), "utf8");
  const dir = path.join(ROOT, "tests", "fixtures", "odoo_workflow");
  const fixtures = ["models.py", "views.xml"].map((f) => path.join(dir, f));
  const tagged = (tag) =>
    fixtures.flatMap((file) =>
      fs
        .readFileSync(file, "utf8")
        .split("\n")
        .flatMap((line, i) => (new RegExp(`FLAG:${tag}(?![\\w-])`).test(line) ? [`${path.basename(file)}:${i + 1}`] : []))
    );

  for (const { tag, cmd } of WORKFLOW_GREPS) {
    if (!skill.includes(cmd)) {
      fail(`odoo-workflow: the ${tag} command in SKILL.md differs from the tested one`);
      continue;
    }
    const run = cmd
      .replace("MODEL_FILES", JSON.stringify(fixtures[0]))
      .replace(/MODEL/g, "x\\.thing")
      .replace("FIELD", "note")
      .replace(/MODULE/g, "sale")
      .replace(/VIEW/g, "view_order_form")
      .replace("$ROOTS", JSON.stringify(dir));
    const out = execSync(`${run} || true`, { encoding: "utf8" });
    const got = out
      .split("\n")
      .filter(Boolean)
      .map((l) => {
        const m = /^(?:.*?(models\.py|views\.xml)[:-])?(\d+)[:-]/.exec(l);
        return m ? `${m[1] || "models.py"}:${m[2]}` : l;
      });
    const want = tagged(tag);
    if (JSON.stringify([...new Set(got)].sort()) === JSON.stringify(want.sort())) {
      ok(`odoo-workflow ${tag} command flags exactly ${want.join(", ")}`);
    } else {
      fail(`odoo-workflow ${tag} command: expected ${want.join(", ")}, got ${got.join(", ") || "none"}`);
    }
  }
}

function validateChangelog() {
  const pkgPath = path.join(ROOT, "package.json");
  const changelogPath = path.join(ROOT, "CHANGELOG.md");
  if (!fs.existsSync(pkgPath) || !fs.existsSync(changelogPath)) return;

  const version = JSON.parse(fs.readFileSync(pkgPath, "utf8")).version;
  if (!version) return;

  const changelog = fs.readFileSync(changelogPath, "utf8");
  const re = new RegExp(
    `^##\\s+\\[?v?${version.replace(/\./g, "\\.")}\\]?\\s*$`,
    "m"
  );
  if (re.test(changelog)) {
    ok(`CHANGELOG.md has section for v${version}`);
  } else {
    fail(
      `CHANGELOG.md: missing section for v${version} (expected '## [${version}]')`
    );
  }
}

function validateVersionedTestingGuides() {
  const expectedFreezeImports = {
    "16.0": "from freezegun import freeze_time",
    "17.0": "from freezegun import freeze_time",
    "18.0": "from odoo.tests.common import freeze_time",
    "19.0": "from odoo.tests.common import freeze_time",
  };
  const requiredPatterns = [
    /regression tests? for fixes|regression and error-path coverage/i,
    /lowest practical permissions/i,
    /subtests? without sharing mutable state|not rolled back between `?subTest/i,
    /with_env\(self\.env\)/i,
    /datetime\.now\(\).*datetime\.today\(\)|fixed dates/i,
    /mock external services by default/i,
    /demo records/i,
    /coverage decreases/i,
  ];

  for (const [version, freezeImport] of Object.entries(expectedFreezeImports)) {
    const filePath = path.join(
      ROOT,
      `skills/odoo-${version}/references/odoo-${version.split(".")[0]}-testing-guide.md`
    );
    if (!fs.existsSync(filePath)) {
      fail(`missing versioned testing guide: ${path.relative(ROOT, filePath)}`);
      continue;
    }
    const content = fs.readFileSync(filePath, "utf8");
    for (const pattern of requiredPatterns) {
      if (!pattern.test(content)) {
        fail(`${path.relative(ROOT, filePath)}: missing generic testing guidance ${pattern}`);
      }
    }
    if (!content.includes(freezeImport)) {
      fail(`${path.relative(ROOT, filePath)}: missing version-correct freeze_time import`);
    }
    ok(`${path.relative(ROOT, filePath)} has generic testing guidance`);
  }
}

function main() {
  console.log("Validating skills/");
  validateSkillDir(path.join(ROOT, "skills"), "skills");

  console.log("\nValidating agents/");
  validateSkillDir(path.join(ROOT, "agents"), "agents");

  console.log("\nValidating plugin manifest");
  validatePluginManifest();

  console.log("\nValidating version parity");
  validateVersionParity();

  console.log("\nValidating sudo naming detector");
  validateSudoDetector();

  console.log("\nValidating odoo-workflow grep commands");
  validateWorkflowGreps();

  console.log("\nValidating CHANGELOG");
  validateChangelog();

  console.log("\nValidating versioned testing guides");
  validateVersionedTestingGuides();

  console.log("");
  if (errors.length > 0) {
    console.log(`${RED}${errors.length} error(s)${RESET}`);
    process.exit(1);
  }
  if (warnings.length > 0) {
    console.log(`${YELLOW}${warnings.length} warning(s)${RESET}`);
  }
  console.log(`${GREEN}All checks passed.${RESET}`);
}

main();

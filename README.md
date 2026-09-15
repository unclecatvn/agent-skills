<div align="center">

![Agent Skills — version-aware expertise for Odoo development, supporting Odoo 16–19](lib/image/hero.png)

# Agent Skills

**Version-aware expertise for Odoo development.**

Reference packs, development workflows, and specialized reviewers for AI-assisted work on Odoo 16–19.

[![npm version](https://img.shields.io/npm/v/@unclecat/agent-skills-cli?style=flat-square&color=714B67)](https://www.npmjs.com/package/@unclecat/agent-skills-cli)
[![MIT license](https://img.shields.io/badge/license-MIT-714B67?style=flat-square)](LICENSE)
[![CI](https://github.com/unclecatvn/agent-skills/actions/workflows/ci.yml/badge.svg)](https://github.com/unclecatvn/agent-skills/actions/workflows/ci.yml)

[Quick start](#quick-start) · [Explore the toolkit](#explore-the-toolkit) · [Example workflow](#example-workflow) · [Odoo versions](#odoo-versions) · [Installation notes](#installation-notes) · [Contributing](#contributing)

</div>

## Built for real Odoo projects

Give your coding assistant a focused reference library instead of repeating framework context in every conversation.

- **Use the right conventions.** Separate Odoo 16, 17, 18, and 19 packs keep version-specific guidance together.
- **Trace before changing code.** The Odoo workflow asks for source citations and a Context Brief before implementation.
- **Review with framework context.** Dedicated agent instructions cover execution tracing and review of correctness, security, and performance.
- **Carry work through to delivery.** Supporting skills cover review feedback, Odoo commits, diagrams, and presentations.

These are documentation and assistant instructions, not an Odoo runtime extension or an automatic enforcement system. Results depend on the host assistant, available project source, and the checks you actually run.

## Quick start

Choose **one installation route** for your setup. Use Node.js **18+** for the bundled CLI; the Claude Code plugin requires Claude Code.

### Claude Code plugin — skills and agents together

Run in your terminal:

```bash
claude plugin marketplace add unclecatvn/agent-skills
claude plugin install agent-skills@unclecat-agent-skills --scope project
```

The plugin exposes this repository's skills and three agents through Claude Code's plugin layout. Project scope records the installation for the project; omit `--scope project` for the default user scope. The top-level `rules/` documents are guidance to integrate separately, not automatically activated plugin rules.

See the [marketplace manifest](.claude-plugin/marketplace.json) and [official plugin reference](https://code.claude.com/docs/en/plugins-reference).

### Skills installer — choose skills for your assistant

```bash
npx skills add unclecatvn/agent-skills
```

Use the installer's selection flow to choose skills and your target assistant. This route installs skill packages; it is not an installation of the repository's standalone agents or rules. Available targets and installer options are maintained by the [upstream skills CLI](https://github.com/vercel-labs/skills#readme).

### Bundled CLI — copy one pack to a known location

```bash
# List installable packs
npx @unclecat/agent-skills-cli versions skills

# Install the Odoo 18 pack for Cursor
npx @unclecat/agent-skills-cli init --ai cursor --skill skills --version odoo-18.0

# Add the workflow pack for Claude Code
npx @unclecat/agent-skills-cli init --ai claude --skill skills --version odoo-workflow
```

Here, `--skill skills` names the repository directory, while `--version` selects a pack inside it, including non-versioned packs such as `odoo-workflow`. Pass both explicitly: the CLI's legacy defaults do not match this repository layout.

The CLI copies the selected pack, not the standalone agents or rules. See [installation notes](#installation-notes) for output paths and limitations.

## Explore the toolkit

![Three parts of the toolkit: Skills for versioned references and workflows, Agents for tracing and review, and Rules for coding and security guidance](lib/image/overview.png)

### Skills — 10 focused packs

| Pack | Purpose |
| --- | --- |
| [Odoo 16.0](skills/odoo-16.0/) | Version-specific development references and API highlights. |
| [Odoo 17.0](skills/odoo-17.0/) | Version-specific development references and API highlights. |
| [Odoo 18.0](skills/odoo-18.0/) | Version-specific development references and API highlights. |
| [Odoo 19.0](skills/odoo-19.0/) | Version-specific development references and API highlights. |
| [Odoo Workflow](skills/odoo-workflow/) | Trace-first procedure, Context Brief, and completion checks for Odoo changes. |
| [Odoo Commit](skills/odoo-commit/) | Odoo-style commit messages, explicit staging, and commit preparation. |
| [Code Review](skills/code-review/) | Requesting reviews, handling feedback, and evidence-based verification. |
| [DTG Base](skills/dtg-base/) | References for DTGBase utilities: dates, timezones, batches, barcodes, text, and files. |
| [Flow Diagram](skills/flow-diagram/) | Interactive HTML/SVG architecture and flow diagrams. |
| [Slide](skills/slide/) | Self-contained HTML/React presentation decks. |

Each Odoo pack covers models, fields, decorators, views, OWL, security, controllers, actions, data, reports, testing, performance, transactions, migrations, translations, mixins, manifests, and development workflow. Start with its `SKILL.md` index and `references/api-highlights.md`.

### Agents — 3 specialized roles

| Agent | Purpose |
| --- | --- |
| [Odoo Code Tracer](agents/odoo-code-tracer.md) | Follow entry points, method overrides, inheritance, and side effects in the project source. |
| [Odoo Code Review](agents/odoo-code-review.md) | Assess Odoo changes using version-aware criteria and a structured, scored report. |
| [Planner](agents/planner.md) | Break down a feature into implementation steps. |

### Rules — 2 reference documents

- [Coding style](rules/coding-style.md): naming, imports, and code organization.
- [Security](rules/security.md): security practices to incorporate into project instructions and review.

## Example workflow

After installing the matching Odoo pack and workflow skill, give your assistant a scoped task:

> This project uses Odoo 18. Use the Odoo workflow to add a field to the sale order form. First trace the existing model and inherited views, then produce a Context Brief with file-and-line citations. Propose the smallest change, implement it, and run the relevant tests. Review the diff for access control, translations, and Odoo 18 conventions.

The intended sequence is:

1. **Choose the version:** read the project's version configuration and matching reference pack.
2. **Understand the source:** inspect models, overrides, views, and tests; use the tracer if installed.
3. **Implement deliberately:** agree on a minimal change based on the Context Brief.
4. **Verify and review:** run relevant project tests and inspect the diff; use the reviewer if installed.

Ask for evidence of executed checks and any remaining limitations. Installing a pack does not run tests or guarantee correct code.

## Odoo versions

Install the pack that matches your project: **16.0, 17.0, 18.0, or 19.0**. Review an existing `.odoo-version` before changing it; for a new file, set its contents to the project's major version, for example:

```text
18.0
```

The review and tracer instructions resolve the version from:

1. An explicit invocation argument, such as `odoo_version: "18.0"`.
2. Project configuration: `.odoo-version`, `.claude/odoo.json` (`odoo_version`), `package.json` (`odoo.version`), or `pyproject.toml` (`tool.odoo.version`).
3. The dominant major version in workspace `__manifest__.py` files.
4. A stated fallback to `19.0` if no version is found.

**The workflow skill is stricter:** it also reads the project `CLAUDE.md` and `version_info` in the core `odoo/release.py`, ignores short addon manifest versions such as `'1.2'`, and asks when the version is unknown instead of silently defaulting. Set the version explicitly to avoid ambiguity. Installing one pack does not automatically install other versions referenced by agent instructions.

### Add project instructions without replacing existing rules

Merge the relevant sections of the [Odoo project template](skills/odoo-workflow/templates/CLAUDE.md) into your existing `CLAUDE.md`; do not overwrite the file. Adjust the Odoo version, installed skill names, and addon paths to your project. Review the template's commit and attribution conventions before adopting them.

## Installation notes

### Bundled CLI targets

Paths below are relative to the destination project. `PACK` stands for the selected directory, such as `odoo-18.0`.

| Target | Files written by the CLI |
| --- | --- |
| `cursor` | `.shared/skills/PACK/` and `.cursor/commands/skills.md` |
| `claude` | `.claude/skills/skills/PACK/` |
| `antigravity` | `.shared/skills/PACK/` and `.agent/workflows/skills.md` |
| `kiro` | `.shared/skills/PACK/` and `.kiro/steering/skills.md` |
| `docs` | `docs/skills/PACK/` |
| `all` | All five destinations above. |

This table describes file-copy behavior, not a guarantee of native skill discovery in every host version. For Claude Code's plugin discovery, use the plugin route above. For other assistants, use the skills installer's supported targets or explicitly supply the copied documentation as context.

- Run from the destination project, or set `--dest /path/to/project`.
- Existing files are preserved unless you pass `--force`. Review changes before overwriting.
- Cursor, Antigravity, and Kiro use a shared entry filename, `skills.md`. Installing another pack preserves the existing entry unless forced; forcing it repoints that entry to the newly selected pack. The pack directories remain separate.
- `--offline` skips the CLI's update check; it does not make `npx` package acquisition offline. `init` copies bundled files.
- Preview local copy operations with `--dry-run --offline`:

```bash
npx @unclecat/agent-skills-cli init --ai cursor --skill skills --version odoo-18.0 --dry-run --offline
```

## Contributing

Help improve version-specific references, add reproducible examples, refine review instructions, or report gaps through [issues](https://github.com/unclecatvn/agent-skills/issues).

Before opening a pull request, run from a local checkout:

```bash
npm test
```

This validates skill and agent structure, plugin paths, version consistency, changelog coverage, selected reference checks, and the `odoo-workflow` grep commands against fixtures. It does not execute Odoo application tests. CI also runs a baseline-aware SkillSpector scan; see the [CI workflow](.github/workflows/ci.yml).

If you change those grep commands, also run them against real Odoo source, once per checkout you have:

```bash
ODOO_ROOT=/path/to/odoo tests/odoo-workflow-greps.sh
```

Keep new skills under `skills/` with a `SKILL.md` entry point. Keep version-specific changes in their matching Odoo pack and include evidence for behavioral claims.

## Releases and license

See the [changelog](CHANGELOG.md) for repository changes and the [npm package](https://www.npmjs.com/package/@unclecat/agent-skills-cli) for published CLI versions. Merging a version bump to `main` tags the release, publishes the GitHub release notes from the changelog, and publishes the CLI to npm.

Released under the [MIT license](LICENSE). This is an independent community project, not an official Odoo product.

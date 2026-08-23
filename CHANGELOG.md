# Changelog

All notable changes to this project will be documented in this file.

## [1.0.14]

### Release Description
Aligned the Odoo 16–19 skill packs with the official Odoo coding guidelines, so the agents now recommend upstream-sanctioned module structure, naming, and formatting instead of ad-hoc conventions — while keeping each version's runtime APIs intact (Odoo 17 stays on `<tree>` / `group_operator` / `_sql_constraints`; Odoo 18/19 use `<list>` / `aggregator`; Odoo 19 keeps `models.Constraint`). Also unblocks CI: the security-scan job now pins SkillSpector instead of tracking upstream `HEAD`, which had silently moved to 2.9.6 and broken the accepted-findings baseline.

### Added
- Coding-convention routing in `skills/odoo-16.0/`, `skills/odoo-17.0/`, `skills/odoo-18.0/`, `skills/odoo-19.0/` (`SKILL.md`, `AGENTS.md`, `CLAUDE.md`) so the agents load guideline coverage alongside the version pack.
- Guideline sections across the per-version reference guides: module structure and filenames, XML IDs and formatting, reports, security, static-asset layout, Python/ORM patterns, translations, and transactions.
- `tests/test-skills.js` — validator coverage for the versioned testing guidance.

### Changed
- `agents/odoo-code-review/SKILL.md` cites the coding guidelines during review.
- `skills/odoo-*/references/odoo-*-testing-guide.md` — reworked versioned testing guidance.
- `.github/workflows/ci.yml` — `skill-security-scan` pins `skillspector@v2.9.6`; regenerating the baseline is documented next to the pin.
- `.skillspector-baseline.yaml` — regenerated in version-2 format for SkillSpector 2.9.6 (101 accepted findings, all static-analysis false positives in reference documentation).

### Removed
- `docs/superpowers/plans/2026-06-20-odoo-16-review-fixes.md` — obsolete planning file.

### Fixed
- CI `skill-security-scan` no longer fails on every run. Installing SkillSpector from an unpinned Git `HEAD` picked up 2.9.6, which rejects version-1 baselines (`unsupported baseline version 1; expected 2`) and re-scored the remaining findings above the gate.

### Notes
- Ships #24.
- Thank you to **Piruin Panichphol** ([@piruin](https://github.com/piruin)) for the Odoo 16–19 coding-guidelines work in #24 — a second contribution after the Odoo Commit skill in 1.0.13.
- Source for the guidelines: [Odoo coding guidelines](https://raw.githubusercontent.com/odoo/documentation/17.0/content/contributing/development/coding_guidelines.rst).
- Bump the SkillSpector pin deliberately from now on; regenerate the baseline in the same commit.

## [1.0.13]

### Release Description
Added two skill packs for day-to-day agent workflows: interactive HTML+SVG flow/architecture diagrams (`flow-diagram`), and Odoo-style commit guidance (`odoo-commit`) so assistants stage, amend, and message commits the way Odoo projects expect. Flow diagrams ship as one self-contained page with zoom/pan, click-to-highlight flows (traveling dots + destination ping), light/dark theme, collision checkers, a layout-patterns guide, and a freight-logistics reference example. Odoo Commit covers amend-vs-new-commit decisions, explicit staging, `[TAG] module:` subjects, and `git commit -F` before opening a PR.

### Added
- `skills/flow-diagram/` — interactive HTML+SVG flow/architecture diagrams: 2-pane layout, zoom/pan, click-to-highlight flows with traveling dots and destination ping, light/dark theme, offline + browser collision checkers, layout-pattern guide, and freight-logistics reference example.
- `skills/odoo-commit/` — Odoo commit workflow: `[TAG] module:` subjects, amend-vs-new-commit decisions, explicit staging, `git commit -F`, and local history cleanup before PRs.

### Changed
- `.claude-plugin/plugin.json` and `README.md` register `flow-diagram` and `odoo-commit`; README inventory, stats, and current-release pointer updated for 1.0.13.
- `.skillspector-baseline.yaml` extended for flow-diagram static-analysis findings accepted for this release.

### Notes
- Ships #21 (`odoo-commit`) and #22 (`flow-diagram`).
- Thank you to **Piruin Panichphol** ([@piruin](https://github.com/piruin)) for contributing the Odoo Commit skill.

## [1.0.12]

### Release Description
Rewrote the README to reflect the current repository: seven skill packs, version-aware Odoo agents (16–19), accurate install paths, and up-to-date project structure.

### Changed
- `README.md` — updated tagline, stats (~57k lines), and skill inventory; removed references to skills no longer in the repo (payment-integration, brainstorming, writing-skills, mcp-builder).
- `README.md` — documented three install methods: Cursor Skills (`npx skills add`), CLI (`@unclecat/agent-skills-cli init`), and Claude Code plugin.
- `README.md` — added Odoo version-targeting section with a 16/17/18+ comparison table; corrected Odoo 16 modifier guidance (`attrs`/`states`, not direct expressions).
- `README.md` — expanded project structure, contributing notes (SkillSpector baseline, changelog guard), and supported IDE matrix.

### Notes
- Documentation-only release; no skill pack or agent logic changes.

## [1.0.11]

### Release Description
Added the `odoo-16.0` skill pack so the Odoo agents resolve 16.0 explicitly instead of applying 17/18/19-only guidance to Odoo 16 code.

### Added
- `skills/odoo-16.0/` — full Odoo 16 reference pack: `SKILL.md`, `AGENTS.md`, `CLAUDE.md`, `references/api-highlights.md`, and version-specific guides for actions, controllers, data files, decorators, development workflow, fields, manifest, migrations, mixins, models, OWL, performance, reports, security, testing, transactions, translations, and views.

### Changed
- `.claude-plugin` metadata and `README.md` register the Odoo 16.0 pack.
- `agents/odoo-code-review/SKILL.md` and `agents/odoo-code-tracer/SKILL.md` are now version-aware for **16 / 17 / 18 / 19** (resolution order and supported-versions list include 16.0).

### Notes
- Supported version matrix: **16.0, 17.0, 18.0, 19.0**.
- Adds #15.

## [1.0.10]

### Release Description
Made the Odoo agents version-aware (17 / 18 / 19) so they load the right reference pack automatically instead of always citing Odoo 18 APIs. Also fixed broken guide paths in `odoo-code-review`.

### Added
- `skills/odoo-17.0/references/api-highlights.md`, `skills/odoo-18.0/references/api-highlights.md`, `skills/odoo-19.0/references/api-highlights.md` — per-version, version-distinguishing rulesets (list tag, attrs syntax, aggregator parameter, optional `_name` in v19, etc.) that the agents load alongside the general checklist.
- Target-version resolution step in `agents/odoo-code-review/SKILL.md` and `agents/odoo-code-tracer/SKILL.md` with a four-level fallback: explicit argument → project config (`.odoo-version`, `.claude/odoo.json`, `package.json`, `pyproject.toml`) → `__manifest__.py` heuristic → default to latest (`19.0`).
- README section "Targeting an Odoo version" documenting the resolution order.

### Changed
- `agents/odoo-code-review/SKILL.md` rewritten version-neutral. Every guide reference now uses `skills/odoo-${ODOO_VERSION}/references/odoo-${ODOO_MAJOR}-*-guide.md` placeholders resolved at invocation time.
- `agents/odoo-code-tracer/SKILL.md` generalised: agent description, "Specific Patterns" section, and "Related Skills" no longer hard-code Odoo 18.
- `README.md` Odoo example comment generalised from "Odoo 18 conventions" to "Odoo conventions (17 / 18 / 19)" since the pattern is identical across supported versions.

### Fixed
- `agents/odoo-code-review/SKILL.md` guide paths: `skills/odoo/18.0/` → `skills/odoo-18.0/`, and `dev/odoo-18-*-guide.md` → `references/odoo-18-*-guide.md` (the original paths did not exist in the repo).

### Notes
- Supported version matrix: **17.0, 18.0, 19.0**. Older versions are out of scope.
- Addresses #7.

## [1.0.9]

### Release Description
Added the `odoo-17.0` skill pack: 18 reference guides plus `SKILL.md`, `CLAUDE.md`, `AGENTS.md`, all verified against the Odoo 17 source tree.

### Added
- New skill pack `skills/odoo-17.0/` covering Odoo 17 development:
  - `SKILL.md`, `CLAUDE.md`, `AGENTS.md` (master index, Claude Code guide, IDE setup)
  - 18 reference guides in `skills/odoo-17.0/references/`: actions, controller, data, decorator, development, field, manifest, migration, mixins, model, owl, performance, reports, security, testing, transaction, translation, view
- Documented v17-specific conventions that differ from v18/v19:
  - `<tree>` list tag (v18 renamed to `<list>`)
  - Direct expression attributes `invisible="state == 'done'"` — v17 removed the legacy `attrs="{...}"` and `states="..."` forms (the view validator raises `ValidationError` since 17.0)
  - `group_operator=` field aggregation (v18 renamed to `aggregator=`)
  - `_sql_constraints` tuple form (v19 introduced `models.Constraint`)
  - `index=True` on fields (v19 introduced `models.Index`)
  - `cr.execute()` with plain SQL as the primary pattern (v18 added `env.execute_query_dict()`)
  - `read_group()` as the public API (v18 deprecated it in favor of `_read_group()` / `formatted_read_group()`)
  - Kanban templates still use `t-name="kanban-box"` (v19 renamed to `t-name="card"`)
  - Explicit `<div class="oe_chatter">` with `message_follower_ids` / `activity_ids` / `message_ids` (v18 introduced the `<chatter/>` shortcut)
  - `res.groups.category_id` (v19 introduced `privilege_id`)
  - `@api.private` decorator and `@api.ondelete(at_uninstall=False)` are available in v17
  - JSONB-based field translations (no `ir.translation` rows for model fields since v16)
  - Module hooks `pre_init_hook(env)` / `post_init_hook(env)` / `uninstall_hook(env)` all take `env`
  - Migration script entry `def migrate(cr, installed_version):` in `migrations/17.0.X.Y.Z/`
  - Module version string format `17.0.X.Y.Z`
  - `web.assets_common` was merged into `web.assets_frontend` before v17 shipped
- Example manifests use `'author': 'UncleCat'` and every module skeleton includes `i18n/` with a `.pot` template.

### Changed
- Updated root `README.md` skills table to list the new `odoo-17.0` pack.

### Build
- Bumped package version in `package.json` from `1.0.8` to `1.0.9`.

## [1.0.8]

### Release Description
Documentation update focused on modernizing Odoo view examples and improving decorator guide accuracy after merging PR #5.

### Changed
- Replaced legacy `oe_chatter` examples with modern `chatter` usage in:
  - `skills/odoo-18.0/references/odoo-18-view-guide.md`
  - `skills/odoo-19.0/references/odoo-19-view-guide.md`
- Corrected decorator reference from `@api_returns` to `@api.returns` in:
  - `skills/odoo-19.0/references/odoo-19-decorator-guide.md`
- Expanded `@api.returns` documentation with clearer usage patterns and examples in Odoo 19 guide.

### Build
- Bumped package version in `package.json` from `1.0.7` to `1.0.8`.

### Contributors
- [@BOKG](https://github.com/BOKG)

## [1.0.7]

### Release Description
This release standardizes the project release process so GitHub Releases are generated directly from `CHANGELOG.md`, with automated semantic version bump support.

### Added
- Added `bin/release-bump.js` to automate release preparation from `CHANGELOG.md`.
- Added npm scripts:
  - `npm run release:bump` to compute and apply the next semantic version.
  - `npm run release:bump:dry` to preview bump type/version without writing files.
- Added root `CHANGELOG.md` as the canonical source for release notes used by CI.

### Changed
- Updated `.github/workflows/github-release.yml` to build release notes from the matching version section in `CHANGELOG.md`.
- Updated `.github/workflows/auto-tag.yml` to create/edit GitHub Releases using `--notes-file` instead of autogenerated notes.
- Release jobs now validate changelog coverage and fail fast if the target version section is missing.
- Updated release flow to support a docs-first process: write notes in-repo, then push once to publish tag and release.

### Build
- Bumped package version to `1.0.7` in `package.json`.

## [1.0.6]

### Release Description
Focused on release-process clarity and documentation cleanup for the `1.0.6` publish cycle.

#### Changed
- Updated release automation workflows in `.github/workflows/auto-tag.yml` and `.github/workflows/github-release.yml` for clearer tagging and publishing behavior.
- Refined project `README.md` release guidance to better explain the publish flow.

#### Build
- Bumped package version in `package.json` from `1.0.5` to `1.0.6`.

#### Reference
- Compare: https://github.com/unclecatvn/agent-skills/compare/v1.0.5...v1.0.6

## [1.0.5]

### Release Description
Release focused on documentation streamlining and release workflow improvements.

#### Changed
- Improved release automation logic in `.github/workflows/auto-tag.yml` and `.github/workflows/github-release.yml`.
- Updated `README.md` for clearer installation and release instructions.
- Refined skill documentation in:
  - `skills/odoo-18.0/SKILL.md`
  - `skills/odoo-18.0/references/odoo-18-data-guide.md`
  - `skills/slide/SKILL.md`

#### Build
- Bumped package version in `package.json` from `1.0.4` to `1.0.5`.

#### Reference
- Compare: https://github.com/unclecatvn/agent-skills/compare/v1.0.4...v1.0.5

## [1.0.4]

### Release Description
Updated all `odoo-19.0` skill files to match the latest Odoo 19 source code. 12 files were updated across references, `CLAUDE.md`, and `SKILL.md`.

#### Added
- `models.Constraint` coverage (UNIQUE/CHECK syntax, migration from `_sql_constraints`, inherited model overrides).
- `models.Index` examples for declarative composite indexes.
- CamelCase model naming note (`_name` can be auto-derived in Odoo 19).
- `@api.private` decorator guidance and comparison with underscore convention.
- Privilege-based security groups (`privilege_id` and `res.groups.privilege`).
- `read_group()` deprecation note and migration guidance.

#### Changed
- Kanban template examples updated from `kanban-box` to `card`.
- Deprecated `t-esc` replaced with `t-out` across multiple guides.
- Removed `t-raw` references from QWeb directive tables.
- Updated `SKILL.md` description to match new Odoo 19 changes.

## [1.0.3]

### Release Description
Refactored Odoo 18/19 skill structure to align with the skill-creator specification.

#### Changed
- Simplified `SKILL.md` frontmatter to standard fields and rewrote descriptions for clearer activation conditions.
- Renamed `dev/` to `references/` and updated all related paths.
- Updated `AGENTS.md` installation flow (`npx skills add`) and corrected repo/branch/path references.
- Updated `CLAUDE.md` to use `references/` consistently.
- Expanded `odoo-18-model-guide.md` with additional ORM patterns.

## [1.0.2]

### Release Description
Improved Odoo 19 skill documentation structure and corrected Odoo 18 aggregation guidance.

#### Changed
- Enhanced Odoo 19 `AGENTS.md` setup instructions for AI IDEs.
- Improved Odoo 19 `SKILL.md` metadata and guide mapping.
- Corrected Odoo 18 `_read_group()` vs `read_group()` documentation and examples.
- Updated Odoo 18 model and performance guides with clearer aggregation best practices.

#### Fixed
- Fixed incorrect `_read_group()` positioning as "internal-only"; clarified real usage in Odoo base.
- Fixed file-count references in documentation.

## [1.0.1]

### Release Description
Focused on Odoo 18 transaction safety and concurrency control.

#### Highlights
- Added record-locking patterns with `SELECT ... FOR UPDATE NOWAIT`.
- Added safe `savepoint(flush=False)` and `LockNotAvailable` handling examples.
- Improved batch-processing recommendations to reduce transaction conflicts.
- Added guidance for choosing locking and savepoint strategies.

## [1.0.0]

### Release Description
First stable release of Agent Skills as a comprehensive knowledge pack for AI coding assistants.

#### Added
- 8 skill packs: Odoo 18.0, Odoo 19.0, DTG Base, Payment Integration, Code Review, Brainstorming, Writing Skills, MCP Builder.
- Expert agents: Odoo Code Review Agent and Planner Agent.
- Intelligence rules: Coding Style and Security guidance.
- Large documentation baseline (100+ markdown files, 10k+ lines).

#### Notes
- Release includes CLI installation flows via `npx` and npm package usage.
- Release provides broad IDE compatibility guidance (Cursor, Claude Code, Windsurf, Aider).

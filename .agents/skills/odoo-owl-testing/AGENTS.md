# Odoo Owl Testing - AI Agents Setup

Setup guide for using the dedicated Odoo frontend testing skill with AI coding assistants.

## Quick Start

### Install via skills.sh

```bash
npx skills add milzamsz/odoo-agents
```

### Cursor IDE - Remote Rule

Configure once in Cursor settings:

- `Settings` -> `Rules` -> `Add Remote Rule`
- Source: `Git Repository`
- URL: `git@github.com:milzamsz/odoo-agents.git`
- Branch: `18.0`
- Subfolder: `skills/odoo-owl-testing/`

## What This Skill Covers

- HOOT-based frontend unit tests
- `web_test_helpers` for mounting components and views
- mock server setup for ORM-backed UI behavior
- `web.assets_unit_tests` manifest wiring

## Version Scope

- Shared across Odoo 18 and 19
- Test bundle placement is the same in both versions
- Helper import paths can drift, so nearby core tests are the best local reference

## Included Files

```text
skills/odoo-owl-testing/
|-- SKILL.md
|-- AGENTS.md
|-- CLAUDE.md
|-- references/
|   |-- test-setup.md
|   |-- hoot.md
|   |-- web-test-helpers.md
|   |-- mock-server.md
|   `-- testing-checklist.md
`-- scripts/
    `-- scaffold_test.py
```

## Related Skills

- `skills/odoo-owl/` for the production component code under test
- `skills/odoo-webclient-extension/` for the registry or service wiring around the feature

# Odoo Webclient Extension - AI Agents Setup

Setup guide for using the dedicated Odoo webclient extension skill with AI coding assistants.

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
- Subfolder: `skills/odoo-webclient-extension/`

## What This Skill Covers

- action registry entries and client actions
- registries, services, and hooks in the Odoo web client
- field or view integrations that need official extension points
- safe `patch()` usage when no supported extension point exists

## Version Scope

- Shared across Odoo 18 and 19
- Registry and service patterns are broadly stable in both versions
- Most version-sensitive differences show up in surrounding XML or server-side view records

## Included Files

```text
skills/odoo-webclient-extension/
|-- SKILL.md
|-- AGENTS.md
|-- CLAUDE.md
|-- references/
|   |-- registries.md
|   |-- client-actions.md
|   |-- services-and-hooks.md
|   |-- patching.md
|   `-- extension-checklist.md
`-- scripts/
    `-- scaffold_client_action.py
```

## Related Skills

- `skills/odoo-owl/` for component authoring, templates, and asset wiring
- `skills/odoo-owl-testing/` for frontend test setup and HOOT coverage

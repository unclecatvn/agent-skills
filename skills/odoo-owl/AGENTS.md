# Odoo Owl - AI Agents Setup

Setup guide for using the dedicated Odoo Owl frontend skill with AI coding assistants.

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
- Subfolder: `skills/odoo-owl/`

## What This Skill Covers

- Owl components in addon `static/src`
- colocated JS/XML/SCSS triplets
- `@odoo-module` and manifest asset wiring
- template naming with `addon_name.ComponentName`
- choosing between backend webclient, portal/website, and standalone apps
- generic `@web` components before custom primitives

## Version Scope

- Shared across Odoo 18 and 19
- Odoo 18 often still contains `<tree>`, `attrs`, and `t-esc` around adjacent XML
- Odoo 19 prefers `<list>`, direct attributes, and `t-out`

## Included Files

```text
skills/odoo-owl/
|-- SKILL.md
|-- AGENTS.md
|-- CLAUDE.md
|-- references/
|   |-- component-basics.md
|   |-- qweb-templates.md
|   |-- assets-and-modules.md
|   |-- generic-components.md
|   `-- standalone-vs-webclient.md
`-- scripts/
    `-- scaffold_component.py
```

## Related Skills

- `skills/odoo-webclient-extension/` for registries, client actions, services, hooks, and patches
- `skills/odoo-owl-testing/` for HOOT, mock environments, and frontend tests

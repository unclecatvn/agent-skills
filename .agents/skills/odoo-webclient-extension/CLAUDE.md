# Odoo Webclient Extension Guide

This file provides guidance to AI agents when extending Odoo webclient behavior in this repository.

> For setup instructions with different AI IDEs, see [AGENTS.md](./AGENTS.md)

## Use This Skill When

- adding a new client action
- registering something in an Odoo registry category
- creating a long-lived frontend service
- wiring hooks into an existing webclient feature
- applying a narrowly scoped `patch()` because no supported extension point exists

## Route to Companion Skills

- Use `skills/odoo-owl/` when the core work is component structure, templates, or asset bundles.
- Use `skills/odoo-owl-testing/` when the main work is frontend test coverage.

## Documentation Structure

```text
skills/odoo-webclient-extension/
|-- SKILL.md
|-- references/
|   |-- registries.md
|   |-- client-actions.md
|   |-- services-and-hooks.md
|   |-- patching.md
|   `-- extension-checklist.md
`-- scripts/
    `-- scaffold_client_action.py
```

## Version Notes

- Odoo 18 and 19 share the same main extension points for client actions, registries, services, and hooks.
- Most version-sensitive differences sit in the XML or data files around the frontend registration.
- Keep patches small and early so they are easy to remove when Odoo adds a real extension point later.

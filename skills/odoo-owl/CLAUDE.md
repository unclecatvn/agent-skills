# Odoo Owl Frontend Guide

This file provides guidance to AI agents when working with dedicated Odoo Owl component work in this repository.

> For setup instructions with different AI IDEs, see [AGENTS.md](./AGENTS.md)

## Use This Skill When

- building a new Owl component inside an addon
- fixing a broken XML template or asset bundle entry
- deciding between backend, portal, website, or standalone Owl runtime contexts
- reusing generic `@web` components before building custom UI

## Route to Companion Skills

- Use `skills/odoo-webclient-extension/` when the main task is a registry, client action, service, hook, or patch.
- Use `skills/odoo-owl-testing/` when the main deliverable is frontend test coverage.

## Documentation Structure

```text
skills/odoo-owl/
|-- SKILL.md
|-- references/
|   |-- component-basics.md
|   |-- qweb-templates.md
|   |-- assets-and-modules.md
|   |-- generic-components.md
|   `-- standalone-vs-webclient.md
`-- scripts/
    `-- scaffold_component.py
```

## Version Notes

- Odoo 18 and 19 share the same broad Owl component patterns.
- The main version-sensitive differences usually live in the XML around the component, not inside `setup()` or `useService()`.
- Match the surrounding module conventions for tags and directives when a component lives inside a mixed XML feature.

## Core Guardrails

- Put `/** @odoo-module **/` on addon JavaScript files.
- Keep production templates in XML so they stay translatable.
- Add JS, XML, and SCSS files to the correct manifest bundle.
- Use `setup()` instead of a constructor.

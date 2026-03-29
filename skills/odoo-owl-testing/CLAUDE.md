# Odoo Owl Testing Guide

This file provides guidance to AI agents when writing or debugging Odoo frontend tests in this repository.

> For setup instructions with different AI IDEs, see [AGENTS.md](./AGENTS.md)

## Use This Skill When

- adding a new HOOT test
- fixing `web_test_helpers` setup or teardown problems
- mounting a component or view in a realistic Odoo environment
- mocking ORM, controller, or service-backed frontend behavior

## Route to Companion Skills

- Use `skills/odoo-owl/` when the main work is production component code.
- Use `skills/odoo-webclient-extension/` when the failure is really in registries, services, or client action wiring.

## Documentation Structure

```text
skills/odoo-owl-testing/
|-- SKILL.md
|-- references/
|   |-- test-setup.md
|   |-- hoot.md
|   |-- web-test-helpers.md
|   |-- mock-server.md
|   `-- testing-checklist.md
`-- scripts/
    `-- scaffold_test.py
```

## Version Notes

- Odoo 18 and 19 share the same main frontend test entrypoint: `web.assets_unit_tests`.
- Helper names and import paths can move, so verify against nearby addon or core tests before copying an import blindly.
- Prefer DOM assertions and realistic environment setup over reaching into component internals.

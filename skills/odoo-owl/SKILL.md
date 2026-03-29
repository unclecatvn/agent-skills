---
name: odoo-owl
description: Build and debug Odoo Owl components inside addons that use `static/src`, QWeb templates, `@odoo-module`, and asset bundles. Use when Codex needs to create or fix Odoo frontend code such as Owl components, XML templates, colocated JS/XML/SCSS files, generic `@web` components, or standalone-vs-webclient integration decisions in Odoo 18 and 19.
---

# Odoo Owl

## Overview

Build the standard Odoo Owl file triplet, wire it into assets, and keep the implementation aligned with how Odoo expects frontend code to be organized. Centralize generic Owl ideas here, then hand off registry-heavy or test-heavy work to the companion skills.

## Workflow Decision Tree

- Stay in this skill when the request is about a new or broken component, template, asset bundle entry, `@odoo-module`, or choosing between backend, portal, and standalone Owl usage.
- Switch to `odoo-webclient-extension` when the main task is a client action, registry entry, service, hook, field/view override, or a patch on existing framework code.
- Switch to `odoo-owl-testing` when the main task is HOOT, `web_test_helpers`, `mock_server`, or `web.assets_unit_tests`.

## Version Notes

- Odoo 18 and 19 share the same broad Owl component model: colocated JS/XML/SCSS files, `setup()`, `useService()`, template naming, and manifest asset wiring all work the same way.
- When frontend work touches surrounding XML views or mixed QWeb, keep version syntax in mind:
  - Odoo 18 codebases often still contain `<tree>`, `attrs`, and `t-esc`.
  - Odoo 19 codebases prefer `<list>`, direct attributes such as `invisible="..."`, and `t-out`.
- Match the target addon's established version conventions instead of rewriting neighboring files into a different version style.

## Build or Debug an Odoo Component

1. Inspect the addon layout and existing `static/src` conventions before writing code.
2. Place component files together whenever possible:
   - `my_component.js`
   - `my_component.xml`
   - `my_component.scss` when styling is needed
3. Put `/** @odoo-module **/` on the first line of addon JavaScript files.
4. Define the production template in XML, not inline, so it remains translatable.
5. Name templates with the `addon_name.ComponentName` convention.
6. Use `setup()` for initialization; do not use a component constructor.
7. Add every created JS/XML/SCSS file to the correct asset bundle.

Use the helper script when you need a clean starter:

```bash
python scripts/scaffold_component.py --root /path/to/my_addon --addon my_addon --component PartnerBadge --with-scss
```

## Choose the Right Runtime Context

- Build a regular addon component when the code belongs inside an existing Odoo screen or feature.
- Build a standalone Owl app only when the page owns its own mount target and environment.
- Treat portal or website work as a separate runtime context from the backend web client.
- Reuse generic `@web` components before inventing custom primitives.

Read the matching reference before going deeper:

- [references/component-basics.md](references/component-basics.md)
- [references/qweb-templates.md](references/qweb-templates.md)
- [references/assets-and-modules.md](references/assets-and-modules.md)
- [references/generic-components.md](references/generic-components.md)
- [references/standalone-vs-webclient.md](references/standalone-vs-webclient.md)

## Companion Skills

- Use `skills/odoo-webclient-extension/` when the job becomes more about registries, client actions, services, hooks, or `patch()`.
- Use `skills/odoo-owl-testing/` when the deliverable is test coverage with HOOT, mock environments, or `web.assets_unit_tests`.

## Guardrails

- Keep inline `xml` templates for prototypes or tests only; move production templates to XML files.
- Preserve Ecmascript 2019 compatibility in addon code.
- Prefer Odoo's `@web` imports and existing patterns over framework-agnostic rewrites.
- Check the manifest bundle before assuming a component is loaded.
- Treat missing asset wiring, missing `@odoo-module`, and wrong template names as first-pass debugging targets.
- Treat Odoo 18 and 19 as the supported range for this standalone skill, and add an explicit note whenever surrounding XML or view syntax is version-sensitive.

---
name: odoo-18-owl
description: Bridge guide for Odoo 18 Owl work. Use it to route frontend-heavy requests into the dedicated standalone Odoo Owl, webclient extension, and frontend testing skills while keeping Odoo 18 version notes in view.
globs: "**/static/src/**/*.js"
topics:
  - Owl skill routing
  - Odoo 18 frontend compatibility notes
  - Component authoring
  - Webclient extension points
  - Frontend testing
when_to_use:
  - Routing Odoo 18 frontend work to the correct standalone skill
  - Checking Odoo 18-specific frontend syntax around Owl features
---

# Odoo 18 OWL Bridge Guide

Use this file as the Odoo 18 router for Owl-related work. The detailed implementation guidance now lives in the dedicated standalone frontend skills.

## Route the Task

| Need | Skill |
|------|-------|
| Build or fix an Owl component, template, asset bundle, or standalone mount | `skills/odoo-owl/` |
| Add a client action, registry entry, service, hook, or patch | `skills/odoo-webclient-extension/` |
| Add or fix HOOT tests, `web_test_helpers`, or `mock_server` usage | `skills/odoo-owl-testing/` |

---

## Odoo 18 Notes

- Odoo 18 frontend work still commonly sits beside `<tree>` views, legacy `attrs`, and `t-esc`.
- Do not force 19-style surrounding XML into an Odoo 18 addon unless the module is already migrating.
- The Owl component structure itself still follows the same main rules: colocated JS/XML/SCSS, `setup()`, `useService()`, and `addon_name.ComponentName`.

---

## Quick Checks Before Implementing

- Confirm the addon loads the right asset bundle.
- Confirm the JavaScript file starts with `/** @odoo-module **/`.
- Confirm the template name matches `addon_name.ComponentName`.
- Confirm the surrounding XML syntax matches Odoo 18 conventions already used by the addon.

## Canonical Deep Guides

- `skills/odoo-owl/` for component authoring, templates, assets, and runtime choice
- `skills/odoo-webclient-extension/` for client actions, registries, services, hooks, and patches
- `skills/odoo-owl-testing/` for HOOT, `web_test_helpers`, mock server setup, and `web.assets_unit_tests`

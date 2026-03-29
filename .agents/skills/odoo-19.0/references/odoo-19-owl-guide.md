# Odoo 19 OWL Bridge Guide

Use this file as the Odoo 19 router for Owl-related work. The detailed implementation guidance now lives in the dedicated standalone frontend skills.

## Route the Task

| Need | Skill |
|------|-------|
| Build or fix an Owl component, template, asset bundle, or standalone mount | `skills/odoo-owl/` |
| Add a client action, registry entry, service, hook, or patch | `skills/odoo-webclient-extension/` |
| Add or fix HOOT tests, `web_test_helpers`, or `mock_server` usage | `skills/odoo-owl-testing/` |

---

## Odoo 19 Notes

- Odoo 19 keeps the same broad Owl component model as Odoo 18: colocated JS/XML/SCSS files, `setup()`, `useService()`, manifest assets, and `addon_name.ComponentName`.
- The main version-sensitive differences live around the component:
  - use `<list>` instead of `<tree>` in surrounding views
  - prefer direct attributes instead of legacy `attrs`
  - prefer `t-out` where the module already follows Odoo 19 QWeb conventions

## Quick Checks Before Implementing

- Confirm the addon loads the right asset bundle.
- Confirm the JavaScript file starts with `/** @odoo-module **/`.
- Confirm the template name matches `addon_name.ComponentName`.
- Confirm the surrounding XML and view syntax already follow Odoo 19 conventions.

## Canonical Deep Guides

- `skills/odoo-owl/` for component authoring, templates, assets, and runtime choice
- `skills/odoo-webclient-extension/` for client actions, registries, services, hooks, and patches
- `skills/odoo-owl-testing/` for HOOT, `web_test_helpers`, mock server setup, and `web.assets_unit_tests`

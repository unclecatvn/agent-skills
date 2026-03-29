---
name: odoo-webclient-extension
description: Extend the Odoo web client through registries, client actions, services, hooks, field or view integrations, and safe patching patterns. Use when Codex needs to register a backend action, add entries to Odoo registries, create long-lived frontend services, hook into the environment, or modify existing web client behavior in Odoo 18 or 19 while preferring official extension points over patches.
---

# Odoo Webclient Extension

## Overview

Prefer the Odoo web client's extension points first, and treat patching as the narrowest possible fallback. Use this skill when the work is more about framework integration than about a standalone component's local template and state.

## Extension Decision Tree

- Use a registry when Odoo already exposes a category for the feature you need to add or replace.
- Use a client action when the new feature is a root backend screen reached by action navigation.
- Use a service when the behavior is long-lived, shared, or not naturally owned by one component.
- Use hooks to consume the environment cleanly from components.
- Use `patch()` only when no supported extension point exists and the change must affect an existing class or object.

## Version Notes

- Registries, client actions, services, and hooks are broadly stable across Odoo 18 and 19.
- Version differences usually show up around the XML or server-side records that surround the frontend code:
  - Odoo 18 modules often still use `<tree>` and legacy `attrs` in related views.
  - Odoo 19 modules prefer `<list>` and direct attributes such as `readonly="..."` or `invisible="..."`.
- Keep client action tags, template names, and action XML consistent with the addon's target version instead of mixing surrounding conventions.

## Extend Safely

1. Inspect the current addon and search for an existing registry category, service, or component extension point.
2. Prefer registration over replacement whenever the framework supports it.
3. Keep action tags, template names, and file paths namespaced with the addon name.
4. Apply patches at module top level as early as possible if a patch is unavoidable.
5. Keep the patch small, documented, and easy to remove when Odoo adds a real extension point later.

Use the helper script when you need a client action starter:

```bash
python scripts/scaffold_client_action.py --root /path/to/my_addon --addon my_addon --action-name SalesDashboard --with-scss
```

## Reach for the Right Reference

- [references/registries.md](references/registries.md)
- [references/client-actions.md](references/client-actions.md)
- [references/services-and-hooks.md](references/services-and-hooks.md)
- [references/patching.md](references/patching.md)
- [references/extension-checklist.md](references/extension-checklist.md)

## Guardrails

- Prefer registries, services, and official hooks before patching.
- Do not patch late inside runtime callbacks if a module-top patch is required.
- Do not skip manifest asset updates or action data wiring when adding a client action.
- Use `useService()` inside components instead of reaching through `this.env.services` directly unless there is a clear reason not to.
- Keep Odoo-specific imports under `@web/...` and addon-local imports relative.
- If a task blends frontend registration with heavy component authoring or test work, route to `skills/odoo-owl/` or `skills/odoo-owl-testing/` rather than overloading this skill.

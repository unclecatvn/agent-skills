---
name: odoo-owl-testing
description: Write and debug Odoo frontend unit tests with HOOT, `@web/../tests/web_test_helpers`, `mock_server`, and `web.assets_unit_tests`. Use when Codex needs to add or repair JavaScript tests for Owl components, services, web client features, async DOM interactions, or ORM-backed frontend behavior in Odoo 18 and 19 addons.
---

# Odoo Owl Testing

## Overview

Use this skill once the main deliverable is confidence, not production UI. Keep tests close to how Odoo actually runs them: HOOT for the framework, `web_test_helpers` for realistic mounting and interaction, and the mock server for backend-dependent behavior.

## Test Decision Tree

- Use a component test when you need to verify DOM output, props, or user interaction for one component.
- Use `makeMockEnv()` when you need a service-focused test without mounting a full UI.
- Use `mountWithCleanup()` for components and `mountView()` when the real unit is a view.
- Use the mock server when the code triggers ORM or route calls.
- Add a test only after confirming the production file is in the right addon and bundle.

## Version Notes

- `web.assets_unit_tests`, HOOT, and the common Odoo frontend helpers are the shared baseline across Odoo 18 and 19.
- Helper names and import paths can shift as Odoo reorganizes internals, so search nearby core or addon tests before assuming a helper path from memory.
- If a test interacts with server-side XML views, remember that Odoo 18 and 19 may differ in the surrounding view syntax even when the Owl test harness looks similar.

## Set Up Tests Correctly

1. Put JavaScript test files under the addon's `static/tests` folder.
2. End test files with `.test.js`.
3. Include the folder in `web.assets_unit_tests`.
4. Run tests from `/web/tests` or the debug menu.

Use the helper script when you need a starter:

```bash
python scripts/scaffold_test.py --root /path/to/my_addon --addon my_addon --name partner_badge --kind component
```

## Write Stable Frontend Tests

- Assert through the DOM when possible instead of reading component internals.
- Prefer `contains(...)`-style helpers and async-safe interactions for Owl rendering.
- Spawn or configure mock data before expecting ORM-backed UI to behave.
- Keep tests narrow: one behavior, one expectation cluster, one clear reason to fail.

Read the matching reference before implementing:

- [references/test-setup.md](references/test-setup.md)
- [references/hoot.md](references/hoot.md)
- [references/web-test-helpers.md](references/web-test-helpers.md)
- [references/mock-server.md](references/mock-server.md)
- [references/testing-checklist.md](references/testing-checklist.md)

## Guardrails

- Do not place tests outside `static/tests`.
- Do not forget to load the folder in `web.assets_unit_tests`.
- Do not expect ORM calls to work until the mock server knows the target model or route.
- Do not overfit assertions to component internals when a visible DOM assertion is enough.
- Do not mix production asset bundles and test-only helpers in the wrong manifest section.
- Route registry-heavy frontend work back to `skills/odoo-webclient-extension/` and component authoring back to `skills/odoo-owl/` when the main deliverable stops being test coverage.

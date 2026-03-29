# Web Test Helpers

## Why They Matter

After `@odoo/hoot`, the most common helper module in Odoo frontend tests is `@web/../tests/web_test_helpers`.

It wraps low-level HOOT helpers with Odoo-aware setup for:

- mock environments
- started services
- mounted components
- mounted views
- async-safe DOM interaction

## Common Helpers

### `makeMockEnv`

Use for service-focused or low-level tests that need a real Odoo environment without mounting a component.

### `mountWithCleanup`

Use to mount an Owl component and get automatic environment and teardown support.

### `mountView`

Use to mount actual Odoo views when the real unit is a list, form, kanban, or another view type.

### `contains`

Use for async-safe UI interaction. It helps when Owl rendering or DOM insertion happens after the interaction request.

## Practical Rule

Prefer DOM-driven assertions. Odoo explicitly discourages poking the component instance directly unless the rendered output is otherwise hard to inspect.

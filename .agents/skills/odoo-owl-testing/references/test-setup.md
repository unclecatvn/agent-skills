# Test Setup

## File and Bundle Rules

Frontend unit tests in Odoo should follow these rules:

- Put test files under `static/tests`
- End test files with `.test.js`
- Include them in `web.assets_unit_tests`
- Run them from `/web/tests`

Manifest reminder:

```python
"assets": {
    "web.assets_unit_tests": [
        "my_addon/static/tests/**/*",
    ],
},
```

## Fast Preflight

- Confirm the addon already ships frontend assets.
- Confirm the test file path is under the correct addon.
- Confirm the test file name ends in `.test.js`.
- Confirm the bundle is test-only, not backend or frontend production assets.

## Odoo 18 and 19 Notes

- The `static/tests` plus `web.assets_unit_tests` setup is shared across Odoo 18 and 19.
- Import paths for helpers can move as Odoo reorganizes modules, so copy the style of nearby core tests when available.
- When the test mounts real views or interacts with server-rendered XML, keep the target version's surrounding view syntax in mind.

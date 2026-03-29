# Mock Server

## Default Behavior

As soon as a test spawns an Odoo environment, a mock server is needed because some services issue requests immediately.

The mock server:

- intercepts server requests
- emulates common Odoo routes such as `/web/dataset/call_kw`
- stores fake model data for ORM-backed interactions

## Practical Consequences

- An "empty" mock server still handles some framework routes such as menus and translations.
- ORM calls will still fail until the target model is defined.
- Mock server helpers live in `@web/../tests/web_test_helpers`.

## Minimal Model Pattern

```js
import { defineModels, fields, models } from "@web/../tests/web_test_helpers";

class ResPartner extends models.Model {
    _name = "res.partner";

    name = fields.Char({ required: true });

    _records = [{ name: "Mitchel Admin" }];
}

defineModels({ ResPartner });
```

## When to Reach for It

- a component calls `orm`
- a service calls `rpc`
- a view expects records, actions, menus, or params

If the production code needs backend data and the test does not define it, suspect the mock server setup first.

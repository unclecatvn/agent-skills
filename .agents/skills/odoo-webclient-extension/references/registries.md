# Registries

## Mental Model

Treat registries as Odoo's main web client extension points. They are ordered key-value maps grouped by category.

Common categories include:

- `actions`
- `fields`
- `views`
- `main_components`
- feature-specific registries exposed by individual addons

## Workflow

1. Search for the relevant category before writing new code.
2. Inspect how nearby addons register entries.
3. Register under an addon-namespaced key.
4. Keep the registration close to the exported implementation.

## Minimal Pattern

```js
/** @odoo-module **/

import { registry } from "@web/core/registry";
import { SalesDashboard } from "./sales_dashboard";

registry.category("actions").add("my_addon.SalesDashboard", SalesDashboard);
```

## Guardrails

- Reuse an existing category instead of inventing one when the framework already exposes the right slot.
- Preserve sequence or ordering behavior when categories use it.
- Avoid silent overrides unless replacement is the point of the feature.

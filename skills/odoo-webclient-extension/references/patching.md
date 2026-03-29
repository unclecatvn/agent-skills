# Patching

Patch only when the framework gives you no cleaner extension point.

## Safe Pattern

```js
/** @odoo-module **/

import { patch } from "@web/core/utils/patch";
import { SomeClass } from "@web/some/module";

patch(SomeClass.prototype, {
    myMethod() {
        super.myMethod(...arguments);
        // Minimal addon-specific behavior
    },
});
```

## Rules

- Apply patches at module top level as early as possible.
- Keep the patch focused on one behavior.
- Explain why a registry, service, or official hook was not enough.
- Avoid runtime or conditional patch application unless the target itself is conditional.

## Risks to Watch

- Patching after instances were already created
- Broad behavior changes that affect unrelated screens
- Conflicts with other addons patching the same target

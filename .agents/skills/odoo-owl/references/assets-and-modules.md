# Assets and Modules

## Asset Bundles

The most common bundle decisions are:

- `web.assets_backend` for backend web client code
- `web.assets_frontend` for portal or website code
- `web.assets_unit_tests` for frontend tests

Starter manifest snippet:

```python
"assets": {
    "web.assets_backend": [
        "my_addon/static/src/components/partner_badge/partner_badge.js",
        "my_addon/static/src/components/partner_badge/partner_badge.xml",
        "my_addon/static/src/components/partner_badge/partner_badge.scss",
    ],
},
```

## JavaScript Modules

Odoo addon JavaScript is opt-in outside transpiled core folders. Put `/** @odoo-module **/` on the first line so Odoo treats the file as a module.

```js
/** @odoo-module **/

import { Component } from "@odoo/owl";
import { Dropdown } from "@web/core/dropdown/dropdown";
```

## Debugging Checklist

- Confirm the file is in the right bundle.
- Confirm the module header is on the first line.
- Confirm XML files were added to assets along with JS.
- Confirm imports use `@web/...` only for Odoo core code and relative imports for addon-local code.
- Confirm the target page actually loads the selected bundle.

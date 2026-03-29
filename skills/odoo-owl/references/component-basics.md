# Component Basics

## Standard Odoo Shape

Prefer a colocated component triplet inside the addon:

```text
my_addon/
  static/
    src/
      components/
        partner_badge/
          partner_badge.js
          partner_badge.xml
          partner_badge.scss
```

Use a JavaScript file for logic, an XML file for the translatable template, and SCSS only when the component owns styling.

## Minimal Starter

```js
/** @odoo-module **/

import { Component, useState } from "@odoo/owl";

export class PartnerBadge extends Component {
    static template = "my_addon.PartnerBadge";

    setup() {
        this.state = useState({ count: 0 });
    }

    increment() {
        this.state.count++;
    }
}
```

```xml
<?xml version="1.0" encoding="UTF-8" ?>
<templates xml:space="preserve">
    <t t-name="my_addon.PartnerBadge">
        <button type="button" t-on-click="increment">
            <t t-esc="state.count"/>
        </button>
    </t>
</templates>
```

## Practical Rules

- Put `/** @odoo-module **/` on the first line when the file lives in addon code.
- Use `setup()` instead of a constructor.
- Keep template names globally unique with `addon_name.ComponentName`.
- Prefer DOM-driven behavior and small state objects.
- Reach for `useService()` only when the component truly needs long-lived app services.

## First Debugging Checks

- Confirm the JS and XML files are both in the asset bundle.
- Confirm the template name in JS matches the XML `t-name`.
- Confirm the file path and imports match the addon's existing structure.
- Confirm the issue is not caused by a missing service, missing props, or an unmounted parent component.

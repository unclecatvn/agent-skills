# Client Actions

Use a client action when the feature is a top-level backend screen navigated by `ir.actions.client`.

## Required Pieces

- JavaScript component
- XML template
- registry registration in `actions`
- asset bundle entries
- `ir.actions.client` record with a `tag`

## Minimal Pattern

```js
/** @odoo-module **/

import { Component } from "@odoo/owl";
import { registry } from "@web/core/registry";

export class SalesDashboard extends Component {
    static template = "my_addon.SalesDashboard";
}

registry.category("actions").add("my_addon.SalesDashboard", SalesDashboard);
```

```xml
<record id="action_sales_dashboard" model="ir.actions.client">
    <field name="name">Sales Dashboard</field>
    <field name="tag">my_addon.SalesDashboard</field>
</record>
```

## Reminders

- Keep the registry tag stable; menus and server-side actions depend on it.
- Add JS, XML, and SCSS to backend assets.
- Add the `ir.actions.client` record to a data XML file loaded by the manifest.

## Odoo 18 and 19 Notes

- The client action pattern itself is the same across Odoo 18 and 19.
- The common version differences are around neighboring XML and view syntax, not the action registration:
  - Odoo 18 modules often still use `<tree>` and legacy `attrs`.
  - Odoo 19 modules usually use `<list>` and direct attributes.
- Keep the client action's surrounding XML aligned with the target module's version conventions.

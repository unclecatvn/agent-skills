# QWeb Templates

## Core Pattern

Use XML templates for production Owl components so Odoo can translate and load them consistently.

```xml
<?xml version="1.0" encoding="UTF-8" ?>
<templates xml:space="preserve">
    <t t-name="my_addon.MyComponent">
        <div class="o_my_component">
            <t t-esc="props.label"/>
        </div>
    </t>
</templates>
```

## Common Directives

- Use `t-esc` for plain escaped output.
- Use `t-if` and `t-elif` for conditional blocks.
- Use `t-foreach` with `t-key` for lists.
- Use `t-on-click`, `t-on-change`, and related event bindings for handlers.
- Use `t-att-*` or `t-attf-*` for dynamic attributes.

## Odoo 18 and 19 Notes

- Odoo 18 codebases still commonly use `t-esc`, and matching local convention is usually safer than drive-by rewrites.
- Odoo 19 increasingly prefers `t-out` in surrounding QWeb and view templates. When touching mixed frontend/server XML, follow the version already used by the addon you are editing.
- Owl component templates still use the same `addon_name.ComponentName` naming pattern in both versions.

## Naming and Placement

- Keep one primary component template per XML file when possible.
- Name templates as `addon_name.ComponentName`.
- Keep XML close to the owning JS file to reduce asset and import mistakes.

## Avoidable Mistakes

- Do not leave a production component using inline `xml` when the template needs translation.
- Do not mismatch `static template = "..."` and XML `t-name`.
- Do not omit `xml:space="preserve"` from the root `<templates>` block.
- Do not duplicate template names across addons.

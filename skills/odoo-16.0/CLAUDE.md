# Odoo 16 Development Guide

This file is the short operational guide for agents working on Odoo 16.

> For install/setup notes, see [AGENTS.md](./AGENTS.md).

## Use These Guides

- `references/odoo-16-development-guide.md` for module naming and file layout.
- `references/odoo-16-view-guide.md` for XML views, inherited views, chatter, kanban.
- `references/odoo-16-model-guide.md` for ORM, CRUD, domains, recordsets.
- `references/odoo-16-field-guide.md` for field definitions and `group_operator=`.
- `references/odoo-16-decorator-guide.md` for `@api.depends`, `@api.ondelete`, `@api.model_create_multi`.
- `references/api-highlights.md` for version-distinguishing rules that differ from 17+.

## Odoo 16 Rules That Matter

| Concern | Odoo 16 rule |
|---------|--------------|
| List views | Use `<tree>` |
| Dynamic attributes | Use `attrs="{...}"` / `states="..."` modifiers |
| Aggregation | Use `group_operator=` |
| Delete validation | Prefer `@api.ondelete(at_uninstall=False)` |
| Batch create | Use `@api.model_create_multi` |
| Kanban card template | Use `t-name="kanban-box"` |
| Chatter | Use explicit `<div class="oe_chatter"> ... </div>` |

## Review Heuristics

- Prefer `attrs` / `states` for client-side dynamic view modifiers; direct `invisible="..."` is valid only for static/context-time visibility.
- Check the view guide before rewriting inherited XML broadly.
- Flag 18/19-only constructs such as `<list>`, `aggregator=`, `models.Constraint(...)`, or `<chatter/>`.
- Apply the Coding Conventions section in the guide you open. Prefer Odoo 16 runtime behavior, then the surrounding stable-addon style, when they conflict with a convention.

## Common Safe Defaults

```python
@api.model_create_multi
def create(self, vals_list):
    return super().create(vals_list)
```

```xml
<tree string="Records">
    <field name="name"/>
</tree>
```

```xml
<field name="amount_total" attrs="{'readonly': [('state', '!=', 'draft')]}"/>
```

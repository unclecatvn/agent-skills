# Odoo 17 Development Guide

This file provides guidance to AI agents when working with Odoo 17 code in this repository.

> **For setup instructions with different AI IDEs, see [AGENTS.md](./AGENTS.md)**

## Documentation Structure

The `skills/odoo-17.0/references/` directory contains modular guides for Odoo 17 development:

```
skills/odoo-17.0/
├── SKILL.md                       # Master index
├── references/                    # Development guides (18 files)
│   ├── odoo-17-actions-guide.md     # ir.actions.*, cron, bindings
│   ├── odoo-17-controller-guide.md  # HTTP, routing, controllers
│   ├── odoo-17-data-guide.md        # XML/CSV data files, records
│   ├── odoo-17-decorator-guide.md   # @api decorators
│   ├── odoo-17-development-guide.md # Manifest, wizards (overview)
│   ├── odoo-17-field-guide.md       # Field types, parameters
│   ├── odoo-17-manifest-guide.md    # __manifest__.py reference
│   ├── odoo-17-mixins-guide.md      # mail.thread, activities, etc.
│   ├── odoo-17-model-guide.md       # ORM, CRUD, search, domain
│   ├── odoo-17-migration-guide.md   # Migration scripts, hooks
│   ├── odoo-17-owl-guide.md         # OWL components, services
│   ├── odoo-17-performance-guide.md # N+1 prevention, optimization
│   ├── odoo-17-reports-guide.md     # QWeb reports, PDF/HTML
│   ├── odoo-17-security-guide.md    # ACL, record rules, security
│   ├── odoo-17-testing-guide.md     # Test classes, decorators
│   ├── odoo-17-transaction-guide.md # Savepoints, errors
│   ├── odoo-17-translation-guide.md # Translations, i18n
│   └── odoo-17-view-guide.md        # XML views, QWeb
├── CLAUDE.md                      # This file
└── AGENTS.md                      # AI agents setup
```

## Which Guide to Use

| Task | Guide |
|------|-------|
| Creating actions, menus, cron jobs | `references/odoo-17-actions-guide.md` |
| Creating a new module | `references/odoo-17-development-guide.md` |
| Configuring __manifest__.py | `references/odoo-17-manifest-guide.md` |
| Creating XML/CSV data files | `references/odoo-17-data-guide.md` |
| Writing ORM queries/search | `references/odoo-17-model-guide.md` |
| Defining model fields | `references/odoo-17-field-guide.md` |
| Using @api decorators | `references/odoo-17-decorator-guide.md` |
| Writing XML views | `references/odoo-17-view-guide.md` |
| Fixing slow code/N+1 queries | `references/odoo-17-performance-guide.md` |
| Handling database errors | `references/odoo-17-transaction-guide.md` |
| Creating HTTP endpoints | `references/odoo-17-controller-guide.md` |
| Building OWL components | `references/odoo-17-owl-guide.md` |
| Upgrading modules/migrating data | `references/odoo-17-migration-guide.md` |
| Using mail.thread, activities, mixins | `references/odoo-17-mixins-guide.md` |
| Creating QWeb reports | `references/odoo-17-reports-guide.md` |
| Configuring security (ACL, rules) | `references/odoo-17-security-guide.md` |
| Writing tests | `references/odoo-17-testing-guide.md` |
| Adding translations/localization | `references/odoo-17-translation-guide.md` |

## Key Odoo 17 Conventions (vs Odoo 18+)

Odoo 17 is the version *before* the big v18 API modernization. Code must use the v17 patterns:

Apply the Coding Conventions section in the guide you open. Prefer Odoo 17
runtime behavior, then the surrounding stable-addon style, when they conflict
with a convention.

| Concern | Odoo 17 convention | Odoo 18+ change (do NOT use in v17) |
|---------|--------------------|-------------------------------------|
| List view tag | `<tree>` | `<list>` |
| Dynamic attributes | Direct Python expressions: `invisible="state == 'done'"`, `readonly="locked"`, `required="type == 'post'"` (v17 REMOVED `attrs=` and `states=` — the view validator raises `ValidationError` if they appear) | (same direct-expression form) |
| Delete validation | `@api.ondelete(at_uninstall=False)` (available since v15) or override `unlink()` | (same, `@api.ondelete` still preferred) |
| Field aggregation | `group_operator='sum'` | `aggregator='sum'` |
| SQL queries | `self.env.cr.execute(query, params)` | `SQL` class + `execute_query_dict()` |
| Batch create | `create([{...}, {...}])` also supported | (same) |
| SQL constraints | `_sql_constraints = [(...)]` | `models.Constraint(...)` |
| QWeb output | `t-esc` and `t-out` both valid (`t-out` is newer, preferred for HTML-safe output) | Only `t-out` |
| Kanban template | `t-name="kanban-box"` | `t-name="card"` |
| Chatter in form view | `<div class="oe_chatter"> <field name="message_follower_ids"/> <field name="message_ids"/> </div>` | `<chatter/>` shortcut tag |

## Critical Anti-Patterns

| Anti-Pattern | Why Bad | Correct Approach |
|--------------|---------|------------------|
| `@api.depends('partner_id')` then accessing `partner_id.email` | N queries per record | Add `@api.depends('partner_id.email')` |
| `search()` inside loop | N+1 queries | Use `search()` with `IN` domain or `read_group()` |
| `create()` in loop | N INSERT statements | Batch: `create([{...}, {...}])` |
| Plain override of `unlink()` for validation | Breaks module uninstall | Use `@api.ondelete(at_uninstall=False)` |
| Using `<list>` in Odoo 17 | Not the v17 convention | Use `<tree>` |
| Using `attrs="{'invisible': [...]}"` or `states="..."` | v17 view validator rejects these since 17.0 | Use direct `invisible="..."`, `readonly="..."`, `required="..."` Python expressions |
| Using `aggregator=` on fields | v18+ only | Use `group_operator=` |
| Using `models.Constraint(...)` | v19+ only | Use `_sql_constraints` |
| Using `privilege_id` on `res.groups` | v19+ only | Use `category_id` |

## @api Decorator Decision Tree

```
Need to define field behavior?
├── Field computed from other fields → @api.depends
│   └── CAN use dotted paths: `@api.depends('partner_id.email')`
├── Validate data → @api.constrains
│   └── CANNOT use dotted paths: only simple field names
├── Prevent record deletion → @api.ondelete (available since v15)
└── Update form UI → @api.onchange
    └── NO CRUD operations allowed

Need to define method behavior?
├── Method-level, doesn't depend on self → @api.model
├── Create multiple records in one call → @api.model_create_multi (required on create)
├── Block RPC access to a public method → @api.private (or rename with leading _)
└── Normal record method → no decorator needed
```

## Common Patterns Reference

### N+1 Query Prevention

```python
# BAD: search in loop
for order in orders:
    payments = self.env['payment'].search([('order_id', '=', order.id)])

# GOOD: single query
payments = self.env['payment'].search_read([('order_id', 'in', orders.ids)])
```

### Tree View (Odoo 17)

```xml
<tree string="Records" editable="bottom" multi_edit="1">
    <field name="state" decoration-success="state == 'done'"/>
    <field name="phone" optional="show"/>
</tree>
```

### Conditional Attributes (Odoo 17)

v17 uses direct Python expressions (NOT the legacy `attrs=`/`states=` dict, which the validator rejects since 17.0):

```xml
<field name="date_done"
       invisible="state != 'done'"
       readonly="state in ('done', 'cancel')"/>
```

Boolean fields can be used directly:

```xml
<field name="note" invisible="not has_note"/>
<button name="action_confirm" invisible="state != 'draft'" string="Confirm"/>
```

### Delete Validation (Odoo 17)

```python
@api.ondelete(at_uninstall=False)
def _unlink_if_not_draft(self):
    if any(rec.state != 'draft' for rec in self):
        raise UserError("Cannot delete non-draft records")
```

### Batch Create (Odoo 17)

```python
@api.model_create_multi
def create(self, vals_list):
    for vals in vals_list:
        # per-vals preprocessing
        pass
    return super().create(vals_list)
```

## Module Structure

```
my_module/
├── __init__.py
├── __manifest__.py
├── models/
│   ├── __init__.py
│   └── my_model.py
├── views/
│   └── my_model_views.xml
├── security/
│   ├── ir.model.access.csv
│   └── my_module_security.xml
├── data/
│   └── my_module_data.xml
├── migrations/
│   └── 17.0.1.0/
│       └── post-migrate_data.py
├── tests/
│   ├── __init__.py
│   └── test_my_model.py
├── wizard/
│   ├── __init__.py
│   └── my_wizard.py
├── controllers/
│   ├── __init__.py
│   └── my_controller.py
├── i18n/
│   ├── my_module.pot
│   └── vi.po
└── static/
    └── src/
        ├── js/
        │   └── my_component.js
        ├── xml/
        │   └── my_component.xml
        └── scss/
            └── my_component.scss
```

## Base Code Reference

The guides are based on Odoo 17 source code. Reference these files in your Odoo installation:
- `odoo/models.py` - ORM implementation
- `odoo/fields.py` - Field types
- `odoo/api.py` - Decorators
- `odoo/http.py` - HTTP layer
- `odoo/exceptions.py` - Exception types

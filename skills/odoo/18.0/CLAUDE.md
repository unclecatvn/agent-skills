# Odoo 18 Development Guide

This file provides guidance to AI agents when working with Odoo 18 code in this repository.

> **For setup instructions with different AI IDEs, see [AGENTS.md](./AGENTS.md)**

## Documentation Structure

The `agent-skills/skills/odoo/18.0/dev/` directory contains modular guides for Odoo 18 development:

```
agent-skills/skills/odoo/18.0/
├── SKILL.md                       # Master index
├── dev/                           # Development guides
│   ├── odoo-18-model-guide.md     # ORM, CRUD operations
│   ├── odoo-18-field-guide.md     # Field types
│   ├── odoo-18-decorator-guide.md  # @api decorators
│   ├── odoo-18-view-guide.md      # XML views, actions, menus
│   ├── odoo-18-performance-guide.md # N+1 prevention
│   ├── odoo-18-transaction-guide.md # Savepoints, errors
│   ├── odoo-18-controller-guide.md # HTTP controllers
│   ├── odoo-18-owl-guide.md       # OWL components
│   ├── odoo-18-migration-guide.md # Migration scripts
│   ├── odoo-18-testing-guide.md   # Testing
│   ├── odoo-18-development-guide.md # Manifest, security
│   └── odoo-18-translation-guide.md # Translations, i18n
├── CLAUDE.md                      # This file
└── AGENTS.md                      # AI agents setup
```

## Which Guide to Use

| Task | Guide |
|------|-------|
| Creating a new module | `dev/odoo-18-development-guide.md` |
| Writing ORM queries/search | `dev/odoo-18-model-guide.md` |
| Defining model fields | `dev/odoo-18-field-guide.md` |
| Using @api decorators | `dev/odoo-18-decorator-guide.md` |
| Writing XML views | `dev/odoo-18-view-guide.md` |
| Fixing slow code/N+1 queries | `dev/odoo-18-performance-guide.md` |
| Handling database errors | `dev/odoo-18-transaction-guide.md` |
| Creating HTTP endpoints | `dev/odoo-18-controller-guide.md` |
| Building OWL components | `dev/odoo-18-owl-guide.md` |
| Upgrading modules/migrating data | `dev/odoo-18-migration-guide.md` |
| Writing tests | `dev/odoo-18-testing-guide.md` |
| Adding translations/localization | `dev/odoo-18-translation-guide.md` |

## Key Odoo 18 Changes

| Change | Old (Odoo 17-) | New (Odoo 18) |
|--------|----------------|---------------|
| List view tag | `<tree>` | `<list>` |
| Dynamic attributes | `attrs="{'invisible': [...]}"` | `invisible="..."` (direct) |
| Delete validation | Override `unlink()` | `@api.ondelete(at_uninstall=False)` |
| Field aggregation | `group_operator=` | `aggregator=` |
| SQL queries | `cr.execute()` | `SQL` class with `execute_query_dict()` |
| Batch create | Single dict | List of dicts (`create([{...}, {...}])`) |

## Critical Anti-Patterns

| Anti-Pattern | Why Bad | Correct Approach |
|--------------|---------|------------------|
| `attrs="{'invisible': [...]}"` | Deprecated in Odoo 18 | Use `invisible="..."` direct attribute |
| `@api.depends('partner_id')` then accessing `partner_id.email` | N queries per record | Add `@api.depends('partner_id.email')` |
| `search()` inside loop | N+1 queries | Use `search()` with `IN` domain or `read_group()` |
| `create()` in loop | N INSERT statements | Batch: `create([{...}, {...}])` |
| Overriding `unlink()` for validation | Breaks module uninstall | Use `@api.ondelete(at_uninstall=False)` |
| Using `<tree>` in Odoo 18 | Deprecated tag | Use `<list>` instead |

## @api Decorator Decision Tree

```
Need to define field behavior?
├── Field computed from other fields → @api.depends
│   └── CAN use dotted paths: `@api.depends('partner_id.email')`
├── Validate data → @api.constrains
│   └── CANNOT use dotted paths: only simple field names
├── Prevent record deletion → @api.ondelete (Odoo 18)
└── Update form UI → @api.onchange
    └── NO CRUD operations allowed

Need to define method behavior?
├── Method-level, doesn't depend on self → @api.model
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

### List View (Odoo 18)

```xml
<list string="Records" editable="bottom" multi_edit="1">
    <field name="state" decoration-success="state == 'done'"/>
    <field name="phone" optional="show"/>
</list>
```

### Delete Validation (Odoo 18)

```python
@api.ondelete(at_uninstall=False)
def _unlink_if_not_draft(self):
    if any(rec.state != 'draft' for rec in self):
        raise UserError("Cannot delete non-draft records")
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
│   └── 18.0.1.0/
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

The guides are based on Odoo 18 source code. Reference these files in your Odoo installation:
- `odoo/models.py` - ORM implementation
- `odoo/fields.py` - Field types
- `odoo/api.py` - Decorators
- `odoo/http.py` - HTTP layer
- `odoo/exceptions.py` - Exception types

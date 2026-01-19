# Odoo 18 Development Guide

This file provides guidance to AI agents when working with Odoo 18 code in this repository.

> **For setup instructions with different AI IDEs, see [AGENTS.md](./AGENTS.md)**

## Documentation Structure

The `docs/odoo/18.0/` directory contains modular guides that can be used independently or together:

```
docs/odoo/18.0/
├── SKILL.md                       # Master reference - start here
├── odoo-18-model-guide.md         # ORM, CRUD operations, domain syntax
├── odoo-18-field-guide.md         # Field types, parameters
├── odoo-18-decorator-guide.md      # @api decorators
├── odoo-18-view-guide.md          # XML views, actions, menus
├── odoo-18-performance-guide.md    # N+1 prevention, optimization
├── odoo-18-controller-guide.md     # HTTP controllers, routing
├── odoo-18-development-guide.md    # Manifest, reports, security, wizards
└── odoo-18.mdc                     # Cursor-compatible rules file
```

## Key Odoo 18 Changes

When reviewing or writing Odoo 18 code, note these breaking changes from earlier versions:

| Change | Old (Odoo 17-) | New (Odoo 18) |
|--------|----------------|---------------|
| List view tag | `<tree>` | `<list>` |
| Delete validation | Override `unlink()` | `@api.ondelete(at_uninstall=False)` |
| Field aggregation | `group_operator=` | `aggregator=` |
| SQL queries | `cr.execute()` | `SQL` class with `execute_query_dict()` |
| Batch create | Single dict | List of dicts (`create([{...}, {...}])`) |

## Which Guide to Use

| Task | Guide |
|------|-------|
| Creating a new module | `odoo-18-development-guide.md` |
| Writing ORM queries/search | `odoo-18-model-guide.md` |
| Defining model fields | `odoo-18-field-guide.md` |
| Using @api decorators | `odoo-18-decorator-guide.md` |
| Writing XML views | `odoo-18-view-guide.md` |
| Fixing slow code/N+1 queries | `odoo-18-performance-guide.md` |
| Creating HTTP endpoints | `odoo-18-controller-guide.md` |

## Critical Anti-Patterns

| Anti-Pattern | Why Bad | Correct Approach |
|--------------|---------|------------------|
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
├── wizard/
│   ├── __init__.py
│   └── my_wizard.py
└── controllers/
    ├── __init__.py
    └── my_controller.py
```

## Base Code Reference

The guides are based on Odoo 18 source code. Reference these files in your Odoo installation:
- `odoo/models.py` - ORM implementation
- `odoo/fields.py` - Field types
- `odoo/api.py` - Decorators
- `odoo/http.py` - HTTP layer
- `odoo/exceptions.py` - Exception types

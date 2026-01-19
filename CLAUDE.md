# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Repository Purpose

This is a documentation repository containing **Odoo 18 development guides**. The guides are organized as modular skill files that can be used independently or together.

## Documentation Structure

```
odoo/18.0/
├── SKILL.md                       # Master reference - start here for overview
├── odoo-18-development-guide.md    # Module structure, manifest, security, reports, wizards
├── odoo-18-model-guide.md          # ORM, CRUD operations, domain syntax, recordsets
├── odoo-18-field-guide.md          # Field types (Char, Monetary, Many2one, etc.)
├── odoo-18-decorator-guide.md       # @api decorators (depends, constrains, onchange, ondelete)
├── odoo-18-view-guide.md           # XML views (list, form, search, kanban), actions, menus
├── odoo-18-performance-guide.md    # N+1 query prevention, optimization patterns
└── odoo-18-controller-guide.md     # HTTP controllers, routing, authentication
```

## Key Odoo 18 Changes

When reviewing or writing Odoo 18 code, note these breaking changes from Odoo 17:

- `<tree>` view tag is now `<list>`
- `@api.ondelete(at_uninstall=False)` is the new pattern for delete validation (replaces overriding `unlink()`)
- `create()` accepts a list of dicts for batch operations
- Use `execute_query_dict()` with SQL class for safe queries
- Prefetch max is 1000 records per batch

## Which Guide to Read

| Task | Guide |
|------|-------|
| Creating a new module | `odoo-18-development-guide.md` |
| Writing ORM queries/search | `odoo-18-model-guide.md` |
| Defining model fields | `odoo-18-field-guide.md` |
| Using @api decorators | `odoo-18-decorator-guide.md` |
| Writing XML views | `odoo-18-view-guide.md` |
| Fixing slow code/N+1 queries | `odoo-18-performance-guide.md` |
| Creating HTTP endpoints | `odoo-18-controller-guide.md` |

## Common Patterns Reference

### N+1 Query Prevention
```python
# BAD - search in loop
for order in orders:
    payments = self.env['payment'].search([('order_id', '=', order.id)])

# GOOD - single query
payments = self.env['payment'].search_read([('order_id', 'in', orders.ids)])
```

### Decorator Decision Tree
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

### @api.depends vs @api.constrains
```python
# @api.depends - CAN use dotted paths
@api.depends('partner_id.email')
def _compute_email(self):
    for rec in self:
        rec.email = rec.partner_id.email

# @api.constrains - CANNOT use dotted paths
@api.constrains('partner_id')  # NOT partner_id.email
def _check_partner(self):
    for rec in self:
        if not rec.partner_id.email:
            raise ValidationError("Email required")
```

### List View (Odoo 18)
```xml
<list string="Records" editable="bottom" multi_edit="1">
    <field name="state" decoration-success="state == 'done'"/>
    <field name="phone" optional="show"/>
</list>
```

## Critical Anti-Patterns

| Anti-Pattern | Why Bad | Correct Approach |
|--------------|---------|------------------|
| `@api.depends('partner_id')` then accessing `partner_id.email` | N queries per record | Add `@api.depends('partner_id.email')` |
| `search()` inside loop | N+1 queries | Use `search()` with `IN` domain or `read_group()` |
| `create()` in loop | N INSERT statements | Batch: `create([{...}, {...}])` |
| `write()` in loop | N UPDATE statements | Write on recordset: `records.write({...})` |
| Overriding `unlink()` for validation | Breaks module uninstall | Use `@api.ondelete(at_uninstall=False)` |
| Using `<tree>` in Odoo 18 | Deprecated tag | Use `<list>` instead |

## Content Source

All guides are based on analysis of Odoo 18 base code located at:
- `odoo/models.py` - ORM implementation
- `odoo/fields.py` - Field types
- `odoo/api.py` - Decorators
- `odoo/http.py` - HTTP layer
- `odoo/exceptions.py` - Exception types

## Repository

`git@github.com:unclecatvn/agent-skills.git`

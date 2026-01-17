# Odoo 18 Development Guides

Complete reference documentation for Odoo 18 development, covering models, fields, decorators, views, performance, controllers, and best practices.

## Introduction

This is a comprehensive reference guide for Odoo 18 development, organized as modular guides that can be used independently or together. Based on analysis of Odoo 18 base source code.

## Documentation Structure

```
odoo/18.0/
├── SKILL.md                       # Master reference - overview
├── odoo-18-development-guide.md    # Module structure, manifest, security, reports, wizards
├── odoo-18-model-guide.md          # ORM, CRUD, domain, recordset
├── odoo-18-field-guide.md          # Field types (Char, Monetary, Many2one, etc.)
├── odoo-18-decorator-guide.md       # @api decorators (depends, constrains, onchange, ondelete)
├── odoo-18-view-guide.md           # XML views (list, form, search, kanban), actions, menus
├── odoo-18-performance-guide.md    # N+1 query prevention, performance optimization
└── odoo-18-controller-guide.md     # HTTP controllers, routing, authentication
```

## The Guides

### 1. Development Guide (`odoo-18-development-guide.md`)

Complete guide to creating Odoo 18 modules:
- Module directory structure
- `__manifest__.py` and all fields
- Security: Access Rights, Record Rules, Groups
- QWeb-PDF, QWeb-HTML reports
- Wizards and TransientModel
- Cron jobs, Server Actions
- Hooks (post_init, pre_init, uninstall)

### 2. Model Guide (`odoo-18-model-guide.md`)

ORM reference and data operations:
- Recordset basics: `browse()`, `exists()`
- Search methods: `search()`, `search_read()`, `read_group()`
- CRUD operations: `create()`, `read()`, `write()`, `unlink()`
- Domain syntax and operators
- Environment context: `with_context()`, `with_user()`, `with_company()`

### 3. Field Guide (`odoo-18-field-guide.md`)

All field types in Odoo 18:
- Simple fields: `Char`, `Text`, `Html`, `Boolean`, `Integer`, `Float`, `Monetary`, `Date`, `Datetime`, `Binary`, `Selection`
- Relational fields: `Many2one`, `One2many`, `Many2many`
- Computed fields with `compute`, `store`, `search`, `inverse`
- Related fields
- Field parameters: `index`, `default`, `copy`, `groups`, `company_dependent`

### 4. Decorator Guide (`odoo-18-decorator-guide.md`)

Odoo API Decorators:
- `@api.model` - Model-level methods
- `@api.depends` - Computed fields (supports dotted paths)
- `@api.depends_context` - Context-dependent computed fields
- `@api.constrains` - Validation (does NOT support dotted paths)
- `@api.onchange` - Form UI updates
- `@api.ondelete` - Delete validation (new in Odoo 18)
- `@api.returns` - Return type specification

### 5. View Guide (`odoo-18-view-guide.md`)

XML Views and QWeb templates:
- View types: `list` (changed from `tree`), `form`, `search`, `kanban`, `graph`, `pivot`, `calendar`
- List view features: `editable`, `decoration`, `optional`, widgets
- Form view structure: sheet, button box, notebook, chatter
- Search view: filters, group by
- Actions: window, server, client, report
- Menus
- View inheritance with XPath

### 6. Performance Guide (`odoo-18-performance-guide.md`)

Odoo performance optimization:
- Prefetch mechanism (PREFETCH_MAX = 1000)
- N+1 query prevention
- Batch operations (create, write, unlink)
- Field selection optimization
- Compute field optimization
- SQL optimization with `execute_query_dict()`

### 7. Controller Guide (`odoo-18-controller-guide.md`)

HTTP controllers and routing:
- Controller class structure
- `@route` decorator with URL parameters
- Authentication types: `auth='user'`, `auth='public'`, `auth='none'`
- Request/Response types: `type='http'`, `type='json'`
- CSRF handling
- Common patterns: JSON endpoints, file download, website pages

## Key Odoo 18 Changes

| Change | Odoo 17 | Odoo 18 |
|--------|---------|---------|
| List view tag | `<tree>` | `<list>` |
| Delete validation | Override `unlink()` | `@api.ondelete(at_uninstall=False)` |
| Batch create | `create({...})` | `create([{...}, {...}])` |
| SQL queries | `cr.execute()` | `env.execute_query_dict(SQL(...))` |

## Quick Start

### Creating a New Module

1. Create directory structure:
```
my_module/
├── __init__.py
├── __manifest__.py
├── models/
│   └── my_model.py
├── views/
│   └── my_model_views.xml
└── security/
    └── ir.model.access.csv
```

2. Read `odoo-18-development-guide.md` to understand manifest and module structure

### Writing Efficient Models

```python
# GOOD: Use automatic prefetch
orders = self.search([('state', '=', 'done')])
for order in orders:
    print(order.name, order.partner_id.name)  # Partners fetched in batch

# BAD: search inside loop (N+1 queries)
for order in orders:
    payments = self.env['payment'].search([('order_id', '=', order.id)])

# GOOD: Use IN domain
payments = self.env['payment'].search_read([('order_id', 'in', orders.ids)])
```

### Decorator Decision Tree

```
Need to define field behavior?
├── Field computed from other fields → @api.depends
├── Validate data → @api.constrains
├── Prevent record deletion → @api.ondelete
└── Update form UI → @api.onchange

Need to define method behavior?
├── Method-level, doesn't depend on self → @api.model
└── Normal record method → no decorator needed
```

## Source Reference

All guides are based on analysis of Odoo 18 base source code:
- `/Users/unclecat/dtg/odoo/odoo/models.py` - ORM implementation
- `/Users/unclecat/dtg/odoo/odoo/fields.py` - Field types
- `/Users/unclecat/dtg/odoo/odoo/api.py` - Decorators
- `/Users/unclecat/dtg/odoo/odoo/http.py` - HTTP layer
- `/Users/unclecat/dtg/odoo/odoo/exceptions.py` - Exception types

## License

MIT License

## Author

UncleCat

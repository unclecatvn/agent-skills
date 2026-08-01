---
name: odoo-16-model
description: Complete reference for Odoo 16 ORM model methods, CRUD operations, domain syntax, and recordset handling. Use this guide when writing model methods, ORM queries, search operations, or working with recordsets.
globs: "**/models/**/*.py"
topics:
  - Recordset basics (browse, exists, empty)
  - Search methods (search, search_read, search_count, search + read)
  - Aggregation methods (read_group public API, _read_group caveats)
  - CRUD operations (create, read, write, unlink)
  - Domain syntax (operators, logical, relational)
  - Environment context (with_context, with_user, with_company)
  - Recordset iteration patterns
when_to_use:
  - Writing ORM queries
  - Performing CRUD operations
  - Building domain filters
  - Using read_group() for aggregations
  - Iterating over recordsets
  - Using environment context
---

# Odoo 16 Model Guide

Complete reference for Odoo 16 ORM model methods, CRUD operations, and recordset handling.

## Table of Contents

1. [Recordset Basics](#recordset-basics)
2. [Search Methods](#search-methods)
3. [read_group Aggregation](#read_group-aggregation)
4. [CRUD Operations](#crud-operations)
5. [Domain Syntax](#domain-syntax)
6. [Environment Context](#environment-context)
7. [Recordset Utility Methods](#recordset-utility-methods)
8. [Iteration Patterns](#iteration-patterns)
9. [Common Patterns](#common-patterns)
10. [Advanced Model Attributes](#advanced-model-attributes)

---

## Recordset Basics

### browse() - Retrieve Records by ID

```python
# Single record (returns a 1-record recordset)
record = self.browse(1)

# Multiple records
records = self.browse([1, 2, 3])

# Empty recordset
empty = self.browse()

# browse() never raises on missing IDs; use .exists() to filter
```

`browse()` always returns a recordset — even for IDs that do not exist in the database. The missing IDs disappear only once you access a field (which triggers a fetch) or filter with `.exists()`.

```python
records = self.browse([1, 999, 1000])
valid_records = records.exists()   # drops missing IDs
```

### Empty Recordset Patterns

```python
# GOOD: use boolean context
if not records:
    return

# GOOD: filter by condition
records = records.filtered(lambda r: r.active)

# GOOD: remove ids that no longer exist in DB
records = records.exists()
```

### ensure_one() - Assert Single Record

```python
order = self.env['sale.order'].search([('name', '=', ref)], limit=1)
order.ensure_one()   # raises ValueError if not exactly 1 record
```

---

## Search Methods

### search() - Find Records

```python
# Basic search - returns a recordset
records = self.search([('state', '=', 'draft')])

# With limit and order
records = self.search(
    [('state', '=', 'draft')],
    limit=10,
    order='date DESC',
)

# With offset (pagination)
records = self.search(
    [('state', '=', 'draft')],
    offset=10,
    limit=10,
)

# Complex domain (polish notation for operators)
records = self.search([
    '&',
    ('state', '=', 'draft'),
    '|',
    ('date', '>=', '2024-01-01'),
    ('date', '=', False),
])
```

Signature in Odoo 16:

```python
def search(self, domain, offset=0, limit=None, order=None, count=False)
```

### search() + read() - Odoo 16-Safe Pattern When You Need Dicts

**Use when**: you want normal recordset behavior for the search step, then a list of dicts for selected fields.

```python
# Search with normal ORM options
records = self.search(
    [('state', '=', 'done')],
    order='date DESC',
    limit=10,
)

# Then read only the fields you actually need
data = records.read(['name', 'amount_total', 'partner_id'])
```

This keeps the documented Odoo 16 flow on public APIs: `search()` returns a recordset, and `read()` converts that recordset into dictionaries when needed.

### search_read() - Find and Read as Dicts

**Use when**: you need records as plain dicts (e.g. for RPC or reports), not recordsets.

```python
data = self.search_read(
    [('state', '=', 'done')],
    ['name', 'date', 'amount_total'],
    order='amount_total desc',
    limit=10,
)
# [{'id': 1, 'name': 'SO001', 'date': '2024-01-15', 'amount_total': 100.0}, ...]
```

`search_read()` is the convenience API when you want dictionaries directly and do not need recordset methods between the search step and the read step.

### search_count() - Count Records

```python
count = self.search_count([('state', '=', 'draft')])
```

If you need an existence-style check, keep that separate from `search_count()`. If you intentionally want a capped probe of the first N matches, that is a different pattern and is not a replacement for `search_count()`:

```python
# At least one matching record?
has_drafts = bool(self.search([('state', '=', 'draft')], limit=1))

# Probe only the first 100 matching rows
sample = self.search([('state', '=', 'draft')], limit=100)
sample_size = len(sample)
```

### read() - Read Field Values

```python
# Read specific fields (returns a list of dicts)
data = records.read(['name', 'state', 'date'])
# [{'id': 1, 'name': 'Test', 'state': 'draft', 'date': ...}, ...]

# Read all fields
data = records.read()
```

For most server-side code, direct attribute access (`record.name`) is preferred over `read()` — Odoo prefetches fields across the recordset automatically.

---

## read_group Aggregation

For Odoo 16 business code, prefer `read_group()`. It is the documented aggregation API and returns dictionaries that are easy to consume in model methods, reports, and UI-oriented code.

`_read_group()` exists in core, but treat it as an internal helper in Odoo 16 documentation. If you inspect or reuse core code that calls `_read_group()`, verify the exact shape in the target Odoo 16 source instead of copying examples from newer versions.

### Aggregate Functions (v16)

Valid aggregate functions in Odoo 16:

| Aggregate | SQL | Result type |
|-----------|-----|-------------|
| `__count` | `COUNT(*)` (no field prefix) | `int` |
| `field:sum` | `SUM(field)` | `float`/`int` |
| `field:avg` | `AVG(field)` | `float` |
| `field:max` | `MAX(field)` | field type |
| `field:min` | `MIN(field)` | field type |
| `field:count` | `COUNT(field)` | `int` (non-null only) |
| `field:count_distinct` | `COUNT(DISTINCT field)` | `int` |
| `field:bool_and` | `BOOL_AND(field)` | `bool` |
| `field:bool_or` | `BOOL_OR(field)` | `bool` |
| `field:array_agg` | `ARRAY_AGG(field ORDER BY id)` | `list` |
Difference between counters:

- `__count` counts every row in the group (like `COUNT(*)`).
- `field:count` counts rows where `field IS NOT NULL`.
- `field:count_distinct` counts distinct non-null values.

### Groupby Granularities (v16)

Supported temporal granularities in Odoo 16:

`hour`, `day`, `week`, `month`, `quarter`, `year`.

Odoo 16 does **not** support numeric granularities like `day_of_month`, `month_number`, `iso_week_number`, `hour_number`, etc. (those were introduced in later versions).

### read_group() - Dict Format for UI

```python
result = self.read_group(
    domain=[('state', '=', 'draft')],
    fields=['amount_total:sum'],
    groupby=['category_id'],
)
# [{'category_id': (1, 'Category A'), 'amount_total': 1500.0,
#   'category_id_count': 3, '__domain': [...], '__context': {...}}]

# `__domain` is useful to drill down:
for group in result:
    orders = self.search(group['__domain'])
```

Multi-groupby:

```python
data = self.read_group(
    domain=[('state', '=', 'done')],
    fields=['partner_id', 'amount_total:sum'],
    groupby=['partner_id', 'date_order:month'],
    lazy=False,   # group by ALL fields at once, not only the first one
)
```

When you see `_read_group()` in Odoo core or framework code, read it as an implementation detail behind aggregation helpers. For user-facing Odoo 16 guidance, prefer examples built on `read_group()`.

### group_expand (ensure empty groups appear)

```python
class SaleOrder(models.Model):
    _name = 'sale.order'

    state = fields.Selection(
        [('draft', 'Draft'), ('confirmed', 'Confirmed'), ('done', 'Done')],
        group_expand='_read_group_expand_states',
    )

    @api.model
    def _read_group_expand_states(self, states, domain, order):
        # Always return every state, even those with 0 records
        return [key for key, _label in type(self).state.selection]
```

---

## CRUD Operations

### create() - Create New Records

In Odoo 16, the `create()` method receives a **list of vals** and returns a **recordset**. If you override it, you must decorate with `@api.model_create_multi` — otherwise Odoo logs `"The model ... is not overriding the create method in batch"` and falls back to the slow per-record wrapper.

```python
from odoo import api, fields, models

class SaleOrder(models.Model):
    _name = 'sale.order'

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            vals.setdefault('state', 'draft')
        orders = super().create(vals_list)
        orders._onboard_new_orders()
        return orders
```

Calls are flexible — both dict and list are accepted:

```python
# Single record (backward-compat, returns 1-record recordset)
record = self.env['sale.order'].create({'partner_id': 1})

# Batch create - recommended whenever you already have many dicts
records = self.env['sale.order'].create([
    {'partner_id': 1},
    {'partner_id': 2},
    {'partner_id': 3},
])
```

Relational fields in `create()` accept the classic command tuples or the `Command` helpers from `odoo.fields`:

```python
from odoo import Command

orders = self.env['sale.order'].create([{
    'partner_id': 1,
    'order_line': [
        Command.create({'product_id': 2, 'product_uom_qty': 3}),
        (0, 0, {'product_id': 5, 'product_uom_qty': 1}),    # equivalent tuple form
    ],
    'tag_ids': [Command.set([1, 2, 3])],
}])
```

x2many command reference:

| Tuple | `Command` helper | Meaning |
|-------|------------------|---------|
| `(0, 0, vals)` | `Command.create(vals)` | Create a new related record |
| `(1, id, vals)` | `Command.update(id, vals)` | Update existing record |
| `(2, id, 0)` | `Command.delete(id)` | Delete from DB |
| `(3, id, 0)` | `Command.unlink(id)` | Remove the relation only |
| `(4, id, 0)` | `Command.link(id)` | Link an existing record |
| `(5, 0, 0)` | `Command.clear()` | Remove all relations |
| `(6, 0, ids)` | `Command.set(ids)` | Replace with this list |

### write() - Update Records

```python
# Update the whole recordset in one statement
records.write({'state': 'done'})

# Several fields at once
records.write({
    'state': 'done',
    'date_done': fields.Datetime.now(),
})
```

`write()` batches SQL updates for the whole recordset. Never call `write()` inside a `for record in records` loop for a scalar change — it issues N separate statements.

### unlink() - Delete Records

Use `@api.ondelete(at_uninstall=False)` (see the decorator guide) for deletion rules instead of overriding `unlink()`:

```python
from odoo.exceptions import UserError

class SaleOrder(models.Model):
    _name = 'sale.order'

    @api.ondelete(at_uninstall=False)
    def _unlink_except_draft(self):
        if any(order.state != 'draft' for order in self):
            raise UserError("Only draft orders can be deleted.")

# Deletion itself:
self.env['sale.order'].browse(ids).unlink()
```

### copy() - Duplicate Records

```python
new_record = record.copy(default={'name': f"{record.name} (copy)"})
```

Fields with `copy=False` (e.g. `state`, dates, sequence numbers) are excluded automatically.

---

## Domain Syntax

### Basic Operators

| Operator | Description | Example |
|----------|-------------|---------|
| `=` | equals | `[('state', '=', 'draft')]` |
| `!=` | not equals | `[('state', '!=', 'draft')]` |
| `>` | greater than | `[('amount', '>', 100)]` |
| `>=` | greater or equal | `[('amount', '>=', 100)]` |
| `<` | less than | `[('amount', '<', 100)]` |
| `<=` | less or equal | `[('amount', '<=', 100)]` |
| `=?` | equals OR value is empty | `[('partner_id', '=?', user_id)]` |
| `in` | value in list | `[('id', 'in', [1, 2, 3])]` |
| `not in` | value not in list | `[('id', 'not in', [1, 2, 3])]` |
| `like` | contains (case-sensitive) | `[('name', 'like', 'test')]` |
| `ilike` | contains (case-insensitive) | `[('name', 'ilike', 'TEST')]` |
| `not like` / `not ilike` | negated contains | `[('name', 'not ilike', 'xxx')]` |
| `=like` / `=ilike` | SQL LIKE without implicit wildcards | `[('code', '=ilike', 'A_1%')]` |
| `child_of` | record is descendant in a parent hierarchy | `[('category_id', 'child_of', 4)]` |
| `parent_of` | record is ancestor of given record | `[('company_id', 'parent_of', 5)]` |

### Logical Operators

Polish prefix notation. `&` / `|` take the next two terms; `!` takes the next one.

```python
# AND is implicit between consecutive terms
domain = [('state', '=', 'draft'), ('date', '>=', '2024-01-01')]

# OR must be explicit
domain = [
    '|',
    ('state', '=', 'draft'),
    ('state', '=', 'confirmed'),
]

# NOT
domain = ['!', ('state', '=', 'draft')]

# (A OR B) AND (C OR D)
domain = [
    '&',
    '|', ('state', '=', 'draft'),        ('state', '=', 'confirmed'),
    '|', ('date', '>=', '2024-01-01'),   ('date', '=', False),
]
```

### Relational Domain Traversal

```python
# Dotted paths on Many2one work directly
domain = [('partner_id.country_id.code', '=', 'US')]

# Dotted traversal across related records can work for simple x2many existence-style filters
domain = [('line_ids.product_id.categ_id', '=', 1)]

# Find orders that contain a service product
domain = [('line_ids.product_id.type', '=', 'service')]
```

If you need more complex "has related record matching X" logic in Odoo 16, prefer valid relation traversal or split the work into two ORM steps. Do not document `any` / `not any` as part of the Odoo 16 public domain syntax.

---

## Environment Context

### with_context() - Set/Override Context Keys

```python
# Language
records.with_context(lang='fr_FR').mapped('name')

# Disable the default `active_test=True` so archived records are included
all_records = self.with_context(active_test=False).search([])

# Binary size instead of content (used in kanban / chatter previews)
attachments.with_context(bin_size=True).read(['datas'])

# Force a specific allowed-companies list
records.with_context(allowed_company_ids=[1, 2]).read(['amount_total'])

# Pass a custom key that your own methods/computed fields depend on
records.with_context(from_cron=True).action_process()
```

### with_user() / sudo() - Change User

```python
# Run as a specific user (respects their access rights)
records.with_user(user).action_confirm()

# Run as the superuser (bypasses security - use sparingly)
record.sudo().write({'notes': 'System note'})
```

### with_company() - Change Current Company

```python
# Temporarily evaluate company-dependent fields for another company
record.with_company(company).read(['property_account_receivable_id'])
```

### Environment Properties and Helpers

```python
# Superuser / admin / system flag
if self.env.is_superuser():
    ...
if self.env.is_admin():
    ...
if self.env.is_system():
    ...

# Current user, company, and enabled companies
self.env.user        # res.users record
self.env.company     # res.company record
self.env.companies   # recordset of all allowed companies
self.env.lang        # str or None

# ref('module.xml_id') -> record
default_partner = self.env.ref('base.partner_root')

# Translation function
from odoo import _

translated = _("Hello %s") % name
```

### Raw SQL (Odoo 16)

Prefer the ORM. Drop to SQL only for reporting, bulk updates that the ORM would slow down, or for referencing virtual tables. In Odoo 16 the canonical form is:

```python
self.env.cr.execute(
    "SELECT id, name FROM sale_order WHERE state = %s",
    ('done',),
)
rows = self.env.cr.fetchall()           # list of tuples
dicts = self.env.cr.dictfetchall()      # list of dicts
```

Always flush pending writes to DB before a raw SQL read that depends on them:

```python
self.env['sale.order'].flush_model(['amount_total'])
self.env.cr.execute("SELECT SUM(amount_total) FROM sale_order")
```

---

## Recordset Utility Methods

### mapped() - Extract Field Values

```python
# Scalar field -> list
names = records.mapped('name')

# Relational field -> recordset (duplicates removed, order arbitrary)
partners = records.mapped('partner_id')
banks = records.mapped('partner_id.bank_ids')

# Lambda -> list (or recordset if the lambda returns recordsets)
doubled = records.mapped(lambda r: r.amount_total * 2)
```

### filtered() - Filter by Predicate

```python
# Lambda
done_orders = orders.filtered(lambda o: o.state == 'done')

# Short form: field name (including dotted path, True if any related record is truthy)
companies = partners.filtered('is_company')
has_banks = partners.filtered('bank_ids')
```

### filtered_domain() - Filter by Domain

```python
# Keeps recordset order, evaluates the domain in Python against cached values
done = orders.filtered_domain([('state', '=', 'done')])

urgent = orders.filtered_domain([
    '&',
    ('state', '=', 'draft'),
    '|', ('priority', '=', '2'),
        ('date', '<', fields.Date.today()),
])
```

### Plain Python Grouping

```python
from collections import defaultdict

order_ids_by_state = defaultdict(list)
for order in orders:
    order_ids_by_state[order.state].append(order.id)

for state, order_ids in order_ids_by_state.items():
    state_orders = orders.browse(order_ids)
    print(f"{state}: {len(state_orders)} orders")
```

Use this as conservative fallback guidance when you do want to partition a recordset in Python, but do not want to rely on higher-level helpers that are not documented here as Odoo 16-safe.

### sorted() - Sort Recordset

```python
# By field
records.sorted('name')

# By lambda
records.sorted(key=lambda r: r.amount_total, reverse=True)

# Default model order (None -> use `_order`)
records.sorted()
```

Note that `sorted()` operates in memory on the recordset; for large result sets it is usually faster to add `order=...` to the original `search()` call.

### Comparison

| Method | Returns | Use case |
|--------|---------|----------|
| `mapped()` | list or recordset | Extract field values |
| `filtered()` | recordset | Keep records matching predicate |
| `filtered_domain()` | recordset | Predicate as a domain (preserves order) |
| Python grouping (`defaultdict`, `setdefault`) | dict/list | Partition (no aggregation, no SQL) |
| `sorted()` | recordset | In-memory sort |

---

## Iteration Patterns

### GOOD: Leverage Prefetching

```python
# Fields are prefetched across the recordset automatically
for order in orders:
    print(order.name, order.amount_total, order.partner_id.name)
# -> 1 query for orders, 1 query for partners
```

### BAD: N+1 Pattern

```python
# BAD: search inside the loop -> N queries
for order in orders:
    payments = self.env['account.payment'].search([('order_id', '=', order.id)])

# GOOD: one query with IN
payments_by_order = {}
payments = self.env['account.payment'].search([('order_id', 'in', orders.ids)])
for payment in payments:
    payments_by_order.setdefault(payment.order_id.id, []).append(payment)
```

### BAD: Writing inside a loop

```python
# BAD: N UPDATE statements
for record in records:
    record.write({'state': 'done'})

# GOOD: 1 UPDATE
records.write({'state': 'done'})

# GOOD when each record needs a different value: conservative Python-side partitioning
from collections import defaultdict

record_ids_by_category = defaultdict(list)
for record in records:
    record_ids_by_category[record.category_id.id].append(record.id)

categories = records.mapped('category_id')
for category in categories:
    subset = self.browse(record_ids_by_category[category.id])
    subset.write({'computed_field': category.default_value})
```

This is a conservative fallback for Odoo 16-safe documentation, not a claim that Python grouping should always be your first choice.

---

## Common Patterns

### Check Emptiness

```python
if not records:
    return {}

# Don't confuse browse() return with existence check
records = self.browse(ids).exists()   # drop IDs that no longer exist
```

### Retrieve Exactly One Record

```python
record = self.search([('code', '=', code)], limit=1)
if not record:
    raise UserError(_("No record found for code %s") % code)
```

### Raise Missing Error on Stale References

```python
from odoo.exceptions import MissingError

records = self.browse(ids)
if len(records.exists()) != len(records):
    raise MissingError(_("Some records were deleted."))
```

### Ordered Searches

```python
# Prefer DB-level order; it's faster and uses indexes
records = self.search([('state', '=', 'draft')], order='date_order DESC, id DESC')
```

### Iterating Chunks for Heavy Jobs

```python
BATCH = 500
all_records = self.search(domain)
for i in range(0, len(all_records), BATCH):
    batch = all_records[i:i + BATCH]
    batch.action_process()
    self.env.cr.commit()     # persist progress; only in cron/migration scripts
```

---

## Advanced Model Attributes

### Model Header Attributes

```python
class SaleOrder(models.Model):
    _name = 'sale.order'                 # REQUIRED model name (dot-notation)
    _description = 'Sales Order'         # human label (used in access rules, logs)
    _inherit = ['mail.thread']           # mixins / parent models to extend
    _order = 'date_order DESC, id DESC'  # default ordering for search()
    _rec_name = 'name'                   # field used for display_name if not overridden
    _rec_names_search = ['name', 'ref']  # fields scanned by name_search()
    _check_company_auto = True           # auto-validate check_company=True relations
```

Odoo 16 **requires** `_name` on every concrete model (there is no auto-naming from the Python class name).

### _parent_store - Hierarchical Optimisation

```python
class Category(models.Model):
    _name = 'product.category'
    _parent_name = 'parent_id'         # default; only set to override
    _parent_store = True               # enable parent_path storage
    _order = 'parent_path'

    name = fields.Char(required=True)
    parent_id = fields.Many2one('product.category', ondelete='cascade')
    parent_path = fields.Char(index=True, unaccent=False)
```

`_parent_store=True` maintains a `parent_path` string (`/1/5/17/`). This makes `child_of` / `parent_of` domain operators index-friendly and avoids recursive CTE queries.

### _check_company_auto - Company Consistency

```python
class Invoice(models.Model):
    _name = 'account.move'
    _check_company_auto = True

    company_id = fields.Many2one('res.company', required=True)
    partner_id = fields.Many2one('res.partner', check_company=True)
    journal_id = fields.Many2one('account.journal', check_company=True)
```

When `_check_company_auto=True`, Odoo calls `_check_company()` on `create()` / `write()` and raises a `UserError` if any `check_company=True` relation points to a company that is not compatible with `self.company_id`.

### SQL Constraints (v16)

SQL-level constraints are declared via `_sql_constraints` — a list of `(name, sql_definition, error_message)` triples.

```python
class SaleOrder(models.Model):
    _name = 'sale.order'

    _sql_constraints = [
        ('name_uniq', 'UNIQUE(company_id, name)',
         'Order reference must be unique per company!'),
        ('positive_amount', 'CHECK(amount_total >= 0)',
         'Total amount must be positive.'),
    ]
```

### Attribute Reference

| Attribute | Type | Default | Purpose |
|-----------|------|---------|---------|
| `_name` | str | — (required) | Model name used in the registry |
| `_description` | str | `_name` | Human label for logs/ACLs |
| `_inherit` | str or list | `()` | Models to extend / mix in |
| `_inherits` | dict | `{}` | Delegation inheritance (`{'parent.model': 'fk_field'}`) |
| `_order` | str | `'id'` | Default `ORDER BY` clause for `search()` |
| `_rec_name` | str | `'name'` (if present) | Field used to compute `display_name` |
| `_rec_names_search` | list | `None` | Fields searched by `name_search()` |
| `_parent_name` | str | `'parent_id'` | Many2one used for hierarchy |
| `_parent_store` | bool | `False` | Enable `parent_path` for hierarchical queries |
| `_fold_name` | str | `'fold'` | Field used for fold state in kanban |
| `_active_name` | str | auto-detected | Field used for archiving (`active` or `x_active`) |
| `_check_company_auto` | bool | `False` | Auto-validate `check_company=True` relations |
| `_sql_constraints` | list | `[]` | `[(name, SQL expression, message), ...]` |
| `_transient` | bool | `False` | `True` for `TransientModel` (wizards) |
| `_abstract` | bool | `False` | `True` for `AbstractModel` (no DB table) |
| `_register` | bool | `True` | Whether to register in the model registry |
| `_log_access` | bool | `True` | Whether `create_date`, `write_date`, etc. are maintained |

---

## Python and Odoo Conventions

- Order imports into standard/external libraries, `odoo` imports, then imports
  from Odoo addons; alphabetize within each group.
- Prefer readable built-ins, comprehensions, and recordset helpers such as
  `filtered`, `mapped`, and `sorted` over clever abstractions. Avoid custom
  generators and decorators in addon business code.
- Use singular dotted model names. Use CamelCase classes, `snake_case` normal
  variables, and `_id`/`_ids` only for integer IDs rather than recordsets.
- Keep model declarations ordered: private attributes, `default_get` and
  `_default_*` helpers, fields, compute/inverse/search methods, selection
  methods, constraints/onchanges, CRUD overrides, actions, then business
  methods.
- Design overrides to be extendable: call `super()`, avoid assumptions about
  a singleton unless the method explicitly calls `ensure_one()`, and avoid
  mutating context directly. Use `with_context()` for a derived environment.
- Context is immutable and automatically propagated. Avoid generic
  `default_<field>` keys: they can become defaults for nested creates on any
  model with the same field name. Prefix custom behavior keys with the module
  name and keep their scope narrow.

## Base Code Reference

The examples in this guide track Odoo 16's source. Verify behaviour in:

- `/Users/unclecat/odoo/16.0/odoo/models.py` — `BaseModel` class, `search*`, `read_group`, `create`, `write`, `unlink`, domain evaluation, recordset utilities.
- `/Users/unclecat/odoo/16.0/odoo/fields.py` — `Command` enum for x2many operations.
- `/Users/unclecat/odoo/16.0/odoo/api.py` — `Environment` class and context helpers.
- `/Users/unclecat/odoo/16.0/odoo/osv/expression.py` — domain operators and relation traversal (`child_of`, `parent_of`, logical operators).

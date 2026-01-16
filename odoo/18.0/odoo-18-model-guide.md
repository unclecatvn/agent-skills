# Odoo 18 Model Guide

Complete reference for Odoo 18 ORM model methods, CRUD operations, and recordset handling.

## Table of Contents

1. [Recordset Basics](#recordset-basics)
2. [Search Methods](#search-methods)
3. [CRUD Operations](#crud-operations)
4. [Domain Syntax](#domain-syntax)
5. [Environment Context](#environment-context)

---

## Recordset Basics

### browse() - Retrieve Records by ID

```python
# Single record
record = self.browse(1)

# Multiple records (returns empty recordset if not found)
records = self.browse([1, 2, 3])

# Empty recordset
empty = self.browse()

# Prefetching: Odoo automatically prefetches up to PREFETCH_MAX (1000) records
# When accessing fields on related records, they are fetched in batch
```

**Important**: `browse()` always returns a recordset, even for IDs that don't exist. Use `.exists()` to filter.

```python
records = self.browse([1, 999, 1000])  # 999, 1000 may not exist
valid_records = records.exists()  # Only existing records
```

### Empty Recordset Pattern

```python
# GOOD: Handle empty recordsets explicitly
if not records:
    return

# GOOD: Use filtered() for conditional operations
records = records.filtered(lambda r: r.active)

# GOOD: Use exists() to remove non-existing records
records = records.exists()
```

---

## Search Methods

### search() - Find Records

```python
# Basic search - returns recordset
records = self.search([('state', '=', 'draft')])

# With limit and order
records = self.search(
    [('state', '=', 'draft')],
    limit=10,
    order='date DESC'
)

# With offset
records = self.search(
    [('state', '=', 'draft')],
    offset=10,
    limit=10
)

# Complex domain
records = self.search([
    '&',
    ('state', '=', 'draft'),
    '|',
    ('date', '>=', '2024-01-01'),
    ('date', '=', False)
])
```

### search_read() - Find and Read in One Query

**Use when**: You need records as dictionaries, not recordsets.

```python
# Returns list of dicts
data = self.search_read(
    [('state', '=', 'done')],
    ['name', 'date', 'amount']
)
# Result: [{'id': 1, 'name': 'Test', 'date': '...', 'amount': 100.0}, ...]

# With ordering and limit
data = self.search_read(
    [('state', '=', 'done')],
    ['name', 'amount'],
    order='amount desc',
    limit=10
)
```

**Performance**: `search_read()` is more efficient than `search().read()` when you only need specific fields as dicts.

### search_count() - Count Records

```python
count = self.search_count([('state', '=', 'draft')])
# Returns integer
```

### read_group() - Aggregation

```python
# Group by field
result = self.read_group(
    [('state', '=', 'draft')],
    ['amount_total:sum'],
    ['category_id']
)
# Result: [{'category_id': [1, 'Category A'], 'amount_total': 1500.0, '__domain': [...]}]

# With time granularity
result = self.read_group(
    [('date', '>=', '2024-01-01')],
    ['amount:sum'],
    ['date:month']
)

# Multiple groupby
result = self.read_group(
    domain,
    ['amount:sum', 'quantity:avg'],
    ['category_id', 'state']
)
```

**Supported aggregates**: `sum`, `avg`, `min`, `max`, `count`, `count_distinct`, `bool_and`, `bool_or`, `array_agg`

---

## CRUD Operations

### create() - Create New Records

**Odoo 18**: `create()` expects a list of dicts and returns a recordset.

```python
# Single record (also accepts dict for compatibility)
record = self.create({'name': 'Test', 'state': 'draft'})

# Multiple records - BATCH create (recommended)
records = self.create([
    {'name': 'Record 1', 'state': 'draft'},
    {'name': 'Record 2', 'state': 'draft'},
    {'name': 'Record 3', 'state': 'draft'},
])
# Returns: recordset of 3 records

# With relational fields
records = self.create([{
    'name': 'Test',
    'partner_id': 1,  # many2one
    'line_ids': [(0, 0, {  # one2many - create new line
        'product_id': 1,
        'quantity': 2,
    })],
    'tag_ids': [(6, 0, [1, 2, 3])],  # many2many - replace with these
}])
```

**One2many commands**:
- `(0, 0, {...})` - Create new record
- `(1, id, {...})` - Update existing record
- `(2, id, ...)` - Remove record (delete from db)
- `(3, id, ...)` - Unlink (remove relation)
- `(4, id, ...)` - Link existing record
- `(5, ...)` - Unlink all
- `(6, 0, [ids])` - Replace with these

### read() - Read Field Values

```python
# Read specific fields (returns list of dicts)
data = records.read(['name', 'state', 'date'])
# Result: [{'id': 1, 'name': 'Test', 'state': 'draft', 'date': '...'}, ...]

# Read all fields
data = records.read()

# Load parameter for performance
data = records.read(['name'], load='_classic_read')
```

**Note**: Using record.field access is usually more efficient than `read()` for recordsets due to prefetching.

### write() - Update Records

```python
# Update all records in recordset
records.write({'state': 'done'})

# Update single record
record.write({'name': 'Updated Name'})

# Update multiple fields
records.write({
    'state': 'done',
    'date_done': fields.Datetime.now(),
})
```

**Performance**: `write()` is batched automatically for the recordset.

### unlink() - Delete Records

```python
# Delete all records in recordset
records.unlink()

# Delete with validation
@api.ondelete(at_uninstall=False)
def _unlink_if_not_done(self):
    if any(rec.state == 'done' for rec in self):
        raise UserError("Cannot delete completed records")

# Then in your method
self.unlink()
```

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
| `=?` | undefined or equals | `[('partner_id', '=?', user_id)]` |
| `in` | in list | `[('id', 'in', [1, 2, 3])]` |
| `not in` | not in list | `[('id', 'not in', [1, 2, 3])]` |
| `like` | contains (case-sensitive) | `[('name', 'like', 'test')]` |
| `ilike` | contains (case-insensitive) | `[('name', 'ilike', 'TEST')]` |
| `not like` | does not contain | `[('name', 'not like', 'test')]` |
| `=ilike` | contains (case-insensitive, undefined or equals) | `[('name', '=ilike', 'test')]` |
| `=like` | contains (case-sensitive, undefined or equals) | `[('name', '=like', 'test')]` |
| `child_of` | is child (in hierarchy) | `[('category_id', 'child_of', category_id)]` |
| `parent_of` | is parent (in hierarchy) | `[('company_id', 'parent_of', company_id)]` |

### Logical Operators

```python
# AND (implicit - default)
domain = [('state', '=', 'draft'), ('date', '>=', '2024-01-01')]

# OR (explicit)
domain = [
    '|',
    ('state', '=', 'draft'),
    ('state', '=', 'confirmed')
]

# NOT
domain = [('!', ('state', '=', 'draft'))]

# Complex: (A OR B) AND (C OR D)
domain = [
    '&',
    '|',
    ('state', '=', 'draft'),
    ('state', '=', 'confirmed'),
    '|',
    ('date', '>=', '2024-01-01'),
    ('date', '=', False)
]
```

### Relational Field Domains

```python
# Many2one field traversal
domain = [('partner_id.country_id.code', '=', 'US')]

# One2many/Many2many - using any record
domain = [('line_ids.product_id.categ_id', '=', 1)]

# Using related field
domain = [('partner_city', '=', 'New York')]  # if partner_id.city related
```

---

## Environment Context

### with_context() - Modify Context

```python
# Change language
records.with_context(lang='fr_FR').name

# Disable active_test for archiving
all_records = self.with_context(active_test=False).search([])

# Bin size for binary fields
attachments.with_context(bin_size=True).read(['datas'])

# Company context
records.with_context(allowed_company_ids=[1, 2])

# Timezone
records.with_context(tz='Asia/Ho_Chi_Minh')

# Custom context key
records.with_context(from_batch=True).action_process()
```

### with_user() - Change User

```python
# Run as different user
records.with_user(user_id).write({'notes': 'Admin note'})

# Run as superuser (use sparingly)
records.sudo().write({'notes': 'System note'})
```

### with_company() - Change Company

```python
# Set specific company
records.with_company(company_id).read(['amount'])

# In multi-company context
records.with_company(main_company).action_process()
```

---

## Recordset Iteration Patterns

### GOOD: Batch Field Access

```python
# GOOD: Fields are prefetched automatically
for order in orders:
    print(order.name, order.amount, order.partner_id.name)
# Only 2 queries: one for orders, one for all partners

# GOOD: Access related recordset
for order in orders:
    for line in order.line_ids:
        print(line.product_id.name)
# Lines and products are prefetched
```

### BAD: N+1 Query Pattern

```python
# BAD: search inside loop
for order in orders:
    partner = self.env['res.partner'].browse(order.partner_id.id)
    print(partner.name)  # New query each iteration

# BAD: Access field that triggers search
for order in orders:
    print(order.message_ids[0].author_id.name)  # New query each time

# GOOD: Pre-fetch messages
orders.read(['message_ids'])  # or use with prefetch
for order in orders:
    if order.message_ids:
        print(order.message_ids[0].author_id.name)
```

---

## Common Patterns

### Check if Recordset is Empty

```python
# GOOD: Use boolean context
if not records:
    return {}

# GOOD: Check length
if len(records) == 0:
    return {}

# BAD: Don't use .exists() for empty check
if not records.exists():  # This is wrong - empty.exists() is empty
    return {}
```

### Ensure Records Exist

```python
# GOOD: Filter out non-existing records
valid_records = records.exists()

# GOOD: Raise error if missing
if not records.exists():
    raise MissingError(_('Record not found'))
```

### Get Single Record

```python
# GOOD: Ensure single record
records = self.search([('code', '=', 'ABC')], limit=1)
if not records:
    raise UserError(_('No record found'))

# GOOD: Use ensure_one()
records = self.search([('code', '=', 'ABC')])
records.ensure_one()
```

### Sorted Recordsets

```python
# Sorted by field (in memory, not efficient for large sets)
sorted_records = records.sorted(key=lambda r: r.date, reverse=True)

# Sorted by default model order
sorted_records = records.sorted()

# Use database order instead
records = self.search(domain, order='date DESC')
```

---
name: odoo-18-model
description: Complete reference for Odoo 18 ORM model methods, CRUD operations, domain syntax, and recordset handling. Use this guide when writing model methods, ORM queries, search operations, or working with recordsets.
topics:
  - Recordset basics (browse, exists, empty)
  - Search methods (search, search_read, search_count, read_group)
  - CRUD operations (create, read, write, unlink)
  - Domain syntax (operators, logical, relational)
  - Environment context (with_context, with_user, with_company)
  - Recordset iteration patterns
when_to_use:
  - Writing ORM queries
  - Performing CRUD operations
  - Building domain filters
  - Iterating over recordsets
  - Using environment context
---

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

---

## read_group Internals (Odoo 18)

### READ_GROUP Constants

```python
# Time granularity (date_trunc)
READ_GROUP_TIME_GRANULARITY = {
    'hour', 'day', 'week', 'month', 'quarter', 'year'
}

# Number granularity (date_part)
READ_GROUP_NUMBER_GRANULARITY = {
    'year_number': 'year',
    'quarter_number': 'quarter',
    'month_number': 'month',
    'iso_week_number': 'week',
    'day_of_year': 'doy',
    'day_of_month': 'day',
    'day_of_week': 'dow',
    'hour_number': 'hour',
    'minute_number': 'minute',
    'second_number': 'second',
}

# All granularities
READ_GROUP_ALL_TIME_GRANULARITY = READ_GROUP_TIME_GRANULARITY | READ_GROUP_NUMBER_GRANULARITY

# Supported aggregate functions
READ_GROUP_AGGREGATE = {
    'sum', 'avg', 'max',', 'min',
    'bool_and', 'bool_or',
    'array_agg', 'recordset',
    'count', 'count_distinct',
}
```

### Aggregate Specification Format

```
<field_name>:<aggregate>    # e.g., "amount:sum", "quantity:avg"
<field_name>:<granularity>   # e.g., "date:month", "date:year"
<field_name>.<property>:<granularity>  # e.g., "date_deadline:month"
```

### _read_group_select (Odoo 18)

Internal method to generate SQL for aggregation.

```python
# Odoo uses this internally
sql_expr = self._read_group_select('amount:sum', query)
# Returns: SQL('SUM(%s)', sql_field)
```

### _read_group_groupby (Odoo 18)

Internal method to generate SQL for groupby.

```python
# Date with granularity
sql_expr = self._read_group_groupby('date:month', query)
# Returns: date_trunc('month', sql_field::timestamp)

# Number granularity
sql_expr = self._read_group_groupby('date:day_of_month', query)
# Returns: date_part('day', sql_field)::int
```

### read_group Result Format

```python
result = self.read_group(
    [('state', '!=', False)],
    ['amount:sum', 'count'],
    ['state', 'date:month'],
)
# Result:
# [
#     {
#         'state': 'draft',
#         'date:month': datetime(2024, 1, 1),
#         'amount': 15000.0,
#         'count': 10,
#         '__domain': [(('state', '=', 'draft'), ...)],
#     },
#     ...
# ]
```

### group_expand Parameter (Odoo 18)

Expand groups to include all possible values.

```python
# Field with group_expand function
state = fields.Selection(
    selection=lambda self: self._get_states(),
    group_expand='_read_group_expand_states',
)

@api.model
def _read_group_expand_states(self, values, domain):
    # Return all possible states to show empty groups
    return ['draft', 'confirmed', 'done', 'cancel']
```

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

## Environment Methods (Odoo 18)

### New SQL Query Methods (Odoo 18)

```python
from odoo.tools import SQL

# execute_query_dict - returns list of dicts, auto-flushes
query = SQL("""
    SELECT id, name, amount
    FROM sale_order
    WHERE state = %s
""", 'done')

results = self.env.execute_query_dict(query)
# Returns: [{'id': 1, 'name': 'SO001', 'amount': 100.0}, ...]

# execute_query - returns list of tuples, auto-flushes
results = self.env.execute_query(query)
# Returns: [(1, 'SO001', 100.0), ...]
```

### Environment Check Methods (Odoo 18)

```python
# Check if in superuser mode
if self.env.is_superuser():
    # Running as superuser (sudo mode)
    pass

# Check if current user is admin (has "Access Rights" group)
if self.env.is_admin():
    # User has admin rights
    pass

# Check if current user has system settings rights
if self.env.is_system():
    # User can access settings
    pass
```

### Environment Properties (Odoo 18)

```python
# Get current user (as record, sudoed)
user = self.env.user

# Get current company
company = self.env.company

# Get enabled companies (recordset)
companies = self.env.companies

# Get current language
lang = self.env.lang

# Get translation method
translated = self.env._("Hello World")
```

### flush_query (Odoo 18)

```python
from odoo.tools import SQL

# Flush specific fields before query
query = SQL("SELECT ...")
query.to_flush = [self._fields['amount']]  # Mark fields to flush
self.env.flush_query(query)
self.env.cr.execute(query)
```

---

## Recordset Utility Methods (Odoo 18)

### mapped() - Extract Field Values

Apply function or get field values from all records.

```python
# Get field values as list
names = records.mapped('name')        # ['A', 'B', 'C']
partner_ids = records.mapped('partner_id')  # recordset of partners

# Nested path - returns union of related records
banks = records.mapped('partner_id.bank_ids')  # recordset, duplicates removed

# With lambda function
amounts = records.mapped(lambda r: r.amount_total * 1.1)

# Multi-level dotted path
emails = records.mapped('partner_id.email')
```

### filtered() - Filter Records

Return records satisfying a condition.

```python
# With lambda
done_orders = orders.filtered(lambda r: r.state == 'done')

# With field name (short syntax)
companies = records.filtered('partner_id.is_company')

# With dotted path - checks if ANY related record satisfies
# records.filtered("partner_id.bank_ids")  # True if has any banks
```

### filtered_domain() - Filter by Domain (Odoo 18)

Filter records by domain while keeping order.

```python
# Filter by domain (keeps original order)
done_orders = orders.filtered_domain([('state', '=', 'done')])

# Complex domain
urgent = orders.filtered_domain([
    '&',
    ('state', '=', 'draft'),
    '|',
    ('priority', '=', '2'),
    ('date', '<', fields.Date.today()),
])
```

### grouped() - Group Records (Odoo 18)

Group records by key without aggregation overhead.

```python
# Group by field name
groups = records.grouped('state')
# Returns: {'draft': recordset1, 'done': recordset2, ...}

# Group by callable
groups = records.grouped(lambda r: r.company_id)

# Process groups
for company, company_records in groups.items():
    print(f"{company.name}: {len(company_records)} records")

# All recordsets share the same prefetch set for efficiency
```

**Note**: Unlike `itertools.groupby`, `grouped()` doesn't require pre-sorting.

### sorted() - Sort Records

Return records sorted by key.

```python
# Sort by field name
sorted_records = records.sorted('name')

# Sort by lambda
sorted_records = records.sorted(key=lambda r: r.amount_total)

# Reverse sort
sorted_records = records.sorted(key=lambda r: r.amount_total, reverse=True)

# Sort by model default order (if key=None)
sorted_records = records.sorted()  # Uses model's _order
```

### Method Comparison

| Method | Returns | Use Case |
|--------|---------|----------|
| `mapped()` | list or recordset | Extract values from all records |
| `filtered()` | recordset | Keep records matching condition |
| `filtered_domain()` | recordset | Filter by domain (keeps order) |
| `grouped()` | dict | Group by key (no aggregation) |
| `sorted()` | recordset | Sort records by key |

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

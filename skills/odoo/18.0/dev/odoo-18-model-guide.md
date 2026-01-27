---
name: odoo-18-model
description: Complete reference for Odoo 18 ORM model methods, CRUD operations, domain syntax, and recordset handling. Use this guide when writing model methods, ORM queries, search operations, or working with recordsets.
globs: "**/models/**/*.py"
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

### search_fetch() - Search and Fetch Fields (Odoo 18)

**Use when**: You need to search AND prefetch specific fields to cache in one operation.

```python
# Search and fetch fields to cache
records = self.search_fetch(
    [('state', '=', 'done')],
    ['name', 'amount_total', 'partner_id'],
    order='date DESC',
    limit=10
)
# Returns recordset with specified fields already in cache

# Equivalent to but more efficient than:
records = self.search([('state', '=', 'done')], order='date DESC', limit=10)
records.fetch(['name', 'amount_total', 'partner_id'])
```

**Performance**: `search_fetch()` is optimized to fetch specified fields in the same query as the search, minimizing database round trips. Use when you know exactly which fields you'll need.

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
| `any` | any related record matches domain | `[('line_ids', 'any', [('state', '=', 'done')])]` |
| `not any` | no related record matches domain | `[('line_ids', 'not any', [('state', '=', 'done')])]` |

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

### Relational Domain Operators (Odoo 18)

```python
# any - matches if ANY related record satisfies the domain
domain = [
    ('invoice_status', '=', 'to invoice'),
    ('order_line', 'any', [('product_id.qty_available', '<=', 0)])  # Has out-of-stock products
]

# not any - matches if NO related record satisfies the domain
domain = [
    ('order_line', 'not any', [('product_id.type', '=', 'service')])  # No service products
]

# parent_of - is parent in hierarchy (inverse of child_of)
domain = [
    ('company_id', 'parent_of', company_id)  # company_id is parent of specified company
]
```

**Important**: `any` and `not any` work with `Many2one`, `One2many`, and `Many2many` fields to check if ANY/NO related record satisfies the given domain.

### Date Field Granularities (Odoo 18)

```python
# Date granularities for domain filtering (returns integer)
domain = [
    ('birthday:day_of_month', '=', 15),     # Day of month (1-31)
    ('birthday:month_number', '=', 2),       # Month number (1-12)
    ('birthday:iso_week_number', '=', 10),    # ISO week number (1-53)
    ('birthday:day_of_year', '=', 100),       # Day of year (1-366)
    ('birthday:day_of_week', '=', 1),         # Day of week (0=Monday, 6=Sunday)
    ('date_order:hour_number', '=', 14),       # Hour (0-23)
    ('date_order:minute_number', '=', 30),     # Minute (0-59)
    ('date_order:second_number', '=', 0),      # Second (0-59)
]

# Time granularity for read_group
result = self.read_group(
    [('create_date', '>=', fields.DateTime.now())],
    ['amount:sum'],
    ['create_date:day']       # Truncate to day
    # Other options: hour, week, month, quarter, year
)
```

**Supported Date Granularities**:

| Granularity | Type | Use Case |
|-------------|------|----------|
| `year_number` | Integer | Year number (2024, 2025, ...) |
| `quarter_number` | Integer | Quarter number (1-4) |
| `month_number` | Integer | Month number (1-12) |
| `iso_week_number` | Integer | ISO week number (1-53) |
| `day_of_year` | Integer | Day of year (1-366) |
| `day_of_month` | Integer | Day of month (1-31) |
| `day_of_week` | Integer | Day of week (0=Mon, 6=Sun) |
| `hour_number` | Integer | Hour (0-23) |
| `minute_number` | Integer | Minute (0-59) |
| `second_number` | Integer | Second (0-59) |

**Note**: For `read_group`, you can use `day`, `week`, `month`, `quarter`, `year`, `hour` which truncate the date to that granularity.

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

---

## Advanced Model Attributes (Odoo 18)

### _check_company_auto - Automatic Company Consistency

```python
class MyModel(models.Model):
    _name = 'my.model'
    _check_company_auto = True

    company_id = fields.Many2one('res.company', required=True)
    partner_id = fields.Many2one(
        'res.partner',
        check_company=True  # Will be validated automatically
    )
```

**Behavior**:
- Automatically calls `_check_company()` on `create()` and `write()`
- Ensures relational fields with `check_company=True` have consistent companies
- Prevents records from linking to companies incompatible with their own company
- Use in multi-company environments to maintain data integrity

### _parent_store - Hierarchical Tree Optimization

```python
class Category(models.Model):
    _name = 'my.category'
    _parent_name = 'parent_id'  # Many2one field to use as parent
    _parent_store = True  # Enable parent_path computation

    name = fields.Char(required=True)
    parent_id = fields.Many2one('my.category', string='Parent Category')
    parent_path = fields.Char(index=True)  # Computed automatically
```

**Behavior**:
- Computes and stores `parent_path` field for efficient tree queries
- Enables fast `child_of` and `parent_of` domain operators
- Automatically maintained when records are created/updated
- Use for hierarchical models (categories, forums, org structures)
- Requires `parent_path` field with `index=True`

**Benefits**:
- Tree queries are much faster with `parent_path` than recursive queries
- No need for recursive SQL queries
- `child_of` and `parent_of` operators become efficient

**Note**: `_parent_store` requires a properly configured `parent_id` field and `parent_path` field.

### Model Attribute Reference

| Attribute | Type | Default | Description |
|-----------|------|---------|-------------|
| `_check_company_auto` | bool | `False` | Auto-check company consistency on write/create |
| `_parent_name` | str | `'parent_id'` | Field to use as parent in hierarchy |
| `_parent_store` | bool | `False` | Enable parent_path for fast tree queries |
| `_fold_name` | str | `'fold'` | Field to determine folded groups in kanban |
| `_order` | str | `'id'` | Default order for search results |
| `_rec_name` | str | `'name'` | Field to use for display name |
| `_sequence` | int | auto | Sequence number for model ordering |
| `_register` | bool | `False` | Registry visibility (set to False for abstract classes) |

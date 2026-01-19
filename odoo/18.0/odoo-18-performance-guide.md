---
name: odoo-18-performance
description: Complete guide for writing performant Odoo 18 code, focusing on N+1 query prevention, batch operations, and optimization patterns.
globs: **/*.{py,xml}
topics:
  - Prefetch mechanism (how it works, understanding groups)
  - N+1 query prevention patterns
  - Batch operations (create, write, unlink)
  - Field selection optimization (search_read, load, bin_size)
  - Compute field optimization (store, precompute, avoiding recursion)
  - SQL optimization (when to use, execute_query, SQL class)
  - Clean code patterns (mapped, filtered, sorted)
when_to_use:
  - Optimizing slow code
  - Preventing N+1 queries
  - Writing batch operations
  - Optimizing computed fields
  - Using direct SQL for aggregations
---

# Odoo 18 Performance Guide

Complete guide for writing performant Odoo 18 code, focusing on N+1 query prevention and clean patterns.

## Table of Contents

1. [Prefetch Mechanism](#prefetch-mechanism)
2. [N+1 Query Prevention](#n1-query-prevention)
3. [Batch Operations](#batch-operations)
4. [Field Selection Optimization](#field-selection-optimization)
5. [Compute Field Optimization](#compute-field-optimization)
6. [SQL Optimization](#sql-optimization)

---

## Prefetch Mechanism

### How Prefetch Works

Odoo automatically prefetches records in batches to minimize queries.

```python
# Constants from Odoo base
PREFETCH_MAX = 1000  # Maximum records prefetched per batch
INSERT_BATCH_SIZE = 100
UPDATE_BATCH_SIZE = 100
```

**How it works**:
1. When you access a field on a recordset, Odoo loads that field for ALL records in the recordset
2. This happens per model, not per relation
3. Related records are also prefetched up to `PREFETCH_MAX`

```python
# GOOD: Automatic prefetch
orders = self.search([('state', '=', 'done')])  # 1 query for orders
for order in orders:
    print(order.name)  # 1 query for all names
    print(order.partner_id.name)  # 1 query for all partners
# Total: 3 queries regardless of number of orders
```

### Understanding Prefetch Groups

```python
# Orders with same partner_id - partner fetched once
orders = self.search([('partner_id', '=', partner_id)])
for order in orders:
    print(order.partner_id.name)  # 1 query for all orders

# Orders with different partners - partners fetched in batch
orders = self.search([])  # Many different partners
for order in orders:
    print(order.partner_id.name)  # Queries in batches of 1000
```

---

## N+1 Query Prevention

### Pattern 1: Search Inside Loop (BAD)

```python
# BAD: N+1 query
for order in orders:
    payments = self.env['payment.transaction'].search([
        ('order_id', '=', order.id)
    ])
    order.payment_count = len(payments)
# Result: 1 + N queries

# GOOD: Use read_group or search with IN domain
order_ids = orders.ids
all_payments = self.env['payment.transaction'].search_read(
    [('order_id', 'in', order_ids)],
    ['order_id']
)
# Count by order
from collections import defaultdict
payment_counts = defaultdict(int)
for payment in all_payments:
    payment_counts[payment['order_id'][0]] += 1

for order in orders:
    order.payment_count = payment_counts.get(order.id, 0)
# Result: 1 query
```

### Pattern 2: One2many Traversal

```python
# GOOD: Use mapped() instead of loop
orders = self.search([('state', '=', 'done')])

# GOOD: Prefetch works automatically
for order in orders:
    for line in order.line_ids:
        print(line.product_id.name)
# Result: ~3 queries (orders, lines, products)

# BETTER: Preload with read() if you only need specific data
lines_data = orders.mapped('line_ids').read(['product_id', 'quantity'])
```

### Pattern 3: Computed Field with Related Access

```python
# BAD: Triggers query for each record
@api.depends('partner_id')
def _compute_partner_email(self):
    for order in self:
        order.partner_email = order.partner_id.email  # N queries

# GOOD: Add partner_id.email to depends
@api.depends('partner_id', 'partner_id.email')
def _compute_partner_email(self):
    for order in self:
        order.partner_email = order.partner_id.email  # 1 query prefetched
```

### Pattern 4: Conditional Computation

```python
# BAD: Check inside loop triggers queries
for order in orders:
    if order.partner_id.customer_rank > 0:
        order.is_customer = True
# Each access to partner_id.customer_rank triggers fetch

# GOOD: Use filtered()
customers = orders.filtered(lambda o: o.partner_id.customer_rank > 0)
customers.is_customer = True
```

---

## Batch Operations

### Batch Create (Odoo 18)

```python
# GOOD: Batch create (Odoo 18 standard)
records = self.create([
    {'name': f'Record {i}', 'state': 'draft'}
    for i in range(100)
])
# Single INSERT batch

# BAD: Create in loop
for i in range(100):
    self.create({'name': f'Record {i}'})
# 100 INSERT statements
```

### Batch Write

```python
# GOOD: Write on recordset
self.search([('state', '=', 'draft')]).write({'state': 'cancel'})
# Single UPDATE batch

# BAD: Write in loop
for order in self.search([('state', '=', 'draft')]):
    order.write({'state': 'cancel'})
# N UPDATE statements
```

### Batch Unlink

```python
# GOOD: Unlink recordset
self.search([('state', '=', 'cancel')]).unlink()
# Single DELETE batch

# BAD: Unlink in loop
for order in self.search([('state', '=', 'cancel')]):
    order.unlink()
# N DELETE statements
```

---

## Field Selection Optimization

### Use search_read for Specific Fields

```python
# GOOD: search_read when you need dicts, not recordsets
data = self.search_read(
    [('state', '=', 'done')],
    ['name', 'amount_total', 'date']
)
# Returns: [{'id': 1, 'name': ..., 'amount_total': ..., 'date': ...}, ...]

# BAD: search() + read() is slower
records = self.search([('state', '=', 'done')])
data = records.read(['name', 'amount_total', 'date'])
```

### Load Parameter for Read

```python
# GOOD: Use load='_classic_read' for simple fields
data = records.read(['name', 'date'], load='_classic_read')

# Use load=None to avoid computing fields
data = records.read(['name', 'state'], load=None)
```

### Bin Size for Binary Fields

```python
# GOOD: Get size instead of content
attachments.with_context(bin_size=True).read(['datas', 'name'])
# Returns: {'datas': 12345, ...} instead of base64 content
```

### Fetch Only What You Need

```python
# GOOD: Select only needed fields
products = self.env['product.product'].search_read(
    [('active', '=', True)],
    ['id', 'name', 'default_code', 'lst_price']
)

# BAD: Fetch all fields
products = self.env['product.product'].search([('active', '=', True)])
```

---

## Compute Field Optimization

### Store Expensive Computations

```python
# GOOD: Store expensive aggregations
amount_total = fields.Float(
    string='Total',
    compute='_compute_amount_total',
    store=True,
    # Store allows search/group by
    compute_sudo=True,  # Compute as admin for performance
)

@api.depends('line_ids.price_subtotal')
def _compute_amount_total(self):
    for order in self:
        order.amount_total = sum(order.line_ids.mapped('price_subtotal'))
```

### Use Precompute for Form Performance

```python
# Use precompute when field can be computed before creation
sequence = fields.Integer(
    string='Sequence',
    compute='_compute_sequence',
    precompute=True,  # Computed at form init
    store=False,
)

@api.depends('date_order')
def _compute_sequence(self):
    for order in self:
        if order.date_order:
            order.sequence = self.env['ir.sequence'].next_by_code(...)
```

**Warning**: `precompute=True` can be counterproductive for:
- Statistics fields (count, sum over search)
- Fields that require database reads
- One-off record creation (not batch)

### Avoid Recursive Dependencies

```python
# BAD: Recursive dependency
field_a = fields.Float(compute='_compute_a', store=True)
field_b = fields.Float(compute='_compute_b', store=True)

@api.depends('field_b')  # A depends on B
def _compute_a(self):
    for rec in self:
        rec.field_a = rec.field_b * 2

@api.depends('field_a')  # B depends on A - INFINITE LOOP
def _compute_b(self):
    for rec in self:
        rec.field_b = rec.field_a / 2

# GOOD: Use a common base field
amount = fields.Float(string='Amount')
tax = fields.Float(compute='_compute_tax', store=True)
total = fields.Float(compute='_compute_total', store=True)

@api.depends('amount')
def _compute_tax(self):
    for rec in self:
        rec.tax = rec.amount * 0.1

@api.depends('amount', 'tax')  # Both depend on amount only
def _compute_total(self):
    for rec in self:
        rec.total = rec.amount + rec.tax
```

---

## SQL Optimization

### When to Use Direct SQL

**Use SQL for**:
- Complex aggregations (count with grouping)
- Bulk data migration
- Reports with joins across many tables
- Performance-critical read operations

```python
def get_statistics(self):
    """Direct SQL for complex aggregation"""
    self.env.cr.execute("""
        SELECT
            state,
            COUNT(*) as count,
            SUM(amount_total) as total
        FROM sale_order
        WHERE create_date >= %s
        GROUP BY state
    """, (fields.date.today(),))
    return dict(self.env.cr.fetchall())
```

**Use SQL class for safety** (Odoo 18):
```python
from odoo.tools import SQL

def get_statistics(self):
    query = SQL("""
        SELECT state, COUNT(*), SUM(amount_total)
        FROM %s
        WHERE create_date >= %s
        GROUP BY state
    """, SQL.identifier('sale_order'), fields.date.today())

    return self.env.execute_query_dict(query)
```

### Never Use SQL for Writes (unless necessary)

```python
# BAD: SQL write bypasses ORM (no compute, no cache, no triggers)
self.env.cr.execute("UPDATE sale_order SET state='done' WHERE id IN %s", (ids,))

# GOOD: Use ORM write
self.browse(ids).write({'state': 'done'})
```

### Use execute_query for Read (Odoo 18)

```python
from odoo.tools import SQL

# GOOD: execute_query handles flush automatically
def get_order_totals(self):
    query = SQL("""
        SELECT id, amount_total
        FROM sale_order
        WHERE state = %s
    """, 'done')

    return self.env.execute_query_dict(query)
```

---

## Clean Code Performance Patterns

### Use Mapped() Instead of List Comprehension

```python
# GOOD: Use mapped() for field access
partner_ids = orders.mapped('partner_id.id')
names = orders.mapped('name')

# GOOD: mapped() works with nested paths
countries = orders.mapped('partner_id.country_id')

# GOOD: mapped() removes duplicates
all_tags = orders.mapped('tag_ids')  # Returns unique tags
```

### Use Filtered() for Conditional Operations

```python
# GOOD: Filter before processing
done_orders = orders.filtered(lambda o: o.state == 'done')
done_orders.action_invoice_create()

# GOOD: Chain filters
high_value = orders.filtered(lambda o: o.amount_total > 1000)
urgent = high_value.filtered(lambda o: o.priority == '2')
```

### Use Sorted() with Key

```python
# GOOD: Sort in memory for small sets
sorted_orders = orders.sorted(key=lambda o: o.amount_total, reverse=True)

# BAD: Don't sort in memory for large sets
# Use database order instead
orders = self.search([], order='amount_total DESC')
```

### Avoid Recomputation in Loops

```python
# BAD: Write in loop triggers recomputation each time
for order in orders:
    order.write({'state': 'done'})  # Triggers compute each iteration

# GOOD: Batch write - single compute at end
orders.write({'state': 'done'})

# GOOD: Use with_context to prevent recomputation
orders.with_context(tracking_disable=True).write({'state': 'done'})
```

---

## Performance Checklist

- [ ] Avoid `search()` inside loops
- [ ] Use `mapped()` instead of list comprehension for field access
- [ ] Use `search_read()` when you need dicts, not recordsets
- [ ] Store expensive computed fields
- [ ] Add all dependencies to `@api.depends`
- [ ] Use `with_context(bin_size=True)` for binary fields
- [ ] Use `with_context(active_test=False)` when including archived
- [ ] Use `read_group()` for aggregations
- [ ] Batch create/write/unlink operations
- [ ] Add indexes on frequently searched fields
- [ ] Use `filtered()` before operations
- [ ] Don't use SQL for writes (use ORM)
- [ ] Use direct SQL for complex read aggregations only

---

## Common Performance Anti-Patterns

### Anti-Pattern 1: Search without limit

```python
# BAD: Could fetch millions of records
all_records = self.search([('state', '=', 'draft')])

# GOOD: Use limit or pagination
records = self.search([('state', '=', 'draft')], limit=100)
```

### Anti-Pattern 2: Computing in loop

```python
# BAD: Compute method does expensive operation
@api.depends('order_id')
def _compute_order_total(self):
    for line in self:
        # Search in loop - N queries
        line.order_total = self.search_count([
            ('order_id', '=', line.order_id.id)
        ])
```

### Anti-Pattern 3: Not using exists()

```python
# BAD: Fetches all records
records = self.search([('state', '=', 'done')])
if len(records) > 0:
    # ...

# GOOD: Only checks existence
exists = self.search_count([('state', '=', 'done')]) > 0
# OR
if self.search([('state', '=', 'done')], limit=1):
    # ...
```

### Anti-Pattern 4: Over-fetching

```python
# BAD: Fetches all fields then only uses one
records = self.search([('state', '=', 'done')])
for record in records:
    print(record.name)  # Only using name

# GOOD: Only fetch needed field
data = self.search_read([('state', '=', 'done')], ['name'])
for row in data:
    print(row['name'])
```

---

## Flush & Recompute (Odoo 18)

### Understanding Flush

Odoo 18 uses lazy writes - changes are cached and flushed to database later.

```python
# Flush specific fields to database
self.flush_model(['amount_total', 'state'])

# Flush current recordset only
self.flush_recordset(['amount'])

# Flush before direct SQL query
self.flush_model()  # Flush all pending changes
self.env.cr.execute("SELECT ...")
```

### flush_model() vs flush_recordset()

```python
# flush_model - flush for entire model (all records)
self.env['sale.order'].flush_model(['amount_total'])

# flush_recordset - flush only current records
orders.flush_recordset(['amount_total'])
```

### Recompute Control

```python
# Manual recompute of stored computed fields
self._recompute_model(['amount_total'])      # Entire model
self._recompute_recordset(['amount_total'])  # Current records
self._recompute_field(self._fields['amount_total'])  # Specific field

# Recompute with specific ids
self._recompute_field(field, ids=[1, 2, 3])
```

### Batch Recompute Optimization

```python
# GOOD: Let Odoo handle recomputation automatically
orders.write({'state': 'done'})
# amount_total will be recomputed in batch automatically

# AVOID: Manual recomputation in loop
for order in orders:
    order.write({'state': 'done'})
    order.amount_total  # Triggers individual recomputation
```

### Flush Before SQL Query (Odoo 18)

```python
from odoo.tools import SQL

# Mark fields to flush before SQL query
query = SQL("""
    SELECT id, amount
    FROM sale_order
    WHERE state = %s
""", 'done')

# Option 1: Mark fields to flush (auto-flushes those fields)
query.to_flush = [self._fields['state']]

# Option 2: Use execute_query_dict (auto-flushes)
results = self.env.execute_query_dict(query)
```

### with_context for Performance

```python
# Disable tracking for bulk operations (faster)
records.with_context(tracking_disable=True).write({'state': 'done'})

# Use bin_size for binary fields
attachments.with_context(bin_size=True).read(['datas', 'name'])

# Disable active_test to include archived
all_records = self.with_context(active_test=False).search([])
```

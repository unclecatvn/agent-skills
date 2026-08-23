---
name: odoo-17-performance
description: Complete guide for writing performant Odoo 17 code, focusing on N+1 query prevention, batch operations, and optimization patterns.
globs: "**/*.{py,xml}"
topics:
  - Prefetch mechanism (how it works, understanding groups)
  - N+1 query prevention patterns
  - Batch operations (create, write, unlink)
  - Field selection optimization (search_read, load, bin_size)
  - Aggregation optimization (read_group public API, _read_group core)
  - Compute field optimization (store, precompute, avoiding recursion)
  - SQL optimization (cr.execute, SQL class helper)
  - Clean code patterns (mapped, filtered, sorted)
when_to_use:
  - Optimizing slow code
  - Preventing N+1 queries
  - Writing batch operations
  - Optimizing computed fields
  - Using read_group() for aggregations
  - Using direct SQL for aggregations
---

# Odoo 17 Performance Guide

Complete guide for writing performant Odoo 17 code, focusing on N+1 query prevention and clean patterns.

## Table of Contents

1. [Prefetch Mechanism](#prefetch-mechanism)
2. [N+1 Query Prevention](#n1-query-prevention)
3. [Batch Operations](#batch-operations)
4. [Field Selection Optimization](#field-selection-optimization)
5. [Compute Field Optimization](#compute-field-optimization)
6. [SQL Optimization](#sql-optimization)
7. [Flush & Cache Control](#flush--cache-control)
8. [Clean Code Patterns](#clean-code-performance-patterns)
9. [Profiling & Query Count](#profiling--query-count)

---

## Prefetch Mechanism

### How Prefetch Works

Odoo automatically prefetches records in batches to minimize queries.

```python
# Constants from odoo/models.py
PREFETCH_MAX = 1000          # Maximum records prefetched per batch
INSERT_BATCH_SIZE = 100      # Batch size for INSERT
```

**How it works**:
1. When you access a field on a recordset, Odoo loads that field for ALL records sharing the same `_prefetch_ids`
2. Prefetch is per-model, not per-relation
3. Related records are prefetched up to `PREFETCH_MAX`

```python
# GOOD: Automatic prefetch
orders = self.search([('state', '=', 'done')])  # 1 query for orders
for order in orders:
    print(order.name)              # 1 query for all names (prefetched)
    print(order.partner_id.name)   # 1 query for all partners (prefetched)
# Total: ~3 queries regardless of recordset size
```

### Prefetch Groups

Every recordset tracks `_prefetch_ids`. When you access a field, Odoo fetches it for every id in `_prefetch_ids` that is not yet cached.

```python
# All orders share the same prefetch group -> single SQL for related fields
orders = self.search([])
for order in orders:
    # One query for partner_id batch, not one per order
    print(order.partner_id.name)
```

### Controlling Prefetch Explicitly

```python
# Break a recordset out of its prefetch group (e.g. "expensive" records)
big_attachments = attachments.with_prefetch()   # Empty prefetch -> each access only hits self

# Force a shared prefetch group between two unrelated recordsets
a = self.browse(ids_a).with_prefetch(all_ids)
b = self.browse(ids_b).with_prefetch(all_ids)

# Disable auto-prefetch of companion fields when fetching one field
records.with_context(prefetch_fields=False).read(['name'])
```

`with_prefetch()` and `_prefetch_ids` live on `BaseModel` in `odoo/models.py`.

---

## N+1 Query Prevention

### Pattern 1: Search Inside Loop (BAD)

```python
# BAD: N+1 queries
for order in orders:
    payments = self.env['payment.transaction'].search([
        ('order_id', '=', order.id)
    ])
    order.payment_count = len(payments)
# Result: 1 + N queries

# GOOD: single IN query + read_group for counting
groups = self.env['payment.transaction'].read_group(
    [('order_id', 'in', orders.ids)],
    fields=['order_id'],
    groupby=['order_id'],
)
counts = {g['order_id'][0]: g['order_id_count'] for g in groups}
for order in orders:
    order.payment_count = counts.get(order.id, 0)
# Result: 1 query
```

### Pattern 2: One2many Traversal

```python
# GOOD: mapped() + automatic prefetch
orders = self.search([('state', '=', 'done')])
for order in orders:
    for line in order.line_ids:
        print(line.product_id.name)
# ~3 queries (orders, lines, products)

# BETTER when you only need a few scalar fields
lines_data = orders.mapped('line_ids').read(['product_id', 'quantity'])
```

### Pattern 3: Computed Field with Related Access

```python
# BAD: missing dependency -> query per record
@api.depends('partner_id')
def _compute_partner_email(self):
    for order in self:
        order.partner_email = order.partner_id.email  # N queries

# GOOD: add dotted dependency -> single batched fetch
@api.depends('partner_id', 'partner_id.email')
def _compute_partner_email(self):
    for order in self:
        order.partner_email = order.partner_id.email
```

### Pattern 4: Conditional Computation

```python
# BAD: field access on single record forces fetch
for order in orders:
    if order.partner_id.customer_rank > 0:
        order.is_customer = True

# GOOD: filtered() uses cached prefetch data
customers = orders.filtered(lambda o: o.partner_id.customer_rank > 0)
customers.is_customer = True
```

### Pattern 5: `exists()` vs `search()` for Existence

```python
# BAD: fetches up to millions of rows
if self.search([('state', '=', 'done')]):
    ...

# GOOD: limit=1
if self.search([('state', '=', 'done')], limit=1):
    ...

# GOOD: search_count when you need the number
count = self.search_count([('state', '=', 'done')])
```

---

## Batch Operations

### Batch Create (Odoo 17)

Odoo 17 supports batch `create()` via a list of dicts (processed in chunks of `INSERT_BATCH_SIZE = 100`).

```python
# GOOD: batch create
records = self.create([
    {'name': f'Record {i}', 'state': 'draft'}
    for i in range(100)
])
# Internal INSERTs chunked by INSERT_BATCH_SIZE

# BAD: create in loop
for i in range(100):
    self.create({'name': f'Record {i}'})
# 100 INSERT statements and 100 compute rounds
```

### Batch Write

```python
# GOOD: recordset write -> single UPDATE
self.search([('state', '=', 'draft')]).write({'state': 'cancel'})

# BAD: loop write
for order in self.search([('state', '=', 'draft')]):
    order.write({'state': 'cancel'})
```

### Batch Unlink

```python
# GOOD: recordset unlink -> single DELETE
self.search([('state', '=', 'cancel')]).unlink()

# BAD: loop unlink
for order in self.search([('state', '=', 'cancel')]):
    order.unlink()
```

### Chunked Processing for Large Datasets

```python
from odoo.tools import split_every

def process_all(self):
    ids = self.search([('to_process', '=', True)]).ids
    for chunk_ids in split_every(500, ids):
        records = self.browse(chunk_ids)
        records._do_process()
        # Keep the ambient transaction under Odoo's control. Use a separately
        # owned cursor only for an independently recoverable batch boundary.
```

---

## Field Selection Optimization

### `search_read` when you need dicts, not recordsets

```python
# GOOD
data = self.search_read(
    [('state', '=', 'done')],
    ['name', 'amount_total', 'date'],
)
# [{'id': 1, 'name': ..., 'amount_total': ..., 'date': ...}, ...]

# SLOWER
records = self.search([('state', '=', 'done')])
data = records.read(['name', 'amount_total', 'date'])
```

### `read_group()` for Aggregations (Odoo 17 public API)

In **Odoo 17**, the public, stable API for aggregation is `read_group()`. It returns a list of dicts including `__domain` / `__context` metadata and supports lazy grouping. `_read_group()` exists and is the core implementation that returns tuples, but in v17 **prefer `read_group()` for business code** - its signature is the stable one.

```python
# GOOD: read_group() - Odoo 17 public API
results = self.read_group(
    domain=[('state', '=', 'done')],
    fields=['amount_total:sum'],
    groupby=['partner_id'],
    lazy=True,
)
# [{
#     'partner_id': (42, 'ACME'),
#     'partner_id_count': 5,
#     'amount_total': 1234.0,
#     '__domain': [...],
#     '__context': {...},
# }, ...]

for row in results:
    partner_id, partner_name = row['partner_id'] or (False, '')
    print(f"{partner_name}: {row['amount_total']} ({row['partner_id_count']} orders)")
```

Multiple groupbys with `lazy=False`:

```python
results = self.read_group(
    domain=[('state', '=', 'done')],
    fields=['amount_total:sum'],
    groupby=['partner_id', 'state'],
    lazy=False,
)
# One dict per (partner_id, state) combination
```

### `_read_group()` (core method, tuple output)

`_read_group()` in Odoo 17 returns tuples and is convenient for internal data processing, but it is not part of the stable public API. Use it when you want to unpack cleanly:

```python
for partner, amount_total in self._read_group(
    domain=[('state', '=', 'done')],
    groupby=['partner_id'],
    aggregates=['amount_total:sum'],
):
    # partner: res.partner recordset, amount_total: float
    ...
```

| Feature | `read_group()` (public) | `_read_group()` (core) |
|---------|-------------------------|------------------------|
| Return type | List of dicts | List of tuples |
| Metadata | `__domain`, `__context`, `__range` | None |
| Lazy grouping | Yes (`lazy=True`) | No |
| Empty group fill | Yes | No |
| API style | `domain, fields, groupby` | `domain, groupby, aggregates` |
| Stability | Stable public API in v17 | Internal helper |

### Load Parameter for `read`

```python
# Skip computed/non-stored fields
records.read(['name', 'state'], load=None)

# Classic read (default): includes name_get for many2one etc.
records.read(['name', 'partner_id'], load='_classic_read')
```

### `bin_size` for Binary Fields

```python
# GOOD: returns file size instead of base64 content
attachments.with_context(bin_size=True).read(['datas', 'name'])
```

### Disable `active_test`

```python
# Include archived records
all_records = self.with_context(active_test=False).search([])
```

---

## Compute Field Optimization

### Store Expensive Computations

```python
class SaleOrder(models.Model):
    _inherit = 'sale.order'

    amount_total = fields.Monetary(
        string='Total',
        compute='_compute_amount_total',
        store=True,           # Store so we can search / group / sort on it
        compute_sudo=True,    # Compute as superuser for performance
    )

    @api.depends('line_ids.price_subtotal')
    def _compute_amount_total(self):
        for order in self:
            order.amount_total = sum(order.line_ids.mapped('price_subtotal'))
```

### Precompute (Odoo 17)

```python
# precompute=True: evaluated at create-time before INSERT,
# stored together with other fields -> 1 INSERT instead of INSERT + UPDATE.
sequence = fields.Integer(
    compute='_compute_sequence',
    precompute=True,
    store=True,
)
```

**Warning**: do NOT `precompute=True` when the compute needs DB reads of records that may not exist yet (e.g. aggregations over children).

### Avoid Recursive Dependencies

```python
# BAD: A depends on B, B depends on A -> infinite recompute
@api.depends('field_b')
def _compute_a(self): ...

@api.depends('field_a')
def _compute_b(self): ...

# GOOD: both depend on a common base field
@api.depends('amount')
def _compute_tax(self):
    for rec in self:
        rec.tax = rec.amount * 0.1

@api.depends('amount', 'tax')
def _compute_total(self):
    for rec in self:
        rec.total = rec.amount + rec.tax
```

### Add Database Indexes on Searched Fields

```python
reference = fields.Char(index=True)       # B-tree index
external_id = fields.Char(index='btree_not_null')  # Odoo 17: partial index
```

---

## SQL Optimization

### When to Use Direct SQL

Use SQL for:
- Complex aggregations with joins across many tables
- Bulk data migration scripts
- Heavy reports
- Read-only analytics that would otherwise cost thousands of ORM queries

Avoid SQL for writes - you lose compute/invalidation/tracking.

### Primary pattern: `cr.execute()`

The canonical v17 pattern is plain parameterized `cr.execute`:

```python
def get_statistics(self):
    self.env.cr.execute("""
        SELECT state,
               COUNT(*)          AS count,
               SUM(amount_total) AS total
          FROM sale_order
         WHERE create_date >= %s
      GROUP BY state
    """, (fields.Date.today(),))
    return self.env.cr.dictfetchall()
```

**Always** use `%s` placeholders and pass a tuple of parameters. Never f-string user input into SQL.

### Optional: `SQL` wrapper (Odoo 17)

Odoo 17 ships a composable `SQL` helper in `odoo/tools/sql.py`. It is safer than string concatenation when you need to build queries dynamically (identifiers, variable GROUP BY, etc.). Unlike Odoo 18, v17 does **not** have `env.execute_query()` / `env.execute_query_dict()` - you still call `cr.execute(sql)` yourself.

```python
from odoo.tools import SQL

def totals_for(self, table):
    query = SQL(
        "SELECT state, SUM(amount_total) FROM %s WHERE state = %s GROUP BY state",
        SQL.identifier(table),   # safely quotes identifier
        'done',
    )
    self.env.cr.execute(query)
    return dict(self.env.cr.fetchall())
```

### Never SQL-Write Without a Reason

```python
# BAD: bypasses cache, compute, tracking, access rules
self.env.cr.execute("UPDATE sale_order SET state='done' WHERE id IN %s", (tuple(ids),))

# GOOD
self.browse(ids).write({'state': 'done'})
```

### Flush Before Reading via SQL

When you bypass the ORM with `cr.execute`, pending in-memory writes on the involved fields may not yet be in the database. Flush them manually:

```python
self.env['sale.order'].flush_model(['state', 'amount_total'])
self.env.cr.execute("SELECT state, SUM(amount_total) FROM sale_order GROUP BY state")
```

`flush_model(fnames=None)` is defined on `BaseModel` in `odoo/models.py` (v17). Without arguments, it flushes every pending field for the model.

---

## Flush & Cache Control

Odoo 17 uses deferred writes: ORM updates accumulate in the cache and are flushed to the database lazily.

### `env.flush_all()` / `env.invalidate_all()`

```python
# Flush every pending computation and write for the current environment
self.env.flush_all()

# Drop the in-memory cache (flushes first by default)
self.env.invalidate_all()
self.env.invalidate_all(flush=False)  # discard cache without flushing (rare)
```

Defined in `odoo/api.py` on `Environment`.

### Per-Model / Per-Recordset Flush

```python
# Flush all pending updates for a model
self.env['sale.order'].flush_model()

# Flush only a few fields
self.env['sale.order'].flush_model(['state', 'amount_total'])
```

### When to Flush Manually

- Before running `cr.execute` on columns you just wrote to
- Before calling a stored procedure / trigger-dependent SQL
- When calling a method that must see previous computed values that were stored

```python
orders.write({'state': 'done'})
# Before a SQL report that reads sale_order.state, flush:
self.env['sale.order'].flush_model(['state'])
self.env.cr.execute("SELECT state, SUM(amount_total) FROM sale_order GROUP BY state")
```

### `sudo()` is Not Free

`sudo()` returns a new env with `su=True`. Each call creates a new recordset with a fresh prefetch group. Calling it inside a loop kills prefetch:

```python
# BAD: new sudo env each iteration breaks prefetch
for order in orders:
    order.sudo().partner_id.name   # each partner fetched alone

# GOOD: sudo once on the recordset
for order in orders.sudo():
    order.partner_id.name          # batched
```

### `with_context` Tricks

```python
# Skip mail.thread tracking on bulk updates (huge speedup for chatter-enabled models)
records.with_context(tracking_disable=True).write({'state': 'done'})

# Include archived
all_records = self.with_context(active_test=False).search([])

# Binary field size only (no base64 payload)
atts.with_context(bin_size=True).read(['datas'])

# Skip prefetching sibling fields when reading a single one
rec.with_context(prefetch_fields=False).read(['name'])
```

---

## Clean Code Performance Patterns

### `mapped()` over list comprehensions

```python
# GOOD: field access via mapped()
partner_ids = orders.mapped('partner_id.id')
countries = orders.mapped('partner_id.country_id')   # dotted paths OK

# GOOD: mapped() of a many2many returns deduplicated recordset
all_tags = orders.mapped('tag_ids')
```

### `filtered()` before operations

```python
done = orders.filtered(lambda o: o.state == 'done')
done.action_invoice_create()
```

For performance on large sets, use `filtered_domain` to reuse domain evaluation:

```python
done = orders.filtered_domain([('state', '=', 'done')])
```

### `sorted()` with key - or let the DB do it

```python
# Small sets: in-memory sort
top = orders.sorted(key='amount_total', reverse=True)[:5]

# Large sets: let PostgreSQL sort with an index
top = self.search([], order='amount_total DESC', limit=5)
```

### Avoid Recomputation in Loops

```python
# BAD: each write triggers a recompute pass
for order in orders:
    order.write({'state': 'done'})

# GOOD: single batch write, single recompute pass
orders.write({'state': 'done'})
```

---

## Profiling & Query Count

### Counting queries in tests

`BaseCase` records the query count on `self.cr.sql_log` when enabled, but the standard pattern is `assertQueryCount`:

```python
from odoo.tests.common import TransactionCase

class TestPerf(TransactionCase):

    def test_loop_is_constant_in_queries(self):
        orders = self.env['sale.order'].search([], limit=20)

        with self.assertQueryCount(3):  # no N, regardless of len(orders)
            for o in orders:
                o.partner_id.name
```

`assertQueryCount` is defined in `odoo/tests/common.py` and is the Odoo 17 standard assertion for regression-proofing N+1 bugs.

### Profiling with `odoo.tools.profiler`

```python
from odoo.tools.profiler import profile

@profile  # writes a profile log on each call
def heavy_method(self):
    ...
```

For interactive profiling, start Odoo with `--dev=all` and use the Developer Tools > Profile menu, which leverages `odoo/tools/profiler.py`.

### SQL log via config

Run Odoo with `--log-sql` (or `log_sql = True` in odoo.conf) to see every SQL statement. Combined with `--log-handler=odoo.sql_db:DEBUG` you get timings, useful for finding N+1 patterns in local dev.

---

## Performance Checklist

- [ ] No `search()` inside loops
- [ ] Use `mapped()` / `filtered()` instead of Python loops for field access/filter
- [ ] Use `search_read()` when you only need dicts
- [ ] Use `read_group()` for aggregations (v17 public API)
- [ ] Store expensive computed fields with `store=True`
- [ ] Add all dependencies (including dotted) to `@api.depends`
- [ ] Use `with_context(bin_size=True)` for binary fields
- [ ] Use `with_context(tracking_disable=True)` for bulk writes on mail.thread models
- [ ] Batch `create` / `write` / `unlink` on recordsets
- [ ] Add `index=True` on frequently filtered fields
- [ ] Call `sudo()` once at the top, not inside loops
- [ ] Flush before `cr.execute()` on pending fields
- [ ] Use `SQL` class wrapper for dynamic identifiers
- [ ] Don't SQL-write - let the ORM do it
- [ ] Add `assertQueryCount` in tests to lock performance

---

## Common Performance Anti-Patterns

### Anti-Pattern 1: Unbounded `search()`

```python
# BAD
records = self.search([('state', '=', 'draft')])  # could be millions

# GOOD
records = self.search([('state', '=', 'draft')], limit=100)
```

### Anti-Pattern 2: Compute with search in loop

```python
# BAD: search per record
@api.depends('order_id')
def _compute_order_total(self):
    for line in self:
        line.order_total = self.search_count([('order_id', '=', line.order_id.id)])
```

### Anti-Pattern 3: Re-reading after write

```python
# BAD: useless cache invalidation
orders.write({'state': 'done'})
self.env.invalidate_all()
for order in orders:
    print(order.state)  # now re-fetches from DB

# GOOD: trust the cache
orders.write({'state': 'done'})
for order in orders:
    print(order.state)  # already up-to-date
```

### Anti-Pattern 4: `sudo()` inside a loop

```python
# BAD: breaks prefetch
for order in orders:
    order.sudo().partner_id.name

# GOOD: sudo once
for order in orders.sudo():
    order.partner_id.name
```

### Anti-Pattern 5: Over-fetching

```python
# BAD
records = self.search([('state', '=', 'done')])
for r in records:
    print(r.name)   # only name used, but all fields prefetched

# GOOD
for row in self.search_read([('state', '=', 'done')], ['name']):
    print(row['name'])
```

---

## Coding Conventions

- Prefer batch-aware ORM operations and `filtered`, `mapped`, and `sorted`
  when they make intent clearer and avoid per-record queries.
- Do not add custom generators or decorators solely for iteration.
- Odoo owns normal request and cron transactions; performance is not a reason
  to commit the ambient cursor.

## Base Code Reference

- `odoo/models.py` - `BaseModel`, `PREFETCH_MAX`, `INSERT_BATCH_SIZE`, `_read_group`, `read_group`, `search_read`, `flush_model`
- `odoo/fields.py` - field prefetch groups, `_prefetch_ids`, `with_prefetch`
- `odoo/api.py` - `Environment.flush_all`, `Environment.invalidate_all`
- `odoo/tools/sql.py` - `SQL` class for composable parameterized queries
- `odoo/tools/profiler.py` - `@profile` decorator
- `odoo/tests/common.py` - `assertQueryCount`
- `odoo/osv/expression.py` - domain-to-SQL translator

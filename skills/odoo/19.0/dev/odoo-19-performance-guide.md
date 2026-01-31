# Odoo 19 Performance Guide

Guide for optimizing Odoo 19 code: preventing N+1 queries, reducing database queries, and using profiler.

## Table of Contents
- [Profiling](#profiling)
- [Batch Operations](#batch-operations)
- [Algorithmic Complexity](#algorithmic-complexity)
- [Indexes](#indexes)
- [Performance Pitfalls](#performance-pitfalls)

---

## Profiling

Odoo provides an integrated profiling tool to record SQL queries and stack traces.

### Enable from User Interface

1. Enable developer mode
2. Toggle **Enable profiling** button
3. Choose expiry time
4. Toggle **Enable profiling** again to start session profiling

Options:
- **Record sql** - Saves all SQL queries with stack trace
- **Record traces** - Saves stack trace periodically (default: 10ms interval)

### Enable from Python Code

```python
from odoo.tools.profiler import Profiler

# Basic profiling
with Profiler():
    do_stuff()

# With custom collectors
with Profiler(collectors=['sql', PeriodicCollector(interval=0.1)]):
    do_stuff()

# In tests
with self.profile():
    do_stuff()
```

### Collectors

| Collector | Key | Description |
|-----------|-----|-------------|
| SQL collector | `sql` | Saves SQL queries with stack trace |
| Periodic collector | `traces_async` | Saves stack trace periodically (separate thread) |
| QWeb collector | `qweb` | Saves QWeb directive execution |
| Sync collector | `traces_sync` | Saves every function call/return (high overhead) |

### Execution Context

Add context to identify calls in speedscope:

```python
for index in range(max_index):
    with ExecutionContext(current_index=index):
        do_stuff()
```

### Performance Pitfalls

- Randomness can lead to different results (garbage collector, etc.)
- Blocking calls may cause unexpected long frames
- Cache state affects results (view/assets in cache)
- Profiler overhead can impact performance (especially SQL collector)
- Large profiles may cause memory issues

---

## Batch Operations

### Avoid Loop Queries

**BAD**: Search in loop (N queries)

```python
def _compute_count(self):
    for record in self:
        domain = [('related_id', '=', record.id)]
        record.count = other_model.search_count(domain)
```

**GOOD**: Use `_read_group` (1 query)

```python
def _compute_count(self):
    domain = [('related_id', 'in', self.ids)]
    counts_data = other_model._read_group(domain, ['related_id'], ['__count'])
    mapped_data = {r['related_id'][0]: r['__count'] for r in counts_data}
    for record in self:
        record.count = mapped_data.get(record.id, 0)
```

### Batch Creates

**BAD**: Create in loop

```python
for name in ['foo', 'bar']:
    model.create({'name': name})
```

**GOOD**: Batch create

```python
create_values = [{'name': name} for name in ['foo', 'bar']]
records = model.create(create_values)
```

### Prefetch Records

**BAD**: Browse one at a time

```python
for record_id in record_ids:
    record = model.browse(record_id)
    record.foo  # One query per record
```

**GOOD**: Browse all together

```python
records = model.browse(record_ids)
for record in records:
    record.foo  # One query for entire recordset
```

### Disable Prefetching (when needed)

```python
for values in values_list:
    message = self.browse(values['id']).with_prefetch(self.ids)
```

---

## Algorithmic Complexity

### Reduce Nested Loops

**BAD**: O(n²) complexity

```python
for record in self:
    for result in results:
        if result['id'] == record.id:
            record.foo = result['foo']
            break
```

**GOOD**: Use dictionary (O(n))

```python
mapped_result = {result['id']: result['foo'] for result in results}
for record in self:
    record.foo = mapped_result.get(record.id)
```

### Use Set Operations

**BAD**: List-like `in` check (quadratic)

```python
invalid_ids = self.search(domain).ids
for record in self:
    if record.id in invalid_ids:  # O(n) for each record
        ...
```

**GOOD**: Use set (O(n) total)

```python
invalid_ids = set(self.search(domain).ids)
for record in self:
    if record.id in invalid_ids:
        ...
```

**ALTERNATIVE**: Recordset operations

```python
invalid_ids = self.search(domain)
for record in self - invalid_ids:
    ...
```

---

## Indexes

Database indexes speed up search operations.

```python
name = fields.Char(string="Name", index=True)
```

**Warning**: Don't index every field - indexes consume space and impact INSERT/UPDATE/DELETE performance.

### Using Indexes

```python
# Without index: full table scan
records = self.search([('name', '=', 'value')])

# With index: index scan
name = fields.Char(index=True)
records = self.search([('name', '=', 'value')])
```

---

## Performance Pitfalls

### N+1 Query Problem

Occurs when you:
1. Fetch a list of records
2. Loop through them
3. Execute a query for each record

**Detection**: Use `--log-sql` CLI parameter or profiler

**Solution**: Fetch related data in one query using:
- `_read_group()`
- `search_fetch()`
- `fetch()`
- `mapped()`

### Large Recordsets

Processing large recordsets can cause memory issues.

**Solution**: Process in batches

```python
def _process_large_dataset(self):
    limit = 1000
    offset = 0
    while True:
        records = self.search([], limit=limit, offset=offset)
        if not records:
            break
        records.process()
        offset += limit
```

### Computed Field Dependencies

Missing dependencies cause recomputation at wrong time.

**BAD**: Missing dotted dependency

```python
@api.depends('partner_id')
def _compute_email(self):
    for record in self:
        record.email = record.partner_id.email  # N queries!
```

**GOOD**: Include dotted path

```python
@api.depends('partner_id.email')
def _compute_email(self):
    for record in self:
        record.email = record.partner_id.email  # 1 query for all
```

### Context Pollution

Excessive context changes can cause issues.

```python
# BAD: Too many with_context calls
records.with_context(lang='fr').with_context(active_test=False).with_context(...)
```

**Solution**: Consolidate context changes

```python
# GOOD: Single with_context call
records.with_context(lang='fr', active_test=False)
```

### Unnecessary invalidate_cache

Calling `invalidate_cache()` too frequently defeats the purpose of caching.

**Solution**: Only invalidate fields that actually changed

```python
# GOOD: Invalidate only changed fields
records.invalidate_recordset(['field1', 'field2'])
```

---

## Query Count Testing

Use `assertQueryCount` in tests to establish query limits.

```python
with self.assertQueryCount(11):
    do_something()
```

Combine with profiler for analysis:

```python
with self.profile():
    with self.assertQueryCount(__system__=1211):
        do_stuff()
```

---

## Good Practices Summary

| Practice | Description |
|----------|-------------|
| **Batch operations** | Accumulate operations, execute in batch |
| **Use _read_group** | Replace search/search_count in loops |
| **Prefetch records** | Browse all records together |
| **Reduce complexity** | Use dictionaries/sets instead of nested loops |
| **Add indexes** | On frequently searched fields |
| **Use fetch/search_fetch** | For targeted data loading |
| **Profile first** | Use profiler before optimizing |
| **Test query counts** | Use assertQueryCount in tests |

---

## References

- Source: Odoo 19 documentation `/doc/developer/reference/backend/performance.rst`

---
name: odoo-18-transaction
description: Complete guide for handling database transactions, UniqueViolation errors, savepoints, and commit operations in Odoo 18.
globs: "**/*.{py,xml}"
topics:
  - Transaction states and error handling
  - UniqueViolation (duplicate key) errors
  - Savepoint usage patterns
  - commit() and rollback() best practices
  - InFailedSqlTransaction errors
  - Serialization errors
when_to_use:
  - Handling duplicate key errors
  - Working with savepoints for error isolation
  - Understanding transaction abort states
  - Preventing serialization conflicts
---

# Odoo 18 Transaction Guide

Complete guide for handling database transactions, UniqueViolation errors, savepoints, and commit operations in Odoo 18.

## Table of Contents

1. [Transaction States](#transaction-states)
2. [UniqueViolation Errors](#uniqueviolation-errors)
3. [Savepoint Usage](#savepoint-usage)
4. [commit() and rollback()](#commit-and-rollback)
5. [Transaction Aborted Errors](#transaction-aborted-errors)
6. [Serialization Errors](#serialization-errors)

---

## Transaction States

### PostgreSQL Transaction Isolation

Odoo uses `REPEATABLE READ` isolation level by default (defined in `odoo/sql_db.py:303`):

```python
# From odoo/sql_db.py
class Cursor(BaseCursor):
    def __init__(self, pool, dbname, dsn):
        # ...
        self.connection.set_isolation_level(ISOLATION_LEVEL_REPEATABLE_READ)
        self.connection.set_session(readonly=pool.readonly)
```

**What this means**:
- Transactions operate on snapshots taken at the first query
- Concurrent updates are detected and may cause serialization errors
- Changes from other transactions are not visible during your transaction

### Transaction State Flow

```
Normal → [Error] → Aborted → [rollback] → Normal
                    ↓
                 [commit] → ERROR! (cannot commit aborted transaction)
```

**Key Point**: Once a transaction enters the "aborted" state due to an error, **all subsequent commands will fail** until you execute `ROLLBACK`.

---

## UniqueViolation Errors

### What is UniqueViolation?

PostgreSQL error code `23505` (UniqueViolation) occurs when inserting or updating data violates a unique constraint.

```python
# Example: Trying to create a duplicate record
existing = self.create({'email': 'test@example.com'})

# This will raise UniqueViolation (psycopg2.errors.UniqueViolation)
duplicate = self.create({'email': 'test@example.com'})
```

### Odoo's Error Handling

Odoo maps PostgreSQL errors to user-friendly messages via `PGERROR_TO_OE` (defined in `odoo/models.py:7618`):

```python
PGERROR_TO_OE = defaultdict(
    lambda: (lambda model, fvg, info, pgerror: {'message': tools.exception_to_unicode(pgerror)}),
    {
        '23502': convert_pgerror_not_null,   # NOT NULL violation
        '23505': convert_pgerror_unique,     # UNIQUE violation
        '23514': convert_pgerror_constraint, # CHECK constraint violation
    },
)
```

### UniqueViolation Error Handler

From `odoo/models.py:7564`, Odoo handles unique violations by:

```python
def convert_pgerror_unique(model, fields, info, e):
    # Uses a NEW cursor because we're in a blown transaction
    with closing(model.env.registry.cursor()) as cr_tmp:
        cr_tmp.execute(SQL("""
            SELECT conname, t.relname, ARRAY(
                SELECT attname FROM pg_attribute
                WHERE attrelid = conrelid AND attnum = ANY(conkey)
            ) as "columns"
            FROM pg_constraint
            JOIN pg_class t ON t.oid = conrelid
            WHERE conname = %s
        """, e.diag.constraint_name))
        constraint, table, ufields = cr_tmp.fetchone() or (None, None, None)
```

**Why a new cursor?** The current transaction is in "aborted" state after the error. A new cursor creates a fresh transaction for the error handler.

### Handling UniqueViolation Correctly

```python
# BAD: Direct exception handling without transaction cleanup
try:
    record = self.create({'email': email})
except psycopg2.errors.UniqueViolation:
    # Transaction is now ABORTED - cannot execute queries!
    existing = self.search([('email', '=', email)])  # ERROR!

# GOOD: Use savepoint to isolate the error
with self.env.cr.savepoint():
    try:
        record = self.create({'email': email})
    except psycopg2.errors.UniqueViolation:
        # Savepoint rolled back, transaction still valid
        pass  # Now we can continue

# GOOD: Check for existence first
existing = self.search([('email', '=', email)], limit=1)
if not existing:
    record = self.create({'email': email})
```

---

## Savepoint Usage

### What is a Savepoint?

A savepoint creates a nested transaction that can be rolled back without affecting the outer transaction.

```python
# From odoo/sql_db.py:79
class Savepoint:
    """ Reifies an active breakpoint, allows users to internally rollback
    the savepoint without having to implement their own savepointing.
    """
    def __init__(self, cr):
        self.name = str(uuid.uuid1())
        self._cr = cr
        cr.execute('SAVEPOINT "%s"' % self.name)

    def rollback(self):
        self._cr.execute('ROLLBACK TO SAVEPOINT "%s"' % self.name)

    def _close(self, rollback):
        if rollback:
            self.rollback()
        self._cr.execute('RELEASE SAVEPOINT "%s"' % self.name)
```

### Basic Savepoint Pattern

```python
# Savepoint context manager
with self.env.cr.savepoint():
    # Any error here rolls back to the savepoint
    record = self.create({'name': 'test'})
    raise ValueError("This will be rolled back")
# Transaction continues normally after the savepoint
```

### Flushing Savepoint vs Non-Flushing

Odoo provides two types of savepoints:

```python
# From odoo/sql_db.py:182
def savepoint(self, flush=True) -> Savepoint:
    if flush:
        return _FlushingSavepoint(self)  # Auto-flushes ORM cache
    else:
        return Savepoint(self)          # No flush
```

**`flush=True` (default)**: Flushes ORM changes before entering savepoint
```python
with self.env.cr.savepoint():  # Equivalent to flush=True
    # All pending ORM changes are written to DB first
    # Useful when your operation needs to see latest data
```

**`flush=False`**: Does NOT flush - changes remain in cache
```python
with self.env.cr.savepoint(flush=False):
    # Changes remain in memory, not written yet
    # Useful for schema operations in odoo/tools/sql.py
```

### _FlushingSavepoint Behavior

```python
# From odoo/sql_db.py:123
class _FlushingSavepoint(Savepoint):
    def __init__(self, cr):
        cr.flush()  # Flush ORM cache before creating savepoint
        super().__init__(cr)

    def rollback(self):
        self._cr.clear()  # Clear ORM cache on rollback
        super().rollback()

    def _close(self, rollback):
        try:
            if not rollback:
                self._cr.flush()  # Final flush on success
        except Exception:
            rollback = True
            raise
        finally:
            super()._close(rollback)
```

### Batch Operation Pattern with Savepoints

```python
# GOOD: Each record isolated with savepoint
for data in data_list:
    with self.env.cr.savepoint():
        record = self.create(data)
        record._process()

# If one fails, others continue
```

### Common Savepoint Anti-Patterns

```python
# BAD: Re-using savepoint name
name = 'my_savepoint'
self.env.cr.execute(f'SAVEPOINT "{name}"')
# ... do work ...
self.env.cr.execute(f'RELEASE SAVEPOINT "{name}"')
self.env.cr.execute(f'SAVEPOINT "{name}"')  # ERROR: savepoint already exists

# GOOD: Use context manager (auto-generates unique name)
with self.env.cr.savepoint():
    # ... do work ...

# BAD: Nested savepoint after error
try:
    with self.env.cr.savepoint():
        raise UniqueViolation("boom")
except UniqueViolation:
    pass  # Transaction might be in bad state
with self.env.cr.savepoint():  # May fail if outer transaction aborted
    # ...
```

---

## commit() and rollback()

### When to Use commit()

**WARNING**: Manual `commit()` is rarely needed in Odoo!

```python
# From odoo/sql_db.py:487
def commit(self):
    """ Perform an SQL `COMMIT` """
    self.flush()
    result = self._cnx.commit()
    self.clear()
    self._now = None
    self.prerollback.clear()
    self.postrollback.clear()
    self.postcommit.run()
    return result
```

Odoo automatically commits at the end of HTTP requests. Only use manual commit for:

1. **Long-running batch jobs** (to release locks periodically)
2. **Multi-transaction operations** (cron jobs, data imports)

```python
# GOOD: Batch commit for long operations
def process_large_dataset(self):
    records = self.search([])
    batch_size = 100
    for i in range(0, len(records), batch_size):
        batch = records[i:i+batch_size]
        batch.write({'processed': True})
        self.env.cr.commit()  # Commit progress
```

### When NOT to Use commit()

```python
# BAD: Commit inside normal business logic
@api.model
def create_order(self, values):
    order = self.create(values)
    self.env.cr.commit()  # DON'T DO THIS!
    order.action_confirm()  # If this fails, order is already committed!
```

### rollback() Usage

```python
# From odoo/sql_db.py:498
def rollback(self):
    """ Perform an SQL `ROLLBACK` """
    self.clear()
    self.postcommit.clear()
    self.prerollback.run()
    result = self._cnx.rollback()
    self._now = None
    self.postrollback.run()
    return result
```

**When to use rollback**:
- After catching critical errors in cron jobs
- In test cleanup
- In multi-phase operations where you want to undo everything

```python
# GOOD: Rollback on error in batch operation
def batch_import(self, data_list):
    try:
        for data in data_list:
            self.create(data)
        self.env.cr.commit()
    except Exception as e:
        self.env.cr.rollback()
        _logger.error("Import failed, rolled back: %s", e)
```

### Cursor as Context Manager

```python
# From odoo/sql_db.py:193
def __enter__(self):
    return self

def __exit__(self, exc_type, exc_value, traceback):
    try:
        if exc_type is None:
            self.commit()
    finally:
        self.close()

# Usage
with self.env.registry.cursor() as cr:
    cr.execute("SELECT ...")
    # Auto-commits on success, auto-rolls back on error
```

---

## Transaction Aborted Errors

### InFailedSqlTransaction

After any database error, PostgreSQL enters an "aborted transaction" state:

```python
# ERROR: current transaction is aborted, commands ignored until end of transaction block
```

### Why This Happens

```
1. Transaction starts
2. Query executes → ERROR (UniqueViolation, etc.)
3. Transaction state → ABORTED
4. Any subsequent query → InFailedSqlTransaction ERROR
5. Must ROLLBACK to return to normal state
```

### Proper Error Recovery

```python
# BAD: Continuing after error without cleanup
try:
    record = self.create({'email': 'duplicate@email.com'})
except psycopg2.errors.UniqueViolation:
    pass  # Transaction is now ABORTED
record = self.create({'email': 'another@email.com'})  # FAILS! InFailedSqlTransaction

# GOOD: Use savepoint for isolation
with self.env.cr.savepoint():
    try:
        record = self.create({'email': 'duplicate@email.com'})
    except psycopg2.errors.UniqueViolation:
        pass  # Savepoint rolled back, transaction OK
# This now works:
record = self.create({'email': 'another@email.com'})

# GOOD: Use context manager for operations that might fail
def safe_create(self, values):
    with self.env.cr.savepoint():
        return self.create(values)
```

### Nested Savepoints and Transaction State

```python
# Outer transaction
with self.env.cr.savepoint():  # Savepoint A
    # Inner savepoint
    with self.env.cr.savepoint():  # Savepoint B
        raise UniqueViolation("boom")
    # B rolled back, A still active, transaction OK

# All good - both savepoints released, no commit
```

---

## Serialization Errors

### What is Serialization Error?

PostgreSQL error code `40001` (serialization_error) occurs when concurrent transactions conflict:

```
ERROR: could not serialize access due to concurrent update
```

### Common Causes

1. **Concurrent updates on same records**
2. **Multiple workers processing same account** (common in cron jobs)

### Detection Pattern

```python
# From logs - same IDs with identical timestamps confirm concurrent processing
2026-01-20 02:45:54.198378 UPDATE fb_daily_expense SET ... WHERE id IN (3807, 3808, ...)
2026-01-20 02:45:54.198378 UPDATE fb_daily_expense SET ... WHERE id IN (3807, 3808, ...)
# → Serialization error: two workers updating same records
```

### Solution: Account-Level Locking

```python
# Use PostgreSQL advisory lock to prevent concurrent processing
def fetch_all_for_account(self, account_id):
    # Try to acquire lock - returns False if locked
    self.env.cr.execute("""
        SELECT pg_try_advisory_xact_lock(%s)
    """, (account_id,))

    if not self.env.cr.fetchone()[0]:
        # Another worker is processing this account
        _logger.info("Account %s already being processed, skipping", account_id)
        return

    # We have the lock - safe to process
    # ... fetch and process data ...
```

### Alternative: Identity-Based Deduplication

For queue jobs, use `identity_key` to prevent duplicates:

```python
# With queue jobs
from odoo.addons.queue_job.job import job

@job(identity_key='{{account_id}}_{{date}}')
def fetch_daily_expenses(self, account_id, date):
    # Only one job per account+date combination
    pass
```

### Batch Updates to Minimize Conflicts

```python
# BAD: Update in loop - each update is a serialization point
for record in records:
    record.write({'amount': computed_amount})

# GOOD: Group identical values, single update
from collections import defaultdict
value_groups = defaultdict(list)
for record, amount in zip(records, amounts):
    value_groups[amount].append(record.id)

for amount, ids in value_groups.items():
    self.env.cr.execute(
        "UPDATE fb_daily_expense SET amount = %s WHERE id IN %s",
        (amount, tuple(ids))
    )
```

---

## Quick Reference

### PostgreSQL Error Codes

| Code | Name | Odoo Handler |
|------|------|--------------|
| 23502 | NOT NULL violation | `convert_pgerror_not_null` |
| 23505 | UNIQUE violation | `convert_pgerror_unique` |
| 23514 | CHECK violation | `convert_pgerror_constraint` |
| 40001 | Serialization failure | Must retry with retry_on_serializable=True |
| 25P02 | InFailedSqlTransaction | Must rollback |

### Savepoint Decision Tree

```
Need error isolation?
├── Single operation that might fail → savepoint()
├── Batch operation with individual failures → Loop with savepoint()
├── Schema operation (ddl) → savepoint(flush=False)
└── Import/data loading → savepoint() with exception handling

Need flush control?
├── Need latest data in savepoint → savepoint(flush=True) [default]
└── Avoid cache invalidation → savepoint(flush=False)
```

### Transaction Recovery Checklist

After catching a database error:

- [ ] Am I using a savepoint? If yes, transaction is fine
- [ ] Do I need to execute more queries? If yes, use savepoint next time
- [ ] Should I rollback the entire transaction?
- [ ] Should I retry the operation?

### Best Practices

1. **Always use `with cr.savepoint()`** for operations that might fail
2. **Never commit() mid-business-logic** unless you know why
3. **Check for duplicates before creating** rather than catching UniqueViolation
4. **Use advisory locks** for cron jobs that might overlap
5. **Group identical updates** to minimize serialization conflicts
6. **Flush before SQL queries** using `self.flush_model()` or SQL.to_flush

---

## Common Patterns Reference

### Pattern 1: Safe Batch Create with Error Isolation

```python
@api.model
def batch_create_safe(self, records_data):
    """Create records, continuing on individual failures"""
    created = []
    failed = []

    for data in records_data:
        with self.env.cr.savepoint():
            try:
                record = self.create(data)
                created.append(record)
            except (psycopg2.Error, ValidationError) as e:
                failed.append({'data': data, 'error': str(e)})

    return created, failed
```

### Pattern 2: Upsert (Update or Insert)

```python
@api.model
def upsert_by_key(self, key_field, key_value, values):
    """Update if exists, insert if not"""
    existing = self.search([(key_field, '=', key_value)], limit=1)
    if existing:
        existing.write(values)
        return existing
    return self.create({key_field: key_value, **values})
```

### Pattern 3: Retry on Serialization Error

```python
from odoo import tools

@api.model
def update_with_retry(self, records, values, max_retries=3):
    """Retry update on serialization error"""
    for attempt in range(max_retries):
        try:
            return records.write(values)
        except psycopg2.errors.SerializationError:
            if attempt == max_retries - 1:
                raise
            tools.config['test_enable'] = False  # Avoid test mode issues
            self.env.cr.rollback()
            self._cr.execute("SELECT 1")  # Reset transaction state
```

### Pattern 4: Flush Before SQL Query

```python
from odoo.tools import SQL

@api.model
def get_aggregated_data(self):
    """Flush ORM changes before direct SQL"""
    # Flush pending ORM changes
    self.flush_model(['state', 'amount'])

    query = SQL("""
        SELECT state, SUM(amount) as total
        FROM %s
        WHERE state IN %s
        GROUP BY state
    """, SQL.identifier(self._table), ('done', 'cancel'))

    self.env.cr.execute(query)
    return dict(self.env.cr.fetchall())
```

---

## Sources

- `odoo/sql_db.py` - Cursor, Savepoint, Connection classes
- `odoo/models.py:7564` - `convert_pgerror_unique()`
- `odoo/models.py:7618` - `PGERROR_TO_OE` mapping
- `odoo/tools/sql.py` - Schema operations with savepoints
- PostgreSQL Documentation: Transaction Isolation, Error Codes


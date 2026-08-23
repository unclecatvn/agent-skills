---
name: odoo-16-transaction
description: Complete guide for handling database transactions, UniqueViolation errors, savepoints, and commit operations in Odoo 16.
globs: "**/*.{py,xml}"
topics:
  - Transaction states and isolation
  - UniqueViolation and other psycopg2 error codes
  - Savepoint usage patterns (flushing vs non-flushing)
  - commit() and rollback() best practices
  - InFailedSqlTransaction recovery
  - Serialization errors and FOR UPDATE NOWAIT
  - flush_all / invalidate_all
  - Cross-cursor patterns
when_to_use:
  - Handling duplicate key errors
  - Working with savepoints for error isolation
  - Understanding transaction abort states
  - Preventing serialization conflicts
  - Writing resilient cron / batch code
---

# Odoo 16 Transaction Guide

Complete guide for handling database transactions, psycopg2 errors, savepoints, and commits in Odoo 16.

## Table of Contents

1. [Transaction States](#transaction-states)
2. [UniqueViolation Errors](#uniqueviolation-errors)
3. [Savepoint Usage](#savepoint-usage)
4. [commit() and rollback()](#commit-and-rollback)
5. [Transaction Aborted Errors](#transaction-aborted-errors)
6. [Serialization Errors](#serialization-errors)
7. [Flush & Cache Interaction](#flush--cache-interaction)
8. [Test Mode & Cross-Cursor Patterns](#test-mode--cross-cursor-patterns)
9. [Exception Classes](#exception-classes)

---

## Transaction States

### PostgreSQL Transaction Isolation

Odoo 16 uses **REPEATABLE READ** as the default isolation level (set once on the psycopg2 connection in `odoo/sql_db.py`):

```python
# odoo/sql_db.py
from psycopg2.extensions import ISOLATION_LEVEL_REPEATABLE_READ

class Cursor(BaseCursor):
    def __init__(self, pool, dbname, dsn):
        ...
        self.connection.set_isolation_level(ISOLATION_LEVEL_REPEATABLE_READ)
```

What this means in practice:

- Your transaction sees a snapshot taken at its first query
- Concurrent updates on the same rows by another transaction cause a **serialization error** (SQLSTATE `40001`) when you try to write them
- Schema changes by other transactions are not visible mid-transaction

### Transaction State Flow

```
Normal --[error]--> ABORTED --[rollback]--> Normal
                       |
                       +--[any SQL]--> InFailedSqlTransaction (25P02)
                       +--[commit]---> ERROR (cannot commit aborted tx)
```

Once PostgreSQL aborts the transaction, **every subsequent statement fails** until you `ROLLBACK` or `ROLLBACK TO SAVEPOINT`.

---

## UniqueViolation Errors

### What triggers it

PostgreSQL error code `23505` - raised when an INSERT/UPDATE would violate a `UNIQUE` constraint.

```python
import psycopg2

self.create({'email': 'user@example.com'})
self.create({'email': 'user@example.com'})  # -> psycopg2.errors.UniqueViolation
```

### Odoo's built-in conversion

Odoo converts Postgres constraint errors into friendlier messages via `PGERROR_TO_OE` (`odoo/models.py`):

```python
# odoo/models.py
PGERROR_TO_OE = defaultdict(
    lambda: (lambda model, fvg, info, pgerror: {'message': tools.ustr(pgerror)}),
    {
        '23502': convert_pgerror_not_null,    # NOT NULL
        '23505': convert_pgerror_unique,      # UNIQUE
        '23514': convert_pgerror_constraint,  # CHECK
    },
)
```

`convert_pgerror_unique` opens a **fresh cursor** to introspect `pg_constraint`, because the original transaction is already aborted:

```python
# odoo/models.py
def convert_pgerror_unique(model, fields, info, e):
    # new cursor since we're probably in an error handler in a blown transaction
    with closing(model.env.registry.cursor()) as cr_tmp:
        cr_tmp.execute("""
            SELECT conname, t.relname, ARRAY(
                SELECT attname FROM pg_attribute
                 WHERE attrelid = conrelid AND attnum = ANY(conkey)
            ) as columns
              FROM pg_constraint
              JOIN pg_class t ON t.oid = conrelid
             WHERE conname = %s
        """, (e.diag.constraint_name,))
```

### Handling UniqueViolation correctly

```python
import psycopg2

# BAD: no savepoint -> transaction is blown after catch
try:
    self.create({'email': email})
except psycopg2.errors.UniqueViolation:
    existing = self.search([('email', '=', email)])  # InFailedSqlTransaction!

# GOOD: isolate with a savepoint and catch outside it
try:
    with self.env.cr.savepoint():
        self.create({'email': email})
except psycopg2.errors.UniqueViolation:
    pass
# Transaction remains valid; you can continue.

# PREFERRED for unique keys: let the database arbitrate, isolate the race,
# then retry or re-read from a fresh transaction if needed.
try:
    with self.env.cr.savepoint():
        self.create({'email': email})
except psycopg2.errors.UniqueViolation:
    raise  # let the caller retry, or reopen a fresh transaction before re-reading

# A pre-check can still be a fast path, but it is not race-safe on its own.
existing = self.search([('email', '=', email)], limit=1)
if not existing:
    self.create({'email': email})
```

---

## Savepoint Usage

### What a savepoint is

A savepoint is a nested transaction you can roll back independently of the outer transaction. In Odoo 16, `cr.savepoint()` is the supported API: it issues the underlying `SAVEPOINT`, `ROLLBACK TO SAVEPOINT`, and `RELEASE SAVEPOINT` statements for you, and the default `flush=True` mode also coordinates ORM flush/cache handling.

```python
# Preferred in business code: let Odoo manage the savepoint lifecycle
with self.env.cr.savepoint():
    self.create({'name': 'something'})
    ...
```

Manual `SAVEPOINT` SQL is only a low-level raw-SQL fallback. It is **not** a drop-in substitute for `cr.savepoint()` when ORM-managed state, flush behavior, or cache invalidation are involved.

If you ever have to manage a savepoint manually in a tightly scoped low-level path, keep it conservative:

- Use a short, hard-coded name local to that code path only
- Never derive the savepoint name from user input or other runtime data
- Treat manual naming as fragile and avoid generalizing this pattern into normal business code
- Use DB-API parameters only for values inside the statements you run under the savepoint; parameters do not substitute SQL identifiers

```python
cr.execute('SAVEPOINT import_step')
try:
    cr.execute(
        'UPDATE my_table SET processed = %s WHERE id = %s',
        (True, record_id),
    )
except Exception:
    cr.execute('ROLLBACK TO SAVEPOINT import_step')
    cr.execute('RELEASE SAVEPOINT import_step')
    raise
else:
    cr.execute('RELEASE SAVEPOINT import_step')
```

### Basic pattern

```python
with self.env.cr.savepoint():
    self.create({'name': 'something'})
    raise ValueError("boom")
# Savepoint rolled back on exception; outer transaction still valid.
```

### Flushing vs non-flushing

**`flush=True` (default)** - what you want 99% of the time:

- Flushes pending ORM cache writes to the DB before `SAVEPOINT`
- On success, flushes again before `RELEASE`
- On rollback, clears the ORM cache (avoids stale data)

**`flush=False`** - only when you deliberately do not want cache interaction:

- You are about to run pure SQL that does not touch ORM-managed fields
- You want to try `SELECT ... FOR UPDATE NOWAIT` without flushing pending writes
- DDL/schema operations (see `odoo/tools/sql.py`)

```python
# FOR UPDATE NOWAIT wants the lock attempt to fail fast,
# not to flush unrelated cached writes beforehand
with self.env.cr.savepoint(flush=False):
    self.env.cr.execute(
        'SELECT id FROM sale_order WHERE id IN %s FOR UPDATE NOWAIT',
        (tuple(ids),),
    )
```

### Batch import with per-record isolation

```python
for data in rows:
    try:
        with self.env.cr.savepoint():
            rec = self.create(data)
            rec._process()
    except (psycopg2.Error, ValidationError) as e:
        _logger.warning("Skipping row %s: %s", data.get('ref'), e)
```

Each failing row rolls back only its own savepoint; the rest still get committed when the request ends.

### `@contextmanager` wrapper

If you need a reusable "try this, undo on any error" helper:

```python
from contextlib import contextmanager

@contextmanager
def safe_step(env, label):
    with env.cr.savepoint():
        try:
            yield
        except Exception as e:
            _logger.exception("Step %s failed", label)
            raise

with safe_step(self.env, 'confirm'):
    order.action_confirm()
```

### Anti-patterns

```python
# BAD: manual SAVEPOINT with reused name
cr.execute('SAVEPOINT foo')
cr.execute('RELEASE SAVEPOINT foo')
cr.execute('SAVEPOINT foo')  # fine but fragile; forget to release -> leak

# GOOD: context manager auto-names with uuid
with self.env.cr.savepoint():
    ...

# BAD: swallowing the error and then doing unrelated ORM work
try:
    self.create(vals)
except Exception:
    pass
self.search([])  # works, but only if no DB error happened;
                 # with psycopg2 errors this is a guaranteed InFailedSqlTransaction
```

---

## commit() and rollback()

### `Cursor.commit()` / `Cursor.rollback()`

```python
# odoo/sql_db.py
def commit(self):
    self.flush()
    result = self._cnx.commit()
    self.clear()
    self._now = None
    self.prerollback.clear()
    self.postrollback.clear()
    self.postcommit.run()
    return result

def rollback(self):
    self.clear()
    self.postcommit.clear()
    self.prerollback.run()
    result = self._cnx.rollback()
    self._now = None
    self.postrollback.run()
    return result
```

Note the hooks: `precommit`, `postcommit`, `prerollback`, `postrollback` are callback queues on `BaseCursor`. Business code rarely manipulates them directly.

### When to use `commit()`

**Almost never** in request-handling code. Odoo commits for you at the end of an HTTP request or cron job.

Never call `commit()` or `rollback()` on Odoo's ambient cursor
(`self.env.cr`). Odoo owns that transaction. Manual control is an
**exceptional last resort** and requires a cursor that this code created
explicitly for one complete, recoverable unit of work. Document why the
boundary is safe. Typical cases include:

1. **Long cron jobs** that must release row locks periodically.
2. **Data imports or migration scripts** that need to persist progress.
3. **Init hooks** running outside a normal HTTP/RPC cycle.
4. **Independent audit or error-path logging** that must survive a caller
   rollback.

```python
# LAST RESORT: each chunk gets its own cursor and is safe to restart after a
# later chunk fails. Never commit the caller's self.env.cr cursor.
from contextlib import closing
from odoo import api

def _cron_sync(self):
    for chunk_ids in self._chunk_ids():
        with closing(self.env.registry.cursor()) as cr:
            env = api.Environment(cr, self.env.uid, self.env.context)
            env['my.model'].browse(chunk_ids)._sync_chunk()
            cr.commit()
```

### When NOT to use `commit()`

```python
# BAD: mid-business-logic commit makes errors impossible to roll back
def create_order(self, vals):
    order = self.create(vals)
    self.env.cr.commit()           # point of no return
    order.action_confirm()         # if this fails, order is orphaned
    self.env.cr.commit()
```

### `rollback()` in error handlers

Manual rollback is also limited to a cursor created explicitly by this code.
For a recoverable sub-operation on the ambient transaction, use a savepoint
and let Odoo handle the outer transaction.

```python
from contextlib import closing
from odoo import api

def batch_import(self, rows):
    # This import deliberately owns an independent cursor and its rollback.
    with closing(self.env.registry.cursor()) as cr:
        env = api.Environment(cr, self.env.uid, self.env.context)
        try:
            env['my.model'].create(rows)
            cr.commit()
        except Exception:
            cr.rollback()
            _logger.exception("Batch import failed, rolled back")
            raise

# For ordinary request/cron work, isolate a recoverable operation instead:
def _create_one(self, values):
    with self.env.cr.savepoint():
        return self.create(values)
```

### Cursor as context manager

```python
# odoo/sql_db.py - BaseCursor.__enter__/__exit__ auto-commits on success
with self.env.registry.cursor() as cr:
    cr.execute("UPDATE ...")
# auto-commit on clean exit, auto-close always
```

---

## Transaction Aborted Errors

### Symptom

```
psycopg2.errors.InFailedSqlTransaction:
current transaction is aborted, commands ignored until end of transaction block
```

### Cause

```
1. Transaction starts
2. A query fails (UniqueViolation, NotNullViolation, etc.)
3. PostgreSQL flags the transaction as aborted
4. Every subsequent SQL fails with 25P02 until you ROLLBACK
```

### Recovery

Prefer isolating a recoverable operation with `savepoint()` so only that
operation is rolled back. If the code owns the entire batch transaction, a
manual rollback remains available as a last-resort recovery boundary.

```python
# GOOD: savepoint keeps outer transaction alive
try:
    with self.env.cr.savepoint():
        self.create({'email': 'dup@x.com'})
except psycopg2.errors.UniqueViolation:
    pass
# We can keep working here.
self.create({'email': 'ok@x.com'})
```

### Nested savepoints

Nested savepoints compose correctly: rolling back the inner one keeps the outer savepoint (and outer transaction) valid.

```python
with self.env.cr.savepoint():           # outer (A)
    try:
        with self.env.cr.savepoint():   # inner (B)
            raise psycopg2.errors.UniqueViolation
    except psycopg2.errors.UniqueViolation:
        pass
    # B rolled back; A and the main tx are still valid
# A also committed normally here.
```

---

## Serialization Errors

### What it is

PostgreSQL error code `40001` - under REPEATABLE READ, two transactions that have each read and are now trying to update the same rows can be told "you lose, retry".

```
ERROR: could not serialize access due to concurrent update
```

### Typical causes

- Two cron workers running the same job for the same record
- Two HTTP requests writing the same record in parallel
- Any code that reads then updates without row-level locking

### The Odoo pattern: `SELECT ... FOR UPDATE NOWAIT`

Used in base modules (`ir_sequence`, `account_edi_document`, `website_sale` payment flow, etc.). Lock the row immediately; if someone else holds it, skip.

```python
from psycopg2.errors import LockNotAvailable

def _process_safe(self, record):
    try:
        with self.env.cr.savepoint(flush=False):
            self.env.cr.execute(
                'SELECT id FROM %s WHERE id = %%s FOR UPDATE NOWAIT' % self._table,
                (record.id,),
            )
    except LockNotAvailable:
        _logger.info("Record %s locked, skipping", record.id)
        return False

    record._do_process()
    return True
```

Key points:

- `FOR UPDATE NOWAIT` raises `LockNotAvailable` (SQLSTATE `55P03`) instead of blocking
- `savepoint(flush=False)` - we deliberately do not flush pending ORM writes just to try the lock
- Catch `LockNotAvailable` to gracefully skip

### Batch processing with locking

```python
from psycopg2.errors import LockNotAvailable

def _batch_process(self, records):
    processed, skipped = 0, 0
    for record in records:
        try:
            with self.env.cr.savepoint(flush=False):
                self.env.cr.execute(
                    'SELECT id FROM %s WHERE id IN %%s FOR UPDATE NOWAIT' % self._table,
                    (tuple(record.ids),),
                )
        except LockNotAvailable:
            skipped += 1
            continue
        record._do_process()
        processed += 1
    return processed, skipped
```

### Retry on serialization error

When you *cannot* avoid the conflict, retry:

```python
import psycopg2
import time

def _write_with_retry(self, values, retries=3):
    for attempt in range(retries):
        try:
            return self.write(values)
        except psycopg2.errors.SerializationFailure:
            if attempt == retries - 1:
                raise
            self.env.cr.rollback()
            time.sleep(0.05 * (2 ** attempt))   # small backoff
```

Note: the RPC layer in `odoo/service/model.py` already retries "concurrent update" errors for you at the request level (`MAX_TRIES_ON_CONCURRENCY_FAILURE`), so manual retry loops are only needed inside cron jobs or long-lived sessions.

### Group identical updates

Each individual `UPDATE` is a serialization point. Collapse identical writes:

```python
from collections import defaultdict

groups = defaultdict(list)
for rec, amount in zip(records, amounts):
    groups[amount].append(rec.id)

for amount, ids in groups.items():
    self.env['fb.daily.expense'].browse(ids).write({'amount': amount})
```

---

## Flush & Cache Interaction

### `env.flush_all()`

Flushes every pending recompute and write across all models in the current environment.

```python
# odoo/api.py
def flush_all(self):
    self._recompute_all()
    for model_name in OrderedSet(f.model_name for f in self.cache.get_dirty_fields()):
        self[model_name].flush_model()
```

Call it before:

- `cr.execute()` that reads columns you just wrote to
- An external script that bypasses Odoo's ORM
- A Postgres trigger-dependent operation

### `env.invalidate_all(flush=True)`

Flushes (by default) and then drops the cache. Use when you suspect the cache is out of sync with the DB (e.g. after raw SQL that modified tracked columns).

```python
self.env.cr.execute("UPDATE sale_order SET state='done' WHERE id = %s", (oid,))
# Cache still says state='draft' for that record
self.env.invalidate_all()
```

### Savepoints and the cache

`_FlushingSavepoint` (the default) already handles this for you: it flushes before `SAVEPOINT` and clears the cache on `ROLLBACK TO SAVEPOINT`. That is why you rarely need to touch `invalidate_all()` manually when you use savepoints.

---

## Test Mode & Cross-Cursor Patterns

### `registry.in_test_mode()`

Odoo test runs keep a single outer transaction that is rolled back at the end of the test. Code that opens a new cursor behaves differently in tests.

```python
# odoo/modules/registry.py
def in_test_mode(self):
    return self.test_cr is not None
```

If you need a "real" independent cursor in production but a shared test cursor during tests, use `self.env.registry.cursor()`. In test mode this returns a `TestCursor` wrapping the main cursor so rollbacks still work. That means the "survives caller rollback" framing is production-oriented; tests may intentionally behave differently.

```python
from contextlib import closing

def _log_audit(self, message):
    # Fresh cursor for production-style independent audit logging;
    # tests may still route this through the shared test cursor wrapper.
    with closing(self.env.registry.cursor()) as cr:
        env = odoo.api.Environment(cr, self.env.uid, self.env.context)
        env['audit.log'].create({'message': message})
        # Required: the audit record survives a later rollback of the caller.
        cr.commit()
```

### Why a new cursor?

Two use cases:

1. **Auditing / logging** that, in production, should outlive a rollback in the caller
2. **Error handlers** that need to run SQL when the outer transaction is already aborted (this is why `convert_pgerror_unique` opens a new cursor)

Warning: a new cursor opens a new PostgreSQL transaction. It cannot see uncommitted data from the outer cursor. Only use it when you genuinely want isolation.

---

## Exception Classes

All Odoo exception types live in `odoo/exceptions.py`:

| Class | Inherits | Typical meaning |
|-------|----------|-----------------|
| `UserError` | `Exception` | Generic user-facing error (shown as dialog). Use for business-rule violations. |
| `ValidationError` | `UserError` | Python constraint violation (`@api.constrains` or field check). |
| `AccessError` | `UserError` | Access right / record rule denial. |
| `AccessDenied` | `UserError` | Login or password error - no traceback attached. |
| `MissingError` | `UserError` | Record does not exist or was deleted. |
| `RedirectWarning` | `Exception` | Error with a follow-up action / button for the user. |
| `CacheMiss` | `KeyError` | Internal: value not in ORM cache. Do not raise from business code. |

```python
from odoo.exceptions import UserError, ValidationError, AccessError, RedirectWarning

if not partner.email:
    raise UserError(_("Partner has no email"))

if amount < 0:
    raise ValidationError(_("Amount must be positive"))
```

### psycopg2 error classes

The database-level errors you will catch most often:

```python
import psycopg2
from psycopg2 import errors
from psycopg2.errors import (
    UniqueViolation,        # 23505
    NotNullViolation,       # 23502
    CheckViolation,         # 23514
    SerializationFailure,   # 40001
    LockNotAvailable,       # 55P03
    InFailedSqlTransaction, # 25P02
)
```

Always isolate these with `with cr.savepoint():`, then catch them outside the block unless you are about to rollback the full transaction.

---

## Quick Reference

### PostgreSQL Error Codes

| Code | Name | Odoo handler / typical fix |
|------|------|-----------------------------|
| 23502 | NOT NULL violation | `convert_pgerror_not_null` |
| 23505 | UNIQUE violation | `convert_pgerror_unique` |
| 23514 | CHECK violation | `convert_pgerror_constraint` |
| 40001 | Serialization failure | Retry, or use `FOR UPDATE NOWAIT` |
| 25P02 | In-failed SQL transaction | `ROLLBACK` or use savepoints |
| 55P03 | Lock not available | Skip / retry later |

### Savepoint decision tree

```
Need error isolation?
|- Single op that might fail                -> with cr.savepoint(): ...
|- Batch of N ops with individual failures   -> for x in xs: with cr.savepoint(): ...
|- Trying to grab a lock                     -> with cr.savepoint(flush=False): SELECT ... FOR UPDATE NOWAIT
|- Schema / DDL                              -> with cr.savepoint(flush=False): ...
```

### Transaction recovery checklist

After catching a database error, ask:

- [ ] Was it caught inside a `with cr.savepoint():`? If yes, transaction is still valid.
- [ ] If not, can I re-raise and let Odoo roll back the ambient transaction?
- [ ] Do I need to `env.invalidate_all()` to drop stale cache entries?
- [ ] Will the caller (HTTP/cron) retry, or should I retry here?

### Best Practices

1. Use `with cr.savepoint()` for anything that may fail.
2. Never `commit()` mid-business-logic.
3. For unique keys, prefer savepoint-scoped create flows that let the database arbitrate races, then retry or re-read from a fresh transaction if needed.
4. Use `SELECT ... FOR UPDATE NOWAIT` + `savepoint(flush=False)` for cron contention.
5. Group identical updates to minimize serialization conflicts.
6. Flush before raw SQL reads.
7. Use a new cursor (`registry.cursor()`) only for exceptional independent
   work such as audit/error-path logging or a restartable batch.

---

## Common Patterns Reference

### Pattern 1: Safe batch create

```python
import psycopg2
from odoo.exceptions import ValidationError

def batch_create_safe(self, rows):
    created, failed = [], []
    for data in rows:
        try:
            with self.env.cr.savepoint():
                created.append(self.create(data))
        except (psycopg2.Error, ValidationError) as e:
            failed.append({'data': data, 'error': str(e)})
    return created, failed
```

### Pattern 2: Unique-key create with a retry boundary

```python
import psycopg2

def create_by_key(self, values):
    try:
        with self.env.cr.savepoint():
            return self.create(values)
    except psycopg2.errors.UniqueViolation:
        # Another transaction won the race; retry or re-read in a fresh transaction.
        raise
```

### Pattern 3: Record locking (Odoo standard)

```python
from psycopg2.errors import LockNotAvailable

def process_with_lock(self, records):
    for record in records:
        try:
            with self.env.cr.savepoint(flush=False):
                self.env.cr.execute(
                    'SELECT id FROM %s WHERE id IN %%s FOR UPDATE NOWAIT' % self._table,
                    (tuple(record.ids),),
                )
        except LockNotAvailable:
            _logger.info("Record %s locked, skipping", record.id)
            continue
        record._do_process()
```

### Pattern 4: Retry on serialization error

```python
import psycopg2
import time

def write_with_retry(self, vals, retries=3):
    for attempt in range(retries):
        try:
            return self.write(vals)
        except psycopg2.errors.SerializationFailure:
            if attempt == retries - 1:
                raise
            self.env.cr.rollback()
            time.sleep(0.05 * (2 ** attempt))
```

### Pattern 5: Production-style audit log with a separate cursor

```python
from contextlib import closing
import odoo

def _audit(self, message):
    with closing(self.env.registry.cursor()) as cr:
        env = odoo.api.Environment(cr, self.env.uid, self.env.context)
        env['audit.log'].create({'message': message})
        # Required: the audit record survives a later rollback of the caller.
        cr.commit()
```

### Pattern 6: Flush before raw SQL

```python
def get_totals(self):
    self.env['sale.order'].flush_model(['state', 'amount_total'])
    self.env.cr.execute("""
        SELECT state, SUM(amount_total)
          FROM sale_order
         WHERE state IN %s
         GROUP BY state
    """, (('done', 'cancel'),))
    return dict(self.env.cr.fetchall())
```

---

## Coding Conventions

- Never call `commit()` or `rollback()` on `self.env.cr`. Odoo owns normal
  request and cron transactions; re-raise failures or use a savepoint.
- Manual `commit()` and `rollback()` are exceptional and permitted only on a
  cursor explicitly created by the current code. Before using them, make the
  unit restartable and document its recovery boundary.
- A manually committed separate cursor is useful for deliberately isolated
  work such as an audit log or recoverable batch; keep its boundary explicit
  and close it reliably.
- Every non-framework `cr.commit()` needs a nearby comment explaining why it
  is necessary and why the isolated transaction is safe.
- Prefer a savepoint for recoverable database errors. Catch only exceptions
  you can handle and re-raise unexpected failures.

## Base Code Reference

- `odoo/sql_db.py` - `Cursor`, `BaseCursor`, `Savepoint`, `_FlushingSavepoint`, isolation level
- `odoo/api.py` - `Environment.flush_all`, `Environment.invalidate_all`, precommit/postcommit hooks
- `odoo/exceptions.py` - `UserError`, `ValidationError`, `AccessError`, `AccessDenied`, `MissingError`, `RedirectWarning`, `CacheMiss`
- `odoo/models.py` - `PGERROR_TO_OE`, `convert_pgerror_unique`, `convert_pgerror_not_null`, `convert_pgerror_constraint`
- `odoo/service/model.py` - RPC-level concurrency retry loop (`MAX_TRIES_ON_CONCURRENCY_FAILURE`)
- `odoo/modules/registry.py` - `Registry.cursor()`, `in_test_mode()`
- `odoo/addons/base/models/ir_sequence.py` - reference `FOR UPDATE NOWAIT` usage
- `odoo/addons/account_edi/models/account_edi_document.py` - reference locking pattern
- PostgreSQL docs: Transaction Isolation, Error Codes

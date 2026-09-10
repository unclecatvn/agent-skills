# Odoo 19 Transaction Guide

## Coding Conventions

- Never call `commit()` or `rollback()` on `self.env.cr`: Odoo owns normal
  request and cron transactions. Re-raise failures or use a savepoint.
- A manual commit or rollback is exceptional and only permitted on a cursor
  explicitly created by the current code. Make the unit restartable and
  document why its independent transaction boundary is safe.
- Prefer a savepoint for recoverable database errors. Catch only exceptions
  that can be handled; re-raise unexpected failures.

Guide for handling database transactions in Odoo 19: errors, savepoints, and serialization failures.

## Table of Contents
- [Transaction Overview](#transaction-overview)
- [Database Errors](#database-errors)
- [Savepoints](#savepoints)
- [Error Handling](#error-handling)
- [Serialization Failures](#serialization-failures)
- [Best Practices](#best-practices)

---

## Transaction Overview

Odoo uses database transactions to ensure data consistency.

### Transaction Properties

| Property | Description |
|-----------|-------------|
| **Atomicity** | All or nothing |
| **Consistency** | Data remains valid |
| **Isolation** | Concurrent transactions don't interfere |
| **Durability** | Committed data persists |

### Transaction Flow

```
Begin Transaction
├── Execute Operations
├── (Commit or Rollback)
└── End Transaction
```

---

## Database Errors

### Common Errors

| Error | When |
|-------|------|
| `UniqueViolation` | Duplicate unique constraint |
| `NotNullViolation` | NULL in NOT NULL column |
| `ForeignKeyViolation` | Invalid foreign key |
| `CheckViolation` | CHECK constraint failed |
| `SerializationFailure` | Concurrent modification |

### Catch Database Errors

```python
from odoo.exceptions import ValidationError, UserError
from psycopg2 import errors

try:
    record.write({'field': 'value'})
except errors.UniqueViolation as e:
    raise ValidationError("Duplicate value!")
except errors.NotNullViolation as e:
    raise ValidationError("Required field missing!")
```

---

## Savepoints

Savepoints isolate errors within a transaction.

### Using Savepoints

```python
def process_records(self):
    for record in self:
        try:
            with self.env.cr.savepoint():
                record.process()
        except (ValidationError, UserError) as error:
            _logger.warning("Failed to process %s: %s", record, error)
```

### Savepoint Lifetime

```python
with self.env.cr.savepoint():
    record.process()
# The context manager releases the savepoint on success and rolls it back
# when an exception escapes the block.
```

---

## Error Handling

### Retry on Serialization Failure

Do not retry an ambient transaction inside model code. Let Odoo retry the
complete request or cron transaction, or re-raise so its scheduler can do so.

### Handle Validation Errors

```python
from odoo.exceptions import ValidationError

@api.constrains('email')
def _check_email(self):
    for record in self:
        if not tools.email_validation(record.email):
            raise ValidationError("Invalid email: %s" % record.email)
```

---

## Serialization Failures

### What is Serialization Failure?

Occurs when two transactions try to modify the same data concurrently.

### Avoid Serialization Failures

```python
# BAD: Loop with search and write
def process(self):
    for record in self.search([('state', '=', 'draft')]):
        record.write({'state': 'done'})

# GOOD: Single write
def process(self):
    self.search([('state', '=', 'draft')]).write({'state': 'done'})
```

### Use SQL FOR UPDATE

```python
self.env.cr.execute("SELECT id FROM my_model WHERE id IN %s FOR UPDATE", (tuple(self.ids),))
# Process records
```

---

## Commit and Rollback

### Auto Commit

Odoo commits the transaction once at the end of a successful request or job
(controller call, RPC call, cron job), not immediately after each ORM call. If
an exception is raised before that boundary, the whole transaction is rolled
back, undoing every write made since it started.

```python
from odoo import http
from odoo.http import request

class MyController(http.Controller):
    @http.route('/process', auth='user', type='jsonrpc')
    def process(self, record_id):
        record = request.env['my.model'].browse(record_id)
        record.write({'field': 'value'})
        # No manual commit here: Odoo commits automatically when this
        # request completes successfully.
```

### Recoverable Work

```python
try:
    with self.env.cr.savepoint():
        record1.write({'field': 'value'})
        record2.write({'field': 'value'})
except ValidationError:
    # The savepoint rolls back only this recoverable unit.
    raise
```

Only an explicitly created cursor may be committed or rolled back. Such code
must document why the independently restartable transaction boundary is safe.

---

## Best Practices

### Batch Operations

```python
# GOOD: Batch create
def create_records(self, values_list):
    return self.create(values_list)

# BAD: Create in loop
def create_records(self, values_list):
    for values in values_list:
        self.create(values)
```

### Use Context for Special Cases

```python
# Skip tracking for bulk update
records.with_context(tracking_disable=True).write({'field': 'value'})
```

### Validate Before Writing

```python
@api.constrains('email')
def _check_email(self):
    # Validate before write
    for record in self:
        if not tools.email_validation(record.email):
            raise ValidationError("Invalid email")
```

---

## Common Patterns

### Safe Update Pattern

```python
def safe_update(self, values):
    try:
        self.write(values)
    except errors.UniqueViolation:
        raise UserError("Duplicate entry!")
    except errors.NotNullViolation:
        raise UserError("Required field missing!")
```

### Bulk Processing with Savepoints

```python
def bulk_process(self, records):
    for record in records:
        try:
            with self.env.cr.savepoint():
                record.process()
        except (ValidationError, UserError) as error:
            _logger.warning("Failed: %s", error)
```

---

## References

- PostgreSQL documentation on transactions
- Odoo 19 ORM documentation

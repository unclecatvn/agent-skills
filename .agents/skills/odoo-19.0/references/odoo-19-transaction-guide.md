# Odoo 19 Transaction Guide

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
        # Create savepoint before each record
        self.env.cr.execute("SAVEPOINT my_savepoint")

        try:
            record.process()
        except Exception as e:
            # Rollback to savepoint on error
            self.env.cr.execute("ROLLBACK TO SAVEPOINT my_savepoint")
            _logger.warning("Failed to process %s: %s", record, e)
```

### Release Savepoint

```python
try:
    record.process()
finally:
    # Release savepoint
    self.env.cr.execute("RELEASE SAVEPOINT my_savepoint")
```

---

## Error Handling

### Retry on Serialization Failure

```python
from odoo.exceptions import UserError
from psycopg2 import OperationalError

def retry_on_failure(max_retries=3):
    def decorator(func):
        def wrapper(self, *args, **kwargs):
            for attempt in range(max_retries):
                try:
                    return func(self, *args, **kwargs)
                except OperationalError as e:
                    if e.pgcode == '40001':  # Serialization failure
                        if attempt < max_retries - 1:
                            self.env.cr.rollback()
                            self.env.cr.execute("SAVEPOINT retry_savepoint")
                            continue
                    raise
        return wrapper
    return decorator
```

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

Odoo auto-commits after successful operations.

```python
# Transaction is auto-committed
record.write({'field': 'value'})
```

### Manual Rollback

```python
try:
    # Multiple operations
    record1.write({'field': 'value'})
    record2.write({'field': 'value'})
except Exception as e:
    # Rollback entire transaction
    self.env.cr.rollback()
    raise
```

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
        self.env.cr.execute("SAVEPOINT process_savepoint")
        try:
            record.process()
        except Exception as e:
            self.env.cr.execute("ROLLBACK TO SAVEPOINT process_savepoint")
            _logger.warning("Failed: %s", e)
        finally:
            self.env.cr.execute("RELEASE SAVEPOINT process_savepoint")
```

---

## References

- PostgreSQL documentation on transactions
- Odoo 19 ORM documentation

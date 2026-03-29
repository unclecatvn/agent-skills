# Odoo 19 Model Guide

Guide for working with Odoo 19 ORM, recordsets, CRUD operations, and domain filters.

## Table of Contents

- [Models](#models)
- [Fields](#fields)
- [SQL Constraints](#sql-constraints)
- [Database Indexes](#database-indexes)
- [Recordsets](#recordsets)
- [CRUD Operations](#crud-operations)
- [Search Domains](#search-domains)
- [Environment](#environment)
- [SQL Execution](#sql-execution)
- [Inheritance](#inheritance)

---

## Models

### Defining a Model

> **Odoo 19 Change**: `_name` is now **optional**. Odoo derives it automatically from the CamelCase class name (each capital letter → `.` separator). E.g. `ResPartner` → `res.partner`, `SaleOrder` → `sale.order`.

```python
from odoo import models, fields

# Odoo 19: _name auto-derived from class name
class MyModel(models.Model):
    # _name = 'my.model'  ← auto-derived, can be omitted
    _description = 'My Model'

    field1 = fields.Char()
    field2 = fields.Integer(string="Field Label")
```

```python
# When _name differs from class name convention, specify explicitly:
class CustomNameModel(models.Model):
    _name = 'custom.different.name'
    _description = 'Custom Named Model'

    name = fields.Char()
```

### Model Attributes

| Attribute       | Description                                                                   |
| --------------- | ----------------------------------------------------------------------------- |
| `_name`         | Model name (**optional in Odoo 19** — auto-derived from CamelCase class name) |
| `_description`  | Model description                                                             |
| `_order`        | Default sort order                                                            |
| `_rec_name`     | Field to use as name representation                                           |
| `_inherit`      | Model(s) to inherit from                                                      |
| `_inherits`     | Delegation inheritance                                                        |
| `_table`        | Database table name                                                           |
| `_log_access`   | Enable create_date, write_date, create_uid, write_uid                         |
| `_auto`         | Auto-create database table                                                    |
| `_abstract`     | Abstract model                                                                |
| `_transient`    | Transient model                                                               |
| `_parent_store` | Enable parent_path field                                                      |
| `_fold_name`    | Field for kanban fold                                                         |

### Model Types

| Class                   | Description                        |
| ----------------------- | ---------------------------------- |
| `models.Model`          | Regular database model             |
| `models.TransientModel` | Temporary/wizard model             |
| `models.AbstractModel`  | Abstract model (no database table) |

---

## Fields

### Field Definition

Fields are defined as class attributes on the model.

```python
from odoo import models, fields

class MyModel(models.Model):
    _name = 'my.model'

    name = fields.Char(required=True)
    description = fields.Text()
    active = fields.Boolean(default=True)
    count = fields.Integer()
    price = fields.Float(digits='Product Price')
```

### Default Values

```python
# Value
name = fields.Char(default="A value")

# Function
def _default_name(self):
    return self.get_value()

name = fields.Char(default=lambda self: self._default_name())
```

### Field Types

| Type              | Class                        | Description                 |
| ----------------- | ---------------------------- | --------------------------- |
| **Basic**         |                              |                             |
| Boolean           | `fields.Boolean()`           | True/False                  |
| Char              | `fields.Char()`              | String (limited length)     |
| Float             | `fields.Float()`             | Floating-point number       |
| Integer           | `fields.Integer()`           | Integer                     |
| **Advanced**      |                              |                             |
| Binary            | `fields.Binary()`            | Binary data (files)         |
| Html              | `fields.Html()`              | HTML content                |
| Image             | `fields.Image()`             | Image (enhanced Binary)     |
| Monetary          | `fields.Monetary()`          | Monetary amount             |
| Selection         | `fields.Selection()`         | Selection from list         |
| Text              | `fields.Text()`              | Long text                   |
| **Date**          |                              |                             |
| Date              | `fields.Date()`              | Date (no time)              |
| Datetime          | `fields.Datetime()`          | Date and time               |
| **Relational**    |                              |                             |
| Many2one          | `fields.Many2one()`          | Many-to-one                 |
| One2many          | `fields.One2many()`          | One-to-many                 |
| Many2many         | `fields.Many2many()`         | Many-to-many                |
| **Pseudo**        |                              |                             |
| Reference         | `fields.Reference()`         | Reference to any model      |
| Many2oneReference | `fields.Many2oneReference()` | Many2one with dynamic model |

### Computed Fields

```python
from odoo import api

total = fields.Float(compute='_compute_total', store=True)

@api.depends('value', 'tax')
def _compute_total(self):
    for record in self:
        record.total = record.value + record.value * record.tax
```

### Related Fields

```python
nickname = fields.Char(related='partner_id.name', store=True)
```

### Automatic Fields

| Field          | Type     | Description           |
| -------------- | -------- | --------------------- |
| `id`           | int      | Identifier            |
| `display_name` | char     | Display name          |
| `create_date`  | datetime | Creation timestamp    |
| `create_uid`   | Many2one | Creator               |
| `write_date`   | datetime | Last update timestamp |
| `write_uid`    | Many2one | Last modifier         |

### Reserved Field Names

| Name          | Type      | Purpose                   |
| ------------- | --------- | ------------------------- |
| `name`        | Char      | Default `rec_name`        |
| `active`      | Boolean   | Toggles global visibility |
| `state`       | Selection | Lifecycle stages          |
| `parent_id`   | Many2one  | Tree structure parent     |
| `parent_path` | Char      | Tree structure path       |
| `company_id`  | Many2one  | Multi-company field       |

---

## SQL Constraints

> **Odoo 19 Breaking Change**: `_sql_constraints` is **no longer supported**. Use `models.Constraint` instead.

### models.Constraint (Odoo 19)

SQL constraints are now defined as model attributes using `models.Constraint`:

```python
from odoo import models, fields

class MyModel(models.Model):
    _name = 'my.model'
    _description = 'My Model'

    name = fields.Char(required=True)
    code = fields.Char()
    quantity = fields.Integer()

    # UNIQUE constraint
    _unique_name = models.Constraint(
        'UNIQUE(name)',
        'Name must be unique!',
    )

    # UNIQUE on multiple fields
    _unique_name_code = models.Constraint(
        'UNIQUE(name, code)',
        'The combination of name and code must be unique!',
    )

    # CHECK constraint
    _check_quantity = models.Constraint(
        'CHECK(quantity > 0)',
        'Quantity must be positive!',
    )
```

### Constraint Naming

If you omit the `_name` in the constraint, Odoo auto-generates a unique name based on model + attribute name.

### Migration from `_sql_constraints`

```python
# ❌ OLD (Odoo 18 and earlier) — NO LONGER WORKS in Odoo 19
class MyModel(models.Model):
    _name = 'my.model'
    _sql_constraints = [
        ('name_uniq', 'UNIQUE(name)', 'Name must be unique!'),
        ('check_qty', 'CHECK(quantity > 0)', 'Quantity must be positive!'),
    ]

# ✅ NEW (Odoo 19)
class MyModel(models.Model):
    _name = 'my.model'

    _name_uniq = models.Constraint(
        'UNIQUE(name)',
        'Name must be unique!',
    )

    _check_qty = models.Constraint(
        'CHECK(quantity > 0)',
        'Quantity must be positive!',
    )
```

### Overriding Constraints in Inherited Models

Constraints can be overridden or removed in inherited models:

```python
class ExtendedModel(models.Model):
    _inherit = 'my.model'

    # Override constraint with different check
    _check_qty = models.Constraint(
        'CHECK(quantity >= 0)',
        'Quantity cannot be negative!',
    )
```

---

## Database Indexes

### Field-Level Index

```python
name = fields.Char(index=True)  # Simple btree index
```

### Declarative Index (Odoo 19)

For composite or custom indexes, use `models.Index`:

```python
class MyModel(models.Model):
    _name = 'my.model'

    name = fields.Char()
    code = fields.Char()
    date = fields.Date()

    # Composite index on multiple fields
    _name_code_idx = models.Index('(name, code)')

    # Index with specific method
    _date_idx = models.Index('(date DESC)')
```

> **Warning**: Don't over-index — indexes consume space and impact INSERT/UPDATE/DELETE performance.

---

## Recordsets

### Active Record Interface

```python
# Read field
record.name
record.company_id.name

# Write field
record.name = "Bob"

# Dynamic field access
field = "name"
record[field]
```

### Iteration

```python
def do_operation(self):
    for record in self:
        # record is a single record
        print(record.name)
```

### Record Cache and Prefetching

Odoo maintains a cache and prefetches records/fields following heuristics.

```python
# Without prefetching: 2000 queries
for partner in partners:
    print(partner.name)
    print(partner.lang)

# With prefetching: 1 query
for partner in partners:
    print(partner.name)
    print(partner.lang)
```

---

## CRUD Operations

### Create

```python
# Single record
record = self.env['model.name'].create({'field': 'value'})

# Multiple records (batch)
records = self.env['model.name'].create([
    {'field': 'value1'},
    {'field': 'value2'},
])
```

### Read

```python
# Browse
record = self.env['model.name'].browse(record_id)
records = self.env['model.name'].browse([id1, id2, id3])

# Read
data = records.read(['field1', 'field2'])
```

### Write

```python
# Single record
record.write({'field': 'value'})

# Multiple records
records.write({'field': 'value'})
```

### Unlink (Delete)

```python
# Single record
record.unlink()

# Multiple records
records.unlink()
```

---

## Search Domains

A search domain is a first-order logical predicate for filtering.

### Domain Condition

```python
# Simple condition
domain = [('name', '=', 'ABC')]

# Multiple conditions
domain = [('name', '=', 'ABC'), ('phone', 'like', '7620')]
```

### Operators

| Operator                             | Description        |
| ------------------------------------ | ------------------ |
| `=`                                  | equals             |
| `!=`                                 | not equals         |
| `>`, `>=`, `<`, `<=`                 | comparison         |
| `=?`                                 | unset or equals    |
| `=like`, `like`, `ilike`, `=ilike`   | pattern matching   |
| `in`, `not in`                       | in list            |
| `child_of`, `parent_of`              | tree traversal     |
| `any`, `any!`, `not any`, `not any!` | relation traversal |

### Logical Operators

```python
# AND (implicit)
domain = [('name', '=', 'ABC'), ('state', '=', 'draft')]

# OR
domain = '|', [('name', '=', 'ABC')], [('name', '=', 'XYZ')]

# NOT
domain = '!', [('state', '=', 'draft')]
```

### Domain Class

```python
from odoo.fields import Domain

# Create domain
d1 = Domain('name', '=', 'abc')
d2 = Domain('phone', 'like', '7620')

# Combine
d3 = d1 & d2  # AND
d4 = d1 | d2  # OR
d5 = ~d1      # NOT

# Parse from list
domain = Domain([('name', '=', 'abc'), ('phone', 'like', '7620')])

# Serialize to list
domain_list = list(domain)
```

### Search Methods

```python
# Search
records = self.env['model'].search(domain)

# Search with limit
records = self.env['model'].search(domain, limit=10)

# Search with offset
records = self.env['model'].search(domain, offset=20)

# Search with order
records = self.env['model'].search(domain, order='name ASC')

# Search count
count = self.env['model'].search_count(domain)

# Search and read
records = self.env['model'].search_read(domain, ['field1', 'field2'])

# Search fetch (Odoo 19+)
records = self.env['model'].search_fetch(domain, ['field1', 'field2'])

# Name search
records = self.env['model'].name_search('keyword', operator='ilike')
```

---

## Environment

The environment holds:

- Database cursor (`cr`)
- Current user (`user`, `uid`)
- Context (`context`)
- Record cache

### Accessing Environment

```python
# From recordset
env = record.env

# Create new recordset in another model
model = env['another.model']

# Access properties
env.uid         # Current user id
env.user        # Current user recordset
env.company     # Current company
env.companies   # Allowed companies
env.lang        # Current language
```

### Altering Environment

```python
# Change context
records.with_context(lang='fr_FR')

# Change user
records.with_user(user_id)

# Change company
records.with_company(company_id)

# Change environment completely
records.with_env(new_env)

# Sudo (superuser mode)
records.sudo()
```

---

## SQL Execution

### Raw SQL

```python
# Execute query
self.env.cr.execute("SELECT id FROM table WHERE field = %s", (value,))

# Fetch results
results = self.env.cr.fetchall()
row = self.env.cr.fetchone()
```

### SQL Class (Recommended)

```python
from odoo.tools import SQL

# Build query
query = SQL("SELECT id FROM table WHERE field = %s", value)

# Execute
self.env.cr.execute(query)
```

### Flush and Invalidate

Before SQL queries, flush pending data:

```python
# Flush all records of a model
self.env['model'].flush_model(['field1', 'field2'])

# Flush specific recordset
records.flush_recordset(['field1', 'field2'])
```

After SQL modifications, invalidate cache:

```python
# Invalidate all records of a model
self.env['model'].invalidate_model(['field1', 'field2'])

# Invalidate specific recordset
records.invalidate_recordset(['field1', 'field2'])

# Notify field modification
records.modified(['field1', 'field2'])
```

---

## Inheritance

### Classical Inheritance

Create new model from existing one:

```python
class Inheritance1(models.Model):
    _name = 'inheritance.1'
    _description = 'Inheritance One'

    name = fields.Char()

class Inheritance2(models.Model):
    _name = 'inheritance.2'
    _inherit = ['inheritance.1']
    _description = 'Inheritance Two'

    # Inherits name field from inheritance.1
    # Adds new fields/methods
```

### Extension

Extend existing model in-place:

```python
class Extension0(models.Model):
    _name = 'extension.0'
    _description = 'Extension zero'

    name = fields.Char(default="A")

class Extension0(models.Model):
    _inherit = 'extension.0'

    description = fields.Char(default="Extended")
```

### Delegation

Delegate fields to child records:

```python
class Screen(models.Model):
    _name = 'delegation.screen'

    size = fields.Float(string='Screen Size')

class Laptop(models.Model):
    _name = 'delegation.laptop'

    _inherits = {
        'delegation.screen': 'screen_id',
    }

    name = fields.Char(string='Name')
    screen_id = fields.Many2one('delegation.screen', required=True, ondelete="cascade")

# Can access size directly on laptop
laptop.size
```

---

## References

- Source: Odoo 19 documentation `/doc/developer/reference/backend/orm.rst`

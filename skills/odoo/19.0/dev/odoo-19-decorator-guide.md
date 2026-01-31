# Odoo 19 Decorator Guide

Guide for using `@api` decorators in Odoo 19: computed fields, validation, onchange, and more.

## Table of Contents
- [Method Decorators](#method-decorators)
- [@api.depends](#apidepends)
- [@api.constrains](#apiconstrains)
- [@api.ondelete](#apiondelete)
- [@api.onchange](#apionchange)
- [@api.model](#apimodel)
- [@api.model_create_multi](#apimodel_create_multi)
- [@api.autovacuum](#apiautovacuum)
- [@api_returns](#apireturns)

---

## Method Decorators

Decorators in Odoo 19 are in `odoo.api` module:

```python
from odoo import api, models

class MyModel(models.Model):
    _name = 'my.model'

    @api.depends('field')
    def _compute_method(self):
        pass
```

---

## @api.depends

For computed fields. Specifies dependencies that trigger recomputation.

### Basic Usage

```python
total = fields.Float(compute='_compute_total', store=True)

@api.depends('value', 'tax')
def _compute_total(self):
    for record in self:
        record.total = record.value + record.value * record.tax
```

### Dotted Paths

Can use dotted paths for relational fields:

```python
@api.depends('partner_id.email')
def _compute_email(self):
    for record in self:
        record.email = record.partner_id.email
```

### Multiple Fields

Compute multiple fields:

```python
discount_value = fields.Float(compute='_apply_discount')
total = fields.Float(compute='_apply_discount')

@api.depends('value', 'discount')
def _apply_discount(self):
    for record in self:
        discount = record.value * record.discount
        record.discount_value = discount
        record.total = record.value - discount
```

### Search on Computed Field

```python
upper_name = fields.Char(compute='_compute_upper', search='_search_upper')

@api.depends('name')
def _compute_upper(self):
    for record in self:
        record.upper_name = record.name.upper() if record.name else False

def _search_upper(self, operator, value):
    if operator == 'like':
        operator = 'ilike'
    return [('name', operator, value)]
```

### Inverse Method

Allow setting computed field:

```python
document = fields.Char(compute='_get_document', inverse='_set_document')

@api.depends('document_path')
def _get_document(self):
    for record in self:
        with open(record.document_path) as f:
            record.document = f.read()

def _set_document(self):
    for record in self:
        if not record.document:
            continue
        with open(record.document_path) as f:
            f.write(record.document)
```

---

## @api.constrains

For validation. Called on create and write.

### Basic Usage

```python
@api.constrains('email')
def _check_email(self):
    for record in self:
        if not tools.email_validation(record.email):
            raise ValidationError("Invalid email")
```

### Multiple Fields

```python
@api.constrains('date_start', 'date_end')
def _check_dates(self):
    for record in self:
        if record.date_end < record.date_start:
            raise ValidationError("End date must be after start date")
```

### No Dotted Paths

Unlike `@api.depends`, **cannot use dotted paths**:

```python
# BAD: dotted path not supported
@api.constrains('partner_id.email')
def _check_email(self):
    pass

# GOOD: use simple field name
@api.constrains('partner_id')
def _check_email(self):
    for record in self:
        if not tools.email_validation(record.partner_id.email):
            raise ValidationError("Invalid email")
```

---

## @api.ondelete

For delete validation (Odoo 18+).

```python
@api.ondelete(at_uninstall=False)
def _unlink_if_not_draft(self):
    if any(rec.state != 'draft' for rec in self):
        raise UserError("Cannot delete non-draft records")
```

### Parameters

| Parameter | Description |
|-----------|-------------|
| `at_uninstall` | If `False`, allows deletion when module is uninstalled |

### Why Use @api.ondelete?

- **Better than overriding `unlink()`**: Doesn't break module uninstall
- **Clear intent**: Explicitly for delete validation
- **Automatic**: Called before deletion

### Unlink Override (Anti-pattern)

```python
# BAD: breaks module uninstall
def unlink(self):
    if any(rec.state != 'draft' for rec in self):
        raise UserError("Cannot delete non-draft records")
    return super().unlink()
```

---

## @api.onchange

For form UI updates when field values change.

### Basic Usage

```python
@api.onchange('partner_id')
def _onchange_partner_id(self):
    if self.partner_id:
        self.email = self.partner_id.email
        self.phone = self.partner_id.phone
```

### Multiple Fields

```python
@api.onchange('country_id', 'state_id')
def _onchange_location(self):
    if self.country_id:
            # Update zip format
            pass
```

### No CRUD Operations

**Important**: `onchange` methods should **not** perform CRUD operations.

```python
# BAD: create in onchange
@api.onchange('field1')
def _onchange_field1(self):
    self.env['another.model'].create({'name': 'test'})

# GOOD: only modify current record
@api.onchange('field1')
def _onchange_field1(self):
    self.field2 = 'computed value'
```

### Return Warning

```python
@api.onchange('amount')
def _onchange_amount(self):
    if self.amount < 0:
        return {
            'warning': {
                'title': "Warning",
                'message': "Amount cannot be negative",
            }
        }
```

---

## @api.model

For model-level methods that don't depend on `self`.

### Usage

```python
@api.model
def get_default_values(self):
    return {
        'field1': 'value1',
        'field2': 'value2',
    }
```

### Can be called on any recordset

```python
# Can call on any recordset (self may be empty)
record = self.env['my.model'].browse([1, 2, 3])
defaults = record.get_default_values()
```

---

## @api.model_create_multi

For handling batch create operations.

```python
@api.model_create_multi
def create(self, vals_list):
    # Add default values
    for vals in vals_list:
        vals.setdefault('field', 'default')
    return super().create(vals_list)
```

### Why Use It?

Odoo 17+ creates records in batches by default. This decorator ensures proper handling.

---

## @api.autovacuum

For methods to run by cron vacuuem.

```python
@api.autovacuum
def _gc_entries(self):
    # Clean old records
    domain = [('create_date', '<', date.today() - timedelta(days=90)])
    self.search(domain).unlink()
```

---

## Decorator Decision Tree

```
Need to define field behavior?
├── Field computed from other fields → @api.depends
│   └── CAN use dotted paths
├── Validate data → @api.constrains
│   └── CANNOT use dotted paths
├── Prevent record deletion → @api.ondelete
└── Update form UI → @api.onchange
    └── NO CRUD operations allowed

Need to define method behavior?
├── Method-level, doesn't depend on self → @api.model
└── Normal record method → no decorator needed
```

---

## Common Patterns

### Computed Field with Inverse

```python
total = fields.Float(compute='_compute_total', inverse='_inverse_total', store=True)

@api.depends('subtotal', 'tax')
def _compute_total(self):
    for record in self:
        record.total = record.subtotal + record.tax

def _inverse_total(self):
    for record in self:
        record.subtotal = record.total - record.tax
```

### Validation with Constraints

```python
@api.constrains('age')
def _check_age(self):
    for record in self:
        if record.age < 18:
            raise ValidationError("Must be 18 or older")
```

### Delete Validation

```python
@api.ondelete(at_uninstall=False)
def _unlink_if_not_cancelled(self):
    if any(rec.state != 'cancel' for rec in self):
        raise UserError("Only cancelled records can be deleted")
```

### Onchange for Defaults

```python
@api.onchange('partner_id')
def _onchange_partner_id(self):
    if self.partner_id:
        self.lang = self.partner_id.lang
        self.user_id = self.partner_id.user_id
```

---

## References

- Source: Odoo 19 documentation `/doc/developer/reference/backend/orm.rst`

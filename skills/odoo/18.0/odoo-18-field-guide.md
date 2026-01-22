---
name: odoo-18-field
description: Complete reference for Odoo 18 field types, parameters, and when to use each. Use this guide when defining model fields, choosing field types, or configuring field parameters.
globs: "**/models/**/*.py"
topics:
  - Simple fields (Char, Text, Html, Boolean, Integer, Float, Monetary, Date, Datetime, Binary, Selection, Reference)
  - Relational fields (Many2one, One2many, Many2many)
  - Computed fields (compute, store, search, inverse)
  - Related fields
  - Field parameters (index, default, copy, store, groups, company_dependent, tracking)
when_to_use:
  - Defining new model fields
  - Choosing appropriate field types
  - Configuring computed fields
  - Setting up relational fields
  - Optimizing field parameters
---

# Odoo 18 Field Guide

Complete reference for Odoo 18 field types, parameters, and when to use each.

## Table of Contents

1. [Simple Fields](#simple-fields)
2. [Relational Fields](#relational-fields)
3. [Computed Fields](#computed-fields)
4. [Related Fields](#related-fields)
5. [Field Parameters](#field-parameters)

---

## Simple Fields

### Char - String Field

```python
name = fields.Char(
    string='Name',
    required=True,
    size=100,  # Optional: max length (not enforced by ORM)
    translate=True,  # Enable translation
    default='',  # Default value
)

# Short text (names, codes, etc.)
code = fields.Char(string='Code', index=True)
reference = fields.Char(string='Reference', copy=False)  # Not copied on duplicate
```

**Use for**: Short text values (names, codes, references). Use `size` hint for UI only.

---

### Text - Long Text Field

```python
description = fields.Text(
    string='Description',
    translate=True,
)

# Notes, descriptions, long content
notes = fields.Text(string='Notes')
```

**Use for**: Long-form text content. Not searchable by default in database.

---

### Html - Rich Text Field

```python
content = fields.Html(
    string='Content',
    translate=True,
    sanitize=True,  # Sanitize HTML to prevent XSS
)

# Email body, website content
email_body = fields.Html(string='Email Body')
```

**Use for**: HTML content (email templates, website pages). Automatically sanitized.

---

### Boolean - True/False Field

```python
active = fields.Boolean(
    string='Active',
    default=True,
)

is_company = fields.Boolean(string='Is Company')
```

**Use for**: Yes/No values. Default is `False` if not specified.

---

### Integer - Whole Number Field

```python
quantity = fields.Integer(
    string='Quantity',
    default=1,
)

# Integer with range constraint
priority = fields.Integer(
    string='Priority',
    default=0,
)
```

**Use for**: Whole numbers. Large numbers should use `Float` or `Monetary` instead.

---

### Float - Decimal Number Field

```python
price = fields.Float(
    string='Price',
    digits='Product Price',  # Named precision from decimal.precision
)

# Direct digits specification
weight = fields.Float(
    string='Weight',
    digits=(16, 3),  # (total digits, decimal places)
)
```

**Use for**: Non-monetary decimal values. For currency, use `Monetary` field instead.

### Float Helper Methods (Odoo 18)

```python
# Float precision helpers
from odoo import fields

# Round to precision
rounded = fields.Float.round(
    value,
    precision_rounding=self.product_uom_id.rounding
)

# Check if value is zero at precision
is_zero = fields.Float.is_zero(
    value,
    precision_rounding=self.product_uom_id.rounding
)

# Compare two values at precision
result = fields.Float.compare(
    value1,
    value2,
    precision_rounding=self.product_uom_id.rounding
)
# Returns: negative (v1 < v2), 0 (equal), positive (v1 > v2)
```

**Common Use Cases**:

```python
# Round quantity before display
display_qty = fields.Float.round(
    self.quantity,
    precision_rounding=self.uom_id.rounding
)

# Check if quantity is effectively zero
if fields.Float.is_zero(self.quantity, precision_rounding=0.001):
    raise UserError("Quantity cannot be zero")

# Compare prices at precision
if fields.Float.compare(self.price, self.list_price, precision_rounding=0.01) >= 0:
    # Price is greater than or equal to list price
    pass
```

**Important**: Always use precision_rounding from the unit of measure (product.uom_id.rounding) or currency (res.currency.rounding) when working with Float fields to avoid floating-point comparison issues.

---

### Monetary - Currency Field

```python
amount = fields.Monetary(
    string='Amount',
    currency_field='currency_id',  # many2one to res.currency
)

amount_total = fields.Monetary(
    string='Total',
    currency_field='company_id.currency_id',
)
```

**Use for**: All monetary values. Automatically handles currency formatting and precision.

**Important**: Always specify `currency_field` pointing to a `res.currency` many2one.

---

### Date - Date Field

```python
date = fields.Date(
    string='Date',
    default=fields.Date.context_today,
    copy=False,
)

# Date computed field
date_deadline = fields.Date(
    string='Deadline',
    compute='_compute_date_deadline',
    store=True,
)
```

**Use for**: Dates without time. Stored as date in database (no timezone issues).

---

### Datetime - Timestamp Field

```python
datetime = fields.Datetime(
    string='DateTime',
    default=fields.Datetime.now,
    copy=False,
)

# Common pattern for tracking
create_date = fields.Datetime(string='Created on', readonly=True)
write_date = fields.Datetime(string='Last Updated on', readonly=True)
```

**Use for**: Dates with time. Stored as UTC, displayed in user timezone.

### Date/Datetime Helper Methods (Odoo 18)

```python
# Date helper methods
from odoo import fields

# Get start/end of period
start_of_month = fields.Date.start_of(fields.Date.today(), 'month')
end_of_quarter = fields.Date.end_of(fields.Date.today(), 'quarter')

# Add/subtract time periods
next_month = fields.Date.add(fields.Date.today(), months=1)
last_week = fields.Date.subtract(fields.Date.today(), weeks=2)

# Supported granularities: 'year', 'quarter', 'month', 'week', 'day', 'hour'

# Convert to/from string
date_obj = fields.Date.to_date('2024-01-15')  # String to date
date_str = fields.Date.to_string(fields.Date.today())  # Date to string

# Context-aware today
today_tz = fields.Date.context_today(record)  # Today in record's timezone

# Datetime helper methods
now_utc = fields.Datetime.now()  # Current UTC datetime
today_midnight = fields.Datetime.today()  # Today at midnight (00:00:00)

# Add/subtract datetime
next_hour = fields.Datetime.add(fields.Datetime.now(), hours=1)
yesterday = fields.Datetime.subtract(fields.Datetime.now(), days=1)

# Convert to/from string
datetime_obj = fields.Datetime.to_datetime('2024-01-15 14:30:00')
datetime_str = fields.Datetime.to_string(fields.Datetime.now())

# Context-aware timestamp
timestamp_tz = fields.Datetime.context_timestamp(record, datetime_obj)
```

**Common Use Cases**:

```python
# Get start of current month for reports
start_date = fields.Date.start_of(fields.Date.today(), 'month')
end_date = fields.Date.end_of(fields.Date.today(), 'month')

# Add 30 days to current date
due_date = fields.Date.add(fields.Date.today(), days=30)

# Get end of current quarter
quarter_end = fields.Date.end_of(fields.Date.today(), 'quarter')
```

---

### Binary - File/Attachment Field

```python
file = fields.Binary(
    string='File',
    attachment=True,  # Show in attachments chatter
)

image = fields.Binary(string='Image')
image_1920 = fields.Binary(string='Image 1920', max_width=1920, max_height=1920)
```

**Use for**: File attachments and images. Use `attachment=True` for chatter integration.

**Note**: With `bin_size` context, returns size in bytes instead of content.

---

### Image - Image Field with Resize (Odoo 18)

```python
# Image field with automatic resize
image = fields.Image(
    string='Image',
    max_width=1920,      # Resize if wider than 1920px
    max_height=1080,     # Resize if taller than 1080px
    verify_resolution=True,  # Check max resolution (50MP default)
)

# Product image
image_1920 = fields.Image(
    string='Product Image',
    max_width=1920,
    max_height=1920,
)

# Without size limit
image_large = fields.Image(
    string='Large Image',
    max_width=0,  # No limit
    max_height=0,  # No limit
    verify_resolution=False,
)
```

**Important**:
- `Image` extends `Binary` field
- Automatically resizes images if they exceed `max_width`/`max_height` while maintaining aspect ratio
- `verify_resolution=True` checks against maximum image resolution (~50MP default)
- If `max_width` or `max_height` is 0 and `verify_resolution` is False, no verification is performed

---

### Many2oneReference - Dynamic Typed Reference (Odoo 18)

```python
# Many2oneReference - model stored in separate field
ref_id = fields.Many2oneReference(
    string='Reference',
    model_field='model_name',  # Char field containing model name
)

# Example usage
class MyModel(models.Model):
    _name = 'my.model'

    model_name = fields.Char(string='Model Name')  # Stores model name
    ref_id = fields.Many2oneReference(
        string='Reference',
        model_field='model_name'
    )

# Usage: ref_id can point to any model, model_name stores which model
# Stored as integer ID in database (more efficient than Reference string)
```

**Important**:
- `Many2oneReference` stores value as integer ID (unlike `Reference` which stores "model,id" string)
- Requires a separate Char field to store the model name
- More efficient than `Reference` for database queries and joins
- Use when you need dynamic references to multiple possible models

---

### Selection - Dropdown Field

```python
# Simple selection
state = fields.Selection([
    ('draft', 'Draft'),
    ('confirmed', 'Confirmed'),
    ('done', 'Done'),
], string='State', default='draft')

# Selection from model method
state = fields.Selection(
    '_get_selection_states',
    string='State'
)

@api.model
def _get_selection_states(self):
    return [
        ('draft', 'Draft'),
        ('confirmed', 'Confirmed'),
    ]
```

**Use for**: Fixed set of options. Values are stored in database, must not change keys.

---

### Reference - Dynamic Reference

```python
ref_id = fields.Reference(
    string='Reference',
    selection='_models_get',
)

@api.model
def _models_get(self):
    models = self.env['ir.model'].search([])
    return [(model.model, model.name) for model in models]
```

**Use for**: References to multiple possible models. Stored as `model,id` string.

---

## Relational Fields

### Many2one - Many-to-One

```python
partner_id = fields.Many2one(
    'res.partner',
    string='Partner',
    required=True,
    ondelete='cascade',  # 'set null', 'restrict', 'cascade'
    domain=[('customer_rank', '>', 0)],
    context={'default_customer_rank': 1},
    default=lambda self: self.env.user.partner_id.id,
)

# Optional many2one
company_id = fields.Many2one(
    'res.company',
    string='Company',
    ondelete='set null',
)

# With delegate (inherits)
partner_id = fields.Many2one(
    'res.partner',
    string='Partner',
    required=True,
    ondelete='cascade',
    delegate=True,  # Inherits all fields from partner
)
```

**Parameters**:
- `comodel_name` - Target model (positional argument)
- `ondelete` - What to do when referenced record is deleted: `'set null'`, `'restrict'`, `'cascade'`
- `domain` - Domain for searchable dropdown
- `context` - Context passed to action
- `default` - Default value (can be callable)
- `delegate` - Enable inheritance (delegate pattern)

---

### One2many - One-to-Many

```python
# Inverse of Many2one - MUST specify inverse_name
line_ids = fields.One2many(
    'sale.order.line',
    'order_id',
    string='Order Lines',
)

# One2many with computed domain (Odoo 18)
active_line_ids = fields.One2many(
    'sale.order.line',
    'order_id',
    string='Active Lines',
    domain=[('state', '!=', 'cancel')],
)
```

**Parameters**:
- `comodel_name` - Target model (positional argument)
- `inverse_name` - Many2one field on target model that points back (REQUIRED)
- `domain` - Domain filter for displayed records
- `copy` - Copy lines on duplicate (default `True`)

**Important**: Always define the corresponding `Many2one` on the child model.

---

### Many2many - Many-to-Many

```python
tag_ids = fields.Many2many(
    'sale.order.tag',
    'sale_order_tag_rel',
    'order_id',
    'tag_id',
    string='Tags',
)

# Without relation table name (auto-generated)
category_ids = fields.Many2many(
    'res.partner.category',
    string='Categories',
)

# Many2many with domain
allowed_category_ids = fields.Many2many(
    'res.partner.category',
    string='Allowed Categories',
    domain=[('parent_id', '=', False)],
)
```

**Parameters**:
- `comodel_name` - Target model (positional argument)
- `relation` - Relation table name (optional, auto-generated if omitted)
- `column1` - Column name for this model's ID in relation table
- `column2` - Column name for target model's ID in relation table
- `domain` - Domain for displayed records

---

## Computed Fields

### Basic Compute Field

```python
amount_total = fields.Float(
    string='Total',
    compute='_compute_amount_total',
)

@api.depends('amount_untaxed', 'tax_amount', 'discount_amount')
def _compute_amount_total(self):
    for record in self:
        record.amount_total = (
            record.amount_untaxed
            + record.tax_amount
            - record.discount_amount
        )
```

### Stored Compute Field

```python
# Stored - can be searched, used in domains
amount_total = fields.Float(
    string='Total',
    compute='_compute_amount_total',
    store=True,
)

@api.depends('line_ids.price_subtotal')
def _compute_amount_total(self):
    for order in self:
        order.amount_total = sum(order.line_ids.mapped('price_subtotal'))
```

### Compute with Search

```python
# Allow searching on computed field
display_name = fields.Char(
    string='Display Name',
    compute='_compute_display_name',
    search='_search_display_name',
)

@api.depends('name', 'ref')
def _compute_display_name(self):
    for record in self:
        record.display_name = f"[{record.ref}] {record.name}"

def _search_display_name(self, operator, value):
    return ['|', ('name', operator, value), ('ref', operator, value)]
```

### Compute with Inverse

```python
# Allow writing to computed field (bidirectional)
name = fields.Char(
    string='Name',
    compute='_compute_name',
    inverse='_inverse_name',
)

@api.depends('first_name', 'last_name')
def _compute_name(self):
    for record in self:
        record.name = f"{record.first_name} {record.last_name}"

def _inverse_name(self):
    for record in self:
        parts = record.name.split(' ', 1)
        record.first_name = parts[0]
        record.last_name = parts[1] if len(parts) > 1 else ''
```

---

## Related Fields

### Basic Related Field

```python
partner_name = fields.Char(
    string='Partner Name',
    related='partner_id.name',
    readonly=True,
)

# Store related field (for search/group by)
partner_country_id = fields.Many2one(
    'res.country',
    string='Country',
    related='partner_id.country_id',
    store=True,
)
```

### Multi-Level Related

```python
partner_country_code = fields.Char(
    string='Country Code',
    related='partner_id.country_id.code',
    readonly=True,
)
```

### Related with Company Dependency

```python
company_currency_id = fields.Many2one(
    'res.currency',
    related='company_id.currency_id',
    string='Company Currency',
    readonly=True,
)
```

---

## Field Parameters

### Common Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| `string` | str | Field label (display name) |
| `required` | bool | Field must have value (validation) |
| `readonly` | bool | Field is read-only in UI (not enforced in code) |
| `index` | bool/str | Create database index (`'btree'`, `'btree_not_null'`, `'trigram'`) |
| `default` | value/callable | Default value |
| `copy` | bool | Copy field on duplicate (default `True`, `False` for o2many) |
| `store` | bool | Store in database (default `True`, `False` for computed) |
| `groups` | str | Comma-separated group XML IDs for access control |
| `company_dependent` | bool | Value varies by company (stored as jsonb) |
| `help` | str | Tooltip text |
| `translate` | bool | Enable translation |
| `tracking` | bool/int | Track changes in chatter (`1`=always, `2`=only if set) |

### Index Types

```python
# Standard btree index (good for many2one, equality)
code = fields.Char(string='Code', index=True)
code = fields.Char(string='Code', index='btree')

# Btree not null (most values are NULL)
category_id = fields.Many2one('category', index='btree_not_null')

# Trigram index (full-text search)
name = fields.Char(string='Name', index='trigram')
```

### Default Value Patterns

```python
# Static default
active = fields.Boolean(default=True)

# Callable default (evaluated per record)
date = fields.Date(default=fields.Date.context_today)
datetime = fields.Datetime(default=fields.Datetime.now)

# Lambda default (can access self/env)
user_id = fields.Many2one(
    'res.users',
    string='User',
    default=lambda self: self.env.user,
)

# Company-dependent default
company_id = fields.Many2one(
    'res.company',
    string='Company',
    default=lambda self: self.env.company,
)
```

### Company Dependent Fields

```python
# Value varies by company (property field)
payment_term_id = fields.Many2one(
    'account.payment.term',
    string='Payment Terms',
    company_dependent=True,
)

# Access for specific company
record.with_context(company_id=1).payment_term_id
```

---

## Odoo 18 Field Parameters

### aggregator (Odoo 18)

**Replaces**: `group_operator` (deprecated since Odoo 18)

```python
# Odoo 18+ - use aggregator
amount = fields.Float(
    string='Amount',
    aggregator='sum',  # NEW in Odoo 18
)

# Supported aggregators (from READ_GROUP_AGGREGATE):
# - sum, avg, max, min
# - bool_and, bool_or
# - array_agg, recordset
# - count, count_distinct
```

### precompute (Odoo 18)

Compute field before record insertion.

```python
sequence = fields.Integer(
    string='Sequence',
    compute='_compute_sequence',
    precompute=True,  # Compute at form init
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

### recursive (Odoo 18)

For fields with recursive dependencies like `parent_id.X`.

```python
# Field has dependency like parent_id.X
total = fields.Float(
    string='Total',
    compute='_compute_total',
    store=True,
    recursive=True,  # Declare recursive dependency explicitly
)
```

### compute_sudo (Odoo 18)

Whether field should be recomputed as superuser.

```python
# Default: True for stored fields, False for non-stored
amount = fields.Float(
    string='Amount',
    compute='_compute_amount',
    store=True,
    compute_sudo=True,  # Compute as admin (default for stored)
)

price = fields.Float(
    string='Price',
    compute='_compute_price',
    compute_sudo=False,  # Compute as current user (default for non-stored)
)
```

### group_operator (Deprecated)

**Deprecated in Odoo 18**: Use `aggregator` instead.

```python
# OLD (deprecated)
amount = fields.Float(group_operator='sum')

# NEW (Odoo 18+)
amount = fields.Float(aggregator='sum')
```

---

## Field Type Selection Guide

| Requirement | Use Field |
|-------------|-----------|
| Short text (name, code) | `Char` |
| Long text (description) | `Text` |
| HTML content (email, web) | `Html` |
| Yes/No | `Boolean` |
| Whole number | `Integer` |
| Decimal (non-currency) | `Float` |
| Money | `Monetary` |
| Date only | `Date` |
| Date + time | `Datetime` |
| File/Attachment | `Binary` |
| Dropdown options | `Selection` |
| Many-to-one relation | `Many2one` |
| One-to-many relation | `One2many` |
| Many-to-many relation | `Many2many` |
| Derived from other fields | `compute` |
| Field from related record | `related` |
| Multi-company value | `company_dependent=True` |

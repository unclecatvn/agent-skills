# Odoo 19 Field Guide

Guide for defining fields in Odoo 19: field types, parameters, computed fields, and relational fields.

## Table of Contents
- [Field Types](#field-types)
- [Basic Fields](#basic-fields)
- [Advanced Fields](#advanced-fields)
- [Date Fields](#date-fields)
- [Relational Fields](#relational-fields)
- [Computed Fields](#computed-fields)
- [Related Fields](#related-fields)
- [Field Parameters](#field-parameters)

---

## Field Types

### Type Summary

| Category | Types |
|----------|-------|
| **Basic** | Boolean, Char, Float, Integer |
| **Advanced** | Binary, Html, Image, Monetary, Selection, Text |
| **Date** | Date, Datetime |
| **Relational** | Many2one, One2many, Many2many |
| **Pseudo** | Reference, Many2oneReference |

---

## Basic Fields

### Boolean

True/False value.

```python
active = fields.Boolean(string="Active", default=True)
is_company = fields.Boolean("Is Company")
```

### Char

String with limited length.

```python
name = fields.Char(string="Name", required=True)
code = fields.Char("Code", size=10)
```

### Float

Floating-point number.

```python
price = fields.Float(string="Price")
weight = fields.Float(digits="Stock Weight")
```

#### Digits

```python
# Using named precision
price = fields.Float(digits="Product Price")

# Custom precision (12 digits, 2 decimal)
amount = fields.Float(digits=(12, 2))
```

### Integer

Whole number.

```python
count = fields.Integer(string="Count")
priority = fields.Integer(default=10)
```

---

## Advanced Fields

### Binary

Binary data (files).

```python
file = fields.Binary(string="File")
attachment = fields.Binary("Attachment")
```

### Html

HTML content (rich text).

```python
description = fields.Html(string="Description")
notes = fields.Html("Notes", sanitize=False)
```

### Image

Enhanced Binary for images with thumbnails.

```python
image = fields.Image(string="Image")
logo = fields.Image("Logo", max_width=1024, max_height=1024)
```

### Monetary

Monetary amount with currency.

```python
amount = fields.Monetary(string="Amount", currency_field="currency_id")
```

**Requires** a currency field (default: `currency_id`).

### Selection

Selection from predefined list.

```python
state = fields.Selection([
    ('draft', 'Draft'),
    ('confirmed', 'Confirmed'),
    ('done', 'Done'),
], string="State", default='draft')

# Or using model reference
type = fields.Selection([
    ('a', 'A'),
    ('b', 'B'),
], string="Type")
```

**Dynamic selection** (from another model):

```python
type_id = fields.Many2one('my.type', string="Type")
```

### Text

Long text (unlimited).

```python
description = fields.Text(string="Description")
notes = fields.Text("Notes")
```

---

## Date Fields

### Date

Date without time.

```python
date = fields.Date(string="Date")
deadline = fields.Date(default=fields.Date.context_today)
```

#### Date Methods

```python
from odoo.fields import Date

# Today
today = Date.context_today(self)

# Add/subtract
next_week = Date.add(Date.today(), weeks=1)
last_month = Date.subtract(Date.today(), months=1)

# Start/end of period
start_of_month = Date.start_of(Date.today(), 'month')
end_of_month = Date.end_of(Date.today(), 'month')

# To string
date_str = Date.to_string(Date.today())

# From string
date_obj = Date.to_date('2023-01-01')
```

### Datetime

Date and time.

```python
datetime = fields.Datetime(string="DateTime")
create_date = fields.Datetime(default=fields.Datetime.now)
```

#### Datetime Methods

```python
from odoo.fields import Datetime

# Now
now = Datetime.now()

# Context timestamp (user timezone)
timestamp = Datetime.context_timestamp(self, datetime)

# Add/subtract
next_hour = Datetime.add(Datetime.now(), hours=1)

# Start/end of period
start_of_day = Datetime.start_of(Datetime.now(), 'day')
end_of_day = Datetime.end_of(Datetime.now(), 'day')

# Convert
date_obj = Datetime.to_datetime('2023-01-01 12:00:00')
date_str = Datetime.to_string(Datetime.now())
```

#### Timezone

Datetime fields are stored as UTC. Conversion is client-side.

---

## Relational Fields

### Many2one

Many-to-one relation (foreign key).

```python
partner_id = fields.Many2one('res.partner', string="Partner")
user_id = fields.Many2one('res.users', 'User', default=lambda self: self.env.user)
```

#### Parameters

| Parameter | Description |
|-----------|-------------|
| `comodel_name` | Related model name |
| `string` | Field label |
| `required` | Whether required |
| `ondelete` | What to do when related record is deleted (`cascade`, `set null`, `restrict`) |
| `domain` | Domain filter |
| `context` | Context for operations |
| `default` | Default value |
| `index` | Add database index |

```python
partner_id = fields.Many2one(
    'res.partner',
    string="Customer",
    required=True,
    ondelete='cascade',
    domain=[('customer_rank', '>', 0)],
    default=lambda self: self.env.partner,
)
```

### One2many

One-to-many relation (inverse of Many2one).

```python
line_ids = fields.One2many('sale.order.line', 'order_id', string="Order Lines")
```

#### Parameters

| Parameter | Description |
|-----------|-------------|
| `comodel_name` | Related model name |
| `inverse_name` | Inverse Many2one field |
| `string` | Field label |

```python
order_id = fields.Many2one('sale.order', 'Order')
line_ids = fields.One2many(
    'sale.order.line',
    'order_id',
    string="Order Lines",
)
```

### Many2many

Many-to-many relation.

```python
tag_ids = fields.Many2many('crm.tag', string="Tags")
category_ids = fields.Many2many('product.category', 'product_category_rel', 'product_id', 'category_id')
```

#### Parameters

| Parameter | Description |
|-----------|-------------|
| `comodel_name` | Related model name |
| `relation` | Relation table name (auto if not specified) |
| `column1` | Column for this model |
| `column2` | Column for related model |
| `string` | Field label |

```python
# Simple (auto relation table)
tag_ids = fields.Many2many('crm.tag', string="Tags")

# Custom relation table
product_ids = fields.Many2many(
    'product.product',
    'my_rel',
    'my_id',
    'product_id',
    string="Products",
)
```

### Commands

Use `Command` class for One2many/Many2many operations:

```python
from odoo.fields import Command

# Create
{
    'line_ids': [
        Command.create({'product_id': 1, 'qty': 10}),
        Command.create({'product_id': 2, 'qty': 5}),
    ]
}

# Update
{
    'line_ids': [
        Command.update(line_id, {'qty': 20}),
    ]
}

# Delete
{
    'line_ids': [
        Command.delete(line_id),
    ]
}

# Clear all
{
    'line_ids': [Command.clear()]
}

# Set (replace all)
{
    'line_ids': [
        Command.set([id1, id2, id3])
    ]
}

# Link (add without deleting existing)
{
    'tag_ids': [
        Command.link(tag_id),
    ]
}

# Unlink
{
    'tag_ids': [
        Command.unlink(tag_id),
    ]
}
```

---

## Computed Fields

Fields computed from other fields.

### Basic Compute

```python
total = fields.Float(compute='_compute_total')

@api.depends('price', 'qty')
def _compute_total(self):
    for record in self:
        record.total = record.price * record.qty
```

### Store and Search

```python
total = fields.Float(
    compute='_compute_total',
    store=True,
    search='_search_total',
)
```

### Inverse

Allow setting computed field:

```python
full_name = fields.Char(
    compute='_compute_full_name',
    inverse='_inverse_full_name',
)

@api.depends('first_name', 'last_name')
def _compute_full_name(self):
    for record in self:
        record.full_name = f"{record.first_name} {record.last_name}"

def _inverse_full_name(self):
    for record in self:
        parts = record.full_name.split(' ', 1)
        record.first_name = parts[0]
        record.last_name = parts[1] if len(parts) > 1 else ''
```

---

## Related Fields

Shortcut for computed fields that follow a relation.

```python
partner_name = fields.Char(related='partner_id.name', string="Partner Name")
partner_email = fields.Char(related='partner_id.email', readonly=True)
```

### Store Related

```python
partner_name = fields.Char(
    related='partner_id.name',
    string="Partner Name",
    store=True,
)
```

### Dependencies

```python
# Only recompute when partner_id changes
partner_name = fields.Char(
    related='partner_id.name',
    store=True,
    depends=['partner_id'],
)
```

---

## Field Parameters

### Common Parameters

| Parameter | Description |
|-----------|-------------|
| `string` | Field label |
| `required` | Whether required (create/write) |
| `readonly` | Whether read-only |
| `index` | Add database index |
| `default` | Default value or callable |
| `help` | Tooltip text |
| `groups` | Comma-separated group IDs |
| `copy` | Copy on duplicate (default: True) |
| `track_visibilty` | Track changes in chatter (`always`, `onchange`, `never`) |

### Examples

```python
name = fields.Char(
    string="Name",
    required=True,
    index=True,
    default='Untitled',
    help="Enter the name",
    copy=True,
    tracking=True,  # Equivalent to track_visibility='always'
)
```

---

## Reserved Field Names

| Name | Purpose |
|------|---------|
| `id` | Record identifier |
| `display_name` | Display name |
| `create_date`, `create_uid`, `write_date`, `write_uid` | Access log fields |
| `name` | Default `rec_name` |
| `active` | Global visibility toggle |
| `state` | Lifecycle stages |
| `parent_id` | Tree structure parent |
| `parent_path` | Tree structure path |
| `company_id` | Multi-company field |

---

## References

- Source: Odoo 19 documentation `/doc/developer/reference/backend/orm.rst`

---
name: odoo-18-decorator
description: Complete reference for Odoo 18 API decorators (@api.model, @api.depends, @api.constrains, @api.onchange, @api.ondelete, @api.returns) and their proper usage patterns.
globs: **/models/**/*.py
topics:
  - @api.model (model-level methods)
  - @api.depends (computed fields)
  - @api.depends_context (context-dependent computed fields)
  - @api.constrains (data validation)
  - @api.onchange (form UI updates)
  - @api.ondelete (delete validation, Odoo 18)
  - @api.returns (return type specification)
  - Decorator combinations and decision tree
when_to_use:
  - Writing computed fields
  - Implementing data validation
  - Creating form onchange handlers
  - Preventing record deletion
  - Defining model methods
---

# Odoo 18 Decorator Guide

Complete reference for Odoo 18 API decorators and their proper usage.

## Table of Contents

1. [@api.model](#api-model)
2. [@api.depends](#api-depends)
3. [@api.depends_context](#api-depends_context)
4. [@api.constrains](#api-constrains)
5. [@api.onchange](#api-onchange)
6. [@api.ondelete](#api-ondelete)
7. [@api.returns](#api-returns)

---

## @api.model

**Purpose**: Decorate methods where `self` is a recordset, but the actual records don't matter - only the model class.

```python
from odoo import api, models

class SaleOrder(models.Model):
    _name = 'sale.order'

    @api.model
    def get_default_values(self):
        """Return default values for new orders"""
        return {
            'state': 'draft',
            'date_order': fields.Datetime.now(),
        }

    @api.model
    def create_from_csv(self, csv_data):
        """Class method alternative"""
        for row in csv_data:
            self.create(row)
```

**When to use**:
- Factory methods that create records
- Methods that don't depend on `self` content
- Utility methods for the model

**Common pattern** - Default value callable:
```python
partner_id = fields.Many2one(
    'res.partner',
    default=lambda self: self.env.user.partner_id.id,
)

# Equivalent with @api.model
@api.model
def _default_partner_id(self):
    return self.env.user.partner_id.id
```

---

## @api.depends

**Purpose**: Declare dependencies for computed fields. The method is re-computed when any dependency changes.

```python
from odoo import api, fields, models

class SaleOrder(models.Model):
    _name = 'sale.order'

    amount_untaxed = fields.Float(string='Untaxed Amount')
    tax_amount = fields.Float(string='Tax Amount')
    discount_amount = fields.Float(string='Discount')

    # Basic depends
    amount_total = fields.Float(
        string='Total',
        compute='_compute_amount_total',
        store=True,
    )

    @api.depends('amount_untaxed', 'tax_amount', 'discount_amount')
    def _compute_amount_total(self):
        for order in self:
            order.amount_total = (
                order.amount_untaxed
                + order.tax_amount
                - order.discount_amount
            )
```

**Relational field dependencies**:
```python
@api.depends('partner_id.name', 'partner_id.email')
def _compute_partner_display(self):
    for order in self:
        if order.partner_id:
            order.partner_display = f"{order.partner_id.name} <{order.partner_id.email}>"
        else:
            order.partner_display = ''
```

**One2many traversal**:
```python
@api.depends('line_ids.price_subtotal')
def _compute_amount_total(self):
    for order in self:
        order.amount_total = sum(order.line_ids.mapped('price_subtotal'))
```

**Nested dependencies**:
```python
@api.depends('line_ids.product_id.list_price')
def _compute_max_price(self):
    for order in self:
        prices = order.line_ids.mapped('product_id.list_price')
        order.max_price = max(prices) if prices else 0.0
```

**Important rules**:
1. **Cannot depend on `id`** - use `depends_context('uid')` instead
2. **Must list all dependencies** - missed dependencies cause stale values
3. **Dot notation for relations** - `partner_id.name` not just `partner_id`
4. **No dotted path in @constrains** - only @api.depends supports dotted paths

---

## @api.depends_context

**Purpose**: Make computed field depend on context values. Field recomputed when context changes.

```python
from odoo import api, fields, models

class ProductProduct(models.Model):
    _name = 'product.product'

    # Price depends on pricelist in context
    price = fields.Float(
        string='Price',
        compute='_compute_price',
    )

    @api.depends_context('pricelist')
    def _compute_price(self):
        pricelist_id = self.env.context.get('pricelist')
        if pricelist_id:
            pricelist = self.env['product.pricelist'].browse(pricelist_id)
            for product in self:
                product.price = pricelist.get_product_price(product, 1.0)
        else:
            for product in self:
                product.price = product.list_price
```

**Built-in context keys**:
```python
# Company context
@api.depends_context('company')
def _compute_company_field(self):
    self.company_field = self.env.company.id

# User context
@api.depends_context('uid')
def _compute_user_field(self):
    self.user_field = self.env.user.id

# Language context
@api.depends_context('lang')
def _compute_translated_name(self):
    lang = self.env.context.get('lang', 'en_US')
    self.translated_name = self.name_with_lang(lang)

# Active test context
@api.depends_context('active_test')
def _compute_all_records(self):
    # When active_test=False, include archived records
    domain = [] if self.env.context.get('active_test') else []
    self.all_records = self.search_count(domain)
```

**Custom context keys**:
```python
@api.depends_context('show_prices')
def _compute_display_price(self):
    show_prices = self.env.context.get('show_prices', True)
    for product in self:
        product.display_price = product.price if show_prices else 0.0
```

---

## @api.constrains

**Purpose**: Validate data integrity. Raise `ValidationError` if validation fails.

```python
from odoo import api, models, ValidationError
from odoo.exceptions import ValidationError

class SaleOrder(models.Model):
    _name = 'sale.order'

    @api.constrains('date_order', 'date_validity')
    def _check_dates(self):
        for order in self:
            if order.date_validity and order.date_order > order.date_validity:
                raise ValidationError(
                    "Order date cannot be after validity date."
                )

    @api.constrains('partner_id', 'payment_term_id')
    def _check_payment_term(self):
        for order in self:
            if order.partner_id.property_payment_term_id:
                if order.payment_term_id != order.partner_id.property_payment_term_id:
                    raise ValidationError(
                        "Payment term must match partner's default."
                    )
```

**Validation with relational fields**:
```python
@api.constrains('line_ids')
def _check_lines(self):
    for order in self:
        if not order.line_ids:
            raise ValidationError("Order must have at least one line.")

        # Check for duplicate products
        products = order.line_ids.mapped('product_id')
        if len(products) != len(order.line_ids):
            raise ValidationError("Duplicate products not allowed.")
```

**Limitations**:
1. **No dotted paths** - `partner_id.name` won't work
2. **Must use simple field names** - only direct fields on the model
3. **Only triggers on included fields** - if field not in create/write, constraint won't run

**Workaround for full validation**:
```python
# Override create/write to ensure constraints always run
@api.model_create_multi
def create(self, vals_list):
    records = super().create(vals_list)
    records._check_full_validation()  # Your full constraint method
    return records
```

---

## @api.onchange

**Purpose**: Update form fields dynamically when another field changes.

```python
from odoo import api, models

class SaleOrderLine(models.Model):
    _name = 'sale.order.line'

    product_id = fields.Many2one('product.product', string='Product')
    price_unit = fields.Float(string='Unit Price')
    description = fields.Text(string='Description')

    @api.onchange('product_id')
    def _onchange_product_id(self):
        if self.product_id:
            self.price_unit = self.product_id.list_price
            self.description = self.product_id.description_sale
        else:
            self.price_unit = 0.0
            self.description = ''

    @api.onchange('product_id', 'quantity')
    def _onchange_product_quantity(self):
        if self.product_id and self.quantity:
            self.price_unit = self.product_id.get_price(quantity=self.quantity)
```

**Return warning/notification**:
```python
@api.onchange('discount')
def _onchange_discount(self):
    if self.discount > 50:
        return {
            'warning': {
                'title': "High Discount",
                'message': "Discount over 50% requires approval.",
                'type': 'notification',  # 'dialog' or 'notification'
            }
        }
```

**Update domain**:
```python
@api.onchange('partner_id')
def _onchange_partner_id(self):
    domain = {}
    if self.partner_id:
        domain['shipping_id'] = [
            ('partner_id', '=', self.partner_id.id),
            ('type', '=', 'delivery'),
        ]
    else:
        domain['shipping_id'] = []
    return {'domain': domain}
```

**Limitations**:
1. **No CRUD operations** - cannot call `create()`, `read()`, `write()`, `unlink()`
2. **Only simple field names** - dotted paths not supported
3. **Pseudo-record** - `self` is a single pseudo-record, not saved to DB

**Correct pattern**:
```python
# GOOD: Set field values
@api.onchange('partner_id')
def _onchange_partner_id(self):
    if self.partner_id:
        self.pricelist_id = self.partner_id.property_product_pricelist
        self.payment_term_id = self.partner_id.property_payment_term_id

# BAD: CRUD operations
@api.onchange('partner_id')
def _onchange_partner_id(self):
    self.env['sale.order'].create({})  # ERROR - undefined behavior
```

---

## @api.ondelete

**Purpose**: Validate before allowing record deletion. Supports module uninstallation.

```python
from odoo import api, models
from odoo.exceptions import UserError

class SaleOrder(models.Model):
    _name = 'sale.order'

    @api.ondelete(at_uninstall=False)
    def _unlink_if_not_confirmed(self):
        """Prevent deletion of confirmed orders"""
        if any(order.state == 'confirmed' for order in self):
            raise UserError(
                "Cannot delete confirmed orders. "
                "Cancel them first."
            )

    @api.ondelete(at_uninstall=False)
    def _unlink_except_draft(self):
        """Alternative naming convention"""
        if any(order.state != 'draft' for order in self):
            raise UserError("Only draft orders can be deleted.")
```

**`at_uninstall` parameter**:

| Value | Behavior |
|-------|----------|
| `False` (default) | Check runs during normal use, NOT during module uninstall |
| `True` | Check runs always, including during module uninstall |

**When to use `at_uninstall=True`**:
- System-critical data (default language, main company)
- Data that would break basic functionality if deleted

```python
# Example: Prevent deleting default language
@api.ondelete(at_uninstall=True)
def _unlink_if_default_language(self):
    if self.env.ref('base.lang_en').id in self.ids:
        raise UserError("Cannot delete the default English language.")
```

**Why not override `unlink()`?**:
- Overriding `unlink()` breaks module uninstallation
- `@api.ondelete` is smart about module lifecycle
- Prevents leftover data after uninstall

---

## @api.returns

**Purpose**: Specify the return model of a method for API compatibility.

```python
from odoo import api, models

class SaleOrder(models.Model):
    _name = 'sale.order'

    @api.returns('res.partner')
    def get_partner(self):
        """Returns partner record(s)"""
        return self.mapped('partner_id')

    @api.returns('self')
    def copy(self, default=None):
        """Returns new record(s) of same model"""
        return super().copy(default)
```

**Common usage in Odoo base**:
```python
# Many methods use @api.returns
@api.returns('mail.message', lambda value: value.id)
def message_post(self, ...):
    # Post a message, return the message
    return message
```

---

## Decorator Combination Patterns

### Computed field with search and inverse

```python
full_name = fields.Char(
    string='Full Name',
    compute='_compute_full_name',
    inverse='_inverse_full_name',
    search='_search_full_name',
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

def _search_full_name(self, operator, value):
    return ['|',
            ('first_name', operator, value),
            ('last_name', operator, value)]
```

### Model method with constrains

```python
@api.model
@api.constrains('code')
def _check_code_format(self):
    """Model method with constraint"""
    for record in self:
        if record.code and not record.code.isalnum():
            raise ValidationError("Code must be alphanumeric.")
```

---

## @api.model_create_multi (Odoo 18)

**Purpose**: Decorate batch create method. The method expects a list of dicts and can be called with either a single dict or a list.

```python
from odoo import api

@api.model_create_multi
def create(self, vals_list):
    """Batch create - receives list of vals, returns recordset"""
    # Add default values
    for vals in vals_list:
        vals.setdefault('state', 'draft')
        vals.setdefault('date', fields.Datetime.now())

    records = super().create(vals_list)

    # Post-processing
    for record in records:
        record._compute_something()

    return records

# Usage:
# record = model.create({'name': 'Test'})      # Single dict
# records = model.create([{'name': 'A'}, ...]) # List of dicts
```

**Note**: If you override `create()` without `@api.model_create_multi`, Odoo 18 will show a deprecation warning.

---

## @api.readonly

**Purpose**: Decorate a method where `self.env.cr` can be a readonly cursor.

```python
@api.readonly
def get_statistics(self):
    """This method can be called with readonly cursor"""
    self.env.cr.execute("SELECT COUNT(*) FROM my_table WHERE ...")
    return self.env.cr.fetchone()[0]
```

Use this decorator for methods that only read from database and don't need write access.

---

## @api.private

**Purpose**: Decorate a method to indicate it cannot be called using RPC.

```python
@api.private
def _internal_method(self):
    """This method cannot be called over RPC"""
    # Only callable internally from Python code
    pass
```

**Best practice**: Prefix business methods that should not be called over RPC with `_` instead of using this decorator.

---

## @api.autovacuum

**Purpose**: Decorate a method to be called by the daily vacuum cron job (model `ir.autovacuum`).

```python
@api.autovacuum
def _gc_expired_records(self):
    """Called daily to clean up old records"""
    expired_date = fields.Datetime.now() - relativedelta(days=30)
    self.search([('create_date', '<', expired_date)]).unlink()
```

**Requirements**:
- Method name must start with `_` (private)
- Use for garbage-collection-like tasks that don't deserve a specific cron job

---

## All API Decorators Reference

| Decorator | Purpose | Odoo Version |
|----------|---------|--------------|
| `@api.model` | Model-level method (self not relevant) | All |
| `@api.depends` | Computed field dependencies | All |
| `@api.depends_context` | Context dependencies | All |
| `@api.constrains` | Data validation | All |
| `@api.onchange` | Form UI updates | All |
| `@api.ondelete` | Delete validation (Odoo 18) | **18+** |
| `@api.returns` | Return type specification | All |
| `@api.model_create_multi` | Batch create | **18+** |
| `@api.readonly` | Readonly cursor | **18+** |
| `@api.private` | Non-RPC callable | **18+** |
| `@api.autovacuum` | Daily vacuum job | **18+** |

---

## Decorator Decision Tree (Updated for Odoo 18)

```
Need to define field behavior?
├── Field value comes from other fields → @api.depends
│   └── Depends on context → also @api.depends_context
│   └── Needs to be searchable → add store=True, search=...
│   └── Can be edited → add inverse=...
├── Validate data integrity → @api.constrains
│   └── Prevent deletion → @api.ondelete
├── Form UI update → @api.onchange
│
Need method behavior?
├── Doesn't depend on self records → @api.model
├── Returns specific model → @api.returns
└── Normal record method → no decorator needed
```

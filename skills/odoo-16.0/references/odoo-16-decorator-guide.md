---
name: odoo-16-decorator
description: Complete reference for Odoo 16 API decorators (@api.model, @api.model_create_multi, @api.depends, @api.depends_context, @api.constrains, @api.onchange, @api.ondelete, @api.returns, @api.autovacuum) and safe internal-helper naming patterns.
globs: "**/models/**/*.py"
topics:
  - api.model (model-level methods)
  - api.model_create_multi (batch create)
  - api.depends (computed field dependencies)
  - api.depends_context (context-dependent computes)
  - api.constrains (data validation)
  - api.onchange (form UI updates)
  - api.ondelete (delete validation)
  - api.returns (return type specification)
  - api.autovacuum (daily cleanup)
  - Internal helper naming (underscore-prefixed methods)
  - Decorator combinations and decision tree
when_to_use:
  - Writing computed fields
  - Implementing data validation
  - Creating onchange handlers
  - Preventing record deletion
  - Defining model-level methods
  - Batching create() overrides
---

# Odoo 16 Decorator Guide

Complete reference for Odoo 16 `@api` decorators, including `@api.private`, plus the usual internal-helper naming patterns.

## Table of Contents

1. [@api.model](#apimodel)
2. [@api.model_create_multi](#apimodel_create_multi)
3. [@api.depends](#apidepends)
4. [@api.depends_context](#apidepends_context)
5. [@api.constrains](#apiconstrains)
6. [@api.onchange](#apionchange)
7. [@api.ondelete](#apiondelete)
8. [@api.private and Internal Helpers](#apiprivate-and-internal-helpers)
9. [@api.returns](#apireturns)
10. [@api.autovacuum](#apiautovacuum)
11. [Combinations](#combinations)
12. [Decision Tree](#decision-tree)

---

## @api.model

Marks a method where `self` is a recordset but its contents are irrelevant — only the model (class) matters. Use it for factories, class-level helpers, or methods callable as `self.env['my.model'].method(...)`.

```python
from odoo import api, fields, models

class SaleOrder(models.Model):
    _name = 'sale.order'

    @api.model
    def default_get(self, fields_list):
        vals = super().default_get(fields_list)
        vals['team_id'] = self.env.user.team_id.id
        return vals

    @api.model
    def _default_pricelist(self):
        return self.env['product.pricelist'].search([], limit=1)

    pricelist_id = fields.Many2one(
        'product.pricelist',
        default=_default_pricelist,
    )
```

Notes:

- Over RPC, `@api.model` methods receive `self` as an empty recordset of the model.
- For a method that takes a dict and is named `create`, `@api.model` automatically falls back to `@api.model_create_single` (see `odoo/api.py:378`). Do **not** rely on that fallback — in Odoo 16 you should explicitly use `@api.model_create_multi` when overriding `create()`.

---

## @api.model_create_multi

**Required** decorator whenever you override `create()` in Odoo 16.

```python
from odoo import api, fields, models

class SaleOrder(models.Model):
    _name = 'sale.order'

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            vals.setdefault('state', 'draft')
            if not vals.get('name'):
                vals['name'] = self.env['ir.sequence'].next_by_code('sale.order')
        orders = super().create(vals_list)
        orders._post_create_hook()
        return orders
```

The decorator adapts the callsite: callers may still pass a single `dict`, which the wrapper silently converts to `[dict]` before invoking the method (see `odoo/api.py:427`). That means `create()` always receives a **list** inside the method body.

Failing to use `@api.model_create_multi` logs:

```
The model <module> is not overriding the create method in batch
```

and falls back to a slow per-record wrapper (`@api.model_create_single`) — every batched create call then loops one record at a time.

**Never** decorate `create()` with `@api.model` in Odoo 16 — it silently degrades to single-record mode with a runtime warning.

---

## @api.depends

Declares the fields whose changes should trigger recomputation of a computed field.

```python
class SaleOrder(models.Model):
    _name = 'sale.order'

    amount_untaxed = fields.Monetary()
    tax_total      = fields.Monetary()
    amount_total   = fields.Monetary(compute='_compute_amount_total', store=True)

    @api.depends('amount_untaxed', 'tax_total')
    def _compute_amount_total(self):
        for order in self:
            order.amount_total = order.amount_untaxed + order.tax_total
```

### Dotted paths (relational dependencies)

```python
@api.depends('partner_id.name', 'partner_id.email')
def _compute_partner_display(self):
    for order in self:
        order.partner_display = f"{order.partner_id.name} <{order.partner_id.email}>"
```

### One2many traversal

```python
@api.depends('order_line.price_subtotal')
def _compute_amount_untaxed(self):
    for order in self:
        order.amount_untaxed = sum(order.order_line.mapped('price_subtotal'))
```

### Dynamic dependencies

Pass a callable for dependencies that vary by model configuration:

```python
@api.depends(lambda self: (self._rec_name,) if self._rec_name else ())
def _compute_display_name(self):
    ...
```

### Rules and caveats

1. **Cannot depend on `id`** — Odoo raises `NotImplementedError("Compute method cannot depend on field 'id'.")` (see `odoo/api.py:267`).
2. **List every field** you actually read — missing dependencies cause stale cached values.
3. **Dotted paths OK** in `@api.depends` (but **not** in `@api.constrains` or `@api.onchange`).
4. **Assign to every record** in `self` — even when you only care about a subset — so the ORM does not re-call the method for the missed ones.
5. **Cycles** — add `recursive=True` on the field if the dependency path loops back (e.g. `parent_id.total`).

---

## @api.depends_context

Tells the ORM that a **non-stored** computed field's value depends on some context keys. When any of those keys change, Odoo invalidates the cached value and re-computes.

```python
class ProductProduct(models.Model):
    _inherit = 'product.product'

    price = fields.Float(compute='_compute_price')

    @api.depends_context('pricelist')
    def _compute_price(self):
        pricelist_id = self.env.context.get('pricelist')
        pricelist = self.env['product.pricelist'].browse(pricelist_id) if pricelist_id else None
        for product in self:
            product.price = (
                pricelist._get_product_price(product, 1.0) if pricelist else product.list_price
            )
```

Built-in context keys with special support (see `odoo/api.py:287`):

| Key | Meaning |
|-----|---------|
| `'company'` | Current `env.company.id` (derived from `allowed_company_ids` or the user's company) |
| `'uid'` | `(env.uid, env.su)` tuple — recomputed when the user or sudo flag changes |
| `'lang'` | `env.context['lang']` |
| `'active_test'` | Either from context, falling back to the field's configured default |
| `'bin_size'`, `'bin_size_<field>'` | Treated as booleans — any truthy value collapses to `True` |

Other keys are used as-is and must be **hashable** (lists are converted to tuples automatically).

```python
@api.depends_context('company')
def _compute_balance(self):
    for partner in self:
        partner.balance = partner._compute_balance_for_company(self.env.company)

@api.depends_context('show_cost')
def _compute_display_price(self):
    show_cost = self.env.context.get('show_cost', False)
    for product in self:
        product.display_price = product.standard_price if show_cost else product.list_price
```

Combine with `@api.depends` when the field depends on both regular fields and context:

```python
price = fields.Float(compute='_compute_price')

@api.depends('list_price')
@api.depends_context('pricelist')
def _compute_price(self):
    ...
```

---

## @api.constrains

Validates data integrity on the listed fields. Raise `ValidationError` on failure.

```python
from odoo import api, fields, models
from odoo.exceptions import ValidationError

class SaleOrder(models.Model):
    _name = 'sale.order'

    @api.constrains('date_order', 'validity_date')
    def _check_dates(self):
        for order in self:
            if order.validity_date and order.validity_date < order.date_order.date():
                raise ValidationError(_("Validity date cannot precede the order date."))

    @api.constrains('order_line')
    def _check_has_lines(self):
        for order in self:
            if not order.order_line:
                raise ValidationError(_("A confirmed order must have at least one line."))
```

### Rules (from `odoo/api.py:100`)

1. **Only simple field names.** Dotted paths (`'partner_id.name'`) are silently ignored.
2. **Triggered only when listed fields are present in `create()` / `write()`** — if the field is not in the view or not in the vals dict, the constraint is **not** evaluated.
3. Raise `ValidationError` (from `odoo.exceptions`). Using `UserError` for constraint failures is technically possible but semantically wrong.
4. A constraint can list several fields; it fires whenever **any** of them is in the write.

### Ensuring a constraint always runs

If you need an absolute invariant (e.g. "a confirmed order must have at least one line") that must be checked even when the user does not touch `order_line`, override `create()` / `write()` and call the constraint method explicitly, or re-write the field to trigger the constraint:

```python
@api.model_create_multi
def create(self, vals_list):
    records = super().create(vals_list)
    records._check_has_lines()
    return records
```

---

## @api.onchange

Runs on the **form view** when the user edits one of the listed fields. The method is invoked on a **pseudo-record**: a single record holding the unsaved form values. Field assignments are sent back to the client.

```python
class SaleOrderLine(models.Model):
    _name = 'sale.order.line'

    @api.onchange('product_id')
    def _onchange_product_id(self):
        if self.product_id:
            self.price_unit = self.product_id.list_price
            self.name       = self.product_id.display_name
            self.product_uom_id = self.product_id.uom_id
        else:
            self.price_unit = 0.0
            self.name = ''
```

### Warnings and notifications

Return a dict with a `warning` key:

```python
@api.onchange('discount')
def _onchange_discount(self):
    if self.discount and self.discount > 50:
        return {
            'warning': {
                'title': _("High Discount"),
                'message': _("Discount above 50%% requires manager approval."),
                'type': 'notification',   # 'dialog' (default) or 'notification'
            }
        }
```

### Dynamic domains

Onchange can return a `domain` dict (field name -> domain) to filter Many2one dropdowns — but the Odoo 16 recommended pattern is to use the `domain=` attribute on the field itself or a `Char` `_domain` field referenced from the view. Returning a domain from onchange is still supported but has been demoted in the code base.

### Rules (from `odoo/api.py:197`)

1. **Only simple field names.** Dotted paths are ignored.
2. **No CRUD on the pseudo-record.** Calling `create()`, `write()`, `unlink()` from inside an onchange is undefined behaviour — the record may not exist yet in the DB.
3. **A one2many / many2many field cannot modify itself via onchange** (webclient limitation, issue #2693).
4. Assign values directly (`self.field = value`) or use `self.update({'field': value})`.

### Onchange is UI only

Onchange does **not** run on server-side `create()` or `write()`. Any invariant that must hold in all cases must also be expressed as `@api.depends` / `@api.constrains`.

---

## @api.ondelete

Preferred way to reject a deletion. Runs during `unlink()`; by default **skipped** during module uninstall so the uninstaller can still drop data.

```python
from odoo import api, models
from odoo.exceptions import UserError

class SaleOrder(models.Model):
    _name = 'sale.order'

    @api.ondelete(at_uninstall=False)
    def _unlink_except_draft(self):
        if any(order.state not in ('draft', 'cancel') for order in self):
            raise UserError(_("Only draft or cancelled orders can be deleted."))
```

### Naming convention

By convention the method is named:

- `_unlink_if_<condition>` — raise when `<condition>` is true
- `_unlink_except_<allowed_state>` — raise unless records are in the allowed state

### at_uninstall

| Value | Behaviour |
|-------|-----------|
| `False` (recommended) | Runs during normal use; **skipped** when the module is being uninstalled. |
| `True` | Always runs — even during uninstall. Reserve for system-critical invariants (e.g. "the default language must not disappear"). |

```python
@api.ondelete(at_uninstall=True)
def _unlink_if_default_language(self):
    if self.env.ref('base.lang_en') in self:
        raise UserError(_("Cannot delete the default language."))
```

### Why not override unlink()?

Overriding `unlink()` for validation breaks module uninstallation: during uninstall, your check raises, the transaction rolls back, and leftover data stays in the DB. `@api.ondelete(at_uninstall=False)` is the supported way to add delete rules (available since Odoo 15).

### Multiple ondelete methods

You can decorate several methods on the same model; all of them run in declaration order.

---

## @api.private and Internal Helpers

Odoo 16 provides `@api.private` to keep a method out of RPC exposure. The
usual underscore-prefixed helper naming convention is still useful for internal
worker methods.

```python
from odoo import api, models
from odoo.exceptions import AccessError

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    @api.private
    def _refund_total(self, reason):
        self.ensure_one()
        self._post_refund(reason)
        return self.amount_total

    def action_refund_total(self, reason):
        self.ensure_one()
        if not self.env.user.has_group('sale.group_sale_manager'):
            raise AccessError(_("Only Sales Managers can refund totals."))
        return self._refund_total(reason)
```

Use `@api.private` for methods that must stay out of RPC on Odoo 16. Continue
to use underscore-prefixed names for helpers such as `_compute_*`,
`_prepare_*`, `_check_*`, and `_action_*` so the codebase stays idiomatic.

Private methods still do not secure any public entry point by themselves. If a
method should remain callable from buttons, server actions, or external
integrations, keep the public entry point non-underscored and perform access
checks there before delegating.

---

## @api.returns

Declares the model of the recordset returned by a method. Affects how the method's result is adapted when called via XML-RPC.

```python
class Partner(models.Model):
    _name = 'res.partner'

    @api.returns('self')
    def copy(self, default=None):
        return super().copy(default)

    @api.returns('res.partner')
    def get_main_contact(self):
        return self.mapped('contact_ids')[:1]
```

When the method is invoked from the Python record-style API, the result is returned as a recordset. When invoked over XML-RPC, Odoo downgrades the recordset to ids (`list[int]`) automatically.

Advanced form with `upgrade` / `downgrade` converters:

```python
@api.returns('mail.message', lambda value: value.id)
def message_post(self, **kwargs):
    ...
```

Here, when a caller uses the traditional RPC style, the message record is downgraded to its id. Inheritance is automatic: a subclass overriding `message_post` inherits the `@api.returns` declaration.

---

## @api.autovacuum

Registers a method to be run by the daily `ir.autovacuum` cron job. The method name **must** start with `_` (the decorator asserts this).

```python
from datetime import timedelta
from odoo import api, fields, models

class IrAttachment(models.Model):
    _inherit = 'ir.attachment'

    @api.autovacuum
    def _gc_orphan_attachments(self):
        threshold = fields.Datetime.now() - timedelta(days=30)
        self.search([
            ('res_model', '=', False),
            ('create_date', '<', threshold),
        ]).unlink()
```

Use this for lightweight GC tasks that would otherwise need their own `ir.cron` record. Autovacuum methods are called with `self` as an empty recordset of the model.

---

## Combinations

### Computed + stored + searchable + writable

```python
full_name = fields.Char(
    compute='_compute_full_name',
    inverse='_inverse_full_name',
    search='_search_full_name',
    store=True,
)

@api.depends('first_name', 'last_name')
def _compute_full_name(self):
    for r in self:
        r.full_name = f"{r.first_name or ''} {r.last_name or ''}".strip()

def _inverse_full_name(self):
    for r in self:
        parts = (r.full_name or '').split(' ', 1)
        r.first_name = parts[0]
        r.last_name  = parts[1] if len(parts) > 1 else ''

def _search_full_name(self, operator, value):
    return ['|', ('first_name', operator, value), ('last_name', operator, value)]
```

### @api.depends + @api.depends_context

```python
price = fields.Float(compute='_compute_price')

@api.depends('list_price')
@api.depends_context('pricelist', 'uid')
def _compute_price(self):
    ...
```

Both decorators stack: the compute is re-run when either a listed field or one of the listed context keys changes.

### @api.model with @api.constrains

`@api.constrains` is normally a record-level decorator, but you can combine it with `@api.model` when the check itself does not iterate (rarely useful):

```python
@api.model
@api.constrains('code')
def _check_code_format(self):
    for rec in self:
        if rec.code and not rec.code.isalnum():
            raise ValidationError(_("Code must be alphanumeric."))
```

### Batch create + constrains

```python
@api.model_create_multi
def create(self, vals_list):
    records = super().create(vals_list)
    records._check_business_rules()    # force invariants missing from vals
    return records
```

---

## Decision Tree

```
Defining / overriding a FIELD
├── Computed from other fields? ............ @api.depends
│   └── Also needs context?  ............... + @api.depends_context
│   └── Should be searchable? .............. store=True OR search=...
│   └── Should be writable? ................ inverse=...
│
Defining / overriding a METHOD
├── Overriding create()? ................... @api.model_create_multi (REQUIRED)
├── Model-level (self content irrelevant)? . @api.model
├── Validates integrity? ................... @api.constrains (simple field names only)
├── Form UI reaction? ...................... @api.onchange (no CRUD, no dotted paths)
├── Deletion guard? ........................ @api.ondelete(at_uninstall=False)
├── Daily cleanup job? ..................... @api.autovacuum (method must be private _)
├── Internal helper only? .................. Prefix the method with `_`
├── Returns a recordset via RPC? ........... @api.returns('model' or 'self')
└── Regular record-level method ............ no decorator
```

---

## Quick Reference

| Decorator / Pattern | Purpose | Dotted paths? | Notes |
|---------------------|---------|---------------|-------|
| `@api.model` | Method where self content is irrelevant | — | Also fallback-handles `create(single_dict)` but use `model_create_multi` instead |
| `@api.model_create_multi` | Batch-capable `create()` override | — | **Required** in v16 when overriding `create()` |
| `@api.depends(*fields)` | Compute dependencies | Yes | Cannot depend on `'id'` |
| `@api.depends_context(*keys)` | Context dependencies | — | Values must be hashable |
| `@api.constrains(*fields)` | Data validation | No | Only runs when listed fields are in vals |
| `@api.onchange(*fields)` | Form UI reaction | No | No CRUD on pseudo-record |
| `@api.ondelete(at_uninstall=False)` | Deletion guard | — | Preferred over overriding `unlink()` |
| Underscore-prefixed helper | Keep method out of RPC | — | Use `_helper_name`; there is no Odoo 16 `@api` decorator for this |
| `@api.returns(model, ...)` | Declare return-model for RPC | — | Inherited by overrides automatically |
| `@api.autovacuum` | Daily cleanup | — | Method name must start with `_` |

---

## Coding Conventions

- Name selection providers `_selection_<field>`, onchange handlers
  `_onchange_<field>`, and constraints `_check_<concern>`.
- Keep compute, inverse, and search methods adjacent to their fields; keep
  constraints and onchanges after field-related methods and before CRUD
  overrides.
- Use public `action_` methods for UI actions and `ensure_one()` when their
  contract is one record. Keep implementation helpers underscore-prefixed.

## Base Code Reference

Verify decorator semantics in:

- `/Users/unclecat/odoo/16.0/odoo/api.py` — all supported Odoo 16 `@api` decorators (`model` L369, `model_create_multi` L434, `depends` L246, `depends_context` L271, `constrains` L100, `onchange` L197, `ondelete` L138, `returns` L297, `autovacuum` L358).
- `/Users/unclecat/odoo/16.0/odoo/models.py` — `@api.model_create_multi` usage on `create()` (line 4561), recomputation engine interacting with `@api.depends`, and the `ir.autovacuum` cron target.
- `/Users/unclecat/odoo/16.0/odoo/exceptions.py` — `ValidationError`, `UserError`, `MissingError` to raise from decorated methods.

---
name: odoo-17-field
description: Complete reference for Odoo 17 field types, parameters, and when to use each. Use this guide when defining model fields, choosing field types, or configuring field parameters.
globs: "**/models/**/*.py"
topics:
  - Simple fields (Char, Text, Html, Boolean, Integer, Float, Monetary, Date, Datetime, Binary, Image, Selection, Reference)
  - Relational fields (Many2one, One2many, Many2many, Many2oneReference)
  - Json and Properties fields
  - Computed fields (compute, store, search, inverse)
  - Related fields
  - Field parameters (index, default, copy, store, groups, company_dependent, tracking, group_operator)
when_to_use:
  - Defining new model fields
  - Choosing appropriate field types
  - Configuring computed fields
  - Setting up relational fields
  - Optimizing field parameters
---

# Odoo 17 Field Guide

Complete reference for Odoo 17 field types, parameters, and when to use each.

## Table of Contents

1. [Simple Fields](#simple-fields)
2. [Relational Fields](#relational-fields)
3. [Json and Properties](#json-and-properties)
4. [Computed Fields](#computed-fields)
5. [Related Fields](#related-fields)
6. [Field Parameters](#field-parameters)
7. [Indexes](#indexes)
8. [Defaults](#defaults)
9. [Field Type Selection Guide](#field-type-selection-guide)

---

## Simple Fields

### Char - Short Text

```python
name = fields.Char(
    string='Name',
    required=True,
    size=128,            # UI hint; not enforced at DB level
    translate=True,      # per-language values stored in jsonb
    default='',
)

code = fields.Char(string='Code', index=True, copy=False)
```

Use for short free-form strings (names, references, codes). Strings stored in a `varchar` column.

### Text - Long Text

```python
description = fields.Text(string='Description', translate=True)
notes       = fields.Text(string='Notes')
```

Use for multi-line plain text. Backed by a `text` column (no length limit).

### Html - Rich Text

```python
content = fields.Html(
    string='Content',
    translate=True,
    sanitize=True,                       # default True - strip dangerous tags
    sanitize_attributes=True,
    sanitize_style=False,
    strip_style=False,
    strip_classes=False,
)
```

Use for HTML fragments (email bodies, CMS content). The sanitizer removes `<script>`, event handlers, and similar vectors by default.

### Boolean

```python
active = fields.Boolean(default=True)
is_company = fields.Boolean(string='Is a Company')
```

Stored as `boolean`. Default when unset: `False`.

### Integer

```python
sequence = fields.Integer(default=10)
priority = fields.Integer(default=0)
```

Stored as `int4`. For large counters use `Float` or dedicated columns. Note: on the `Integer` class, `group_operator = 'sum'` by default, but the framework sets it to `None` for fields named `sequence` so kanban columns don't try to sum them (see `odoo/fields.py:1442`).

### Float

```python
# Fixed digits (precision, scale)
weight = fields.Float(
    string='Weight',
    digits=(16, 3),       # total digits, decimal places
)

# Named precision from decimal.precision records
price = fields.Float(
    string='Unit Price',
    digits='Product Price',
)
```

**Always use the named precision form for domain-specific numbers** (prices, quantities) — it lets the user configure precision at `Settings > Technical > Decimal Accuracy` without code changes.

For currency amounts, use `Monetary`, not `Float`.

Helper methods (static, on `fields.Float`, backed by `odoo.tools.float_utils`):

```python
# Round to precision
rounded = fields.Float.round(value, precision_rounding=0.01)

# Check zero at precision
if fields.Float.is_zero(qty, precision_rounding=self.uom_id.rounding):
    raise UserError(_("Quantity cannot be zero."))

# Compare at precision
cmp = fields.Float.compare(a, b, precision_rounding=0.01)
# cmp < 0  -> a < b
# cmp == 0 -> equal (within precision)
# cmp > 0  -> a > b
```

Use these helpers instead of native `==` / `<` comparisons to avoid floating-point drift.

### Monetary

```python
currency_id = fields.Many2one('res.currency', required=True)

amount = fields.Monetary(
    string='Amount',
    currency_field='currency_id',     # REQUIRED: points to a res.currency m2o
)

# If you already have a company_id and want its currency:
company_id = fields.Many2one('res.company', default=lambda self: self.env.company)
company_currency_id = fields.Many2one(related='company_id.currency_id')
amount = fields.Monetary(string='Amount', currency_field='company_currency_id')
```

Monetary fields format to the currency's digits and respect its rounding. Mixing currencies in the same list view forces `Monetary` aggregates into `sum` with automatic currency awareness.

### Date

```python
date_order = fields.Date(
    string='Order Date',
    default=fields.Date.context_today,   # callable: today in user's TZ
    copy=False,
)
```

Stored as `date` (no time, no timezone). Helper API (see `odoo/fields.py:2137`):

```python
fields.Date.today()                              # date.today() (server TZ)
fields.Date.context_today(record)                # today in record.env.user TZ
fields.Date.to_date('2024-01-15')                # str -> date
fields.Date.to_string(fields.Date.today())       # date -> 'YYYY-MM-DD'

# Period math (from odoo.tools.date_utils)
fields.Date.start_of(fields.Date.today(), 'month')
fields.Date.end_of(fields.Date.today(), 'quarter')
fields.Date.add(fields.Date.today(), months=1)
fields.Date.subtract(fields.Date.today(), weeks=2)
# granularities: year, quarter, month, week, day, hour
```

### Datetime

```python
date_deadline = fields.Datetime(
    string='Deadline',
    default=fields.Datetime.now,     # UTC now at creation
)
```

Stored as `timestamp without time zone` in UTC. Displayed in the user's timezone.

Helper API (see `odoo/fields.py:2241`):

```python
fields.Datetime.now()                            # utcnow
fields.Datetime.today()                          # today @ 00:00:00 UTC
fields.Datetime.to_datetime('2024-01-15 14:30:00')
fields.Datetime.to_string(fields.Datetime.now())
fields.Datetime.context_timestamp(record, dt)    # UTC -> user TZ
fields.Datetime.start_of(fields.Datetime.now(), 'day')
fields.Datetime.add(fields.Datetime.now(), hours=1)
```

### Binary

```python
file_data = fields.Binary(
    string='File',
    attachment=True,      # default True - stored as ir.attachment, not in table
)
filename = fields.Char(string='Filename')
```

With `attachment=True` (the default), content goes into the filestore via `ir.attachment` — the model table only holds a pointer. Pair with a `Char` for the filename.

When reading Binary fields you usually want small metadata (size + mimetype), not raw bytes — use the `bin_size` context:

```python
self.env['ir.attachment'].with_context(bin_size=True).search([...])
# field value is returned as a human-readable size ("1.23 Kb") instead of bytes
```

### Image

```python
image_1920 = fields.Image(
    string='Image',
    max_width=1920,
    max_height=1920,
    verify_resolution=True,        # default True - rejects images over ~50 Mpx
)

# Resized derivatives (Odoo adds tools/views to convert on the fly)
image_512  = fields.Image(related='image_1920', max_width=512, max_height=512, store=True)
```

`Image` extends `Binary` and resizes on `create` / `write` while keeping aspect ratio. If both `max_width` and `max_height` are `0` and `verify_resolution=False`, no processing happens — use plain `Binary` instead.

`Image` fields require `_log_access=True` on the model (the default); the framework warns otherwise.

### Selection

```python
state = fields.Selection(
    [
        ('draft', 'Draft'),
        ('confirmed', 'Confirmed'),
        ('done', 'Done'),
        ('cancel', 'Cancelled'),
    ],
    string='Status',
    default='draft',
    required=True,
    tracking=True,        # available when inheriting mail.thread
)

# Dynamic selection from a method
kind = fields.Selection(selection='_selection_kind', string='Kind')

@api.model
def _selection_kind(self):
    return [(k, k.title()) for k in self._get_kinds()]
```

Selection values are stored as their **keys** in the DB (`varchar`), so never rename an existing key without a migration script.

Extend a Selection in a child module with `selection_add`:

```python
class SaleOrder(models.Model):
    _inherit = 'sale.order'

    state = fields.Selection(
        selection_add=[('locked', 'Locked')],
        ondelete={'locked': 'set default'},
    )
```

### Reference

```python
ref = fields.Reference(
    selection='_selection_target_model',
    string='Referenced Record',
)

@api.model
def _selection_target_model(self):
    return [(m.model, m.name) for m in self.env['ir.model'].search([])]
```

Stored as a `'model,id'` string — flexible but poor for indexes/joins. Prefer `Many2oneReference` when you already store the model name in a separate `Char`.

### Many2oneReference

```python
res_model = fields.Char(string='Resource Model', index=True)
res_id    = fields.Many2oneReference(
    string='Resource ID',
    model_field='res_model',   # Char that holds the target model name
    index=True,
)
```

Stored as an integer FK-less id. Much faster than `Reference` for lookups and joins. This is the pattern used by `ir.attachment`, `mail.followers`, etc.

---

## Relational Fields

### Many2one

```python
partner_id = fields.Many2one(
    comodel_name='res.partner',
    string='Customer',
    required=True,
    ondelete='restrict',      # 'cascade', 'set null', 'restrict'
    domain="[('customer_rank', '>', 0)]",
    context={'default_customer_rank': 1},
    tracking=True,
    index=True,
    check_company=True,       # pair with _check_company_auto on the model
)

# Default callable -> current user's partner
partner_id = fields.Many2one(
    'res.partner',
    default=lambda self: self.env.user.partner_id,
)

# Delegation inheritance (_inherits pattern)
partner_id = fields.Many2one('res.partner', required=True, ondelete='cascade', delegate=True)
```

`ondelete` values:

| Value | Behaviour on referenced-record deletion |
|-------|----------------------------------------|
| `'set null'` (default) | Set FK column to `NULL` |
| `'cascade'` | Delete this record as well |
| `'restrict'` | Refuse to delete the referenced record |

### One2many

```python
line_ids = fields.One2many(
    comodel_name='sale.order.line',
    inverse_name='order_id',       # REQUIRED - the Many2one on the child model
    string='Order Lines',
    copy=True,
    auto_join=False,               # True to generate SQL JOINs on search
)

# Filtered shadow O2M
active_line_ids = fields.One2many(
    'sale.order.line',
    'order_id',
    domain=[('state', '!=', 'cancel')],
    string='Active Lines',
)
```

The child model must declare the reverse `Many2one` with the same name you pass to `inverse_name`. `One2many` is virtual — no DB column lives on the parent table.

`copy=True` on `One2many` duplicates the child records when the parent is copied.

### Many2many

```python
tag_ids = fields.Many2many(
    comodel_name='res.partner.category',
    relation='sale_order_tag_rel',    # optional - DB table name
    column1='order_id',               # optional - this side's FK column
    column2='tag_id',                 # optional - comodel side's FK column
    string='Tags',
    domain=[('active', '=', True)],
)

# Minimal form - Odoo generates table & columns from the field name
category_ids = fields.Many2many('res.partner.category', string='Categories')
```

Pass `relation`, `column1`, `column2` explicitly when two `Many2many` fields target the same comodel from the same model, otherwise Odoo's auto-generated relation name will collide.

---

## Json and Properties

### Json (beta)

```python
config = fields.Json(string='Configuration')
# Stored in a jsonb column. Values are deep-copied on read.
```

Odoo 17's `Json` field is marked experimental in the source (`odoo/fields.py:3288`) — searching, indexing, and partial mutation are not supported. Treat the value as immutable: assign a fresh dict rather than mutating `record.config['x'] = 1` (the ORM will not detect the change).

### Properties

```python
class ProjectTask(models.Model):
    _name = 'project.task'

    project_id = fields.Many2one('project.project', required=True)
    user_properties = fields.Properties(
        string='Properties',
        definition='project_id.task_properties_definition',
        copy=True,
    )

class Project(models.Model):
    _name = 'project.project'

    task_properties_definition = fields.PropertiesDefinition(string='Task Properties')
```

`Properties` lets a parent record define ad-hoc sub-fields (type + default) that child records can fill in. The values are stored as `jsonb` on the child; the definition lives on the parent. Allowed property types (`Properties.ALLOWED_TYPES`): `boolean`, `integer`, `float`, `char`, `date`, `datetime`, `many2one`, `many2many`, `selection`, `tags`, `separator`.

---

## Computed Fields

### Non-stored Compute

```python
subtotal = fields.Monetary(compute='_compute_subtotal', currency_field='currency_id')

@api.depends('price_unit', 'quantity')
def _compute_subtotal(self):
    for line in self:
        line.subtotal = line.price_unit * line.quantity
```

Non-stored computed fields are evaluated on read. They **must** assign a value to every record in `self` (including when `self` is empty) — otherwise Odoo raises `CacheMiss` when the field is later accessed.

### Stored Compute

```python
amount_total = fields.Monetary(
    compute='_compute_amount_total',
    store=True,                       # persisted, searchable, indexable
    currency_field='currency_id',
)

@api.depends('line_ids.price_subtotal')
def _compute_amount_total(self):
    for order in self:
        order.amount_total = sum(order.line_ids.mapped('price_subtotal'))
```

Add `store=True` to make the field searchable/groupable and to avoid recomputation at every read. Dependencies in `@api.depends` determine when the value gets recomputed.

### Inverse (write back)

```python
full_name = fields.Char(compute='_compute_full_name', inverse='_inverse_full_name', store=True)

@api.depends('first_name', 'last_name')
def _compute_full_name(self):
    for rec in self:
        rec.full_name = f"{rec.first_name or ''} {rec.last_name or ''}".strip()

def _inverse_full_name(self):
    for rec in self:
        parts = (rec.full_name or '').split(' ', 1)
        rec.first_name = parts[0]
        rec.last_name  = parts[1] if len(parts) > 1 else ''
```

`inverse` gives a computed field write support. The method must not be decorated with `@api.depends` — it is triggered on write, not on recompute.

### search (for non-stored computes)

```python
display_ref = fields.Char(compute='_compute_display_ref', search='_search_display_ref')

def _search_display_ref(self, operator, value):
    return ['|', ('name', operator, value), ('ref', operator, value)]
```

`search=` turns a non-stored computed field into a searchable one by mapping domain clauses to real-field clauses.

### Recursive Dependencies

```python
total = fields.Float(
    compute='_compute_total',
    store=True,
    recursive=True,            # REQUIRED when the field depends on itself through a relation
)

@api.depends('child_ids.total', 'own_amount')
def _compute_total(self):
    for rec in self:
        rec.total = rec.own_amount + sum(rec.child_ids.mapped('total'))
```

Without `recursive=True`, Odoo refuses to register a self-dependent compute graph.

### precompute (compute at create time)

```python
sequence = fields.Char(
    compute='_compute_sequence',
    store=True,
    precompute=True,          # compute during create(), before INSERT
)
```

`precompute=True` avoids an extra `UPDATE` right after `INSERT`. It only makes sense on **stored, computed** fields. A warning is emitted when used on a non-computed or non-stored field. Beware that default values disable precomputation, and that precompute can slow down batches that would otherwise benefit from recompute flushing (see `odoo/fields.py:239`).

### compute_sudo

```python
amount = fields.Float(compute='_compute_amount', store=True, compute_sudo=True)
```

When `compute_sudo=True`, the compute method runs with `su=True` so it can access fields the current user cannot read. Defaults: `True` for stored computes, `False` for non-stored.

---

## Related Fields

### Basic Related

```python
partner_name = fields.Char(related='partner_id.name', readonly=True)

# Store a related field -> it becomes searchable and indexable
partner_country_id = fields.Many2one(related='partner_id.country_id', store=True, index=True)
```

Related fields are implemented as computes internally. They are read-only by default; add `readonly=False` to let users write to them (the write is forwarded to the target field).

### Multi-level Related

```python
country_code = fields.Char(
    related='partner_id.country_id.code',
    string='Country Code',
    readonly=True,
)
```

### Company-dependent Related

```python
company_id = fields.Many2one('res.company', default=lambda self: self.env.company)
company_currency_id = fields.Many2one(related='company_id.currency_id', readonly=True)
```

---

## Field Parameters

### Common Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `string` | str | capitalized field name | Label shown in UI |
| `help` | str | `None` | Tooltip |
| `required` | bool | `False` | Validation: value must be set |
| `readonly` | bool | `False` (or `True` for computed / related) | UI only; writes from code still work on stored fields |
| `default` | value or callable | `None` | Static or `lambda self: ...` |
| `copy` | bool | `True` for scalars, `False` for one2many / computed | Included by `copy()` |
| `store` | bool | `True` for scalars, `False` for computed / related | Persist to DB |
| `index` | `False` / `True` / `'btree'` / `'btree_not_null'` / `'trigram'` | `None` | Create a DB index |
| `translate` | bool or callable | `False` | Per-language storage |
| `groups` | str | `None` | CSV of group xml ids that may read/write this field |
| `company_dependent` | bool | `False` | Per-company value stored in `ir.property` |
| `compute` | str | `None` | Name of compute method |
| `inverse` | str | `None` | Name of inverse method |
| `search` | str | `None` | Name of search method for non-stored computes |
| `compute_sudo` | bool | `True` for stored computes, else `False` | Recompute as superuser |
| `precompute` | bool | `False` | Compute during `create()` (before INSERT) |
| `recursive` | bool | `False` | Declare self-referential dependency |
| `related` | str | `None` | Dotted path replacing the field's storage |
| `group_operator` | str | type-dependent (`'sum'` for numeric, `None` for sequence/many2one_reference) | Aggregator used by `read_group()` |
| `group_expand` | str | `None` | Method name used to expand empty groups |
| `tracking` | bool or int | `False` | With `mail.thread`: log field changes in chatter (`True` / `1`-`100` priority) |

### group_operator (Odoo 17)

Odoo 17 uses `group_operator=` to control how `read_group()` aggregates a field in list / pivot views. Valid values (see `READ_GROUP_AGGREGATE` in `odoo/models.py:355`):

`sum`, `avg`, `max`, `min`, `count`, `count_distinct`, `bool_and`, `bool_or`, `array_agg`.

```python
amount = fields.Float(string='Amount', group_operator='sum')   # default for numeric types

# Disable the default aggregation (useful for id-like numeric fields)
sequence = fields.Integer(string='Sequence', group_operator=None)

# Boolean aggregation
is_paid = fields.Boolean(group_operator='bool_and')
```

Note: v17 uses `group_operator=`. Later versions renamed this parameter to `aggregator=`. In v17 source code, `aggregator=` will raise a parameter-unknown error (or be silently stored as an unknown key).

### Tracking (requires mail.thread)

```python
class SaleOrder(models.Model):
    _name = 'sale.order'
    _inherit = ['mail.thread']

    state = fields.Selection([...], tracking=True)
    amount_total = fields.Monetary(tracking=20)     # priority, lower = shown first
```

`tracking` is contributed by the `mail` module; it only takes effect on models that inherit `mail.thread`.

### company_dependent

```python
property_payment_term_id = fields.Many2one(
    'account.payment.term',
    company_dependent=True,
    string='Default Payment Terms',
)
```

Company-dependent fields are not stored on the model's own table; they are kept as `ir.property` records keyed by company. Writing to them creates / updates the property for the current company. Reading them resolves to the value of the current company.

---

## Indexes

```python
code       = fields.Char(index=True)                  # equivalent to 'btree'
name       = fields.Char(index='trigram')             # full-text ilike
category_id = fields.Many2one(index='btree_not_null') # mostly NULL column
parent_path = fields.Char(index=True)                 # required by _parent_store
```

Options (from `odoo/fields.py:152`):

| Value | Meaning |
|-------|---------|
| `True` / `'btree'` | Standard B-tree index. Good for equality / many2one joins. |
| `'btree_not_null'` | B-tree that excludes `NULL`. Saves space when the column is mostly null. |
| `'trigram'` | PostgreSQL `pg_trgm` index. Required for fast `ilike '%term%'` matching. |
| `None` / `False` | No index (default). |

Indexes only apply to **stored** fields. Adding `index=True` to a non-stored computed field is a no-op.

Odoo 17 uses the `index=` field parameter as the only way to declare indexes in model code. There is no `models.Index(...)` helper (that was introduced in later versions). For composite indexes, add them in SQL within a post-init hook or via migration scripts.

---

## Defaults

```python
# Static value
active = fields.Boolean(default=True)
priority = fields.Integer(default=0)

# Callable (evaluated per record on create)
date = fields.Date(default=fields.Date.context_today)
datetime = fields.Datetime(default=fields.Datetime.now)

# Lambda reading env
user_id = fields.Many2one(
    'res.users',
    default=lambda self: self.env.user,
)
company_id = fields.Many2one(
    'res.company',
    default=lambda self: self.env.company,
)

# Method referenced by name (use @api.model on the method)
ref = fields.Char(default='_default_ref')

@api.model
def _default_ref(self):
    return self.env['ir.sequence'].next_by_code('my.model') or '/'
```

The callable signature is `default(self)` where `self` is an empty recordset of the model. It must **not** write to the database — `create()` is not reentrant from within a default.

Defaults defined in XML context (e.g. `default_partner_id` in an action's context) override the field's own `default=`.

---

## Field Type Selection Guide

| Requirement | Use |
|-------------|-----|
| Short text (name, code) | `Char` |
| Long plain text | `Text` |
| Rich text (HTML) | `Html` |
| Yes / No | `Boolean` |
| Whole number | `Integer` |
| Decimal (non-currency) | `Float` (with `digits='Named Precision'`) |
| Money | `Monetary` (+ `currency_field`) |
| Date only | `Date` |
| Date + time | `Datetime` |
| File attachment | `Binary(attachment=True)` |
| Image (with resize) | `Image` |
| Fixed list of choices | `Selection` |
| Dynamic reference (arbitrary model) | `Reference` |
| Dynamic reference (efficient, model stored separately) | `Many2oneReference` |
| Link to one record | `Many2one` |
| Link to many records (inverse side) | `One2many` (with `inverse_name`) |
| Many-to-many relation | `Many2many` |
| Ad-hoc user-defined sub-fields | `Properties` |
| Derived from other fields | `compute=...` |
| Projection of a related record's field | `related='path.to.field'` |
| Per-company value | `company_dependent=True` |

---

## Coding Conventions

- Name `Many2one` fields with `_id` and `One2many`/`Many2many` fields with
  `_ids`; do not use those suffixes for recordsets.
- Keep fields together near the model top and keep their compute, inverse,
  and search methods in the same order.
- Use `_default_<field>`, `_compute_<field>`, and `_search_<field>` for their
  corresponding helpers.

## Base Code Reference

Verify every parameter/type described here against:

- `/Users/unclecat/odoo/17.0/odoo/fields.py` — all field classes (`Field`, `Char`, `Float`, `Monetary`, `Date`, `Datetime`, `Binary`, `Image`, `Selection`, `Reference`, `Many2one`, `Many2oneReference`, `One2many`, `Many2many`, `Json`, `Properties`, `Command`).
- `/Users/unclecat/odoo/17.0/odoo/models.py` — `READ_GROUP_AGGREGATE` (line 355), `READ_GROUP_TIME_GRANULARITY` (line 345), `_check_company_auto` (line 614), `_parent_store` (line 599), `_sql_constraints` (line 593).
- `/Users/unclecat/odoo/17.0/odoo/tools/date_utils.py` — `start_of`, `end_of`, `add`, `subtract` used by `fields.Date` / `fields.Datetime`.
- `/Users/unclecat/odoo/17.0/odoo/tools/float_utils.py` — `float_round`, `float_is_zero`, `float_compare` used by `fields.Float`.

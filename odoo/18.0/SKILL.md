---
name: odoo-18
description: Complete skill guide for AI agents to write proper Odoo 18 code. This master file references detailed guides for each topic including models, fields, decorators, views, performance optimization, controllers, and development best practices. Use this skill when writing, reviewing, or refactoring Odoo 18 code to ensure proper ORM patterns, API usage, and performance optimization.
license: MIT
author: UncleCat
version: 1.0.0
---

# Odoo 18 Skill

Complete skill guide for AI agents to write proper Odoo 18 code. This master file references detailed guides for each topic.

## Quick Reference

| Topic | File | When to Use |
|-------|------|-------------|
| [Model Methods](#model-guide) | `odoo-18-model-guide.md` | Writing ORM queries, CRUD operations |
| [Field Types](#field-guide) | `odoo-18-field-guide.md` | Defining model fields |
| [API Decorators](#decorator-guide) | `odoo-18-decorator-guide.md` | Using @api decorators |
| [Views & XML](#view-guide) | `odoo-18-view-guide.md` | Writing XML views, actions, menus |
| [Performance](#performance-guide) | `odoo-18-performance-guide.md` | Optimizing queries, preventing N+1 |
| [Controllers](#controller-guide) | `odoo-18-controller-guide.md` | HTTP endpoints, routing |
| [Development](#development-guide) | `odoo-18-development-guide.md` | Manifest, reports, security, wizards |

---

## Model Guide

**File**: `odoo-18-model-guide.md`

**When to read**: Writing model methods, ORM queries, domain filters

### Quick Patterns

```python
# Search with prefetch (auto)
orders = self.search([('state', '=', 'done')])
for order in orders:
    print(order.name, order.partner_id.name)  # Partners prefetched

# search_read for dicts
data = self.search_read([('state', '=', 'done')], ['name', 'amount'])

# Batch create (Odoo 18)
records = self.create([
    {'name': f'Record {i}'}
    for i in range(100)
])
```

### Anti-Patterns to Avoid

```python
# BAD: search in loop (N+1)
for order in orders:
    payments = self.env['payment'].search([('order_id', '=', order.id)])

# GOOD: search with IN
payments = self.env['payment'].search_read(
    [('order_id', 'in', orders.ids)]
)
```

---

## Field Guide

**File**: `odoo-18-field-guide.md`

**When to read**: Defining new fields, choosing field types

### Quick Reference

```python
# Monetary (always use currency_field)
amount = fields.Monetary(currency_field='company_id.currency_id')

# Computed + stored
total = fields.Float(compute='_compute_total', store=True)

# Many2one with ondelete
partner_id = fields.Many2one('res.partner', ondelete='cascade')

# Index types
code = fields.Char(index='trigram')  # Full-text search
```

### Field Selection

| Need | Use |
|------|-----|
| Short text | `Char` |
| Long text | `Text` |
| Money | `Monetary` (with `currency_field`) |
| Dropdown | `Selection` |
| Many-to-one | `Many2one` (specify `ondelete`) |
| One-to-many | `One2many` (specify `inverse_name`) |
| Computed | `compute=` (add `store=True` if searchable) |

---

## Decorator Guide

**File**: `odoo-18-decorator-guide.md`

**When to read**: Using @api decorators, compute fields, validation

### Decision Tree

```
Need field behavior?
├── Computed from other fields → @api.depends
├── Validate data → @api.constrains
├── Prevent deletion → @api.ondelete (Odoo 18!)
├── Form UI update → @api.onchange
│
Need method behavior?
├── Model-level method → @api.model
└── Normal record method → no decorator
```

### Key Patterns

```python
# @api.depends with dotted paths (Odoo 18)
@api.depends('partner_id.email')
def _compute_email(self):
    for rec in self:
        rec.email = rec.partner_id.email

# @api.ondelete (Odoo 18 feature)
@api.ondelete(at_uninstall=False)
def _unlink_if_not_draft(self):
    if any(rec.state != 'draft' for rec in self):
        raise UserError("Cannot delete non-draft records")
```

### Important Rules

- `@api.depends`: **CAN** use dotted paths (`partner_id.name`)
- `@api.constrains`: **CANNOT** use dotted paths (only simple field names)
- `@api.onchange`: **NO CRUD operations** (no create/read/write/unlink)
- `@api.ondelete`: **Use instead of overriding unlink()** (supports uninstall)

---

## View Guide

**File**: `odoo-18-view-guide.md`

**When to read**: Writing XML views, actions, menus, QWeb templates

### View Types (Odoo 18)

```xml
<!-- LIST VIEW (not tree!) -->
<list string="Records" editable="bottom" multi_edit="1">
    <field name="name" decoration-success="state == 'done'"/>
    <field name="phone" optional="show"/>
</list>

<!-- FORM VIEW -->
<form string="Record">
    <sheet>
        <div class="oe_button_box" name="button_box">
            <button name="action_confirm" type="object" class="oe_stat_button" icon="fa-check"/>
        </div>
        <group>
            <field name="name"/>
        </group>
    </sheet>
    <div class="oe_chatter">
        <field name="message_ids"/>
    </div>
</form>

<!-- SEARCH VIEW -->
<search>
    <field name="name"/>
    <filter string="Active" name="active" domain="[('active', '=', True)]"/>
    <group expand="0" string="Group By">
        <filter string="State" context="{'group_by': 'state'}"/>
    </group>
</search>
```

### View Inheritance (XPath)

```xml
<record id="view_partner_form_inherit" model="ir.ui.view">
    <field name="inherit_id" ref="base.view_partner_form"/>
    <field name="arch" type="xml">
        <!-- Add after field -->
        <xpath expr="//field[@name='email']" position="after">
            <field name="my_field"/>
        </xpath>

        <!-- Shorthand -->
        <field name="email" position="after">
            <field name="my_field"/>
        </field>
    </field>
</record>
```

### Odoo 18 View Changes

| Change | Old | New |
|--------|-----|-----|
| List view tag | `<tree>` | `<list>` |
| Decoration | Limited | Full support (`decoration-success`, etc.) |
| Optional fields | Manual | `<field optional="show/hide"/>` |
| Multi edit | Limited | `multi_edit="1"` attribute |

---

## Performance Guide

**File**: `odoo-18-performance-guide.md`

**When to read**: Optimizing queries, fixing slow code, preventing N+1

### N+1 Prevention Checklist

```python
# ✅ GOOD: Prefetch works automatically
for order in orders:
    print(order.partner_id.name)  # Partners fetched in batch

# ❌ BAD: search in loop
for order in orders:
    partner = self.env['res.partner'].browse(order.partner_id.id)

# ❌ BAD: access without proper depends
@api.depends('partner_id')  # Missing .email
def _compute_email(self):
    for rec in self:
        rec.email = rec.partner_id.email  # N queries!
```

### Performance Constants (Odoo 18)

```python
PREFETCH_MAX = 1000      # Records prefetched per batch
INSERT_BATCH_SIZE = 100   # Batch insert size
UPDATE_BATCH_SIZE = 100   # Batch update size
```

### Optimization Patterns

```python
# Use mapped() instead of list comprehension
partner_ids = orders.mapped('partner_id.id')

# Use filtered() before operations
done_orders = orders.filtered(lambda o: o.state == 'done')

# Use search_read() for dicts
data = self.search_read(domain, ['name', 'amount'])

# Bin size for binary fields
attachments.with_context(bin_size=True).read(['datas'])

# read_group for aggregations
result = self.read_group(domain, ['amount:sum'], ['category_id'])
```

---

## Controller Guide

**File**: `odoo-18-controller-guide.md`

**When to read**: Writing HTTP endpoints, routes, web controllers

### Quick Patterns

```python
from odoo import http
from odoo.http import request

class MyController(http.Controller):

    # JSON endpoint for frontend
    @http.route('/my/data', type='json', auth='user')
    def get_data(self):
        return request.env['my.model'].search_read([], ['name'])

    # HTTP page
    @http.route('/my/page', type='http', auth='public', website=True)
    def my_page(self):
        return request.render('my_module.template', {})

    # External API (no CSRF)
    @http.route('/api/webhook', type='http', auth='none', csrf=False)
    def webhook(self):
        return "OK"
```

### Auth Types

| Auth | Behavior | Use For |
|------|----------|---------|
| `auth='user'` | Login required | Normal pages, internal APIs |
| `auth='public'` | No login, respects ACL | Website pages, public content |
| `auth='none'` | No environment, no ACL | Login page, health checks, webhooks |

---

## Common Issues & Solutions

### Issue: N+1 Queries

**Symptom**: Loop with search inside
```python
# BAD
for order in orders:
    payments = self.env['payment'].search([('order_id', '=', order.id)])
```

**Solution**: Use IN domain or read_group
```python
# GOOD
payments = self.env['payment'].search_read([('order_id', 'in', orders.ids)])
```

---

### Issue: Compute Field Not Recomputing

**Symptom**: Stale computed value

**Solution**: Check `@api.depends` includes ALL dependencies
```python
# BAD - missing dependency
@api.depends('partner_id')
def _compute_email(self):
    rec.email = rec.partner_id.email

# GOOD - full path
@api.depends('partner_id', 'partner_id.email')
def _compute_email(self):
    rec.email = rec.partner_id.email
```

---

### Issue: Constraint Not Triggering

**Symptom**: `@api.constrains` not called

**Cause**: Field not in `create()`/`write()` call

**Solution**: Override create/write if validation always needed
```python
@api.model_create_multi
def create(self, vals_list):
    records = super().create(vals_list)
    records._check_full_validation()
    return records
```

---

## File Structure

```
docs/odoo/18.0/
├── SKILL.md                       # THIS FILE - master reference
├── odoo-18-model-guide.md         # ORM, CRUD, search, domain
├── odoo-18-field-guide.md         # Field types, parameters
├── odoo-18-decorator-guide.md      # @api decorators
├── odoo-18-view-guide.md          # XML views, actions, menus, QWeb
├── odoo-18-performance-guide.md    # N+1 prevention, optimization
├── odoo-18-controller-guide.md     # HTTP, routing, controllers
└── odoo-18-development-guide.md    # Manifest, reports, security, wizards
```

---

## Development Guide

**File**: `odoo-18-development-guide.md`

**When to read**: Creating modules, manifest structure, reports, security, wizards

### Module Structure

```
my_module/
├── __init__.py
├── __manifest__.py
├── models/
│   ├── __init__.py
│   └── my_model.py
├── views/
│   └── my_model_views.xml
├── security/
│   ├── ir.model.access.csv
│   └── my_module_security.xml
├── wizard/
│   ├── __init__.py
│   └── my_wizard.py
└── report/
    └── my_report_views.xml
```

### Manifest Keys

```python
{
    'name': 'My Module',
    'version': '18.0.1.0.0',
    'depends': ['base'],
    'data': [...],
    'installable': True,
}
```

### Access Rights (CSV)

```csv
id,name,model_id:id,group_id:id,perm_read,perm_write,perm_create,perm_unlink
access_my_model_user,my.model.user,model_my_model,base.group_user,1,1,1,0
```

### Record Rules

```xml
<record id="my_model_personal" model="ir.rule">
    <field name="domain_force">[('user_id', '=', user.id)]</field>
</record>
```

### TransientModel (Wizards)

```python
class MyWizard(models.TransientModel):
    _name = 'my.wizard'

    def action_process(self):
        # Process selected records
        return {'type': 'ir.actions.client', 'tag': 'display_notification'}
```

### Reports

```xml
<record id="action_report_my_model" model="ir.actions.report">
    <field name="report_type">qweb-pdf</field>
    <field name="report_name">my_module.report_my_model</field>
    <field name="binding_model_id" ref="model_my_model"/>
</record>
```

---

## Base Code Reference (Odoo 18)

All guides are based on analysis of Odoo 18 base code:
- `/Users/unclecat/dtg/odoo/odoo/models.py` - ORM implementation
- `/Users/unclecat/dtg/odoo/odoo/fields.py` - Field types
- `/Users/unclecat/dtg/odoo/odoo/api.py` - Decorators
- `/Users/unclecat/dtg/odoo/odoo/http.py` - HTTP layer
- `/Users/unclecat/dtg/odoo/odoo/exceptions.py` - Exception types

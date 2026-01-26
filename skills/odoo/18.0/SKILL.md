---
name: odoo-18
description: Complete skill guide for AI agents to write proper Odoo 18 code. This master file references detailed guides for each topic including models, fields, decorators, views, performance optimization, controllers, and development best practices. Use this skill when writing, reviewing, or refactoring Odoo 18 code to ensure proper ORM patterns, API usage, and performance optimization.
globs: "**/*.{py,xml}"
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
| [Transactions](#transaction-guide) | `odoo-18-transaction-guide.md` | Savepoints, UniqueViolation, commit/rollback |
| [Controllers](#controller-guide) | `odoo-18-controller-guide.md` | HTTP endpoints, routing |
| [OWL Components](#owl-guide) | `odoo-18-owl-guide.md` | Building OWL UI components |
| [Migration](#migration-guide) | `odoo-18-migration-guide.md` | Upgrading modules, data migration |
| [Testing](#testing-guide) | `odoo-18-testing-guide.md` | Writing tests, mocking, assertions |
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

## Transaction Guide

**File**: `odoo-18-transaction-guide.md`

**When to read**: Handling database errors, UniqueViolation, savepoints, commit/rollback

### Quick Patterns

```python
# Savepoint for error isolation
with self.env.cr.savepoint():
    try:
        record = self.create(data)
    except psycopg2.errors.UniqueViolation:
        pass  # Transaction still valid

# Batch create with error isolation
for data in data_list:
    with self.env.cr.savepoint():
        record = self.create(data)

# Check for duplicates before creating
existing = self.search([('email', '=', email)], limit=1)
if not existing:
    record = self.create({'email': email})
```

### PostgreSQL Error Codes

| Code | Name | Odoo Handler |
|------|------|--------------|
| 23502 | NOT NULL violation | `convert_pgerror_not_null` |
| 23505 | UNIQUE violation | `convert_pgerror_unique` |
| 23514 | CHECK violation | `convert_pgerror_constraint` |
| 40001 | Serialization failure | Retry with advisory lock |
| 25P02 | InFailedSqlTransaction | Must rollback |

### Transaction State Flow

```
Normal → [Error] → Aborted → [rollback] → Normal
                    ↓
                 [commit] → ERROR! (cannot commit aborted transaction)
```

**Key Rule**: Once a transaction enters "aborted" state due to error, all subsequent commands fail until `ROLLBACK`.

### Common Issues

```python
# BAD: Continuing after UniqueViolation without cleanup
try:
    record = self.create({'email': 'duplicate@email.com'})
except psycopg2.errors.UniqueViolation:
    pass  # Transaction is now ABORTED
record = self.create({'email': 'another@email.com'})  # FAILS!

# GOOD: Use savepoint
with self.env.cr.savepoint():
    try:
        record = self.create({'email': 'duplicate@email.com'})
    except psycopg2.errors.UniqueViolation:
        pass
# This now works:
record = self.create({'email': 'another@email.com'})
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

## OWL Guide

**File**: `odoo-18-owl-guide.md`

**When to read**: Building OWL components, hooks, services for frontend UI

### Quick Patterns

```javascript
/** @odoo-module **/
import { Component, useState, onWillStart } from "@owl/swidget";

// Basic OWL Component
class MyComponent extends Component {
    static template = "my_module.MyComponent";

    setup() {
        this.state = useState({ count: 0 });
    }

    increment() {
        this.state.count++;
    }
}

// Using ORM service
setup() {
    this.orm = useService("orm");
}

async loadRecords() {
    this.records = await this.orm.searchRead(
        "my.model",
        [["active", "=", true]],
        ["name", "date"]
    );
}

// Using RPC service
setup() {
    this.rpc = useService("rpc");
}

async callMethod() {
    await this.rpc("/my/controller", { params: {...} });
}
```

### Key Services

| Service | Purpose |
|---------|---------|
| `orm` | Database operations (search, read, create, write) |
| `rpc` | Call Python controllers / HTTP routes |
| `action` | Execute ir.actions |
| `dialog` | Show modal dialogs |
| `notification` | Show toasts |
| `router` | Navigate in app |

### Component Lifecycle

```javascript
setup() {
    onWillStart(() => {
        // Before render, async OK
        return this.loadData();
    });

    onMounted(() => {
        // After DOM ready
    });

    onWillUnmount(() => {
        // Cleanup
    });
}
```

---

## Migration Guide

**File**: `odoo-18-migration-guide.md`

**When to read**: Upgrading modules, data migration, handling version changes

### Quick Patterns

```python
# Migration script (migrations/18.0.1.0/pre-migrate.py)
def migrate(cr, version):
    """Migration script for Odoo 18.0"""
    if version is None:
        return  # New installation

    # Your migration code here
    cr.execute("""
        UPDATE your_model
        SET field_name = 'new_value'
        WHERE condition = true
    """)

# With ORM
from odoo import api
env = api.Environment(cr, 1, {})
records = env['my.model'].search([])
for record in records:
    record.write({'field': 'new_value'})
```

### Migration Stages

| Stage | When Runs | Use For |
|-------|-----------|---------|
| `pre-*.py` | Before module initialization | Schema changes, raw SQL |
| `post-*.py` | After module initialization | Data migration with ORM |
| `end-*.py` | After all modules updated | Cross-module consistency |

### Module Hooks

```python
# __manifest__.py
{
    'pre_init_hook': 'pre_init_function',   # Before installation
    'post_init_hook': 'post_init_function',  # After installation
    'uninstall_hook': 'uninstall_function',  # Before uninstallation
}
```

### Version Check

```python
def migrate(cr, version):
    if version is None:
        return  # New installation

    # Version-specific migration
    if parse_version(version) < parse_version('17.0'):
        cr.execute("UPDATE model SET field = 'v16_value'")
```

---

## Testing Guide

**File**: `odoo-18-testing-guide.md`

**When to read**: Writing tests, mocking, assertions, browser testing

### Test Classes

```python
from odoo.tests import TransactionCase, HttpCase, tagged

# TransactionCase - each test in savepoint
class TestMyModel(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.record = cls.env['my.model'].create({'name': 'Test'})

    def test_basic(self):
        self.assertEqual(self.record.name, 'Test')

# HttpCase - for browser testing
@tagged('-at_install', 'post_install')
class TestMyUI(HttpCase):
    def test_browser_js(self):
        self.browser_js(
            url_path='/web',
            code="console.log('test successful')",
            ready="odoo.isReady",
            login='admin'
        )
```

### Test Decorators

```python
from odoo.tests import tagged, users, warmup

# Tag tests for selective execution
@tagged('-at_install', 'post_install', 'slow')
class TestExternalAPI(TransactionCase):
    pass

# Run test with multiple users
@users('admin', 'portal')
def test_access_rights(self):
    # Runs twice, once for each user
    pass

# Stabilize query count assertions
@warmup
def test_query_count(self):
    with self.assertQueryCount(5):
        pass
```

### Form Testing

```python
from odoo.tests import Form

def test_create_with_form(self):
    with Form(self.env['sale.order']) as f:
        f.partner_id = self.customer
        with f.order_line.new() as line:
            line.product_id = self.product
            line.product_uom_qty = 5

    order = f.save()
    self.assertTrue(order.order_line)
```

### Mocking

```python
from unittest.mock import patch

def test_external_api(self):
    with patch('requests.post') as mock_post:
        mock_post.return_value.status_code = 200
        result = self.env['my.model'].call_external_api()
        mock_post.assert_called_once()
```

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
./
├── SKILL.md                       # THIS FILE - master reference
├── odoo-18-model-guide.md         # ORM, CRUD, search, domain
├── odoo-18-field-guide.md         # Field types, parameters
├── odoo-18-decorator-guide.md      # @api decorators
├── odoo-18-view-guide.md          # XML views, actions, menus, QWeb
├── odoo-18-performance-guide.md    # N+1 prevention, optimization
├── odoo-18-transaction-guide.md   # Savepoints, UniqueViolation, commit/rollback
├── odoo-18-controller-guide.md     # HTTP, routing, controllers
├── odoo-18-owl-guide.md           # OWL components, hooks, services
├── odoo-18-migration-guide.md     # Migration scripts, upgrade hooks
├── odoo-18-testing-guide.md       # Test classes, decorators, mocking
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

All guides are based on analysis of Odoo 18 base code. To reference in your project:
- `odoo/models.py` - ORM implementation
- `odoo/fields.py` - Field types
- `odoo/api.py` - Decorators
- `odoo/http.py` - HTTP layer
- `odoo/exceptions.py` - Exception types

---

**For setup instructions with different AI IDEs, see [AGENTS.md](./AGENTS.md)**

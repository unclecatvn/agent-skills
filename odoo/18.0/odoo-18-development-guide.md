---
name: odoo-18-development
description: Complete guide for Odoo 18 module development covering manifest structure, security, reports, wizards, data files, hooks, and exception handling.
topics:
  - Module structure (folders and files)
  - __manifest__.py (all fields, assets, external dependencies)
  - Security (access rights CSV, record rules, groups)
  - Reports (qweb-pdf, qweb-html, report actions, templates)
  - Wizards & TransientModel (structure, views, multi-step)
  - Data files (records, cron jobs, server actions)
  - Hooks (post_init, pre_init, uninstall)
  - Exception handling (UserError, AccessError, ValidationError, etc.)
  - Complete module examples
when_to_use:
  - Creating new Odoo modules
  - Configuring security and access rights
  - Building reports
  - Creating wizards/transient models
  - Setting up cron jobs and server actions
  - Writing module hooks
  - Handling exceptions properly
---

# Odoo 18 Development Guide

Complete guide for Odoo 18 module development: manifest structure, reports, security, wizards, and advanced patterns.

## Table of Contents

1. [Module Structure](#module-structure)
2. [__manifest__.py](#manifestpy)
3. [Security](#security)
4. [Reports](#reports)
5. [Wizards & Transient Models](#wizards--transient-models)
6. [Data Files](#data-files)
7. [Hooks](#hooks)

---

## Module Structure

### Standard Module Structure

```
my_module/
├── __init__.py                 # Package init
├── __manifest__.py             # Module manifest (REQUIRED)
├── models/
│   ├── __init__.py
│   ├── my_model.py             # Model definitions
│   └── ir_rule.py              # Optional: security rules in Python
├── views/
│   ├── my_model_views.xml      # View definitions
│   ├── my_model_templates.xml  # QWeb templates
│   └── report_templates.xml    # Report templates
├── security/
│   ├── ir.model.access.csv     # Access rights (REQUIRED)
│   └── my_module_security.xml   # Record rules
├── data/
│   ├── my_module_data.xml      # Data records
│   └── ir_cron_data.xml        # Scheduled actions
├── demo/
│   └── my_module_demo.xml      # Demo data
├── report/
│   ├── my_report_views.xml     # Report actions
│   └── my_report_templates.xml # Report QWeb templates
├── wizard/
│   ├── __init__.py
│   ├── my_wizard.py            # TransientModel
│   └── my_wizard_views.xml     # Wizard views
├── static/
│   ├── src/
│   │   ├── js/                 # JavaScript files
│   │   ├── css/                # CSS files
│   │   └── scss/               # SCSS files
│   └── description/
│       └── icon.png            # Module icon
├── controllers/
│   ├── __init__.py
│   └── my_controller.py        # HTTP controllers
├── tests/
│   ├── __init__.py
│   └── test_my_module.py       # Test cases
└── lib/
    └── controller/
        ├── __init__.py
        └── main.py             # Alternative controller location
```

---

## __manifest__.py

### Basic Manifest

```python
#!/usr/bin/env python
# -*- coding: utf-8 -*-

{
    'name': 'My Module',
    'version': '18.0.1.0.0',
    'summary': 'Short description of module',
    'description': """
Long Description
==================
Detailed description of what the module does.
    """,
    'category': 'My Category',
    'author': 'Your Name',
    'website': 'https://www.example.com',
    'license': 'LGPL-3',

    # Dependencies
    'depends': [
        'base',
        'product',
    ],

    # Data files
    'data': [
        'security/my_module_security.xml',
        'security/ir.model.access.csv',
        'views/my_module_views.xml',
        'data/my_module_data.xml',
        'report/my_report_views.xml',
    ],

    # Demo data
    'demo': [
        'demo/my_module_demo.xml',
    ],

    # Installation
    'installable': True,
    'application': False,  # True = creates app menu
    'auto_install': False,  # True = auto-install with dependencies

    # Hooks
    'post_init_hook': 'post_init_hook',
    'uninstall_hook': 'uninstall_hook',
}
```

### Manifest Fields Reference

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `name` | str | Yes | Module name |
| `version` | str | Yes | Version (e.g., `18.0.1.0.0`) |
| `summary` | str | No | Short description (one line) |
| `description` | str | No | Long description (can be multi-line) |
| `category` | str | No | Module category |
| `author` | str | No | Author name(s) |
| `website` | str | No | Module URL |
| `license` | str | No | License (default: LGPL-3) |
| `depends` | list | Yes | Required module dependencies |
| `data` | list | No | Data files to load |
| `demo` | list | No | Demo data files |
| `assets` | dict | No | Web assets (CSS/JS) |
| `installable` | bool | Yes | Whether module can be installed |
| `application` | bool | No | Whether it's an app (shows in Apps menu) |
| `auto_install` | bool | No | Auto-install when dependencies installed |
| `post_init_hook` | str | No | Function to call after install |
| `pre_init_hook` | str | No | Function to call before install |
| `uninstall_hook` | str | No | Function to call after uninstall |
| `external_dependencies` | dict | No | Python/ binary dependencies |
| `sequence` | int | No | Installation order in Apps |
| `images` | list | No | Module screenshot URLs |
| `html` | bool | No | Whether description is HTML |

### Assets Declaration (Odoo 18)

```python
'assets': {
    # CSS Variables
    'web._assets_primary_variables': [
        'my_module/static/src/scss/variables.scss',
    ],

    # Backend assets
    'web.assets_backend': [
        'my_module/static/src/js/my_script.js',
        'my_module/static/src/css/my_style.css',
        'my_module/static/src/scss/my_style.scss',
        'my_module/static/src/xml/*.xml',  # QWeb templates
    ],

    # Frontend (website) assets
    'web.assets_frontend': [
        'my_module/static/src/js/frontend.js',
        'my_module/static/src/css/frontend.css',
    ],

    # Report assets
    'web.report_assets_common': [
        'my_module/static/src/css/report.css',
    ],

    # Test assets
    'web.assets_tests': [
        'my_module/static/tests/**/*',
    ],
}
```

### External Dependencies

```python
'external_dependencies': {
    'python': [
        'geopy',
        'openpyxl',
        'python-dateutil',
    ],
    'bin': [
        'pdftk',
        'phantomjs',
    ],
}
```

---

## Security

### Access Rights (ir.model.access.csv)

**Location**: `security/ir.model.access.csv`

```csv
id,name,model_id:id,group_id:id,perm_read,perm_write,perm_create,perm_unlink
access_my_model_user,my.model.user,model_my_model,base.group_user,1,1,1,0
access_my_model_manager,my.model.manager,model_my_model,group_my_module_manager,1,1,1,1
```

**Columns**:
- `id`: Unique XML ID for the access right
- `name`: Human-readable name
- `model_id:id`: Model (reference to `ir.model`)
- `group_id:id`: Group (reference to `res.groups`, empty = all users)
- `perm_read`: Can read (1 = yes, 0 = no)
- `perm_write`: Can write
- `perm_create`: Can create
- `perm_unlink`: Can delete

### Common Access Patterns

```csv
# Full access for managers
access_my_model_manager,my.model.manager,model_my_model,group_my_manager,1,1,1,1

# Read-only for regular users
access_my_model_user,my.model.user,model_my_model,base.group_user,1,0,0,0

# Read and write for regular users
access_my_model_user,my.model.user,model_my_model,base.group_user,1,1,1,0

# No access for portal users
# (Don't declare = no access)

# Portal access (read-only, specific domain)
access_my_model_portal,my.model.portal,model_my_model,base.group_portal,1,0,0,0
```

### Record Rules (ir.rule)

**Location**: `security/my_module_security.xml`

```xml
<?xml version="1.0" encoding="utf-8"?>
<odoo noupdate="1">

    <!-- Multi-company rule -->
    <record id="my_model_comp_rule" model="ir.rule">
        <field name="name">My Model multi-company</field>
        <field name="model_id" ref="model_my_model"/>
        <field name="domain_force">[('company_id', 'in', company_ids)]</field>
        <field name="global" eval="True"/>
    </record>

    <!-- User can only see their own records -->
    <record id="my_model_personal_rule" model="ir.rule">
        <field name="name">Personal My Records</field>
        <field name="model_id" ref="model_my_model"/>
        <field name="domain_force">[('user_id', '=', user.id)]</field>
        <field name="groups" eval="[(4, ref('base.group_user'))]"/>
    </record>

    <!-- Managers can see all records -->
    <record id="my_model_manager_rule" model="ir.rule">
        <field name="name">My Model: All Records</field>
        <field name="model_id" ref="model_my_model"/>
        <field name="domain_force">[(1, '=', 1)]</field>
        <field name="groups" eval="[(4, ref('group_my_module_manager'))]"/>
        <field name="perm_read" eval="True"/>
        <field name="perm_write" eval="True"/>
        <field name="perm_create" eval="True"/>
        <field name="perm_unlink" eval="True"/>
    </record>

    <!-- Portal access -->
    <record id="my_model_portal_rule" model="ir.rule">
        <field name="name">My Model: Portal Access</field>
        <field name="model_id" ref="model_my_model"/>
        <field name="domain_force">
            [('partner_id', 'in', user.commercial_partner_id.child_ids.ids)]
        </field>
        <field name="groups" eval="[(4, ref('base.group_portal'))]"/>
        <field name="perm_unlink" eval="False"/>
    </record>

</odoo>
```

### ir.rule Fields Reference

| Field | Description |
|-------|-------------|
| `name` | Rule description |
| `model_id` | Model (reference to `ir.model`) |
| `domain_force` | Domain expression for filtering |
| `groups` | Groups rule applies to (empty = all) |
| `perm_read` | Override read permission |
| `perm_write` | Override write permission |
| `perm_create` | Override create permission |
| `perm_unlink` | Override unlink permission |
| `global` | Apply to all users (ignores groups) |

### Rule Domain Variables

| Variable | Description |
|----------|-------------|
| `user` | Current user record |
| `uid` | Current user ID |
| `company_ids` | Allowed companies for current user |
| `company_id` | Current company |
| `context` | Current context |

### Groups Definition

```xml
<?xml version="1.0" encoding="utf-8"?>
<odoo>

    <!-- Category for module groups -->
    <record id="module_category_my_module" model="ir.module.category">
        <field name="name">My Module</field>
        <field name="description">Helps you manage your records</field>
        <field name="sequence">20</field>
    </record>

    <!-- Manager group -->
    <record id="group_my_module_manager" model="res.groups">
        <field name="name">Manager</field>
        <field name="category_id" ref="module_category_my_module"/>
        <field name="implied_ids" eval="[(4, ref('group_my_module_user'))]"/>
        <field name="comment">User can manage all records.</field>
    </record>

    <!-- User group -->
    <record id="group_my_module_user" model="res.groups">
        <field name="name">User</field>
        <field name="category_id" ref="module_category_my_module"/>
        <field name="comment">User can access own records.</field>
    </record>

</odoo>
```

### Group Inheritance

```xml
<!-- Manager implies user rights -->
<record id="group_my_module_manager" model="res.groups">
    <field name="name">Manager</field>
    <field name="implied_ids" eval="[(4, ref('group_my_module_user'))]"/>
</record>

<!-- Manager also has base group_portal -->
<record id="group_my_module_manager" model="res.groups">
    <field name="implied_ids" eval="[
        (4, ref('group_my_module_user')),
        (4, ref('base.group_portal')),
    ]"/>
</record>
```

---

## Reports

### Report Action (ir.actions.report)

```xml
<?xml version="1.0" encoding="utf-8"?>
<odoo>

    <record id="action_report_my_model" model="ir.actions.report">
        <field name="name">My Model Report</field>
        <field name="model">my.model</field>
        <field name="report_type">qweb-pdf</field>
        <field name="report_name">my_module.report_my_model</field>
        <field name="report_file">my_model_report</field>
        <field name="print_report_name">'My Model - %s' % (object.name)</field>
        <field name="binding_model_id" ref="model_my_model"/>
        <field name="binding_type">report</field>
    </record>

</odoo>
```

### Report Types

| Type | Description |
|------|-------------|
| `qweb-pdf` | PDF report (most common) |
| `qweb-html` | HTML report (viewed in browser) |
| `qweb-text` | Text report (e.g., for labels) |

### Report with Groups

```xml
<record id="action_report_my_model_confidential" model="ir.actions.report">
    <field name="name">Confidential Report</field>
    <field name="model">my.model</field>
    <field name="report_type">qweb-pdf</field>
    <field name="report_name">my_module.report_confidential</field>
    <field name="groups_id" eval="[(4, ref('group_my_module_manager'))]"/>
    <field name="binding_model_id" ref="model_my_model"/>
    <field name="binding_type">report</field>
</record>
```

### QWeb Report Template

```xml
<?xml version="1.0" encoding="utf-8"?>
<odoo>

    <!-- Main report template (called for each record) -->
    <template id="report_my_model_document">
        <t t-call="web.external_layout">
            <t t-set="doc" t-value="doc.with_context(lang=doc.partner_id.lang)"/>

            <div class="page">
                <h2 t-field="doc.name"/>
                <table class="table table-sm">
                    <tr>
                        <th>Date</th>
                        <td><span t-field="doc.date"/></td>
                    </tr>
                    <tr>
                        <th>Customer</th>
                        <td>
                            <span t-field="doc.partner_id.name"/>
                            <br/>
                            <span t-field="doc.partner_id.street"/>
                            <span t-field="doc.partner_id.city"/>,
                            <span t-field="doc.partner_id.country_id.code"/>
                        </td>
                    </tr>
                </table>

                <!-- Lines -->
                <t t-if="doc.line_ids">
                    <table class="table table-bordered">
                        <thead>
                            <tr>
                                <th>Product</th>
                                <th class="text-right">Quantity</th>
                                <th class="text-right">Price</th>
                                <th class="text-right">Total</th>
                            </tr>
                        </thead>
                        <tbody>
                            <tr t-foreach="doc.line_ids" t-as="line">
                                <td><span t-field="line.product_id.name"/></td>
                                <td class="text-right"><span t-field="line.quantity"/></td>
                                <td class="text-right"><span t-field="line.price_unit"/></td>
                                <td class="text-right"><span t-field="line.price_total"/></td>
                            </tr>
                        </tbody>
                    </table>
                </t>

                <!-- Totals -->
                <div class="row">
                    <div class="col-6 offset-6">
                        <table class="table table-sm">
                            <tr>
                                <td class="text-right"><strong>Total</strong></td>
                                <td class="text-right"><span t-field="doc.amount_total"/></td>
                            </tr>
                        </table>
                    </div>
                </div>
            </div>

            <!-- Footer note -->
            <div class="footer_note">
                <t t-if="doc.note">
                    <p t-field="doc.note"/>
                </t>
                <t t-if="doc.conditions">
                    <p t-esc="doc.conditions"/>
                </t>
            </div>
        </t>
    </template>

    <!-- Wrapper template (handles multiple records) -->
    <template id="report_my_model_raw">
        <t t-call="web.html_container">
            <t t-foreach="docs" t-as="doc">
                <t t-call="my_module.report_my_model_document" t-lang="doc.partner_id.lang"/>
            </t>
        </t>
    </template>

    <!-- Main entry point -->
    <template id="report_my_model">
        <t t-call="my_module.report_my_model_raw"/>
    </template>

</odoo>
```

### Report Layouts

Odoo provides several built-in layouts:

| Layout | Usage |
|--------|-------|
| `web.external_layout` | Standard external layout (with header/footer) |
| `web.external_layout_background` | With background styling |
| `web.external_layout_clean` | Minimal layout |
| `web.html_container` | Container without header/footer |
| `web.internal_layout` | Internal layout for backend |

### Dynamic Report Name

```xml
<field name="print_report_name">
    (object.state == 'draft' and 'Draft - %s' % (object.name))
    or 'Confirmed - %s' % (object.name)
</field>
```

---

## Wizards & Transient Models

### TransientModel Structure

```python
from odoo import models, fields, api
from odoo.exceptions import UserError

class MyWizard(models.TransientModel):
    """Wizard for processing selected records"""
    _name = 'my.wizard'
    _description = 'My Wizard'

    # Fields
    date = fields.Date(string='Date', default=fields.Date.context_today, required=True)
    reason = fields.Text(string='Reason')
    user_id = fields.Many2one('res.users', string='User', default=lambda self: self.env.user)

    # Related records (from context)
    record_ids = fields.Many2many(
        'my.model',
        'my_wizard_record_rel',
        'wizard_id',
        'record_id',
        string='Records',
    )

    @api.model
    def default_get(self, fields):
        """Set defaults from context (active_ids)"""
        res = super(MyWizard, self).default_get(fields)

        if 'record_ids' in fields and self.env.context.get('active_model') == 'my.model':
            records = self.env['my.model'].browse(self.env.context.get('active_ids', []))
            res['record_ids'] = [(6, 0, records.ids)]

        return res

    def action_process(self):
        """Process selected records"""
        self.ensure_one()

        # Process records
        for record in self.record_ids:
            record.action_done(self.date, self.reason)

        # Close wizard and show message
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'message': 'Processed {} records'.format(len(self.record_ids)),
                'type': 'success',
            }
        }

    def action_open_records(self):
        """Open processed records in list view"""
        self.ensure_one()

        return {
            'type': 'ir.actions.act_window',
            'name': 'Processed Records',
            'res_model': 'my.model',
            'domain': [('id', 'in', self.record_ids.ids)],
            'view_mode': 'list,form',
        }
```

### Wizard View

```xml
<?xml version="1.0" encoding="utf-8"?>
<odoo>

    <!-- Wizard Form View -->
    <record id="view_my_wizard_form" model="ir.ui.view">
        <field name="name">my.wizard.form</field>
        <field name="model">my.wizard</field>
        <field name="arch" type="xml">
            <form string="My Wizard">
                <field name="record_ids" invisible="1"/>
                <group>
                    <group>
                        <field name="date"/>
                    </group>
                    <group>
                        <field name="user_id"/>
                    </group>
                </group>
                <group>
                    <field name="reason" nolabel="1" placeholder="Enter reason..."/>
                </group>
                <footer>
                    <button string="Process" name="action_process" type="object" class="btn-primary"/>
                    <button string="Cancel" class="btn-secondary" special="cancel"/>
                </footer>
            </form>
        </field>
    </record>

    <!-- Wizard Action -->
    <record id="action_my_wizard" model="ir.actions.act_window">
        <field name="name">My Wizard</field>
        <field name="res_model">my.wizard</field>
        <field name="view_mode">form</field>
        <field name="view_id" ref="view_my_wizard_form"/>
        <field name="target">new</field>
    </record>

</odoo>
```

### Wizard Action from Record

```xml
<!-- Add wizard button to model form -->
<record id="view_my_model_form" model="ir.ui.view">
    <field name="name">my.model.form</field>
    <field name="model">my.model</field>
    <field name="inherit_id" ref="my_module.view_my_model_form"/>
    <field name="arch" type="xml">
        <header position="inside">
            <button string="Open Wizard" name="%(action_my_wizard)d"
                    type="action" class="btn-primary"/>
        </header>
    </field>
</record>
```

### TransientModel vs Model

| Feature | TransientModel | Model |
|---------|---------------|-------|
| Data persistence | Auto-deleted (periodic cleanup) | Persistent |
| Use for | Wizards, temporary data | Regular business data |
| Database table | Yes (temporary) | Yes (permanent) |
| Inheritance | `models.TransientModel` | `models.Model` |
| Lifecycle | ~1 day (configurable) | Forever |
| `active_id` | Works | Works |

### Multi-Step Wizard

```python
class MultiStepWizard(models.TransientModel):
    _name = 'multi.step.wizard'

    step = fields.Selection([
        ('step1', 'Step 1'),
        ('step2', 'Step 2'),
        ('step3', 'Step 3'),
    ], default='step1')

    field1 = fields.Char(string='Field 1')
    field2 = fields.Char(string='Field 2')
    field3 = fields.Char(string='Field 3')

    def action_next(self):
        if self.step == 'step1':
            self.write({'step': 'step2'})
        elif self.step == 'step2':
            self.write({'step': 'step3'})
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'multi.step.wizard',
            'res_id': self.id,
            'view_mode': 'form',
            'target': 'new',
        }
```

### Wizard with Context

```python
@api.model
def default_get(self, fields):
    res = super(MyWizard, self).default_get(fields)

    # Get active_ids from context
    active_ids = self.env.context.get('active_ids', [])
    active_model = self.env.context.get('active_model')

    if active_model and active_ids:
        res['record_ids'] = [(6, 0, active_ids)]

    # Get other context values
    res['date'] = self.env.context.get('default_date', fields.Date.today())

    return res
```

---

## Data Files

### Data Records (XML)

```xml
<?xml version="1.0" encoding="utf-8"?>
<odoo>

    <!-- Simple record -->
    <record id="my_record_1" model="my.model">
        <field name="name">Record 1</field>
        <field name="code">R001</field>
    </record>

    <!-- Record with relation -->
    <record id="my_record_2" model="my.model">
        <field name="name">Record 2</field>
        <field name="category_id" ref="my_category_1"/>
        <field name="user_id" ref="base.user_admin"/>
    </record>

    <!-- noupdate: don't update on module upgrade -->
    <record id="my_record_3" model="my.model" noupdate="1">
        <field name="name">Record 3 (Customizable)</field>
    </record>

</odoo>
```

### Cron Jobs

```xml
<?xml version="1.0" encoding="utf-8"?>
<odoo>

    <record id="cron_my_model_cleanup" model="ir.cron">
        <field name="name">Clean up old records</field>
        <field name="model_id" ref="model_my_model"/>
        <field name="state">code</field>
        <field name="code">model.cron_cleanup_old_records()</field>
        <field name="interval_number">1</field>
        <field name="interval_type">days</field>
        <field name="numbercall">-1</field>
        <field name="doall" eval="False"/>
        <field name="active" eval="True"/>
    </record>

</odoo>
```

### Server Actions

```xml
<?xml version="1.0" encoding="utf-8"?>
<odoo>

    <!-- Python code server action -->
    <record id="server_action_my_model" model="ir.actions.server">
        <field name="name">My Server Action</field>
        <field name="model_id" ref="model_my_model"/>
        <field name="state">code</field>
        <field name="code">
records.action_done()
        </field>
    </record>

    <!-- Create new record server action -->
    <record id="server_action_create" model="ir.actions.server">
        <field name="name">Create Record</field>
        <field name="model_id" ref="model_my_model"/>
        <field name="state">object_create</field>
        <field name="use_create">new</field>
        <field name="fields_lines_ids">
            <field eval="[(0, 0, {'field_id': ref('field_my_model_name'), 'value': 'New Record'})]"
                   name="fields_lines_ids"/>
        </field>
    </record>

</odoo>
```

---

## Hooks

### Post-Init Hook

```python
# In __manifest__.py:
# 'post_init_hook': 'post_init_hook',

# In your model file:
def post_init_hook(env):
    """Called after module installation"""
    # Create default records
    env['my.model'].create({
        'name': 'Default Record',
        'code': 'DEFAULT',
    })

    # Run SQL for performance
    env.cr.execute("""
        ALTER TABLE my_model ADD COLUMN IF NOT EXISTS computed_field VARCHAR;
    """)
```

### Uninstall Hook

```python
# In __manifest__.py:
# 'uninstall_hook': 'uninstall_hook',

def uninstall_hook(env):
    """Called before module uninstallation"""
    # Clean up data
    env['my.model'].search([]).unlink()

    # Drop custom columns
    env.cr.execute("""
        ALTER TABLE my_model DROP COLUMN IF EXISTS computed_field;
    """)
```

### Pre-Init Hook

```python
# In __manifest__.py:
# 'pre_init_hook': 'pre_init_hook',

def pre_init_hook(env):
    """Called before module installation"""
    # Prepare database
    env.cr.execute("""
        ALTER TABLE my_model ADD COLUMN IF NOT EXISTS new_field VARCHAR;
    """)
```

---

## Complete Module Example

### __manifest__.py

```python
#!/usr/bin/env python
# -*- coding: utf-8 -*-

{
    'name': 'My Module',
    'version': '18.0.1.0.0',
    'summary': 'My Custom Module',
    'description': """
My Module Description
====================
Detailed description.
    """,
    'author': 'Me',
    'category': 'Tools',
    'website': 'https://example.com',
    'license': 'LGPL-3',

    'depends': ['base'],

    'data': [
        'security/my_module_security.xml',
        'security/ir.model.access.csv',
        'views/my_model_views.xml',
        'views/wizard_views.xml',
        'data/my_module_data.xml',
        'report/my_report_views.xml',
    ],

    'demo': [
        'demo/my_module_demo.xml',
    ],

    'installable': True,
    'application': False,

    'assets': {
        'web.assets_backend': [
            'my_module/static/src/js/my_script.js',
        ],
    },
}
```

### models/my_model.py

```python
from odoo import models, fields, api

class MyModel(models.Model):
    _name = 'my.model'
    _description = 'My Model'
    _order = 'date desc'

    name = fields.Char(string='Name', required=True)
    date = fields.Date(string='Date', default=fields.Date.context_today)
    state = fields.Selection([
        ('draft', 'Draft'),
        ('done', 'Done'),
    ], default='draft')

    @api.model
    def action_done(self):
        self.write({'state': 'done'})
```

### security/ir.model.access.csv

```csv
id,name,model_id:id,group_id:id,perm_read,perm_write,perm_create,perm_unlink
access_my_model_user,my.model.user,model_my_model,base.group_user,1,1,1,0
access_my_model_manager,my.model.manager,model_my_model,group_my_module_manager,1,1,1,1
```

### security/my_module_security.xml

```xml
<?xml version="1.0" encoding="utf-8"?>
<odoo noupdate="1">
    <record id="group_my_module_manager" model="res.groups">
        <field name="name">Manager</field>
        <field name="implied_ids" eval="[(4, ref('base.group_user'))]"/>
    </record>
</odoo>
```

---

## Common Development Tasks

### Create Custom Action on Model

```xml
<!-- Window action -->
<record id="action_my_model" model="ir.actions.act_window">
    <field name="name">My Models</field>
    <field name="res_model">my.model</field>
    <field name="view_mode">list,form</field>
    <field name="domain">[]</field>
    <field name="context">{'search_default_draft': 1}</field>
    <field name="help" type="html">
        <p class="o_view_nocontent_smiling_face">Create your first record!</p>
    </field>
</record>
```

### Add Context Action

```xml
<!-- Action accessible from smart button -->
<record id="action_my_model_from_partner" model="ir.actions.act_window">
    <field name="name">My Models</field>
    <field name="res_model">my.model</field>
    <field name="view_mode">list,form</field>
    <field name="domain">[('partner_id', '=', active_id)]</field>
    <field name="context">{'default_partner_id': active_id}</field>
</record>

<!-- Bind to partner model -->
<record id="action_my_model_from_partner_value" model="ir.values">
    <field name="name">My Models</field>
    <field name="model_id" ref="model_my_model"/>
    <field name="binding_model_id" ref="model_res_partner"/>
</record>
```

### Add Print Button

```xml
<!-- Report action appears in Print menu -->
<record id="action_report_my_model" model="ir.actions.report">
    <field name="name">My Model Report</field>
    <field name="model">my.model</field>
    <field name="report_type">qweb-pdf</field>
    <field name="report_name">my_module.report_my_model</field>
    <field name="binding_model_id" ref="model_my_model"/>
    <field name="binding_type">report</field>
</record>
```

### Add Server Action Button

```xml
<!-- Server action -->
<record id="server_action_my_model_done" model="ir.actions.server">
    <field name="name">Mark as Done</field>
    <field name="model_id" ref="model_my_model"/>
    <field name="state">code</field>
    <field name="code">records.action_done()</field>
</record>

<!-- Bind to model -->
<record id="server_action_my_model_done_value" model="ir.values">
    <field name="name">Mark as Done</field>
    <field name="model_id" ref="model_my_model"/>
    <field name="binding_model_id" ref="model_my_model"/>
    <field name="action_id" ref="server_action_my_model_done"/>
</record>
```

### Add Context Menu Entry

```xml
<!-- Add to right-click menu -->
<act_window id="action_my_model_context"
    name="My Action"
    res_model="my.model"
    src_model="my.model"
    multi="False"
/>
```

---

## Exception Reference

### Exception Hierarchy (Odoo 18)

```
Exception
├── UserError (Base exception for client errors)
│   ├── AccessDenied (Login/password error - no traceback)
│   ├── AccessError (Access rights error)
│   ├── MissingError (Record not found / deleted)
│   ├── RedirectWarning (Warning with redirect option)
│   └── ValidationError (Constraint violation)
└── CacheMiss (Missing value in cache)
```

### UserError

**Purpose**: Generic error managed by the client. When the user tries to do something that doesn't make sense.

```python
from odoo.exceptions import UserError

def action_confirm(self):
    for order in self:
        if not order.line_ids:
            raise UserError("Cannot confirm an order without lines.")
```

### AccessDenied

**Purpose**: Login/password error. No traceback is shown.

```python
from odoo.exceptions import AccessDenied

def check_password(self, password):
    if not self.env.user._check_password(password):
        raise AccessDenied("Incorrect password")
```

### AccessError

**Purpose**: Access rights error. When user tries to access records they're not allowed to.

```python
from odoo.exceptions import AccessError

def action_delete(self):
    if not self.env.user.has_group('base.group_system'):
        raise AccessError("Only administrators can delete records.")
```

### MissingError

**Purpose**: Record not found or deleted.

```python
from odoo.exceptions import MissingError

def action_update(self):
    record = self.browse(self.id)
    if not record.exists():
        raise MissingError(_("This record has been deleted"))
```

### ValidationError

**Purpose**: Violation of Python constraints.

```python
from odoo.exceptions import ValidationError

@api.constrains('email')
def _check_email(self):
    for record in self:
        if record.email and '@' not in record.email:
            raise ValidationError("Email must contain '@'")
```

### RedirectWarning

**Purpose**: Warning with option to redirect user to another action.

```python
from odoo.exceptions import RedirectWarning

def action_check_config(self):
    if not self.company_id.payment_term_id:
        raise RedirectWarning(
            _("Please configure a default payment term"),
            action=self.env.ref('account.action_payment_term_form').id,
            button_text=_("Configure Payment Terms"),
        )
```

### CacheMiss

**Purpose**: Missing value in cache. Usually raised internally by ORM.

```python
from odoo.exceptions import CacheMiss

try:
    value = self.env.cache.get(record, field)
except CacheMiss:
    # Value not in cache, need to fetch
    value = record._fetch_field(field)
```

### Exception Usage Guidelines

| Exception | When to Use | Behavior |
|-----------|-------------|----------|
| `UserError` | Generic business logic errors | Shows modal to user |
| `AccessDenied` | Wrong login/password | No traceback, login error |
| `AccessError` | Insufficient permissions | Shows error to user |
| `MissingError` | Record deleted/not found | Shows error to user |
| `ValidationError` | Data validation fails | Shows error to user |
| `RedirectWarning` | Need to redirect user | Shows dialog with button |
| `CacheMiss` | Cache lookup (internal) | Handled by ORM |

### Import Statement

```python
from odoo.exceptions import (
    UserError,
    AccessDenied,
    AccessError,
    MissingError,
    ValidationError,
    RedirectWarning,
    CacheMiss,
)
```

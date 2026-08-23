# Odoo 19 Development Guide

## Coding Conventions

Use singular, descriptive module names and model-oriented filenames. Keep
Python, XML, JS, CSS, and SCSS concise and purpose-specific; Odoo 19 runtime
behavior and established addon style take precedence over a style-only rewrite.

Guide for developing Odoo 19 modules: creating modules, manifest, structure, and common patterns.

## Table of Contents
- [Module Structure](#module-structure)
- [Creating a Module](#creating-a-module)
- [Manifest File](#manifest-file)
- [Models](#models)
- [Views](#views)
- [Security](#security)
- [Data Files](#data-files)
- [Assets](#assets)
- [Wizards](#wizards)

---

## Module Structure

### Standard Structure

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
│   ├── my_module_groups.xml
│   └── my_model_security.xml
├── data/
│   └── my_model_data.xml
├── demo/
│   └── demo_data.xml
├── migrations/
│   └── 19.0.1.0/
│       └── post-migration.py
├── tests/
│   ├── __init__.py
│   └── test_my_model.py
├── wizard/
│   ├── __init__.py
│   └── make_my_model.py
├── controllers/
│   ├── __init__.py
│   └── my_model.py
├── static/
│   ├── src/
│   │   ├── js/
│   │   ├── xml/
│   │   └── scss/
│   └── description/
│       └── icon.png
└── report/
    ├── my_model_templates.xml
    └── my_model_reports.xml
```

---

## Creating a Module

### Step 1: Create Directory

```bash
mkdir -p my_module/models
mkdir -p my_module/views
mkdir -p my_module/security
mkdir -p my_module/static/src/js
```

### Step 2: Create __init__.py

```python
# __init__.py

from . import models
from . import controllers
```

```python
# models/__init__.py

from . import my_model
```

### Step 3: Create Model

```python
# models/my_model.py

from odoo import models, fields

class MyModel(models.Model):
    _name = 'my.model'
    _description = 'My Model'

    name = fields.Char(string="Name", required=True)
    description = fields.Text(string="Description")
    active = fields.Boolean(string="Active", default=True)
```

### Step 4: Create Manifest

```python
# __manifest__.py

{
    'name': 'My Module',
    'version': '1.0.0',
    'category': 'Tools',
    'summary': 'My awesome module',
    'description': """
        My Module
        ==========
        This module does something useful.
    """,
    'author': 'Your Name',
    'website': 'https://github.com/yourname/my_module',
    'license': 'LGPL-3',
    'depends': ['base'],
    'data': [
        'security/my_module_groups.xml',
        'security/my_model_security.xml',
        'security/ir.model.access.csv',
        'data/my_model_data.xml',
        'views/my_model_views.xml',
        'report/my_model_templates.xml',
        'report/my_model_reports.xml',
        'views/my_module_menus.xml',
    ],
    'demo': [
        'demo/demo_data.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'my_module/static/src/js/my_script.js',
        ],
    },
    'installable': True,
    'application': False,
}
```

---

## Manifest File

### Required Fields

```python
{
    'name': 'My Module',      # Required
    'version': '1.0',          # Optional
    'depends': ['base'],       # Optional but recommended
}
```

### Common Fields

```python
{
    # Information
    'name': 'My Module',
    'version': '1.0.0',
    'category': 'Tools',
    'summary': 'Short description',
    'description': 'Long description',
    'author': 'Author Name',
    'website': 'https://example.com',
    'license': 'LGPL-3',

    # Dependencies
    'depends': ['base', 'web'],
    'data': ['views/views.xml'],
    'demo': ['demo/demo.xml'],

    # Assets
    'assets': {
        'web.assets_backend': [
            'my_module/static/src/js/file.js',
        ],
    },

    # Other
    'application': False,
    'installable': True,
    'auto_install': False,
}
```

---

## Models

### Basic Model

```python
from odoo import models, fields

class MyModel(models.Model):
    _name = 'my.model'
    _description = 'My Model'
    _order = 'name'

    name = fields.Char(string="Name", required=True)
    code = fields.Char(string="Code")
    description = fields.Text(string="Description")
    active = fields.Boolean(string="Active", default=True)
```

### Model Inheritance (Extension)

```python
class Partner(models.Model):
    _inherit = 'res.partner'

    my_field = fields.Char(string="My Field")
```

### Model Inheritance (Prototype)

```python
class NewModel(models.Model):
    _name = 'new.model'
    _inherit = 'base.model'

    # Inherits all fields and methods from base.model
    my_field = fields.Char(string="My Field")
```

---

## Views

### Create Views

```xml
<?xml version="1.0" encoding="UTF-8"?>
<odoo>
    <!-- List View -->
    <record id="my_model_view_list" model="ir.ui.view">
        <field name="name">my.model.list</field>
        <field name="model">my.model</field>
        <field name="arch" type="xml">
            <list string="My Models">
                <field name="name"/>
                <field name="code"/>
                <field name="active"/>
            </list>
        </field>
    </record>

    <!-- Form View -->
    <record id="view_my_model_form" model="ir.ui.view">
        <field name="name">my.model.form</field>
        <field name="model">my.model</field>
        <field name="arch" type="xml">
            <form string="My Model">
                <sheet>
                    <group>
                        <group>
                            <field name="name"/>
                            <field name="code"/>
                        </group>
                        <group>
                            <field name="active"/>
                        </group>
                    </group>
                    <notebook>
                        <page string="Description">
                            <field name="description"/>
                        </page>
                    </notebook>
                </sheet>
            </form>
        </field>
    </record>

    <!-- Search View -->
    <record id="view_my_model_search" model="ir.ui.view">
        <field name="name">my.model.search</field>
        <field name="model">my.model</field>
        <field name="arch" type="xml">
            <search string="Search My Models">
                <field name="name"/>
                <field name="code"/>
                <filter string="Active" name="active" domain="[('active','=',True)]"/>
            </search>
        </field>
    </record>

    <!-- Action -->
    <record id="action_my_model" model="ir.actions.act_window">
        <field name="name">My Models</field>
        <field name="res_model">my.model</field>
        <field name="view_mode">list,form</field>
        <field name="help" type="html">
            <p class="o_view_nocontent_smiling_face">
                Create your first my.model!
            </p>
        </field>
    </record>

    <!-- Menu -->
    <menuitem id="menu_my_model_root" name="My Module" web_icon="my_module,static/description/icon.png"/>
    <menuitem id="menu_my_model" name="My Models" parent="menu_my_model_root" action="action_my_model"/>
</odoo>
```

---

## Security

### Access Rights (CSV)

File: `security/ir.model.access.csv`

```csv
id,name,model_id:id,group_id:id,perm_read,perm_write,perm_create,perm_unlink
access_my_model_user,my.model.user,model_my_model,base.group_user,1,1,1,0
access_my_model_manager,my.model.manager,model_my_model,group_my_module_manager,1,1,1,1
```

### Record Rules (XML)

```xml
<odoo>
    <data noupdate="1">
        <!-- User can only see their own records -->
        <record id="my_model_user_rule" model="ir.rule">
            <field name="name">My Model: user can see own records</field>
            <field name="model_id" ref="model_my_model"/>
            <field name="domain_force">[('create_uid', '=', user.id)]</field>
            <field name="groups" eval="[(4, ref('base.group_user'))]"/>
            <field name="perm_read" eval="True"/>
            <field name="perm_write" eval="True"/>
            <field name="perm_create" eval="True"/>
            <field name="perm_unlink" eval="True"/>
        </record>

        <!-- Manager can see all -->
        <record id="my_model_manager_rule" model="ir.rule">
            <field name="name">My Model: manager sees all</field>
            <field name="model_id" ref="model_my_model"/>
            <field name="domain_force">[(1, '=', 1)]</field>
            <field name="groups" eval="[(4, ref('group_my_module_manager'))]"/>
        </record>
    </data>
</odoo>
```

---

## Data Files

### Create Records

```xml
<odoo>
    <record id="my_model_1" model="my.model">
        <field name="name">Record 1</field>
        <field name="code">R001</field>
    </record>

    <record id="my_model_2" model="my.model">
        <field name="name">Record 2</field>
        <field name="code">R002</field>
    </record>
</odoo>
```

### noupdate Flag

```xml
<odoo>
    <data noupdate="1">
        <!-- Only loaded on install -->
        <record id="demo_data" model="my.model">
            <field name="name">Demo</field>
        </record>
    </data>

    <!-- Loaded on install and update -->
    <record id="core_data" model="my.model">
        <field name="name">Core</field>
    </record>
</odoo>
```

---

## Assets

### JavaScript, CSS, and SCSS Conventions

- Put addon source in `static/src/js`, `static/src/scss`, and `static/src/css`;
  reserve `static/lib` for bundled third-party code.
- Use one component or concern per file, explicit imports/exports, and Odoo's
  module conventions. Do not load remote third-party assets from a manifest.
- Prefer SCSS for themed styles. Scope selectors beneath a module/component
  class, use variables and nesting sparingly, and avoid `!important`.
- Keep CSS/SCSS presentation-only and put behavior in JS; list assets in the
  appropriate bundle in dependency order.

### JavaScript

```python
'assets': {
    'web.assets_backend': [
        'my_module/static/src/js/my_widget.js',
        'my_module/static/src/js/my_view.js',
    ],
    'web.assets_frontend': [
        'my_module/static/src/js/frontend.js',
    ],
},
```

### CSS/SCSS

```python
'assets': {
    'web.assets_backend': [
        'my_module/static/src/scss/my_style.scss',
    ],
    'web.assets_frontend': [
        'my_module/static/src/scss/frontend.scss',
    ],
},
```

---

## Wizards

### TransientModel

```python
from odoo import models, fields

class MyModelMake(models.TransientModel):
    _name = 'my.model.make'
    _description = 'Make My Model'

    date = fields.Date(string="Date", required=True, default=fields.Date.context_today)
    note = fields.Text(string="Note")

    def action_confirm(self):
        # Do something
        return {'type': 'ir.actions.act_window_close'}
```

### Wizard View

```xml
<record id="view_my_model_make_form" model="ir.ui.view">
    <field name="name">my.model.make.form</field>
    <field name="model">my.model.make</field>
    <field name="arch" type="xml">
        <form string="Make My Model">
            <group>
                <field name="date"/>
                <field name="note"/>
            </group>
            <footer>
                <button name="action_confirm" string="Confirm" type="object" class="btn-primary"/>
                <button string="Cancel" class="btn-secondary" special="cancel"/>
            </footer>
        </form>
    </field>
</record>
```

### Action to Open Wizard

```python
def action_open_wizard(self):
    return {
        'type': 'ir.actions.act_window',
        'name': 'Make My Model',
        'res_model': 'my.model.make',
        'view_mode': 'form',
        'target': 'new',
        'context': {
            'default_date': fields.Date.context_today(self),
        }
    }
```

---

## Common Patterns

### State Field

```python
state = fields.Selection([
    ('draft', 'Draft'),
    'confirmed', 'Confirmed'),
    ('done', 'Done'),
], string='State', default='draft', tracking=True)
```

### Create Default from Context

```python
def default_get(self, fields_list):
    defaults = super().default_get(fields_list)
    if 'field' in fields_list:
        defaults['field'] = self.env.context.get('default_field', 'default')
    return defaults
```

### Name Search

```python
def name_search(self, name='', args=None, operator='ilike', limit=100):
    args = args or []
    if name:
        args = [('name', operator, name)] + args
    return super().name_search(name, args, operator, limit)
```

---

## References

- Based on Odoo 19 best practices

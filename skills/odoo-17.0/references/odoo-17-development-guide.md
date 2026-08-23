---
name: odoo-17-development
description: Overview guide for authoring Odoo 17 modules — directory structure, __init__.py patterns, wizards (TransientModel), report declarations, security files, asset bundles, i18n/.pot, static assets, and JavaScript/CSS/SCSS conventions.
globs: "**/*.{py,xml,csv,js,css,scss}"
topics:
  - Standard Odoo 17 module directory structure
  - __init__.py patterns (root, models/, wizard/, controllers/)
  - Wizards with models.TransientModel
  - Report declaration (actions + QWeb templates)
  - Security files in `data` (order matters)
  - Asset bundles available in Odoo 17
  - i18n folder with .pot template + locale .po files
  - Static assets layout (description/icon.png, src/, lib/)
  - JavaScript and CSS/SCSS conventions
when_to_use:
  - Scaffolding a new Odoo 17 module
  - Adding a wizard, report, or controllers subpackage
  - Setting up translations for a module
  - Deciding where an asset/file belongs
  - Authoring or reviewing JavaScript, CSS, or SCSS assets
---

# Odoo 17 Development Guide

Module creation overview for Odoo 17: directory structure, `__init__.py`
patterns, wizards, reports, security, asset bundles, i18n, static assets, and
JavaScript/CSS/SCSS conventions.
For the full `__manifest__.py` reference see
[`odoo-17-manifest-guide.md`](./odoo-17-manifest-guide.md). For migration
scripts see [`odoo-17-migration-guide.md`](./odoo-17-migration-guide.md).

## Table of Contents

1. [Module Structure](#module-structure)
2. [`__init__.py` Patterns](#__init__py-patterns)
3. [`__manifest__.py` (quick)](#__manifest__py-quick)
4. [Security Declaration](#security-declaration)
5. [Reports](#reports)
6. [Wizards & `TransientModel`](#wizards--transientmodel)
7. [Data Files](#data-files)
8. [Asset Bundles](#asset-bundles)
9. [Static Assets Layout](#static-assets-layout)
10. [i18n Folder (.pot + locale .po)](#i18n-folder-pot--locale-po)
11. [Complete Module Skeleton](#complete-module-skeleton)
12. [Base Code Reference](#base-code-reference)

---

## Module Structure

Standard Odoo 17 module skeleton:

```
my_module/
├── __init__.py                      # Python package init (imports submodules)
├── __manifest__.py                  # Module manifest (REQUIRED)
│
├── models/
│   ├── __init__.py
│   ├── my_model.py                  # models.Model subclasses
│   └── res_partner.py               # inherits / extensions
│
├── wizard/
│   ├── __init__.py
│   ├── make_my_model.py             # models.TransientModel subclasses
│   └── make_my_model_views.xml
│
├── controllers/
│   ├── __init__.py
│   ├── my_module.py                 # http.Controller subclasses
│   └── portal.py                     # inherited portal controller, if needed
│
├── views/
│   ├── my_model_views.xml
│   ├── my_model_templates.xml       # QWeb website templates
│   └── my_module_menus.xml
│
├── security/
│   ├── my_module_groups.xml         # res.groups, categories
│   ├── my_model_security.xml        # ir.rule record rules
│   └── ir.model.access.csv          # Model-level ACL
│
├── data/
│   ├── ir_sequence_data.xml
│   ├── ir_cron_data.xml
│   ├── mail_template_data.xml
│   └── my_model_data.xml             # reference data for the main model
│
├── demo/
│   └── my_module_demo.xml
│
├── report/
│   ├── my_model_reports.xml         # ir.actions.report and paper formats
│   └── my_model_templates.xml       # QWeb templates
│
├── migrations/
│   └── 17.0.1.0.0/
│       ├── pre-migrate.py
│       ├── post-migrate.py
│       └── end-migrate.py
│
├── i18n/
│   ├── my_module.pot                # Translation template (REQUIRED)
│   ├── vi.po                        # Vietnamese
│   └── fr.po                        # Optional additional locales
│
├── static/
│   ├── description/
│   │   ├── icon.png                 # Shown in Apps list
│   │   └── index.html               # Optional marketing page
│   ├── lib/
│   │   └── vendor_library/           # Bundled third-party browser library
│   └── src/
│       ├── js/
│       │   └── my_component.js
│       ├── xml/
│       │   └── my_component.xml     # OWL templates
│       ├── scss/
│       │   └── my_component.scss
│       └── img/
│           └── logo.svg
│
└── tests/
    ├── __init__.py
    └── test_my_model.py
```

Optional subfolders:

- `lib/` — bundled third-party Python modules (avoid; prefer
  `external_dependencies`).
- `populate/` — `populate` CLI data generators.
- `report/` / `reports/` — both names work; pick one and be consistent.

### Coding Conventions

- Prefer a community module prefix such as `company_feature` to avoid naming
  collisions. Use lowercase filenames containing only `[a-z0-9_]`.
- Split model logic by main model and keep inherited-model extensions in
  separate files. Name controller files after their module or inherited module;
  `main.py` is legacy for new code.
- Name transient files `<action>.py` and `<action>_views.xml`; use
  `<model>_views.xml`, `<module>_menus.xml`, `<model>_data.xml`, and
  `<model>_demo.xml` for focused XML files.
- Keep third-party browser libraries under `static/lib/<library>/`; bundle
  assets instead of linking remote images or libraries. Use directories `755`
  and files `644` for deployment.

---

## `__init__.py` Patterns

### Module root `__init__.py`

```python
# my_module/__init__.py
from . import controllers
from . import models
from . import wizard

# Hooks referenced from __manifest__.py — all three take `env` in Odoo 17.

def pre_init_hook(env):
    """Runs before install (fresh installs only)."""
    pass


def post_init_hook(env):
    """Runs after install (fresh installs only). `env` is a full Environment."""
    env['ir.config_parameter'].sudo().set_param('my_module.enabled', 'True')


def uninstall_hook(env):
    """Runs when the module is removed."""
    env['ir.config_parameter'].sudo().search([
        ('key', '=like', 'my_module.%')
    ]).unlink()


def post_load():
    """Runs once per server process when the Python module is imported.
       No arguments, no database access guaranteed."""
    pass
```

### `models/__init__.py`

```python
# my_module/models/__init__.py
from . import my_model
from . import res_partner
```

Each file inside `models/` defines one or more classes inheriting from
`models.Model` (or `models.AbstractModel`).

### `wizard/__init__.py`

```python
# my_module/wizard/__init__.py
from . import make_my_model
```

### `controllers/__init__.py`

```python
# my_module/controllers/__init__.py
from . import my_module
from . import portal
```

### `tests/__init__.py`

```python
# my_module/tests/__init__.py
from . import test_my_model
```

Tests are only auto-loaded when `--test-enable` is active.

---

## `__manifest__.py` (quick)

For the full reference, see `odoo-17-manifest-guide.md`. Minimum viable
manifest:

```python
# my_module/__manifest__.py
{
    'name': 'My Module',
    'version': '17.0.1.0.0',
    'summary': 'Short description',
    'author': 'UncleCat',
    'license': 'LGPL-3',
    'category': 'Tools',
    'depends': ['base'],
    'data': [
        'security/my_module_groups.xml',
        'security/ir.model.access.csv',
        'views/my_model_views.xml',
        'views/my_module_menus.xml',
    ],
    'demo': [
        'demo/my_module_demo.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
```

**Ordering in `data`:** security first → reference data → wizards → views →
reports → menus last. Menus reference actions, so actions must be loaded
before them.

---

## Security Declaration

Security files must be listed in `data` **first**, because every view that
references a group or a model needs those records to already exist.

### Files

```
security/
├── my_module_groups.xml       # res.groups records
├── my_model_security.xml       # Record rules
└── ir.model.access.csv        # Model-level access control
```

### Manifest entry (order)

```python
'data': [
    'security/my_module_groups.xml',     # groups first (rules reference them)
    'security/my_model_security.xml',    # then rules
    'security/ir.model.access.csv',      # then ACL
    # ...views, reports, menus...
],
```

### `ir.model.access.csv`

```csv
id,name,model_id:id,group_id:id,perm_read,perm_write,perm_create,perm_unlink
access_my_model_user,my.model user,model_my_model,base.group_user,1,1,1,0
access_my_model_manager,my.model manager,model_my_model,my_module.group_my_module_manager,1,1,1,1
```

- `model_id:id` uses the auto-generated ID `model_<model_name_with_underscores>`.
- Empty `group_id:id` means every user with the implicit public group.

### Groups

```xml
<!-- security/my_module_groups.xml -->
<?xml version="1.0" encoding="utf-8"?>
<odoo>
    <record id="module_category_my_module" model="ir.module.category">
        <field name="name">My Module</field>
        <field name="sequence">20</field>
    </record>

    <record id="group_my_module_user" model="res.groups">
        <field name="name">User</field>
        <field name="category_id" ref="module_category_my_module"/>
    </record>

    <record id="group_my_module_manager" model="res.groups">
        <field name="name">Manager</field>
        <field name="category_id" ref="module_category_my_module"/>
        <field name="implied_ids" eval="[(4, ref('group_my_module_user'))]"/>
    </record>
</odoo>
```

### Record rules

```xml
<!-- security/my_model_security.xml -->
<?xml version="1.0" encoding="utf-8"?>
<odoo noupdate="1">
    <record id="my_model_personal_rule" model="ir.rule">
        <field name="name">My Model: own records</field>
        <field name="model_id" ref="model_my_model"/>
        <field name="domain_force">[('user_id', '=', user.id)]</field>
        <field name="groups" eval="[(4, ref('group_my_module_user'))]"/>
    </record>

    <record id="my_model_manager_rule" model="ir.rule">
        <field name="name">My Model: all records</field>
        <field name="model_id" ref="model_my_model"/>
        <field name="domain_force">[(1, '=', 1)]</field>
        <field name="groups" eval="[(4, ref('group_my_module_manager'))]"/>
    </record>
</odoo>
```

For the full security reference see `odoo-17-security-guide.md`.

---

## Reports

### Files

```
report/
├── my_model_reports.xml              # ir.actions.report and paper formats
└── my_model_templates.xml            # QWeb templates
```

Declared in `data` **before** menus but **after** views (reports may be
referenced from view buttons):

```python
'data': [
    # ...security, data, views...
    'report/my_model_templates.xml',
    'report/my_model_reports.xml',
    'views/my_module_menus.xml',
],
```

### Action

```xml
<!-- report/my_model_reports.xml -->
<odoo>
    <record id="action_report_my_model" model="ir.actions.report">
        <field name="name">My Model Report</field>
        <field name="model">my.model</field>
        <field name="report_type">qweb-pdf</field>
        <field name="report_name">my_module.report_my_model</field>
        <field name="report_file">my_module.report_my_model</field>
        <field name="print_report_name">'My Model - %s' % (object.name)</field>
        <field name="binding_model_id" ref="model_my_model"/>
        <field name="binding_type">report</field>
    </record>
</odoo>
```

| `report_type` | Output |
|---------------|--------|
| `qweb-pdf`    | PDF via wkhtmltopdf. |
| `qweb-html`   | HTML (viewed in browser). |
| `qweb-text`   | Plain text (labels, barcodes). |

### Template

```xml
<!-- report/my_model_templates.xml -->
<odoo>
    <template id="report_my_model_document">
        <t t-call="web.external_layout">
            <div class="page">
                <h2 t-field="doc.name"/>
                <p t-field="doc.description"/>
            </div>
        </t>
    </template>

    <template id="report_my_model">
        <t t-call="web.html_container">
            <t t-foreach="docs" t-as="doc">
                <t t-call="my_module.report_my_model_document"/>
            </t>
        </t>
    </template>
</odoo>
```

Report CSS/SCSS goes into the `web.report_assets_common` bundle (see
[Asset Bundles](#asset-bundles)).

For the full reports reference see `odoo-17-reports-guide.md`.

---

## Wizards & `TransientModel`

Wizards are short-lived models whose records are periodically purged (by
default daily). Use them for dialogs, multi-step assistants, and actions
triggered from a model's form view.

### File layout

```
wizard/
├── __init__.py
├── make_my_model.py
└── make_my_model_views.xml
```

### Python

```python
# wizard/make_my_model.py
from odoo import api, fields, models
from odoo.exceptions import UserError


class MyWizard(models.TransientModel):
    _name = 'my.wizard'
    _description = 'My Action Wizard'

    date = fields.Date(default=fields.Date.context_today, required=True)
    reason = fields.Text()
    user_id = fields.Many2one('res.users', default=lambda self: self.env.user)

    record_ids = fields.Many2many(
        'my.model',
        string='Records',
    )

    @api.model
    def default_get(self, fields_list):
        res = super().default_get(fields_list)
        if 'record_ids' in fields_list and self.env.context.get('active_model') == 'my.model':
            res['record_ids'] = [(6, 0, self.env.context.get('active_ids', []))]
        return res

    def action_apply(self):
        self.ensure_one()
        if not self.record_ids:
            raise UserError('Select at least one record.')
        for rec in self.record_ids:
            rec.action_done(self.date, self.reason)
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': 'Applied',
                'message': f'Processed {len(self.record_ids)} records',
                'type': 'success',
            },
        }
```

### View

```xml
<!-- wizard/make_my_model_views.xml -->
<odoo>
    <record id="view_my_wizard_form" model="ir.ui.view">
        <field name="name">my.wizard.form</field>
        <field name="model">my.wizard</field>
        <field name="arch" type="xml">
            <form string="My Wizard">
                <group>
                    <field name="date"/>
                    <field name="user_id"/>
                </group>
                <group>
                    <field name="reason"/>
                </group>
                <field name="record_ids" invisible="1"/>
                <footer>
                    <button string="Apply" name="action_apply" type="object" class="btn-primary"/>
                    <button string="Cancel" class="btn-secondary" special="cancel"/>
                </footer>
            </form>
        </field>
    </record>

    <record id="action_my_wizard" model="ir.actions.act_window">
        <field name="name">Run My Wizard</field>
        <field name="res_model">my.wizard</field>
        <field name="view_mode">form</field>
        <field name="target">new</field>
    </record>
</odoo>
```

Declared in `data`:

```python
'data': [
    # ...security...
    'wizard/make_my_model_views.xml',
    # ...views, menus...
],
```

### `TransientModel` vs `Model`

| | `TransientModel` | `Model` |
|---|------------------|---------|
| Lifetime | Auto-GC (default: rows >1 day old). | Permanent. |
| DB table | Yes. | Yes. |
| `_name` | Convention: end with `.wizard`. | Free. |
| Use case | Wizards, confirmation dialogs, one-shot actions. | Business data. |

---

## Data Files

### Records

```xml
<!-- data/my_module_data.xml -->
<odoo>
    <record id="my_config_1" model="my.model">
        <field name="name">Default</field>
        <field name="code">DEFAULT</field>
    </record>

    <!-- noupdate="1" means module upgrades will NOT overwrite user edits. -->
    <record id="my_config_editable" model="my.model" noupdate="1">
        <field name="name">Customizable</field>
    </record>
</odoo>
```

### Cron jobs

```xml
<odoo>
    <record id="ir_cron_my_model_cleanup" model="ir.cron">
        <field name="name">Clean old my.model records</field>
        <field name="model_id" ref="model_my_model"/>
        <field name="state">code</field>
        <field name="code">model._cron_cleanup()</field>
        <field name="interval_number">1</field>
        <field name="interval_type">days</field>
        <field name="numbercall">-1</field>
        <field name="active" eval="True"/>
    </record>
</odoo>
```

For exhaustive data-file syntax see `odoo-17-data-guide.md` and
`odoo-17-actions-guide.md`.

---

## Asset Bundles

Asset bundles in Odoo 17 (verified against `addons/web/__manifest__.py`):

| Bundle | Use for |
|--------|---------|
| `web.assets_backend` | Backend JS, SCSS, and OWL XML templates. |
| `web.assets_frontend` | Website/portal assets (includes what used to be `assets_common`). |
| `web.assets_tests` | Tour/integration test assets. |
| `web.qunit_suite_tests` | Desktop QUnit test suites. |
| `web.qunit_mobile_suite_tests` | Mobile QUnit tests. |
| `web.report_assets_common` | SCSS/JS used when rendering QWeb reports. |
| `web.report_assets_pdf` | Extra PDF-only CSS. |
| `web.assets_web` | Full web client (rarely extended by custom modules). |
| `web.assets_web_dark` | Dark-mode overrides. |
| `web._assets_primary_variables` | Primary SCSS variables (early include, e.g. theme colors). |
| `web._assets_secondary_variables` | Secondary SCSS variables. |

> **Not present in v17:** `web.assets_common`. It was merged into
> `web.assets_frontend` before Odoo 17 shipped. Do not declare an asset under
> `web.assets_common` in a v17 module.

### Declaring in `__manifest__.py`

```python
'assets': {
    'web.assets_backend': [
        'my_module/static/src/scss/form_override.scss',
        'my_module/static/src/js/**/*.js',
        'my_module/static/src/xml/**/*.xml',         # OWL templates
    ],
    'web.assets_frontend': [
        'my_module/static/src/js/portal.js',
        'my_module/static/src/scss/portal.scss',
    ],
    'web.report_assets_common': [
        'my_module/static/src/scss/report.scss',
    ],
    'web.assets_tests': [
        'my_module/static/tests/tours/**/*',
    ],
    'web.qunit_suite_tests': [
        'my_module/static/tests/**/*',
        ('remove', 'my_module/static/tests/tours/**/*'),
    ],
}
```

### Operations recap

| Operation | Shape |
|-----------|-------|
| Include entire bundle | `('include', 'web._assets_core')` |
| Remove a glob already in the bundle | `('remove', 'my_module/static/src/js/exp.js')` |
| Prepend | `('prepend', 'my_module/static/src/scss/vars.scss')` |
| Insert after / before a specific file | `('after', '<anchor>', '<new>')` / `('before', ...)` |
| Replace | `('replace', '<old>', '<new>')` |

---

## Static Assets Layout

```
static/
├── description/
│   ├── icon.png                 # 128×128 recommended; shown in Apps list
│   └── index.html               # (optional) Apps-store marketing page
└── src/
    ├── js/
    │   ├── components/
    │   │   └── my_widget.js     # OWL component (JS)
    │   └── services/
    │       └── my_service.js
    ├── xml/
    │   └── my_widget.xml        # OWL template (paired with the JS file)
    ├── scss/
    │   └── my_widget.scss
    ├── css/
    │   └── plain.css            # CSS that isn't SCSS
    ├── lib/                     # Bundled third-party libs (avoid where possible)
    └── img/
        └── logo.svg
```

Conventions:

- OWL components live in `static/src/js/` with a matching `.xml` template in
  `static/src/xml/` (or colocated, then include both with the same glob).
- `static/description/icon.png` is picked up automatically by the Apps UI —
  you do not declare it in the manifest.
- Third-party libraries go in `static/lib/` (each library in its own
  subfolder).
- Keep one meaningful component per JavaScript, XML template, and stylesheet
  file; use subdirectories to group a component package.

### JavaScript and CSS/SCSS Conventions

- Colocate JS, XML templates, and SCSS when they change together. Use
  meaningful component files, strict mode where the asset format permits it,
  and no minified third-party source.
- Indent CSS/SCSS with four spaces, one declaration per line, and avoid ID
  selectors. Prefix module classes with `o_<module_name>`.
- Order styles from variables through positioning, layout, box model,
  backgrounds, typography, then decorative effects. Use SCSS for global
  design-system values and CSS variables for contextual DOM adaptations.

---

## i18n Folder (.pot + locale .po)

**Every Odoo module ships an `i18n/` folder.** The folder must contain:

1. A `.pot` template named after the module (`<module>.pot`) — the machine-
   extractable strings.
2. One `.po` file per supported locale (e.g. `vi.po`, `fr.po`).

```
i18n/
├── my_module.pot          # REQUIRED: translation template
├── vi.po                  # Vietnamese
└── fr.po                  # Optional extras
```

The `.pot` file is not loaded at install; it is the source of truth for
translators. Locale `.po` files *are* loaded automatically (Odoo scans the
`i18n/` folder when installing or updating the module).

### Generating the `.pot`

From the Odoo server:

```bash
./odoo-bin -d <db> --modules=my_module --i18n-export=my_module/i18n/my_module.pot
```

Or from Settings → Translations → Export Translations (UI), selecting
`New language (Empty template)` + the module.

### `my_module.pot` skeleton

```po
# Translation of Odoo Server.
# This file contains the translation of the following modules:
# 	* my_module
#
msgid ""
msgstr ""
"Project-Id-Version: Odoo Server 17.0\n"
"Report-Msgid-Bugs-To: \n"
"POT-Creation-Date: 2026-04-23 00:00+0000\n"
"PO-Revision-Date: 2026-04-23 00:00+0000\n"
"Last-Translator: \n"
"Language-Team: \n"
"MIME-Version: 1.0\n"
"Content-Type: text/plain; charset=UTF-8\n"
"Content-Transfer-Encoding: \n"
"Plural-Forms: \n"

#. module: my_module
#: model:ir.model,name:my_module.model_my_model
msgid "My Model"
msgstr ""

#. module: my_module
#: model:ir.model.fields,field_description:my_module.field_my_model__name
msgid "Name"
msgstr ""
```

### `vi.po` skeleton

```po
# Translation of Odoo Server.
# This file contains the translation of the following modules:
# 	* my_module
#
msgid ""
msgstr ""
"Project-Id-Version: Odoo Server 17.0\n"
"Report-Msgid-Bugs-To: \n"
"POT-Creation-Date: 2026-04-23 00:00+0000\n"
"PO-Revision-Date: 2026-04-23 00:00+0000\n"
"Language-Team: Vietnamese <vi@li.org>\n"
"Language: vi\n"
"MIME-Version: 1.0\n"
"Content-Type: text/plain; charset=UTF-8\n"
"Content-Transfer-Encoding: 8bit\n"
"Plural-Forms: nplurals=1; plural=0;\n"

#. module: my_module
#: model:ir.model,name:my_module.model_my_model
msgid "My Model"
msgstr "Mô hình của tôi"

#. module: my_module
#: model:ir.model.fields,field_description:my_module.field_my_model__name
msgid "Name"
msgstr "Tên"
```

For the full translation workflow see `odoo-17-translation-guide.md`.

---

## Complete Module Skeleton

### Files

```
business_trip/
├── __init__.py
├── __manifest__.py
├── models/
│   ├── __init__.py
│   └── business_trip.py
├── wizard/
│   ├── __init__.py
│   ├── business_trip_cancel.py
│   └── business_trip_cancel_views.xml
├── controllers/
│   ├── __init__.py
│   └── business_trip.py
├── views/
│   ├── business_trip_views.xml
│   └── business_trip_menus.xml
├── security/
│   ├── business_trip_groups.xml
│   ├── business_trip_security.xml
│   └── ir.model.access.csv
├── data/
│   └── ir_sequence_data.xml
├── demo/
│   └── business_trip_demo.xml
├── report/
│   ├── business_trip_reports.xml
│   └── business_trip_templates.xml
├── migrations/
│   └── 17.0.1.0.0/
│       └── post-migrate.py
├── i18n/
│   ├── business_trip.pot
│   └── vi.po
├── static/
│   ├── description/
│   │   └── icon.png
│   └── src/
│       ├── js/
│       │   └── trip_form.js
│       ├── xml/
│       │   └── trip_form.xml
│       └── scss/
│           └── trip.scss
└── tests/
    ├── __init__.py
    └── test_business_trip.py
```

### `__manifest__.py`

```python
# -*- coding: utf-8 -*-
{
    'name': 'Business Trip Management',
    'version': '17.0.1.0.0',
    'summary': 'Plan trips and track expenses',
    'author': 'UncleCat',
    'license': 'LGPL-3',
    'category': 'Human Resources',
    'depends': ['base', 'mail', 'hr'],
    'data': [
        'security/business_trip_groups.xml',
        'security/business_trip_security.xml',
        'security/ir.model.access.csv',
        'data/ir_sequence_data.xml',
        'wizard/business_trip_cancel_views.xml',
        'views/business_trip_views.xml',
        'report/business_trip_templates.xml',
        'report/business_trip_reports.xml',
        'views/business_trip_menus.xml',
    ],
    'demo': [
        'demo/business_trip_demo.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'business_trip/static/src/js/trip_form.js',
            'business_trip/static/src/xml/trip_form.xml',
            'business_trip/static/src/scss/trip.scss',
        ],
    },
    'post_init_hook': 'post_init_hook',
    'uninstall_hook': 'uninstall_hook',
    'installable': True,
    'application': True,
}
```

### `__init__.py`

```python
# business_trip/__init__.py
from . import controllers
from . import models
from . import wizard


def post_init_hook(env):
    env['ir.config_parameter'].sudo().set_param('business_trip.enabled', 'True')


def uninstall_hook(env):
    env['ir.config_parameter'].sudo().search([
        ('key', '=like', 'business_trip.%')
    ]).unlink()
```

### `models/business_trip.py`

```python
from odoo import api, fields, models


class BusinessTrip(models.Model):
    _name = 'business.trip'
    _description = 'Business Trip'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'date_start desc'

    name = fields.Char(required=True, tracking=True)
    date_start = fields.Date(required=True, tracking=True)
    date_end = fields.Date(required=True)
    employee_id = fields.Many2one('hr.employee', required=True, tracking=True)
    state = fields.Selection([
        ('draft', 'Draft'),
        ('confirmed', 'Confirmed'),
        ('done', 'Done'),
        ('cancel', 'Cancelled'),
    ], default='draft', tracking=True)

    def action_confirm(self):
        self.write({'state': 'confirmed'})

    def action_done(self, date=None, reason=None):
        self.write({'state': 'done'})
```

### `security/ir.model.access.csv`

```csv
id,name,model_id:id,group_id:id,perm_read,perm_write,perm_create,perm_unlink
access_business_trip_user,business.trip user,model_business_trip,business_trip.group_business_trip_user,1,1,1,0
access_business_trip_manager,business.trip manager,model_business_trip,business_trip.group_business_trip_manager,1,1,1,1
```

### `i18n/business_trip.pot`

```po
msgid ""
msgstr ""
"Project-Id-Version: Odoo Server 17.0\n"
"Report-Msgid-Bugs-To: \n"
"POT-Creation-Date: 2026-04-23 00:00+0000\n"
"PO-Revision-Date: 2026-04-23 00:00+0000\n"
"Last-Translator: \n"
"Language-Team: \n"
"MIME-Version: 1.0\n"
"Content-Type: text/plain; charset=UTF-8\n"
"Content-Transfer-Encoding: \n"
"Plural-Forms: \n"

#. module: business_trip
#: model:ir.model,name:business_trip.model_business_trip
msgid "Business Trip"
msgstr ""
```

### `i18n/vi.po`

```po
msgid ""
msgstr ""
"Project-Id-Version: Odoo Server 17.0\n"
"Language-Team: Vietnamese <vi@li.org>\n"
"Language: vi\n"
"MIME-Version: 1.0\n"
"Content-Type: text/plain; charset=UTF-8\n"
"Content-Transfer-Encoding: 8bit\n"
"Plural-Forms: nplurals=1; plural=0;\n"

#. module: business_trip
#: model:ir.model,name:business_trip.model_business_trip
msgid "Business Trip"
msgstr "Chuyến công tác"
```

---

## Base Code Reference

- `odoo/modules/module.py` — module discovery, `_DEFAULT_MANIFEST`, manifest
  loading (`load_manifest`, `get_manifest`), version normalization
  (`adapt_version`).
- `odoo/modules/loading.py` — module initialization and hook invocation. All
  installation hooks (`pre_init_hook`, `post_init_hook`, `uninstall_hook`) are
  called with a single `env` argument in v17.
- `addons/web/__manifest__.py` — authoritative list of asset bundles in v17
  (`web.assets_backend`, `web.assets_frontend`, `web.report_assets_common`,
  `web.assets_tests`, `web.qunit_suite_tests`, …). Note there is **no**
  `web.assets_common` in v17.
- `odoo/addons/base/models/ir_asset.py` — `ir.asset` model used to manage
  bundle entries at runtime.
- `odoo/addons/base/models/ir_model.py`, `ir_rule.py` — security records.
- `odoo/release.py` — `major_version = '17.0'`.

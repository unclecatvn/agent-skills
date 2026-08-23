---
name: odoo-17-manifest
description: Complete reference for Odoo 17 module manifest (__manifest__.py) covering every valid key, dependencies, data loading order, assets, external dependencies, hooks, auto_install, version scheme, and license identifiers.
globs: "**/__manifest__.py"
topics:
  - Every valid __manifest__.py key in Odoo 17
  - Module dependencies and loading order
  - `data` list ordering (security first, views last)
  - Assets bundles (web.assets_backend, web.assets_frontend, web.report_assets_common, etc.)
  - External dependencies (python, bin)
  - Hooks (pre_init_hook, post_init_hook, uninstall_hook, post_load)
  - auto_install (bool or list of dependencies)
  - `installable`, `application`, `sequence`
  - Version scheme 17.0.X.Y.Z
  - License identifiers
when_to_use:
  - Authoring a new Odoo 17 module manifest
  - Configuring module dependencies or assets
  - Declaring external Python/binary dependencies
  - Setting up module lifecycle hooks
  - Deciding between `auto_install=True` and an explicit trigger set
---

# Odoo 17 Module Manifest Guide

Complete reference for Odoo 17 `__manifest__.py`: every valid key, the `_DEFAULT_MANIFEST` defaults, dependencies, assets, hooks, and version rules.

## Table of Contents

1. [Manifest Basics](#manifest-basics)
2. [Default Values (`_DEFAULT_MANIFEST`)](#default-values-_default_manifest)
3. [Core Identification Fields](#core-identification-fields)
4. [Version Scheme (`17.0.X.Y.Z`)](#version-scheme-170xyz)
5. [License Identifiers](#license-identifiers)
6. [Dependencies](#dependencies)
7. [Data Loading](#data-loading)
8. [Assets](#assets)
9. [External Dependencies](#external-dependencies)
10. [Hooks](#hooks)
11. [Other Fields](#other-fields)
12. [Complete Example](#complete-example)
13. [Common Patterns](#common-patterns)
14. [Base Code Reference](#base-code-reference)

---

## Manifest Basics

### File Name

Odoo 17 looks for these filenames (in order), via `MANIFEST_NAMES` in
`odoo/modules/module.py`:

```python
MANIFEST_NAMES = ('__manifest__.py', '__openerp__.py')
```

- Always use `__manifest__.py`.
- `__openerp__.py` is accepted but raises `DeprecationWarning` (removed in a
  future major version).

### Manifest Shape

The file must evaluate (via `ast.literal_eval`) to a single Python `dict`
literal. No imports, no function calls, no expressions — just literals:

```python
# -*- coding: utf-8 -*-
{
    'name': 'My Module',
    'version': '17.0.1.0.0',
    'depends': ['base'],
    'data': [],
    'installable': True,
    'license': 'LGPL-3',
    'author': 'UncleCat',
}
```

### Minimal Installable Manifest

```python
{
    'name': 'My Module',
    'version': '17.0.1.0.0',
    'license': 'LGPL-3',
    'author': 'UncleCat',
    'depends': ['base'],
    'installable': True,
}
```

---

## Default Values (`_DEFAULT_MANIFEST`)

Every key the v17 loader understands appears in `_DEFAULT_MANIFEST`
(`odoo/modules/module.py`). Keys not in your manifest fall back to these
defaults:

| Key | Default | Notes |
|-----|---------|-------|
| `name` | — | **Required.** |
| `version` | `'1.0'` | Gets normalized to `'17.0.1.0'` by `adapt_version`. |
| `license` | `'LGPL-3'` | Warning emitted if missing. |
| `author` | `'Odoo S.A.'` | Override in every custom module. |
| `category` | `'Uncategorized'` | |
| `summary` | `''` | One-line description. |
| `description` | `''` | RST; falls back to `README.rst/md/txt` if empty. |
| `website` | `''` | |
| `sequence` | `100` | Ordering in Apps list. |
| `depends` | `[]` | |
| `data` | `[]` | |
| `demo` | `[]` | |
| `demo_xml` | `[]` | Legacy alias, avoid. |
| `init_xml` | `[]` | Legacy alias, avoid. |
| `update_xml` | `[]` | Legacy alias, avoid. |
| `test` | `[]` | Legacy test declarations, avoid. |
| `installable` | `True` | |
| `application` | `False` | |
| `auto_install` | `False` | `True`, `False`, or an iterable of module names. |
| `assets` | `{}` | Asset bundles. |
| `external_dependencies` | `{}` | Python/bin requirements. |
| `pre_init_hook` | `''` | Name of function in the module's package. |
| `post_init_hook` | `''` | Same. |
| `uninstall_hook` | `''` | Same. |
| `post_load` | `''` | Server-wide hook run at module import. |
| `images` | `[]` | Screenshot paths. |
| `images_preview_theme` | `{}` | Website themes only. |
| `live_test_url` | `''` | Website themes only. |
| `new_page_templates` | `{}` | Website themes only. |
| `configurator_snippets` | `{}` | Website themes only. |
| `countries` | `[]` | Localization modules only. |
| `web` | `False` | Internal flag, do not set. |
| `bootstrap` | `False` | Used by the `web` module only. |

Keys not listed here (e.g. `maintainer`) are accepted as plain metadata — they
are stored but not interpreted by the loader.

---

## Core Identification Fields

### `name` (required)

```python
'name': 'Business Trip Management',
```

Human-readable name shown in the Apps list.

### `summary`

```python
'summary': 'Plan business trips and track expenses',
```

One-line description shown under the module title in the Apps list.

### `description`

```python
'description': """
Business Trip Management
========================
Manage business trips, per-diems, and expense reports.
""",
```

reStructuredText. If empty, Odoo reads `README.rst`, `README.md`, or
`README.txt` from the module directory (see `load_manifest`).

### `author`

```python
'author': 'UncleCat',
```

Can be a person, company, or comma-separated list:

```python
'author': 'UncleCat, Acme Corp.',
```

### `website`

```python
'website': 'https://example.com',
```

### `category`

```python
'category': 'Sales/Subscriptions',
```

Slashes create a hierarchy (`Sales` → `Subscriptions`). Common values include
`Accounting`, `Human Resources`, `Inventory`, `Manufacturing`, `Marketing`,
`Point of Sale`, `Productivity/Discuss`, `Project`, `Sales`, `Services`,
`Tools`, `Warehouse`, `Website`, `Hidden` (for technical-only modules).

### `maintainer`

```python
'maintainer': 'UncleCat',
```

Not in `_DEFAULT_MANIFEST`; stored as metadata. Defaults to `author` if
consumers read it.

---

## Version Scheme (`17.0.X.Y.Z`)

### Format

Odoo 17 enforces that `version` must match one of these shapes (see
`adapt_version` in `odoo/modules/module.py`):

```
x.y
x.y.z
17.0.x.y
17.0.x.y.z
```

If the prefix is missing, the loader prepends `17.0.` automatically:

```python
'version': '1.0.0'        # becomes '17.0.1.0.0'
'version': '17.0.1.0.0'   # stays  '17.0.1.0.0'
```

### Recommended

Always write the full form so the manifest is self-documenting and so migration
folders line up with the declared version:

```python
'version': '17.0.1.0.0',
```

Interpretation (convention, not enforced):

- `17.0` — target Odoo series.
- `1` — MAJOR of the module (incompatible schema changes).
- `0` — MINOR (backwards-compatible feature additions).
- `0` — PATCH (bug fixes).

### Bumping for Migrations

The migration runner compares `parsed_installed_version` against
`current_version`. Migration scripts under `migrations/17.0.1.1.0/` only run
when you bump from `17.0.1.0.0` to `17.0.1.1.0` or higher. Always bump the
version in the manifest **before** committing a migration script.

---

## License Identifiers

The loader warns if `license` is missing and falls back to `LGPL-3`. Always
declare it explicitly. Valid values include:

| Identifier | Description |
|------------|-------------|
| `LGPL-3` | GNU Lesser General Public License v3 (Odoo default). |
| `GPL-2` | GNU General Public License v2. |
| `GPL-2 or any later version` | |
| `GPL-3` | GNU General Public License v3. |
| `GPL-3 or any later version` | |
| `AGPL-3` | GNU Affero General Public License v3. |
| `OEEL-1` | Odoo Enterprise Edition License v1.0 (Enterprise addons). |
| `OPL-1` | Odoo Proprietary License v1.0. |
| `Other OSI approved licence` | Any OSI-approved license. |
| `Other proprietary` | Closed-source custom license. |

---

## Dependencies

### `depends`

```python
'depends': ['base', 'mail', 'product'],
```

List of modules that must be installed before this one. Odoo resolves the
dependency graph and installs/loads them first.

- Always include `base` (sometimes transitive, but explicit is better).
- Depend on `mail` when you use `mail.thread` / `mail.activity.mixin`.
- Avoid circular dependencies — the loader will error out.

### `auto_install`

Three accepted shapes (`odoo/modules/module.py`, `load_manifest`):

```python
# 1) Opt-in (default)
'auto_install': False,

# 2) Auto-install once every module in `depends` is installed
'auto_install': True,

# 3) Auto-install once this specific subset is installed
#    (Subset must be a subset of `depends`.)
'auto_install': ['sale', 'purchase'],
```

Shape #3 is used by bridge modules: they declare `depends: ['sale',
'purchase']` and `auto_install: ['sale', 'purchase']`, meaning they appear
automatically when both Sales and Purchase are installed.

The loader asserts `auto_install ⊆ depends`:

```
AssertionError: auto_install triggers must be dependencies, found
non-dependencies [...] for module <name>
```

---

## Data Loading

### `data`

```python
'data': [
    # 1. Security FIRST (groups, ACL, record rules) — views reference them.
    'security/res_groups.xml',
    'security/ir_rules.xml',
    'security/ir.model.access.csv',

    # 2. Reference data (sequences, parameters, templates)
    'data/ir_sequence_data.xml',
    'data/mail_template_data.xml',

    # 3. Wizards
    'wizard/make_my_model_views.xml',

    # 4. Views
    'views/my_model_views.xml',
    'views/res_partner_views.xml',

    # 5. Reports (templates + actions)
    'report/my_model_templates.xml',
    'report/my_model_reports.xml',

    # 6. Menus LAST — they reference window actions defined above.
    'views/my_menus.xml',
],
```

**Ordering rules:**

1. **Security first.** `ir.model.access.csv` and groups must exist before any
   view that references them.
2. **Records before their references.** A view that sets `action_id` must come
   after the action.
3. **Menus last.** They usually reference actions defined earlier.
4. **Wizards before view bindings** that embed wizard buttons.

Paths are relative to the module root. Absolute paths and `../` are rejected.

### `demo`

```python
'demo': [
    'demo/my_module_demo.xml',
],
```

Loaded **only** when the database is created with `--demo=all` (or equivalent).
`data` is loaded on install *and* update; `demo` is loaded on install *only*
when demo mode is active.

| Attribute | When loaded |
|-----------|-------------|
| `data` | Install AND update. |
| `demo` | Install in demo mode only. |

### `demo_xml`, `init_xml`, `update_xml`, `test`

Legacy aliases from Odoo 7 and earlier. Do not use in new v17 modules — they
exist in `_DEFAULT_MANIFEST` only for backwards compatibility.

---

## Assets

### Structure

Assets are a dict of *bundle name → list of glob patterns*:

```python
'assets': {
    'web.assets_backend': [
        'my_module/static/src/js/**/*.js',
        'my_module/static/src/xml/**/*.xml',
        'my_module/static/src/scss/style.scss',
    ],
    'web.assets_frontend': [
        'my_module/static/src/js/portal.js',
    ],
    'web.report_assets_common': [
        'my_module/static/src/scss/report.scss',
    ],
}
```

### Bundles Available in Odoo 17

Verified against `addons/web/__manifest__.py` in the v17 source:

| Bundle | Purpose |
|--------|---------|
| `web.assets_backend` | Backend (web client) JS/CSS/XML. |
| `web.assets_frontend` | Website / portal assets. Contains what used to live in `assets_common`. |
| `web.assets_frontend_minimal` | Minimal frontend polyfills / module loader. |
| `web.assets_frontend_lazy` | Lazily loaded frontend bundle. |
| `web.assets_web` | Full web client (`assets_backend` + bootstrap entry points). |
| `web.assets_web_dark` | Dark-theme variant of `assets_web`. |
| `web.assets_tests` | Tour/integration test assets. |
| `web.tests_assets` | QUnit test runtime. |
| `web.qunit_suite_tests` | Desktop QUnit test suites. |
| `web.qunit_mobile_suite_tests` | Mobile QUnit suites. |
| `web.report_assets_common` | SCSS/JS included when rendering QWeb reports (PDF/HTML). |
| `web.report_assets_pdf` | Extra CSS for PDF-only rendering. |
| `web.assets_emoji` | Emoji data (lazy loaded). |
| `web.pdf_js_lib` | pdf.js library (lazy loaded). |
| `web.ace_lib` | Ace editor library. |
| `web._assets_primary_variables` | Primary SCSS variables (early include). |
| `web._assets_secondary_variables` | Secondary SCSS variables. |
| `web._assets_helpers` / `web._assets_core` / `web._assets_bootstrap*` | Private sub-bundles referenced via `('include', ...)`. |

> **Not present in v17:** `web.assets_common`. The bundle was merged into
> `web.assets_frontend` before v17. Do **not** add entries to
> `web.assets_common` in an Odoo 17 module.

### Operations

Each entry in a bundle list is either a string (glob path) or a 2/3-tuple
operation:

```python
'web.assets_backend': [
    # plain include
    'my_module/static/src/js/core.js',

    # glob
    'my_module/static/src/js/components/**/*.js',

    # relative operations
    ('include',  'web._assets_backend_helpers'),
    ('remove',   'my_module/static/src/js/experimental.js'),
    ('prepend',  'my_module/static/src/scss/vars.scss'),
    ('replace',  'other_module/static/src/js/thing.js', 'my_module/static/src/js/thing.js'),
    ('after',    'other_module/static/src/scss/core.scss', 'my_module/static/src/scss/override.scss'),
    ('before',   'other_module/static/src/js/boot.js',    'my_module/static/src/js/pre_boot.js'),
],
```

### Creating a Custom Bundle

```python
'assets': {
    'my_module.assets_reports_custom': [
        'my_module/static/src/js/custom_report.js',
    ],
}
```

Then reference it from a QWeb template with `<t t-call-assets="my_module.assets_reports_custom"/>`.

### Static Description

Odoo looks for `static/description/icon.png` automatically; no manifest entry
needed. Additional screenshots go in `images`:

```python
'images': [
    'static/description/banner.png',
    'static/description/screenshot_1.png',
],
```

---

## External Dependencies

### `external_dependencies`

```python
'external_dependencies': {
    'python': [
        'requests',
        'pyjwt',
        'python-dateutil',
    ],
    'bin': [
        'wkhtmltopdf',
        'ghostscript',
    ],
}
```

- `python`: Python package names (as importable / as listed in PyPI). Checked
  via `pkg_resources.get_distribution`; falls back to `importlib.import_module`
  (see `check_python_external_dependency`).
- `bin`: Binaries that must be present on `PATH`.

If a declared dependency is missing, the module refuses to install with an
exception from `check_manifest_dependencies`.

---

## Hooks

### Manifest Entries

```python
'pre_init_hook':   'pre_init_hook',
'post_init_hook':  'post_init_hook',
'uninstall_hook':  'uninstall_hook',
'post_load':       'post_load',
```

Each value is a function name to look up inside the module's `__init__.py`
(technically `sys.modules['odoo.addons.<module_name>']`).

### Signatures in Odoo 17

Verified against `odoo/modules/loading.py` (lines ~191, 247, 565):

```python
# __init__.py  — all three installation hooks take a single `env` argument.

def pre_init_hook(env):
    """Runs before the module's models/data are loaded, on fresh install only."""
    # env.cr is the cursor; env['model'] gives access to the registry.
    ...

def post_init_hook(env):
    """Runs after install (after data load), on fresh install only."""
    ...

def uninstall_hook(env):
    """Runs when the module is being removed."""
    ...
```

> **Historical note.** Earlier Odoo versions used `(cr,)` for `pre_init_hook`
> and `(cr, registry)` for `post_init_hook` / `uninstall_hook`. Odoo 17
> standardized all three on a single `env` argument. From `env` you can still
> reach the cursor (`env.cr`) and the registry (`env.registry`).

### `post_load`

Different beast — runs **at module import time**, once per server process, not
per database:

```python
def post_load():
    # No arguments. Called exactly once per worker.
    # Use for server-wide monkey-patching or global registration.
    ...
```

Declared in `module.py` (`load_openerp_module`): `getattr(sys.modules[qualname], info['post_load'])()`.

### Example `__init__.py`

```python
# my_module/__init__.py
from . import controllers
from . import models
from . import wizard


def pre_init_hook(env):
    env.cr.execute("""
        CREATE TABLE IF NOT EXISTS my_module_audit (
            id SERIAL PRIMARY KEY,
            message TEXT,
            create_date TIMESTAMP DEFAULT NOW()
        )
    """)


def post_init_hook(env):
    env['ir.config_parameter'].sudo().set_param('my_module.enabled', 'True')
    env['my.model'].create({'name': 'Default', 'code': 'DFLT'})


def uninstall_hook(env):
    env.cr.execute("DROP TABLE IF EXISTS my_module_audit")
    env['ir.config_parameter'].sudo().search([
        ('key', '=like', 'my_module.%')
    ]).unlink()
```

---

## Other Fields

### `application`

```python
'application': True,
```

Marks the module as an application. Applications appear in the **Apps** filter
by default and get their own entry in the Apps category tree.

### `installable`

```python
'installable': True,
```

Set to `False` to hide a module from the Apps list (useful for WIP or
deprecated modules). The loader still parses the manifest.

### `sequence`

```python
'sequence': 100,
```

Integer used to order modules within their category. Lower values appear first.
Mainly cosmetic for the Apps list.

### `countries`

```python
'countries': ['vn', 'th'],
```

Used by localization modules (`l10n_*`) to restrict availability. Lowercase
ISO 3166-1 alpha-2 codes.

### `images`

```python
'images': [
    'static/description/banner.png',
    'static/description/main_screenshot.png',
],
```

Paths relative to the module root. Shown on the Apps store page.

### `website`

```python
'website': 'https://example.com/my_module',
```

Module homepage (project page / documentation).

---

## Complete Example

```python
# -*- coding: utf-8 -*-
{
    # == Identification ==
    'name': 'Business Trip Management',
    'version': '17.0.1.0.0',
    'summary': 'Plan business trips, track per-diems and expenses',
    'description': """
Business Trip Management
========================
Features:

* Plan trips with itinerary, per-diem rates, and approvers.
* Track expenses and link receipts.
* Generate PDF reports per trip.
* Email templates for approval and reimbursement.
""",
    'category': 'Human Resources/Expenses',
    'author': 'UncleCat',
    'maintainer': 'UncleCat',
    'website': 'https://example.com/business_trip',
    'license': 'LGPL-3',

    # == Dependencies ==
    'depends': [
        'base',
        'mail',
        'hr',
        'hr_expense',
        'product',
    ],
    'auto_install': False,

    # == Data (order matters) ==
    'data': [
        # Security first
        'security/business_trip_groups.xml',
        'security/business_trip_security.xml',
        'security/ir.model.access.csv',

        # Reference data
        'data/ir_sequence_data.xml',
        'data/mail_template_data.xml',
        'data/ir_cron_data.xml',

        # Wizards
        'wizard/business_trip_cancel_views.xml',

        # Views
        'views/business_trip_views.xml',
        'views/business_trip_expense_views.xml',
        'views/hr_employee_views.xml',

        # Reports
        'report/business_trip_templates.xml',
        'report/business_trip_reports.xml',

        # Menus (last)
        'views/business_trip_menus.xml',
    ],

    # == Demo ==
    'demo': [
        'demo/business_trip_demo.xml',
    ],

    # == Assets ==
    'assets': {
        'web.assets_backend': [
            'business_trip/static/src/scss/trip_form.scss',
            'business_trip/static/src/js/**/*.js',
            'business_trip/static/src/xml/**/*.xml',
        ],
        'web.assets_frontend': [
            'business_trip/static/src/js/portal_trip.js',
        ],
        'web.report_assets_common': [
            'business_trip/static/src/scss/report.scss',
        ],
    },

    # == External requirements ==
    'external_dependencies': {
        'python': ['python-dateutil'],
        'bin':    ['wkhtmltopdf'],
    },

    # == Hooks ==
    'pre_init_hook':  'pre_init_hook',
    'post_init_hook': 'post_init_hook',
    'uninstall_hook': 'uninstall_hook',

    # == Flags ==
    'application': True,
    'installable': True,
    'sequence':    20,
}
```

---

## Common Patterns

### Bridge / link module

```python
{
    'name': 'Sale ↔ Stock Bridge',
    'version': '17.0.1.0.0',
    'author': 'UncleCat',
    'license': 'LGPL-3',
    'category': 'Hidden',
    'depends': ['sale', 'stock'],
    'auto_install': True,     # or ['sale', 'stock']
    'data': ['views/sale_order_views.xml'],
    'installable': True,
}
```

### Website / portal module

```python
{
    'name': 'My Portal Pages',
    'version': '17.0.1.0.0',
    'author': 'UncleCat',
    'license': 'LGPL-3',
    'depends': ['portal', 'website'],
    'data': [
        'security/ir.model.access.csv',
        'views/portal_templates.xml',
    ],
    'assets': {
        'web.assets_frontend': [
            'my_portal/static/src/js/portal.js',
            'my_portal/static/src/scss/portal.scss',
        ],
    },
    'installable': True,
}
```

### Theme module

```python
{
    'name': 'Theme Acme',
    'version': '17.0.1.0.0',
    'author': 'UncleCat',
    'license': 'LGPL-3',
    'category': 'Website/Theme',
    'depends': ['website'],
    'data': ['views/options.xml'],
    'assets': {
        'web._assets_primary_variables': [
            'theme_acme/static/src/scss/primary_variables.scss',
        ],
        'web.assets_frontend': [
            'theme_acme/static/src/scss/style.scss',
        ],
    },
    'images': ['static/description/banner.png'],
    'installable': True,
}
```

### Module with `external_dependencies`

```python
{
    'name': 'Acme REST Connector',
    'version': '17.0.1.0.0',
    'author': 'UncleCat',
    'license': 'LGPL-3',
    'depends': ['base'],
    'external_dependencies': {
        'python': ['requests', 'pyjwt'],
    },
    'data': ['security/ir.model.access.csv', 'views/config_views.xml'],
    'installable': True,
}
```

---

## Coding Conventions

- Load groups before ACLs and rules that reference them, and security before
  views; load actions/reports before menus that reference them.
- Use focused filenames: `<module>_groups.xml`, `<model>_security.xml`,
  `<model>_views.xml`, `<model>_templates.xml`, and `<model>_reports.xml`.

## Base Code Reference

All behavior documented above is derived from the Odoo 17 source:

- `odoo/modules/module.py` — `MANIFEST_NAMES`, `_DEFAULT_MANIFEST`,
  `load_manifest`, `get_manifest`, `adapt_version`, `load_openerp_module`
  (invokes `post_load`), `check_python_external_dependency`.
- `odoo/modules/loading.py` — hook invocation sites for `pre_init_hook`
  (line ~194), `post_init_hook` (line ~247), and `uninstall_hook`
  (line ~565). All three are called with `env`.
- `odoo/release.py` — `version_info = (17, 0, 0, FINAL, 0, '')`,
  `major_version = '17.0'` (used by `adapt_version`).
- `addons/web/__manifest__.py` — canonical bundle names in v17
  (`web.assets_backend`, `web.assets_frontend`, `web.report_assets_common`,
  `web.assets_tests`, `web.qunit_suite_tests`, …). Note: **no
  `web.assets_common`** in v17.
- `addons/sale/__manifest__.py`, `addons/mail/__manifest__.py` — real-world
  manifests to cross-reference when unsure about a field.

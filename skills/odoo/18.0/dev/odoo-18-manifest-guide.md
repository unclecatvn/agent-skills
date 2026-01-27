---
name: odoo-18-manifest
description: Complete reference for Odoo 18 module manifest (__manifest__.py) covering all fields, dependencies, assets, external dependencies, hooks, auto_install, and module structure.
globs: "**/__manifest__.py"
topics:
  - All __manifest__.py fields
  - Module dependencies and loading order
  - Assets bundles (web.assets_frontend, etc.)
  - External dependencies (python, bin)
  - Hooks (pre_init, post_init, uninstall)
  - auto_install behavior
  - Module categories
  - License types
when_to_use:
  - Creating new Odoo modules
  - Configuring module dependencies
  - Setting up assets (JS, CSS, SCSS)
  - Declaring external Python/binary dependencies
  - Using module hooks for initialization
---

# Odoo 18 Module Manifest Guide

Complete reference for Odoo 18 `__manifest__.py`: all fields, dependencies, assets, hooks, and configuration.

## Table of Contents

1. [Manifest Basics](#manifest-basics)
2. [Core Fields](#core-fields)
3. [Dependencies](#dependencies)
4. [Data Loading](#data-loading)
5. [Assets](#assets)
6. [External Dependencies](#external-dependencies)
7. [Hooks](#hooks)
8. [Complete Example](#complete-example)

---

## Manifest Basics

### File Name and Location

```
my_module/
├── __init__.py
├── __manifest__.py  # <-- Manifest file
├── models/
├── views/
└── ...
```

### File Name

- Odoo 13+: `__manifest__.py`
- Odoo 12 and older: `__openerp__.py` (deprecated)

### Basic Structure

```python
#!/usr/bin/env python
# -*- coding: utf-8 -*-

{
    'name': 'My Module',
    'version': '1.0.0',
    'category': 'Tools',
    'summary': 'Short description',
    'description': """
        Long Description
    """,
    'author': 'Author Name',
    'website': 'https://www.example.com',
    'license': 'LGPL-3',
    'depends': ['base'],
    'data': [
        'views/my_views.xml',
    ],
    'demo': [
        'demo/my_demo.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}
```

---

## Core Fields

### Required Fields

Only `name` is truly required, but `version` and `depends` should always be specified.

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `name` | str | - | Human-readable module name (required) |
| `version` | str | - | Module version (should use semantic versioning) |
| `description` | str | - | Extended description in RST |
| `author` | str | - | Module author name |
| `website` | str | - | Author website URL |
| `license` | str | LGPL-3 | Distribution license |
| `category` | str | Uncategorized | Module category |
| `depends` | list(str) | - | Required modules |
| `data` | list(str) | - | Data files to load |
| `installable` | bool | True | Whether module can be installed |

### name (Required)

```python
'name': 'My Module',
```

The display name shown in Apps menu.

### version

```python
'version': '1.0.0',
```

Should follow [semantic versioning](https://semver.org):
- `MAJOR.MINOR.PATCH`
- Increment: MAJOR for incompatible changes, MINOR for backwards-compatible features, PATCH for bug fixes

```python
# Examples
'version': '1.0.0',      # First release
'version': '1.1.0',      # Added feature
'version': '1.1.1',      # Bug fix
'version': '2.0.0',      # Breaking changes
```

### description

```python
'description': """
This module provides functionality for managing business trips.
Features include:
- Trip creation and management
- Expense tracking
- Email notifications
""",
```

Supports reStructuredText formatting.

### author

```python
'author': 'Author Name',
```

Can be person name, company name, or both:

```python
'author': 'Odoo SA',
'author': 'John Doe',
'author': 'My Company, Inc.',
```

### website

```python
'website': 'https://www.odoo.com',
```

### license

```python
'license': 'LGPL-3',
```

Valid values:

| License | Description |
|---------|-------------|
| `LGPL-3` | GNU Lesser General Public License v3 (default) |
| `GPL-2` | GNU General Public License v2 |
| `GPL-3` | GNU General Public License v3 |
| `GPL-2 or any later version` | GPL v2 or later |
| `GPL-3 or any later version` | GPL v3 or later |
| `AGPL-3` | GNU Affero General Public License v3 |
| `OEEL-1` | Odoo Enterprise Edition License v1.0 |
| `OPL-1` | Odoo Proprietary License v1.0 |
| `Other OSI approved licence` | Other OSI-approved license |
| `Other proprietary` | Proprietary license |

### category

```python
'category': 'Tools',
```

Common categories (use existing when possible):

| Category |
|----------|
| Accounting |
| Discussion |
| Document Management |
| eCommerce |
| Human Resources |
| Marketing |
| Manufacturing |
| Point of Sale |
| Project |
| Purchases |
| Sales |
| Tools |
| Warehouse |
| Website |

Custom categories with hierarchy:

```python
'category': 'Tools/Trip Management',
```

Creates `Tools` (parent) → `Trip Management` (child).

### summary

```python
'summary': 'Short description for module list',
```

Brief description shown in module list (one line).

---

## Dependencies

### depends

```python
'depends': ['base', 'mail', 'web'],
```

Modules that must be loaded before this one.

#### Loading Order

1. All dependencies are installed/upgraded before this module
2. Dependencies are loaded before this module

```python
# base always exists but still specify
'depends': ['base'],

# Multiple dependencies
'depends': ['mail', 'web', 'website'],

# With custom modules
'depends': ['base', 'my_other_module'],
```

#### Circular Dependencies

**Avoid circular dependencies!** They cause installation failures.

```
Bad:
Module A depends on B
Module B depends on A
```

### auto_install

```python
'auto_install': True,
```

Automatically install if all dependencies are installed.

```python
# Simple auto_install
'auto_install': True,

# Auto-install if specific subset is installed
'auto_install': ['sale', 'crm'],
```

Common for "link modules":

```python
# sale_crm links sale and crm
'depends': ['sale', 'crm'],
'auto_install': True,
```

---

## Data Loading

### data

```python
'data': [
    'views/my_views.xml',
    'security/my_security.xml',
    'report/my_reports.xml',
],
```

Files loaded at **both** installation and update.

### demo

```python
'demo': [
    'demo/my_demo.xml',
],
```

Files loaded **only in demo mode**.

```python
# Demo mode vs regular mode
'data': [
    'data/core_data.xml',   # Always loaded
],
'demo': [
    'demo/demo_data.xml',    # Only in demo mode
],
```

### data vs demo

| Type | When Loaded |
|------|-------------|
| `data` | Install and update |
| `demo` | Only in demo mode (install only) |

### File Paths

Paths are relative to module root:

```python
'data': [
    'views/views.xml',           # OK: relative path
    '/views/views.xml',          # BAD: absolute path
    '../other_module/file.xml',  # BAD: other module
],
```

---

## Assets

### assets

```python
'assets': {
    'web.assets_frontend': [
        'my_module/static/src/js/main.js',
        'my_module/static/src/scss/style.scss',
    ],
    'web.assets_backend': [
        'my_module/static/src/js/backend.js',
    ],
    'web.assets_tests': [
        'my_module/static/tests/js/test.js',
    ],
},
```

### Asset Bundles

| Bundle | Description |
|--------|-------------|
| `web.assets_frontend` | Website frontend assets |
| `web.assets_backend` | Backend interface assets |
| `web.assets_tests` | Test assets |
| `web.assets_common` | Common assets (rarely used) |

### Asset Paths

```python
'assets': {
    'web.assets_frontend': [
        # JavaScript files
        'my_module/static/src/js/module.js',
        'my_module/static/src/xml/component.xml',  # OWL templates

        # CSS/SCSS files
        'my_module/static/src/scss/main.scss',
        'my_module/static/src/css/custom.css',

        # External files (rare)
        'https://cdn.example.com/library.js',
    ],
}
```

### Module-specific Assets

```python
'assets': {
    'web.assets_frontend': [
        'my_module/static/src/js/*.js',
        'my_module.static.src.scss.*',  # Note: different format
    ],
    'my_module.assets': [
        'my_module/static/lib/library.js',
    ],
}
```

---

## External Dependencies

### external_dependencies

```python
'external_dependencies': {
    'python': [
        'requests',
        'python-dateutil',
        'openpyxl',
    ],
    'bin': [
        'wkhtmltopdf',
        'pdftk',
    ],
}
```

### Python Dependencies

```python
'external_dependencies': {
    'python': [
        'requests',           # pip install requests
        'gevent',             # pip install gevent
        'Pillow',             # pip install Pillow
    ],
}
```

Module installation will **fail** if Python package not available.

### Binary Dependencies

```python
'external_dependencies': {
    'bin': [
        'wkhtmltopdf',        # Must be in PATH
        'ffmpeg',             # Must be in PATH
        'curl',               # Must be in PATH
    ],
}
```

Module installation will **fail** if binary not found in PATH.

---

## Hooks

### Hook Functions

```python
'pre_init_hook': 'module_pre_init',
'post_init_hook': 'module_post_init',
'uninstall_hook': 'module_uninstall',
```

### pre_init_hook

```python
'pre_init_hook': 'pre_init_function',
```

Executed **before** module installation.

```python
# __init__.py
def pre_init_function(env):
    """Create tables before module install"""
    env.cr.execute("""
        CREATE TABLE IF NOT EXISTS my_custom_table (
            id SERIAL PRIMARY KEY,
            name VARCHAR(100)
        )
    """)
```

### post_init_hook

```python
'post_init_hook': 'post_init_function',
```

Executed **after** module installation.

```python
# __init__.py
def post_init_function(env):
    """Set up data after module install"""
    # Create default records
    env['my.model'].create({
        'name': 'Default Record',
    })

    # Configure settings
    config = env['ir.config_parameter'].sudo()
    config.set_param('my_module.key', 'value')
```

### uninstall_hook

```python
'uninstall_hook': 'uninstall_function',
```

Executed **after** module uninstallation.

```python
# __init__.py
def uninstall_function(env):
    """Clean up after module uninstall"""
    # Drop custom tables
    env.cr.execute("DROP TABLE IF EXISTS my_custom_table")

    # Clean up settings
    env['ir.config_parameter'].sudo().search([
        ('key', 'like', 'my_module.%')
    ]).unlink()
```

### Hook Signatures

All hooks receive `env` (Environment):

```python
def my_hook(env):
    # env: Odoo Environment
    # Use: env['model'], env.cr, etc.
    pass
```

---

## Other Fields

### application

```python
'application': True,
```

Whether module is a full application (vs technical module).

```python
# Technical module (default)
'application': False,  # or omit

# Full application
'application': True,
```

Applications appear in Apps menu separately.

### installable

```python
'installable': True,
```

Whether users can install from UI.

```python
# Default: can be installed
'installable': True,

# Prevent installation (for development/unstable modules)
'installable': False,
```

### maintainer

```python
'maintainer': 'Maintainer Name',
```

Person/entity maintaining the module (defaults to `author` if not set).

### series

```python
'series': '18.0',
```

Odoo version series (deprecated, use directory structure instead).

---

## Complete Example

### Full Manifest

```python
#!/usr/bin/env python
# -*- coding: utf-8 -*-

{
    # == Identification ==
    'name': 'Business Trip Management',
    'version': '1.0.0',
    'category': 'Tools/Trip Management',
    'summary': 'Manage business trips and expenses',
    'description': """
Business Trip Management
=======================

This module allows you to:
* Create and manage business trips
* Track expenses related to trips
* Send email notifications to participants
* Generate trip reports

Features
---------
* Trip planning and management
* Expense tracking with receipts
* Email aliases for expense submission
* Activity management for trip tasks
    """,
    'author': 'My Company',
    'website': 'https://www.example.com',
    'license': 'LGPL-3',
    'maintainer': 'John Doe <john@example.com>',

    # == Dependencies ==
    'depends': [
        'base',
        'mail',
        'web',
        'web_kanban',
        'portal',
    ],
    'auto_install': False,

    # == Data ==
    'data': [
        # Security
        'security/business_trip_security.xml',
        'security/ir.model.access.csv',

        # Views
        'views/business_trip_views.xml',
        'views/expense_views.xml',
        'views/business_trip_templates.xml',

        # Data
        'data/business_trip_data.xml',
        'data/ir_cron_data.xml',

        # Reports
        'report/trip_report_views.xml',
        'report/trip_report_templates.xml',

        # Wizards
        'wizard/trip_wizard_views.xml',

        # Demo (only in demo mode)
        'demo/business_trip_demo.xml',
    ],

    # == Assets ==
    'assets': {
        'web.assets_backend': [
            'business_trip/static/src/js/trip_form.js',
            'business_trip/static/src/xml/trip_qweb.xml',
            'business_trip/static/src/scss/trip.scss',
        ],
        'web.assets_frontend': [
            'business_trip/static/src/js/portal_trip.js',
        ],
    },

    # == External Dependencies ==
    'external_dependencies': {
        'python': [
            'requests',      # For external API calls
            'python-dateutil',
        ],
        'bin': [
            'wkhtmltopdf',   # For reports
        ],
    },

    # == Hooks ==
    'pre_init_hook': 'pre_init_business_trip',
    'post_init_hook': 'post_init_business_trip',
    'uninstall_hook': 'uninstall_business_trip',

    # == Configuration ==
    'application': False,
    'installable': True,

    # == Version Info ==
    'post_init_hook': 'post_init_business_trip',
}
```

### With Hook Implementation

```python
# __init__.py
# -*- coding: utf-8 -*-

def pre_init_business_trip(env):
    """Create custom table before install"""
    env.cr.execute("""
        CREATE TABLE IF NOT EXISTS business_trip_log (
            id SERIAL PRIMARY KEY,
            trip_id INTEGER NOT NULL,
            message TEXT,
            create_date TIMESTAMP DEFAULT NOW()
        )
    """)

def post_init_business_trip(env):
    """Set up default configuration"""
    # Create default trip type
    env['business.trip.type'].create({
        'name': 'General',
        'code': 'GEN',
    })

    # Configure settings
    config = env['ir.config_parameter'].sudo()
    config.set_param('business_trip.auto_confirm', False)

def uninstall_business_trip(env):
    """Clean up on uninstall"""
    # Drop custom table
    env.cr.execute("DROP TABLE IF EXISTS business_trip_log")

    # Clean up parameters
    env['ir.config_parameter'].sudo().search([
        ('key', 'like', 'business_trip.%')
    ]).unlink()
```

---

## Quick Reference

### Minimal Manifest

```python
{
    'name': 'My Module',
    'version': '1.0',
    'depends': ['base'],
    'installable': True,
}
```

### Common Patterns

#### Web Module

```python
{
    'name': 'My Website Module',
    'depends': ['website'],
    'data': [
        'views/templates.xml',
    ],
    'assets': {
        'web.assets_frontend': [
            'my_module/static/src/js/main.js',
            'my_module/static/src/scss/style.scss',
        ],
    },
}
```

#### Module with Mail

```python
{
    'name': 'My Mail Module',
    'depends': ['mail'],
    'data': [
        'views/views.xml',
        'data/mail_template_data.xml',
    ],
}
```

#### Portal Module

```python
{
    'name': 'My Portal Module',
    'depends': ['portal', 'web'],
    'data': [
        'views/portal_templates.xml',
    ],
}
```

#### With External Libraries

```python
{
    'name': 'My API Module',
    'external_dependencies': {
        'python': ['requests', 'oauthlib'],
        'bin': ['curl'],
    },
}
```

---

**For more Odoo 18 guides, see [SKILL.md](../SKILL.md)**

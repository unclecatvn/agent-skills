# Odoo 19 Manifest Guide

Guide for configuring `__manifest__.py` in Odoo 19 modules.

## Table of Contents
- [Manifest File](#manifest-file)
- [Required Fields](#required-fields)
- [Module Information](#module-information)
- [Dependencies](#dependencies)
- [Data Files](#data-files)
- [Assets](#assets)
- [Hooks](#hooks)
- [External Dependencies](#external-dependencies)
- [Auto-Install](#auto-install)

---

## Manifest File

The manifest file declares a python package as an Odoo module and specifies module metadata.

File: `__manifest__.py`

```python
{
    'name': "A Module",
    'version': '1.0',
    'depends': ['base'],
    'author': "Author Name",
    'category': 'Category',
    'description': """
    Description text
    """,
    'data': [
        'views/mymodule_view.xml',
    ],
    'demo': [
        'demo/demo_data.xml',
    ],
}
```

---

## Required Fields

### name (str, required)

The human-readable name of the module.

```python
'name': "My Module",
```

---

## Module Information

### version (str)

Module version, should follow semantic versioning rules.

```python
'version': '1.0.0',
```

### description (str)

Extended description in reStructuredText.

```python
'description': """
This module does something useful.
""",
```

### author (str)

Name of the module author.

```python
'author': "UncleCat",
```

### website (str)

Website URL for the module author.

```python
'website': "https://github.com/unclecat",
```

### license (str, default: LGPL-3)

Distribution license.

Possible values:
- `GPL-2`
- `GPL-2 or any later version`
- `GPL-3`
- `GPL-3 or any later version`
- `AGPL-3`
- `LGPL-3`
- `Other OSI approved licence`
- `OEEL-1` (Odoo Enterprise Edition License v1.0)
- `OPL-1` (Odoo Proprietary License v1.0)
- `Other proprietary`

```python
'license': 'LGPL-3',
```

### category (str, default: Uncategorized)

Classification category within Odoo.

Use existing categories or create hierarchies with `/`:

```python
'category': 'Tools / My Category',
```

### application (bool, default: False)

Whether the module should be considered a fully-fledged application.

```python
'application': True,  # Appears in Apps menu
```

### installable (bool, default: True)

Whether a user can install the module from the Web UI.

```python
'installable': False,  # Hidden from Apps menu
```

### maintainer (str)

Person or entity in charge of maintenance.

```python
'maintainer': "UncleCat",
```

---

## Dependencies

### depends (list(str))

Odoo modules which must be loaded before this one.

```python
'depends': ['base', 'web', 'sale'],
```

**Important**: Module `base` is always installed, but you should still specify it as a dependency to ensure your module is updated when `base` is updated.

When a module is installed, all dependencies are installed first.

---

## Data Files

### data (list(str))

Data files always loaded at installation and update.

```python
'data': [
    'security/my_module_security.xml',
    'views/my_model_views.xml',
    'data/my_module_data.xml',
],
```

### demo (list(str))

Data files only loaded in demonstration mode.

```python
'demo': [
    'demo/demo_data.xml',
],
```

---

## Assets

### assets (dict)

Definition of how static files are loaded in asset bundles.

```python
'assets': {
    'web.assets_backend': [
        'my_module/static/src/js/my_script.js',
        'my_module/static/src/scss/my_style.scss',
    ],
    'web.assets_frontend': [
        'my_module/static/src/js/frontend.js',
    ],
},
```

---

## Hooks

### {pre_init, post_init, uninstall}_hook (str)

Hooks for module installation/uninstallation.

```python
# In __init__.py
def pre_init_hook(env):
    """Executed prior to module installation"""
    pass

def post_init_hook(env):
    """Executed right after module installation"""
    pass

def uninstall_hook(env):
    """Executed after module uninstallation"""
    pass
```

```python
# In __manifest__.py
'pre_init_hook': 'pre_init_hook',
'post_init_hook': 'post_init_hook',
'uninstall_hook': 'uninstall_hook',
```

**Usage**: Only when setup/cleanup is extremely difficult or impossible through the API.

---

## External Dependencies

### external_dependencies (dict(key=list(str)))

Dictionary of Python and binary dependencies.

```python
'external_dependencies': {
    'python': ['requests', 'openpyxl'],
    'bin': ['zip', 'unzip'],
},
```

The module won't be installed if dependencies are not available.

---

## Auto-Install

### auto_install (bool or list(str), default: False)

If `True`, automatically installs if all dependencies are installed.

Used for "link modules" implementing integration between independent modules.

```python
'auto_install': True,  # Install when all dependencies are present
```

If it is a list, must contain a subset of dependencies:

```python
'auto_install': ['sale', 'crm'],  # Install when both sale and crm are present
```

If the list is empty, always auto-install regardless of dependencies.

```python
'auto_install': [],  # Always install
```

---

## Complete Example

```python
{
    'name': "My Awesome Module",
    'version': '1.0.0',
    'category': 'Tools',
    'summary': 'Does something awesome',
    'description': """
My Awesome Module
=================

This module adds awesome functionality to Odoo.
""",
    'author': "UncleCat",
    'website': "https://github.com/unclecat/my_module",
    'license': 'LGPL-3',
    'depends': ['base', 'web'],
    'data': [
        'security/my_module_security.xml',
        'views/my_model_views.xml',
        'data/ir_cron_data.xml',
    ],
    'demo': [
        'demo/demo_data.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'my_module/static/src/js/my_widget.js',
            'my_module/static/src/scss/my_style.scss',
        ],
    },
    'external_dependencies': {
        'python': ['requests'],
    },
    'application': True,
    'installable': True,
    'auto_install': False,
}
```

---

## References

- Source: Odoo 19 documentation `/doc/developer/reference/backend/module.rst`

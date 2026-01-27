---
name: odoo-18-translation
description: Complete guide for Odoo 18 translations and localization. Covers Python translations with _() and _lt(), JavaScript/OWL translations with _t(), QWeb template translations, field translations with translate=True, PO file structure, translation export/import, language management, and translation term loading.
globs: "**/*.{py,js,xml}"
topics:
  - Python translations (_ and _lt)
  - JavaScript translations (_t)
  - QWeb template translations
  - Field translations (translate=True)
  - PO file structure
  - Translation export/import
when_to_use:
  - Adding translatable strings to Python code
  - Adding translations to JavaScript/OWL components
  - Creating translatable QWeb templates
  - Setting up translated fields
  - Exporting/importing translations
---

# Odoo 18 Translation & Localization Guide

Complete guide for translating and localizing Odoo 18 modules.

## Quick Reference

| Context | Function | Example |
|---------|----------|---------|
| Python code | `_()` | `_("Hello World")` |
| Python module constants | `_lt()` | `TITLE = _lt("Module Title")` |
| JavaScript/OWL | `_t()` | `_t("Hello World")` |
| Field definition | `translate=True` | `name = fields.Char(translate=True)` |

---

## Table of Contents

1. [Python Translations](#python-translations)
2. [Field Translations](#field-translations)
3. [QWeb Template Translations](#qweb-template-translations)
4. [JavaScript/OWL Translations](#javascriptowl-translations)
5. [Module Translation Structure](#module-translation-structure)
6. [Translation Export/Import](#translation-exportimport)
7. [Language Management](#language-management)
8. [Translation Types](#translation-types)
9. [Best Practices](#best-practices)
10. [Anti-Patterns](#anti-patterns)

---

## Python Translations

### Standard Translation Function

**File:** `odoo/tools/translate.py`

```python
from odoo.tools.translate import _

# Simple translation
message = _("Hello World")

# With formatting (positional)
message = _("Hello %s", user.name)

# With formatting (named)
message = _("Hello %(name)s, you have %(count)d messages",
            name=user.name, count=5)
```

### Lazy Translation (Module Constants)

For module-level constants that should be translated lazily:

```python
from odoo.tools.translate import LazyTranslate

_lt = LazyTranslate(__name__)

# Module-level constants
MODULE_NAME = _lt("My Module Name")
TITLE_USER = _lt("User")
LABEL_CONFIRM = _lt("Confirm")

# Usage later - translation happens at display time
def get_title(self):
    return MODULE_NAME  # Translated when displayed
```

**When to use `_lt()`:**
- Module-level constants
- Class-level attributes
- Default values for fields
- Any string defined outside of methods

### Translation with Context

Provide context for translators using comments:

```python
# Button label (verb)
_(_t("Export"))

# File format (noun)
_("CSV")

# For ambiguous terms, add context
_("Delete", context="verb")  # To remove something
_("Delete", context="noun")  # A deletion record
```

---

## Field Translations

### Simple Field Translation

```python
class MyModel(models.Model):
    _name = 'my.model'
    _description = 'My Model'

    # Entire field value is translated
    name = fields.Char(string='Name', translate=True)
    description = fields.Text(string='Description', translate=True)
    notes = fields.Html(string='Notes', translate=html_translate)
```

**Storage:** Translations stored as JSONB in database:
```json
{
    "en_US": "Product",
    "fr_FR": "Produit",
    "es_ES": "Producto"
}
```

### Field Labels and Help

Field `string` and `help` attributes are automatically translatable:

```python
# These are automatically extracted for translation
status = fields.Selection([
    ('draft', 'Draft'),
    ('confirmed', 'Confirmed'),
    ('done', 'Done'),
], string='Status', help='Document status')
```

### Term-by-Term Translation

For HTML/XML content with translatable terms inside:

```python
from odoo.tools.translate import html_translate

# Each translatable term is translated separately
description = fields.Html(
    'Description',
    translate=html_translate
)
```

### Accessing Field Translations

```python
# Get translations for a specific field
translations, context = record.get_field_translations('name')
# Returns: [{'lang': 'fr_FR', 'source': 'Name', 'value': 'Nom'}, ...]

# Update field translations
record._update_field_translations('name', {
    'fr_FR': 'Nom',
    'es_ES': 'Nombre'
})
```

---

## QWeb Template Translations

### Translatable Content

**File:** `odoo/tools/translate.py` (Lines 153-196)

**Translatable Elements:** `span`, `div`, `p`, `h1`-`h6`, `button`, `b`, `i`, `strong`, `em`, `small`, `text`, `option`, etc.

**Translatable Attributes:** `string`, `placeholder`, `title`, `alt`, `help`, `confirm`, `aria-label`, `data-tooltip`, etc.

### Basic QWeb Translation

```xml
<template xml:space="preserve">
    <!-- Text content is automatically translatable -->
    <div>
        <p>This text will be extracted for translation</p>
        <h2>Welcome to Odoo</h2>
    </div>

    <!-- Using JavaScript _t in templates -->
    <span t-esc="_t('Translate me')"/>

    <!-- String attributes are translatable -->
    <button string="Click Me"/>
    <field name="name" string="Name" placeholder="Enter name"/>

    <!-- Help text -->
    <field name="email" help="Email address for notifications"/>
</template>
```

### Disable Translation

```xml
<!-- Disable translation for specific content -->
<span class="fa fa-warning" t-translation="off">&nbsp;</span>

<!-- Code/technical content -->
<code t-translation="off">user_id</code>
```

### QWeb with Formatting

```xml
<!-- Variables are NOT translated -->
<div>
    Hello <t t-esc="user.name"/>,
    you have <t t-esc="message_count"/> new messages.
</div>

<!-- For mixed content, split into translatable parts -->
<div>
    <t t-esc="_t('Hello %(name)s', name=user.name)"/>
    <t t-esc="_t('You have %(count)d messages', count=message_count)"/>
</div>
```

### Translatable Attributes

```xml
<!-- All these attributes are automatically translatable -->
<button string="Save" confirm="Are you sure?"/>
<field name="email" placeholder="email@example.com"/>
<span class="fa fa-info-circle"
      title="Information"
      data-tooltip="More details"/>
<input aria-label="Search"/>
```

### OWL Component Attributes

```xml
<!-- OWL components with .translate suffix -->
<Component title.translate="Some title"/>
<button label.translate="Click me"/>
```

---

## JavaScript/OWL Translations

### Translation Function

**File:** `addons/web/static/src/core/l10n/translation.js`

```javascript
import { _t } from "@web/core/l10n/translation";

// Simple translation
const message = _t("Good morning");

// With positional argument
const msg = _t("Good morning %s", userName);

// With named arguments
const formatted = _t("Hello %(name)s, you have %(count)d new messages", {
    name: user.name,
    count: messageCount
});
```

### In OWL Components

```javascript
/** @odoo-module **/
import { Component, useState } from "@owl/swidget";
import { _t } from "@web/core/l10n/translation";

class MyComponent extends Component {
    static template = "my_module.MyComponent";

    setup() {
        this.state = useState({
            title: _t("My Component Title"),
            message: _t("Loading...")
        });
    }

    showMessage() {
        this.displayNotification({
            message: _t("Operation completed successfully"),
            type: 'success',
        });
    }
}
```

### Lazy Translations

```javascript
// Translation happens when the value is converted to string
const lazyText = new LazyTranslatedString("Hello", []);

// Later...
console.log(`${lazyText}`); // Translated at this point
```

### Translation with Markup

```javascript
import { markup } from "@odoo/owl";

// HTML-safe markup in translations
const message = _t("I love %s", markup("<b>Odoo</b>"));
// Result: "I love <b>Odoo</b>" (HTML preserved)
```

---

## Module Translation Structure

### Directory Structure

```
my_module/
├── i18n/
│   ├── my_module.pot       # Template (source strings)
│   ├── fr.po              # French translations
│   ├── de.po              # German translations
│   ├── vi.po              # Vietnamese translations
│   └── i18n_extra/        # Optional additional translations
│       └── fr_BE.po       # Belgian French override
├── models/
│   └── my_model.py        # Python with _("text")
├── static/
│   └── src/
│       ├── js/
│       │   └── my_script.js    # JS with _t("text")
│       └── xml/
│           └── my_template.xml # QWeb templates
```

### PO File Format

**Example:** `i18n/fr.po`

```po
# Translation of Odoo Server
# This file contains the French translations
msgid ""
msgstr ""
"Project-Id-Version: Odoo Server 18.0\n"
"Report-Msgid-Bugs-To: \n"
"POT-Creation-Date: 2024-01-01 12:00+0000\n"
"PO-Revision-Date: 2024-01-01 12:00+0000\n"
"Last-Translator: \n"
"Language-Team: \n"
"Language: fr_FR\n"
"MIME-Version: 1.0\n"
"Content-Type: text/plain; charset=UTF-8\n"
"Content-Transfer-Encoding: 8bit\n"

#. module: my_module
#. odoo-python
#: code:addons/my_module/models/my_model.py:45
msgid "Code Lazy, English"
msgstr "Code Lazy, Français"

#. module: my_module
#: model:ir.model.fields,field_description:my_module.field_my_model__name
msgid "Name"
msgstr "Nom"

#. module: my_module
#. odoo-javascript
#: static/src/js/my_script.js:23
msgid "Save"
msgstr "Enregistrer"

#. module: my_module
#: model:ir.model,name:model_my_model
msgid "My Model"
msgstr "Mon Modèle"
```

### Translation Comments

```po
#. odoo-python       # Python code translation (_() or _lt())
#. odoo-javascript    # JavaScript translation (_t())
# model:ir.model,name:model_my_model
# model:ir.ui.view,view_id:view_my_form
```

### Language Fallback

Odoo automatically falls back through language variants:

```
fr_BE (Belgian French)
  ↓ (not found)
fr_419 (French generic)
  ↓ (not found)
fr (French base)
  ↓ (not found)
en_US (English - default)
```

---

## Translation Export/Import

### Export Translations via UI

1. Go to **Settings** → **Translations** → **Export Terms**
2. Select language
3. Choose format: PO, CSV, or TGZ
4. Select modules to export
5. Download file

### Export Translations via Code

```python
# File: odoo/tools/translate.py
from odoo.tools.translate import trans_export

import io

buffer = io.BytesIO()
trans_export(
    lang='fr_FR',
    modules=['my_module'],
    buffer=buffer,
    format='po',
    cr=self.env.cr
)

# Save to file
with open('/tmp/my_module-fr.po', 'wb') as f:
    f.write(buffer.getvalue())
```

### Import Translations via UI

1. Go to **Settings** → **Translations** → **Import Terms**
2. Select or create language
3. Upload PO file
4. Choose overwrite option

### Import Translations via Code

```python
from odoo.tools.translate import TranslationImporter

translation_importer = TranslationImporter(self.env.cr)

# Load from file
translation_importer.load_file(
    filepath='/path/to/i18n/fr.po',
    lang='fr_FR'
)

# Or load from file object
with open('/path/to/i18n/fr.po', 'rb') as f:
    translation_importer.load(f, fileformat='po', lang='fr_FR')

# Save to database
translation_importer.save(overwrite=True)
```

### Updating Translations

After adding new translatable strings:

```bash
# Update POT file with new strings
./odoo-bin -c odoo.conf -d my_db --i18n-export=my_module/i18n/my_module.pot --addons-path=addons,custom_addons --modules=my_module
```

---

## Language Management

### Language Model

**File:** `odoo/addons/base/models/res_lang.py`

```python
class Lang(models.Model):
    _name = 'res.lang'
    _description = 'Languages'

    name = fields.Char(required=True)           # Display name
    code = fields.Char(string='Locale Code', required=True)  # en_US, fr_FR
    iso_code = fields.Char(string='ISO code')   # en, fr
    url_code = fields.Char(required=True)       # en-us, fr-fr
    active = fields.Boolean()
    direction = fields.Selection([
        ('ltr', 'Left-to-Right'),
        ('rtl', 'Right-to-Left')
    ])
    date_format = fields.Char(required=True)
    time_format = fields.Char(required=True)
    week_start = fields.Selection([
        ('1', 'Monday'),
        ('7', 'Sunday')
    ])
    grouping = fields.Char(string='Separator Format')
    decimal_point = fields.Char(required=True)
    thousands_sep = fields.Char()
```

### Loading a Language

```python
from odoo.addons.base.models.res_lang import Lang

# Activate a language
Lang._activate_lang('vi_VN')

# Or create if not exists
if not Lang.search_count([('code', '=', 'vi_VN')]):
    Lang._create_lang('vi_VN')

# Load translation terms for a language
self.env['ir.module.module']._load_module_terms(
    modules=['my_module'],
    langs=['vi_VN'],
    overwrite=False
)
```

### Get Installed Languages

```python
# Get all active languages
languages = self.env['res.lang'].get_installed()
# Returns: [{'code': 'en_US', 'name': 'English'}, ...]

# Get current user language
current_lang = self.env.lang or 'en_US'
```

### Language Context

```python
# Override language for specific operations
records.with_context(lang='fr_FR').name  # Returns French value

# In methods
def print_name(self):
    lang = self.env.context.get('lang', 'en_US')
    print(f"Language: {lang}")
```

---

## Translation Types

### Type: "code"

**Used for:** Python code strings (`_()`, `_lt()`) and JavaScript strings (`_t()`)

**Storage:** Loaded from PO files into memory at runtime

**Location in PO file:**
```po
#. odoo-python
#: code:addons/my_module/models.py:42
msgid "Translate me"
msgstr ""
```

### Type: "model"

**Used for:** Simple field translations (`translate=True`)

**Storage:** JSONB in database column

**Example:**
```python
name = fields.Char(translate=True)
# Stored as: {"en_US": "Name", "fr_FR": "Nom"}
```

### Type: "model_terms"

**Used for:** Term-based field translations (callable translate)

**Storage:** JSONB with individual term translations

**Example:**
```python
description = fields.Html(translate=html_translate)
# Stored as: {"en_US": "<p>Hello</p>", "fr_FR": "<p>Bonjour</p>"}
```

---

## Best Practices

### DO: Use Formatting for Dynamic Content

```python
# GOOD
message = _("Hello %(name)s, welcome to %(app)s", name=user.name, app="Odoo")
```

### DON'T: Concatenate Translated Strings

```python
# BAD - Grammar differs between languages
message = _("Hello") + " " + user.name + ", " + _("welcome")
```

### DO: Translate Complete Phrases

```python
# GOOD - Context preserved
msg = _("Delete selected records?")
```

### DON'T: Split Translatable Phrases

```python
# BAD - Loses context
msg = _("Delete") + " " + _("selected") + " " + _("records")
```

### DO: Provide Context for Ambiguous Terms

```python
# Use comments for translators
# Button label - verb
_(_t("Export"))

# Noun - file format
_("CSV")
```

### DO: Use Lazy Translation for Constants

```python
# GOOD
_lt = LazyTranslate(__name__)
STATUS_DRAFT = _lt("Draft")
STATUS_CONFIRMED = _lt("Confirmed")
```

### DON'T: Use Regular Translation for Constants

```python
# BAD - Translated at definition time (wrong language)
STATUS_DRAFT = _("Draft")
```

---

## Anti-Patterns

### ❌ Dynamic Source Strings

```python
# BAD - Cannot be extracted or translated
message = _(f"User {user.name} created")

# GOOD
message = _("User %(name)s created", name=user.name)
```

### ❌ Translated Technical Terms

```python
# BAD - Technical IDs should not be translated
xml_id = _("my_module.my_record")

# GOOD
xml_id = 'my_module.my_record'
```

### ❌ Conditional Inside Translation

```python
# BAD
if condition:
    msg = _("Success")
else:
    msg = _("Failure")

# GOOD - Different messages for different cases
msg = _("Operation %(status)s", status='success' if condition else 'failed')
```

### ❌ Translation in Loops

```python
# BAD - Performance issue
for record in records:
    name = _(record.name)  # Lookup each time

# GOOD - Translate once
label = _("Name")
for record in records:
    print(f"{label}: {record.name}")
```

### ❌ HTML in Python Translations

```python
# BAD - HTML should be in QWeb templates
message = _("<strong>Error:</strong> Invalid input")

# GOOD
message = _("Error: Invalid input")  # Format in QWeb
```

---

## Translation Testing

### Test Translations in Different Languages

```python
# Switch language context
def test_translations(self):
    # Test in French
    records_fr = self.records.with_context(lang='fr_FR')
    self.assertEqual(records_fr.name, "Nom Français")

    # Test in Vietnamese
    records_vi = self.records.with_context(lang='vi_VN')
    self.assertEqual(records_vi.name, "Tên Tiếng Việt")
```

### Test Translation Loading

```python
def test_translation_loaded(self):
    # Ensure translations are loaded
    self.env['ir.module.module']._load_module_terms(
        modules=['my_module'],
        langs=['fr_FR']
    )

    # Check translation exists
    translations = self.env['ir.translation'].search([
        ('module', '=', 'my_module'),
        ('lang', '=', 'fr_FR'),
        ('src', '=', 'Source String')
    ])
    self.assertTrue(translations)
    self.assertEqual(translations.value, 'Chaîne traduite')
```

---

## Key Files Reference

| Purpose | File |
|---------|------|
| Core translation system | `odoo/tools/translate.py` |
| Field definitions | `odoo/fields.py` |
| Model translation methods | `odoo/models.py` |
| Language model | `odoo/addons/base/models/res_lang.py` |
| JS translation utilities | `addons/web/static/src/core/l10n/translation.js` |
| Translation web controller | `addons/web/controllers/webclient.py` |
| Export wizard | `odoo/addons/base/wizard/base_export_language.py` |
| Import wizard | `odoo/addons/base/wizard/base_import_language.py` |
| Translation tests | `odoo/addons/base/tests/test_translate.py` |
| Base translation template | `odoo/addons/base/i18n/base.pot` |

---

## Quick Checklist

When adding translatable content:

- [ ] Python strings: Use `_()` for runtime, `_lt()` for constants
- [ ] JavaScript strings: Use `_t()`
- [ ] Field values: Add `translate=True` parameter
- [ ] QWeb templates: Text content is auto-translatable
- [ ] Provide context for ambiguous terms
- [ ] Use formatting for dynamic content
- [ ] Don't concatenate translated strings
- [ ] Update POT file after adding new strings
- [ ] Test in multiple languages
- [ ] Check RTL language support if needed

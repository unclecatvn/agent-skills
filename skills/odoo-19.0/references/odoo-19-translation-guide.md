# Odoo 19 Translation Guide

## Coding Conventions

- Translate literal source strings with parameters, never dynamically built strings.
- Use `_()` for immediate Python translations and `_t()` in JavaScript; pass
  values as interpolation parameters rather than concatenating translated text.
- Keep technical identifiers and markup outside translatable strings unless
  they are part of the user-visible message.

Guide for adding translations and localization in Odoo 19: Python, JavaScript, and QWeb templates.

## Table of Contents

- [Translation Overview](#translation-overview)
- [Python Translations](#python-translations)
- [JavaScript Translations](#javascript-translations)
- [QWeb Translations](#qweb-translations)
- [Translated Fields](#translated-fields)
- [Export/Import](#exportimport)
- [Languages](#languages)
- [Quick Checklist](#quick-checklist)

---

## Translation Overview

Odoo supports multi-language through:

- Python `_()` function
- JavaScript `_t()` function
- Translatable fields
- QWeb translation mechanisms

### Supported File Formats

| Format | Use                           |
| ------ | ----------------------------- |
| `.po`  | Portable Object (main format) |
| `.pot` | Portable Object Template      |
| `.csv` | For some data imports         |

---

## Python Translations

### Basic Translation

```python
from odoo import _

def my_method(self):
    message = _("Hello World")
    return message
```

### Translation with Parameters

```python
# Old style (still works)
message = _("Hello %s") % name

# New style (recommended)
message = _("Hello %(name)s") % {'name': name}
```

### Lazy Translation

```python
from odoo import _

# Lazy translation (evaluated when displayed, not when imported)
ERROR_MESSAGE = _("Error occurred")

def my_method(self):
    # ERROR_MESSAGE is translated when needed
    return {'error': ERROR_MESSAGE}
```

### Multi-Line Translation

```python
message = _(
    "This is a long message "
    "that spans multiple lines"
)
```

### Context Translation

```python
# Provide context for translators
message = _("Cancel", default_code="refund_cancel")
```

---

## JavaScript Translations

### Basic Translation

```javascript
import { _t } from "@web/core/l10n/translation";

const message = _t("Hello World");
```

### Translation with Parameters

```javascript
const message = _t("Hello %(name)s", { name: "John" });
```

### Lazy Translation

```javascript
import { lazyTranslation } from "@web/core/l10n/translation";

const lt = lazyTranslation(() => _t("Error occurred"));
```

### Class Translation

```javascript
import { _lt } from "@web/core/l10n/translation";

class MyClass {
  errorMessage = _lt("Error occurred");
}
```

---

## QWeb Translations

### Translate Static Text

```xml
<template id="my_template">
    <h1>Hello World</h1>
</template>
```

### Translate in Code

```xml
<template id="my_template">
    <h1><t t-out="translate('Hello World')"/></h1>
</template>
```

### Translate Field Content

```xml
<template id="my_template">
    <span t-field="record.name"/>
</template>
```

### Translate Template Content

```xml
<template id="my_template">
    <div>
        <p>This content is translatable</p>
    </div>
</template>
```

---

## Translated Fields

### Define Translated Field

```python
name = fields.Char(translate=True)
description = fields.Text(translate=True)
```

### Translation Options

```python
# Enable translation
name = fields.Char(translate=True)

# Translation with context (Odoo 19+)
notes = fields.Text(translate=True, translation_modifiable=True)
```

### Read Translated Field

```python
# Record is fetched in user's language
record = self.env['my.model'].browse(record_id)
print(record.name)  # Translated name
```

### Read in Specific Language

```python
# Read in French
record_fr = record.with_context(lang='fr_FR')
print(record_fr.name)  # French name
```

---

## Export/Import

Odoo 19 replaced the `--i18n-export` / `--i18n-import` server flags with the `odoo-bin i18n`
subcommand (`odoo/cli/i18n.py`). Update the module first (`-u <module>`) so new terms are in
the database, then:

### Export the template (`.pot`)

```bash
odoo-bin i18n export -c odoo.conf -d mydb my_module
# writes my_module/i18n/my_module.pot ('pot' is the default language)
```

### Export a language (`.po`)

```bash
odoo-bin i18n loadlang -c odoo.conf -d mydb -l fr_FR     # once, if not installed yet
odoo-bin i18n export -c odoo.conf -d mydb -l fr_FR my_module
# writes my_module/i18n/fr.po (named by ISO code); -o file.po merges several modules into one file
```

### Import translations

```bash
odoo-bin i18n import -c odoo.conf -d mydb -l fr_FR my_module/i18n/fr.po
# -w / --overwrite replaces terms already translated in the database
```

**Via UI**: Settings → Translations → Export Translations / Import Translations.

---

## Languages

### Install Language

```python
# Load language
language = self.env['res.lang'].load_lang(self.env.cr, self._uid, 'fr_FR')
```

### Available Languages

```python
languages = self.env['res.lang'].search([])
for lang in languages:
    print(lang.code, lang.name)
```

### Get User Language

```python
user_lang = self.env.user.lang
context_lang = self.env.context.get('lang', 'en_US')
```

---

## Translation Best Practices

### Always Use Translation Functions

```python
# GOOD
message = _("Hello World")

# BAD
message = "Hello World"
```

### Use Parameters for Dynamic Content

```python
# GOOD
message = _("Hello %(name)s") % {'name': name}

# BAD
message = _("Hello ") + name
```

### Provide Context When Needed

```python
# GOOD (with context)
message = _("Cancel", default_code="refund_cancel")

# BAD (ambiguous)
message = _("Cancel")
```

### Don't Concatenate Translations

```python
# BAD
message = _("Hello ") + name + _("!")

# GOOD
message = _("Hello %(name)s!") % {'name': name}
```

---

## Quick Checklist

When adding translatable content to an Odoo 19 module:

- [ ] Python runtime strings wrapped in `_()`, module-level constants in `_lt()`
- [ ] JavaScript/OWL strings wrapped in `_t()`
- [ ] Translatable field values declared with `translate=True` (or `html_translate`)
- [ ] `string=` / `help=` / `placeholder=` present in views (auto-extracted)
- [ ] `i18n/<module>.pot` regenerated with `odoo-bin i18n export -d <db> <module>` after `-u <module>`
- [ ] Every shipped locale has a `.po` in `i18n/` refreshed from that `.pot` (`msgmerge --update` or re-export)
- [ ] Dynamic content uses `%(name)s` placeholders, never f-strings / `+`
- [ ] Tests cover at least one non-`en_US` language switch

---

## Common Translation Terms

| English | French      | German     | Spanish  |
| ------- | ----------- | ---------- | -------- |
| Save    | Enregistrer | Speichern  | Guardar  |
| Cancel  | Annuler     | Abbrechen  | Cancelar |
| Delete  | Supprimer   | Löschen    | Eliminar |
| Edit    | Modifier    | Bearbeiten | Editar   |
| Create  | Créer       | Erstellen  | Crear    |
| Search  | Rechercher  | Suchen     | Buscar   |

---

## References

- Odoo 19 translation documentation
- GNU gettext documentation

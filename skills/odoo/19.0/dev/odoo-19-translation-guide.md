# Odoo 19 Translation Guide

Guide for adding translations and localization in Odoo 19: Python, JavaScript, and QWeb templates.

## Table of Contents
- [Translation Overview](#translation-overview)
- [Python Translations](#python-translations)
- [JavaScript Translations](#javascript-translations)
- [QWeb Translations](#qweb-translations)
- [Translated Fields](#translated-fields)
- [Export/Import](#exportimport)
- [Languages](#languages)

---

## Translation Overview

Odoo supports multi-language through:
- Python `_()` function
- JavaScript `_t()` function
- Translatable fields
- QWeb translation mechanisms

### Supported File Formats

| Format | Use |
|--------|-----|
| `.po` | Portable Object (main format) |
| `.pot` | Portable Object Template |
| `.csv` | For some data imports |

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
const message = _t("Hello %(name)s", {name: "John"});
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
    <h1><t t-esc="translate('Hello World')"/></h1>
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

### Export Translations

**Via CLI**:

```bash
odoo-bin -d mydb -l fr --i18n-export=fr --stop-after-init
```

**Via UI**:
1. Settings → Translations → Export Translations
2. Select language
3. Choose file format (PO)
4. Export

### Import Translations

**Via CLI**:

```bash
odoo-bin -d mydb -l fr --i18n-import=/path/to/fr.po --stop-after-init
```

**Via UI**:
1. Settings → Translations → Import Translations
2. Select language
3. Upload PO file
4. Import

### Update Translations

**Via CLI**:

```bash
odoo-bin -d mydb -l fr --i18n-overwrite --stop-after-init
```

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

## Common Translation Terms

| English | French | German | Spanish |
|---------|--------|--------|---------|
| Save | Enregistrer | Speichern | Guardar |
| Cancel | Annuler | Abbrechen | Cancelar |
| Delete | Supprimer | Löschen | Eliminar |
| Edit | Modifier | Bearbeiten | Editar |
| Create | Créer | Erstellen | Crear |
| Search | Rechercher | Suchen | Buscar |

---

## References

- Odoo 19 translation documentation
- GNU gettext documentation

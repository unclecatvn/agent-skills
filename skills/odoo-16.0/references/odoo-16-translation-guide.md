---
name: odoo-16-translation
description: Complete guide for Odoo 16 translations and localization. Covers Python translations with _() and _lt(), JavaScript/OWL translations with _t(), QWeb template translations, field translations with translate=True (JSONB column), PO/POT file structure, translation export/import, language management.
globs: "**/*.{py,js,xml}"
topics:
  - Python translations (_ and _lt)
  - JavaScript translations (_t)
  - QWeb template translations
  - Field translations (translate=True, JSONB storage)
  - PO / POT file structure
  - Translation export/import
  - Language / context switching
when_to_use:
  - Adding translatable strings to Python code
  - Adding translations to JavaScript/OWL components
  - Creating translatable QWeb templates
  - Setting up translated fields
  - Exporting/importing translations
  - Reading translations in a specific language
---

# Odoo 16 Translation & Localization Guide

Complete guide for translating and localizing Odoo 16 modules.

> **Odoo 16 storage model**: since Odoo 16, the legacy `ir.translation` table is **gone for model field translations**. A field declared with `translate=True` is stored as a **JSONB column** `{lang_code: value}` on the model's own table. The old `ir.translation` model has been removed in v16 - you will not find it via `self.env['ir.translation']`. "Code" translations (`_()`, `_t()`) are still loaded from PO files into memory at runtime, not stored in the database.

## Quick Reference

| Context | Function | Example |
|---------|----------|---------|
| Python code (inside method) | `_()` | `_("Hello World")` |
| Python module-level constants | `_lt()` | `TITLE = _lt("Module Title")` |
| JavaScript / OWL | `_t()` | `_t("Hello World")` |
| JavaScript lazy (alias of `_t` in v16) | `_lt()` | `const L = _lt("Later")` |
| Field definition | `translate=True` | `name = fields.Char(translate=True)` |
| HTML field term translation | `translate=html_translate` | `body = fields.Html(translate=html_translate)` |

---

## Table of Contents

1. [Python Translations](#python-translations)
2. [Field Translations](#field-translations)
3. [QWeb Template Translations](#qweb-template-translations)
4. [JavaScript / OWL Translations](#javascript--owl-translations)
5. [Module Translation Structure](#module-translation-structure)
6. [Translation Export / Import](#translation-export--import)
7. [Language Management](#language-management)
8. [Translation Types](#translation-types)
9. [Best Practices](#best-practices)
10. [Anti-Patterns](#anti-patterns)
11. [Testing Translations](#testing-translations)

---

## Python Translations

### Standard translation function `_()`

`_` is a `GettextAlias` instance defined in `odoo/tools/translate.py`; it reads the current `env.context['lang']` from the calling frame and looks up the translated string in the code translations loaded in memory.

```python
from odoo import _                        # re-export of odoo.tools.translate._
# or:
from odoo.tools.translate import _

# Simple translation
message = _("Hello World")

# Positional formatting
message = _("Hello %s", user.name)

# Named formatting
message = _(
    "Hello %(name)s, you have %(count)d messages",
    name=user.name, count=5,
)
```

Important: the source string passed to `_()` must be a **string literal**. Do not build it with f-strings or `+` or `format()` - the extractor cannot recognize dynamic strings.

```python
# BAD - not extractable
_(f"Hello {user.name}")

# GOOD - translator-friendly
_("Hello %(name)s", name=user.name)
```

### Lazy translation `_lt()` for module-level constants

When a translatable string is evaluated at import time (class attribute, module constant, Selection label default, etc.), the user's language context is not known yet. Use `_lt()` to defer the lookup until the string is actually rendered.

```python
from odoo.tools.translate import _lt

# Module-level
MODULE_NAME = _lt("My Module")
STATUS_DRAFT = _lt("Draft")
STATUS_DONE = _lt("Done")

class MyModel(models.Model):
    _name = 'my.model'
    _description = 'My Model'

    label = fields.Char(default=lambda self: str(MODULE_NAME))

    def get_status_label(self, status):
        return {'draft': STATUS_DRAFT, 'done': STATUS_DONE}[status]
```

In Odoo 16, `_lt` is a **class** (`class _lt:` in `odoo/tools/translate.py`). Each `_lt("...")` instance defers `_get_translation` until `__str__` / `__add__` etc. are called.

> There is **no `LazyTranslate(__name__)` pattern** in v16 — that shape appears in Odoo 18. In v16 you simply import `_lt` and instantiate it with the source string; the resulting object is a lazy `_lt` instance that resolves on `__str__`/`__add__`/etc.

### Where `_()` resolves language from

`GettextAlias._get_lang()` walks the call stack looking for a context:

1. If the calling frame has `self` with an `env`, use `self.env.lang`
2. If it has an `env` local, use `env.lang`
3. Otherwise fall back to `lang='en_US'` (no translation)

This means `_()` "just works" inside any model method, controller, or wizard that has `self`. For code run outside a model method (e.g. helper functions), wrap with `with_context(lang=...)` or use `_lt` + resolve later.

---

## Field Translations

### Declaring a translatable field

```python
from odoo import fields, models
from odoo.tools.translate import html_translate

class Product(models.Model):
    _name = 'my.product'
    _description = 'Product'

    # Whole-value translation: entire string replaced per language
    name = fields.Char(string='Name', translate=True)

    # Same for Text
    summary = fields.Text(translate=True)

    # HTML with term-by-term translation (translates pieces of the markup)
    description = fields.Html(translate=html_translate)
```

### Storage: JSONB per field (Odoo 16+, still used in v16)

Under the hood, `translate=True` changes the Postgres column type to `jsonb`. The JSON payload is `{lang_code: value}`:

```json
{
    "en_US": "Product",
    "fr_FR": "Produit",
    "vi_VN": "San pham"
}
```

Odoo 16 field code (`odoo/fields.py`, `_String` family):

```python
@property
def column_type(self):
    return ('jsonb', 'jsonb') if self.translate else ('varchar', pg_varchar(self.size))
```

Reading a translatable field picks the value for the current `env.context['lang']`, falling back to `en_US` if that language's key is missing. Writing to a translatable field updates the JSON key for the current language.

### Reading in a specific language

```python
# Read in French
name_fr = partner.with_context(lang='fr_FR').name

# Read in Vietnamese
name_vi = partner.with_context(lang='vi_VN').name

# Read every stored translation as a raw dict - use get_field_translations
translations, ctx = partner.get_field_translations('name')
# translations: [{'lang': 'fr_FR', 'source': 'Name', 'value': 'Nom'}, ...]
```

### Writing translations programmatically

```python
# Set the value for the current language only
partner.with_context(lang='fr_FR').name = 'Nom'

# Set multiple languages at once using update_field_translations
partner.update_field_translations('name', {
    'fr_FR': 'Nom',
    'es_ES': 'Nombre',
    'vi_VN': 'Ten',
})

# To void a translation for a lang (fallback to en_US), pass False
partner.update_field_translations('name', {'fr_FR': False})
```

`update_field_translations` and the internal `_update_field_translations` are defined on `BaseModel` in `odoo/models.py` (v16).

### Field `string` and `help` - automatic

The `string` label and `help` tooltip on every field are already marked translatable by Odoo's extractor. You do **not** need to wrap them in `_()`:

```python
state = fields.Selection(
    [('draft', 'Draft'), ('done', 'Done')],
    string='Status',
    help='Document state',
)
```

Both `'Status'`, `'Document state'`, `'Draft'`, `'Done'` end up in the `.pot` file automatically.

### Term-by-term translation via `html_translate`

When translating HTML, whole-value translation is usually wrong - you want translators to see each paragraph as a term. Use `translate=html_translate`:

```python
from odoo.tools.translate import html_translate

description = fields.Html(translate=html_translate)
```

Stored as JSONB too, but internally broken into terms during extraction and recomposed on read.

---

## QWeb Template Translations

### Text content is auto-translatable

Any text inside a translatable element in a QWeb template is extracted:

```xml
<template id="thanks_page" xml:space="preserve">
    <div>
        <h2>Thank you for your order</h2>
        <p>We will process it within 24 hours.</p>
    </div>
</template>
```

Both the heading and paragraph land in the `.pot`.

### Translatable attributes

The extractor considers these attributes translatable: `string`, `placeholder`, `title`, `alt`, `help`, `confirm`, `aria-label`, `data-tooltip`, ...

```xml
<field name="email" string="Email" placeholder="name@example.com"/>
<button string="Save" confirm="Save changes?"/>
<span title="Information" aria-label="Info"/>
```

### Disabling translation

```xml
<span t-translation="off">v16.0</span>
<code t-translation="off">user_id</code>
```

### Dynamic content

Keep the full sentence as one translatable string, not concatenated pieces:

```xml
<!-- BAD: grammatically untranslatable in many languages -->
<div>
    Hello <t t-esc="user.name"/>, you have
    <t t-esc="count"/> messages.
</div>

<!-- GOOD: single translatable sentence with named placeholders -->
<div>
    <t t-esc="_t('Hello %(name)s, you have %(count)d messages',
                 name=user.name, count=count)"/>
</div>
```

### Odoo 16 view syntax reminder

In Odoo 16 views:
- List views still use `<tree>` (not `<list>` — `<list>` arrived in v18)
- Client-side dynamic modifiers use `attrs` / `states`: `attrs="{'invisible': [('state', '=', 'done')]}"`, `attrs="{'readonly': [('locked', '=', True)]}"`, `attrs="{'required': [('type', '=', 'post')]}"`. Direct attributes like `invisible="1"` or `invisible="context.get('default_state')"` are accepted in Odoo 16, but they are static/context-time, not record-reactive client modifiers.

This matters for translators only indirectly: the `string=` attributes inside `<tree>` and on fields/buttons follow the normal extraction rules.

---

## JavaScript / OWL Translations

### Translation function `_t`

`_t` is exported from `@web/core/l10n/translation` (source: `addons/web/static/src/core/l10n/translation.js`):

```javascript
import { _t } from "@web/core/l10n/translation";

// Simple
const message = _t("Good morning");

// With sprintf-style placeholders
const msg = _t("Good morning %s", userName);

// Named placeholders (via sprintf)
const formatted = _t(
    "Hello %(name)s, you have %(count)d new messages",
    { name: user.name, count: count }
);
```

### `_lt` - alias of `_t` in Odoo 16

In v16, the JS side does not have a distinct lazy implementation. `_lt` is defined as:

```javascript
// addons/web/static/src/core/l10n/translation.js
export const _lt = (term, ...values) => _t(term, ...values);
```

However, `_t` itself returns a `LazyTranslatedString` when the translation bundle has not finished loading yet. That lazy string resolves when converted to a primitive string (`.toString()` / `.valueOf()` / template literal). So in practice:

- Use `_t(...)` everywhere in v16 JS/OWL
- Prefer `_lt(...)` for strings defined at module-top-level or as class static fields, to signal intent

```javascript
// Module-level / class static: use _lt for clarity
class MyDialog extends Component {
    static title = _lt("Confirm");
}
```

### In OWL components

```javascript
/** @odoo-module **/
import { Component, useState } from "@odoo/owl";
import { _t } from "@web/core/l10n/translation";

class MyComponent extends Component {
    static template = "my_module.MyComponent";

    setup() {
        this.state = useState({
            title: _t("My Component"),
            loading: _t("Loading..."),
        });
    }

    onSave() {
        this.notification.add(_t("Saved successfully"), { type: "success" });
    }
}
```

### Markup in translations

```javascript
import { markup } from "@odoo/owl";

const msg = _t("I love %s", markup("<b>Odoo</b>"));
// HTML preserved when injected into a template
```

### Note about loading

JS translations are shipped to the browser via `/web/webclient/translations/<lang>` (see `addons/web/controllers/webclient.py`). They are loaded once per session before the action manager starts. The `translationIsReady` `Deferred` in `translation.js` resolves when they are available.

---

## Module Translation Structure

### Directory layout

```
my_module/
|-- i18n/
|   |-- my_module.pot      # Template - EXTRACTED source strings (required!)
|   |-- fr.po              # French translation
|   |-- de.po              # German translation
|   |-- vi.po              # Vietnamese translation
|   `-- i18n_extra/        # Optional locale overrides
|       `-- fr_BE.po       # Belgian French override of fr.po
|-- models/
|   `-- my_model.py        # Python code with _() / _lt()
|-- views/
|   `-- my_model_views.xml # XML with string=, placeholder=
|-- static/
|   `-- src/
|       |-- js/
|       |   `-- my_component.js   # JS with _t()
|       `-- xml/
|           `-- my_component.xml  # OWL template
`-- __manifest__.py
```

**Rule of thumb for this project**: the `i18n/` folder MUST contain the `.pot` template, not just locale `.po` files. The `.pot` is the source of truth - translators regenerate their `.po` from it.

### `__manifest__.py` example

```python
{
    'name': 'My Module',
    'version': '16.0.1.0.0',
    'author': 'UncleCat',
    'license': 'LGPL-3',
    'depends': ['base'],
    'data': [
        'views/my_model_views.xml',
    ],
    'installable': True,
}
```

### PO file format

`i18n/fr.po`:

```po
# Translation of Odoo Server.
# This file contains the translation of the following modules:
#       * my_module
#
msgid ""
msgstr ""
"Project-Id-Version: Odoo Server 16.0\n"
"Report-Msgid-Bugs-To: \n"
"POT-Creation-Date: 2026-04-01 10:00+0000\n"
"PO-Revision-Date: 2026-04-01 10:00+0000\n"
"Last-Translator: \n"
"Language-Team: French\n"
"Language: fr\n"
"MIME-Version: 1.0\n"
"Content-Type: text/plain; charset=UTF-8\n"
"Content-Transfer-Encoding: 8bit\n"
"Plural-Forms: nplurals=2; plural=(n > 1);\n"

#. module: my_module
#. odoo-python
#: code:addons/my_module/models/my_model.py:0
#, python-format
msgid "Hello %(name)s"
msgstr "Bonjour %(name)s"

#. module: my_module
#: model:ir.model.fields,field_description:my_module.field_my_model__name
msgid "Name"
msgstr "Nom"

#. module: my_module
#. odoo-javascript
#: code:addons/my_module/static/src/js/my_component.js:0
msgid "Saved successfully"
msgstr "Enregistre avec succes"
```

Important comment markers:

- `#. odoo-python` - string from `_()` / `_lt()`
- `#. odoo-javascript` - string from `_t()`
- `#: model:ir.model.fields,...` - auto-translatable field label/help
- `#: model:ir.model,name:model_...` - auto-translatable `_description`
- `#: model:ir.ui.view,arch_db:...` - QWeb template text

### Language fallback

Odoo walks from the requested locale down to any available variant:

```
fr_BE -> fr_FR (if no fr_BE.po is loaded) -> en_US (source)
vi_VN -> vi (if vi.po present) -> en_US
```

---

## Translation Export / Import

### Generating / updating the `.pot`

This project expects a `.pot` file in `i18n/` at all times. Regenerate it after adding/removing translatable strings:

```bash
./odoo-bin -c odoo.conf \
    -d <your_db> \
    --modules=my_module \
    --i18n-export=addons/my_module/i18n/my_module.pot \
    --addons-path=addons,custom_addons
```

To export a translated `.po`:

```bash
./odoo-bin -c odoo.conf \
    -d <your_db> \
    --modules=my_module \
    --i18n-export=addons/my_module/i18n/fr.po \
    -l fr_FR
```

To import/update a `.po` into the database:

```bash
./odoo-bin -c odoo.conf \
    -d <your_db> \
    --i18n-import=addons/my_module/i18n/fr.po \
    -l fr_FR \
    --i18n-overwrite
```

### UI export / import

- **Settings -> Translations -> Export Terms**: pick language, format (PO/CSV/TGZ), modules
- **Settings -> Translations -> Import Terms**: upload PO, pick language, tick "Overwrite"

### Programmatic export

```python
import io
from odoo.tools.translate import TranslationModuleReader

buf = io.BytesIO()
reader = TranslationModuleReader(
    cr=self.env.cr,
    modules=['my_module'],
    lang='fr_FR',
)
# Iterate and write PO via polib, or call the higher-level exporter
# used by the export wizard (base/wizard/base_export_language.py).
```

### Programmatic import

```python
from odoo.tools.translate import TranslationImporter

importer = TranslationImporter(self.env.cr)
importer.load_file('/path/to/my_module/i18n/fr.po', lang='fr_FR')
importer.save(overwrite=True)
```

### Reloading after adding strings

After you add new `_()` / `_t()` / `translate=True` strings:

1. Regenerate `.pot` (`--i18n-export`)
2. Merge into existing `.po` files with `msgmerge` (or re-export from DB)
3. Translate the new `msgid` entries
4. `--i18n-import --i18n-overwrite` to push back
5. Or reinstall the module, which calls `_load_module_terms`

```python
# odoo/addons/base/models/ir_module.py
self.env['ir.module.module']._load_module_terms(
    modules=['my_module'],
    langs=['fr_FR'],
    overwrite=True,
)
```

---

## Language Management

### The `res.lang` model

Defined in `odoo/addons/base/models/res_lang.py`:

```python
class Lang(models.Model):
    _name = "res.lang"
    _description = "Languages"

    name = fields.Char(required=True)
    code = fields.Char(string='Locale Code', required=True)       # 'fr_FR'
    iso_code = fields.Char(string='ISO code')                     # 'fr'
    url_code = fields.Char('URL Code', required=True)             # 'fr'
    active = fields.Boolean()
    direction = fields.Selection(
        [('ltr', 'Left-to-Right'), ('rtl', 'Right-to-Left')],
        required=True, default='ltr',
    )
    date_format = fields.Char(required=True, default='%m/%d/%Y')
    time_format = fields.Char(required=True, default='%H:%M:%S')
    week_start = fields.Selection([...], default='7')
    grouping = fields.Char(required=True, default='[]')
    decimal_point = fields.Char(required=True, default='.')
    thousands_sep = fields.Char(default=',')
```

### Activating / creating a language

```python
Lang = self.env['res.lang']

# Activate an existing language
Lang._activate_lang('vi_VN')

# Activate-or-create
Lang._activate_lang('vi_VN') or Lang._create_lang('vi_VN')
```

### Installed languages

```python
# Returns list of (code, name) tuples for all active languages
installed = self.env['res.lang'].get_installed()
# [('en_US', 'English (US)'), ('fr_FR', 'French / Francais'), ...]

# Current user language
current_lang = self.env.lang or 'en_US'
```

### Switching language per-operation

```python
# Read translated fields in a specific language
name_fr = record.with_context(lang='fr_FR').name

# Run a whole piece of logic as if the user were French
record_fr = record.with_context(lang='fr_FR')
record_fr.action_confirm()   # any _() inside will use fr_FR
```

### Date / number / currency localization

Date and number formats come from `res.lang`:

```python
lang = self.env['res.lang']._lang_get(self.env.lang or 'en_US')

formatted_date = lang.format_date(fields.Date.today())
formatted_number = lang.format(
    '%.2f', 1234567.89, grouping=True,
)  # "1,234,567.89" or "1 234 567,89" depending on lang
```

Currency formatting goes through `res.currency`:

```python
formatted = self.currency_id.with_context(lang=self.env.lang).format(amount)
```

---

## Translation Types

### Type: `code` - Python & JavaScript

- Source: `_()`, `_lt()` in Python; `_t()`, `_lt()` in JS
- Storage: NOT in the database - loaded from PO files into the per-process code_translations cache at startup / install
- In the PO: `#. odoo-python` or `#. odoo-javascript` comment

### Type: `model` - `translate=True` whole-value

- Source: `fields.Char(translate=True)`, `fields.Text(translate=True)`
- Storage: **JSONB column on the model's table** (v16)
- PO reference: `#: model:ir.model.fields,field_description:module.field_model__fname`

### Type: `model_terms` - callable translate (e.g. `html_translate`)

- Source: `fields.Html(translate=html_translate)`
- Storage: JSONB, but each translator-visible term is a separate key in an internal dict
- Terms are extracted from the HTML with `html_translate` and recomposed on read

> There is **no `ir.translation` model in Odoo 16**. Any code you see doing `self.env['ir.translation']...` is from Odoo <= 15 and will fail on v16. Use `get_field_translations` / `update_field_translations` instead.

---

## Best Practices

### DO use named placeholders for dynamic content

```python
# GOOD
_("Hello %(name)s, welcome to %(app)s", name=user.name, app='Odoo')
```

### DON'T concatenate translated strings

```python
# BAD - unusable in languages with different grammar
msg = _("Hello") + " " + user.name + ", " + _("welcome")
```

### DO keep full sentences in one `_()`

```python
# GOOD
msg = _("Delete the selected records?")

# BAD - loses context, translators cannot know which verb form to use
msg = _("Delete") + " " + _("the selected records")
```

### DO use `_lt()` for module-level constants

```python
# GOOD
STATUS_DRAFT = _lt("Draft")
STATUS_DONE = _lt("Done")

class MyModel(models.Model):
    @api.depends('state')
    def _compute_state_label(self):
        for rec in self:
            rec.state_label = str({
                'draft': STATUS_DRAFT,
                'done': STATUS_DONE,
            }[rec.state])
```

### DON'T use `_()` at module scope

```python
# BAD - translated once at import time using whatever lang was active then
STATUS_DRAFT = _("Draft")
```

### DO commit the `.pot` file

The `i18n/<module>.pot` file is the canonical list of translatable strings for the module. Keep it up to date and commit it alongside code changes.

### DO use `with_context(lang=...)` for per-user rendering

```python
# Send a notification in the partner's own language
partner = record.partner_id
body = record.with_context(lang=partner.lang or 'en_US').message_body
```

---

## Anti-Patterns

### Dynamic source strings

```python
# BAD - extractor cannot see the string
message = _(f"User {user.name} created")

# GOOD
message = _("User %(name)s created", name=user.name)
```

### Translating technical IDs

```python
# BAD - XML IDs are not for translation
xml_id = _("my_module.my_record")

# GOOD
xml_id = 'my_module.my_record'
```

### Branching inside translation

```python
# BAD
msg = _("Success" if ok else "Failure")

# GOOD
msg = _("Success") if ok else _("Failure")
```

### Translation inside hot loops

```python
# BAD - calls _get_translation per iteration
for rec in records:
    label = _("Name")   # same value every time
    print(f"{label}: {rec.name}")

# GOOD - hoist out of the loop
label = _("Name")
for rec in records:
    print(f"{label}: {rec.name}")
```

### HTML baked into Python translations

```python
# BAD - translators have to keep HTML syntax correct
msg = _("<strong>Error:</strong> Invalid input")

# GOOD - mark up in the template, not in the string
msg = _("Error: Invalid input")
```

### Talking to `ir.translation`

```python
# BAD - will raise KeyError in Odoo 16: model does not exist
self.env['ir.translation'].search([...])

# GOOD
translations, ctx = record.get_field_translations('name')
record.update_field_translations('name', {'fr_FR': 'Nom'})
```

---

## Testing Translations

### Per-test language switch

```python
from odoo.tests.common import TransactionCase

class TestTranslation(TransactionCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env['res.lang']._activate_lang('fr_FR')

    def test_translate_field(self):
        product = self.env['my.product'].create({'name': 'Chair'})
        product.with_context(lang='fr_FR').name = 'Chaise'

        # Read back in each language
        self.assertEqual(product.with_context(lang='en_US').name, 'Chair')
        self.assertEqual(product.with_context(lang='fr_FR').name, 'Chaise')

    def test_code_translation(self):
        self.env['ir.module.module']._load_module_terms(
            modules=['my_module'],
            langs=['fr_FR'],
        )
        # _t() inside a method run in fr_FR context returns fr_FR string
        msg = self.env['my.model'].with_context(lang='fr_FR')._hello()
        self.assertEqual(msg, 'Bonjour')
```

### Asserting `get_field_translations`

```python
def test_get_field_translations(self):
    product = self.env['my.product'].create({'name': 'Chair'})
    product.update_field_translations('name', {'fr_FR': 'Chaise'})

    translations, context = product.get_field_translations('name')
    by_lang = {t['lang']: t['value'] for t in translations}

    self.assertEqual(by_lang['en_US'], 'Chair')
    self.assertEqual(by_lang['fr_FR'], 'Chaise')
    self.assertEqual(context['translation_type'], 'char')
```

---

## Quick Checklist

When adding translatable content to an Odoo 16 module:

- [ ] Python runtime strings wrapped in `_()`
- [ ] Python module-level / class-level strings wrapped in `_lt()`
- [ ] JavaScript/OWL strings wrapped in `_t()` (or `_lt()` for module-top-level)
- [ ] Translatable field values declared with `translate=True` (or `html_translate`)
- [ ] All `string=` / `help=` / `placeholder=` attributes present in views (auto-extracted)
- [ ] `i18n/<module>.pot` present and up to date
- [ ] Every shipped locale has a `.po` in `i18n/` derived from that `.pot`
- [ ] Dynamic content uses `%(name)s` placeholders, never f-string / `+`
- [ ] No `self.env['ir.translation']` usage (model removed in v16)
- [ ] Tests cover at least one non-en_US language switch

---

## Coding Conventions

- Call `_()` with a literal source string and pass values as its arguments;
  never translate a dynamically built string or format after translation.
- Prefer `%s` for one replacement and named `%(name)s` placeholders for
  several replacements so translators can safely reorder them.
- Let translatable fields translate their values. Do not wrap a field value or
  technical XML ID in `_()`.

## Key Files Reference

| Purpose | File |
|---------|------|
| Core translation logic | `odoo/tools/translate.py` |
| `_` / `_lt` Python helpers | `odoo/tools/translate.py` (`GettextAlias`, `_lt`) |
| Field type definitions (JSONB column) | `odoo/fields.py` (`_String`, `Char`, `Text`, `Html`) |
| `get_field_translations` / `update_field_translations` | `odoo/models.py` |
| Language model | `odoo/addons/base/models/res_lang.py` |
| JS translation utilities | `addons/web/static/src/core/l10n/translation.js` |
| JS translation controller | `addons/web/controllers/webclient.py` |
| Export wizard | `odoo/addons/base/wizard/base_export_language.py` |
| Import wizard | `odoo/addons/base/wizard/base_import_language.py` |
| Module term loader | `odoo/addons/base/models/ir_module.py` (`_load_module_terms`) |
| Translation tests (upstream) | `odoo/addons/base/tests/test_translate.py` |
| Base translation template | `odoo/addons/base/i18n/base.pot` |

---

## Base Code Reference

- `odoo/tools/translate.py` - `_`, `_lt`, `TranslationImporter`, `TranslationModuleReader`, `code_translations`, `html_translate`, `xml_translate`
- `odoo/fields.py` - translatable field JSONB storage (`_String.column_type`)
- `odoo/models.py` - `BaseModel.get_field_translations`, `BaseModel.update_field_translations`, `BaseModel._update_field_translations`
- `odoo/addons/base/models/res_lang.py` - `Lang._activate_lang`, `Lang._create_lang`, `Lang.get_installed`
- `odoo/addons/base/models/ir_module.py` - `Module._load_module_terms`
- `addons/web/static/src/core/l10n/translation.js` - `_t`, `_lt`, `LazyTranslatedString`

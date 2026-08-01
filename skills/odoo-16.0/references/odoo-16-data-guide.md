---
name: odoo-16-data
description: Complete reference for Odoo 16 data files - XML and CSV. Covers record/field/delete/function tags, shortcuts (menuitem, template, asset), noupdate, and value resolution (eval/ref/search/obj/file/type).
globs: "**/*.{xml,csv}"
topics:
  - XML data files structure (<odoo>, <data>)
  - record tag (create / update records)
  - field tag value resolution (eval, ref, search, obj, file, type)
  - delete tag
  - function tag (calling methods / module hooks)
  - Shortcuts (menuitem, template, asset)
  - CSV data files and :id suffix references
  - noupdate attribute
  - External IDs and module prefixes
when_to_use:
  - Authoring v16 data / demo files
  - Loading views, menus, actions, security rules
  - Populating seed data on install
  - Referencing other modules' records
---

# Odoo 16 Data Files Guide

Reference for Odoo 16 data files: XML structure, record/field/delete/function tags, shortcuts, CSV files, and value resolution.

## Table of Contents

1. [Data File Structure](#data-file-structure)
2. [External IDs](#external-ids)
3. [`<record>` Tag](#record-tag)
4. [`<field>` Tag Values (eval / ref / search / obj / type / file)](#field-tag-values)
5. [Relational Field Commands](#relational-field-commands)
6. [`<delete>` Tag](#delete-tag)
7. [`<function>` Tag](#function-tag)
8. [Shortcuts (`<menuitem>`, `<template>`, `<report>`, `<act_window>`)](#shortcuts)
9. [CSV Data Files](#csv-data-files)
10. [`noupdate` Attribute](#noupdate-attribute)
11. [Loading Order & Modes](#loading-order--modes)
12. [Quick Reference](#quick-reference)

---

## Data File Structure

Every XML data file is a well-formed XML document whose root is `<odoo>`:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<odoo>
    <!-- (Re-)loaded at install and at every module upgrade -->
    <record id="always_updatable" model="my.model">
        <field name="name">Value</field>
    </record>

    <!-- Loaded on install; skipped on upgrade -->
    <data noupdate="1">
        <record id="user_editable" model="my.model">
            <field name="name">Default</field>
        </record>
    </data>
</odoo>
```

### Accepted Top-Level Tags

The loader (`odoo/tools/convert.py`) recognises these children of `<odoo>` / `<data>`:

| Tag | Purpose |
|-----|---------|
| `<record>` | Create or update a record of an arbitrary model |
| `<delete>` | Delete records by id or by search domain |
| `<function>` | Call an arbitrary model method |
| `<menuitem>` | Shortcut to create an `ir.ui.menu` |
| `<template>` | Shortcut to create a QWeb `ir.ui.view` |
| `<report>` | Shortcut to create an `ir.actions.report` |
| `<act_window>` | Shortcut to create an `ir.actions.act_window` (legacy) |
Any other tag at the top level is silently ignored by the loader.

### File Locations

Convention-based, declared via the `data:` / `demo:` keys of `__manifest__.py`:

| Directory | When Loaded |
|-----------|-------------|
| `data/` | Always, at install and upgrade |
| `demo/` | Only when `--without-demo` is not set |
| `security/` | Typically contains `ir.model.access.csv` and record-rule XML (loaded from `data:` in the manifest) |
| `views/` | Views/menus/actions (loaded from `data:`) |

---

## External IDs

Every data record is addressed by an **external ID** (aka XML-id), stored in `ir.model.data`.

Format: `module.name`

- Inside the same module, `module.` can be omitted: `<field name="user_id" ref="admin"/>` is equivalent to `ref="<current_module>.admin"`.
- Across modules always use the full form: `ref="base.user_admin"`.
- Only **one dot** is allowed: `module.identifier` (the identifier itself must not contain a dot).

```xml
<record id="my_partner" model="res.partner">
    <field name="name">Corp</field>
</record>

<record id="my_contact" model="res.partner">
    <field name="name">Jane</field>
    <field name="parent_id" ref="my_partner"/>            <!-- same module -->
    <field name="country_id" ref="base.us"/>              <!-- cross module -->
</record>
```

---

## `<record>` Tag

```xml
<record id="partner_acme" model="res.partner">
    <field name="name">ACME Corp</field>
    <field name="is_company" eval="True"/>
    <field name="country_id" ref="base.us"/>
</record>
```

### `<record>` Attributes

| Attribute | Purpose |
|-----------|---------|
| `id` | External ID (recommended, required to make the record updatable) |
| `model` | Target model (required) |
| `context` | Extra context dict passed to create/write (rarely needed) |
| `forcecreate` | If `"0"`/`"false"` and the record does not exist during an **update** run inside a `noupdate="1"` block, skip creation instead of raising |

### Create vs. Update

The loader decides based on the existence of the external ID:

- First time the file is loaded → `create`.
- Subsequent upgrades → `write` (unless the data is protected by `noupdate="1"`).

If you re-declare only a subset of the fields, only those fields are written:

```xml
<!-- Later XML (same id) only updates `email` -->
<record id="partner_acme" model="res.partner">
    <field name="email">info@acme.test</field>
</record>
```

An empty `<record>` (no `<field>` children) produces no write.

---

## `<field>` Tag Values

A `<field>` sets one attribute of the record. Its value is resolved in the following priority:

1. `search="..."` — evaluate a domain, use the first match (or all matches for many2many).
2. `ref="..."` — resolve an external ID.
3. `eval="..."` — evaluate a Python expression.
4. Inline text (interpreted based on `type="..."`, default `char`).

### Empty Field = `False`

```xml
<field name="partner_id"/>   <!-- Sets to False -->
```

### Direct Value

```xml
<field name="name">ACME Corp</field>
<field name="ref">ACME-001</field>
```

Leading / trailing whitespace is preserved. Numeric/boolean coercion is driven by the destination field's ORM type (so `<field name="active">1</field>` writes `True` on a Boolean).

### `type="..."` — Interpretation Hints

| Type | Semantics |
|------|-----------|
| `char` (default) | Plain string |
| `int` | Integer (`None` maps to Python `None`) |
| `float` | Float |
| `xml` / `html` | Serialise child XML/HTML into the field (wraps multiple roots in a `<data>` container) |
| `file` | Stored as `"module,/path"` - validated against `addons_path` |
| `base64` | Base64-encode the bytes read from `file=` |
| `list` / `tuple` | Build a list/tuple from nested `<value>` children |

```xml
<!-- HTML body -->
<field name="description" type="html">
    <p>Read the <a href="https://odoo.com">docs</a>.</p>
</field>

<!-- Binary file loaded from a module path -->
<field name="data" type="base64" file="my_module/static/src/img/logo.png"/>

<!-- File path reference -->
<field name="image_path" type="file" name="my_module/static/src/img/photo.jpg"/>

<!-- Integer -->
<field name="priority" type="int">10</field>

<!-- List -->
<field name="tags" type="list">
    <value>alpha</value>
    <value>beta</value>
    <value eval="'gamma'"/>
</field>
```

### `eval="..."` — Python Expression

Evaluated with `safe_eval`. The evaluation context (see `convert.py::_get_idref`) includes:

| Name | Description |
|------|-------------|
| `True`, `False`, `None` | Python literals |
| `ref` | `ref('module.xmlid')` → database integer id |
| `obj` | `obj('res.partner')` → browse by model name (resolves to `env['res.partner'].browse`) |
| `Command` | `odoo.fields.Command` helpers (`Command.link`, `Command.set`, ...) |
| `time`, `datetime`, `DateTime`, `timedelta`, `relativedelta` | Date/time helpers |
| `pytz` | Timezone helper |
| `version` | Odoo major version string (e.g. `"16.0"`) |

```xml
<field name="active" eval="True"/>
<field name="amount" eval="19.95"/>
<field name="date"   eval="(datetime.date.today() + relativedelta(days=30)).strftime('%Y-%m-%d')"/>
<field name="groups_id" eval="[Command.link(ref('base.group_user'))]"/>
<field name="tag_ids"   eval="[Command.set([ref('tag_a'), ref('tag_b')])]"/>
```

### `ref="..."` — External ID Reference

Resolves an external ID to its database integer id. Works on Many2one and on any field expecting an id.

```xml
<field name="user_id" ref="base.user_admin"/>
<field name="country_id" ref="base.us"/>
```

On a **reference** (polymorphic) field, `ref` sets `"model,id"` automatically:

```xml
<field name="resource_ref" ref="base.user_admin"/>
<!-- Stored as "res.users,<id>" -->
```

### `search="..."` — Domain Search

Evaluate an ORM domain, take the result.

```xml
<record id="demo_partner" model="res.partner">
    <field name="name">Demo</field>
    <field name="country_id" search="[('code','=','US')]"/>   <!-- first match -->
    <field name="category_id" search="[('name','in',['VIP','Gold'])]"/>
    <!-- For Many2many: all matched ids become the linked set -->
</record>
```

Rules:

- Many2one: uses the first matching record.
- Many2many: uses the full set, written via `Command.set`.
- Use `use="..."` to pick a field other than `id`.

### `obj` — Browse Records in `eval`

Inside `eval`, `obj('model.name')` returns a recordset proxy. Useful for computed defaults:

```xml
<record id="seq_my_model" model="ir.sequence">
    <field name="name">My sequence</field>
    <field name="prefix">MM-</field>
    <field name="padding" eval="obj('res.company').search([], limit=1).id or 4"/>
</record>
```

### Inline File Content

```xml
<!-- File path stored as "module,path" (for fields that expect a relative path) -->
<field name="image_path" type="file" name="my_module/static/src/img/photo.png"/>

<!-- File content base64-encoded (for Binary fields) -->
<field name="icon" type="base64" file="my_module/static/description/icon.png"/>
```

---

## Relational Field Commands

Odoo 16 uses `odoo.Command` (exposed in `eval` as `Command`) or the legacy tuple form.

| Command | Tuple form | Effect |
|---------|------------|--------|
| `Command.create(values)` | `(0, 0, {values})` | Create a related record |
| `Command.update(id, values)` | `(1, id, {values})` | Update the linked record |
| `Command.delete(id)` | `(2, id, 0)` | Delete the record and unlink |
| `Command.unlink(id)` | `(3, id, 0)` | Unlink only |
| `Command.link(id)` | `(4, id, 0)` | Link (for M2M/O2M) |
| `Command.clear()` | `(5, 0, 0)` | Clear all links |
| `Command.set([ids])` | `(6, 0, [ids])` | Replace the link set |

Examples:

```xml
<!-- Replace tags (M2M) -->
<field name="category_id" eval="[Command.set([ref('cat_customer'), ref('cat_supplier')])]"/>

<!-- Add a tag without removing existing -->
<field name="category_id" eval="[Command.link(ref('cat_vip'))]"/>

<!-- Clear -->
<field name="line_ids" eval="[Command.clear()]"/>

<!-- Create inline child (O2M) -->
<field name="line_ids" eval="[
    Command.create({'name': 'Line A', 'price': 10.0}),
    Command.create({'name': 'Line B', 'price': 20.0}),
]"/>
```

Legacy tuples still work everywhere:

```xml
<field name="groups_id" eval="[(6, 0, [ref('base.group_user')])]"/>
```

### Inline O2M via Nested `<record>`

A nicer way to create children with their own external IDs:

```xml
<record id="order_demo" model="sale.order">
    <field name="partner_id" ref="base.res_partner_2"/>

    <record id="order_demo_line_1" model="sale.order.line">
        <field name="product_id" ref="product.product_product_1"/>
        <field name="product_uom_qty">1</field>
    </record>
    <record id="order_demo_line_2" model="sale.order.line">
        <field name="product_id" ref="product.product_product_2"/>
        <field name="product_uom_qty">2</field>
    </record>
</record>
```

The loader writes the parent first, then inserts each nested record with the right `inverse_name` set to the parent's id.

---

## `<delete>` Tag

Remove records at load time.

```xml
<!-- By external ID -->
<delete model="res.partner" id="legacy.partner_old"/>

<!-- By domain (removes all matching) -->
<delete model="ir.ui.menu" search="[('name','=','Obsolete')]"/>
```

`id` and `search` are mutually exclusive. If `id` does not exist the loader logs a warning and continues.

---

## `<function>` Tag

Invoke a method on a model.

```xml
<!-- With eval -> positional args list -->
<function model="res.partner" name="create"
          eval="[{'name': 'From XML', 'email': 'x@example.com'}]"/>

<!-- With explicit <value> children -->
<function model="my.module" name="setup_defaults">
    <value>arg1</value>
    <value eval="ref('base.user_admin')"/>
    <value name="company_id" eval="ref('base.main_company')"/>   <!-- becomes kwarg -->
</function>

<!-- Nested function: the inner call's result is passed as args -->
<function model="res.partner" name="write">
    <function model="res.partner" name="search"
              eval="[[('vip','=',True)]]"/>
    <value eval="{'category_id': [Command.link(ref('cat_vip'))]}"/>
</function>
```

Note: inside a `<data noupdate="1">` block, `<function>` is **skipped** except during an `init` install (`convert.py::_tag_function`). Use it for post-install hooks, cache clearing, or one-shot migrations.

---

## Shortcuts

### `<menuitem>` — ir.ui.menu Shortcut

```xml
<menuitem id="menu_root" name="My Module" sequence="10" web_icon="my_module,static/description/icon.png"/>

<menuitem id="menu_records"
          name="Records"
          parent="menu_root"
          action="action_my_records"
          sequence="1"/>

<!-- Nested (auto-creates intermediate from id of another menuitem) -->
<menuitem id="menu_reporting" parent="menu_root" name="Reporting"/>
<menuitem id="menu_report_analysis"
          parent="menu_reporting"
          action="action_report_analysis"/>

<!-- Security groups (prefix "-" to remove) -->
<menuitem id="menu_admin_only"
          name="Administration"
          parent="menu_root"
          groups="base.group_system"/>

<menuitem id="menu_regular_users"
          name="Users"
          parent="menu_root"
          groups="base.group_user,-base.group_portal"/>

<!-- Nested via XML nesting (rarely used; equivalent to parent=) -->
<menuitem id="menu_outer" name="Outer">
    <menuitem id="menu_inner" name="Inner" action="action_x"/>
</menuitem>
```

| Attribute | Description |
|-----------|-------------|
| `id` | External ID (required) |
| `name` | Label (defaults to `id` if omitted) |
| `parent` | Parent menu external ID |
| `action` | External ID of any `ir.actions.*` record |
| `sequence` | Integer; lower sorts first |
| `groups` | Comma-separated groups; prefix `-` to exclude |
| `web_icon` | `module,path/to/icon.png` — used for top-level app menus |
| `active` | `"True"` / `"False"` |

### `<template>` — QWeb ir.ui.view Shortcut

```xml
<template id="landing_page" name="Landing Page">
    <div class="container">
        <h1 t-out="title"/>
    </div>
</template>

<!-- Inheritance -->
<template id="landing_page_extra" inherit_id="my_module.landing_page">
    <xpath expr="//h1" position="after">
        <p>Extended</p>
    </xpath>
</template>

<!-- Primary (a clone rather than a modifier) -->
<template id="landing_alternative"
          inherit_id="my_module.landing_page"
          primary="True"/>

<!-- Groups, active, priority -->
<template id="admin_only" groups="base.group_system" priority="20" active="True">
    ...
</template>
```

The shortcut expands to an `ir.ui.view` record with `type="qweb"` and `arch` set to the inner XML.

### `ir.asset` records in XML

```xml
<record id="my_module_backend_asset" model="ir.asset">
    <field name="name">My Module Backend Assets</field>
    <field name="bundle">web.assets_backend</field>
    <field name="path">my_module/static/src/js/my_component.js</field>
</record>
```

Odoo 16 does not provide a top-level `<asset>` loader shortcut. When you need
XML-managed assets, declare `ir.asset` rows with normal `<record>` tags. For
most module assets, prefer the `'assets'` key in `__manifest__.py`.

### `<report>` Shortcut (Actions)

```xml
<report
    id="action_report_my_model"
    string="My Report"
    model="my.model"
    report_type="qweb-pdf"
    name="my_module.my_report_template"
    file="my_module.my_report"
    attachment_use="True"
    attachment="'Report-' + (object.name or '').replace('/', '_') + '.pdf'"
    print_report_name="'Report-%s' % (object.name)"/>
```

This expands to an `ir.actions.report` record.

---

## CSV Data Files

CSV files are the go-to format for flat, bulk data (access rights, translations, country lookups, etc.).

### Naming

The file name is `<model_with_dots_as_underscores>.csv`:

| Model | File |
|-------|------|
| `ir.model.access` | `ir.model.access.csv` |
| `res.country.state` | `res.country.state.csv` |

### Structure

- Header row: field names. `id` references the external id.
- Each subsequent row is one record.
- Use `:id` suffix on a column to look up related records by their external id.

```csv
id,country_id:id,name,code
state_us_ca,base.us,California,CA
state_us_ny,base.us,New York,NY
```

### Typical Use Cases

#### `ir.model.access.csv`

```csv
id,name,model_id:id,group_id:id,perm_read,perm_write,perm_create,perm_unlink
access_my_model_user,my.model.user,my_module.model_my_model,base.group_user,1,0,0,0
access_my_model_manager,my.model.manager,my_module.model_my_model,my_module.group_manager,1,1,1,1
```

#### Simple Master Data

```csv
id,name,code,active
tag_vip,VIP,VIP,True
tag_new,New Customer,NEW,True
```

### CSV vs XML

| CSV | XML |
|-----|-----|
| Simpler for bulk seed data | Supports all features (eval, search, type, relational commands) |
| No Python evaluation | Required for HTML blocks, complex relationships |
| Only `:id` reference shorthand | Full external-id + domain search |
| Single model per file | Multiple models per file |

---

## `noupdate` Attribute

`noupdate` controls whether records in a block are refreshed on `-u` (module update).

```xml
<odoo>
    <!-- Always refreshed on upgrade -->
    <record id="view_x_form" model="ir.ui.view">
        <field name="model">x</field>
        <field name="arch" type="xml">...</field>
    </record>

    <!-- Only inserted once (install), never overwritten -->
    <data noupdate="1">
        <record id="default_company_website" model="res.company">
            <field name="website">https://example.com</field>
        </record>
    </data>
</odoo>
```

### `noupdate` On the Record Itself

You can also set `noupdate` on a single record's `ir.model.data`:

```xml
<record id="my_partner" model="res.partner">
    <field name="name">Partner</field>
</record>
<!-- Then protect it in a second pass -->
<function model="ir.model.data" name="write" eval="[
    [ref('__ir_model_data_id_of_my_partner__')],
    {'noupdate': True},
]"/>
```

In practice you wrap records in `<data noupdate="1">`. The convenience is important for demo data and user-editable defaults.

### Recommended Defaults

| Record Kind | `noupdate` |
|-------------|-----------|
| Views, menus, actions, reports | `0` (default) |
| Scheduled jobs you want users to reconfigure | `1` |
| Default records (sequences, warehouses, journals) | `1` |
| Demo data | `1` (and inside `<data noupdate="1">`) |
| Access-control records (`ir.model.access`) | `0` — keep in sync |
| Record rules | `0` — keep in sync |

### `forcecreate`

Inside a `noupdate="1"` block, if a record referenced by id does not exist during upgrade, the loader will still create it. To opt out, add `forcecreate="0"` on the `<record>`:

```xml
<data noupdate="1">
    <record id="optional_cron" model="ir.cron" forcecreate="0">
        <field name="name">Optional Job</field>
        ...
    </record>
</data>
```

---

## Loading Order & Modes

- Files are loaded in the order declared in `__manifest__.py` (`data:` then `demo:`).
- Within a file, operations execute top-to-bottom. A later record can reference an earlier external id, but not the other way around.
- Update mode (`-u my_module`) re-runs every file but skips `noupdate="1"` blocks and `<function>` calls.
- Init mode (first install) runs everything, including `<function>` in `noupdate="1"` blocks.

### Multiple `<data>` Blocks

You can freely mix updatable and non-updatable blocks in one file:

```xml
<odoo>
    <record id="view_x_form" model="ir.ui.view">...</record>

    <data noupdate="1">
        <record id="default_config" model="res.config.settings">...</record>
    </data>

    <record id="action_x" model="ir.actions.act_window">...</record>

    <menuitem id="menu_x" name="X" action="action_x"/>
</odoo>
```

---

## Quick Reference

### `<record>` and `<field>`

```xml
<record id="external_id" model="model.name" context="{}">
    <field name="char_field">plain string</field>
    <field name="boolean" eval="True"/>
    <field name="m2o_field" ref="module.other_xmlid"/>
    <field name="m2o_field" search="[('code','=','X')]"/>
    <field name="m2m_field" eval="[Command.set([ref('a'), ref('b')])]"/>
    <field name="html_field" type="html"><p>HTML content</p></field>
    <field name="binary" type="base64" file="module/static/file.bin"/>
    <field name="file_ref" type="file" name="module/static/x.png"/>
    <field name="count" type="int">42</field>
</record>
```

### Shortcuts

```xml
<menuitem id="m1" name="Label" parent="m_root" action="act_x" sequence="10"
          groups="base.group_user"/>

<template id="tpl" name="My Template" inherit_id="parent.tpl" priority="16">
    <xpath expr="//div" position="inside"><p>Extra</p></xpath>
</template>

<asset id="bundle_x" name="Bundle">
    <bundle>web.assets_backend</bundle>
    <path>my_module/static/src/js/a.js</path>
</asset>

<report id="act_rep_x" string="My Report"
        model="my.model" report_type="qweb-pdf"
        name="my_module.tpl_report_x" file="my_module.report_x"/>
```

### `<delete>` / `<function>`

```xml
<delete model="res.partner" id="obsolete.legacy_partner"/>
<delete model="ir.ui.menu" search="[('name','=','Old')]"/>

<function model="res.partner" name="unlink_inactive"/>
<function model="my.model" name="post_install_hook"
          eval="[ref('base.main_company')]"/>
```

### Relational Commands

| Command | Tuple | Meaning |
|---------|-------|---------|
| `Command.create({...})` | `(0, 0, {...})` | Create |
| `Command.update(id, {...})` | `(1, id, {...})` | Update |
| `Command.delete(id)` | `(2, id, 0)` | Delete |
| `Command.unlink(id)` | `(3, id, 0)` | Unlink |
| `Command.link(id)` | `(4, id, 0)` | Link |
| `Command.clear()` | `(5, 0, 0)` | Clear |
| `Command.set([ids])` | `(6, 0, [ids])` | Replace |

---

## Coding Conventions

- Prefer `<record>` for full declarations and shortcut tags such as
  `<menuitem>` and `<template>` when they express the record completely.
- Put `id` before `model` on records. In fields, put `name` first, then the
  value (`text`, `eval`, or `ref`), then optional presentation attributes.
- Group records by model when dependencies allow it. Use `<data>` only when
  setting `noupdate="1"`; put `noupdate="1"` on `<odoo>` when the whole file
  is immutable.
- Keep IDs lowercase and descriptive. Follow the record-family patterns in
  the view, action, report, and security guides instead of anonymous IDs.

## Base Code Reference

- `odoo/tools/convert.py` — XML data loader, all tag handlers (`_tag_record`, `_tag_delete`, `_tag_function`, `_tag_menuitem`, `_tag_template`, `_tag_asset`), `eval` context (`_get_idref`).
- `odoo/addons/base/models/ir_model.py` — `ir.model.data` and the external-id resolver (`_xmlid_to_res_model_res_id`).
- `odoo/addons/base/models/ir_ui_menu.py` — menu model backing `<menuitem>`.
- `odoo/addons/base/models/ir_ui_view.py` — `ir.ui.view` backing `<template>`.
- `odoo/fields.py` — `Command` helpers exposed in `eval`.

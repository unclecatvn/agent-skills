# Odoo 19 Data Files Guide

Guide for working with Odoo 19 data files (XML and CSV), records, and shortcuts.

## Table of Contents
- [XML Data Files Structure](#xml-data-files-structure)
- [Record Tag](#record-tag)
- [Field Tag](#field-tag)
- [Delete Tag](#delete-tag)
- [Function Tag](#function-tag)
- [Shortcuts](#shortcuts)
- [CSV Data Files](#csv-data-files)

---

## XML Data Files Structure

The main way to define data in Odoo is via XML data files:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<odoo>
    <operation/>
    ...
</odoo>
```

### noupdate Flag

If content should only be applied once:

```xml
<odoo>
    <data noupdate="1">
        <!-- Only loaded when installing the module -->
        <operation/>
    </data>

    <!-- (Re)Loaded at install and update -->
    <operation/>
</odoo>
```

---

## Record Tag

`record` - Defines or updates a database record.

### Attributes

| Attribute | Type | Required | Description |
|-----------|------|----------|-------------|
| `model` | string | Yes | Name of the model to create/update |
| `id` | string | No* | External identifier for this record (strongly recommended) |
| `context` | dict | No | Context to use when creating |
| `forcecreate` | bool | No | In update mode, create if doesn't exist (default: True) |

*Required for record updates; recommended for creation

### Example

```xml
<record id="partner_1" model="res.partner">
    <field name="name">Odoo</field>
    <field name="is_company" eval="True"/>
    <field name="customer_rank" eval="1"/>
</record>
```

---

## Field Tag

Each `record` can have `field` tags defining values.

### Attributes

| Attribute | Type | Description |
|-----------|------|-------------|
| `name` | string | **Required**. Name of the field to set |
| `ref` | string | External ID to look up and set |
| `search` | domain | Search domain, result set as field value |
| `eval` | string | Python expression to evaluate |
| `type` | string | Interpret field content (see types below) |

### Value Methods

#### Nothing (False)

```xml
<field name="description"/>
```

#### search

For relational fields, evaluates a domain and sets the result:

```xml
<field name="partner_id" search="[('name', '=', 'Odoo')]"/>
```

Only first result used for Many2one fields.

#### ref

Look up an external ID:

```xml
<field name="country_id" ref="base.vn"/>
<field name="user_id" ref="base.user_admin"/>
```

#### type

Available types:

| Type | Description |
|------|-------------|
| `xml`, `html` | Extract children as document, evaluate external IDs |
| `file` | Ensure content is valid file path, saves `module,path` |
| `char` | Set content directly without alterations |
| `base64` | Base64-encode content (use with `file` attribute) |
| `int`, `float` | Convert to number |
| `list`, `tuple` | Contains `value` elements |

```xml
<field name="description" type="xml">
    <p>Hello <t t-esc="user.name"/></p>
</field>

<field name="image" type="base64" file="static/img/logo.png"/>
```

#### eval

Evaluate a Python expression:

```xml
<field name="active" eval="True"/>
<field name="date_today" eval="datetime.date.today()"/>
<field name="partner_id" eval="ref('base.main_partner')"/>
```

Evaluation context:
- `time`, `datetime`, `timedelta`, `relativedelta` modules
- `ref()` function to resolve external IDs
- `obj` for current field's model

---

## Delete Tag

`delete` - Removes records.

### Attributes

| Attribute | Type | Required | Description |
|-----------|------|----------|-------------|
| `model` | string | Yes | Model in which to delete |
| `id` | string | No* | External ID of record to remove |
| `search` | domain | No* | Domain to find records to remove |

*Exclusive: use either `id` or `search`

### Examples

```xml
<!-- Delete by external ID -->
<delete model="ir.ui.view" id="my_module.unwanted_view"/>

<!-- Delete by search -->
<delete model="ir.ui.menu" search="[('name', '=', 'Old Menu')]"/>
```

---

## Function Tag

`function` - Calls a method on a model.

### Attributes

| Attribute | Type | Required | Description |
|-----------|------|----------|-------------|
| `model` | string | Yes | Model to call method on |
| `name` | string | Yes | Name of method to call |

### Parameters

Via `eval` (should evaluate to sequence):

```xml
<function model="res.partner" name="send_inscription_notice"
    eval="[[ref('partner_1'), ref('partner_2')]]"/>
```

Via `value` elements:

```xml
<function model="res.users" name="send_vip_inscription_notice">
    <function eval="[[('vip','=',True)]]" model="res.partner" name="search"/>
</function>
```

---

## Shortcuts

Because some structural models are complex, data files provide shorter alternatives.

### menuitem

Defines an `ir.ui.menu` record with defaults:

| Attribute | Description |
|-----------|-------------|
| `parent` | External ID of parent menu, or interpret `name` as `/`-separated sequence |
| `name` | Menu name (or get from linked action) |
| `groups` | Comma-separated external IDs for `res.groups` (prefix `-` removes group) |
| `action` | External ID of action to execute |
| `id` | External identifier |

```xml
<menuitem id="my_module_menu_root" name="My Module" web_icon="my_module,static/description/icon.png"/>
<menuitem id="my_module_menu" name="My Model" parent="my_module_menu_root" action="my_module_action"/>
```

### template

Creates a QWeb view requiring only the `arch` section:

| Attribute | Description |
|-----------|-------------|
| `id` | External identifier |
| `name` | View name |
| `inherit_id` | External ID of parent view |
| `priority` | View priority |
| `primary` | If True with `inherit_id`, defines as primary |
| `groups` | Comma-separated group external IDs |
| `active` | Whether view is active (for inheritance views) |

```xml
<template id="my_template" name="My Template">
    <t t-call="website.layout">
        <div class="oe_structure">
            <h1>My Content</h1>
        </div>
    </t>
</template>
```

### asset

Creates an `ir.asset` record:

```xml
<asset id="website_something.some_style_asset" name="Some style asset" active="False">
    <bundle>web.assets_frontend</bundle>
    <path>website_something/static/src/some_style.scss</path>
</asset>
```

---

## CSV Data Files

XML is verbose for bulk creation. CSV files are simpler for same-model records.

### Structure

- File name: `{model_name}.csv`
- First row: fields to write, special field `id` for external IDs
- Each row: creates a new record

### Example: `res.country.state.csv`

```csv
id,country_id,name,code
state_1_us,country_us,Alabama,AL
state_2_us,country_us,Alaska,AK
state_3_us,country_us,Arizona,AZ
```

### Notes

- First column: external ID for creation/update
- Second column: external ID of country object to link to
- Third column: `name` field value
- Fourth column: `code` field value

---

## References

- Source: Odoo 19 documentation `/doc/developer/reference/backend/data.rst`

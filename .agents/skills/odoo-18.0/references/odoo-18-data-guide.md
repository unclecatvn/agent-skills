---
name: odoo-18-data
description: Complete reference for Odoo 18 data files covering XML data files, CSV data files, record tags, field tags, shortcuts (menuitem, template, asset), function tags, delete tags, and noupdate attribute.
globs: "**/*.{xml,csv}"
topics:
  - XML data files structure
  - record tag (create/update records)
  - field tag (set field values)
  - delete tag (remove records)
  - function tag (call model methods)
  - Shortcuts (menuitem, template, asset)
  - CSV data files
  - noupdate attribute
  - search and ref in fields
when_to_use:
  - Creating data files for modules
  - Defining views, menus, actions
  - Setting up default data
  - Creating demo data
  - Understanding record references
---

# Odoo 18 Data Files Guide

Complete reference for Odoo 18 data files: XML structure, records, fields, shortcuts, and CSV files.

## Table of Contents

1. [Data File Structure](#data-file-structure)
2. [record Tag](#record-tag)
3. [field Tag](#field-tag)
4. [delete Tag](#delete-tag)
5. [function Tag](#function-tag)
6. [Shortcuts](#shortcuts)
7. [CSV Data Files](#csv-data-files)
8. [noupdate Attribute](#noupdate-attribute)

---

## Data File Structure

### Basic XML Data File

```xml
<?xml version="1.0" encoding="UTF-8"?>
<odoo>
    <data noupdate="1">
        <!-- Operations here -->
    </data>

    <!-- (Re)Loaded at install and update -->
    <operation/>
</odoo>
```

### Root Element

All data files must have `<odoo>` as root element containing operations.

### Data Elements

Operations are executed sequentially:
- Earlier operations can be referenced by later operations
- Later operations cannot reference earlier operations

### File Locations

| Location | When Used |
|----------|-----------|
| `data/` | Always loaded at install/update |
| `demo/` | Only in demo mode |

---

## record Tag

### Creating Records

```xml
<record id="partner_1" model="res.partner">
    <field name="name">Odoo</field>
    <field name="email">info@odoo.com</field>
    <field name="is_company" eval="True"/>
    <field name="customer" eval="False"/>
</record>
```

### Record Attributes

| Attribute | Type | Required | Description |
|-----------|------|----------|-------------|
| `id` | string | No* | External identifier (strongly recommended) |
| `model` | string | Yes | Model name |
| `context` | dict | No | Context for creation |
| `forcecreate` | bool | No | Create if doesn't exist in update mode (default: True) |

### Updating Records

If `id` exists, record is updated instead of created:

```xml
<!-- First time: creates -->
<record id="partner_1" model="res.partner">
    <field name="name">Odoo</field>
</record>

<!-- Second time: updates -->
<record id="partner_1" model="res.partner">
    <field name="email">newemail@odoo.com</field>
</record>
```

### No Fields = No Change

```xml
<!-- Does nothing on update -->
<record id="existing_record" model="res.partner"/>
```

---

## field Tag

### field Attributes

| Attribute | Type | Description |
|-----------|------|-------------|
| `name` | string | Field name (required) |
| `ref` | string | External ID reference |
| `search` | domain | Search for relational field |
| `eval` | expression | Python expression |
| `type` | string | Interpretation type |

### Setting Values

#### No Value = False

```xml
<record id="record" model="my.model">
    <field name="my_field"/>  <!-- Sets to False -->
</record>
```

#### Direct Value

```xml
<field name="name">My Name</field>
<field name="code">123</field>
<field name="active">True</field>
```

#### eval - Python Expression

```xml
<field name="value" eval="42"/>
<field name="total" eval="10 + 20"/>
<field name="now" eval="datetime.datetime.now()"/>
<field name="list" eval="[(4, ref('base.group_user'))]"/>
```

### eval Context

Available in `eval`:

| Variable | Description |
|----------|-------------|
| `time` | Python `time` module |
| `datetime` | Python `datetime` module |
| `timedelta` | Python `timedelta` module |
| `relativedelta` | `dateutil.relativedelta` |
| `ref()` | Resolve external ID |
| `obj` | Current model (for field-specific) |

```xml
<field name="date" eval="datetime.date.today()"/>
<field name="next_week" eval="datetime.date.today() + relativedelta.relativedelta(weeks=1)"/>
```

#### ref - External ID Reference

```xml
<field name="user_id" ref="base.user_admin"/>
<field name="group_id" ref="base.group_user"/>
<field name="view_id" ref="my_module.my_view"/>
```

```xml
<!-- With ref in eval -->
<field name="groups_id" eval="[(6, 0, [ref('base.group_user'), ref('base.group_system')])]"/>
```

#### search - Domain Search

For relational fields, search for records:

```xml
<!-- Search for partner -->
<record id="record" model="my.model">
    <field name="partner_id" search="[('name', '=', 'Odoo')]"/>
</record>

<!-- Search with multiple results (first used for Many2one) -->
<field name="country_id" search="[('code', '=', 'US')]"/>
```

### type - Interpretation Type

| Type | Description |
|------|-------------|
| `xml` / `html` | Extract children as document |
| `file` | File path (stores as `module,path`) |
| `char` | Direct string value |
| `base64` | Base64 encode content |
| `int` | Convert to integer |
| `float` | Convert to float |
| `list` / `tuple` | List of values |

#### type="xml" / type="html"

```xml
<field name="description" type="xml">
    <p>This is <strong>formatted</strong> content.</p>
    <a href="%(link)s">Click here</a>
</field>
```

#### type="file"

```xml
<field name="image" type="file" name="my_module/static/img/logo.png"/>
<!-- Stores as: my_module,/static/img/logo.png -->
```

#### type="base64"

```xml
<field name="file_data" type="base64" file="my_module/static/data/file.bin"/>
```

#### type="list"

```xml
<field name="my_list" type="list">
    <value>1</value>
    <value>2</value>
    <value>3</value>
</field>
```

#### type="int" / type="float"

```xml
<field name="count" type="int">42</field>
<field name="price" type="float">19.99</field>
```

### Relational Fields

#### Many2one

```xml
<field name="partner_id" ref="base.main_partner"/>
<field name="user_id" ref="base.user_admin"/>
<field name="category_id" search="[('name', '=', 'Customers')]"/>
```

#### One2many / Many2many

Using Command values:

| Command | Description | Format |
|---------|-------------|--------|
| 0 | Create | `(0, 0, {values})` |
| 1 | Update | `(1, id, {values})` |
| 2 | Remove | `(2, id)` |
| 3 | Unlink | `(3, id)` |
| 4 | Link | `(4, id)` |
| 5 | Clear | `(5, )` |
| 6 | Replace | `(6, 0, [ids])` |

```xml
<record id="my_record" model="my.model">
    <!-- Create new line -->
    <field name="line_ids" eval="[
        (0, 0, {'name': 'Line 1', 'price': 100}),
        (0, 0, {'name': 'Line 2', 'price': 200}),
    ]"/>

    <!-- Link existing records -->
    <field name="tag_ids" eval="[(6, 0, [ref('tag_1'), ref('tag_2')])]"/>

    <!-- Clear all -->
    <field name="line_ids" eval="[(5,)]"/>

    <!-- Replace with new set -->
    <field name="tag_ids" eval="[(6, 0, [ref('tag_3')])]"/>
</record>
```

---

## delete Tag

### Deleting Records

```xml
<delete model="res.partner" id="partner_to_delete"/>
```

### delete Attributes

| Attribute | Type | Required | Description |
|-----------|------|----------|-------------|
| `model` | string | Yes | Model to delete from |
| `id` | string | No* | External ID to delete |
| `search` | domain | No* | Domain to find records |

`id` and `search` are mutually exclusive.

### Delete by External ID

```xml
<delete model="ir.ui.view" id="my_module.old_view"/>
```

### Delete by Search

```xml
<delete model="res.partner" search="[('name', '=', 'Test Partner')]"/>
```

### Delete Multiple

```xml
<delete model="ir.rule" search="[('domain_force', '=', False)]"/>
```

---

## function Tag

### Calling Model Methods

```xml
<function model="res.partner" name="send_notification">
    <!-- Parameters via value elements -->
    <value eval="[[ref('partner_1'), ref('partner_2')]]"/>
</function>
```

### function Attributes

| Attribute | Type | Required | Description |
|-----------|------|----------|-------------|
| `model` | string | Yes | Model to call method on |
| `name` | string | Yes | Method name |
| `eval` | expression | No | Parameters as expression |

### Parameters via eval

```xml
<function model="res.partner" name="create" eval="[
    {'name': 'Partner from XML', 'email': 'test@example.com'}
]"/>
```

### Parameters via value

```xml
<function model="my.model" name="my_method">
    <value>arg1</value>
    <value>arg2</value>
</function>
```

### Nested function

```xml
<function model="res.partner" name="send_vip_inscription_notice">
    <function eval="[[('vip', '=', True)]]" model="res.partner" name="search"/>
</function>
```

### Common Use Cases

```xml
<!-- Recompute views -->
<function model="ir.ui.view" name="search"/>

<!-- Clear cache -->
<function model="ir.cron" name="_process_job"/>

<!-- Call module hook -->
<function model="my.module" name="post_init_hook">
    <value eval="[]"/>
</function>
```

---

## Shortcuts

### menuitem Shortcut

Creates `ir.ui.menu` with defaults:

```xml
<menuitem id="menu_root" name="My Module"/>
```

#### menuitem Attributes

| Attribute | Description |
|-----------|-------------|
| `id` | External ID |
| `name` | Menu name (defaults to id if not set) |
| `parent` | Parent menu (external ID or name path) |
| `action` | Action to execute (external ID) |
| `groups` | Comma-separated group external IDs (prefix with `-` to remove) |

#### Menu Hierarchy

```xml
<!-- Top level -->
<menuitem id="menu_root" name="My Module" sequence="10"/>

<!-- Child (using parent) -->
<menuitem id="menu_sub" name="Sub Menu" parent="menu_root" sequence="1"/>

<!-- Child (using path - auto-creates intermediate) -->
<menuitem id="menu_deep" name="Deep Menu" parent="menu_root/Sub Menu" action="action_my"/>

<!-- With action -->
<menuitem id="menu_action" name="My Action" action="action_my_model"/>
```

#### Groups

```xml
<!-- Only for managers -->
<menuitem id="menu_manager" name="Manager" groups="base.group_system"/>

<!-- Remove group from menu -->
<menuitem id="menu_employees" name="Employees" groups="base.group_user,-base.group_system"/>
```

### template Shortcut

Creates `ir.ui.view` for QWeb template:

```xml
<template id="my_template" name="My Template">
    <div>
        <h1>Hello World</h1>
    </div>
</template>
```

#### template Attributes

| Attribute | Description |
|-----------|-------------|
| `id` | External ID (required) |
| `name` | View name |
| `inherit_id` | Parent template to inherit from |
| `priority` | View priority |
| `primary` | Set as primary view with inheritance |
| `groups` | Comma-separated group external IDs |
| `active` | Whether view is active |

```xml
<!-- Basic template -->
<template id="website_my_template">
    <div>
        <t t-foreach="docs" t-as="doc">
            <span t-field="doc.name"/>
        </t>
    </div>
</template>

<!-- Inheritance -->
<template id="inherit_template" inherit_id="website.my_template" priority="10">
    <xpath expr="//div" position="inside">
        <p>Inherited content</p>
    </xpath>
</template>

<!-- Primary inheritance -->
<template id="primary_template" inherit_id="base.template" primary="True">
    <!-- Primary template for this view -->
</template>

<!-- With groups -->
<template id="manager_template" groups="base.group_system">
    <!-- Only visible to system group -->
</template>

<!-- Active control -->
<template id="conditional_template" active="False">
    <!-- Inactive by default (XPath rules won't apply) -->
</template>
```

### asset Shortcut

Creates `ir.asset` record:

```xml
<asset id="website_something.style_asset" name="Some Style Asset">
    <bundle>web.assets_frontend</bundle>
    <path>website_something/static/src/some_style.scss</path>
</asset>
```

#### asset Attributes

| Attribute | Description |
|-----------|-------------|
| `id` | External ID (required) |
| `name` | Asset name |
| `active` | Whether asset is active |

#### asset Child Elements

| Element | Description |
|---------|-------------|
| `<bundle>` | Asset bundle name |
| `<path>` | File path |
| `<directive>` | Directive (include, replace, etc.) |

```xml
<asset id="my_module.assets" name="My Assets" active="True">
    <bundle>web.assets_frontend</bundle>
    <path>my_module/static/src/js/main.js</path>
    <path>my_module/static/src/scss/style.scss</path>
    <field name="directive">replace</field>
</asset>
```

---

## CSV Data Files

### CSV Structure

```
my_module/
└── data/
    └── res_country_state.csv
```

### CSV Format

- File name: `{model_name}.csv`
- First row: Field names including `id` for external IDs
- Each subsequent row: One record

### Example: Country States

```csv
id,country_id,name,code
state_au_nsw,country_au,New South Wales,NSW
state_au_vic,country_au,Victoria,VIC
state_au_qld,country_au,Queensland,QLD
```

### CSV Fields

| Column | Description |
|--------|-------------|
| `id` | External ID (for create/update) |
| `country_id:id` | Reference to country (external ID) |
| `name` | State name |
| `code` | State code |

### CSV for Access Rights

```csv
id,name,model_id:id,group_id:id,perm_read,perm_write,perm_create,perm_unlink
access_trip_user,trip.user,model_business_trip,base.group_user,1,0,0,0
access_trip_manager,trip.manager,model_business_trip,module.group_manager,1,1,1,1
```

### CSV vs XML

| CSV | XML |
|-----|-----|
| Simpler for bulk data | More flexible |
| Good for flat structures | Good for complex structures |
| Easier to edit | Better for relationships |
| Limited to simple values | Supports eval, search, etc. |

---

## noupdate Attribute

### noupdate="1"

Data in `<data noupdate="1">` is only loaded at installation:

```xml
<odoo>
    <!-- Loaded at install and update -->
    <record id="core_data" model="my.model">
        <field name="name">Core Data</field>
    </record>

    <!-- Loaded only at install -->
    <data noupdate="1">
        <record id="demo_data" model="my.model">
            <field name="name">Demo Data</field>
        </record>
    </data>
</odoo>
```

### When to Use noupdate

| Use Case | noupdate |
|----------|----------|
| Core module data | 0 (default) |
| User-editable data | 1 |
| Default records | 1 |
| Demo data | 1 |
| Configuration | 1 |
| Views, actions, menus | 0 |

### noupdate Examples

```xml
<!-- Core data: always update -->
<record id="ir_cron_send_email" model="ir.cron">
    <field name="name">Send Email</field>
</record>

<!-- User data: never update after install -->
<data noupdate="1">
    <record id="default_warehouse" model="stock.warehouse">
        <field name="name">Default Warehouse</field>
    </record>
</data>

<!-- Demo data: only in demo mode -->
<data noupdate="1" demo="true">
    <record id="demo_partner" model="res.partner">
        <field name="name">Demo Partner</field>
    </record>
</data>
```

---

## Quick Reference

### record Tag

```xml
<record id="external_id" model="model.name" context="{}">
    <field name="field_name">value</field>
    <field name="field_ref" ref="module.external_id"/>
    <field name="field_eval" eval="True"/>
    <field name="field_search" search="[('name', '=', 'Value')]"/>
    <field name="field_xml" type="xml"><p>content</p></field>
</record>
```

### field Tag Value Types

| Type | Usage |
|------|-------|
| Direct | `<field name="name">Value</field>` |
| eval | `<field name="active" eval="True"/>` |
| ref | `<field name="user" ref="base.user_admin"/>` |
| search | `<field name="country" search="[('code', '=', 'US')]"/>` |
| type="xml" | `<field name="desc" type="xml"><p>HTML</p></field>` |
| type="file" | `<field name="image" type="file" name="path.png"/>` |
| type="base64" | `<field name="data" type="base64" file="file.bin"/>` |
| type="int" | `<field name="count" type="int">42</field>` |

### Relational Commands

| Command | Use |
|---------|-----|
| `(0, 0, {...})` | Create new |
| `(1, id, {...})` | Update |
| `(2, id)` | Remove |
| `(3, id)` | Unlink |
| `(4, id)` | Link |
| `(5,)` | Clear all |
| `(6, 0, [ids])` | Replace set |

### Shortcuts

```xml
<!-- Menu -->
<menuitem id="menu_id" name="Label" parent="parent_id" action="action_id"/>

<!-- Template -->
<template id="template_id" inherit_id="parent_template" active="True"/>

<!-- Asset -->
<asset id="asset_id" name="Name" active="True">
    <bundle>web.assets_frontend</bundle>
    <path>path/to/file</path>
</asset>
```

---

**For more Odoo 18 guides, see [SKILL.md](../SKILL.md)**

---
name: odoo-17-view
description: Complete reference for Odoo 17 XML views, QWeb templates, and view inheritance. Covers tree, form, search, kanban, graph, pivot, calendar, activity, gantt views and Odoo 17 conventions.
globs: "**/views/**/*.xml"
topics:
  - View types (tree, form, search, kanban, graph, pivot, calendar, activity, gantt)
  - Tree view features (editable, decoration, optional fields, widgets)
  - Form view structure (sheet, button box, notebook, chatter)
  - Search view features (fields, filters, group by)
  - Kanban view (color, progress, kanban-box templates)
  - Dynamic attributes (invisible, readonly, required as Python expressions)
  - View inheritance (xpath, position, shorthand)
  - QWeb templates (t-esc, t-out, t-field)
when_to_use:
  - Writing Odoo 17 XML views
  - Implementing view inheritance
  - Building QWeb templates
  - Migrating views from Odoo 16 to 17
---

# Odoo 17 View Guide

Complete reference for Odoo 17 XML views, QWeb templates, and view inheritance.

## Table of Contents

1. [View Types](#view-types)
2. [Tree View (List)](#tree-view-list)
3. [Form View](#form-view)
4. [Search View](#search-view)
5. [Kanban View](#kanban-view)
6. [Graph & Pivot Views](#graph--pivot-views)
7. [Calendar View](#calendar-view)
8. [Activity View](#activity-view)
9. [Gantt View](#gantt-view)
10. [Dynamic Attributes (invisible/readonly/required)](#dynamic-attributes)
11. [View Inheritance](#view-inheritance)
12. [QWeb Templates](#qweb-templates)
13. [Complete Module Example](#complete-module-example)

---

## View Types

Odoo 17 supports the following view types. The XML root tag matches the value stored in `ir.ui.view.type`.

| Type | XML Tag | Use For |
|------|---------|---------|
| `tree` | `<tree>` | Table / list view (still `<tree>` in v17; renamed to `<list>` in v18) |
| `form` | `<form>` | Single-record edit/view |
| `search` | `<search>` | Search panel, filters, group-by |
| `kanban` | `<kanban>` | Card-based view |
| `graph` | `<graph>` | Bar/line/pie charts |
| `pivot` | `<pivot>` | Pivot table |
| `calendar` | `<calendar>` | Calendar view |
| `gantt` | `<gantt>` | Gantt chart (enterprise) |
| `activity` | `<activity>` | Activity view (requires `mail` module) |
| `qweb` | `<template>` | QWeb template |

Defined in `odoo/addons/base/models/ir_ui_view.py` (`VIEW_TYPES` and the `type` selection).

---

## Tree View (List)

The Odoo 17 list view is declared with `<tree>`. (Odoo 18 renamed this tag to `<list>` — in v17 it is still `<tree>` everywhere, including in `xpath` expressions and action `view_mode` values such as `tree,form`.)

### Basic Tree View

```xml
<record id="view_my_model_tree" model="ir.ui.view">
    <field name="name">my.model.tree</field>
    <field name="model">my.model</field>
    <field name="arch" type="xml">
        <tree string="My Records">
            <field name="name"/>
            <field name="date"/>
            <field name="state"/>
        </tree>
    </field>
</record>
```

### Tree View Features

```xml
<tree string="My Records"
      sample="1"               <!-- Show sample data when empty -->
      multi_edit="1"           <!-- Allow multi-record inline edit -->
      editable="bottom"        <!-- "top" or "bottom" to enable inline edit -->
      default_order="date desc"
      limit="80"
      create="true" edit="true" delete="true"
      expand="1">              <!-- Auto-expand groups -->

    <!-- Decoration (row styling via domain-style expression) -->
    <field name="state"
           decoration-success="state == 'done'"
           decoration-danger="state == 'cancel'"
           decoration-warning="state == 'pending'"
           decoration-muted="not active"/>

    <!-- Optional fields (user can toggle column) -->
    <field name="phone" optional="show"/>   <!-- shown by default -->
    <field name="mobile" optional="hide"/>  <!-- hidden by default -->

    <!-- Specialized widgets -->
    <field name="image" widget="image"/>
    <field name="user_id" widget="many2one_avatar_user"/>
    <field name="tag_ids" widget="many2many_tags" options="{'color_field': 'color'}"/>
    <field name="sequence" widget="handle"/>   <!-- drag-to-reorder -->

    <!-- Hidden column (still usable for decorations/computations) -->
    <field name="currency_id" column_invisible="True"/>

    <!-- Group restriction -->
    <field name="company_id" groups="base.group_multi_company"/>

    <!-- Inline button -->
    <button name="action_confirm" type="object" string="Confirm"
            invisible="state != 'draft'"/>
</tree>
```

### Decoration Types

| Attribute | Effect | Typical Meaning |
|-----------|--------|-----------------|
| `decoration-bf` | Bold | Highlight |
| `decoration-it` | Italic | Emphasis |
| `decoration-danger` | Red text | Error / cancelled |
| `decoration-warning` | Orange text | Warning |
| `decoration-success` | Green text | Success / done |
| `decoration-info` | Blue text | Informational |
| `decoration-muted` | Grey text | Inactive / archived |
| `decoration-primary` | Brand colour | Primary / featured |

The value of each `decoration-*` is a Python expression evaluated against the record (e.g. `state == 'done'`).

### Groupable / Hidden Columns

- `column_invisible="True"` — hide the column in the list (still available on the record for decorations).
- `invisible="1"` inside a tree — only hides per-row (useful for edit-only columns, rare).
- `readonly="state in ('cancel','sale')"` — per-row read-only expression.

---

## Form View

### Basic Form View

```xml
<record id="view_my_model_form" model="ir.ui.view">
    <field name="name">my.model.form</field>
    <field name="model">my.model</field>
    <field name="arch" type="xml">
        <form string="My Record">
            <sheet>
                <group>
                    <group>
                        <field name="name"/>
                        <field name="date"/>
                    </group>
                    <group>
                        <field name="user_id"/>
                        <field name="company_id"/>
                    </group>
                </group>
            </sheet>
        </form>
    </field>
</record>
```

### Full Form Structure

```xml
<form string="My Record" create="true" edit="true" delete="true">

    <!-- 1. Header: status bar + workflow buttons -->
    <header>
        <button name="action_confirm" type="object" string="Confirm"
                class="btn-primary" invisible="state != 'draft'"/>
        <button name="action_done" type="object" string="Done"
                invisible="state != 'confirmed'"/>
        <button name="action_cancel" type="object" string="Cancel"
                invisible="state in ('done','cancel')"/>
        <field name="state" widget="statusbar" statusbar_visible="draft,confirmed,done"/>
    </header>

    <!-- 2. Sheet: main body -->
    <sheet>

        <!-- Ribbon (e.g. "Archived" badge) -->
        <widget name="web_ribbon" title="Archived" bg_color="bg-danger"
                invisible="active"/>

        <!-- Stat buttons -->
        <div class="oe_button_box" name="button_box">
            <button name="action_view_related" type="object"
                    class="oe_stat_button" icon="fa-tasks">
                <field name="task_count" widget="statinfo" string="Tasks"/>
            </button>
        </div>

        <!-- Image / avatar -->
        <field name="image" widget="image" class="oe_avatar"/>

        <!-- Title block -->
        <div class="oe_title">
            <h1>
                <field name="name" placeholder="Record name..." required="1"/>
            </h1>
        </div>

        <!-- Two-column group layout -->
        <group>
            <group>
                <field name="partner_id"/>
                <field name="date"/>
                <field name="email" widget="email"/>
            </group>
            <group>
                <field name="user_id"/>
                <field name="company_id" groups="base.group_multi_company"/>
                <field name="priority" widget="priority"/>
            </group>
        </group>

        <!-- Notebook (tabs) -->
        <notebook>
            <page string="Lines" name="lines">
                <field name="line_ids">
                    <tree editable="bottom">
                        <field name="product_id"/>
                        <field name="quantity"/>
                        <field name="price_unit"/>
                        <field name="subtotal" sum="Total"/>
                    </tree>
                </field>
            </page>
            <page string="Notes" name="notes">
                <field name="note" placeholder="Add internal notes..."/>
            </page>
            <page string="Admin" name="admin" groups="base.group_system">
                <field name="debug_info" widget="ace" options="{'mode': 'python'}"/>
            </page>
        </notebook>
    </sheet>

    <!-- 3. Chatter (explicit div + fields in v17) -->
    <div class="oe_chatter">
        <field name="message_follower_ids"/>
        <field name="activity_ids"/>
        <field name="message_ids"/>
    </div>
</form>
```

> **Chatter (v17)**: you declare the chatter as a `<div class="oe_chatter">` containing the three mail fields. The shorthand `<chatter/>` tag was introduced in Odoo 18 and does **not** exist in v17.

### Form Root Attributes

| Attribute | Effect |
|-----------|--------|
| `string` | Default record label |
| `create` / `edit` / `delete` | `"false"` to disable per-view |
| `duplicate` | `"false"` disables the "Duplicate" action |
| `js_class` | Replace controller with a registered JS class |

### Field Widgets (Form)

```xml
<!-- Text -->
<field name="description" widget="text"/>
<field name="html_body" widget="html"/>

<!-- Date / Datetime -->
<field name="date" widget="date"/>
<field name="deadline" widget="datetime"/>
<field name="create_date" readonly="1" widget="relative"/>

<!-- Specialized -->
<field name="email" widget="email"/>
<field name="phone" widget="phone" options="{'enable_sms': false}"/>
<field name="website" widget="url"/>
<field name="image" widget="image" class="oe_avatar"/>

<!-- Many2one -->
<field name="partner_id"
       options="{'no_open': True, 'no_create': True, 'no_quick_create': True}"/>
<field name="user_id" widget="many2one_avatar_user"/>

<!-- Many2many -->
<field name="tag_ids" widget="many2many_tags" options="{'color_field': 'color'}"/>
<field name="category_ids" widget="many2many_checkboxes"/>

<!-- Selection / status bar -->
<field name="state" widget="statusbar" statusbar_visible="draft,confirmed,done"/>
<field name="priority" widget="priority"/>
<field name="kanban_state" widget="state_selection"/>

<!-- Boolean -->
<field name="active" widget="boolean_toggle"/>

<!-- Monetary -->
<field name="amount_total" widget="monetary"
       options="{'currency_field': 'currency_id'}"/>
<field name="currency_id" invisible="1"/>

<!-- Signature -->
<field name="signature" widget="signature"/>

<!-- Domain builder -->
<field name="domain" widget="domain" options="{'model': 'res.partner'}"/>

<!-- Code editor (Ace) -->
<field name="arch" widget="ace" options="{'mode': 'xml'}"/>
```

### Field Common Attributes

```xml
<!-- Placeholder, required, readonly, groups -->
<field name="name" placeholder="Enter name..." required="1"/>
<field name="reference" readonly="1"/>
<field name="internal_note" groups="base.group_user"/>

<!-- Context / domain -->
<field name="product_id"
       context="{'default_type': 'service'}"
       domain="[('sale_ok', '=', True)]"/>

<!-- No label -->
<field name="description" nolabel="1"/>

<!-- Inline edit of relational field -->
<field name="partner_id" options="{'always_reload': True}"/>
```

---

## Search View

### Basic Search View

```xml
<record id="view_my_model_search" model="ir.ui.view">
    <field name="name">my.model.search</field>
    <field name="model">my.model</field>
    <field name="arch" type="xml">
        <search string="Search My Model">
            <field name="name"/>
            <field name="partner_id"/>
            <filter string="Active" name="active" domain="[('active','=',True)]"/>
        </search>
    </field>
</record>
```

### Full Search View

```xml
<search string="Search Orders">

    <!-- Searchable fields (appear in search bar autocomplete) -->
    <field name="name" string="Reference"
           filter_domain="['|', ('name', 'ilike', self), ('client_ref', 'ilike', self)]"/>
    <field name="partner_id" operator="child_of"/>
    <field name="date"/>

    <!-- Domain filters -->
    <filter string="My Orders" name="my_orders" domain="[('user_id', '=', uid)]"/>
    <filter string="Unassigned" name="unassigned" domain="[('user_id', '=', False)]"/>

    <separator/>

    <!-- Date filters (domain expressions using context_today / relativedelta) -->
    <filter string="Today" name="today"
            domain="[('date', '=', context_today().strftime('%Y-%m-%d'))]"/>
    <filter string="This Month" name="this_month"
            domain="[('date', '&gt;=', (context_today() + relativedelta(day=1)).strftime('%Y-%m-%d')),
                     ('date', '&lt;=', (context_today() + relativedelta(months=1, day=1, days=-1)).strftime('%Y-%m-%d'))]"/>

    <separator/>

    <!-- State filters -->
    <filter string="Draft" name="draft" domain="[('state', '=', 'draft')]"/>
    <filter string="Confirmed" name="confirmed" domain="[('state', '=', 'confirmed')]"/>

    <!-- Archived toggle -->
    <filter string="Archived" name="inactive" domain="[('active', '=', False)]"/>

    <!-- Group By section -->
    <group expand="0" string="Group By">
        <filter string="Salesperson" name="group_user" context="{'group_by': 'user_id'}"/>
        <filter string="Customer" name="group_partner" context="{'group_by': 'partner_id'}"/>
        <filter string="Status" name="group_state" context="{'group_by': 'state'}"/>
        <filter string="Order Date" name="group_date" context="{'group_by': 'date:month'}"/>
    </group>

    <!-- Search panel (left-hand side filter tree/list) -->
    <searchpanel>
        <field name="category_id" enable_counters="1"/>
        <field name="stage_id" select="multi" icon="fa-tasks"/>
    </searchpanel>
</search>
```

`date:month` groups by month (other granularities: `day`, `week`, `month`, `quarter`, `year`).

`filter_domain` replaces the default field domain — handy for fuzzy "search many columns at once".

`&gt;=` / `&lt;=` are XML entities for `>=` / `<=`.

---

## Kanban View

### Basic Kanban (v17 uses `t-name="kanban-box"`)

```xml
<record id="view_my_model_kanban" model="ir.ui.view">
    <field name="name">my.model.kanban</field>
    <field name="model">my.model</field>
    <field name="arch" type="xml">
        <kanban default_group_by="state" sample="1">
            <field name="name"/>
            <field name="state"/>
            <templates>
                <t t-name="kanban-box">
                    <div class="oe_kanban_card oe_kanban_global_click">
                        <strong><field name="name"/></strong>
                        <div><field name="state"/></div>
                    </div>
                </t>
            </templates>
        </kanban>
    </field>
</record>
```

> The v17 card template name is `kanban-box`. (Odoo 19 introduced `t-name="card"`; do not use that name in v17.)

### Kanban with Colour, Priority, and Progress Bar

```xml
<kanban default_group_by="state"
        class="o_kanban_small_column"
        quick_create="true"
        records_draggable="true"
        group_create="true"
        sample="1">

    <field name="name"/>
    <field name="color"/>
    <field name="priority"/>
    <field name="kanban_state"/>
    <field name="user_id"/>
    <field name="activity_ids"/>

    <!-- Column-level progress bar -->
    <progressbar field="kanban_state"
                 colors='{"done": "success", "blocked": "danger", "normal": "200"}'/>

    <templates>
        <t t-name="kanban-box">
            <div t-attf-class="oe_kanban_card oe_kanban_global_click
                               oe_kanban_color_#{kanban_getcolor(record.color.raw_value)}">
                <div class="o_kanban_record_top">
                    <div class="o_kanban_record_headings">
                        <strong class="o_kanban_record_title">
                            <field name="name"/>
                        </strong>
                    </div>
                    <field name="priority" widget="priority"/>
                </div>

                <div class="o_kanban_record_body">
                    <field name="description"/>
                </div>

                <div class="o_kanban_record_bottom">
                    <div class="oe_kanban_bottom_left">
                        <field name="activity_ids" widget="kanban_activity"/>
                        <field name="kanban_state" widget="state_selection"/>
                    </div>
                    <div class="oe_kanban_bottom_right">
                        <img t-att-src="kanban_image('res.users', 'avatar_128', record.user_id.raw_value)"
                             t-att-title="record.user_id.value"
                             class="oe_kanban_avatar"/>
                    </div>
                </div>

                <!-- Kanban contextual menu -->
                <div class="o_dropdown_kanban dropdown" t-if="!selection_mode">
                    <a role="button" class="dropdown-toggle o-no-caret btn"
                       data-bs-toggle="dropdown" data-bs-display="static" href="#"
                       aria-label="Dropdown menu" title="Dropdown menu">
                        <span class="fa fa-ellipsis-v"/>
                    </a>
                    <div class="dropdown-menu" role="menu">
                        <a role="menuitem" type="edit" class="dropdown-item">Edit</a>
                        <a role="menuitem" type="delete" class="dropdown-item">Delete</a>
                    </div>
                </div>
            </div>
        </t>
    </templates>
</kanban>
```

Useful helpers available inside the template:

| Helper | Purpose |
|--------|---------|
| `kanban_getcolor(index)` | Map integer 0..11 to an `oe_kanban_color_*` CSS class |
| `kanban_image(model, field, id)` | Build `/web/image/...` URL for an image field |
| `record.<field>.value` | Formatted value |
| `record.<field>.raw_value` | Raw value |
| `widget.editable` / `widget.deletable` | Booleans for permissions |

### Kanban Attributes

| Attribute | Purpose |
|-----------|---------|
| `default_group_by` | Default grouping field |
| `default_order` | Initial sort order |
| `quick_create` | Show the "+" column quick-create |
| `quick_create_view` | Alternative form view reference for quick-create |
| `group_create` | Allow creating new groups |
| `group_delete` / `group_edit` | Group-level permissions |
| `records_draggable` | Drag records between groups |
| `sample="1"` | Show sample data when empty |
| `class` | CSS class (`o_kanban_small_column`, `o_kanban_mobile`, ...) |

---

## Graph & Pivot Views

### Graph View

```xml
<record id="view_my_model_graph" model="ir.ui.view">
    <field name="name">my.model.graph</field>
    <field name="model">my.model</field>
    <field name="arch" type="xml">
        <graph string="Sales Analysis" type="bar" stacked="1" sample="1">
            <field name="date" interval="month" type="row"/>
            <field name="partner_id" type="row"/>
            <field name="amount_total" type="measure"/>
        </graph>
    </field>
</record>
```

| Graph attribute | Values |
|-----------------|--------|
| `type` | `bar`, `line`, `pie` |
| `stacked` | `"1"` for stacked bars |
| `order` | `asc` or `desc` on the measure |
| `disable_linking` | `"1"` prevents drill-down on click |

Field roles: `type="row"` (dimension), `type="col"` (secondary dimension), `type="measure"` (aggregated value).

### Pivot View

```xml
<record id="view_my_model_pivot" model="ir.ui.view">
    <field name="name">my.model.pivot</field>
    <field name="model">my.model</field>
    <field name="arch" type="xml">
        <pivot string="Sales Analysis" sample="1" disable_linking="0">
            <field name="date" interval="month" type="row"/>
            <field name="partner_id" type="col"/>
            <field name="amount_total" type="measure"/>
            <field name="qty" type="measure"/>
        </pivot>
    </field>
</record>
```

---

## Calendar View

```xml
<record id="view_my_model_calendar" model="ir.ui.view">
    <field name="name">my.model.calendar</field>
    <field name="model">my.model</field>
    <field name="arch" type="xml">
        <calendar string="Meetings"
                  date_start="start"
                  date_stop="stop"
                  color="partner_id"
                  mode="month"
                  quick_create="1">
            <field name="name"/>
            <field name="partner_id" avatar_field="image_128"/>
        </calendar>
    </field>
</record>
```

| Attribute | Description |
|-----------|-------------|
| `date_start` | Start datetime field (required) |
| `date_stop` | End datetime field |
| `date_delay` | Duration field (alternative to `date_stop`) |
| `color` | Field used to color events (many2one recommended) |
| `mode` | `day`, `week`, `month`, `year` |
| `all_day` | Boolean field toggling all-day events |
| `quick_create` | Enable quick record creation from the calendar |

---

## Activity View

The `<activity>` view requires the `mail` module. The model must inherit `mail.activity.mixin`.

```xml
<record id="view_my_model_activity" model="ir.ui.view">
    <field name="name">my.model.activity</field>
    <field name="model">my.model</field>
    <field name="arch" type="xml">
        <activity string="My Records">
            <field name="name"/>
            <templates>
                <div t-name="activity-box">
                    <img t-att-src="activity_image('res.users', 'avatar_128', record.user_id.raw_value)"
                         t-att-title="record.user_id.value"
                         class="rounded-circle"/>
                    <div>
                        <field name="name" display="full"/>
                        <field name="partner_id" muted="1"/>
                    </div>
                </div>
            </templates>
        </activity>
    </field>
</record>
```

---

## Gantt View

The `<gantt>` view is part of Odoo Enterprise (web_gantt module).

```xml
<record id="view_project_gantt" model="ir.ui.view">
    <field name="name">project.task.gantt</field>
    <field name="model">project.task</field>
    <field name="arch" type="xml">
        <gantt string="Tasks"
               date_start="date_start"
               date_stop="date_end"
               default_group_by="user_id"
               color="stage_id"
               progress="progress"
               precision="{'day': 'hour:half', 'week': 'day:full', 'month': 'day:full'}">
            <field name="name"/>
        </gantt>
    </field>
</record>
```

---

## Dynamic Attributes

> **v17 note:** Since Odoo 17.0 the legacy `attrs="{...}"` and `states="..."` attributes are **rejected by the view validator** (see `ir_ui_view.py`: *"Since 17.0, the attrs and states attributes are no longer used."*). Use direct Python-expression attributes instead.

### invisible / readonly / required

```xml
<!-- Single-field condition -->
<field name="company_name" invisible="is_company"/>
<field name="email"        required="is_company"/>
<field name="code"         readonly="state != 'draft'"/>

<!-- Compound expressions -->
<field name="phone" invisible="not is_company or parent_id"/>
<button name="action_confirm" type="object" string="Confirm"
        invisible="state != 'draft'" class="btn-primary"/>

<!-- In tree views: column_invisible for entire column -->
<tree>
    <field name="currency_id" column_invisible="True"/>
    <field name="amount" widget="monetary"/>
</tree>

<!-- Page (notebook tab) -->
<page string="Contract" name="contract" invisible="not has_contract">
    ...
</page>

<!-- Group / div -->
<group invisible="not partner_id">
    <field name="partner_invoice_id"/>
    <field name="partner_shipping_id"/>
</group>
```

Expressions are evaluated in a Python-like context with access to every field loaded by the view, the context (via `context`), `parent.*` for nested one2many lines, and helpers like `True`, `False`, `uid`.

### Migration From Pre-17 `attrs`

| Old (<=16.0) | New (17.0+) |
|--------------|-------------|
| `attrs="{'invisible': [('state','=','done')]}"` | `invisible="state == 'done'"` |
| `attrs="{'readonly': [('locked','=',True)]}"` | `readonly="locked"` |
| `attrs="{'required': [('type','=','post')]}"` | `required="type == 'post'"` |
| `attrs="{'invisible': [('a','=',1),('b','=',2)]}"` (AND) | `invisible="a == 1 and b == 2"` |
| `attrs="{'invisible': ['|',('a','=',1),('b','=',2)]}"` (OR) | `invisible="a == 1 or b == 2"` |
| `states="draft,confirmed"` | `invisible="state not in ('draft','confirmed')"` |

---

## View Inheritance

Inherited views are stored with `inherit_id` pointing to the parent view, and their `arch` contains spec nodes that describe where/what to modify.

### XPath Inheritance

```xml
<record id="view_res_partner_form_inherit" model="ir.ui.view">
    <field name="name">res.partner.form.inherit.my.module</field>
    <field name="model">res.partner</field>
    <field name="inherit_id" ref="base.view_partner_form"/>
    <field name="arch" type="xml">

        <!-- Insert AFTER an existing field -->
        <xpath expr="//field[@name='email']" position="after">
            <field name="my_custom_field"/>
        </xpath>

        <!-- Insert BEFORE an existing field -->
        <xpath expr="//field[@name='name']" position="before">
            <field name="prefix"/>
        </xpath>

        <!-- Insert INSIDE an element (at the end) -->
        <xpath expr="//sheet/group[1]" position="inside">
            <field name="extra_note"/>
        </xpath>

        <!-- REPLACE an element -->
        <xpath expr="//field[@name='name']" position="replace">
            <field name="name" required="1" placeholder="Name..."/>
        </xpath>

        <!-- REMOVE an element (replace with empty content) -->
        <xpath expr="//field[@name='comment']" position="replace"/>

        <!-- Modify ATTRIBUTES of an element -->
        <xpath expr="//field[@name='name']" position="attributes">
            <attribute name="readonly">1</attribute>
            <attribute name="string">Full Name</attribute>
        </xpath>

        <!-- Append to attribute value (comma-separated) -->
        <xpath expr="//field[@name='name']" position="attributes">
            <attribute name="groups" add="base.group_system" separator=","/>
        </xpath>

        <!-- Move an existing element (see MOVE pattern below) -->
        <xpath expr="//field[@name='email']" position="after">
            <field name="phone" position="move"/>
        </xpath>

        <!-- Replace the ROOT tag (rare - used for top-level tree changes) -->
        <xpath expr="//tree" position="attributes">
            <attribute name="editable">bottom</attribute>
        </xpath>
    </field>
</record>
```

> In v17 tree views, xpath expressions targeting the root list element use `//tree`, not `//list`.

### Shorthand (Field / Tag Position)

You can skip `<xpath>` when targeting a named field or a unique top-level tag:

```xml
<field name="arch" type="xml">
    <!-- Equivalent to <xpath expr="//field[@name='email']" position="after"> -->
    <field name="email" position="after">
        <field name="my_field"/>
    </field>

    <!-- Target the tree root directly -->
    <tree position="attributes">
        <attribute name="editable">bottom</attribute>
    </tree>

    <!-- Target the form root -->
    <form position="inside">
        <div>Content appended at the end of &lt;form&gt;</div>
    </form>
</field>
```

### Position Values Summary

| Position | Effect |
|----------|--------|
| `after` | Insert spec children right after the matched node |
| `before` | Insert spec children right before the matched node |
| `inside` (default) | Append spec children as last children of the matched node |
| `replace` | Replace matched node with spec children (empty spec = remove) |
| `attributes` | Add/change attributes on the matched node |
| `move` | On a CHILD of an insertion spec, move an existing node into the new location |

### Multiple Matches / Cascades

Inherited views themselves can be inherited. The engine combines all `inherit_id` descendants ordered by `priority` (default 16, lower runs first) and applies specs sequentially.

### Extending Inline Sub-Views

The `<tree>` nested inside a `<field name="line_ids">` is also reachable via xpath:

```xml
<xpath expr="//field[@name='line_ids']/tree/field[@name='price_unit']" position="after">
    <field name="discount"/>
</xpath>
```

---

## QWeb Templates

QWeb powers reports, backend views (list/kanban/form templates), and website pages. Templates are `ir.ui.view` records of `type="qweb"`, usually written with the `<template>` shortcut.

### Basic Template

```xml
<template id="my_module.landing_page" name="Landing Page">
    <div class="container">
        <h1 t-out="title"/>
        <t t-if="records">
            <ul>
                <t t-foreach="records" t-as="rec">
                    <li>
                        <span t-field="rec.name"/>
                        -
                        <span t-esc="rec.date" t-options="{'widget': 'date'}"/>
                    </li>
                </t>
            </ul>
        </t>
        <t t-else="">
            <p>No records found.</p>
        </t>
    </div>
</template>
```

### Output Directives

| Directive | Purpose | Notes |
|-----------|---------|-------|
| `t-esc` | Output escaped text | Classic; still fully supported in v17 |
| `t-out` | Output escaped text, but **respects `Markup`** | **Preferred** for trusted HTML / rich-text fields |
| `t-field` | Output a record field with formatting | Uses field widget formatting |
| `t-raw` | Output raw (unescaped) — **deprecated**, avoid | Use `t-out` with `Markup(...)` instead |

```xml
<!-- Plain text -->
<span t-esc="record.name"/>
<span t-out="record.name"/>

<!-- Rich HTML field (safe) -->
<div t-out="record.body_html"/>

<!-- Field with formatting widget -->
<span t-field="record.amount_total"
      t-options='{"widget": "monetary", "display_currency": record.currency_id}'/>

<!-- Conditional text -->
<span t-esc="record.ref or 'Draft'"/>
```

### Control Flow

```xml
<t t-if="condition">true branch</t>
<t t-elif="other_cond">elif branch</t>
<t t-else="">else branch</t>

<t t-foreach="docs" t-as="doc">
    <div>
        <span t-esc="doc_index"/>   <!-- index (0-based) -->
        <span t-esc="doc_first"/>   <!-- True on first -->
        <span t-esc="doc_last"/>    <!-- True on last -->
        <span t-esc="doc_size"/>    <!-- total length -->
    </div>
</t>

<!-- Set a variable -->
<t t-set="total" t-value="sum(line.subtotal for line in doc.line_ids)"/>
<span t-esc="total"/>
```

### Attribute Directives

```xml
<!-- Dynamic attribute value -->
<a t-att-href="'/shop/%d' % product.id">View</a>

<!-- Attribute from dict -->
<div t-att="{'data-id': record.id, 'class': 'my-card'}"/>

<!-- Format-string attribute -->
<div t-attf-class="o_card color-#{record.color}"/>

<!-- Conditional attribute -->
<button t-att-disabled="'disabled' if readonly else None">Save</button>
```

### Template Inheritance

```xml
<template id="landing_page_inherit"
          inherit_id="my_module.landing_page">
    <xpath expr="//h1" position="after">
        <p class="lead">Added via inheritance</p>
    </xpath>
</template>
```

### Calling Other Templates

```xml
<t t-call="web.external_layout">
    <t t-set="doc" t-value="doc"/>
    <div class="page">
        <h2 t-field="doc.name"/>
    </div>
</t>
```

---

## Complete Module Example

```xml
<?xml version="1.0" encoding="utf-8"?>
<odoo>
    <data>

        <!-- TREE -->
        <record id="view_my_module_tree" model="ir.ui.view">
            <field name="name">my.module.tree</field>
            <field name="model">my.module</field>
            <field name="arch" type="xml">
                <tree string="My Modules" sample="1"
                      decoration-success="state == 'done'"
                      decoration-muted="state == 'cancel'">
                    <field name="name"/>
                    <field name="partner_id"/>
                    <field name="date"/>
                    <field name="user_id" optional="show" widget="many2one_avatar_user"/>
                    <field name="state" widget="badge"
                           decoration-success="state == 'done'"
                           decoration-info="state == 'draft'"/>
                </tree>
            </field>
        </record>

        <!-- FORM -->
        <record id="view_my_module_form" model="ir.ui.view">
            <field name="name">my.module.form</field>
            <field name="model">my.module</field>
            <field name="arch" type="xml">
                <form string="My Module">
                    <header>
                        <button name="action_confirm" type="object"
                                string="Confirm" class="btn-primary"
                                invisible="state != 'draft'"/>
                        <button name="action_done" type="object"
                                string="Mark Done"
                                invisible="state != 'confirmed'"/>
                        <field name="state" widget="statusbar"
                               statusbar_visible="draft,confirmed,done"/>
                    </header>
                    <sheet>
                        <widget name="web_ribbon" title="Archived"
                                bg_color="bg-danger" invisible="active"/>
                        <div class="oe_button_box" name="button_box">
                            <button name="action_view_lines" type="object"
                                    class="oe_stat_button" icon="fa-list">
                                <field name="line_count" widget="statinfo" string="Lines"/>
                            </button>
                        </div>
                        <div class="oe_title">
                            <h1><field name="name" placeholder="Record name..."/></h1>
                        </div>
                        <group>
                            <group>
                                <field name="partner_id"/>
                                <field name="date"/>
                            </group>
                            <group>
                                <field name="user_id"/>
                                <field name="priority" widget="priority"/>
                                <field name="active" invisible="1"/>
                            </group>
                        </group>
                        <notebook>
                            <page string="Lines" name="lines">
                                <field name="line_ids">
                                    <tree editable="bottom">
                                        <field name="product_id"/>
                                        <field name="quantity"/>
                                        <field name="price_unit"/>
                                        <field name="subtotal" sum="Total"/>
                                    </tree>
                                </field>
                            </page>
                            <page string="Notes" name="notes">
                                <field name="note" nolabel="1"
                                       placeholder="Internal notes..."/>
                            </page>
                        </notebook>
                    </sheet>
                    <div class="oe_chatter">
                        <field name="message_follower_ids"/>
                        <field name="activity_ids"/>
                        <field name="message_ids"/>
                    </div>
                </form>
            </field>
        </record>

        <!-- SEARCH -->
        <record id="view_my_module_search" model="ir.ui.view">
            <field name="name">my.module.search</field>
            <field name="model">my.module</field>
            <field name="arch" type="xml">
                <search string="Search My Module">
                    <field name="name"
                           filter_domain="['|',('name','ilike',self),('partner_id','ilike',self)]"/>
                    <filter string="My Records" name="my_records"
                            domain="[('user_id','=',uid)]"/>
                    <separator/>
                    <filter string="Draft" name="draft" domain="[('state','=','draft')]"/>
                    <filter string="Done"  name="done"  domain="[('state','=','done')]"/>
                    <filter string="Archived" name="archived" domain="[('active','=',False)]"/>
                    <group expand="0" string="Group By">
                        <filter string="Salesperson" name="group_user"
                                context="{'group_by': 'user_id'}"/>
                        <filter string="Status" name="group_state"
                                context="{'group_by': 'state'}"/>
                        <filter string="Date" name="group_date"
                                context="{'group_by': 'date:month'}"/>
                    </group>
                </search>
            </field>
        </record>

        <!-- KANBAN -->
        <record id="view_my_module_kanban" model="ir.ui.view">
            <field name="name">my.module.kanban</field>
            <field name="model">my.module</field>
            <field name="arch" type="xml">
                <kanban default_group_by="state" sample="1">
                    <field name="name"/>
                    <field name="state"/>
                    <field name="user_id"/>
                    <templates>
                        <t t-name="kanban-box">
                            <div class="oe_kanban_card oe_kanban_global_click">
                                <div class="o_kanban_record_top">
                                    <strong><field name="name"/></strong>
                                    <field name="priority" widget="priority"/>
                                </div>
                                <div class="o_kanban_record_bottom">
                                    <field name="user_id" widget="many2one_avatar_user"/>
                                </div>
                            </div>
                        </t>
                    </templates>
                </kanban>
            </field>
        </record>

        <!-- ACTION -->
        <record id="action_my_module" model="ir.actions.act_window">
            <field name="name">My Modules</field>
            <field name="res_model">my.module</field>
            <field name="view_mode">tree,kanban,form</field>
            <field name="search_view_id" ref="view_my_module_search"/>
            <field name="context">{'search_default_my_records': 1}</field>
            <field name="help" type="html">
                <p class="o_view_nocontent_smiling_face">Create your first record</p>
            </field>
        </record>

        <!-- MENU -->
        <menuitem id="menu_my_module_root" name="My Module" sequence="50"/>
        <menuitem id="menu_my_module"
                  parent="menu_my_module_root"
                  action="action_my_module"
                  sequence="10"/>

    </data>
</odoo>
```

---

## Common Anti-Patterns (v17)

### Using deprecated `attrs` / `states`

```xml
<!-- Rejected by the v17 validator -->
<field name="email" attrs="{'invisible': [('is_company','=',False)]}"/>
<field name="code"  states="draft,confirmed"/>
```

Use direct expressions:

```xml
<field name="email" invisible="not is_company"/>
<field name="code"  invisible="state not in ('draft','confirmed')"/>
```

### Using `<list>` instead of `<tree>` in v17

```xml
<!-- Odoo 18+ only -->
<list string="Records">...</list>
```

In v17 use `<tree>`:

```xml
<tree string="Records">...</tree>
```

This includes `view_mode` values on actions: **`tree,form`** (v17), not `list,form`.

### Using `<chatter/>` shortcut (v18+)

```xml
<!-- Not available in v17 -->
<chatter/>
```

Use the explicit v17 pattern:

```xml
<div class="oe_chatter">
    <field name="message_follower_ids"/>
    <field name="activity_ids"/>
    <field name="message_ids"/>
</div>
```

### Using `t-name="card"` in Kanban

```xml
<!-- Odoo 19 only -->
<t t-name="card">...</t>
```

In v17 the kanban card template is always `kanban-box`:

```xml
<t t-name="kanban-box">...</t>
```

### Hard-coded primary-key domains in views

```xml
<!-- Brittle, will break between DBs -->
<field name="partner_id" domain="[('id','=',42)]"/>
```

Use a meaningful domain or an XML-id reference in the action context instead.

---

## Coding Conventions

- Name view IDs `<model>_view_<type>` and use the matching dotted name in
  `ir.ui.view.name`.
- For inherited views, reuse the original view-ID portion and add a dotted
  `.inherit.<purpose>` suffix to the view name; primary views need none.
- Group records by model where practical, place `id` before `model`, and use
  meaningful XML IDs rather than generic names.

## Base Code Reference

All behaviour above is backed by the Odoo 17 source:

- `odoo/addons/base/models/ir_ui_view.py` — view types, `apply_inheritance_specs`, attrs/states validation (search for *"Since 17.0, the attrs and states attributes are no longer used."*).
- `odoo/addons/base/models/ir_actions.py` — `VIEW_TYPES`, `ir.actions.act_window.view_mode` (default `tree,form`).
- `odoo/tools/convert.py` — XML data loader, shorthand processing for `<template>`, `<menuitem>`.
- Real-world examples: `odoo/addons/base/views/*.xml`, `addons/sale/views/sale_order_views.xml`, `addons/mail/views/*.xml`.

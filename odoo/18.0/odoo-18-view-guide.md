---
name: odoo-18-view
description: Complete reference for Odoo 18 XML views, actions, menus, and QWeb templates. Covers list, form, search, kanban, graph, pivot, calendar views and Odoo 18 changes.
globs: **/views/**/*.xml
topics:
  - View types (list, form, search, kanban, graph, pivot, calendar, activity)
  - List view features (editable, decoration, optional fields, widgets)
  - Form view structure (sheet, button box, notebook, chatter)
  - Search view features (fields, filters, group by)
  - Kanban view (color, progress, templates)
  - Actions (window, server, client, report)
  - Menus (structure, attributes)
  - View inheritance (xpath, position, shorthand)
  - QWeb templates
when_to_use:
  - Writing XML views
  - Creating actions and menus
  - Implementing view inheritance
  - Building QWeb templates
  - Migrating from Odoo 17 to 18
---

# Odoo 18 View Guide

Complete reference for Odoo 18 XML views, actions, menus, and QWeb templates.

## Table of Contents

1. [View Types](#view-types)
2. [List View (Tree)](#list-view-tree)
3. [Form View](#form-view)
4. [Search View](#search-view)
5. [Kanban View](#kanban-view)
6. [Graph & Pivot Views](#graph--pivot-views)
7. [Calendar View](#calendar-view)
8. [Actions](#actions)
9. [Menus](#menus)
10. [View Inheritance](#view-inheritance)

---

## View Types

| Type | XML Tag | Use For |
|------|---------|---------|
| `list` | `<list>` | Table/List view (formerly `<tree>`) |
| `form` | `<form>` | Single record edit/view |
| `search` | `<search>` | Search panel and filters |
| `kanban` | `<kanban>` | Card-based view |
| `graph` | `<graph>` | Bar/line/pie charts |
| `pivot` | `<pivot>` | Pivot table |
| `calendar` | `<calendar>` | Calendar view |
| `activity` | `<activity>` | Activity/messaging view |
| `cohort` | `<cohort>` | Cohort analysis |
| `qweb` | `<template>` | QWeb template |

---

## List View (Tree)

### Basic List View

```xml
<record id="view_my_model_list" model="ir.ui.view">
    <field name="name">my.model.list</field>
    <field name="model">my.model</field>
    <field name="arch" type="xml">
        <list string="My Records">
            <field name="name"/>
            <field name="date"/>
            <field name="state"/>
        </list>
    </field>
</record>
```

### List View Features (Odoo 18)

```xml
<list string="My Records"
      sample="1"              # Show sample data when empty
      multi_edit="1"          # Enable inline edit
      editable="bottom"       # Edit mode (top/bottom)
      default_order="date desc"
      limit="80">

    <!-- Decoration (row styling) -->
    <field name="state"
           decoration-success="state == 'done'"
           decoration-danger="state == 'cancel'"
           decoration-muted="not active"/>

    <!-- Optional fields -->
    <field name="phone" optional="show"/>    <!-- shown by default -->
    <field name="mobile" optional="hide"/>    <!-- hidden by default -->
    <field name="note" optional="hide"/>      <!-- can toggle in UI -->

    <!-- Special widgets -->
    <field name="image" widget="image"/>
    <field name="user_id" widget="many2one_avatar_user"/>
    <field name="category_id" widget="many2many_tags" options="{'color_field': 'color'}"/>
    <field name="sequence" widget="handle"/>   <!-- drag to reorder -->

    <!-- Groups restriction -->
    <field name="company_id" groups="base.group_multi_company"/>
</list>
```

### Decoration Types

| Type | Color | Use For |
|------|-------|---------|
| `decoration-danger` | Red | Error, cancelled |
| `decoration-warning` | Orange | Warning |
| `decoration-success` | Green | Success, done |
| `decoration-info` | Blue | Info |
| `decoration-muted` | Gray | Inactive, archived |
| `decoration-bf` | Bold font | Highlight |
| `decoration-it` | Italic | Emphasis |

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

### Form View Structure (Odoo 18)

```xml
<form string="My Record" create="true" edit="true" delete="true">

    <!-- Edit-only alerts -->
    <div class="alert alert-warning oe_edit_only" role="alert"
         invisible="not warning_message">
        <field name="warning_message"/>
    </div>

    <!-- Ribbon (archived badge) -->
    <widget name="web_ribbon" title="Archived"
            bg_color="text-bg-danger" invisible="active"/>

    <sheet>
        <!-- Button box (stat buttons) -->
        <div class="oe_button_box" name="button_box">
            <button name="action_confirm" type="object" class="oe_stat_button" icon="fa-check">
                <div class="o_field_widget o_stat_info">
                    <span class="o_stat_text">Confirm</span>
                </div>
            </button>
        </div>

        <!-- Chatter -->
        <div class="oe_chatter">
            <field name="message_ids"/>
            <field name="activity_ids"/>
        </div>

        <!-- Main content -->
        <group>
            <group>
                <field name="name" default_focus="1" placeholder="Record Name"/>
                <field name="code" required="1"/>
            </group>
            <group>
                <field name="user_id"/>
                <field name="company_id"/>
            </group>
        </group>

        <!-- Notebook (tabs) -->
        <notebook>
            <page string="Information" name="info">
                <group>
                    <field name="description"/>
                </group>
            </page>
            <page string="Lines" name="lines">
                <field name="line_ids" nolabel="1">
                    <tree editable="bottom">
                        <field name="product_id"/>
                        <field name="quantity"/>
                    </tree>
                </field>
            </page>
        </notebook>
    </sheet>

    <!-- Chatter (alternative position) -->
    <div class="oe_chatter">
        <field name="message_ids"/>
        <field name="activity_ids"/>
    </div>
</form>
```

### Field Widgets (Form)

```xml
<!-- Basic fields -->
<field name="name"/>
<field name="description" widget="text"/>  <!-- Long text -->
<field name="notes" widget="text" placeholder="Notes..."/>

<!-- Date/Datetime -->
<field name="date" widget="date"/>
<field name="datetime" widget="datetime"/>

<!-- Specialized widgets -->
<field name="email" widget="email"/>
<field name="phone" widget="phone" options="{'enable_sms': false}"/>
<field name="website" widget="url"/>
<field name="image" widget="image" class="oe_avatar"/>

<!-- Many2one with options -->
<field name="partner_id" options="{'no_open': True, 'no_create': True}"/>
<field name="user_id" widget="many2one_avatar_user"/>

<!-- Many2many -->
<field name="tag_ids" widget="many2many_tags" options="{'color_field': 'color'}"/>
<field name="category_ids" widget="many2many_checkboxes"/>

<!-- Radio, Boolean -->
<field name="type" widget="radio"/>
<field name="active" widget="boolean_toggle"/>

<!-- Selection -->
<field name="state" widget="statusbar"/>
<field name="priority" widget="priority"/>

<!-- Monetary -->
<field name="amount" widget="monetary" options="{'currency_field': 'currency_id'"/>

<!-- Read-only indicators -->
<field name="country_id" readonly="1"/>
<field name="create_date" readonly="1" widget="relative"/>

<!-- Domain widget (visual domain builder) -->
<field name="domain" widget="domain"/>

<!-- Code editor -->
<field name="arch" widget="code" options="{'mode': 'xml'}"/>
```

### Field Options

```xml
<!-- Common options -->
<field name="name" options="{'horizontal': true}"/>  <!-- radio horizontal -->
<field name="name" options="{'line_breaks': false}"/>  <!-- text widget -->
<field name="partner_id" options="{'no_open': True, 'no_create': True}"/>
<field name="date" options="{'no_create': True}"/>

<!-- Placeholder -->
<field name="email" placeholder="email@example.com"/>

<!-- Required / Readonly -->
<field name="name" required="1"/>
<field name="code" readonly="1"/>

<!-- Invisible -->
<field name="field_a" invisible="not is_company"/>

<!-- Context / Domain -->
<field name="product_id" context="{'default_type': 'service'}"/>
<field name="partner_id" domain="[('supplier_rank', '>', 0)]"/>

<!-- Class -->
<field name="phone" class="o_force_ltr"/>
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
            <field name="code"/>
            <filter string="Active" name="active" domain="[('active', '=', True)]"/>
            <filter string="Draft" name="draft" domain="[('state', '=', 'draft')]"/>
        </search>
    </field>
</record>
```

### Search View Features (Odoo 18)

```xml
<search string="Search My Model">

    <!-- Searchable fields -->
    <field name="name"
           filter_domain="['|', ('name', 'ilike', self), ('code', 'ilike', self)]"
           string="Name"/>
    <field name="partner_id"/>
    <field name="date"/>

    <!-- Filters (saved searches) -->
    <filter string="My Records" name="my_records"
            domain="[('user_id', '=', uid)]"/>
    <filter string="This Month" name="this_month"
            domain="[('date', '>=', (context_today() + relativedelta(day=1)).strftime('%Y-%m-%d'))]"/>

    <!-- Separator -->
    <separator/>

    <!-- Group By -->
    <group expand="0" string="Group By">
        <filter string="State" name="state" context="{'group_by': 'state'}"/>
        <filter string="Partner" name="partner" context="{'group_by': 'partner_id'}"/>
        <filter string="Date" name="date" context="{'group_by': 'date:month'}"/>
    </group>
</search>
```

---

## Kanban View

### Basic Kanban View

```xml
<record id="view_my_model_kanban" model="ir.ui.view">
    <field name="name">my.model.kanban</field>
    <field name="model">my.model</field>
    <field name="arch" type="xml">
        <kanban default_group_by="state" quick_create="false">
            <field name="name"/>
            <field name="state"/>
            <templates>
                <t t-name="kanban-box">
                    <div class="oe_kanban_card">
                        <field name="name"/>
                        <field name="state"/>
                    </div>
                </t>
            </templates>
        </kanban>
    </field>
</record>
```

### Kanban with Color and Progress

```xml
<kanban default_group_by="state"
       class="o_kanban_small_column"
       quick_create="true"
       drag_drop="true"
       group_drag_drop="true">

    <field name="name"/>
    <field name="priority"/>
    <field name="color"/>

    <templates>
        <t t-name="kanban-box">
            <div t-attf-class="oe_kanban_card oe_kanban_global_click">
                <div class="oe_kanban_content">
                    <!-- Color bar -->
                    <div class="oe_kanban_card_header"
                         t-attf-style="background-color: #{record.color.raw_value or '#EEE'}">
                        <field name="name"/>
                    </div>

                    <!-- Priority -->
                    <field name="priority" widget="priority"/>

                    <!-- Footer -->
                    <div class="oe_kanban_footer">
                        <field name="date"/>
                    </div>
                </div>
            </div>
        </t>
    </templates>
</kanban>
```

---

## Graph & Pivot Views

### Graph View (Charts)

```xml
<record id="view_my_model_graph" model="ir.ui.view">
    <field name="name">my.model.graph</field>
    <field name="model">my.model</field>
    <field name="arch" type="xml">
        <graph string="Sales Analysis" type="bar">
            <field name="date" interval="month" type="row"/>
            <field name="partner_id" type="col"/>
            <field name="amount" type="measure"/>
        </graph>
    </field>
</record>
```

**Graph attributes**:
- `type`: `bar`, `line`, `pie`
- `stacked`: `true` for stacked charts
- `interval`: `day`, `week`, `month`, `quarter`, `year`

### Pivot View

```xml
<record id="view_my_model_pivot" model="ir.ui.view">
    <field name="name">my.model.pivot</field>
    <field name="model">my.model</field>
    <field name="arch" type="xml">
        <pivot string="Sales Analysis">
            <field name="date" interval="month" type="row"/>
            <field name="partner_id" type="col"/>
            <field name="amount" type="measure"/>
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
        <calendar string="My Meetings"
                  date_start="start"
                  date_stop="stop"
                  color="partner_id"
                  mode="month">
            <field name="name"/>
            <field name="partner_id"/>
        </calendar>
    </field>
</record>
```

**Calendar attributes**:
- `date_start`: Start date field (required)
- `date_stop`: End date field
- `date_delay`: Duration alternative to date_stop
- `color`: Field for color coding
- `mode`: `day`, `week`, `month`, `year`

---

## Actions

### Window Action (ir.actions.act_window)

```xml
<record id="action_my_model" model="ir.actions.act_window">
    <field name="name">My Model</field>
    <field name="res_model">my.model</field>
    <field name="view_mode">tree,form</field>
    <field name="domain">[]</field>
    <field name="context">{'search_default_active': 1}</field>
    <field name="view_id" ref="view_my_model_tree"/>
    <field name="limit">80</field>
    <field name="target">current</field>  <!-- or "new" for popup -->
    <field name="help" type="html">
        <p class="o_view_nocontent_smiling_face">
            Create your first record!
        </p>
    </field>
</record>
```

### Server Action (ir.actions.server)

```xml
<record id="action_my_server" model="ir.actions.server">
    <field name="name">My Server Action</field>
    <field name="model_id" ref="model_my_model"/>
    <field name="state">code</field>
    <field name="code">
        records.action_done()
    </field>
</record>
```

**Server action states**:
- `code`: Execute Python code
- `object_create`: Create new record
- `object_write`: Update records
- `object_delete`: Delete records
- `multi`: Execute multiple actions

### Client Action (ir.actions.client)

```xml
<record id="action_my_client" model="ir.actions.client">
    <field name="name">My Client Action</field>
    <field name="tag">reload</field>  <!-- reload, opening, etc. -->
    <field name="params">{'param': 'value'}</field>
</record>
```

### Report Action (ir.actions.report)

```xml
<record id="report_my_model" model="ir.actions.report">
    <field name="name">My Report</field>
    <field name="model">my.model</field>
    <field name="report_type">qweb-pdf</field>
    <field name="report_name">my_module.report_template</field>
    <field name="report_file">my_report</field>
    <field name="binding_model_id" ref="model_my_model"/>
    <field name="binding_type">report</field>
</record>
```

---

## Menus

### Menu Structure

```xml
<!-- Top-level menu -->
<menuitem id="menu_my_root"
          name="My Module"
          sequence="10"/>

<!-- Sub-menu -->
<menuitem id="menu_my_model"
          name="My Models"
          parent="menu_my_root"
          action="action_my_model"
          sequence="1"/>

<!-- Without action (folder) -->
<menuitem id="menu_my_folder"
          name="Folder"
          parent="menu_my_root"
          sequence="2"/>
```

### Menu Attributes

| Attribute | Description |
|-----------|-------------|
| `id` | Unique XML ID |
| `name` | Display name |
| `parent` | Parent menu XML ID |
| `action` | Action to execute |
| `sequence` | Sort order (lower = first) |
| `groups` | Comma-separated group IDs |
| `web_icon` | Icon for web client |
| `active` | True/False |

---

## View Inheritance

### Extend View with XPath

```xml
<record id="view_res_partner_form_inherit" model="ir.ui.view">
    <field name="name">res.partner.form.inherit</field>
    <field name="model">res.partner</field>
    <field name="inherit_id" ref="base.view_partner_form"/>
    <field name="arch" type="xml">

        <!-- Insert after existing field -->
        <xpath expr="//field[@name='email']" position="after">
            <field name="my_field"/>
        </xpath>

        <!-- Replace entire element -->
        <xpath expr="//field[@name='name']" position="replace">
            <field name="name" required="1" placeholder="Name..."/>
        </xpath>

        <!-- Add inside element (before content) -->
        <xpath expr="//sheet/group" position="inside">
            <field name="extra_field"/>
        </xpath>

        <!-- Add before element -->
        <xpath expr="//field[@name='email']" position="before">
            <field name="prefix_field"/>
        </xpath>

        <!-- Remove element -->
        <xpath expr="//field[@name='old_field']" position="replace"/>

        <!-- Modify attributes -->
        <xpath expr="//field[@name='name']" position="attributes">
            <attribute name="required">True</attribute>
            <attribute name="readonly">True</attribute>
        </xpath>

        <!-- Add attribute -->
        <xpath expr="//field[@name='name']" position="attributes">
            <attribute name="placeholder" add="true">Enter name</attribute>
        </xpath>

    </field>
</record>
```

### Shorthand Position (Odoo 18)

```xml
<!-- Instead of xpath, use direct field name with position -->
<field name="email" position="after">
    <field name="my_field"/>
</field>

<field name="name" position="replace">
    <field name="name" required="1"/>
</field>

<sheet position="inside">
    <div class="my_class">Content</div>
</sheet>
```

---

## Complete Module Example

```xml
<?xml version="1.0" encoding="utf-8"?>
<odoo>
    <data>

        <!-- LIST VIEW -->
        <record id="view_my_module_list" model="ir.ui.view">
            <field name="name">my.module.list</field>
            <field name="model">my.module</field>
            <field name="arch" type="xml">
                <list string="My Modules">
                    <field name="name" decoration-success="state == 'done'"/>
                    <field name="date"/>
                    <field name="state"/>
                    <field name="user_id" optional="show"/>
                </list>
            </field>
        </record>

        <!-- FORM VIEW -->
        <record id="view_my_module_form" model="ir.ui.view">
            <field name="name">my.module.form</field>
            <field name="model">my.module</field>
            <field name="arch" type="xml">
                <form string="My Module" create="true">
                    <sheet>
                        <div class="oe_button_box" name="button_box">
                            <button name="action_confirm" type="object"
                                    string="Confirm" class="oe_stat_button" icon="fa-check"/>
                        </div>
                        <widget name="web_ribbon" title="Archived"
                                bg_color="text-bg-danger" invisible="active"/>
                        <div class="oe_title">
                            <h1>
                                <field name="name" placeholder="Module Name"/>
                            </h1>
                        </div>
                        <group>
                            <group>
                                <field name="date"/>
                                <field name="user_id"/>
                            </group>
                            <group>
                                <field name="state" widget="statusbar"/>
                                <field name="priority" widget="priority"/>
                            </group>
                        </group>
                        <notebook>
                            <page string="Description">
                                <field name="description" nolabel="1"/>
                            </page>
                            <page string="Lines">
                                <field name="line_ids" nolabel="1">
                                    <tree editable="bottom">
                                        <field name="product_id"/>
                                        <field name="quantity"/>
                                        <field name="price"/>
                                    </tree>
                                </field>
                            </page>
                        </notebook>
                    </sheet>
                    <div class="oe_chatter">
                        <field name="message_ids"/>
                        <field name="activity_ids"/>
                    </div>
                </form>
            </field>
        </record>

        <!-- SEARCH VIEW -->
        <record id="view_my_module_search" model="ir.ui.view">
            <field name="name">my.module.search</field>
            <field name="model">my.module</field>
            <field name="arch" type="xml">
                <search string="Search My Module">
                    <field name="name" filter_domain="['|', ('name', 'ilike', self), ('code', 'ilike', self)]"/>
                    <filter string="My Items" name="my_items" domain="[('user_id', '=', uid)]"/>
                    <separator/>
                    <filter string="Draft" name="draft" domain="[('state', '=', 'draft')]"/>
                    <filter string="Done" name="done" domain="[('state', '=', 'done')]"/>
                    <group expand="0" string="Group By">
                        <filter string="State" name="state" context="{'group_by': 'state'}"/>
                        <filter string="User" name="user" context="{'group_by': 'user_id'}"/>
                    </group>
                </search>
            </field>
        </record>

        <!-- KANBAN VIEW -->
        <record id="view_my_module_kanban" model="ir.ui.view">
            <field name="name">my.module.kanban</field>
            <field name="model">my.module</field>
            <field name="arch" type="xml">
                <kanban default_group_by="state">
                    <field name="name"/>
                    <field name="state"/>
                    <templates>
                        <t t-name="kanban-box">
                            <div class="oe_kanban_card">
                                <div class="oe_kanban_content">
                                    <strong><field name="name"/></strong>
                                    <field name="state"/>
                                </div>
                            </div>
                        </t>
                    </templates>
                </kanban>
            </field>
        </record>

        <!-- ACTION -->
        <record id="action_my_module" model="ir.actions.act_window">
            <field name="name">My Module</field>
            <field name="res_model">my.module</field>
            <field name="view_mode">tree,form,kanban</field>
            <field name="context">{'search_default_my_items': 1}</field>
            <field name="help" type="html">
                <p class="o_view_nocontent_smiling_face">
                    Create your first record!
                </p>
            </field>
        </record>

        <!-- MENU -->
        <menuitem id="menu_my_root" name="My Module" sequence="50"/>
        <menuitem id="menu_my_module" name="Records"
                  parent="menu_my_root"
                  action="action_my_module"
                  sequence="1"/>

    </data>
</odoo>
```

---

## QWeb Templates

### Basic Template

```xml
<template id="my_module_template">
    <div class="my_class">
        <h1>My Template</h1>
        <t t-if="records">
            <t t-foreach="records" t-as="record">
                <span t-esc="record.name"/>
            </t>
        </t>
        <t t-else="">
            <p>No records found</p>
        </t>
    </div>
</template>
```

### Inherit Template

```xml
<template id="website_sale_products_inherit" inherit_id="website_sale.products">
    <xpath expr="//div[@id='products_wrap']" position="inside">
        <div class="my_extra_content">Extra content</div>
    </xpath>
</template>
```

---

## Common Anti-Patterns

### ❌ BAD: Using old `<tree>` tag

```xml
<!-- Odoo 17- -->
<tree string="Records">
    <field name="name"/>
</tree>
```

### ✅ GOOD: Use `<list>` tag

```xml
<!-- Odoo 18+ -->
<list string="Records">
    <field name="name"/>
</list>
```

### ❌ BAD: Missing `inverse_name` for One2many

```xml
<field name="line_ids" comodel_name="sale.order.line"/>
```

### ✅ GOOD: Always specify `inverse_name`

```xml
<field name="line_ids" comodel_name="sale.order.line" inverse_name="order_id"/>
```

### ❌ BAD: Hardcoded domain in view

```xml
<field name="partner_id" domain="[('id', '=', 1)]"/>
```

### ✅ GOOD: Use dynamic domain or none

```xml
<field name="partner_id" domain="[('supplier_rank', '>', 0)]"/>
```

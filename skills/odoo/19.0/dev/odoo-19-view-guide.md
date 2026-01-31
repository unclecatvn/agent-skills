# Odoo 19 View Guide

Guide for creating views in Odoo 19: list, form, search, kanban, calendar, graph, pivot, and QWeb templates.

## Table of Contents
- [View Types](#view-types)
- [List Views](#list-views)
- [Form Views](#form-views)
- [Search Views](#search-views)
- [Kanban Views](#kanban-views)
- [Calendar Views](#calendar-views)
- [Graph Views](#graph-views)
- [Pivot Views](#pivot-views)
- [View Inheritance](#view-inheritance)
- [QWeb Templates](#qweb-templates)

---

## View Types

| Type | Tag | Description |
|------|-----|-------------|
| List | `<list>` | Table view (formerly `<tree>`) |
| Form | `<form>` | Single record view |
| Search | `<search>` | Search/filter view |
| Kanban | `<kanban>` | Card-based view |
| Calendar | `<calendar>` | Calendar view |
| Graph | `<graph>` | Chart view |
| Pivot | `<pivot>` | Pivot table view |
| Activity | `<activity>` | Activity view |
| QWeb | `<template>` | HTML/PDF template |

---

## List Views

### Basic List View

```xml
<record id="view_my_model_tree" model="ir.ui.view">
    <field name="name">my.model.tree</field>
    <field name="model">my.model</field>
    <field name="arch" type="xml">
        <list string="My Models">
            <field name="name"/>
            <field name="code"/>
            <field name="date"/>
        </list>
    </field>
</record>
```

### List View Options

```xml
<list string="My Models" editable="bottom" multi_edit="1" limit="80">
    <field name="name"/>
    <field name="code"/>
</list>
```

| Option | Description |
|---------|-------------|
| `editable` | `top` or `bottom`: inline editing |
| `multi_edit` | Enable multi-row editing |
| `limit` | Default records per page |
| `create` | Show create button (default: true) |

### Decoration

```xml
<list string="My Models">
    <field name="state" decoration-success="state == 'done'"
                       decoration-warning="state == 'pending'"
                       decoration-danger="state == 'cancelled'"/>
    <field name="name"/>
</list>
```

| Decoration | Description |
|-------------|-------------|
| `decoration-success` | Green |
| `decoration-warning` | Yellow/Orange |
| `decoration-danger` | Red |
| `decoration-info` | Blue |
| `decoration-muted` | Grey |
| `decoration-bf` | Bold font |
| `decoration-it` | Italic font |

### Optional Fields

```xml
<list string="My Models">
    <field name="name"/>
    <field name="description" optional="show"/>
    <field name="notes" optional="hide"/>
</list>
```

---

## Form Views

### Basic Form View

```xml
<record id="view_my_model_form" model="ir.ui.view">
    <field name="name">my.model.form</field>
    <field name="model">my.model</field>
    <field name="arch" type="xml">
        <form string="My Model">
            <sheet>
                <group>
                    <group>
                        <field name="name"/>
                        <field name="code"/>
                    </group>
                    <group>
                        <field name="active"/>
                        <field name="date"/>
                    </group>
                </group>
                <notebook>
                    <page string="Description">
                        <field name="description"/>
                    </page>
                    <page string="Notes">
                        <field name="notes"/>
                    </page>
                </notebook>
            </sheet>
        </form>
    </field>
</record>
```

### Form Attributes

```xml
<form string="My Model" create="false" edit="false" delete="false">
    ...
</form>
```

| Attribute | Description |
|-----------|-------------|
| `create` | Show create button |
| `edit` | Show edit button |
| `delete` | Show delete button |

### Chatter

```xml
<form string="My Model">
    <sheet>
        <!-- Form content -->
    </sheet>
    <div class="oe_chatter">
        <field name="message_follower_ids"/>
        <field name="activity_ids"/>
        <field name="message_ids"/>
    </div>
</form>
```

Or use shortcut:

```xml
<form string="My Model">
    <sheet>
        <!-- Form content -->
    </sheet>
    <chatter/>
</form>
```

### Statusbar

```xml
<form string="My Model">
    <header>
        <button name="action_confirm" string="Confirm" type="object" states="draft"/>
        <button name="action_done" string="Done" type="object" states="confirmed"/>
        <field name="state" widget="statusbar"/>
    </header>
    <sheet>
        <!-- Form content -->
    </sheet>
</form>
```

---

## Search Views

### Basic Search View

```xml
<record id="view_my_model_search" model="ir.ui.view">
    <field name="name">my.model.search</field>
    <field name="model">my.model</field>
    <field name="arch" type="xml">
        <search string="Search My Models">
            <field name="name"/>
            <field name="code"/>
            <filter string="Active" name="active" domain="[('active','=',True)]"/>
            <separator/>
            <group expand="0" string="Group By">
                <filter string="State" name="state" context="{'group_by': 'state'}"/>
            </group>
        </search>
    </field>
</record>
```

### Custom Filters

```xml
<search string="Search My Models">
    <field name="name"/>
    <field name="partner_id"/>

    <!-- Simple filter -->
    <filter string="Active" name="active" domain="[('active','=',True)]"/>

    <!-- Advanced filter -->
    <filter string="My Partners" domain="[('partner_id.user_id', '=', uid)]"/>

    <!-- Separator -->
    <separator/>

    <!-- Group by -->
    <group expand="0" string="Group By">
        <filter string="State" name="state" context="{'group_by': 'state'}"/>
        <filter string="Partner" name="partner_id" context="{'group_by': 'partner_id'}"/>
    </group>
</search>
```

---

## Kanban Views

### Basic Kanban View

```xml
<record id="view_my_model_kanban" model="ir.ui.view">
    <field name="name">my.model.kanban</field>
    <field name="model">my.model</field>
    <field name="arch" type="xml">
        <kanban string="My Models" default_group_by="state">
            <field name="name"/>
            <field name="state"/>
            <templates>
                <t t-name="kanban-box">
                    <div class="oe_kanban_card">
                        <div class="oe_kanban_content">
                            <strong><field name="name"/></strong>
                            <div><field name="state"/></div>
                        </div>
                    </div>
                </t>
            </templates>
        </kanban>
    </field>
</record>
```

### Kanban with Colors

```xml
<kanban default_group_by="state" color="priority">
    <field name="name"/>
    <field name="priority"/>
    <field name="state"/>
    <templates>
        <t t-name="kanban-box">
            <div class="oe_kanban_card">
                <div class="oe_kanban_content">
                    <field name="name"/>
                </div>
            </div>
        </t>
    </templates>
</kanban>
```

---

## Calendar Views

### Calendar View

```xml
<record id="view_my_model_calendar" model="ir.ui.view">
    <field name="name">my.model.calendar</field>
    <field name="model">my.model</field>
    <field name="arch" type="xml">
        <calendar string="My Calendar" date_start="date_start" date_end="date_end">
            <field name="name"/>
            <field name="user_id"/>
        </calendar>
    </field>
</record>
```

| Attribute | Description |
|-----------|-------------|
| `date_start` | Start date field |
| `date_end` | End date field |
| `date_delay` | Duration field (alternative to date_end) |
| `color` | Field for color |
| `mode` | Default view (month, week, day) |

---

## Graph Views

### Graph View

```xml
<record id="view_my_model_graph" model="ir.ui.view">
    <field name="name">my.model.graph</field>
    <field name="model">my.model</field>
    <field name="arch" type="xml">
        <graph string="Sales Analysis" type="bar">
            <field name="date" interval="month" type="row"/>
            <field name="product_id" type="col"/>
            <field name="price_total" type="measure"/>
        </graph>
    </field>
</record>
```

| Attribute | Description |
|-----------|-------------|
| `type` | `bar`, `pie`, `line` |
| `stacked` | Stack bars |

---

## Pivot Views

### Pivot View

```xml
<record id="view_my_model_pivot" model="ir.ui.view">
    <field name="name">my.model.pivot</field>
    <field name="model">my.model</field>
    <field name="arch" type="xml">
        <pivot string="Sales Analysis">
            <field name="date" interval="month" type="row"/>
            <field name="product_id" type="col"/>
            <field name="price_total" type="measure"/>
        </pivot>
    </field>
</record>
```

---

## View Inheritance

### Extend View

```xml
<record id="view_my_model_form_inherit" model="ir.ui.view">
    <field name="name">my.model.form.inherit</field>
    <field name="model">my.model</field>
    <field name="inherit_id" ref="view_my_model_form"/>
    <field name="arch" type="xml">
        <xpath expr="//field[@name='name']" position="after">
            <field name="new_field"/>
        </xpath>
    </field>
</record>
```

### Position Options

| Position | Description |
|----------|-------------|
| `inside` | Inside element |
| `replace` | Replace element |
| `before` | Before element |
| `after` | After element |
| `attributes` | Modify attributes |

### Example: Add Field

```xml
<xpath expr="//field[@name='name']" position="after">
    <field name="new_field"/>
</xpath>
```

### Example: Replace Field

```xml
<xpath expr="//field[@name='name']" position="replace">
    <field name="name" widget="char" required="1"/>
</xpath>
```

### Example: Modify Attributes

```xml
<xpath expr="//field[@name='name']" position="attributes">
    <attribute name="required">True</attribute>
</xpath>
```

---

## QWeb Templates

### Basic Template

```xml
<template id="my_template" name="My Template">
    <div class="my-class">
        <h1>Hello World</h1>
    </div>
</template>
```

### Template Inheritance

```xml
<template id="my_template_inherit" inherit_id="my_template" name="My Template Inherit">
    <xpath expr="//div[@class='my-class']" position="inside">
        <p>This is inherited content</p>
    </xpath>
</template>
```

### QWeb Directives

| Directive | Description |
|-----------|-------------|
| `t-esc` | Escape and output |
| `t-raw` | Output raw (XSS risk) |
| `t-field` | Output formatted field |
| `t-if` | Conditional |
| `t-elif` | Else if |
| `t-else` | Else |
| `t-foreach` | Loop |
| `t-as` | Loop variable |
| `t-set` | Set variable |
| `t-call` | Call template |
| `t-att-*` | Set attribute |

---

## References

- Odoo 19 official documentation

---
name: odoo-18-actions
description: Complete reference for Odoo 18 actions (ir.actions.*). Covers window actions, URL actions, server actions, report actions, client actions, scheduled actions, and action bindings.
globs: "**/*.{py,xml}"
topics:
  - Window actions (ir.actions.act_window)
  - URL actions (ir.actions.act_url)
  - Server actions (ir.actions.server)
  - Report actions (ir.actions.report)
  - Client actions (ir.actions.client)
  - Scheduled actions (ir.cron)
  - Action bindings (binding_model_id, binding_type)
when_to_use:
  - Creating menu items and action buttons
  - Defining window actions for models
  - Setting up scheduled/cron jobs
  - Configuring server actions for automation
  - Creating report actions
  - Implementing client-side actions
---

# Odoo 18 Actions Guide

Complete reference for Odoo 18 actions: window, URL, server, report, client, and scheduled actions with bindings.

## Table of Contents

1. [Action Basics](#action-basics)
2. [Window Actions](#window-actions)
3. [URL Actions](#url-actions)
4. [Server Actions](#server-actions)
5. [Report Actions](#report-actions)
6. [Client Actions](#client-actions)
7. [Scheduled Actions](#scheduled-actions)
8. [Action Bindings](#action-bindings)

---

## Action Basics

### What are Actions?

Actions define the behavior of the system in response to user actions: login, action button, selection of an invoice, etc.

### Common Action Attributes

All actions share these mandatory attributes:

| Attribute | Type | Description |
|-----------|------|-------------|
| `type` | string | Category of the action (determines available fields) |
| `name` | string | Short user-readable description |

### Action Forms

A client can receive actions in 4 forms:

| Form | Description |
|------|-------------|
| `False` | Close any open action dialog |
| String | Client action tag or number |
| Number | Database ID or external ID of an action record |
| Dictionary | Client action descriptor to execute |

---

## Window Actions

### `ir.actions.act_window` - Most Common Action

The most common action type, used to present visualizations of a model through views.

#### Window Action Fields

| Field | Type | Description |
|-------|------|-------------|
| `res_model` | string | Model to present views for (required) |
| `views` | list | List of `[(view_id, view_type)]` pairs |
| `res_id` | int | Record to load for form views (optional) |
| `search_view_id` | (id, name) | Specific search view to load (optional) |
| `target` | string | Where to open: `current`, `fullscreen`, `new`, `main` |
| `context` | dict | Additional context data for views |
| `domain` | list | Filtering domain for search queries |
| `limit` | int | Records to display in lists (default: 80) |

#### View Types

| Type | Description |
|------|-------------|
| `list` | List view (formerly `tree` in Odoo 17) |
| `form` | Form view |
| `graph` | Graph view |
| `pivot` | Pivot view |
| `kanban` | Kanban view |
| `calendar` | Calendar view |
| `gantt` | Gantt view |
| `map` | Map view |
| `activity` | Activity view |
| `search` | Search view |

### Window Action Examples

#### Basic List and Form Views

```xml
<record id="action_customer" model="ir.actions.act_window">
    <field name="name">Customers</field>
    <field name="res_model">res.partner</field>
    <field name="view_mode">list,form</field>
    <field name="domain">[('customer', '=', True)]</field>
</record>
```

#### Using Dictionary (Python)

```python
{
    "type": "ir.actions.act_window",
    "res_model": "res.partner",
    "views": [[False, "list"], [False, "form"]],
    "domain": [["customer", "=", true]],
}
```

#### Open Specific Record in Dialog

```python
{
    "type": "ir.actions.act_window",
    "res_model": "product.product",
    "views": [[False, "form"]],
    "res_id": a_product_id,
    "target": "new",
}
```

#### Custom Search View

```xml
<record id="action_sale_order" model="ir.actions.act_window">
    <field name="name">Sales Orders</field>
    <field name="res_model">sale.order</field>
    <field name="view_mode">list,form</field>
    <field name="search_view_id" ref="sale_view_search"/>
    <field name="context">{'default_user_id': uid}</field>
</record>
```

### In-Database Window Action Fields

These fields are used in XML data files:

| Field | Description |
|-------|-------------|
| `view_mode` | Comma-separated view types (no spaces!) |
| `view_ids` | M2M to view objects for initial views |
| `view_id` | Specific view to add if in view_mode |

```xml
<record model="ir.actions.act_window" id="test_action">
    <field name="name">A Test Action</field>
    <field name="res_model">some.model</field>
    <field name="view_mode">graph</field>
    <field name="view_id" ref="my_specific_view"/>
</record>
```

### ir.actions.act_window.view (Cleaner Approach)

```xml
<record model="ir.actions.act_window.view" id="test_action_tree">
   <field name="sequence" eval="1"/>
   <field name="view_mode">list</field>
   <field name="view_id" ref="view_test_list"/>
   <field name="act_window_id" ref="test_action"/>
</record>
```

---

## URL Actions

### `ir.actions.act_url` - Open Web Pages

Allow opening a URL (website/web page) via an Odoo action.

| Field | Type | Description |
|-------|------|-------------|
| `url` | string | Address to open (required) |
| `target` | string | `new`, `self`, or `download` (default: `new`) |

### URL Action Examples

```xml
<record id="action_open_documentation" model="ir.actions.act_url">
    <field name="name">Documentation</field>
    <field name="url">https://odoo.com</field>
    <field name="target">new</field>
</record>
```

```python
{
    "type": "ir.actions.act_url",
    "url": "https://odoo.com",
    "target": "self",  # Replaces current content
}
```

### Target Values

| Value | Description |
|-------|-------------|
| `new` | Opens URL in new window/page |
| `self` | Replaces current window/page content |
| `download` | Redirects to a download URL |

---

## Server Actions

### `ir.actions.server` - Execute Python Code

Allow triggering complex server code from any valid action location.

#### Server Action Fields

| Field | Type | Description |
|-------|------|-------------|
| `id` | int | In-database identifier of the server action |
| `model_id` | Many2one | Odoo model linked to the action |
| `state` | Selection | Type of action: `code`, `object_create`, `object_write`, `multi` |
| `code` | Text | Python code to execute (for `code` state) |
| `crud_model_id` | Many2one | Model for create actions |
| `child_ids` | One2many | Sub-actions for `multi` state |

### Server Action States

#### `code` - Execute Python Code

```xml
<record model="ir.actions.server" id="print_instance">
    <field name="name">Res Partner Server Action</field>
    <field name="model_id" ref="model_res_partner"/>
    <field name="state">code</field>
    <field name="code">
        raise Warning(record.name)
    </field>
</record>
```

#### Returning Next Action

```xml
<record model="ir.actions.server" id="open_related">
    <field name="name">Open Related Record</field>
    <field name="model_id" ref="model_res_partner"/>
    <field name="state">code</field>
    <field name="code">
        if record.some_condition():
            action = {
                "type": "ir.actions.act_window",
                "view_mode": "form",
                "res_model": record._name,
                "res_id": record.id,
            }
    </field>
</record>
```

#### `object_create` - Create New Record

```xml
<record model="ir.actions.server" id="create_task">
    <field name="name">Create Task from Lead</field>
    <field name="model_id" ref="model_crm_lead"/>
    <field name="state">object_create</field>
    <field name="crud_model_id" ref="model_project_task"/>
    <field name="link_field_id" ref="field_project_task_lead_id"/>
    <!-- fields_lines specifications -->
</record>
```

#### `object_write` - Update Current Record

```xml
<record model="ir.actions.server" id="mark_done">
    <field name="name">Mark as Done</field>
    <field name="model_id" ref="model_my_model"/>
    <field name="state">object_write</field>
    <!-- fields_lines specifications -->
</record>
```

#### `multi` - Execute Multiple Actions

```xml
<record model="ir.actions.server" id="multi_action">
    <field name="name">Multi Action</field>
    <field name="model_id" ref="model_res_partner"/>
    <field name="state">multi</field>
    <field name="child_ids" eval="[
        ref('action_create'),
        ref('action_notify'),
    ]"/>
</record>
```

### Evaluation Context

Available variables in server action code:

| Variable | Description |
|----------|-------------|
| `model` | Model object linked via `model_id` |
| `record` / `records` | Record/recordset action is triggered on (can be empty) |
| `env` | Odoo Environment |
| `datetime`, `dateutil`, `time`, `timezone` | Python modules |
| `log(message, level)` | Logging function (writes to ir.logging) |
| `Warning` | Constructor for Warning exception |

---

## Report Actions

### `ir.actions.report` - Print Reports

Triggers the printing of a report.

#### Report Action Fields

| Field | Type | Description |
|-------|------|-------------|
| `name` | string | File name (if `print_report_name` not specified) |
| `model` | string | Model the report is about (required) |
| `report_type` | string | `qweb-pdf` or `qweb-html` (default: `qweb-pdf`) |
| `report_name` | string | External ID of the QWeb template (required) |
| `print_report_name` | string | Python expression for report file name |
| `groups_id` | Many2many | Groups allowed to view/use the report |
| `multi` | boolean | If `True`, action not displayed on form view |
| `paperformat_id` | Many2one | Paper format to use |
| `attachment_use` | boolean | Generate once, then reprint from stored report |
| `attachment` | string | Python expression for attachment name |

### Report Action Examples

```xml
<report
    id="account_invoices"
    model="account.move"
    string="Invoices"
    report_type="qweb-pdf"
    name="account.report_invoice"
    file="account_report_invoice"
    print_report_name="'Invoice-{}-{}'.format(object.number or 'n/a', object.state)"
    groups_id="account.group_account_user"
    paperformat_id="account.paperformat_euro"
    attachment_use="True"
    attachment="'Invoice-'+str(object.number)+'.pdf'"/>
```

### Binding to Print Menu

To show in Print menu, specify `binding_model_id`:

```xml
<record id="report_my_report" model="ir.actions.report">
    <field name="name">My Report</field>
    <field name="model">my.model</field>
    <field name="report_type">qweb-pdf</field>
    <field name="report_name">my_module.my_report</field>
    <field name="binding_model_id" ref="model_my_model"/>
    <!-- binding_type defaults to 'report' automatically -->
</record>
```

---

## Client Actions

### `ir.actions.client` - Client-Side Actions

Triggers an action implemented entirely in the client (JavaScript).

| Field | Type | Description |
|-------|------|-------------|
| `tag` | string | Client-side identifier (arbitrary string) |
| `params` | dict | Additional data for the client |
| `target` | string | `current`, `fullscreen`, or `new` |

### Client Action Examples

```python
{
    "type": "ir.actions.client",
    "tag": "pos.ui"
}
```

```xml
<record id="action_client" model="ir.actions.client">
    <field name="name">Open POS</field>
    <field name="tag">pos.ui</field>
</record>
```

### Common Client Action Tags

| Tag | Description |
|-----|-------------|
| `pos.ui` | Point of Sale interface |
| `web_dashboard.open` | Open dashboard |
| `account.reload_view` | Reload account view |
| `bus.bus.reload` | Reload bus communication |

---

## Scheduled Actions

### `ir.cron` - Automated Actions

Actions triggered automatically on a predefined frequency.

#### Scheduled Action Fields

| Field | Type | Description |
|-------|------|-------------|
| `name` | string | Name of the scheduled action |
| `interval_number` | int | Number of interval units between executions |
| `interval_type` | selection | `minutes`, `hours`, `days`, `weeks`, `months` |
| `model_id` | Many2one | Model on which action is called |
| `code` | Text | Code content to execute |
| `nextcall` | datetime | Next planned execution date |
| `priority` | int | Priority when executing multiple actions simultaneously |

### Scheduled Action Examples

```xml
<record id="ir_cron_send_quotation_email" model="ir.cron">
    <field name="name">Send Quotation Email</field>
    <field name="model_id" ref="model_sale_order"/>
    <field name="state">code</field>
    <field name="code">model._send_quotation_email()</field>
    <field name="interval_number">1</field>
    <field name="interval_type">hours</field>
    <field name="numbercall">-1</field>
    <field name="doall" eval="False"/>
    <field name="active" eval="True"/>
</record>
```

### Advanced: Batching

For long-running cron jobs, use batching API:

```python
self.env['ir.cron']._notify_progress(done=50, remaining=100)
```

This allows the scheduler to:
- Know if progress was made
- Determine if there's remaining work
- Process up to 10 batches in one sitting by default

### Advanced: Triggers

Trigger scheduled actions from business code:

```python
action_record._trigger(at=datetime(2025, 1, 1))
```

### Security Measures

- If a scheduled action encounters an error/timeout 3 consecutive times → skip execution, mark as failed
- If a scheduled action fails 5 consecutive times over at least 7 days → deactivate and notify DB admin

---

## Action Bindings

### Binding Attributes

Actions can be bound to contextual menus of models.

| Attribute | Type | Description |
|-----------|------|-------------|
| `binding_model_id` | Many2one | Model the action is bound to |
| `binding_type` | selection | `action` (default) or `report` |
| `binding_view_types` | string | Comma-separated: `list`, `form`, `list,form` (default) |

### Binding Examples

#### Action Binding (More Menu)

```xml
<record id="action_custom" model="ir.actions.server">
    <field name="name">Custom Action</field>
    <field name="model_id" ref="model_sale_order"/>
    <field name="state">code</field>
    <field name="code">
        # Do something
    </field>
    <field name="binding_model_id" ref="model_sale_order"/>
    <field name="binding_type">action</field>
    <field name="binding_view_types">list</field>
</record>
```

#### Report Binding (Print Menu)

```xml
<record id="report_custom" model="ir.actions.report">
    <field name="name">Custom Report</field>
    <field name="model">sale.order</field>
    <field name="report_type">qweb-pdf</field>
    <field name="report_name">sale.report_custom</field>
    <field name="binding_model_id" ref="model_sale_order"/>
    <!-- binding_type automatically 'report' for ir.actions.report -->
</record>
```

### Binding View Types

| Value | Description |
|-------|-------------|
| `list` | Shows in list view menu |
| `form` | Shows in form view menu |
| `list,form` | Shows in both (default) |

---

## Quick Reference

### Action Types Summary

| Type | Model | Use Case |
|------|-------|----------|
| Window | `ir.actions.act_window` | Open views for a model |
| URL | `ir.actions.act_url` | Open web page |
| Server | `ir.actions.server` | Execute Python code |
| Report | `ir.actions.report` | Print/generate report |
| Client | `ir.actions.client` | Execute JavaScript |
| Scheduled | `ir.cron` | Automated recurring action |

### Common Target Values

| Target | Description |
|--------|-------------|
| `current` | Open in main content area |
| `main` | Open in main area, clear breadcrumbs |
| `new` | Open in dialog/popup |
| `fullscreen` | Open in full screen mode |

### Returning Actions from Python

```python
# Window action
return {
    'type': 'ir.actions.act_window',
    'res_model': 'sale.order',
    'view_mode': 'form',
    'res_id': self.id,
}

# Refresh current view
return {
    'type': 'ir.actions.act_window_close',
}

# Reload entire client
return {
    'type': 'ir.actions.client',
    'tag': 'reload',
}
```

---

**For more Odoo 18 guides, see [SKILL.md](../SKILL.md)**

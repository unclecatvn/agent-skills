---
name: odoo-17-actions
description: Complete reference for Odoo 17 actions (ir.actions.*), menus (ir.ui.menu), and scheduled jobs (ir.cron). Covers act_window, act_url, server, report, client actions, menu structure, cron fields, and action bindings.
globs: "**/*.{py,xml}"
topics:
  - Window actions (ir.actions.act_window) with view_mode tree,form
  - URL actions (ir.actions.act_url)
  - Server actions (ir.actions.server) states code/object_write/object_create/multi/webhook
  - Report actions (ir.actions.report)
  - Client actions (ir.actions.client)
  - Scheduled actions (ir.cron) - interval_type, numbercall, doall
  - Menus (ir.ui.menu) with menuitem shortcut
  - Action bindings (binding_model_id, binding_type, binding_view_types)
when_to_use:
  - Creating window actions and menus
  - Writing server actions / automations
  - Setting up scheduled jobs
  - Exposing actions / reports in the "Action" or "Print" menu
  - Building client (JS) actions
---

# Odoo 17 Actions Guide

Reference for Odoo 17 `ir.actions.*`, `ir.ui.menu`, and `ir.cron`.

## Table of Contents

1. [Action Basics](#action-basics)
2. [Window Actions (ir.actions.act_window)](#window-actions)
3. [URL Actions (ir.actions.act_url)](#url-actions)
4. [Server Actions (ir.actions.server)](#server-actions)
5. [Report Actions (ir.actions.report)](#report-actions)
6. [Client Actions (ir.actions.client)](#client-actions)
7. [Scheduled Actions (ir.cron)](#scheduled-actions)
8. [Menus (ir.ui.menu)](#menus)
9. [Action Bindings](#action-bindings)
10. [Returning Actions From Python](#returning-actions-from-python)
11. [Quick Reference](#quick-reference)

---

## Action Basics

An action tells the client what to do in response to a user interaction: opening a view, calling server code, printing a report, opening a URL, refreshing the UI, etc.

### Common Shape

Every action record exposes:

| Field | Description |
|-------|-------------|
| `type` | Model name (`ir.actions.act_window`, `ir.actions.server`, ...) — implicit via the `model` attribute of `<record>` |
| `name` | Human-readable label |

From Python, actions can be returned as:

| Form | Meaning |
|------|---------|
| `False` | Close any open dialog |
| string (tag) | Client action tag |
| integer / XML-id | Reference to an existing `ir.actions.*` record |
| dict | Inline action descriptor, executed as-is |

---

## Window Actions

`ir.actions.act_window` drives the standard "view a model through one or more views" behaviour.

### Key Fields

| Field | Type | Notes |
|-------|------|-------|
| `name` | Char | Action label (shown in breadcrumbs if `target != 'new'`) |
| `res_model` | Char (required) | Target model |
| `view_mode` | Char | Comma-separated view types (no spaces). **v17 default: `tree,form`** |
| `view_id` | Many2one (`ir.ui.view`) | Specific view to use for the first matching `view_mode` type |
| `view_ids` | One2many (`ir.actions.act_window.view`) | Fine-grained `(sequence, view_mode, view_id)` list |
| `search_view_id` | Many2one (`ir.ui.view`) | Specific search view |
| `res_id` | Integer | Opens a specific record in form mode |
| `domain` | Char (Python list) | Default domain filter |
| `context` | Char (Python dict) | Default context (supports `search_default_*`, `default_*`) |
| `target` | Selection | `current` (default), `new` (dialog), `inline`, `fullscreen`, `main` |
| `limit` | Integer | List pagination (default 80) |
| `mobile_view_mode` | Char | First view mode on small screens (default `kanban`) |
| `help` | Html | Nocontent help shown when the list is empty |
| `binding_model_id` | Many2one (`ir.model`) | Attaches the action to the *Action* menu of another model |
| `binding_view_types` | Char | `list,form` (default); restricts which views display the binding |
| `groups_id` | Many2many (`res.groups`) | Restrict visibility |

> **v17 vs v18:** the list view tag and the value you put in `view_mode` is `tree` in v17 (it was renamed to `list` in v18). Default `view_mode` in v17 is `tree,form`.

### View Types (`VIEW_TYPES`)

Defined in `odoo/addons/base/models/ir_actions.py`:

`tree`, `form`, `graph`, `pivot`, `calendar`, `gantt`, `kanban` — plus `search` and `qweb` recognised by `ir.ui.view`.

### Basic Example

```xml
<record id="action_my_model" model="ir.actions.act_window">
    <field name="name">My Records</field>
    <field name="res_model">my.model</field>
    <field name="view_mode">tree,kanban,form</field>
    <field name="domain">[('active','=',True)]</field>
    <field name="context">{'search_default_my_records': 1, 'default_user_id': uid}</field>
    <field name="help" type="html">
        <p class="o_view_nocontent_smiling_face">Create your first record!</p>
        <p>Start by giving it a name.</p>
    </field>
</record>
```

### Binding a Specific View

```xml
<record id="action_my_model" model="ir.actions.act_window">
    <field name="name">Customers</field>
    <field name="res_model">res.partner</field>
    <field name="view_mode">tree,form</field>
    <field name="view_id" ref="view_partner_tree_custom"/>
    <field name="search_view_id" ref="view_partner_search_custom"/>
</record>
```

### Open a Single Record in a Dialog

```xml
<record id="action_open_wizard" model="ir.actions.act_window">
    <field name="name">Configure</field>
    <field name="res_model">my.config.wizard</field>
    <field name="view_mode">form</field>
    <field name="target">new</field>
</record>
```

### Per-Mode View Ordering with `ir.actions.act_window.view`

When several views of the same type exist, or you want strict ordering, prefer `ir.actions.act_window.view`:

```xml
<record id="action_sale" model="ir.actions.act_window">
    <field name="name">Sales</field>
    <field name="res_model">sale.order</field>
    <field name="view_mode">tree,kanban,form</field>
</record>

<record id="action_sale_tree" model="ir.actions.act_window.view">
    <field name="sequence">1</field>
    <field name="view_mode">tree</field>
    <field name="view_id" ref="view_sale_tree_custom"/>
    <field name="act_window_id" ref="action_sale"/>
</record>

<record id="action_sale_form" model="ir.actions.act_window.view">
    <field name="sequence">2</field>
    <field name="view_mode">form</field>
    <field name="view_id" ref="view_sale_form_custom"/>
    <field name="act_window_id" ref="action_sale"/>
</record>
```

### Target Values

| Value | Effect |
|-------|--------|
| `current` (default) | Replace the main content area; breadcrumb added |
| `new` | Open in a modal dialog |
| `inline` | Edit the form inline without a modal (rare) |
| `fullscreen` | Full-screen takeover |
| `main` | Replace the main content and reset breadcrumbs |

---

## URL Actions

`ir.actions.act_url` opens a URL — either in the same tab, a new tab, or triggers a download.

| Field | Values |
|-------|--------|
| `url` | Any absolute/relative URL |
| `target` | `new` (default), `self`, `download` |

```xml
<record id="action_open_docs" model="ir.actions.act_url">
    <field name="name">Documentation</field>
    <field name="url">https://www.odoo.com/documentation/17.0/</field>
    <field name="target">new</field>
</record>
```

Returned from Python:

```python
return {
    'type': 'ir.actions.act_url',
    'url': '/web/binary/download?attachment_id=%s' % attachment.id,
    'target': 'self',
}
```

---

## Server Actions

`ir.actions.server` runs server-side logic. The `state` field selects the flavour:

| `state` | Purpose |
|---------|---------|
| `code` | Execute a Python snippet |
| `object_create` | Create a record of `crud_model_id` from the current context |
| `object_write` | Update the current record (or records) |
| `multi` | Run a list of other server actions sequentially (`child_ids`) |
| `webhook` | Send an HTTP POST to an external URL |

(See `odoo/addons/base/models/ir_actions.py::ServerActions`.)

### `code` — Run Python

```xml
<record id="action_server_notify" model="ir.actions.server">
    <field name="name">Notify Owner</field>
    <field name="model_id" ref="model_my_model"/>
    <field name="state">code</field>
    <field name="code">
if records:
    for record in records:
        record.message_post(body="Processed via server action")
action = {
    'type': 'ir.actions.client',
    'tag': 'display_notification',
    'params': {
        'title': 'Done',
        'message': '%d record(s) processed' % len(records),
        'type': 'success',
    },
}
    </field>
</record>
```

#### `code` Evaluation Context

| Name | Description |
|------|-------------|
| `env` | Current environment |
| `model` | `env[model_id.model]` |
| `record` | Current record, if any (may be empty) |
| `records` | Recordset the action is run on |
| `action` | Assign here to return a follow-up action |
| `log(msg, level='info')` | Writes into `ir.logging` |
| `Warning` | `UserError` constructor (aliased for legacy compat) |
| `datetime`, `dateutil`, `time`, `timezone`, `UserError`, `float_compare` | Python helpers |

### `object_write` — Update Record

```xml
<record id="action_mark_done" model="ir.actions.server">
    <field name="name">Mark Done</field>
    <field name="model_id" ref="model_my_model"/>
    <field name="state">object_write</field>
    <field name="update_path">state</field>
    <field name="value">done</field>
</record>
```

### `object_create` — Create a Record

```xml
<record id="action_spawn_task" model="ir.actions.server">
    <field name="name">Create Task</field>
    <field name="model_id" ref="model_res_partner"/>
    <field name="state">object_create</field>
    <field name="crud_model_id" ref="project.model_project_task"/>
    <field name="link_field_id" ref="project.field_project_task__partner_id"/>
</record>
```

### `multi` — Chain Actions

```xml
<record id="action_multi" model="ir.actions.server">
    <field name="name">Process &amp; Notify</field>
    <field name="model_id" ref="model_my_model"/>
    <field name="state">multi</field>
    <field name="child_ids" eval="[(6, 0, [
        ref('action_mark_done'),
        ref('action_server_notify'),
    ])]"/>
</record>
```

### `webhook` — Outgoing HTTP Call

```xml
<record id="action_webhook" model="ir.actions.server">
    <field name="name">Notify external CRM</field>
    <field name="model_id" ref="model_my_model"/>
    <field name="state">webhook</field>
    <field name="webhook_url">https://hooks.example.com/odoo</field>
    <field name="webhook_field_ids" eval="[(6, 0, [
        ref('field_my_model__name'),
        ref('field_my_model__state'),
    ])]"/>
</record>
```

### Common Server-Action Fields

| Field | Purpose |
|-------|---------|
| `model_id` | Model the action is declared on |
| `crud_model_id` | (object_create) target model to create |
| `link_field_id` | (object_create) auto-link the new record to `record` via this field |
| `child_ids` | (multi) ordered list of sub-actions |
| `update_path` | (object_write) dot-path of the field to update |
| `value` | (object_write) new value (string; coerced per field) |
| `code` | (code) Python source |
| `webhook_url` / `webhook_field_ids` | (webhook) endpoint + exported fields |

---

## Report Actions

`ir.actions.report` prints a QWeb template.

### Key Fields

| Field | Notes |
|-------|-------|
| `name` | Default file name if `print_report_name` is empty |
| `model` | Required — the model the report is about |
| `report_type` | `qweb-pdf`, `qweb-html`, `qweb-text` (default `qweb-pdf`) |
| `report_name` | External id of the QWeb template (required) |
| `report_file` | Base name for generated files (without extension) |
| `print_report_name` | Python expression using `object` (one record) for the file name |
| `paperformat_id` | Defaults to the company's paperformat |
| `attachment_use` | If True, reuse saved attachment instead of regenerating |
| `attachment` | Python expression producing the attachment filename |
| `binding_model_id` | Bind to the model's *Print* menu |
| `binding_type` | `'report'` (default for `ir.actions.report`) |
| `groups_id` | Restrict by group |

### XML Record

```xml
<record id="action_report_my_model" model="ir.actions.report">
    <field name="name">My Model Report</field>
    <field name="model">my.model</field>
    <field name="report_type">qweb-pdf</field>
    <field name="report_name">my_module.report_my_model_template</field>
    <field name="report_file">my_module.report_my_model</field>
    <field name="print_report_name">'Report - %s' % (object.name or '')</field>
    <field name="binding_model_id" ref="model_my_model"/>
    <field name="paperformat_id" ref="base.paperformat_euro"/>
</record>
```

### `<report>` Shortcut

Equivalent to the record above but shorter:

```xml
<report
    id="action_report_my_model"
    string="My Model Report"
    model="my.model"
    report_type="qweb-pdf"
    name="my_module.report_my_model_template"
    file="my_module.report_my_model"
    print_report_name="'Report - %s' % (object.name or '')"
    attachment_use="False"/>
```

The shortcut automatically sets `binding_model_id` to the given `model` and `binding_type='report'`, so the action appears under the model's *Print* menu.

---

## Client Actions

`ir.actions.client` triggers a JS-side action registered via `registry.category('actions')`.

| Field | Description |
|-------|-------------|
| `tag` | Registered client action identifier |
| `params` | Arbitrary dict passed to the JS handler |
| `target` | `current`, `new`, `fullscreen`, `main` |

```xml
<record id="action_open_dashboard" model="ir.actions.client">
    <field name="name">Dashboard</field>
    <field name="tag">my_module.dashboard</field>
    <field name="params" eval="{'filter': 'my_open'}"/>
</record>
```

Commonly used built-in tags:

| Tag | Effect |
|-----|--------|
| `reload` | Reload the entire web client |
| `reload_context` | Refresh the current action with latest context |
| `soft_reload` | Soft reload without losing breadcrumbs |
| `display_notification` | Show a toast (pass `params`: `title`, `message`, `type`, `sticky`) |
| `home` | Go back to the home menu |
| `pos.ui` | Launch the Point of Sale UI |

Example from Python:

```python
return {
    'type': 'ir.actions.client',
    'tag': 'display_notification',
    'params': {
        'title': 'Success',
        'message': 'Data imported',
        'type': 'success',      # 'info', 'warning', 'danger', 'success'
        'sticky': False,
        'next': {'type': 'ir.actions.act_window_close'},
    },
}
```

---

## Scheduled Actions

`ir.cron` schedules the execution of an `ir.actions.server` on an interval. Internally `ir.cron` *delegates* to a related `ir.actions.server` (`ir_actions_server_id`), so every scheduled job is also a server action.

### Fields

| Field | Description |
|-------|-------------|
| `name` (via `ir_actions_server_id`) | Job name |
| `user_id` | User whose permissions drive execution (default: current user) |
| `active` | `True` to enable |
| `interval_number` | Integer, combined with `interval_type` |
| `interval_type` | `minutes`, `hours`, `days`, `weeks`, `months` |
| `numbercall` | Remaining number of executions; `-1` = unlimited (v17 still uses this) |
| `doall` | If `True`, catch up on missed occurrences after downtime |
| `nextcall` | Next planned execution datetime |
| `priority` | Integer, lower runs first when several jobs are due (default 5) |
| `model_id` | Model the underlying server action runs on |
| `code` | Python snippet (same context as a `code` server action) |
| `state` | Mirror of the server action `state` — typically `code` for crons |

### Declaration

```xml
<record id="ir_cron_my_job" model="ir.cron">
    <field name="name">My Module: Daily Sync</field>
    <field name="model_id" ref="model_my_model"/>
    <field name="state">code</field>
    <field name="code">model._cron_daily_sync()</field>
    <field name="user_id" ref="base.user_root"/>
    <field name="interval_number">1</field>
    <field name="interval_type">days</field>
    <field name="numbercall">-1</field>
    <field name="doall" eval="False"/>
    <field name="active" eval="True"/>
    <field name="priority">10</field>
</record>
```

Wrap in `<data noupdate="1">` if users are allowed to tweak the schedule:

```xml
<odoo>
    <data noupdate="1">
        <record id="ir_cron_my_job" model="ir.cron">
            ...
        </record>
    </data>
</odoo>
```

### `interval_type` Values

Defined in `odoo/addons/base/models/ir_cron.py`:

`minutes`, `hours`, `days`, `weeks`, `months`.

(`weeks` and `months` are computed with `dateutil.relativedelta`, so a "1 month" cron fired on Jan 31 will land on Feb 28/29.)

### Writing Cron Code

```python
class MyModel(models.Model):
    _name = 'my.model'

    @api.model
    def _cron_daily_sync(self):
        # Process records in batches to keep the worker responsive
        limit = 500
        to_do = self.search([('sync_required', '=', True)], limit=limit)
        to_do.action_sync()
        # Let the scheduler continue if work remains
        if self.search_count([('sync_required', '=', True)]) > limit:
            self.env['ir.cron']._trigger()   # re-run ASAP
```

Good practices:

- Always use `@api.model` and operate on explicit recordsets (never `self`).
- Batch work and signal remaining effort (`self.env['ir.cron']._trigger()` can re-arm a job immediately).
- Catch exceptions locally if one bad record should not poison the rest; otherwise let the scheduler mark the job failed.
- Cron users are `OdooBot` (`base.user_root`) by default; make sure the code can read the data.

### Triggering a Cron From Code

```python
cron = self.env.ref('my_module.ir_cron_my_job')
cron._trigger()                                  # runs as soon as possible
cron._trigger(at=datetime(2026, 1, 1, 3, 0))     # schedule a one-off extra run
```

### Failure Handling (v17)

- A scheduled action that raises is retried the next tick.
- Persistent failures are visible in the job log; administrators can deactivate the cron from the UI.
- Setting `numbercall` to a positive integer runs the job N times and then auto-deactivates; `-1` runs indefinitely.

---

## Menus

Menus live in `ir.ui.menu`. The usual way to create them is the `<menuitem>` shortcut (see the data-files guide for details).

### Minimal Tree

```xml
<!-- Top-level app menu -->
<menuitem id="menu_my_module_root"
          name="My Module"
          sequence="50"
          web_icon="my_module,static/description/icon.png"/>

<!-- First-level -->
<menuitem id="menu_my_records"
          name="Records"
          parent="menu_my_module_root"
          action="action_my_model"
          sequence="10"/>

<!-- Second-level -->
<menuitem id="menu_reporting"
          name="Reporting"
          parent="menu_my_module_root"
          sequence="90"/>
<menuitem id="menu_report_analysis"
          name="Analysis"
          parent="menu_reporting"
          action="action_report_analysis"
          sequence="10"/>
```

### Attributes Recap

| Attribute | Purpose |
|-----------|---------|
| `id` | External ID |
| `name` | Visible label |
| `parent` | Parent menu external ID |
| `action` | External ID of any action (`act_window`, `server`, `client`, `url`, ...) |
| `sequence` | Integer, lower first (default 10) |
| `groups` | Comma-separated group ids; prefix `-` to hide from a group |
| `web_icon` | `module,path/to/icon.png` — only meaningful on top-level app menus |
| `active` | `True`/`False` |

The `<menuitem>` shortcut automatically copies the action's `name` onto the menu if you don't set one (see `convert.py::_tag_menuitem`).

### Security

Menus are filtered using the `groups_id` of both the menu and the referenced action. To hide a menu from a specific group, use `-group.xml_id`:

```xml
<menuitem id="menu_admin_tools"
          name="Admin Tools"
          parent="menu_my_module_root"
          action="action_admin_tools"
          groups="base.group_system,-base.group_portal"/>
```

### `web_icon` Asset

For top-level application menus, `web_icon` points to a PNG inside the module. The standard location is `static/description/icon.png`. Sub-menus do not need a `web_icon`.

---

## Action Bindings

Any `ir.actions.*` can be "bound" to a model, making it appear in the *Action* or *Print* menu of that model's list/form views.

| Field | Description |
|-------|-------------|
| `binding_model_id` | `ir.model` ref — where the action is displayed |
| `binding_type` | `action` (default) or `report` |
| `binding_view_types` | Where in the UI: `list` / `form` / `list,form` (default) |

### Server Action Binding (Action Menu)

```xml
<record id="action_bulk_archive" model="ir.actions.server">
    <field name="name">Archive Selected</field>
    <field name="model_id" ref="model_my_model"/>
    <field name="state">code</field>
    <field name="code">records.action_archive()</field>
    <field name="binding_model_id" ref="model_my_model"/>
    <field name="binding_type">action</field>
    <field name="binding_view_types">list</field>
</record>
```

### Report Binding (Print Menu)

```xml
<record id="action_report_invoice_custom" model="ir.actions.report">
    <field name="name">Custom Invoice</field>
    <field name="model">account.move</field>
    <field name="report_type">qweb-pdf</field>
    <field name="report_name">my_module.report_invoice_custom</field>
    <field name="binding_model_id" ref="account.model_account_move"/>
    <!-- binding_type = 'report' is set automatically for ir.actions.report -->
</record>
```

### `binding_view_types` Values

| Value | Where shown |
|-------|-------------|
| `list` | Only in the list view (after selecting records) |
| `form` | Only in the form view (for the current record) |
| `list,form` | Default — both views |

---

## Returning Actions From Python

### Open a Form View

```python
def action_open_partner(self):
    self.ensure_one()
    return {
        'type': 'ir.actions.act_window',
        'name': 'Partner',
        'res_model': 'res.partner',
        'view_mode': 'form',
        'res_id': self.partner_id.id,
        'target': 'current',
    }
```

### Open a Filtered List

```python
def action_view_orders(self):
    self.ensure_one()
    return {
        'type': 'ir.actions.act_window',
        'name': 'Orders',
        'res_model': 'sale.order',
        'view_mode': 'tree,form',
        'domain': [('partner_id', '=', self.id)],
        'context': {'default_partner_id': self.id, 'search_default_my_orders': 1},
    }
```

### Open via External ID

```python
def action_wizard(self):
    action = self.env['ir.actions.actions']._for_xml_id('my_module.action_configure')
    action['context'] = {'default_partner_id': self.id}
    return action
```

### Close a Dialog

```python
return {'type': 'ir.actions.act_window_close'}
```

### Reload / Notify

```python
return {'type': 'ir.actions.client', 'tag': 'reload'}

return {
    'type': 'ir.actions.client',
    'tag': 'display_notification',
    'params': {'title': 'Saved', 'type': 'success', 'next': {'type': 'ir.actions.act_window_close'}},
}
```

---

## Quick Reference

### Action Types

| Type | Model | Use |
|------|-------|-----|
| Window | `ir.actions.act_window` | Open views for a model |
| URL | `ir.actions.act_url` | Open / download a URL |
| Server | `ir.actions.server` | Run server Python / create / update / multi / webhook |
| Report | `ir.actions.report` | QWeb PDF / HTML / Text |
| Client | `ir.actions.client` | Registered JS action |
| Cron | `ir.cron` | Schedule a server action |

### Targets

| Value | Effect |
|-------|--------|
| `current` | Replace main content |
| `new` | Open in dialog |
| `inline` | Edit inline (form only) |
| `fullscreen` | Hide the chrome |
| `main` | Replace main content, reset breadcrumbs |

### Minimum XML for Each Type

```xml
<!-- Window -->
<record id="a1" model="ir.actions.act_window">
    <field name="name">Customers</field>
    <field name="res_model">res.partner</field>
    <field name="view_mode">tree,form</field>
</record>

<!-- URL -->
<record id="a2" model="ir.actions.act_url">
    <field name="name">Docs</field>
    <field name="url">https://odoo.com</field>
    <field name="target">new</field>
</record>

<!-- Server -->
<record id="a3" model="ir.actions.server">
    <field name="name">Archive</field>
    <field name="model_id" ref="model_my_model"/>
    <field name="state">code</field>
    <field name="code">records.action_archive()</field>
</record>

<!-- Report -->
<report id="a4" model="my.model" string="My Report"
        report_type="qweb-pdf" name="my_module.tpl"/>

<!-- Client -->
<record id="a5" model="ir.actions.client">
    <field name="name">Dashboard</field>
    <field name="tag">my_module.dashboard</field>
</record>

<!-- Cron -->
<record id="a6" model="ir.cron">
    <field name="name">Daily Sync</field>
    <field name="model_id" ref="model_my_model"/>
    <field name="state">code</field>
    <field name="code">model._cron_daily_sync()</field>
    <field name="interval_number">1</field>
    <field name="interval_type">days</field>
    <field name="numbercall">-1</field>
</record>
```

### Menu With Action

```xml
<menuitem id="menu_root" name="My Module" sequence="50"/>
<menuitem id="menu_records"
          parent="menu_root"
          action="a1"
          sequence="10"/>
```

---

## Coding Conventions

- Name a model's main action `<model>_action`; suffix additional actions with
  a short lowercase purpose, and action-view records `<model>_action_view_<type>`.
- Name menus `<model>_menu` or `<model>_menu_<purpose>` and define actions
  before menus that reference them.
- Prefix object action methods with `action_`; call `self.ensure_one()` when
  the action contract is exactly one record.

## Base Code Reference

- `odoo/addons/base/models/ir_actions.py` — `IrActions`, `act_window`, `act_url`, `server`, `client`, `act_window_view`, `VIEW_TYPES`, default `view_mode='tree,form'` (v17).
- `odoo/addons/base/models/ir_actions_report.py` — `ir.actions.report`, `report_type` selection (`qweb-pdf`, `qweb-html`, `qweb-text`), paperformat handling.
- `odoo/addons/base/models/ir_cron.py` — `ir.cron`, `interval_type`, `numbercall`, `doall`, `nextcall`, `priority`, `_trigger()`, batching, the underlying `ir_actions_server_id` link.
- `odoo/addons/base/models/ir_ui_menu.py` — `ir.ui.menu` model and access filtering.
- `odoo/tools/convert.py` — data-loader shortcuts (`<menuitem>`, `<report>`, `<template>`, `<asset>`).

# Odoo 19 Actions Guide

Guide for working with Odoo 19 actions (`ir.actions.*`), scheduled jobs (cron), and action bindings.

## Table of Contents
- [Action Types](#action-types)
- [Window Actions](#window-actions)
- [Server Actions](#server-actions)
- [Report Actions](#report-actions)
- [Client Actions](#client-actions)
- [URL Actions](#url-actions)
- [Scheduled Actions (Cron)](#scheduled-actions-cron)
- [Action Bindings](#action-bindings)

---

## Action Types

Actions define the behavior of the system in response to user actions: login, action button, selection of records, etc.

Actions can be stored in the database or returned directly as dictionaries. All actions share two mandatory attributes:

| Attribute | Type | Description |
|-----------|------|-------------|
| `type` | string | The category of the current action |
| `name` | string | Short user-readable description |

A client can get actions in 4 forms:
- `False` - closes any open action dialog
- A string - client action tag or number
- A number - database identifier or external ID
- A dictionary - client action descriptor

---

## Window Actions

`ir.actions.act_window` - The most common action type, used to present visualizations of a model through views.

### Key Attributes

| Attribute | Type | Description |
|-----------|------|-------------|
| `res_model` | string | Model to present views for |
| `views` | list | List of `(view_id, view_type)` pairs |
| `res_id` | int | If default view is `form`, specifies the record to load |
| `search_view_id` | tuple | `(id, name)` pair for specific search view |
| `target` | string | `current`, `fullscreen`, `new`, or `main` |
| `context` | dict | Additional context data |
| `domain` | list | Filtering domain |
| `limit` | int | Number of records to display (default: 80) |

### Example: Opening customers

```python
{
    "type": "ir.actions.act_window",
    "res_model": "res.partner",
    "views": [[False, "list"], [False, "form"]],
    "domain": [["customer", "=", True]],
}
```

### Example: Opening specific product in dialog

```python
{
    "type": "ir.actions.act_window",
    "res_model": "product.product",
    "views": [[False, "form"]],
    "res_id": a_product_id,
    "target": "new",
}
```

### In-Database Fields

When defining actions from XML data files:

| Attribute | Description |
|-----------|-------------|
| `view_mode` | Comma-separated list of view types (e.g., `list,form`) |
| `view_ids` | Many2many to view objects |
| `view_id` | Specific view to add to views list |

### Using ir.actions.act_window.view

```xml
<record model="ir.actions.act_window.view" id="test_action_tree">
   <field name="sequence" eval="1"/>
   <field name="view_mode">list</field>
   <field name="view_id" ref="view_test_tree"/>
   <field name="act_window_id" ref="test_action"/>
</record>
```

---

## Server Actions

`ir.actions.server` - Allow triggering complex server code from any valid action location.

### Key Attributes

| Attribute | Type | Description |
|-----------|------|-------------|
| `id` | int | In-database identifier |
| `model_id` | ref | Odoo model linked to the action |
| `state` | string | Type of action: `code`, `object_create`, `object_write`, `multi` |
| `code` | string | Python code to execute |

### State: code

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

### Returning next action

```xml
<record model="ir.actions.server" id="open_form">
    <field name="name">Open Form Action</field>
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

### State: object_create

| Attribute | Description |
|-----------|-------------|
| `crud_model_id` | Model in which to create a new record |
| `link_field_id` | Many2one field on which to set newly created record |
| `fields_lines` | Fields to override when creating |

### State: object_write

Updates the current record(s) following `fields_lines` specifications.

### State: multi

Executes several actions given through `child_ids`.

### Evaluation Context

Available variables in server actions:
- `model` - Model object linked to the action
- `record`/`records` - Record/recordset on which the action is triggered
- `env` - Odoo Environment
- `datetime`, `dateutil`, `time`, `timezone` - Python modules
- `log(message, level='info')` - Logging function
- `Warning` - Constructor for Warning exception

---

## Report Actions

`ir.actions.report` - Triggers the printing of a report.

### Key Attributes

| Attribute | Type | Description |
|-----------|------|-------------|
| `name` | string | Used as file name if `print_report_name` not specified |
| `model` | string | Model your report will be about |
| `report_type` | string | `qweb-pdf` or `qweb-html` |
| `report_name` | string | External ID of the qweb template |
| `print_report_name` | string | Python expression for report name |
| `groups_id` | Many2many | Groups allowed to view/use the report |
| `multi` | boolean | If True, not displayed on form view |
| `paperformat_id` | Many2one | Paper format to use |
| `attachment_use` | boolean | Generate once, then reprint from stored report |
| `attachment` | string | Python expression for attachment name |

### Print Menu Integration

If you define your report through a `<record>` and want it in the Print menu:

```xml
<record id="my_report" model="ir.actions.report">
    <field name="name">My Report</field>
    <field name="model">my.model</field>
    <field name="report_type">qweb-pdf</field>
    <field name="report_name">my_module.my_template</field>
    <field name="binding_model_id" ref="model_my_model"/>
</record>
```

---

## Client Actions

`ir.actions.client` - Triggers an action implemented entirely in the client.

### Key Attributes

| Attribute | Type | Description |
|-----------|------|-------------|
| `tag` | string | Client-side identifier of the action |
| `params` | dict | Additional data to send to the client |
| `target` | string | `current`, `fullscreen`, or `new` |

```python
{
    "type": "ir.actions.client",
    "tag": "pos.ui"
}
```

Tells the client to start the Point of Sale interface.

---

## URL Actions

`ir.actions.act_url` - Allow opening a URL (website/web page).

### Key Attributes

| Attribute | Type | Description |
|-----------|------|-------------|
| `url` | string | The address to open |
| `target` | string | `new`, `self`, or `download` |

```python
{
    "type": "ir.actions.act_url",
    "url": "https://odoo.com",
    "target": "self",
}
```

---

## Scheduled Actions (Cron)

`ir.cron` - Actions triggered automatically on a predefined frequency.

### Key Attributes

| Attribute | Type | Description |
|-----------|------|-------------|
| `name` | string | Name of the scheduled action |
| `interval_number` | int | Number of interval_type units between executions |
| `interval_type` | string | `minutes`, `hours`, `days`, `weeks`, `months` |
| `model_id` | ref | Model on which this action will be called |
| `code` | string | Code content of the action |
| `nextcall` | datetime | Next planned execution date |
| `priority` | int | Priority when executing multiple actions |

### Writing cron functions

When writing cron functions, batch the progress to avoid blocking workers:

```python
def _cron_do_something(self, *, limit=300):
    domain = [('state', '=', 'ready')]
    records = self.search(domain, limit=limit)
    records.do_something()
    # notify progression
    remaining = 0 if len(records) == limit else self.search_count(domain)
    self.env['ir.cron']._commit_progress(len(records), remaining=remaining)
```

### Managing resources between batches

```python
def _cron_do_something(self):
    assert self.env.context.get('cron_id'), "Run only inside cron jobs"
    domain = [('state', '=', 'ready')]
    records = self.search(domain)
    self.env['ir.cron']._commit_progress(remaining=len(records))

    with open_some_connection() as conn:
        for record in records:
            record = record.try_lock_for_update().filtered_domain(domain)
            if not record:
                continue
            try:
                record.do_something(conn)
                if not self.env['ir.cron']._commit_progress(1):
                    break
            except Exception:
                self.env.cr.rollback()
```

### Running cron functions

Do not call cron functions directly. Use:
- `IrCron.method_direct_trigger()` - for testing
- `IrCron._trigger()` - for scheduled execution

### Security Measures

- If a scheduled action encounters an error or timeout **3 consecutive times**, it skips current execution
- If it fails **5 consecutive times** over **7 days**, it is deactivated and notifies the DB admin
- A hard-limit exists for cron execution at the database level

---

## Action Bindings

Actions can be bound to models to appear in contextual menus.

### Binding Attributes

| Attribute | Type | Description |
|-----------|------|-------------|
| `binding_model_id` | Many2one | Model the action is bound to (use `model_id` for Server Actions) |
| `binding_type` | string | `action` (default) or `report` |
| `binding_view_types` | string | Comma-separated list: `list`, `form`, or `list,form` (default) |

### Binding Type: action

Action appears in the **Action** contextual menu.

### Binding Type: report

Action appears in the **Print** contextual menu.

---

## References

- Source: Odoo 19 documentation `/doc/developer/reference/backend/actions.rst`

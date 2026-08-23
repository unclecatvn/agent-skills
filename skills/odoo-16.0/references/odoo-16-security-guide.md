---
name: odoo-16-security
description: Complete reference for Odoo 16 security covering access rights (ACL via ir.model.access.csv), record rules (ir.rule), user groups (res.groups with category_id), field-level permissions, multi-company, the _check_company_auto flag, sudo() / with_user(), check_access_rights / check_access_rule and common security pitfalls.
globs: "**/*.{py,xml,csv}"
topics:
  - Access rights (ir.model.access.csv)
  - Record rules (ir.rule)
  - Field-level access (groups attribute)
  - User groups (res.groups, category_id)
  - Multi-company and _check_company_auto
  - sudo() / with_user() / bypass patterns
  - check_access_rights / check_access_rule
  - Security pitfalls (SQL injection, XSS, eval)
when_to_use:
  - Configuring security for new models
  - Setting up access rights CSV
  - Creating record rules
  - Preventing security vulnerabilities
  - Understanding multi-company security
  - Implementing field-level permissions
---

# Odoo 16 Security Guide

Complete reference for Odoo 16 security: access rights, record rules, field access, groups, multi-company and common pitfalls.

## Table of Contents

1. [Security Overview](#security-overview)
2. [User Groups](#user-groups)
3. [Access Rights (ACL)](#access-rights-acl)
4. [Record Rules](#record-rules)
5. [Field-Level Access](#field-level-access)
6. [Multi-Company](#multi-company)
7. [sudo / with_user / bypass patterns](#sudo--with_user--bypass-patterns)
8. [Access Checks in Code](#access-checks-in-code)
9. [Security Pitfalls](#security-pitfalls)

---

## Security Overview

### Two-Layer Security

| Layer | Mechanism | Purpose |
|-------|-----------|---------|
| 1 | Access Rights (ACL) | Grants CRUD access on an **entire model** |
| 2 | Record Rules | Restricts **which records** of the model a user can access |

Both are linked to users through **groups** (`res.groups`). A user belongs to multiple groups and permissions are the union of them.

### Access Control Flow

```
User operation (read/write/create/unlink)
        |
        v
Is at least one of user's groups allowed by ir.model.access?
   |-- no --> AccessError
   |
   v
Apply ir.rule for (model, operation, user's groups):
   - Global rules (no `groups`)         -> AND together  (all must match)
   - Group rules (have `groups`)        -> OR together   (one match is enough)
   - Final domain = (AND of globals) AND (OR of group rules)
        |
        v
Does record match the final domain?
   |-- no --> AccessError
   |
   v
Access granted
```

### Bypass Rules

- Superuser (`self.env.su`, OdooBot / `__system__`) bypasses record rules.
- `sudo()` returns a recordset whose `env.su` is True.
- `with_user(user)` switches the user but **does not** bypass anything.
- ACLs are **not** bypassed by `sudo` alone - only by the superuser context (`sudo()` elevates to superuser).

---

## User Groups

### res.groups

Groups are the foundation of Odoo security. In Odoo 16, `res.groups` has `category_id` pointing at `ir.module.category` - there is no `privilege_id` (that was introduced in later versions).

### Defining a Group

```xml
<!-- security/security_groups.xml -->
<odoo>
    <!-- Module category (optional, used for grouping in Settings > Users) -->
    <record id="module_category_trip_management" model="ir.module.category">
        <field name="name">Trip Management</field>
        <field name="description">Manage business trips</field>
        <field name="sequence">20</field>
    </record>

    <record id="group_trip_user" model="res.groups">
        <field name="name">User</field>
        <field name="category_id" ref="module_category_trip_management"/>
        <field name="implied_ids" eval="[(4, ref('base.group_user'))]"/>
    </record>

    <record id="group_trip_manager" model="res.groups">
        <field name="name">Manager</field>
        <field name="category_id" ref="module_category_trip_management"/>
        <field name="implied_ids" eval="[(4, ref('my_module.group_trip_user'))]"/>
    </record>
</odoo>
```

### res.groups Fields

| Field | Description |
|-------|-------------|
| `name` | Display name |
| `category_id` | Many2one on `ir.module.category` - groups appear in that app's section in user settings |
| `implied_ids` | Other groups implied by this one (users get both) |
| `users` | Many2many on `res.users` |
| `model_access` | One2many on `ir.model.access` |
| `rule_groups` | Many2many on `ir.rule` |
| `menu_access` | Menus accessible to the group |
| `view_access` | Views accessible to the group |
| `comment` | Description |
| `share` | True if this group is only for sharing (portal-like) |

### Group Inheritance via `implied_ids`

If `group_manager` has `implied_ids` pointing to `group_user`, every user in `group_manager` is automatically added to `group_user` too. Use this to build hierarchies:

```
group_manager  >>  group_user  >>  base.group_user  (internal user)
```

### Checking Groups in Code

```python
# Is current user in a group?
if self.env.user.has_group('my_module.group_trip_manager'):
    ...

# Safer when called as another user - re-check with sudo if needed
if self.env.user.sudo().has_group('base.group_system'):
    ...

# has_group respects implied_ids: a manager is also a user automatically
```

---

## Access Rights (ACL)

### ir.model.access - Model-Level Access

Access rights grant CRUD operations on an entire model. They are normally declared via a CSV file.

```
my_module/
  security/
    ir.model.access.csv
```

### CSV Columns (Odoo 16)

```csv
id,name,model_id:id,group_id:id,perm_read,perm_write,perm_create,perm_unlink
```

Note: Odoo 16 uses exactly these 8 columns. Do not include `active` or any other column unless you know it is supported.

### Example `ir.model.access.csv`

```csv
id,name,model_id:id,group_id:id,perm_read,perm_write,perm_create,perm_unlink
access_business_trip_user,business.trip.user,model_business_trip,my_module.group_trip_user,1,1,1,0
access_business_trip_manager,business.trip.manager,model_business_trip,my_module.group_trip_manager,1,1,1,1
access_business_trip_portal,business.trip.portal,model_business_trip,base.group_portal,1,0,0,0
access_business_expense_all,business.expense.all,model_business_expense,,1,0,0,0
```

### Fields Explained

| Column | Description |
|--------|-------------|
| `id` | Unique external ID for this ACL row |
| `name` | Human-readable label |
| `model_id:id` | External ID of the `ir.model` row - convention is `model_<model_name_with_underscores>` |
| `group_id:id` | External ID of the `res.groups` row; **empty means all users** (including portal/public) |
| `perm_read` | `1` or `0` - allow read |
| `perm_write` | `1` or `0` - allow write |
| `perm_create` | `1` or `0` - allow create |
| `perm_unlink` | `1` or `0` - allow unlink (delete) |

### ACL Rules of Thumb

- ACLs are **additive**: a user gets the union of CRUD flags from every matching group.
- An **empty `group_id`** grants access to **everyone** (internal, portal, public). Use sparingly.
- A model with **no ACL row** is inaccessible to everyone except the superuser.
- Every non-abstract model needs at least one ACL row, otherwise module installation fails with a warning and RPC access is denied.

### Model ID Naming Convention

For a model with `_name = 'business.trip'`, the `ir.model` external ID is `model_business_trip` in the module that declares the model. When referencing a model declared in another module, prefix: `other_module.model_business_trip`.

---

## Record Rules

### ir.rule - Record-Level Security

Record rules filter which records of a model a given user can access.

```xml
<record id="trip_personal_rule" model="ir.rule">
    <field name="name">Business Trip: own records</field>
    <field name="model_id" ref="model_business_trip"/>
    <field name="domain_force">[('user_id', '=', user.id)]</field>
    <field name="groups" eval="[(4, ref('my_module.group_trip_user'))]"/>
    <field name="perm_read" eval="True"/>
    <field name="perm_write" eval="True"/>
    <field name="perm_create" eval="True"/>
    <field name="perm_unlink" eval="False"/>
</record>
```

### ir.rule Fields (Odoo 16)

| Field | Description |
|-------|-------------|
| `name` | Description of the rule |
| `active` | Disable without deleting |
| `model_id` | Many2one on `ir.model` |
| `groups` | Many2many on `res.groups`; empty = global rule |
| `domain_force` | **String containing a Python list literal** for the domain (not XML) |
| `perm_read`, `perm_write`, `perm_create`, `perm_unlink` | When this rule applies |

`domain_force` must be a plain string that evaluates to a domain list - e.g. `"[('user_id', '=', user.id)]"`. It is parsed with `safe_eval`.

### Variables Available in `domain_force`

| Variable | Description |
|----------|-------------|
| `user` | Current user record (singleton, accessed via `sudo()` context) |
| `user.id` | Current user ID |
| `user.partner_id` | Partner linked to user |
| `user.company_id` | User's current main company |
| `user.company_ids` | IDs of companies the user can access (legacy alias) |
| `company_id` | Current allowed company (`self.env.company.id`) |
| `company_ids` | List of IDs of allowed companies (`self.env.companies.ids`) |
| `time` | Python `time` module |

### Global vs Group Rules

| Type | How they combine |
|------|------------------|
| **Global** (`groups` empty) | **AND** together - all global rules must match |
| **Group** (has groups) | **OR** together (within matching groups) - any rule of a matching group is enough |
| Combined | `(AND of globals) AND (OR of group rules that apply)` |

Use global rules for company separation; use group rules to broaden access for managers vs. employees.

### Classic Patterns

#### Own records only (employees)

```xml
<record id="trip_user_rule" model="ir.rule">
    <field name="name">Trip: own records</field>
    <field name="model_id" ref="model_business_trip"/>
    <field name="domain_force">[('user_id', '=', user.id)]</field>
    <field name="groups" eval="[(4, ref('my_module.group_trip_user'))]"/>
</record>
```

#### All records (managers)

```xml
<record id="trip_manager_rule" model="ir.rule">
    <field name="name">Trip: all records (manager)</field>
    <field name="model_id" ref="model_business_trip"/>
    <field name="domain_force">[(1, '=', 1)]</field>
    <field name="groups" eval="[(4, ref('my_module.group_trip_manager'))]"/>
</record>
```

#### Portal users (own partner's records)

```xml
<record id="trip_portal_rule" model="ir.rule">
    <field name="name">Trip: portal own</field>
    <field name="model_id" ref="model_business_trip"/>
    <field name="domain_force">[('partner_id', '=', user.partner_id.id)]</field>
    <field name="groups" eval="[(4, ref('base.group_portal'))]"/>
    <field name="perm_read" eval="True"/>
    <field name="perm_write" eval="False"/>
    <field name="perm_create" eval="False"/>
    <field name="perm_unlink" eval="False"/>
</record>
```

#### Time-sensitive access

```xml
<record id="archive_rule" model="ir.rule">
    <field name="name">Only this year's records</field>
    <field name="model_id" ref="model_business_trip"/>
    <field name="domain_force">[('create_date', '&gt;=', time.strftime('%Y-01-01'))]</field>
    <field name="groups" eval="[(4, ref('my_module.group_trip_user'))]"/>
</record>
```

---

## Field-Level Access

### Restricting Fields to Groups

The `groups=` attribute on a field limits who can read/write it. The field is hidden from `fields_get`, removed from views and raises `AccessError` on direct read/write for users who lack the group.

```python
class BusinessTrip(models.Model):
    _name = 'business.trip'

    name = fields.Char()                                       # all users
    internal_notes = fields.Text(groups='base.group_user')     # internal users only
    secret_code = fields.Char(groups='my_module.group_trip_manager')
    salary = fields.Float(groups='base.group_system')          # admin only

    # Multiple groups: comma-separated = OR
    estimate = fields.Monetary(groups='base.group_user,base.group_portal')
```

### Field-Level Group Behaviour

1. Field is automatically removed from `fields_get()` for users without any of the groups.
2. Field is removed from **views** at load time (no placeholder rendered).
3. Explicit `record.read(['secret_code'])` or `record.secret_code = x` raises `AccessError`.
4. `record.with_context(prefetch_fields=False)` does NOT bypass the check.
5. A computed stored field can still be computed for the database, but its value is hidden from the user.

### Related Fields with Groups

```python
partner_email = fields.Char(related='partner_id.email', groups='base.group_user')
```

The field-level group on the related alias does not remove the check on the source field - but it does hide the field from users outside the group.

---

## Multi-Company

### `_check_company_auto` Flag

Set on a model to automatically validate that all Many2one fields pointing to company-scoped records have a compatible `company_id`.

```python
class SaleOrder(models.Model):
    _name = 'sale.order'
    _check_company_auto = True

    company_id = fields.Many2one('res.company', default=lambda s: s.env.company, required=True)
    partner_id = fields.Many2one('res.partner', check_company=True)
    pricelist_id = fields.Many2one('product.pricelist', check_company=True)
```

On every `create()` / `write()`, Odoo calls `_check_company()` which validates all fields declared with `check_company=True` against the record's `company_id`. If the linked record belongs to another company (and isn't company-less), a `UserError` is raised.

### Multi-Company Record Rule

Always add a **global** rule for company filtering on any model with `company_id`:

```xml
<record id="business_trip_company_rule" model="ir.rule">
    <field name="name">Business Trip: multi-company</field>
    <field name="model_id" ref="model_business_trip"/>
    <field name="domain_force">
        ['|', ('company_id', '=', False), ('company_id', 'in', company_ids)]
    </field>
</record>
```

Use `company_ids` (the user's **currently allowed** companies, honouring the company switcher) rather than `user.company_ids` (all companies the user can switch to) to respect the company switcher.

### Recommended Field Definitions

```python
company_id = fields.Many2one(
    'res.company', required=True, index=True,
    default=lambda self: self.env.company,
)

# Always use check_company=True on Many2one to company-scoped records
user_id = fields.Many2one('res.users', check_company=True)
product_id = fields.Many2one('product.product', check_company=True)
```

---

## sudo / with_user / bypass patterns

### `sudo()` - Elevate to Superuser

`sudo()` returns a new recordset whose environment runs as superuser. Record rules and field-level groups are bypassed; ACLs still work because the superuser has access to everything.

```python
# Read a field the current user can't see (e.g. internal audit log)
internal_ref = record.sudo().internal_reference

# Create a record the user isn't allowed to create directly
self.env['mail.mail'].sudo().create({...})
```

Use sparingly - `sudo()` is a **bypass of permissions** and is a common source of vulnerabilities.

### `with_user(user)` - Switch User Without Superuser

Run code as a different user, **all permissions still enforced**.

```python
# Act on behalf of a specific user; AccessError will still fire if that user
# lacks rights.
res = self.with_user(self.env.ref('base.user_demo')).search([])
```

### `with_company(company)` - Switch Company Context

```python
records = self.with_company(other_company).search([])
```

### Typical `sudo()` Patterns

```python
# GOOD: sudo to read one safe related field, then keep processing as the real user
partner_country = record.partner_id.sudo().country_id
if partner_country.code == 'US':
    record.action_apply_us_logic()          # still runs with ACL/rules

# GOOD: manual gatekeeping before sudo - guarantees the caller is allowed
def action_validate(self):
    if not self.env.user.has_group('my_module.group_trip_manager'):
        raise AccessError(_("Only Trip Managers can validate."))
    self.sudo().write({'state': 'validated'})

# BAD: blanket sudo() lets any user mutate any record
def action_unsafe(self):
    self.sudo().write({'active': False})   # No caller check - dangerous
```

### Checking Whether We Run as Superuser

```python
if self.env.su:
    # We are running as superuser (record rules bypass)
    ...
```

---

## Access Checks in Code

### `check_access_rights(operation, raise_exception=True)`

Checks the ACL only - model-level permission.

```python
# Silent check
can_read = self.env['business.trip'].check_access_rights('read', raise_exception=False)

# Raising check
self.env['business.trip'].check_access_rights('write')  # AccessError if denied
```

Valid operations: `'read'`, `'write'`, `'create'`, `'unlink'`.

### `check_access_rule(operation)`

Checks the record rules only on a specific recordset. Does nothing when running as superuser.

```python
# Will raise AccessError if any record in self is filtered out
self.check_access_rule('write')
```

### Combined Check

Typical "can this user do X on this record?" check:

```python
try:
    self.check_access_rights('write')
    self.check_access_rule('write')
except AccessError:
    raise UserError(_("You cannot modify this record."))
```

### Filtering by Rules (Non-Raising)

```python
# Returns the subset of self for which the operation is allowed
allowed = self._filter_access_rules('read')
```

---

## Security Pitfalls

### 1. Public Methods Are Callable via RPC

Any method that does **not** start with an underscore can be invoked by any authenticated user via JSON-RPC / XML-RPC - including internal users with minimal permissions. Always gate-keep:

```python
# BAD: any user can call this
def action_force_done(self, new_state):
    self.write({'state': new_state})

# GOOD: private worker + controlled public entry point
def action_force_done(self):
    if not self.env.user.has_group('my_module.group_trip_manager'):
        raise AccessError(_("Not allowed."))
    self._set_state('done')

def _set_state(self, state):
    self.sudo().write({'state': state})
```

Note: In Odoo 16, keep internal-only helpers underscore-prefixed because the RPC layer does not expose underscore methods through JSON-RPC/XML-RPC. If you need a public button or service entry point, keep the permission checks on the public method and move the internal work into an underscore helper instead of relying on a decorator that does not exist in Odoo 16.

### 2. Bypassing the ORM with Raw SQL

Raw SQL bypasses ACLs, record rules, field-level access, translations and computed fields.

```python
# BAD
self.env.cr.execute("SELECT id FROM business_trip WHERE user_id = %s", (user_id,))
rows = self.env.cr.fetchall()

# GOOD
trips = self.env['business.trip'].search([('user_id', '=', user_id)])
```

When SQL is truly necessary, always use parameter substitution (`%s` placeholders) and post-filter the results through `browse().exists()` to re-apply access rules.

### 3. SQL Injection

```python
# VERY BAD: concatenation/formatting opens SQL injection
self.env.cr.execute("SELECT id FROM my_table WHERE name = '" + user_input + "'")

# GOOD: parameterised query
self.env.cr.execute("SELECT id FROM my_table WHERE name = %s", (user_input,))
```

### 4. XSS via `t-raw`

```xml
<!-- BAD: renders user content as HTML -->
<div t-raw="message"/>

<!-- GOOD -->
<div t-esc="message"/>

<!-- GOOD: explicit Markup for trusted structure -->
<div t-out="rendered_body"/>     <!-- t-out auto-escapes but respects Markup -->
```

In Python:

```python
from markupsafe import Markup, escape

# BAD: f-strings insert before escaping
body = Markup(f"<p>{user_input}</p>")

# GOOD: % formatting escapes the content
body = Markup("<p>%s</p>") % user_input

# GOOD: explicit escape
body = Markup("<p>%s</p>") % escape(user_input)
```

### 5. Dangerous `eval`

```python
from ast import literal_eval
from odoo.tools import safe_eval

# VERY BAD
domain = eval(self.filter_domain)

# BAD (can still execute many functions with default globals)
domain = safe_eval(self.filter_domain)

# GOOD for simple literal expressions
domain = literal_eval(self.filter_domain)
```

### 6. `getattr` on Arbitrary Field Names

```python
# BAD: can access private methods / attributes
value = getattr(record, user_supplied_field)

# GOOD: goes through the ORM, respects field-level groups
value = record[user_supplied_field]   # AccessError if field is restricted
```

### 7. Skipping `check_company`

Forgetting `check_company=True` on Many2one fields in multi-company models allows cross-company references, leaking data across companies.

```python
# BAD
partner_id = fields.Many2one('res.partner')

# GOOD
partner_id = fields.Many2one('res.partner', check_company=True)
```

And set `_check_company_auto = True` on the model to enforce checks on every write/create.

### 8. Overusing `sudo()`

```python
# BAD: wide open
def action_archive(self):
    for rec in self:
        rec.sudo().write({'active': False})

# GOOD: only elevate where required
def action_archive(self):
    self.check_access_rights('write')
    self.check_access_rule('write')
    self.sudo().write({'active': False})  # only elevate to update denormalised data
```

### 9. Validation Must Survive Race Conditions

Use database constraints (`_sql_constraints`) or `@api.constrains` to enforce invariants, not just a pre-check in a method.

```python
_sql_constraints = [
    ('amount_positive', 'CHECK (amount >= 0)', 'Amount must be positive'),
]
```

### 10. Field Whitelisting on Public Endpoints

HTTP controllers receiving user values must restrict which fields they forward to `write()`:

```python
ALLOWED_FIELDS = {'name', 'note', 'partner_id'}

def _apply_form(self, record, values):
    cleaned = {k: v for k, v in values.items() if k in ALLOWED_FIELDS}
    record.sudo().write(cleaned)
```

---

## Quick Reference

### Security Checklist

| Item | Done |
|------|------|
| Every non-abstract model has at least one `ir.model.access.csv` row | |
| Groups declared with `category_id` on a module category | |
| Record rules for own/all access per group | |
| Global rule for `company_id` in multi-company models | |
| `check_company=True` on Many2one + `_check_company_auto = True` | |
| Sensitive fields restricted with `groups=` | |
| Public methods gated with `has_group()` / `check_access_rights()` | |
| No raw SQL with string concatenation | |
| No `t-raw` with user-provided content | |
| `sudo()` used sparingly, never to skip a permission the caller should have | |

### Minimal Security Scaffold

`security/security_groups.xml`:

```xml
<odoo>
    <record id="module_category_my_module" model="ir.module.category">
        <field name="name">My Module</field>
        <field name="sequence">20</field>
    </record>

    <record id="group_my_user" model="res.groups">
        <field name="name">User</field>
        <field name="category_id" ref="module_category_my_module"/>
        <field name="implied_ids" eval="[(4, ref('base.group_user'))]"/>
    </record>

    <record id="group_my_manager" model="res.groups">
        <field name="name">Manager</field>
        <field name="category_id" ref="module_category_my_module"/>
        <field name="implied_ids" eval="[(4, ref('my_module.group_my_user'))]"/>
    </record>

    <record id="my_model_user_rule" model="ir.rule">
        <field name="name">My Model: own</field>
        <field name="model_id" ref="model_my_model"/>
        <field name="domain_force">[('user_id', '=', user.id)]</field>
        <field name="groups" eval="[(4, ref('my_module.group_my_user'))]"/>
    </record>

    <record id="my_model_manager_rule" model="ir.rule">
        <field name="name">My Model: all</field>
        <field name="model_id" ref="model_my_model"/>
        <field name="domain_force">[(1, '=', 1)]</field>
        <field name="groups" eval="[(4, ref('my_module.group_my_manager'))]"/>
    </record>

    <record id="my_model_company_rule" model="ir.rule">
        <field name="name">My Model: multi-company</field>
        <field name="model_id" ref="model_my_model"/>
        <field name="domain_force">['|', ('company_id', '=', False), ('company_id', 'in', company_ids)]</field>
    </record>
</odoo>
```

`security/ir.model.access.csv`:

```csv
id,name,model_id:id,group_id:id,perm_read,perm_write,perm_create,perm_unlink
access_my_model_user,my.model.user,model_my_model,my_module.group_my_user,1,1,1,0
access_my_model_manager,my.model.manager,model_my_model,my_module.group_my_manager,1,1,1,1
```

Register both in the manifest (order matters - security XML must be loaded before the CSV uses its groups):

```python
# __manifest__.py
{
    'author': 'UncleCat',
    'data': [
        'security/security_groups.xml',
        'security/ir.model.access.csv',
        ...
    ],
}
```

---

## Coding Conventions

- Keep ACLs in `ir.model.access.csv`, groups in `<module>_groups.xml`, and
  rules in `<model>_security.xml` where separate files improve discovery.
- Name groups `<module>_group_<role>` and rules
  `<model>_rule_<concerned_group>`; use the same dotted name in record names.
- Load groups before ACLs or rules that reference them, and keep security
  declarations ahead of views in the manifest.

## Base Code Reference

The guide is based on the Odoo 16 source tree. Reference files:

| File | Contents |
|------|----------|
| `odoo/addons/base/models/ir_model.py` | `ir.model.access` implementation and CSV loader |
| `odoo/addons/base/models/ir_rule.py` | `ir.rule` evaluation, `_eval_context`, global/group combination |
| `odoo/addons/base/models/res_users.py` | `res.groups` (with `category_id`, `implied_ids`), `has_group`, `with_user` |
| `odoo/models.py` | `check_access_rights`, `check_access_rule`, `_check_company`, `_check_company_auto` |
| `odoo/api.py` | `Environment.su`, `sudo()`, `with_user()`, `with_company()` |

**For more Odoo 16 guides, see [SKILL.md](../SKILL.md)**

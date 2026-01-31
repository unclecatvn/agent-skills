# Odoo 19 Security Guide

Guide for Odoo 19 security: access rights, record rules, field permissions, and security pitfalls.

## Table of Contents
- [Security Overview](#security-overview)
- [Groups](#groups)
- [Access Rights (ACL)](#access-rights-acl)
- [Record Rules](#record-rules)
- [Field Access](#field-access)
- [Security Pitfalls](#security-pitfalls)

---

## Security Overview

Odoo provides two main data-driven mechanisms to manage access:

1. **Access Rights (ACL)** - Grants access to an entire model for operations
2. **Record Rules** - Conditions that must be satisfied for operations

Both are linked to users through **groups**.

---

## Groups

`res.groups` - Users belong to groups, security mechanisms are associated to groups.

### Key Attributes

| Attribute | Description |
|-----------|-------------|
| `name` | User-readable identification (role/purpose) |
| `category_id` | Module category, associates groups with an Odoo App |
| `implied_ids` | Other groups to set on the user alongside this one |
| `comment` | Additional notes |

### Example

```python
<record id="group_my_module_user" model="res.groups">
    <field name="name">My Module User</field>
    <field name="category_id" ref="base.module_category_my_module"/>
    <field name="implied_ids" eval="[(4, ref('base.group_user'))]"/>
    <field name="comment">Users can access my module features.</field>
</record>
```

---

## Access Rights (ACL)

Access rights **grant** access to an entire model for operations. If no access rights matches an operation, the user doesn't have access.

Access rights are **additive** - a user's accesses are the union of all groups.

`ir.model.access` - Access control list entries.

### Key Attributes

| Attribute | Description |
|-----------|-------------|
| `name` | Purpose or role of the group |
| `model_id` | Model whose access the ACL controls |
| `group_id` | Group granted access (empty = every user) |
| `perm_create` | Grant create access |
| `perm_read` | Grant read access |
| `perm_write` | Grant write access |
| `perm_unlink` | Grant unlink (delete) access |

### Example CSV (Common Format)

File: `security/ir.model.access.csv`

```csv
id,name,model_id:id,group_id:id,perm_read,perm_write,perm_create,perm_unlink
access_my_model_user,my.model.user,model_my_model,group_my_module_user,1,1,0,0
access_my_model_manager,my.model.manager,model_my_model,group_my_module_manager,1,1,1,1
```

### Example XML

```xml
<record id="access_my_model_user" model="ir.model.access">
    <field name="name">my.model.user</field>
    <field name="model_id" ref="model_my_model"/>
    <field name="group_id" ref="group_my_module_user"/>
    <field name="perm_read" eval="1"/>
    <field name="perm_write" eval="1"/>
    <field name="perm_create" eval="0"/>
    <field name="perm_unlink" eval="0"/>
</record>
```

---

## Record Rules

Record rules are **conditions** which must be satisfied for operations. They are evaluated record-by-record, following access rights.

Record rules are **default-allow**: if access rights grant access and no rule applies, access is granted.

`ir.rule` - Record rules.

### Key Attributes

| Attribute | Description |
|-----------|-------------|
| `name` | Description of the rule |
| `model_id` | Model to which the rule applies |
| `groups` | Groups to which access is granted (empty = global) |
| `domain_force` | Domain predicate (Python expression) |
| `perm_read`, `perm_write`, `perm_create`, `perm_unlink` | Operations the rule applies to (all by default) |

### Domain Force Variables

| Variable | Description |
|----------|-------------|
| `time` | Python's `time` module |
| `user` | Current user (singleton recordset) |
| `company_id` | Current user's selected company (single id) |
| `company_ids` | All companies the user has access (list of ids) |

### Example: Multi-Company Rule

```xml
<record id="my_model_company_rule" model="ir.rule">
    <field name="name">My Module: multi-company</field>
    <field name="model_id" ref="model_my_model"/>
    <field name="domain_force">['|', ('company_id', '=', False), ('company_id', 'in', company_ids)]</field>
</record>
```

### Example: User-Only Records

```xml
<record id="my_model_user_rule" model="ir.rule">
    <field name="name">My Module: user records</field>
    <field name="model_id" ref="model_my_model"/>
    <field name="domain_force">[('user_id', '=', user.id)]</field>
    <field name="groups" eval="[(4, ref('group_my_module_user'))]"/>
</record>
```

### Global vs Group Rules

There's a large difference between global and group rules:

| Rule Type | Behavior |
|-----------|----------|
| **Global** (no groups) | **Intersect** - all global rules must be satisfied |
| **Group** rules | **Unify** - any group rule can be satisfied |
| **Global + Group** | **Intersect** - first group rule restricts access |

> **Danger**: Creating multiple global rules is risky - possible to create non-overlapping rulesets which will remove all access.

---

## Field Access

An ORM field can have a `groups` attribute providing a list of groups (comma-separated external identifiers).

If the current user is not in one of the listed groups:
- Restricted fields are removed from views
- Restricted fields are removed from `fields_get()` responses
- Attempts to read/write restricted fields result in an access error

```python
notes = fields.Text('Internal Notes', groups='base.group_system')

# Only users in base.group_system can see/edit this field
```

---

## Security Pitfalls

### Unsafe Public Methods

Any public method can be executed via RPC call. Methods starting with `_` are not callable from action buttons or external API.

```python
# BAD: this method is public and arguments can not be trusted
def action_done(self):
    if self.state == "draft" and self.env.user.has_group('base.manager'):
        self._set_state("done")

# GOOD: this method is private and can only be called from other methods
def _set_state(self, new_state):
    self.sudo().write({"state": new_state})
```

### Bypassing the ORM

**Never** use the database cursor directly when the ORM can do the same thing!

#### Wrong (very bad)

```python
# SQL injection vulnerability
self.env.cr.execute('SELECT id FROM auction_lots WHERE auction_id in (' +
                    ','.join(map(str, ids)) + ') AND state=%s AND obj_price > 0',
                    ('draft',))
```

#### Better (no injection, but still wrong)

```python
self.env.cr.execute('SELECT id FROM auction_lots WHERE auction_id in %s '
                    'AND state=%s AND obj_price > 0',
                    (tuple(ids), 'draft',))
```

#### Best (use ORM)

```python
auction_lots_ids = self.search([
    ('auction_id', 'in', ids),
    ('state', '=', 'draft'),
    ('obj_price', '>', 0)
]).ids
```

#### Using SQL class (recommended)

```python
from odoo.tools import SQL

auction_lots_ids = self.env.execute_query(SQL("""
    SELECT id FROM auction_lots
    WHERE auction_id IN %s AND state = %s AND obj_price > 0
""", tuple(ids), 'draft'))
```

### SQL Injections

**Never** use Python string concatenation (+) or interpolation (%) for SQL queries.

Use psycopg2 parameter passing or `odoo.tools.SQL` wrapper.

```python
# BAD: SQL injection vulnerability
self.env.cr.execute('SELECT distinct child_id FROM account_account_consol_rel '
                    'WHERE parent_id IN ('+','.join(map(str, ids))+')')

# GOOD: use parameter passing
self.env.cr.execute('SELECT DISTINCT child_id '
                    'FROM account_account_consol_rel '
                    'WHERE parent_id IN %s',
                    (tuple(ids),))

# BETTER: use SQL wrapper
from odoo.tools import SQL
self.env.cr.execute(SQL("""
    SELECT DISTINCT child_id
    FROM account_account_consol_rel
    WHERE parent_id IN %s
""", tuple(ids)))
```

### Building Domains

Use `odoo.fields.Domain` to handle domain manipulation safely.

```python
# BAD: the user can pass ['|', ('id', '>', 0)] to access all
domain = ...  # passed by user
security_domain = [('user_id', '=', self.env.uid)]
domain += security_domain  # can have side effects
self.search(domain)

# GOOD: use Domain class
from odoo.fields import Domain
domain = Domain(...)
domain &= Domain('user_id', '=', self.env.uid)
self.search(domain)
```

### Unescaped Field Content

Avoid using `t-raw` for rich-text content - it's an XSS vector.

#### Bad XML

```xml
<div t-name="insecure_template">
    <div id="information-bar"><t t-raw="info_message" /></div>
</div>
```

#### Good XML

```xml
<div t-name="secure_template">
    <div class="info"><t t-esc="message" /></div>
    <div class="subject"><t t-esc="subject" /></div>
</div>
```

### Escaping vs Sanitizing

**Escaping** (always mandatory) converts TEXT to CODE.

```python
from markupsafe import Markup

# data is TEXT
code = html_escape(data)  # Convert to CODE
self.website_description = Markup("<strong>%s</strong>") % code
```

**Sanitizing** converts CODE to SAFER CODE (but not necessarily safe).

```python
from odoo.tools import html_sanitize

code = Markup("<p class='text-warning'>Important</p>")
html_sanitize(code, strip_classes=True)  # => Markup('<p>Important</p>')
```

### Evaluating Content

Avoid `eval()` - use `ast.literal_eval()` for parsing.

```python
# BAD: very bad
domain = eval(self.filter_domain)

# BETTER: still not recommended
from odoo.tools import safe_eval
domain = safe_eval(self.filter_domain)

# GOOD: use literal_eval
from ast import literal_eval
domain = literal_eval(self.filter_domain)
```

### Accessing Object Attributes

Use `__getitem__` instead of `getattr()` for dynamic field access.

```python
# BAD: unsafe, can access any attribute
def _get_state_value(self, res_id, state_field):
    record = self.sudo().browse(res_id)
    return getattr(record, state_field, False)

# GOOD: safer
def _get_state_value(self, res_id, state_field):
    record = self.sudo().browse(res_id)
    return record[state_field]
```

---

## References

- Source: Odoo 19 documentation `/doc/developer/reference/backend/security.rst`

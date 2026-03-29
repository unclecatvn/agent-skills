---
name: odoo-18-security
description: Complete reference for Odoo 18 security covering access rights (ACL), record rules, field-level access, security pitfalls, SQL injection prevention, XSS prevention, and safe coding practices.
globs: "**/*.{py,xml,csv}"
topics:
  - Access rights (ir.model.access.csv)
  - Record rules (ir.rule)
  - Field-level access (groups attribute)
  - Security pitfalls (SQL injection, XSS, eval)
  - User groups and categories
  - ACL vs Record Rules interaction
  - Public/Portal user security
when_to_use:
  - Configuring security for new models
  - Setting up access rights CSV
  - Creating record rules
  - Preventing security vulnerabilities
  - Understanding multi-company security
  - Implementing field-level permissions
---

# Odoo 18 Security Guide

Complete reference for Odoo 18 security: access rights, record rules, field access, and preventing security pitfalls.

## Table of Contents

1. [Security Overview](#security-overview)
2. [User Groups](#user-groups)
3. [Access Rights (ACL)](#access-rights-acl)
4. [Record Rules](#record-rules)
5. [Field-Level Access](#field-level-access)
6. [Security Pitfalls](#security-pitfalls)

---

## Security Overview

### Two-Layer Security

Odoo provides two main data-driven security mechanisms:

| Layer | Mechanism | Purpose |
|-------|-----------|---------|
| 1 | Access Rights (ACL) | Grants access to an entire model for operations |
| 2 | Record Rules | Restricts which specific records can be accessed |

Both are linked to users through **groups**. A user belongs to multiple groups, and security mechanisms apply to all groups cumulatively.

### Access Control Flow

```
User Request
    ↓
Is user in a group with ACL access?  ───→ No ───→ Access Denied
    ↓ Yes
Do any record rules apply?            ───→ No rules ───→ Access Granted
    ↓
Do all global rules match?           ───→ No ───→ Access Denied
    ↓ Yes
Do any group rule match?             ───→ Yes ───→ Access Granted
    ↓ No
Access Denied
```

---

## User Groups

### res.groups - User Groups

Groups are the foundation of Odoo security.

```python
# Creating a group via XML
<record id="group_trip_manager" model="res.groups">
    <field name="name">Trip Manager</field>
    <field name="category_id" ref="base.module_category_trip_management"/>
    <field name="implied_ids" eval="[(4, ref('base.group_user'))]"/>
    <field name="comment">Can manage business trips</field>
</record>
```

### Group Fields

| Field | Description |
|-------|-------------|
| `name` | User-readable name of the group |
| `category_id` | Module category (for grouping in UI) |
| `implied_ids` | Other groups automatically applied |
| `comment` | Additional notes |

### Group Inheritance

```xml
<!-- Manager group includes Employee group -->
<record id="group_manager" model="res.groups">
    <field name="name">Manager</field>
    <field name="implied_ids" eval="[(4, ref('base.group_user'))]"/>
</record>
```

Users in `group_manager` automatically get `base.group_user` too.

### Checking Groups in Code

```python
# Check if user has group
if self.env.user.has_group('my_module.group_manager'):
    # Do manager-only things
    pass

# Check with sudo
if self.sudo().env.user.has_group('base.group_system'):
    # System-only things
    pass
```

---

## Access Rights (ACL)

### ir.model.access - Model-Level Access

Access rights grant CRUD operations on entire models.

### Access Rights CSV File

```
security/
└── ir.model.access.csv
```

```csv
id,name,model_id:id,group_id:id,perm_read,perm_write,perm_create,perm_unlink
access_trip_user,trip.user,model_business_trip,base.group_user,1,0,0,0
access_trip_manager,trip.manager,model_business_trip,group_trip_manager,1,1,1,1
access_trip_all,trip.all,model_business_trip,,1,0,0,0
```

### CSV Fields

| Field | Description |
|-------|-------------|
| `id` | Unique external ID for this access record |
| `name` | Human-readable name |
| `model_id:id` | Model this ACL controls (must match `_name`) |
| `group_id:id` | Group granted access (empty = all users) |
| `perm_read` | Can read records |
| `perm_write` | Can update records |
| `perm_create` | Can create records |
| `perm_unlink` | Can delete records |

### Access Rules

- **Additive**: User's access = union of all their groups' access
- **Empty group_id**: Access granted to **everyone** (including public/portal)
- **At least one**: User needs at least one group with access to perform operation

### Example ACLs

```csv
# Employees can read trips
id,name,model_id:id,group_id:id,perm_read,perm_write,perm_create,perm_unlink
access_trip_read,trip.read,model_business_trip,base.group_user,1,0,0,0

# Managers can do everything
access_trip_full,trip.full,model_business_trip,module.group_trip_manager,1,1,1,1

# Portal users can read their own trips (via record rules)
access_trip_portal,trip.portal,model_business_trip,base.group_portal,1,0,0,0

# Public (non-logged in) cannot access
# (No entry = no access)
```

### Creating ACLs via Python (Not Recommended)

```python
# Possible but use CSV instead
self.env['ir.model.access'].create({
    'name': 'trip.user',
    'model_id': self.env.ref('model_business_trip').id,
    'group_id': self.env.ref('base.group_user').id,
    'perm_read': True,
    'perm_write': False,
    'perm_create': False,
    'perm_unlink': False,
})
```

---

## Record Rules

### ir.rule - Record-Level Security

Record rules restrict which specific records a user can access based on domain filters.

### Record Rule Structure

```xml
<record id="trip_personal_rule" model="ir.rule">
    <field name="name">Personal Trips</field>
    <field name="model_id" ref="model_business_trip"/>
    <field name="domain_force">[('user_id', '=', user.id)]</field>
    <field name="groups" eval="[(4, ref('base.group_user'))]"/>
    <field name="perm_read" eval="True"/>
    <field name="perm_write" eval="True"/>
    <field name="perm_create" eval="True"/>
    <field name="perm_unlink" eval="True"/>
</record>
```

### Record Rule Fields

| Field | Description |
|-------|-------------|
| `name` | Description of the rule |
| `model_id` | Model this rule applies to |
| `groups` | Groups this rule applies to (empty = global rule) |
| `domain_force` | Domain expression to filter records |
| `perm_read` | Rule applies to read operations |
| `perm_write` | Rule applies to write operations |
| `perm_create` | Rule applies to create operations |
| `perm_unlink` | Rule applies to delete operations |

### Domain Force Variables

Available variables in `domain_force`:

| Variable | Type | Description |
|----------|------|-------------|
| `user` | Recordset | Current user (singleton) |
| `user.id` | Int | Current user ID |
| `user.company_id` | Int | Current user's main company ID |
| `user.company_ids` | List[Int] | All company IDs user has access to |
| `time` | Module | Python `time` module |
| `datetime` | Module | Python `datetime` module |

### Rule Evaluation Context

```python
# Example: Users can only see their own records
domain_force = [('user_id', '=', user.id)]

# Example: Multi-company
domain_force = [('company_id', 'in', user.company_ids)]

# Example: Time-based
domain_force = [('create_date', '>=', time.strftime('%Y-%m-%d'))]

# Example: Complex with user's company
domain_force = [
    '|',
    ('company_id', '=', False),
    ('company_id', 'in', user.company_ids)
]
```

### Global vs Group Rules

**Critical Difference:**

| Rule Type | Behavior |
|-----------|----------|
| **Global** (no groups) | All global rules **intersect** - ALL must match |
| **Group** (has groups) | Group rules **unify** - ANY can match |
| Combined | Global + Group = **intersect** |

```xml
<!-- Global Rule 1: Must be active -->
<record id="rule_active" model="ir.rule">
    <field name="name">Active Records</field>
    <field name="model_id" ref="model_business_trip"/>
    <field name="domain_force">[('active', '=', True)]</field>
    <field name="global" eval="True"/>
</record>

<!-- Global Rule 2: Must belong to user's company -->
<record id="rule_company" model="ir.rule">
    <field name="name">User Company</field>
    <field name="model_id" ref="model_business_trip"/>
    <field name="domain_force">[('company_id', 'in', user.company_ids)]</field>
    <field name="global" eval="True"/>
</record>

<!-- Result: Records must be BOTH active AND in user's company -->
```

```xml
<!-- Group Rule: Employees see own records -->
<record id="rule_employee_own" model="ir.rule">
    <field name="name">Employee Own Records</field>
    <field name="model_id" ref="model_business_trip"/>
    <field name="domain_force">[('user_id', '=', user.id)]</field>
    <field name="groups" eval="[(4, ref('base.group_user'))]"/>
</record>

<!-- Group Rule: Managers see all records -->
<record id="rule_manager_all" model="ir.rule">
    <field name="name">Manager All Records</field>
    <field name="model_id" ref="model_business_trip"/>
    <field name="domain_force">[(1, '=', 1)]</field>
    <field name="groups" eval="[(4, ref('module.group_manager'))]"/>
</record>

<!-- Result: Employees see own, Managers see all (because rules unify) -->
```

### Danger: Multiple Global Rules

**Warning**: Creating multiple global rules is risky as it can create non-overlapping rulesets:

```xml
<!-- DANGEROUS: Two restrictive global rules -->
<record id="rule_a" model="ir.rule">
    <field name="domain_force">[('state', '=', 'draft')]</field>
    <field name="global" eval="True"/>
</record>

<record id="rule_b" model="ir.rule">
    <field name="domain_force">[('state', '=', 'done')]</field>
    <field name="global" eval="True"/>
</record>

<!-- Result: NO records match both conditions! All access removed. -->
```

### Record Rule Examples

#### Own Records Only

```xml
<record id="personal_trip_rule" model="ir.rule">
    <field name="name">Personal Trips</field>
    <field name="model_id" ref="model_business_trip"/>
    <field name="domain_force">[('user_id', '=', user.id)]</field>
    <field name="groups" eval="[(4, ref('base.group_user'))]"/>
</record>
```

#### Multi-Company Security

```xml
<record id="company_rule" model="ir.rule">
    <field name="name">Multi-company Trips</field>
    <field name="model_id" ref="model_business_trip"/>
    <field name="domain_force">
        ['|',
        ('company_id', '=', False),
        ('company_id', 'in', user.company_ids)]
    </field>
    <field name="global" eval="True"/>
</record>
```

#### Read-Own, Write-Manager

```xml
<!-- Employees read own -->
<record id="trip_read_own" model="ir.rule">
    <field name="name">Trip: Read Own</field>
    <field name="model_id" ref="model_business_trip"/>
    <field name="domain_force">[('user_id', '=', user.id)]</field>
    <field name="groups" eval="[(4, ref('base.group_user'))]"/>
    <field name="perm_read" eval="True"/>
    <field name="perm_write" eval="False"/>
    <field name="perm_create" eval="True"/>
    <field name="perm_unlink" eval="False"/>
</record>

<!-- Managers read all -->
<record id="trip_read_all" model="ir.rule">
    <field name="name">Trip: Read All (Manager)</field>
    <field name="model_id" ref="model_business_trip"/>
    <field name="domain_force">[(1, '=', 1)]</field>
    <field name="groups" eval="[(4, ref('module.group_manager'))]"/>
    <field name="perm_read" eval="True"/>
</record>
```

#### Portal User Rules

```xml
<!-- Portal users see their own data -->
<record id="trip_portal_rule" model="ir.rule">
    <field name="name">Trips: Portal Own</field>
    <field name="model_id" ref="model_business_trip"/>
    <field name="domain_force">[('partner_id', '=', user.partner_id.id)]</field>
    <field name="groups" eval="[(4, ref('base.group_portal'))]"/>
    <field name="perm_read" eval="True"/>
</record>
```

### Testing Record Rules

```python
def test_record_rules(self):
    # Test as regular user
    trips = self.env['business.trip'].sudo(self.user_employee).search([])
    assert trips, "Employee should see their trips"

    # Test as manager
    all_trips = self.env['business.trip'].sudo(self.user_manager).search([])
    assert len(all_trips) >= len(trips), "Manager should see all trips"
```

---

## Field-Level Access

### Field Groups Attribute

Restrict access to specific fields using the `groups` parameter:

```python
class BusinessTrip(models.Model):
    _name = 'business.trip'

    name = fields.Char()  # Everyone
    internal_notes = fields.Text(groups='base.group_user')  # Employees only
    secret_code = fields.Char(groups='module.group_manager')  # Managers only
    salary = fields.Float(groups='base.group_system')  # Admin only
```

### Field Access Effects

When a user lacks access to a field:
1. Field automatically removed from views
2. Field removed from `fields_get()` response
3. Explicit read/write raises `AccessError`

### Checking Field Access

```python
# Check if user can access field
if self.env.user.has_group('base.group_user'):
    # Can access internal_notes
    records.read(['internal_notes'])
else:
    # Cannot access - will be filtered out
    records.read(['name'])  # Only name
```

### Related Fields with Groups

```python
# Restrict access to partner's email
partner_email = fields.Char(
    related='partner_id.email',
    groups='base.group_user'
)
```

---

## Security Pitfalls

### 1. Unsafe Public Methods

**Problem**: Any public method can be called via RPC with arbitrary parameters.

```python
# BAD: Public method with untrusted parameters
def action_done(self):
    if self.state == "draft":
        self._set_state("done")  # No ACL check!

# GOOD: Use private method with ACL-protected wrapper
def action_done(self):
    if not self.env.user.has_group('base.group_manager'):
        raise AccessError("Only managers can do this")
    self._set_state("done")

def _set_state(self, new_state):
    self.sudo().write({"state": new_state})
```

### 2. Bypassing ORM

**Problem**: Using `cr.execute()` bypasses security.

```python
# VERY BAD: Direct SQL - bypasses ACL, record rules, translations
self.env.cr.execute(
    'SELECT id FROM auction_lots WHERE auction_id IN (' +
    ','.join(map(str, ids)) + ')'
)

# BAD: Still bypasses ORM
self.env.cr.execute(
    'SELECT id FROM auction_lots WHERE auction_id IN %s',
    (tuple(ids),)
)

# GOOD: Use ORM
lots = self.search([('auction_id', 'in', ids)])
```

### 3. SQL Injection

**Problem**: String concatenation in SQL queries.

```python
# VERY BAD: SQL injection vulnerability
query = "SELECT id FROM table WHERE name = '" + user_input + "'"
self.env.cr.execute(query)

# BAD: Still using concatenation
query = "SELECT id FROM table WHERE name = '%s'" % user_input
self.env.cr.execute(query)

# GOOD: Use parameterized queries
self.env.cr.execute("SELECT id FROM table WHERE name = %s", (user_input,))
```

### 4. Unescaped Content (XSS)

**Problem**: Using `t-raw` with user-provided content.

```xml
<!-- BAD: t-raw with user content -->
<div t-raw="info_message"/>

<!-- GOOD: t-esc auto-escapes -->
<div t-esc="info_message"/>
```

```python
# BAD: Unescaped user content
QWeb.render('insecure_template', {
    'info_message': user_provided_content,
})

# GOOD: Separate structure from content
QWeb.render('secure_template', {
    'message': user_provided_content,
})
```

### 5. Using Markup Safely

```python
from markupsafe import Markup

# GOOD: Structure is Markup, content is escaped
message = Markup("<p>%s</p>") % user_provided_content

# GOOD: Use escape() to convert text to Markup
from odoo.tools.misc import html_escape
safe_content = html_escape(user_provided_content)
message = Markup("<p>%s</p>") % safe_content

# BAD: f-strings insert before escaping
# Markup(f"<p>{self.user_input}</p>")  # WRONG!

# GOOD: Use format() with Markup
Markup("<p>{field}</p>").format(field=user_input)
```

### 6. Evaluating Content

```python
# VERY BAD: eval is dangerous
domain = eval(self.filter_domain)
self.search(domain)

# BAD: safe_eval still powerful
from odoo.tools import safe_eval
domain = safe_eval(self.filter_domain)
self.search(domain)

# GOOD: Use literal_eval for parsing
from ast import literal_eval
domain = literal_eval(self.filter_domain)
self.search(domain)
```

### 7. Accessing Dynamic Attributes

```python
# BAD: getattr can access private methods/attributes
def _get_state(self, res_id, state_field):
    record = self.sudo().browse(res_id)
    return getattr(record, state_field)  # Unsafe!

# GOOD: Use __getitem__ which respects field access rules
def _get_state(self, res_id, state_field):
    record = self.sudo().browse(res_id)
    return record[state_field]  # Safe
```

### 8. sudo() Overuse

```python
# BAD: sudo() everywhere bypasses all security
def action_archive(self):
    for record in self:
        record.sudo().write({'active': False})  # No checks!

# GOOD: Use sudo() sparingly and only when needed
def action_archive(self):
    # Archive as current user (ACL checked)
    self.write({'active': False})

# GOOD: Use sudo() to access related model for permission check
def check_access(self):
    # Check if partner is accessible
    partner = self.partner_id.sudo()
    if not partner.check_access_rights('read'):
        raise AccessError("Cannot access partner")
```

### 9. Missing Validation

```python
# BAD: No validation on user input
def update_from_form(self, values):
    self.write(values)  # User could set any field!

# GOOD: Validate and whitelist
def update_from_form(self, values):
    allowed = {'name', 'date', 'notes'}
    updates = {k: v for k, v in values.items() if k in allowed}
    self.write(updates)
```

### 10. Time-of-Check to Time-of-Use (TOCTOU)

```python
# BAD: State changes between check and use
def process_payment(self):
    if self.state != 'paid':  # Check
        # ... time passes ...
        self.write({'state': 'processed'})  # Use (state might have changed)

# GOOD: Use database constraints
_state_constraint = sql_constraint(
    'check_state_before_process',
    'CHECK (state = ''paid'')',
    'Can only process paid records'
)

# Or use @api.constrains
@api.constrains('state')
def _check_state(self):
    for record in self:
        if record.state == 'processed' and record.state != 'paid':
            raise ValidationError("Must be paid to process")
```

---

## Quick Reference

### Security Checklist

| ☐ | Task |
|---|------|
| ☐ | Define user groups |
| ☐ | Create ir.model.access.csv |
| ☐ | Add ACL for each model |
| ☐ | Create record rules for multi-company |
| ☐ | Create record rules for own/all access |
| ☐ | Test with different user roles |
| ☐ | Test with portal/public users |
| ☐ | Review public methods for security |
| ☐ | Check for SQL injection risks |
| ☐ | Check for XSS vulnerabilities |

### Common Security Patterns

#### Own Records Only (Employee)

```python
# Model
user_id = fields.Many2one('res.users', default=lambda s: s.env.user)
```

```xml
<!-- ACL -->
access_model_user,model_my_model,base.group_user,1,0,0,0

<!-- Rule -->
<record id="model_own_rule" model="ir.rule">
    <field name="domain_force">[('user_id', '=', user.id)]</field>
    <field name="groups" eval="[(4, ref('base.group_user'))]"/>
</record>
```

#### Managers See All

```xml
<record id="model_all_rule" model="ir.rule">
    <field name="domain_force">[(1, '=', 1)]</field>
    <field name="groups" eval="[(4, ref('module.group_manager'))]"/>
</record>
```

#### Multi-Company

```python
# Model
company_id = fields.Many2one('res.company', default=lambda s: s.env.company)
```

```xml
<!-- Global rule -->
<record id="model_company_rule" model="ir.rule">
    <field name="domain_force">
        ['|', ('company_id', '=', False), ('company_id', 'in', user.company_ids)]
    </field>
    <field name="global" eval="True"/>
</record>
```

### Security Debugging

```python
# Check current user's groups
self.env.user.groups_id  # All groups

# Check specific group
self.env.user.has_group('base.group_system')

# Check access rights
model.check_access_rights('read')
model.check_access_rights('write', raise_exception=False)

# Check record access
record.check_access_rule('read')
record.check_access_rule('write')
```

---

**For more Odoo 18 guides, see [SKILL.md](../SKILL.md)**

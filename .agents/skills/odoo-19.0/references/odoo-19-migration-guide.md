# Odoo 19 Migration Guide

Guide for migrating modules from Odoo 17/18 to Odoo 19.

## Table of Contents
- [Migration Overview](#migration-overview)
- [Key Changes](#key-changes)
- [Migration Scripts](#migration-scripts)
- [Module Hooks](#module-hooks)
- [Common Migrations](#common-migrations)
- [Testing](#testing)

---

## Migration Overview

### When to Migrate

- **Major version upgrade**: Odoo 17 → 18 → 19
- **Module dependencies changed**
- **API breaking changes**

### Migration Strategy

1. Review changelog and breaking changes
2. Update `__manifest__.py` version
3. Run migration scripts
4. Test thoroughly
5. Update documentation

---

## Key Changes

### Odoo 19 Key Changes

| Area | Change |
|------|--------|
| **List view** | Use `<list>` instead of `<tree>` |
| **Dynamic attributes** | Use direct attributes instead of `attrs` |
| **Delete validation** | Use `@api.ondelete` instead of overriding `unlink()` |
| **Field aggregation** | Use `aggregator=` instead of `group_operator=` |
| **SQL queries** | Use `odoo.tools.SQL` class |
| **Batch create** | Use list of dicts instead of single dict |

### Odoo 18 Key Changes

| Area | Change |
|------|--------|
| **Views** | Use `<list>` instead of `<tree>` |
| **attrs** | Deprecated, use direct attributes |
| **ondelete** | New `@api.ondelete` decorator |

---

## Migration Scripts

### Migration Script Location

```
my_module/
└── migrations/
    └── 19.0.1.0/
        ├── pre-migration.py
        ├── end-migration.py
        └── post-migration.py
```

### Migration Script Naming

| Script | When it runs |
|--------|--------------|
| `pre-migration.py` | Before module update |
| `post-migration.py` | After module update |
| `end-migration.py` | After all migrations |

### Migration Script Template

```python
def migrate(cr, version):
    """
    Migration script for Odoo 19
    """
    # Your migration code here
    pass
```

---

## Common Migrations

### Tree to List View

**Odoo 17 and earlier**:

```xml
<tree string="Records">
    <field name="name"/>
</tree>
```

**Odoo 18+**:

```xml
<list string="Records">
    <field name="name"/>
</list>
```

### attrs to Direct Attributes

**Odoo 17 and earlier**:

```xml
<field name="state" attrs="{'invisible': [('state', '!=', 'draft')]}"/>
```

**Odoo 18+**:

```xml
<field name="state" invisible="state != 'draft'"/>
```

### Delete Validation

**Odoo 17 and earlier**:

```python
def unlink(self):
    for record in self:
        if record.state != 'draft':
            raise UserError("Cannot delete non-draft records")
    return super().unlink()
```

**Odoo 18+**:

```python
@api.ondelete(at_uninstall=False)
def _unlink_if_not_draft(self):
    if any(rec.state != 'draft' for rec in self):
        raise UserError("Cannot delete non-draft records")
```

### Field Aggregation

**Odoo 17 and earlier**:

```python
amount_total = fields.Monetary(group_operator="sum")
```

**Odoo 18+**:

```python
amount_total = fields.Monetary(aggregator="sum")
```

---

## Module Hooks

### pre_init_hook

```python
def pre_init_hook(env):
    """Called before module installation"""
    # Create custom tables, etc.
    pass
```

### post_init_hook

```python
def post_init_hook(env):
    """Called after module installation"""
    # Set default values, create records, etc.
    pass
```

### uninstall_hook

```python
def uninstall_hook(env):
    """Called after module uninstallation"""
    # Clean up custom tables, files, etc.
    pass
```

### Register Hooks in Manifest

```python
{
    ...
    'pre_init_hook': 'my_module.pre_init_hook',
    'post_init_hook': 'my_module.post_init_hook',
    'uninstall_hook': 'my_module.uninstall_hook',
}
```

---

## Migration Checklist

- [ ] Review Odoo 19 changelog
- [ ] Update `__manifest__.py` version
- [ ] Update dependencies
- [ ] Rename `<tree>` to `<list>`
- [ ] Replace `attrs` with direct attributes
- [ ] Replace `unlink()` override with `@api.ondelete`
- [ ] Update field aggregators
- [ ] Update SQL queries to use `odoo.tools.SQL`
- [ ] Run migration scripts
- [ ] Test all functionality
- [ ] Update documentation

---

## Testing Migrations

### Test Migration Script

```python
from odoo.tests import TransactionCase

class TestMigration(TransactionCase):
    def test_migration(self):
        # Test migration script
        pass
```

### Manual Testing

1. Install previous version with sample data
2. Update to Odoo 19
3. Verify all data migrated correctly
4. Test all features

---

## References

- Odoo 19 changelog
- Odoo 18 changelog

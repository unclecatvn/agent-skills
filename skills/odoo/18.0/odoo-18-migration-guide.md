---
name: odoo-18-migration
description: Comprehensive guide for upgrading modules and data to Odoo 18,
  including migration scripts, upgrade hooks, deprecations, and best practices.
globs: "**/migrations/**/*.py"
topics:
  - Migration script structure (pre/post/end)
  - Module upgrade hooks (pre_init, post_init, uninstall)
  - Deprecations and replacements
  - Data migration with SQL and ORM
  - Version checks and upgrade tooling
when_to_use:
  - Creating or reviewing migration scripts
  - Upgrading modules across major versions
  - Handling data migration and cleanup
  - Dealing with deprecations
---

# Odoo 18 Migration Guide

Comprehensive guide for migrating modules and data to Odoo 18, covering migration scripts, upgrade hooks, deprecations, and best practices.

## Table of Contents

1. [Migration Script Structure](#migration-script-structure)
2. [Module Upgrade Hooks](#module-upgrade-hooks)
3. [Migration Stages](#migration-stages)
4. [Code Upgrade Tool](#code-upgrade-tool)
5. [Deprecations in Odoo 18](#deprecations-in-odoo-18)
6. [Migration Best Practices](#migration-best-practices)
7. [Real-World Examples](#real-world-examples)
8. [Version Management](#version-management)

---

## Migration Script Structure

### Directory Layout

Migration scripts are organized in versioned directories within your module:

```python
<module>/
├── __init__.py
├── __manifest__.py
├── models/
├── migrations/
│   ├── 1.0/
│   │   ├── pre-update_table_x.py
│   │   ├── post-create_plop_records.py
│   │   └── end-cleanup.py
│   ├── 9.0.1.1/           # Server-specific version
│   ├── 16.0.1.0/          # Odoo 16.0 only
│   ├── 17.0.2.1/          # Odoo 17.0 only
│   ├── 0.0.0/             # Runs on any version change
│   └── tests/
└── upgrades/              # Alternative location
    └── 1.1/
        └── pre-migrate.py
```

### Migration Script Function Signature

```python
# File: migrations/18.0.1.0/pre-migrate_data.py

def migrate(cr, version):
    """
    Migration script for Odoo 18.0

    Args:
        cr: Database cursor (SQL operations)
        version: Previously installed version (None for new installs)
    """
    if version is None:
        return  # New installation, skip migration

    # Your migration code here
    cr.execute("""
        UPDATE your_model
        SET field_name = 'new_value'
        WHERE condition = true
    """)
```

**Valid Parameter Signatures:**
- `(cr, version)` - Recommended
- `(cr, _version)` - If version is unused
- `(_cr, version)` - If cr is unused (rare)
- `(_cr, _version)` - If both unused (rare)

### Version Format

The migration system supports these version formats:

```python
# VERSION_RE pattern from odoo/modules/migration.py
^(6.1|6.0-18.0|saas~11-99)\.?  # Optional server version prefix
\d+\.\d+(\.\d+)?              # Module version (x.y or x.y.z)

# Examples:
16.0.1.0   # Odoo 16.0, module version 1.0
17.0.2.1   # Odoo 17.0, module version 2.1
0.0.0      # Any version change
18.0       # Odoo 18.0, module version 0
```

---

## Module Upgrade Hooks

### Manifest Hooks (`__manifest__.py`)

```python
# File: __manifest__.py

{
    'name': 'My Module',
    'version': '18.0.1.0',

    # Hooks executed during module lifecycle
    'pre_init_hook': 'pre_init_function',      # Before installation
    'post_init_hook': 'post_init_function',     # After installation
    'uninstall_hook': 'uninstall_function',     # Before uninstallation
}
```

### pre_init_hook

Runs **before** the module is installed. Use for:
- Checking prerequisites
- Preparing data structures
- Validating system requirements

```python
# File: __init__.py

def pre_init_function(env):
    """Check system requirements before installation."""
    # Example: Check if required module is installed
    if not env['ir.module.module'].search([('name', '=', 'required_module')]):
        raise ValueError('Required module must be installed first')

    # Example: Create custom database tables
    env.cr.execute("""
        CREATE TABLE IF NOT EXISTS custom_table (
            id SERIAL PRIMARY KEY,
            name VARCHAR(255)
        )
    """)
```

### post_init_hook

Runs **after** the module is installed. Use for:
- Creating initial data
- Setting up configurations
- Initializing default values

```python
def post_init_function(env):
    """Initialize data after installation."""
    # Create default records
    env['my.model'].create([
        {'name': 'Default Record 1', 'code': 'DEFAULT1'},
        {'name': 'Default Record 2', 'code': 'DEFAULT2'},
    ])

    # Configure ir.config_parameter
    env['ir.config_parameter'].set_param('my_module.key', 'default_value')
```

### uninstall_hook

Runs **before** the module is uninstalled. Use for:
- Cleaning up custom tables
- Removing generated files
- Reverting system changes

```python
def uninstall_function(env):
    """Clean up before uninstallation."""
    # Drop custom tables
    env.cr.execute("DROP TABLE IF EXISTS custom_table")

    # Remove generated files
    import os
    path = os.path.join('/filestore', 'my_module')
    if os.path.exists(path):
        shutil.rmtree(path)
```

### Hook Execution Order

```
Module Upgrade Process:
├── For each module being upgraded:
│   ├── Run 'pre' migrations
│   ├── Load Python module
│   ├── Execute pre_init_hook (if new install)
│   ├── Create/update database tables
│   ├── Load data files (XML, CSV)
│   ├── Run 'post' migrations
│   └── Execute post_init_hook (if new install)
└── After all modules:
    └── Run 'end' migrations
```

---

## Migration Stages

### Pre-Stage (`pre-*.py`)

Runs **before** module initialization:
- Tables may not exist yet
- Models are not loaded
- Use raw SQL for data manipulation

```python
# File: migrations/18.0.1.0/pre-update_schema.py

def migrate(cr, version):
    """Update database schema before models are loaded."""
    # Add new column
    cr.execute("""
        ALTER TABLE your_model
        ADD COLUMN IF NOT EXISTS new_field VARCHAR(255)
    """)

    # Migrate data from old field
    cr.execute("""
        UPDATE your_model
        SET new_field = old_field
        WHERE new_field IS NULL
    """)
```

### Post-Stage (`post-*.py`)

Runs **after** module initialization:
- Tables and models are loaded
- Can use ORM (`api.Environment`)
- Best for data migrations

```python
# File: migrations/18.0.1.0/post-migrate_data.py

def migrate(cr, version):
    """Migrate data using ORM after models are loaded."""
    from odoo import api
    env = api.Environment(cr, 1, {})  # SUPERUSER_ID = 1

    # Example: Split name into first_name and last_name
    Partner = env['res.partner']
    partners = Partner.search([('name', '!=', False)])

    for partner in partners:
        names = partner.name.split(' ', 1)
        partner.write({
            'first_name': names[0],
            'last_name': names[1] if len(names) > 1 else '',
        })
```

### End-Stage (`end-*.py`)

Runs **after ALL modules have been updated:
- Can reference models from other modules
- Use for cross-module data consistency

```python
# File: migrations/18.0.1.0/end-update_references.py

def migrate(cr, version):
    """Update cross-module references after all modules loaded."""
    from odoo import api
    env = api.Environment(cr, 1, {})

    # Update references to other module's models
    sales = env['sale.order'].search([])
    for order in sales:
        # Update fields that depend on other modules
        if order.partner_id.country_id.code == 'US':
            order.write({'warehouse_id': env.ref('stock.stock_warehouse_us').id})
```

### Stage Execution Order for `0.0.0`

Version `0.0.0` scripts have special execution order:

```python
migrations/0.0.0/
├── pre-script.py  # Runs FIRST (before any other migrations)
├── post-script.py # Runs LAST (after any other migrations)
└── end-script.py  # Runs LAST among end-stage scripts
```

---

## Code Upgrade Tool

### Command-Line Usage

Odoo 18 provides a tool for automated source code transformations:

```bash
# Upgrade from one version to another
./odoo-bin upgrade_code --from 17.0 --to 18.0

# Run specific upgrade script
./odoo-bin upgrade_code --script 17.5-01-tree-to-list

# Upgrade specific addons
./odoo-bin upgrade_code --addons-path=/path/to/addons --from 17.0 --to 18.0
```

### Upgrade Script Template

```python
# File: odoo/upgrade_code/18.0-01-example.py

def upgrade(file_manager):
    """
    Upgrade script for transforming source code.

    Args:
        file_manager: Provides access to all source files
    """
    total = len(file_manager)

    for i, file in enumerate(file_manager, 1):
        # Process Python files
        if file.path.suffix == '.py':
            file.content = file.content.replace('old_pattern', 'new_pattern')

        # Process XML files
        elif file.path.suffix == '.xml':
            file.content = file.content.replace('<tree', '<list')

        # Print progress
        file_manager.print_progress(i, total)
```

### Built-in Upgrade Scripts

Located in `/Users/unclecat/dtg/odoo/odoo/upgrade_code/`:

```python
# 17.5-01-tree-to-list.py
# Converts 'tree' views to 'list' views (Odoo 17+ naming change)

def upgrade(file_manager):
    for file in file_manager:
        if file.path.suffix == '.xml':
            file.content = re.sub(
                r'(<record\s+[^>]*?)\btree\b',
                r'\1list',
                file.content
            )
```

---

## Deprecations in Odoo 18

### Manifest File Deprecation

```python
# DEPRECATED (since Odoo 17)
__openerp__.py

# Use instead
__manifest__.py
```

**Warning:**
```python
DeprecationWarning: __openerp__.py manifests are deprecated since 17.0,
rename to __manifest__.py
```

### API Method Deprecations

```python
# DEPRECATED (Odoo 18+)
records.check_access_rights(operation, raise_exception=True)
records.check_access_rule(operation)

# Use instead
records.check_access(operations=[operation])
```

### XML Declaration Deprecation

```xml
<!-- DEPRECATED (since Odoo 17) -->
<?xml version="1.0" encoding="UTF-8"?>
<odoo>
    <record model="ir.ui.view" id="view_form">
        <field name="name">my.model.form</field>
    </record>
</odoo>

<!-- XML declaration in HTML descriptions is deprecated -->
<!-- Use plain HTML without XML declaration -->
```

### Version-Specific Deprecations

```python
# Odoo 17+
# - __openerp__.py manifests
# - XML declarations in module descriptions

# Odoo 18+
# - check_access_rights() → check_access()
# - check_access_rule() → check_access()
# - _filter_access_rules() → _filtered_access()
# - _filter_access_rules_python() → _filtered_access()
```

---

## Migration Best Practices

### 1. Use Raw SQL for Performance

For large data migrations, use SQL instead of ORM:

```python
def migrate(cr, version):
    # GOOD: Fast SQL for bulk updates
    cr.execute("""
        UPDATE sale_order_line
        SET price_unit = COALESCE(
            (SELECT list_price FROM product_product
             WHERE product_product.id = sale_order_line.product_id),
            0.0
        )
    """)

    # AVOID: Slow ORM loop
    # env = api.Environment(cr, 1, {})
    # for line in env['sale.order.line'].search([]):
    #     line.price_unit = line.product_id.list_price
```

### 2. Handle NULL Version (New Installs)

```python
def migrate(cr, version):
    # Always check for new installations
    if version is None:
        return

    # Only run on upgrades from previous versions
    if parse_version(version) < parse_version('17.0.1.0'):
        # Specific migration for old versions
        pass
```

### 3. Use Environment for ORM Access

```python
from odoo import api

def migrate(cr, version):
    # Create environment with SUPERUSER_ID
    env = api.Environment(cr, 1, {})

    # Now use ORM normally
    products = env['product.product'].search([])
    for product in products:
        product.write({'default_code': product.code})
```

### 4. Batch Large Operations

```python
def migrate(cr, version):
    # Process in batches to avoid memory issues
    batch_size = 1000
    offset = 0

    while True:
        cr.execute("""
            SELECT id FROM large_table
            ORDER BY id
            LIMIT %s OFFSET %s
        """, (batch_size, offset))

        ids = [row[0] for row in cr.fetchall()]
        if not ids:
            break

        # Process batch
        cr.execute("""
            UPDATE large_table
            SET processed = true
            WHERE id = ANY(%s)
        """, (ids,))

        offset += batch_size
        cr.commit()  # Commit each batch
```

### 5. Add Rollback Protection

```python
def migrate(cr, version):
    try:
        # Migration code here
        cr.execute("ALTER TABLE model ADD COLUMN new_field VARCHAR")
    except Exception as e:
        # Log error but don't fail entire upgrade
        import logging
        logger = logging.getLogger(__name__)
        logger.warning("Migration failed: %s", e)
```

### 6. Test Migrations

```python
# File: migrations/18.0.1.0/tests/test_migration.py

from odoo.tests import TransactionCase

class TestMigration(TransactionCase):
    def test_migration(self):
        """Test that migration runs without errors."""
        # Simulate old version
        self.cr.execute("UPDATE ir_module_module SET latest_version = '17.0.1.0'")

        # Run migration
        from odoo.modules import migration
        manager = migration.MigrationManager(self.cr, 'my_module')
        manager.migrate_module(['my_module'], 'post')

        # Verify results
        self.cr.execute("SELECT COUNT(*) FROM my_model WHERE new_field IS NOT NULL")
        self.assertGreater(self.cr.fetchone()[0], 0)
```

---

## Real-World Examples

### Example 1: Field to Property Migration

```python
# File: addons/purchase/migrations/9.0.1.2/pre-create-properties.py

def migrate(cr, version):
    """Convert field to ir.property for multi-company support."""

    def convert_field(cr, model, field, target_model):
        # Get existing values
        cr.execute("""
            SELECT id, {field}, company_id
            FROM {table}
            WHERE {field} IS NOT NULL
        """.format(field=field, table=model.replace('.', '_')))

        # Insert as properties
        for record_id, value, company_id in cr.fetchall():
            cr.execute("""
                INSERT INTO ir_property (
                    name, type, fields_id,
                    company_id, value_reference, res_id
                )
                VALUES (
                    %s, 'many2one',
                    (SELECT id FROM ir_model_fields
                     WHERE model = %s AND name = %s),
                    %s, %s, %s
                )
            """, (field, model, field, company_id,
                  f'{target_model},{value}', f'{model},{record_id}'))

        # Drop old column
        cr.execute(f'ALTER TABLE "{model.replace(".", "_")}" DROP COLUMN "{field}"')

    convert_field(cr, 'purchase.order', 'warehouse_id', 'stock.warehouse')
```

### Example 2: UUID Deduplication

```python
# File: addons/point_of_sale/upgrades/1.0.2/post-deduplicate-uuids.py

def migrate(cr, version):
    """Fix duplicate UUIDs from upgrade."""

    def deduplicate_uuids(table):
        # Find duplicates
        cr.execute(f"""
            SELECT UNNEST(ARRAY_AGG(id))
            FROM {table}
            WHERE uuid IS NOT NULL
            GROUP BY uuid
            HAVING COUNT(*) > 1
        """)

        for record_ids in cr.fetchall():
            # Keep first, regenerate rest
            record_ids = list(record_ids)
            for record_id in record_ids[1:]:
                cr.execute(f"""
                    UPDATE {table}
                    SET uuid = gen_random_uuid()
                    WHERE id = %s
                """, (record_id,))

    deduplicate_uuids('pos_order')
    deduplicate_uuids('pos_order_line')
```

### Example 3: Tag Migration with SQL

```python
# File: addons/l10n_nl/migrations/3.3/post-migrate_update_taxes.py

def migrate(cr, version):
    """Update tax tags with SQL for performance."""
    from odoo.tools import SQL

    env = api.Environment(cr, 1, {})

    # Find old and new tags
    old_tag = env.ref('l10n_nl.tax_tag_old', raise_if_not_found=False)
    new_tag = env.ref('l10n_nl.tax_tag_new', raise_if_not_found=False)

    if old_tag and new_tag:
        # Use SQL for bulk update
        cr.execute(SQL("""
            UPDATE account_account_tag_account_tax_repartition_line_rel
            SET account_account_tag_id = %(new_tag)s
            WHERE account_account_tag_id = %(old_tag)s
        """), {'old_tag': old_tag.id, 'new_tag': new_tag.id}))
```

### Example 4: Currency Migration

```python
# File: migrations/18.0.1.0/post-migrate_currency.py

def migrate(cr, version):
    """Migrate to multi-currency support."""
    from odoo import api

    env = api.Environment(cr, 1, {})

    # Get company currency
    company = env['res.company'].search([], limit=1)
    currency_id = company.currency_id.id

    # Add currency field to existing records
    cr.execute("""
        UPDATE sale_order
        SET currency_id = %s
        WHERE currency_id IS NULL
    """, (currency_id,))

    # Update pricelist currency
    cr.execute("""
        UPDATE product_pricelist
        SET currency_id = %s
        WHERE currency_id IS NULL
    """, (currency_id,))
```

### Example 5: Many2many Relationship Migration

```python
# File: migrations/18.0.1.0/post-migrate_m2m.py

def migrate(cr, version):
    """Migrate Many2many relationship to new model."""
    from odoo import api

    env = api.Environment(cr, 1, {})

    # Create new relationship records
    cr.execute("""
        INSERT INTO model1_model2_rel (model1_id, model2_id)
        SELECT m1.id, m2.id
        FROM old_table ot
        JOIN model1 m1 ON ot.old_field1 = m1.old_id
        JOIN model2 m2 ON ot.old_field2 = m2.old_id
        ON CONFLICT DO NOTHING
    """)

    # Drop old table
    cr.execute("DROP TABLE IF EXISTS old_table")
```

---

## Version Management

### Version Parsing

```python
from odoo.tools.parse_version import parse_version

# Parse versions for comparison
v1 = parse_version('17.0.1.0')
v2 = parse_version('18.0.0.1')

if v2 > v1:
    print("v2 is newer")

# Supports semantic versioning
parse_version('18.0.1.0.alpha')  # Pre-release
parse_version('18.0.1.0.beta1')   # Beta
parse_version('18.0.1.0.rc2')     # Release candidate
```

### Version Adaptation

```python
# From odoo/modules/module.py
def adapt_version(version):
    """Adapts module version to current Odoo series."""
    serie = release.major_version  # e.g., "18.0"

    if version == serie or not version.startswith(serie + '.'):
        version = f'{serie}.{version}'

    # Validates format: x.y or x.y.z or serie.x.y or serie.x.y.z
    return version

# Examples:
adapt_version('1.0')      # → '18.0.1.0'
adapt_version('18.0.1.0') # → '18.0.1.0'
```

### Version-Specific Migrations

```python
def migrate(cr, version):
    """Handle migration from multiple previous versions."""

    if version is None:
        return  # New installation

    parsed_version = parse_version(version)

    # Migrate from 16.0
    if parsed_version < parse_version('17.0'):
        cr.execute("UPDATE model SET field = 'v16_value'")

    # Migrate from 17.0
    if parsed_version < parse_version('18.0'):
        cr.execute("UPDATE model SET field = 'v17_value'")

    # Migrate to 18.0
    cr.execute("UPDATE model SET field = 'v18_value'")
```

---

## Additional Resources

### Key Files Reference

| File Path | Purpose |
|-----------|---------|
| `/odoo/modules/migration.py` | Core migration system |
| `/odoo/modules/loading.py` | Module loading & upgrade orchestration |
| `/odoo/modules/module.py` | Module discovery & version management |
| `/odoo/modules/registry.py` | Model registry management |
| `/odoo/cli/upgrade_code.py` | Source code upgrade tool |
| `/odoo/tools/parse_version.py` | Version parsing utilities |
| `/addons/base/models/ir_module.py` | Module model & operations |
| `/odoo/upgrade_code/` | Automated upgrade scripts |

### Testing Migrations

```python
# Test migration with upgrade
python odoo-bin -d test_db --init=your_module --test-enable

# Test specific migration
python odoo-bin -d test_db --update=your_module --test-enable
```

### Debug Mode

```bash
# Enable logging for migration debugging
./odoo-bin --log-level=debug --log-handler=odoo.modules.migration:DEBUG
```

### Quick Reference

```python
# Migration script template
def migrate(cr, version):
    """
    Odoo 18 Migration Script

    Args:
        cr: Database cursor
        version: Previously installed version
    """
    # Check for new install
    if version is None:
        return

    # Migration code here
    pass
```

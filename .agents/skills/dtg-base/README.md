# DTG Base Skill

Complete reference for DTG Base module utilities and helpers in Odoo 18.

## Overview

DTG Base is a custom abstract model that provides common utility methods for Odoo development. This skill contains comprehensive documentation for all DTGBase utilities.

## What's Included

- **Date & Period Utilities** - Find first/last dates, iterate over periods
- **Timezone Conversion** - Convert between local time and UTC
- **Barcode Utilities** - Validate and generate EAN13 barcodes
- **Batch Processing** - Split large recordsets into manageable batches
- **after_commit Decorator** - Execute code after transaction commit
- **Vietnamese Text** - Strip accents for search/comparison
- **File Utilities** - Zip directories, get file sizes
- **Number Utilities** - Round to specific decimal places

## Files

| File | Description |
|------|-------------|
| `SKILL.md` | Master index and quick reference |
| `CLAUDE.md` | AI agent guidance |
| `odoo-18-dtg-base-guide.md` | Complete DTG Base utilities reference |

## Quick Start

```python
class MyModel(models.Model):
    _name = 'my.model'
    _inherit = ['dtg_base.dtg_base']

    def my_method(self):
        # Use DTGBase utilities
        first_date = self.find_first_date_of_period('2024-01-15', 'month')
        utc_date = self.convert_local_to_utc('2024-01-15 10:00:00')
```

## Links

- [Full Documentation](./odoo-18-dtg-base-guide.md)
- [SKILL.md](./SKILL.md) - Quick reference

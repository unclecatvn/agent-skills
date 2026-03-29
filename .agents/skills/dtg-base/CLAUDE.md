# DTG Base Development Guide

This file provides guidance to AI agents when working with DTG Base utilities in Odoo 18.

## What is DTG Base?

DTG Base is a custom abstract model (`dtg_base.DTGBase`) that provides common utility methods for Odoo development at DTG. It's inherited by other models to gain access to helpful utilities.

## Location

**Module**: `addons_customs/erp/dtg_base/`

**Main Model**: `dtg_base/models/dtg_base.py`

## When to Use DTG Base

| Task | Method |
|------|--------|
| Get first date of month/quarter/year | `find_first_date_of_period(date, 'month')` |
| Get last date of month/quarter/year | `find_last_date_of_period(date, 'year')` |
| Convert local datetime to UTC | `convert_local_to_utc(local_dt, 'Asia/Ho_Chi_Minh')` |
| Convert UTC to local datetime | `convert_utc_to_local(utc_dt, 'Asia/Ho_Chi_Minh')` |
| Check if barcode exists | `barcode_exists('1234567890123')` |
| Generate EAN13 barcode | `get_ean13('product_code')` |
| Process large recordsets in batches | `splittor(limit=100)` |
| Remove Vietnamese accents | `strip_accents('Tiếng Việt')` |
| Zip a directory | `zip_dir(source_path, output_path)` |
| Get file size in readable format | `_get_file_size(file_path)` |

## Inheritance Pattern

```python
from odoo import models

class MyModel(models.Model):
    _name = 'my.model'
    _inherit = ['dtg_base.dtg_base']

    def process_records(self):
        # Use DTGBase utilities
        for batch in self.splittor(limit=100):
            # Process batch
            pass
```

## Key Utilities

### Date & Period

```python
# Get first date of current month
first_date = self.find_first_date_of_period(fields.Date.today(), 'month')

# Get last date of current quarter
last_date = self.find_last_date_of_period(fields.Date.today(), 'quarter')

# Iterate over months in a period
for start, end in self.period_iter('2024-01-01', '2024-12-31', 'month'):
    print(f"Period: {start} to {end}")
```

### Timezone Conversion

```python
# Convert Vietnam local time to UTC
utc_dt = self.convert_local_to_utc('2024-01-15 10:00:00', 'Asia/Ho_Chi_Minh')

# Convert UTC to Vietnam local time
local_dt = self.convert_utc_to_local(utc_dt, 'Asia/Ho_Chi_Minh')
```

### Batch Processing

```python
# Process 1000 records in batches of 100
records = self.env['my.model'].search([])
for batch in records.splittor(limit=100):
    # Process each batch
    for record in batch:
        # Do something
        pass
```

### Barcode

```python
# Check if barcode already exists
if self.barcode_exists('1234567890123'):
    raise UserError("Barcode already exists!")

# Generate EAN13 barcode
ean13 = self.get_ean13('PRODUCT123')
```

### Vietnamese Text

```python
# Remove accents for search/comparison
search_text = self.strip_accents('Tiếng Việt')  # -> 'Ties Viet'

# For comparison
if self.strip_accents(record.name) == self.strip_accents(search_term):
    # Match
    pass
```

## Period Types

| Type | Description |
|------|-------------|
| `'month'` | Month period |
| `'quarter'` | Quarter period |
| `'year'` | Year period |
| `'week'` | Week period |

## Common Timezones

| Timezone | UTC Offset |
|----------|------------|
| `'Asia/Ho_Chi_Minh'` | UTC+7 |
| `'UTC'` | UTC+0 |
| `'Asia/Bangkok'` | UTC+7 |
| `'Asia/Singapore'` | UTC+8 |

---

**For complete reference, see [odoo-18-dtg-base-guide.md](./odoo-18-dtg-base-guide.md)**

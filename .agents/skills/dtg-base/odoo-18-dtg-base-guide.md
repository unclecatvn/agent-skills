---
name: odoo-18-dtg-base
description: Complete reference for DTG Base module utilities and helpers. DTGBase is an abstract model providing common utility methods for date/time handling, barcode generation, timezone conversion, file operations, and more.
globs: "**/addons_customs/erp/**/*.py"
topics:
  - DTGBase abstract model inheritance
  - Date/Period utilities (find_first_date_of_period, find_last_date_of_period, period_iter)
  - Timezone conversion (convert_local_to_utc, convert_utc_to_local)
  - Barcode utilities (barcode_exists, get_ean13)
  - Batch processing (splittor)
  - after_commit decorator
  - Vietnamese text utilities (strip_accents, _no_accent_vietnamese)
  - File utilities (zip_dir, zip_dirs, _get_file_size)
when_to_use:
  - Working with DTG Odoo codebase
  - Need date/period calculations
  - Timezone conversions
  - Barcode validation
  - Batch processing large recordsets
  - Vietnamese text processing
---

# Odoo 18 DTG Base Guide

Complete reference for DTG Base module utilities and helpers.

## Table of Contents

1. [DTGBase Abstract Model](#dtgbase-abstract-model)
2. [Date & Period Utilities](#date--period-utilities)
3. [Timezone Conversion](#timezone-conversion)
4. [Barcode Utilities](#barcode-utilities)
5. [Batch Processing](#batch-processing)
6. [after_commit Decorator](#after_commit-decorator)
7. [String & Text Utilities](#string--text-utilities)
8. [File Utilities](#file-utilities)
9. [Number Utilities](#number-utilities)

---

## DTGBase Abstract Model

### Inherit from DTGBase

**Location**: `addons_customs/erp/dtg_base/models/dtg_base.py`

```python
from odoo import models, fields

class MyModel(models.Model):
    _name = 'my.model'
    _inherit = ['dtg.base']  # Inherit DTGBase to access all utilities

    name = fields.Char()
```

**When to inherit**:
- Need date/period calculation utilities
- Need timezone conversion
- Need barcode validation/generation
- Need batch processing with memory management
- Need Vietnamese text processing
- Need file zipping utilities

---

## Date & Period Utilities

### Period Names

Supported periods: `'hourly'`, `'daily'`, `'weekly'`, `'monthly'`, `'quarterly'`, `'biannually'`, `'annually'`

Aliases also work: `'hour'`, `'day'`, `'week'`, `'month'`, `'quarter'`, `'biannual'`, `'year'`, `'annual'`

### find_first_date_of_period()

Find the first date of a period from any date within that period.

```python
# Get first day of month from any date
date = fields.Date.to_date('2024-02-15')
first_day = self.find_first_date_of_period('monthly', date)
# Result: datetime(2024, 2, 1, 0, 0, 0)

# Get first day of week (Monday)
first_week_day = self.find_first_date_of_period('weekly', date)
# Result: datetime(2024, 2, 12, 0, 0, 0) - Monday of that week

# Get first day of quarter
first_quarter_day = self.find_first_date_of_period('quarterly', date)
# Result: datetime(2024, 1, 1, 0, 0, 0) - Q1 starts Jan 1

# With offset - start from 5th day
first_day_offset = self.find_first_date_of_period('monthly', date, start_day_offset=5)
# Result: datetime(2024, 2, 6, 0, 0, 0)
```

### find_last_date_of_period()

Find the last date of a period from any date within that period.

```python
# Get last day of month
date = fields.Date.to_date('2024-02-15')
last_day = self.find_last_date_of_period('monthly', date)
# Result: datetime(2024, 2, 29, 23, 59, 59, 999999) - 2024 is leap year

# Get last day of quarter
last_quarter_day = self.find_last_date_of_period('quarterly', date)
# Result: datetime(2024, 3, 31, 23, 59, 59, 999999)

# When given_date is also the start date
start_date = fields.Date.to_date('2024-02-01')
last_day_from_start = self.find_last_date_of_period('monthly', start_date, date_is_start_date=True)
# Result: datetime(2024, 2, 29, 23, 59, 59, 999999)

# Custom cycle value - 2 months
last_day_2months = self.find_last_date_of_period('monthly', date, cycle_value=2)
# Result: datetime(2024, 3, 31, 23, 59, 59, 999999) - 2 month period
```

### period_iter()

Generate sorted dates for periods between two dates.

```python
# Get all month ends between two dates
dt_start = fields.Date.to_date('2024-01-15')
dt_end = fields.Date.to_date('2024-06-20')

period_dates = self.period_iter('monthly', dt_start, dt_end)
# Result: [
#   date(2024, 1, 15),   # start date
#   date(2024, 1, 31),   # end of Jan
#   date(2024, 2, 29),   # end of Feb
#   date(2024, 3, 31),   # end of Mar
#   date(2024, 4, 30),   # end of Apr
#   date(2024, 5, 31),   # end of May
#   date(2024, 6, 20),   # end date
# ]

# Quarterly with offset
quarterly_dates = self.period_iter('quarterly', dt_start, dt_end, start_day_offset=5)
# Result includes dates starting from 5th day of each quarter
```

### Date Difference Utilities

```python
# Days between dates
days = self.get_days_between_dates(date_from, date_to)

# Hours between datetimes
hours = self.get_hours_between_dates(datetime_from, datetime_to)

# Weeks between dates
weeks = self.get_weeks_between_dates(date_from, date_to)

# Months between dates (float, respects odd/even months)
months = self.get_months_between_dates(date_from, date_to)
# Example: Jan 15 to Feb 14 = 0.9677 months (31 days in Jan)

# Years between dates (float, respects leap years)
years = self.get_number_of_years_between_dates(date_from, date_to)

# Days in month
days_in_month = self.get_days_of_month_from_date(date)

# Day of year (1-366)
day_of_year = self.get_day_of_year_from_date(date)
# Example: Jan 6 returns 6

# Days in year (365 or 366)
days_in_year = self.get_days_in_year(date)
```

### Other Date Utilities

```python
# Split date into components
year, month, day = self.split_date(date)

# Next weekday
next_monday = self.next_weekday(date, weekday=0)  # 0=Monday, 6=Sunday
same_weekday = self.next_weekday(date)  # Same weekday next week

# Break time range at midnight
# 2024-02-02 20:00 to 2024-02-03 04:00
# -> [2024-02-02 20:00, 2024-02-03 00:00, 2024-02-03 04:00]
intervals = self.break_timerange_for_midnight(start_dt, end_dt)
```

### Period Ratio Calculation

```python
# Calculate ratio between two periods
# Example: monthly vs daily on Feb 2024 (29 days)
ratio = self.get_ratio_between_periods('monthly', 1, 'daily', 1, given_date=date(2024, 2, 1))
# Result: 29/7

# Example: quarterly vs monthly
ratio = self.get_ratio_between_periods('quarterly', 1, 'monthly', 1)
# Result: 3.0
```

---

## Timezone Conversion

### get_company_tz()

Get company timezone.

```python
# Get current company's timezone
tz = self.get_company_tz()
# Returns: 'Asia/Ho_Chi_Minh' or 'UTC' or company's timezone

# Get specific company's timezone
tz = self.get_company_tz(company=company_record)
```

### convert_local_to_utc()

Convert local datetime to UTC.

```python
# Convert local datetime to UTC
local_dt = datetime(2024, 2, 15, 14, 30, 0)
utc_dt = self.convert_local_to_utc(local_dt, force_local_tz_name='Asia/Ho_Chi_Minh')
# Result: datetime(2024, 2, 15, 7, 30, 0) (UTC is 7 hours behind)

# Use context tz or user tz
utc_dt = self.convert_local_to_utc(local_dt)

# With naive=True (no timezone info in result)
utc_dt_naive = self.convert_local_to_utc(local_dt, naive=True)
# Result: datetime(2024, 2, 15, 7, 30, 0) without tzinfo

# Convert date to datetime then to UTC
date_only = date(2024, 2, 15)
utc_from_date = self.convert_local_to_utc(date_only)
```

### convert_utc_to_local()

Convert UTC datetime to local timezone.

```python
# Convert UTC to local
utc_dt = datetime(2024, 2, 15, 7, 30, 0)
local_dt = self.convert_utc_to_local(utc_dt, force_local_tz_name='Asia/Ho_Chi_Minh')
# Result: datetime(2024, 2, 15, 14, 30, 0)

# With DST handling
local_dt = self.convert_utc_to_local(utc_dt, is_dst=False)
```

### Time Conversion Utilities

```python
# Convert datetime to float hours
# datetime(2024, 1, 1, 14, 30, 0) -> 14.5
float_hours = self.time_to_float_hour(datetime)

# Convert float hours to time
# 14.5 -> time(14, 30, 0)
time_obj = self.float_hours_to_time(14.5)

# Convert hours to string "HH:MM"
time_str = self.hours_time_string(14.5)  # "14:30"
time_str = self.hours_time_string(8.5)   # "08:30"

# Convert date to datetime (combines with current time)
dt = self.date_to_datetime(date_value)
```

---

## Barcode Utilities

### barcode_exists()

Check if barcode exists in a model.

```python
# Check in current model
exists = self.barcode_exists('8901234567890')

# Check in specific model
exists = self.barcode_exists('8901234567890', model_name='product.product')

# Check with custom barcode field
exists = self.barcode_exists('8901234567890', barcode_field='default_code')

# Check only active records (default)
exists = self.barcode_exists('8901234567890', inactive_rec=True)

# Check all records including inactive
exists = self.barcode_exists('8901234567890', inactive_rec=False)
```

### get_ean13()

Generate EAN-13 barcode checksum.

```python
# Generate EAN-13 from 12-digit base
barcode = self.get_ean13('123456789012')
# Result: '1234567890128' (last digit is checksum)

# Pads with zeros if less than 12 digits
barcode = self.get_ean13('123')
# Result: '000000000123X' (padded to 12 digits + checksum)
```

---

## Batch Processing

### splittor()

Split large recordsets into batches to avoid memory issues.

```python
# Basic usage - splits into batches of PREFETCH_MAX (1000)
for batch in self.splittor(large_recordset):
    # Process batch
    batch.compute_expensive_field()

# Custom batch size
for batch in self.splittor(large_recordset, max_rec_in_batch=500):
    # Process 500 records at a time
    batch.write({'field': value})

# Maintain order - high priority items first
for batch in self.splittor(recordset, max_rec_in_batch=100, maintain_order=True):
    # Batches maintain relative order
    batch.process()

# No flush - keep in cache
for batch in self.splittor(recordset, flush=False):
    # Records stay in cache
    batch.read_only_operation()
```

**Key features**:
- Automatically divides collection into equal-sized batches
- Invalidates recordset after each batch (default) to free memory
- Set `flush=False` to keep records in cache
- Use `maintain_order=True` to preserve order across batches

---

## after_commit Decorator

Execute tasks after database transaction commits.

```python
from odoo.addons.dtg_base.models.dtg_base import after_commit

class MyModel(models.Model):
    _name = 'my.model'
    _inherit = ['dtg.base']

    @after_commit
    def send_notification_after_commit(self):
        """Send notification ONLY after transaction commits"""
        for rec in self:
            rec.message_post(
                body=_("Record created successfully"),
                message_type='notification'
            )

    def action_process(self):
        # This will be called after commit
        self.send_notification_after_commit()
        return {'type': 'ir.actions.act_window_close'}
```

**Important**:
- Function runs AFTER commit, in a new cursor
- Use for notifications, external API calls, emails
- If the function raises an exception, it's logged but doesn't rollback the transaction

---

## String & Text Utilities

### strip_accents() & _no_accent_vietnamese()

Remove accents from Vietnamese text.

```python
# Strip accents (general + Vietnamese specific)
text = "Tiếng Việt có dấu"
no_accent = self.strip_accents(text)
# Result: "Tieng Viet khong dau"

# Direct Vietnamese conversion
vietnamese = "Xin chào, Đất Việt nước đẹp"
converted = self._no_accent_vietnamese(vietnamese)
# Result: "Xin chao, Dat Viet nuoc dep"
```

---

## File Utilities

### zip_dir()

Zip a directory into bytes for storage in Binary field.

```python
# Zip a directory
path = '/path/to/directory'
zipped_bytes = self.zip_dir(path, incl_dir=False)

# Store in binary field
self.attachment_data = zipped_bytes

# Include directory name in zip
zipped_with_dir = self.zip_dir(path, incl_dir=True)
```

### zip_dirs()

Zip multiple directories into one archive.

```python
# Zip multiple directories
paths = ['/path/to/dir1', '/path/to/dir2']
zipped_bytes = self.zip_dirs(paths)

# Store in attachment
attachment = self.env['ir.attachment'].create({
    'name': 'archives.zip',
    'res_id': self.id,
    'res_model': self._name,
    'datas': zipped_bytes,
})
```

### _get_file_size()

Get size of file or directory.

```python
# Get file size
file_size = self._get_file_size('/path/to/file.pdf')
# Returns: size in bytes

# Get directory size (recursive)
dir_size = self._get_file_size('/path/to/directory')
# Returns: total size in bytes (excluding symbolic links)
```

---

## Number Utilities

### sum_digits()

Sum digits until result has specified number of digits.

```python
# Sum all digits once
result = self.sum_digits(178)
# Result: 16 (1 + 7 + 8)

# Sum until single digit
result = self.sum_digits(178, number_of_digit_return=1)
# Result: 7 (1 + 6 = 7)

# Sum until 2 digits
result = self.sum_digits(9999, number_of_digit_return=2)
# Result: 36 (9 + 9 + 9 + 9 = 36)
```

### find_nearest_lucky_number()

Find nearest number where digit sum equals 9.

```python
# Find nearest lucky number
lucky = self.find_nearest_lucky_number(178)
# Result: 171 (1 + 7 + 1 = 9)

# With rounding
lucky = self.find_nearest_lucky_number(178999, rounding=2)
# Result: 178900 (then adjusted to nearest lucky number)

# Round up
lucky = self.find_nearest_lucky_number(100, round_up=True)
# Result: 108 (1 + 0 + 8 = 9)
```

### calculate_weights()

Calculate weight percentages.

```python
# Calculate weights as percentages
weights = self.calculate_weights(2, 6)
# Result: [0.25, 0.75] (25%, 75%)

# With precision
weights = self.calculate_weights(2, 6, precision_digits=2)
# Result: [0.25, 0.75]

# Ensure sum equals 1
assert sum(weights) == 1.0
```

### fibonacci()

Generate Fibonacci sequence.

```python
# Generate 5 terms
fib = self.fibonacci(5)
# Result: [0, 1, 1, 2, 3]

# Deduplicate first 1
fib = self.fibonacci(5, deduplicate_1=True)
# Result: [0, 1, 2, 3] - removed duplicate 1
```

---

## Other Utilities

### validate_year()

Validate and convert year to integer.

```python
# Valid year
year = self.validate_year('2024')  # Returns: 2024
year = self.validate_year(2024)    # Returns: 2024

# Invalid year - raises ValidationError
year = self.validate_year('abc')   # Raises ValidationError
year = self.validate_year(0)       # Raises ValidationError
year = self.validate_year(10000)   # Raises ValidationError
```

### identical_images()

Compare two Image fields.

```python
# Compare two images
is_same = self.identical_images(img1_field, img2_field)
# Returns: True if identical, False otherwise

# Note: Does not support SVG format (PIL limitation)
```

### Unit Conversion

```python
# Miles to kilometers
km = self.mile2km(10)  # Returns: 16.09344

# Kilometers to miles
miles = self.km2mile(16)  # Returns: 9.9419
```

### Week Utilities

```python
# Get weekdays for a period (max 7 days)
weekdays = self.get_weekdays_for_period(date_from, date_to)
# Returns: {0: date, 1: date, ...} where 0=Monday, 6=Sunday
```

---

## Common Patterns

### Pattern 1: Date Range by Period

```python
def _get_period_dates(self, date_from, date_to):
    """Get all month-end dates in range"""
    return self.period_iter('monthly', date_from, date_to)

def action_report_by_period(self):
    date_from = fields.Date.to_date(self.env.context.get('date_from'))
    date_to = fields.Date.to_date(self.env.context.get('date_to'))

    # Get all period boundaries
    period_dates = self._get_period_dates(date_from, date_to)

    for i in range(len(period_dates) - 1):
        period_start = period_dates[i]
        period_end = period_dates[i + 1]
        # Process each period
        self._process_period(period_start, period_end)
```

### Pattern 2: Safe Timezone Conversion

```python
def action_schedule_meeting(self):
    # Get user's local timezone
    tz = self.get_company_tz()

    # Convert user input (local) to UTC for storage
    utc_dt = self.convert_local_to_utc(
        self.meeting_date,
        force_local_tz_name=tz
    )
    self.meeting_date_utc = utc_dt

    # Convert back to local for display
    local_dt = self.convert_utc_to_local(
        self.meeting_date_utc,
        force_local_tz_name=tz
    )
    self.meeting_date_display = local_dt
```

### Pattern 3: Batch Processing Large Recordsets

```python
def action_recompute_all(self):
    # Get all records
    records = self.search([])

    # Process in batches to avoid memory issues
    for batch in self.splittor(records, max_rec_in_batch=500):
        # Each batch is automatically invalidated after processing
        for rec in batch:
            rec._compute_expensive_field()
```

### Pattern 4: After-Commit Notification

```python
@after_commit
def _send_external_notification(self):
    """Send to external API after commit"""
    for rec in self:
        requests.post(
            'https://api.example.com/notify',
            json={'record_id': rec.id, 'state': rec.state}
        )

def action_confirm(self):
    self.state = 'confirmed'
    # Notification only sent if transaction commits
    self._send_external_notification()
```

### Pattern 5: Barcode Validation

```python
def _check_barcode_unique(self, barcode):
    """Validate barcode doesn't exist"""
    if self.barcode_exists(barcode):
        raise UserError(_("Barcode %s already exists") % barcode)

def create(self, vals):
    if vals.get('barcode'):
        self._check_barcode_unique(vals['barcode'])
    return super().create(vals)
```

---

## Anti-Patterns

| Anti-Pattern | Why Bad | Correct Approach |
|--------------|---------|------------------|
| Manual date calculation for periods | Error-prone, timezone issues | Use `find_first_date_of_period()`, `find_last_date_of_period()` |
| Processing all records at once | Memory issues with large datasets | Use `splittor()` for batch processing |
| Sending notifications before commit | Sent even if transaction rolls back | Use `@after_commit` decorator |
| Manual timezone conversion | DST issues, error-prone | Use `convert_local_to_utc()`, `convert_utc_to_local()` |
| Checking barcode with search() | Doesn't check inactive records | Use `barcode_exists()` |

---

## Method Reference

### Date/Period Methods

| Method | Description |
|--------|-------------|
| `find_first_date_of_period(period, date, offset)` | Get first date of period |
| `find_last_date_of_period(period, date, is_start, cycle)` | Get last date of period |
| `period_iter(period, dt_start, dt_end, offset, cycle)` | Get all period dates in range |
| `get_days_between_dates(dt_from, dt_to)` | Days between dates |
| `get_months_between_dates(dt_from, dt_to)` | Months between (float) |
| `get_number_of_years_between_dates(dt_from, dt_to)` | Years between (float) |
| `get_hours_between_dates(dt_from, dt_to)` | Hours between datetimes |
| `get_days_of_month_from_date(dt)` | Number of days in month |
| `get_day_of_year_from_date(dt)` | Day of year (1-366) |
| `get_days_in_year(dt)` | Days in year (365 or 366) |
| `split_date(date)` | Split into year, month, day |
| `next_weekday(date, weekday)` | Get date next week |
| `break_timerange_for_midnight(start, end)` | Split at midnight |
| `get_ratio_between_periods(p1, d1, p2, d2, date)` | Ratio between periods |

### Timezone Methods

| Method | Description |
|--------|-------------|
| `get_company_tz(company)` | Get company timezone |
| `convert_local_to_utc(dt, tz, is_dst, naive)` | Local to UTC |
| `convert_utc_to_local(utc_dt, tz, is_dst, naive)` | UTC to local |
| `time_to_float_hour(dt)` | Datetime to float hours |
| `float_hours_to_time(hours, tz)` | Float to time |
| `hours_time_string(hours)` | Hours to "HH:MM" string |
| `date_to_datetime(date)` | Date to datetime |

### Barcode Methods

| Method | Description |
|--------|-------------|
| `barcode_exists(barcode, model, field, active)` | Check if barcode exists |
| `get_ean13(base_number)` | Generate EAN-13 checksum |

### Batch Methods

| Method | Description |
|--------|-------------|
| `splittor(collection, max, order, flush)` | Split into batches |

### String Methods

| Method | Description |
|--------|-------------|
| `strip_accents(s)` | Remove all accents |
| `_no_accent_vietnamese(s)` | Vietnamese accent removal |

### File Methods

| Method | Description |
|--------|-------------|
| `zip_dir(path, incl_dir)` | Zip directory |
| `zip_dirs(paths)` | Zip multiple directories |
| `_get_file_size(path)` | Get file/dir size |

### Number Methods

| Method | Description |
|--------|-------------|
| `sum_digits(n, digits)` | Sum digits |
| `find_nearest_lucky_number(n, round, up)` | Find lucky number |
| `calculate_weights(*weights, ...)` | Calculate percentages |
| `fibonacci(n, dedup)` | Fibonacci sequence |

### Other Methods

| Method | Description |
|--------|-------------|
| `validate_year(year)` | Validate year (1-9999) |
| `identical_images(img1, img2)` | Compare images |
| `mile2km(miles)` | Convert to km |
| `km2mile(km)` | Convert to miles |
| `get_weekdays_for_period(from, to)` | Get weekdays dict |

---

## Module Info

**Module**: `dtg_base`
**Version**: 1.0.0
**Author**: AnhBT
**Location**: `addons_customs/erp/dtg_base/`
**License**: OPL-1

**Dependencies**: `base`

**Files**:
- `models/dtg_base.py` - DTGBase abstract model with all utilities

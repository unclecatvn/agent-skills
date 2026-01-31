# Odoo 19 Testing Guide

Guide for testing Odoo 19: Python unit tests, JS tests, and tours (integration tests).

## Table of Contents
- [Test Types](#test-types)
- [Python Tests](#python-tests)
- [Test Classes](#test-classes)
- [Test Decorators](#test-decorators)
- [Test Selection](#test-selection)
- [JS Tests](#js-tests)
- [Integration Tests (Tours)](#integration-tests-tours)
- [Performance Testing](#performance-testing)

---

## Test Types

Odoo has three kinds of tests:

| Type | Purpose |
|------|---------|
| **Python unit tests** | Test model business logic |
| **JS unit tests** | Test JavaScript code in isolation |
| **Tours** | Integration testing (Python + JS together) |

---

## Python Tests

### Test Structure

Create a `tests` sub-package in your module:

```
your_module/
├── ...
├── tests/
│   ├── __init__.py
│   ├── test_bar.py
│   └── test_foo.py
```

**Important**: Import test modules from `tests/__init__.py`

```python
# tests/__init__.py
from . import test_foo, test_bar
```

### Test Methods

Test methods must start with `test_`:

```python
class TestModelA(TransactionCase):
    def test_some_action(self):
        record = self.env['model.a'].create({'field': 'value'})
        record.some_action()
        self.assertEqual(record.field, expected_value)
```

---

## Test Classes

### TransactionCase

Most common test class. Each test runs in its own transaction, rolled back at the end.

```python
from odoo.tests import TransactionCase

class TestMyModel(TransactionCase):
    def test_create_record(self):
        record = self.env['my.model'].create({'name': 'Test'})
        self.assertTrue(record.id)
        self.assertEqual(record.name, 'Test')
```

### SingleTransactionCase

Runs all tests in a single transaction (not rolled back). Faster, but tests can affect each other.

```python
from odoo.tests import SingleTransactionCase

class TestMyModel(SingleTransactionCase):
    def test_1_first(self):
        # Creates data
        pass

    def test_2_second(self):
        # Can use data from test_1_first
        pass
```

### HttpCase

For web-related tests. Starts a browser (headless Chrome by default).

```python
from odoo.tests import HttpCase

class TestWebsite(HttpCase):
    def test_homepage(self):
        self.url_open('/hello')
```

---

## Test Decorators

### tagged

Add or remove tags from test classes.

```python
from odoo.tests import TransactionCase, tagged

@tagged('-standard', 'nice')
class NiceTest(TransactionCase):
    pass
```

### Default Tags

- `standard` - Default tag (selected by `--test-tags`)
- `at_install` - Run after module installation (default)
- `post_install` - Run after all modules installed

```python
@tagged('-at_install', 'post_install')
class WebsiteVisitorTests(HttpCase):
    def test_create_visitor(self):
        pass
```

---

## Test Selection

### By Tag

```bash
# Run only nice tests
odoo-bin --test-tags nice

# Run nice and standard tests
odoo-bin --test-tags nice,standard

# Run standard except slow
odoo-bin --test-tags standard,-slow
```

### By Module

```bash
# Run only sale module tests
odoo-bin --test-tags /sale

# Run sale module but not slow tests
odoo-bin --test-tags '/sale,-slow'

# Run stock or slow tests
odoo-bin --test-tags '-standard, slow, /stock'
```

### By Specific Test

```bash
# Run specific test function
odoo-bin --test-tags .test_supplier_invoice

# Equivalent (full path)
odoo-bin --test-tags /account:TestAccount.test_supplier_invoice
```

### Tag Format

```
[-][tag][/module][:class][.method]
```

| Prefix | Meaning |
|--------|---------|
| `-` | Deselect/remove tag |
| `+` | Select/add tag (implicit, optional) |
| `/module` | Specific module |
| `:class` | Specific class |
| `.method` | Specific method |

---

## Test Utilities

### browse_ref

Browse an external ID:

```python
record = self.browse_ref('base.user_admin')
self.assertEqual(record.login, 'admin')
```

### ref

Get database ID from external ID:

```python
user_id = self.ref('base.user_admin')
```

### Form

Helper for testing form views:

```python
from odoo.tests import Form

with Form(self.env['sale.order']) as form:
    form.partner_id = self.partner
    form.date_order = '2023-01-01'
    with form.order_line.new() as line:
        line.product_id = self.product
        line.product_uom_qty = 10

order = form.save()
```

---

## JS Tests

Odoo uses Hoot for JS unit testing. See the frontend testing documentation.

Test files go in `static/tests/`:

```
your_module/
└── static/
    └── tests/
        └── my_test.js
```

```javascript
import { start } from '@mail/utils/test_utils';

QUnit.module('My Module', {
    beforeEach() {
        this.data = {
            records: {
                'my.model': [{id: 1, name: 'Test'}],
            },
        };
    },
}, function () {
    QUnit.test('my test', async function (assert) {
        // Test code here
    });
});
```

---

## Integration Tests (Tours)

Tours simulate real user scenarios in the browser.

### Tour Structure

```
your_module/
├── static/
│   └── tests/
│       └── tours/
│           └── my_tour.js
├── tests/
│   ├── __init__.py
│   └── test_my_tour.py
└── __manifest__.py
```

### Register Tour (JavaScript)

```javascript
import tour from 'web_tour.tour';

tour.register('my_tour', {
    url: '/web',
}, [
    // Step 1: Show apps menu
    tour.stepUtils.showAppsMenuItem(),
    // Step 2: Click on app
    {
        trigger: '.o_app[data-menu-xmlid="my_module.menu_root"]',
        run: "click",
    },
    // Step 3: Fill form
    {
        trigger: 'input[name="name"]',
        run: "text",
    },
    // Step 4: Verify
    {
        trigger: '.o_data_row:first',
        run: function () {
            // Assertions here
        },
    },
]);
```

### Add to Manifest

```python
'assets': {
    'web.assets_tests': [
        'your_module/static/tests/tours/my_tour.js',
    ],
},
```

### Start Tour (Python)

```python
from odoo.tests import HttpCase

class TestMyTour(HttpCase):
    def test_my_tour(self):
        self.start_tour("/web", "my_tour", login="admin")
```

### Tour Step Options

| Option | Description |
|--------|-------------|
| `trigger` | Selector/element to run action on |
| `run` | Action to perform (see helpers below) |
| `isActive` | Array of conditions (mobile, enterprise, auto/manual) |
| `content` | Tooltip content |
| `tooltipPosition` | `top`, `right`, `bottom`, or `left` |
| `timeout` | Wait time in ms (default: 10000) |

### Run Actions

| Action | Description |
|--------|-------------|
| `click` | Clicks the element |
| `dblclick` | Double-clicks the element |
| `drag_and_drop {target}` | Drags to target |
| `edit {content}` | Clears and fills |
| `editor {content}` | WYSIWYG editor fill |
| `fill {content}` | Fills the element |
| `hover` | Hovers over element |
| `press {content}` | Keyboard input |
| `range {content}` | Range slider value |
| `select {value}` | Select by value |
| `selectByIndex {index}` | Select by index |
| `selectByLabel {label}` | Select by label |
| `check` | Checks checkbox |
| `uncheck` | Unchecks checkbox |
| `clear` | Clears input |

### Run Tour from Browser

```javascript
odoo.startTour("tour_name");
```

Or use `?debug=tests` URL parameter.

### Debug Tours

```python
# Watch mode (opens Chrome window)
self.start_tour("/web", "my_tour", watch=True)

# Debug mode (opens devtools)
self.start_tour("/web", "my_tour", debug=True)
```

### Onboarding Tours

Onboarding tours are interactive guides for users.

Create `web_tour.tour` record:

```xml
<record id="my_tour" model="web_tour.tour">
    <field name="name">my_tour</field>
    <field name="sequence">10</field>
    <field name="rainbow_man_message">Great job!</field>
</record>
```

Add to manifest:

```python
'data': [
    'data/my_tour.xml',
],
'assets': {
    'web.assets_backend': [
        'your_module/static/src/js/tours/my_tour.js',
    ],
},
```

---

## Performance Testing

### Query Count Testing

Use `assertQueryCount` to establish query limits:

```python
with self.assertQueryCount(11):
    do_something()
```

### Per-System Limits

```python
with self.assertQueryCount(__system__=1211):
    do_something()
```

---

## Running Tests

Enable tests when starting Odoo:

```bash
# Enable tests
odoo-bin --test-enable

# With specific tags
odoo-bin --test-tags post_install

# Specific module
odoo-bin -i my_module --test-enable

# Update and test
odoo-bin -u my_module --test-enable
```

---

## Screenshot and Screencast

When `HttpCase.browser_js` tests fail:

- Screenshot saved to: `/tmp/odoo_tests/{db_name}/screenshots/`

CLI options:

```bash
odoo-bin --screenshots /tmp/screenshots
odoo-bin --screencasts /tmp/screencasts
```

---

## Special Tags Reference

| Tag | Description |
|-----|-------------|
| `standard` | Default tag for BaseCase subclasses |
| `at_install` | Run after module installation (default) |
| `post_install` | Run after all modules installed |
| `-standard` | Remove from default |
| `-at_install` | Don't run at install (use with `post_install`) |

---

## References

- Source: Odoo 19 documentation `/doc/developer/reference/backend/testing.rst`

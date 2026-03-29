---
name: odoo-18-testing
description: Comprehensive guide for testing Odoo 18 modules, including
  TransactionCase, HttpCase, browser testing, and best practices.
globs: "**/tests/**/*.py"
topics:
  - Test case types (TransactionCase, SavepointCase, HttpCase)
  - Test decorators (tagged, users, warmup)
  - Form testing and fixtures
  - Browser testing (browser_js)
  - Mocking and patching
when_to_use:
  - Writing module tests
  - Adding regression coverage
  - Testing UI flows or JS
  - Mocking external services
---

# Odoo 18 Testing Guide

Comprehensive guide for testing Odoo 18 modules, covering test classes, decorators, mocking, form testing, browser testing, and best practices.

## Table of Contents

1. [Base Test Classes](#base-test-classes)
2. [Test Decorators](#test-decorators)
3. [Mocking and Patching](#mocking-and-patching)
4. [Form Testing](#form-testing)
5. [Browser Testing](#browser-testing)
6. [Setup and Teardown](#setup-and-teardown)
7. [Assert Methods](#assert-methods)
8. [Test Data Helpers](#test-data-helpers)
9. [Running Tests](#running-tests)
10. [Best Practices](#best-practices)

---

## Base Test Classes

### Location

Test infrastructure is located in `/odoo/tests/`:

- `common.py` - Base test classes and utilities
- `case.py` - Core TestCase implementation
- `form.py` - Form testing utility
- `loader.py` - Test loading and discovery
- `tag_selector.py` - Tag-based test filtering

### Class Hierarchy

```
BaseCase (abstract)
├── TransactionCase
│   └── (uses savepoints internally)
├── SingleTransactionCase
└── HttpCase (extends TransactionCase)
```

### TransactionCase

**Purpose**: Each test method runs in a sub-transaction using savepoints. The main transaction is never committed.

**Key Features**:
- Each test method gets its own savepoint
- Data created in `setUpClass()` persists across all test methods
- Each test method rolls back to its savepoint after completion
- Use when you have expensive test data setup common to all tests

```python
from odoo.tests import TransactionCase

class TestMyModel(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # Expensive setup done once for all tests
        cls.product = cls.env['product.product'].create({
            'name': 'Test Product',
            'default_code': 'TEST001',
        })

    def test_01_product_exists(self):
        # Can use cls.product
        self.assertTrue(cls.product)
        self.assertEqual(cls.product.name, 'Test Product')

    def test_02_changes_rolled_back(self):
        # Changes from test_01 are rolled back
        self.product.name = 'Modified'
        self.assertEqual(self.product.name, 'Modified')

    def test_03_original_state(self):
        # Product is in original state
        self.assertEqual(self.product.name, 'Test Product')
```

### SingleTransactionCase

**Purpose**: All test methods run in a single transaction that rolls back at the end.

**Key Features**:
- No savepoints between test methods
- Data persists across all test methods
- Faster than TransactionCase (no savepoint overhead)
- Use for fast tests where data isolation isn't critical

```python
from odoo.tests import SingleTransactionCase

class TestFast(SingleTransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.counter = 0

    def test_01_increment(self):
        self.counter += 1
        self.assertEqual(self.counter, 1)

    def test_02_value_persists(self):
        # self.counter persists from test_01
        self.assertEqual(self.counter, 1)
        self.counter += 1
        self.assertEqual(self.counter, 2)
```

**Warning**: Cannot inherit from both TransactionCase and SingleTransactionCase.

### HttpCase

**Purpose**: For HTTP/browser-based testing with headless Chrome support.

**Key Features**:
- Extends TransactionCase
- Provides `url_open()` for HTTP requests
- Provides `browser_js()` for JavaScript testing
- Provides `start_tour()` for tour testing
- Uses Chrome headless browser via WebSocket
- Session management and authentication helpers

```python
from odoo.tests import HttpCase

class TestMyUI(HttpCase):
    def test_http_request(self):
        """Test HTTP endpoint."""
        response = self.url_open('/my/route')
        self.assertEqual(response.status_code, 200)

    def test_browser_js(self):
        """Test JavaScript code."""
        self.browser_js(
            url_path='/web',
            code="console.log('test successful')",
            ready="odoo.isReady",
            login='admin'
        )

    def test_tour(self):
        """Run Odoo tour."""
        self.start_tour(
            url_path='/web',
            tour_name='my_tour_name',
            step_delay=100,
            login='admin'
        )
```

**Browser Configuration**:

```python
class TestMyHttp(HttpCase):
    browser_size = '1920x1080'  # Default: '1366x768'
    touch_enabled = False        # Enable touch events
    allow_end_on_form = False    # Allow ending on form view
```

---

## Test Decorators

### @tagged

Tag test classes or methods for selective execution.

```python
from odoo.tests import tagged

@tagged('-at_install', 'post_install')
class TestMyFeature(TransactionCase):
    """Tests that run after installation."""
    pass

@tagged('slow', 'external')
class TestExternalAPI(TransactionCase):
    """Tests marked as slow and external."""
    pass
```

**Built-in Tags**:
- `standard` - Default tag for regular tests
- `at_install` - Run during module installation (default)
- `post_install` - Run after installation
- `-at_install` - Exclude from at_install
- `-standard` - Remove standard tag

**Tag Selection Syntax**:

```bash
# Run only post_install tests
python odoo-bin --test-tags=post_install

# Run specific test
python odoo-bin --test-tags=post_install:/my_module:TestMyClass.test_method

# Exclude tests
python odoo-bin --test-tags=-slow

# Multiple tags
python odoo-bin --test-tags=post_install,-standard
```

### @users

Run a test method multiple times with different users.

```python
from odoo.tests import users

class TestAccessRights(TransactionCase):
    @users('admin', 'demo', 'portal')
    def test_with_different_users(self):
        """Test runs 3 times, once for each user."""
        # self.uid is automatically switched
        user = self.env.user
        self.assertIn(user.login, ['admin', 'demo', 'portal'])
```

### @warmup

Stabilize query count assertions by running tests twice.

```python
from odoo.tests import warmup

class TestQueryCount(TransactionCase):
    @warmup
    def test_query_count(self):
        """Test runs twice to stabilize query counts."""
        with self.assertQueryCount(5):
            # Some code
            pass
```

### @no_retry

Disable automatic retry on test failure.

```python
from odoo.tests import no_retry

@no_retry
class TestFlaky(TransactionCase):
    """Disable retry for flaky external tests."""
    pass
```

### @standalone

For tests that install/upgrade/uninstall modules (forbidden in regular tests).

```python
from odoo.tests import standalone

@standalone('module_install', 'upgrade')
def test_install_module(self):
    """Can install/uninstall modules here."""
    module = self.env['ir.module.module'].search([('name', '=', 'my_module')])
    module.button_install()
```

### @freeze_time

Freeze time for testing date/time-dependent code.

```python
from odoo.tests.common import freeze_time

# As class decorator
@freeze_time('2024-01-01 12:00:00')
class TestDates(TransactionCase):
    def test_new_year(self):
        from datetime import datetime
        self.assertEqual(fields.Date.today(), '2024-01-01')

# As method decorator
@freeze_time('2024-01-01')
def test_something(self):
    # Time is frozen
    pass

# As context manager
def test_something(self):
    with freeze_time('2024-01-01'):
        # Time is frozen here
        pass
```

---

## Mocking and Patching

### self.patch()

Patch an object attribute with automatic cleanup.

```python
def test_something(self):
    """Patch method with automatic cleanup."""
    def replacement(self):
        return 'mocked value'

    self.patch(MyModel, 'compute_method', replacement)

    record = self.env['my.model'].create({})
    self.assertEqual(record.compute_method(), 'mocked value')

    # Automatically restored after test
```

### self.classPatch()

Class-level patching with cleanup.

```python
@classmethod
def setUpClass(cls):
    super().setUpClass()

    def mock_method(self):
        return 'mocked'

    cls.classPatch(MyModel, 'method', mock_method)
```

### self.startPatcher()

Start a patcher and return the mock.

```python
from unittest.mock import patch

def test_something(self):
    mock_func = self.startPatcher(patch.object(MyModel, 'method'))

    # Returns the mock object
    mock_func.return_value = 'test'

    record = self.env['my.model'].browse(1)
    result = record.method()

    mock_func.assert_called_once()
    self.assertEqual(result, 'test')
```

### Mocking Examples

**Mock external API**:

```python
from unittest.mock import patch

def test_external_api(self):
    """Mock external API calls."""
    with patch('requests.post') as mock_post:
        mock_post.return_value.status_code = 200
        mock_post.return_value.json.return_value = {'success': True}

        # Code that calls external API
        result = self.env['my.model'].call_external_api()

        mock_post.assert_called_once()
        self.assertTrue(result)
```

**Mock file operations**:

```python
from unittest.mock import mock_open, patch

def test_file_read(self):
    """Mock file reading."""
    with patch('builtins.open', mock_open(read_data='file content')):
        content = self.env['my.model'].read_file('/path/to/file')
        self.assertEqual(content, 'file content')
```

---

## Form Testing

### Basic Form Creation

The `Form` class provides server-side form view simulation with onchange support.

```python
from odoo.tests import Form

# Create mode
with Form(self.env['sale.order']) as f:
    f.partner_id = self.customer
    f.payment_term_id = self.env.ref('account.account_payment_term_15days')
    f.note = 'Test order'

# Automatically saved
order = f.save()
self.assertEqual(order.state, 'draft')

# Edit mode
with Form(order) as f:
    f.note = 'Updated note'

# Automatically saved
self.assertEqual(order.note, 'Updated note')
```

### One2Many Fields

```python
with Form(self.env['sale.order']) as f:
    f.partner_id = self.customer

    # Add new line
    with f.order_line.new() as line:
        line.product_id = self.product
        line.product_uom_qty = 5
        # Onchange is automatically triggered

    # Add another line
    with f.order_line.new() as line:
        line.product_id = self.product2
        line.product_uom_qty = 10

    # Edit existing line (index 0)
    with f.order_line.edit(0) as line:
        line.product_uom_qty = 7

    # Remove line (index 1)
    f.order_line.remove(1)

order = f.save()
self.assertEqual(len(order.order_line), 1)
self.assertEqual(order.order_line[0].product_uom_qty, 7)
```

### Many2Many Fields

```python
# Add/remove/set/clear operations
with Form(user) as f:
    # Add single group
    f.groups_id.add(self.env.ref('account.group_account_manager'))

    # Remove by ID
    f.groups_id.remove(id=self.env.ref('base.group_portal').id)

    # Set multiple groups
    all_groups = self.env['res.groups'].search([])
    f.groups_id.set(all_groups)

    # Clear all
    f.groups_id.clear()
```

### Form Options

```python
# Form with specific view
with Form(self.env['sale.order'], view='sale.order_form') as f:
    pass

# Form with initial values
partner_values = {'name': 'Test Partner'}
with Form(self.env['res.partner'], values=partner_values) as f:
    f.email = 'test@example.com'
```

---

## Browser Testing

### browser_js()

Execute JavaScript in headless Chrome browser.

```python
def test_js_code(self):
    """Test JavaScript code execution."""
    self.browser_js(
        url_path='/web',
        code="""
            console.log('test successful');
            $('body').addClass('test-class');
        """,
        ready="odoo.isReady",
        login='admin',
        timeout=60
    )
```

**Parameters**:
- `url_path` - URL to load
- `code` - JavaScript to execute
- `ready` - JavaScript to wait for before executing code
- `login` - User login (default: None)
- `timeout` - Maximum wait time in seconds (default: 60)
- `cookies` - Dictionary of cookies
- `error_checker` - Function to filter errors
- `watch` - Open visible browser for debugging

### start_tour()

Run Odoo tour (JavaScript tour).

```python
def test_tour(self):
    """Run predefined tour."""
    self.start_tour(
        url_path='/web',
        tour_name='my_tour_name',
        step_delay=100,
        login='admin'
    )
```

### url_open()

Make HTTP requests to the server.

```python
def test_http_request(self):
    """Test HTTP endpoint."""
    # GET request
    response = self.url_open('/my/route')
    self.assertEqual(response.status_code, 200)

    # POST request with data
    response = self.url_open(
        '/my/route',
        data={'key': 'value'},
        method='POST'
    )

    # With authentication
    response = self.url_open(
        '/api/endpoint',
        headers={'Authorization': 'Bearer token'}
    )
```

---

## Setup and Teardown

### setUpClass()

Setup shared test data for all test methods.

```python
@classmethod
def setUpClass(cls):
    super().setUpClass()
    # Create expensive test data once

    cls.partner = cls.env['res.partner'].create({
        'name': 'Test Partner',
        'email': 'test@example.com',
    })

    cls.product = cls.env['product.product'].create({
        'name': 'Test Product',
        'list_price': 100.0,
    })

    cls.warehouse = cls.env.ref('stock.stock_warehouse_main')
```

### setUp()

Setup for each test method.

```python
def setUp(self):
    super().setUp()
    # Setup before each test

    # Register cleanup function
    self.addCleanup(self.cleanup_function)

    # Patch method for this test only
    self.patch(MyModel, 'method', replacement)
```

### tearDown()

Cleanup after each test method.

```python
def tearDown(self):
    # Cleanup after each test
    super().tearDown()
```

### tearDownClass()

Cleanup after all test methods.

```python
@classmethod
def tearDownClass(cls):
    # Cleanup shared resources
    super().tearDownClass()
```

---

## Assert Methods

### assertRecordValues()

Compare recordset with list of dictionaries.

```python
def test_record_values(self):
    partners = self.env['res.partner'].create([
        {'name': 'Partner 1', 'email': 'p1@test.com'},
        {'name': 'Partner 2', 'email': 'p2@test.com'},
    ])

    self.assertRecordValues(
        partners,
        [
            {'name': 'Partner 1', 'email': 'p1@test.com'},
            {'name': 'Partner 2', 'email': 'p2@test.com'},
        ]
    )
```

### assertQueryCount()

Count number of SQL queries executed.

```python
def test_query_count(self):
    """Single user query count."""
    with self.assertQueryCount(5):
        # Code that should execute exactly 5 queries
        partners = self.env['res.partner'].search([])

def test_multi_user_query_count(self):
    """Multi-user query count."""
    with self.assertQueryCount(admin=3, demo=5):
        # admin runs 3 queries, demo runs 5
        pass
```

### assertQueries()

Check exact SQL queries executed.

```python
def test_queries(self):
    with self.assertQueries([
        'SELECT.*FROM res_partner',
        'SELECT.*FROM product_product',
    ]):
        # Code that executes these specific queries
        pass
```

### assertXMLEqual() / assertHTMLEqual()

Compare XML/HTML strings.

```python
def test_xml(self):
    xml1 = '<root><child>text</child></root>'
    xml2 = '<root><child>text</child></root>'
    self.assertXMLEqual(xml1, xml2)
```

### assertURLEqual()

Compare URLs, handling missing scheme/host.

```python
def test_url(self):
    url1 = '/web?action=1'
    url2 = 'http://localhost:8069/web?action=1'
    self.assertURLEqual(url1, url2)
```

### assertTreesEqual()

Compare XML/HTML trees.

```python
def test_tree(self):
    tree1 = etree.fromstring('<root><child>text</child></root>')
    tree2 = etree.fromstring('<root><child>text</child></root>')
    self.assertTreesEqual(tree1, tree2)
```

---

## Test Data Helpers

### new_test_user()

Helper to create test users with proper defaults.

```python
from odoo.tests.common import new_test_user

def test_with_user(self):
    """Create test user with groups."""
    user = new_test_user(
        self.env,
        login='testuser',
        groups='base.group_user,base.group_portal',
        company_id=self.main_company.id,
        name='Test User'
    )

    # Test with user
    records = self.env['my.model'].sudo(user).search([])
```

### RecordCapturer

Capture records created during a test.

```python
from odoo.tests.common import RecordCapturer

def test_capture_records(self):
    """Capture records matching domain."""
    with RecordCapturer(
        self.env['res.partner'],
        [('name', '=', 'test')]
    ) as capturer:
        # Create partners
        self.env['res.partner'].create({'name': 'test'})
        self.env['res.partner'].create({'name': 'test2'})
        self.env['res.partner'].create({'name': 'other'})

    # Only 'test' partner captured
    self.assertEqual(len(capturer.records), 1)
```

---

## Running Tests

### Command-Line Options

```bash
# Run all tests
python odoo-bin -d test_db --test-enable

# Run specific module
python odoo-bin -d test_db --test-enable --test-tags=my_module

# Run post_install tests only
python odoo-bin -d test_db --test-enable --test-tags=post_install

# Run specific test
python odoo-bin -d test_db --test-enable --test-tags=post_install/my_module:TestClass.test_method

# Exclude tests
python odoo-bin -d test_db --test-enable --test-tags=-slow

# Stop after N failures
export ODOO_TEST_MAX_FAILED_TESTS=5

# Enable logging
python odoo-bin --log-level=debug --test-enable
```

### Test Tags Selector

```bash
# Include specific tag
--test-tags=post_install

# Exclude tag
--test-tags=-slow

# Specific module
--test-tags=post_install/my_module

# Specific class
--test-tags=post_install/my_module:TestClass

# Specific method
--test-tags=post_install/my_module:TestClass.test_method

# Multiple filters
--test-tags=post_install,-slow

# Complex filtering
--test-tags='post_install and not slow'
```

### Testing Individual Modules

```bash
# Test specific addon
python odoo-bin -d test_db --test-enable --init=my_module

# Test after update
python odoo-bin -d test_db --test-enable --update=my_module

# Test multiple modules
python odoo-bin -d test_db --test-enable --init=my_module,other_module
```

---

## Best Practices

### 1. Use Appropriate Test Case

```python
# Use TransactionCase for most tests
class TestFeature(TransactionCase):
    """Tests with isolated data per method."""
    pass

# Use HttpCase for browser/JS testing
class TestUI(HttpCase):
    """Tests for UI components."""
    pass

# Use SingleTransactionCase for fast, non-isolated tests
class TestFast(SingleTransactionCase):
    """Fast tests without data isolation."""
    pass
```

### 2. Tag Tests Properly

```python
# Browser tests should be post_install
@tagged('-at_install', 'post_install')
class TestUI(HttpCase):
    pass

# Mark slow tests
@tagged('slow')
class TestHeavyComputation(TransactionCase):
    pass

# Mark external API tests
@tagged('external', 'slow')
class TestExternalAPI(TransactionCase):
    pass
```

### 3. Use Context Managers for Cleanup

```python
def test_something(self):
    """Automatic cleanup with context manager."""
    with self.patch(Model, 'method', replacement):
        # Test code
        pass
    # Automatically cleaned up
```

### 4. Use Form for UI-like Testing

```python
def test_create_record(self):
    """Test with form simulation."""
    with Form(self.env['sale.order']) as f:
        f.partner_id = self.partner
        with f.order_line.new() as line:
            line.product_id = self.product

    # Automatically saved and onchange triggered
    order = f.save()
    self.assertTrue(order.order_line)
```

### 5. Test with Multiple Users

```python
@users('admin', 'portal')
def test_access_rights(self):
    """Test runs for both users."""
    records = self.env['my.model'].search([])
    # Test with different access rights
```

### 6. Use subTest for Multiple Cases

```python
def test_multiple_cases(self):
    """Test multiple scenarios with subTest."""
    for value, expected in [(1, 2), (2, 4), (3, 6)]:
        with self.subTest(value=value):
            self.assertEqual(value * 2, expected)
```

### 7. Use addCleanup for Resources

```python
def test_with_resource(self):
    """Automatic cleanup with addCleanup."""
    import tempfile
    import os

    temp_file = tempfile.mktemp()
    self.addCleanup(os.remove, temp_file)

    # Use temp_file
    with open(temp_file, 'w') as f:
        f.write('test')
```

### 8. Mock External Dependencies

```python
def test_external_api(self):
    """Mock external API calls."""
    with patch('requests.post') as mock_post:
        mock_post.return_value.status_code = 200
        mock_post.return_value.json.return_value = {'success': True}

        # Test code that calls external API
        result = self.env['my.model'].call_external_api()

        mock_post.assert_called_once()
        self.assertTrue(result)
```

### 9. setUpClass for Expensive Setup

```python
@classmethod
def setUpClass(cls):
    super().setUpClass()
    # Create expensive test data once

    cls.warehouse = cls.env.ref('stock.stock_warehouse_main')
    cls.location = cls.warehouse.lot_stock_id

    # Create many records at once
    cls.products = cls.env['product.product'].create([
        {'name': f'Product {i}'} for i in range(100)
    ])
```

### 10. Use freeze_time for Date-Dependent Tests

```python
@freeze_time('2024-01-01')
def test_year_end(self):
    """Test with frozen time."""
    from datetime import date
    self.assertEqual(fields.Date.today(), date(2024, 1, 1))
```

### 11. Test Error Cases

```python
def test_validation_error(self):
    """Test that validation errors are raised."""
    with self.assertRaises(ValidationError):
        self.env['res.partner'].create({'name': None})

def test_access_error(self):
    """Test that access errors are raised."""
    user = new_test_user(self.env, login='test')
    with self.assertRaises(AccessError):
        self.env['mail.channel'].sudo(user).search([])
```

### 12. Test Onchange Behavior

```python
def test_onchange(self):
    """Test onchange behavior with Form."""
    partner = self.env['res.partner'].create({'name': 'Test'})

    with Form(self.env['sale.order']) as f:
        f.partner_id = partner
        # Onchange automatically triggered
        self.assertEqual(f.payment_term_id, partner.property_payment_term_id)
```

---

## Additional Resources

### Key Files Reference

| File Path | Purpose |
|-----------|---------|
| `/odoo/tests/common.py` | Base test classes and utilities |
| `/odoo/tests/form.py` | Form testing utility |
| `/odoo/tests/case.py` | Core TestCase implementation |
| `/odoo/tests/loader.py` | Test loading and discovery |
| `/odoo/tests/tag_selector.py` | Tag-based test filtering |
| `/addons/base/tests/common.py` | Base module test helpers |

### Quick Test Template

```python
from odoo.tests import TransactionCase, tagged

@tagged('-at_install', 'post_install')
class TestMyModel(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.record = cls.env['my.model'].create({
            'name': 'Test',
        })

    def test_01_basic(self):
        """Test basic functionality."""
        self.assertEqual(self.record.name, 'Test')

    def test_02_method(self):
        """Test method behavior."""
        result = self.record.my_method()
        self.assertTrue(result)
```

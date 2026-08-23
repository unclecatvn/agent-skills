---
name: odoo-16-testing
description: Comprehensive guide for testing Odoo 16 modules - TransactionCase, SingleTransactionCase, HttpCase, ChromeBrowser tour tests, @tagged, @users, @mute_logger, @warmup, @standalone, @no_retry, mocking (self.patch / self.classPatch / self.startPatcher), assertQueryCount, form helpers (odoo.tests.common.Form, O2MProxy, M2MProxy) and running specific test tags.
globs: "**/tests/**/*.py"
topics:
  - Test case types (TransactionCase, SingleTransactionCase, HttpCase)
  - Test decorators (tagged, users, warmup, mute_logger, no_retry, standalone)
  - Form testing (Form, O2MProxy, M2MProxy)
  - Browser testing via ChromeBrowser and tours
  - Mocking and patching
  - Query-count assertions
  - Tag selector syntax
when_to_use:
  - Writing module tests
  - Adding regression coverage
  - Testing UI flows or JS via tours
  - Mocking external services
  - Asserting query counts to catch N+1 regressions
---

# Odoo 16 Testing Guide

Comprehensive guide to testing Odoo 16 modules: base test classes, decorators, mocking, form helpers, browser testing and best practices.

## Table of Contents

1. [Base Test Classes](#base-test-classes)
2. [Test Decorators](#test-decorators)
3. [Mocking and Patching](#mocking-and-patching)
4. [Form Testing](#form-testing)
5. [Browser Testing](#browser-testing)
6. [Setup and Teardown](#setup-and-teardown)
7. [Assert Helpers](#assert-helpers)
8. [Test Data Helpers](#test-data-helpers)
9. [Running Tests](#running-tests)
10. [Best Practices](#best-practices)

---

## Base Test Classes

### Location

Test infrastructure for Odoo 16 lives in `odoo/tests/`:

| File | Contents |
|------|----------|
| `common.py` | Base classes (`BaseCase`, `TransactionCase`, `SingleTransactionCase`, `HttpCase`, `ChromeBrowser`), decorators (`tagged`, `users`, `warmup`, `no_retry`, `standalone`) and helpers (`new_test_user`, `RecordCapturer`, `mute_logger`) |
| `form.py` | `Form`, `O2MProxy`, `M2MProxy` - server-side form view simulation |
| `case.py` | Lower-level `TestCase` |
| `loader.py` | Test discovery |
| `tag_selector.py` | `--test-tags` parser |

`from odoo.tests import ...` re-exports everything from `odoo.tests.common` plus `Form`, `O2MProxy`, `M2MProxy` from `odoo.tests.form`.

### Class Hierarchy

```
BaseCase
  TransactionCase           (savepoint per test method)
    HttpCase                (adds HTTP + ChromeBrowser)
  SingleTransactionCase     (one transaction for the whole class)
```

### TransactionCase

Each test method runs in its own **savepoint** on top of a class-wide transaction; nothing is committed and the savepoint is rolled back after each method. Use this for almost every test.

```python
from odoo.tests.common import TransactionCase, tagged


@tagged('post_install', '-at_install')
class TestBusinessTrip(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.partner = cls.env['res.partner'].create({'name': 'Alice'})
        cls.trip = cls.env['business.trip'].create({
            'name': 'Kickoff',
            'partner_id': cls.partner.id,
        })

    def test_01_default_state(self):
        self.assertEqual(self.trip.state, 'draft')

    def test_02_confirm(self):
        self.trip.action_confirm()
        self.assertEqual(self.trip.state, 'confirmed')

    def test_03_isolated(self):
        # The write from test_02 has been rolled back
        self.assertEqual(self.trip.state, 'draft')
```

Key points:

- Data created in `setUpClass` is visible to every test but is rolled back at class teardown.
- Mutations inside `test_X` are rolled back at the end of `test_X`.
- `cls.env` is created in `setUpClass` and is the environment of the class-wide cursor.

### SingleTransactionCase

All tests in the class share the same transaction, which is rolled back at class teardown only. Tests see each other's writes, so ordering matters.

```python
from odoo.tests.common import SingleTransactionCase


class TestStatefulFlow(SingleTransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.order = cls.env['sale.order'].create({'partner_id': cls.env.ref('base.res_partner_1').id})

    def test_01_confirm(self):
        self.order.action_confirm()
        self.assertEqual(self.order.state, 'sale')

    def test_02_invoice(self):
        # test_01's change is still visible
        self.assertEqual(self.order.state, 'sale')
```

Use when:

- You want to reuse heavy state between tests (integration-style).
- The savepoint overhead matters.

### HttpCase

Extends `TransactionCase` with HTTP access (`url_open`, `authenticate`) and a headless Chrome driver (`browser_js`, `start_tour`). Typically paired with `@tagged('post_install', '-at_install')` so the database is fully set up.

```python
from odoo.tests.common import HttpCase, tagged


@tagged('post_install', '-at_install')
class TestUI(HttpCase):
    def test_homepage(self):
        r = self.url_open('/web/login')
        self.assertEqual(r.status_code, 200)

    def test_admin_tour(self):
        self.start_tour('/web', 'my_module_tour', login='admin')
```

Class attributes that can be tweaked:

| Attribute | Default | Description |
|-----------|---------|-------------|
| `browser_size` | `'1366x768'` | Window size |
| `touch_enabled` | `False` | Emulate touch events |
| `allow_inherited_tests_method` | `False` | Allow running tests defined on a base class |

### ChromeBrowser

`HttpCase` lazily spins up a `ChromeBrowser` instance for `browser_js` / `start_tour`. It connects over the Chrome DevTools Protocol, captures console logs / errors, and fails the test on any `error:` message matching the internal filters. You rarely use it directly - prefer `start_tour`.

---

## Test Decorators

### `@tagged`

Tag classes (and, since the decorator is class-level, indirectly their test methods) for selective execution. Default tags on test classes are `'standard'` and `'at_install'`. Prefix with `-` to remove a tag.

```python
from odoo.tests.common import tagged, TransactionCase


@tagged('post_install', '-at_install')
class TestAfterInstall(TransactionCase):
    ...


@tagged('-standard', 'nightly')
class TestNightly(TransactionCase):
    """Run only when --test-tags=nightly is passed."""
    ...


@tagged('my_module', 'my_tag')
class TestCustom(TransactionCase):
    ...
```

Common built-in tags:

| Tag | Meaning |
|-----|---------|
| `standard` | Default - included unless excluded |
| `at_install` | Run during module install |
| `post_install` | Run after install (use for HttpCase) |
| `-at_install` | Remove default `at_install` |
| `-standard` | Skip unless explicitly asked |

### `@users`

Run a test method once for each listed login. Login must exist. Inside the test, `self.env.user` and `self.uid` reflect the current user.

```python
from odoo.tests.common import users, TransactionCase


class TestAccess(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env['res.users'].create({
            'name': 'Alice', 'login': 'alice', 'password': 'alicexxx',
            'groups_id': [(6, 0, [cls.env.ref('base.group_user').id])],
        })

    @users('admin', 'alice')
    def test_can_read(self):
        self.assertTrue(self.env['business.trip'].search([]))
```

### `@warmup`

Run the test **twice** - once to warm caches (results rolled back via savepoint), once for real. `self.warm` is `False` during warm-up and `True` during the real run. Use with `assertQueryCount` to get stable counts.

```python
from odoo.tests.common import warmup, TransactionCase


class TestPerf(TransactionCase):
    @warmup
    def test_read_list(self):
        with self.assertQueryCount(5):
            self.env['business.trip'].search([]).mapped('name')
```

### `@mute_logger`

Silence noisy loggers during a test (used as decorator or context manager).

```python
from odoo.tools import mute_logger


class TestThings(TransactionCase):
    @mute_logger('odoo.sql_db', 'odoo.addons.mail.models.mail_mail')
    def test_creates_mail(self):
        ...
```

### `@no_retry`

Turn off the retry-on-serialization-failure wrapper (useful for tests that should fail deterministically).

```python
from odoo.tests.common import no_retry


@no_retry
class TestDeterministic(TransactionCase):
    ...
```

### `@standalone`

Mark a free function as a standalone test that can install / uninstall / upgrade modules (forbidden inside `TransactionCase`). Runs outside the normal test cycle.

```python
from odoo.tests.common import standalone


@standalone('module_install')
def test_install(env):
    module = env['ir.module.module'].search([('name', '=', 'my_module')])
    module.button_immediate_install()
```

### `freeze_time`

Odoo 16 does **not** ship its own `freeze_time` in `odoo.tests.common`. Use the external `freezegun` package directly:

```python
from datetime import datetime
from freezegun import freeze_time
from odoo.tests import TransactionCase

class TestSomething(TransactionCase):
    @freeze_time("2024-01-01 10:10:10")
    def test_creation_time(self):
        partner = self.env["res.partner"].create({"name": "Foo"})
        self.assertEqual(partner.create_date, datetime(2024, 1, 1, 10, 10, 10))
```

---

## Mocking and Patching

`BaseCase` exposes three helpers that register automatic cleanup with `addCleanup` / `addClassCleanup`, so patches are always unwound.

### `self.patch(obj, attr, value)`

```python
def test_patch_method(self):
    def replacement(self):
        return 'mocked'

    self.patch(type(self.env['business.trip']), 'compute_amount', replacement)
    self.assertEqual(self.env['business.trip'].compute_amount(), 'mocked')
```

### `cls.classPatch(obj, attr, value)`

Patch that lives for the whole class.

```python
@classmethod
def setUpClass(cls):
    super().setUpClass()

    def always_ok(self):
        return True

    cls.classPatch(type(cls.env['business.trip']), '_validate', always_ok)
```

### `self.startPatcher(patcher)`

Wrap any `unittest.mock._patch` and register its cleanup.

```python
from unittest.mock import patch


def test_external_call(self):
    mock_post = self.startPatcher(patch('requests.post'))
    mock_post.return_value.status_code = 200
    mock_post.return_value.json.return_value = {'ok': True}

    result = self.env['my.model'].call_external()

    mock_post.assert_called_once()
    self.assertTrue(result)
```

### Common Mocking Patterns

```python
from unittest.mock import patch, mock_open


# Mock an HTTP client
def test_api(self):
    with patch('requests.get') as mock_get:
        mock_get.return_value.json.return_value = {'value': 42}
        result = self.env['my.model'].fetch_value()
        self.assertEqual(result, 42)


# Mock file reads
def test_read_config(self):
    with patch('builtins.open', mock_open(read_data='KEY=VALUE')):
        data = self.env['my.model']._read_config('/etc/nope')
        self.assertEqual(data, {'KEY': 'VALUE'})
```

---

## Form Testing

`odoo.tests.common.Form` (re-exported from `odoo.tests.form`) simulates the client-side form view entirely server-side: onchange methods are triggered, defaults are applied, modifiers are evaluated, and x2many proxies manage inline editing.

### Create Mode

```python
from odoo.tests.common import Form


def test_create_via_form(self):
    with Form(self.env['business.trip']) as f:
        f.name = 'Berlin Workshop'
        f.partner_id = self.partner
    # f is saved on __exit__
    trip = f.record
    self.assertEqual(trip.name, 'Berlin Workshop')
```

### Edit Mode

```python
def test_edit_via_form(self):
    with Form(self.trip) as f:
        f.name = 'Updated'
    self.assertEqual(self.trip.name, 'Updated')
```

### One2many with `O2MProxy`

```python
def test_one2many(self):
    with Form(self.env['business.trip']) as f:
        f.name = 'Trip A'

        with f.expense_ids.new() as line:
            line.description = 'Taxi'
            line.amount = 25.0

        with f.expense_ids.new() as line:
            line.description = 'Hotel'
            line.amount = 250.0

        # Edit first line
        with f.expense_ids.edit(0) as line:
            line.amount = 30.0

        # Remove second line
        f.expense_ids.remove(1)

    trip = f.record
    self.assertEqual(len(trip.expense_ids), 1)
    self.assertEqual(trip.expense_ids.amount, 30.0)
```

### Many2many with `M2MProxy`

```python
with Form(user) as f:
    f.groups_id.add(self.env.ref('base.group_user'))
    f.groups_id.remove(id=self.env.ref('base.group_portal').id)
    f.groups_id.set(self.env['res.groups'].search([], limit=3))
    f.groups_id.clear()
```

### Selecting a Specific View

```python
with Form(self.env['sale.order'], view='sale.view_order_form') as f:
    ...
```

### Saving and Re-Opening

```python
f = Form(self.env['business.trip'])
f.name = 'Trip'
record = f.save()  # explicit save, returns the recordset

# Re-open in edit mode later
with Form(record) as f2:
    f2.note = 'See you there'
```

---

## Browser Testing

### `url_open(path, data=None, method=None, timeout=None, headers=None, allow_redirects=True)`

Issue an HTTP request to the running test server.

```python
def test_controller(self):
    r = self.url_open('/my_module/api/ping')
    self.assertEqual(r.status_code, 200)

    r = self.url_open('/my_module/submit', data={'name': 'Bob'}, method='POST')
    self.assertIn('thanks', r.text.lower())
```

### `authenticate(user, password)`

Log in through the HTTP session (uses `requests.Session` under the hood).

```python
def test_as_admin(self):
    self.authenticate('admin', 'admin')
    r = self.url_open('/web/session/get_session_info')
    self.assertEqual(r.status_code, 200)
```

### `browser_js(url_path, code, ready="", login=None, timeout=60, ...)`

Execute arbitrary JavaScript in headless Chrome. The test succeeds when `code` resolves, fails on any unhandled console error.

```python
def test_some_js(self):
    self.browser_js(
        url_path='/web',
        code="console.log('ok');",
        ready="odoo.isReady",
        login='admin',
    )
```

### `start_tour(url_path, tour_name, step_delay=None, login=None, timeout=60, ...)`

Run a JS tour defined in a module's `static/tests/tours/*.js`. Typical ergonomic wrapper.

```python
def test_checkout_tour(self):
    self.start_tour('/shop', 'checkout_tour', login='demo')
```

Tours test files live under `static/tests/tours/`, registered in a QWeb assets bundle (usually `web.assets_tests`).

---

## Setup and Teardown

### `setUpClass(cls)`

Runs once before any test method. Use it to build shared fixtures with `cls.env`.

```python
@classmethod
def setUpClass(cls):
    super().setUpClass()
    cls.manager = cls.env['res.users'].create({
        'name': 'Manager', 'login': 'mgr', 'password': 'mgrxxxxx',
        'groups_id': [(6, 0, [cls.env.ref('base.group_user').id])],
    })
    cls.trip = cls.env['business.trip'].create({'name': 'Demo'})
```

### `setUp(self)`

Runs before each test method. Register cleanup with `self.addCleanup`.

```python
def setUp(self):
    super().setUp()
    self.addCleanup(self._cleanup_files)
```

### `tearDown(self)` / `tearDownClass(cls)`

Usually not needed - `setUpClass` / `setUp` plus `addClassCleanup` / `addCleanup` cover most cases. If you override, call `super()`.

### `addCleanup(callable, *args)` and `addClassCleanup(callable, *args)`

Register a function to run on teardown, regardless of test outcome.

```python
temp = tempfile.mkdtemp()
self.addCleanup(shutil.rmtree, temp)
```

---

## Assert Helpers

### `assertQueryCount(default=0, **counters)`

Context manager that asserts the number of SQL queries executed. Use with `@warmup` to stabilise.

```python
@warmup
def test_read_cost(self):
    trips = self.env['business.trip'].search([])
    with self.assertQueryCount(3):
        trips.mapped('partner_id.name')
```

Multi-user form (paired with `@users`):

```python
@users('admin', 'demo')
@warmup
def test_multi_user_cost(self):
    with self.assertQueryCount(admin=4, demo=6):
        self.env['business.trip'].search([]).read(['name', 'state'])
```

The context manager logs a message when the real count is **lower** than expected (so you can tighten the assertion), and fails when it is **higher**.

### `assertQueries(expected_queries, flush=True)`

Assert that the exact sequence of queries was executed (partial string match per query).

```python
def test_order_of_queries(self):
    with self.assertQueries([
        'SELECT.*FROM business_trip',
        'SELECT.*FROM res_partner',
    ]):
        self.env['business.trip'].search([]).mapped('partner_id.name')
```

### `assertRecordValues(records, expected)`

Compare a recordset to a list of expected dicts (index-based).

```python
self.assertRecordValues(trips, [
    {'name': 'Trip A', 'state': 'draft'},
    {'name': 'Trip B', 'state': 'confirmed'},
])
```

### `assertXMLEqual` / `assertHTMLEqual`

Normalise whitespace/attribute order before comparison.

### `assertTreesEqual(tree1, tree2)`

Compare two `lxml` trees.

### `assertURLEqual(url1, url2)`

Tolerate missing scheme/host when comparing URLs.

---

## Test Data Helpers

### `new_test_user(env, login, groups='base.group_user', context=None, **kwargs)`

Create a user with sensible defaults (`name`, `email`, `password=login+'x'*N`) and the listed groups (comma-separated XML IDs).

```python
from odoo.tests.common import new_test_user


@classmethod
def setUpClass(cls):
    super().setUpClass()
    cls.trip_mgr = new_test_user(
        cls.env, login='trip_mgr',
        groups='base.group_user,my_module.group_trip_manager',
        name='Trip Manager',
    )
```

### `RecordCapturer(model, domain)`

Capture records created (matching the domain) inside a block.

```python
from odoo.tests.common import RecordCapturer


def test_capture(self):
    with RecordCapturer(self.env['business.trip'], [('name', 'like', 'Auto-%')]) as cap:
        self.env['business.trip'].create({'name': 'Auto-1'})
        self.env['business.trip'].create({'name': 'Manual'})
    self.assertEqual(len(cap.records), 1)
```

### `loaded_demo_data(env)`

Returns `True` if demo data was loaded - use it to skip tests that rely on demo records.

```python
from odoo.tests.common import loaded_demo_data


def test_needs_demo(self):
    if not loaded_demo_data(self.env):
        self.skipTest("Demo data not loaded")
    ...
```

---

## Running Tests

### Basic Commands

```bash
# Install the module and run its at_install tests
odoo-bin -d test_db -i my_module --test-enable --stop-after-init

# Update and re-run tests
odoo-bin -d test_db -u my_module --test-enable --stop-after-init

# Run only post_install tests of my_module
odoo-bin -d test_db --test-enable --test-tags=post_install -u my_module --stop-after-init
```

### `--test-tags` Syntax

The selector supports `+include / -exclude` tokens separated by commas. Empty inclusion means *"everything tagged `standard`"*.

```bash
# Include a specific tag
--test-tags=post_install

# Exclude a tag
--test-tags=-slow

# Narrow to a module
--test-tags=/my_module

# Narrow to a class
--test-tags=/my_module:TestBusinessTrip

# Narrow to a method
--test-tags=/my_module:TestBusinessTrip.test_02_confirm

# Multiple filters
--test-tags=post_install,-slow

# Run only tests tagged `my_tag` (and exclude the standard default)
--test-tags=-standard,my_tag
```

### Tips

- HttpCase tests need the HTTP layer and module setup; tag them `post_install` so they run after module installation. Create any required test data explicitly.
- `--log-level=test` shows each test class and method as it runs.
- Set `--log-handler=odoo.tests.common:DEBUG` to see query counts and browser events.
- A test that modifies the registry must restore it (`self.registry.reset_changes()` / `addCleanup`).

---

## Best Practices

### 1. Inherit `TransactionCase` by default

Use `SingleTransactionCase` only when you really need shared mutable state, and `HttpCase` only for HTTP/browser tests.

### 2. Always tag HttpCase

```python
@tagged('post_install', '-at_install')
class TestUI(HttpCase):
    ...
```

### 3. Keep `setUpClass` fast and deterministic

Create the minimum fixtures there; tests should create the data they need instead of relying on demo data.

### 4. Use `Form` to exercise real UI flow

Onchange, defaults, and modifiers are tested for free - this catches bugs that a raw `create()` misses.

### 5. Pair `assertQueryCount` with `@warmup`

Counts are unstable on cold caches. A warmup run flushes + invalidates, so the second run reflects the steady-state cost.

### 6. Prefer `self.patch` / `self.startPatcher` over manual `patch().start()`

They auto-unwind on cleanup and survive early test failures.

### 7. Gate external integrations behind a tag

```python
@tagged('-standard', 'external')
class TestPaymentGateway(TransactionCase):
    ...
```

Run only on CI with `--test-tags=external`.

### 8. Test Error Paths

```python
from odoo.exceptions import AccessError, ValidationError


def test_access(self):
    with self.assertRaises(AccessError):
        self.env['business.trip'].with_user(self.portal_user).search([])


def test_validation(self):
    with self.assertRaises(ValidationError):
        self.env['business.trip'].create({'name': False})
```

### 9. Use subtests without sharing mutable state

```python
def test_cases(self):
    for raw, expected in [('42', 42), (' 42 ', 42), ('0', 0)]:
        with self.subTest(raw=raw):
            self.assertEqual(self.env['my.model']._parse_int(raw), expected)
```

Database changes are not rolled back between subtests. Use unique fixtures or explicitly reset the state for each case, and do not carry records or cached values from one case into another.

### 10. Add regression tests for fixes

Every reproducible bug fix should include a test that fails before the fix and passes afterward. New behavior should cover its success path and important error paths.

### 11. Test with the lowest practical permissions

Use `new_test_user()` and `@users` to exercise access-sensitive flows as the least privileged user that should be allowed to perform them. This avoids false positives from tests that run as an administrator.

### 12. Keep records aligned with the active environment

Records stored on a class or test instance retain their original `.env` (including user, context, cursor, and sudo state). After changing the test environment, use `record.with_env(self.env)` before asserting access behavior.

### 13. Freeze time-dependent behavior

Use fixed dates instead of `datetime.now()` or `datetime.today()` in assertions. See the canonical `freeze_time` example above.

### 14. Mock external services by default

Use `self.patch()`, `self.classPatch()`, or `self.startPatcher()` to isolate network and other external services. If a live integration test is necessary, keep it out of the standard test selection with an explicit test tag such as `external`.

### 15. Treat coverage drops as a test signal

When coverage decreases after a change, inspect the uncovered paths and add tests where the behavior is meaningful rather than lowering the expectation.

### 16. Minimal Template

```python
from odoo.tests.common import TransactionCase, tagged


@tagged('post_install', '-at_install')
class TestBusinessTrip(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.partner = cls.env['res.partner'].create({'name': 'Alice'})
        cls.trip = cls.env['business.trip'].create({
            'name': 'Demo', 'partner_id': cls.partner.id,
        })

    def test_01_confirm(self):
        self.trip.action_confirm()
        self.assertEqual(self.trip.state, 'confirmed')

    def test_02_cancel_requires_manager(self):
        from odoo.exceptions import AccessError
        with self.assertRaises(AccessError):
            self.trip.with_user(self.env.ref('base.user_demo')).action_cancel()
```

---

## Base Code Reference

The guide is based on the Odoo 16 source tree. Reference files:

| File | Contents |
|------|----------|
| `odoo/tests/__init__.py` | Re-exports `TransactionCase`, `SingleTransactionCase`, `HttpCase`, `Form`, decorators |
| `odoo/tests/common.py` | `BaseCase`, `TransactionCase`, `SingleTransactionCase`, `HttpCase`, `ChromeBrowser`, decorators `tagged` / `users` / `warmup` / `no_retry` / `standalone`, helpers `new_test_user`, `RecordCapturer`, `mute_logger` |
| `odoo/tests/form.py` | `Form`, `O2MProxy`, `M2MProxy` |
| `odoo/tests/case.py` | Low-level `TestCase` |
| `odoo/tests/loader.py` | Test discovery |
| `odoo/tests/tag_selector.py` | `--test-tags` parser |

**For more Odoo 16 guides, see [SKILL.md](../SKILL.md)**

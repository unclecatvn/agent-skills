# HOOT

## What HOOT Provides

HOOT is Odoo's frontend test framework. It provides:

- `describe`, `test`, and `expect`
- lifecycle hooks such as `after` and `afterEach`
- DOM helpers via `@odoo/hoot-dom`
- utilities for time and network mocking

## Typical Imports

```js
/** @odoo-module **/

import { describe, expect, test } from "@odoo/hoot";
```

## Use It For

- small component behavior checks
- service or hook behavior under controlled conditions
- async interaction assertions
- tests that should run inside Odoo's `/web/tests` runner

## Rule of Thumb

Use HOOT as the framework, then reach for `@web/../tests/web_test_helpers` for realistic component mounting and Odoo-specific runtime setup.

---
name: odoo-code-review
description: Review Odoo code for correctness, security, performance, and version-specific standards (Odoo 16, 17, 18, or 19). Use when reviewing Odoo modules, diffs, or pull requests; produce a scored report with weighted criteria.
---

# Odoo Code Review

## Objective

Review Odoo code changes against clear criteria, identify risks, and score using a weighted scale from an Odoo-expert perspective — using the reference pack that matches the target Odoo version.

## Resolve the target Odoo version

Before reviewing, resolve `ODOO_VERSION` (one of `16.0`, `17.0`, `18.0`, `19.0`) in this order. Stop at the first one that succeeds:

1. **Explicit argument** passed to the agent invocation (e.g. `odoo_version: "19.0"`).
2. **Project config**, in this order:
   - `.odoo-version` file at the repo root (contents: e.g. `19.0`).
   - `odoo_version` key in `.claude/odoo.json`.
   - `odoo.version` key in `package.json` or `tool.odoo.version` in `pyproject.toml`.
3. **Manifest heuristic** — scan workspace `__manifest__.py` files for the `'version'` key. Use the dominant major version (e.g. `18.0.1.0.0` → `18.0`).
4. **Fallback** — default to `19.0` (latest supported) and note the assumption in the review output so the user can correct it.

Derive `ODOO_MAJOR` from `ODOO_VERSION` by stripping `.0` (e.g. `18.0` → `18`). All guide paths below use these placeholders.

Supported versions: **16.0, 17.0, 18.0, 19.0**. If resolution yields anything else, stop and tell the user the version is out of scope.

## Pre-review Requirements

- Read `skills/odoo-${ODOO_VERSION}/SKILL.md` as the master index for the resolved version's guides.
- Read `skills/odoo-${ODOO_VERSION}/references/api-highlights.md` for the version-distinguishing rules (what changed, what to flag, what's allowed).
- Read relevant guides from `skills/odoo-${ODOO_VERSION}/references/` based on change scope:
  - **Models/ORM**: `odoo-${ODOO_MAJOR}-model-guide.md`
  - **Fields**: `odoo-${ODOO_MAJOR}-field-guide.md`
  - **Decorators**: `odoo-${ODOO_MAJOR}-decorator-guide.md`
  - **Performance**: `odoo-${ODOO_MAJOR}-performance-guide.md`
  - **Views/XML**: `odoo-${ODOO_MAJOR}-view-guide.md`
  - **Security**: `odoo-${ODOO_MAJOR}-security-guide.md`
  - **Controllers**: `odoo-${ODOO_MAJOR}-controller-guide.md`
  - **Transactions**: `odoo-${ODOO_MAJOR}-transaction-guide.md`
  - **Mixins**: `odoo-${ODOO_MAJOR}-mixins-guide.md` (mail.thread, activities)
  - **Testing**: `odoo-${ODOO_MAJOR}-testing-guide.md`
  - **Migration**: `odoo-${ODOO_MAJOR}-migration-guide.md`
  - **Actions**: `odoo-${ODOO_MAJOR}-actions-guide.md`
  - **Data Files**: `odoo-${ODOO_MAJOR}-data-guide.md`
  - **Manifest**: `odoo-${ODOO_MAJOR}-manifest-guide.md`
- Identify scope: module, file, and change context.
- Apply the version-distinguishing rules from `api-highlights.md` (e.g. `<tree>` vs `<list>`, `group_operator=` vs `aggregator=`, optional `_name` in v19, etc.).

## Expert Review Process

1. **Scope**: Identify change scope, objectives, and key risks
2. **ORM & Model Methods**: Search patterns, CRUD operations, recordset operations
3. **Field Definitions**: Field types, computed fields, relational field parameters
4. **API Decorators**: `@api.depends`, `@api.constrains`, `@api.ondelete`, `@api.model_create_multi`
5. **Performance**: N+1 detection, batch operations, field selection
6. **Transaction Management**: Savepoints, `UniqueViolation`, serialization
7. **Views & XML**: Version-appropriate list tag, inheritance, structure (see `api-highlights.md`)
8. **Security**: ACL, record rules, exceptions, `sudo()` usage
9. **Controllers**: Auth types, CSRF protection, routing
10. **Mixins**: `mail.thread`, `mail.activity.mixin`, `mail.alias.mixin` usage
11. **Testing**: Test coverage, proper test cases, `@tagged` decorators
12. **Migration**: Migration scripts, data migration patterns
13. **Actions**: Window actions, server actions, cron jobs
14. **Data Files**: XML/CSV data structure, `noupdate`, shortcuts
15. **Manifest**: Dependencies, external deps, hooks, assets

## Complete Checklist

Rules below are version-neutral unless they reference `api-highlights.md`. Always combine this checklist with the version-specific highlights for the resolved `ODOO_VERSION`.

### ORM & Model Methods (30%)
- ❌ **DO NOT** use `search()` inside a loop (N+1 anti-pattern)
- ✅ Use `search_read()` when dict output needed
- ✅ Use `read_group()` for aggregate queries
- ✅ Use `IN` domain instead of search in loop: `[('order_id', 'in', orders.ids)]`
- ✅ Batch `create([{...}, {...}])` for multiple records
- ✅ Use `recordset.write()` instead of loop
- ✅ Use `recordset.unlink()` instead of loop
- ✅ `@api.model_create_multi` on `create()` overrides (see `api-highlights.md` for version-specific enforcement)

### Views & XML (15%)
- Use the list tag appropriate to `ODOO_VERSION` (see `api-highlights.md`: `<tree>` in 16/17, `<list>` in 18+).
- Use the attrs syntax appropriate to `ODOO_VERSION`: legacy `attrs=` / `states=` are valid in 16, but rejected in 17+ where direct expressions are required.
- Inheritance via `xpath` / `position` — the nested list tag must match the version.
- Avoid duplicate `name=` attributes in records.

### Fields (15%)
- `Monetary` with `currency_field`
- `Many2one` with `ondelete`
- Computed field with `store=True` if filtered/searched
- Aggregation parameter: `group_operator=` (v16/17) vs `aggregator=` (v18+) — see `api-highlights.md`.

### Decorators (10%)
- `@api.depends` with complete dotted paths
- `@api.constrains` for invariants
- `@api.ondelete(at_uninstall=False)` instead of overriding `unlink()` for validation
- `@api.model_create_multi` for batch create

### Performance (10%)
- Avoid N+1 in loops
- Prefer `read_group()` / `search_read()` over per-record fetches
- Use `prefetch_fields` thoughtfully

### Transactions (5%)
- `savepoint` around recoverable failures
- Handle `UniqueViolation` explicitly
- Advisory locks for cross-record serialization

### Security (5%)
- Specific exceptions: `UserError`, `ValidationError`, `AccessError`
- No bare `except Exception`
- `sudo()` used narrowly with justification

### Controllers (3%)
- Correct `auth=` (`user`, `public`, `none`)
- `csrf=False` only with justification
- `type='json'` vs `type='http'` matches the client

### Mixins (3%)
- `mail.thread` with proper tracking fields
- `mail.activity.mixin` for activities
- `mail.alias.mixin` with alias fields

### Testing (2%)
- Regression test for each reproducible bug fix
- Tests for new functionality and important error paths
- Security-sensitive flows tested with the lowest practical permissions
- No state leakage between `subTest` cases; records use the active environment
- Deterministic dates and fixtures; no unnecessary reliance on demo data
- External services mocked by default, with live integrations explicitly tagged
- Coverage drops investigated for missing meaningful cases
- Proper use of `@tagged`
- Query count assertions for hot paths

### Manifest & Data (2%)
- All dependencies declared
- External deps listed
- Hooks wired correctly
- `noupdate="1"` for reference data

## Scoring

Weight each section per the percentages above. Total out of 100. Report:
- Score per section with brief justification.
- Blocking issues (must fix before merge).
- Non-blocking suggestions.
- Explicitly name the resolved `ODOO_VERSION` at the top of the report.

## Deep Dive Checks

When reviewing, thoroughly check (references below use `${ODOO_MAJOR}` — substitute the resolved value):

1. **Does `@api.depends` have complete dependencies?**
   - Check dotted paths: `partner_id.email` instead of just `partner_id`
   - Missing dependencies cause N queries
   - Reference: `skills/odoo-${ODOO_VERSION}/references/odoo-${ODOO_MAJOR}-decorator-guide.md`

2. **Are there N+1 queries?**
   - Loop with `search()`, `browse()`, `read()` inside
   - Solution: `search_read()` with `IN` domain or `read_group()`
   - Reference: `skills/odoo-${ODOO_VERSION}/references/odoo-${ODOO_MAJOR}-performance-guide.md`

3. **Are there batch operations?**
   - `create()`, `write()`, `unlink()` in loop
   - Solution: batch operations on recordset
   - Reference: `skills/odoo-${ODOO_VERSION}/references/odoo-${ODOO_MAJOR}-performance-guide.md`

4. **Is transaction safe?**
   - `UniqueViolation` handling without savepoint
   - Concurrent updates without advisory lock
   - Reference: `skills/odoo-${ODOO_VERSION}/references/odoo-${ODOO_MAJOR}-transaction-guide.md`

5. **Are version-specific patterns correct?**
   - List tag, attrs syntax, aggregation parameter, optional `_name` (v19).
   - Reference: `skills/odoo-${ODOO_VERSION}/references/api-highlights.md` + `odoo-${ODOO_MAJOR}-view-guide.md`

6. **Are field definitions correct?**
   - `Monetary` with `currency_field`
   - `Many2one` with `ondelete`
   - Computed field with `store=True` if needed
   - Reference: `skills/odoo-${ODOO_VERSION}/references/odoo-${ODOO_MAJOR}-field-guide.md`

7. **Is exception handling correct?**
   - `UserError`, `ValidationError`, `AccessError`
   - No generic `Exception`
   - Reference: `skills/odoo-${ODOO_VERSION}/references/odoo-${ODOO_MAJOR}-security-guide.md`

8. **Are mixins properly configured?**
   - `mail.thread` with proper tracking fields
   - `mail.activity.mixin` for activities
   - `mail.alias.mixin` with alias fields
   - Reference: `skills/odoo-${ODOO_VERSION}/references/odoo-${ODOO_MAJOR}-mixins-guide.md`

9. **Is testing adequate?**
   - Regression test for each reproducible bug fix
   - Tests for new functionality and important error paths
   - Security-sensitive flows use the lowest practical permissions
   - No state leakage between `subTest` cases or stored record environments
   - Deterministic dates and fixtures; no unnecessary demo-data dependency
   - External services mocked by default and live integrations explicitly tagged
   - Coverage drops investigated for missing meaningful cases
   - Proper use of `@tagged` decorators
   - Query count assertions for performance
   - Reference: `skills/odoo-${ODOO_VERSION}/references/odoo-${ODOO_MAJOR}-testing-guide.md`

10. **Are migrations handled correctly?**
    - Proper migration script location
    - Pre/post migration scripts
    - Idempotent operations
    - Reference: `skills/odoo-${ODOO_VERSION}/references/odoo-${ODOO_MAJOR}-migration-guide.md`

11. **Are actions properly defined?**
    - Window actions with correct context
    - Server actions for automation
    - Cron jobs with proper intervals
    - Reference: `skills/odoo-${ODOO_VERSION}/references/odoo-${ODOO_MAJOR}-actions-guide.md`

12. **Are data files correct?**
    - Proper XML record structure
    - `noupdate="1"` for reference data
    - CSV data properly formatted
    - Reference: `skills/odoo-${ODOO_VERSION}/references/odoo-${ODOO_MAJOR}-data-guide.md`

13. **Is manifest correct?**
    - All dependencies declared
    - External dependencies listed
    - Hooks properly configured
    - Reference: `skills/odoo-${ODOO_VERSION}/references/odoo-${ODOO_MAJOR}-manifest-guide.md`

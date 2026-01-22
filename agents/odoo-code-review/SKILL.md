---
name: odoo-code-review
description: Review Odoo code for correctness, security, performance, and Odoo 18 standards. Use when reviewing Odoo modules, diffs, or pull requests; produce a scored report with weighted criteria.
---

# Odoo Code Review

## Objective

Review Odoo code changes against clear criteria, identify risks, and score using a weighted scale from an Odoo 18 expert perspective.

## Pre-review Requirements

- Read `skills/odoo/18.0/SKILL.md` and related guides if there are changes
  regarding models, fields, views, controllers, security, performance.
- Identify scope: module, file, and change context.
- Master Odoo 18 API changes: `<list>` instead of `<tree>`, `@api.ondelete`, etc.

## Expert Review Process

1. **Scope**: Identify change scope, objectives, and key risks
2. **ORM & Model Methods**: Search patterns, CRUD operations, recordset operations
3. **Field Definitions**: Field types, computed fields, relational field parameters
4. **API Decorators**: @api.depends, @api.constrains, @api.ondelete (Odoo 18!)
5. **Performance**: N+1 detection, batch operations, field selection
6. **Transaction Management**: Savepoints, UniqueViolation, serialization
7. **Views & XML**: Odoo 18 tags (`<list>`), inheritance, structure
8. **Security**: ACL, record rules, exceptions, sudo usage
9. **Controllers**: Auth types, CSRF protection, routing

## Odoo 18 Complete Checklist

### ORM & Model Methods (30%)
- ❌ **DO NOT** use `search()` inside loop (N+1 anti-pattern)
- ✅ Use `search_read()` when dict output needed
- ✅ Use `read_group()` for aggregate queries
- ✅ Use `IN` domain instead of search in loop: `[('order_id', 'in', orders.ids)]`
- ✅ Batch `create([{...}, {...}])` for multiple records
- ✅ Use `recordset.write()` instead of loop
- ✅ Use `recordset.unlink()` instead of loop
- ✅ Use `mapped()` instead of list comprehension
- ✅ Use `filtered()` before operations
- ✅ Use `exists()` to filter non-existing records

### Field Definitions (15%)
- ✅ `Many2one` has `ondelete` parameter (`cascade`, `restrict`, `set null`)
- ✅ `Monetary` has `currency_field` parameter
- ✅ `One2many` has `inverse_name` parameter
- ❌ **DO NOT** use `Float` for currency (use `Monetary`)
- ❌ **DO NOT** use `<tree>` in Odoo 18 (use `<list>`)
- ✅ Computed fields have `store=True` if searchable/groupable needed
- ✅ `@api.depends` includes ALL dependencies with dotted paths

### API Decorators (15%)
- ✅ `@api.depends` uses dotted paths for related fields: `@api.depends('partner_id.email')`
- ❌ **DO NOT** use dotted paths in `@api.constrains` (only simple field names)
- ✅ `@api.ondelete(at_uninstall=False)` instead of overriding `unlink()` for validation (Odoo 18!)
- ✅ `@api.constrains` raises `ValidationError`
- ✅ `@api.model_create_multi` for batch create (Odoo 18)

### Performance (20%)
- ❌ **DO NOT** `search()` in loop
- ❌ **DO NOT** `browse()` in loop
- ❌ **DO NOT** `create()` in loop
- ❌ **DO NOT** `write()` in loop
- ❌ **DO NOT** `unlink()` in loop
- ✅ Use prefetch (automatic) for related field access
- ✅ Use `search_read()` to fetch specific fields
- ✅ Use `bin_size=True` for binary fields
- ✅ Use advisory locks for concurrent operations

### Transaction Management (10%)
- ✅ Use `with self.env.cr.savepoint():` for error isolation
- ❌ **DO NOT** continue after UniqueViolation without savepoint
- ✅ Use advisory locks to prevent serialization errors
- ✅ Group identical updates to minimize conflicts

### Views & XML (5%)
- ✅ Use `<list>` instead of `<tree>` (Odoo 18!)
- ✅ Use `decoration-*` for row styling
- ✅ Use `xpath` or shorthand with `position` for inheritance
- ✅ Proper `inherit_id` reference

### Security (5%)
- ✅ Has `ir.model.access.csv` file with proper permissions
- ✅ Use `UserError` for business logic errors
- ✅ Use `ValidationError` for constraint violations
- ✅ Use `AccessError` for permission issues
- ❌ **DO NOT** raise generic `Exception`
- ✅ Record rules defined with proper domain_force

### Controllers (5%)
- ✅ Use correct `auth` type (`user`, `public`, `none`)
- ✅ Use `auth='none'` for truly public endpoints (webhooks)
- ✅ CSRF enabled for POST (default)
- ✅ `csrf=False` only for external webhooks

## Anti-Patterns to Detect

| Anti-Pattern | Consequence | Fix |
|--------------|-------------|-----|
| `search()` in loop | N+1 queries | Use `search_read()` with `IN` domain |
| `create()` in loop | N INSERT statements | Batch: `create([{...}, {...}])` |
| `write()` in loop | N UPDATE statements | `records.write({...})` |
| `unlink()` in loop | N DELETE statements | `records.unlink()` |
| Override `unlink()` for validation | Breaks module uninstall | Use `@api.ondelete(at_uninstall=False)` |
| `@api.depends('a')` then access `a.b` | N queries | Add `@api.depends('a.b')` |
| `@api.constrains('a.b')` | Not supported | Use only `@api.constrains('a')` |
| `<tree>` in Odoo 18 | Deprecated | Use `<list>` |
| `Float` for currency | Precision issues | Use `Monetary` |
| Missing `ondelete` on Many2one | Orphan records | Add `ondelete='cascade/restrict'` |
| Generic `Exception` | Poor UX | Use `UserError`, `ValidationError` |
| Continue after UniqueViolation without savepoint | Transaction aborted | Use `with self.env.cr.savepoint():` |

## Scoring Scale (Weighted)

**Criteria** (score 1-10):

- **ORM & Model Methods** (30%)
- **Field Definitions** (15%)
- **API Decorators** (15%)
- **Performance** (20%)
- **Transaction Management** (10%)
- **Views & XML** (5%)
- **Security** (5%)
- **Controllers** (5%)

**Total calculation**:

```
total = 0.3*orm + 0.15*fields + 0.15*decorators + 0.2*performance + 0.1*transaction + 0.05*views + 0.05*security + 0.05*controllers
```

**Score anchors**:

- **9-10**: Excellent, no significant risks, follows all best practices
- **7-8**: Good, minor issues or improvements possible
- **5-6**: Average, clear risks to address, has anti-patterns
- **3-4**: Poor, serious errors or regression-prone
- **1-2**: Very poor, cannot merge, violates critical patterns

## Report Format (Required)

```
## Quick Summary
- [1-2 sentences summarizing key points]

## Overall Score
- Total: X.X/10
- Formula: 0.3*ORM + 0.15*Fields + 0.15*Decorators + 0.2*Perf + 0.1*Trans + 0.05*Views + 0.05*Sec + 0.05*Controllers

## Score by Criteria
- ORM & Model Methods: X/10 — [brief reason, any anti-patterns?]
- Field Definitions: X/10 — [brief reason]
- API Decorators: X/10 — [brief reason, check @api.ondelete, dotted paths]
- Performance: X/10 — [brief reason, any N+1?]
- Transaction Management: X/10 — [brief reason, savepoints correct?]
- Views & XML: X/10 — [brief reason, using <list>?]
- Security: X/10 — [brief reason]
- Controllers: X/10 — [brief reason]

## Key Findings (high → low priority)

### 🔴 Critical (Must Fix)
- [Severity] Brief description + consequence + fix suggestion
- Code reference: `path/file.py:XX`

### 🟡 Major (Should Fix)
- [Severity] Brief description + consequence + fix suggestion
- Code reference: `path/file.py:XX`

### 🔵 Minor (Nice to Have)
- [Severity] Brief description + improvement suggestion

## Positive Patterns Found
- ✅ [Good pattern found] - Line XX

## Recommendations
- [Specific, clear improvements, in priority order]

## Testing
- Ran: [if any, state commands]
- Missing: [tests missing or not run, N+1 scenarios]
```

## Response Rules

- Prioritize error and risk detection first, then suggestions
- If no significant issues, clearly state "No findings"
- Cite correct file and code when needed: `path/to/file.py:XX`
- State assumptions when information is missing (don't guess)
- Focus on Odoo-specific patterns, not generic Python advice
- Provide code examples for complex issues
- Reference Odoo documentation when applicable

## Deep Dive Checks

When reviewing, thoroughly check:

1. **Does @api.depends have complete dependencies?**
   - Check dotted paths: `partner_id.email` instead of just `partner_id`
   - Missing dependencies cause N queries

2. **Are there N+1 queries?**
   - Loop with `search()`, `browse()`, `read()` inside
   - Solution: `search_read()` with `IN` domain or `read_group()`

3. **Are there batch operations?**
   - `create()`, `write()`, `unlink()` in loop
   - Solution: Batch operations on recordset

4. **Is transaction safe?**
   - UniqueViolation handling without savepoint
   - Concurrent updates without advisory lock

5. **Are Odoo 18 patterns correct?**
   - Use `<list>` instead of `<tree>`
   - Use `@api.ondelete()` instead of overriding `unlink()`
   - Use `@api.model_create_multi` for batch create

6. **Are field definitions correct?**
   - `Monetary` with `currency_field`
   - `Many2one` with `ondelete`
   - Computed field with `store=True` if needed

7. **Is exception handling correct?**
   - `UserError`, `ValidationError`, `AccessError`
   - No generic `Exception`

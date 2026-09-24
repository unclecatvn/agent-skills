---
name: odoo-code-review
description: Review Odoo code for correctness, security, performance, and version-specific standards (Odoo 16, 17, 18, or 19). Use when reviewing Odoo modules, diffs, or pull requests; produce a scored report with weighted criteria.
---

# Odoo Code Review

## Objective

Review Odoo code changes against clear criteria, identify risks, and score using a weighted scale from an Odoo-expert perspective — using the reference pack that matches the target Odoo version.

## Resolve the target Odoo version

Before reviewing, resolve `ODOO_VERSION` (one of `16.0`, `17.0`, `18.0`, `19.0`) in this order. Stop at the first one that succeeds:

1. **Explicit argument** passed to the agent invocation (e.g. `odoo_version: "19.0"`) or stated by the user.
2. **Project instructions**: the Odoo version stated in the project `CLAUDE.md` or `AGENTS.md`.
3. **The odoo-workflow helper**: the `version` line of `python3 <helper> env`, where `<helper>` is the `helper` the invocation passes (with its flags) or the newest `~/.claude/plugins/cache/unclecat-agent-skills/agent-skills/*/skills/odoo-workflow/scripts/odoo_trace.py`. It reads `.claude/odoo.json`, `.odoo-version`, `.claude/launch.json` and the conf the way step 4 describes. Exit 2 (`SETUP ERROR`, for example a version in `.claude/odoo.json` or `.odoo-version` that disagrees with `odoo/release.py`): stop and ask.
4. **Without the helper**: `grep -n "^version_info" <odoo_root>/odoo/release.py` (`(18, 0, ...)` → `18.0`) in the core located by `odoo_root` in `.claude/odoo.json`, the `odoo-bin` configuration in `.claude/launch.json` whose addons path covers the cwd, or the one `*.conf` whose uncommented `addons_path` covers the cwd, searched from the parent directory upwards (each level and its subdirectories; Odoo ignores `#` / `;` comment lines). An `odoo_version` in `.claude/odoo.json` or the first line of a `.odoo-version` file (cwd or nearest parent) must match it.
5. **Serie-prefixed manifest versions**: only `version` values (`'version'` or `"version"` keys) in workspace `__manifest__.py` files with four or five parts that start with the serie (`18.0.1.0`, `18.0.1.0.0`). Ignore short versions such as `'1.2'` or `'1.0.3'`; never count leading numbers.
6. **Nothing found**: write `version unknown` at the top of the review and stop to ask. Never default to a version.

If two sources disagree (e.g. the argument and `release.py`), stop and ask. Derive `ODOO_MAJOR` from `ODOO_VERSION` by stripping `.0` (e.g. `18.0` → `18`). All guide paths below use these placeholders.

Supported versions: **16.0, 17.0, 18.0, 19.0**. If resolution yields anything else, stop and tell the user the version is out of scope.

## Locate the reference pack

`PACK_DIR` is the `odoo-<major>` pack directory (it holds `SKILL.md` and `references/`). Use `pack_dir` when the invocation passes it. Otherwise take the first directory that exists:

1. `~/.claude/plugins/cache/unclecat-agent-skills/agent-skills/<ver>/skills/odoo-${ODOO_VERSION}/` (Claude Code plugin; newest `<ver>`: `ls -d ~/.claude/plugins/cache/unclecat-agent-skills/agent-skills/*/skills/odoo-${ODOO_VERSION} | sort -V | tail -1`)
2. `~/.claude/skills/odoo-${ODOO_MAJOR}/`
3. `.claude/skills/odoo-${ODOO_MAJOR}/`
4. `~/.agents/skills/odoo-${ODOO_MAJOR}/`
5. `skills/odoo-${ODOO_VERSION}/` (a checkout of this repository)

None exists: write `pack not found` at the top of the review, skip every `${PACK_DIR}` read below, and review against the real source only. Never guess what the pack says.

Use `roots` (addons roots in `addons_path` order) when the invocation passes them to find the base code a change extends. With the helper (step 3), check what the diff relies on outside its own module: `python3 <helper> field MODEL FIELD[.FIELD...]`, `method MODEL METHOD --module MODULE` (a def the change relies on tagged `NOT in depends` is a missing dependency), `xmlid module.name`, and `unlisted MODULE` for files the manifest never loads. Exit 1 (NOT FOUND) or an unexplained unlisted file is a blocking issue; exit 2 means unknown, never missing.

## Pre-review Requirements

- Read `${PACK_DIR}/SKILL.md` as the master index for the resolved version's guides.
- Read `${PACK_DIR}/references/api-highlights.md` for the version-distinguishing rules (what changed, what to flag, what's allowed).
- Read relevant guides from `${PACK_DIR}/references/` based on change scope:
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
- Apply the version-distinguishing rules from `api-highlights.md` (e.g. `<tree>` vs `<list>`, `group_operator=` vs `aggregator=`, a missing `_name`: on 19 a class with neither `_name` nor a string `_inherit` becomes a model named after the class, with a warning).

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
- ✅ Aggregate with the grouping API of `ODOO_VERSION`, not Python loops:
  - 19: `_read_group(domain, groupby, aggregates)` in backend code, `formatted_read_group()` when a formatted dict result is needed; `read_group()` is deprecated since 19.0 - flag new calls.
  - 18: `_read_group()` in backend code (returns recordsets and values); public `read_group()` (not deprecated) when dict output is needed.
  - 16/17: follow `odoo-${ODOO_MAJOR}-performance-guide.md` (unverified against 16/17 source).
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
- Prefer the version's grouping API (see ORM above) / `search_read()` over per-record fetches
- Use `prefetch_fields` thoughtfully

### Transactions (5%)
- `savepoint` around recoverable failures
- Handle `UniqueViolation` explicitly
- Advisory locks for cross-record serialization

### Security (5%)
- Specific exceptions: `UserError`, `ValidationError`, `AccessError`
- No bare `except Exception`
- `sudo()` used narrowly with justification: every `sudo()` / `with_user(SUPERUSER_ID)` states its reason (which ACL or record rule it bypasses and why the caller may do that); flag any without one
- An access check runs before the elevated record is used or returned:
  - Models, 18+: `check_access(operation)` / `has_access(operation)` (`check_access_rights()` / `check_access_rule()` are deprecated since 18.0); 16/17: per `odoo-${ODOO_MAJOR}-security-guide.md` (unverified against 16/17 source).
  - Controllers: an access token or group check (`has_group()`). Reference pattern, 18.0 `portal/controllers/portal.py` `_document_check_access()`: `document.check_access('read')` on the non-sudo record, on `AccessError` accept only a matching `access_token` (`consteq`), then return the sudo record.
- `sudo()` results bound to a variable carry the `_sudo` suffix (`partner_sudo = self.partner_id.sudo()`);
  one-shot calls (`record.sudo().write(vals)`) are fine; no `_sudo` recordset returned or stored on `self`.
  Heuristic for one-line assignments - confirm the right-hand side is a recordset (`search_count()` and other scalars are exempt):
  ```bash
  grep -nE '^[[:space:]]*[A-Za-z_][A-Za-z0-9_]*[[:space:]]*=[[:space:]]*[^=].*\.sudo\(' <file> \
    | grep -vE '^[0-9]+:[[:space:]]*[A-Za-z0-9_]*_sudo[[:space:]]*='
  ```
- Multi-company: a relational field to a company-bound comodel (one with `company_id`) on a model with `company_id` sets `check_company=True`, and the model sets `_check_company_auto = True` so `create()` / `write()` call `_check_company()`.
  A new model with `company_id` ships a multi-company `ir.rule` on `company_ids`: `[('company_id', 'in', company_ids)]`, or `[('company_id', 'in', company_ids + [False])]` when the company is optional.

### Controllers (3%)
- Correct `auth=` (`user`, `public`, `none`; `bearer` on 18+)
- `csrf=False` only with justification
- `type='json'` vs `type='http'` matches the client (19: `type='jsonrpc'`; `'json'` is a deprecated alias)

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

### Hygiene (blocking, 0%)
Not scored - any hit blocks the merge regardless of the total:
- `ponytail:` or other "simplified for now" markers in added lines
- `Co-Authored-By` / `Generated with` in added lines, commit messages, or the PR body
- User-facing strings added or changed without a regenerated `i18n/<module>.pot` (and merged `.po` files) in the same change

Check added lines only, so a deleted marker never trips it. A workspace can hold several git repos (e.g. `erp`, `erp-external`, `erp-internal`): run the checks once per repo that holds a touched file (`git -C <dir-of-file> rev-parse --show-toplevel`), with that repo's own `<base>`:
```bash
git -C <repo> rev-parse --verify '<base>^{commit}'
git -C <repo> diff HEAD -U0 | grep -E '^\+[^+]' | grep -nE 'ponytail:|Co-Authored-By|Generated with'
git -C <repo> ls-files -z --others --exclude-standard | (cd <repo> && xargs -0 grep -nE 'ponytail:|Co-Authored-By|Generated with' /dev/null)
git -C <repo> diff <base>...HEAD -U0 | grep -E '^\+[^+]' | grep -nE 'ponytail:|Co-Authored-By|Generated with'
git -C <repo> log <base>..HEAD --format=%B | grep -nE 'Co-Authored-By|Generated with'
```
The `diff HEAD` and `ls-files` lines cover uncommitted and untracked files. `<base>...HEAD` (three dots) diffs from the merge base, so lines the base branch changed after the fork never count as added.
A `fatal:` line or a non-zero exit from `git` (not a repo, unknown `<base>`) is a failed check, not a pass: the `grep` pipeline prints nothing in that case too. Report the repo and the error.

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
   - Reference: `${PACK_DIR}/references/odoo-${ODOO_MAJOR}-decorator-guide.md`

2. **Are there N+1 queries?**
   - Loop with `search()`, `browse()`, `read()` inside
   - Solution: `search_read()` with `IN` domain or the version's grouping API (`_read_group()` on 18/19; see ORM checklist)
   - Reference: `${PACK_DIR}/references/odoo-${ODOO_MAJOR}-performance-guide.md`

3. **Are there batch operations?**
   - `create()`, `write()`, `unlink()` in loop
   - Solution: batch operations on recordset
   - Reference: `${PACK_DIR}/references/odoo-${ODOO_MAJOR}-performance-guide.md`

4. **Is transaction safe?**
   - `UniqueViolation` handling without savepoint
   - Concurrent updates without advisory lock
   - Reference: `${PACK_DIR}/references/odoo-${ODOO_MAJOR}-transaction-guide.md`

5. **Are version-specific patterns correct?**
   - List tag, attrs syntax, aggregation parameter, explicit `_name` (on 19 a class with neither `_name` nor a string `_inherit` becomes a model named after the class, with a warning).
   - Reference: `${PACK_DIR}/references/api-highlights.md` + `odoo-${ODOO_MAJOR}-view-guide.md`

6. **Are field definitions correct?**
   - `Monetary` with `currency_field`
   - `Many2one` with `ondelete`
   - Computed field with `store=True` if needed
   - Reference: `${PACK_DIR}/references/odoo-${ODOO_MAJOR}-field-guide.md`

7. **Is exception handling correct?**
   - `UserError`, `ValidationError`, `AccessError`
   - No generic `Exception`
   - Reference: `${PACK_DIR}/references/odoo-${ODOO_MAJOR}-security-guide.md`

8. **Are mixins properly configured?**
   - `mail.thread` with proper tracking fields
   - `mail.activity.mixin` for activities
   - `mail.alias.mixin` with alias fields
   - Reference: `${PACK_DIR}/references/odoo-${ODOO_MAJOR}-mixins-guide.md`

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
   - Reference: `${PACK_DIR}/references/odoo-${ODOO_MAJOR}-testing-guide.md`

10. **Are migrations handled correctly?**
    - Proper migration script location
    - Pre/post migration scripts
    - Idempotent operations
    - Reference: `${PACK_DIR}/references/odoo-${ODOO_MAJOR}-migration-guide.md`

11. **Are actions properly defined?**
    - Window actions with correct context
    - Server actions for automation
    - Cron jobs with proper intervals
    - Reference: `${PACK_DIR}/references/odoo-${ODOO_MAJOR}-actions-guide.md`

12. **Are data files correct?**
    - Proper XML record structure
    - `noupdate="1"` for reference data
    - CSV data properly formatted
    - Reference: `${PACK_DIR}/references/odoo-${ODOO_MAJOR}-data-guide.md`

13. **Is manifest correct?**
    - All dependencies declared
    - External dependencies listed
    - Hooks properly configured
    - Reference: `${PACK_DIR}/references/odoo-${ODOO_MAJOR}-manifest-guide.md`

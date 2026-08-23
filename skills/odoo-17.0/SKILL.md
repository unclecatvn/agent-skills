---
name: odoo-17
description: >
  Odoo 17 development reference for Python models and ORM (search, domain, read_group, compute fields),
  XML/CSV data and views, OWL/JS client code, QWeb reports, security (ACL, record rules, groups),
  cron and server actions, migrations and module upgrades, tests, i18n, and performance.
  Use this skill whenever work involves Odoo 17 or custom addons—even if the user only pastes a traceback,
  mentions addons/ or __manifest__.py, describes form/tree/kanban/XML errors, HTTP controllers, or
  business rules on models—including building features, fixing bugs, refactoring, or reviewing addon code.
  Includes CSS/SCSS asset authoring and review for Odoo addons.
globs: "**/*.{py,xml,csv,js,ts,css,scss}"
---

# Odoo 17 Skill - Master Index

Master index for all Odoo 17 development guides. Read the appropriate guide from `references/` based on your task.

## Quick Reference

| Topic | File | When to Use |
|-------|------|-------------|
| Actions | `references/odoo-17-actions-guide.md` | Creating actions, menus, scheduled jobs, server actions |
| API Decorators | `references/odoo-17-decorator-guide.md` | Using @api decorators, compute fields, validation |
| Controllers | `references/odoo-17-controller-guide.md` | Writing HTTP endpoints, routes, web controllers |
| Data Files | `references/odoo-17-data-guide.md` | XML/CSV data files, records, shortcuts |
| Development | `references/odoo-17-development-guide.md` | Creating modules, manifest, reports, security, wizards |
| Field Types | `references/odoo-17-field-guide.md` | Defining model fields, choosing field types |
| Manifest | `references/odoo-17-manifest-guide.md` | __manifest__.py configuration, dependencies, hooks |
| Migration | `references/odoo-17-migration-guide.md` | Upgrading modules, data migration, version changes |
| Mixins | `references/odoo-17-mixins-guide.md` | mail.thread, activities, email aliases, tracking |
| Model Methods | `references/odoo-17-model-guide.md` | Writing ORM queries, CRUD operations, domain filters |
| OWL Components | `references/odoo-17-owl-guide.md` | Building OWL UI components, hooks, services |
| Performance | `references/odoo-17-performance-guide.md` | Optimizing queries, fixing slow code, preventing N+1 |
| Reports | `references/odoo-17-reports-guide.md` | QWeb reports, PDF/HTML, templates, paper formats |
| Security | `references/odoo-17-security-guide.md` | Access rights, record rules, field permissions |
| Testing | `references/odoo-17-testing-guide.md` | Writing tests, mocking, assertions, browser testing |
| Transactions | `references/odoo-17-transaction-guide.md` | Handling database errors, savepoints, UniqueViolation |
| Translation | `references/odoo-17-translation-guide.md` | Adding translations, localization, i18n |
| Views & XML | `references/odoo-17-view-guide.md` | Writing XML views, actions, menus, QWeb templates |

## Coding Conventions

Apply the relevant convention section in the guide you open. Conventions are
advisory: preserve the style of an existing stable addon and keep diffs
focused. When guidance conflicts, prefer Odoo 17 runtime/source behavior,
then the surrounding addon style, then the convention.

- Module layout and asset placement: development and controller guides.
- XML formatting and external IDs: data, view, action, report, and security guides.
- Python naming, imports, recordsets, transactions, and translations: model,
  field, decorator, performance, transaction, and translation guides.
- JavaScript and CSS/SCSS: development guide.

## File Structure

```
skills/odoo-17.0/
├── SKILL.md                          # This file - master index
└── references/                       # Development guides
    ├── odoo-17-actions-guide.md
    ├── odoo-17-controller-guide.md
    ├── odoo-17-data-guide.md
    ├── odoo-17-decorator-guide.md
    ├── odoo-17-development-guide.md
    ├── odoo-17-field-guide.md
    ├── odoo-17-manifest-guide.md
    ├── odoo-17-migration-guide.md
    ├── odoo-17-mixins-guide.md
    ├── odoo-17-model-guide.md
    ├── odoo-17-owl-guide.md
    ├── odoo-17-performance-guide.md
    ├── odoo-17-reports-guide.md
    ├── odoo-17-security-guide.md
    ├── odoo-17-testing-guide.md
    ├── odoo-17-transaction-guide.md
    ├── odoo-17-translation-guide.md
    └── odoo-17-view-guide.md
```

## Base Code Reference (Odoo 17)

All guides are based on analysis of Odoo 17 source code:
- `odoo/models.py` - ORM implementation
- `odoo/fields.py` - Field types
- `odoo/api.py` - Decorators
- `odoo/http.py` - HTTP layer
- `odoo/exceptions.py` - Exception types
- `odoo/tools/translate.py` - Translation system
- `odoo/addons/base/models/res_lang.py` - Language model
- `addons/web/static/src/core/l10n/translation.js` - JS translations

## External Documentation

- [Odoo 17 Official Documentation](https://github.com/odoo/documentation/tree/17.0)
- [Odoo 17 Developer Reference](https://github.com/odoo/documentation/blob/17.0/content/developer/reference/backend/orm.rst)
- [Odoo 17 Coding Guidelines](https://raw.githubusercontent.com/odoo/documentation/17.0/content/contributing/development/coding_guidelines.rst)

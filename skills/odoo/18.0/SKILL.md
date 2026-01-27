---
name: odoo-18
description: Master index for Odoo 18 guides. This file provides a quick reference to find the appropriate detailed guide for each topic. Use this as an index to locate specific guides when working with Odoo 18 code.
globs: "**/*.{py,xml}"
license: MIT
author: UncleCat
version: 1.0.0
---

# Odoo 18 Skill - Master Index

Master index for all Odoo 18 guides. Use this to quickly find the appropriate guide for your task.

## Quick Reference

| Topic | File | When to Use |
|-------|------|-------------|
| [Model Methods](#model-guide) | `odoo-18-model-guide.md` | Writing ORM queries, CRUD operations, domain filters |
| [Field Types](#field-guide) | `odoo-18-field-guide.md` | Defining model fields, choosing field types |
| [API Decorators](#decorator-guide) | `odoo-18-decorator-guide.md` | Using @api decorators, compute fields, validation |
| [Views & XML](#view-guide) | `odoo-18-view-guide.md` | Writing XML views, actions, menus, QWeb templates |
| [Performance](#performance-guide) | `odoo-18-performance-guide.md` | Optimizing queries, fixing slow code, preventing N+1 |
| [Transactions](#transaction-guide) | `odoo-18-transaction-guide.md` | Handling database errors, savepoints, UniqueViolation |
| [Controllers](#controller-guide) | `odoo-18-controller-guide.md` | Writing HTTP endpoints, routes, web controllers |
| [OWL Components](#owl-guide) | `odoo-18-owl-guide.md` | Building OWL UI components, hooks, services |
| [Migration](#migration-guide) | `odoo-18-migration-guide.md` | Upgrading modules, data migration, version changes |
| [Testing](#testing-guide) | `odoo-18-testing-guide.md` | Writing tests, mocking, assertions, browser testing |
| [Development](#development-guide) | `odoo-18-development-guide.md` | Creating modules, manifest, reports, security, wizards |
| [Translation](#translation-guide) | `odoo-18-translation-guide.md` | Adding translations, localization, i18n |

---

## Guide Index

### Model Guide
**File**: `odoo-18-model-guide.md`

**When to read**:
- Writing model methods
- Using ORM queries (`search`, `read`, `create`, `write`, `unlink`)
- Working with domain filters
- Understanding recordsets and prefetching
- Batch operations

---

### Field Guide
**File**: `odoo-18-field-guide.md`

**When to read**:
- Defining new model fields
- Choosing appropriate field types (Char, Text, Monetary, etc.)
- Setting field parameters (required, default, index, etc.)
- Creating computed fields
- Setting up relational fields (Many2one, One2many, Many2many)

---

### Decorator Guide
**File**: `odoo-18-decorator-guide.md`

**When to read**:
- Using `@api.depends` for computed fields
- Using `@api.constrains` for validation
- Using `@api.ondelete` (Odoo 18) for delete validation
- Using `@api.onchange` for form UI updates
- Using `@api.model` for model-level methods

---

### View Guide
**File**: `odoo-18-view-guide.md`

**When to read**:
- Writing list views (use `<list>` not `<tree>` in Odoo 18)
- Writing form views
- Writing search views
- Creating view inheritance with xpath
- Writing QWeb templates
- Creating actions and menus

---

### Performance Guide
**File**: `odoo-18-performance-guide.md`

**When to read**:
- Fixing N+1 query problems
- Optimizing slow code
- Reducing database queries
- Understanding prefetch behavior
- Using `search_read()`, `read_group()`, `mapped()`, `filtered()`

---

### Transaction Guide
**File**: `odoo-18-transaction-guide.md`

**When to read**:
- Handling database errors (UniqueViolation, NotNullViolation)
- Using savepoints for error isolation
- Understanding transaction states
- Dealing with serialization failures
- Commit and rollback patterns

---

### Controller Guide
**File**: `odoo-18-controller-guide.md`

**When to read**:
- Creating HTTP endpoints
- Writing web controllers
- Setting up routes
- Choosing auth types (user, public, none)
- Handling JSON vs HTTP responses

---

### OWL Guide
**File**: `odoo-18-owl-guide.md`

**When to read**:
- Building OWL components
- Using hooks (useState, onWillStart, onMounted, etc.)
- Using services (orm, rpc, action, dialog, notification)
- Component lifecycle management
- JavaScript/OWL translations with `_t()`

---

### Migration Guide
**File**: `odoo-18-migration-guide.md`

**When to read**:
- Upgrading modules from earlier versions
- Writing migration scripts (pre, post, end)
- Handling data migration
- Using module hooks (pre_init, post_init, uninstall)
- Version-specific migration logic

---

### Testing Guide
**File**: `odoo-18-testing-guide.md`

**When to read**:
- Writing unit tests (TransactionCase)
- Writing browser tests (HttpCase)
- Using test decorators (@tagged, @users, @warmup)
- Testing with Form class
- Mocking external APIs
- Query count assertions

---

### Development Guide
**File**: `odoo-18-development-guide.md`

**When to read**:
- Creating new modules
- Writing `__manifest__.py`
- Setting up module structure
- Configuring access rights (CSV)
- Creating record rules
- Building wizards (TransientModel)
- Creating reports

---

### Translation Guide
**File**: `odoo-18-translation-guide.md`

**When to read**:
- Adding translatable strings in Python (`_()`, `_lt()`)
- Adding translatable strings in JavaScript (`_t()`)
- Creating translatable QWeb templates
- Setting up translated fields (`translate=True`)
- Managing PO files
- Exporting/importing translations
- Working with languages (`res.lang`)

---

## File Structure

```
agent-skills/skills/odoo/18.0/
├── SKILL.md                       # THIS FILE - master index
├── dev/                           # Development guides folder
│   ├── odoo-18-model-guide.md     # ORM, CRUD, search, domain
│   ├── odoo-18-field-guide.md     # Field types, parameters
│   ├── odoo-18-decorator-guide.md  # @api decorators
│   ├── odoo-18-view-guide.md      # XML views, actions, menus, QWeb
│   ├── odoo-18-performance-guide.md # N+1 prevention, optimization
│   ├── odoo-18-transaction-guide.md # Savepoints, UniqueViolation, commit/rollback
│   ├── odoo-18-controller-guide.md # HTTP, routing, controllers
│   ├── odoo-18-owl-guide.md       # OWL components, hooks, services
│   ├── odoo-18-migration-guide.md # Migration scripts, upgrade hooks
│   ├── odoo-18-testing-guide.md   # Test classes, decorators, mocking
│   ├── odoo-18-development-guide.md # Manifest, reports, security, wizards
│   └── odoo-18-translation-guide.md # Translations, localization, i18n
├── CLAUDE.md                      # Claude Code specific
└── AGENTS.md                      # AI agents setup
```

---

## Base Code Reference (Odoo 18)

All guides are based on analysis of Odoo 18 source code:
- `odoo/models.py` - ORM implementation
- `odoo/fields.py` - Field types
- `odoo/api.py` - Decorators
- `odoo/http.py` - HTTP layer
- `odoo/exceptions.py` - Exception types
- `odoo/tools/translate.py` - Translation system
- `odoo/addons/base/models/res_lang.py` - Language model
- `addons/web/static/src/core/l10n/translation.js` - JS translations

---

**For setup instructions with different AI IDEs, see [AGENTS.md](./AGENTS.md)**

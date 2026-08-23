# Odoo 19 Documentation - AI Agents Setup

Setup guide for using Odoo 19 documentation with AI coding assistants (Cursor, Claude Code, Windsurf, Aider, etc.).

## Quick Start

### Install via skills.sh (Recommended)

```bash
# Add Odoo 19 skill to your project
npx skills add unclecatvn/agent-skills
```

Visit [https://skills.sh/](https://skills.sh/) for more installation options.

### Cursor IDE - Remote Rule

Configure once in Cursor settings:
- `Settings` → `Rules` → `Add Remote Rule`
- Source: `Git Repository`
- URL: `git@github.com:unclecatvn/agent-skills.git`
- Branch: `19.0`
- Subfolder: `skills/odoo-19.0/`

---

## Documentation Structure

```
skills/odoo-19.0/
├── SKILL.md                       # Master index (all agents)
├── references/                    # Development guides (18 files)
│   ├── odoo-19-actions-guide.md     # ir.actions.*, cron, bindings
│   ├── odoo-19-controller-guide.md  # HTTP, routing, controllers
│   ├── odoo-19-data-guide.md        # XML/CSV data files, records
│   ├── odoo-19-decorator-guide.md   # @api decorators
│   ├── odoo-19-development-guide.md # Manifest, wizards (overview)
│   ├── odoo-19-field-guide.md       # Field types, parameters
│   ├── odoo-19-manifest-guide.md    # __manifest__.py reference
│   ├── odoo-19-mixins-guide.md      # mail.thread, activities, etc.
│   ├── odoo-19-model-guide.md       # ORM, CRUD, search, domain
│   ├── odoo-19-migration-guide.md   # Migration scripts, hooks
│   ├── odoo-19-owl-guide.md         # OWL components, services
│   ├── odoo-19-performance-guide.md # N+1 prevention, optimization
│   ├── odoo-19-reports-guide.md     # QWeb reports, PDF/HTML
│   ├── odoo-19-security-guide.md    # ACL, record rules, security
│   ├── odoo-19-testing-guide.md     # Test classes, decorators
│   ├── odoo-19-transaction-guide.md # Savepoints, errors
│   ├── odoo-19-translation-guide.md # Translations, i18n
│   └── odoo-19-view-guide.md        # XML views, QWeb
├── CLAUDE.md                      # Claude Code specific
└── AGENTS.md                      # THIS FILE - setup guide
```

---

## Guide Reference

| File | Purpose | When to Use |
|------|---------|-------------|
| `SKILL.md` | Master index for all guides | Find the right guide for your task |
| `references/odoo-19-actions-guide.md` | Actions (window, URL, server, cron) | Creating actions, menus, scheduled jobs |
| `references/odoo-19-controller-guide.md` | HTTP controllers, routing | Writing endpoints |
| `references/odoo-19-data-guide.md` | XML/CSV data files, records | Creating data files |
| `references/odoo-19-decorator-guide.md` | @api decorators usage | Using @api decorators |
| `references/odoo-19-development-guide.md` | Module structure, wizards | Creating new modules |
| `references/odoo-19-field-guide.md` | Field types, parameters | Defining model fields |
| `references/odoo-19-manifest-guide.md` | __manifest__.py reference | Configuring module manifest |
| `references/odoo-19-mixins-guide.md` | mail.thread, activities, mixins | Adding messaging, activities |
| `references/odoo-19-model-guide.md` | ORM methods, CRUD, domains | Writing model methods |
| `references/odoo-19-migration-guide.md` | Migration scripts, hooks | Upgrading modules |
| `references/odoo-19-owl-guide.md` | OWL components, hooks, services | Building OWL UI |
| `references/odoo-19-performance-guide.md` | Performance optimization | Fixing slow code |
| `references/odoo-19-reports-guide.md` | QWeb reports, templates | Creating reports |
| `references/odoo-19-security-guide.md` | ACL, record rules, security | Configuring security |
| `references/odoo-19-testing-guide.md` | Test classes, decorators, mocking | Writing tests |
| `references/odoo-19-transaction-guide.md` | Database transactions, error handling | Savepoints, UniqueViolation |
| `references/odoo-19-translation-guide.md` | Translations, localization, i18n | Adding translations |
| `references/odoo-19-view-guide.md` | XML views, actions, menus | Writing view XML |

---

## AI Agent Configuration

### Cursor IDE

| Setting | Value |
|---------|-------|
| Source | Git Repository |
| URL | `git@github.com:unclecatvn/agent-skills.git` |
| Branch | `19.0` |
| Subfolder | `skills/odoo-19.0/` |

**Globs patterns used by Cursor:**

| File | globs Pattern |
|------|---------------|
| `SKILL.md` | `**/*.{py,xml,csv,js,ts,css,scss}` |
| `references/odoo-19-actions-guide.md` | `**/*.{py,xml}` |
| `references/odoo-19-controller-guide.md` | `**/controllers/**/*.py` |
| `references/odoo-19-data-guide.md` | `**/*.{xml,csv}` |
| `references/odoo-19-decorator-guide.md` | `**/models/**/*.py` |
| `references/odoo-19-development-guide.md` | `**/*.{py,xml,csv,js,ts,css,scss}` |
| `references/odoo-19-field-guide.md` | `**/models/**/*.py` |
| `references/odoo-19-manifest-guide.md` | `**/__manifest__.py` |
| `references/odoo-19-mixins-guide.md` | `**/models/**/*.py` |
| `references/odoo-19-model-guide.md` | `**/models/**/*.py` |
| `references/odoo-19-migration-guide.md` | `**/migrations/**/*.py` |
| `references/odoo-19-owl-guide.md` | `static/src/**/*.{js,xml}` |
| `references/odoo-19-performance-guide.md` | `**/*.{py,xml}` |
| `references/odoo-19-reports-guide.md` | `**/report/**/*.xml` |
| `references/odoo-19-security-guide.md` | `**/security/**/*.{csv,xml}` |
| `references/odoo-19-testing-guide.md` | `**/tests/**/*.py` |
| `references/odoo-19-transaction-guide.md` | `**/models/**/*.py` |
| `references/odoo-19-translation-guide.md` | `**/*.{py,js,xml}` |
| `references/odoo-19-view-guide.md` | `**/views/**/*.xml` |

### Claude Code

```bash
# Install via skills.sh
npx skills add unclecatvn/agent-skills
```

Claude Code reads:
- `CLAUDE.md` - Project overview and quick reference
- `SKILL.md` - Master index for all guides
- Individual guides in `references/` - Detailed information

### Other Agents

| Agent | Setup |
|-------|-------|
| Windsurf | Same as Cursor (uses `.mdc` files) |
| Continue | Place `CLAUDE.md` or `SKILL.md` in root |
| Aider | Place `CLAUDE.md` or add to prompt |
| OpenCode | Copy skill folder to project - no additional config needed |

---

## Cursor / Claude Skills Folder

After installing via `npx skills add unclecatvn/agent-skills`, the skill is placed at:

```
.cursor/skills/
└── odoo-19/
    └── SKILL.md

.claude/skills/
└── odoo-19/
    └── SKILL.md
```

---

## Key Odoo 19 Changes

| Change | Old | New |
|--------|-----|-----|
| List view tag | `<tree>` | `<list>` |
| Dynamic attributes | `attrs="{'invisible': [...]}"` | `invisible="..."` |
| Delete validation | Override `unlink()` | `@api.ondelete(at_uninstall=False)` |
| Field aggregation | `group_operator=` | `aggregator=` |
| SQL queries | `cr.execute()` | `SQL` class with `execute_query_dict()` |

## Coding Conventions

Apply the Coding Conventions section in the guide you open. Odoo 19 runtime
behavior takes precedence, followed by the surrounding stable-addon style;
keep convention-only changes focused. The common source is the [Odoo Coding
Guidelines](https://raw.githubusercontent.com/odoo/documentation/17.0/content/contributing/development/coding_guidelines.rst).

- Use the development guide for module layout, asset, JavaScript, CSS, and
  SCSS conventions.
- Use the data, action, report, security, and view guides for XML formatting
  and external IDs.
- Use the model, field, decorator, performance, transaction, and translation
  guides for Python, recordsets, context, database work, and i18n.

---

## Repository

**URL**: `git@github.com:unclecatvn/agent-skills.git`
**Branch**: `19.0`
**License**: MIT

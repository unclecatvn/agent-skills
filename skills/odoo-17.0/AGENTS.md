# Odoo 17 Documentation - AI Agents Setup

Setup guide for using Odoo 17 documentation with AI coding assistants (Cursor, Claude Code, Windsurf, Aider, etc.).

## Quick Start

### Install via skills.sh (Recommended)

```bash
# Add Odoo 17 skill to your project
npx skills add unclecatvn/agent-skills
```

Visit [https://skills.sh/](https://skills.sh/) for more installation options.

### Cursor IDE - Remote Rule

Configure once in Cursor settings:
- `Settings` → `Rules` → `Add Remote Rule`
- Source: `Git Repository`
- URL: `git@github.com:unclecatvn/agent-skills.git`
- Branch: `17.0`
- Subfolder: `skills/odoo-17.0/`

---

## Documentation Structure

```
skills/odoo-17.0/
├── SKILL.md                       # Master index (all agents)
├── references/                    # Development guides (18 files)
│   ├── odoo-17-actions-guide.md     # ir.actions.*, cron, bindings
│   ├── odoo-17-controller-guide.md  # HTTP, routing, controllers
│   ├── odoo-17-data-guide.md        # XML/CSV data files, records
│   ├── odoo-17-decorator-guide.md   # @api decorators
│   ├── odoo-17-development-guide.md # Manifest, wizards (overview)
│   ├── odoo-17-field-guide.md       # Field types, parameters
│   ├── odoo-17-manifest-guide.md    # __manifest__.py reference
│   ├── odoo-17-mixins-guide.md      # mail.thread, activities, etc.
│   ├── odoo-17-model-guide.md       # ORM, CRUD, search, domain
│   ├── odoo-17-migration-guide.md   # Migration scripts, hooks
│   ├── odoo-17-owl-guide.md         # OWL components, services
│   ├── odoo-17-performance-guide.md # N+1 prevention, optimization
│   ├── odoo-17-reports-guide.md     # QWeb reports, PDF/HTML
│   ├── odoo-17-security-guide.md    # ACL, record rules, security
│   ├── odoo-17-testing-guide.md     # Test classes, decorators
│   ├── odoo-17-transaction-guide.md # Savepoints, errors
│   ├── odoo-17-translation-guide.md # Translations, i18n
│   └── odoo-17-view-guide.md        # XML views, QWeb
├── CLAUDE.md                      # Claude Code specific
└── AGENTS.md                      # THIS FILE - setup guide
```

---

## Guide Reference

| File | Purpose | When to Use |
|------|---------|-------------|
| `SKILL.md` | Master index for all guides | Find the right guide for your task |
| `references/odoo-17-actions-guide.md` | Actions (window, URL, server, cron) | Creating actions, menus, scheduled jobs |
| `references/odoo-17-controller-guide.md` | HTTP controllers, routing | Writing endpoints |
| `references/odoo-17-data-guide.md` | XML/CSV data files, records | Creating data files |
| `references/odoo-17-decorator-guide.md` | @api decorators usage | Using @api decorators |
| `references/odoo-17-development-guide.md` | Module structure, wizards | Creating new modules |
| `references/odoo-17-field-guide.md` | Field types, parameters | Defining model fields |
| `references/odoo-17-manifest-guide.md` | __manifest__.py reference | Configuring module manifest |
| `references/odoo-17-mixins-guide.md` | mail.thread, activities, mixins | Adding messaging, activities |
| `references/odoo-17-model-guide.md` | ORM methods, CRUD, domains | Writing model methods |
| `references/odoo-17-migration-guide.md` | Migration scripts, hooks | Upgrading modules |
| `references/odoo-17-owl-guide.md` | OWL components, hooks, services | Building OWL UI |
| `references/odoo-17-performance-guide.md` | Performance optimization | Fixing slow code |
| `references/odoo-17-reports-guide.md` | QWeb reports, templates | Creating reports |
| `references/odoo-17-security-guide.md` | ACL, record rules, security | Configuring security |
| `references/odoo-17-testing-guide.md` | Test classes, decorators, mocking | Writing tests |
| `references/odoo-17-transaction-guide.md` | Database transactions, error handling | Savepoints, UniqueViolation |
| `references/odoo-17-translation-guide.md` | Translations, localization, i18n | Adding translations |
| `references/odoo-17-view-guide.md` | XML views, actions, menus | Writing view XML |

Apply the **Coding Conventions** section in the guide you open. Odoo 17
runtime behavior, then the style of a stable addon being changed, take
precedence over a convention; do not make style-only rewrites.

---

## AI Agent Configuration

### Cursor IDE

| Setting | Value |
|---------|-------|
| Source | Git Repository |
| URL | `git@github.com:unclecatvn/agent-skills.git` |
| Branch | `17.0` |
| Subfolder | `skills/odoo-17.0/` |

**Globs patterns used by Cursor:**

| File | globs Pattern |
|------|---------------|
| `SKILL.md` | `**/*.{py,xml}` |
| `references/odoo-17-actions-guide.md` | `**/*.{py,xml}` |
| `references/odoo-17-controller-guide.md` | `**/controllers/**/*.py` |
| `references/odoo-17-data-guide.md` | `**/*.{xml,csv}` |
| `references/odoo-17-decorator-guide.md` | `**/models/**/*.py` |
| `references/odoo-17-development-guide.md` | `**/*.{py,xml,csv}` |
| `references/odoo-17-field-guide.md` | `**/models/**/*.py` |
| `references/odoo-17-manifest-guide.md` | `**/__manifest__.py` |
| `references/odoo-17-mixins-guide.md` | `**/models/**/*.py` |
| `references/odoo-17-model-guide.md` | `**/models/**/*.py` |
| `references/odoo-17-migration-guide.md` | `**/migrations/**/*.py` |
| `references/odoo-17-owl-guide.md` | `static/src/**/*.{js,xml}` |
| `references/odoo-17-performance-guide.md` | `**/*.{py,xml}` |
| `references/odoo-17-reports-guide.md` | `**/report/**/*.xml` |
| `references/odoo-17-security-guide.md` | `**/security/**/*.{csv,xml}` |
| `references/odoo-17-testing-guide.md` | `**/tests/**/*.py` |
| `references/odoo-17-transaction-guide.md` | `**/models/**/*.py` |
| `references/odoo-17-translation-guide.md` | `**/*.{py,js,xml}` |
| `references/odoo-17-view-guide.md` | `**/views/**/*.xml` |

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
└── odoo-17/
    └── SKILL.md

.claude/skills/
└── odoo-17/
    └── SKILL.md
```

---

## Key Odoo 17 Conventions

Odoo 17 is the last version before the v18 API modernization. Write code using the v17 conventions:

| Concern | Odoo 17 | v18+ (not valid in v17) |
|--------|---------|-------------------------|
| List view tag | `<tree>` | `<list>` |
| Dynamic attributes | Direct `invisible="..."`, `readonly="..."`, `required="..."` (v17 REMOVED the legacy `attrs=`/`states=` forms — validator rejects them) | (same, `attrs=`/`states=` removed starting 17.0) |
| Field aggregation | `group_operator=` | `aggregator=` |
| SQL queries | `cr.execute()` | `SQL` class + `execute_query_dict()` |
| SQL constraints | `_sql_constraints` | `models.Constraint(...)` |
| Kanban card | `t-name="kanban-box"` | `t-name="card"` |

---

## Repository

**URL**: `git@github.com:unclecatvn/agent-skills.git`
**Branch**: `17.0`
**License**: MIT

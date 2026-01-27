# Odoo 18 Documentation - AI Agents Setup

Setup guide for using Odoo 18 documentation with AI coding assistants (Cursor, Claude Code, OpenCode, etc.).

## Quick Start

### Remote Repository (Recommended)

**Cursor IDE** - Configure once:
- `Settings` → `Rules` → `Add Remote Rule`
- Source: `Git Repository`
- URL: `git@github.com:unclecatvn/agent-skills.git`
- Branch: `odoo/18.0`
- Subfolder: `agent-skills/skills/odoo/18.0/`

### Local Copy

```bash
# Clone repository
git clone git@github.com:unclecatvn/agent-skills.git

# Copy to your project
cp -r agent-skills/skills/odoo/18.0 /your-project/agent-skills/skills/odoo/

# For Claude Code, create symlink
ln -s agent-skills/skills/odoo/18.0/CLAUDE.md ./CLAUDE.md
```

---

## Documentation Structure

```
agent-skills/skills/odoo/18.0/
├── SKILL.md                       # Master index (all agents)
├── dev/                           # Development guides folder
│   ├── odoo-18-model-guide.md     # ORM, CRUD, search, domain
│   ├── odoo-18-field-guide.md     # Field types, parameters
│   ├── odoo-18-decorator-guide.md  # @api decorators
│   ├── odoo-18-view-guide.md      # XML views, actions, menus
│   ├── odoo-18-performance-guide.md # N+1 prevention, optimization
│   ├── odoo-18-transaction-guide.md # Savepoints, UniqueViolation
│   ├── odoo-18-controller-guide.md # HTTP, routing, controllers
│   ├── odoo-18-owl-guide.md       # OWL components, hooks, services
│   ├── odoo-18-migration-guide.md # Migration scripts, upgrade hooks
│   ├── odoo-18-testing-guide.md   # Test classes, decorators, mocking
│   ├── odoo-18-development-guide.md # Manifest, reports, security, wizards
│   └── odoo-18-translation-guide.md # Translations, localization, i18n
├── CLAUDE.md                      # Claude Code specific
└── AGENTS.md                      # THIS FILE - setup guide
```

---

## Guide Reference

| File | Purpose | When to Use |
|------|---------|-------------|
| `SKILL.md` | Master index for all guides | Find the right guide for your task |
| `dev/odoo-18-model-guide.md` | ORM methods, CRUD, domains | Writing model methods |
| `dev/odoo-18-field-guide.md` | Field types, parameters | Defining model fields |
| `dev/odoo-18-decorator-guide.md` | @api decorators usage | Using @api decorators |
| `dev/odoo-18-view-guide.md` | XML views, actions, menus | Writing view XML |
| `dev/odoo-18-performance-guide.md` | Performance optimization | Fixing slow code |
| `dev/odoo-18-transaction-guide.md` | Database transactions, error handling | Savepoints, UniqueViolation |
| `dev/odoo-18-controller-guide.md` | HTTP controllers, routing | Writing endpoints |
| `dev/odoo-18-owl-guide.md` | OWL components, hooks, services | Building OWL UI components |
| `dev/odoo-18-migration-guide.md` | Migration scripts, upgrade hooks | Upgrading modules, data migration |
| `dev/odoo-18-testing-guide.md` | Test classes, decorators, mocking | Writing tests |
| `dev/odoo-18-development-guide.md` | Module structure, security | Creating new modules |
| `dev/odoo-18-translation-guide.md` | Translations, localization, i18n | Adding translatable strings |

---

## AI Agent Configuration

### Cursor IDE

| Setting | Value |
|---------|-------|
| Source | Git Repository |
| URL | `git@github.com:unclecatvn/agent-skills.git` |
| Branch | `odoo/18.0` |
| Subfolder | `agent-skills/skills/odoo/18.0/` |

**Globs patterns used by Cursor:**

| File | globs Pattern |
|------|---------------|
| `SKILL.md` | `**/*.{py,xml}` |
| `dev/odoo-18-model-guide.md` | `**/models/**/*.py` |
| `dev/odoo-18-field-guide.md` | `**/models/**/*.py` |
| `dev/odoo-18-decorator-guide.md` | `**/models/**/*.py` |
| `dev/odoo-18-view-guide.md` | `**/views/**/*.xml` |
| `dev/odoo-18-controller-guide.md` | `**/controllers/**/*.py` |
| `dev/odoo-18-performance-guide.md` | `**/*.{py,xml}` |
| `dev/odoo-18-transaction-guide.md` | `**/models/**/*.py` |
| `dev/odoo-18-owl-guide.md` | `static/src/**/*.{js,xml}` |
| `dev/odoo-18-migration-guide.md` | `**/migrations/**/*.py` |
| `dev/odoo-18-testing-guide.md` | `**/tests/**/*.py` |
| `dev/odoo-18-development-guide.md` | `**/*.{py,xml,csv}` |
| `dev/odoo-18-translation-guide.md` | `**/*.{py,js,xml}` |

### Claude Code

```bash
# Place CLAUDE.md in project root
ln -s agent-skills/skills/odoo/18.0/CLAUDE.md ./CLAUDE.md
```

Claude Code reads:
- `CLAUDE.md` - Project overview and quick reference
- `SKILL.md` - Master index for all guides
- Individual guides in `dev/` - Detailed information

### OpenCode

Copy documentation to project - no additional configuration needed.

### Other Agents

| Agent | Setup |
|-------|-------|
| Windsurf | Same as Cursor (uses `.mdc` files) |
| Continue | Place `CLAUDE.md` or `dev/SKILL.md` in root |
| Aider | Place `CLAUDE.md` or add to prompt |

---

## Cursor / Claude Skills Folder

For Cursor IDE with local rules, create:

```
.cursor/skills/
└── odoo-18/
    └── SKILL.md -> ../../agent-skills/skills/odoo/18.0/SKILL.md
```

Or for Claude Code:

```
.claude/skills/
└── odoo-18/
    └── SKILL.md -> ../../agent-skills/skills/odoo/18.0/SKILL.md
```

---

## Version Compatibility

| Odoo Version | Branch | Status |
|--------------|--------|--------|
| 18.0 | `odoo/18.0` | ✅ Current |
| 17.0 | `odoo/17.0` | ✅ Available |
| 16.0 | `odoo/16.0` | ✅ Available |

### Key Odoo 18 Changes

| Change | Old | New |
|--------|-----|-----|
| List view tag | `<tree>` | `<list>` |
| Dynamic attributes | `attrs="{'invisible': [...]}"` | `invisible="..."` |
| Delete validation | Override `unlink()` | `@api.ondelete(at_uninstall=False)` |
| Field aggregation | `group_operator=` | `aggregator=` |

---

## Repository

**URL**: `git@github.com:unclecatvn/agent-skills.git`

**License**: MIT

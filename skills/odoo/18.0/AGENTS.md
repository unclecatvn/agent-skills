# Odoo 18 Documentation - AI Agents Setup

This guide explains how to use the Odoo 18 documentation with different AI coding assistants (Cursor, Claude Code, OpenCode, GitHub Copilot, etc.).

## Quick Start

### Using Remote Rules (Cursor - Recommended)

1. **Configure once in Cursor:**
   - `Settings` → `Rules` → `Add Remote Rule`
   - Source: `Git Repository`
   - URL: `git@github.com:unclecatvn/agent-skills.git`
   - Branch: `odoo/18.0` (hoặc `main`)

2. **Done!** Rules auto-apply to ALL your projects

### Local Copy (Alternative)

1. **Clone the repository:**
   ```bash
   git clone git@github.com:unclecatvn/agent-skills.git
   cd agent-skills
   ```

2. **Copy to your project:**
   ```bash
  cp -r skills/odoo/18.0 /your-project/docs/skills/odoo/
   ```

3. **For Claude Code, add symlink:**
   ```bash
  ln -s docs/skills/odoo/18.0/CLAUDE.md ./CLAUDE.md
   ```

## Documentation Structure

```
docs/skills/odoo/18.0/
├── SKILL.md                       # Master reference (all agents)
├── CLAUDE.md                      # Claude Code specific
├── AGENTS.md                      # THIS FILE - setup guide
├── odoo-18-model-guide.md         # ORM, CRUD, search, domain
├── odoo-18-field-guide.md         # Field types, parameters
├── odoo-18-decorator-guide.md      # @api decorators
├── odoo-18-view-guide.md          # XML views, actions, menus
├── odoo-18-performance-guide.md    # N+1 prevention, optimization
├── odoo-18-transaction-guide.md   # Savepoints, UniqueViolation, commit/rollback
├── odoo-18-controller-guide.md     # HTTP, routing, controllers
├── odoo-18-owl-guide.md           # OWL components, hooks, services
├── odoo-18-migration-guide.md     # Migration scripts, upgrade hooks
├── odoo-18-testing-guide.md       # Test classes, decorators, mocking
└── odoo-18-development-guide.md    # Manifest, reports, security
```

## Quick Reference for Each File

| File | Purpose | When AI Needs It |
|------|---------|------------------|
| `SKILL.md` | Master reference with all key patterns | Quick lookups, common issues |
| `odoo-18-model-guide.md` | ORM methods, CRUD, domains | Writing model methods |
| `odoo-18-field-guide.md` | Field types, parameters | Defining model fields |
| `odoo-18-decorator-guide.md` | @api decorators usage | Using @api decorators |
| `odoo-18-view-guide.md` | XML views, actions, menus | Writing view XML |
| `odoo-18-performance-guide.md` | Performance optimization | Fixing slow code |
| `odoo-18-transaction-guide.md` | Database transactions, error handling | Savepoints, UniqueViolation |
| `odoo-18-controller-guide.md` | HTTP controllers, routing | Writing endpoints |
| `odoo-18-owl-guide.md` | OWL components, hooks, services | Building OWL UI components |
| `odoo-18-migration-guide.md` | Migration scripts, upgrade hooks | Upgrading modules, data migration |
| `odoo-18-testing-guide.md` | Test classes, decorators, mocking | Writing tests |
| `odoo-18-development-guide.md` | Module structure, security | Creating new modules |

---

> **Repository**: `git@github.com:unclecatvn/agent-skills.git`
> **Branch**: `odoo/18.0` (or `main`)
> **This documentation is part of the agent-skills repository**

---

## Cursor IDE

### How Cursor Uses This Documentation

Cursor automatically discovers `.mdc` files with YAML frontmatter and applies the rules based on the `globs` pattern.

### Setup Options

#### Option A: Remote Rules (Recommended)

**This documentation is already in** `git@github.com:unclecatvn/agent-skills.git`

1. **Configure Cursor Remote Rule:**
   - Go to `Settings` → `Rules` → `Add Remote Rule`
   - Source: `Git Repository`
   - URL: `git@github.com:unclecatvn/agent-skills.git`
   - Branch: `odoo/18.0` (hoặc `main`)
  - **Optional:** Subfolder: `skills/odoo/18.0/` (nếu có nhiều skills)

2. **Done!** Cursor auto-applies rules to ALL your projects

**Benefits:**
- ✅ One central source of truth for all AI agent skills
- ✅ Update once, all projects受益
- ✅ No file pollution in projects
- ✅ Shared across teams

#### Option B: Local Copy

**Copy documentation to project:**
```bash
cp -r docs/skills/odoo/18.0 /your-project/docs/skills/odoo/
```

**Use when:**
- Working offline frequently
- Want project-specific overrides

### .mdc Format

```yaml
---
description: What this guide covers
globs: "**/*.py"
alwaysApply: true
---

# Content here
```

### Key .mdc Files for Cursor

| File | globs Pattern | Scope |
|------|---------------|-------|
| `SKILL.md` | `**/*.{py,xml}` | All Odoo files (master rules) |
| `odoo-18-model-guide.md` | `**/models/**/*.py` | Model files only |
| `odoo-18-field-guide.md` | `**/models/**/*.py` | Model files only |
| `odoo-18-decorator-guide.md` | `**/models/**/*.py` | Model files only |
| `odoo-18-view-guide.md` | `**/views/**/*.xml` | View XML files only |
| `odoo-18-controller-guide.md` | `**/controllers/**/*.py` | Controller files only |
| `odoo-18-performance-guide.md` | `**/*.{py,xml}` | All Odoo files |
| `odoo-18-transaction-guide.md` | `**/models/**/*.py` | Model files only |
| `odoo-18-owl-guide.md` | `static/src/**/*.{js,xml}` | OWL/JS files only |
| `odoo-18-migration-guide.md` | `**/migrations/**/*.py` | Migration scripts |
| `odoo-18-testing-guide.md` | `**/tests/**/*.py` | Test files only |
| `odoo-18-development-guide.md` | `**/*.{py,xml,csv}` | All Odoo files |

### Frontmatter Fields Used by Cursor

| Field | Type | Description |
|-------|------|-------------|
| `description` | string | Summary of what the guide covers |
| `globs` | string/array | File patterns to apply this guide to |
| `alwaysApply` | boolean | Apply this guide to all matching files |

---

## Claude Code (claude.ai/code)

### How Claude Code Uses This Documentation

Claude Code reads `CLAUDE.md` and `SKILL.md` to understand project-specific patterns and best practices.

### Setup

1. **Place CLAUDE.md in project root** (or symlink):
   ```bash
  ln -s docs/skills/odoo/18.0/CLAUDE.md ./CLAUDE.md
   ```

2. **Or copy**:
   ```bash
  cp docs/skills/odoo/18.0/CLAUDE.md ./CLAUDE.md
   ```

### What Claude Code Reads

| File | Content |
|------|---------|
| `CLAUDE.md` | Project overview, quick patterns, which guide to use when |
| `SKILL.md` | Complete reference with all patterns and anti-patterns |
| Individual guides | Detailed information when explicitly referenced |

---

## OpenCode

### How OpenCode Uses This Documentation

OpenCode reads markdown files with YAML frontmatter, using the `description` and `globs` fields to determine when to apply each guide.

### Setup

1. **Copy documentation** to your project
2. **No additional configuration** - OpenCode auto-discovers markdown files with frontmatter

### Frontmatter Format

```yaml
---
name: odoo-18-model
description: Complete reference for Odoo 18 ORM...
globs: "**/models/**/*.py"
topics:
  - Recordset basics
  - Search methods
when_to_use:
  - Writing ORM queries
---
```

---

## GitHub Copilot

### How Copilot Uses This Documentation

Copilot doesn't have built-in documentation reading, but having clear code examples in markdown files can improve suggestions.

### Setup

1. **Keep documentation in `docs/`** folder
2. **Reference in comments** when needed:
   ```python
  # See docs/skills/odoo/18.0/odoo-18-model-guide.md for ORM patterns
   ```

---

## Other AI Agents

### Windsurf

Similar to Cursor - uses `.mdc` files with YAML frontmatter.

### Continue

Reads project documentation. Place `CLAUDE.md` or `SKILL.md` in project root.

### Tabnine

Limited documentation reading. Use code comments to reference guides.

### Aider

Reads markdown files. Can use `CLAUDE.md` or add to prompt.

### Codeium

Limited documentation reading. Use inline code comments.

---

## Installation in Your Project

### Option 1: Remote Rules (Recommended for Cursor)

**No files needed in project** - Configure once in Cursor:

1. Already configured in repo: `git@github.com:unclecatvn/agent-skills.git`
2. Cursor → Settings → Rules → Add Remote Rule
3. URL: `git@github.com:unclecatvn/agent-skills.git`
4. Branch: `odoo/18.0` (hoặc `main`)

### Option 2: Local Copy

For **Cursor** only:
```bash
cp docs/skills/odoo/18.0/SKILL.md /your-project/
```

For **Claude Code** only:
```bash
cp docs/skills/odoo/18.0/CLAUDE.md /your-project/
```

For **Both**:
```bash
cp docs/skills/odoo/18.0/SKILL.md /your-project/
cp docs/skills/odoo/18.0/CLAUDE.md /your-project/
```

### Option 3: Git Submodule (Alternative)

```bash
# In your project
git submodule add git@github.com:unclecatvn/agent-skills.git docs/skills/odoo/18.0
```

---

## Frontmatter Reference

All guide files use this YAML frontmatter format:

```yaml
---
name: odoo-18-[topic]
description: [Brief description of what this guide covers]
globs: [file pattern to apply this guide to]
topics:
  - [Topic 1]
  - [Topic 2]
when_to_use:
  - [Use case 1]
  - [Use case 2]
---
```

### Common glob Patterns

| Pattern | Matches |
|---------|---------|
| `**/*.{py,xml}` | All Python and XML files anywhere |
| `**/models/**/*.py` | Python files in `models/` folders |
| `**/views/**/*.xml` | XML files in `views/` folders |
| `**/controllers/**/*.py` | Python files in `controllers/` folders |
| `**/*.{py,xml,csv}` | Python, XML, and CSV files |

---

## File Priority (When Multiple Guides Match)

When a file matches multiple guides (e.g., `models/my_model.py`), agents typically use:

1. **Most specific globs** win (`**/models/**/*.py` > `**/*.{py,xml}`)
2. **Alphabetical order** as tiebreaker

### Example Priority for `models/sale_order.py`

| Priority | Guide | glob Pattern |
|----------|-------|--------------|
| 1 | `odoo-18-model-guide.md` | `**/models/**/*.py` |
| 2 | `odoo-18-field-guide.md` | `**/models/**/*.py` |
| 3 | `odoo-18-decorator-guide.md` | `**/models/**/*.py` |
| 4 | `odoo-18-performance-guide.md` | `**/*.{py,xml}` |
| 5 | `odoo-18-development-guide.md` | `**/*.{py,xml,csv}` |

---

## Customizing for Your Project

### Adding Project-Specific Rules

Create a `.mdc` file in your project root:

```yaml
---
description: Project-specific Odoo 18 rules and conventions
globs: "**/*.{py,xml}"
---

# Project Specific Rules

## Naming Convention

- Model names: `project.module.name`
- XML IDs: `project_module_view_...`
- Python files: lowercase with underscores

## Custom Patterns

# Always include company_id in domain
domain = [('company_id', '=', self.env.company.id)] + domain
```

### Overriding Default Rules

To override a specific rule, create a new `.mdc` with a more specific `globs` pattern:

```yaml
---
description: Override for specific module
globs: "**/models/specific_model.py"
---

# This overrides general rules for specific_model.py only
```

---

## Troubleshooting

### Cursor not applying rules

1. Check file extension is `.mdc`
2. Verify YAML frontmatter is valid (use a YAML validator)
3. Check `globs` pattern matches your files
4. Try reopening the project

### Claude Code not seeing documentation

1. Ensure `CLAUDE.md` is in project root
2. Check file is readable (not binary)
3. Try referencing explicitly: "See CLAUDE.md for..."

### Conflicting rules from multiple guides

1. Check `globs` specificity
2. More specific patterns take precedence
3. Rename files to control alphabetical order if needed

---

## Version Compatibility

| Odoo Version | Documentation Branch | Status |
|--------------|---------------------|--------|
| 18.0 | `18.0` | ✅ Current |
| 17.0 | `17.0` | ❌ Not compatible (breaking changes) |
| 16.0 | `16.0` | ❌ Not compatible |

### Key Breaking Changes (Odoo 17 → 18)

- `<tree>` → `<list>` for list views
- `unlink()` override → `@api.ondelete()`
- `group_operator=` → `aggregator=`
- `cr.execute()` → `SQL` class

---

## Contributing

To improve this documentation:

1. Edit the relevant guide file
2. Update frontmatter if adding new topics
3. Test with your AI agent
4. Submit pull request

---

## License

MIT License - See individual files for details.

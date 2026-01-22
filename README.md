# Agent Skills Documentation

> Comprehensive documentation and skill packs for AI-powered development assistants

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Odoo Version](https://img.shields.io/badge/Odoo-18.0-blue)](https://www.odoo.com/)
[![Type](https://img.shields.io/badge/Type-Skills%20Pack-green)]()

---

## Overview

This repository contains **versioned documentation and skill packs** designed to enhance AI coding assistants (Cursor, Claude Code, Windsurf, Continue, etc.) with domain-specific knowledge for professional development workflows.

### What are Skill Packs?

Skill packs are structured markdown files with YAML frontmatter that AI agents use to understand:
- **Framework patterns** and best practices
- **API conventions** and idiomatic code
- **Anti-patterns** to avoid
- **Project-specific conventions**

When an AI agent has access to these skill packs, it generates code that follows your project's standards, uses correct patterns, and avoids common mistakes.

---

## Features

| Feature | Description |
|---------|-------------|
| **Versioned Documentation** | Separate skill packs for each major version (e.g., Odoo 17.0, 18.0) |
| **AI-IDE Compatible** | Works with Cursor, Claude Code, Windsurf, Continue, and more |
| **Remote Rules Support** | Configure once, apply to all projects (Cursor) |
| **Modular Architecture** | Each topic has its own guide file |
| **Breaking Changes Tracking** | Clear documentation of version differences |
| **NPM Package** | Install via CLI for easy setup |

---

## Quick Start

### Option 1: Remote Configuration (Cursor - Recommended)

Configure once in Cursor IDE:

1. Open **Settings** → **Rules** → **Add Remote Rule**
2. Source: `Git Repository`
3. URL: `git@github.com:unclecatvn/agent-skills.git`
4. Branch: `odoo/18.0`

Done! Rules automatically apply to all your projects.

### Option 2: NPM CLI

```bash
# Install the CLI globally
npm install -g @unclecat/agent-skills-cli

# Initialize skills for your project
agent-skills init --ai cursor odoo --version 18.0

# List available versions
agent-skills versions odoo
```

### Option 3: Manual Setup

```bash
# Clone the repository
git clone git@github.com:unclecatvn/agent-skills.git

# Copy to your project
cp -r agent-skills/skills/odoo/18.0 /your-project/docs/skills/odoo/

# For Claude Code, create symlink
ln -s docs/skills/odoo/18.0/CLAUDE.md ./CLAUDE.md
```

---

## Repository Structure

```
docs/
├── README.md                                # This file
├── skills/
│   └── odoo/
│       └── 18.0/                            # Odoo 18.0 skill pack
│           ├── SKILL.md                     # Master reference
│           ├── CLAUDE.md                    # Claude Code specific
│           ├── AGENTS.md                    # Setup guide for AI IDEs
│           ├── odoo-18-model-guide.md       # ORM, CRUD, search, domain
│           ├── odoo-18-field-guide.md       # Field types, parameters
│           ├── odoo-18-decorator-guide.md    # @api decorators
│           ├── odoo-18-view-guide.md         # XML views, actions, menus
│           ├── odoo-18-performance-guide.md  # N+1 prevention, optimization
│           ├── odoo-18-transaction-guide.md # Savepoints, error handling
│           ├── odoo-18-controller-guide.md  # HTTP, routing, controllers
│           ├── odoo-18-owl-guide.md         # OWL components, hooks
│           └── odoo-18-development-guide.md  # Manifest, reports, security
├── commands/                                # Helper prompts and templates
└── bin/                                     # CLI entry point
```

---

## Odoo 18.0 Skill Pack

### Available Guides

| Guide | Lines | Topics Covered |
|-------|-------|----------------|
| Model Guide | 896 | ORM methods, CRUD operations, domain syntax, search methods |
| Field Guide | 844 | Field types, parameters, Float/Date helpers, Image/Many2oneReference |
| Decorator Guide | 599 | @api decorators, compute fields, constraints, onchange |
| View Guide | 868 | XML views, actions, menus, QWeb templates, list views (Odoo 18) |
| Performance Guide | 611 | N+1 prevention, optimization, batch operations |
| Transaction Guide | 640 | Savepoints, UniqueViolation, commit/rollback strategies |
| Controller Guide | 527 | HTTP routing, authentication, JSON endpoints |
| OWL Guide | 1483 | OWL components, hooks, services, templates |
| Development Guide | 1196 | Module structure, manifest, security, wizards, reports |

**Total: 8,773 lines of comprehensive Odoo 18 documentation**

### Key Odoo 18 Changes

| Change | Odoo 17 | Odoo 18 |
|--------|---------|---------|
| List view tag | `<tree>` | `<list>` |
| Delete validation | Override `unlink()` | `@api.ondelete(at_uninstall=False)` |
| Field aggregation | `group_operator=` | `aggregator=` |
| SQL queries | `cr.execute()` | `SQL` class with `execute_query_dict()` |
| Batch create | Single dict | List of dicts: `create([{...}, {...}])` |

---

## Supported AI IDEs

| IDE | Status | Setup Method |
|-----|--------|--------------|
| **Cursor** | ✅ Full Support | Remote Rules (recommended) or local `.mdc` files |
| **Claude Code** | ✅ Full Support | `CLAUDE.md` in project root |
| **Windsurf** | ✅ Full Support | `.mdc` files with frontmatter |
| **Continue** | ✅ Full Support | `CLAUDE.md` or `SKILL.md` |
| **OpenCode** | ✅ Full Support | Auto-discovers markdown with frontmatter |
| **GitHub Copilot** | ⚠️ Limited | Reference in code comments |
| **Aider** | ✅ Full Support | Markdown files in project |
| **Tabnine** | ⚠️ Limited | Code comments only |

For detailed setup instructions, see [AGENTS.md](./skills/odoo/18.0/AGENTS.md).

---

## Usage Examples

### For Model Development

When working with Odoo models, AI agents will:

- ✅ Use `@api.depends('partner_id.email')` with dotted paths
- ✅ Apply `@api.ondelete(at_uninstall=False)` for delete validation
- ✅ Use `aggregator='sum'` instead of deprecated `group_operator`
- ✅ Write `<list>` instead of `<tree>` for list views
- ✅ Batch operations: `create([{...}, {...}])`
- ❌ Avoid N+1 queries in loops
- ❌ Avoid overriding `unlink()` for validation

### For Frontend Development

When building OWL components, AI agents will:

- ✅ Use proper services: `orm`, `rpc`, `dialog`, `notification`
- ✅ Follow lifecycle hooks: `onWillStart`, `onMounted`, `onWillUnmount`
- ✅ Use `useState` for reactive state management
- ✅ Properly import with `/** @odoo-module **/`

---

## Version Compatibility

| Odoo Version | Branch | Status | Breaking Changes |
|--------------|--------|--------|------------------|
| 18.0 | `odoo/18.0` | ✅ Current | N/A |
| 17.0 | `odoo/17.0` | ⚠️ Legacy | Incompatible with 18.0 skill pack |
| 16.0 | `odoo/16.0` | ⚠️ Legacy | Incompatible with 18.0 skill pack |

---

## Contributing

We welcome contributions! To improve the skill packs:

1. **Identify the gap**: Missing pattern, incorrect example, or unclear documentation
2. **Edit the guide**: Modify the relevant `.md` file in `skills/odoo/18.0/`
3. **Update frontmatter**: Add new topics if introducing new sections
4. **Test locally**: Verify with your AI agent before submitting
5. **Submit PR**: Include description of what was improved

### Contribution Areas

- **New Guides**: WebSocket integration, testing patterns, migration guides
- **Expanded Topics**: More QWeb examples, advanced ORM patterns
- **Code Examples**: Real-world use cases from production code
- **Translations**: Multi-language support

---

## License

This project is licensed under the MIT License - see individual files for details.

---

## Links

- **Repository**: [git@github.com:unclecatvn/agent-skills.git](https://github.com/unclecatvn/agent-skills)
- **NPM Package**: [@unclecat/agent-skills-cli](https://www.npmjs.com/package/@unclecat/agent-skills-cli)
- **Issue Tracker**: [GitHub Issues](https://github.com/unclecatvn/agent-skills/issues)

---

## Acknowledgments

Built with references to official Odoo 18 source code:
- `odoo/models.py` - ORM implementation
- `odoo/fields.py` - Field types
- `odoo/api.py` - Decorators
- `odoo/http.py` - HTTP layer
- `odoo/exceptions.py` - Exception types

---

*Last updated: January 2026*

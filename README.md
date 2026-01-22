# Agent Skills Documentation

> **Skill packs, agents, and commands** for AI-powered development assistants

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![NPM Version](https://img.shields.io/npm/v/@unclecat/agent-skills-cli.svg)](https://www.npmjs.com/package/@unclecat/agent-skills-cli)
[![Odoo](https://img.shields.io/badge/Odoo-18.0-blue)](https://www.odoo.com/)
[![Type](https://img.shields.io/badge/Type-Skills%20Pack-green)]()

---

## Overview

This repository contains a comprehensive suite of **versioned documentation, skill packs, specialized agents, and command templates** designed to enhance AI coding assistants (Cursor, Claude Code, Windsurf, Continue, etc.) with domain-specific knowledge.

### What's Inside?

| Component | Description | Location |
|-----------|-------------|----------|
| **Skill Packs** | Versioned framework documentation (Odoo 18.0) | `skills/` |
| **Agents** | Specialized AI agents (Odoo code reviewer) | `agents/` |
| **Commands** | Reusable prompt templates | `commands/` |
| **CLI Tool** | Install & manage skills via CLI | `bin/` |

---

## Table of Contents

- [Quick Start](#quick-start)
- [Skill Packs](#skill-packs)
- [Agents](#agents)
- [Commands](#commands)
- [Installation](#installation)
- [Supported AI IDEs](#supported-ai-ides)
- [Repository Structure](#repository-structure)
- [Contributing](#contributing)

---

## Quick Start

### Remote Configuration (Cursor - Recommended)

1. Open **Settings** → **Rules** → **Add Remote Rule**
2. Source: `Git Repository`
3. URL: `git@github.com:unclecatvn/agent-skills.git`
4. Branch: `odoo/18.0`

### NPM CLI Installation

```bash
# Install CLI globally
npm install -g @unclecat/agent-skills-cli

# Initialize skills for your project
agent-skills init --ai cursor odoo --version 18.0

# List available versions
agent-skills versions odoo
```

### Manual Setup

```bash
# Clone repository
git clone git@github.com:unclecatvn/agent-skills.git

# Copy to your project
cp -r agent-skills/skills/odoo/18.0 /your-project/docs/skills/odoo/

# For Claude Code
ln -s docs/skills/odoo/18.0/CLAUDE.md ./CLAUDE.md
```

---

## Skill Packs

### Odoo 18.0 Skill Pack

Comprehensive Odoo 18 framework documentation with **7,761 lines** across 9 specialized guides.

| Guide | Lines | Topics |
|-------|-------|--------|
| [Model Guide](skills/odoo/18.0/odoo-18-model-guide.md) | 896 | ORM, CRUD, search, domain syntax |
| [Field Guide](skills/odoo/18.0/odoo-18-field-guide.md) | 844 | Field types, Float/Date helpers, Image, Many2oneReference |
| [Decorator Guide](skills/odoo/18.0/odoo-18-decorator-guide.md) | 599 | @api decorators, compute, constraints, onchange |
| [View Guide](skills/odoo/18.0/odoo-18-view-guide.md) | 868 | XML views, actions, menus, QWeb templates |
| [Performance Guide](skills/odoo/18.0/odoo-18-performance-guide.md) | 611 | N+1 prevention, batch operations |
| [Transaction Guide](skills/odoo/18.0/odoo-18-transaction-guide.md) | 640 | Savepoints, UniqueViolation, commit/rollback |
| [Controller Guide](skills/odoo/18.0/odoo-18-controller-guide.md) | 527 | HTTP routing, authentication, JSON endpoints |
| [OWL Guide](skills/odoo/18.0/odoo-18-owl-guide.md) | 1483 | OWL components, hooks, services, templates |
| [Development Guide](skills/odoo/18.0/odoo-18-development-guide.md) | 1196 | Module structure, manifest, security, wizards |

**Supporting Files:**
- `SKILL.md` - Master reference (623 lines)
- `CLAUDE.md` - Claude Code specific (146 lines)
- `AGENTS.md` - AI IDE setup guide (428 lines)

#### Key Odoo 18 Changes

| Change | Odoo 17 | Odoo 18 |
|--------|---------|---------|
| List view tag | `<tree>` | `<list>` |
| Delete validation | Override `unlink()` | `@api.ondelete(at_uninstall=False)` |
| Field aggregation | `group_operator=` | `aggregator=` |
| SQL queries | `cr.execute()` | `SQL.execute_query_dict()` |
| Batch create | Single dict | List of dicts |

### Brainstorming Skill Pack

Facilitates structured brainstorming sessions for feature planning and problem-solving.

---

## Agents

### Odoo Code Review Agent

**Location:** `agents/odoo-code-review/SKILL.md` (228 lines)

Expert-level Odoo 18 code review with weighted scoring across multiple criteria:

**Review Criteria:**
- ORM Best Practices (N+1 prevention, prefetching)
- @api Decorator Usage (@api.depends, @api.ondelete, @api.constrains)
- Field Type Selection (Monetary vs Float, proper indexes)
- Odoo 18 Compatibility (`<list>` vs `<tree>`, aggregator, precompute)
- Performance Patterns (batch operations, mapped(), filtered())
- Transaction Safety (savepoints, UniqueViolation handling)
- Security & Access Control (record rules, ir.rule)
- View & XML Standards (proper inheritance, QWeb templates)
- Naming Conventions (Python, XML IDs, modules)

**Usage:**
```bash
# Via command
/odoo-code-review path/to/code.py

# Via AI IDE reference
"Review this using the odoo-code-review agent"
```

---

## Commands

Reusable prompt templates for common development workflows.

| Command | Description | Location |
|---------|-------------|----------|
| `brainstorm` | Structured brainstorming session | `commands/brainstorm.md` |
| `code-reviewer` | Trigger Odoo code review | `commands/code-reviewer.md` |
| `write-plan` | Create implementation plan | `commands/write-plan.md` |
| `execute-plan` | Execute from plan | `commands/execute-plan.md` |

### Using Commands

**In Cursor IDE:**
- Commands appear as slash commands (`/brainstorm`, `/code-reviewer`)
- Type `/` to see available commands

**In Claude Code:**
- Reference command files in prompts
- Use built-in slash command support

---

## Installation

### Option 1: Remote Rules (Cursor)

Configure once, apply to all projects:

1. **Settings** → **Rules** → **Add Remote Rule**
2. Source: `Git Repository`
3. URL: `git@github.com:unclecatvn/agent-skills.git`
4. Branch: `odoo/18.0` or `main`

### Option 2: NPM CLI

```bash
npm install -g @unclecat/agent-skills-cli
agent-skills init --ai <ide> <framework> --version <version>
```

### Option 3: Manual Copy

```bash
# Skills
cp -r skills/odoo/18.0 /your-project/docs/skills/odoo/

# Agents
cp -r agents/odoo-code-review /your-project/.claude/agents/

# Commands
cp -r commands/* /your-project/.claude/commands/
```

---

## Supported AI IDEs

| IDE | Skills | Agents | Commands | Setup |
|-----|--------|--------|----------|-------|
| **Cursor** | ✅ Remote Rules | ✅ | ✅ | Settings → Rules |
| **Claude Code** | ✅ CLAUDE.md | ✅ | ✅ | Project root |
| **Windsurf** | ✅ .mdc files | ✅ | ✅ | Project root |
| **Continue** | ✅ Markdown | ✅ | ⚠️ | Config file |
| **OpenCode** | ✅ Auto-discover | ⚠️ | ⚠️ | None |
| **Aider** | ✅ Markdown | ✅ | ⚠️ | Prompt ref |

For detailed setup, see [AGENTS.md](skills/odoo/18.0/AGENTS.md).

---

## Repository Structure

```
docs/
├── README.md                                # This file
├── LICENSE                                  # MIT License
├── package.json                             # NPM package config
├── .npmignore                               # NPM publish ignore rules
│
├── skills/                                  # Framework skill packs
│   ├── odoo/
│   │   ├── 18.0/                            # Odoo 18.0 (7,761 lines)
│   │   │   ├── SKILL.md                     # Master reference
│   │   │   ├── CLAUDE.md                    # Claude Code specific
│   │   │   ├── AGENTS.md                    # Setup guide
│   │   │   ├── odoo-18-model-guide.md
│   │   │   ├── odoo-18-field-guide.md
│   │   │   ├── odoo-18-decorator-guide.md
│   │   │   ├── odoo-18-view-guide.md
│   │   │   ├── odoo-18-performance-guide.md
│   │   │   ├── odoo-18-transaction-guide.md
│   │   │   ├── odoo-18-controller-guide.md
│   │   │   ├── odoo-18-owl-guide.md
│   │   │   └── odoo-18-development-guide.md
│   │   ├── README.md                        # Odoo skills overview
│   │   └── README_EN.md                     # English overview
│   └── brainstorming/
│       └── SKILL.md                         # Brainstorming facilitator
│
├── agents/                                  # Specialized AI agents
│   └── odoo-code-review/
│       └── SKILL.md                         # Odoo code reviewer (228 lines)
│
├── commands/                                # Prompt templates
│   ├── brainstorm.md                        # Brainstorming session
│   ├── code-reviewer.md                     # Trigger code review
│   ├── write-plan.md                        # Create plans
│   └── execute-plan.md                      # Execute plans
│
└── bin/                                     # CLI tool entry point
```

---

## Documentation Statistics

| Category | Files | Total Lines |
|----------|-------|-------------|
| **Odoo 18 Skills** | 12 files | 7,761 lines |
| **Odoo Code Review Agent** | 1 file | 228 lines |
| **Brainstorming Skill** | 1 file | 53 lines |
| **Commands** | 4 files | 21 lines |
| **Total** | **18 files** | **8,063 lines** |

---

## Usage Examples

### Odoo Model Development

With Odoo 18.0 skills loaded, AI agents will:

```python
# ✅ Correct patterns automatically applied
@api.depends('partner_id.email')  # Dotted paths (Odoo 18)
def _compute_email(self):
    for rec in self:
        rec.email = rec.partner_id.email

@api.ondelete(at_uninstall=False)  # Odoo 18 delete validation
def _unlink_if_not_draft(self):
    if any(rec.state != 'draft' for rec in self):
        raise UserError("Cannot delete non-draft records")

amount = fields.Float(aggregator='sum')  # Not group_operator (deprecated)
```

### Code Review

```
You: /code-reviewer

AI: [Invokes odoo-code-review agent]
     Reviewing code.py...

     ✓ ORM Best Practices: 9/10
     ✓ @api Decorators: 10/10
     ⚠ Performance: 7/10 - Consider using search_fetch()

     [Detailed findings and recommendations...]
```

### Planning & Brainstorming

```
You: /write-plan

AI: I'll create an implementation plan for this feature.
     [Structured plan with tasks, dependencies, and estimates...]

You: /brainstorm

AI: Let's brainstorm approaches for this problem...
     [Facilitates structured brainstorming session...]
```

---

## Version Compatibility

| Framework | Version | Status | Branch |
|-----------|---------|--------|--------|
| Odoo | 18.0 | ✅ Current | `odoo/18.0` |
| Odoo | 17.0 | ⚠️ Legacy | `odoo/17.0` |
| Odoo | 16.0 | ⚠️ Legacy | `odoo/16.0` |

---

## Roadmap

- [ ] **Odoo 19.0** skill pack (Q3 2026)
- [ ] **Laravel** skill pack
- [ ] **Django** skill pack
- [ ] **Testing Agents** (pytest, unittest specialists)
- [ ] **Migration Agents** (Odoo version upgrade assistant)
- [ ] **Web Commands** (React, Vue, Angular templates)

---

## Contributing

We welcome contributions! Areas of interest:

1. **New Skill Packs** - Additional frameworks (Laravel, Django, Express)
2. **New Agents** - Specialized reviewers (security, performance, testing)
3. **New Commands** - Workflow templates
4. **Enhanced Guides** - More examples, patterns, edge cases
5. **Translations** - Multi-language support

### Contribution Workflow

1. Fork the repository
2. Create a feature branch
3. Add/edit files in `skills/`, `agents/`, or `commands/`
4. Test with your AI agent
5. Submit PR with description

---

## License

MIT License - see [LICENSE](LICENSE) for details.

---

## Links

| Resource | URL |
|----------|-----|
| **Repository** | [github.com/unclecatvn/agent-skills](https://github.com/unclecatvn/agent-skills) |
| **NPM Package** | [@unclecat/agent-skills-cli](https://www.npmjs.com/package/@unclecat/agent-skills-cli) |
| **Issues** | [GitHub Issues](https://github.com/unclecatvn/agent-skills/issues) |
| **Discussions** | [GitHub Discussions](https://github.com/unclecatvn/agent-skills/discussions) |

---

## Acknowledgments

Built with references to official source code:
- **Odoo 18**: `odoo/models.py`, `odoo/fields.py`, `odoo/api.py`, `odoo/http.py`

---

*Last updated: January 2026*

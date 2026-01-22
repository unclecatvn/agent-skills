# Agent Skills Documentation

This repo hosts versioned documentation and skills packs used by AI IDEs,
along with the CLI that installs them.

## What's inside

- `skills/`: versioned skill packs (e.g. `skills/odoo/18.0`)
- `commands/`: helper prompts and command templates
- `bin/`: CLI entry point (`agent-skills`)

## CLI

Install the CLI:

```bash
npm install -g @unclecat/agent-skills-cli
```

Initialize an Odoo 18.0 skills pack:

```bash
agent-skills init --ai cursor odoo --version 18.0
```

List supported versions:

```bash
agent-skills versions odoo
```

## Repository layout

```
skills/
├── odoo/
│   └── 18.0/
│       ├── SKILL.md
│       └── odoo-18-*.md
commands/
bin/
```

## License

MIT License

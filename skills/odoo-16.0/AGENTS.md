# Odoo 16 Documentation - AI Agents Setup

Setup guide for using the Odoo 16 pack with AI coding assistants.

## Quick Start

```bash
npx skills add unclecatvn/agent-skills
```

Use `skills/odoo-16.0/SKILL.md` as the entry point, then open the matching guide in `references/`.

## Pack Layout

```
skills/odoo-16.0/
|-- SKILL.md
|-- CLAUDE.md
|-- AGENTS.md
`-- references/
```

## Which Guides Matter Most

- `references/odoo-16-development-guide.md` for module naming and file layout.
- `references/odoo-16-view-guide.md` for XML views, inherited views, chatter, kanban.
- `references/odoo-16-model-guide.md` for ORM, CRUD, domains, recordsets.
- `references/odoo-16-field-guide.md` for field definitions and `group_operator=`.
- `references/odoo-16-decorator-guide.md` for `@api.depends`, `@api.ondelete`, `@api.model_create_multi`.
- `references/api-highlights.md` for version-distinguishing rules that differ from 17+.

## Key Odoo 16 Conventions

| Concern | Odoo 16 | Newer-version change |
|---------|---------|----------------------|
| List view tag | `<tree>` | `<list>` in 18+ |
| Dynamic attributes | Use `attrs="{...}"` / `states="..."` for client-side dynamic behavior; direct `invisible="..."` is static/context-time only | Direct-expression modifiers become record-reactive in 17+ |
| Aggregation parameter | `group_operator=` | `aggregator=` in 18+ |
| Kanban template | `t-name="kanban-box"` | `t-name="card"` in 19 |
| Chatter in form view | Explicit `<div class="oe_chatter"> ... </div>` | `<chatter/>` shortcut in 18+ |

## Agent Guidance

- Prefer the `attrs` / `states` patterns documented in the 16 view guide for client-side dynamic modifiers; direct `invisible="..."` is valid only for static/context-time visibility.
- Match the existing addon style when editing 16 code, but check `api-highlights.md` before mass-rewriting XML.
- Treat `skills/odoo-16.0/references/api-highlights.md` as the authority when 16 and 17 guidance diverge.
- Apply the Coding Conventions section in the guide you open; Odoo 16 runtime behavior and the local stable-file style take precedence when they conflict.
